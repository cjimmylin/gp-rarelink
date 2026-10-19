"""Convert supplementary files to text and append them to the paper Markdown (D-22 item 7).

Run after to_markdown (which rewrites fulltext_md/<pmid>.md from the XML). For
each file kept by fetch_supplementary:

  docx, odt, rtf  -> pandoc to GitHub Markdown (tables kept)
  doc             -> LibreOffice to docx, then pandoc
  pdf             -> pdftotext -layout
  xlsx, xls, ods  -> every sheet as a Markdown table
  csv, tsv, txt   -> as is

Relevance and size:
  - A file is used only if its text mentions TNFAIP3, A20 or HA20. Files that
    don't (conflict-of-interest forms, unrelated cohort data, figure-only PDFs)
    are skipped.
  - A file whose text is longer than --max-file-chars is cut to the lines that
    mention TNFAIP3, A20 or HA20 plus --context lines around each, with the
    table header lines kept. The appended section says so.
  - At most --max-paper-chars are appended per paper; files are taken in name
    order and the rest are skipped with status "paper_cap".

The appended block starts with "## Supplementary material" and one
"### Supplementary file: <name>" heading per file, so quotes from it can be
told apart from the main text. Writes data/literature/<disease>/supplementary/
conversion.csv (committed): pmid, file, status, chars_in, chars_out.

  uv run python -m pipeline.extract.corpus.supplementary_to_text --disease ha20
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import tempfile
from pathlib import Path

import pandas as pd

RELEVANT = re.compile(r"TNFAIP3|\bA20\b|HA20|haploinsufficiency of A20", re.IGNORECASE)
HEADER_HINT = re.compile(r"^\s*\|.*\|\s*$|^\s*(patient|case|family|pt|no\.|id)\b", re.IGNORECASE)


def run(cmd: list[str], timeout: int = 180) -> str:
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, check=True).stdout


def sheet_markdown(df: pd.DataFrame, name: str) -> str:
    df = df.fillna("").astype(str)
    cols = [str(c) for c in df.columns]
    lines = [f"#### Sheet: {name}", "", "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(v.replace("|", "\\|").replace("\n", " ") for v in row) + " |")
    return "\n".join(lines)


def to_text(path: Path) -> str:
    ext = path.suffix.lower()
    if ext in (".docx", ".odt", ".rtf"):
        return run(["pandoc", str(path), "-t", "gfm", "--wrap=none"])
    if ext == ".doc":
        with tempfile.TemporaryDirectory() as tmp:
            run(["soffice", "--headless", "--convert-to", "docx", "--outdir", tmp, str(path)], timeout=300)
            out = next(Path(tmp).glob("*.docx"))
            return run(["pandoc", str(out), "-t", "gfm", "--wrap=none"])
    if ext == ".pdf":
        return run(["pdftotext", "-layout", str(path), "-"])
    if ext in (".xlsx", ".xls", ".ods"):
        sheets = pd.read_excel(path, sheet_name=None, header=0)
        return "\n\n".join(sheet_markdown(df, str(name)) for name, df in sheets.items())
    if ext in (".csv", ".tsv"):
        df = pd.read_csv(path, sep="\t" if ext == ".tsv" else ",", dtype=str, on_bad_lines="skip")
        return sheet_markdown(df, path.name)
    return path.read_text(encoding="utf-8", errors="ignore")


def excerpt(text: str, context: int) -> str:
    lines = text.splitlines()
    keep = set()
    for i, line in enumerate(lines[:400]):
        if HEADER_HINT.match(line) and i < 40:
            keep.add(i)
    for i, line in enumerate(lines):
        if RELEVANT.search(line):
            keep.update(range(max(0, i - context), min(len(lines), i + context + 1)))
    out, prev = [], -2
    for i in sorted(keep):
        if i != prev + 1:
            out.append("[...]")
        out.append(lines[i])
        prev = i
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--max-file-chars", type=int, default=60000)
    ap.add_argument("--max-paper-chars", type=int, default=120000)
    ap.add_argument("--context", type=int, default=3)
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    files_dir = base / "supplementary" / "files"
    md_dir = base / "fulltext_md"
    log = []
    for paper_dir in sorted(p for p in files_dir.iterdir() if p.is_dir()):
        pmid = paper_dir.name
        md_path = md_dir / f"{pmid}.md"
        if not md_path.exists():
            continue
        md = md_path.read_text()
        if "\n## Supplementary material\n" in md:  # already appended; to_markdown must run first
            md = md.split("\n## Supplementary material\n", 1)[0].rstrip() + "\n"
        blocks, used = [], 0
        for f in sorted(paper_dir.iterdir()):
            try:
                text = to_text(f)
            except Exception as e:  # noqa: BLE001 - record and continue
                log.append({"pmid": pmid, "file": f.name, "status": f"error: {type(e).__name__}", "chars_in": "", "chars_out": ""})
                continue
            text = re.sub(r"\n{3,}", "\n\n", text).strip()
            if not RELEVANT.search(text):
                log.append({"pmid": pmid, "file": f.name, "status": "skipped_no_TNFAIP3_or_A20_mention", "chars_in": len(text), "chars_out": 0})
                continue
            status, body = "included_full", text
            if len(text) > args.max_file_chars:
                status = "included_excerpt"
                body = (f"*Excerpt: the file has {len(text):,} characters; shown are the lines mentioning TNFAIP3, A20 or HA20 "
                        f"with {args.context} lines around each, and the first header lines.*\n\n" + excerpt(text, args.context))
            if used + len(body) > args.max_paper_chars:
                log.append({"pmid": pmid, "file": f.name, "status": "skipped_paper_cap", "chars_in": len(text), "chars_out": 0})
                continue
            blocks.append(f"### Supplementary file: {f.name}\n\n{body}")
            used += len(body)
            log.append({"pmid": pmid, "file": f.name, "status": status, "chars_in": len(text), "chars_out": len(body)})
        if blocks:
            md = md.rstrip() + "\n\n## Supplementary material\n\n*Converted from the files published with the article (Europe PMC).*\n\n" + "\n\n".join(blocks) + "\n"
        md_path.write_text(md)
        print(f"{pmid}: {len(blocks)} file(s) appended, {used:,} characters")
    with (base / "supplementary" / "conversion.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pmid", "file", "status", "chars_in", "chars_out"])
        w.writeheader()
        w.writerows(log)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
