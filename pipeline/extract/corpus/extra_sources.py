"""Corpus seeds from sources beyond the PubMed query and review reference lists.

Written 2026-11-15 for the Majeed syndrome (LPIN2) search, where Dr. Lin asked
for every available search method. The six registered corpora used only the
PubMed query and backward citations (pre-registration §5.1, D-35); these extra
sources are not part of that registered search.

Each command writes one seed CSV (pmid,doi,seed_source,note) under
data/literature/<disease>/seeds/, ready for build_manifest.py --seeds, and, where
a source returns records with no PMID, a *_nopmid.csv beside it for hand review.
Every PMID keeps the name of the source that found it.

  epmc        Europe PMC search (title, abstract AND open full text):
              --query is a Europe PMC query string.
  citations   Forward citations of key papers from Europe PMC (/citations):
              --source LABEL=PMID, repeatable.
  similar     PubMed "similar articles" (elink neighbor_score), top --top per
              key paper: --source LABEL=PMID, repeatable.
  litvar      LitVar2, queried by gene symbol only (pre-registration §5.1): every
              variant LitVar lists for the gene, and the PMIDs it links to each.
              No variant is filtered by any database assertion it carries; that
              field is ignored.
  openalex    OpenAlex works search (title, abstract and full text) for --query,
              plus works citing each --source LABEL=PMID.

No source here is a variant-database citation list. Stops on an unreachable host;
never fills rows from memory.

  uv run python -m pipeline.extract.corpus.extra_sources epmc --disease majeed --label majeed --query '"Majeed syndrome"'
"""

from __future__ import annotations

import argparse
import csv
import json
import time
import xml.etree.ElementTree as ET
from datetime import date
from pathlib import Path
from urllib.parse import quote

import httpx

from pipeline.extract.corpus.eutils import EUROPEPMC, Client, Unreachable

LITVAR = "https://www.ncbi.nlm.nih.gov/research/litvar2-api"
OPENALEX = "https://api.openalex.org"
ELINK = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/elink.fcgi"


def seeds_dir(disease: str) -> Path:
    d = Path("data/literature") / disease / "seeds"
    d.mkdir(parents=True, exist_ok=True)
    return d


def write(disease: str, name: str, rows: dict[str, dict], nopmid: list[dict] | None = None) -> None:
    out = seeds_dir(disease) / f"{name}.csv"
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pmid", "doi", "seed_source", "note"])
        w.writeheader()
        for pmid in sorted(rows, key=int):
            w.writerow({"pmid": pmid, **rows[pmid]})
    msg = f"{out}: {len(rows)} PMIDs"
    if nopmid:
        out2 = seeds_dir(disease) / f"{name}_nopmid.csv"
        cols = sorted({k for r in nopmid for k in r})
        with out2.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=cols)
            w.writeheader()
            w.writerows(nopmid)
        msg += f"; {len(nopmid)} records without a PMID in {out2}"
    print(msg)
    log = seeds_dir(disease) / "extra_sources_log.json"
    data = json.loads(log.read_text()) if log.exists() else {"runs": []}
    data["runs"].append({"date": date.today().isoformat(), "file": out.name, "n_pmids": len(rows),
                         "n_without_pmid": len(nopmid or [])})
    log.write_text(json.dumps(data, indent=2) + "\n")


def parse_sources(items: list[str]) -> list[tuple[str, str]]:
    return [tuple(s.split("=", 1)) for s in items]  # type: ignore[misc]


