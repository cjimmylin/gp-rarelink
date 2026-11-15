"""Build the URL list for papers Europe PMC lists as free (OA/F) but our fetch did not get.

Reads reports/paywalled_papers_<date>.csv, asks the Europe PMC REST search API
(resultType=core) for each paper's fullTextUrlList, and writes
data/literature/free_copies/candidates_<date>.json (git-ignored folder) with, per
paper, the free URLs in the order fetch_browser.js tries them: PDF links first,
then other HTML links, then DOI landing pages. Europe PMC and PMC website links
are kept apart: both sites answer an automated browser with a challenge page
(Cloudflare, reCAPTCHA), which we do not try to get past.

  python3 analysis/corpus/free_copies/candidates.py --date 2026-11-14
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
REST = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
CHALLENGE_HOSTS = ("europepmc.org", "ncbi.nlm.nih.gov")


def get_json(url: str, tries: int = 5) -> dict:
    for k in range(tries):
        try:
            return json.load(urllib.request.urlopen(url, timeout=60))
        except Exception:
            if k == tries - 1:
                raise
            time.sleep(5 * (k + 1))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    rows = [r for r in csv.DictReader(open(ROOT / f"reports/paywalled_papers_{a.date}.csv"))
            if r["europepmc_availability"] in ("OA", "F")]
    lists: dict[str, list] = {}
    pmids = [r["pmid"] for r in rows]
    for i in range(0, len(pmids), 50):
        q = "(" + " OR ".join(f"EXT_ID:{p}" for p in pmids[i:i + 50]) + ") AND SRC:MED"
        url = REST + "?" + urllib.parse.urlencode({"query": q, "resultType": "core", "format": "json", "pageSize": 100})
        for res in get_json(url)["resultList"]["result"]:
            lists[res["pmid"]] = (res.get("fullTextUrlList") or {}).get("fullTextUrl", []), res.get("pmcid", "")
    out = []
    for r in rows:
        urls, pmcid = lists.get(r["pmid"], ([], ""))
        free = [u for u in urls if u["availabilityCode"] in ("OA", "F")]
        challenge = [u["url"] for u in free if any(h in urllib.parse.urlparse(u["url"]).netloc for h in CHALLENGE_HOSTS)]
        if not pmcid:
            m = next((re.search(r"PMC\d+", c) for c in challenge if re.search(r"PMC\d+", c)), None)
            pmcid = m.group(0) if m else ""
        rest = [u for u in free if u["url"] not in challenge]
        rank = {"pdf": 0, "html": 1, "doi": 2, "abs": 3}
        rest.sort(key=lambda u: rank.get(u["documentStyle"], 4))
        seen, tries = set(), []
        for u in rest:
            if u["url"] not in seen:
                seen.add(u["url"])
                tries.append({"url": u["url"], "style": u["documentStyle"], "site": u["site"], "code": u["availabilityCode"]})
        out.append({"disease": r["disease"], "pmid": r["pmid"], "doi": r["doi"], "pmcid": pmcid,
                    "priority": r["priority"], "try": tries, "challenge_urls": challenge})
    dest = ROOT / "data/literature/free_copies"
    dest.mkdir(parents=True, exist_ok=True)
    (dest / f"candidates_{a.date}.json").write_text(json.dumps(out, indent=1))
    print(len(out), "papers;", sum(bool(o["try"]) for o in out), "with a non-PMC free URL;",
          sum(bool(o["pmcid"]) for o in out), "with a PMCID")


if __name__ == "__main__":
    main()
