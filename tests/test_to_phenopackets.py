"""Stage 4: phenopacket building and validation on a tiny synthetic run with a tiny ontology."""

import csv
import json

from pipeline.extract import ontologies, to_phenopackets, validate

HP_OBO = """format-version: 1.2
data-version: hp/releases/test

[Term]
id: HP:0000001
name: All

[Term]
id: HP:0000118
name: Phenotypic abnormality
is_a: HP:0000001

[Term]
id: HP:0000951
name: Abnormality of the skin
is_a: HP:0000118

[Term]
id: HP:0000988
name: Skin rash
is_a: HP:0000951

[Term]
id: HP:0000155
name: Oral ulcer
is_a: HP:0000118

[Term]
id: HP:0003249
name: Genital ulcers
is_a: HP:0000118
"""
MONDO_OBO = """format-version: 1.2
data-version: releases/test

[Term]
id: MONDO:0800045
name: autoinflammatory syndrome, familial, Behcet-like 1

[Term]
id: MONDO:0100222
name: A20 haploinsufficiency
"""
ECO_OBO = """format-version: 1.2
data-version: releases/test

[Term]
id: ECO:0007539
name: author statement supported from referenced clinical study used in automatic assertion
"""
GENO_OBO = """format-version: 1.2
data-version: releases/test

[Term]
id: GENO:0000134
name: hemizygous

[Term]
id: GENO:0000135
name: heterozygous

[Term]
id: GENO:0000136
name: homozygous

[Term]
id: GENO:0000964
name: mosaic
"""


def cell(value, span="x"):
    return {"value": value, "span": span if value not in (None, "not reported") else None}


