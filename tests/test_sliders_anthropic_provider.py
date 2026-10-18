"""The SLIDERS Anthropic provider, exercised against a local fake Messages API.

Runs only when the patched SLIDERS is installed (scripts/install_sliders.sh).
No network, no key: ANTHROPIC_BASE_URL points at a thread-local HTTP server
that records the request body and returns a canned Claude response. The
assertions are about the wire payload the adapter produces.
"""

from __future__ import annotations

import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

import pytest

sliders = pytest.importorskip("sliders")
from pydantic import BaseModel  # noqa: E402


class _Handler(BaseHTTPRequestHandler):
    requests: list[dict] = []
    reply_text: str = "{}"

    def do_POST(self):  # noqa: N802
        n = int(self.headers.get("Content-Length", 0))
        body = json.loads(self.rfile.read(n) or b"{}")
        _Handler.requests.append({"path": self.path, "headers": dict(self.headers), "body": body})
        reply = {
            "id": "msg_test",
            "type": "message",
            "role": "assistant",
            "model": body.get("model", "claude-opus-5-5"),
            "content": [{"type": "text", "text": _Handler.reply_text}],
            "stop_reason": "end_turn",
            "stop_sequence": None,
            "usage": {"input_tokens": 120, "output_tokens": 30, "cache_read_input_tokens": 100, "cache_creation_input_tokens": 0},
        }
        data = json.dumps(reply).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *a):  # silence
        pass


@pytest.fixture()
def fake_api(monkeypatch):
    server = HTTPServer(("127.0.0.1", 0), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    _Handler.requests.clear()
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", f"http://127.0.0.1:{server.server_port}")
    monkeypatch.setenv("SLIDERS_LLM_PROVIDER", "anthropic")
    monkeypatch.delenv("SLIDERS_ANTHROPIC_FALLBACKS", raising=False)
    monkeypatch.delenv("SLIDERS_ANTHROPIC_CACHE", raising=False)
    yield _Handler
    server.shutdown()


class Verdict(BaseModel):
    reasoning: str
    is_relevant: bool


def test_structured_output_uses_json_schema_not_forced_tools(fake_api):
    from sliders.llm.llm import get_llm_client

    fake_api.reply_text = json.dumps({"reasoning": "mentions TNFAIP3", "is_relevant": True})
    llm = get_llm_client(model="claude-opus-5-5", temperature=0.0, max_tokens=256, effort="medium")
    chain = llm.with_structured_output(Verdict)
    out = chain.invoke("Is this chunk relevant?")
    assert isinstance(out, Verdict) and out.is_relevant is True

    body = fake_api.requests[-1]["body"]
    assert body["model"] == "claude-opus-5-5"
    assert "temperature" not in body and "top_p" not in body and "top_k" not in body
    assert "tool_choice" not in body, "forced tool choice is rejected by current Claude models"
    assert body["output_config"]["format"]["type"] == "json_schema"
    assert body["output_config"]["effort"] == "medium"
    assert body["fallbacks"] == "default"
    assert body["cache_control"] == {"type": "ephemeral"}
    betas = fake_api.requests[-1]["headers"].get("anthropic-beta", "")
    assert "server-side-fallback-2026-07-01" in betas
    assert "/v1/messages" in fake_api.requests[-1]["path"]


def test_json_mode_without_schema_parses_json_text(fake_api):
    from sliders.llm.llm import get_llm_client

    fake_api.reply_text = "```json\n{\"tables\": [{\"a\": 1}]}\n```"
    llm = get_llm_client(model="claude-opus-5-5", temperature=0.7)
    chain = llm.with_structured_output(method="json_mode")
    out = chain.invoke("Extract.")
    assert out == {"tables": [{"a": 1}]}
    body = fake_api.requests[-1]["body"]
    assert "output_config" not in body or "format" not in body.get("output_config", {})


def test_fallbacks_and_cache_can_be_disabled(fake_api, monkeypatch):
    from sliders.llm.llm import get_llm_client

    monkeypatch.setenv("SLIDERS_ANTHROPIC_FALLBACKS", "off")
    monkeypatch.setenv("SLIDERS_ANTHROPIC_CACHE", "off")
    fake_api.reply_text = "ok"
    llm = get_llm_client(model="claude-opus-5-5")
    llm.invoke("hi")
    body = fake_api.requests[-1]["body"]
    assert "fallbacks" not in body and "cache_control" not in body


def test_usage_recorder_feeds_run_manifest(fake_api):
    from sliders.llm.llm import get_llm_client

    from pipeline.common.run_manifest import RunManifest
    from pipeline.extract.sliders_adapter.usage_callback import UsageRecorder

    manifest = RunManifest(run_id="t", stage=2, model="claude-opus-5-5")
    rec = UsageRecorder(manifest)
    fake_api.reply_text = "ok"
    llm = get_llm_client(model="claude-opus-5-5")
    llm.invoke("hi", config={"callbacks": [rec]})
    assert rec.calls == 1
    assert manifest.usage["cache_read_input_tokens"] == 100
    assert manifest.usage["input_tokens"] == 120  # API input_tokens excludes cached; langchain adds them, the recorder removes them again
    assert manifest.usage["output_tokens"] == 30
    assert manifest.cost_usd > 0


def test_invalid_effort_is_rejected(fake_api):
    from sliders.llm.llm import get_llm_client

    with pytest.raises(ValueError):
        get_llm_client(model="claude-opus-5-5", effort="turbo")
