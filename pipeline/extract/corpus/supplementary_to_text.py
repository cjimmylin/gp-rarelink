"""Convert supplementary files to text and append them to the paper Markdown (D-22 item 7).

Run after to_markdown (which rewrites fulltext_md/<pmid>.md from the XML). For
each file kept by fetch_supplementary:

  docx, odt, rtf  -> pandoc to GitHub Markdown (tables kept)
  doc             -> LibreOffice to docx, then pandoc
  pdf             -> pdftotext -layout
  xlsx, xls, ods  -> every sheet as a Markdown table
  csv, tsv, txt   -> as is

Filter v2 (2026-10-19, D-24). Filter v1 kept only files that mention TNFAIP3,
A20 or HA20; that dropped a per-patient variant table that never names the gene
(42128528) and lab tables of case reports. v2 keeps every file except
administrative ones (conflict-of-interest and disclosure forms, reporting
checklists, peer-review files, data-sharing statements), recognised by file
name or by their opening text. --filter v1 restores the old rule.

Size:
  - A file whose text is longer than --max-file-chars is cut to the lines that
    mention TNFAIP3, A20 or HA20, or print an HGVS-style variant, plus
    --context lines around each, with the table header lines kept. If no line
    qualifies, the first --max-file-chars characters are kept. The appended
    section says which.
  - At most --max-paper-chars are appended per paper; files are taken in name
    order and the rest are skipped with status "paper_cap".

Clean-up of pandoc output (2026-10-19, D-24): pandoc writes complex tables as
HTML, with entities such as "&gt;". Those tables are turned into Markdown pipe
tables (rowspan and colspan repeated, as in jats_to_markdown) and the remaining
entities are decoded. Lines stacked inside one cell are joined with " / " when
another cell of the same row is also stacked, so a cell listing one value per
patient reads "18 / 24 / 21 / 57"; a lone multi-line cell is wrapped text and is
joined with a space. Pandoc drops empty
lines, so a stacked cell can hold fewer values than the row has patients; the
extraction instructions (v4) say not to assign values then.

The appended block starts with "## Supplementary material" and one
"### Supplementary file: <name>" heading per file, so quotes from it can be
told apart from the main text. Writes data/literature/<disease>/supplementary/
conversion.csv (committed): pmid, file, status, chars_in, chars_out.

  uv run python -m pipeline.extract.corpus.supplementary_to_text --disease ha20
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from pathlib import Path

import pandas as pd

RELEVANT = re.compile(r"TNFAIP3|\bA20\b|HA20|haploinsufficiency of A20", re.IGNORECASE)


def relevant_pattern(disease: str) -> re.Pattern:
    """Lines worth keeping from an oversized file: the disease's gene or name.

    HA20 keeps the pilot's pattern unchanged. The other diseases use the gene
    symbol and name from configs/diseases.yaml (generalized 2026-10-20 for the
    six-disease run; logged in DECISIONS.md under D-37).
    """
    if disease == "ha20":
        return RELEVANT
    import yaml

    cfg = yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"][disease]
    name = cfg["name"]
    terms = [re.sub(r"\s*\(.*?\)", "", name).strip(), *re.findall(r"\((.*?)\)", name)]
    alts = "|".join(rf"\b{re.escape(t)}\b" for t in [cfg["gene"], *terms] if t)
    return re.compile(alts, re.IGNORECASE)
HGVS = re.compile(r"\b[cp]\.\s?\(?[*-]?[A-Za-z]{0,3}\d+")
HEADER_HINT = re.compile(r"^\s*\|.*\|\s*$|^\s*(patient|case|family|pt|no\.|id)\b", re.IGNORECASE)
ADMIN_NAME = re.compile(r"coif|conflict|disclosure|icmje|checklist|mdar|peer.?review|reviewer|response.?to|cover.?letter"
                        r"|copyright|data.?sharing|[-_.](prf|rc|dss)\.[a-z]+$", re.IGNORECASE)
ADMIN_TEXT = re.compile(r"ICMJE|Conflict of Interest|Disclosure of Potential Conflicts|Disclosure Form|reporting checklist"
                        r"|MDAR|Peer Review File|Data Sharing Statement|CARE Checklist|STROBE Statement|PRISMA 20\d\d"
                        r"|Response to Reviewers|Reviewer Comments", re.IGNORECASE)
HTML_TABLE = re.compile(r"<table\b.*?</table>", re.IGNORECASE | re.DOTALL)


class _TableParser(HTMLParser):
    """Collect the cells of one HTML table, with their rowspan and colspan."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[tuple[list[str], int, int]]] = []
        self._cell: list[str] | None = None  # lines of the current cell
        self._spans = (1, 1)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "tr":
            self.rows.append([])
        elif tag in ("td", "th"):
            if not self.rows:
                self.rows.append([])
            self._cell = []

            def num(k):
                try:
                    return max(1, int(a.get(k) or 1))
                except ValueError:
                    return 1
            self._spans = (num("rowspan"), num("colspan"))
            self._cell = [""]
        elif tag in ("br", "p") and self._cell is not None and self._cell[-1].strip():
            self._cell.append("")  # start a new line inside the cell

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            lines = [re.sub(r"\s+", " ", x).strip().replace("|", "\\|") for x in self._cell]
            self.rows[-1].append(([x for x in lines if x], *self._spans))
            self._cell = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell[-1] += data


