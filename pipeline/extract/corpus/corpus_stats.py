"""Stage 1 gate numbers from the manifest: counts by study type and access status, token totals."""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from datetime import date
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    rows = list(csv.DictReader((base / "manifest.csv").open(newline="")))
    in_corpus = [r for r in rows if r.get("in_extraction_corpus", "").lower() == "true"]
    have_text = [r for r in in_corpus if r.get("fulltext_format")]
    tokens = {}
    for meta in (base / "fulltext_md").glob("*.meta.json") if (base / "fulltext_md").exists() else []:
        m = json.loads(meta.read_text())
        if "tokens" in m:
            tokens[m["pmid"]] = (m["tokens"], m.get("token_count_method"))
    stats = {
        "date": date.today().isoformat(),
        "n_manifest_rows": len(rows),
        "n_in_extraction_corpus": len(in_corpus),
        "by_study_type": dict(Counter(r.get("study_type", "") for r in rows)),
        "by_study_type_method": dict(Counter(r.get("study_type_method", "") for r in rows)),
        "by_access_status_in_corpus": dict(Counter(r.get("access_status", "") or "not attempted" for r in in_corpus)),
        "n_in_corpus_with_fulltext": len(have_text),
        "fulltext_coverage": round(len(have_text) / len(in_corpus), 4) if in_corpus else None,
        "gate_q1_min_coverage": 0.70,
        "gate_q1_met": (len(have_text) / len(in_corpus) >= 0.70) if in_corpus else None,
        "tokens_total": sum(t for t, _ in tokens.values()),
        "tokens_by_method": dict(Counter(m for _, m in tokens.values())),
        "n_docs_over_150k_tokens": sum(1 for t, _ in tokens.values() if t > 150_000),
        "paywalled": [{"pmid": r["pmid"], "doi": r.get("doi"), "journal": r.get("journal")} for r in in_corpus if r.get("access_status") == "paywalled"],
    }
    path = base / "corpus_stats.json"
    existing = json.loads(path.read_text()) if path.exists() else {}
    existing["latest"] = stats
    path.write_text(json.dumps(existing, indent=2) + "\n")
    print(json.dumps(stats, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
