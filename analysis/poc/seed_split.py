"""Run counts with and without ClinVar-seeded papers (D-19).

Some corpus papers were found because ClinVar cites them (seed_source
clinvar_citations, harness side). D-19 asks for pilot results reported with and
without those papers. This script splits a run's papers three ways, using only
the manifest's seed_sources column (no ClinVar content is read):

  clinvar_only   found only through ClinVar citations;
  clinvar_also   found through ClinVar citations and at least one other route;
  no_clinvar     never seeded from ClinVar.

and reports papers, individuals, TNFAIP3 variant rows and distinct TNFAIP3
variant strings for: all papers; all minus clinvar_only; no_clinvar only.

Writes analysis/poc/seed_split_<run_id>.json.

  uv run python analysis/poc/seed_split.py --disease ha20 --run-id poc-ha20-run-1
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

from pipeline.extract.reconcile import is_gene

MISSING = {None, "", "not reported"}


def v(cell):
    return (cell or {}).get("value")


def tally(docs: dict[str, dict], gene: str) -> dict:
    inds = rows = 0
    distinct: set[str] = set()
    with_rows = 0
    for doc in docs.values():
        t = doc.get("tables") or {}
        n = len(t.get("individuals") or [])
        inds += n
        with_rows += bool(n)
        for r in t.get("variants") or []:
            if is_gene(v(r.get("gene_symbol_as_stated")), gene):
                rows += 1
                orig = v(r.get("variant_original_string"))
                if orig not in MISSING:
                    distinct.add(re.sub(r"\s+", "", str(orig)).lower())
    return {"papers": len(docs), "papers_with_individual_rows": with_rows, "individuals": inds,
            "tnfaip3_variant_rows": rows, "distinct_tnfaip3_variant_strings": len(distinct)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    args = ap.parse_args(argv)
    manifest = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / args.disease / "manifest.csv").open())}
    per = Path("data/extracted") / args.disease / args.run_id / "per_paper"
    docs = {p.stem: json.loads(p.read_text()) for p in sorted(per.glob("*.json"))}
    group = {}
    for pmid in docs:
        seeds = {s.strip() for s in manifest.get(pmid, {}).get("seed_sources", "").split(";") if s.strip()}
        group[pmid] = ("clinvar_only" if seeds == {"clinvar_citations"}
                       else "clinvar_also" if "clinvar_citations" in seeds else "no_clinvar")
    gene = args.gene.upper()
    out = {
        "run_id": args.run_id,
        "groups": {g: sorted(p for p in docs if group[p] == g) for g in ("clinvar_only", "clinvar_also", "no_clinvar")},
        "all_papers": tally(docs, gene),
        "excluding_clinvar_only": tally({p: d for p, d in docs.items() if group[p] != "clinvar_only"}, gene),
        "no_clinvar_seed_at_all": tally({p: d for p, d in docs.items() if group[p] == "no_clinvar"}, gene),
    }
    dest = Path("analysis/poc") / f"seed_split_{args.run_id}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in out if k != "groups"} | {"group_sizes": {g: len(x) for g, x in out["groups"].items()}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
