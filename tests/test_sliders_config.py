"""The HA20 SLIDERS config and pinned schema load into SLIDERS without a model call."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

sliders = pytest.importorskip("sliders")

REPO = Path(__file__).resolve().parents[1]


def test_ha20_config_builds_agent_with_anthropic_clients(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("SLIDERS_LLM_PROVIDER", "anthropic")
    monkeypatch.setenv("SLIDERS_RESULTS", str(REPO / "runs" / "_test"))
    from sliders.run import _load_config
    from sliders.system import SlidersAgent

    config = _load_config(str(REPO / "configs" / "sliders_ha20.yaml"))
    models = config["system_config"]["models"]
    assert all(m["model"] == "claude-opus-5-5" for m in models.values())
    assert all("temperature" not in m for m in models.values())
    assert all(m.get("provider") == "anthropic" for m in models.values())
    assert {m["effort"] for m in models.values()} <= {"high", "medium"}
    config["system_config"]["output_folder"] = str(REPO / "runs" / "_test")
    agent = SlidersAgent(config["system_config"])  # constructs chains, no network
    assert agent is not None


def test_pinned_schema_is_complete_and_three_state():
    from sliders.modules.generate_schema import _build_tables_from_normalized, _normalize_user_schema, _user_schema_is_already_complete

    schema = json.loads((REPO / "pipeline/extract/sliders_adapter/schema_ha20.json").read_text())
    norm = _normalize_user_schema(schema)
    assert _user_schema_is_already_complete(norm), "incomplete schema would trigger an LLM completion call"
    tables = {t.name: t for t in _build_tables_from_normalized(norm).tables}
    assert set(tables) == {"publications", "individuals", "variants", "phenotypic_features", "phenotype_checklist"}
    status = {f.name: f for f in tables["phenotype_checklist"].fields}["status"]
    assert status.enum_values == ["observed", "excluded", "not reported"]
    feat_status = {f.name: f for f in tables["phenotypic_features"].fields}["status"]
    assert feat_status.enum_values == ["observed", "excluded"]
    orig = {f.name: f for f in tables["variants"].fields}["variant_original_string"]
    assert orig.required and "exactly as printed" in orig.description


def test_run_sliders_refuses_without_key(monkeypatch, tmp_path):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "docs").mkdir()
    from pipeline.extract.sliders_adapter.run_sliders import main

    with pytest.raises(SystemExit, match="ANTHROPIC_API_KEY"):
        main(["--docs", "docs", "--run-id", "x"])
