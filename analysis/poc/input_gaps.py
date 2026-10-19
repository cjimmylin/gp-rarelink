"""Input gaps that limit extraction regardless of the model (Stage 3b report, §7).

For the papers of one run (runs/<run_id>/manifest.json), counts:
  - tables in the JATS XML that are images only (a <table-wrap> with a
    <graphic> and no <table>), by paper;
  - supplementary-file outcomes from data/literature/<disease>/supplementary/
    manifest.csv (fetch) and conversion.csv (relevance filter and appending),
    by status, with the papers for each status.

Writes analysis/poc/input_gaps_<run_id>.json and prints the totals.

  uv run python analysis/poc/input_gaps.py --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

TABLE_WRAP = re.compile(r"<table-wrap\b.*?</table-wrap>", re.S)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    docs = [str(x) for x in json.loads((Path("runs") / args.run_id / "manifest.json").read_text())["notes"]["documents"]]
    n_tables, image_only = 0, defaultdict(int)
    for pmid in docs:
        xml = (base / "fulltext" / f"{pmid}.nxml").read_text(encoding="utf-8", errors="ignore")
        for m in TABLE_WRAP.finditer(xml):
            n_tables += 1
            body = m.group(0).replace("<table-wrap", "")
            if "<table" not in body and "<graphic" in body:
                image_only[pmid] += 1
    fetch, conv = defaultdict(set), defaultdict(set)
    man = base / "supplementary" / "manifest.csv"
    if man.exists():
        for r in csv.DictReader(man.open()):
            if r["pmid"] in docs:
                fetch[r["status"]].add(r["pmid"])
    cv = base / "supplementary" / "conversion.csv"
    if cv.exists():
        for r in csv.DictReader(cv.open()):
            if r["pmid"] in docs:
                conv[r["status"]].add(r["pmid"])
    appended = conv.get("included_full", set()) | conv.get("included_excerpt", set())
    out = {
        "run_id": args.run_id,
        "papers": len(docs),
        "tables_in_xml": n_tables,
        "image_only_tables": sum(image_only.values()),
        "papers_with_image_only_tables": dict(sorted(image_only.items())),
        "supplementary_fetch_status_papers": {k: sorted(v) for k, v in sorted(fetch.items())},
        "supplementary_conversion_status_papers": {k: sorted(v) for k, v in sorted(conv.items())},
        "papers_with_supplementary_text_appended": len(appended),
    }
    (Path("analysis/poc") / f"input_gaps_{args.run_id}.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({"papers": out["papers"], "tables_in_xml": n_tables, "image_only_tables": out["image_only_tables"],
                      "papers_with_image_only_tables": out["papers_with_image_only_tables"],
                      "fetch_status_paper_counts": {k: len(v) for k, v in fetch.items()},
                      "conversion_status_paper_counts": {k: len(v) for k, v in conv.items()},
                      "papers_with_supplementary_text_appended": len(appended)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
