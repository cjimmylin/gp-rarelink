"""Stage 6 step 4: concordance of a tagged extraction run with a dated ClinVar/HPO snapshot (POC_DESIGN.md §3.10).

Harness side. Reads the run's outputs under data/extracted/<disease>/<run_id>/
(variants_normalized.csv, per_paper/*.json, phenopackets/*.json) and a
snapshot folder written by snapshot_reference.py (kept outside the repo).

Measures (Wilson 95% intervals, snapshot date on every table):
  variant presence      distinct extracted TNFAIP3 variants normalized to a
                        GRCh38 VCF key that match a ClinVar VariationID for the
                        gene (key: chrom:pos:ref:alt from ClinVar's VCF columns).
                        Denominator: distinct normalized extracted variants.
                        Variants VariantValidator could not place (protein-only,
                        not normalized) are counted and listed, not matched.
  classification        ClinVar aggregate germline classification of matched
                        variants, cross-tabulated with the authors' stated
                        pathogenicity (all papers' statements for the variant,
                        summarised as P/LP, VUS, mixed, other wording, or none).
  condition             matched variants whose ClinVar conditions include the
                        disease IDs given (OMIM:616744 / MONDO:0800045).
  phenotype             observed HPO terms in the run's phenopackets against the
                        HPO annotations for the disease (phenotype.hpoa).
                        Matching rule: an extracted term matches when it is an
                        annotated term or a descendant of one (is_a closure,
                        hp.obo pinned by the run). Precision over
                        individual x term pairs and over distinct terms;
                        recall over annotated terms (an annotated term is
                        recalled when at least one individual has it or a
                        descendant).
  gap candidates        normalized extracted variants with no ClinVar record.
                        OMIM is not checked (no access), so these are ClinVar
                        gaps only.
Every measure is also given two ways for D-19: without papers that entered
the corpus only through ClinVar citations (a variant or individual counts as
"non-seeded" when at least one of its papers came from another seed source),
and, stricter, without any paper ClinVar cites (at least one of its papers is
not ClinVar-cited). Gap candidates get a scripted pre-triage that compares
the protein change the papers state with the one VariantValidator predicts
from the normalized cDNA: agreeing means the normalization is consistent with
the paper ("ClinVar absent (candidate)"); a difference or no stated protein
means "check". The final triage is by hand (miss_triage.csv).

Writes to --out (default analysis/poc):
  concordance_<run_id>.json, concordance_variants_<run_id>.csv,
  gap_candidates_<run_id>.csv

  uv run python -m pipeline.harness.concordance --disease ha20 --run-id poc-ha20-run-2 \
      --snapshot /home/user/gp-rarelink-reference/2026-10-19 --disease-id OMIM:616744 --disease-id MONDO:0800045
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, cdna_of, clean, is_gene, protein_key, transcript_of, v
from pipeline.harness.snapshot_reference import classify, names_any


def wilson(k: int, n: int, z: float = 1.959964) -> dict:
    if n == 0:
        return {"k": k, "n": n, "share": None, "ci95": None}
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return {"k": k, "n": n, "share": round(p, 6), "ci95": [round(max(0.0, c - h), 6), round(min(1.0, c + h), 6)]}


def author_class(s: str) -> str:
    t = s.lower()
    if t in ("", "not reported"):
        return "none"
    if "uncertain" in t or "vus" in t or "unknown significance" in t:
        return "VUS"
    if "benign" in t:
        return "B/LB"
    if "pathogenic" in t:
        return "P/LP"
    return "other wording"


def summarise(classes: set[str]) -> str:
    stated = classes - {"none"}
    if not stated:
        return "not stated"
    if "P/LP" in stated and "VUS" in stated:
        return "mixed P/LP and VUS"
    for c in ("P/LP", "VUS", "B/LB"):
        if c in stated:
            return c
    return "other wording only"


AA3 = {"Ala": "A", "Arg": "R", "Asn": "N", "Asp": "D", "Cys": "C", "Gln": "Q", "Glu": "E", "Gly": "G", "His": "H", "Ile": "I",
       "Leu": "L", "Lys": "K", "Met": "M", "Phe": "F", "Pro": "P", "Ser": "S", "Thr": "T", "Trp": "W", "Tyr": "Y", "Val": "V",
       "Ter": "*", "Sec": "U"}


def protein_short(p: str) -> str:
    """'NP_..:p.(Leu227Ter)' or 'p.L227X' -> 'L227*' (fs and extensions cut after the first residue and position)."""
    s = p.split(":")[-1].replace("p.", "").replace("(", "").replace(")", "").strip()
    for k3, k1 in AA3.items():
        s = s.replace(k3, k1)
    s = s.replace("X", "*").replace("Ter", "*")
    m = re.match(r"^([A-Z*])(\d+)(.*)$", s)
    if not m:
        return s
    rest = m.group(3)
    if "fs" in rest or "ext" in rest or "del" in rest or "dup" in rest or "ins" in rest:
        return f"{m.group(1)}{m.group(2)}{'fs' if 'fs' in rest else rest[:3]}"
    return f"{m.group(1)}{m.group(2)}{rest}"


def protein_check(stated: set[str], predicted: str) -> str:
    stated = {protein_short(x) for x in stated if x}
    if not stated:
        return "no stated protein"
    pred = protein_short(predicted)
    return "agrees" if pred in stated else f"differs (stated {'/'.join(sorted(stated))}, predicted {pred})"


def load_obo_parents(path: Path) -> dict[str, set[str]]:
    parents, cur = defaultdict(set), None
    for line in path.open():
        line = line.strip()
        if line == "[Term]":
            cur = None
        elif line.startswith("id: HP:"):
            cur = line[4:]
        elif cur and line.startswith("is_a: "):
            parents[cur].add(line[6:].split()[0])
        elif cur and line.startswith("alt_id: "):
            parents.setdefault(line[8:], set()).add(cur)  # an alt id points at its primary term
    return parents


def ancestors_or_self(term: str, parents: dict[str, set[str]], cache: dict) -> set[str]:
    if term in cache:
        return cache[term]
    out, stack = {term}, [term]
    while stack:
        for p in parents.get(stack.pop(), ()):
            if p not in out:
                out.add(p)
                stack.append(p)
    cache[term] = out
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    ap.add_argument("--gene-id", default="7128")
    ap.add_argument("--disease-id", action="append", required=True)
    ap.add_argument("--hp-obo", default="data/ontologies/2026-10-19/hp.obo")
    ap.add_argument("--out", default="analysis/poc")
    args = ap.parse_args(argv)
    run = Path("data/extracted") / args.disease / args.run_id
    snap = Path(args.snapshot)
    snap_manifest = json.loads((snap / "MANIFEST.json").read_text())
    snap_date = snap_manifest["date"]
    dis = set(args.disease_id)

    # papers seeded only from ClinVar citations (D-19)
    manifest = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / args.disease / "manifest.csv").open())}
    seed_only = {p for p, r in manifest.items() if {s.strip() for s in r["seed_sources"].split(";") if s.strip()} == {"clinvar_citations"}}
    cited = {p for p, r in manifest.items() if "clinvar_citations" in r["seed_sources"]}

    # ClinVar records for the gene, GRCh38, by VCF key
    rows = list(csv.DictReader((l.lstrip("#") if i == 0 else l for i, l in enumerate((snap / "clinvar" / f"variant_summary_{args.gene}.tsv").open(encoding="utf-8"))), delimiter="\t"))
    clinvar = {}
    for r in rows:
        if r["Assembly"] != "GRCh38" or r["PositionVCF"] in ("", "-1", "na"):
            continue
        key = f"{r['Chromosome']}:{r['PositionVCF']}:{r['ReferenceAlleleVCF']}:{r['AlternateAlleleVCF']}"
        clinvar.setdefault(key, r)

    # authors' pathogenicity per variant key (same key as normalize_variants.py) and spans for gap listing
    authors, spans = defaultdict(set), defaultdict(list)
    for p in sorted((run / "per_paper").glob("*.json")):
        for r in (json.loads(p.read_text()).get("tables") or {}).get("variants") or []:
            if not is_gene(v(r.get("gene_symbol_as_stated")), args.gene) or v(r.get("variant_original_string")) in MISSING:
                continue
            orig = str(v(r.get("variant_original_string")))
            (cdna, _), tx = cdna_of(r), transcript_of(r)
            prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
            key = f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"
            authors[key].add(author_class(str(v(r.get("pathogenicity_as_stated_by_authors")) or "")))
            sp = (r.get("variant_original_string") or {}).get("span")
            if len(spans[key]) < 3:
                spans[key].append(f"PMID:{p.stem}: {sp if isinstance(sp, str) else ' | '.join(sp or [])}")

    # distinct extracted variants, collapsed to normalized VCF keys
    by_vcf: dict[str, dict] = {}
    unplaced = Counter()
    for r in csv.DictReader((run / "variants_normalized.csv").open()):
        if not r["vcf_grch38"]:
            unplaced[r["status"]] += 1
            continue
        d = by_vcf.setdefault(r["vcf_grch38"], {"variant_keys": [], "pmids": set(), "authors": set(), "spans": [], "flags": set(),
                                                 "hgvs_c": r["mane_hgvs_transcript"] or r["hgvs_transcript"],
                                                 "hgvs_p": r["mane_hgvs_protein"] or r["hgvs_protein"]})
        d["variant_keys"].append(r["variant_key"])
        d.setdefault("stated_protein", set()).update(x for x in r["variant_key"].split("|")[2].split("p.")[1:] and
                                                     ["p." + y for y in r["variant_key"].split("|")[2].split("p.")[1:]])
        if r["transcript_assumed"]:
            d["flags"].add(f"transcript assumed ({r['transcript_assumed']})")
        if r["legacy_notation_rewritten"]:
            d["flags"].add("legacy notation rewritten")
        if r["status"] == "corrected":
            d["flags"].add("corrected by VariantValidator")
        if r["query_corrected_from"]:
            d["flags"].add("query typo corrected")
        d["pmids"].update(r["pmids"].split())
        d["authors"] |= authors.get(r["variant_key"], set())
        d["spans"] += spans.get(r["variant_key"], [])

    out_rows, cross = [], defaultdict(Counter)
    for key, d in sorted(by_vcf.items()):
        cv = clinvar.get(key)
        non_seeded = bool(d["pmids"] - seed_only)
        non_cited = bool(d["pmids"] - cited)
        row = {"vcf_grch38": key, "hgvs_c": d["hgvs_c"], "hgvs_p": d["hgvs_p"], "pmids": " ".join(sorted(d["pmids"])),
               "non_seeded": non_seeded, "non_clinvar_cited": non_cited, "author_class": summarise(d["authors"]), "in_clinvar": bool(cv),
               "clinvar_variation_id": cv["VariationID"] if cv else "", "clinvar_name": cv["Name"] if cv else "",
               "clinvar_classification": classify(cv["ClinicalSignificance"]) if cv else "",
               "clinvar_significance_raw": cv["ClinicalSignificance"] if cv else "",
               "clinvar_review_status": cv["ReviewStatus"] if cv else "",
               "clinvar_names_disease": names_any(cv["PhenotypeIDS"], dis) if cv else "",
               "normalization_flags": "; ".join(sorted(d["flags"])),
               "protein_check": protein_check(d.get("stated_protein", set()), d["hgvs_p"]),
               "pre_triage": "",
               "spans": " || ".join(d["spans"][:3])}
        if not cv:
            pc = row["protein_check"]
            row["pre_triage"] = ("ClinVar absent (candidate)" if pc == "agrees" else
                                 "check: no stated protein to confirm the normalization" if pc == "no stated protein" else
                                 "check: stated protein differs from the normalized cDNA")
        out_rows.append(row)
        if cv:
            cross[row["clinvar_classification"]][row["author_class"]] += 1

    def block(rows_):
        n = len(rows_)
        matched = [r for r in rows_ if r["in_clinvar"]]
        plp = [r for r in matched if r["clinvar_classification"] in ("P", "LP", "P/LP")]
        auth_plp = [r for r in matched if r["author_class"] == "P/LP"]
        return {"distinct_normalized_variants": n,
                "variant_presence": wilson(len(matched), n),
                "matched_clinvar_plp": wilson(len(plp), len(matched)),
                "author_plp_with_clinvar_plp": wilson(sum(r["clinvar_classification"] in ("P", "LP", "P/LP") for r in auth_plp), len(auth_plp)),
                "condition_names_disease": wilson(sum(bool(r["clinvar_names_disease"]) for r in matched), len(matched)),
                "gap_candidates": n - len(matched)}

    # phenotype concordance on the run's phenopackets
    annotated = set()
    for hp in (snap / "hpo").glob("*.hpoa"):
        for l in hp.open():
            if l.startswith("#") or l.startswith("database_id"):
                continue
            f = l.rstrip("\n").split("\t")
            if f[0] in dis and f[2] != "NOT" and f[10] == "P":
                annotated.add(f[3])
    parents, cache = load_obo_parents(Path(args.hp_obo)), {}
    pairs = []
    for p in sorted((run / "phenopackets").glob("*.json")):
        pp = json.loads(p.read_text())
        pm = {x["id"].split(":", 1)[1] for x in pp.get("metaData", {}).get("externalReferences", []) if x.get("id", "").startswith("PMID:")}
        for f in pp.get("phenotypicFeatures", []):
            if f.get("excluded"):
                continue
            t = f["type"]["id"]
            anc = ancestors_or_self(t, parents, cache)
            pairs.append({"individual": pp["subject"]["id"], "term": t, "matched": bool(anc & annotated),
                          "recalls": anc & annotated, "non_seeded": bool(pm - seed_only), "non_cited": bool(pm - cited)})

    def pheno(ps):
        distinct = {}
        for x in ps:
            distinct.setdefault(x["term"], x["matched"])
        recalled = set().union(*[x["recalls"] for x in ps]) if ps else set()
        return {"individuals_with_observed_terms": len({x["individual"] for x in ps}),
                "pair_precision": wilson(sum(x["matched"] for x in ps), len(ps)),
                "distinct_term_precision": wilson(sum(distinct.values()), len(distinct)),
                "annotation_recall": wilson(len(recalled), len(annotated)),
                "annotated_terms_not_recalled": sorted(annotated - recalled)}

    summary = {"run_id": args.run_id, "snapshot_date": snap_date,
               "clinvar_release_last_modified": snap_manifest["files"]["variant_summary"]["last_modified"],
               "hpoa_version": next((h for h in snap_manifest["files"]["phenotype_hpoa"].get("header", []) if h.startswith("#version")), ""),
               "disease_ids": sorted(dis), "omim": "not checked (no access in place)",
               "clinvar_gene_records_grch38_with_vcf": len(clinvar),
               "extracted_variants_not_placed_by_variantvalidator": dict(unplaced),
               "all_papers": block(out_rows),
               "without_clinvar_seeded_papers_D19": block([r for r in out_rows if r["non_seeded"]]),
               "without_any_clinvar_cited_paper_D19": block([r for r in out_rows if r["non_clinvar_cited"]]),
               "papers": {"seed_only_clinvar": len(seed_only & set(p.stem for p in (run / "per_paper").glob("*.json"))),
                          "clinvar_cited": len(cited & set(p.stem for p in (run / "per_paper").glob("*.json"))),
                          "in_run": len(list((run / "per_paper").glob("*.json")))},
               "classification_crosstab_rows_clinvar_cols_authors": {k: dict(c) for k, c in sorted(cross.items())},
               "phenotype": {"annotated_terms": len(annotated), "matching_rule": "extracted term equals or descends from an annotated term (is_a)",
                             "all_papers": pheno(pairs), "without_clinvar_seeded_papers_D19": pheno([x for x in pairs if x["non_seeded"]]),
                             "without_any_clinvar_cited_paper_D19": pheno([x for x in pairs if x["non_cited"]])},
               "intervals": "Wilson 95%"}
    out = Path(args.out)
    with (out / f"concordance_variants_{args.run_id}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()))
        w.writeheader()
        w.writerows(out_rows)
    with (out / f"gap_candidates_{args.run_id}.csv").open("w", newline="") as fh:
        gaps = [{k: r[k] for k in ("vcf_grch38", "hgvs_c", "hgvs_p", "pmids", "non_seeded", "non_clinvar_cited", "author_class",
                                   "normalization_flags", "protein_check", "pre_triage", "spans")} | {"snapshot_date": snap_date}
                for r in out_rows if not r["in_clinvar"]]
        w = csv.DictWriter(fh, fieldnames=list(gaps[0].keys()) if gaps else ["vcf_grch38"])
        w.writeheader()
        w.writerows(gaps)
    (out / f"concordance_{args.run_id}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("snapshot_date", "papers", "extracted_variants_not_placed_by_variantvalidator", "all_papers",
                                               "without_any_clinvar_cited_paper_D19")}, indent=2))
    print(json.dumps(Counter(g["pre_triage"] for g in gaps)))
    print(json.dumps({k: v_ for k, v_ in summary["phenotype"]["all_papers"].items()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
