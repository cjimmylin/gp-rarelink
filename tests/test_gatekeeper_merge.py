"""Stage 5: merging gatekeeper verdicts and the exact interval."""

import csv
import json

import pytest

from pipeline.extract.claude_code import gatekeeper_merge


def test_clopper_pearson_matches_reference_values():
    # reference values from scipy.stats.beta.ppf
    assert gatekeeper_merge.clopper_pearson(0, 50) == (0.0, 0.071122)
    assert gatekeeper_merge.clopper_pearson(1, 250) == (0.000101, 0.022084)
    assert gatekeeper_merge.clopper_pearson(5, 100) == (0.016432, 0.112835)
    assert gatekeeper_merge.clopper_pearson(0, 0) is None


def write(path, rows):
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def test_merge(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run = tmp_path / "data/extracted/ha20/r1"
    (run / "gatekeeper").mkdir(parents=True)
    claims = [
        {"claim_id": "C000001", "pmid": "111", "table": "publications", "row": 0, "field": "pmid", "value": '"111"', "class": "bookkeeping"},
        {"claim_id": "C000002", "pmid": "111", "table": "individuals", "row": 0, "field": "individual_label_in_paper", "value": '"P1"', "class": "verbatim"},
        {"claim_id": "C000003", "pmid": "111", "table": "individuals", "row": 0, "field": "sex", "value": '"female"', "class": "model"},
        {"claim_id": "C000004", "pmid": "111", "table": "phenotypic_features", "row": 0, "field": "status", "value": '"excluded"', "class": "model"},
    ]
    write(run / "gatekeeper_claims.csv", claims)
    (run / "gatekeeper_prep.json").write_text(json.dumps({"chunk_list": [{"chunk": "111_1", "pmid": "111", "claims": 2}]}))
    with pytest.raises(SystemExit):  # chunk file missing
        gatekeeper_merge.main(["--disease", "ha20", "--run-id", "r1"])
    write(run / "gatekeeper/111_1.csv", [{"claim_id": "C000003", "verdict": "supported", "reason": ""},
                                         {"claim_id": "C000004", "verdict": "unsupported", "reason": "absence inferred from silence"}])
    assert gatekeeper_merge.main(["--disease", "ha20", "--run-id", "r1"]) == 0
    out = {r["claim_id"]: r for r in csv.DictReader((run / "gatekeeper.csv").open())}
    assert out["C000001"]["verdict"] == "not_judged" and out["C000002"]["source"] == "script"
    assert out["C000004"]["verdict"] == "unsupported"
    s = json.loads((run / "gatekeeper_summary.json").read_text())
    assert s["rates_all_values"]["judged"] == 3 and s["rates_all_values"]["unsupported_or_not_found"]["k"] == 1
    assert s["rates_model_claims"]["judged"] == 2
    assert [f["claim_id"] for f in s["flagged"]] == ["C000004"]
    # a verdict for a claim that is not in the chunk's paper fails the merge
    write(run / "gatekeeper/111_1.csv", [{"claim_id": "C000003", "verdict": "supported", "reason": ""},
                                         {"claim_id": "C000002", "verdict": "supported", "reason": ""}])
    with pytest.raises(SystemExit):
        gatekeeper_merge.main(["--disease", "ha20", "--run-id", "r1"])
