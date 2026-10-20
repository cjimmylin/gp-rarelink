import csv
import json
from pathlib import Path

import pytest

from pipeline.extract.corpus import claude_code_fulltext_screen as fts

HEADER = ["pmid", "title", "in_extraction_corpus", "fulltext_format", "notes"]
LABEL_HEADER = ["pmid", "decision", "exclusion_reason", "study_type", "n_individuals", "has_genotype",
                "literature_table", "evidence_quote", "note"]


def setup(tmp_path: Path, labels: list[dict]) -> Path:
    base = tmp_path / "data/literature/xx"
    (base / "fulltext_md").mkdir(parents=True)
    (base / "screening_fulltext/labels").mkdir(parents=True)
    with (base / "manifest.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=HEADER)
        w.writeheader()
        w.writerow({"pmid": "1", "title": "a", "in_extraction_corpus": "true", "fulltext_format": "nxml", "notes": ""})
        w.writerow({"pmid": "2", "title": "b", "in_extraction_corpus": "true", "fulltext_format": "", "notes": ""})
        w.writerow({"pmid": "3", "title": "c", "in_extraction_corpus": "false", "fulltext_format": "", "notes": ""})
    (base / "fulltext_md/1.md").write_text("PMID: 1\n\nWe report a   girl with\nthe disease.\n")
    with (base / "screening_fulltext/labels/batch_01.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=LABEL_HEADER)
        w.writeheader()
        w.writerows(labels)
    return base


def good(**kw) -> dict:
    d = {"pmid": "1", "decision": "include", "exclusion_reason": "", "study_type": "case report", "n_individuals": "1",
         "has_genotype": "no", "literature_table": "no", "evidence_quote": "We report a girl with the disease.", "note": ""}
    d.update(kw)
    return d


def test_import_writes_columns_and_not_accessible(tmp_path, monkeypatch):
    base = setup(tmp_path, [good()])
    monkeypatch.chdir(tmp_path)
    prompt = tmp_path / "p.md"
    prompt.write_text("x")
    assert fts.import_labels("xx", prompt, False) == 0
    rows = {r["pmid"]: r for r in csv.DictReader((base / "manifest.csv").open())}
    assert rows["1"]["fulltext_screen"] == "include" and rows["1"]["fulltext_quote_found"] == "true"
    assert rows["2"]["fulltext_screen"] == "not_accessible"
    assert rows["3"]["fulltext_screen"] == ""
    log = json.loads((base / "screening_fulltext/screening_log.json").read_text())
    assert log["runs"][-1]["included_primary_reports"] == 1


@pytest.mark.parametrize("bad", [
    {"decision": "maybe"},
    {"decision": "exclude", "exclusion_reason": ""},
    {"decision": "include", "exclusion_reason": "not_disease"},
    {"n_individuals": "about 5"},
    {"evidence_quote": ""},
])
def test_import_rejects_invalid(tmp_path, monkeypatch, bad):
    setup(tmp_path, [good(**bad)])
    monkeypatch.chdir(tmp_path)
    prompt = tmp_path / "p.md"
    prompt.write_text("x")
    with pytest.raises(SystemExit):
        fts.import_labels("xx", prompt, False)


def test_import_stops_on_quote_not_found(tmp_path, monkeypatch):
    setup(tmp_path, [good(evidence_quote="A boy with the disease.")])
    monkeypatch.chdir(tmp_path)
    prompt = tmp_path / "p.md"
    prompt.write_text("x")
    with pytest.raises(SystemExit):
        fts.import_labels("xx", prompt, False)
    assert fts.import_labels("xx", prompt, True) == 0
