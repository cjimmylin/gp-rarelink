"""Re-check O3 gap candidates against a newer ClinVar snapshot (pre-registration §7.3).

§7.3: candidates are re-checked against ClinVar before submission, with the date recorded. This
runs that check against a dated snapshot: a candidate whose GRCh38 allele now has a ClinVar
record is listed with the record's VariationID, classification and the date ClinVar gives for
its last evaluation. Candidates are not removed from candidates.csv; the result is a flag
(`newly_in_clinvar` in triage_flags.py) for the panel.

A gene is checked only when its snapshot manifest exists (a complete, md5-checked download).

  uv run python -m pipeline.harness.gap_recheck --snapshot /home/user/gp-rarelink-reference/2026-10-21
writes adjudication/o3_gaps/recheck_<snapshot date>.json.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from pipeline.harness.gap_candidates import clinvar_by_vcf
from pipeline.harness.snapshot_reference import classify

OUT = Path("adjudication/o3_gaps")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--manifests", default="analysis/poc/reference_snapshot")
    a = ap.parse_args(argv)
    snap = Path(a.snapshot)
    date = snap.name
    cands = list(csv.DictReader((OUT / "candidates.csv").open()))
    genes = sorted({c["gene"] for c in cands})
    checked, skipped, release = {}, [], {}
    for g in genes:
        man = Path(a.manifests) / date / f"MANIFEST_{g}.json"
        if not man.exists():
            skipped.append(g)
            continue
        m = json.loads(man.read_text())
        release[g] = m["files"]["variant_summary"]["last_modified"]
        checked[g] = clinvar_by_vcf(snap, g)
    now_in, rows = [], []
    for c in cands:
        g = c["gene"]
        if g not in checked:
            continue
        rec = checked[g].get(c["vcf_grch38"])
        if rec:
            now_in.append(c["candidate_id"])
            rows.append({"candidate_id": c["candidate_id"], "hgvs_c": c["hgvs_c"], "clinvar_variation_id": rec["VariationID"],
                         "clinvar_class": classify(rec["ClinicalSignificance"]), "last_evaluated": rec.get("LastEvaluated", ""),
                         "review_status": rec.get("ReviewStatus", ""), "submitters": rec.get("NumberSubmitters", "")})
    out = {"snapshot": date, "variant_summary_last_modified": release, "genes_checked": sorted(checked), "genes_skipped_incomplete": skipped,
           "candidates_checked": sum(1 for c in cands if c["gene"] in checked), "now_in_clinvar": now_in, "records": rows}
    (OUT / f"recheck_{date}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "records"}, indent=1))
    for r in rows:
        print(r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
