"""Export unbound phenotype phrases for the model-assisted HPO binding step (Stage 4 step 3).

After a first pass of bind_ontologies, reads data/extracted/<disease>/<run_id>/hpo_bindings.csv,
takes the distinct feature texts of rows still 'unbound' (folded the way bind_ontologies
folds them for --model-bindings: whitespace collapsed, lower case), and writes batches
for helpers working under prompts/hpo_binding_v1.md:

  <run_dir>/hpo_model_bindings/input_<n>.csv   text_id, feature_text, label_candidate
  <run_dir>/hpo_model_bindings/keymap.csv      text_id, norm_text

Text ids are <DISEASE>-B<n>-<row>. The pilot did the same export by hand
(poc-ha20-run-2/hpo_model_bindings); this script makes it re-runnable (D-40).

  uv run python -m pipeline.extract.hpo_binding_export --disease danon --run-id pv1-danon --batch-size 300
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--batch-size", type=int, default=300)
    a = ap.parse_args(argv)
    run_dir = Path("data/extracted") / a.disease / a.run_id
    seen: dict[str, tuple[str, str]] = {}
    for r in csv.DictReader((run_dir / "hpo_bindings.csv").open()):
        if r["method"] != "unbound":
            continue
        k = norm(r["feature_text_as_stated"])
        if k and k not in seen:
            seen[k] = (r["feature_text_as_stated"], r["hpo_label_candidate"])
    out = run_dir / "hpo_model_bindings"
    out.mkdir(exist_ok=True)
    for old in out.glob("input_*.csv"):
        old.unlink()
    keys = sorted(seen)
    keymap = []
    for b in range(0, len(keys), a.batch_size):
        n = b // a.batch_size + 1
        with (out / f"input_{n}.csv").open("w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["text_id", "feature_text", "label_candidate"])
            for i, k in enumerate(keys[b:b + a.batch_size], 1):
                tid = f"{a.disease.upper()}-B{n}-{i:04d}"
                w.writerow([tid, seen[k][0], seen[k][1]])
                keymap.append((tid, k))
    with (out / "keymap.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["text_id", "norm_text"])
        w.writerows(keymap)
    print(f"{a.disease}: {len(keys)} distinct unbound phrases in {(len(keys) + a.batch_size - 1) // a.batch_size} batches -> {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
