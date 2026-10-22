"""Collect same-person identity groups the dossier helpers proposed (WS3 follow-on, 2026-10-21).

The helpers found people the reconciliation step (policy v4 + duplicate-publication route) left
as separate identities, mostly a person cited by a later review or cohort paper. This lists
each proposed group with the helper's own wording as evidence. Nothing is merged: changing the
records after the freeze would be a deviation (needs Jimmy), and each group needs a person to
confirm it. The effect on counts is reported so the size of the problem is known.

  python3 -I adjudication/o3_gaps/proposed_merges.py
writes adjudication/o3_gaps/proposed_merges.csv and proposed_merges_summary.json.
"""
import csv
import glob
import json
import re
from collections import defaultdict

RX = re.compile(r"same (person|patient|girl|boy|woman|man|individual|people)|probably one|is a citation of|very likely (the same|one)|= ", re.I)
IDRX = re.compile(r"\b(?:HA20|SSADH|TANGIER|LAD1|AXD|DANON)-ID\d{4}\b|\bID\d{4}\b")
groups = {}
for f in sorted(glob.glob("adjudication/o3_gaps/dossiers/*.json")):
    d = json.load(open(f))
    dis = d["candidate_id"].split("-")[1].upper()
    for c in d.get("concerns", []):
        if RX.search(c):
            ids = tuple(sorted({x if "-" in x else f"{dis}-{x}" for x in IDRX.findall(c)}))
            if len(ids) >= 2:
                g = groups.setdefault(ids, {"disease": dis.lower(), "identities": ids, "candidates": set(), "evidence": c})
                g["candidates"].add(d["candidate_id"])
rows = [{"disease": g["disease"], "identities": " ".join(g["identities"]), "n": len(g["identities"]),
         "candidates": " ".join(sorted(g["candidates"])), "evidence_from_dossier": g["evidence"], "confirmed_by": "", "decision": ""}
        for g in groups.values()]
rows.sort(key=lambda r: (r["disease"], r["identities"]))
with open("adjudication/o3_gaps/proposed_merges.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
    w.writeheader(); w.writerows(rows)
totals = defaultdict(int)
for d in sorted({r["disease"] for r in rows}):
    ids = {r["identity"] for r in csv.DictReader(open(f"data/extracted/{d}/pv1-{d}/individuals_reconciled.csv"))}
    totals[d] = len(ids)
by = defaultdict(lambda: {"groups": 0, "identities_that_would_collapse": 0})
for r in rows:
    by[r["disease"]]["groups"] += 1
    by[r["disease"]]["identities_that_would_collapse"] += r["n"] - 1
summary = {d: {**v, "identities_now": totals[d], "share": round(v["identities_that_would_collapse"] / totals[d], 4)} for d, v in by.items()}
json.dump({"note": "Proposed by model helpers from the papers; unconfirmed. Only people in the 215 gap-candidate dossiers were examined, so the corpus-wide count is likely higher. A group can hold more than one person (the AxD group of 4 is probably 2 people), so collapse counts are upper bounds for these groups. Overlapping groups are not deduplicated.", "by_disease": summary},
          open("adjudication/o3_gaps/proposed_merges_summary.json", "w"), indent=1)
print(json.dumps(summary, indent=1))
