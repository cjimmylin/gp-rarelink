"""D-47 addendum batch 2: review checks on the committed pv1a2 outputs (2026-11-15).

Reads only committed run outputs, plus the git-ignored Markdown when it is present.
Writes:
  analysis/corpus/free_copies/batch2_review_<date>.json       the numbers below
  analysis/corpus/free_copies/batch2_audit_list_<date>.csv    claims for the human audit

What it computes:
1. Gatekeeper `about` against `verdict`. Gatekeeper v4 says a quote about another person or
   about the cohort in general makes the value unsupported; helpers sometimes record that
   `about` and still judge "partially_supported". The strict count treats those as unsupported.
2. What the phenopackets hold: how many carry a disease, an interpretation, any phenotypic
   feature, or nothing but identity fields; the same for the registered (pv1) and batch-1 (pv1a)
   runs for comparison; and the observed/excluded conflicts to_phenopackets resolved.
3. Papers with no variant row.
4. The share of each paper's converted text that the committed verbatim quotes reproduce
   (only when data/literature/<d>/fulltext_md/<pmid>.md exists; whitespace-normalized).
5. The audit list: softened verdicts, and claims whose gatekeeper reason notes that the paper
   contradicts itself.
6. For comparison, the as-judged and strict unsupported shares of the registered (pv1) and
   batch-1 (pv1a) runs from their merged gatekeeper_v4.csv files, and how many batch-2 records
   without a disease term carry a relative's label (a rough pattern match on the label).

  python3 -I analysis/corpus/free_copies/batch2_review.py --date 2026-11-15
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import statistics
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DISEASES = ["ha20", "axd", "danon", "lad1", "ssadh", "tangier"]
SOFT_ABOUT = {"other_person", "cohort_general"}
UNSUPPORTED = {"unsupported", "span_not_found"}
CONTRA = re.compile(r"contradict|conflict|inconsisten", re.I)
RELATIVE = re.compile(r"mother|father|parent|sibling|sister|brother|son |son$|daughter|uncle|aunt|grand|nephew|relative|^(IV|V|VI)\d|VI-|^\d{3}$", re.I)


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s)


def spans_of(x, out: set) -> None:
    if isinstance(x, dict):
        sp = x.get("span")
        if isinstance(sp, str):
            out.add(sp)
        elif isinstance(sp, list):
            out.update(s for s in sp if isinstance(s, str))
        for v in x.values():
            spans_of(v, out)
    elif isinstance(x, list):
        for v in x:
            spans_of(v, out)


def packets(run_dir: Path) -> Counter:
    c = Counter()
    for f in run_dir.glob("phenopackets/*.json"):
        p = json.loads(f.read_text())
        feats = p.get("phenotypicFeatures", [])
        c["phenopackets"] += 1
        c["with_disease"] += bool(p.get("diseases"))
        c["with_interpretation"] += bool(p.get("interpretations"))
        c["no_phenotypic_feature"] += not feats
        c["identity_only"] += (not feats) and not p.get("interpretations")
    return c


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    names = {r["pmid"]: r["file_name"] for r in csv.DictReader((ROOT / "analysis/corpus/free_copies/hand_fetched_2026-11-14.csv").open())}
    gk, audit, per_disease, novar, coverage, nodisease = Counter(), [], {}, {}, [], Counter()
    for d in DISEASES:
        run = ROOT / f"data/extracted/{d}/pv1a2-{d}"
        n = u = s = 0
        for f in sorted((run / "gatekeeper_v4").glob("*.csv")):
            for r in csv.DictReader(f.open()):
                gk[f"{r['about']}|{r['verdict']}"] += 1
                n += 1
                uns = r["verdict"] in UNSUPPORTED
                soft = r["about"] in SOFT_ABOUT and not uns
                u += uns
                s += soft
                why = "softened: about another person or the cohort, not judged unsupported" if soft else (
                    "paper contradicts itself (gatekeeper note)" if CONTRA.search(r.get("reason") or "") else None)
                if why:
                    audit.append({"disease": d, "chunk": f.stem, "claim_id": r["claim_id"], "about": r["about"],
                                  "verdict": r["verdict"], "why_listed": why, "gatekeeper_reason": r.get("reason") or ""})
        build = json.loads((run / "phenopacket_build.json").read_text())
        rec = list(csv.DictReader((run / "individuals_reconciled.csv").open()))
        idcol = next(c for c in rec[0] if "identity" in c.lower())
        label = {r[idcol]: r["individual_label_in_paper"] for r in rec}
        for f in run.glob("phenopackets/*.json"):
            p = json.loads(f.read_text())
            if not p.get("diseases"):
                nodisease["records_without_disease"] += 1
                nodisease["of_which_relative_label"] += bool(RELATIVE.search(label.get(p["subject"]["id"], "")))
        per_disease[d] = {"judged": n, "unsupported": u, "softened": s, "unsupported_strict": u + s,
                          "share": round(u / n, 4), "share_strict": round((u + s) / n, 4),
                          "packets": dict(packets(run)),
                          "observed_excluded_conflicts": build.get("observed_excluded_conflicts")}
        nv = []
        for f in sorted((run / "per_paper").glob("*.json")):
            doc = json.loads(f.read_text())
            if not doc["tables"].get("variants"):
                nv.append({"pmid": f.stem, "file_name": names.get(f.stem, "")})
            md = ROOT / f"data/literature/{d}/fulltext_md/{f.stem}.md"
            if md.exists():
                text = norm(md.read_text())
                sp: set = set()
                spans_of(doc, sp)
                cov = bytearray(len(text))
                for q in sp:
                    q = norm(q)
                    if len(q) < 3:
                        continue
                    i = text.find(q)
                    while i != -1:
                        cov[i:i + len(q)] = b"\x01" * len(q)
                        i = text.find(q, i + 1)
                coverage.append({"disease": d, "pmid": f.stem, "share_of_text_quoted": round(sum(cov) / len(text), 3), "text_chars": len(text)})
        novar[d] = nv
    by_run = {}
    for run_prefix in ("pv1", "pv1a", "pv1a2"):
        c = Counter()
        for d in DISEASES:
            c.update(packets(ROOT / f"data/extracted/{d}/{run_prefix}-{d}"))
        by_run[run_prefix] = dict(c)
    earlier = {}
    for run_prefix in ("pv1", "pv1a"):
        n = u = s = 0
        for d in DISEASES:
            f = ROOT / f"data/extracted/{d}/{run_prefix}-{d}/gatekeeper_v4.csv"
            if not f.exists():
                continue
            for r in csv.DictReader(f.open()):
                v = r.get("verdict") or ""
                if v in ("", "not_judged"):
                    continue
                uns = v in UNSUPPORTED
                n += 1
                u += uns
                s += r.get("about") in SOFT_ABOUT and not uns
        earlier[run_prefix] = {"judged": n, "unsupported": u, "softened": s, "share": round(u / n, 4), "share_strict": round((u + s) / n, 4)}
    tot = {k: sum(per_disease[d][k] for d in DISEASES) for k in ("judged", "unsupported", "softened", "unsupported_strict")}
    shares = sorted(x["share_of_text_quoted"] for x in coverage)
    out = {
        "date": a.date,
        "gatekeeper_about_by_verdict": dict(sorted(gk.items())),
        "gatekeeper_totals": {**tot, "share": round(tot["unsupported"] / tot["judged"], 4), "share_strict": round(tot["unsupported_strict"] / tot["judged"], 4)},
        "gatekeeper_earlier_runs": earlier,
        "records_without_disease": dict(nodisease),
        "per_disease": per_disease,
        "phenopacket_content_by_run": by_run,
        "observed_excluded_conflicts_total": sum(per_disease[d]["observed_excluded_conflicts"] or 0 for d in DISEASES),
        "papers_without_variant_rows": novar,
        "papers_without_variant_rows_total": sum(len(v) for v in novar.values()),
        "quote_coverage": {"papers": len(coverage), "median": statistics.median(shares) if shares else None,
                           "max": shares[-1] if shares else None, "papers_at_or_above_0_3": sum(x >= 0.3 for x in shares),
                           "top": sorted(coverage, key=lambda x: -x["share_of_text_quoted"])[:8]},
        "audit_list_rows": len(audit), "audit_list_by_reason": dict(Counter(r["why_listed"] for r in audit)),
    }
    (ROOT / f"analysis/corpus/free_copies/batch2_review_{a.date}.json").write_text(json.dumps(out, indent=1) + "\n")
    with (ROOT / f"analysis/corpus/free_copies/batch2_audit_list_{a.date}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["disease", "chunk", "claim_id", "about", "verdict", "why_listed", "gatekeeper_reason"])
        w.writeheader()
        w.writerows(audit)
    print(json.dumps({k: out[k] for k in ("gatekeeper_totals", "gatekeeper_earlier_runs", "records_without_disease", "phenopacket_content_by_run", "observed_excluded_conflicts_total",
                                           "papers_without_variant_rows_total", "audit_list_rows", "audit_list_by_reason")}, indent=1))
    print(json.dumps({d: {k: per_disease[d][k] for k in ("judged", "unsupported", "unsupported_strict", "share_strict")} | per_disease[d]["packets"] for d in DISEASES}, indent=0))
    print(json.dumps(out["quote_coverage"])[:600])


if __name__ == "__main__":
    main()
