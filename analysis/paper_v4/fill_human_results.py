"""Fill the paper's pending human results (\\HR{<id>}) from a JSON file of values.

  python3 -I analysis/paper_v4/fill_human_results.py VALUES.json RUN/latex/human_results.tex

VALUES.json maps ids from reports/paper_v4/materials/pending_human_results.md to LaTeX strings,
e.g. {"o1_unsupported_n": "3", "o1_unsupported_pct": "1.2\\%"}. Ids not in the list are refused;
ids left out stay "pending". The values must come from the scoring scripts' outputs, never typed
from memory. Per-rater results are not paper values and must not go in VALUES.json.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

LIST = Path("reports/paper_v4/materials/pending_human_results.md")
MARK = "% ---- values"


def main() -> int:
    values = json.loads(Path(sys.argv[1]).read_text())
    target = Path(sys.argv[2])
    known = set(re.findall(r"^\| `([a-z0-9_]+)` \|", LIST.read_text(), flags=re.M))
    unknown = sorted(set(values) - known)
    if unknown:
        raise SystemExit(f"ids not in {LIST}: {unknown}")
    head = target.read_text().split(MARK)[0]
    defs = [f"\\makeatletter\\@namedef{{hr@{k}}}{{{v}}}\\makeatother" for k, v in sorted(values.items())]
    target.write_text(head + f"{MARK} ({len(values)} of {len(known)} filled) ----\n" + "\n".join(defs) + "\n")
    print(f"{len(values)} of {len(known)} ids filled; {len(known) - len(values)} still pending")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
