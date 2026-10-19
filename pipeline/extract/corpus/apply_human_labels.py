"""Apply human-confirmed study-type and relevance labels to a disease manifest.

Reads a labels CSV with columns pmid, human_study_type, human_ha20_relevance,
reason, confirmed_by (e.g. data/literature/ha20/spotcheck_human_labels_2026-10-19.csv,
40 papers Jimmy confirmed on 2026-10-19 in the pilot-design session, after
Claude read each abstract). For each labelled PMID in manifest.csv:
  - a human study type fills study_type_human_check and study_type, and sets
    study_type_method = human (a human label always outranks an agent label);
  - a human relevance label replaces relevance, mapped to this manifest's
    vocabulary: ha20_patients -> yes, tnfaip3_other -> no, unclear -> unclear;
  - the reason and who confirmed it are appended to notes;
  - in_extraction_corpus is recomputed for that row only, by the screening
    rule (study type in case report / case series/cohort / review/meta-analysis
    AND relevance yes or unclear). Rows the labels do not name are untouched,
    including rows included by hand at the Stage 1 reconciliation.
Rows of the 20-row spot-check sheet (study_type_spotcheck.csv) that the labels
name get their human_study_type and human_relevance columns filled.

Prints every change and every corpus flip. Re-run corpus_stats afterwards.

  uv run python -m pipeline.extract.corpus.apply_human_labels --disease ha20 \
      --labels data/literature/ha20/spotcheck_human_labels_2026-10-19.csv
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

IN_CORPUS_TYPES = {"case report", "case series/cohort", "review/meta-analysis"}
STUDY_TYPES = IN_CORPUS_TYPES | {"functional only", "other"}
RELEVANCE_MAP = {"ha20_patients": "yes", "tnfaip3_other": "no", "unclear": "unclear"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--labels", required=True)
    args = ap.parse_args(argv)
    base = Path("data/literature") / args.disease
    labels = {r["pmid"].strip(): r for r in csv.DictReader(Path(args.labels).open(newline=""))}
    for pmid, lab in labels.items():
        st, rel = lab.get("human_study_type", "").strip(), lab.get("human_ha20_relevance", "").strip()
        if st and st not in STUDY_TYPES:
            raise SystemExit(f"{pmid}: unknown study type {st!r}")
        if rel and rel not in RELEVANCE_MAP:
            raise SystemExit(f"{pmid}: unknown relevance {rel!r}")
    path = base / "manifest.csv"
    rows = list(csv.DictReader(path.open(newline="")))
    cols = list(rows[0].keys())
    changes, flips, missing = [], [], sorted(set(labels) - {r["pmid"] for r in rows})
    original_type = {r["pmid"]: r["study_type"] for r in rows}
    typed = [p for p, lab in labels.items() if lab.get("human_study_type", "").strip() and p in original_type]
    agree = sum(original_type[p] == labels[p]["human_study_type"].strip() for p in typed)
    for r in rows:
        lab = labels.get(r["pmid"])
        if not lab:
            continue
        before = {k: r[k] for k in ("study_type", "relevance", "in_extraction_corpus")}
        st, rel = lab.get("human_study_type", "").strip(), lab.get("human_ha20_relevance", "").strip()
        if st:
            r["study_type_human_check"] = st
            r["study_type"] = st
            r["study_type_method"] = "human"
        if rel:
            r["relevance"] = RELEVANCE_MAP[rel]
        note = f"human check ({lab.get('confirmed_by', '').strip()}): " + "; ".join(
            x for x in (f"study type {st}" if st else "", f"relevance {rel}" if rel else "", lab.get("reason", "").strip()) if x)
        r["notes"] = (r.get("notes", "") + " | " + note).strip(" |")
        r["in_extraction_corpus"] = "true" if (r["study_type"] in IN_CORPUS_TYPES and r["relevance"] in ("yes", "unclear")) else "false"
        after = {k: r[k] for k in before}
        if after != before:
            changes.append({"pmid": r["pmid"], "before": before, "after": after})
        if after["in_extraction_corpus"] != before["in_extraction_corpus"]:
            flips.append({"pmid": r["pmid"], "from": before["in_extraction_corpus"], "to": after["in_extraction_corpus"]})
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    sheet = base / "study_type_spotcheck.csv"
    filled = []
    if sheet.exists():
        srows = list(csv.DictReader(sheet.open(newline="")))
        for s in srows:
            lab = labels.get(s["pmid"])
            if lab:
                s["human_study_type"] = lab.get("human_study_type", "").strip()
                s["human_relevance"] = RELEVANCE_MAP.get(lab.get("human_ha20_relevance", "").strip(), "")
                s["comment"] = (s.get("comment", "") + " " + f"from {Path(args.labels).name}").strip()
                filled.append(s["pmid"])
        with sheet.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(srows[0].keys()))
            w.writeheader()
            w.writerows(srows)
    print(json.dumps({"labels": len(labels), "not_in_manifest": missing, "rows_changed": len(changes),
                      "study_type_labels": len(typed),
                      "study_type_agreeing_with_agent": agree,
                      "corpus_flips": flips, "spotcheck_sheet_rows_filled": filled, "changes": changes}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
