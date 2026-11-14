"""Full-text screening import for the D-47 corpus addendum, kept apart from the registered manifest.

The registered import (`pipeline.extract.corpus.claude_code_fulltext_screen import`)
writes its decisions into data/literature/<disease>/manifest.csv. D-47 says the
registered corpus records stay unchanged, so this script applies the same label
validation and the same verbatim evidence-quote check (whitespace normalized),
using that module's own constants and `norm`, and writes the decisions to:

  data/literature/<disease>/addendum_d47/screening.csv   one row per paper
  data/literature/<disease>/addendum_d47/screening_log.json   run log with the prompt sha256

Labels come from data/literature/<disease>/addendum_d47/labels/*.csv, written by
helpers under pipeline/extract/claude_code/prompts/screen_fulltext_v1.md.

  uv run python analysis/corpus/free_copies/addendum_screen.py --disease tangier
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from pipeline.extract.corpus.claude_code_fulltext_screen import (
    DECISIONS,
    PROMPT,
    REASONS,
    STUDY_TYPES,
    YESNO,
    norm,
)

COLS = ["pmid", "decision", "exclusion_reason", "study_type", "n_individuals", "has_genotype",
        "literature_table", "evidence_quote", "quote_found", "note", "label_file"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    a = ap.parse_args()
    base = Path("data/literature") / a.disease
    add = base / "addendum_d47"
    files = sorted((add / "labels").glob("*.csv"))
    labels, problems = {}, []
    for f in files:
        for lab in csv.DictReader(f.open(newline="")):
            lab = {k: (v or "").strip() for k, v in lab.items() if k}
            pmid, dec, why = lab.get("pmid", ""), lab.get("decision", "").lower(), lab.get("exclusion_reason", "").lower()
            st, n = lab.get("study_type", "").lower(), lab.get("n_individuals", "").lower()
            ok = (dec in DECISIONS and (why in REASONS if dec == "exclude" else why == "")
                  and st in STUDY_TYPES and (n.isdigit() or n == "unclear")
                  and lab.get("has_genotype", "").lower() in YESNO and lab.get("literature_table", "").lower() in YESNO
                  and lab.get("evidence_quote"))
            if not ok:
                problems.append(f"{f.name}: pmid {pmid}: invalid label {lab}")
                continue
            if pmid in labels:
                problems.append(f"{f.name}: pmid {pmid} labelled twice")
            lab["label_file"] = str(f)
            labels[pmid] = lab
    if problems:
        raise SystemExit("invalid labels, nothing written:\n  " + "\n  ".join(problems))
    missing = []
    for pmid, lab in labels.items():
        path = base / "fulltext_md" / f"{pmid}.md"
        lab["quote_found"] = "true" if path.exists() and norm(lab["evidence_quote"]) in norm(path.read_text()) else "false"
        if lab["quote_found"] == "false":
            missing.append(pmid)
    if missing:
        raise SystemExit(f"evidence_quote not found verbatim for {missing}; nothing written")
    with (add / "screening.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=COLS, extrasaction="ignore")
        w.writeheader()
        for pmid in sorted(labels, key=int):
            lab = labels[pmid]
            w.writerow({**lab, "decision": lab["decision"].lower(), "exclusion_reason": lab["exclusion_reason"].lower(),
                        "study_type": lab["study_type"].lower()})
    run = {
        "date": datetime.now(UTC).date().isoformat(),
        "decision": "D-47 corpus addendum",
        "route": "claude_code (D-20)",
        "prompt_file": str(PROMPT),
        "prompt_sha256": hashlib.sha256(PROMPT.read_bytes()).hexdigest(),
        "label_files": [str(f) for f in files],
        "n_labels": len(labels),
        "by_decision": dict(Counter(l["decision"].lower() for l in labels.values())),
        "exclusion_reasons": dict(Counter(l["exclusion_reason"].lower() for l in labels.values() if l["exclusion_reason"])),
        "included": sorted((p for p, l in labels.items() if l["decision"].lower() == "include"), key=int),
    }
    log = add / "screening_log.json"
    data = json.loads(log.read_text()) if log.exists() else {"runs": []}
    data["runs"].append(run)
    log.write_text(json.dumps(data, indent=2) + "\n")
    print(json.dumps(run))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
