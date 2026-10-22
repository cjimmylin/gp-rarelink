"""Stage 6 steps 5-6 (Q7, D-30): recall of the Chen 2020 Table S1 variants, and patient counts per source paper.

Benchmark (D-30): Chen et al. 2020 Table S1, transcribed by benchmark_chen2020.py
into <snapshot>/benchmarks/chen2020_tableS1.csv: 39 families, 89 patients,
each family with a protein change and its source paper(s). Variants are
compared at protein level, because the table prints protein changes only:
residue and position, plus the consequence (missense residue, "*" for a stop,
"fs" for a frameshift); exon deletions by their exon range.

An extracted TNFAIP3 variant row of run-2 yields protein keys from the
protein the paper states (protein field or the original string) and from the
protein VariantValidator predicts for its normalized cDNA.

Recall (Wilson 95%), as POC_DESIGN.md Stage 6 step 5 defines it:
  restricted (the gated figure)  denominator: benchmark variants with at least
      one source paper among the run's papers; numerator: those found in rows
      from primary papers (not reviews, and not Chen 2020 itself);
  restricted, found in a source paper  stricter: found in the rows of one of
      that variant's own source papers;
  unrestricted   denominator: all benchmark variants; primary-paper rows;
  review-inclusive  denominator restricted; any paper's rows, reviews and
      Chen 2020 included (labelled; the benchmark table itself was extracted).
Q7 gate: restricted recall >= 80%.

Catalogues (pre-registration §7.2.7):
  chen2020    HA20, Chen et al. 2020 Table S1 (D-30); one row per family; protein level.
  grossi2024  AxD, Grossi et al. 2024 Suppl. Table 2 (D-39), transcribed by
              catalogue_grossi2024.py into <snapshot>/catalogues/grossi2024_axd_table2.csv;
              one row per patient; printed at protein and cDNA level. The unit is the
              distinct protein change (the cDNA where no protein is printed). A variant
              counts as found if either level matches: protein key, or cDNA (as stated,
              or as normalized on the gene's MANE transcript); each level's recall is
              also reported alone. The table's genomic column is not used: checked
              against VariantValidator, its alleles are on the coding strand and most
              positions are one off (genomic_column_check in the output). Rows whose
              source is "patient from internal database" (unpublished) or not a PMID
              are counted apart: a variant with no published source is outside both
              denominators.

Step 6 (dedup check): for each source paper in the run, the benchmark's
patient count against the run's individuals from that paper who carry a
TNFAIP3 variant row.

  uv run python -m pipeline.harness.completeness --disease ha20 --run-id poc-ha20-run-2 \
      --snapshot /home/user/gp-rarelink-reference/2026-10-19
  uv run python -m pipeline.harness.completeness --disease axd --run-id pv1-axd --catalogue grossi2024 \
      --snapshot /home/user/gp-rarelink-reference/2026-10-20 --out analysis/six_disease
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, cdna_of, clean, is_gene, protein_key, transcript_of, v
from pipeline.harness.concordance import protein_short, wilson

CATALOGUE_PMID = {"chen2020": "33101300", "grossi2024": "39420046"}
CATALOGUE_NAME = {"chen2020": "Chen 2020 Table S1 (D-30)", "grossi2024": "Grossi 2024 Suppl. Table 2 (D-39)"}
EXON_DEL = re.compile(r"(?:deletion|del)\w*\s+of\s+exons?\s*(\d+)\s*(?:[-–~]|to)\s*(\d+)|exons?\s*(\d+)\s*(?:[-–~]|to)\s*(\d+)\s*(?:deletion|del)", re.I)
PMID = re.compile(r"^\d{6,9}$")


def row_keys(r: dict, predicted: dict[str, str]) -> set[str]:
    """Protein-level keys of an extracted variant row (stated protein, original string, VariantValidator prediction, exon deletions)."""
    keys = set()
    orig = str(v(r.get("variant_original_string")) or "")
    for s in (v(r.get("protein_hgvs_as_stated")), protein_key(orig)):
        if s and s not in MISSING:
            keys.add(protein_short(str(s)))
    vkey = variant_key(r)
    if predicted.get(vkey):
        keys.add(protein_short(predicted[vkey]))
    m = EXON_DEL.search(orig)
    if m:
        a, b = [x for x in m.groups() if x][:2]
        keys.add(f"del ex{a}-{b}")
    return {k for k in keys if k}


def variant_key(r: dict) -> str:
    """The key normalize_variants.py gives a row in variants_normalized.csv."""
    orig = str(v(r.get("variant_original_string")) or "")
    (cdna, _), tx = cdna_of(r), transcript_of(r)
    prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
    return f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"


def cdna_short(c: str) -> str:
    """'NM_002055.5:c.250G>A' or '250G>A' -> 'c.250G>A'."""
    c = clean(c).split(":")[-1]
    return c if c.startswith("c.") else f"c.{c}"


def vcf_key(chrom_pos: str, ref: str, alt: str) -> str:
    cp = clean(chrom_pos).replace("chr", "")
    return f"{cp}:{clean(ref)}:{clean(alt)}" if cp and ref and alt else ""


def load_catalogue(name: str, snap: Path) -> list[dict]:
    """One dict per catalogue row: key, as printed, sources (PMIDs), patients, cdna, vcf, unpublished flag."""
    out = []
    if name == "chen2020":
        for f in csv.DictReader((snap / "benchmarks" / "chen2020_tableS1.csv").open()):
            out.append({"key": f["protein_key"], "printed": f["variant_as_printed"], "group": f["family"],
                        "sources": {x for x in f["ref_pmids"].split(";") if x}, "patients": int(f["n_patients"]),
                        "cdna": "", "vcf": "", "unpublished": False})
    elif name == "grossi2024":
        for i, f in enumerate(csv.DictReader((snap / "catalogues" / "grossi2024_axd_table2.csv").open()), 1):
            prot = clean(f["Protein Description"])
            cdna = cdna_short(f["cDNA description"]) if clean(f["cDNA description"]) else ""
            pkey = protein_short(prot) if prot.startswith("p.") and prot not in ("p.?", "p.=") else ""
            ref = clean(f["Reference (PMID)"])
            out.append({"key": pkey or cdna or prot or f"row{i}", "printed": prot or cdna, "group": f"row{i}",
                        "sources": {ref} if PMID.match(ref) else set(), "patients": 1, "cdna": cdna,
                        "vcf": "",  # genomic column not used (see docstring)
                        "genomic_as_printed": vcf_key(f["Genomic_ Position"], f["REF"], f["ALT"]),
                        "unpublished": not PMID.match(ref), "source_as_printed": ref})
    else:
        raise SystemExit(f"unknown catalogue {name}")
    return out


def genomic_check(cat: list[dict], norm: list[dict]) -> dict:
    """Compare the catalogue's printed genomic allele with VariantValidator's GRCh38 allele for the same cDNA."""
    vv = {}
    for r in norm:
        if r.get("vcf_grch38") and r.get("mane_hgvs_transcript"):
            vv[cdna_short(r["mane_hgvs_transcript"])] = r["vcf_grch38"]
    comp = {"same": 0, "same_position_other_strand": 0, "position_off_by_one": 0, "other": 0}
    seen = set()
    for f in cat:
        g, c = f.get("genomic_as_printed"), f.get("cdna")
        if not g or not c or c not in vv or (c, g) in seen:
            continue
        seen.add((c, g))
        gp, ours = g.split(":"), vv[c].split(":")
        if g == vv[c]:
            comp["same"] += 1
        elif gp[1] == ours[1]:
            comp["same_position_other_strand"] += 1
        elif gp[1].isdigit() and abs(int(gp[1]) - int(ours[1])) == 1:
            comp["position_off_by_one"] += 1
        else:
            comp["other"] += 1
    comp["compared"] = sum(comp.values())
    comp["note"] = "Distinct (cDNA, printed allele) pairs whose cDNA VariantValidator normalized in this run."
    return comp


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--catalogue", default="chen2020", choices=sorted(CATALOGUE_PMID))
    ap.add_argument("--gene", default=None, help="default: the gene in configs/stage4/<disease>.json, else TNFAIP3")
    ap.add_argument("--gate", type=float, default=0.80, help="the pilot's Q7 development gate; descriptive only in the study")
    ap.add_argument("--out", default="analysis/poc")
    args = ap.parse_args(argv)
    gene = args.gene
    if not gene:
        cfg = Path("configs/stage4") / f"{args.disease}.json"
        gene = json.loads(cfg.read_text())["gene"] if cfg.exists() else "TNFAIP3"
    run = Path("data/extracted") / args.disease / args.run_id
    snap = Path(args.snapshot)
    cat = load_catalogue(args.catalogue, snap)
    cat_pmid = CATALOGUE_PMID[args.catalogue]
    manifest = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / args.disease / "manifest.csv").open())}
    papers = sorted(p.stem for p in (run / "per_paper").glob("*.json"))
    norm = list(csv.DictReader((run / "variants_normalized.csv").open()))
    predicted = {r["variant_key"]: r["hgvs_protein"] for r in norm if r["hgvs_protein"]}
    norm_by_key = {r["variant_key"]: r for r in norm}

    found = {"protein": defaultdict(set), "cdna": defaultdict(set), "vcf": defaultdict(set)}  # key -> papers
    carriers = defaultdict(set)  # paper -> labels with a target-gene variant row
    for p in papers:
        for r in (json.loads((run / "per_paper" / f"{p}.json").read_text()).get("tables") or {}).get("variants") or []:
            if not is_gene(v(r.get("gene_symbol_as_stated")), gene):
                continue
            carriers[p].add(str(v(r.get("individual_label_in_paper"))))
            for k in row_keys(r, predicted):
                found["protein"][k].add(p)
            cdna, _ = cdna_of(r)
            nr = norm_by_key.get(variant_key(r)) or {}
            for c in (cdna, nr.get("mane_hgvs_transcript"), nr.get("hgvs_transcript")):
                if c:
                    found["cdna"][cdna_short(c)].add(p)
            if nr.get("vcf_grch38"):
                found["vcf"][nr["vcf_grch38"]].add(p)

    def primary(p: str) -> bool:
        m = manifest.get(p, {})
        return p != cat_pmid and m.get("study_type") != "review/meta-analysis" and m.get("fulltext_study_type") != "review/meta-analysis"

    bench: dict[str, dict] = {}
    for f in cat:
        b = bench.setdefault(f["key"], {"variant_as_printed": f["printed"], "groups": [], "sources": set(), "patients": 0,
                                        "cdna": set(), "vcf": set(), "unpublished_patients": 0})
        b["groups"].append(f["group"])
        b["sources"] |= f["sources"]
        b["patients"] += f["patients"]
        b["unpublished_patients"] += f["patients"] if f["unpublished"] else 0
        if f["cdna"]:
            b["cdna"].add(f["cdna"])
        if f["vcf"]:
            b["vcf"].add(f["vcf"])
    rows = []
    for k, b in sorted(bench.items()):
        in_run = sorted(b["sources"] & set(papers))
        where_by = {"protein": set(found["protein"].get(k, set())),
                    "cdna": set().union(*[found["cdna"].get(c, set()) for c in b["cdna"]]) if b["cdna"] else set(),
                    "vcf": set().union(*[found["vcf"].get(x, set()) for x in b["vcf"]]) if b["vcf"] else set()}
        where = where_by["protein"] | where_by["cdna"] | where_by["vcf"]
        row = {"variant_key": k, "variant_as_printed": b["variant_as_printed"], "groups": ";".join(b["groups"]),
               "catalogue_patients": b["patients"], "unpublished_patients": b["unpublished_patients"],
               "published_source": bool(b["sources"]), "source_pmids": ";".join(sorted(b["sources"])),
               "source_in_run": ";".join(in_run), "restricted": bool(in_run),
               "found_primary": bool({p for p in where if primary(p)}), "found_in_source": bool(where & set(in_run)),
               "found_any_paper": bool(where), "found_in_papers": ";".join(sorted(where))}
        if args.catalogue != "chen2020":
            for lvl in ("protein", "cdna"):
                row[f"found_primary_{lvl}"] = bool({p for p in where_by[lvl] if primary(p)})
            row["catalogue_cdna"] = ";".join(sorted(b["cdna"]))
        rows.append(row)
    published = [r for r in rows if r["published_source"]]
    restricted = [r for r in rows if r["restricted"]]
    summary = {
        "run_id": args.run_id, "disease": args.disease, "gene": gene, "catalogue": CATALOGUE_NAME[args.catalogue],
        "catalogue_pmid": cat_pmid,
        "unit": "distinct protein-level variant" + ("" if args.catalogue == "chen2020" else " (cDNA where no protein is printed)"),
        "benchmark_variants": len(rows), "benchmark_patients": sum(r["catalogue_patients"] for r in rows),
        "restricted_variants": len(restricted),
        "recall_restricted_primary": wilson(sum(r["found_primary"] for r in restricted), len(restricted)),
        "recall_restricted_in_source_paper": wilson(sum(r["found_in_source"] for r in restricted), len(restricted)),
        "recall_unrestricted_primary": wilson(sum(r["found_primary"] for r in published), len(published)),
        "recall_restricted_review_inclusive": wilson(sum(r["found_any_paper"] for r in restricted), len(restricted)),
        "q7_gate": {"threshold": args.gate},
        "missed_restricted": [{k: r[k] for k in ("variant_key", "variant_as_printed", "source_in_run", "found_in_papers")}
                              for r in restricted if not r["found_primary"]],
    }
    if args.catalogue != "chen2020":
        summary["variants_without_published_source"] = len(rows) - len(published)
        summary["patients_without_published_source"] = sum(1 for f in cat if f["unpublished"])
        summary["unpublished_sources_as_printed"] = sorted({f["source_as_printed"] for f in cat if f["unpublished"]})
        summary["note_unrestricted"] = "Unrestricted denominator: catalogue variants with at least one published (PMID) source."
        summary["recall_restricted_primary_by_level"] = {
            lvl: wilson(sum(r[f"found_primary_{lvl}"] for r in restricted), len(restricted)) for lvl in ("protein", "cdna")}
        summary["genomic_column_check"] = genomic_check(cat, norm)
    summary["q7_gate"]["met"] = (summary["recall_restricted_primary"]["share"] or 0) >= args.gate
    if args.catalogue != "chen2020":
        summary["q7_gate"]["note"] = "Development gate from the pilot; descriptive only in the study (§7.2.7)."

    # step 6: patients per source paper
    per_src = defaultdict(int)
    for f in cat:
        for s in f["sources"]:
            per_src[s] += f["patients"]
    dedup = [{"pmid": s, "benchmark_patients": n, "run_carriers": len(carriers.get(s, set())), "in_run": s in papers}
             for s, n in sorted(per_src.items())]
    summary["patients_per_source_paper"] = dedup
    summary["note_patients"] = ("Families citing two papers count in both. 'run_carriers' are individuals from that paper "
                                f"with a {gene} variant row in this run; the paper may also describe relatives or other "
                                "patients that the catalogue did not take.")
    out = Path(args.out)
    with (out / f"completeness_{args.run_id}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / f"completeness_{args.run_id}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k not in ("patients_per_source_paper", "missed_restricted")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
