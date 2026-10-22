"""Write runs/ow-<d>/manifest.json for the open-weight runs (D-10): what ran, on what, and how often.

From the transcripts and logs: model, endpoint, pinned provider and the providers that served
calls; launch prompt and instruction files; papers; harness tool version per final attempt;
calls, tokens, cost the host reported and wall-clock for final attempts; retries and resumes;
failed attempts kept in runs/ow-<d>/failed_attempts/. Key spend for the whole batch (failed and
stopped attempts included) is passed in, because only the host's key reading covers it.

  uv run python analysis/openweight/make_manifest.py --key-start 1.0689 --key-end 21.4237
"""
import argparse
import hashlib
import json
import subprocess
from collections import Counter
from pathlib import Path


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()[:16]


def one(d):
    run = Path(f"runs/ow-{d}")
    pmids = sorted(p.stem for p in Path(f"data/extracted/{d}/ow-{d}/per_paper").glob("*.json"))
    tools, served, calls, ptok, ctok, wall, cost, retries, resumes = Counter(), Counter(), 0, 0, 0, 0.0, 0.0, 0, 0
    meta0 = None
    for p in pmids:
        r = json.loads((run / "transcripts" / f"{p}.json").read_text())["result"]
        meta0 = meta0 or r["meta"]
        tools[r["meta"].get("tools_version", "v1")] += 1
        calls += r["usage"]["calls"]; ptok += r["usage"]["prompt_tokens"]; ctok += r["usage"]["completion_tokens"]
        wall += r["wall_seconds"] or 0
        resumes += r.get("continuations", 0)
        last = [l for l in (run / "logs" / f"{p}.log").read_text(errors="replace").splitlines() if l.startswith('{"usage"')]
        if last:
            j = json.loads(last[-1])
            cost += j.get("cost_usd_reported") or 0
            served.update(j.get("served_by") or [])
            retries += len(j.get("retried_calls") or [])
    fa = run / "failed_attempts"
    failed = sorted({f.name.split(".")[0] for f in fa.glob("*.log")}) if fa.exists() else []
    instr = "pipeline/extract/claude_code/prompts/" + ("extract_v6.md" if d == "ha20" else f"extract_v6_{d}.md")
    files = [instr, f"pipeline/extract/claude_code/schema_{d}_v5.json", "pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md",
             "pipeline/extract/openweight/launch_prompt_v1.txt"]
    return {"run_id": f"ow-{d}", "disease": d, "date": meta0.get("date"), "model": meta0.get("model"), "endpoint": meta0.get("endpoint"),
            "provider_pinned": meta0.get("provider_pinned"), "served_by_final_attempts": dict(served),
            "papers": len(pmids), "papers_from": f"pv1-{d}", "input_files_sha256_16": {f: sha(f) for f in files},
            "tools_version_of_final_attempt": dict(tools),
            "final_attempts": {"calls": calls, "prompt_tokens": ptok, "completion_tokens": ctok,
                               "cost_usd_reported_by_host": round(cost, 4), "wall_seconds_sum": round(wall),
                               "retried_calls": retries, "resumes_after_cut_off_reply": resumes},
            "papers_with_failed_attempts": failed,
            "harness": "pipeline/extract/openweight/agent.py + batch.py (DECISIONS.md, D-10 OpenRouter entry)"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--key-start", type=float, required=True)
    ap.add_argument("--key-end", type=float, required=True)
    a = ap.parse_args()
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True).stdout.strip()
    for d in ("ha20", "ssadh"):
        m = one(d)
        m["key_spend_both_runs_usd"] = {"start": a.key_start, "end": a.key_end, "spent": round(a.key_end - a.key_start, 4),
                                        "note": "OpenRouter key usage (GET /api/v1/key) before HA20 and after SSADH; covers both runs, failed and stopped attempts included"}
        m["written_at_commit"] = commit
        Path(f"runs/ow-{d}/manifest.json").write_text(json.dumps(m, indent=1) + "\n")
        print(json.dumps(m, indent=1))


if __name__ == "__main__":
    main()
