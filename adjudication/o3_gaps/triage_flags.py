"""Pre-adjudication flags per gap candidate (O3, §7.3), from the evidence dossiers and candidates.csv.

Flags are pointers for the panel, not verdicts; every flag cites where it came from. Sources:
  protein_mismatch       candidates.csv protein_check says "differs" (stated protein vs the protein
                         VariantValidator predicts from the normalized cDNA)
  review_only            every supporting paper is a review (candidates.csv n_non_review_papers = 0)
  possible_same_person   a dossier concern mentions the same person or patient under several
                         identities ("same person", "same patient", "same girl/boy/woman/man",
                         "probably one", "citation of")
  notation_conflict      a concern reports a notation conflict: a typo, legacy numbering, the
                         paper writing the variant two ways, or a coordinate that does not fit
                         (a missing transcript alone is not flagged)
  carriers_not_attached  a concern says carriers are missing from the batch
  other_variant          a concern mentions another variant or gene in the same person
  mosaic_or_somatic      a concern mentions mosaicism or a somatic finding
  possible_existing_record  a concern mentions an existing database accession (SCV/RCV/VCV)
  newly_in_clinvar       the allele has a GRCh38 record in a newer ClinVar snapshot (--recheck)
Keyword flags come from model-written concerns; they can be wrong in either direction.

  python3 -I adjudication/o3_gaps/triage_flags.py [--recheck-summary adjudication/o3_gaps/recheck_<date>.json]
writes adjudication/o3_gaps/triage.csv and triage_summary.json.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path("adjudication/o3_gaps")
RULES = {
    "possible_same_person": re.compile(r"same (person|patient|girl|boy|woman|man|individual|family|proband|people)|probably one|is a citation of|cited (patient|case)|counted twice|entered twice|very likely (the same|one)", re.I),
    "notation_conflict": re.compile(r"typo|legacy (numbering|notation|intron)|probably (a typo|means|c\.)|(writes|written|gives|reads) [^.;]{0,60}c\.[^.;]{0,60}\b(but|vs\.?|against|elsewhere|while)\b|both [^.;]{0,20}(G>C|G>T|A>G|C>T)|inconsistent(ly)? [^.;]{0,40}(c\.|position|nucleotide)|coordinate is probably wrong|wrong base|does not fit", re.I),
    "carriers_not_attached": re.compile(r"(missing|not) (from|in) (the )?batch|not attached|not linked|no identity in the batch|not in batch", re.I),
    "other_variant": re.compile(r"(another|second|other) (candidate )?variant|also carries|also (homozygous|heterozygous) for|variants? in [A-Z0-9]{3,}|exome .* found", re.I),
    "mosaic_or_somatic": re.compile(r"mosaic|somatic", re.I),
    "possible_existing_record": re.compile(r"\b(SCV|RCV|VCV)\d{5,}", re.I),
}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--recheck-summary", default=None)
    a = ap.parse_args(argv)
    newly = set()
    if a.recheck_summary and Path(a.recheck_summary).exists():
        newly = set(json.loads(Path(a.recheck_summary).read_text()).get("now_in_clinvar", []))
    rows, tally = [], Counter()
    for c in csv.DictReader((ROOT / "candidates.csv").open()):
        cid = c["candidate_id"]
        d = json.loads((ROOT / "dossiers" / f"{cid}.json").read_text())
        concerns = [str(x) for x in d.get("concerns") or []]
        flags = {}
        if c["protein_check"].startswith("differs"):
            flags["protein_mismatch"] = c["protein_check"]
        if c.get("n_non_review_papers") == "0":
            flags["review_only"] = "all supporting papers are reviews"
        for name, rx in RULES.items():
            hits = [x for x in concerns if rx.search(x)]
            if hits:
                flags[name] = hits[0][:240]
        if cid in newly:
            flags["newly_in_clinvar"] = "GRCh38 allele now in ClinVar (see recheck)"
        tally.update(flags.keys())
        rows.append({"candidate_id": cid, "disease": c["disease"], "hgvs_c": c["hgvs_c"], "n_flags": len(flags),
                     "flags": ";".join(sorted(flags)), "evidence": json.dumps(flags, ensure_ascii=False)})
    with (ROOT / "triage.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    summ = {"candidates": len(rows), "with_any_flag": sum(r["n_flags"] > 0 for r in rows), "by_flag": dict(sorted(tally.items())),
            "by_disease_any_flag": dict(Counter(r["disease"] for r in rows if r["n_flags"])),
            "note": "Keyword flags from model-written dossier concerns; pointers for the panel, not verdicts."}
    (ROOT / "triage_summary.json").write_text(json.dumps(summ, indent=1) + "\n")
    print(json.dumps(summ, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
