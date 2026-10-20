"""Stage 1 screening with Claude Code helper agents (D-20); replaces the Haiku call.

Two commands:

  export  Writes every manifest row that has no study_type yet as JSONL batches
          under data/literature/<disease>/screening/work/ (git-ignored, because
          abstracts are publisher text). One line per paper: pmid, title,
          abstract, publication_types, year, journal. Abstracts come from
          PubMed efetch.

  import  Reads the label CSVs the helper agents wrote
          (data/literature/<disease>/screening/labels/*.csv with columns
          pmid, study_type, relevance, reason), validates every value, and
          merges them into manifest.csv:
            study_type, relevance, study_type_method = claude_code,
            in_extraction_corpus = study_type in the in-corpus set AND
                                   relevance in {yes, unclear}.
          A filled study_type_human_check always wins over the label. Writes a
          20-row spot-check sheet (10 included, 10 excluded, seeded) and logs
          the run, including the sha256 of the screening instructions, to
          screening/screening_log.json.

The helper agents follow pipeline/extract/claude_code/prompts/screen_v1.md.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
from datetime import date
from pathlib import Path

from pipeline.extract.corpus.eutils import Client, Unreachable
from pipeline.extract.corpus.pubmed_parse import parse_pubmed_xml

STUDY_TYPES = {"case report", "case series/cohort", "review/meta-analysis", "functional only", "other"}
IN_CORPUS_TYPES = {"case report", "case series/cohort", "review/meta-analysis"}
RELEVANCE = {"yes", "no", "unclear"}
PROMPT = Path("pipeline/extract/claude_code/prompts/screen_v1.md")


def _chunks(xs: list, n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def export(disease: str, batch_size: int) -> int:
    base = Path("data/literature") / disease
    rows = list(csv.DictReader((base / "manifest.csv").open(newline="")))
    todo = [r for r in rows if not r.get("study_type")]
    work = base / "screening" / "work"
    work.mkdir(parents=True, exist_ok=True)
    for old in work.glob("batch_*.jsonl"):
        old.unlink()
    client = Client()
    records: dict[str, dict] = {}
    try:
        for chunk in _chunks([r["pmid"] for r in todo], 200):
            for rec in parse_pubmed_xml(client.efetch_pubmed_xml(chunk)):
                records[rec.pmid] = {"abstract": rec.abstract, "languages": rec.languages}
    except Unreachable as exc:
        raise SystemExit(f"STOP: PubMed unreachable ({exc}).") from exc
    n_batches = 0
    for i, chunk in enumerate(_chunks(todo, batch_size), start=1):
        with (work / f"batch_{i:02d}.jsonl").open("w") as fh:
            for r in chunk:
                extra = records.get(r["pmid"], {})
                fh.write(json.dumps({
                    "pmid": r["pmid"], "title": r["title"], "abstract": extra.get("abstract", ""),
                    "publication_types": r["publication_types"], "year": r["year"], "journal": r["journal"],
                    "languages": extra.get("languages", []),
                }) + "\n")
        n_batches = i
    print(f"exported {len(todo)} rows in {n_batches} batches to {work}")
    return 0


def import_labels(disease: str, seed: int, prompt: Path = PROMPT) -> int:
    base = Path("data/literature") / disease
    manifest = base / "manifest.csv"
    rows = list(csv.DictReader(manifest.open(newline="")))
    cols = list(rows[0].keys())
    if "relevance" not in cols:
        cols.insert(cols.index("study_type_human_check") + 1, "relevance")
    labels: dict[str, dict] = {}
    problems: list[str] = []
    label_files = sorted((base / "screening" / "labels").glob("*.csv"))
    for f in label_files:
        for lab in csv.DictReader(f.open(newline="")):
            pmid = (lab.get("pmid") or "").strip()
            st = (lab.get("study_type") or "").strip().lower()
            rel = (lab.get("relevance") or "").strip().lower()
            if st not in STUDY_TYPES or rel not in RELEVANCE:
                problems.append(f"{f.name}: pmid {pmid}: study_type={st!r} relevance={rel!r}")
                continue
            if pmid in labels and (labels[pmid]["study_type"], labels[pmid]["relevance"]) != (st, rel):
                problems.append(f"{f.name}: pmid {pmid} labelled twice with different values")
            labels[pmid] = {"study_type": st, "relevance": rel, "reason": (lab.get("reason") or "").strip()}
    if problems:
        raise SystemExit("invalid labels, nothing written:\n  " + "\n  ".join(problems))

    missing = [r["pmid"] for r in rows if not r.get("study_type") and r["pmid"] not in labels]
    for r in rows:
        r.setdefault("relevance", "")
        if r.get("study_type_human_check"):
            r["study_type"] = r["study_type_human_check"]
            r["study_type_method"] = "human"
        elif r["pmid"] in labels and not r.get("study_type"):
            lab = labels[r["pmid"]]
            r["study_type"] = lab["study_type"]
            r["relevance"] = lab["relevance"]
            r["study_type_method"] = "claude_code"
            r["notes"] = (r.get("notes", "") + " | screen: " + lab["reason"]).strip(" |")
        if r.get("study_type"):
            r["in_extraction_corpus"] = "true" if (r["study_type"] in IN_CORPUS_TYPES and r.get("relevance") in ("yes", "unclear")) else "false"
    with manifest.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    rng = random.Random(seed)
    inc = [r for r in rows if r.get("in_extraction_corpus") == "true"]
    exc = [r for r in rows if r.get("in_extraction_corpus") == "false"]
    sample = rng.sample(inc, min(10, len(inc))) + rng.sample(exc, min(10, len(exc)))
    with (base / "study_type_spotcheck.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "title", "study_type", "relevance", "in_extraction_corpus", "method",
                    "human_study_type", "human_relevance", "comment"])
        for r in sample:
            w.writerow([r["pmid"], r["title"], r["study_type"], r.get("relevance", ""), r["in_extraction_corpus"],
                        r.get("study_type_method", ""), "", "", ""])

    log_path = base / "screening" / "screening_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {"runs": []}
    log["runs"].append({
        "date": date.today().isoformat(),
        "route": "claude_code (D-20)",
        "prompt_file": str(prompt),
        "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest() if prompt.exists() else None,
        "label_files": [str(f) for f in label_files],
        "n_labels": len(labels),
        "n_rows_still_unlabelled": len(missing),
        "n_in_extraction_corpus": len(inc),
        "spotcheck_seed": seed,
        "spotcheck_design": "10 included + 10 excluded rows, random within each group",
    })
    log_path.write_text(json.dumps(log, indent=2) + "\n")
    print(f"merged {len(labels)} labels; {len(inc)} rows in the extraction corpus; {len(missing)} rows still unlabelled")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--disease", required=True)
    e.add_argument("--batch-size", type=int, default=100)
    i = sub.add_parser("import")
    i.add_argument("--disease", required=True)
    i.add_argument("--seed", type=int, default=20261018)
    i.add_argument("--prompt", default=str(PROMPT), help="screening instructions the helpers followed (logged with its hash)")
    args = ap.parse_args(argv)
    return export(args.disease, args.batch_size) if args.cmd == "export" else import_labels(args.disease, args.seed, Path(args.prompt))


if __name__ == "__main__":
    raise SystemExit(main())
