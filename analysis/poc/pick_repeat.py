"""Pick the papers for the Stage 3 repeat run (D-21: one full run plus a 15-paper repeat).

Draws N papers at random, with a fixed recorded seed, from the run-1 papers that
have at least one individual row. Papers with no individual rows (reviews without
patient-level data, off-topic papers) are left out of the draw because they would
agree trivially and say nothing about stability. The draw is reproducible:
same run-1 outputs and seed give the same list.

Writes runs/<repeat_run_id>/selection.json and prints the list.

  uv run python analysis/poc/pick_repeat.py --disease ha20 --run-id poc-ha20-run-1 \
      --repeat-run-id poc-ha20-run-1-repeat --n 15 --seed 20261018
"""

from __future__ import annotations

import argparse
import json
import random
from datetime import date
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--repeat-run-id", required=True)
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--seed", type=int, default=20261018)
    args = ap.parse_args(argv)
    per = Path("data/extracted") / args.disease / args.run_id / "per_paper"
    eligible = sorted(p.stem for p in per.glob("*.json")
                      if (json.loads(p.read_text()).get("tables") or {}).get("individuals"))
    picked = sorted(random.Random(args.seed).sample(eligible, min(args.n, len(eligible))))
    out = {
        "repeat_run_id": args.repeat_run_id, "source_run_id": args.run_id, "date": date.today().isoformat(),
        "seed": args.seed, "n": len(picked), "eligible_rule": "source-run papers with at least one individual row",
        "n_eligible": len(eligible), "selected": picked,
    }
    dest = Path("runs") / args.repeat_run_id
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "selection.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