def make_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    snap = tmp_path / "data/ontologies/2026-01-01"
    snap.mkdir(parents=True)
    for name, text in (("hp", HP_OBO), ("mondo", MONDO_OBO), ("eco", ECO_OBO), ("geno", GENO_OBO)):
        (snap / f"{name}.obo").write_text(text)
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/ha20_checklist_hpo.json").write_text(json.dumps({"items": {
        "oral ulcers": {"observed": "HP:0000155", "excluded": ["HP:0000155"]},
        "genital ulcers": {"observed": "HP:0003249", "excluded": ["HP:0003249"]}}}))
    run = tmp_path / "data/extracted/ha20/r1"
    (run / "per_paper").mkdir(parents=True)
    paper = {"pmid": "111", "tables": {
        "publications": [{"pmid": cell("111")}],
        "individuals": [{"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "sex": cell("female"),
                         "age_at_last_evaluation_iso8601": cell("P12Y"), "disease_label_as_stated": cell("HA20")}],
        "variants": [{"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "gene_symbol_as_stated": cell("TNFAIP3"),
                      "variant_original_string": cell("c.811C>T"), "cdna_hgvs_as_stated": cell("c.811C>T"),
                      "transcript_as_stated": cell("not reported"), "protein_hgvs_as_stated": cell("p.R271*"),
                      "zygosity": cell("heterozygous"), "pathogenicity_as_stated_by_authors": cell("not reported")}],
        "phenotypic_features": [
            {"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "feature_text_as_stated": cell("rash", "a rash"), "status": cell("observed"),
             "onset_iso8601": cell(None)},
            {"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "feature_text_as_stated": cell("skin", "no skin disease"), "status": cell("excluded"),
             "onset_iso8601": cell(None)}],
        "phenotype_checklist": [
            {"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "checklist_feature": cell("oral ulcers", None), "status": cell("observed", "oral ulcers")},
            {"pmid": cell("111"), "individual_label_in_paper": cell("P1"), "checklist_feature": cell("genital ulcers", None), "status": cell("excluded", "no genital ulcers")}]}}
    (run / "per_paper/111.json").write_text(json.dumps(paper))
    rows = {"individuals_reconciled.csv": [{"pmid": "111", "individual_label_in_paper": "P1", "identity": "HA20-ID0001", "record_of_record": "True"}],
            "hpo_bindings.csv": [{"pmid": "111", "row": 0, "hpo_id": "HP:0000988"}, {"pmid": "111", "row": 1, "hpo_id": "HP:0000951"}],
            "disease_bindings.csv": [{"pmid": "111", "individual_label_in_paper": "P1", "mondo_id": "MONDO:0800045", "method": "ha20_label_rule"}]}
    for name, data in rows.items():
        with (run / name).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    monkeypatch.setattr(ontologies, "BASE", tmp_path / "data/ontologies")
    return run


def test_build_and_validate(tmp_path, monkeypatch):
    run = make_run(tmp_path, monkeypatch)
    assert to_phenopackets.main(["--disease", "ha20", "--run-id", "r1", "--created", "2026-01-01", "--gatekeeper", "none"]) == 0
    pp = json.loads((run / "phenopackets/HA20-ID0001.json").read_text())
    feats = {(f["type"]["id"], f.get("excluded", False)) for f in pp["phenotypicFeatures"]}
    # the excluded broad skin term is dropped because a skin rash is observed; checklist adds oral (observed) and genital (excluded)
    assert feats == {("HP:0000988", False), ("HP:0000155", False), ("HP:0003249", True)}
    assert pp["subject"]["sex"] == "FEMALE" and pp["subject"]["timeAtLastEncounter"]["age"]["iso8601duration"] == "P12Y"
    gi = pp["interpretations"][0]["diagnosis"]["genomicInterpretations"][0]
    assert gi["interpretationStatus"] == "CAUSATIVE"  # HA20 stated
    assert pp["interpretations"][0]["diagnosis"]["disease"]["id"] == "MONDO:0800045"
    assert gi["variantInterpretation"]["variationDescriptor"]["description"] == "c.811C>T"
    assert all(f["evidence"][0]["reference"]["id"] == "PMID:111" for f in pp["phenotypicFeatures"])
    build = json.loads((run / "phenopacket_build.json").read_text())
    assert build["conflicts"][0]["kind"] == "excluded_ancestor_of_observed"
    assert validate.main(["--disease", "ha20", "--run-id", "r1"]) == 0
    report = json.loads((run / "validation_report.json").read_text())
    assert report["share_schema_valid"] == 1.0 and report["errors_by_check"] == {}


def test_gatekeeper_verdicts_drop_claims(tmp_path, monkeypatch):
    run = make_run(tmp_path, monkeypatch)
    # without gatekeeper.csv the default mode refuses to build
    try:
        to_phenopackets.main(["--disease", "ha20", "--run-id", "r1"])
        raise AssertionError("expected SystemExit")
    except SystemExit:
        pass
    verdicts = [
        ("111", "phenotypic_features", 0, "status", "unsupported"),      # the rash row goes
        ("111", "individuals", 0, "sex", "partially_supported"),         # sex goes under not_supported only
        ("111", "phenotype_checklist", 1, "status", "supported"),
        ("111", "variants", 0, "zygosity", "span_not_found"),            # allelic state goes
    ]
    with (run / "gatekeeper.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["claim_id", "pmid", "table", "row", "field", "value", "class", "verdict", "source", "reason"])
        for n, (pm, t, r, f, verdict) in enumerate(verdicts, 1):
            w.writerow([f"C{n:06d}", pm, t, r, f, "", "model", verdict, "gatekeeper", ""])
    assert to_phenopackets.main(["--disease", "ha20", "--run-id", "r1", "--created", "2026-01-01"]) == 0
    pp = json.loads((run / "phenopackets/HA20-ID0001.json").read_text())
    feats = {(f["type"]["id"], f.get("excluded", False)) for f in pp["phenotypicFeatures"]}
    # with the rash row gone, the excluded skin term no longer conflicts and stays
    assert feats == {("HP:0000951", True), ("HP:0000155", False), ("HP:0003249", True)}
    assert pp["subject"].get("sex", "UNKNOWN_SEX") == "UNKNOWN_SEX"
    vd = pp["interpretations"][0]["diagnosis"]["genomicInterpretations"][0]["variantInterpretation"]["variationDescriptor"]
    assert "allelicState" not in vd
    build = json.loads((run / "phenopacket_build.json").read_text())
    assert build["gatekeeper"] == "not_supported"
    assert build["counts"]["gk_dropped_feature_rows"] == 1 and build["counts"]["gk_dropped_sex"] == 1
    # the sensitivity build keeps partially supported claims
    assert to_phenopackets.main(["--disease", "ha20", "--run-id", "r1", "--gatekeeper", "unsupported", "--out-name", "pp_lenient"]) == 0
    pp2 = json.loads((run / "pp_lenient/HA20-ID0001.json").read_text())
    assert pp2["subject"]["sex"] == "FEMALE"
    assert (run / "pp_lenient_build.json").exists()
