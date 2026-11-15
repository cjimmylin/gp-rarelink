"""Bias arm: comparator-overlap tags and their use in frequency_deviation.py.

The frequency test runs on a made-up disease tree in tmp_path, so no literature frequency is
computed on project data before a person has filled the comparator sheets (§7.4.2 step 1).
"""
import csv
import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OVERLAP = REPO / "analysis/bias/comparator_overlap"


def _load(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_evidence_tables_are_consistent():
    tagger = _load(OVERLAP / "tag_individuals.py")
    papers = list(csv.DictReader((OVERLAP / "paper_evidence.csv").open()))
    overrides = list(csv.DictReader((OVERLAP / "person_overrides.csv").open()))
    assert len({(r["disease"], r["pmid"]) for r in papers}) == len(papers)
    for r in papers + overrides:
        assert tagger.RULES[r["rule"]] == r["tag"]
        assert "@" not in r["evidence_quote"] + r["note"]
        if r["tag"] != "no_link_found":
            assert r["evidence_quote"], f"{r['pmid']}: a tag other than no_link_found needs evidence"
    # every paper of the three runs has a row, and nothing else does
    for disease in tagger.COMPARATOR:
        in_runs = {f.stem for run in tagger.RUNS for f in (REPO / f"data/extracted/{disease}/{run}-{disease}/per_paper").glob("*.json")}
        assert in_runs == {r["pmid"] for r in papers if r["disease"] == disease}


def test_tags_cover_every_phenopacket():
    files = sorted(OVERLAP.glob("tags_2*.csv"))
    assert files, "run analysis/bias/comparator_overlap/tag_individuals.py"
    tagger = _load(OVERLAP / "tag_individuals.py")
    rows = list(csv.DictReader(files[-1].open()))
    seen = {(r["disease"], r["run"], r["identity"]) for r in rows}
    assert len(seen) == len(rows)
    for disease in tagger.COMPARATOR:
        for run in tagger.RUNS:
            for f in (REPO / f"data/extracted/{disease}/{run}-{disease}/phenopackets").glob("*.json"):
                assert (disease, run, json.loads(f.read_text())["subject"]["id"]) in seen
    for r in rows:
        assert (r["tag"] == "no_disease_term") == (r["has_disease_term"] == "no")


def _packet(pid, obs=(), exc=(), disease=True, pmid="PMID:1"):
    feats = [{"type": {"id": t}} for t in obs] + [{"type": {"id": t}, "excluded": True} for t in exc]
    return {"id": f"x-{pid}", "subject": {"id": pid}, "phenotypicFeatures": feats,
            "diseases": [{"term": {"id": "MONDO:1"}}] if disease else [],
            "metaData": {"externalReferences": [{"id": pmid}]}}


def test_frequency_deviation_excludes_tagged_people(tmp_path):
    fd = _load(REPO / "analysis/bias/frequency_deviation.py")
    (tmp_path / fd.HPO).parent.mkdir(parents=True)
    (tmp_path / fd.HPO).write_text("[Term]\nid: HP:1\n\n[Term]\nid: HP:2\nis_a: HP:1 ! parent\n")
    people = {  # identity: (run, tag, packet)
        "A": ("pv1", "no_link_found", _packet("A", obs=["HP:2"], pmid="PMID:1")),
        "B": ("pv1", "no_link_found", _packet("B", exc=["HP:1"], pmid="PMID:2")),
        "C": ("pv1", "in_cohort_probable", _packet("C", obs=["HP:1"], pmid="PMID:3")),
        "D": ("pv1", "in_cohort_possible", _packet("D", obs=["HP:1"], pmid="PMID:4")),
        "E": ("pv1", "no_disease_term", _packet("E", exc=["HP:1"], disease=False, pmid="PMID:5")),
        "F": ("pv1a2", "in_cohort_stated", _packet("F", obs=["HP:1"], pmid="PMID:6")),
        "G": ("pv1a2", "no_link_found", _packet("G", exc=["HP:1"], pmid="PMID:7")),
    }
    for ident, (run, _, pk) in people.items():
        d = tmp_path / f"data/extracted/toy/{run}-toy/phenopackets"
        d.mkdir(parents=True, exist_ok=True)
        (d / f"{ident}.json").write_text(json.dumps(pk))
    (tmp_path / fd.OVERLAP).mkdir(parents=True)
    with (tmp_path / fd.OVERLAP / "tags_2026-01-01.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["disease", "run", "identity", "tag"])
        w.writerows(["toy", run, ident, tag] for ident, (run, tag, _) in people.items())
    (tmp_path / fd.SHEETS).mkdir(parents=True)
    (tmp_path / fd.SHEETS / "toy__cohort.csv").write_text(
        "comparator_key,pmid_or_doi,cohort_n,cohort_type,feature_as_stated,hpo_id,hpo_label,n_with_feature,n_assessed,frequency_as_printed,location_in_paper,notes\n"
        "cohort,1,10,clinical,f,HP:1,parent,5,10,5/10,T1,\n")
    assert fd.main(tmp_path) == 0
    out = json.loads(next((tmp_path / "analysis/bias").glob("frequency_deviation_*.json")).read_text())
    comp = out["comparators"][0]
    assert comp["status"] == "computed" and comp["overlap_tags"] == "tagged"
    assert comp["people"]["registered"] == {"all_records": 5, "with_disease_term": 4,
                                            "by_tag": {"in_cohort_possible": 1, "in_cohort_probable": 1, "no_disease_term": 1, "no_link_found": 2}}
    cell = {(a["run_set"], a["exclusion"], a["records"]): a for a in comp["analyses"]}
    assert len(cell) == 16

    def prim(key):
        f = cell[key]["features"][0]
        return f["lit_observed"], f["lit_excluded"], cell[key]["individuals"], cell[key]["removed_as_comparator_cohort"]

    # registered run, nobody removed: A, C, D observed; B and E (no disease term) excluded
    assert prim(("registered", "none", "all_records")) == (3, 2, 5, 0)
    assert prim(("registered", "none", "with_disease_term")) == (3, 1, 4, 0)
    assert prim(("registered", "stated_probable", "with_disease_term")) == (2, 1, 3, 1)
    assert prim(("registered", "stated_probable_possible", "with_disease_term")) == (1, 1, 2, 2)
    # the addendum adds F (stated, removed from "stated" on) and G
    assert prim(("with_addendum", "none", "with_disease_term")) == (4, 2, 6, 0)
    assert prim(("with_addendum", "stated", "with_disease_term")) == (3, 2, 5, 1)
    a = cell[("registered", "stated_probable", "with_disease_term")]
    assert abs(a["mad_primary"] - abs(2 / 3 - 0.5)) < 1e-9
    assert a["clusters"] == 3 and a["mad_ci95_cluster_bootstrap"] is not None
