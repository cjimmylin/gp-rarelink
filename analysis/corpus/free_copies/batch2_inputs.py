"""D-47 addendum batch 2: sha256 of every input PDF and converted Markdown (identifiers only).

The papers and their converted text are git-ignored (D-46) and live only in the container that ran
batch 2, so this file is what a later session checks a re-fetched or re-converted copy against.
For each paper in analysis/corpus/free_copies/hand_fetched_2026-11-14.csv it records:
  received_sha256     the file as received (PDF, or a PMC page saved as MHTML), from that manifest
  pdf_sha256          the PDF the converter read (data/literature/<d>/fulltext/<pmid>.pdf); for the
                      four MHTML pages this is the PDF printed from the page, not the received file
  markdown_sha256     the converted text the extraction quotes were checked against
                      (data/literature/<d>/fulltext_md/<pmid>.md)
plus the screening decision, sizes, the converter named in <pmid>.meta.json and the share of the
PDF's text-layer words found in the Markdown (conversion_coverage_<date>.json).

  python3 -I analysis/corpus/free_copies/batch2_inputs.py --date 2026-11-15
writes analysis/corpus/free_copies/batch2_inputs_<date>.csv. No paper text is written.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    cov = {(x["disease"], x["pmid"]): x for x in json.loads((HERE / f"conversion_coverage_{a.date}.json").read_text())["papers"]}
    rows, missing = [], []
    for r in csv.DictReader((HERE / "hand_fetched_2026-11-14.csv").open()):
        d, p = r["disease"], r["pmid"]
        scr = {s["pmid"]: s["decision"] for s in csv.DictReader((ROOT / f"data/literature/{d}/addendum_d47/batch2/screening.csv").open())}
        pdf = ROOT / f"data/literature/{d}/fulltext/{p}.pdf"
        md = ROOT / f"data/literature/{d}/fulltext_md/{p}.md"
        meta = ROOT / f"data/literature/{d}/fulltext_md/{p}.meta.json"
        if not (pdf.exists() and md.exists()):
            missing.append(p)
            continue
        mm = json.loads(meta.read_text()) if meta.exists() else {}
        rows.append({
            "disease": d, "pmid": p, "screening": scr.get(p, ""), "received_file_kind": r["file_kind"], "received_sha256": r["sha256"],
            "pdf_sha256": sha(pdf), "pdf_bytes": pdf.stat().st_size, "pdf_is_received_file": "yes" if sha(pdf) == r["sha256"] else "no",
            "markdown_sha256": sha(md), "markdown_chars": len(md.read_text()), "converter": mm.get("converter", ""),
            "share_pdf_words_in_markdown": cov.get((d, p), {}).get("share_pdf_words_in_md", ""),
        })
    assert not missing, f"papers without PDF or Markdown in this container: {missing}"
    with (HERE / f"batch2_inputs_{a.date}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "papers;", sum(x["pdf_is_received_file"] == "no" for x in rows), "with a printed PDF;",
          sum(x["screening"] == "include" for x in rows), "included")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
