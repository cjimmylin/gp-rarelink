"""Check each disease's candidate variant catalogue before extraction (pre-registration §7.2.7; D-35).

Harness side only: catalogues are never shown to extraction (§5.3).

A candidate is suitable when its open full text (main text plus appended
supplementary material, data/literature/<disease>/fulltext_md/<pmid>.md) holds
a per-variant table that names source papers:
  - a Markdown table with at least MIN_ROWS rows;
  - a variant column: at least half its cells look like a variant description
    (c./p./g. notation, an exon deletion, or a protein change such as R79H);
  - a source column: its header names a reference, source, author, study or
    citation, or at least half its cells look like a citation (et al., a year,
    a bracketed reference number, a PMID). A column of bare numbers counts
    only when its header names a reference.
  - at least SHARE of the table's rows have both.
A candidate without open full text, or without such a table, is dropped, and
that disease reports no completeness figure (§7.2.7).

  uv run python -m pipeline.harness.catalogue_check
writes analysis/catalogue/catalogue_check_<date>.json and .md.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import UTC, datetime
from pathlib import Path

CANDIDATES = {  # §7.2.7 table (frozen v1.0); HA20 uses Chen 2020 Table S1 (D-30), checked in the pilot
    "axd": "grossi2024_axd_meta",
    "lad1": "almarzanovoa2018_lad1_review",
    "ssadh": "tokatlylatzer2023_ssadh_genotype",
    "danon": None,
    "tangier": "koseki2021_tangier_review",
}
MIN_ROWS, SHARE = 10, 0.8
VARIANT = re.compile(r"\b[cpg]\.\s?[\(\[]?[-*]?[A-Za-z]{0,3}\d+|\bexons?\s?\d+[-–]?\d*\s*(del|dup)|\b(del|dup)\w*\s+exons?\b"
                     r"|\b[ACDEFGHIKLMNPQRSTVWY]\d{2,4}[ACDEFGHIKLMNPQRSTVWY*X]\b"
                     r"|\b(Ala|Arg|Asn|Asp|Cys|Gln|Glu|Gly|His|Ile|Leu|Lys|Met|Phe|Pro|Ser|Thr|Trp|Tyr|Val)\d+", re.IGNORECASE)
CITE_CELL = re.compile(r"et al|\b(19|20)\d{2}\b|\[\d+(?:[,–-]\s?\d+)*\]|PMID|\bref", re.IGNORECASE)
# A bare number is a citation only under a header that names a reference (e.g. "Ref."), never under "Patient".
CITE_HEAD = re.compile(r"ref|source|author|study|citation|publication|literature|report", re.IGNORECASE)


def tables(md: str) -> list[dict]:
    out, block, title = [], [], ""
    for line in md.splitlines() + [""]:
        if line.lstrip().startswith("|"):
            block.append(line)
            continue
        if block:
            rows = [[c.strip() for c in r.strip().strip("|").split("|")] for r in block]
            rows = [r for r in rows if not all(re.fullmatch(r":?-{2,}:?", c or "--") for c in r)]
            if len(rows) >= 2:
                out.append({"title": title, "header": rows[0], "rows": rows[1:]})
            block = []
        if line.strip():
            title = line.strip()[:120]
    return out


def judge(t: dict) -> dict:
    head, rows = t["header"], t["rows"]
    ncol = max(len(head), *(len(r) for r in rows))
    col = lambda j: [r[j] if j < len(r) else "" for r in rows]
    vshare = [sum(bool(VARIANT.search(c)) for c in col(j)) / len(rows) for j in range(ncol)]
    cshare = [sum(bool(CITE_CELL.search(c)) for c in col(j)) / len(rows) for j in range(ncol)]
    vcol = max(range(ncol), key=lambda j: vshare[j])
    src = [j for j in range(ncol) if j != vcol and ((j < len(head) and CITE_HEAD.search(head[j]) and not re.search(r"patient|case|family", head[j], re.I))
                                                    or cshare[j] >= 0.5)]
    scol = max(src, key=lambda j: cshare[j]) if src else None
    both = (sum(1 for r in rows if vcol < len(r) and VARIANT.search(r[vcol]) and scol is not None and scol < len(r) and r[scol].strip())
            / len(rows))
    ok = len(rows) >= MIN_ROWS and vshare[vcol] >= 0.5 and scol is not None and both >= SHARE
    return {"title": t["title"], "n_rows": len(rows), "header": head,
            "variant_column": head[vcol] if vcol < len(head) else vcol, "variant_share": round(vshare[vcol], 3),
            "source_column": (head[scol] if scol is not None and scol < len(head) else scol), "rows_with_both": round(both, 3),
            "suitable": ok}


def main() -> int:
    bib = {r["key"]: r for r in csv.DictReader(open("background/manifest.csv"))}
    res = []
    for d, key in CANDIDATES.items():
        if key is None:
            res.append({"disease": d, "candidate": None, "verdict": "no candidate", "reason": "no open catalogue named in §7.2.7"})
            continue
        pmid = bib[key]["pmid"]
        f = Path(f"data/literature/{d}/fulltext_md/{pmid}.md")
        if not f.exists():
            res.append({"disease": d, "candidate": key, "pmid": pmid, "verdict": "dropped",
                        "reason": "no open full text fetched (D-32: open access only)"})
            continue
        md = f.read_text(encoding="utf-8")
        judged = [judge(t) for t in tables(md)]
        good = [j for j in judged if j["suitable"]]
        best = max(good or judged, key=lambda j: (j["suitable"], j["n_rows"] * j["rows_with_both"]), default=None)
        res.append({"disease": d, "candidate": key, "pmid": pmid, "has_supplement_section": "## Supplementary material" in md,
                    "n_tables": len(judged), "verdict": "suitable" if good else "dropped",
                    "reason": "per-variant table naming source papers found" if good else
                              "no table with a variant column and a source column on at least 80% of 10+ rows",
                    "best_table": best})
    today = datetime.now(UTC).date().isoformat()
    out = Path("analysis/catalogue")
    out.mkdir(parents=True, exist_ok=True)
    (out / f"catalogue_check_{today}.json").write_text(json.dumps(res, indent=2, ensure_ascii=False) + "\n")
    lines = [f"# Variant catalogue check ({today})", "",
             "*Generated by `pipeline/harness/catalogue_check.py` (pre-registration §7.2.7, D-35). Harness side only.*", "",
             "| Disease | Candidate | Verdict | Best table | Rows | Variant / source columns | Rows with both |", "|---|---|---|---|---|---|---|"]
    for r in res:
        b = r.get("best_table") or {}
        lines.append(f"| {r['disease']} | {r['candidate'] or '—'} | **{r['verdict']}**: {r['reason']} | {b.get('title', '—')[:60]} | "
                     f"{b.get('n_rows', '—')} | {b.get('variant_column', '—')} / {b.get('source_column', '—')} | {b.get('rows_with_both', '—')} |")
    (out / f"catalogue_check_{today}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
