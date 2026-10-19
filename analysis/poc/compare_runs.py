"""Compare two full extraction runs paper by paper (Stage 3b: run-1 vs run-2, D-22).

Unlike run_agreement.py, which measures stability between two runs under the
same instructions, this script describes what changed between runs whose
inputs differ on purpose (run-2: extract_v3, schema v3, converter fixes and
supplementary files). For every paper in either run it reports:

  - the reports_individuals_with_tnfaip3_variant flag in each run;
  - individual rows in each run;
  - TNFAIP3 variant rows with a printed variant in each run;
  - TNFAIP3 variant keys (folded cDNA/protein keys from pipeline.extract.reconcile)
    found only in run A, only in run B, and in both;
  - whether run B's Markdown had a supplementary section appended
    (data/literature/<disease>/supplementary/conversion.csv).

Totals split the gains and losses by whether the paper had supplementary text,
so the effect of the supplements can be told apart from the instruction change.

Writes analysis/poc/compare_runs_<a>_vs_<b>.json and prints the totals.

  uv run python analysis/poc/compare_runs.py --disease ha20 --run-a poc-ha20-run-1 --run-b poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path

from pipeline.extract.reconcile import cdna_key, is_gene, orig_key, protein_key

MISSING = {None, "", "not reported"}


def v(cell):
    return (cell or {}).get("value")


def vkey(r) -> str | None:
    return (cdna_key(v(r.get("cdna_hgvs_as_stated"))) or cdna_key(v(r.get("variant_original_string")))
            or protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(v(r.get("variant_original_string")))
            or orig_key(v(r.get("variant_original_string"))))


def summarise(doc: dict | None, gene: str) -> dict:
    if doc is None:
        return {"present": False}
    t = doc.get("tables") or {}
    keys, printed = set(), 0
    for r in t.get("variants") or []:
        if not is_gene(v(r.get("gene_symbol_as_stated")), gene):
            continue
        if v(r.get("variant_original_string")) in MISSING:
            continue
        printed += 1
        if k := vkey(r):
            keys.add(k)
    return {"present": True, "flag": doc.get("reports_individuals_with_tnfaip3_variant"),
            "individuals": len(t.get("individuals") or []), "tnfaip3_printed_variant_rows": printed, "keys": keys}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-a", required=True)
    ap.add_argument("--run-b", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    args = ap.parse_args(argv)
    base = Path("data/extracted") / args.disease
    load = lambda run: {p.stem: json.loads(p.read_text()) for p in sorted((base / run / "per_paper").glob("*.json"))}  # noqa: E731
    a, b = load(args.run_a), load(args.run_b)
    conv = Path("data/literature") / args.disease / "supplementary" / "conversion.csv"
    with_supp = set()
    if conv.exists():
        with_supp = {r["pmid"] for r in csv.DictReader(conv.open()) if r["status"].startswith("included")}
    gene = args.gene.upper()
    per_paper, tot = {}, Counter()
    for p in sorted(set(a) | set(b)):
        sa, sb = summarise(a.get(p), gene), summarise(b.get(p), gene)
        supp = p in with_supp
        grp = "with_supplement" if supp else "without_supplement"
        row = {"supplement_appended": supp}
        if sa["present"] and sb["present"]:
            only_a, only_b, both = sa["keys"] - sb["keys"], sb["keys"] - sa["keys"], sa["keys"] & sb["keys"]
            row |= {
                "flag": [sa["flag"], sb["flag"]],
                "individuals": [sa["individuals"], sb["individuals"]],
                "tnfaip3_printed_variant_rows": [sa["tnfaip3_printed_variant_rows"], sb["tnfaip3_printed_variant_rows"]],
                "variant_keys_only_a": sorted(only_a), "variant_keys_only_b": sorted(only_b), "variant_keys_both": len(both),
            }
            tot["papers_in_both"] += 1
            tot[f"papers_{grp}"] += 1
            if sa["flag"] != sb["flag"]:
                tot[f"flag_{str(sa['flag']).lower()}_to_{str(sb['flag']).lower()}"] += 1
            d = sb["individuals"] - sa["individuals"]
            tot["papers_more_individuals_in_b" if d > 0 else "papers_fewer_individuals_in_b" if d < 0 else "papers_same_individuals"] += 1
            tot[f"individuals_a_{grp}"] += sa["individuals"]
            tot[f"individuals_b_{grp}"] += sb["individuals"]
            tot[f"variant_keys_only_a_{grp}"] += len(only_a)
            tot[f"variant_keys_only_b_{grp}"] += len(only_b)
            tot[f"variant_keys_both_{grp}"] += len(both)
        else:
            row |= {"present_in": args.run_a if sa["present"] else args.run_b}
            tot["papers_in_one_run_only"] += 1
        per_paper[p] = row
    out = {"run_a": args.run_a, "run_b": args.run_b, "gene": gene,
           "supplement_source": str(conv) if conv.exists() else None,
           "totals": dict(sorted(tot.items())), "per_paper": per_paper}
    dest = Path("analysis/poc") / f"compare_runs_{args.run_a}_vs_{args.run_b}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
