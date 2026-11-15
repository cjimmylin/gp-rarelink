"""Confirm or add the extension diseases' key reviews in background/manifest.csv (D-47).

Every title, author list, year, venue and identifier is read from Europe PMC's core
record for the PMID at run time; nothing is typed from memory. Existing rows keep their
key and notes; only a title marked "exact title not confirmed" is replaced, and the
confirmation is written into id_notes with the date.

    python3 -I analysis/extension/update_background_manifest.py
"""
from __future__ import annotations

import csv
import datetime as dt
import io
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

MANIFEST = Path("background/manifest.csv")
# key -> (pmid, relevance note for new rows)
ROWS = {
    "wouters2014_blau": ("25136265", None),
    "rose2015_blau_cohort": ("25416713", None),
    "wang2025_blau_review": ("40456554", "Blau syndrome state-of-the-art review; key review for the extension (D-47)."),
    "ferguson2021_majeed": ("33670882", None),
    "vitali2022_lcat": ("35065092", None),
    "stockleripsiroglu2014_gamt": ("24268530", None),
    "biagiotti2025_gamt_review": ("41373441", "GAMT deficiency review; key review for the extension (D-47)."),
    "beyens2018_ats": ("29323665", None),
    "genovese2020_papa_spectrum": ("32618443", "PAPA-spectrum disorders review; key review for the extension (D-47)."),
    "satoh2024_pg_genetics": ("38031879", "Review of genetic variants in pyoderma gangrenosum and associated autoinflammatory syndromes incl. PAPA; key review for the extension (D-47)."),
}


def epmc(pmid: str) -> dict:
    q = urllib.parse.urlencode({"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core"})
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"https://www.ebi.ac.uk/europepmc/webservices/rest/search?{q}", timeout=60) as r:
                return json.load(r)["resultList"]["result"][0]
        except Exception:
            time.sleep(3 * (attempt + 1))
    raise SystemExit(f"Europe PMC unreachable for {pmid}; nothing written")


def venue(r: dict) -> str:
    j = r.get("journalInfo", {})
    t = j.get("journal", {}).get("isoabbreviation") or j.get("journal", {}).get("title") or r.get("bookOrReportDetails", {}).get("publisher", "")
    vol, iss, pg = j.get("volume", ""), j.get("issue", ""), r.get("pageInfo", "")
    s = t
    if vol:
        s += f" {vol}" + (f"({iss})" if iss else "")
    if pg:
        s += f":{pg}"
    return s.strip()


def main() -> None:
    text = MANIFEST.read_text()
    rows = list(csv.DictReader(io.StringIO(text)))
    fields = list(rows[0].keys())
    by_key = {r["key"]: r for r in rows}
    today = dt.date.today().isoformat()
    for key, (pmid, rel) in ROWS.items():
        r = epmc(pmid)
        title = r["title"].rstrip(".")
        if key in by_key:
            row = by_key[key]
            if row["pmid"] != pmid:
                raise SystemExit(f"{key}: manifest PMID {row['pmid']} != {pmid}")
            if "not confirmed" in row["title"]:
                row["title"] = title
                row["id_notes"] = f"Title confirmed from Europe PMC, {today}."
                row["verified_at"] = row["verified_at"] or f"https://europepmc.org/article/MED/{pmid}"
                print("confirmed", key, "|", title[:80])
        else:
            pmcid = r.get("pmcid", "")
            row = {f: "" for f in fields}
            row.update({
                "key": key, "theme": "diseases", "subtheme": "Substitutes", "priority": "supporting",
                "authors": r.get("authorString", "").rstrip("."), "year": r.get("pubYear", ""),
                "title": title, "venue": venue(r), "pmid": pmid, "pmcid": pmcid, "doi": r.get("doi", ""),
                "oa_status": "open (PMC)" if r.get("isOpenAccess") == "Y" else "not open in Europe PMC",
                "url": f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}" if pmcid else "",
                "verified_at": f"https://europepmc.org/article/MED/{pmid}",
                "id_notes": f"Added from Europe PMC's record, {today}.", "relevance": rel,
            })
            rows.append(row)
            print("added", key, "|", title[:80])
        time.sleep(0.3)
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=fields, lineterminator="\r\n")
    w.writeheader()
    w.writerows(rows)
    MANIFEST.write_text(out.getvalue())


if __name__ == "__main__":
    main()
