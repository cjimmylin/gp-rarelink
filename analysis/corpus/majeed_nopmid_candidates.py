"""Records with no PMID whose title names Majeed syndrome or LPIN2 (2026-11-15).

Reads data/literature/majeed/seeds/*_nopmid.csv (Europe PMC, OpenAlex), keeps rows
whose title matches the disease or gene, removes duplicates by DOI or normalised
title, and writes data/literature/majeed/nopmid_candidates.csv for hand review.
These are outside PubMed (regional journals, preprints, conference abstracts,
dissertations, book chapters); they were not screened by the helpers.

  python3 analysis/corpus/majeed_nopmid_candidates.py
"""
import csv
import re
from pathlib import Path

BASE = Path("data/literature/majeed")
PAT = re.compile(r"majeed|lpin2|lipin.?2", re.I)
out: dict[str, dict] = {}
for f in sorted((BASE / "seeds").glob("*_nopmid.csv")):
    for r in csv.DictReader(f.open()):
        title = (r.get("title") or "").strip()
        if not PAT.search(title):
            continue
        doi = (r.get("doi") or "").lower().replace("https://doi.org/", "")
        key = doi or re.sub(r"\W+", " ", title.lower()).strip()
        row = out.setdefault(key, {"title": title, "doi": doi, "year": r.get("year", ""),
                                   "venue": r.get("venue") or r.get("journal") or "",
                                   "type": r.get("type") or r.get("source") or "",
                                   "ids": set(), "found_by": set()})
        row["ids"].add(r.get("openalex") or f"{r.get('source', '')}:{r.get('id', '')}")
        row["found_by"].add(f.name.replace("_nopmid.csv", ""))
with (BASE / "nopmid_candidates.csv").open("w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=["title", "year", "venue", "type", "doi", "ids", "found_by", "hand_review"])
    w.writeheader()
    for row in sorted(out.values(), key=lambda r: (str(r["year"]), r["title"])):
        w.writerow({**row, "ids": "; ".join(sorted(row["ids"])), "found_by": "; ".join(sorted(row["found_by"])), "hand_review": ""})
print(f"{len(out)} candidates -> {BASE / 'nopmid_candidates.csv'}")
