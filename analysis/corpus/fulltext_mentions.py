"""Add full-text context to title/abstract screening batches (written 2026-11-15, Majeed syndrome).

Sources beyond the PubMed query (Europe PMC full-text search, citations, LitVar,
similar articles) return papers whose title and abstract never name the disease
or gene. For each such record in data/literature/<disease>/screening/work/batch_*.jsonl
that has a PMCID, this fetches the open JATS text from Europe PMC and adds
`fulltext_mentions`: up to --max sentences that contain a term from --terms
(case-insensitive). Records whose title or abstract already contains a term, or
with no open full text, are left as they are (`fulltext_mentions` absent).

The batches are git-ignored (publisher text). The counts go to
screening/fulltext_mentions_log.json. Helpers follow screen_v3.md, which says how
to use the field.

  uv run python analysis/corpus/fulltext_mentions.py --disease majeed --terms majeed lpin2 "lipin-2" "lipin 2" dyserythropoie
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path

from concurrent.futures import ThreadPoolExecutor

import httpx

from pipeline.extract.corpus.eutils import EUROPEPMC

SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\[])")


def text_of(xml: bytes) -> str:
    root = ET.fromstring(xml)
    body = root.find(".//body")
    parts = []
    for el in ([body] if body is not None else []) + root.findall(".//table-wrap") + root.findall(".//supplementary-material"):
        parts.append(" ".join("".join(el.itertext()).split()))
    return " ".join(parts)


def fetch(pmcid: str) -> bytes | None:
    # Europe PMC answers 500 (not 404) when it has no text; a timeout counts as none (logged).
    for _ in range(2):
        try:
            r = httpx.get(f"{EUROPEPMC}/{pmcid}/fullTextXML", timeout=30)
        except httpx.HTTPError:
            continue
        if r.status_code == 200 and r.content.lstrip().startswith(b"<"):
            return r.content
        if r.status_code in (404, 500):
            return None
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    ap.add_argument("--terms", nargs="+", required=True)
    ap.add_argument("--max", type=int, default=5)
    a = ap.parse_args()
    base = Path("data/literature") / a.disease
    pmcid = {r["pmid"]: r["pmcid"] for r in csv.DictReader((base / "manifest.csv").open())}
    pat = re.compile("|".join(re.escape(t) for t in a.terms), re.I)
    n = {"records": 0, "term_in_title_abstract": 0, "no_pmcid": 0, "no_fulltext": 0, "fulltext_no_term": 0, "with_mentions": 0}
    for f in sorted((base / "screening" / "work").glob("batch_*.jsonl")):
        recs = [json.loads(line) for line in f.open()]
        todo = []
        for r in recs:
            n["records"] += 1
            if "fulltext_mentions" in r or r.get("fulltext_checked"):  # resumed run: done already
                n["already_done"] = n.get("already_done", 0) + 1
            elif pat.search(r["title"] + " " + (r.get("abstract") or "")):
                n["term_in_title_abstract"] += 1
            elif not pmcid.get(r["pmid"]):
                n["no_pmcid"] += 1
            else:
                todo.append(r)
        with ThreadPoolExecutor(6) as ex:
            xmls = list(ex.map(lambda r: fetch(pmcid[r["pmid"]]), todo))
        for r, xml in zip(todo, xmls):
            r["fulltext_checked"] = True
            if not xml:
                n["no_fulltext"] += 1
                continue
            try:
                sents = [s for s in SENT.split(text_of(xml)) if pat.search(s)]
            except ET.ParseError:
                n["no_fulltext"] += 1
                continue
            if not sents:
                n["fulltext_no_term"] += 1
                r["fulltext_mentions"] = []
                continue
            n["with_mentions"] += 1
            r["fulltext_mentions"] = [s[:600] for s in sents[: a.max]]
            r["fulltext_mentions_total"] = len(sents)
        f.write_text("".join(json.dumps(r) + "\n" for r in recs))
        print(f.name, n, flush=True)
    log = base / "screening" / "fulltext_mentions_log.json"
    log.write_text(json.dumps({"date": date.today().isoformat(), "terms": a.terms, "max_sentences": a.max, "counts": n}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
