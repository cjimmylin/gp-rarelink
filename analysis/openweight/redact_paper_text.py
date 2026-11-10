"""Remove the full text of papers from the open-weight run transcripts (D-46, 2026-11-10).

The open-weight agent (`pipeline/extract/openweight/agent.py`) stores the whole conversation of each run in
`runs/ow-<d>/transcripts/<pmid>.json`, including every tool result. The results of `read_file` and `grep` calls on
`data/literature/<d>/fulltext_md/<pmid>.md` therefore held the paper's full text, a copy of the git-ignored corpus.
Most of those papers are not under a Creative Commons license (PMC's "text mining only" terms, or no license
recorded), so they must not be redistributed in a public repository.

This script replaces each such tool result with a one-line placeholder that keeps the tool, the path, the length
and the sha256 of the removed text, so a re-fetched paper can be checked against the record. Nothing else in a
transcript changes: the model's own messages, tool calls, the extraction outputs it wrote, usage and timing stay.
The scripts that read transcripts (`analysis/openweight/summary.py`, `make_manifest.py`) use only `result`,
which is untouched. Running it twice changes nothing. `--check` exits 1 if any paper text is still present.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATE = "2026-11-10"
MARK = "[paper text removed"
PAPER_PATH = re.compile(r"/data/literature/[^/]+/(fulltext|supplementary)")  # paths whose contents are the paper's text
TOOLS = ("read_file", "grep")


def transcripts() -> list[Path]:
    out = sorted((ROOT / "runs").glob("ow-*/transcripts/*.json"))
    # failed attempts are kept as <pmid>.transcript.json or <pmid>.transcript.attempt<n>.json
    out += sorted(f for f in (ROOT / "runs").glob("ow-*/failed_attempts/*.json") if ".transcript" in f.name)
    return out


def redact(d: dict, rel: str) -> tuple[int, int]:
    """Redact in place; return (tool results removed now, characters removed now)."""
    calls: dict[str, tuple[str, dict]] = {}
    for m in d.get("messages", []):
        for c in m.get("tool_calls") or []:
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = {}
            calls[c["id"]] = (c["function"]["name"], args if isinstance(args, dict) else {})
    n = chars = 0
    for m in d.get("messages", []):
        if m.get("role") != "tool":
            continue
        name, args = calls.get(m.get("tool_call_id"), ("?", {}))
        path = str(args.get("path") or "")
        if name not in TOOLS or not PAPER_PATH.search(path):
            continue
        content = m.get("content")
        if not isinstance(content, str) or content.startswith(MARK) or content.startswith("ERROR:") or content == "(no matches)":
            continue
        short = path.split("/gp-rarelink/")[-1]
        digest = hashlib.sha256(content.encode("utf-8")).hexdigest()
        m["content"] = (f"{MARK} {DATE} before the repository was made public (D-46): {name} {short}"
                        f"{' offset ' + str(args['offset']) if args.get('offset') else ''}"
                        f"{' limit ' + str(args['limit']) if args.get('limit') else ''}"
                        f"{' pattern ' + json.dumps(args['pattern']) if name == 'grep' else ''}"
                        f", {len(content)} characters, sha256 {digest}; the paper is re-fetchable with the pipeline's fetch tooling]")
        n += 1
        chars += len(content)
    if n:
        r = d.setdefault("redaction", {"date": DATE, "decision": "D-46", "script": "analysis/openweight/redact_paper_text.py",
                                       "tool_results_removed": 0, "characters_removed": 0,
                                       "note": "Tool results that returned paper text were replaced by placeholders carrying the sha256 of the removed text."})
        r["tool_results_removed"] += n
        r["characters_removed"] += chars
    return n, chars


def remaining(d: dict) -> int:
    """Tool results on paper paths that still carry text (for --check)."""
    calls = {c["id"]: c["function"] for m in d.get("messages", []) for c in (m.get("tool_calls") or [])}
    k = 0
    for m in d.get("messages", []):
        if m.get("role") != "tool":
            continue
        f = calls.get(m.get("tool_call_id"))
        if not f or f["name"] not in TOOLS:
            continue
        try:
            path = str(json.loads(f.get("arguments") or "{}").get("path") or "")
        except (json.JSONDecodeError, AttributeError):
            path = ""
        c = m.get("content")
        if PAPER_PATH.search(path) and isinstance(c, str) and not (c.startswith(MARK) or c.startswith("ERROR:") or c == "(no matches)"):
            k += 1
    return k


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--check", action="store_true", help="report only; exit 1 if any paper text remains")
    a = ap.parse_args()
    files = transcripts()
    tot_n = tot_c = left = changed = 0
    for f in files:
        raw = f.read_text(encoding="utf-8")
        d = json.loads(raw)
        rel = str(f.relative_to(ROOT))
        if a.check:
            k = remaining(d)
            left += k
            if k:
                print(f"{rel}: {k} tool results still hold paper text")
            continue
        n, c = redact(d, rel)
        if n:
            f.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
            changed += 1
        tot_n += n
        tot_c += c
    if a.check:
        print(f"{len(files)} transcripts checked; {left} tool results with paper text remain")
        return 1 if left else 0
    print(f"{len(files)} transcripts; {changed} files changed; {tot_n} tool results replaced; {tot_c:,} characters removed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
