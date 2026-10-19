"""Per-paper use of the rules that helpers applied unevenly (Stage 3b report).

For one run, lists by paper:
  - TNFAIP3 variant rows whose inheritance is "inherited maternal", "inherited
    paternal" or "inherited unspecified parent", with the parental-testing
    statement, so a reader can see which rest on an explicit statement and which
    on the helper's inference from a carrier parent;
  - phenotypic_features and checklist rows marked "inferred from group
    statement", split by status (observed or excluded);
  - checklist rows marked excluded whose status span quotes a table symbol
    definition (a span list of two or more quotes), as a rough count of the v3
    table-symbol rule in use;
  - TNFAIP3 variant rows without a printed variant, and variant rows in other
    genes without a printed variant.

Writes analysis/poc/rule_usage_<run_id>.json and prints the totals.

  uv run python analysis/poc/rule_usage.py --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.reconcile import is_gene

MISSING = {None, "", "not reported"}


def v(cell):
    return (cell or {}).get("value")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    args = ap.parse_args(argv)
    per = Path("data/extracted") / args.disease / args.run_id / "per_paper"
    inherited, groups, symbol_spans, no_string = defaultdict(list), defaultdict(Counter), Counter(), defaultdict(Counter)
    tot = Counter()
    for p in sorted(per.glob("*.json")):
        pmid, t = p.stem, (json.loads(p.read_text()).get("tables") or {})
        for r in t.get("variants") or []:
            target = is_gene(v(r.get("gene_symbol_as_stated")), args.gene)
            if v(r.get("variant_original_string")) in MISSING:
                no_string[pmid]["target_gene" if target else "other_gene"] += 1
                tot["variant_rows_without_string_" + ("target_gene" if target else "other_gene")] += 1
            inh = v(r.get("inheritance"))
            if target and str(inh).startswith("inherited"):
                inherited[pmid].append({"individual": v(r.get("individual_label_in_paper")), "inheritance": inh,
                                        "parental_testing_statement": (r.get("parental_testing_statement") or {}).get("span")})
                tot[f"inheritance:{inh}"] += 1
        for table in ("phenotypic_features", "phenotype_checklist"):
            for r in t.get(table) or []:
                if v(r.get("evidence_basis")) == "inferred from group statement":
                    groups[pmid][f"{table}:{v(r.get('status'))}"] += 1
                    tot[f"group_statement:{table}:{v(r.get('status'))}"] += 1
        for r in t.get("phenotype_checklist") or []:
            span = (r.get("status") or {}).get("span")
            if v(r.get("status")) == "excluded" and isinstance(span, list) and len(span) >= 2:
                symbol_spans[pmid] += 1
                tot["checklist_excluded_with_two_or_more_quotes"] += 1
    out = {"run_id": args.run_id, "totals": dict(sorted(tot.items())),
           "inherited_rows_by_paper": dict(inherited),
           "group_statement_rows_by_paper": {k: dict(c) for k, c in groups.items()},
           "checklist_excluded_with_two_or_more_quotes_by_paper": dict(symbol_spans),
           "variant_rows_without_string_by_paper": {k: dict(c) for k, c in no_string.items()}}
    (Path("analysis/poc") / f"rule_usage_{args.run_id}.json").write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(out["totals"], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
