"""Draw the pre-registered 250-claim audit sample (O1, pre-registration §7.1; D-35, D-40).

Claim pool: every value asserted in the final (post-gatekeeper) records across the six
diseases, at atomic level. Operationally, for each run pv1-<disease>:
  - claims from gatekeeper_v4.csv with class 'model' (bookkeeping fields such as pmid and
    repeated labels are not values about a person);
  - verdict 'supported' (the records leave out every claim the gatekeeper did not judge
    supported: to_phenopackets --gatekeeper not_supported);
  - a value that is not empty, null, 'not reported' or 'unknown' ("not reported" outputs
    carry no span and are not in the pool).
The unit is the extracted value with its quoted span (e.g. a phenotypic feature's status
for one person, one variant field, sex, an onset age). HPO term choice is checked
separately (bindings), as in the pilot.

Sample: 250 claims, simple random sampling stratified by disease in proportion to pool
size (largest-remainder allocation), with a recorded seed. Run once, after all six runs
are complete and before any concordance result for them is looked at.

Writes adjudication/o1_audit/sample.csv (for raters: no gatekeeper verdict or reason) and
adjudication/o1_audit/sample_key.json (seed, pool sizes, allocation, claim ids, input
sha256). Refuses to overwrite an existing sample.

  uv run python analysis/six_disease/make_audit_sample.py --seed 40250
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
from datetime import UTC, datetime
from pathlib import Path

DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
EMPTY = {"", "null", '""', '"not reported"', '"unknown"', "[]", '"Not reported"'}
N = 250


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--out-dir", default="adjudication/o1_audit")
    a = ap.parse_args(argv)
    dest = Path(a.out_dir)
    if (dest / "sample_key.json").exists():
        raise SystemExit(f"{dest}/sample_key.json exists; the audit sample is drawn once")
    pools, inputs = {}, {}
    for d in DISEASES:
        run = Path(f"data/extracted/{d}/pv1-{d}")
        gk = run / "gatekeeper_v4.csv"
        inputs[str(gk)] = sha(gk)
        pools[d] = sorted(r["claim_id"] for r in csv.DictReader(gk.open())
                          if r["class"] == "model" and r["verdict"] == "supported" and r["value"].strip() not in EMPTY)
    total = sum(len(p) for p in pools.values())
    quota = {d: N * len(p) / total for d, p in pools.items()}
    alloc = {d: int(q) for d, q in quota.items()}
    for d in sorted(quota, key=lambda d: (quota[d] - alloc[d], d), reverse=True)[: N - sum(alloc.values())]:
        alloc[d] += 1
    rng = random.Random(a.seed)
    picked = [(d, cid) for d in DISEASES for cid in sorted(rng.sample(pools[d], alloc[d]))]
    rng.shuffle(picked)  # raters see diseases mixed
    rows = []
    for n, (d, cid) in enumerate(picked, 1):
        run = Path(f"data/extracted/{d}/pv1-{d}")
        g = next(r for r in csv.DictReader((run / "gatekeeper_v4.csv").open()) if r["claim_id"] == cid)
        sp = list(csv.DictReader((run / "claims.csv").open()))[int(cid[1:]) - 1]
        assert (sp["pmid"], sp["table"], sp["row"], sp["field"]) == (g["pmid"], g["table"], g["row"], g["field"]), cid
        rec = ((json.loads((run / "per_paper" / f"{g['pmid']}.json").read_text()).get("tables") or {}).get(g["table"]) or [])[int(g["row"])]
        context = ""
        if g["table"] in ("phenotypic_features",):
            context = (rec.get("feature_text_as_stated") or {}).get("value", "")
        elif g["table"] == "phenotype_checklist":
            context = (rec.get("checklist_feature") or {}).get("value", "")
        elif g["table"] == "variants":
            context = (rec.get("variant_original_string") or {}).get("value", "")
        rows.append({"n": n, "item_id": f"O1-{n:03d}", "disease": d, "pmid": g["pmid"],
                     "pubmed": f"https://pubmed.ncbi.nlm.nih.gov/{g['pmid']}/",
                     "paper_text": f"data/literature/{d}/fulltext_md/{g['pmid']}.md",
                     "individual": (rec.get("individual_label_in_paper") or {}).get("value", ""),
                     "context": context, "table": g["table"], "field": g["field"], "value": g["value"], "span": sp["span"]})
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    key = {"drawn_utc": datetime.now(UTC).isoformat(timespec="seconds"), "seed": a.seed, "n": N,
           "commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
           "pool_rule": "gatekeeper_v4 class=model, verdict=supported, value not empty/null/not reported/unknown",
           "pool_sizes": {d: len(p) for d, p in pools.items()}, "pool_total": total, "allocation": alloc,
           "inputs_sha256": inputs, "items": [{"item_id": r["item_id"], "disease": d, "claim_id": cid}
                                               for r, (d, cid) in zip(rows, picked)]}
    (dest / "sample_key.json").write_text(json.dumps(key, indent=2) + "\n")
    print(json.dumps({k: key[k] for k in ("seed", "pool_sizes", "pool_total", "allocation")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
