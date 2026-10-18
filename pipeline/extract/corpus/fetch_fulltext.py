"""Stage 1, step 2: fetch open-access full text for every in-corpus manifest row.

Order of attempts per row (first success wins):
  1. PMC OA service (needs a PMCID): .tar.gz with the article .nxml (+ PDF)
  2. Europe PMC fullTextXML (needs a PMCID)
  3. Unpaywall best OA PDF (needs a DOI and UNPAYWALL_EMAIL)
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
import io
import json
import os
import tarfile
from datetime import date
from pathlib import Path

import httpx

from pipeline.extract.corpus.eutils import Client, Unreachable

UNPAYWALL = "https://api.unpaywall.org/v2/"


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def _nxml_from_tgz(blob: bytes) -> bytes | None:
    with tarfile.open(fileobj=io.BytesIO(blob), mode="r:gz") as tf:
        for m in tf.getmembers():
            if m.isfile() and m.name.lower().endswith((".nxml", ".xml")):
                f = tf.extractfile(m)
                if f is not None:
                    return f.read()
    return None


def fetch_one(client: Client, row: dict, out: Path, unpaywall_email: str | None) -> dict:
    pmid, pmcid, doi = row["pmid"], (row.get("pmcid") or "").strip(), (row.get("doi") or "").strip()
    meta = {"pmid": pmid, "retrieved_at": date.today().isoformat(), "source": None, "license": None, "format": None, "sha256": None}
    if pmcid:
        links = client.pmc_oa_links(pmcid)
        for link in sorted(links, key=lambda l: 0 if l["format"] == "tgz" else 1):
            if link["format"] == "tgz":
                blob = client.download(link["href"].replace("ftp://", "https://"))
                nxml = _nxml_from_tgz(blob)
                if nxml:
                    (out / f"{pmid}.nxml").write_bytes(nxml)
                    meta.update(source="pmc_oa", license=link.get("license"), format="nxml", sha256=sha256(nxml))
                    return meta
        xml = client.europepmc_fulltext_xml(pmcid)
        if xml:
            (out / f"{pmid}.nxml").write_bytes(xml)
            meta.update(source="europepmc", format="nxml", sha256=sha256(xml))
            return meta
        for link in links:
            if link["format"] == "pdf":
                blob = client.download(link["href"].replace("ftp://", "https://"))
                (out / f"{pmid}.pdf").write_bytes(blob)
                meta.update(source="pmc_oa", license=link.get("license"), format="pdf", sha256=sha256(blob))
                return meta
    if doi and unpaywall_email:
        r = client.get(UNPAYWALL + doi, {"email": unpaywall_email})
        if r.status_code == 200:
            best = (r.json() or {}).get("best_oa_location") or {}
            url = best.get("url_for_pdf")
            if url:
                try:
                    blob = client.download(url)
                    if blob[:4] == b"%PDF":
                        (out / f"{pmid}.pdf").write_bytes(blob)
                        meta.update(source="unpaywall:" + str(best.get("host_type")), license=best.get("license"), format="pdf", sha256=sha256(blob))
                        return meta
                except (Unreachable, httpx.HTTPError):
                    pass
    meta["source"] = "paywalled" if doi else "not_found"
    return meta


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--only-missing", action="store_true", default=True)
    ap.add_argument("--limit", type=int, default=None)
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
            if args.only_missing and row.get("access_status") and row["access_status"] not in ("", "not_found"):
                continue
            if args.limit and n >= args.limit:
                break
            meta = fetch_one(client, row, out, email)
            (out / f"{row['pmid']}.meta.json").write_text(json.dumps(meta, indent=2) + "\n")
            row["access_status"] = {"pmc_oa": "pmc_oa_xml", "europepmc": "europepmc_xml"}.get(meta["source"], meta["source"] or "")
            if meta["format"] == "pdf":
                row["access_status"] = "publisher_pdf" if meta["source"] != "pmc_oa" else "pmc_oa_pdf"
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
