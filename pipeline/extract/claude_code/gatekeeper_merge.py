"""Merge the Stage 5 gatekeeper verdicts for one run (POC_DESIGN.md §3.9; D-25).

Inputs, under data/extracted/<disease>/<run_id>/:
  gatekeeper_claims.csv   every claim with its class (gatekeeper_prep.py)
  gatekeeper_prep.json    the chunk list
  gatekeeper/<chunk>.csv  one helper's verdicts per chunk (claim_id, verdict, reason)

Each claim gets one verdict and a source:
  bookkeeping   not judged (pmid fields, labels repeated in child tables);
  verbatim      supported by construction (source "script"): the value occurs
                inside its own span, and the span is verbatim in the paper;
  model         the helper's verdict (source "gatekeeper").

The script fails if a chunk file is missing, a model claim has no verdict or
more than one, a verdict names a claim outside its chunk, or a verdict is not
one of the four allowed values. With --allow-missing it reports missing chunks
and leaves their claims as "not judged yet" (for progress checks only).

Writes:
  gatekeeper.csv          one row per claim (claim_id, pmid, table, row, field,
                          value, class, verdict, source, reason)
  gatekeeper_summary.json counts by verdict, overall and by class, field and
                          paper; the unsupported share with exact (Clopper-
                          Pearson) 95% intervals; and every claim not supported,
                          with its reason.

The shares are the gatekeeper's own reading. The pre-registered false-positive
metric is the human audit of 50 claims (analysis/poc/audit_metrics.py), which
also calibrates these verdicts.

  uv run python -m pipeline.extract.claude_code.gatekeeper_merge --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

VERDICTS = ("supported", "partially_supported", "unsupported", "span_not_found")


def binom_cdf(k: int, n: int, p: float) -> float:
    """P(X <= k) for X ~ Binomial(n, p), summed in log space (no scipy in the uv project)."""
    if k < 0:
        return 0.0
    if k >= n or p <= 0.0:
        return 1.0
    if p >= 1.0:
        return 0.0
    lp, lq = math.log(p), math.log1p(-p)
    terms = [math.lgamma(n + 1) - math.lgamma(i + 1) - math.lgamma(n - i + 1) + i * lp + (n - i) * lq for i in range(k + 1)]
    m = max(terms)
    return min(1.0, math.exp(m) * sum(math.exp(t - m) for t in terms))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float] | None:
    """Exact two-sided interval by bisection on the binomial tails."""
    if n == 0:
        return None

    def solve(f, target: float) -> float:  # f decreasing in p
        lo, hi = 0.0, 1.0
        for _ in range(200):
            mid = (lo + hi) / 2
            if f(mid) > target:
                lo = mid
            else:
                hi = mid
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(lambda p: binom_cdf(k - 1, n, p), 1.0 - alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: binom_cdf(k, n, p), alpha / 2)
    return round(lower, 6), round(upper, 6)


def share(k: int, n: int) -> dict:
    ci = clopper_pearson(k, n)
    return {"k": k, "n": n, "share": round(k / n, 6) if n else None, "ci95": ci}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--allow-missing", action="store_true")
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    claims = list(csv.DictReader((run_dir / "gatekeeper_claims.csv").open()))
    prep = json.loads((run_dir / "gatekeeper_prep.json").read_text())
    by_id = {c["claim_id"]: c for c in claims}
    model_ids = {c["claim_id"] for c in claims if c["class"] == "model"}
    verdicts: dict[str, tuple[str, str]] = {}
    problems, missing_chunks = [], []
    for ch in prep["chunk_list"]:
        path = run_dir / "gatekeeper" / f"{ch['chunk']}.csv"
        if not path.exists():
            missing_chunks.append(ch["chunk"])
            continue
        rows = list(csv.DictReader(path.open()))
        seen = Counter(r["claim_id"].strip() for r in rows)
        if len(rows) != ch["claims"]:
            problems.append(f"{ch['chunk']}: {len(rows)} rows for {ch['claims']} claims")
        for cid, k in seen.items():
            if k > 1:
                problems.append(f"{ch['chunk']}: {cid} judged {k} times")
        for r in rows:
            cid, verdict = r["claim_id"].strip(), r["verdict"].strip().lower()
            if cid not in model_ids or by_id[cid]["pmid"] != ch["pmid"]:
                problems.append(f"{ch['chunk']}: {cid} is not a model claim of this paper")
                continue
            if verdict not in VERDICTS:
                problems.append(f"{ch['chunk']}: {cid} has verdict {verdict!r}")
                continue
            if cid in verdicts:
                problems.append(f"{cid} judged in two chunks")
            verdicts[cid] = (verdict, (r.get("reason") or "").strip())
    missing_chunk_pmids = {ch["pmid"] for ch in prep["chunk_list"] if ch["chunk"] in missing_chunks}
    unjudged = sorted(model_ids - set(verdicts))
    if missing_chunks and not args.allow_missing:
        problems.append(f"missing chunk files: {', '.join(missing_chunks)}")
    if not args.allow_missing and unjudged:
        problems.append(f"{len(unjudged)} model claims without a verdict")
    if problems:
        raise SystemExit("gatekeeper merge failed:\n  " + "\n  ".join(problems[:50]))

    out, c = [], Counter()
    by_class, by_field, by_paper = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    flagged = []
    for cl in claims:
        cid, kind = cl["claim_id"], cl["class"]
        if kind == "bookkeeping":
            verdict, source, reason = "not_judged", "bookkeeping", ""
        elif kind == "verbatim":
            verdict, source, reason = "supported", "script", "value occurs inside its verbatim span"
        elif cid in verdicts:
            verdict, source = "gatekeeper", "gatekeeper"
            verdict, reason = verdicts[cid]
        else:
            verdict, source, reason = "not_judged_yet", "missing", ""
        out.append({**{k: cl[k] for k in ("claim_id", "pmid", "table", "row", "field", "value", "class")},
                    "verdict": verdict, "source": source, "reason": reason})
        c[verdict] += 1
        by_class[kind][verdict] += 1
        if kind != "bookkeeping":
            by_field[f"{cl['table']}.{cl['field']}"][verdict] += 1
            by_paper[cl["pmid"]][verdict] += 1
        if verdict in ("partially_supported", "unsupported", "span_not_found"):
            flagged.append({k: out[-1][k] for k in ("claim_id", "pmid", "table", "row", "field", "value", "verdict", "reason")})

    with (run_dir / "gatekeeper.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)

    def rates(cnt: Counter) -> dict:
        n = sum(v for k, v in cnt.items() if k in VERDICTS)
        strict = cnt["unsupported"] + cnt["span_not_found"]
        return {"judged": n, "unsupported_or_not_found": share(strict, n),
                "not_supported": share(strict + cnt["partially_supported"], n)}

    judged_values = Counter()
    for kind in ("verbatim", "model"):
        judged_values.update(by_class[kind])
    summary = {
        "run_id": args.run_id, "claims": len(claims), "verdicts": dict(c),
        "by_class": {k: dict(v) for k, v in by_class.items()},
        "rates_all_values": rates(judged_values),
        "rates_model_claims": rates(by_class["model"]),
        "denominators": "all_values = verbatim + model claims (bookkeeping not counted); "
                        "model_claims = the claims the helpers judged. 'unsupported_or_not_found' counts "
                        "unsupported and span_not_found; 'not_supported' adds partially_supported. Exact 95% intervals.",
        "missing_chunks": missing_chunks, "missing_chunk_pmids": sorted(missing_chunk_pmids),
        "model_claims_not_judged_yet": len(unjudged),
        "by_field": {k: dict(v) for k, v in sorted(by_field.items(), key=lambda kv: -sum(kv[1].values()))},
        "by_paper": {k: dict(v) for k, v in sorted(by_paper.items())},
        "flagged": flagged,
    }
    (run_dir / "gatekeeper_summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({k: summary[k] for k in ("claims", "verdicts", "rates_all_values", "rates_model_claims",
                                               "missing_chunks", "model_claims_not_judged_yet")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
