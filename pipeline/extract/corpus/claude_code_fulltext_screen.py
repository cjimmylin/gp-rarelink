"""Full-text screening with Claude Code helper agents (D-20): pre-registration §5.1.

Two commands:

  export  Lists every manifest row that passed title/abstract screening
          (in_extraction_corpus = true) and has converted full text
          (fulltext_md/<pmid>.md) and no full-text decision yet, in batches:
          data/literature/<disease>/screening_fulltext/work/batch_NN.txt, one
          Markdown path per line (git-ignored folder; paths only).

  import  Reads the helpers' label CSVs (screening_fulltext/labels/*.csv; columns
          as in screen_fulltext_v1.md), validates every value, checks that each
          evidence_quote occurs verbatim in its Markdown file (whitespace
          normalized), and writes to manifest.csv:
            fulltext_screen         include | exclude | not_accessible
            fulltext_screen_reason  exclusion reason, if excluded
            fulltext_study_type, fulltext_n_individuals, fulltext_has_genotype,
            fulltext_literature_table, fulltext_quote_found
          Rows in the corpus without full text get not_accessible. A quote that is
          not found stops the import unless --allow-missing-quotes is given (it is
          then logged and flagged per row). in_extraction_corpus is not changed:
          the extraction set is in_extraction_corpus = true AND
          fulltext_screen = include. Logs the run, with the instructions' sha256,
          to screening_fulltext/screening_log.json.

The helpers follow pipeline/extract/claude_code/prompts/screen_fulltext_v1.md.

  uv run python -m pipeline.extract.corpus.claude_code_fulltext_screen export --disease axd
  uv run python -m pipeline.extract.corpus.claude_code_fulltext_screen import --disease axd
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

PROMPT = Path("pipeline/extract/claude_code/prompts/screen_fulltext_v1.md")
DECISIONS = {"include", "exclude"}
REASONS = {"not_disease", "no_individual_data", "review_no_new_individuals", "functional_only", "not_english", "unusable_text"}
STUDY_TYPES = {"case report", "case series/cohort", "review/meta-analysis", "functional only", "other"}
YESNO = {"yes", "no"}
NEW_COLS = ["fulltext_screen", "fulltext_screen_reason", "fulltext_study_type", "fulltext_n_individuals",
            "fulltext_has_genotype", "fulltext_literature_table", "fulltext_quote_found"]


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def export(disease: str, batch_size: int, max_tokens: int = 100_000, prefix_start: int = 1) -> int:
    base = Path("data/literature") / disease
    rows = list(csv.DictReader((base / "manifest.csv").open(newline="")))
    md = base / "fulltext_md"
    todo = [r for r in rows if r["in_extraction_corpus"].lower() == "true" and not r.get("fulltext_screen")
            and (md / f"{r['pmid']}.md").exists()]
    work = base / "screening_fulltext" / "work"
    work.mkdir(parents=True, exist_ok=True)
    if prefix_start == 1:  # a fresh export replaces old batch lists; a later wave numbers on
        for old in work.glob("batch_*.txt"):
            old.unlink()
    def tokens(pmid: str) -> int:
        m = md / f"{pmid}.meta.json"
        return int(json.loads(m.read_text()).get("tokens") or 0) if m.exists() else 0

    batches: list[list[str]] = [[]]
    size = 0
    for r in todo:  # close a batch at batch_size papers or max_tokens tokens
        t = tokens(r["pmid"])
        if batches[-1] and (len(batches[-1]) >= batch_size or size + t > max_tokens):
            batches.append([])
            size = 0
        batches[-1].append(str((md / f"{r['pmid']}.md").resolve()))
        size += t
    batches = [b for b in batches if b]
    for n, b in enumerate(batches, start=prefix_start):
        (work / f"batch_{n:02d}.txt").write_text("\n".join(b) + "\n")
    print(json.dumps({"disease": disease, "papers": len(todo), "batches": len(batches), "dir": str(work)}))
    return 0


def import_labels(disease: str, prompt: Path, allow_missing_quotes: bool) -> int:
    base = Path("data/literature") / disease
    manifest = base / "manifest.csv"
    rows = list(csv.DictReader(manifest.open(newline="")))
    cols = list(rows[0].keys())
    for c in NEW_COLS:
        if c not in cols:
            cols.insert(cols.index("notes"), c)
    labels: dict[str, dict] = {}
    problems: list[str] = []
    label_files = sorted((base / "screening_fulltext" / "labels").glob("*.csv"))
    for f in label_files:
        for lab in csv.DictReader(f.open(newline="")):
            lab = {k: (v or "").strip() for k, v in lab.items() if k}
            pmid, dec, why = lab.get("pmid", ""), lab.get("decision", "").lower(), lab.get("exclusion_reason", "").lower()
            st, n = lab.get("study_type", "").lower(), lab.get("n_individuals", "").lower()
            ok = (dec in DECISIONS and (why in REASONS if dec == "exclude" else why == "")
                  and st in STUDY_TYPES and (n.isdigit() or n == "unclear")
                  and lab.get("has_genotype", "").lower() in YESNO and lab.get("literature_table", "").lower() in YESNO
                  and lab.get("evidence_quote"))
            if not ok:
                problems.append(f"{f.name}: pmid {pmid}: {dec!r} {why!r} {st!r} n={n!r} "
                                f"gen={lab.get('has_genotype')!r} lit={lab.get('literature_table')!r} quote={'yes' if lab.get('evidence_quote') else 'empty'}")
                continue
            if pmid in labels:
                problems.append(f"{f.name}: pmid {pmid} labelled twice")
            labels[pmid] = lab
    if problems:
        raise SystemExit("invalid labels, nothing written:\n  " + "\n  ".join(problems))

    missing_quotes = []
    for pmid, lab in labels.items():
        path = base / "fulltext_md" / f"{pmid}.md"
        found = path.exists() and norm(lab["evidence_quote"]) in norm(path.read_text())
        lab["_found"] = "true" if found else "false"
        if not found:
            missing_quotes.append(pmid)
    if missing_quotes and not allow_missing_quotes:
        raise SystemExit(f"evidence_quote not found verbatim for {len(missing_quotes)} papers, nothing written: {missing_quotes}")

    in_corpus = [r for r in rows if r["in_extraction_corpus"].lower() == "true"]
    unlabelled = []
    for r in rows:
        for c in NEW_COLS:
            r.setdefault(c, "")
        if r["in_extraction_corpus"].lower() != "true":
            continue
        lab = labels.get(r["pmid"])
        if lab:
            r.update(fulltext_screen=lab["decision"].lower(), fulltext_screen_reason=lab["exclusion_reason"].lower(),
                     fulltext_study_type=lab["study_type"].lower(), fulltext_n_individuals=lab["n_individuals"].lower(),
                     fulltext_has_genotype=lab["has_genotype"].lower(), fulltext_literature_table=lab["literature_table"].lower(),
                     fulltext_quote_found=lab["_found"])
            note = f"full-text screen: {lab['decision'].lower()}" + (f" ({lab['exclusion_reason'].lower()})" if lab["exclusion_reason"] else "")
            if lab.get("note"):
                note += f"; {lab['note']}"
            if note not in r.get("notes", ""):
                r["notes"] = (r.get("notes", "") + " | " + note).strip(" |")
        elif not r.get("fulltext_format"):
            r["fulltext_screen"] = "not_accessible"
        elif not r.get("fulltext_screen"):
            unlabelled.append(r["pmid"])
    with manifest.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)

    counts = Counter(r["fulltext_screen"] or "pending" for r in in_corpus)
    reasons = Counter(r["fulltext_screen_reason"] for r in in_corpus if r["fulltext_screen"] == "exclude")
    included_primary = sum(1 for r in in_corpus if r["fulltext_screen"] == "include"
                           and r["fulltext_study_type"] in ("case report", "case series/cohort"))
    log_path = base / "screening_fulltext" / "screening_log.json"
    log = json.loads(log_path.read_text()) if log_path.exists() else {"runs": []}
    run = {
        "date": datetime.now(UTC).date().isoformat(),
        "route": "claude_code (D-20)",
        "prompt_file": str(prompt),
        "prompt_sha256": hashlib.sha256(prompt.read_bytes()).hexdigest(),
        "label_files": [str(f) for f in label_files],
        "n_labels": len(labels),
        "by_decision": dict(counts),
        "exclusion_reasons": dict(reasons),
        "included_primary_reports": included_primary,
        "evidence_quote_not_found": missing_quotes,
        "unlabelled_with_fulltext": unlabelled,
    }
    log["runs"].append(run)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(log, indent=2) + "\n")
    print(json.dumps(run))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    e = sub.add_parser("export")
    e.add_argument("--disease", required=True)
    e.add_argument("--batch-size", type=int, default=15)
    e.add_argument("--max-tokens", type=int, default=100_000, help="token budget per batch (from fulltext_md meta)")
    e.add_argument("--start", type=int, default=1, help="first batch number; >1 keeps earlier batch lists (second wave)")
    i = sub.add_parser("import")
    i.add_argument("--disease", required=True)
    i.add_argument("--prompt", default=str(PROMPT))
    i.add_argument("--allow-missing-quotes", action="store_true")
    args = ap.parse_args(argv)
    if args.cmd == "export":
        return export(args.disease, args.batch_size, args.max_tokens, args.start)
    return import_labels(args.disease, Path(args.prompt), args.allow_missing_quotes)


if __name__ == "__main__":
    raise SystemExit(main())
