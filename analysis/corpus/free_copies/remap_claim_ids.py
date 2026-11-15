"""Keep gatekeeper verdicts when one paper of a run is re-extracted (D-47 batch 1, Qian 2020).

gatekeeper_prep numbers a run's claims in order, so replacing one paper's extraction shifts the
claim ids of every paper after it. This script carries the existing verdict files of the papers
that did not change over to the new numbering:

  1. match every claim of an unchanged paper between the old and the new gatekeeper_v4_claims.csv
     on (pmid, table, row, field), and stop unless value and class are identical;
  2. rewrite claim_id in gatekeeper_v4/<chunk>.csv and gatekeeper_v4_set_aside/<chunk>.*.csv
     for those papers; nothing else in those files changes;
  3. write claim_id_remap_<date>.csv (pmid, old_id, new_id) into the run directory.

The replaced paper's own chunk files must have been moved away first; its claims are judged anew.

  python3 -I analysis/corpus/free_copies/remap_claim_ids.py --disease lad1 --run-id pv1a-lad1 \
      --old-claims <copy of the old gatekeeper_v4_claims.csv> --replaced 32154133 --date 2026-11-15
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--old-claims", required=True, type=Path)
    ap.add_argument("--replaced", required=True, nargs="+")
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    run = ROOT / "data/extracted" / a.disease / a.run_id
    key = lambda r: (r["pmid"], r["table"], r["row"], r["field"])  # noqa: E731
    old = [r for r in csv.DictReader(a.old_claims.open()) if r["pmid"] not in a.replaced]
    new = {key(r): r for r in csv.DictReader((run / "gatekeeper_v4_claims.csv").open()) if r["pmid"] not in a.replaced}
    if len(old) != len(new):
        raise SystemExit(f"unchanged papers have {len(old)} old claims but {len(new)} new ones")
    remap = {}
    for r in old:
        n = new.get(key(r))
        if n is None or n["value"] != r["value"] or n["class"] != r["class"]:
            raise SystemExit(f"claim {r['claim_id']} {key(r)} does not match the new claims file")
        remap[r["claim_id"]] = (r["pmid"], n["claim_id"])
    files = [f for d in ("gatekeeper_v4", "gatekeeper_v4_set_aside") for f in sorted((run / d).glob("*.csv"))]
    changed = 0
    for f in files:
        if f.name.split("_")[0] in a.replaced:
            raise SystemExit(f"{f} belongs to a replaced paper; move it away first")
        rows = list(csv.DictReader(f.open()))
        cols = list(rows[0].keys())
        for r in rows:
            pmid, r["claim_id"] = remap[r["claim_id"]][0], remap[r["claim_id"]][1]
            if pmid != f.name.split("_")[0]:
                raise SystemExit(f"{f}: claim of another paper")
        with f.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
        changed += 1
    with (run / f"claim_id_remap_{a.date}.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "old_claim_id", "new_claim_id"])
        w.writerows((p, o, n) for o, (p, n) in remap.items())
    moved = sum(o != n for o, (_, n) in remap.items())
    print(f"{len(remap)} claims of unchanged papers matched; {moved} ids changed; {changed} verdict files rewritten")


if __name__ == "__main__":
    main()
