"""Counts for one extraction run (POC_DESIGN.md Stage 3, checks 1, 3 and 4).

Reads data/extracted/<disease>/<run_id>/per_paper/*.json, the run manifest's
document list (runs/<run_id>/manifest.json) and, if present, the reconciliation
summary written by pipeline.extract.reconcile. Reports:

  - papers expected, processed and missing;
  - papers flagged as reporting individuals with a TNFAIP3 variant, and papers
    flagged true but with no individual rows;
  - individuals, split into those described first-hand and those taken from a
    table or summary of previously published cases (source_reference_in_review);
  - variant rows by gene, TNFAIP3 rows with a printed variant (D-22: rows
    without one are kept but left out of variant counts and concordance),
    distinct TNFAIP3 variant strings, variant rows without an original string;
  - TNFAIP3 variant rows by inheritance, and "de novo" rows with no parental
    testing statement (rule 8 says de novo needs stated parental testing);
  - phenotypic_features by status and evidence basis; checklist cells by status
    and evidence basis; individuals whose checklist is incomplete (check 4);
  - individuals before and after merging, by confidence label (from reconcile).

Writes analysis/poc/extraction_counts_<run_id>.json and prints it.

  uv run python analysis/poc/extraction_counts.py --disease ha20 --run-id poc-ha20-run-1
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path

from pipeline.extract.reconcile import is_gene

MISSING = {None, "", "not reported"}
WS = re.compile(r"\s+")


def v(cell):
    return (cell or {}).get("value")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    ap.add_argument("--checklist-size", type=int, default=20)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    manifest_path = Path("runs") / args.run_id / "manifest.json"
    expected = []
    if manifest_path.exists():
        expected = [str(x) for x in json.loads(manifest_path.read_text()).get("notes", {}).get("documents", [])]
    papers = {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "per_paper").glob("*.json"))}
    gene = args.gene.upper()

    c: Counter = Counter()
    distinct_variants: set[str] = set()
    flagged_true_no_rows, incomplete_checklist, no_original_string, de_novo_without_testing = [], [], [], []
    for pmid, doc in papers.items():
        t = doc.get("tables") or {}
        flag = doc.get("reports_individuals_with_tnfaip3_variant")
        c[f"papers_flag_{str(flag).lower()}"] += 1
        inds = t.get("individuals") or []
        if flag is True and not inds:
            flagged_true_no_rows.append(pmid)
        if inds:
            c["papers_with_individual_rows"] += 1
        for r in inds:
            c["individuals"] += 1
            c["individuals_from_prior_report_summary" if v(r.get("source_reference_in_review")) not in MISSING
              else "individuals_first_hand"] += 1
        carriers = set()
        for i, r in enumerate(t.get("variants") or []):
            g = gene if is_gene(v(r.get("gene_symbol_as_stated")), gene) else "other"
            c[f"variant_rows_gene:{g}"] += 1
            orig = v(r.get("variant_original_string"))
            if orig in MISSING:
                no_original_string.append(f"{pmid}:variants[{i}]")
            elif g == gene:
                distinct_variants.add(WS.sub("", html.unescape(str(orig))).lower())
                c["variant_rows_gene:TNFAIP3_with_printed_variant"] += 1
            if g == gene:
                carriers.add(v(r.get("individual_label_in_paper")))
                inh = v(r.get("inheritance"))
                c[f"tnfaip3_inheritance:{inh}"] += 1
                if inh == "de novo" and v(r.get("parental_testing_statement")) in MISSING:
                    de_novo_without_testing.append(f"{pmid}:{v(r.get('individual_label_in_paper'))}")
        c["individuals_with_tnfaip3_variant_row"] += len(carriers)
        for r in t.get("phenotypic_features") or []:
            c[f"features_status:{v(r.get('status'))}"] += 1
            c[f"features_basis:{v(r.get('evidence_basis'))}"] += 1
        per_ind = Counter()
        for r in t.get("phenotype_checklist") or []:
            c[f"checklist_status:{v(r.get('status'))}"] += 1
            if v(r.get("status")) not in MISSING:
                c[f"checklist_basis:{v(r.get('evidence_basis'))}"] += 1
            per_ind[v(r.get("individual_label_in_paper"))] += 1
        for r in inds:
            lab = v(r.get("individual_label_in_paper"))
            if per_ind[lab] != args.checklist_size:
                incomplete_checklist.append(f"{pmid}:{lab}:{per_ind[lab]}")

    out = {
        "run_id": args.run_id,
        "papers_expected": len(expected) or None,
        "papers_processed": len(papers),
        "papers_missing": sorted(set(expected) - set(papers)),
        "counts": dict(sorted(c.items())),
        "distinct_tnfaip3_variant_strings": len(distinct_variants),
        "papers_flag_true_without_individual_rows": flagged_true_no_rows,
        "variant_rows_without_original_string": no_original_string,
        "individuals_with_incomplete_checklist": incomplete_checklist,
        "tnfaip3_de_novo_without_parental_testing_statement": de_novo_without_testing,
    }
    rec = run_dir / "reconcile_summary.json"
    if rec.exists():
        out["reconciliation"] = json.loads(rec.read_text())
    dest = Path("analysis/poc") / f"extraction_counts_{args.run_id}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
