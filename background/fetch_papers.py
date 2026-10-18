#!/usr/bin/env python3
"""Download the open-access papers listed in manifest.csv into background/papers/.

GP-RareLink background literature. Standard library only (Python 3.8+).

Usage (run from anywhere):
    python3 fetch_papers.py                 # download everything open access
    python3 fetch_papers.py --theme diseases
    python3 fetch_papers.py --dry-run       # show what would be fetched

Sources tried, in order, for each row:
  1. arXiv PDF                (arxiv_id column)
  2. Europe PMC PDF render    (pmcid column)
  3. Europe PMC full-text XML (pmcid column; saved as .xml when no PDF is served)
  4. url column               (only when oa_status starts with "open")

Paywalled or unknown-access rows are skipped and listed in download_log.csv,
so the corpus manifest can record which papers we could not access
(see INSTRUCTIONS.md, "Licensing"). Nothing is downloaded from a source
that is not open access.
"""
import argparse
import csv
import datetime as dt
import os
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "manifest.csv")
OUT_ROOT = os.path.join(HERE, "papers")
LOG = os.path.join(HERE, "download_log.csv")
UA = "GP-RareLink-background-fetch/1.0 (Rare Genomics Institute; mailto:jimmy.lin@raregenomics.org)"
PAUSE_S = 1.0  # be polite to arXiv / Europe PMC


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def is_pdf(data):
    return data[:5] == b"%PDF-"


def candidates(row):
    arx = (row.get("arxiv_id") or "").strip()
    pmc = (row.get("pmcid") or "").strip().upper()
    url = (row.get("url") or "").strip()
    oa = (row.get("oa_status") or "").lower()
    if arx and arx.upper() != "UNVERIFIED":
        yield "pdf", f"https://arxiv.org/pdf/{arx}"
    if pmc.startswith("PMC"):
        yield "pdf", f"https://europepmc.org/articles/{pmc}?pdf=render"
        yield "xml", f"https://www.ebi.ac.uk/europepmc/webservices/rest/{pmc}/fullTextXML"
    if url and oa.startswith("open") and not (arx and url.rstrip("/").endswith(arx)):
        yield "pdf", url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", help="only rows whose theme column matches")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="re-download existing files")
    args = ap.parse_args()

    with open(MANIFEST, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if args.theme:
        rows = [r for r in rows if r["theme"] == args.theme]

    log = []
    today = dt.date.today().isoformat()
    for row in rows:
        key, theme = row["key"], row["theme"]
        outdir = os.path.join(OUT_ROOT, theme)
        existing = [p for p in (os.path.join(outdir, key + ext) for ext in (".pdf", ".xml")) if os.path.exists(p)]
        if existing and not args.force:
            log.append((key, theme, "already_present", os.path.relpath(existing[0], HERE), "", today))
            continue
        oa = (row.get("oa_status") or "").lower()
        if oa.startswith(("free-html", "software", "official page")):
            log.append((key, theme, "read_online", "", row.get("url", ""), today))
            print(f"web   {key}: read online at {row.get('url', '')}")
            continue
        cands = list(candidates(row))
        if not cands:
            log.append((key, theme, "skipped_no_open_download", "", row.get("oa_status", ""), today))
            print(f"skip  {key}: no open-access download on file ({row.get('oa_status', '')})")
            continue
        if args.dry_run:
            print(f"would {key}: " + " | ".join(u for _, u in cands))
            continue
        os.makedirs(outdir, exist_ok=True)
        done = False
        last_err = ""
        for kind, url in cands:
            try:
                data, ctype = get(url)
                time.sleep(PAUSE_S)
            except (urllib.error.URLError, TimeoutError, OSError) as e:
                last_err = f"{url}: {e}"
                continue
            if kind == "pdf" and is_pdf(data):
                path = os.path.join(outdir, key + ".pdf")
            elif kind == "xml" and data.lstrip().startswith(b"<"):
                path = os.path.join(outdir, key + ".xml")
            else:
                last_err = f"{url}: unexpected content ({ctype})"
                continue
            with open(path, "wb") as f:
                f.write(data)
            log.append((key, theme, "downloaded", os.path.relpath(path, HERE), url, today))
            print(f"ok    {key} <- {url}")
            done = True
            break
        if not done:
            log.append((key, theme, "failed", "", last_err, today))
            print(f"FAIL  {key}: {last_err}", file=sys.stderr)

    if not args.dry_run:
        with open(LOG, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["key", "theme", "status", "file", "source_or_note", "date"])
            w.writerows(log)
        n_ok = sum(1 for r in log if r[2] in ("downloaded", "already_present"))
        print(f"\n{n_ok}/{len(log)} available locally; details in {os.path.relpath(LOG)}")


if __name__ == "__main__":
    main()