def epmc(client: Client, query: str) -> tuple[dict[str, dict], list[dict], int]:
    rows: dict[str, dict] = {}
    nopmid: list[dict] = []
    cursor, hit = "*", 0
    while True:
        r = client.get(f"{EUROPEPMC}/search", {"query": query, "format": "json", "pageSize": 1000,
                                               "cursorMark": cursor, "resultType": "lite"})
        r.raise_for_status()
        data = r.json()
        hit = int(data.get("hitCount") or 0)
        for res in (data.get("resultList") or {}).get("result") or []:
            if res.get("pmid"):
                rows[res["pmid"]] = {"doi": res.get("doi", ""), "note": ""}
            else:
                nopmid.append({"source": res.get("source", ""), "id": res.get("id", ""), "doi": res.get("doi", ""),
                               "title": res.get("title", ""), "year": res.get("pubYear", ""),
                               "journal": res.get("journalTitle", "") or res.get("bookOrReportDetails", {}).get("publisher", "")})
        nxt = data.get("nextCursorMark")
        if not nxt or nxt == cursor:
            break
        cursor = nxt
    return rows, nopmid, hit


def epmc_citations(client: Client, pmid: str) -> tuple[list[str], list[dict]]:
    pmids, nopmid, page = [], [], 1
    while True:
        r = client.get(f"{EUROPEPMC}/MED/{pmid}/citations", {"format": "json", "pageSize": 1000, "page": page})
        if r.status_code == 404:
            break
        r.raise_for_status()
        data = r.json()
        batch = (data.get("citationList") or {}).get("citation") or []
        for c in batch:
            if c.get("source") == "MED" and c.get("id"):
                pmids.append(c["id"])
            else:
                nopmid.append({"source": c.get("source", ""), "id": c.get("id", ""), "title": c.get("title", ""),
                               "year": c.get("pubYear", ""), "journal": c.get("journalAbbreviation", "")})
        if not batch or len(pmids) + len(nopmid) >= int(data.get("hitCount") or 0):
            break
        page += 1
    return pmids, nopmid


def similar(client: Client, pmid: str, top: int) -> list[str]:
    r = client.get(ELINK, {"dbfrom": "pubmed", "db": "pubmed", "cmd": "neighbor_score", "id": pmid})
    r.raise_for_status()
    root = ET.fromstring(r.content)
    out: list[tuple[int, str]] = []
    for lsd in root.iter("LinkSetDb"):
        if lsd.findtext("LinkName") != "pubmed_pubmed":
            continue
        for link in lsd.iter("Link"):
            lid, score = link.findtext("Id"), int(link.findtext("Score") or 0)
            if lid and lid != pmid:
                out.append((score, lid))
    return [lid for _, lid in sorted(out, reverse=True)[:top]]


def _get_json(url: str, params: dict | None = None, tries: int = 5) -> dict:
    for i in range(tries):
        try:
            r = httpx.get(url, params=params, timeout=60)
        except httpx.TransportError as exc:
            if i == tries - 1:
                raise Unreachable(str(exc)) from exc
            time.sleep(2 ** i)
            continue
        if r.status_code == 429 or r.status_code >= 500:
            time.sleep(2 ** i)
            continue
        if r.status_code == 404:
            return {}
        r.raise_for_status()
        return r.json()
    raise Unreachable(f"{url}: gave up after {tries} tries")


def litvar(gene: str) -> tuple[dict[str, list[str]], int]:
    """PMIDs per LitVar variant for one gene symbol. Returns {pmid: [variant names]}, n_variants."""
    r = httpx.get(f"{LITVAR}/variant/search/gene/{gene}", timeout=120)
    r.raise_for_status()
    variants = [json.loads(line.replace("'", '"')) for line in r.text.splitlines() if line.strip()]
    by_pmid: dict[str, list[str]] = {}
    for v in variants:
        vid = v["_id"]
        data = _get_json(f"{LITVAR}/variant/get/{quote(vid, safe='')}/publications")
        for p in data.get("pmids") or []:
            by_pmid.setdefault(str(p), []).append(v.get("rsid") or vid)
        time.sleep(0.2)
    return by_pmid, len(variants)


def _oa_pmid(work: dict) -> str:
    p = (work.get("ids") or {}).get("pmid") or ""
    return p.rsplit("/", 1)[-1] if p else ""


