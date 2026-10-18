"""Run manifests for the Claude Code route (D-20).

Claude Code helper agents do not expose per-call token usage, so this records
what can be recorded: the commit, the hashes of the instructions, schema and
rules the agents were given, the documents processed, the model requested for
the agents, and the session's own list-price usage readings taken before and
after the stage (from the session metadata; estimates, not billing figures).

  uv run python -m pipeline.extract.claude_code.run_record start --run-id poc-ha20-smoke-1 \
      --stage 2 --agent-model opus --prompt pipeline/extract/claude_code/prompts/extract_v1.md \
      --docs 12345 23456 --session-cost-before 19.63
  uv run python -m pipeline.extract.claude_code.run_record finish --run-id poc-ha20-smoke-1 \
      --session-cost-after 27.10 --served-model claude-opus-5-5
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.common.run_manifest import RUNS_DIR, RunManifest, sha256_file

SCHEMA = Path("pipeline/extract/claude_code/schema_ha20_v2.json")
RULES = Path("pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md")


def start(args: argparse.Namespace) -> int:
    m = RunManifest(run_id=args.run_id, stage=args.stage, model=f"Claude Code helper agents ({args.agent_model})",
                    effort=None, provider="claude_code")
    m.schema_sha256 = sha256_file(args.schema)
    m.notes["schema_file"] = str(args.schema)
    m.prompt_sha256 = {"rules": sha256_file(RULES)}
    for p in args.prompt:
        m.prompt_sha256[Path(p).stem] = sha256_file(p)
    m.n_documents = len(args.docs)
    m.notes.update({
        "route": "claude_code (D-20)",
        "documents": args.docs,
        "agent_model_requested": args.agent_model,
        "session_cost_usd_before": args.session_cost_before,
        "session_cost_note": "Session metadata list-price estimate; not a billing figure. Reconcile against claude.ai Settings > Usage.",
        "cost_usd_field": "0.0 by construction: per-call usage is not available on this route",
    })
    print(m.write())
    return 0


def finish(args: argparse.Namespace) -> int:
    path = RUNS_DIR / args.run_id / "manifest.json"
    data = json.loads(path.read_text())
    m = RunManifest(**data)
    m.notes["session_cost_usd_after"] = args.session_cost_after
    before = m.notes.get("session_cost_usd_before")
    if before is not None and args.session_cost_after is not None:
        m.notes["session_cost_usd_delta"] = round(args.session_cost_after - before, 2)
    if args.served_model:
        m.notes["served_model_reported"] = args.served_model
    if args.note:
        m.notes.setdefault("remarks", []).append(args.note)
    m.finish()
    print(m.write())
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("start")
    s.add_argument("--run-id", required=True)
    s.add_argument("--stage", type=int, required=True)
    s.add_argument("--agent-model", required=True)
    s.add_argument("--prompt", nargs="+", required=True)
    s.add_argument("--docs", nargs="*", default=[])
    s.add_argument("--session-cost-before", type=float, default=None)
    s.add_argument("--schema", default=str(SCHEMA))
    f = sub.add_parser("finish")
    f.add_argument("--run-id", required=True)
    f.add_argument("--session-cost-after", type=float, default=None)
    f.add_argument("--served-model", default=None)
    f.add_argument("--note", default=None)
    args = ap.parse_args(argv)
    return start(args) if args.cmd == "start" else finish(args)


if __name__ == "__main__":
    raise SystemExit(main())
