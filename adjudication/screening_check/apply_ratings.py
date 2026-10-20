"""Collect the screening-check ratings and compute agreement with the screening.

Input: the page's store, read with ArtifactData `list` (`out_dir`) into
<store>/abstract_check/*.json and <store>/exclusion_check/*.json.

  Part A (title/abstract inclusions, rated blind): agreement = the rater also
      says include. "unsure" is reported apart, not counted as agreement.
  Part B (full-text exclusions): agreement = the rater agrees with the exclusion.

Writes adjudication/screening_check/ratings.csv (item_id, part, disease, pmid,
screen_label, rater_label, note, updated_at) and ratings_summary.json with
counts and exact (Clopper-Pearson) 95% intervals.

  uv run python adjudication/screening_check/apply_ratings.py --store <scratch>/store
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from pipeline.extract.claude_code.gatekeeper_merge import share

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--store", required=True)
    args = ap.parse_args(argv)
    sample = {r["item_id"]: r for r in csv.DictReader((HERE / "sample.csv").open())}
    rows = []
    for coll in ("abstract_check", "exclusion_check"):
        for f in sorted((Path(args.store) / coll).glob("*.json")):
            d = json.loads(f.read_text())
            body = d.get("data", d)
            iid = f.stem
            if iid not in sample:
                raise SystemExit(f"rating for an item not in sample.csv: {iid}")
            s = sample[iid]
            rows.append({"item_id": iid, "part": s["part"], "disease": s["disease"], "pmid": s["pmid"],
                         "screen_label": s["screen_label"], "rater_label": body.get("label", ""),
                         "note": body.get("note", ""), "updated_at": body.get("updated_at", "")})
    rows.sort(key=lambda r: r["item_id"])
    with (HERE / "ratings.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    out = {"rater": "Jimmy Lin", "sample_size": {p: sum(1 for s in sample.values() if s["part"] == p) for p in "AB"}}
    for part, agree in (("A", "include"), ("B", "agree")):
        rated = [r for r in rows if r["part"] == part and r["rater_label"]]
        n_agree = sum(r["rater_label"] == agree for r in rated)
        out[f"part_{part}"] = {"rated": len(rated), "labels": dict(Counter(r["rater_label"] for r in rated)),
                               "by_disease": dict(Counter(r["disease"] for r in rated)),
                               "agreement": share(n_agree, len(rated)),
                               "disagreements": [{k: r[k] for k in ("item_id", "rater_label", "note")}
                                                 for r in rated if r["rater_label"] != agree]}
    (HERE / "ratings_summary.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
