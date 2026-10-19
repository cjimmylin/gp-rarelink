"""D-29 check: how the variant-field rule in instructions v5 changed what is filled.

For the 20 papers of poc-ha20-v5-subset, compares run-2 (instructions v3) with
the v5 re-run on the TNFAIP3 variant rows: per field, how many rows carry a
value and how many say "not reported" (or null). The rule should make
zygosity, inheritance, variant type and pathogenicity abstain more often where
the paper gives them only for a group. Row counts differ between runs (scope
and labels are re-read), so the shares are compared, not row by row.

  uv run python analysis/poc/v5_variant_fields.py
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

FIELDS = ("zygosity", "inheritance", "variant_type_as_stated", "pathogenicity_as_stated_by_authors", "acmg_criteria_as_stated",
          "functional_evidence_statement")
MISSING = {None, "", "not reported"}


def tally(run: str, papers: list[str]) -> dict:
    rows, filled = 0, Counter()
    for p in papers:
        f = Path("data/extracted/ha20") / run / "per_paper" / f"{p}.json"
        for r in (json.loads(f.read_text()).get("tables") or {}).get("variants") or []:
            if "TNFAIP3" not in str((r.get("gene_symbol_as_stated") or {}).get("value") or "").upper():
                continue
            rows += 1
            for k in FIELDS:
                if (r.get(k) or {}).get("value") not in MISSING:
                    filled[k] += 1
    return {"tnfaip3_variant_rows": rows, "filled": {k: filled[k] for k in FIELDS},
            "filled_share": {k: round(filled[k] / rows, 3) if rows else None for k in FIELDS}}


def main() -> int:
    papers = sorted(json.loads(Path("runs/poc-ha20-v5-subset/selection.json").read_text())["papers"])
    out = {"papers": len(papers), "run2_v3": tally("poc-ha20-run-2", papers), "v5": tally("poc-ha20-v5-subset", papers)}
    Path("analysis/poc/v5_variant_fields.json").write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
