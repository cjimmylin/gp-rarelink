"""Harness-side helper: PMIDs that ClinVar cites for one gene, as a corpus seed list.

Why this lives on the harness side: it queries ClinVar, which only the harness
may touch. It keeps nothing from ClinVar except the list of cited PMIDs, and
writes that list as data/literature/<disease>/seeds/clinvar_citations.csv with
seed_source = clinvar_citations so every paper it adds can be separated later.
POC_DESIGN.md Stage 1 includes these seeds; D-19 (open) recommends reporting
pilot results with and without them.

Method: E-utilities esearch on db=clinvar for "<GENE>[gene]", then elink
clinvar -> pubmed (linkname clinvar_pubmed). No ClinVar files are downloaded
and no variant-level content is stored.

  uv run python -m pipeline.harness.seed_from_clinvar --disease ha20 --gene TNFAIP3
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from pipeline.extract.corpus.eutils import EUTILS, Client, Unreachable


def chunked(xs: list[str], n: int):
    for i in range(0, len(xs), n):
        yield xs[i : i + n]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--gene", required=True)
    args = ap.parse_args(argv)

    client = Client()
    try:
        r = client.get(f"{EUTILS}/esearch.fcgi", {"db": "clinvar", "term": f"{args.gene}[gene]", "retmax": 10000, "retmode": "json"})
        r.raise_for_status()
        ids = r.json()["esearchresult"]["idlist"]
        pmids: set[str] = set()
        for batch in chunked(ids, 200):
            lr = client.get(f"{EUTILS}/elink.fcgi", {"dbfrom": "clinvar", "db": "pubmed", "linkname": "clinvar_pubmed", "id": ",".join(batch), "retmode": "json"})
            lr.raise_for_status()
            for ls in lr.json().get("linksets", []):
                for db in ls.get("linksetdbs", []) or []:
                    pmids.update(str(x) for x in db.get("links", []))
    except Unreachable as exc:
        raise SystemExit(f"STOP: NCBI unreachable ({exc}).") from exc

    today = date.today().isoformat()
    out = Path("data/literature") / args.disease / "seeds" / "clinvar_citations.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pmid", "doi", "seed_source", "note"])
        w.writeheader()
        for pmid in sorted(pmids, key=int):
            w.writerow({"pmid": pmid, "doi": "", "seed_source": "clinvar_citations",
                        "note": f"cited by >=1 record returned for {args.gene}[gene]; E-utilities elink, {today}"})
    print(f"{args.gene}: {len(ids)} records queried, {len(pmids)} distinct cited PMIDs -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
