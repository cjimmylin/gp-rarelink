"""ClinVar placement of OMIM allelic variants (ground-truth side; never imported by pipeline.extract).

For every allelic variant in <root>/<date>/omim/allelic_variants.csv (written by
pipeline/harness/omim_entries.py from the entry pages Dr. Lin froze on 2026-10-28),
ask ClinVar's E-utilities which Variation record carries it:
  esearch db=clinvar  "<gene MIM>.<nnnn>[OMIM]"     ClinVar's own OMIM cross-reference
  esearch db=clinvar  "<RCV accession>"             each RCV OMIM prints
  esearch db=clinvar  "<rsID>"                      each dbSNP id OMIM prints
then esummary for each VariationID found: title (HGVS on ClinVar's preferred
transcript), canonical SPDI, GRCh38 location and alleles, germline classification
and review status, OMIM cross-references, genes.

Raw responses are cached under <root>/<date>/omim/clinvar_lookup.json. The table
written into the repo (analysis/omim_holdout/omim_av_clinvar.csv) holds ClinVar
facts only (public domain) plus the allelic-variant number and title, which are
identifiers; no OMIM prose.

  uv run python analysis/omim_holdout/clinvar_lookup.py --root /home/user/gp-rarelink-reference --date 2026-10-28
"""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

import urllib.error
import urllib.parse
import urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
REPO = Path(__file__).resolve().parents[2]


class Client:
    """Minimal E-utilities client on the standard library (no httpx in the default uv group); 2.5 requests/s, retries on 429/5xx."""

    def __init__(self, pause: float = 0.4):
        self.pause = pause
        self.last = 0.0

    def get(self, path: str, params: dict) -> dict:
        q = urllib.parse.urlencode({**params, "retmode": "json", "tool": "gp-rarelink", "email": "mail@drjimmylin.com"})
        for attempt in range(6):
            wait = self.pause - (time.monotonic() - self.last)
            if wait > 0:
                time.sleep(wait)
            self.last = time.monotonic()
            try:
                with urllib.request.urlopen(f"{EUTILS}/{path}?{q}", timeout=60) as r:
                    return json.loads(r.read().decode())
            except urllib.error.HTTPError as e:
                if e.code not in (429,) and e.code < 500:
                    raise
            except (urllib.error.URLError, json.JSONDecodeError, TimeoutError):
                pass
            time.sleep(2 ** attempt)
        raise SystemExit(f"E-utilities failed repeatedly: {path} {params}")


def esearch(c: Client, term: str) -> list[str]:
    d = c.get("esearch.fcgi", {"db": "clinvar", "term": term, "retmax": 50})
    return d.get("esearchresult", {}).get("idlist", [])


def esummary(c: Client, ids: list[str]) -> dict:
    out = {}
    for i in range(0, len(ids), 20):
        chunk = ids[i:i + 20]
        d = c.get("esummary.fcgi", {"db": "clinvar", "id": ",".join(chunk)})
        res = d.get("result", {})
        for uid in res.get("uids", []):
            out[uid] = res[uid]
    return out


