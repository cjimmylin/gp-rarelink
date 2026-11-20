"""Score the raters' audit calibration round against the reference labels (D-55).

Written on 2026-11-16, before any rater had entered a rating (all eight stores read empty that
day), so that how a rating counts is fixed before a result exists.

How a rating counts (the page tells raters the same thing):
  - A claim whose reference label is unsupported is CAUGHT when the rater's label is
    "unsupported", "quote not in paper" or "cannot verify" (the registered audit counts
    "cannot verify" as unsupported). The strict count, "unsupported" or "quote not in paper"
    only, is reported beside it.
  - A claim whose reference label is supported is PASSED only when the rater's label is
    "supported".
  - The floor (DECISIONS.md, D-55): at least 15 of the 20 unsupported claims caught and at
    least 18 of the 20 supported claims passed. It is applied only to a rater who has rated
    all 40 claims.

Reported beside the floor, as description and not as a second rule:
  - the same counts on the claims that all three versions of the set share (the set was
    amended twice after the reference labels were seen; DECISIONS.md, D-55);
  - on the unsupported side, the capped kind of claim apart from the others (the kind is named
    only in the private rule file);
  - each rater's agreement with the majority of the OTHER raters who finished, and the share
    of claims on which each pair of raters agrees;
  - minutes per rating, from the time stamps, per sitting (a gap of ten minutes or more starts
    a new sitting).

Inputs, all private (adjudication/calibration/private/, git-ignored):
  calibration_set/reference.json           the 40 reference labels
  raters/R<n>/map.json                     page number (R3-07) -> candidate
  rater_exports/R<n>/ratings/*.json        each rater's store, exported with
                                           ArtifactData list (collection "ratings", out_dir)
Output: private/calibration_scores.json, and the same printed. Per-rater results are about
people on the team; nothing here is written to a committed file. Whether and how results go
into the repository is Jimmy's decision.

  python3 -I analysis/assessment_plan/calibration_score.py --date 2026-11-20
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import statistics
from itertools import combinations
from pathlib import Path

PRIV = Path("adjudication/calibration/private")


def raters() -> list[str]:
    """Every rater who has a page: R1 to R8, and anyone added later (a ninth joined on 2026-11-16)."""
    return sorted((p.parent.name for p in (PRIV / "raters").glob("R*/map.json")), key=lambda r: int(r[1:]))

FLOOR = {"caught": 15, "passed": 18}
NOT_SUPPORTED = {"unsupported", "span_not_found", "cannot_verify"}
STRICT = {"unsupported", "span_not_found"}


def sittings(stamps: list[str]) -> list[dict]:
    ts = sorted(dt.datetime.fromisoformat(s.replace("Z", "+00:00")) for s in stamps if s)
    if not ts:
        return []
    groups, cur = [], [ts[0]]
    for t0, t1 in zip(ts, ts[1:]):
        if (t1 - t0).total_seconds() >= 600:
            groups.append(cur)
            cur = []
        cur.append(t1)
    groups.append(cur)
    return [{"ratings": len(g), "minutes": round((g[-1] - g[0]).total_seconds() / 60, 1),
             "median_seconds_between_ratings": round(statistics.median([(b - a).total_seconds() for a, b in zip(g, g[1:])])) if len(g) > 1 else None}
            for g in groups]


def score(reference: dict[str, str], labels: dict[str, dict[str, str]], capped: set[str] | None = None,
          common: set[str] | None = None) -> dict:
    """reference: candidate -> 'supported' | 'unsupported'. labels: rater -> candidate -> the rater's label."""
    uns = sorted(c for c, v in reference.items() if v == "unsupported")
    sup = sorted(c for c, v in reference.items() if v == "supported")

    def counts(lab: dict[str, str], within: set[str] | None = None) -> dict:
        u = [c for c in uns if within is None or c in within]
        s = [c for c in sup if within is None or c in within]
        return {"unsupported_claims": len(u), "caught": sum(lab.get(c) in NOT_SUPPORTED for c in u),
                "caught_strict": sum(lab.get(c) in STRICT for c in u),
                "supported_claims": len(s), "passed": sum(lab.get(c) == "supported" for c in s)}

    done = [r for r in labels if all(labels[r].get(c) for c in reference)]
    out = {"raters": {}, "finished": done}
    for r, lab in labels.items():
        row = {"rated": sum(1 for c in reference if lab.get(c)), "of": len(reference), "finished": r in done,
               "labels": {k: sum(1 for c in reference if lab.get(c) == k) for k in ("supported", "unsupported", "span_not_found", "cannot_verify")},
               **counts(lab)}
        row["meets_floor"] = (row["caught"] >= FLOOR["caught"] and row["passed"] >= FLOOR["passed"]) if r in done else None
        if common is not None:
            row["on_claims_in_all_three_versions"] = counts(lab, common)
        if capped is not None:
            row["capped_kind"] = {"claims": sum(1 for c in uns if c in capped), "caught": sum(lab.get(c) in NOT_SUPPORTED for c in uns if c in capped)}
            row["other_kinds"] = {"claims": sum(1 for c in uns if c not in capped), "caught": sum(lab.get(c) in NOT_SUPPORTED for c in uns if c not in capped)}
        others = [o for o in done if o != r]
        if r in done and len(others) >= 2:
            agree = n = 0
            for c in reference:
                votes = sum(labels[o][c] != "supported" for o in others)
                if votes * 2 == len(others):
                    continue                              # the others are split evenly: no majority
                n += 1
                agree += (lab[c] != "supported") == (votes * 2 > len(others))
            row["agrees_with_majority_of_the_others"] = {"claims_with_a_majority": n, "agrees": agree}
        out["raters"][r] = row
    out["pairs"] = {f"{a}-{b}": sum((labels[a][c] != "supported") == (labels[b][c] != "supported") for c in reference)
                    for a, b in combinations(done, 2)}
    if len(done) >= 3:
        out["majority_of_the_finished_raters_vs_reference"] = {
            "claims": len(reference),
            "agrees": sum((sum(labels[r][c] != "supported" for r in done) * 2 > len(done)) == (reference[c] == "unsupported") for c in reference),
            "ties": sum(sum(labels[r][c] != "supported" for r in done) * 2 == len(done) for c in reference)}
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    reference = json.loads((PRIV / "calibration_set/reference.json").read_text())
    rule = json.loads((PRIV / "set_rule.json").read_text())
    field = {}
    for f in sorted(PRIV.glob("audit_candidates*/sample.csv")):
        import csv
        for r in csv.DictReader(f.open(newline="")):
            field[r["item_id"]] = r["field"]
    capped = {c for c in reference if field[c] == rule["cap_field"]}
    earlier = [json.loads(p.read_text()) for p in (PRIV / "superseded_first_set/calibration_set/reference.json", PRIV / "calibration_set_amendment1/reference.json") if p.exists()]
    common = set(reference).intersection(*[set(e) for e in earlier]) if earlier else None
    labels, times, missing = {}, {}, []
    for r in raters():
        folder = PRIV / "rater_exports" / r / "ratings"
        if not folder.exists():
            missing.append(r)
            continue
        mp = json.loads((PRIV / "raters" / r / "map.json").read_text())
        docs = {f.stem: json.loads(f.read_text()) for f in folder.glob("*.json")}
        unknown = sorted(set(docs) - set(mp))
        if unknown:
            raise SystemExit(f"{r}: the export holds documents that are not on this rater's page: {unknown[:5]}")
        labels[r] = {mp[k]: v.get("rating") for k, v in docs.items() if v.get("rating")}
        times[r] = sittings([v.get("updated_at") for v in docs.values() if v.get("rating")])
    out = {"date": a.date, "decision": "D-55", "floor": FLOOR, "no_export_yet": missing,
           "versions_of_the_set_compared": 1 + len(earlier), "claims_in_all_versions": len(common) if common is not None else None,
           **score(reference, labels, capped, common), "sittings": times,
           "sha256": {"calibration_set/reference.json": hashlib.sha256((PRIV / "calibration_set/reference.json").read_bytes()).hexdigest()}}
    (PRIV / "calibration_scores.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
