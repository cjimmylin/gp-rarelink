"""Apply the OMIM check (D-42) and the D-43 withdrawal to the gap-candidate list.

Pre-registration §7.3 requires a gap variant to be absent from ClinVar and not
listed among OMIM's allelic variants. The OMIM half waited on D-12 and was
computed on 2026-10-28 from the entry pages Dr. Lin froze (D-42;
analysis/omim_holdout/assess.py -> gap_candidates_omim_check_<date>.csv). This
script copies that verdict into candidates.csv's ``omim_checked`` column and adds
two columns, ``status`` and ``status_note``. No row is removed: dossiers,
batches, triage flags and the adjudication page key on candidate_id.

Withdrawn (D-43, Dr. Lin, 2026-10-28): G-danon-001, whose description the paper
places on LAMP2 exon 9b (NM_013995) while the run assumed the MANE transcript,
so its genomic allele is an artefact; on the right transcript it is OMIM
309060.0001 / ClinVar 1410728.

  uv run python adjudication/o3_gaps/apply_omim_check.py --date 2026-10-28
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
WITHDRAWN = {
    "G-danon-001": "withdrawn (D-43, 2026-10-28): reported on LAMP2 exon 9b (NM_013995; the paper's table reads 'E9b') but normalized on the MANE "
                   "transcript NM_002294.3, so X:120431457:CTT:C is an artefact; on NM_013995 it is OMIM 309060.0001 / ClinVar 1410728 (not a gap)",
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--date", default="2026-10-28")
    args = ap.parse_args(argv)
    check = {r["candidate_id"]: r for r in csv.DictReader((REPO / "analysis/omim_holdout" / f"gap_candidates_omim_check_{args.date}.csv").open())}
    rows = list(csv.DictReader((HERE / "candidates.csv").open()))
    fields = list(rows[0].keys())
    for col in ("status", "status_note"):
        if col not in fields:
            fields.append(col)
    n_checked = 0
    for r in rows:
        c = check.get(r["candidate_id"])
        if c:
            r["omim_checked"] = c["omim_check_2026_10_28"] + f" [entries frozen {args.date}, D-42]"
            n_checked += 1
        if r["candidate_id"] in WITHDRAWN:
            r["status"], r["status_note"] = "withdrawn", WITHDRAWN[r["candidate_id"]]
        else:
            r["status"], r["status_note"] = "candidate", ""
    with (HERE / "candidates.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print({"rows": len(rows), "omim_checked_applied": n_checked, "withdrawn": sum(1 for r in rows if r["status"] == "withdrawn"),
           "omim_absent": sum(1 for r in rows if r["omim_checked"].startswith("absent")),
           "omim_collision_noted": sum(1 for r in rows if r["omim_checked"].startswith("possible"))})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
