"""For corpus papers without fetched full text: does Europe PMC list a free copy elsewhere?

fetch_fulltext gets XML from Europe PMC and PMC only; Unpaywall is skipped while
UNPAYWALL_EMAIL is unset. So "paywalled" in the manifest means "no PMC copy",
not "no free copy anywhere". This script asks the Europe PMC search API
(resultType=core) for each in-corpus row without full text and records the
availability codes of its fullTextUrlList:

  OA  open access (licensed for reuse)
  F   free to read
  S   subscription required
  (none listed)

Nothing is downloaded. Output: data/literature/<disease>/oa_elsewhere.csv and
oa_elsewhere.json (counts, plus counts by publication decade). These feed D-08;
they are an upper bound on what a fetch through publisher sites could add,
since some hosts refuse automated access.

  uv run python -m pipeline.extract.corpus.oa_elsewhere --disease axd
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from pipeline.extract.corpus.eutils import EUROPEPMC, Client, Unreachable

RANK = {"OA": 3, "F": 2, "S": 1}


def lookup(client: Client, pmids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i in range(0, len(pmids), 50):
        chunk = pmids[i : i + 50]
        q = "(" + " OR ".join(f"EXT_ID:{p}" for p in chunk) + ") AND SRC:MED"
        r = client.get(f"{EUROPEPMC}/search", {"query": q, "resultType": "core", "format": "json", "pageSize": 100})
        r.raise_for_status()
        for res in r.json().get("resultList", {}).get("result", []):
            urls = (res.get("fullTextUrlList") or {}).get("fullTextUrl") or []
            codes = sorted({u.get("availabilityCode", "") for u in urls if u.get("availabilityCode")}, key=lambda c: -RANK.get(c, 0))
            free = [u for u in urls if u.get("availabilityCode") in ("OA", "F")]
            out[res.get("pmid", "")] = {
                "best": codes[0] if codes else "none",
                "codes": ";".join(codes),
                "free_sites": ";".join(sorted({u.get("site", "") for u in free})),
                "is_open_access": res.get("isOpenAccess", ""),
                "in_pmc": res.get("inPMC", ""),
            }
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    rows = [r for r in csv.DictReader((base / "manifest.csv").open(newline=""))
            if r.get("in_extraction_corpus", "").lower() == "true" and not r.get("fulltext_format")]
    try:
        found = lookup(Client(), [r["pmid"] for r in rows])
    except Unreachable as e:
        print(f"unreachable: {e}")
        return 2
    out_rows = []
    for r in rows:
        f = found.get(r["pmid"], {"best": "not in Europe PMC", "codes": "", "free_sites": "", "is_open_access": "", "in_pmc": ""})
        out_rows.append({"pmid": r["pmid"], "year": r.get("year", ""), "access_status": r.get("access_status", ""), **f})
    with (base / "oa_elsewhere.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0].keys()) if out_rows else ["pmid"])
        w.writeheader()
        w.writerows(out_rows)

    def decade(y: str) -> str:
        return f"{y[:3]}0s" if y[:4].isdigit() else "unknown"

    summary = {
        "date": datetime.now(UTC).date().isoformat(),
        "source": "Europe PMC REST search, resultType=core, fullTextUrlList availabilityCode",
        "n_in_corpus_without_fulltext": len(out_rows),
        "best_availability": dict(Counter(r["best"] for r in out_rows)),
        "free_elsewhere": sum(r["best"] in ("OA", "F") for r in out_rows),
        "by_decade": {d: dict(Counter(r["best"] for r in out_rows if decade(r["year"]) == d))
                      for d in sorted({decade(r["year"]) for r in out_rows})},
    }
    (base / "oa_elsewhere.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
