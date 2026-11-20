"""Turn the project's checked reference list (background/manifest.csv) into a BibTeX file.

The paper-writing pipeline (PaperOrchestra, tools/paper-orchestra) treats this file as references
already verified by hand: their keys are citable and are not searched again. Only entries with an
identifier (PMID, DOI or arXiv id) are written; an entry without one is "not confirmed" (NOTES §7).

  python3 -I analysis/paper_v4/manifest_to_bib.py reports/paper_v4/materials/extra_references.bib
"""
from __future__ import annotations

import csv
import re
import sys
from pathlib import Path


def esc(s: str) -> str:
    return re.sub(r"([&%#_$])", r"\\\1", s.strip())


def authors(s: str) -> str:
    # manifest style "Joshi H, Shethia P, Lam MS" -> "Joshi, H. and Shethia, P. and Lam, M. S."
    out = []
    s = re.sub(r"\([^)]*\)", "", s)            # drop parenthetical notes such as "(incl. ...)"
    for a in [x.strip().rstrip(".") for x in s.replace(";", ",").split(",") if x.strip()]:
        if "et al" in a.lower():
            name = re.sub(r"(?i)\s*et al\.?", "", a).strip()
            if name:                                     # "Lansdon LA et al" -> the named author, then "others"
                out.append(authors(name))
            out.append("others")
            continue
        if a.lower() in ("et al", "et al."):
            out.append("others")
            continue
        parts = a.split()
        if len(parts) >= 2 and parts[-1].isupper() and len(parts[-1]) <= 4:
            out.append(f"{' '.join(parts[:-1])}, {' '.join(c + '.' for c in parts[-1])}")
        else:
            out.append("{" + a + "}")
    return " and ".join(out)


def main() -> int:
    out = Path(sys.argv[1])
    rows = list(csv.DictReader(open("background/manifest.csv", newline="", encoding="utf-8")))
    n = skipped = 0
    lines = ["% Generated from background/manifest.csv by analysis/paper_v4/manifest_to_bib.py; do not edit by hand.", ""]
    for r in rows:
        if not (r["pmid"].strip() or r["doi"].strip() or r["arxiv_id"].strip()):
            skipped += 1
            continue
        kind = "misc" if r["arxiv_id"].strip() and not r["doi"].strip() else "article"
        f = [f"  title = {{{{{esc(r['title'])}}}}}", f"  author = {{{authors(r['authors'])}}}", f"  year = {{{r['year'].strip()}}}"]
        if r["venue"].strip():
            f.append(f"  {'howpublished' if kind == 'misc' else 'journal'} = {{{esc(r['venue'])}}}")
        if r["doi"].strip():
            f.append(f"  doi = {{{r['doi'].strip()}}}")
        if r["pmid"].strip():
            f.append(f"  note = {{PMID {r['pmid'].strip()}}}")
        if r["arxiv_id"].strip():
            f.append(f"  eprint = {{{r['arxiv_id'].strip()}}}")
            f.append("  archivePrefix = {arXiv}")
        lines.append(f"@{kind}{{{r['key']},\n" + ",\n".join(f) + "\n}\n")
        n += 1
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"{n} entries written, {skipped} without an identifier left out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
