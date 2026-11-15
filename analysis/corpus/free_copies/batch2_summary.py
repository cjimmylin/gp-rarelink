"""D-47 addendum batch 2: summary of screening, extraction, gatekeeper and Stage 4 for the pv1a2 runs.

A copy of batch1_summary.py with the batch-2 paths: screening decisions in
data/literature/<d>/addendum_d47/batch2/screening.csv, runs data/extracted/<d>/pv1a2-<d>/,
papers received from analysis/corpus/free_copies/hand_fetched_2026-11-14.csv, and Danon added.
It also prints batch 1 + batch 2 phenopacket totals from batch1_summary_<date>.json.
Writes analysis/corpus/free_copies/batch2_summary_<date>.json and the numbers block of
reports/addendum_d47_batch2_findings.md (narrative sections are kept, not regenerated).

  python3 -I analysis/corpus/free_copies/batch2_summary.py --date 2026-11-15
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DISEASES = [("ha20", "A20 haploinsufficiency"), ("axd", "Alexander disease"), ("danon", "Danon disease"),
            ("lad1", "LAD-I"), ("ssadh", "SSADH deficiency"), ("tangier", "Tangier disease")]


def load(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def rejudge(run: Path) -> dict:
    aside = run / "gatekeeper_v4_set_aside"
    out = {"chunks": 0, "claims": 0, "agree": 0, "disagreements": []}
    if not aside.exists():
        return out
    for f in sorted(aside.glob("*.first_attempt.csv")):
        chunk = f.name.replace(".first_attempt.csv", "")
        a = {r["claim_id"]: r["verdict"] for r in csv.DictReader(f.open())}
        b = {r["claim_id"]: r["verdict"] for r in csv.DictReader((run / "gatekeeper_v4" / f"{chunk}.csv").open())}
        out["chunks"] += 1
        out["claims"] += len(b)
        out["agree"] += sum(a.get(k) == v for k, v in b.items())
        out["disagreements"] += [{"chunk": chunk, "claim_id": k, "first": a.get(k), "record": v} for k, v in b.items() if a.get(k) != v]
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    reg4 = load(ROOT / "analysis/six_disease/stage4_summary_2026-10-28.json")
    reg4 = {r["disease"]: r for r in reg4["diseases"]} if reg4 else {}
    received = list(csv.DictReader((ROOT / "analysis/corpus/free_copies/hand_fetched_2026-11-14.csv").open()))
    rows = []
    for d, name in DISEASES:
        scr = list(csv.DictReader((ROOT / f"data/literature/{d}/addendum_d47/batch2/screening.csv").open()))
        assert len(scr) == sum(r["disease"] == d for r in received), d
        run = ROOT / f"data/extracted/{d}/pv1a2-{d}"
        sc, gk = load(run / "span_check.json"), load(run / "gatekeeper_v4_summary.json")
        rc, nm = load(run / "reconcile_summary.json"), load(run / "normalization_summary.json")
        bd, pb, vr = load(run / "binding_summary.json"), load(run / "phenopacket_build.json"), load(run / "validation_report.json")
        man = load(ROOT / f"runs/pv1-{d}/manifest.json")
        res = man.get("results")
        res = eval(res) if isinstance(res, str) else (res or {})  # noqa: S307 (the manifest stores a repr)
        g = gk["rates_model_claims"]
        rows.append({
            "disease": d, "name": name,
            "fetched": len(scr), "included": sum(r["decision"] == "include" for r in scr),
            "excluded": {r["pmid"]: r["exclusion_reason"] for r in scr if r["decision"] == "exclude"},
            "papers_extracted": sc["n_papers"], "values_quoted": sc["counts"]["values_asserted"],
            "span_found_rate": sc["span_found_rate"], "span_problems": sc["n_problems"],
            "individual_rows": rc["individuals_before_merging"], "identities": rc["identities_after_merging"],
            "gk_judged": g["judged"], "gk_unsupported": g["unsupported_or_not_found"]["k"],
            "gk_unsupported_share": g["unsupported_or_not_found"]["share"], "gk_unsupported_ci95": g["unsupported_or_not_found"]["ci95"],
            "gk_not_supported_share": g["not_supported"]["share"], "gk_verdicts": gk["verdicts"],
            "rejudged": rejudge(run),
            "variant_descriptions": nm["distinct_descriptions"], "variant_status": nm["status_counts"],
            "feature_rows": bd["feature_rows"], "feature_share_bound": bd["feature_share_bound"],
            "phenopackets": pb["counts"].get("phenopackets"), "with_interpretation": pb["counts"].get("with_interpretation"),
            "features_observed": pb["counts"].get("features_observed"), "features_excluded": pb["counts"].get("features_excluded"),
            "schema_valid": vr["schema_valid"], "validation_errors": len(vr["errors"]),
            "registered": {"documents": man["n_documents"], "unsupported_share": res.get("unsupported_share"),
                           "unsupported_ci95": res.get("unsupported_ci95"),
                           "phenopackets": reg4.get(d, {}).get("phenopackets"),
                           "with_interpretation": reg4.get(d, {}).get("with_interpretation")},
        })
    out = ROOT / f"analysis/corpus/free_copies/batch2_summary_{a.date}.json"
    out.write_text(json.dumps({"date": a.date, "diseases": rows}, indent=1) + "\n")

    def pct(x):
        return f"{100 * x:.1f}%"
    L = ["<!-- numbers: generated by analysis/corpus/free_copies/batch2_summary.py; do not edit by hand -->", "",
         "### Screening and extraction", "",
         "| Disease | Free copies received | Included after full-text screening | Excluded (reason) | Values quoted, all verbatim | Individual rows |",
         "|---|---|---|---|---|---|"]
    for r in rows:
        exc = "; ".join(f"{p} ({why})" for p, why in r["excluded"].items()) or "none"
        L.append(f"| {r['name']} | {r['fetched']} | {r['included']} | {exc} | {r['values_quoted']} ({pct(r['span_found_rate'])}) | {r['individual_rows']} |")
    t = {k: sum(r[k] for r in rows) for k in ("fetched", "included", "values_quoted", "individual_rows")}
    L.append(f"| **Total** | **{t['fetched']}** | **{t['included']}** | | **{t['values_quoted']}** | **{t['individual_rows']}** |")
    L += ["", "### Gatekeeper v4 (model-judged claims)", "",
          "| Disease | Judged | Unsupported | Share (exact 95% CI) | Not fully supported | Registered pv1 unsupported share (95% CI) |",
          "|---|---|---|---|---|---|"]
    for r in rows:
        rg = r["registered"]
        L.append(f"| {r['name']} | {r['gk_judged']} | {r['gk_unsupported']} | {pct(r['gk_unsupported_share'])} "
                 f"({pct(r['gk_unsupported_ci95'][0])}–{pct(r['gk_unsupported_ci95'][1])}) | {pct(r['gk_not_supported_share'])} | "
                 f"{pct(rg['unsupported_share'])} ({pct(rg['unsupported_ci95'][0])}–{pct(rg['unsupported_ci95'][1])}) |")
    j = sum(r["gk_judged"] for r in rows)
    u = sum(r["gk_unsupported"] for r in rows)
    L.append(f"| **Total** | **{j}** | **{u}** | **{pct(u / j)}** | | |")
    rj = [r["rejudged"] for r in rows]
    L += ["", f"Chunks judged twice (see *Gatekeeper write refusals*): {sum(x['chunks'] for x in rj)} chunks, "
          f"{sum(x['claims'] for x in rj)} claims, verdicts agree on {sum(x['agree'] for x in rj)}. "
          "The second judgment is the record in every case.", "",
          "### Stage 4", "",
          "| Disease | Identities | Variant descriptions (normalized) | Phenotype rows bound to HPO | Phenopackets (with interpretation) | Schema-valid | Registered pv1 phenopackets (with interpretation) |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        st = r["variant_status"]
        nrm = st.get("normalized", 0) + st.get("corrected", 0)
        rg = r["registered"]
        L.append(f"| {r['name']} | {r['identities']} | {r['variant_descriptions']} ({nrm}) | {pct(r['feature_share_bound'])} of {r['feature_rows']} | "
                 f"{r['phenopackets']} ({r['with_interpretation']}) | {r['schema_valid']}, {r['validation_errors']} errors | {rg['phenopackets']} ({rg['with_interpretation']}) |")
    p = sum(r["phenopackets"] for r in rows)
    wi = sum(r["with_interpretation"] for r in rows)
    L.append(f"| **Total** | **{sum(r['identities'] for r in rows)}** | | | **{p} ({wi})** | | |")
    b1 = load(ROOT / f"analysis/corpus/free_copies/batch1_summary_{a.date}.json")
    if b1:
        p1 = sum(r["phenopackets"] for r in b1["diseases"])
        w1 = sum(r["with_interpretation"] for r in b1["diseases"])
        L += ["", f"Addendum so far (batch 1 + batch 2): {p1} + {p} = {p1 + p} phenopackets, "
              f"{w1} + {wi} = {w1 + wi} with an interpretation (batch 1 from batch1_summary_{a.date}.json)."]
    L.append("")
    L.append("<!-- /numbers -->")
    rep = ROOT / "reports/addendum_d47_batch2_findings.md"
    text = rep.read_text() if rep.exists() else "<!-- numbers --><!-- /numbers -->\n"
    start = text.index("<!-- numbers")
    end = text.index("<!-- /numbers -->") + len("<!-- /numbers -->")
    rep.write_text(text[:start] + "\n".join(L) + text[end:])
    print(json.dumps({"phenopackets": p, "with_interpretation": wi, "judged": j, "unsupported": u}))


if __name__ == "__main__":
    main()
