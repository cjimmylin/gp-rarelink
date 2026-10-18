import json

from pipeline.common.run_manifest import RunManifest, sha256_text


def test_manifest_round_trip(tmp_path):
    m = RunManifest(run_id="test-run", stage=0, model="claude-opus-5-5", effort="high")
    m.schema_sha256 = sha256_text("{}")
    m.add_usage({"input_tokens": 500_000, "output_tokens": 10_000, "cache_read_input_tokens": 500_000})
    m.record_fallback("PMID:1", "claude-opus-5-5", "claude-opus-4-8", reason="refusal")
    m.record_error(None, "example")
    m.finish()
    path = m.write(tmp_path / "manifest.json")
    data = json.loads(path.read_text())
    assert data["git_commit"] and len(data["git_commit"]) == 40
    assert data["n_requests"] == 1
    assert data["cache_hit_rate"] == 0.5
    assert data["cost_usd"] == (500_000 * 4 + 10_000 * 20 + 500_000 * 0.2) / 1e6
    assert data["price_table"].startswith("configs/prices.yaml@")
    assert data["fallbacks"][0]["served_model"] == "claude-opus-4-8"
    back = RunManifest.read(path)
    assert back.run_id == "test-run" and back.finished is not None
