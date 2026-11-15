"""Fill missing label spans in child tables from the person's own individuals-table label span (D-47 extension).

Helpers sometimes leave `individual_label_in_paper` without a span in the child tables
(variants, phenotypic_features, phenotype_checklist) once the person has been introduced.
In the first six runs this was fixed by repair-only resumes of the same helper, which copied
the label quote from the individuals table (NOTES_FOR_AGENTS.md, Stage 3b and 4-5 lessons).
This script does the same copy deterministically:

  - only cells whose value is set and whose span is empty are touched;
  - the span copied is the one on the individuals row with the same label value, and only
    when exactly one individuals row has that value;
  - nothing else in the file changes; every change is logged.

Child-table labels are bookkeeping claims (gatekeeper_prep.py): they are not judged by the
gatekeeper, and no value is marked supported by this script (D-28).

  uv run python -m analysis.extension.fill_label_spans --disease papa --run-id pv1-papa
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

CHILD = ("variants", "phenotypic_features", "phenotype_checklist")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    run = Path("data/extracted") / a.disease / a.run_id
    log, unresolved = [], []
    for p in sorted((run / "per_paper").glob("*.json")):
        d = json.loads(p.read_text())
        t = d.get("tables") or {}
        labels = Counter()
        spans = {}
        for r in t.get("individuals") or []:
            c = r.get("individual_label_in_paper") or {}
            v = c.get("value") if isinstance(c, dict) else None
            if v:
                labels[v] += 1
                spans[v] = c.get("span")
        changed = 0
        for tab in CHILD:
            for i, r in enumerate(t.get(tab) or []):
                c = r.get("individual_label_in_paper")
                if not isinstance(c, dict) or not c.get("value") or c.get("span"):
                    continue
                v = c["value"]
                if labels[v] == 1 and spans.get(v):
                    c["span"] = spans[v]
                    changed += 1
                    log.append({"pmid": p.stem, "table": tab, "row": i, "label": v})
                else:
                    unresolved.append({"pmid": p.stem, "table": tab, "row": i, "label": v, "individuals_rows_with_label": labels[v]})
        if changed:
            p.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    out = {"run_id": a.run_id, "filled": len(log), "unresolved": len(unresolved),
           "by_paper": dict(Counter(x["pmid"] for x in log)), "unresolved_rows": unresolved}
    (run / "label_span_fill.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "unresolved_rows"}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
