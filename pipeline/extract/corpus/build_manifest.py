"""Stage 1, step 1: build data/literature/<disease>/manifest.csv.

Inputs (all optional, union taken):
  --seeds   CSV files with columns pmid[,doi,seed_source,note]  (reference lists of reviews, etc.)
  --query   PubMed query string (recorded verbatim in corpus_stats.json)
  --mindate YYYY/MM/DD lower bound on publication date for the query

For every PMID: fetch PubMed metadata, convert IDs (PMCID/DOI), set a provisional
study_type from MeSH publication types, and leave the rest to
classify_study_type.py (model call) and the human spot-check column.

Needs network to NCBI. If the host is unreachable the script stops with a clear
error; it never fills rows from memory.
"""

from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

from pipeline.extract.corpus.eutils import Client, Unreachable
from pipeline.extract.corpus.pubmed_parse import parse_pubmed_xml, study_type_from_pubtypes

MANIFEST_COLUMNS = [
    "pmid", "pmcid", "doi", "first_author", "year", "journal", "title",
    "publication_types", "study_type_provisional", "study_type", "study_type_method",
    "study_type_human_check", "relevance", "in_extraction_corpus",
    "seed_sources", "access_status", "fulltext_format", "retrieved_at", "sha256", "license", "notes",
]
IN_CORPUS_TYPES = {"case report", "case series/cohort", "review/meta-analysis"}


def read_seeds(paths: list[Path]) -> dict[str, dict]:
    seeds: dict[str, dict] = {}
    for p in paths:
        with p.open(newline="") as fh:
            for row in csv.DictReader(fh):
                pmid = (row.get("pmid") or "").strip()
                if not pmid:
                    continue
                src = (row.get("seed_source") or p.stem).strip()
                entry = seeds.setdefault(pmid, {"seed_sources": set(), "doi": "", "notes": ""})
                entry["seed_sources"].add(src)
                if row.get("doi") and not entry["doi"]:
                    entry["doi"] = row["doi"].strip()
                if row.get("note"):
                    entry["notes"] = (entry["notes"] + " | " + row["note"].strip()).strip(" |")
    return seeds


def chunked(xs: list[str], n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True, help="slug, e.g. ha20")
    ap.add_argument("--seeds", nargs="*", type=Path, default=[])
    ap.add_argument("--query", default=None)
    ap.add_argument("--mindate", default=None)
    ap.add_argument("--out-dir", type=Path, default=None)
    args = ap.parse_args(argv)

    out_dir = args.out_dir or Path("data/literature") / args.disease
    out_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_dir / "manifest.csv"

    existing: dict[str, dict] = {}
    if manifest_path.exists():
        with manifest_path.open(newline="") as fh:
            for row in csv.DictReader(fh):
                existing[row["pmid"]] = row

    seeds = read_seeds(args.seeds)
    client = Client()
    query_pmids: list[str] = []
    if args.query:
        try:
            query_pmids = client.esearch_pubmed(args.query, mindate=args.mindate)
        except Unreachable as exc:
            raise SystemExit(f"STOP: PubMed unreachable ({exc}). Run on a networked machine.") from exc
        for pmid in query_pmids:
            seeds.setdefault(pmid, {"seed_sources": set(), "doi": "", "notes": ""})["seed_sources"].add("pubmed_query")

    all_pmids = sorted(set(seeds) | set(existing), key=int)
    new_pmids = [p for p in all_pmids if p not in existing]

    rows: dict[str, dict] = dict(existing)
    for batch in chunked(new_pmids, 100):
        try:
            root = client.efetch_pubmed_xml(batch)
            idmap = {r.get("pmid"): r for r in client.idconv(batch)}
        except Unreachable as exc:
            raise SystemExit(f"STOP: NCBI unreachable ({exc}). Run on a networked machine.") from exc
        for rec in parse_pubmed_xml(root):
            conv = idmap.get(rec.pmid, {})
            prov = study_type_from_pubtypes(rec.publication_types)
            rows[rec.pmid] = {
                "pmid": rec.pmid,
                "pmcid": rec.pmcid or conv.get("pmcid", ""),
                "doi": rec.doi or conv.get("doi", "") or seeds.get(rec.pmid, {}).get("doi", ""),
                "first_author": rec.first_author,
                "year": rec.year,
                "journal": rec.journal,
                "title": rec.title,
                "publication_types": "; ".join(rec.publication_types),
                "study_type_provisional": prov or "",
                "study_type": "",
                "study_type_method": "",
                "study_type_human_check": "",
                "in_extraction_corpus": "",
                "seed_sources": "; ".join(sorted(seeds.get(rec.pmid, {}).get("seed_sources", []))),
                "access_status": "",
                "fulltext_format": "",
                "retrieved_at": "",
                "sha256": "",
                "license": "",
                "notes": seeds.get(rec.pmid, {}).get("notes", ""),
            }
    # seed sources can grow for existing rows
    for pmid, s in seeds.items():
        if pmid in rows and s["seed_sources"]:
            have = set(filter(None, rows[pmid].get("seed_sources", "").split("; ")))
            rows[pmid]["seed_sources"] = "; ".join(sorted(have | s["seed_sources"]))

    with manifest_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=MANIFEST_COLUMNS, extrasaction="ignore")
        w.writeheader()
        for pmid in sorted(rows, key=int):
            w.writerow({c: rows[pmid].get(c, "") for c in MANIFEST_COLUMNS})

    stats_path = out_dir / "corpus_stats.json"
    stats = json.loads(stats_path.read_text()) if stats_path.exists() else {}
    stats.setdefault("build_manifest_runs", []).append({
        "date": date.today().isoformat(),
        "query": args.query,
        "mindate": args.mindate,
        "query_hits": len(query_pmids),
        "seed_files": [str(p) for p in args.seeds],
        "n_rows_total": len(rows),
        "n_rows_new": len(new_pmids),
    })
    stats_path.write_text(json.dumps(stats, indent=2) + "\n")
    print(f"manifest: {manifest_path} ({len(rows)} rows, {len(new_pmids)} new)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
