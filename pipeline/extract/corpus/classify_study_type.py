"""Stage 1, step 1 (model part): classify study_type for manifest rows from title + abstract.

Uses claude-haiku-5-5 with structured output; writes study_type and
study_type_method = "model" for rows whose provisional type is empty, keeps
provisional MeSH-derived types (method = "mesh"), and never overwrites a row
whose study_type_human_check is filled. Then sets in_extraction_corpus.

Also writes a 20-row spot-check sheet (random, seeded) for the human check.
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, Field

from pipeline.common.run_manifest import RunManifest
from pipeline.extract.guard import assert_isolated

STUDY_TYPES = ("case report", "case series/cohort", "review/meta-analysis", "functional only", "other")
IN_CORPUS_TYPES = {"case report", "case series/cohort", "review/meta-analysis"}
MODEL = "claude-haiku-5-5"


class StudyType(BaseModel):
    study_type: Literal["case report", "case series/cohort", "review/meta-analysis", "functional only", "other"]
    reason: str = Field(description="One sentence citing the words in the title/abstract that decide it.")


SYSTEM = (
    "You classify biomedical publications by study design from title and abstract only. "
    "'case report' = one patient or one family described clinically; 'case series/cohort' = several "
    "unrelated patients described with clinical detail (including registry and multicentre studies); "
    "'review/meta-analysis' = narrative or systematic review, meta-analysis, guideline; 'functional only' = "
    "laboratory or model-organism work with no new patient descriptions; 'other' = anything else "
    "(editorials, letters without patients, methods). Use only the text given."
)


def classify(client, pmid: str, title: str, abstract: str, manifest: RunManifest) -> StudyType:
    msg = client.messages.parse(
        model=MODEL,
        max_tokens=512,
        system=SYSTEM,
        messages=[{"role": "user", "content": f"PMID {pmid}\nTitle: {title}\n\nAbstract: {abstract or '(no abstract)'}"}],
        output_format=StudyType,
    )
    manifest.add_usage(msg.usage.model_dump(exclude_none=True))
    if msg.stop_reason == "refusal":
        manifest.record_error(pmid, "refusal")
        raise RuntimeError("refusal")
    return msg.parsed_output


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, default=20261018)
    args = ap.parse_args(argv)
    assert_isolated()

    from anthropic import Anthropic

    client = Anthropic()
    path = Path("data/literature") / args.disease / "manifest.csv"
    rows = list(csv.DictReader(path.open(newline="")))
    cols = rows[0].keys()
    manifest = RunManifest(run_id=args.run_id, stage=1, model=MODEL, effort=None)
    n_model = 0
    for row in rows:
        if row.get("study_type_human_check"):
            row["study_type"] = row["study_type_human_check"]
            row["study_type_method"] = "human"
        elif row.get("study_type"):
            pass
        elif row.get("study_type_provisional"):
            row["study_type"] = row["study_type_provisional"]
            row["study_type_method"] = "mesh"
        else:
            res = classify(client, row["pmid"], row["title"], row.get("abstract", ""), manifest)
            row["study_type"] = res.study_type
            row["study_type_method"] = "model"
            row["notes"] = (row.get("notes", "") + " | classifier: " + res.reason).strip(" |")
            n_model += 1
        row["in_extraction_corpus"] = "true" if row["study_type"] in IN_CORPUS_TYPES else "false"
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cols))
        w.writeheader()
        w.writerows(rows)
    manifest.notes.update({"n_rows": len(rows), "n_model_classified": n_model})
    manifest.finish()
    print(manifest.write())

    rng = random.Random(args.seed)
    sample = rng.sample(rows, min(20, len(rows)))
    check = path.with_name("study_type_spotcheck.csv")
    with check.open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pmid", "title", "study_type", "study_type_method", "human_label", "comment"])
        for r in sample:
            w.writerow([r["pmid"], r["title"], r["study_type"], r["study_type_method"], "", ""])
    print(f"spot-check sheet: {check} (seed {args.seed})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
