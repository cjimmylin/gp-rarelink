"""Launch and finish records for the direct-extraction runs (SLIDERS ablation, D-44).

The Claude Code route gives no per-call usage, so the record keeps what can be kept: the commit,
the sha256 of the instruction and launch prompt the helpers were given, the papers, the model
requested, and the session's cost readings where the session reports one (they lag and freeze;
helper tokens are the better estimate, `analysis/cost/helper_tokens.py`).

  uv run python analysis/sliders_ablation/run_manifest.py start --disease ha20 --run-id direct-ha20 --session-cost-before 0
  uv run python analysis/sliders_ablation/run_manifest.py finish --disease ha20 --run-id direct-ha20 \
      --served-model claude-opus-5-5 --helpers "85 extraction helpers" --note "..."
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def commit() -> str:
    return subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("start", "finish"))
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--agent-model", default="opus")
    ap.add_argument("--session-cost-before", type=float)
    ap.add_argument("--session-cost-after", type=float)
    ap.add_argument("--served-model")
    ap.add_argument("--helpers")
    ap.add_argument("--note", action="append", default=[])
    a = ap.parse_args(argv)
    run_dir = ROOT / "runs" / a.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    instr = ROOT / f"pipeline/extract/claude_code/prompts/direct_v1_{a.disease}.md"
    launch = ROOT / "pipeline/extract/claude_code/prompts/direct_launch_v1.txt"
    template = ROOT / "pipeline/extract/claude_code/prompts/direct_v1.md"
    if a.cmd == "start":
        papers = json.loads((ROOT / f"runs/pv1-{a.disease}/manifest.json").read_text())["documents"]
        rec = {"run_id": a.run_id, "disease": a.disease, "arm": "D (direct extraction, no SLIDERS-style scaffold)",
               "decision": "D-44 (SLIDERS ablation pilot; reports/sliders_ablation_design.md)",
               "route": f"Claude Code helper agents, {a.agent_model} (as pv1, D-20)", "launch_commit": commit(),
               "launched_utc": datetime.now(UTC).isoformat(timespec="seconds"),
               "papers": papers, "n_papers": len(papers), "papers_from": f"pv1-{a.disease}",
               "markdown_dir": f"data/literature/{a.disease}/fulltext_md",
               "prompt_sha256": {str(p.relative_to(ROOT)): sha(p) for p in (instr, launch, template)},
               "helpers_read": "the paper and the instruction file only",
               "session_cost_usd_before": a.session_cost_before,
               "session_cost_note": "Session metadata list-price estimate when available; it lags and freezes. Helper tokens are the cost estimate of record.",
               "notes": a.note}
        (run_dir / "launch.json").write_text(json.dumps(rec, indent=1) + "\n")
        print(json.dumps({k: rec[k] for k in ("run_id", "n_papers", "launch_commit", "prompt_sha256")}, indent=1))
        return 0
    rec = json.loads((run_dir / "launch.json").read_text())
    rec.update({"finished_utc": datetime.now(UTC).isoformat(timespec="seconds"), "finish_commit": commit(),
                "prompt_sha256_at_finish_unchanged": all(sha(p) == rec["prompt_sha256"][str(p.relative_to(ROOT))] for p in (instr, launch, template)),
                "served_model_reported": a.served_model, "helpers": a.helpers, "session_cost_usd_after": a.session_cost_after})
    rec["notes"] = rec.get("notes", []) + a.note
    out_dir = ROOT / "data/extracted" / a.disease / a.run_id
    rec["outputs"] = {"records": len(list((out_dir / "records").glob("*.json"))), "per_paper": len(list((out_dir / "per_paper").glob("*.json")))}
    conv = out_dir / "conversion_summary.json"
    if conv.exists():
        rec["conversion_counts"] = {k: v for k, v in json.loads(conv.read_text())["counts"].items() if not k.startswith(("filled:", "unknown:", "enum_outside:"))}
    (run_dir / "manifest.json").write_text(json.dumps(rec, indent=1) + "\n")
    print(json.dumps({k: rec[k] for k in ("run_id", "outputs", "prompt_sha256_at_finish_unchanged", "served_model_reported")}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
