"""Rule-by-rule check of instructions v4 against run-2 on the 10 purposive papers (D-24 item 7).

Each paper in runs/poc-ha20-v4-check/selection.json was picked for one or more
rules changed in v4. For each, this script measures the rule's target in run-2
(instructions v3) and in the v4 check run, and says whether v4 behaves as the
rule intends. The checks are mechanical counts from the extraction files; the
expected direction is written next to each check.

Writes analysis/poc/v4_check_<run_id>.json and prints a table.

  uv run python analysis/poc/v4_check.py --disease ha20 --run-a poc-ha20-run-2 --run-b poc-ha20-v4-check
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pipeline.extract.reconcile import is_gene

MISSING = {None, "", "not reported"}


def v(cell):
    return (cell or {}).get("value")


def tables(run: Path, pmid: str) -> dict:
    return json.loads((run / "per_paper" / f"{pmid}.json").read_text()).get("tables") or {}


def tn_rows(t):
    return [r for r in t.get("variants") or [] if is_gene(v(r.get("gene_symbol_as_stated")), "TNFAIP3")]


def checks() -> dict:
    """pmid -> list of (name, function(tables) -> value, test(a, b) -> bool, expectation)."""
    inh = lambda t: sorted(str(v(r.get("inheritance"))) for r in tn_rows(t))  # noqa: E731
    return {
        "42128528": [("TNFAIP3 rows with a printed variant", lambda t: sum(v(r.get("variant_original_string")) not in MISSING for r in tn_rows(t)),
                      lambda a, b: b > a, "more (filter v2 appends the per-patient table)")],
        "30526650": [("TNFAIP3 inheritance values", inh,
                      lambda a, b: "inherited maternal" not in b, "no 'inherited maternal' (the mother is untested; a hedged sentence is not a carrier statement)")],
        "33549127": [("TNFAIP3 inheritance values", inh,
                      lambda a, b: sum(x.startswith("inherited") for x in b) > sum(x.startswith("inherited") for x in a),
                      "more 'inherited' values (each patient's parent carries the same variant)")],
        "37848905": [("excluded rows inferred from a group statement",
                      lambda t: sum(v(r.get("status")) == "excluded" and v(r.get("evidence_basis")) == "inferred from group statement"
                                    for k in ("phenotypic_features", "phenotype_checklist") for r in t.get(k) or []),
                      lambda a, b: b < a, "fewer (zero counts exclude no one)")],
        "36064566": [("labels using 'Table <n> #<k>'", lambda t: sum(bool(re.match(r"Table \d+ #", str(v(r.get("individual_label_in_paper"))))) for r in t.get("individuals") or []),
                      lambda a, b: b > 0, "at least one"),
                     ("labels guessing mother/father for 'parents'", lambda t: sum(bool(re.match(r"(mother|father) of Patient two", str(v(r.get("individual_label_in_paper"))))) for r in t.get("individuals") or []),
                      lambda a, b: b == 0, "none")],
        "41929919": [("individuals", lambda t: len(t.get("individuals") or []), lambda a, b: True, "reported only (literature patients with one fact stay in scope)")],
        "33446651": [("rows for the common SNP c.305A>G", lambda t: sum("305" in str(v(r.get("variant_original_string"))) for r in tn_rows(t)),
                      lambda a, b: b == 0, "none (authors treat it as common, non-causal)"),
                     ("labels using 'Table <n> column <k>'", lambda t: sum(bool(re.match(r"Table \d+ column \d+", str(v(r.get("individual_label_in_paper"))))) for r in t.get("individuals") or []),
                      lambda a, b: b > 0, "at least one")],
        "42572791": [("other-gene variant rows", lambda t: sum(not is_gene(v(r.get("gene_symbol_as_stated")), "TNFAIP3") for r in t.get("variants") or []),
                      lambda a, b: b == 0, "none (named but not described)")],
        "40574834": [("individuals with source_reference_in_review", lambda t: sum(v(r.get("source_reference_in_review")) not in MISSING for r in t.get("individuals") or []),
                      lambda a, b: b > a, "more (per-patient reference column, D-23)"),
                     ("TNFAIP3 rows with zygosity 'mosaic'", lambda t: sum(v(r.get("zygosity")) == "mosaic" for r in tn_rows(t)),
                      lambda a, b: b > 0, "at least one (germline mosaic carriers)")],
        "35958611": [("labels with '(Family <n>)'", lambda t: sum("(Family" in str(v(r.get("individual_label_in_paper"))) for r in t.get("individuals") or []),
                      lambda a, b: b > 0, "at least one (repeated pedigree label)"),
                     ("TNFAIP3 inheritance values", inh, lambda a, b: sum(x.startswith("inherited") for x in b) >= sum(x.startswith("inherited") for x in a),
                      "no fewer 'inherited' values (carrier parents named)")],
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-a", required=True)
    ap.add_argument("--run-b", required=True)
    args = ap.parse_args(argv)
    base = Path("data/extracted") / args.disease
    ra, rb = base / args.run_a, base / args.run_b
    results = []
    for pmid, cs in checks().items():
        if not (rb / "per_paper" / f"{pmid}.json").exists():
            results.append({"pmid": pmid, "check": "(v4 output missing)", "run_a": None, "run_b": None, "as_intended": None})
            continue
        ta, tb = tables(ra, pmid), tables(rb, pmid)
        for name, fn, test, expect in cs:
            a, b = fn(ta), fn(tb)
            results.append({"pmid": pmid, "check": name, "expected": expect, "run_a": a, "run_b": b, "as_intended": bool(test(a, b))})
    tested = [r for r in results if r["as_intended"] is not None and not r["expected"].startswith("reported only")]
    out = {"run_a": args.run_a, "run_b": args.run_b, "checks": results,
           "as_intended": sum(r["as_intended"] for r in tested), "tested": len(tested)}
    dest = Path("analysis/poc") / f"v4_check_{args.run_b}.json"
    dest.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n")
    for r in results:
        print(f"{r['pmid']} | {r['check']} | {r.get('run_a')} -> {r.get('run_b')} | {r['as_intended']}")
    print(f"as intended: {out['as_intended']} of {out['tested']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
