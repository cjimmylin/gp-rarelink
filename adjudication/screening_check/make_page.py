"""Build the screening-check rating page from make_sample.py's item list.

Injects <out>/screening_check_items.json into page_template.html and writes
<out>/screening_check.html, published as a private claude.ai Artifact with the
`db` capability. Ratings save to the page's store, in two collections:
abstract_check (part A: include / exclude / unsure) and exclusion_check
(part B: agree / disagree / unsure), each doc keyed by item_id with label and note.
Part A shows no screening label, so the rater's judgment is independent.

  uv run python adjudication/screening_check/make_page.py --out <scratch>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    out = Path(args.out)
    items = json.loads((out / "screening_check_items.json").read_text())
    for i in items:
        if i["part"] == "A" and ("reason" in i or "quote" in i):
            raise SystemExit("part A items must not carry screening labels")
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    html = (HERE / "page_template.html").read_text().replace("/*DATA*/[]/*END*/", data)
    (out / "screening_check.html").write_text(html)
    print(json.dumps({"items": len(items), "file": str(out / "screening_check.html"), "bytes": len(html)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
