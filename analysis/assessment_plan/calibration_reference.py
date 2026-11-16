"""Reference labels for the audit calibration candidates (D-55): tabulate them and pick the calibration set.

Reads the exports of the reference-labelling page's store (ArtifactData list with out_dir,
saved under adjudication/calibration/private/reference_export*/ratings/) and the private keys
of every draw. Writes, privately, one canonical labels file and, when enough clear labels
exist, the calibration set: the first 20 claims labelled unsupported and the first 20 labelled
supported, in item order (the order the seeded draw gave them). Only the two clear labels
count; "cannot verify" and "quote not in paper" are left out of the set.

Amended 2026-11-16 on Jimmy's word (DECISIONS.md, D-55): one kind of claim filled half of the
unsupported side, so that kind is capped. The field and the cap are in the private rule file
(private/set_rule.json, sha256 committed with the third draw) and are read from there, because
naming them here would hint at the answers. With the rule file present, the unsupported side is
the other claims in item order up to 20 minus the cap, then claims of the capped field to make
20; the supported side is unchanged. Without the file the first rule applies.

Amended a second time the same day, again on his word: with papers of earlier draws allowed in
the third draw, two pairs of claims in the set rested on the same quote of the same paper. With
private/set_rule_2.json present, a claim with the same paper and quote as an earlier claim of
its side (in item order) is skipped and the next claim takes its place.

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
PRIVATE_KEYS = {"unsupported_outside_the_capped_kind", "of_which_usable_after_repeats", "places_for_the_capped_kind"}


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
    rule_file = PRIV / "set_rule.json"
    rule = json.loads(rule_file.read_text()) if rule_file.exists() else None
    field, quote = {}, {}
    for f in sorted(PRIV.glob("audit_candidates*/sample.csv")):
        for r in csv.DictReader(f.open(newline="")):
            field[r["item_id"]] = r["field"]
            quote[r["item_id"]] = (r["disease"], r["pmid"], r["span"])
    rule2_file = PRIV / "set_rule_2.json"
    rule2 = json.loads(rule2_file.read_text()) if rule2_file.exists() else None
    sup = [i["item_id"] for i in items if canon.get(i["item_id"], {}).get("rating") == "supported"]

    def no_repeats(seq: list[str]) -> tuple[list[str], list[str]]:
        """Item order kept; a claim with the same paper and quote as an earlier one of the same side is left out."""
        if not (rule2 and rule2.get("skip_same_paper_same_quote")):
            return seq, []
        seen, kept, left_out = set(), [], []
        for c in seq:
            (left_out if quote[c] in seen else kept).append(c)
            seen.add(quote[c])
        return kept, left_out

    uns_side, uns_rep = no_repeats(uns)
    sup_side, sup_rep = no_repeats(sup)
    if rule:
        other = [c for c in uns_side if field[c] != rule["cap_field"]][:NEED - rule["cap"]]
        capped = [c for c in uns_side if field[c] == rule["cap_field"]][:NEED - len(other)]
        uns_set = sorted(other + capped) if len(other) + len(capped) >= NEED else []
    else:
        uns_set = uns_side[:NEED]
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
    out["set_rule"] = ("amended twice (private/set_rule.json, set_rule_2.json)" if rule and rule2 else
                       "amended rule (private/set_rule.json)" if rule else "first rule")
    if rule2:
        out["sha256"]["set_rule_2.json"] = hashlib.sha256(rule2_file.read_bytes()).hexdigest()
        out["labelled_claims_that_repeat_a_quote_of_their_paper"] = {"unsupported": len(uns_rep), "supported": len(sup_rep)}
    if rule:
        out["sha256"]["set_rule.json"] = hashlib.sha256(rule_file.read_bytes()).hexdigest()
        out["unsupported_outside_the_capped_kind"] = sum(1 for c in uns if field[c] != rule["cap_field"])
        out["of_which_usable_after_repeats"] = sum(1 for c in uns_side if field[c] != rule["cap_field"])
        out["places_for_the_capped_kind"] = NEED - min(NEED - rule["cap"], out["of_which_usable_after_repeats"])
    if len(uns_set) >= NEED and len(sup_side) >= NEED:
        chosen = uns_set + sup_side[:NEED]
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
    (PRIV / "reference_summary.json").write_text(json.dumps(out, indent=1) + "\n")     # the full summary stays private
    public = {k: v for k, v in out.items() if k not in PRIVATE_KEYS}                  # the cap's size is not published
    Path(f"adjudication/calibration/reference_labels_{a.date}.json").write_text(json.dumps(public, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
