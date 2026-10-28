"""Convert direct-extraction records to the five-table shape (SLIDERS ablation, D-42).

The baseline helpers write one nested JSON document per paper
(data/extracted/<disease>/<run_id>/records/<pmid>.json; format in prompts/direct_v1.md). The
scoring scripts (span_check structure checks, reconcile, normalize_variants, the comparison
and the O2 harness) read the frozen five-table shape, so this script rewrites each document
as data/extracted/<disease>/<run_id>/per_paper/<pmid>.json with every field of the disease's
v5 schema present as a {"value": ..., "span": null} cell. Field names are the schema's, so the
mapping is one to one; the structure is the only thing that changes.

What the conversion does, and counts in conversion_summary.json:
  - a field the record omits is filled with the schema's missing value ("not reported" for
    text and enum fields, null otherwise) and counted as `filled_missing`;
  - a checklist item the record omits is "not reported" and counted as `checklist_items_filled`;
    a key that is not a checklist item is dropped and counted as `checklist_items_unknown`;
  - a key the schema does not know is dropped and counted as `unknown_keys`;
  - a value outside an enum is kept as written (span_check reports it) and counted as
    `enum_values_outside_schema`;
  - a document that does not parse, or has no `individuals` list, is reported and skipped.
  - `evidence_basis` (schema v2+) does not exist in the baseline: it is set to
    "not reported" on checklist rows whose status is "not reported" and to null otherwise,
    so the structure check accepts the row without crediting an evidence basis.
Nothing is inferred and no value is changed.

  uv run python -m pipeline.extract.claude_code.direct_to_tables --disease ha20 --run-id direct-ha20
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
MISSING_TEXT = "not reported"

# Record keys -> (schema table, field). Everything else in the schema is a nested list or
# bookkeeping (pmid, individual_label_in_paper) added here.
PUBLICATION_FIELDS = ("first_author", "year", "study_type", "n_patients_reported", "cohort_size_as_stated",
                      "cites_prior_report_of_same_patients", "prior_report_citation")


def load_schema(disease: str) -> dict[str, dict]:
    raw = json.loads((BASE / f"schema_{disease}_v5.json").read_text())
    tables = {}
    for t in raw["tables"]:
        tables[t["name"]] = {"fields": {f["name"]: f for f in t["fields"]}, "description": t.get("description", "")}
    return tables


def checklist_features(schema: dict[str, dict]) -> list[str]:
    tail = schema["phenotype_checklist"]["description"].split("Checklist:", 1)[1].split(". (v3", 1)[0]
    return [x.strip().rstrip(".") for x in tail.split(";") if x.strip()]


def missing_value(fdef: dict):
    desc = (fdef.get("description") or "").lower()
    if fdef.get("data_type") in ("int", "float", "bool"):
        return None
    if fdef.get("name", "").endswith("_iso8601"):
        return None
    if "otherwise null" in desc or "or null" in desc or "if stated; otherwise null" in desc:
        return None
    if fdef.get("name") in ("hpo_label_candidate", "hpo_id_candidate", "cdna_hgvs_as_stated", "protein_hgvs_as_stated",
                            "genomic_coordinates_as_stated", "onset_original_text", "severity_or_detail"):
        return None
    return MISSING_TEXT


def cell(v):
    return {"value": v, "span": None}


def make_row(table: str, src: dict, schema: dict[str, dict], counts: Counter, fixed: dict) -> dict:
    row = {}
    for fname, fdef in schema[table]["fields"].items():
        if fname in fixed:
            row[fname] = cell(fixed[fname])
            continue
        if fname in src:
            v = src[fname]
            allowed = fdef.get("enum_values")
            if allowed and v not in (None, MISSING_TEXT) and v not in allowed:
                counts["enum_values_outside_schema"] += 1
                counts[f"enum_outside:{table}.{fname}"] += 1
            row[fname] = cell(v)
        else:
            counts["filled_missing"] += 1
            counts[f"filled:{table}.{fname}"] += 1
            row[fname] = cell(missing_value(fdef))
    for k in src:
        if k not in schema[table]["fields"] and k not in fixed and k not in ("variants", "phenotypic_features", "phenotype_checklist"):
            counts["unknown_keys"] += 1
            counts[f"unknown:{table}.{k}"] += 1
    return row


def convert(doc: dict, pmid: str, schema: dict[str, dict], features: list[str], counts: Counter) -> dict:
    pub_src = doc.get("publication") if isinstance(doc.get("publication"), dict) else {}
    if not isinstance(doc.get("publication"), dict):
        counts["publication_block_missing"] += 1
    tables = {"publications": [make_row("publications", pub_src, schema, counts, {"pmid": pmid})],
              "individuals": [], "variants": [], "phenotypic_features": [], "phenotype_checklist": []}
    inds = doc.get("individuals")
    if not isinstance(inds, list):
        counts["individuals_not_a_list"] += 1
        inds = []
    for ind in inds:
        if not isinstance(ind, dict):
            counts["individual_not_an_object"] += 1
            continue
        label = ind.get("individual_label_in_paper")
        if not isinstance(label, str) or not label.strip():
            counts["individual_without_label"] += 1
            label = f"unnamed person {sum(1 for _ in tables['individuals']) + 1}"
        fixed = {"pmid": pmid, "individual_label_in_paper": label}
        tables["individuals"].append(make_row("individuals", ind, schema, counts, fixed))
        for v in ind.get("variants") or []:
            if isinstance(v, dict):
                tables["variants"].append(make_row("variants", v, schema, counts, fixed))
            else:
                counts["variant_not_an_object"] += 1
        for f in ind.get("phenotypic_features") or []:
            if isinstance(f, dict):
                fx = dict(fixed)
                fx["evidence_basis"] = None  # the baseline records no evidence basis
                tables["phenotypic_features"].append(make_row("phenotypic_features", f, schema, counts, fx))
            else:
                counts["feature_not_an_object"] += 1
        cl = ind.get("phenotype_checklist")
        if not isinstance(cl, dict):
            counts["checklist_missing"] += 1
            cl = {}
        for k in cl:
            if k not in features:
                counts["checklist_items_unknown"] += 1
        for feat in features:
            status = cl.get(feat)
            if status is None:
                counts["checklist_items_filled"] += 1
                status = MISSING_TEXT
            elif status not in ("observed", "excluded", MISSING_TEXT):
                counts["enum_values_outside_schema"] += 1
                counts["enum_outside:phenotype_checklist.status"] += 1
            basis = MISSING_TEXT if status == MISSING_TEXT else None
            tables["phenotype_checklist"].append(make_row("phenotype_checklist", {"checklist_feature": feat, "status": status, "evidence_basis": basis},
                                                          schema, counts, fixed))
    flag = doc.get("reports_individuals")
    return {"pmid": pmid, "instructions_version": doc.get("instructions_version", "direct_v1"),
            "reports_individuals_with_tnfaip3_variant": flag if isinstance(flag, bool) else None,
            "relevance_note": None, "method_note": None, "tables": tables}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    a = ap.parse_args(argv)
    schema = load_schema(a.disease)
    features = checklist_features(schema)
    run_dir = ROOT / "data/extracted" / a.disease / a.run_id
    out_dir = run_dir / "per_paper"
    out_dir.mkdir(parents=True, exist_ok=True)
    counts: Counter = Counter()
    per_paper = {}
    for p in sorted((run_dir / "records").glob("*.json")):
        c = Counter()
        try:
            doc = json.loads(p.read_text())
        except json.JSONDecodeError as e:
            counts["records_unparseable"] += 1
            per_paper[p.stem] = {"error": f"does not parse: {e}"}
            continue
        if not isinstance(doc, dict):
            counts["records_not_an_object"] += 1
            per_paper[p.stem] = {"error": "not a JSON object"}
            continue
        pmid = str(doc.get("pmid")) if str(doc.get("pmid") or "").isdigit() else p.stem
        if pmid != p.stem:
            c["pmid_differs_from_file_name"] += 1
            pmid = p.stem
        out = convert(doc, pmid, schema, features, c)
        (out_dir / f"{pmid}.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
        per_paper[pmid] = {"individuals": len(out["tables"]["individuals"]), "variants": len(out["tables"]["variants"]),
                           "features": len(out["tables"]["phenotypic_features"]), "counts": dict(c)}
        counts.update(c)
        counts["records_converted"] += 1
    summary = {"run_id": a.run_id, "disease": a.disease, "schema": f"pipeline/extract/claude_code/schema_{a.disease}_v5.json",
               "checklist_features": features, "counts": dict(sorted(counts.items())), "per_paper": per_paper}
    (run_dir / "conversion_summary.json").write_text(json.dumps(summary, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in summary["counts"].items() if not k.startswith(("filled:", "unknown:", "enum_outside:"))}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
