"""WS5 memorization probe, open-weight side (pre-registration §7.4.3, D-10; approved by Dr. Lin 2026-10-21).

Runs the same twelve probe batches the Claude helpers answered (batches/<disease>_<probe>.json) on
the D-10 open-weight model: DeepSeek-V4.1-Flash on OpenRouter, provider pinned to DeepInfra fp8,
temperature 0, through the same client as the open-weight extraction
(pipeline/extract/openweight/agent.py), with no tools.

The task text is the Claude helpers' launch message, word for word, except for the two lines
about tools. The Claude helpers were told to Read the batch file and Write their answer; this
model gets the batch's items inline and returns the answer as its reply. The difference is
stated in scores_summary and the report.

Outputs: responses_openweight/<batch>.json (the parsed answer, same shape as responses/) and
responses_openweight/raw/<batch>.json (reply text, usage, provider, cost). A batch whose reply
does not parse is retried once; if it still fails it is left out and named.

  uv run python analysis/bias/memorization/run_openweight.py            # all twelve batches
  uv run python analysis/bias/memorization/score_probes.py --responses-dir responses_openweight \
      --out-prefix openweight_ --label "open-weight side (DeepSeek-V4.1-Flash)" --no-tool-check
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

from pipeline.extract.openweight.agent import OpenAICompatClient

ROOT = Path("analysis/bias/memorization")
MODEL, BASE, PROVIDER = "deepseek/deepseek-v4.1-flash", "https://openrouter.ai/api/v1", "deepinfra/fp8"

TASK = {
    "closed_book": (
        "Memorization probe, closed-book recall. This is a test of what you remember from training, not a research task.\n\n"
        "The items are given below. Each has a paper's PubMed ID, title and year. Use no tools and look nothing up.\n\n"
        "Task: for each paper, from memory alone, say what it reports:\n"
        "- variants: the gene variants it reports in patients, in HGVS-like notation where you can;\n"
        "- phenotypes: up to 8 key clinical features it reports in those patients, as short clinical terms (HPO labels where you can).\n\n"
        "If you do not remember a paper, give \"recall\": \"none\" and empty lists. Guessing from the title is allowed only if marked "
        "\"recall\": \"guess\". Use \"recall\": \"specific\" only for things you believe you remember from the paper itself. No commentary.\n\n"
        "Output (your whole reply): {{\"batch\": \"{batch}\", \"answers\": [{{\"id\": \"...\", \"recall\": \"specific|guess|none\", "
        "\"variants\": [\"...\"], \"phenotypes\": [\"...\"]}}]}}, with one answer per item in the order given.\n\nItems:\n{items}"),
    "completion": (
        "Memorization probe, guided completion. This is a test of what you remember from training, not a writing task.\n\n"
        "The items are given below. Each gives a paper's title, year, section heading and the first 50 words of a paragraph from its "
        "body (\"opening\"). Use no tools and look nothing up.\n\n"
        "Task: for each item, continue the paragraph exactly as it appears in the published paper, for about 50 words, from memory "
        "alone. If you do not recall the actual text, write your best guess anyway and mark it \"recall\": \"guess\". Use "
        "\"recall\": \"specific\" only when you believe you remember the paper's actual wording. No commentary.\n\n"
        "Output (your whole reply): {{\"batch\": \"{batch}\", \"answers\": [{{\"id\": \"...\", \"recall\": \"specific|guess\", "
        "\"continuation\": \"...\"}}]}}, with one answer per item in the order given.\n\nItems:\n{items}"),
}


def parse(text: str) -> dict | None:
    t = (text or "").strip()
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", t)
    i, k = t.find("{"), t.rfind("}")
    if i < 0 or k < 0:
        return None
    try:
        d = json.loads(t[i:k + 1])
    except json.JSONDecodeError:
        return None
    return d if isinstance(d.get("answers"), list) else None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--batches", nargs="*", default=None)
    a = ap.parse_args()
    out, raw = ROOT / "responses_openweight", ROOT / "responses_openweight" / "raw"
    raw.mkdir(parents=True, exist_ok=True)
    batches = a.batches or sorted(p.stem for p in (ROOT / "batches").glob("*.json"))
    failed = []
    for b in batches:
        if (out / f"{b}.json").exists():
            continue
        spec = json.loads((ROOT / "batches" / f"{b}.json").read_text())
        prompt = TASK[spec["probe"]].format(batch=b, items=json.dumps(spec["items"], indent=1, ensure_ascii=False))
        client = OpenAICompatClient(BASE, MODEL, "", PROVIDER)
        ans, attempts = None, []
        for _ in range(2):
            t0 = time.time()
            resp = client.complete([{"role": "user", "content": prompt}], [])
            text = resp["choices"][0]["message"].get("content") or ""
            attempts.append({"reply": text, "usage": resp.get("usage"), "provider": resp.get("provider"), "model": resp.get("model"),
                             "finish_reason": resp.get("finish_reason"), "wall_seconds": round(time.time() - t0, 1)})
            ans = parse(text)
            if ans:
                break
        (raw / f"{b}.json").write_text(json.dumps({"batch": b, "date": time.strftime("%Y-%m-%d", time.gmtime()), "model": MODEL,
                                                   "provider_pinned": PROVIDER, "attempts": attempts,
                                                   "retried_calls": client.retried}, indent=1, ensure_ascii=False) + "\n")
        if ans:
            ans["batch"] = b
            (out / f"{b}.json").write_text(json.dumps(ans, indent=1, ensure_ascii=False) + "\n")
            print(f"{b}: {len(ans['answers'])} answers for {len(spec['items'])} items", flush=True)
        else:
            failed.append(b)
            print(f"{b}: reply did not parse", flush=True)
    if failed:
        print("not parsed:", failed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
