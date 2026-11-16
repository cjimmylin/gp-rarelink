"""Sizing of the third calibration draw (D-55, amended 2026-11-16): how many more candidates to label.

Reads the private keys, samples and reference labels of the earlier draws and the private rule
file (which names the capped kind of claim). Prints how often Jimmy labelled a claim the
gatekeeper had removed as unsupported, outside the capped kind, how many more such labels the
amended set needs, and the chance of getting them for several draw sizes. It also counts the
claims still available. Nothing is written; the figures are quoted in DECISIONS.md.

  python3 -I analysis/assessment_plan/third_draw_sizing.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from math import comb
from pathlib import Path

PRIV = Path("adjudication/calibration/private")
DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
EMPTY = {"", "null", '""', '"not reported"', '"unknown"', "[]", '"Not reported"'}
NEED = 20


def main() -> int:
    rule = json.loads((PRIV / "set_rule.json").read_text())
    lab = json.loads((PRIV / "reference_labels.json").read_text())
    items, rows = [], {}
    for k in sorted(PRIV.glob("audit_candidates*/key.json")):
        key = json.loads(k.read_text())
        if key.get("draw", 1) <= 2:
            items += key["items"]
            for r in csv.DictReader((k.parent / "sample.csv").open(newline="")):
                rows[r["item_id"]] = r
    other = [i for i in items if i["pool"] == "unsupported" and rows[i["item_id"]]["field"] != rule["cap_field"]]
    hit = sum(lab[i["item_id"]]["rating"] == "unsupported" for i in other)
    have = sum(1 for i in items if lab[i["item_id"]]["rating"] == "unsupported" and rows[i["item_id"]]["field"] != rule["cap_field"])
    need = NEED - rule["cap"] - have
    p = hit / len(other)
    out = {"removed_claims_outside_the_capped_kind_labelled": len(other), "of_which_unsupported": hit, "share": round(p, 3),
           "unsupported_outside_the_capped_kind_so_far": have, "more_needed": need,
           "chance_of_enough_by_draw_size": {n: round(sum(comb(n, k) * p**k * (1 - p)**(n - k) for k in range(need, n + 1)), 2) for n in (15, 20, 24, 30)},
           "expected_by_draw_size": {n: round(n * p, 1) for n in (15, 20, 24, 30)}}
    # what is left to draw from, outside the capped kind
    sample = defaultdict(set)
    for it in json.loads(Path("adjudication/o1_audit/sample_key.json").read_text())["items"]:
        sample[it["disease"]].add(it["claim_id"])
    used_claims = {(i["disease"], i["claim_id"]) for i in items}
    used_papers = {(r["disease"], r["pmid"]) for r in rows.values()}
    left = {"unused_papers": [0, set()], "any_paper": [0, set()]}
    for d in DISEASES:
        run = Path(f"data/extracted/{d}/pv1-{d}")
        man = {r["pmid"]: r for r in csv.DictReader(open(f"data/literature/{d}/manifest.csv", newline=""))}
        conv = Path(f"data/literature/{d}/supplementary/conversion.csv")
        supp = {r["pmid"] for r in csv.DictReader(conv.open())} if conv.exists() else set()
        for r in csv.DictReader((run / "gatekeeper_v4.csv").open(newline="")):
            if (r["class"] == "model" and r["verdict"] == "unsupported" and r["value"].strip() not in EMPTY and r["claim_id"] not in sample[d]
                    and man.get(r["pmid"], {}).get("fulltext_format") == "nxml" and r["pmid"] not in supp
                    and (d, r["claim_id"]) not in used_claims and r["field"] != rule["cap_field"]):
                for name in ("any_paper",) + (("unused_papers",) if (d, r["pmid"]) not in used_papers else ()):
                    left[name][0] += 1
                    left[name][1].add((d, r["pmid"]))
    out["removed_claims_left_outside_the_capped_kind"] = {k: {"claims": v[0], "papers": len(v[1])} for k, v in left.items()}
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
