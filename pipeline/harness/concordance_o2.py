"""O2 concordance for the six-disease runs (pre-registration §7.2; harness side only).

Extends the pilot's harness (pipeline/harness/concordance.py, whose helpers it reuses) to
every registered O2 measure, per disease, from the frozen extraction and the dated
snapshot under the reference root (outside the repo):

  7.2.1 gene              deduplicated identities with a variant row naming a gene: share
                          whose genes include the disease's gene (near ceiling by design).
  7.2.2 normalized HGVS   reference pairs (PMID, VariationID) from ClinVar's citation table
                          for the gene, restricted to the run's PMIDs. Recall: share of pairs
                          where the run extracted the same variant from that PMID, tier 1
                          (same GRCh38 VCF allele) and tiers 1+2 (or the same protein change,
                          for papers giving no placeable c./g. description). Pairs whose
                          ClinVar record has no GRCh38 VCF allele are counted apart.
                          Normalization success is taken from normalization_summary.json.
                          Overlap (not precision): share of distinct extracted variants found
                          in ClinVar, tier 1, and tier 2 for protein-only descriptions.
                          OMIM allelic-variant references: not available (no OMIM access, D-12).
  7.2.3 classification    matched variants: authors' stated class (P/LP, VUS, B/LB, not stated)
                          against ClinVar's aggregate germline class collapsed the same way,
                          conflicting counted as VUS. Confusion matrix and percent agreement
                          among stated values.
  7.2.4 phenotype         (a) matched variants whose ClinVar condition names the disease (OMIM or
                          Mondo ID). (b) phenotype.hpoa terms for the disease observed in at
                          least one extracted individual (term or descendant); and the share of
                          terms observed in >= 2 deduplicated individuals that match an
                          annotated term (D-35).
  7.2.5 overlap/coverage  share of the run's PMIDs ClinVar cites for the gene; per-field share
                          of rows with an asserted value.
  D-19                    every variant figure again without ClinVar-cited papers: a variant
                          counts when at least one of its PMIDs is not cited by ClinVar for the
                          gene (seed tags count as cited too).
Wilson 95% intervals. Misses (reference pairs not recalled at tiers 1+2) are written out per
disease; --triage-sample draws the §7.2.6 sample of 50 (seeded) across all six.

  uv run python -m pipeline.harness.concordance_o2 --snapshot /home/user/gp-rarelink-reference/2026-10-19
  uv run python -m pipeline.harness.concordance_o2 --snapshot ... --triage-sample --seed 72650
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import re
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, cdna_of, clean, is_gene, protein_key, transcript_of, v
from pipeline.harness.concordance import ancestors_or_self, author_class, load_obo_parents, wilson
from pipeline.harness.snapshot_reference import classify, names_any

DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
NAME_PROT = re.compile(r"\(p\.([^)]+)\)")


def collapse_clinvar(c: str) -> str:
    if c in ("P", "LP", "P/LP"):
        return "P/LP"
    if c in ("VUS", "conflicting"):
        return "VUS"
    if c in ("B", "LB", "B/LB"):
        return "B/LB"
    return "other"


def collapse_authors(classes: set[str]) -> str:
    stated = classes - {"none", "other wording"}
    if not stated:
        return "not stated"
    if len(stated) > 1:
        return "mixed"
    return next(iter(stated))


def variant_key(r: dict) -> str:
    orig = str(v(r.get("variant_original_string")))
    (cdna, _), tx = cdna_of(r), transcript_of(r)
    prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
    return f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"


def one(disease: str, snap: Path, hp_parents, cache) -> tuple[dict, list[dict], list[dict]]:
    cfg = json.loads(Path(f"configs/stage4/{disease}.json").read_text())
    gene = cfg["gene"]
    run = Path(f"data/extracted/{disease}/pv1-{disease}")
    man_path = snap / (f"MANIFEST_{gene}.json" if (snap / f"MANIFEST_{gene}.json").exists() else "MANIFEST.json")
    sman = json.loads(man_path.read_text())
    if sman.get("gene", gene) != gene:
        raise SystemExit(f"{man_path} is for {sman.get('gene')}, not {gene}")
    dis = set(sman["disease_ids"])
    run_pmids = {p.stem for p in (run / "per_paper").glob("*.json")}

    # ClinVar records for the gene (GRCh38)
    vs = list(csv.DictReader((l.lstrip("#") if i == 0 else l for i, l in enumerate((snap / "clinvar" / f"variant_summary_{gene}.tsv").open(encoding="utf-8"))), delimiter="\t"))
    by_vcf, by_vid = {}, {}
    for r in vs:
        if r["Assembly"] != "GRCh38":
            continue
        key = "" if r["PositionVCF"] in ("", "-1", "na") else f"{r['Chromosome']}:{r['PositionVCF']}:{r['ReferenceAlleleVCF']}:{r['AlternateAlleleVCF']}"
        m = NAME_PROT.search(r["Name"])
        prot = protein_key("p." + m.group(1)) if m else None
        by_vid.setdefault(r["VariationID"], {"vcf": key, "protein": prot, "row": r})
        if key:
            by_vcf.setdefault(key, r)
    prot_index = defaultdict(set)
    for vid, x in by_vid.items():
        if x["protein"]:
            prot_index[x["protein"]].add(vid)

    # ClinVar citations for the gene
    cites = defaultdict(set)
    for l in (snap / "clinvar" / f"var_citations_{gene}.tsv").open(encoding="utf-8"):
        if l.startswith("#"):
            continue
        f = l.rstrip("\n").split("\t")
        if len(f) > 5 and f[4] == "PubMed" and f[1] in by_vid:
            cites[f[5]].add(f[1])
    lit = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / disease / "manifest.csv").open())}
    cited_pmids = {p for p in run_pmids if p in cites} | {p for p in run_pmids if "clinvar_citations" in (lit.get(p, {}).get("seed_sources") or "")}

    # extracted: normalized keys, per-PMID alleles and proteins, authors' classes
    norm = {r["variant_key"]: r for r in csv.DictReader((run / "variants_normalized.csv").open())}
    per_pmid_vcf, per_pmid_prot = defaultdict(set), defaultdict(set)
    vcf_info = defaultdict(lambda: {"pmids": set(), "authors": set(), "hgvs_c": "", "hgvs_p": ""})
    protonly_info = defaultdict(lambda: {"pmids": set(), "authors": set()})
    gene_of_label = defaultdict(set)
    for p in sorted(run_pmids):
        t = json.loads((run / "per_paper" / f"{p}.json").read_text()).get("tables") or {}
        for r in t.get("variants") or []:
            g = v(r.get("gene_symbol_as_stated"))
            if g not in MISSING:
                gene_of_label[(p, str(v(r.get("individual_label_in_paper"))))].add("target" if is_gene(g, gene) else "other")
            if not is_gene(g, gene) or v(r.get("variant_original_string")) in MISSING:
                continue
            k = variant_key(r)
            n = norm.get(k, {})
            ac = author_class(str(v(r.get("pathogenicity_as_stated_by_authors")) or ""))
            pk = k.split("|")[2] or None
            if pk:
                per_pmid_prot[p].add(pk)
            if n.get("vcf_grch38"):
                per_pmid_vcf[p].add(n["vcf_grch38"])
                d = vcf_info[n["vcf_grch38"]]
                d["pmids"].add(p); d["authors"].add(ac)
                d["hgvs_c"] = d["hgvs_c"] or n.get("mane_hgvs_transcript") or n.get("hgvs_transcript", "")
                d["hgvs_p"] = d["hgvs_p"] or n.get("mane_hgvs_protein") or n.get("hgvs_protein", "")
            elif pk:
                d = protonly_info[pk]
                d["pmids"].add(p); d["authors"].add(ac)

    def keep(pmids: set[str], mode: str) -> bool:
        return True if mode == "all" else bool(pmids - cited_pmids)

    variants_out = []
    for key, d in sorted(vcf_info.items()):
        cv = by_vcf.get(key)
        variants_out.append({"disease": disease, "tier": "1" if cv else "unmatched", "allele_or_protein": key, "hgvs_c": d["hgvs_c"], "hgvs_p": d["hgvs_p"],
                             "pmids": " ".join(sorted(d["pmids"])), "author_class": collapse_authors(d["authors"]),
                             "clinvar_variation_id": cv["VariationID"] if cv else "", "clinvar_class": classify(cv["ClinicalSignificance"]) if cv else "",
                             "clinvar_names_disease": names_any(cv["PhenotypeIDS"], dis) if cv else "", "non_cited": bool(d["pmids"] - cited_pmids)})
    for pk, d in sorted(protonly_info.items()):
        vids = prot_index.get(pk, set())
        cv = by_vid[sorted(vids)[0]]["row"] if vids else None
        variants_out.append({"disease": disease, "tier": "2" if cv else "unmatched_protein_only", "allele_or_protein": pk, "hgvs_c": "", "hgvs_p": pk,
                             "pmids": " ".join(sorted(d["pmids"])), "author_class": collapse_authors(d["authors"]),
                             "clinvar_variation_id": " ".join(sorted(vids)), "clinvar_class": classify(cv["ClinicalSignificance"]) if cv else "",
                             "clinvar_names_disease": names_any(cv["PhenotypeIDS"], dis) if cv else "", "non_cited": bool(d["pmids"] - cited_pmids)})

    # 7.2.2 recall over (PMID, VariationID) reference pairs
    pairs, misses = [], []
    for p in sorted(run_pmids):
        for vid in sorted(cites.get(p, ())):
            x = by_vid[vid]
            t1 = bool(x["vcf"]) and x["vcf"] in per_pmid_vcf[p]
            t2 = (not t1) and bool(x["protein"]) and x["protein"] in per_pmid_prot[p]
            pairs.append({"pmid": p, "vid": vid, "placeable": bool(x["vcf"]), "t1": t1, "t12": t1 or t2})
            if not (t1 or t2):
                misses.append({"disease": disease, "pmid": p, "clinvar_variation_id": vid, "clinvar_name": x["row"]["Name"],
                               "clinvar_vcf": x["vcf"], "extracted_alleles_in_pmid": " ".join(sorted(per_pmid_vcf[p])),
                               "extracted_proteins_in_pmid": " ".join(sorted(per_pmid_prot[p]))})

    def var_block(mode: str) -> dict:
        rows = [r for r in variants_out if mode == "all" or r["non_cited"]]
        placed = [r for r in rows if r["tier"] in ("1", "unmatched")]
        prot_only = [r for r in rows if r["tier"] in ("2", "unmatched_protein_only")]
        matched = [r for r in rows if r["tier"] in ("1", "2")]
        stated = [r for r in matched if r["author_class"] in ("P/LP", "VUS", "B/LB")]
        conf = Counter((collapse_clinvar(r["clinvar_class"]), r["author_class"]) for r in matched)
        prs = [x for x in pairs if mode == "all" or x["pmid"] not in cited_pmids]
        return {"overlap_tier1": wilson(sum(r["tier"] == "1" for r in placed), len(placed)),
                "overlap_tier2_protein_only": wilson(sum(r["tier"] == "2" for r in prot_only), len(prot_only)),
                "classification_agreement_among_stated": wilson(sum(collapse_clinvar(r["clinvar_class"]) == r["author_class"] for r in stated), len(stated)),
                "classification_confusion_clinvar_x_authors": {f"{a} | {b}": n for (a, b), n in sorted(conf.items())},
                "condition_names_disease": wilson(sum(bool(r["clinvar_names_disease"]) for r in matched), len(matched)),
                "reference_pairs": len(prs), "reference_pairs_unplaceable_in_clinvar": sum(not x["placeable"] for x in prs),
                "hgvs_recall_tier1": wilson(sum(x["t1"] for x in prs), len(prs)),
                "hgvs_recall_tier12": wilson(sum(x["t12"] for x in prs), len(prs)),
                "gap_candidates_tier1_unmatched": sum(r["tier"] == "unmatched" for r in rows)}

    # 7.2.1 gene, per deduplicated identity
    ident = defaultdict(set)
    for r in csv.DictReader((run / "individuals_reconciled.csv").open()):
        ident[r["identity"]] |= gene_of_label.get((r["pmid"], r["individual_label_in_paper"]), set())
    with_gene = [s for s in ident.values() if s]
    # 7.2.4 (b) phenotype profile
    annotated = set()
    for hp in (snap / "hpo").glob("*.hpoa"):
        for l in hp.open():
            if l.startswith("#") or l.startswith("database_id"):
                continue
            f = l.rstrip("\n").split("\t")
            if f[0] in dis and f[2] != "NOT" and f[10] == "P":
                annotated.add(f[3])
    term_people = defaultdict(set)
    for pth in (run / "phenopackets").glob("*.json"):
        pp = json.loads(pth.read_text())
        for f in pp.get("phenotypicFeatures", []):
            if not f.get("excluded"):
                term_people[f["type"]["id"]].add(pp["subject"]["id"])
    recalled = set()
    for t in term_people:
        recalled |= ancestors_or_self(t, hp_parents, cache) & annotated
    two = [t for t, ppl in term_people.items() if len(ppl) >= 2]
    # 7.2.5 coverage per field
    cov = defaultdict(lambda: [0, 0])
    for p in run_pmids:
        t = json.loads((run / "per_paper" / f"{p}.json").read_text()).get("tables") or {}
        for tab, rows in t.items():
            for r in rows or []:
                for fld, cell in r.items():
                    if isinstance(cell, dict) and "value" in cell:
                        cov[f"{tab}.{fld}"][1] += 1
                        cov[f"{tab}.{fld}"][0] += cell.get("value") not in (None, "", "not reported", "unknown", [])
    summary = {"disease": disease, "run_id": f"pv1-{disease}", "gene": gene, "disease_ids": sorted(dis),
               "snapshot_date": sman["date"], "clinvar_variant_summary_last_modified": sman["files"]["variant_summary"]["last_modified"],
               "omim": "not checked (no OMIM access, D-12)",
               "gene_7_2_1": wilson(sum("target" in s for s in with_gene), len(with_gene)),
               "normalization_7_2_2": json.loads((run / "normalization_summary.json").read_text())["status_counts"],
               "all_papers": var_block("all"), "without_clinvar_cited_papers_D19": var_block("non_cited"),
               "phenotype_7_2_4b": {"annotated_terms": len(annotated), "annotation_recall": wilson(len(recalled), len(annotated)),
                                    "terms_in_2plus_individuals_matching_annotation": wilson(sum(bool(ancestors_or_self(t, hp_parents, cache) & annotated) for t in two), len(two))},
               "corpus_overlap_7_2_5": wilson(len(cited_pmids & run_pmids), len(run_pmids)),
               "coverage_7_2_5": {k: round(a / b, 4) for k, (a, b) in sorted(cov.items()) if b},
               "intervals": "Wilson 95%"}
    return summary, variants_out, misses


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--hp-obo", default="data/ontologies/2026-10-19/hp.obo")
    ap.add_argument("--out", default="analysis/six_disease/o2")
    ap.add_argument("--triage-sample", action="store_true")
    ap.add_argument("--seed", type=int)
    a = ap.parse_args(argv)
    snap, out = Path(a.snapshot), Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    parents, cache = load_obo_parents(Path(a.hp_obo)), {}
    allsum, allvar, allmiss = [], [], []
    for d in DISEASES:
        s, vr, ms = one(d, snap, parents, cache)
        allsum.append(s); allvar += vr; allmiss += ms
        (out / f"o2_{d}.json").write_text(json.dumps(s, indent=1) + "\n")
    for name, rows in (("o2_variants.csv", allvar), ("o2_recall_misses.csv", allmiss)):
        with (out / name).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    pct = lambda w: "—" if w["share"] is None else f"{100 * w['share']:.1f}% ({w['k']}/{w['n']}; {100 * w['ci95'][0]:.1f}–{100 * w['ci95'][1]:.1f})"
    L = [f"# O2 concordance, six-disease run (snapshot {allsum[0]['snapshot_date']})", "",
         "*Generated by `pipeline/harness/concordance_o2.py` (pre-registration §7.2). Estimates with Wilson 95% intervals; no pass/fail threshold (D-03). OMIM not checked (D-12). Overlap is not precision; precision comes from the O1 audit.*", "",
         "| Disease | Gene (7.2.1) | HGVS recall, tier 1 | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement | Condition names disease | HPO annotation recall | Terms in ≥2 people matching | PMIDs ClinVar cites |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for s in allsum:
        b = s["all_papers"]
        L.append(f"| {s['disease']} | {pct(s['gene_7_2_1'])} | {pct(b['hgvs_recall_tier1'])} | {pct(b['hgvs_recall_tier12'])} | {pct(b['overlap_tier1'])} | "
                 f"{pct(b['classification_agreement_among_stated'])} | {pct(b['condition_names_disease'])} | {pct(s['phenotype_7_2_4b']['annotation_recall'])} | "
                 f"{pct(s['phenotype_7_2_4b']['terms_in_2plus_individuals_matching_annotation'])} | {pct(s['corpus_overlap_7_2_5'])} |")
    L += ["", "## Without ClinVar-cited papers (D-19)", "", "| Disease | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement |", "|---|---|---|---|"]
    for s in allsum:
        b = s["without_clinvar_cited_papers_D19"]
        L.append(f"| {s['disease']} | {pct(b['hgvs_recall_tier12'])} | {pct(b['overlap_tier1'])} | {pct(b['classification_agreement_among_stated'])} |")
    (out / "o2_summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    if a.triage_sample:
        if a.seed is None:
            raise SystemExit("--triage-sample needs --seed")
        dest = Path("adjudication/o2_triage")
        if (dest / "sample_key.json").exists():
            raise SystemExit("triage sample already drawn")
        rng = random.Random(a.seed)
        pick = sorted(rng.sample(range(len(allmiss)), min(50, len(allmiss))))
        dest.mkdir(parents=True, exist_ok=True)
        rows = [{"n": i + 1, **allmiss[j], "category (1 extraction / 2 normalization / 3 paper / 4 reference / 5 citation not about variant)": "", "note": ""}
                for i, j in enumerate(pick)]
        with (dest / "sample.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
        (dest / "sample_key.json").write_text(json.dumps({"seed": a.seed, "misses": len(allmiss), "drawn": len(rows),
                                                          "by_disease": dict(Counter(r["disease"] for r in rows))}, indent=1) + "\n")
        print(f"triage sample: {len(rows)} of {len(allmiss)} misses")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
