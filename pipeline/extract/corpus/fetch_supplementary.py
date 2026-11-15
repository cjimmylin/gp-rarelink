"""Fetch supplementary files for the full-text papers (D-22 item 7).

For every paper with full text (data/literature/<disease>/fulltext/<pmid>.nxml)
and a PMCID, asks Europe PMC for its supplementary files
(GET /europepmc/webservices/rest/<PMCID>/supplementaryFiles, a zip). From the
zip it keeps only document and table formats (docx, doc, xlsx, xls, csv, tsv,
txt, pdf, rtf, odt, ods), each at most --max-file-mb, and skips figures and
media. Files go to data/literature/<disease>/supplementary/files/<pmid>/
(git-ignored); they are used for text mining and are never redistributed.

The licence class of each paper is read from its JATS licence statement and
recorded with every file, so the licensing check is reproducible. Writes
data/literature/<disease>/supplementary/manifest.csv (one row per kept or
skipped file, plus one row per paper without supplementary files): pmid, pmcid,
licence class, file name, bytes, sha256, status, retrieval date.

  uv run python -m pipeline.extract.corpus.fetch_supplementary --disease ha20
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import re
import zipfile
from datetime import date
from pathlib import Path

import httpx

EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
KEEP = {".docx", ".doc", ".xlsx", ".xls", ".csv", ".tsv", ".txt", ".pdf", ".rtf", ".odt", ".ods"}
COLUMNS = ["pmid", "pmcid", "licence_class", "file", "bytes", "sha256", "status", "retrieved", "source"]
# Fallback (2026-11-14, Europe PMC supplementaryFiles outage): NLM's PMC Cloud Service, the open bulk
# distribution of the PMC Open Access Subset and Author Manuscripts (https://pmc.ncbi.nlm.nih.gov/tools/pmcaws/).
# Each article version is a folder PMC<id>.<version>/ holding the article (PMC<id>.<v>.xml/.txt/.pdf/.json)
# and its supplementary files under their published names.
PMC_CLOUD = "https://pmc-oa-opendata.s3.amazonaws.com"


def licence_class(nxml: str) -> str:
    """Coarse licence class from the JATS licence element or statement."""
    m = re.search(r"<license[^>]*?href=\"([^\"]+)\"", nxml)
    lp = re.search(r"<license-p[^>]*>(.*?)</license-p>", nxml, re.S)
    ali = re.search(r"<ali:license_ref[^>]*>([^<]+)<", nxml)
    s = " ".join(x for x in [m.group(1) if m else "", ali.group(1) if ali else "",
                             re.sub(r"<[^>]+>", " ", lp.group(1)) if lp else ""]).lower()
    s = re.sub(r"\s+", " ", s)
    if "by-nc-nd" in s or "noncommercial-noderivatives" in s or "non-commercial-noderivatives" in s:
        return "CC BY-NC-ND"
    if "by-nc-sa" in s:
        return "CC BY-NC-SA"
    if "by-nc" in s or "attribution-noncommercial" in s or "attribution non-commercial" in s:
        return "CC BY-NC"
    if "creativecommons.org/licenses/by" in s or "creative commons attribution" in s or "(cc by)" in s:
        return "CC BY"
    if "publicdomain" in s or "cc0" in s:
        return "CC0"
    if "text mining" in s or "data-mine" in s or "text and data" in s:
        return "text-and-data-mining terms (non-CC)"
    if "dovepress.com/terms" in s:
        return "Dove Medical Press terms (CC BY-NC 3.0 per publisher)"
    return "unclassified" if s.strip() else "none stated"


def pmc_cloud(client: httpx.Client, pmcid: str, pmid: str, row0: dict, out_dir: Path, max_mb: float) -> list[dict] | None:
    """Supplementary files from the PMC Cloud Service, or None if the service could not be read.

    Lists the latest version folder of the article; keeps document and table files (KEEP) that are not the
    article's own PMC<id>.<v>.* files. An article absent from the service (not in the open subsets) is a
    settled answer: one row with status none (pmc_cloud: not in the open subsets).
    """
    try:
        r = client.get(f"{PMC_CLOUD}/", params={"list-type": "2", "prefix": f"{pmcid}.", "max-keys": "1000"})
    except httpx.HTTPError:
        return None
    if r.status_code != 200:
        return None
    keys = re.findall(r"<Key>([^<]+)</Key>", r.text)
    versions = sorted({k.split("/", 1)[0] for k in keys if "/" in k}, key=lambda v: int(v.rsplit(".", 1)[-1]) if v.rsplit(".", 1)[-1].isdigit() else 0)
    base = {**row0, "source": "pmc_cloud"}
    if not versions:
        return [base | {"file": "", "bytes": "", "sha256": "", "status": "none (pmc_cloud: not in the open subsets)"}]
    v = versions[-1]
    rows, kept = [], 0
    for k in keys:
        folder, _, name = k.partition("/")
        if folder != v or not name or name.startswith(f"{v}.") or Path(name).suffix.lower() not in KEEP:
            continue
        try:
            f = client.get(f"{PMC_CLOUD}/{k}")
        except httpx.HTTPError:
            return None
        if f.status_code != 200:
            return None
        if len(f.content) > max_mb * 1e6:
            rows.append(base | {"file": name, "bytes": len(f.content), "sha256": "", "status": "skipped_too_large"})
            continue
        dest = out_dir / pmid
        dest.mkdir(exist_ok=True)
        (dest / name).write_bytes(f.content)
        rows.append(base | {"file": name, "bytes": len(f.content), "sha256": hashlib.sha256(f.content).hexdigest(), "status": "kept"})
        kept += 1
    if not kept and not rows:
        rows.append(base | {"file": "", "bytes": "", "sha256": "", "status": f"none (pmc_cloud {v}: no document files)"})
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--max-file-mb", type=float, default=15.0)
    ap.add_argument("--pmid", nargs="*", default=None)
    ap.add_argument("--fallback-pmc-cloud", action="store_true",
                    help="when Europe PMC returns no zip, take the files from NLM's PMC Cloud Service instead")
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    manifest = {r["pmid"]: r for r in csv.DictReader((base / "manifest.csv").open())}
    out_dir = base / "supplementary" / "files"
    out_dir.mkdir(parents=True, exist_ok=True)
    pmids = args.pmid or sorted(p.stem for p in (base / "fulltext").glob("*.nxml"))
    rows, today = [], date.today().isoformat()
    with httpx.Client(timeout=120, follow_redirects=True, headers={"User-Agent": "gp-rarelink (literature curation)"}) as client:
        for pmid in pmids:
            pmcid = manifest.get(pmid, {}).get("pmcid", "")
            lic = licence_class((base / "fulltext" / f"{pmid}.nxml").read_text(encoding="utf-8", errors="ignore"))
            row0 = {"pmid": pmid, "pmcid": pmcid, "licence_class": lic, "retrieved": today, "source": "europepmc"}
            if not pmcid:
                rows.append(row0 | {"file": "", "bytes": "", "sha256": "", "status": "no_pmcid"})
                continue
            try:
                r = client.get(f"{EUROPEPMC}/{pmcid}/supplementaryFiles")
            except httpx.HTTPError as e:
                got = pmc_cloud(client, pmcid, pmid, row0, out_dir, args.max_file_mb) if args.fallback_pmc_cloud else None
                if got is None:
                    raise SystemExit(f"{pmid}: Europe PMC unreachable ({e}); stopping")
                rows.extend(got)
                print(f"{pmid} {pmcid}: Europe PMC unreachable ({type(e).__name__}); "
                      f"{sum(1 for x in got if x['status'] == 'kept')} file(s) kept (PMC Cloud Service)")
                continue
            if (r.status_code != 200 or not r.content.startswith(b"PK")) and args.fallback_pmc_cloud:
                got = pmc_cloud(client, pmcid, pmid, row0, out_dir, args.max_file_mb)
                if got is not None:
                    rows.extend(got)
                    print(f"{pmid} {pmcid}: {sum(1 for x in got if x['status'] == 'kept')} file(s) kept (PMC Cloud Service)")
                    continue
            if r.status_code != 200 or not r.content.startswith(b"PK"):
                # Europe PMC wraps backend failures in an XML errorBean, sometimes with HTTP 200
                # (2026-11-14: "Failed: HTTP error code: 503"); keep its message so an outage is not
                # mistaken for a paper without supplementary files.
                m = re.search(rb"<errMsg>(.*?)</errMsg>", r.content[:2000])
                msg = f": {m.group(1).decode(errors='replace')}" if m else ""
                rows.append(row0 | {"file": "", "bytes": "", "sha256": "", "status": f"none (HTTP {r.status_code}{msg})"})
                continue
            kept = 0
            with zipfile.ZipFile(io.BytesIO(r.content)) as z:
                for info in z.infolist():
                    name = Path(info.filename).name
                    if info.is_dir() or not name:
                        continue
                    ext = Path(name).suffix.lower()
                    if ext not in KEEP:
                        continue
                    if info.file_size > args.max_file_mb * 1e6:
                        rows.append(row0 | {"file": name, "bytes": info.file_size, "sha256": "", "status": "skipped_too_large"})
                        continue
                    data = z.read(info)
                    dest = out_dir / pmid
                    dest.mkdir(exist_ok=True)
                    (dest / name).write_bytes(data)
                    rows.append(row0 | {"file": name, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "status": "kept"})
                    kept += 1
            if not kept:
                rows.append(row0 | {"file": "", "bytes": "", "sha256": "", "status": "zip_without_document_files"})
            print(f"{pmid} {pmcid}: {kept} file(s) kept")
    man_path = base / "supplementary" / "manifest.csv"
    if args.pmid and man_path.exists():  # a partial re-fetch replaces only these papers' rows
        keep = [r for r in csv.DictReader(man_path.open()) if r["pmid"] not in set(pmids)]
        rows = sorted(keep + rows, key=lambda r: (r["pmid"], r["file"]))
    with man_path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"{sum(1 for r in rows if r['status'] == 'kept')} files kept for "
          f"{len({r['pmid'] for r in rows if r['status'] == 'kept'})} of {len(pmids)} papers")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
