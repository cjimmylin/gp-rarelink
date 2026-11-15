"""Mark withdrawn extension gap candidates in candidates.csv (D-48 entry, 2026-11-15; same form as D-43's G-danon-001).

Adds `status` (candidate / withdrawn) and `status_note` columns. Re-run after any gap_candidates.py
re-run, because that rewrites candidates.csv. Withdrawn candidates keep their row and dossier.

  python3 -I adjudication/o3_gaps_ext/apply_withdrawals.py
"""
import csv
from pathlib import Path

PATH = Path("adjudication/o3_gaps_ext/candidates.csv")
# keyed by genomic position, because candidate ids are positional and shift when the candidate set changes
WITHDRAWN = {
    "16:50711530:T:C": "withdrawn (D-48, 2026-11-15; Claude under Jimmy's delegation): the papers write c.1538T>C (M513T) in legacy "
                       "NM_022162 numbering; with no transcript stated it was read on MANE, where the reference base also matches, giving "
                       "p.Leu513Pro, which no paper describes. On MANE the stated allele is c.1457T>C p.Met486Thr. Not a gap.",
    "4:67583648:T:C": "withdrawn (D-48, 2026-11-15; Claude under Jimmy's delegation): placed on chromosome 4 because paper 31684177 states "
                      "transcript NM_012108.3, which is not an LCAT transcript; the paper's change is p.Ile202Thr in LCAT. Not a gap.",
}


def main() -> int:
    rows = list(csv.DictReader(PATH.open()))
    fields = [f for f in rows[0] if f not in ("status", "status_note")] + ["status", "status_note"]
    for r in rows:
        note = WITHDRAWN.get(r["vcf_grch38"], "")
        r["status"], r["status_note"] = ("withdrawn", note) if note else ("candidate", "")
    with PATH.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    out = [(r["candidate_id"], r["vcf_grch38"]) for r in rows if r["status"] == "withdrawn"]
    print({"rows": len(rows), "withdrawn": out})
    assert len(out) == len(WITHDRAWN), "a withdrawn position is missing from candidates.csv"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
