"""Automated checks on Claude Code per-paper extraction output (D-20 route).

For every per-paper JSON under data/extracted/<disease>/<run_id>/per_paper/:

1. Structure: the five schema tables exist; each row has every schema field;
   each cell is {"value": ..., "span": ...}; enum values are allowed ones.
2. Provenance: every non-missing value has a span. The exceptions are the HPO
   candidate fields, which are the extractor's suggestions.
3. Verbatim spans: each span is searched in the paper's Markdown
   (data/literature/<disease>/fulltext_md/<pmid>.md):
     exact   = found after collapsing whitespace only;
     lenient = found after also lower-casing, NFKC-normalizing and dropping
               Markdown markup characters (* _ ` | #).
   A span counts as found if it is found at either level; the level is
   recorded so exact and lenient rates can be reported separately.
4. Three-state: phenotypic_features carries only observed/excluded rows; the
   checklist covers every individual times every checklist feature.
5. Label consistency: variant, feature and checklist rows name individuals
   that exist in the individuals table.

Writes claims.csv (one row per value with a span) and span_check.json (all
counts and every problem) next to per_paper/, and prints a summary.

  uv run python -m pipeline.extract.claude_code.span_check --disease ha20 --run-id poc-ha20-smoke-1
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import unicodedata
from collections import Counter
from pathlib import Path

SCHEMA = Path("pipeline/extract/sliders_adapter/schema_ha20.json")
NO_SPAN_FIELDS = {"hpo_label_candidate", "hpo_id_candidate"}
MISSING = {None, "not reported", ""}
MARKUP = re.compile(r"[*_`|#]")
WS = re.compile(r"\s+")


def norm_exact(s: str) -> str:
    return WS.sub(" ", s).strip()


def norm_lenient(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    s = MARKUP.sub(" ", s)
    return WS.sub(" ", s).strip()


def load_schema(path: Path = SCHEMA) -> dict[str, dict]:
    raw = json.loads(path.read_text())
    tables: dict[str, dict] = {}
    for t in raw["tables"]:
        fields = {}
        for f in t["fields"]:
            if isinstance(f, str):
                fields[f] = {"name": f}
            else:
                fields[f["name"]] = f
        tables[t["name"]] = {"fields": fields, "description": t.get("description", "")}
    return tables


def checklist_features(schema: dict[str, dict]) -> list[str]:
    desc = schema["phenotype_checklist"]["description"]
    tail = desc.split("Checklist:", 1)[1]
    return [x.strip().rstrip(".") for x in tail.split(";") if x.strip()]


def spans_of(cell) -> list[str]:
    span = cell.get("span") if isinstance(cell, dict) else None
    if span is None:
        return []
    return [s for s in (span if isinstance(span, list) else [span]) if isinstance(s, str) and s.strip()]


def check_paper(path: Path, md_dir: Path, schema: dict[str, dict], features: list[str]) -> tuple[list[dict], list[str], Counter]:
    doc = json.loads(path.read_text())
    pmid = str(doc.get("pmid", path.stem))
    problems: list[str] = []
    counts: Counter = Counter()
    md_path = md_dir / f"{pmid}.md"
    if not md_path.exists():
        return [], [f"{pmid}: paper Markdown not found at {md_path}"], counts
    text = md_path.read_text()
    hay_exact, hay_lenient = norm_exact(text), norm_lenient(text)
    tables = doc.get("tables") or {}
    claims: list[dict] = []
    for tname, tdef in schema.items():
        rows = tables.get(tname)
        if rows is None:
            problems.append(f"{pmid}: table {tname} missing")
            continue
        counts[f"rows:{tname}"] += len(rows)
        for i, row in enumerate(rows):
            for fname, fdef in tdef["fields"].items():
                if fname not in row:
                    problems.append(f"{pmid}: {tname}[{i}] missing field {fname}")
                    continue
                cell = row[fname]
                if not isinstance(cell, dict) or "value" not in cell:
                    problems.append(f"{pmid}: {tname}[{i}].{fname} is not a {{value, span}} cell")
                    continue
                value = cell["value"]
                allowed = fdef.get("enum_values")
                if allowed and value not in MISSING and value not in allowed:
                    problems.append(f"{pmid}: {tname}[{i}].{fname} value {value!r} not in {allowed}")
                if value in MISSING or fname in NO_SPAN_FIELDS:
                    counts["values_missing_or_candidate"] += 1
                    continue
                spans = spans_of(cell)
                counts["values_asserted"] += 1
                if not spans:
                    problems.append(f"{pmid}: {tname}[{i}].{fname} = {value!r} has no span")
                    counts["values_without_span"] += 1
                    claims.append({"pmid": pmid, "table": tname, "row": i, "field": fname, "value": json.dumps(value),
                                   "span": "", "found": "no_span"})
                    continue
                levels = []
                for s in spans:
                    if norm_exact(s) in hay_exact:
                        levels.append("exact")
                    elif norm_lenient(s) in hay_lenient:
                        levels.append("lenient")
                    else:
                        levels.append("not_found")
                found = "not_found" if "not_found" in levels else ("lenient" if "lenient" in levels else "exact")
                counts[f"span_{found}"] += 1
                claims.append({"pmid": pmid, "table": tname, "row": i, "field": fname, "value": json.dumps(value),
                               "span": " || ".join(spans), "found": found})
    # three-state and checklist completeness
    for i, row in enumerate(tables.get("phenotypic_features") or []):
        st = (row.get("status") or {}).get("value")
        if st not in ("observed", "excluded"):
            problems.append(f"{pmid}: phenotypic_features[{i}] status {st!r} (only observed/excluded allowed)")
    labels = {(r.get("individual_label_in_paper") or {}).get("value") for r in tables.get("individuals") or []}
    for tname in ("variants", "phenotypic_features", "phenotype_checklist"):
        for i, row in enumerate(tables.get(tname) or []):
            lab = (row.get("individual_label_in_paper") or {}).get("value")
            if lab not in labels:
                problems.append(f"{pmid}: {tname}[{i}] names individual {lab!r} not in individuals table")
    seen = Counter()
    for row in tables.get("phenotype_checklist") or []:
        seen[((row.get("individual_label_in_paper") or {}).get("value"), (row.get("checklist_feature") or {}).get("value"))] += 1
    for lab in labels:
        for feat in features:
            if seen[(lab, feat)] != 1:
                problems.append(f"{pmid}: checklist has {seen[(lab, feat)]} rows for ({lab!r}, {feat!r}); expected 1")
    counts["individuals"] += len(labels)
    return claims, problems, counts


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    md_dir = Path("data/literature") / args.disease / "fulltext_md"
    schema = load_schema()
    features = checklist_features(schema)
    all_claims, all_problems, total = [], [], Counter()
    per_paper = {}
    for path in sorted((run_dir / "per_paper").glob("*.json")):
        claims, problems, counts = check_paper(path, md_dir, schema, features)
        all_claims += claims
        all_problems += problems
        total.update(counts)
        per_paper[path.stem] = {"problems": len(problems), **{k: v for k, v in counts.items()}}
    with (run_dir / "claims.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pmid", "table", "row", "field", "value", "span", "found"])
        w.writeheader()
        w.writerows(all_claims)
    with_span = total["span_exact"] + total["span_lenient"] + total["span_not_found"]
    summary = {
        "run_id": args.run_id,
        "n_papers": len(per_paper),
        "checklist_features": features,
        "counts": dict(total),
        "span_found_rate": round((total["span_exact"] + total["span_lenient"]) / with_span, 4) if with_span else None,
        "span_exact_rate": round(total["span_exact"] / with_span, 4) if with_span else None,
        "n_problems": len(all_problems),
        "problems": all_problems,
        "per_paper": per_paper,
    }
    (run_dir / "span_check.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("n_papers", "counts", "span_found_rate", "span_exact_rate", "n_problems")}, indent=2))
    for p in all_problems[:40]:
        print("  -", p)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
