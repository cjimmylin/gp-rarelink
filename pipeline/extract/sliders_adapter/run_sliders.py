"""Run SLIDERS (Anthropic provider) over a corpus directory with a pinned schema.

    uv run python -m pipeline.extract.sliders_adapter.run_sliders \
        --docs data/literature/ha20/fulltext_md --run-id poc-ha20-smoke-1 \
        --max-docs 3 --debug

Writes:
  runs/<run_id>/manifest.json      token usage, cost, hashes, fallbacks, errors
  runs/<run_id>/sliders/           SLIDERS output dir (results JSON, intermediate tables with --debug)
  runs/<run_id>/question.txt       the exact question sent (task + extraction rules)

Refuses to start if ground truth is reachable (pipeline.extract.guard).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import shutil
import tempfile
from contextvars import ContextVar
from pathlib import Path

from pipeline.common.run_manifest import RunManifest, sha256_file, sha256_text
from pipeline.extract.guard import assert_isolated

HERE = Path(__file__).resolve().parent
DEFAULT_SCHEMA = HERE / "schema_ha20.json"
DEFAULT_RULES = HERE / "prompts" / "extraction_rules_v1.md"
DEFAULT_CONFIG = Path("configs/sliders_ha20.yaml")
DEFAULT_QUESTION = (
    "For each individual person with a TNFAIP3 variant described in these documents, record the "
    "individual, their family, the variant exactly as printed, its zygosity and inheritance, and "
    "every clinical feature the document explicitly reports as present or explicitly reports as "
    "absent for that person, together with the publication-level facts."
)
DOCUMENT_DESCRIPTION = (
    "Published biomedical article (case report, case series, cohort study or review) describing "
    "patients with a genetic disorder; the header lines give PMID, title, journal and year."
)

_usage_recorder_var: ContextVar = ContextVar("gp_rarelink_usage_recorder", default=None)


def build_question(task: str, rules_path: Path) -> str:
    rules = rules_path.read_text().strip()
    return f"{task}\n\n{rules}"


def _register_global_callback(recorder) -> None:
    """Attach the usage recorder to every LangChain run in this process."""
    from langchain_core.tracers.context import register_configure_hook

    register_configure_hook(_usage_recorder_var, inheritable=True)
    _usage_recorder_var.set(recorder)


async def _run(args) -> dict:
    from sliders.run import _load_config, _resolve_docs_dir  # patched SLIDERS, see scripts/install_sliders.sh

    config = _load_config(str(args.config))
    schema = json.loads(Path(args.schema).read_text())
    question = build_question(args.question, args.rules)

    run_dir = Path("runs") / args.run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "question.txt").write_text(question + "\n")
    out_dir = run_dir / "sliders"
    out_dir.mkdir(exist_ok=True)
    os.environ["SLIDERS_RESULTS"] = str(out_dir)
    os.environ.setdefault("SLIDERS_LOGS_DIR", str(run_dir / "logs"))

    model = config["system_config"]["models"]["extract_schema"]["model"]
    effort = config["system_config"]["models"]["extract_schema"].get("effort")
    manifest = RunManifest(run_id=args.run_id, stage=args.stage, model=model, effort=effort)
    manifest.schema_sha256 = sha256_file(args.schema)
    manifest.prompt_sha256 = {"extraction_rules": sha256_file(args.rules), "question": sha256_text(question), "sliders_config": sha256_file(args.config)}
    manifest.sliders_version = _sliders_version()

    from pipeline.extract.sliders_adapter.usage_callback import UsageRecorder

    recorder = UsageRecorder(manifest)
    _register_global_callback(recorder)

    if not args.verbose:
        from sliders.log_utils import suppress_console_logging

        suppress_console_logging()

    from sliders.experiments.wiki_celeb import WikiCeleb
    from sliders.globals import SlidersGlobal
    from sliders.system import SlidersAgent

    class CaseReportCorpus(WikiCeleb):
        @property
        def description(self) -> str:
            return DOCUMENT_DESCRIPTION

    docs = sorted(p for p in Path(args.docs).glob("*.md"))
    if args.max_docs:
        docs = docs[: args.max_docs]
    if not docs:
        raise SystemExit(f"no .md documents under {args.docs}")
    manifest.n_documents = len(docs)
    manifest.input_manifest_sha256 = sha256_text("\n".join(f"{p.name}:{sha256_file(p)}" for p in docs))
    manifest.notes["documents"] = [p.name for p in docs]

    with tempfile.TemporaryDirectory() as tmp:
        files_dir = _resolve_docs_dir([str(p) for p in docs], tmp)
        qfile = Path(tmp) / "questions.txt"
        qfile.write_text(question + "\n")
        config["experiment_config"].update({"questions_path": str(qfile), "files_dir": files_dir, "num_questions": None})
        if args.debug:
            config["system_config"].setdefault("merge_tables", {}).setdefault("reconciliation", {})["debug_mode"] = True
        config["system_config"].setdefault("generate_schema", {})["user_schema"] = schema
        config["system_config"]["output_folder"] = str(out_dir)

        experiment = CaseReportCorpus(config["experiment_config"])
        system = SlidersAgent(config["system_config"])
        try:
            results = await experiment.run(system, sample_size=None, random_state=config["experiment_config"].get("random_state", 42))
        except Exception as exc:  # record, then re-raise after writing the manifest
            manifest.record_error(None, f"{type(exc).__name__}: {exc}")
            manifest.finish()
            manifest.write()
            raise
        results["config"] = config
        results_path = out_dir / f"sliders_output_{SlidersGlobal.experiment_id}.json"
        results_path.write_text(json.dumps(results, indent=2, default=str))

    manifest.notes.update({"results_json": str(results_path), "llm_calls": recorder.calls, "unpriced_calls": recorder.unpriced})
    manifest.finish()
    path = manifest.write()
    return {"manifest": str(path), "results": str(results_path), "cost_usd": manifest.cost_usd, "usage": manifest.usage}


def _sliders_version() -> str:
    vendor = Path(".vendor/sliders")
    try:
        import subprocess

        commit = subprocess.check_output(["git", "-C", str(vendor), "rev-parse", "HEAD"], text=True).strip()
        return f"stanford-oval/sliders@{commit[:12]}+0001-anthropic-provider"
    except Exception:
        return "unknown (see scripts/install_sliders.sh)"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--docs", type=Path, required=True, help="directory of .md documents")
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--stage", type=int, default=3)
    ap.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    ap.add_argument("--question", default=DEFAULT_QUESTION)
    ap.add_argument("--max-docs", type=int, default=None, help="smoke tests: first N documents only")
    ap.add_argument("--debug", action="store_true", help="save intermediate reconciliation tables")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    assert_isolated()
    if not os.getenv("ANTHROPIC_API_KEY"):
        raise SystemExit("STOP: ANTHROPIC_API_KEY is not set (put it in .env). No run was made.")
    os.environ.setdefault("SLIDERS_LLM_PROVIDER", "anthropic")
    if (Path("runs") / args.run_id / "manifest.json").exists():
        raise SystemExit(f"STOP: runs/{args.run_id}/manifest.json exists; runs are immutable, pick a new run id.")

    summary = asyncio.run(_run(args))
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
