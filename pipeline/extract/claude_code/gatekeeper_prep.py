"""Prepare the Stage 5 gatekeeper pass for one run (POC_DESIGN.md §3.9; D-25).

Reads the run's claims.csv (one row per value with a span, written by
span_check) and the per-paper JSON, and sorts every claim into one of:

  bookkeeping   the pmid field of every row, and individual_label_in_paper in
                the variants, phenotypic_features and phenotype_checklist
                tables (the label is judged once, in the individuals table).
                Not judged.
  verbatim      a free-text field (original text, statements, labels as
                printed) whose value, case and spacing folded, occurs inside its
                own span. Supported by construction: the span is verbatim in the
                paper (span_check) and the value is copied from it. Marked by
                script.
  model         everything else: enums (status, sex, zygosity, inheritance,
                evidence basis, study type, vital status), booleans, numbers,
                ISO conversions of ages, and text values not found in their
                span. These go to the gatekeeper helpers.

For model claims, each claim carries the row's individual label and, for
phenotype rows, the feature, so the gatekeeper can check that the span ties the
value to that person. Claims are written per paper, split into chunks of at
most --chunk claims, as CSV files under the scratch directory given; a summary
and the full classification go to data/extracted/<disease>/<run_id>/.

  uv run python -m pipeline.extract.claude_code.gatekeeper_prep --disease ha20 \
      --run-id poc-ha20-run-2 --out-dir <scratch>/gatekeeper
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

FREE_TEXT = {
    "feature_text_as_stated", "severity_or_detail", "onset_original_text", "age_at_onset_original_text",
    "age_at_last_evaluation_original_text", "age_at_diagnosis_original_text", "disease_label_as_stated",
    "clinical_diagnosis_basis", "treatment_summary", "source_reference_in_review", "family_label_in_paper",
    "ethnicity_or_country", "cause_of_death", "variant_original_string", "gene_symbol_as_stated",
    "transcript_as_stated", "cdna_hgvs_as_stated", "protein_hgvs_as_stated", "genomic_coordinates_as_stated",
    "parental_testing_statement", "functional_evidence_statement", "pathogenicity_as_stated_by_authors",
    "acmg_criteria_as_stated", "variant_type_as_stated", "first_author", "prior_report_citation",
    "individual_label_in_paper",
}
FOLD = re.compile(r"[\W_]+", re.UNICODE)


def fold(s) -> str:
    return FOLD.sub("", str(s or "").lower())


def classify(table: str, field: str, value: str, span: str) -> str:
    if field == "pmid" or (field == "individual_label_in_paper" and table != "individuals"):
        return "bookkeeping"
    try:
        val = json.loads(value)
    except (TypeError, ValueError):
        val = value
    if field in FREE_TEXT and isinstance(val, str) and fold(val) and fold(val) in fold(span):
        return "verbatim"
    return "model"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--chunk", type=int, default=350)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    papers = {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "per_paper").glob("*.json"))}
    claims = list(csv.DictReader((run_dir / "claims.csv").open()))
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    rows, per_paper, c = [], defaultdict(list), Counter()
    for n, cl in enumerate(claims, 1):
        cid = f"C{n:06d}"
        kind = classify(cl["table"], cl["field"], cl["value"], cl["span"])
        c[kind] += 1
        rows.append({"claim_id": cid, **{k: cl[k] for k in ("pmid", "table", "row", "field", "value")}, "class": kind})
        if kind != "model":
            continue
        t = (papers[cl["pmid"]].get("tables") or {}).get(cl["table"]) or []
        rec = t[int(cl["row"])] if int(cl["row"]) < len(t) else {}
        label = (rec.get("individual_label_in_paper") or {}).get("value", "")
        context = ""
        if cl["table"] == "phenotypic_features":
            context = str((rec.get("feature_text_as_stated") or {}).get("value", ""))
        elif cl["table"] == "phenotype_checklist":
            context = str((rec.get("checklist_feature") or {}).get("value", ""))
        elif cl["table"] == "variants":
            context = str((rec.get("variant_original_string") or {}).get("value", ""))
        per_paper[cl["pmid"]].append({"claim_id": cid, "table": cl["table"], "individual": label, "context": context,
                                      "field": cl["field"], "value": cl["value"], "span": cl["span"]})
    chunks = []
    for pmid, items in sorted(per_paper.items()):
        for k in range(0, len(items), args.chunk):
            part = items[k:k + args.chunk]
            name = f"{pmid}_{k // args.chunk + 1}"
            with (out_dir / f"{name}.csv").open("w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(part[0].keys()))
                w.writeheader()
                w.writerows(part)
            chunks.append({"chunk": name, "pmid": pmid, "claims": len(part)})
    with (run_dir / "gatekeeper_claims.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = {"run_id": args.run_id, "claims": len(claims), "by_class": dict(c), "chunks": len(chunks),
               "model_claims_by_field": dict(Counter(f"{x['table']}.{x['field']}" for items in per_paper.values() for x in items).most_common()),
               "chunk_list": chunks}
    (run_dir / "gatekeeper_prep.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in ("claims", "by_class", "chunks")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
