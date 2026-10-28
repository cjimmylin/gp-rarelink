"""Draw the locate-and-judge sample and the human audit sheets for the SLIDERS ablation (D-42, design §4.1, §4.3).

Two arms per disease, scored on the same papers:
  S  the SLIDERS-style run pv1-<disease>   (claims from its claims.csv and gatekeeper_v4_claims.csv)
  D  the direct run direct-<disease>       (claims from its converted per_paper/*.json)

Claim pool (the same rule for both arms, the pre-registration's O1 unit): one asserted value for one
person in the four person-level tables (individuals, variants, phenotypic_features, phenotype_checklist).
Not in the pool: bookkeeping fields (pmid; individual_label_in_paper outside the individuals table),
fields whose value comes from the schema or the extractor rather than the paper (checklist_feature,
evidence_basis, hpo_*_candidate), and missing values (null, "", "not reported", "unknown"). Arm S's pool
is its raw extraction, before the gatekeeper, because arm D's records are raw too.

Field groups: variant = any variants-table field; phenotype = phenotypic_features.status and
.feature_text_as_stated, phenotype_checklist.status; other = the remaining individuals-table fields.

Judge sample: per paper that both arms have output for, per arm, per group, up to --per-group claims
(default 2), simple random with the recorded seed. Both arms' claims for one paper go into one chunk
file with opaque ids and shuffled order, so the judge helper cannot tell the arms apart. Quotes are
not included (arm S's spans are hidden). The key (id -> arm, source claim, group, span) is written
apart from the chunks.

Audit sheets: --audit-n claims per arm per disease (default 50), simple random from the same pools with
a second seed (--audit-seed), independent of the judge draw, written as CSV sheets with the arm hidden
and a separate key. No rating page is built (no publishing, Jimmy, 2026-10-21).

  uv run python analysis/sliders_ablation/judge_sample.py --diseases ha20 ssadh --seed 42281 --audit-seed 42282
Writes adjudication/sliders_ablation/judge/chunks/<disease>_<pmid>.csv, judge_key.json, sample_summary.json,
adjudication/sliders_ablation/audit/sheet_<disease>.csv and audit_key.json. Refuses to overwrite a key.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import random
import subprocess
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TABLES = ("individuals", "variants", "phenotypic_features", "phenotype_checklist")
NOT_FROM_PAPER = {"checklist_feature", "evidence_basis", "hpo_label_candidate", "hpo_id_candidate"}
EMPTY = {None, "", "not reported", "unknown", "Not reported", "null", "[]"}


def group_of(table: str, field: str) -> str | None:
    if table == "variants":
        return "variant"
    if table == "phenotypic_features" and field in ("status", "feature_text_as_stated"):
        return "phenotype"
    if table == "phenotype_checklist" and field == "status":
        return "phenotype"
    if table == "individuals":
        return "other"
    return None  # other phenotypic_features fields (onset, detail) are not sampled


def cv(cell):
    return cell.get("value") if isinstance(cell, dict) else None


def spans(cell) -> str:
    s = cell.get("span") if isinstance(cell, dict) else None
    if s is None:
        return ""
    return " || ".join(x for x in (s if isinstance(s, list) else [s]) if isinstance(x, str))


def pool_from_tables(disease: str, run_id: str, arm: str) -> list[dict]:
    """Every poolable claim of a run, from its per_paper JSON (works for both arms)."""
    out = []
    for p in sorted((ROOT / "data/extracted" / disease / run_id / "per_paper").glob("*.json")):
        doc = json.loads(p.read_text())
        tables = doc.get("tables") or {}
        for table in TABLES:
            for i, row in enumerate(tables.get(table) or []):
                if not isinstance(row, dict):
                    continue
                label = cv(row.get("individual_label_in_paper"))
                context = ""
                if table == "phenotypic_features":
                    context = str(cv(row.get("feature_text_as_stated")) or "")
                elif table == "phenotype_checklist":
                    context = str(cv(row.get("checklist_feature")) or "")
                elif table == "variants":
                    context = str(cv(row.get("variant_original_string")) or "")
                for field, cell in row.items():
                    if field == "pmid" or (field == "individual_label_in_paper" and table != "individuals") or field in NOT_FROM_PAPER:
                        continue
                    value = cv(cell)
                    if value in EMPTY or (isinstance(value, str) and value.strip() in EMPTY):
                        continue
                    g = group_of(table, field)
                    if g is None:
                        continue
                    out.append({"arm": arm, "disease": disease, "run_id": run_id, "pmid": p.stem, "table": table, "row": i,
                                "field": field, "value": json.dumps(value, ensure_ascii=False), "individual": str(label or ""),
                                "context": context, "group": g, "span": spans(cell)})
    return out


def attach_gatekeeper_ids(pool: list[dict], disease: str, run_id: str) -> None:
    """For arm S, the claim id gatekeeper_v4_claims.csv gave the same (pmid, table, row, field)."""
    path = ROOT / "data/extracted" / disease / run_id / "gatekeeper_v4_claims.csv"
    if not path.exists():
        return
    ids = {(r["pmid"], r["table"], r["row"], r["field"]): r["claim_id"] for r in csv.DictReader(path.open())}
    for c in pool:
        c["source_claim_id"] = ids.get((c["pmid"], c["table"], str(c["row"]), c["field"]), "")


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diseases", nargs="+", default=["ha20", "ssadh"])
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--audit-seed", type=int, required=True)
    ap.add_argument("--per-group", type=int, default=2)
    ap.add_argument("--audit-n", type=int, default=50)
    ap.add_argument("--out-dir", default="adjudication/sliders_ablation")
    a = ap.parse_args(argv)
    out = ROOT / a.out_dir
    judge_dir, audit_dir = out / "judge", out / "audit"
    if (judge_dir / "judge_key.json").exists() or (audit_dir / "audit_key.json").exists():
        raise SystemExit("a sample already exists; refusing to overwrite its key")
    (judge_dir / "chunks").mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)
    rng, arng = random.Random(a.seed), random.Random(a.audit_seed)
    key, audit_key, summary = [], [], {"seed": a.seed, "audit_seed": a.audit_seed, "per_group": a.per_group, "audit_n": a.audit_n,
                                       "drawn_utc": datetime.now(UTC).isoformat(timespec="seconds"),
                                       "commit": subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, cwd=ROOT).stdout.strip(),
                                       "diseases": {}}
    n_id = 0
    for d in a.diseases:
        runs = {"S": f"pv1-{d}", "D": f"direct-{d}"}
        pools = {arm: pool_from_tables(d, run, arm) for arm, run in runs.items()}
        attach_gatekeeper_ids(pools["S"], d, runs["S"])
        papers = sorted(set(c["pmid"] for c in pools["S"]) & set(p.stem for p in (ROOT / "data/extracted" / d / runs["D"] / "per_paper").glob("*.json")))
        by = {arm: defaultdict(lambda: defaultdict(list)) for arm in runs}
        for arm, pool in pools.items():
            for c in pool:
                by[arm][c["pmid"]][c["group"]].append(c)
        drawn = Counter()
        chunk_rows = {}
        for pmid in papers:
            items = []
            for arm in runs:
                for g in ("variant", "phenotype", "other"):
                    cands = sorted(by[arm][pmid][g], key=lambda c: (c["table"], c["row"], c["field"]))
                    take = rng.sample(cands, min(a.per_group, len(cands)))
                    for c in take:
                        items.append(c)
                        drawn[(arm, g)] += 1
            rng.shuffle(items)
            rows = []
            for c in items:
                n_id += 1
                jid = f"J{hashlib.sha256(f'{a.seed}:{n_id}'.encode()).hexdigest()[:8]}"
                key.append({"judge_id": jid, "chunk": f"{d}_{pmid}", **{k: c[k] for k in ("arm", "disease", "run_id", "pmid", "table", "row", "field", "value", "individual", "context", "group", "span")},
                            "source_claim_id": c.get("source_claim_id", "")})
                rows.append({"claim_id": jid, "table": c["table"], "individual": c["individual"], "context": c["context"], "field": c["field"], "value": c["value"]})
            if rows:
                with (judge_dir / "chunks" / f"{d}_{pmid}.csv").open("w", newline="") as fh:
                    w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                    w.writeheader()
                    w.writerows(rows)
                chunk_rows[f"{d}_{pmid}"] = len(rows)
        # audit sheets: independent simple random draw per arm from the pools on the same papers
        sheet = []
        for arm, pool in pools.items():
            cands = sorted((c for c in pool if c["pmid"] in set(papers)), key=lambda c: (c["pmid"], c["table"], c["row"], c["field"]))
            for c in arng.sample(cands, min(a.audit_n, len(cands))):
                item = f"A{hashlib.sha256(f'{a.audit_seed}:{d}:{len(audit_key)}'.encode()).hexdigest()[:8]}"
                audit_key.append({"item_id": item, **{k: c[k] for k in ("arm", "disease", "run_id", "pmid", "table", "row", "field", "value", "individual", "context", "group", "span")},
                                  "source_claim_id": c.get("source_claim_id", "")})
                sheet.append({"item_id": item, "pmid": c["pmid"], "individual": c["individual"], "table": c["table"], "context": c["context"],
                              "field": c["field"], "value": c["value"], "rating (supported / unsupported / cannot verify)": "", "note": ""})
        arng.shuffle(sheet)
        with (audit_dir / f"sheet_{d}.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(sheet[0].keys()))
            w.writeheader()
            w.writerows(sheet)
        summary["diseases"][d] = {"papers_in_both_arms": len(papers), "pool_sizes": {arm: len(p) for arm, p in pools.items()},
                                  "pool_by_group": {arm: dict(Counter(c["group"] for c in p)) for arm, p in pools.items()},
                                  "judge_drawn": {f"{arm}:{g}": n for (arm, g), n in sorted(drawn.items())},
                                  "judge_chunks": len(chunk_rows), "judge_claims": sum(chunk_rows.values()),
                                  "audit_items": sum(1 for k in audit_key if k["disease"] == d),
                                  "inputs_sha256": {runs[arm]: sha(ROOT / "data/extracted" / d / runs[arm] / ("claims.csv" if arm == "S" else "conversion_summary.json"))
                                                    for arm in runs if (ROOT / "data/extracted" / d / runs[arm] / ("claims.csv" if arm == "S" else "conversion_summary.json")).exists()}}
    (judge_dir / "judge_key.json").write_text(json.dumps(key, indent=1, ensure_ascii=False) + "\n")
    (audit_dir / "audit_key.json").write_text(json.dumps(audit_key, indent=1, ensure_ascii=False) + "\n")
    (out / "sample_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps({d: {k: v for k, v in s.items() if k != "inputs_sha256"} for d, s in summary["diseases"].items()}, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
