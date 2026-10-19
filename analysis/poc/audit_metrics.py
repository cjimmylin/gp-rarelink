"""Score the Stage 5 human audit (POC_DESIGN.md Stage 5 step 4; Q4).

Inputs:
  adjudication/poc_audit/sample.csv   the 50-claim sheet with the rater's labels
      column 'rating (supported / partially supported / unsupported)', a 'note',
      and optionally 'final_rating' and 'final_reason' (step 3: after re-reading
      disagreements and partials with the full paragraph; when present it is the
      label scored).
  adjudication/poc_audit/sample_key.json  seed and strata
  data/extracted/<disease>/<run_id>/gatekeeper.csv  the gatekeeper verdicts
  data/extracted/<disease>/<run_id>/span_check.json  automated span match
  adjudication/poc_audit/hpo_model_binding_sample.csv  (optional) 30 model HPO
      bindings with 'rater_ok (yes/no)'

Outputs analysis/poc/audit_metrics.json:
  - counts of human labels, overall and per stratum;
  - the human unsupported rate with an exact (Clopper-Pearson) 95% interval,
    strict (unsupported) and lenient (unsupported or partially supported);
  - the Q4 gate: automated span match >= 98% and human unsupported rate <= 4%
    (point estimate, n = 50); the strict rate is the one gated;
  - the gatekeeper vs human confusion matrix, and the gatekeeper's precision
    and recall for 'not supported' against the human label;
  - the disagreements and every claim the rater did not call supported, with
    the note (error classes are assigned from these notes in the report);
  - for the HPO sample, the share the rater accepted, by binding method.

Stops with a message if no rating is filled in yet. Rows left blank are
reported as unrated and left out of the denominators.

  uv run python analysis/poc/audit_metrics.py --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.claude_code.gatekeeper_merge import share

RATING_COL = "rating (supported / partially supported / unsupported)"
LABELS = {"supported": "supported", "s": "supported", "partially supported": "partially_supported",
          "partially_supported": "partially_supported", "partial": "partially_supported", "p": "partially_supported",
          "unsupported": "unsupported", "u": "unsupported", "not supported": "unsupported"}


def label(raw: str | None) -> str | None:
    s = " ".join(str(raw or "").strip().lower().replace("-", " ").split())
    if not s:
        return None
    if s not in LABELS:
        raise SystemExit(f"unrecognised rating {raw!r}; use supported / partially supported / unsupported")
    return LABELS[s]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--sheet", default="adjudication/poc_audit/sample.csv")
    ap.add_argument("--hpo-sheet", default="adjudication/poc_audit/hpo_model_binding_sample.csv")
    ap.add_argument("--gate", type=float, default=0.04)
    ap.add_argument("--gatekeeper-file", default="gatekeeper.csv", help="verdict file in the run directory (e.g. gatekeeper_v2_recheck.csv)")
    ap.add_argument("--out", default="analysis/poc/audit_metrics.json")
    ap.add_argument("--exclude-claims", default="", help="comma-separated claim ids left out (a labelled sensitivity run only)")
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    rows = list(csv.DictReader(Path(args.sheet).open()))
    gk = {r["claim_id"]: r for r in csv.DictReader((run_dir / args.gatekeeper_file).open())}
    span = json.loads((run_dir / "span_check.json").read_text())

    excluded = {c.strip() for c in args.exclude_claims.split(",") if c.strip()}
    rows = [r for r in rows if r["claim_id"] not in excluded]
    rated, unrated = [], []
    for r in rows:
        first = label(r.get(RATING_COL))
        final = label(r.get("final_rating")) if "final_rating" in r else None
        human = final or first
        if human is None:
            unrated.append(r["claim_id"])
            continue
        g = gk.get(r["claim_id"], {})
        rated.append({"claim_id": r["claim_id"], "stratum": r["stratum"], "pmid": r["pmid"], "table": r["table"],
                      "field": r["field"], "value": r["value"], "human_first": first, "human": human,
                      "changed_on_reread": bool(final and final != first), "gatekeeper": g.get("verdict", "missing"),
                      "gatekeeper_source": g.get("source", ""), "gatekeeper_reason": g.get("reason", ""),
                      "note": r.get("note", ""), "final_reason": r.get("final_reason", "")})
    if not rated:
        raise SystemExit(f"no ratings in {args.sheet} yet ({len(unrated)} rows blank)")

    n = len(rated)
    c = Counter(x["human"] for x in rated)
    per_stratum = defaultdict(Counter)
    for x in rated:
        per_stratum[x["stratum"]][x["human"]] += 1
    strict, lenient = share(c["unsupported"], n), share(c["unsupported"] + c["partially_supported"], n)
    # The sample is stratified with fixed counts per stratum, so the plain rate over-weights small pools
    # (excluded features). Weight each stratum's rate by its pool size (sample_key.json) as a sensitivity.
    weighted = None
    key_path = Path(args.sheet).with_name("sample_key.json")
    if key_path.exists():
        pools = json.loads(key_path.read_text()).get("pool_sizes", {})
        total = sum(pools.get(k, 0) for k in per_stratum)
        if total:
            def wrate(labels: set[str]) -> float:
                return sum(pools.get(k, 0) / total * sum(v[l] for l in labels) / sum(v.values()) for k, v in per_stratum.items())
            weighted = {"pool_sizes": {k: pools.get(k, 0) for k in per_stratum},
                        "unsupported": round(wrate({"unsupported"}), 4),
                        "not_supported": round(wrate({"unsupported", "partially_supported"}), 4),
                        "note": "stratum rates weighted by pool size; point estimates only (no interval)"}

    # gatekeeper vs human
    gk_levels = ["supported", "partially_supported", "unsupported", "span_not_found", "not_judged", "missing"]
    confusion = {g: {h: 0 for h in ("supported", "partially_supported", "unsupported")} for g in gk_levels}
    for x in rated:
        confusion.setdefault(x["gatekeeper"], {h: 0 for h in ("supported", "partially_supported", "unsupported")})
        confusion[x["gatekeeper"]][x["human"]] += 1
    confusion = {g: v for g, v in confusion.items() if sum(v.values())}

    def pr(gk_pos: set[str], human_pos: set[str]) -> dict:
        tp = sum(1 for x in rated if x["gatekeeper"] in gk_pos and x["human"] in human_pos)
        fp = sum(1 for x in rated if x["gatekeeper"] in gk_pos and x["human"] not in human_pos)
        fn = sum(1 for x in rated if x["gatekeeper"] not in gk_pos and x["human"] in human_pos)
        return {"tp": tp, "fp": fp, "fn": fn, "precision": share(tp, tp + fp), "recall": share(tp, tp + fn)}

    not_sup = {"partially_supported", "unsupported", "span_not_found"}
    calib = {"not_supported_vs_human_not_supported": pr(not_sup, {"partially_supported", "unsupported"}),
             "unsupported_vs_human_unsupported": pr({"unsupported", "span_not_found"}, {"unsupported"})}
    agree = sum(1 for x in rated if (x["gatekeeper"] == "supported") == (x["human"] == "supported"))

    span_ok = float(span.get("span_found_rate") or 0)
    gate = {"automated_span_match": span_ok, "automated_span_match_ok": span_ok >= 0.98,
            "human_unsupported_rate": strict["share"], "human_unsupported_rate_ok": strict["share"] <= args.gate,
            "threshold": args.gate, "complete": not unrated}

    hpo = None
    if Path(args.hpo_sheet).exists():
        hrows = list(csv.DictReader(Path(args.hpo_sheet).open()))
        col = next((k for k in (hrows[0].keys() if hrows else []) if k.startswith("rater_ok")), None)
        filled = [h for h in hrows if col and (h.get(col) or "").strip()]
        if filled:
            ok = [h for h in filled if h[col].strip().lower() in ("yes", "y", "ok", "true")]
            by_method = defaultdict(Counter)
            for h in filled:
                by_method[h["method"]]["yes" if h in ok else "no"] += 1
            hpo = {"rated": len(filled), "of": len(hrows), "accepted": share(len(ok), len(filled)),
                   "by_method": {k: dict(v) for k, v in by_method.items()},
                   "rejected": [{k: h[k] for k in ("n", "pmid", "feature_text_as_stated", "hpo_id", "hpo_label", "method")} | {"note": h.get("rater_note", "")}
                                for h in filled if h not in ok]}

    out = {"run_id": args.run_id, "sheet": args.sheet, "excluded_claims_sensitivity": sorted(excluded), "gatekeeper_file": args.gatekeeper_file, "rated": n, "unrated": unrated,
           "labels": dict(c), "per_stratum": {k: dict(v) for k, v in sorted(per_stratum.items())},
           "unsupported_strict": strict, "not_supported_lenient": lenient, "stratum_weighted": weighted, "q4_gate": gate,
           "gatekeeper_confusion_rows_gatekeeper_cols_human": confusion,
           "gatekeeper_agreement_supported_vs_not": share(agree, n), "gatekeeper_calibration": calib,
           "changed_on_reread": sum(x["changed_on_reread"] for x in rated),
           "disagreements": [x for x in rated if (x["gatekeeper"] == "supported") != (x["human"] == "supported")],
           "not_supported_by_human": [x for x in rated if x["human"] != "supported"],
           "hpo_binding_sample": hpo}
    dest = Path(args.out)
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: out[k] for k in ("rated", "labels", "unsupported_strict", "not_supported_lenient", "stratum_weighted", "q4_gate",
                                           "gatekeeper_agreement_supported_vs_not")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
