"""Open-weight comparison (pre-registration §7.5, D-10): one extraction helper as a tool-using agent.

The Claude side ran each paper as a Claude Code helper agent (D-17, D-20). This module gives
the open-weight model the same task in the same shape:
  - the same launch prompt (launch_prompt_v1.txt, copied verbatim from the pv1 helpers, with
    the same placeholders filled),
  - the same instruction, schema and rules files (read by the model through its tools),
  - file tools with the same limits: read_file, grep, glob, write_file and edit_file. Reads are
    allowed only for the paper, the schema, the rules, the instructions file and the scratch
    directory; writes only for the output file and the scratch directory. A refused call
    returns an error message to the model and is logged.
Remaining differences, to state in the write-up: the Claude helpers also had a shell (they used
it to run small checking scripts) and Claude Code's own system prompt; this loop has neither.

The model is called through an OpenAI-compatible chat-completions endpoint (the hosted APIs
for DeepSeek-V4.1-Flash use that format). Endpoint, model id and key come from the environment
(OPENWEIGHT_BASE_URL, OPENWEIGHT_MODEL, OPENWEIGHT_API_KEY, OPENWEIGHT_PROVIDER), or from
OPENROUTER_API_KEY alone, which selects OpenRouter (https://openrouter.ai/api/v1) and the model id
deepseek/deepseek-v4.1-flash, the 2026-09-10 checkpoint (read from OpenRouter's model list on
2026-10-21). Endpoint, model, pinned provider and the provider that served each call are
recorded in the transcript, never the key.

  uv run python -m pipeline.extract.openweight.agent --disease danon --pmid 22290069 \
      --run-id ow-danon-pilot --dry-run      # prints the filled prompt and the tool allowlist
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Protocol

ROOT = Path(__file__).resolve().parents[3]
PROMPT = Path(__file__).with_name("launch_prompt_v1.txt")
MAX_TURNS = 200
MAX_READ_CHARS = 60_000

TOOLS = [
    {"type": "function", "function": {"name": "read_file", "description": "Read a text file. Optional 1-based line offset and line limit.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "offset": {"type": "integer"}, "limit": {"type": "integer"}},
                    "required": ["path"]}}},
    {"type": "function", "function": {"name": "grep", "description": "Search a file for a regular expression; returns matching lines with line numbers.",
     "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string"}, "context": {"type": "integer"}},
                    "required": ["pattern", "path"]}}},
    {"type": "function", "function": {"name": "glob", "description": "List files under the scratch directory matching a pattern.",
     "parameters": {"type": "object", "properties": {"pattern": {"type": "string"}}, "required": ["pattern"]}}},
    {"type": "function", "function": {"name": "write_file", "description": "Write (replace) a whole file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}}, "required": ["path", "content"]}}},
    {"type": "function", "function": {"name": "edit_file", "description": "Replace one exact, unique string in a file.",
     "parameters": {"type": "object", "properties": {"path": {"type": "string"}, "old": {"type": "string"}, "new": {"type": "string"}},
                    "required": ["path", "old", "new"]}}},
]


class ChatClient(Protocol):
    def complete(self, messages: list[dict], tools: list[dict]) -> dict: ...


@dataclass
class OpenAICompatClient:
    """Minimal OpenAI-compatible chat client over httpx (no new dependency).

    With OpenRouter, `provider` pins one upstream endpoint (e.g. "deepinfra/fp8") with fallbacks
    off, so every call is served by the same provider and precision; the provider that answered
    is read back from each response and logged."""
    base_url: str
    model: str
    api_key: str
    provider: str | None = None
    timeout: float = 600.0
    served_by: list = field(default_factory=list)

    max_tokens: int = 65536
    call_wall_seconds: float = 1800.0

    def complete(self, messages: list[dict], tools: list[dict]) -> dict:
        """Streams the reply (so a long JSON answer shows progress and a stalled call is caught)
        and reassembles it into one chat-completions response."""
        import httpx
        body: dict[str, Any] = {"model": self.model, "messages": messages, "tools": tools, "temperature": 0,
                                "max_tokens": self.max_tokens, "stream": True}
        if "openrouter.ai" in self.base_url:
            body["usage"] = {"include": True}
            if self.provider:
                body["provider"] = {"order": [self.provider], "allow_fallbacks": False}
        headers = {"Authorization": f"Bearer {self.api_key}"} if self.api_key else {}  # empty: the environment's proxy adds the key
        content, reasoning, calls, usage, meta = [], [], {}, {}, {}
        t0, last_report = time.time(), 0
        with httpx.stream("POST", self.base_url.rstrip("/") + "/chat/completions", headers=headers, json=body,
                          timeout=httpx.Timeout(self.timeout, read=300.0)) as r:
            r.raise_for_status()
            for line in r.iter_lines():
                if time.time() - t0 > self.call_wall_seconds:
                    raise TimeoutError(f"call exceeded {self.call_wall_seconds:.0f} s")
                if not line.startswith("data:"):
                    continue  # SSE comments are keep-alives
                data = line[5:].strip()
                if data == "[DONE]":
                    break
                ev = json.loads(data)
                if ev.get("error"):
                    raise RuntimeError(f"provider error: {ev['error']}")
                meta.update({k: ev[k] for k in ("provider", "model", "id") if k in ev})
                if ev.get("usage"):
                    usage = ev["usage"]
                for ch in ev.get("choices") or []:
                    dl = ch.get("delta") or {}
                    if dl.get("content"):
                        content.append(dl["content"])
                    if dl.get("reasoning"):
                        reasoning.append(dl["reasoning"])
                    for tc in dl.get("tool_calls") or []:
                        slot = calls.setdefault(tc.get("index", 0), {"id": "", "type": "function", "function": {"name": "", "arguments": ""}})
                        if tc.get("id"):
                            slot["id"] = tc["id"]
                        fn = tc.get("function") or {}
                        slot["function"]["name"] += fn.get("name") or ""
                        slot["function"]["arguments"] += fn.get("arguments") or ""
                n = sum(len(x) for x in content) + sum(len(c["function"]["arguments"]) for c in calls.values())
                if n - last_report > 20000:
                    last_report = n
                    print(f"  ... {n} characters streamed, {time.time() - t0:.0f} s", flush=True)
        msg: dict[str, Any] = {"role": "assistant", "content": "".join(content) or None}
        if calls:
            msg["tool_calls"] = [calls[i] for i in sorted(calls)]
        out = {"choices": [{"message": msg}], "usage": usage, **meta, "reasoning_chars": sum(len(x) for x in reasoning)}
        self.served_by.append({"provider": out.get("provider"), "model": out.get("model"),
                               "cost": (out.get("usage") or {}).get("cost")})
        return out


@dataclass
class Sandbox:
    reads: set[Path]
    writes: set[Path]
    scratch: Path
    log: list[dict] = field(default_factory=list)

    def _resolve(self, p: str) -> Path:
        return Path(p).expanduser().resolve()

    def can_read(self, p: Path) -> bool:
        return p in self.reads or p in self.writes or self.scratch in p.parents

    def can_write(self, p: Path) -> bool:
        return p in self.writes or self.scratch in p.parents

    def call(self, name: str, args: dict) -> str:
        try:
            out = self._call(name, args)
            self.log.append({"tool": name, "args": {k: v for k, v in args.items() if k != "content"}, "ok": True})
            return out
        except PermissionError as e:
            self.log.append({"tool": name, "args": {k: v for k, v in args.items() if k != "content"}, "ok": False, "refused": str(e)})
            return f"ERROR: {e}"
        except Exception as e:  # noqa: BLE001  (reported back to the model, as a tool error would be)
            self.log.append({"tool": name, "args": {k: v for k, v in args.items() if k != "content"}, "ok": False, "error": str(e)})
            return f"ERROR: {type(e).__name__}: {e}"

    def _call(self, name: str, a: dict) -> str:
        if name == "glob":
            return "\n".join(str(p) for p in sorted(self.scratch.rglob("*")) if fnmatch.fnmatch(p.name, a["pattern"])) or "(no files)"
        p = self._resolve(a["path"])
        if name in ("read_file", "grep"):
            if not self.can_read(p):
                raise PermissionError(f"reading {p} is not allowed")
            lines = p.read_text(errors="replace").splitlines()
            if name == "read_file":
                off = max(1, int(a.get("offset") or 1))
                lim = int(a.get("limit") or len(lines))
                text = "\n".join(f"{i}\t{l}" for i, l in enumerate(lines[off - 1:off - 1 + lim], off))
                return text[:MAX_READ_CHARS] + ("\n[truncated; read on with offset]" if len(text) > MAX_READ_CHARS else "")
            rx, ctx = re.compile(a["pattern"]), int(a.get("context") or 0)
            hits = [i for i, l in enumerate(lines) if rx.search(l)]
            out = []
            for i in hits[:200]:
                for j in range(max(0, i - ctx), min(len(lines), i + ctx + 1)):
                    out.append(f"{j + 1}\t{lines[j]}")
            return "\n".join(out) or "(no matches)"
        if name in ("write_file", "edit_file"):
            if not self.can_write(p):
                raise PermissionError(f"writing {p} is not allowed")
            p.parent.mkdir(parents=True, exist_ok=True)
            if name == "write_file":
                p.write_text(a["content"])
                return f"wrote {len(a['content'])} characters"
            text = p.read_text()
            if text.count(a["old"]) != 1:
                raise ValueError("old string must occur exactly once")
            p.write_text(text.replace(a["old"], a["new"]))
            return "edited"
        raise ValueError(f"unknown tool {name}")


def task_paths(disease: str, pmid: str, run_id: str, scratch: Path) -> dict[str, Path]:
    instr = ROOT / "pipeline/extract/claude_code/prompts" / (f"extract_v6_{disease}.md" if disease != "ha20" else "extract_v6.md")
    schema = ROOT / "pipeline/extract/claude_code" / f"schema_{disease}_v5.json"
    return {"instructions": instr, "schema": schema,
            "rules": ROOT / "pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md",
            "paper": ROOT / f"data/literature/{disease}/fulltext_md/{pmid}.md",
            "output": ROOT / f"data/extracted/{disease}/{run_id}/per_paper/{pmid}.json", "scratch": scratch}


def run(client: ChatClient, paths: dict[str, Path], transcript: Path, meta: dict | None = None,
        now: Callable[[], float] = time.time, progress: bool = False) -> dict:
    prompt = PROMPT.read_text().format(**{k: str(v) for k, v in paths.items()})
    paths["scratch"].mkdir(parents=True, exist_ok=True)
    box = Sandbox(reads={paths[k].resolve() for k in ("instructions", "schema", "rules", "paper")},
                  writes={paths["output"].resolve()}, scratch=paths["scratch"].resolve())
    messages: list[dict[str, Any]] = [{"role": "user", "content": prompt}]
    usage = {"prompt_tokens": 0, "completion_tokens": 0, "calls": 0}
    t0, final = now(), ""
    transcript.parent.mkdir(parents=True, exist_ok=True)

    def save(status: str) -> None:  # written after every turn, so an interrupted run keeps its transcript
        transcript.write_text(json.dumps({"status": status, "meta": meta or {}, "usage": usage, "tool_log": box.log,
                                          "messages": messages}, indent=1, ensure_ascii=False) + "\n")

    for turn in range(MAX_TURNS):
        resp = client.complete(messages, TOOLS)
        usage["calls"] += 1
        for k in ("prompt_tokens", "completion_tokens"):
            usage[k] += int((resp.get("usage") or {}).get(k) or 0)
        msg = resp["choices"][0]["message"]
        messages.append({k: v for k, v in msg.items() if k in ("role", "content", "tool_calls")})
        calls = msg.get("tool_calls") or []
        if not calls:
            final = msg.get("content") or ""
            break
        for c in calls:
            try:
                args = json.loads(c["function"].get("arguments") or "{}")
            except json.JSONDecodeError:
                args = None
            content = box.call(c["function"]["name"], args) if isinstance(args, dict) else "ERROR: arguments were not valid JSON"
            messages.append({"role": "tool", "tool_call_id": c["id"], "content": content})
        save("running")
        if progress:
            print(f"turn {turn + 1}: {[c['function']['name'] for c in calls]} tokens {usage['prompt_tokens']}+{usage['completion_tokens']}",
                  flush=True)
    result = {"meta": meta or {}, "prompt_file": str(PROMPT.relative_to(ROOT)), "usage": usage, "wall_seconds": round(now() - t0, 1),
              "tool_log": box.log, "final_reply": final, "output_written": paths["output"].exists(),
              "refused_calls": sum(1 for x in box.log if "refused" in x)}
    transcript.parent.mkdir(parents=True, exist_ok=True)
    transcript.write_text(json.dumps({"result": result, "messages": messages}, indent=1, ensure_ascii=False) + "\n")
    return result


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--pmid", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--scratch", default="/tmp/openweight_scratch")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)
    paths = task_paths(a.disease, a.pmid, a.run_id, Path(a.scratch) / a.pmid)
    if a.dry_run:
        print(PROMPT.read_text().format(**{k: str(v) for k, v in paths.items()}))
        print("reads allowed:", [str(paths[k]) for k in ("instructions", "schema", "rules", "paper")])
        print("writes allowed:", str(paths["output"]), "and", str(paths["scratch"]))
        return 0
    envf = ROOT / ".env"  # git-ignored; keys never go in code or commits
    if envf.exists():
        for line in envf.read_text().splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())
    key = os.environ.get("OPENWEIGHT_API_KEY") or os.environ.get("OPENROUTER_API_KEY") or ""
    # Default: OpenRouter. In this cloud environment the key is a network secret for openrouter.ai that the
    # proxy adds to each request, so the session never holds it (checked 2026-10-21 with GET /api/v1/key).
    base = os.environ.get("OPENWEIGHT_BASE_URL") or "https://openrouter.ai/api/v1"
    model = os.environ.get("OPENWEIGHT_MODEL") or "deepseek/deepseek-v4.1-flash"  # OpenRouter id of the 2026-09-10 checkpoint (D-10)
    provider = os.environ.get("OPENWEIGHT_PROVIDER") or "deepinfra/fp8"  # one fp8 provider, no fallbacks (DECISIONS 2026-10-21)
    if not key and "openrouter.ai" not in base:
        raise SystemExit("no key for a non-OpenRouter endpoint: set OPENWEIGHT_API_KEY (D-10)")
    client = OpenAICompatClient(base, model, key, provider)
    meta = {"endpoint": base, "model": model, "provider_pinned": provider, "run_id": a.run_id, "disease": a.disease, "pmid": a.pmid,
            "date": time.strftime("%Y-%m-%d", time.gmtime())}
    res = run(client, paths, ROOT / f"runs/{a.run_id}/transcripts/{a.pmid}.json", meta, progress=True)
    served = client.served_by
    res["served_by"] = sorted({f"{x['provider']}|{x['model']}" for x in served})
    res["cost_usd_reported"] = round(sum(x["cost"] or 0 for x in served), 6)
    print(json.dumps({k: res[k] for k in ("usage", "wall_seconds", "output_written", "refused_calls", "served_by", "cost_usd_reported")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
