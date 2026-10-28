"""The direct-extraction baseline of the SLIDERS ablation (D-42): prompt rendering and conversion."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline.extract.claude_code import direct_prompt, direct_to_tables
from pipeline.extract.claude_code.span_check import check_paper, checklist_features, load_schema

REPO = Path(__file__).resolve().parents[1]


def test_render_names_disease_gene_and_full_checklist():
    text = direct_prompt.render("ssadh")
    assert "succinic semialdehyde dehydrogenase (SSADH) deficiency" in text
    assert "*ALDH5A1*" in text
    items = direct_prompt.checklist("ssadh")
    assert len(items) == 20
    for item in items:
        assert f"- {item}\n" in text or text.endswith(f"- {item}")
    assert "{" + "DISEASE" + "}" not in text and "{CHECKLIST}" not in text
    # nothing from the frozen rules file leaks into the baseline
    for frozen_only in ("evidence_basis", "span", "verbatim quote", "stacked", "Table <n> row"):
        assert frozen_only not in text, frozen_only


def test_render_ha20_checklist_matches_frozen_schema():
    items = direct_prompt.checklist("ha20")
    schema = load_schema(REPO / "pipeline/extract/claude_code/schema_ha20_v5.json")
    assert items == checklist_features(schema)
    assert len(items) == 20


def _record(label: str, checklist: dict) -> dict:
    return {"individual_label_in_paper": label, "sex": "male", "is_proband": True,
            "age_at_onset_original_text": "3 months", "age_at_onset_iso8601": "P3M",
            "variants": [{"gene_symbol_as_stated": "ALDH5A1", "variant_original_string": "c.1226G>A",
                          "cdna_hgvs_as_stated": "c.1226G>A", "protein_hgvs_as_stated": "p.Gly409Asp", "zygosity": "homozygous",
                          "inheritance": "not reported", "pathogenicity_as_stated_by_authors": "pathogenic"}],
            "phenotypic_features": [{"feature_text_as_stated": "hypotonia", "status": "observed", "hpo_label_candidate": "Hypotonia"},
                                    {"feature_text_as_stated": "seizures", "status": "excluded"}],
            "phenotype_checklist": checklist}


def test_convert_fills_every_schema_field_and_counts_fills(tmp_path, monkeypatch):
    disease, run = "ssadh", "direct-test"
    schema_sc = load_schema(REPO / f"pipeline/extract/claude_code/schema_{disease}_v5.json")
    features = checklist_features(schema_sc)
    doc = {"pmid": "12345678", "instructions_version": "direct_v1", "reports_individuals": True,
           "publication": {"first_author": "Doe", "year": 2020, "study_type": "case report", "n_patients_reported": 1,
                           "cohort_size_as_stated": None, "cites_prior_report_of_same_patients": False, "prior_report_citation": "not reported",
                           "journal_impact": "high"},
           "individuals": [_record("patient", {features[0]: "observed", features[1]: "excluded", "not a feature": "observed"}),
                           _record("mother of patient", {f: "not reported" for f in features})]}
    root = tmp_path
    run_dir = root / "data/extracted" / disease / run
    (run_dir / "records").mkdir(parents=True)
    (run_dir / "records" / "12345678.json").write_text(json.dumps(doc))
    (run_dir / "records" / "bad.json").write_text("{not json")
    monkeypatch.setattr(direct_to_tables, "ROOT", root)
    direct_to_tables.main(["--disease", disease, "--run-id", run])
    out = json.loads((run_dir / "per_paper" / "12345678.json").read_text())
    summary = json.loads((run_dir / "conversion_summary.json").read_text())
    c = summary["counts"]
    assert c["records_converted"] == 1 and c["records_unparseable"] == 1
    assert c["unknown_keys"] == 1 and c["checklist_items_unknown"] == 1
    assert c["checklist_items_filled"] == 18  # the first record gave 2 of 20 items
    assert len(out["tables"]["individuals"]) == 2 and len(out["tables"]["variants"]) == 2  # both fixture records carry one variant
    assert len(out["tables"]["phenotype_checklist"]) == 40 and len(out["tables"]["phenotypic_features"]) == 4
    # every schema field present as a {value, span: null} cell; the frozen structure check accepts it
    for tname, tdef in schema_sc.items():
        for row in out["tables"][tname]:
            for fname in tdef["fields"]:
                assert fname in row and set(row[fname]) == {"value", "span"} and row[fname]["span"] is None
    md_dir = root / "md"
    md_dir.mkdir()
    (md_dir / "12345678.md").write_text("PMID: 12345678\n")
    claims, problems, counts = check_paper(run_dir / "per_paper" / "12345678.json", md_dir, schema_sc, features)
    structural = [p for p in problems if "has no span" not in p]
    assert structural == [], structural
    assert counts["values_asserted"] == counts["values_without_span"] > 0