def openalex_works(params: dict) -> list[dict]:
    # Page-based paging: cursor paging answered 401 without an API key (2026-11-15).
    works, page = [], 1
    while True:
        data = _get_json(f"{OPENALEX}/works", {**params, "per-page": 200, "page": page,
                                               "select": "id,ids,doi,title,publication_year,type,primary_location"})
        batch = data.get("results") or []
        works.extend(batch)
        if not batch or len(works) >= int((data.get("meta") or {}).get("count") or 0):
            return works
        page += 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["epmc", "citations", "similar", "litvar", "openalex"])
    ap.add_argument("--disease", required=True)
    ap.add_argument("--label", default="")
    ap.add_argument("--query", default="")
    ap.add_argument("--gene", default="")
    ap.add_argument("--source", action="append", default=[])
    ap.add_argument("--top", type=int, default=50)
    a = ap.parse_args(argv)
    client = Client()
    try:
        if a.cmd == "epmc":
            rows, nopmid, hit = epmc(client, a.query)
            for r in rows.values():
                r.update(seed_source=f"epmc_search_{a.label}", note="")
            print(f"Europe PMC hitCount {hit} for {a.query!r}")
            write(a.disease, f"epmc_{a.label}", rows, nopmid)
        elif a.cmd == "citations":
            for label, pmid in parse_sources(a.source):
                pmids, nopmid = epmc_citations(client, pmid)
                write(a.disease, f"cites_{label}", {p: {"doi": "", "seed_source": f"cited_by_{label}", "note": f"cites PMID {pmid} (Europe PMC)"} for p in pmids}, nopmid)
        elif a.cmd == "similar":
            for label, pmid in parse_sources(a.source):
                pmids = similar(client, pmid, a.top)
                write(a.disease, f"similar_{label}", {p: {"doi": "", "seed_source": f"pubmed_similar_{label}", "note": f"PubMed similar articles to {pmid}, top {a.top}"} for p in pmids})
        elif a.cmd == "litvar":
            by_pmid, nvar = litvar(a.gene)
            print(f"LitVar2: {nvar} variants for {a.gene}")
            write(a.disease, f"litvar_{a.gene}", {p: {"doi": "", "seed_source": f"litvar_gene_{a.gene}",
                                                      "note": "variants: " + ", ".join(sorted(set(v))[:5]) + (" ..." if len(set(v)) > 5 else "")}
                                                  for p, v in by_pmid.items()})
        elif a.cmd == "openalex":
            def split(works, src, note):
                rows, nopmid = {}, []
                for w in works:
                    p = _oa_pmid(w)
                    if p:
                        rows[p] = {"doi": (w.get("doi") or "").replace("https://doi.org/", ""), "seed_source": src, "note": note}
                    else:
                        loc = (w.get("primary_location") or {}).get("source") or {}
                        nopmid.append({"openalex": w.get("id", ""), "doi": w.get("doi") or "", "title": w.get("title") or "",
                                       "year": w.get("publication_year") or "", "type": w.get("type") or "",
                                       "venue": loc.get("display_name", "")})
                return rows, nopmid
            if a.query:
                works = openalex_works({"search": a.query})
                print(f"OpenAlex search {a.query!r}: {len(works)} works")
                write(a.disease, f"openalex_{a.label}", *split(works, f"openalex_search_{a.label}", ""))
            for label, pmid in parse_sources(a.source):
                w = _get_json(f"{OPENALEX}/works/pmid:{pmid}")
                if not w:
                    print(f"OpenAlex has no work for PMID {pmid}")
                    continue
                wid = w["id"].rsplit("/", 1)[-1]
                works = openalex_works({"filter": f"cites:{wid}"})
                write(a.disease, f"openalex_cites_{label}", *split(works, f"openalex_cited_by_{label}", f"cites PMID {pmid} (OpenAlex {wid})"))
    except Unreachable as exc:
        raise SystemExit(f"STOP: host unreachable ({exc}).") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
