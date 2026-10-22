"""Check a disease checklist written from its key review(s) (D-38; checklist_from_review_v1.md).

Checks, for configs/checklists/<disease>.json:
  - exactly 20 entries with distinct, non-empty names and no ';' in a name;
  - every entry has at least one quote;
  - every quote occurs verbatim in its source review's Markdown
    (data/literature/<disease>/fulltext_md/<pmid>.md). A quote is either a string
    (the single source in "source_pmid") or {"pmid": ..., "text": ...}.

  uv run python -m pipeline.extract.claude_code.check_checklist --disease ssadh
Exit code 1 if any check fails.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def check(disease: str) -> list[str]:
    d = json.loads(Path(f"configs/checklists/{disease}.json").read_text())
    pmids = [p.strip() for p in str(d["source_pmid"]).split(";") if p.strip()]
    texts = {p: Path(f"data/literature/{disease}/fulltext_md/{p}.md").read_text(encoding="utf-8") for p in pmids}
    problems = []
    items = d["checklist"]
    names = [x.get("name", "").strip() for x in items]
    if len(items) != 20:
        problems.append(f"{len(items)} entries, not 20")
    if len(set(names)) != len(names) or any(not n or ";" in n for n in names):
        problems.append("names must be distinct, non-empty and free of ';'")
    for x in items:
        quotes = x.get("quotes") or []
        if not quotes:
            problems.append(f"{x.get('name')}: no quote")
        for q in quotes:
            pmid, text = (q["pmid"], q["text"]) if isinstance(q, dict) else (pmids[0] if len(pmids) == 1 else None, q)
            if pmid not in texts:
                problems.append(f"{x.get('name')}: quote names no known source ({pmid})")
            elif text not in texts[pmid]:
                problems.append(f"{x.get('name')}: quote not found verbatim in {pmid}: {text[:80]!r}")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    args = ap.parse_args(argv)
    problems = check(args.disease)
    print(json.dumps({"disease": args.disease, "problems": problems, "ok": not problems}, indent=2))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
