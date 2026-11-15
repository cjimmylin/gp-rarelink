"""How much of each PDF's own text layer survives Docling conversion (D-47 batch 2).

For every paper in analysis/corpus/free_copies/hand_fetched_2026-11-14.csv this compares the
distinct words (5+ letters, lower-cased) in `pdftotext` output of
data/literature/<d>/fulltext/<pmid>.pdf with those in data/literature/<d>/fulltext_md/<pmid>.md.
The share of PDF words also found in the Markdown flags dropped text (for example a lost
abstract) and garbled OCR. Scanned PDFs without a text layer report pdf_words = 0.
It also counts one conversion artefact helpers reported: '>' printed as '.' in cDNA notation
(regex c.<digits><base>.<base>; it misses strings printed without 'c.', so it is a lower bound).
A second artefact, '+'/'-' table marks turned into '1'/'2', cannot be detected by script; the
findings report lists it from the helpers' notes.

Writes analysis/corpus/free_copies/conversion_coverage_<date>.json (identifiers and counts only).

  python3 -I analysis/corpus/free_copies/conversion_coverage.py --date 2026-11-15
"""
import argparse
import csv
import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
WORD = re.compile(r"[a-z]{5,}")
GT_AS_DOT = re.compile(r"c\.\s?\d+[+-]?\d*\s?[ACGT]\s?\.\s?[ACGT]\b")


def words(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    rows = list(csv.DictReader(open(ROOT / "analysis/corpus/free_copies/hand_fetched_2026-11-14.csv")))
    out = []
    for r in rows:
        d, p = r["disease"], r["pmid"]
        pdf = ROOT / f"data/literature/{d}/fulltext/{p}.pdf"
        md = ROOT / f"data/literature/{d}/fulltext_md/{p}.md"
        if not pdf.exists() or not md.exists():
            out.append({"disease": d, "pmid": p, "missing": True})
            continue
        pdf_text = subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout
        md_text = md.read_text()
        pw, mw = words(pdf_text), words(md_text)
        out.append({
            "disease": d, "pmid": p, "source_kind": r["file_kind"],
            "pdf_words": len(pw), "md_words": len(mw),
            "share_pdf_words_in_md": round(len(pw & mw) / len(pw), 3) if pw else None,
            "md_chars": len(md_text),
            "gt_printed_as_dot_in_md": len(GT_AS_DOT.findall(md_text)),
        })
    low = sorted((x for x in out if x.get("share_pdf_words_in_md") is not None and x["share_pdf_words_in_md"] < 0.9),
                 key=lambda x: x["share_pdf_words_in_md"])
    summary = {
        "date": a.date,
        "n_papers": len(out),
        "missing": [x["pmid"] for x in out if x.get("missing")],
        "no_text_layer": [x["pmid"] for x in out if x.get("pdf_words") == 0],
        "below_0_9": [(x["disease"], x["pmid"], x["share_pdf_words_in_md"]) for x in low],
        "with_gt_printed_as_dot": [(x["disease"], x["pmid"], x["gt_printed_as_dot_in_md"]) for x in out if x.get("gt_printed_as_dot_in_md")],
        "papers": out,
    }
    dest = ROOT / f"analysis/corpus/free_copies/conversion_coverage_{a.date}.json"
    dest.write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "papers"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
