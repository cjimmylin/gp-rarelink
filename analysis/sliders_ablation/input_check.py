"""Prove that the re-created inputs are the ones the SLIDERS arm read (D-44, design §3).

This container held none of the git-ignored full text, so the HA20 and SSADH papers were re-fetched
and re-converted on 2026-10-28. Three checks, written to analysis/sliders_ablation/input_check.json:

  1. fetched files: for every paper of pv1-<d>, the sha256 of the re-fetched XML or PDF against the
     sha256 the corpus manifest recorded at the original fetch (data/literature/<d>/manifest.csv);
  2. supplementary conversion: the regenerated conversion table against the committed one
     (data/literature/<d>/supplementary/conversion.csv): same files, statuses and character counts;
  3. spans: the frozen span check (pipeline.extract.claude_code.span_check) run on the pv1 output
     against the re-created Markdown. Every pv1 quote was found verbatim at the original run, so the
     span-found rate must be 1.0 again; the check runs in a scratch copy of the run folder so the
     committed pv1 files are not rewritten.

  uv run python analysis/sliders_ablation/input_check.py --diseases ha20 ssadh \
      --conversion-before <dir with <d>_conversion.csv copies of the committed tables>
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def check_fetched(d: str, papers: list[str]) -> dict:
    man = {r["pmid"]: r for r in csv.DictReader((ROOT / f"data/literature/{d}/manifest.csv").open())}
    same, differ, missing = [], [], []
    for p in papers:
        row = man[p]
        f = ROOT / f"data/literature/{d}/fulltext/{p}.{row['fulltext_format']}"
        if not f.exists():
            missing.append(p)
        elif sha(f) == row["sha256"]:
            same.append(p)
        else:
            differ.append(p)
    return {"papers": len(papers), "same_sha256": len(same), "different_sha256": differ, "missing": missing}


def check_conversion(d: str, before_dir: Path | None) -> dict:
    now = ROOT / f"data/literature/{d}/supplementary/conversion.csv"
    if before_dir is None or not (before_dir / f"{d}_conversion.csv").exists():
        return {"note": "no committed copy given; skipped"}
    key = lambda r: (r["pmid"], r["file"])
    b = {key(r): r for r in csv.DictReader((before_dir / f"{d}_conversion.csv").open())}
    n = {key(r): r for r in csv.DictReader(now.open())}
    same = [k for k in b if k in n and all(b[k][c] == n[k][c] for c in ("status", "chars_in", "chars_out"))]
    changed = [{"pmid": k[0], "file": k[1], "before": {c: b[k][c] for c in ("status", "chars_out")}, "now": {c: n[k][c] for c in ("status", "chars_out")}}
               for k in b if k in n and k not in set(same)]
    return {"rows_committed": len(b), "rows_now": len(n), "same": len(same), "changed": changed,
            "only_committed": [list(k) for k in b if k not in n], "only_now": [list(k) for k in n if k not in b]}


def check_spans(d: str) -> dict:
    run, tmp = f"pv1-{d}", f"pv1-{d}-inputcheck"
    src, dst = ROOT / f"data/extracted/{d}/{run}", ROOT / f"data/extracted/{d}/{tmp}"
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    os.symlink(src / "per_paper", dst / "per_paper")
    try:
        r = subprocess.run([sys.executable, "-m", "pipeline.extract.claude_code.span_check", "--disease", d, "--run-id", tmp,
                            "--schema", f"pipeline/extract/claude_code/schema_{d}_v5.json"], cwd=ROOT, capture_output=True, text=True)
        sc = json.loads((dst / "span_check.json").read_text())
        return {"n_papers": sc["n_papers"], "values_asserted": sc["counts"].get("values_asserted"), "span_found_rate": sc["span_found_rate"],
                "span_exact_rate": sc["span_exact_rate"], "n_problems": sc["n_problems"], "problems_head": sc["problems"][:10],
                "returncode": r.returncode}
    finally:
        shutil.rmtree(dst, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diseases", nargs="+", default=["ha20", "ssadh"])
    ap.add_argument("--conversion-before", type=Path, default=None)
    a = ap.parse_args(argv)
    out = {"checked_utc": datetime.now(UTC).isoformat(timespec="seconds"), "diseases": {}}
    for d in a.diseases:
        papers = json.loads((ROOT / f"runs/pv1-{d}/manifest.json").read_text())["documents"]
        out["diseases"][d] = {"fetched_files": check_fetched(d, papers), "supplementary_conversion": check_conversion(d, a.conversion_before),
                              "pv1_spans_in_recreated_markdown": check_spans(d),
                              "markdown_files": len(list((ROOT / f"data/literature/{d}/fulltext_md").glob("*.md")))}
    dest = ROOT / "analysis/sliders_ablation/input_check.json"
    dest.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
