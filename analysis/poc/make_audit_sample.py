"""Draw the Stage 5 human-audit sample (POC_DESIGN.md Stage 5 step 2).

50 claims from one run, stratified as POC_DESIGN.md specifies, random with a
recorded seed, oversampling nothing:
  20 variant fields       variants table, any field except pmid, the label and
                          inheritance;
  20 phenotypic features  phenotypic_features.status, 10 observed and 10 excluded;
  10 demographic or inheritance fields  individuals: sex, ages, ethnicity or
                          country, consanguinity, vital status, proband status;
                          plus variants.inheritance.
Bookkeeping claims (pmid fields, labels repeated in child tables) are not
eligible. Each row shows the value, the span, the PMID, the person and the
feature or variant the row is about. The gatekeeper verdict is not shown; it is
joined only when the ratings are scored (audit_metrics.py).

Writes adjudication/poc_audit/sample.csv (for the rater) and
adjudication/poc_audit/sample_key.json (seed, strata, claim ids).

  uv run python analysis/poc/make_audit_sample.py --disease ha20 --run-id poc-ha20-run-2 --seed 20261019
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from pathlib import Path

DEMOGRAPHIC = {"sex", "age_at_onset_original_text", "age_at_onset_iso8601", "age_at_last_evaluation_original_text",
               "age_at_last_evaluation_iso8601", "age_at_diagnosis_original_text", "age_at_diagnosis_iso8601",
               "ethnicity_or_country", "consanguinity", "vital_status", "is_proband"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--seed", type=int, required=True)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    claims = {r["claim_id"]: r for r in csv.DictReader((run_dir / "gatekeeper_claims.csv").open())}
    spans = list(csv.DictReader((run_dir / "claims.csv").open()))
    papers = {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "per_paper").glob("*.json"))}
    strata = {"variant": [], "feature_observed": [], "feature_excluded": [], "demographic_inheritance": []}
    for n, (cid, c) in enumerate(claims.items()):
        if c["class"] == "bookkeeping":
            continue
        t, f = c["table"], c["field"]
        value = json.loads(c["value"]) if c["value"] else c["value"]
        if t == "variants" and f == "inheritance":
            strata["demographic_inheritance"].append(cid)
        elif t == "variants" and f not in ("individual_label_in_paper",):
            strata["variant"].append(cid)
        elif t == "phenotypic_features" and f == "status":
            strata["feature_observed" if value == "observed" else "feature_excluded"].append(cid)
        elif t == "individuals" and f in DEMOGRAPHIC:
            strata["demographic_inheritance"].append(cid)
    rng = random.Random(args.seed)
    want = {"variant": 20, "feature_observed": 10, "feature_excluded": 10, "demographic_inheritance": 10}
    picked = []
    for s, k in want.items():
        pool = sorted(strata[s])
        picked += [(s, cid) for cid in rng.sample(pool, min(k, len(pool)))]
    index = {f"C{i:06d}": sp for i, sp in enumerate(spans, 1)}
    out = []
    for n, (s, cid) in enumerate(picked, 1):
        c, sp = claims[cid], index[cid]
        rec = ((papers[c["pmid"]].get("tables") or {}).get(c["table"]) or [])[int(c["row"])]
        context = ""
        if c["table"] == "phenotypic_features":
            context = (rec.get("feature_text_as_stated") or {}).get("value", "")
        elif c["table"] == "variants":
            context = (rec.get("variant_original_string") or {}).get("value", "")
        out.append({"n": n, "claim_id": cid, "stratum": s, "pmid": c["pmid"],
                    "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{c['pmid']}/",
                    "individual": (rec.get("individual_label_in_paper") or {}).get("value", ""),
                    "context": context, "table": c["table"], "field": c["field"], "value": c["value"], "span": sp["span"],
                    "rating (supported / partially supported / unsupported)": "", "note": ""})
    dest = Path("adjudication/poc_audit")
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    key = {"run_id": args.run_id, "seed": args.seed, "pool_sizes": {k: len(v) for k, v in strata.items()},
           "drawn": {k: sum(1 for s, _ in picked if s == k) for k in want}, "claim_ids": [cid for _, cid in picked]}
    (dest / "sample_key.json").write_text(json.dumps(key, indent=2) + "\n")
    print(json.dumps({k: key[k] for k in ("pool_sizes", "drawn")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
