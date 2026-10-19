"""Pick the papers for the D-29 re-run (instructions v5 + gatekeeper v3) and estimate its cost.

D-29 (Jimmy, 2026-10-19): re-run about 20 HA20 papers weighted toward cohort
papers, then draw a fresh 50-claim audit from them with a new seed. The papers
are drawn at random from the 85 run-2 papers, by stratum:
  cohort  = study type "case series/cohort" or "review/meta-analysis" (the
            papers with group statements, where the Stage 5 errors came from);
  case    = "case report".
Papers of study type "other" are not drawn. The draw does not look at the
audit sample, the gatekeeper verdicts or any reference data.

Cost estimate, from run-2 session readings (BUDGET.md):
  extraction  run-2 cost $165.80 for 85 papers; each paper's share is taken
              as half by Markdown size and half by its run-2 judged-claim
              count;
  gatekeeper  about $0.0074 per judged claim (the Stage 5 window, $116.81,
              less about $25 for the v4 check and HPO binding, over 12,155
              model claims), times 1.3 for v3's extra step, over all
              non-bookkeeping claims (D-28), using run-2 counts.
These are planning figures, not measurements.

  uv run python analysis/poc/pick_v5_subset.py --seed 29 --cohort 14 --case 6
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path

RUN2 = Path("data/extracted/ha20/poc-ha20-run-2")
MD = Path("data/literature/ha20/fulltext_md")
RUN2_EXTRACTION_USD = 418.07 - 252.27
GK_USD_PER_CLAIM = (116.81 - 25.0) / 12155
GK_V3_FACTOR = 1.3


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--cohort", type=int, default=14)
    ap.add_argument("--case", type=int, default=6)
    ap.add_argument("--out", default="runs/poc-ha20-v5-subset/selection.json")
    args = ap.parse_args(argv)
    manifest = {r["pmid"]: r for r in csv.DictReader(Path("data/literature/ha20/manifest.csv").open())}
    papers = sorted(p.stem for p in (RUN2 / "per_paper").glob("*.json"))
    claims = Counter(r["pmid"] for r in csv.DictReader((RUN2 / "gatekeeper_claims.csv").open()) if r["class"] != "bookkeeping")
    size = {p: (MD / f"{p}.md").stat().st_size for p in papers}
    stratum = {}
    for p in papers:
        t = manifest[p]["study_type"]
        stratum[p] = "cohort" if t in ("case series/cohort", "review/meta-analysis") else "case" if t == "case report" else None
    rng = random.Random(args.seed)
    picked = []
    for s, k in (("cohort", args.cohort), ("case", args.case)):
        pool = sorted(p for p in papers if stratum[p] == s)
        picked += sorted(rng.sample(pool, k))
    tot_size, tot_claims = sum(size.values()), sum(claims.values())

    def extraction_cost(ps):
        return RUN2_EXTRACTION_USD * (0.5 * sum(size[p] for p in ps) / tot_size + 0.5 * sum(claims[p] for p in ps) / tot_claims)

    ext = extraction_cost(picked)
    gk = GK_USD_PER_CLAIM * GK_V3_FACTOR * sum(claims[p] for p in picked)
    out = {"run_id": "poc-ha20-v5-subset", "decision": "D-29", "seed": args.seed,
           "selection_rule": f"random by stratum from the 85 run-2 papers: {args.cohort} cohort/review, {args.case} case reports",
           "pool_sizes": dict(Counter(v for v in stratum.values() if v)),
           "papers": {p: {"stratum": stratum[p], "study_type": manifest[p]["study_type"], "markdown_bytes": size[p],
                          "run2_judged_claims": claims[p]} for p in picked},
           "estimate_usd": {"extraction": round(ext, 2), "gatekeeper_v3": round(gk, 2), "total": round(ext + gk, 2),
                            "basis": "run-2 session readings; planning figures only (see script docstring)"},
           "run2_claims_in_selection": sum(claims[p] for p in picked)}
    dest = Path(args.out)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in ("pool_sizes", "estimate_usd", "run2_claims_in_selection")}, indent=2))
    print(" ".join(picked))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
