"""Bring copies found by hand into a disease corpus (written 2026-11-15 for Majeed syndrome).

Input: the folder Dr. Lin returned (unzipped), holding the PDFs, `downloaded_files.csv`
(record_id, file_name, source_url, sha256, ...), `majeed_search_results.csv` (one row
per record on the to-find list, with search_status) and `README.txt`.

For every row of downloaded_files.csv the sha256 is checked against the file; a
mismatch stops the import. Then:
  * numeric record_id (a PMID in the manifest): the PDF is copied to
    data/literature/<d>/fulltext/<pmid>.pdf with a meta.json (source
    "hand_fetched:<host>", the URL, the retrieval date, sha256). The manifest row
    gets access_status = hand_fetched_free, fulltext_format = pdf and its
    full-text screening columns are cleared, so the next full-text screening
    export picks it up;
  * any other record_id (records with no PMID, or extra references): copied to
    data/literature/<d>/fulltext_nopmid/<record_id>.pdf and listed in
    data/literature/<d>/nopmid_fulltext.csv.
The three provenance files are copied to data/literature/<d>/hand_retrieval_<date>/.
PDFs stay git-ignored (data/literature/**/*.pdf). Only free copies were sought
(README.txt; D-32 open access, D-47 free copies).

  uv run python analysis/corpus/import_hand_fetched.py --disease majeed --src <folder> --date 2026-11-14
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
from pathlib import Path
from urllib.parse import urlparse

FT_COLS = ["fulltext_screen", "fulltext_screen_reason", "fulltext_study_type", "fulltext_n_individuals",
           "fulltext_has_genotype", "fulltext_literature_table", "fulltext_quote_found"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    ap.add_argument("--src", type=Path, required=True)
    ap.add_argument("--date", required=True, help="date the copies were retrieved (ISO)")
    a = ap.parse_args()
    base = Path("data/literature") / a.disease
    files = list(csv.DictReader((a.src / "downloaded_files.csv").open(encoding="utf-8-sig", newline="")))
    for f in files:
        got = hashlib.sha256((a.src / f["file_name"]).read_bytes()).hexdigest()
        if got != f["sha256"]:
            raise SystemExit(f"STOP: sha256 mismatch for {f['file_name']}")

    man_path = base / "manifest.csv"
    rows = list(csv.DictReader(man_path.open(newline="")))
    cols = list(rows[0].keys())
    by_pmid = {r["pmid"]: r for r in rows}
    (base / "fulltext").mkdir(exist_ok=True)
    (base / "fulltext_nopmid").mkdir(exist_ok=True)
    nopmid_out, n_pmid = [], 0
    for f in files:
        rid, src = f["record_id"].strip(), a.src / f["file_name"]
        meta = {"retrieved_at": a.date, "source": f"hand_fetched:{urlparse(f['source_url']).netloc}",
                "url": f["source_url"], "format": "pdf", "sha256": f["sha256"], "pages": f["pages"],
                "license": "", "note": "free copy found by hand (Dr. Lin); only free copies were sought"}
        if rid.isdigit():
            if rid not in by_pmid:
                raise SystemExit(f"STOP: PMID {rid} is not in the manifest")
            shutil.copyfile(src, base / "fulltext" / f"{rid}.pdf")
            (base / "fulltext" / f"{rid}.meta.json").write_text(json.dumps({"pmid": rid, **meta}, indent=2) + "\n")
            r = by_pmid[rid]
            r.update(access_status="hand_fetched_free", fulltext_format="pdf", retrieved_at=a.date, sha256=f["sha256"])
            for c in FT_COLS:
                if c in r:
                    r[c] = ""
            r["notes"] = (r.get("notes", "") + f" | full text found by hand {a.date}: {f['source_url']}").strip(" |")
            n_pmid += 1
        else:
            shutil.copyfile(src, base / "fulltext_nopmid" / f"{rid}.pdf")
            (base / "fulltext_nopmid" / f"{rid}.meta.json").write_text(json.dumps({"record_id": rid, **meta}, indent=2) + "\n")
            nopmid_out.append({"record_id": rid, "title": f["title"], "category": f["category"], "file": f"fulltext_nopmid/{rid}.pdf",
                               "source_url": f["source_url"], "pages": f["pages"], "sha256": f["sha256"]})
    with man_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    with (base / "nopmid_fulltext.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(nopmid_out[0].keys()))
        w.writeheader()
        w.writerows(nopmid_out)
    prov = base / f"hand_retrieval_{a.date}"
    prov.mkdir(exist_ok=True)
    for name in ("downloaded_files.csv", "README.txt", f"{a.disease}_search_results.csv"):
        if (a.src / name).exists():
            shutil.copyfile(a.src / name, prov / name)
    print(json.dumps({"pmid_copies": n_pmid, "nopmid_copies": len(nopmid_out), "provenance": str(prov)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
