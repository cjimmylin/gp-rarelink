"""Stage 1, step 2: fetch open-access full text for every in-corpus manifest row.

Order of attempts per row (first success wins):
  1. Europe PMC fullTextXML (needs a PMCID)
  2. NCBI E-utilities efetch db=pmc (needs a PMCID); ported from the pilot
     session's branch. The PMC OA web service is gone (404, 2026-10-18).
  3. Unpaywall best OA PDF (needs a DOI and UNPAYWALL_EMAIL)
The licence is read from the JATS <license> element when present.
Otherwise the row is marked paywalled (DOI known, no OA copy) or not_found.

Full text is stored under data/literature/<disease>/fulltext/ (git-ignored):
<pmid>.nxml or <pmid>.pdf, plus <pmid>.meta.json with source, licence,
retrieval date and sha256. The manifest's access columns are updated in place.
Licences are recorded, never redistributed. Stops on an unreachable host.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import re
from datetime import date
from pathlib import Path

import httpx

from pipeline.extract.corpus.eutils import Client, Unreachable

UNPAYWALL = "https://api.unpaywall.org/v2/"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


_LICENSE_HREF = re.compile(rb'<license[^>]*href="([^"]+)"')
_LICENSE_TEXT = re.compile(rb"<license[^>]*>(.*?)</license>", re.S)


def license_from_jats(xml: bytes) -> str | None:
    m = _LICENSE_HREF.search(xml)
    if m:
        return m.group(1).decode(errors="ignore")
    m = _LICENSE_TEXT.search(xml)
    if m:
        text = re.sub(rb"<[^>]+>", b" ", m.group(1))
        return re.sub(rb"\s+", b" ", text).strip().decode(errors="ignore")[:200] or None
    return None


def fetch_one(client: Client, row: dict, out: Path, unpaywall_email: str | None) -> dict:
    pmid, pmcid, doi = row["pmid"], (row.get("pmcid") or "").strip(), (row.get("doi") or "").strip()
    meta = {"pmid": pmid, "retrieved_at": date.today().isoformat(), "source": None, "license": None, "format": None, "sha256": None}
    if pmcid:
        for src_name, fn in (("europepmc", client.europepmc_fulltext_xml), ("pmc_efetch", client.efetch_pmc_xml)):
            try:
                xml = fn(pmcid)
            except (Unreachable, httpx.HTTPError) as exc:  # one source failing is not fatal
                meta.setdefault("errors", []).append(f"{src_name}: {exc}")
                xml = None
            if xml:
                (out / f"{pmid}.nxml").write_bytes(xml)
                meta.update(source=src_name, format="nxml", sha256=sha256(xml), license=license_from_jats(xml))
                return meta
    if doi and unpaywall_email:
        r = client.get(UNPAYWALL + doi, {"email": unpaywall_email})
        if r.status_code == 200:
            data = r.json() or {}
            best = data.get("best_oa_location") or {}
            # best location first, then the other open locations that offer a PDF
            locs = [best] + [loc for loc in (data.get("oa_locations") or []) if loc and loc != best]
            for loc in locs:
                url = loc.get("url_for_pdf")
                if not url:
                    continue
                try:
                    blob = client.download(url)
                except (Unreachable, httpx.HTTPError) as exc:
                    meta.setdefault("errors", []).append(f"unpaywall {url}: {type(exc).__name__}")
                    continue
                if blob[:4] == b"%PDF":
                    (out / f"{pmid}.pdf").write_bytes(blob)
                    meta.update(source="unpaywall:" + str(loc.get("host_type")), license=loc.get("license"), format="pdf",
                                sha256=sha256(blob), oa_version=loc.get("version"), url=url)
                    return meta
                meta.setdefault("errors", []).append(f"unpaywall {url}: not a PDF")
            if data.get("is_oa"):
                meta["oa_landing_url"] = best.get("url")
    meta["source"] = "paywalled" if doi else "not_found"
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--only-missing", action="store_true", default=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--retry-status", nargs="*", default=[], help="re-attempt rows with these access_status values")
    args = ap.parse_args(argv)

    base = Path("data/literature") / args.disease
    manifest = base / "manifest.csv"
    out = base / "fulltext"
    out.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader(manifest.open(newline="")))
    cols = list(rows[0].keys())
    client = Client()
    email = os.getenv("UNPAYWALL_EMAIL")
    n = 0
    try:
        for row in rows:
            if row.get("in_extraction_corpus", "").lower() != "true":
                continue
            if args.only_missing and row.get("access_status") and row["access_status"] not in ("", "not_found", *args.retry_status):
                continue
            if args.limit and n >= args.limit:
                break
            meta = fetch_one(client, row, out, email)
            (out / f"{row['pmid']}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            row["access_status"] = {"europepmc": "europepmc_xml", "pmc_efetch": "pmc_efetch_xml"}.get(meta["source"], meta["source"] or "")
            if meta["format"] == "pdf":
                row["access_status"] = "publisher_pdf"
            row["fulltext_format"] = meta["format"] or ""
            row["retrieved_at"] = meta["retrieved_at"]
            row["sha256"] = meta["sha256"] or ""
            row["license"] = meta["license"] or ""
            n += 1
            print(f"{row['pmid']}: {row['access_status']}")
    except Unreachable as exc:
        print(f"STOP: {exc}. Manifest saved with progress so far; rerun on a networked machine.")
    finally:
        with manifest.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
