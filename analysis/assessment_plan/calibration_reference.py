"""Reference labels for the audit calibration candidates (D-55): tabulate them and pick the calibration set.

Reads the exports of the reference-labelling page's store (ArtifactData list with out_dir,
saved under adjudication/calibration/private/reference_export*/ratings/) and the private keys
of every draw. Writes, privately, one canonical labels file and, when enough clear labels
exist, the calibration set: the first 20 claims labelled unsupported and the first 20 labelled
supported, in item order (the order the seeded draw gave them). Only the two clear labels
count; "cannot verify" and "quote not in paper" are left out of the set.

Publicly it writes counts only, with the sha256 of the private files
(adjudication/calibration/reference_labels_<date>.json). Item-level labels stay private until
calibration ends.

  python3 -I analysis/assessment_plan/calibration_reference.py --date 2026-11-16
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import statistics
from collections import Counter
from pathlib import Path

PRIV = Path("adjudication/calibration/private")
NEED = 20


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    items = []
    for k in sorted(PRIV.glob("audit_candidates*/key.json")):
        key = json.loads(k.read_text())
        items += [{**i, "draw": key.get("draw", 1)} for i in key["items"]]
    labels = {}
    for f in sorted(PRIV.glob("reference_export*/ratings/CAL-*.json")):
        labels[f.stem] = json.loads(f.read_text())          # a later export of the same item replaces an earlier one
    rated = [i for i in items if (labels.get(i["item_id"]) or {}).get("rating")]
    canon = {i["item_id"]: {"rating": labels[i["item_id"]]["rating"], "updated_at": labels[i["item_id"]].get("updated_at")} for i in rated}
    lab_file = PRIV / "reference_labels.json"
    lab_file.write_text(json.dumps(canon, indent=1, sort_keys=True) + "\n")
    uns = [i["item_id"] for i in items if canon.get(i["item_id"], {}).get("rating") == "unsupported"]
    sup = [i["item_id"] for i in items if canon.get(i["item_id"], {}).get("rating") == "supported"]
    out = {"date": a.date, "decision": "D-55", "candidates": len(items), "labelled": len(rated),
           "by_draw": {str(d): sum(1 for i in items if i["draw"] == d) for d in sorted({i["draw"] for i in items})},
           "labels": dict(Counter(canon[i["item_id"]]["rating"] for i in rated)),
           "by_source_and_label": {f"{p}:{r}": n for (p, r), n in sorted(Counter((i["pool"], canon[i["item_id"]]["rating"]) for i in rated).items())},
           "clear_unsupported": len(uns), "clear_supported": len(sup), "needed_of_each": NEED,
           "sha256": {"reference_labels.json": hashlib.sha256(lab_file.read_bytes()).hexdigest()}}
    # time per rating, per sitting (a gap of ten minutes or more starts a new sitting)
    ts = sorted(dt.datetime.fromisoformat(v["updated_at"].replace("Z", "+00:00")) for v in canon.values() if v.get("updated_at"))
    sittings, cur = [], [ts[0]] if ts else []
    for t0, t1 in zip(ts, ts[1:]):
        if (t1 - t0).total_seconds() >= 600:
            sittings.append(cur)
            cur = []
        cur.append(t1)
    if cur:
        sittings.append(cur)
    out["sittings"] = [{"ratings": len(s), "minutes": round((s[-1] - s[0]).total_seconds() / 60, 1),
                        "median_seconds_between_ratings": round(statistics.median([(b - x).total_seconds() for x, b in zip(s, s[1:])])) if len(s) > 1 else None}
                       for s in sittings]
    if len(uns) >= NEED and len(sup) >= NEED:
        chosen = uns[:NEED] + sup[:NEED]
        ref = {c: canon[c]["rating"] for c in chosen}
        rows = {}
        for f in sorted(PRIV.glob("audit_candidates*/sample.csv")):
            for r in csv.DictReader(f.open(newline="")):
                rows[r["item_id"]] = r
        cal = PRIV / "calibration_set"
        cal.mkdir(exist_ok=True)
        ordered = sorted(chosen)                                # page order is set per rater when the pages are built
        with (cal / "sample.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[ordered[0]].keys()))
            w.writeheader()
            w.writerows(rows[c] for c in ordered)
        (cal / "reference.json").write_text(json.dumps(ref, indent=1, sort_keys=True) + "\n")
        dis = {i["item_id"]: i["disease"] for i in items}
        out["calibration_set"] = {"claims": len(chosen), "unsupported": NEED, "supported": NEED,
                                  "by_disease": dict(sorted(Counter(dis[c] for c in chosen).items())),
                                  "candidates_not_used": len(items) - len(chosen)}
        out["sha256"]["calibration_set/sample.csv"] = hashlib.sha256((cal / "sample.csv").read_bytes()).hexdigest()
        out["sha256"]["calibration_set/reference.json"] = hashlib.sha256((cal / "reference.json").read_bytes()).hexdigest()
    else:
        out["calibration_set"] = None
        out["short_of"] = {"unsupported": max(0, NEED - len(uns)), "supported": max(0, NEED - len(sup))}
    Path(f"adjudication/calibration/reference_labels_{a.date}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
