import csv
import json

from pipeline.extract import reconcile as rc


def cell(value, span="x"):
    return {"value": value, "span": span if value not in (None, "not reported") else None}


def paper(pmid, year, people, study_type="case report", prior=None):
    pub = {"pmid": cell(pmid), "first_author": cell("A"), "year": cell(year), "study_type": cell(study_type),
           "n_patients_reported": cell(len(people)),
           "cites_prior_report_of_same_patients": cell(True if prior else None),
           "prior_report_citation": cell(prior or "not reported")}
    inds, vars_ = [], []
    for p in people:
        inds.append({"pmid": cell(pmid), "individual_label_in_paper": cell(p["label"]), "sex": cell(p.get("sex", "not reported")),
                     "age_at_onset_iso8601": cell(p.get("onset")), "family_label_in_paper": cell("not reported"),
                     "source_reference_in_review": cell(p.get("src", "not reported"))})
        if p.get("cdna") or p.get("protein"):
            vars_.append({"pmid": cell(pmid), "individual_label_in_paper": cell(p["label"]), "gene_symbol_as_stated": cell("TNFAIP3"),
                          "variant_original_string": cell(p.get("cdna") or p.get("protein")),
                          "cdna_hgvs_as_stated": cell(p.get("cdna", "not reported")),
                          "protein_hgvs_as_stated": cell(p.get("protein", "not reported"))})
    return {"pmid": pmid, "tables": {"publications": [pub], "individuals": inds, "variants": vars_,
                                     "phenotypic_features": [], "phenotype_checklist": []}}


def jats(pmid, refs):
    items = "".join(f'<ref id="r{i}"><label>{i}</label><mixed-citation>{text}<pub-id pub-id-type="pmid">{p}</pub-id></mixed-citation></ref>'
                    for i, (text, p) in enumerate(refs, 1))
    return f'<article><front><article-meta><article-id pub-id-type="pmid">{pmid}</article-id></article-meta></front><back><ref-list>{items}</ref-list></back></article>'


def test_variant_keys_fold_notation():
    assert rc.protein_key("p.(Arg271Ter)") == rc.protein_key("p.R271*") == rc.protein_key("p.R271X") == "p.R271*"
    assert rc.cdna_key("NM_006290.4: c.811 C>T") == rc.cdna_key("c.811C>T") == "c.811c>t"
    # entities from supplementary-file conversion, thin spaces from the papers
    assert rc.cdna_key("c.259C&gt;T") == rc.cdna_key("c.259C > T") == "c.259c>t"
    assert rc.orig_key("c.259C&gt;T") == "c.259c>t"
    # bare protein changes, as reviews often print them
    assert rc.protein_key("Leu227Ter") == rc.protein_key("p.Leu227*") == "p.L227*"
    assert rc.protein_key("Phe224Ser fs*4") == rc.protein_key("p.Phe224Serfs*4")
    assert rc.protein_key("c.680T>A") is None and rc.protein_key("exon 7-8 deletion") is None


def test_resolve_by_number_and_by_author_year():
    refs = [("1", "Zhou Q, Wang H. Loss-of-function mutations in TNFAIP3. 2016", "26642243"),
            ("2", "Aeschlimann FA, Laxer RM. A20 haploinsufficiency. 2018", "29317407")]
    assert rc.resolve("[2]", refs) == ["29317407"]
    assert rc.resolve("Zhou et al. (2016)", refs) == ["26642243"]
    assert rc.resolve("1-2", refs) == ["26642243", "29317407"]
    assert rc.resolve("not reported", refs) == []


