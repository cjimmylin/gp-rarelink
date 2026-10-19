"""Stage 5: scoring the human audit against the gatekeeper."""

import csv
import importlib.util
import json
from pathlib import Path

import pytest

SPEC = importlib.util.spec_from_file_location("audit_metrics", Path(__file__).resolve().parents[1] / "analysis/poc/audit_metrics.py")
audit_metrics = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit_metrics)

COL = audit_metrics.RATING_COL


def write(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def test_audit_metrics(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run = tmp_path / "data/extracted/ha20/r1"
    run.mkdir(parents=True)
    (run / "span_check.json").write_text(json.dumps({"span_found_rate": 1.0}))
    write(run / "gatekeeper.csv", [
        {"claim_id": "C1", "verdict": "supported", "source": "gatekeeper", "reason": ""},
        {"claim_id": "C2", "verdict": "unsupported", "source": "gatekeeper", "reason": "silence"},
        {"claim_id": "C3", "verdict": "supported", "source": "script", "reason": ""},
        {"claim_id": "C4", "verdict": "partially_supported", "source": "gatekeeper", "reason": "range"}])
    base = {"stratum": "variant", "pmid": "1", "table": "variants", "field": "zygosity", "value": '"heterozygous"', "note": ""}
    sheet = [dict(base, claim_id="C1", **{COL: "supported"}), dict(base, claim_id="C2", **{COL: "Unsupported"}),
             dict(base, claim_id="C3", **{COL: "partially supported"}), dict(base, claim_id="C4", **{COL: ""})]
    write(tmp_path / "adjudication/poc_audit/sample.csv", sheet)
    (tmp_path / "analysis/poc").mkdir(parents=True)
    assert audit_metrics.main(["--disease", "ha20", "--run-id", "r1", "--hpo-sheet", "none.csv"]) == 0
    out = json.loads((tmp_path / "analysis/poc/audit_metrics.json").read_text())
    assert out["rated"] == 3 and out["unrated"] == ["C4"]
    assert out["unsupported_strict"]["k"] == 1 and out["not_supported_lenient"]["k"] == 2
    assert out["q4_gate"]["human_unsupported_rate_ok"] is False and out["q4_gate"]["complete"] is False
    cal = out["gatekeeper_calibration"]["not_supported_vs_human_not_supported"]
    assert (cal["tp"], cal["fp"], cal["fn"]) == (1, 0, 1)
    assert [d["claim_id"] for d in out["disagreements"]] == ["C3"]


def test_no_ratings_yet(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    run = tmp_path / "data/extracted/ha20/r1"
    run.mkdir(parents=True)
    (run / "span_check.json").write_text(json.dumps({"span_found_rate": 1.0}))
    write(run / "gatekeeper.csv", [{"claim_id": "C1", "verdict": "supported", "source": "gatekeeper", "reason": ""}])
    write(tmp_path / "adjudication/poc_audit/sample.csv", [{"claim_id": "C1", "stratum": "variant", "pmid": "1", "table": "t",
                                                            "field": "f", "value": "v", COL: "", "note": ""}])
    with pytest.raises(SystemExit):
        audit_metrics.main(["--disease", "ha20", "--run-id", "r1"])
