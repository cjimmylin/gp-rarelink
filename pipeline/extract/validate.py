"""Validate one run's phenopackets (POC_DESIGN.md Stage 4 step 5).

1. Schema: each file must parse into the GA4GH Phenopacket v2 protobuf message
   (phenopackets package), with no unknown fields.
2. Ontology, against the pinned HPO release (pipeline/extract/ontologies.py):
   every phenotypic feature term exists, is not obsolete, and carries the
   release's label.
3. Logic:
   - no term both observed and excluded in one phenopacket;
   - no observed term whose ancestor is excluded (a contradiction, e.g.
     observed 'Polyarthritis' with excluded 'Arthritis');
   - redundant terms (an observed term together with an observed ancestor, or
     an excluded term together with an excluded ancestor) are counted as
     warnings, as cohort validators flag them.
4. Provenance: every phenotypic feature and every phenopacket has at least one
   PMID reference, and each feature's PMIDs appear in metaData.
5. Interpretations: each genomic interpretation has a variation descriptor with
   a gene context; CAUSATIVE ones belong to an interpretation marked SOLVED.

POC_DESIGN.md named pyphetools for cohort validation. This script implements
the checks the pilot needs directly against the pinned HPO instead, to avoid a
large dependency (Claude's call, 2026-10-19).

Writes data/extracted/<disease>/<run_id>/validation_report.json and prints it.

  uv run python -m pipeline.extract.validate --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from google.protobuf.json_format import Parse, ParseError
from phenopackets import GenomicInterpretation, Interpretation, Phenopacket

from pipeline.extract import ontologies


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    hp = ontologies.load("hp")
    files = sorted((run_dir / "phenopackets").glob("*.json"))
    c, errors, warnings = Counter(), [], []
    for f in files:
        try:
            pp = Parse(f.read_text(), Phenopacket(), ignore_unknown_fields=False)
        except ParseError as e:
            errors.append({"file": f.name, "check": "schema", "detail": str(e)[:300]})
            continue
        c["schema_valid"] += 1
        refs = {r.id for r in pp.meta_data.external_references}
        if not refs:
            errors.append({"file": f.name, "check": "provenance", "detail": "no PMID in metaData"})
        observed, excluded = set(), set()
        for feat in pp.phenotypic_features:
            tid = feat.type.id
            t = hp.terms.get(tid)
            if t is None or t.obsolete:
                errors.append({"file": f.name, "check": "hpo_term", "detail": f"{tid} missing or obsolete"})
                continue
            if feat.type.label != t.name:
                errors.append({"file": f.name, "check": "hpo_label", "detail": f"{tid} label {feat.type.label!r} != {t.name!r}"})
            pmids = {e.reference.id for e in feat.evidence}
            if not pmids:
                errors.append({"file": f.name, "check": "provenance", "detail": f"{tid} has no evidence"})
            elif not pmids <= refs:
                errors.append({"file": f.name, "check": "provenance", "detail": f"{tid} cites PMIDs not in metaData"})
            (excluded if feat.excluded else observed).add(tid)
            c["features_excluded" if feat.excluded else "features_observed"] += 1
        for tid in observed & excluded:
            errors.append({"file": f.name, "check": "observed_and_excluded", "detail": tid})
        for tid in observed:
            anc = hp.ancestors(tid)
            for x in anc & excluded:
                errors.append({"file": f.name, "check": "observed_under_excluded_ancestor",
                               "detail": f"observed {tid} {hp.terms[tid].name} but excluded ancestor {x} {hp.terms[x].name}"})
            for x in anc & observed:
                warnings.append({"file": f.name, "check": "redundant_observed_ancestor", "detail": f"{tid} with ancestor {x}"})
        for tid in excluded:
            for x in hp.ancestors(tid) & excluded:
                warnings.append({"file": f.name, "check": "redundant_excluded_ancestor", "detail": f"{tid} with ancestor {x}"})
        for interp in pp.interpretations:
            causative = False
            for gi in interp.diagnosis.genomic_interpretations:
                vd = gi.variant_interpretation.variation_descriptor
                if not vd.gene_context.value_id:
                    errors.append({"file": f.name, "check": "interpretation", "detail": "variation descriptor without gene context"})
                causative |= gi.interpretation_status == GenomicInterpretation.CAUSATIVE
                c["genomic_interpretations"] += 1
            if causative and interp.progress_status != Interpretation.SOLVED:
                errors.append({"file": f.name, "check": "interpretation", "detail": "CAUSATIVE variant in an interpretation not marked SOLVED"})
    by_check = Counter(e["check"] for e in errors)
    report = {"run_id": args.run_id, "hpo_release": hp.version, "phenopackets": len(files),
              "schema_valid": c["schema_valid"], "share_schema_valid": round(c["schema_valid"] / len(files), 4) if files else None,
              "counts": dict(sorted(c.items())), "errors_by_check": dict(sorted(by_check.items())),
              "warnings_by_check": dict(sorted(Counter(w["check"] for w in warnings).items())),
              "errors": errors[:500], "warnings_sample": warnings[:50]}
    (run_dir / "validation_report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: report[k] for k in report if k not in ("errors", "warnings_sample")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
