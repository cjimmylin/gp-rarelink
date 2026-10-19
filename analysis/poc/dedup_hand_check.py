"""Combine merge hand-check verdicts into one table and a summary (Stage 3 check 6).

Helpers check every merged pair from pipeline.extract.reconcile against the two
papers and write verdict CSVs (pair_no, pmid_a, label_a, pmid_b, label_b,
reference_check, verdict, evidence_a, evidence_b, reason). This script joins
those verdicts back to merges.csv, so each verdict carries the pair's
confidence label and evidence, and checks that every merged pair has exactly
one verdict.

Writes analysis/poc/dedup_hand_check_<run_id>.csv and
analysis/poc/dedup_hand_check_summary_<run_id>.json, and prints the summary.

  uv run python analysis/poc/dedup_hand_check.py --disease ha20 --run-id poc-ha20-run-2 \
      --merges-file merges_policy_v3.csv --verdicts batch_a/verdicts.csv batch_b/verdicts.csv batch_c/verdicts.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--verdicts", nargs="+", required=True)
    ap.add_argument("--checked-by", default="helper agent (Opus)")
    ap.add_argument("--merges-file", default="merges.csv",
                    help="merge table the helpers checked; run-2's check used merges_policy_v3.csv")
    args = ap.parse_args(argv)
    merges = [r for r in csv.DictReader((Path("data/extracted") / args.disease / args.run_id / args.merges_file).open())
              if r["merged"] == "True"]
    key = lambda r: (r["pmid_a"], r["label_a"], r["pmid_b"], r["label_b"])  # noqa: E731
    by_key = {key(r): r for r in merges}
    verdicts, unmatched = [], []
    for i, path in enumerate(args.verdicts):
        batch = chr(ord("A") + i)
        for v in csv.DictReader(Path(path).open()):
            m = by_key.get(key(v))
            if m is None:
                unmatched.append(dict(v))
                continue
            verdicts.append(v | {"checked_by": f"{args.checked_by}, batch {batch}", "confidence": m["confidence"],
                                 "variant_key": m["variant_key"], "script_evidence": m["evidence"]})
    seen = Counter(key(v) for v in verdicts)
    missing = [list(k) for k in by_key if seen[k] == 0]
    duplicated = [list(k) for k, n in seen.items() if n > 1]
    cols = ["pair_no", "pmid_a", "label_a", "pmid_b", "label_b", "variant_key", "confidence", "script_evidence",
            "reference_check", "verdict", "evidence_a", "evidence_b", "reason", "checked_by"]
    out_csv = Path("analysis/poc") / f"dedup_hand_check_{args.run_id}.csv"
    with out_csv.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        w.writerows(sorted(verdicts, key=lambda v: int(v["pair_no"])))
    by_conf: dict[str, Counter] = {}
    for v in verdicts:
        by_conf.setdefault(v["confidence"], Counter())[v["verdict"]] += 1
    summary = {
        "run_id": args.run_id,
        "policy": merges[0].get("policy") if merges else None,
        "merged_pairs": len(merges),
        "hand_checked": len(verdicts),
        "verdicts": dict(Counter(v["verdict"] for v in verdicts)),
        "verdicts_by_confidence": {k: dict(c) for k, c in sorted(by_conf.items())},
        "reference_check": dict(Counter(v["reference_check"] for v in verdicts)),
        "false_merges": [{k: v[k] for k in ("pair_no", "pmid_a", "label_a", "pmid_b", "label_b", "confidence", "reason")}
                         for v in verdicts if v["verdict"] == "false_merge"],
        "cannot_tell": [{k: v[k] for k in ("pair_no", "pmid_a", "label_a", "pmid_b", "label_b", "confidence", "reason")}
                        for v in verdicts if v["verdict"] == "cannot_tell"],
        "merged_pairs_without_verdict": missing,
        "pairs_with_more_than_one_verdict": duplicated,
        "verdict_rows_not_matching_a_merge": unmatched,
    }
    (Path("analysis/poc") / f"dedup_hand_check_summary_{args.run_id}.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k not in ("false_merges", "cannot_tell")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
