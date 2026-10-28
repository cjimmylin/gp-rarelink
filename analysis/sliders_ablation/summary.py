"""SLIDERS ablation (D-44): arm S (pv1-<d>, SLIDERS-style) against arm D (direct-<d>) per disease.

Reads both arms' per-paper tables on the papers both have, plus the harness outputs made for this
study, and writes analysis/sliders_ablation/summary_<d>.json and summary.md. Measures follow
reports/sliders_ablation_design.md §4:

  structure      arm D's conversion counts (records that parse, fields filled, enum values outside
                 the schema); arm S's span-check problem count (0 at the run of record).
  coverage       individuals, variant rows, distinct target-gene variant keys (protein level, as the
                 D-10 comparison), feature rows, checklist cells by state (observed / excluded / not
                 reported) and the excluded share.
  agreement      per paper, target-gene variant keys shared / union; checklist status agreement on
                 cells both arms have for the same (label, item); label sets (Jaccard, pooled);
                 papers with the same individual count.
  grounding      the share of asserted values found verbatim (whitespace, case, markup and NFKC
                 folded) in the paper text, by field group: variant descriptions on target-gene
                 rows, feature text, ages as written, disease label. Arm S's values carry a quote
                 each, so its rates are near 1 by construction; arm D's measure literal fidelity.
  cost and time  arm D from analysis/sliders_ablation/helper_stats.json (this session's helper
                 transcripts; $5.996 per weighted million); arm S from
                 analysis/openweight/claude_helper_stats.json (the pv1 helpers), plus its gatekeeper
                 pass at $0.0044 per judged claim. Estimates, not invoices.
  concordance    analysis/sliders_ablation/o2/<arm>/o2_<d>.json, both arms on the 2026-10-28 snapshot
                 (pipeline/harness/concordance_o2.py --run-prefix pv1|direct --out ...).
  completeness   analysis/sliders_ablation/completeness_<run>.json (HA20, Chen 2020 Table S1).
  reconciliation data/extracted/<d>/<run>/reconcile_summary.json; normalization_summary.json.
  judge          analysis/sliders_ablation/judge_summary.json (judge_merge.py).

  uv run python analysis/sliders_ablation/summary.py --diseases ha20 ssadh
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
import unicodedata
from collections import Counter
from pathlib import Path

from pipeline.extract.normalize_variants import is_gene, protein_key
from pipeline.harness.concordance import protein_short, wilson

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "analysis/sliders_ablation"
RATE = 5.996
GATEKEEPER_PER_CLAIM = 0.0044
MISSING = (None, "", "not reported", "not stated", "unknown")
WS, MARKUP = re.compile(r"\s+"), re.compile(r"[*_`|#]")
GROUNDING_FIELDS = {
    "variant descriptions (target gene)": ("variants", ("variant_original_string", "cdna_hgvs_as_stated", "protein_hgvs_as_stated", "transcript_as_stated")),
    "feature text": ("phenotypic_features", ("feature_text_as_stated",)),
    "ages as written": ("individuals", ("age_at_onset_original_text", "age_at_diagnosis_original_text", "age_at_last_evaluation_original_text")),
    "disease label": ("individuals", ("disease_label_as_stated",)),
    "variant pathogenicity as stated": ("variants", ("pathogenicity_as_stated_by_authors",)),
}


def norm(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s)).lower().replace("&gt;", ">").replace("&lt;", "<")
    return WS.sub(" ", MARKUP.sub(" ", s)).strip()


def cv(cell):
    return cell.get("value") if isinstance(cell, dict) else None


def j(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def tables(d: str, run: str, pmid: str):
    p = ROOT / f"data/extracted/{d}/{run}/per_paper/{pmid}.json"
    try:
        return json.loads(p.read_text()).get("tables") or {}
    except (OSError, json.JSONDecodeError):
        return None


def rows(t, name):
    return [r for r in (t.get(name) or []) if isinstance(r, dict)]


def vkeys(t, gene):
    out = set()
    for r in rows(t, "variants"):
        if is_gene(cv(r.get("gene_symbol_as_stated")), gene):
            for f in ("protein_hgvs_as_stated", "variant_original_string"):
                k = protein_key(cv(r.get(f)))
                if k:
                    out.add(protein_short(k))
    return out


def label_key(s) -> str:
    return WS.sub(" ", str(s or "")).strip().lower()


def checklist(t):
    return {(label_key(cv(r.get("individual_label_in_paper"))), str(cv(r.get("checklist_feature")))): str(cv(r.get("status")))
            for r in rows(t, "phenotype_checklist")}


def coverage(ts, gene):
    out, states = Counter(), Counter()
    for t in ts:
        out["individuals"] += len(rows(t, "individuals"))
        out["variant_rows"] += len(rows(t, "variants"))
        out["target_gene_variant_rows"] += sum(1 for r in rows(t, "variants") if is_gene(cv(r.get("gene_symbol_as_stated")), gene))
        out["target_gene_variant_keys"] += len(vkeys(t, gene))
        out["phenotypic_feature_rows"] += len(rows(t, "phenotypic_features"))
        out["feature_rows_observed"] += sum(1 for r in rows(t, "phenotypic_features") if cv(r.get("status")) == "observed")
        out["feature_rows_excluded"] += sum(1 for r in rows(t, "phenotypic_features") if cv(r.get("status")) == "excluded")
        states.update(checklist(t).values())
    cells = sum(states.values())
    res = dict(out)
    res["checklist_cells"] = cells
    res["checklist_by_state"] = {k: states.get(k, 0) for k in ("observed", "excluded", "not reported")}
    res["checklist_excluded_share"] = wilson(states.get("excluded", 0), cells) if cells else None
    res["checklist_not_reported_share"] = wilson(states.get("not reported", 0), cells) if cells else None
    return res


def grounding(d: str, pairs, arm_index: int, gene: str):
    res = {}
    for name, (table, fields) in GROUNDING_FIELDS.items():
        k = n = 0
        for pmid, *arms in pairs:
            t = arms[arm_index]
            text = norm((ROOT / f"data/literature/{d}/fulltext_md/{pmid}.md").read_text())
            for r in rows(t, table):
                if table == "variants" and not is_gene(cv(r.get("gene_symbol_as_stated")), gene):
                    continue
                for f in fields:
                    v = cv(r.get(f))
                    if v in MISSING or not isinstance(v, str) or not v.strip():
                        continue
                    n += 1
                    k += norm(v) in text
        res[name] = wilson(k, n)
    return res


def costs(d: str, run: str, pmids: list[str], stats_rows: list[dict]) -> dict:
    per_paper_cost, per_paper_wall, helpers = Counter(), Counter(), Counter()
    for r in stats_rows:
        if r.get("run") == run and r.get("pmid") in pmids:
            per_paper_cost[r["pmid"]] += r["weighted_tokens"] / 1e6 * RATE
            per_paper_wall[r["pmid"]] += r.get("wall_seconds") or 0
            helpers[r["pmid"]] += 1
    med = lambda xs: round(statistics.median(xs), 4) if xs else None
    return {"papers_with_stats": len(per_paper_cost), "helpers": sum(helpers.values()),
            "cost_total_usd": round(sum(per_paper_cost.values()), 2), "cost_median_per_paper_usd": med(list(per_paper_cost.values())),
            "wall_total_seconds": round(sum(per_paper_wall.values())), "wall_median_per_paper_seconds": med([x for x in per_paper_wall.values() if x])}


def one(d: str, direct_stats: list[dict], s_stats: list[dict]) -> dict:
    gene = json.loads((ROOT / f"configs/stage4/{d}.json").read_text())["gene"]
    S, D = f"pv1-{d}", f"direct-{d}"
    pmids = sorted(p.stem for p in (ROOT / f"data/extracted/{d}/{D}/per_paper").glob("*.json"))
    pairs = [(p, tables(d, S, p), tables(d, D, p)) for p in pmids]
    pairs = [(p, s, t) for p, s, t in pairs if s is not None and t is not None]
    used = [p for p, _, _ in pairs]
    shared_v = union_v = only_s = only_d = 0
    cl_shared = cl_agree = 0
    cl_cross = Counter()
    lab_shared = lab_union = 0
    same_n = 0
    for _, s, t in pairs:
        vs, vd = vkeys(s, gene), vkeys(t, gene)
        shared_v += len(vs & vd); union_v += len(vs | vd); only_s += len(vs - vd); only_d += len(vd - vs)
        cs, cd = checklist(s), checklist(t)
        sh = set(cs) & set(cd)
        cl_shared += len(sh); cl_agree += sum(cs[k] == cd[k] for k in sh)
        cl_cross.update(f"S={cs[k]}|D={cd[k]}" for k in sh if cs[k] != cd[k])
        ls, ld = {label_key(cv(r.get("individual_label_in_paper"))) for r in rows(s, "individuals")}, {label_key(cv(r.get("individual_label_in_paper"))) for r in rows(t, "individuals")}
        lab_shared += len(ls & ld); lab_union += len(ls | ld)
        same_n += len(rows(s, "individuals")) == len(rows(t, "individuals"))
    conv = j(ROOT / f"data/extracted/{d}/{D}/conversion_summary.json") or {}
    sc = j(ROOT / f"data/extracted/{d}/{S}/span_check.json") or {}
    gk = j(ROOT / f"data/extracted/{d}/{S}/gatekeeper_v4_summary.json") or {}
    judged = (gk.get("rates_model_claims") or {}).get("judged")  # model-class claims the gatekeeper judged
    if not isinstance(judged, int):
        judged = sum(v for k, v in (gk.get("verdicts") or {}).items() if k != "not_judged") or None
    s_cost = costs(d, S, used, s_stats)
    s_cost["gatekeeper_claims_judged"] = judged
    s_cost["gatekeeper_cost_usd_estimate"] = round(judged * GATEKEEPER_PER_CLAIM, 2) if isinstance(judged, int) else None
    s_cost["cost_total_with_gatekeeper_usd"] = round(s_cost["cost_total_usd"] + (s_cost["gatekeeper_cost_usd_estimate"] or 0), 2)
    o2 = {arm: j(OUT / f"o2/{arm}/o2_{d}.json") for arm in ("pv1", "direct")}
    comp = {arm: j(OUT / f"completeness_{run}.json") for arm, run in (("S", S), ("D", D))}
    rec = {arm: j(ROOT / f"data/extracted/{d}/{run}/reconcile_summary.json") for arm, run in (("S", S), ("D", D))}
    nrm = {arm: j(ROOT / f"data/extracted/{d}/{run}/normalization_summary.json") for arm, run in (("S", S), ("D", D))}
    judge = (j(OUT / "judge_summary.json") or {}).get("diseases", {}).get(d)

    def o2pick(x):
        if not x:
            return None
        a = x["all_papers"]
        return {"hgvs_recall_tier1": a["hgvs_recall_tier1"], "hgvs_recall_tier12": a["hgvs_recall_tier12"], "reference_pairs": a["reference_pairs"],
                "overlap_tier1": a["overlap_tier1"], "classification_agreement": a["classification_agreement_among_stated"],
                "condition_names_disease": a["condition_names_disease"], "gap_candidates_tier1_unmatched": a["gap_candidates_tier1_unmatched"],
                "overlap_tier1_without_clinvar_cited_papers": x["without_clinvar_cited_papers_D19"]["overlap_tier1"],
                "normalization": x.get("normalization_7_2_2"), "snapshot_date": x.get("snapshot_date"),
                "clinvar_last_modified": x.get("clinvar_variant_summary_last_modified")}

    return {"disease": d, "gene": gene, "runs": {"S": S, "D": D}, "papers_compared": len(used), "papers_in_direct_run": len(pmids),
            "structure": {"D_conversion": {k: v for k, v in (conv.get("counts") or {}).items() if not k.startswith(("filled:", "unknown:", "enum_outside:"))},
                          "D_enum_outside_by_field": {k.split(":", 1)[1]: v for k, v in (conv.get("counts") or {}).items() if k.startswith("enum_outside:")},
                          "S_span_check_problems": sc.get("n_problems"), "S_values_asserted": (sc.get("counts") or {}).get("values_asserted")},
            "coverage": {"S": coverage([s for _, s, _ in pairs], gene), "D": coverage([t for _, _, t in pairs], gene)},
            "agreement": {"variant_keys": {"shared": shared_v, "union": union_v, "S_only": only_s, "D_only": only_d,
                                           "jaccard_pooled": round(shared_v / union_v, 4) if union_v else None},
                          "checklist": {"cells_shared": cl_shared, "status_agreement": round(cl_agree / cl_shared, 4) if cl_shared else None,
                                        "disagreements": dict(cl_cross.most_common())},
                          "labels": {"shared": lab_shared, "union": lab_union, "jaccard_pooled": round(lab_shared / lab_union, 4) if lab_union else None},
                          "papers_same_individual_count": same_n},
            "grounding": {"S": grounding(d, pairs, 0, gene), "D": grounding(d, pairs, 1, gene)},
            "cost_time": {"S": s_cost, "D": costs(d, D, used, direct_stats)},
            "concordance_o2_snapshot_2026-10-28": {"S": o2pick(o2["pv1"]), "D": o2pick(o2["direct"])},
            "completeness_chen2020": {arm: ({k: c[k] for k in ("recall_restricted_primary", "recall_unrestricted_primary", "restricted_variants", "benchmark_variants", "missed_restricted")} if c else None) for arm, c in comp.items()},
            "reconciliation": {arm: ({k: r.get(k) for k in ("individuals_before_merging", "identities_after_merging", "identities_with_target_gene_variant", "merged_pairs", "identities_review_only")} if r else None) for arm, r in rec.items()},
            "normalization": {arm: ({k: n.get(k) for k in ("distinct_descriptions", "status_counts", "share_normalized_or_corrected_of_cdna", "cdna_descriptions")} if n else None) for arm, n in nrm.items()},
            "judge": judge}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diseases", nargs="+", default=["ha20", "ssadh"])
    a = ap.parse_args()
    direct_stats = j(OUT / "helper_stats.json") or []
    s_stats = j(ROOT / "analysis/openweight/claude_helper_stats.json") or []
    out = [one(d, direct_stats, s_stats) for d in a.diseases]
    for s in out:
        (OUT / f"summary_{s['disease']}.json").write_text(json.dumps(s, indent=1) + "\n")
    pc = lambda b: "—" if not b or b.get("share") is None else f"{100 * b['share']:.1f}% ({b['k']}/{b['n']})"
    L = ["# SLIDERS ablation: arm S (pv1, SLIDERS-style) vs arm D (direct extraction)", "",
         "*Generated by `analysis/sliders_ablation/summary.py`. Same papers, same model and route; arm D has no evidence tables, quotes, rules file, gatekeeper or reconciliation step. Exploratory (D-44).*", "",
         "| Measure | " + " | ".join(f"{s['disease']} S | {s['disease']} D" for s in out) + " |", "|---|" + "---|---|" * len(out)]
    row = lambda name, f: L.append(f"| {name} | " + " | ".join(f"{f(s, 'S')} | {f(s, 'D')}" for s in out) + " |")
    row("Papers compared", lambda s, k: s["papers_compared"])
    for m in ("individuals", "variant_rows", "target_gene_variant_keys", "phenotypic_feature_rows", "checklist_cells"):
        row(m.replace("_", " ").capitalize(), lambda s, k, m=m: s["coverage"][k].get(m, 0))
    row("Checklist excluded share", lambda s, k: pc(s["coverage"][k]["checklist_excluded_share"]))
    row("Checklist not-reported share", lambda s, k: pc(s["coverage"][k]["checklist_not_reported_share"]))
    for g in GROUNDING_FIELDS:
        row(f"Found verbatim in paper: {g}", lambda s, k, g=g: pc(s["grounding"][k][g]))
    row("HGVS recall tiers 1+2 (2026-10-28 snapshot)", lambda s, k: pc((s["concordance_o2_snapshot_2026-10-28"][k] or {}).get("hgvs_recall_tier12")))
    row("Overlap with ClinVar, tier 1", lambda s, k: pc((s["concordance_o2_snapshot_2026-10-28"][k] or {}).get("overlap_tier1")))
    row("Classification agreement", lambda s, k: pc((s["concordance_o2_snapshot_2026-10-28"][k] or {}).get("classification_agreement")))
    row("Judge: unsupported or not found", lambda s, k: pc(((s["judge"] or {}).get("arms", {}).get(k) or {}).get("unsupported_or_not_found")))
    row("Cost per paper, median ($, estimate)", lambda s, k: s["cost_time"][k]["cost_median_per_paper_usd"])
    row("Cost total ($, estimate; S without gatekeeper)", lambda s, k: s["cost_time"][k]["cost_total_usd"])
    row("Wall-clock per paper, median (s)", lambda s, k: s["cost_time"][k]["wall_median_per_paper_seconds"])
    L += ["", "| Agreement S vs D | " + " | ".join(s["disease"] for s in out) + " |", "|---|" + "---|" * len(out)]
    L.append("| Target-gene variant keys shared / union | " + " | ".join(f"{s['agreement']['variant_keys']['shared']}/{s['agreement']['variant_keys']['union']} (S only {s['agreement']['variant_keys']['S_only']}, D only {s['agreement']['variant_keys']['D_only']})" for s in out) + " |")
    L.append("| Checklist status agreement on shared cells | " + " | ".join(f"{s['agreement']['checklist']['status_agreement']} of {s['agreement']['checklist']['cells_shared']}" for s in out) + " |")
    L.append("| Label Jaccard (pooled) | " + " | ".join(f"{s['agreement']['labels']['jaccard_pooled']}" for s in out) + " |")
    L.append("| Papers with the same individual count | " + " | ".join(f"{s['agreement']['papers_same_individual_count']}/{s['papers_compared']}" for s in out) + " |")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
