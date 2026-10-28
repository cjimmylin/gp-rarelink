"""Choose which sampled papers the locate-and-judge helpers judge, within the D-44 ceiling.

The design (reports/sliders_ablation_design.md §4.1) planned one judge helper per paper on all
116 papers. The three pilot judge helpers cost $0.76-1.60 each (mean about $1.18), so the full
run (about $137) on top of arm D's extraction ($197.34) would pass the $300 ceiling. This script
draws, by seed, the subset that fits: every SSADH paper (the non-development disease), the two
hand-picked HA20 pilot papers, and a seeded random subset of the other HA20 papers. The rest of
HA20 waits on Jimmy's answer about the ceiling. Writes judge/paper_subset.json.

Usage: uv run python analysis/sliders_ablation/judge_paper_subset.py --seed 42283 --ha20-n 30
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import random
from pathlib import Path

JUDGE = Path("adjudication/sliders_ablation/judge")
PILOT = {"ha20": ["37324276", "40574834"], "ssadh": ["14635103"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--ha20-n", type=int, required=True, help="HA20 papers drawn at random, besides the two pilot papers")
    args = ap.parse_args(argv)
    out_path = JUDGE / "paper_subset.json"
    if out_path.exists():
        raise SystemExit(f"{out_path} exists; the subset is drawn once")
    chunks = {d: sorted(p.stem.split("_", 1)[1] for p in JUDGE.glob(f"chunks/{d}_*.csv")) for d in ("ha20", "ssadh")}
    rng = random.Random(args.seed)
    ha20_rest = [p for p in chunks["ha20"] if p not in PILOT["ha20"]]
    drawn = sorted(rng.sample(ha20_rest, args.ha20_n))
    subset = {
        "seed": args.seed,
        "drawn_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "reason": "pilot judge helpers cost about $1.18 each; the full 116-paper judge would pass the $300 ceiling (D-44)",
        "pilot_papers_hand_picked": PILOT,
        "ssadh": {"judged": chunks["ssadh"], "deferred": []},
        "ha20": {"judged": sorted(set(PILOT["ha20"]) | set(drawn)), "random_draw": drawn,
                 "deferred": sorted(set(ha20_rest) - set(drawn))},
    }
    out_path.write_text(json.dumps(subset, indent=1) + "\n")
    print(json.dumps({d: {"judged": len(subset[d]["judged"]), "deferred": len(subset[d]["deferred"])} for d in ("ha20", "ssadh")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
