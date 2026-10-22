"""Transcribe the AxD completeness catalogue (Grossi 2024, PMID 39420046) by script (D-39).

Harness side only (pre-registration §5.3, §7.2.7). The catalogue is never shown to
extraction: it is written under the reference root outside the repo, and only a
manifest (counts, source sha256, the suitability verdict) is committed.

D-39 (Jimmy, 2026-10-20): the pre-extraction catalogue check dropped Grossi 2024
because Europe PMC answered HTTP 500 for its supplement. The supplement came
through after pv1-axd finished. Its per-patient table is transcribed here and
judged with the same rule as every other candidate (catalogue_check.judge).

Source: 41598_2024_75383_MOESM2_ESM.xlsx, sheet "Suppl. Table 2" (CC BY), one row
per patient: variant (protein and cDNA), onset, sex, country and "Reference (PMID)".

  uv run python -m pipeline.harness.catalogue_grossi2024 \
      --xlsx data/literature/axd/supplementary/files/39420046/41598_2024_75383_MOESM2_ESM.xlsx \
      --root /home/user/gp-rarelink-reference --date 2026-10-20 --manifest-out analysis/catalogue
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import openpyxl

from pipeline.harness.catalogue_check import judge

SHEET = "Suppl. Table 2"
NCOL = 22  # 'Affected Domain' ... 'Reference (PMID)'; later columns are empty


def clean(c) -> str:
    if c is None:
        return ""
    if isinstance(c, float) and c.is_integer():
        c = int(c)
    return str(c).strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--xlsx", required=True)
    ap.add_argument("--root", required=True, help="reference root outside the repo")
    ap.add_argument("--date", required=True)
    ap.add_argument("--manifest-out", required=True)
    a = ap.parse_args(argv)
    src = Path(a.xlsx)
    root = Path(a.root).resolve()
    if Path.cwd().resolve() in root.parents or root == Path.cwd().resolve():
        raise SystemExit("reference root must be outside the repository")
    ws = openpyxl.load_workbook(src, read_only=True, data_only=True)[SHEET]
    rows = [[clean(c) for c in r[:NCOL]] for r in ws.iter_rows(values_only=True)]
    header = rows[1]
    if header[0] != "Affected Domain" or header[-1] != "Reference (PMID)":
        raise SystemExit(f"unexpected header: {header}")
    body = [r for r in rows[2:] if any(r)]
    n_trailing_blank = len(rows) - 2 - len(body)
    pidx, cidx, ridx = header.index("Protein Description"), header.index("cDNA description"), header.index("Reference (PMID)")
    verdict = judge({"title": f"Grossi 2024 {SHEET}", "header": header, "rows": body})
    out = root / a.date / "catalogues"
    out.mkdir(parents=True, exist_ok=True)
    dest = out / "grossi2024_axd_table2.csv"
    with dest.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(body)
    refs = {r[ridx] for r in body if r[ridx]}
    man = {
        "catalogue": "grossi2024_axd_meta", "pmid": "39420046", "decision": "D-39",
        "source_file": str(src), "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(), "sheet": SHEET,
        "output": str(dest), "date": a.date,
        "n_rows": len(body), "n_blank_rows_skipped": n_trailing_blank,
        "rows_with_protein_change": sum(1 for r in body if r[pidx] and r[pidx] != "-"),
        "rows_with_cdna": sum(1 for r in body if r[cidx] and r[cidx] != "-"),
        "rows_with_reference": sum(1 for r in body if r[ridx]),
        "distinct_references": len(refs),
        "distinct_protein_changes": len({r[pidx] for r in body if r[pidx]}),
        "suitability": verdict,
        # judge() picks the first column whose header matches its source pattern, which here is
        # "REF" (the reference allele), not "Reference (PMID)". The rule is left as registered
        # (D-35); the share is also given for the intended column so the verdict does not rest
        # on the allele column.
        "suitability_note": "judge() chose 'REF' (reference allele) as its source column; "
                            "share with the intended 'Reference (PMID)' column given below",
        "rows_with_variant_and_reference_pmid_share": round(
            sum(1 for r in body if r[pidx] and r[pidx] != "-" and r[ridx]) / len(body), 3),
    }
    mo = Path(a.manifest_out)
    mo.mkdir(parents=True, exist_ok=True)
    (mo / f"grossi2024_manifest_{a.date}.json").write_text(json.dumps(man, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(man, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
