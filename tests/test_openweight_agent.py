"""The open-weight agent loop (D-10) on a scripted stub model: tools, limits and the transcript."""
import json
from pathlib import Path

from pipeline.extract.openweight import agent


class Stub:
    """Replays a fixed list of assistant messages; records what it was sent."""

    def __init__(self, script):
        self.script, self.seen = list(script), []

    def complete(self, messages, tools):
        self.seen.append(len(messages))
        msg = self.script.pop(0)
        return {"choices": [{"message": {"role": "assistant", **msg}}], "usage": {"prompt_tokens": 10, "completion_tokens": 5}}


def call(i, name, **args):
    return {"id": f"c{i}", "type": "function", "function": {"name": name, "arguments": json.dumps(args)}}


def make_paths(tmp: Path) -> dict:
    for n in ("instr.md", "schema.json", "rules.md", "paper.md", "secret.txt"):
        (tmp / n).write_text(f"{n} line one\nTNFAIP3 c.559C>T\n")
    return {"instructions": tmp / "instr.md", "schema": tmp / "schema.json", "rules": tmp / "rules.md",
            "paper": tmp / "paper.md", "output": tmp / "out" / "p.json", "scratch": tmp / "scratch"}


def test_loop_reads_writes_and_refuses(tmp_path):
    p = make_paths(tmp_path)
    stub = Stub([
        {"content": None, "tool_calls": [call(1, "read_file", path=str(p["paper"])), call(2, "grep", pattern="559", path=str(p["paper"]))]},
        {"content": None, "tool_calls": [call(3, "read_file", path=str(tmp_path / "secret.txt"))]},
        {"content": None, "tool_calls": [call(4, "write_file", path=str(tmp_path / "elsewhere.json"), content="{}")]},
        {"content": None, "tool_calls": [call(5, "write_file", path=str(p["output"]), content='{"tables": {}}'),
                                         call(6, "write_file", path=str(p["scratch"] / "notes.txt"), content="x")]},
        {"content": "1 individual; done."},
    ])
    res = agent.run(stub, p, tmp_path / "t.json", {"model": "stub"}, now=lambda: 0.0)
    assert res["output_written"] and json.loads(p["output"].read_text()) == {"tables": {}}
    assert res["refused_calls"] == 2
    assert not (tmp_path / "elsewhere.json").exists()
    assert res["usage"] == {"prompt_tokens": 50, "completion_tokens": 25, "calls": 5}
    assert res["final_reply"] == "1 individual; done."
    t = json.loads((tmp_path / "t.json").read_text())
    first = t["messages"][0]["content"]
    assert str(p["paper"]) in first and str(p["output"]) in first and "{paper}" not in first
    tool_msgs = [m for m in t["messages"] if m["role"] == "tool"]
    assert "c.559C>T" in tool_msgs[1]["content"] and tool_msgs[2]["content"].startswith("ERROR")


def test_prompt_matches_the_claude_helpers():
    text = agent.PROMPT.read_text()
    assert text.startswith("You are an extraction helper for the GP-RareLink research study")
    for ph in ("{instructions}", "{schema}", "{rules}", "{paper}", "{output}", "{scratch}"):
        assert ph in text


def test_client_retries_dropped_connection(monkeypatch):
    import httpx

    from pipeline.extract.openweight import agent as ag
    c = ag.OpenAICompatClient("https://example.invalid/v1", "m", "")
    calls = {"n": 0}

    def flaky(messages, tools):
        calls["n"] += 1
        if calls["n"] < 3:
            raise httpx.ReadError("Connection reset by peer")
        return {"ok": True}

    monkeypatch.setattr(c, "_complete_once", flaky)
    monkeypatch.setattr(ag.time, "sleep", lambda s: None)
    assert c.complete([], []) == {"ok": True}
    assert len(c.retried) == 2


def test_client_does_not_retry_client_error(monkeypatch):
    import httpx
    import pytest

    from pipeline.extract.openweight import agent as ag
    c = ag.OpenAICompatClient("https://example.invalid/v1", "m", "")
    req = httpx.Request("POST", "https://example.invalid/v1/chat/completions")

    def bad(messages, tools):
        raise httpx.HTTPStatusError("bad", request=req, response=httpx.Response(400, request=req))

    monkeypatch.setattr(c, "_complete_once", bad)
    with pytest.raises(httpx.HTTPStatusError):
        c.complete([], [])
    assert c.retried == []
