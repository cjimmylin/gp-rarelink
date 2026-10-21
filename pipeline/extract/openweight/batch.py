"""Run the open-weight agent over a run's papers, several at a time (D-10, §7.5).

Each paper runs as its own process (`python -m pipeline.extract.openweight.agent`), with its log in
runs/<run_id>/logs/<pmid>.log. A paper whose transcript already holds a final result is skipped,
so the batch can be resumed. Before launching each paper the batch reads the OpenRouter key's
usage (GET /api/v1/key; the environment's proxy adds the key) and stops launching new papers once
this batch has spent more than --stop-usd. Papers default to those of the matching Claude run
(pv1-<disease>), so both models see the same papers.

  uv run python -m pipeline.extract.openweight.batch --disease ha20 --run-id ow-ha20 --workers 10 --stop-usd 40
writes runs/<run_id>/batch_status.json (updated as papers finish).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


def key_usage() -> float | None:
    import httpx
    try:
        r = httpx.get("https://openrouter.ai/api/v1/key", timeout=30)
        return float(r.json()["data"]["usage"])
    except Exception:  # noqa: BLE001
        return None


def done(run_id: str, pmid: str) -> bool:
    t = ROOT / f"runs/{run_id}/transcripts/{pmid}.json"
    if not t.exists():
        return False
    try:
        return "result" in json.loads(t.read_text())
    except json.JSONDecodeError:
        return False


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--papers-from", default=None, help="Claude run whose papers to use (default pv1-<disease>)")
    ap.add_argument("--workers", type=int, default=10)
    ap.add_argument("--stop-usd", type=float, default=40.0)
    ap.add_argument("--baseline-usd", type=float, default=None,
                    help="key usage to count spend from (default: usage when this batch starts); pass the first batch's start to cap several batches together")
    ap.add_argument("--scratch", default="/tmp/openweight_scratch")
    a = ap.parse_args(argv)
    src = a.papers_from or f"pv1-{a.disease}"
    papers = sorted(p.stem for p in (ROOT / f"data/extracted/{a.disease}/{src}/per_paper").glob("*.json"))
    todo = [p for p in papers if not done(a.run_id, p)]
    logs = ROOT / f"runs/{a.run_id}/logs"
    logs.mkdir(parents=True, exist_ok=True)
    start_usage = a.baseline_usd if a.baseline_usd is not None else key_usage()
    status = {"run_id": a.run_id, "disease": a.disease, "papers": len(papers), "skipped_done": len(papers) - len(todo),
              "start_key_usage": start_usage, "stop_usd": a.stop_usd, "finished": {}, "stopped_for_spend": False,
              "started_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    status_path = ROOT / f"runs/{a.run_id}/batch_status.json"

    def write_status() -> None:
        status["key_usage_now"] = key_usage()
        status_path.write_text(json.dumps(status, indent=1) + "\n")

    def one(pmid: str) -> tuple[str, int]:
        if start_usage is not None:
            u = key_usage()
            if u is not None and u - start_usage > a.stop_usd:
                status["stopped_for_spend"] = True
                return pmid, -1
        with (logs / f"{pmid}.log").open("w") as fh:
            rc = subprocess.call([sys.executable, "-m", "pipeline.extract.openweight.agent", "--disease", a.disease, "--pmid", pmid,
                                  "--run-id", a.run_id, "--scratch", f"{a.scratch}/{a.run_id}"], cwd=ROOT, stdout=fh,
                                 stderr=subprocess.STDOUT, env={**__import__("os").environ, "PYTHONUNBUFFERED": "1"})
        return pmid, rc

    write_status()
    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        futs = [ex.submit(one, p) for p in todo]
        for f in as_completed(futs):
            pmid, rc = f.result()
            status["finished"][pmid] = rc
            write_status()
            print(f"{pmid} rc={rc} ({len(status['finished'])}/{len(todo)})", flush=True)
    status["ended_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    write_status()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
