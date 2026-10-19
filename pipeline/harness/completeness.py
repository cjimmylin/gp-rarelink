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

Step 6 (dedup check): for each source paper in the run, the benchmark's
patient count against the run's individuals from that paper who carry a
TNFAIP3 variant row.

  uv run python -m pipeline.harness.completeness --disease ha20 --run-id poc-ha20-run-2 \
      --snapshot /home/user/gp-rarelink-reference/2026-10-19
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

BENCHMARK_PMID = "33101300"
EXON_DEL = re.compile(r"(?:deletion|del)\w*\s+of\s+exons?\s*(\d+)\s*(?:[-–~]|to)\s*(\d+)|exons?\s*(\d+)\s*(?:[-–~]|to)\s*(\d+)\s*(?:deletion|del)", re.I)


def row_keys(r: dict, predicted: dict[str, str]) -> set[str]:
    keys = set()
    orig = str(v(r.get("variant_original_string")) or "")
    for s in (v(r.get("protein_hgvs_as_stated")), protein_key(orig)):
        if s and s not in MISSING:
            keys.add(protein_short(str(s)))
    (cdna, _), tx = cdna_of(r), transcript_of(r)
    prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
    vkey = f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"
    if predicted.get(vkey):
        keys.add(protein_short(predicted[vkey]))
    m = EXON_DEL.search(orig)
    if m:
        a, b = [x for x in m.groups() if x][:2]
        keys.add(f"del ex{a}-{b}")
    return {k for k in keys if k}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    ap.add_argument("--gate", type=float, default=0.80)
    ap.add_argument("--out", default="analysis/poc")
    args = ap.parse_args(argv)
    run = Path("data/extracted") / args.disease / args.run_id
    snap = Path(args.snapshot)
    fams = list(csv.DictReader((snap / "benchmarks" / "chen2020_tableS1.csv").open()))
    manifest = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / args.disease / "manifest.csv").open())}
    papers = sorted(p.stem for p in (run / "per_paper").glob("*.json"))
    predicted = {r["variant_key"]: r["hgvs_protein"] for r in csv.DictReader((run / "variants_normalized.csv").open()) if r["hgvs_protein"]}

    found = defaultdict(set)  # protein key -> papers whose rows give it
    carriers = defaultdict(set)  # paper -> labels with a TNFAIP3 variant row
    for p in papers:
        for r in (json.loads((run / "per_paper" / f"{p}.json").read_text()).get("tables") or {}).get("variants") or []:
            if not is_gene(v(r.get("gene_symbol_as_stated")), args.gene):
                continue
            carriers[p].add(str(v(r.get("individual_label_in_paper"))))
            for k in row_keys(r, predicted):
                found[k].add(p)

    def primary(p: str) -> bool:
        return p != BENCHMARK_PMID and manifest.get(p, {}).get("study_type") != "review/meta-analysis"

    bench = {}
    for f in fams:
        b = bench.setdefault(f["protein_key"], {"variant_as_printed": f["variant_as_printed"], "families": [], "sources": set(), "patients": 0})
        b["families"].append(f["family"])
        b["sources"].update(x for x in f["ref_pmids"].split(";") if x)
        b["patients"] += int(f["n_patients"])
    rows = []
    for k, b in sorted(bench.items()):
        in_run = sorted(b["sources"] & set(papers))
        where = found.get(k, set())
        rows.append({"protein_key": k, "variant_as_printed": b["variant_as_printed"], "families": ";".join(b["families"]),
                     "benchmark_patients": b["patients"], "source_pmids": ";".join(sorted(b["sources"])),
                     "source_in_run": ";".join(in_run), "restricted": bool(in_run),
                     "found_primary": bool({p for p in where if primary(p)}), "found_in_source": bool(where & set(in_run)),
                     "found_any_paper": bool(where), "found_in_papers": ";".join(sorted(where))})
    restricted = [r for r in rows if r["restricted"]]
    summary = {
        "run_id": args.run_id, "benchmark": "Chen 2020 Table S1 (D-30)", "unit": "distinct protein-level variant",
        "benchmark_variants": len(rows), "benchmark_patients": sum(r["benchmark_patients"] for r in rows),
        "restricted_variants": len(restricted),
        "recall_restricted_primary": wilson(sum(r["found_primary"] for r in restricted), len(restricted)),
        "recall_restricted_in_source_paper": wilson(sum(r["found_in_source"] for r in restricted), len(restricted)),
        "recall_unrestricted_primary": wilson(sum(r["found_primary"] for r in rows), len(rows)),
        "recall_restricted_review_inclusive": wilson(sum(r["found_any_paper"] for r in restricted), len(restricted)),
        "q7_gate": {"threshold": args.gate},
        "missed_restricted": [{k: r[k] for k in ("protein_key", "variant_as_printed", "source_in_run", "found_in_papers")}
                              for r in restricted if not r["found_primary"]],
    }
    summary["q7_gate"]["met"] = (summary["recall_restricted_primary"]["share"] or 0) >= args.gate

    # step 6: patients per source paper
    per_src = defaultdict(int)
    for f in fams:
        for s in {x for x in f["ref_pmids"].split(";") if x}:
            per_src[s] += int(f["n_patients"])
    dedup = [{"pmid": s, "benchmark_patients": n, "run_carriers": len(carriers.get(s, set())), "in_run": s in papers}
             for s, n in sorted(per_src.items())]
    summary["patients_per_source_paper"] = dedup
    summary["note_patients"] = ("Families citing two papers count in both. 'run_carriers' are individuals from that paper "
                                "with a TNFAIP3 variant row in this run; the paper may also describe relatives or other "
                                "patients that Chen 2020 did not take.")
    out = Path(args.out)
    with (out / f"completeness_{args.run_id}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    (out / f"completeness_{args.run_id}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "patients_per_source_paper"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
