"""O1 audit (pre-registration §7.1): combine the two raters, build the tie-breaker sheet, compute O1.

Inputs are the rater pages' stores, saved with ArtifactData `list` of collection `ratings` with
`out_dir` (one JSON file per claim, `<dir>/ratings/O1-nnn.json`, fields rating and note):
  rater A  https://claude.ai/artifact/Jvk4nxzG79u9AchAXvwPe4
  rater B  https://claude.ai/artifact/1VVgQNgSpyzDrsApErz8YU
  rater C  the tie-breaker page, built from tiebreak/sample.csv once A and B are complete.

Labels: supported, unsupported, span_not_found, cannot_verify. For O1, unsupported, span not
found and cannot verify all count as unsupported (§7.1); a sensitivity figure leaves the
cannot-verify claims out of numerator and denominator.
Agreement: percent agreement and Cohen's kappa on the four labels and on the binary
(supported vs not). A disagreement on the four labels goes to the tie-breaker.
Decision rule C (D-02): pass if at most 4 of 250 are unsupported. Every report gives the exact
95% interval and the highest rate the audit cannot exclude, and never calls a pass proof that
the true rate is below 2%.
Gatekeeper accuracy (§7.1 b): every sampled claim was judged supported by gatekeeper v4 (the
pool rule), so the human unsupported share is also the gatekeeper's false-acceptance rate.

  python3 -I adjudication/o1_audit/collect_o1.py --a-dir <dirA> --b-dir <dirB> [--c-dir <dirC>]
writes adjudication/o1_audit/o1_result.json, ratings_merged.csv and tiebreak/sample.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1]))
from pipeline.extract.claude_code.gatekeeper_merge import share  # noqa: E402  (pure-Python exact interval)

LABELS = ("supported", "unsupported", "span_not_found", "cannot_verify")
BAD = {"unsupported", "span_not_found", "cannot_verify"}


def load(d: str | None) -> dict[str, str]:
    if not d:
        return {}
    out = {}
    for f in sorted(Path(d).rglob("O1-*.json")):
        doc = json.loads(f.read_text())
        body = doc.get("data", doc)
        if body.get("rating") in LABELS:
            out[f.stem] = body["rating"]
    return out


def kappa(pairs: list[tuple[str, str]]) -> float | None:
    n = len(pairs)
    if not n:
        return None
    po = sum(a == b for a, b in pairs) / n
    ca, cb = Counter(a for a, _ in pairs), Counter(b for _, b in pairs)
    pe = sum(ca[k] * cb[k] for k in set(ca) | set(cb)) / (n * n)
    return round((po - pe) / (1 - pe), 4) if pe < 1 else None


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--a-dir", required=True)
    ap.add_argument("--b-dir", required=True)
    ap.add_argument("--c-dir", default=None)
    ap.add_argument("--out", default=str(HERE))
    a = ap.parse_args(argv)
    sample = list(csv.DictReader((HERE / "sample.csv").open()))
    ids = [r["item_id"] for r in sample]
    A, B, C = load(a.a_dir), load(a.b_dir), load(a.c_dir)
    res = {"n_sample": len(ids), "rated_A": sum(i in A for i in ids), "rated_B": sum(i in B for i in ids),
           "rated_C": sum(i in C for i in ids)}
    both = [i for i in ids if i in A and i in B]
    pairs = [(A[i], B[i]) for i in both]
    binp = [("bad" if x in BAD else "ok", "bad" if y in BAD else "ok") for x, y in pairs]
    res["agreement"] = {"pairs": len(pairs), "percent_4_labels": round(sum(x == y for x, y in pairs) / len(pairs), 4) if pairs else None,
                        "kappa_4_labels": kappa(pairs), "percent_binary": round(sum(x == y for x, y in binp) / len(binp), 4) if binp else None,
                        "kappa_binary": kappa(binp)}
    disagree = [i for i in both if A[i] != B[i]]
    res["disagreements"] = len(disagree)
    out = Path(a.out)
    (out / "tiebreak").mkdir(exist_ok=True)
    rows = [r for r in sample if r["item_id"] in set(disagree)]
    if rows:
        with (out / "tiebreak" / "sample.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader(); w.writerows(rows)
    final, merged = {}, []
    for r in sample:
        i = r["item_id"]
        f = A[i] if i in A and i in B and A[i] == B[i] else C.get(i)
        if f:
            final[i] = f
        merged.append({"item_id": i, "disease": r["disease"], "A": A.get(i, ""), "B": B.get(i, ""), "C": C.get(i, ""), "final": f or ""})
    with (out / "ratings_merged.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(merged[0].keys()))
        w.writeheader(); w.writerows(merged)
    res["final_labelled"] = len(final)
    res["complete"] = len(final) == len(ids)
    if res["complete"]:
        k = sum(v in BAD for v in final.values())
        o1 = share(k, len(ids))
        cv = sum(v == "cannot_verify" for v in final.values())
        sens = share(k - cv, len(ids) - cv)
        res["o1"] = {"unsupported": o1, "rule_C_pass": k <= 4, "highest_rate_not_excluded": o1["ci95"][1],
                     "sensitivity_without_cannot_verify": sens,
                     "label_counts": dict(Counter(final.values())),
                     "by_disease": {d: share(sum(final[r["item_id"]] in BAD for r in sample if r["disease"] == d),
                                             sum(1 for r in sample if r["disease"] == d)) for d in sorted({r["disease"] for r in sample})},
                     "gatekeeper_false_acceptance": o1,
                     "wording": "Observed rate with exact 95% interval; a pass under rule C is not proof that the true rate is below 2%."}
    (out / "o1_result.json").write_text(json.dumps(res, indent=1) + "\n")
    print(json.dumps({k: v for k, v in res.items() if k != "o1"}, indent=1))
    if "o1" in res:
        print(json.dumps(res["o1"]["unsupported"]), "rule C pass:", res["o1"]["rule_C_pass"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