def test_merge_policy(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    per = tmp_path / "data/extracted/ha20/r1/per_paper"
    per.mkdir(parents=True)
    xml = tmp_path / "data/literature/ha20/fulltext"
    xml.mkdir(parents=True)
    # 111 primary report; 222 review row citing 111 (explicit); 333 same variant, nothing else (weak);
    # 444 same variant but different sex (blocked); 111 has a second patient with another variant (never merged).
    docs = {
        "111": paper("111", 2016, [{"label": "P1", "sex": "female", "onset": "P2Y", "cdna": "c.811C>T"},
                                   {"label": "P2", "sex": "male", "cdna": "c.100del"}]),
        "222": paper("222", 2020, [{"label": "case 5", "sex": "female", "protein": "p.Arg271Ter", "src": "[1]"}],
                     study_type="review/meta-analysis"),
        "333": paper("333", 2021, [{"label": "II-1", "cdna": "c.811C>T"}]),
        "444": paper("444", 2022, [{"label": "Pt A", "sex": "male", "cdna": "c.811C>T"}]),
    }
    docs["111"]["tables"]["variants"][0]["protein_hgvs_as_stated"] = cell("p.R271*")
    for pmid, d in docs.items():
        (per / f"{pmid}.json").write_text(json.dumps(d))
    (xml / "222.nxml").write_text(jats("222", [("Zhou Q. TNFAIP3. 2016", "111")]))
    assert rc.main(["--disease", "ha20", "--run-id", "r1"]) == 0
    run = tmp_path / "data/extracted/ha20/r1"
    rows = {(r["pmid_a"], r["pmid_b"]): r for r in csv.DictReader((run / "merges.csv").open())}
    assert rows[("111", "222")]["confidence"] == "explicit_citation" and rows[("111", "222")]["merged"] == "True"
    assert rows[("111", "333")]["confidence"] == "weak_match" and rows[("111", "333")]["merged"] == "False"
    assert rows[("111", "444")]["confidence"] == "blocked_conflict"
    assert not any("P2" in (r["label_a"], r["label_b"]) for r in rows.values())
    summary = json.loads((run / "reconcile_summary.json").read_text())
    assert summary["individuals_before_merging"] == 5 and summary["identities_after_merging"] == 4
    inds = {(r["pmid"], r["individual_label_in_paper"]): r for r in csv.DictReader((run / "individuals_reconciled.csv").open())}
    assert inds[("111", "P1")]["identity"] == inds[("222", "case 5")]["identity"]
    assert inds[("111", "P1")]["record_of_record"] == "True" and inds[("222", "case 5")]["record_of_record"] == "False"
    assert inds[("222", "case 5")]["review_only"] == "False"


def test_review_row_citing_a_family_is_not_merged_into_relatives(tmp_path, monkeypatch):
    """Policy v2: a review row that matches several relatives with the same variant stays unmerged,
    and relatives from one paper never end up in one identity."""
    monkeypatch.chdir(tmp_path)
    per = tmp_path / "data/extracted/ha20/r2/per_paper"
    per.mkdir(parents=True)
    xml = tmp_path / "data/literature/ha20/fulltext"
    xml.mkdir(parents=True)
    docs = {
        "111": paper("111", 2016, [{"label": "mother", "sex": "female", "cdna": "c.680T>A"},
                                   {"label": "daughter", "sex": "female", "cdna": "c.680T>A"}]),
        "222": paper("222", 2020, [{"label": "case 3", "sex": "female", "cdna": "c.680T>A", "src": "(1)"}],
                     study_type="review/meta-analysis"),
    }
    for pmid, d in docs.items():
        (per / f"{pmid}.json").write_text(json.dumps(d))
    (xml / "222.nxml").write_text(jats("222", [("Zhou Q. TNFAIP3. 2016", "111")]))
    assert rc.main(["--disease", "ha20", "--run-id", "r2"]) == 0
    run = tmp_path / "data/extracted/ha20/r2"
    rows = list(csv.DictReader((run / "merges.csv").open()))
    assert rows and all(r["decision"] == "ambiguous_one_to_many" and r["merged"] == "False" for r in rows)
    summary = json.loads((run / "reconcile_summary.json").read_text())
    assert summary["identities_after_merging"] == 3


def test_review_listing_one_patient_twice_does_not_block_primary_merge(tmp_path, monkeypatch):
    """Two primary papers say they describe the same girl; a review lists her twice under both citations.
    The primary pair must merge; one review row is skipped instead."""
    monkeypatch.chdir(tmp_path)
    per = tmp_path / "data/extracted/ha20/r3/per_paper"
    per.mkdir(parents=True)
    xml = tmp_path / "data/literature/ha20/fulltext"
    xml.mkdir(parents=True)
    docs = {
        "111": paper("111", 2019, [{"label": "P1", "sex": "female", "cdna": "c.559C>T"}]),
        "222": paper("222", 2020, [{"label": "patient 7", "sex": "female", "cdna": "c.559C>T"}], prior="[1]"),
        "333": paper("333", 2024, [{"label": "Gln187Ter [1]", "sex": "female", "protein": "Gln187Ter", "src": "[1]"},
                                   {"label": "Gln187Ter [2]", "sex": "female", "protein": "Gln187Ter", "src": "[2]"}],
                     study_type="review/meta-analysis"),
    }
    docs["111"]["tables"]["variants"][0]["protein_hgvs_as_stated"] = cell("p.Q187X")
    docs["222"]["tables"]["variants"][0]["protein_hgvs_as_stated"] = cell("p.Q187X")
    for pmid, d in docs.items():
        (per / f"{pmid}.json").write_text(json.dumps(d))
    (xml / "222.nxml").write_text(jats("222", [("Li G. A20 haploinsufficiency. 2019", "111")]))
    (xml / "333.nxml").write_text(jats("333", [("Li G. A20 haploinsufficiency. 2019", "111"), ("Li G. Lupus. 2020", "222")]))
    assert rc.main(["--disease", "ha20", "--run-id", "r3"]) == 0
    run = tmp_path / "data/extracted/ha20/r3"
    rows = {(r["pmid_a"], r["label_a"], r["pmid_b"], r["label_b"]): r for r in csv.DictReader((run / "merges.csv").open())}
    assert rows[("111", "P1", "222", "patient 7")]["decision"] == "merged"
    assert sum(r["decision"] == "skipped_same_paper" for r in rows.values()) == 1
