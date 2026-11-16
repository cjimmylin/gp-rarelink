"""Build the eight raters' audit calibration pages (D-55) as local files.

Every rater gets the same 40 calibration claims, in an order of their own (a shuffle seeded
by the private seed of the first draw and the rater's label), on a page with its own store
key, so no rater's ratings can mix with another's. The pages carry no reference label and no
gatekeeper information. They are written to the git-ignored private folder; publishing them
is a separate step that needs Jimmy's word.

  uv run python analysis/assessment_plan/calibration_pages.py

Reads adjudication/calibration/private/calibration_set/sample.csv (written by
calibration_reference.py). Raters are R1 to R8; names stay with Jimmy.
"""
from __future__ import annotations

import csv
import hashlib
import json
import random
import subprocess
import sys
from pathlib import Path

PRIV = Path("adjudication/calibration/private")
RATERS = [f"R{i}" for i in range(1, 9)]


def main() -> int:
    rows = list(csv.DictReader((PRIV / "calibration_set/sample.csv").open(newline="")))
    seed = (PRIV / "audit_candidates/seed.txt").read_text().strip()
    out = {"claims": len(rows), "raters": RATERS, "pages": {}}
    for r in RATERS:
        order = rows[:]
        random.Random(f"{seed}:{r}").shuffle(order)
        d = PRIV / "raters" / r
        d.mkdir(parents=True, exist_ok=True)
        with (d / "sample.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for n, x in enumerate(order, 1):
                w.writerow({**x, "n": n})
        page = PRIV / "pages" / f"o1cal_{r}.html"
        res = subprocess.run([sys.executable, "adjudication/o1_audit/make_rating_page.py", "--rater", r, "--sample-dir", str(d),
                              "--store-prefix", "o1cal", "--title", f"Calibration claims, rater {r}", "--tab-title", f"Calibration Rater {r}",
                              "--out", str(page)], capture_output=True, text=True, check=True)
        info = json.loads(res.stdout[res.stdout.index("{"):])
        out["pages"][r] = {"file": str(page), "claims": info["claims"], "quote_parts_not_located": info["quote_parts_not_located"],
                           "store_key": f"o1cal-rater-{r}-v1", "first_items": [x["item_id"] for x in order[:3]],
                           "sha256": hashlib.sha256(page.read_bytes()).hexdigest()}
    print(json.dumps({r: {k: v for k, v in p.items() if k != "sha256"} for r, p in out["pages"].items()}, indent=1))
    (PRIV / "raters" / "pages.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
