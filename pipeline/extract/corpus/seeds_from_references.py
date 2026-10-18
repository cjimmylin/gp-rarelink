"""Stage 1 seeds: reference lists of review papers, via the Europe PMC REST API.

For each source given as LABEL=PMID, fetch that paper's reference list from
Europe PMC (/MED/<pmid>/references) and write
data/literature/<disease>/seeds/refs_<label>.csv with columns
pmid,doi,seed_source,note. References that Europe PMC lists without a PMID are
written to refs_<label>_unresolved.csv so they can be resolved by hand later;
nothing is filled in from memory. Stops on an unreachable host.

Example:
  uv run python -m pipeline.extract.corpus.seeds_from_references --disease ha20 \
      --source elhani2024=38128752 --source li2026=42169681
"""

from __future__ import annotations

import argparse
import csv
from datetime import date
from pathlib import Path

from pipeline.extract.corpus.eutils import EUROPEPMC, Client, Unreachable


def fetch_references(client: Client, pmid: str, page_size: int = 1000) -> list[dict]:
    refs: list[dict] = []
    page = 1
    while True:
        r = client.get(f"{EUROPEPMC}/MED/{pmid}/references", {"format": "json", "pageSize": page_size, "page": page})
        if r.status_code == 404:
            return refs
        r.raise_for_status()
        data = r.json()
        batch = (data.get("referenceList") or {}).get("reference") or []
        refs.extend(batch)
        if len(refs) >= int(data.get("hitCount") or 0) or not batch:
            return refs
        page += 1


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--source", action="append", required=True, help="LABEL=PMID of a review whose references seed the corpus")
    args = ap.parse_args(argv)

    seeds_dir = Path("data/literature") / args.disease / "seeds"
    seeds_dir.mkdir(parents=True, exist_ok=True)
    client = Client()
    today = date.today().isoformat()
    for spec in args.source:
        label, _, pmid = spec.partition("=")
        if not label or not pmid.isdigit():
            raise SystemExit(f"bad --source {spec!r}; expected LABEL=PMID")
        try:
            refs = fetch_references(client, pmid)
        except Unreachable as exc:
            raise SystemExit(f"STOP: Europe PMC unreachable ({exc}).") from exc
        resolved, unresolved = [], []
        for ref in refs:
            ref_pmid = ref.get("id") if ref.get("source") == "MED" else None
            note = f"reference of PMID {pmid} ({label}); Europe PMC references API, {today}"
            if ref_pmid:
                resolved.append({"pmid": ref_pmid, "doi": ref.get("doi") or "", "seed_source": f"refs_{label}", "note": note})
            else:
                unresolved.append({
                    "source_pmid": pmid,
                    "title": ref.get("title") or "",
                    "authors": ref.get("authorString") or "",
                    "journal": ref.get("journalAbbreviation") or "",
                    "year": ref.get("pubYear") or "",
                    "doi": ref.get("doi") or "",
                })
        out = seeds_dir / f"refs_{label}.csv"
        with out.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=["pmid", "doi", "seed_source", "note"])
            w.writeheader()
            w.writerows(sorted({r["pmid"]: r for r in resolved}.values(), key=lambda r: int(r["pmid"])))
        if unresolved:
            with (seeds_dir / f"refs_{label}_unresolved.csv").open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(unresolved[0].keys()))
                w.writeheader()
                w.writerows(unresolved)
        print(f"{label} (PMID {pmid}): {len(refs)} references, {len(resolved)} with PMID, {len(unresolved)} unresolved -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