def html_table_to_pipe(fragment: str) -> str:
    parser = _TableParser()
    parser.feed(fragment)
    grid: dict[tuple[int, int], str] = {}
    for r, row in enumerate(parser.rows):
        c = 0
        multi = sum(len(lines) > 1 for lines, _, _ in row)
        for lines, rs, cs in row:
            # several lines in a cell are values stacked one per patient only when another cell of the
            # row is stacked too; a lone multi-line cell is wrapped text ("119-kb" + "microdeletion")
            text = " / ".join(lines) if (len(lines) > 1 and multi > 1) else " ".join(lines)
            while (r, c) in grid:
                c += 1
            for dr in range(rs):
                for dc in range(cs):
                    grid.setdefault((r + dr, c + dc), text)
            c += cs
    if not grid:
        return ""
    n_rows = max(r for r, _ in grid) + 1
    width = max(c for _, c in grid) + 1
    rows = [[grid.get((i, j), "") for j in range(width)] for i in range(n_rows)]
    lines = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
    lines += ["| " + " | ".join(r) + " |" for r in rows[1:]]
    return "\n" + "\n".join(lines) + "\n"


def clean_pandoc(text: str) -> str:
    """HTML tables to pipe tables, then decode the remaining entities."""
    return html.unescape(HTML_TABLE.sub(lambda m: html_table_to_pipe(m.group(0)), text))


def is_administrative(path: Path, text: str) -> bool:
    return bool(ADMIN_NAME.search(path.name) or ADMIN_TEXT.search(text[:3000]))


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
        return clean_pandoc(run(["pandoc", str(path), "-t", "gfm", "--wrap=none"]))
    if ext == ".doc":
        with tempfile.TemporaryDirectory() as tmp:
            run(["soffice", "--headless", "--convert-to", "docx", "--outdir", tmp, str(path)], timeout=300)
            out = next(Path(tmp).glob("*.docx"))
            return clean_pandoc(run(["pandoc", str(out), "-t", "gfm", "--wrap=none"]))
    if ext == ".pdf":
        return run(["pdftotext", "-layout", str(path), "-"])
    if ext in (".xlsx", ".xls", ".ods"):
        sheets = pd.read_excel(path, sheet_name=None, header=0)
        return "\n\n".join(sheet_markdown(df, str(name)) for name, df in sheets.items())
    if ext in (".csv", ".tsv"):
        df = pd.read_csv(path, sep="\t" if ext == ".tsv" else ",", dtype=str, on_bad_lines="skip")
        return sheet_markdown(df, path.name)
    return path.read_text(encoding="utf-8", errors="ignore")


def excerpt(text: str, context: int, relevant: re.Pattern = RELEVANT) -> str:
    lines = text.splitlines()
    keep = set()
    for i, line in enumerate(lines[:400]):
        if HEADER_HINT.match(line) and i < 40:
            keep.add(i)
    for i, line in enumerate(lines):
        if relevant.search(line) or HGVS.search(line):
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
    ap.add_argument("--filter", choices=["v2", "v1"], default="v2")
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    relevant = relevant_pattern(args.disease)
    label = "TNFAIP3, A20 or HA20" if args.disease == "ha20" else re.sub(r"\\(.)", r"\1", relevant.pattern.replace("\\b", "")).replace("|", ", ")
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
            if args.filter == "v1" and not relevant.search(text):
                log.append({"pmid": pmid, "file": f.name, "status": "skipped_no_TNFAIP3_or_A20_mention", "chars_in": len(text), "chars_out": 0})
                continue
            if args.filter == "v2" and is_administrative(f, text):
                log.append({"pmid": pmid, "file": f.name, "status": "skipped_administrative", "chars_in": len(text), "chars_out": 0})
                continue
            if args.filter == "v2" and not text.strip():
                log.append({"pmid": pmid, "file": f.name, "status": "skipped_no_text", "chars_in": 0, "chars_out": 0})
                continue
            status, body = "included_full", text
            if len(text) > args.max_file_chars:
                ex = excerpt(text, args.context, relevant)
                if any(relevant.search(x) or HGVS.search(x) for x in ex.splitlines()):
                    status = "included_excerpt"
                    body = (f"*Excerpt: the file has {len(text):,} characters; shown are the lines mentioning {label} "
                            f"or printing a variant, with {args.context} lines around each, and the first header "
                            f"lines.*\n\n" + ex)
                else:
                    status = "included_truncated"
                    body = (f"*Truncated: the file has {len(text):,} characters; shown are the first "
                            f"{args.max_file_chars:,}.*\n\n" + text[:args.max_file_chars] + "\n[...]")
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
