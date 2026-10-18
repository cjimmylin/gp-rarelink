"""Stage 3 cost estimate from the smoke-test run manifest (D-20 route).

Per-paper cost = session usage delta of the smoke run / papers in it. That delta
includes the orchestrating session's own work, so it is an upper bound, and it
is a list-price estimate from session metadata, not a billing figure.

  uv run python analysis/poc/stage3_estimate.py --smoke-run poc-ha20-smoke-1 --disease ha20 --subset 15
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke-run", required=True)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--subset", type=int, default=15, help="papers re-run for the stability check")
    args = ap.parse_args(argv)
    m = json.loads(Path(f"runs/{args.smoke_run}/manifest.json").read_text())
    stats = json.loads(Path(f"data/literature/{args.disease}/corpus_stats.json").read_text())["latest"]
    delta, n = m["notes"]["session_cost_usd_delta"], m["n_documents"]
    per_paper = delta / n
    corpus = stats["n_in_corpus_with_fulltext"]
    out = {
        "smoke_run": args.smoke_run,
        "smoke_session_delta_usd": delta,
        "smoke_papers": n,
        "per_paper_usd_upper_bound": round(per_paper, 2),
        "corpus_papers_with_fulltext": corpus,
        "one_full_run_usd": round(per_paper * corpus, 0),
        "two_full_runs_usd": round(2 * per_paper * corpus, 0),
        "one_run_plus_stability_subset_usd": round(per_paper * (corpus + args.subset), 0),
        "stability_subset_papers": args.subset,
        "note": "Upper bound: the smoke-run delta includes orchestration. Gatekeeper (Stage 5) not included; it is a separate estimate.",
    }
    print(json.dumps(out, indent=2))
    Path(f"runs/{args.smoke_run}/stage3_estimate.json").write_text(json.dumps(out, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