def grch38(summary: dict) -> dict:
    for vs in summary.get("variation_set", []) or []:
        for loc in vs.get("variation_loc", []) or []:
            if loc.get("assembly_name") == "GRCh38" and loc.get("status") == "current":
                return {"chr": loc.get("chr"), "start": loc.get("start"), "stop": loc.get("stop"), "ref": loc.get("ref"), "alt": loc.get("alt"),
                        "canonical_spdi": vs.get("canonical_spdi"), "variant_type": vs.get("variant_type"),
                        "omim_xrefs": [x["db_id"] for x in vs.get("variation_xrefs", []) if x.get("db_source") == "OMIM"],
                        "dbsnp": [x["db_id"] for x in vs.get("variation_xrefs", []) if x.get("db_source") == "dbSNP"]}
    vs = (summary.get("variation_set") or [{}])[0]
    return {"chr": None, "start": None, "stop": None, "ref": None, "alt": None, "canonical_spdi": vs.get("canonical_spdi"),
            "variant_type": vs.get("variant_type"),
            "omim_xrefs": [x["db_id"] for x in vs.get("variation_xrefs", []) if x.get("db_source") == "OMIM"],
            "dbsnp": [x["db_id"] for x in vs.get("variation_xrefs", []) if x.get("db_source") == "dbSNP"]}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="/home/user/gp-rarelink-reference")
    ap.add_argument("--date", default="2026-10-28")
    ap.add_argument("--out", default="analysis/omim_holdout/omim_av_clinvar.csv")
    args = ap.parse_args(argv)
    folder = Path(args.root) / args.date / "omim"
    avs = list(csv.DictReader((folder / "allelic_variants.csv").open()))
    cache_path = folder / "clinvar_lookup.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {"searches": {}, "summaries": {}, "queried_utc": None}
    c = Client()
    for a in avs:
        terms = [f"{a['av']}[OMIM]"] + [r for r in a["clinvar_rcvs"].split("|") if r] + [r for r in a["rsids"].split("|") if r]
        for t in terms:
            if t not in cache["searches"]:
                cache["searches"][t] = esearch(c, t)
                cache_path.write_text(json.dumps(cache))
    ids = sorted({i for v in cache["searches"].values() for i in v})
    missing = [i for i in ids if i not in cache["summaries"]]
    if missing:
        cache["summaries"].update(esummary(c, missing))
    cache["queried_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    cache_path.write_text(json.dumps(cache))
    rows = []
    for a in avs:
        by_route = {"omim_xref": set(cache["searches"].get(f"{a['av']}[OMIM]", [])),
                    "rcv": {i for r in a["clinvar_rcvs"].split("|") if r for i in cache["searches"].get(r, [])},
                    "rsid": {i for r in a["rsids"].split("|") if r for i in cache["searches"].get(r, [])}}
        found = by_route["omim_xref"] | by_route["rcv"] | by_route["rsid"]
        if not found:
            rows.append({"gene": a["gene"], "av": a["av"], "status": a["status"], "title": a["title"], "omim_label": a["label"],
                         "variation_id": "", "routes": "", "clinvar_title": "", "classification": "", "review_status": "",
                         "variant_type": "", "grch38_chr": "", "grch38_start": "", "grch38_stop": "", "grch38_ref": "", "grch38_alt": "",
                         "canonical_spdi": "", "clinvar_omim_xrefs": "", "clinvar_dbsnp": "", "genes": "", "protein_change": "",
                         "omim_rcvs": a["clinvar_rcvs"], "omim_rsids": a["rsids"]})
            continue
        for vid in sorted(found, key=int):
            s = cache["summaries"].get(vid, {})
            g = grch38(s)
            rows.append({"gene": a["gene"], "av": a["av"], "status": a["status"], "title": a["title"], "omim_label": a["label"],
                         "variation_id": vid, "routes": "|".join(k for k, v in by_route.items() if vid in v),
                         "clinvar_title": s.get("title", ""), "classification": (s.get("germline_classification") or {}).get("description", ""),
                         "review_status": (s.get("germline_classification") or {}).get("review_status", ""),
                         "variant_type": g["variant_type"] or "", "grch38_chr": g["chr"] or "", "grch38_start": g["start"] or "",
                         "grch38_stop": g["stop"] or "", "grch38_ref": g["ref"] or "", "grch38_alt": g["alt"] or "",
                         "canonical_spdi": g["canonical_spdi"] or "", "clinvar_omim_xrefs": "|".join(g["omim_xrefs"]),
                         "clinvar_dbsnp": "|".join(g["dbsnp"]), "genes": "|".join(x.get("symbol", "") for x in s.get("genes", []) or []),
                         "protein_change": s.get("protein_change", ""), "omim_rcvs": a["clinvar_rcvs"], "omim_rsids": a["rsids"]})
    out = REPO / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    n_av = len(avs)
    placed = len({r["av"] for r in rows if r["variation_id"]})
    multi = sum(1 for av in {r["av"] for r in rows} if sum(1 for r in rows if r["av"] == av and r["variation_id"]) > 1)
    print(json.dumps({"allelic_variants": n_av, "placed_in_clinvar": placed, "with_more_than_one_variation_id": multi,
                      "queried_utc": cache["queried_utc"], "out": str(out)}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
