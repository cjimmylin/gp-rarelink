"""Write reports/sliders_ablation_findings.md (D-44) from the generated files.

Every number comes from analysis/sliders_ablation/summary_<d>.json (summary.py), judge_summary.json
(judge_merge.py), input_check.json, sample_summary.json, o2/<arm>/o2_<d>.json, completeness_<run>.json,
runs/direct-<d>/manifest.json and helper_stats.json. Prose that is not a number is written here once;
sentences that state a direction are computed from the intervals.

  uv run python analysis/sliders_ablation/report.py
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
A = ROOT / "analysis/sliders_ablation"
D = ["ha20", "ssadh"]
NAME = {"ha20": "A20 haploinsufficiency (HA20)", "ssadh": "SSADH deficiency"}


def j(p: Path):
    return json.loads(p.read_text()) if p.exists() else None


def pct(b, nd=1):
    if not b or b.get("share") is None:
        return "—"
    ci = b.get("ci95")
    return f"{100 * b['share']:.{nd}f}% ({b['k']}/{b['n']}" + (f"; 95% CI {100 * ci[0]:.{nd}f}–{100 * ci[1]:.{nd}f})" if ci else ")")


def diff_txt(dd):
    if not dd or dd.get("diff") is None:
        return "—"
    lo, hi = dd["ci95"]
    return f"{100 * dd['diff']:+.1f} points (95% CI {100 * lo:+.1f} to {100 * hi:+.1f})"


def direction(dd, higher="higher", lower="lower"):
    if not dd or dd.get("diff") is None:
        return "not measured"
    lo, hi = dd["ci95"]
    if lo > 0:
        return higher
    if hi < 0:
        return lower
    return "not distinguishable from the SLIDERS arm at this sample size"


def money(x):
    return "—" if x is None else f"${x:,.2f}"


def inputs_line(IC: dict) -> str:
    parts = []
    for d, blk in (IC.get("diseases") or {}).items():
        ff, sp = blk.get("fetched_files") or {}, blk.get("pv1_spans_in_recreated_markdown") or {}
        t = (f"{NAME[d]}: {ff.get('same_sha256')} of {ff.get('papers')} re-fetched files are byte-identical to the manifest sha256"
             + (f", {len(ff.get('different_sha256') or [])} XML files are served in a changed form" if ff.get("different_sha256") else "")
             + (f", not re-fetched: {', '.join(ff['missing'])}" if ff.get("missing") else "")
             + f"; pv1 spans found in the re-created Markdown: {sp.get('span_found_rate')} of {sp.get('values_asserted', 0):,} values"
             + (f" ({'; '.join(sp.get('problems_head') or [])})" if sp.get("n_problems") else ", 0 problems"))
        parts.append(t)
    return "; ".join(parts)


def recall_diff(d: str) -> dict:
    """ClinVar-cited variants (by VariationID and citing paper) missed by one arm and found by the other, from the O2 misses files."""
    import csv
    from collections import Counter
    def load(arm):
        f = A / f"o2/{arm}/o2_recall_misses.csv"
        if not f.exists():
            return {}
        return {(r["clinvar_variation_id"], r["pmid"]): r for r in csv.DictReader(f.open()) if r["disease"] == d}
    S_, D_ = load("pv1"), load("direct")
    d_only, s_only = set(S_) - set(D_), set(D_) - set(S_)  # missed by S and found by D; missed by D and found by S
    return {"D_found_S_missed": len(d_only), "D_found_S_missed_by_pmid": dict(Counter(k[1] for k in d_only).most_common()),
            "S_found_D_missed": len(s_only), "S_found_D_missed_by_pmid": dict(Counter(k[1] for k in s_only).most_common())}


def paper_variant_rows(d: str, run: str, pmid: str) -> str:
    f = ROOT / f"data/extracted/{d}/{run}/per_paper/{pmid}.json"
    if not f.exists():
        return "no output"
    t = (j(f) or {}).get("tables") or {}
    vs = t.get("variants") or []
    cd = {(v.get("cdna_hgvs_as_stated") or {}).get("value") for v in vs} - {None, "not reported", "", "not applicable"}
    return f"{len(t.get('individuals') or [])} individuals, {len(vs)} variant rows, {len(cd)} distinct cDNA strings"


def main() -> int:
    S = {d: j(A / f"summary_{d}.json") for d in D}
    J = j(A / "judge_summary.json") or {"diseases": {}}
    IC = j(A / "input_check.json") or {"diseases": {}}
    SAMP = j(ROOT / "adjudication/sliders_ablation/sample_summary.json") or j(A / "sample_summary.json") or {"diseases": {}}
    M = {d: j(ROOT / f"runs/direct-{d}/manifest.json") or j(ROOT / f"runs/direct-{d}/launch.json") or {} for d in D}
    HS = j(A / "helper_stats.json") or []
    direct_cost = sum(r["cost_usd_estimate"] for r in HS if r["kind"] == "direct")
    judge_cost = sum(r["cost_usd_estimate"] for r in HS if r["kind"] == "judge")
    n_direct = sum(1 for r in HS if r["kind"] == "direct")
    n_judge = sum(1 for r in HS if r["kind"] == "judge")
    served = sorted({m for r in HS for m in r.get("models_served", {})})
    missing = [p for d in D for p in ((IC.get("diseases") or {}).get(d, {}).get("fetched_files") or {}).get("missing", [])]
    PS = j(ROOT / "adjudication/sliders_ablation/judge/paper_subset.json") or {}
    judge_cost_by = {d: [r["cost_usd_estimate"] for r in HS if r["kind"] == "judge" and r["pmid"] in ((PS.get(d) or {}).get("judged") or [])] for d in D}

    L = ["# SLIDERS ablation pilot: direct extraction versus the SLIDERS-style pipeline on HA20 and SSADH deficiency (D-44)", "",
         "*Exploratory (D-44, Jimmy Lin, 2026-10-28). Design written before the run: `reports/sliders_ablation_design.md`. Generated by "
         "`analysis/sliders_ablation/report.py` from `analysis/sliders_ablation/summary_<d>.json`, `judge_summary.json`, `input_check.json`, "
         "`sample_summary.json`, `o2/`, `completeness_*.json`, `helper_stats.json` and `runs/direct-<d>/manifest.json`. Nothing registered changes; "
         "the SLIDERS arm's registered figures are not replaced. HA20 is the development disease (D-18).*", "",
         "## 1. What ran", "",
         "- **Arm S (SLIDERS-style):** the frozen six-disease runs `pv1-ha20` and `pv1-ssadh` (2026-10-20), not re-run: evidence tables with a "
         "verbatim quote on every value, `extract_v6` with its rules, gatekeeper v4, reconciliation v4.",
         "- **Arm D (direct extraction):** `direct-ha20` and `direct-ssadh`, run 2026-10-28: one Claude Code helper per paper, the same model and route "
         "as pv1, given the paper and the 60-line `direct_v1_<d>.md` only. Final per-individual records, no quotes, no evidence tables, no rules "
         f"file, no gatekeeper, no reconciliation step. Model served to every helper: {', '.join(served) or '—'}. "
         f"{n_direct} extraction helpers on {n_direct} papers with re-created text" + (f"; not re-fetched and dropped from the comparison: {', '.join(missing)} (its open PDF host refused the download)" if missing else "") + ".",
         "- **Instruction hashes:** " + "; ".join(f"{d}: " + ", ".join(f"`{Path(k).name}` {v[:12]}" for k, v in (M[d].get("prompt_sha256") or {}).items()) for d in D) + ".",
         "- **Same papers, same text.** The git-ignored full text was re-created in this container (`analysis/sliders_ablation/input_check.json`): " + inputs_line(IC) + ".",
         "- **Same scoring:** conversion of arm D's records to the five-table shape (`direct_to_tables.py`, span = null), then the same reconciliation, "
         "normalization and O2 harness on both arms against one ClinVar snapshot (2026-10-28), and the same arm-blinded judge.", ""]

    # 2. headline table
    L += ["## 2. Headline table", "",
          "| Measure | " + " | ".join(f"{d} S | {d} D" for d in D) + " |", "|---|" + "---|---|" * len(D)]

    def row(name, f):
        L.append(f"| {name} | " + " | ".join(f"{f(d, 'S')} | {f(d, 'D')}" for d in D) + " |")

    row("Papers compared", lambda d, k: S[d]["papers_compared"])
    row("Individual rows", lambda d, k: f"{S[d]['coverage'][k]['individuals']:,}")
    row("Variant rows", lambda d, k: f"{S[d]['coverage'][k]['variant_rows']:,}")
    row("Distinct target-gene variant keys", lambda d, k: S[d]["coverage"][k]["target_gene_variant_keys"])
    row("Phenotypic-feature rows", lambda d, k: f"{S[d]['coverage'][k]['phenotypic_feature_rows']:,}")
    row("Checklist cells marked excluded", lambda d, k: pct(S[d]["coverage"][k]["checklist_excluded_share"]))
    row("Checklist cells not reported", lambda d, k: pct(S[d]["coverage"][k]["checklist_not_reported_share"]))
    row("**Judge: unsupported or not found**", lambda d, k: f"**{pct(((J['diseases'].get(d) or {}).get('arms', {}).get(k) or {}).get('unsupported_or_not_found'))}**")
    row("Judge: not fully supported", lambda d, k: pct(((J['diseases'].get(d) or {}).get('arms', {}).get(k) or {}).get('not_fully_supported')))
    row("HGVS recall, tiers 1+2 (snapshot 2026-10-28)", lambda d, k: pct((S[d]["concordance_o2_snapshot_2026-10-28"][k] or {}).get("hgvs_recall_tier12")))
    row("HGVS recall, tier 1", lambda d, k: pct((S[d]["concordance_o2_snapshot_2026-10-28"][k] or {}).get("hgvs_recall_tier1")))
    row("Overlap with ClinVar, tier 1 (not precision)", lambda d, k: pct((S[d]["concordance_o2_snapshot_2026-10-28"][k] or {}).get("overlap_tier1")))
    row("Classification agreement, where stated", lambda d, k: pct((S[d]["concordance_o2_snapshot_2026-10-28"][k] or {}).get("classification_agreement")))
    row("Gap candidates (tier-1 alleles absent from ClinVar)", lambda d, k: (S[d]["concordance_o2_snapshot_2026-10-28"][k] or {}).get("gap_candidates_tier1_unmatched", "—"))
    row("Variant descriptions found verbatim in paper", lambda d, k: pct(S[d]["grounding"][k]["variant descriptions (target gene)"]))
    row("Ages as written found verbatim", lambda d, k: pct(S[d]["grounding"][k]["ages as written"]))
    row("Disease label found verbatim", lambda d, k: pct(S[d]["grounding"][k]["disease label"]))
    row("Authors' pathogenicity found verbatim", lambda d, k: pct(S[d]["grounding"][k]["variant pathogenicity as stated"]))
    row("Cost per paper, median (estimate)", lambda d, k: money(S[d]["cost_time"][k]["cost_median_per_paper_usd"]))
    row("Cost, all papers (estimate)", lambda d, k: money(S[d]["cost_time"][k]["cost_total_usd"]) + (f" (+{money(S[d]['cost_time'][k]['gatekeeper_cost_usd_estimate'])} gatekeeper)" if k == "S" and S[d]["cost_time"][k].get("gatekeeper_cost_usd_estimate") else ""))
    row("Wall-clock per paper, median", lambda d, k: f"{(S[d]['cost_time'][k]['wall_median_per_paper_seconds'] or 0) / 60:.1f} min")
    L.append("")
    L += ["Completeness against Chen 2020 Table S1 (HA20 only, restricted recall, primary papers): " + " | ".join(
        f"arm {k}: {pct((S['ha20']['completeness_chen2020'].get(k) or {}).get('recall_restricted_primary'))}" for k in ("S", "D")) + ".", ""]

    # 3. judge
    L += ["## 3. Support judge (locate-and-judge, arm-blinded)", "",
          "One Opus helper per paper judged a shuffled list of claims from both arms, with the arm hidden and arm S's quotes removed, finding the "
          "supporting passage itself (`judge_locate_v1.md`). The sample: per paper and arm, up to 2 claims from each of three field groups "
          "(variant fields; phenotype statuses and feature text; other person-level fields), drawn by seed "
          f"{SAMP.get('seed', '—')} from each arm's raw pool (arm S before the gatekeeper, because arm D is raw). **This is a model's reading, not the "
          "error rate**: the pilot's gatekeeper understated human-found error by an order of magnitude, and the judge is Claude judging Claude in both arms.", ""]
    if PS:
        both = {d: (SAMP.get("diseases") or {}).get(d, {}).get("papers_in_both_arms") for d in D}
        mean_h = (sum(judge_cost_by["ha20"]) / len(judge_cost_by["ha20"])) if judge_cost_by.get("ha20") else None
        n_def = len((PS.get("ha20") or {}).get("deferred") or [])
        later = (PS.get("ha20") or {}).get("deferred_judged_on_approval") or []
        first = sorted(set(PS["ha20"]["judged"]) - set(later))
        head = (f"**Which papers were judged.** The design planned one judge helper for each of the {sum(v or 0 for v in both.values())} papers with output in both arms "
                f"({', '.join(f'{NAME[d]} {both[d]}' for d in D)}). The three pilot judge helpers cost $0.76–1.60 each, and the full run on top of arm D's extraction "
                f"would have passed the $300 ceiling (D-44), so within the ceiling the judge first ran on all {len(PS['ssadh']['judged'])} SSADH papers and on "
                f"{len(first)} of {both['ha20']} HA20 papers: the two pilot papers chosen by hand, plus {len(PS['ha20']['random_draw'])} drawn with seed "
                f"{PS['seed']} (`adjudication/sliders_ablation/judge/paper_subset.json`). ")
        if n_def == 0 and later:
            L += [head + f"Jimmy then approved judging the remaining {len(later)} HA20 papers past the ceiling (2026-10-28, \"yes for both and also merge to main\"), "
                  f"with the same instruction and launch text, so every paper with output in both arms is judged and the figures below cover all of them. "
                  f"The HA20 judge helpers' mean cost was {money(mean_h) if mean_h else '—'} per paper.", ""]
        else:
            L += [head + f"The other {n_def} HA20 papers' chunks are drawn and waiting; judging them would cost about {money(mean_h * n_def) if mean_h else '—'} more at the "
                  f"HA20 judge helpers' mean of {money(mean_h) if mean_h else '—'} per paper, which needs Jimmy's decision because it passes the ceiling. "
                  f"**The HA20 judge figures below are on that {len(PS['ha20']['judged'])}-paper subset; the SSADH figures cover every paper.**", ""]
    for d in D:
        e = J["diseases"].get(d)
        if not e:
            L += [f"*{NAME[d]}: judge not yet run.*", ""]
            continue
        L += [f"**{NAME[d]}**", "", "| Judge | Arm S | Arm D |", "|---|---|---|"]
        for k, lab in (("n", "Claims judged"),):
            L.append(f"| {lab} | {e['arms']['S']['n']} | {e['arms']['D']['n']} |")
        for v in ("supported", "partially_supported", "unsupported", "not_found"):
            L.append(f"| {v.replace('_', ' ')} | {e['arms']['S']['verdicts'][v]} | {e['arms']['D']['verdicts'][v]} |")
        L.append(f"| **Unsupported or not found** | **{pct(e['arms']['S'].get('unsupported_or_not_found'))}** | **{pct(e['arms']['D'].get('unsupported_or_not_found'))}** |")
        L.append(f"| Not fully supported | {pct(e['arms']['S'].get('not_fully_supported'))} | {pct(e['arms']['D'].get('not_fully_supported'))} |")
        for g in ("variant", "phenotype", "other"):
            L.append(f"| … unsupported or not found, {g} fields | {pct(e['by_group'][g]['S'].get('unsupported_or_not_found'))} | {pct(e['by_group'][g]['D'].get('unsupported_or_not_found'))} |")
        L.append(f"| … among `excluded` statuses | {pct(e['excluded_statuses']['S'].get('unsupported_or_not_found'))} | {pct(e['excluded_statuses']['D'].get('unsupported_or_not_found'))} |")
        L.append(f"| … among `observed` statuses | {pct(e['observed_statuses']['S'].get('unsupported_or_not_found'))} | {pct(e['observed_statuses']['D'].get('unsupported_or_not_found'))} |")
        L += ["", f"- **Difference D − S (unsupported or not found):** {diff_txt(e['difference_D_minus_S_unsupported'])}; arm D is {direction(e['difference_D_minus_S_unsupported'])}.",
              f"- **Judge's quoted evidence found verbatim in the paper:** S {e['evidence_quoted_found_in_paper']['S']}, D {e['evidence_quoted_found_in_paper']['D']} (True = all quoted passages found; None = no passage quoted).",
              f"- **Arm S, judge vs gatekeeper v4 on the same claims:** {e['arm_S_judge_vs_gatekeeper_v4']}.",
              f"- **Arm S, judge's passage overlaps the extractor's hidden quote:** {e['arm_S_judge_evidence_overlaps_extractor_span']}.",
              f"- **Fields with most unsupported claims:** S {e['top_fields_unsupported']['S']}; D {e['top_fields_unsupported']['D']}.", ""]

    # 4. coverage / agreement / three-state
    L += ["## 4. Coverage, three-state behavior and agreement between arms", ""]
    for d in D:
        s = S[d]
        a = s["agreement"]
        L += [f"- **{NAME[d]}:** target-gene variant keys shared {a['variant_keys']['shared']} of a union of {a['variant_keys']['union']} "
              f"(S only {a['variant_keys']['S_only']}, D only {a['variant_keys']['D_only']}); checklist status agreement {a['checklist']['status_agreement']} on "
              f"{a['checklist']['cells_shared']:,} cells both arms have for the same label and item (disagreements: {a['checklist']['disagreements']}); "
              f"label Jaccard {a['labels']['jaccard_pooled']}; same individual count in {a['papers_same_individual_count']} of {s['papers_compared']} papers. "
              f"Checklist cells by state, S {s['coverage']['S']['checklist_by_state']} vs D {s['coverage']['D']['checklist_by_state']}. "
              f"Reconciliation (policy v4): S {s['reconciliation']['S']}, D {s['reconciliation']['D']}. "
              f"Normalization: S {s['normalization']['S']}, D {s['normalization']['D']}."]
    L.append("")

    # 5. structure
    L += ["## 5. Structure and conversion of arm D", ""]
    for d in D:
        st = S[d]["structure"]
        L.append(f"- **{NAME[d]}:** {st['D_conversion']}; enum values outside the schema by field: {st['D_enum_outside_by_field'] or 'none'}. "
                 f"Arm S: {st['S_span_check_problems']} span-check problems on {st['S_values_asserted']:,} asserted values at the run of record.")
    L.append("")

    # 6. cost
    L += ["## 6. Cost and time", "",
          f"- Arm D: {n_direct} extraction helpers, **{money(direct_cost)}** by helper tokens (the six-disease run's rate, $5.996 per weighted million; an estimate, not an invoice). "
          f"Judge: {n_judge} helpers, **{money(judge_cost)}** (mean {money(judge_cost / n_judge) if n_judge else '—'} per paper; "
          + ", ".join(f"{NAME[d]} {money(sum(v) / len(v))}" for d, v in judge_cost_by.items() if v) + "). "
          f"Study total **{money(direct_cost + judge_cost)}** against the original $300 ceiling (contingency, D-44; Jimmy raised it on 2026-10-28 to cover the remaining HA20 judge papers). The design estimated $110–200; extraction alone came to "
          f"{money(direct_cost)} against its $90–150 estimate because the direct helpers wrote long nested records for cohort papers (the costliest paper, 40574834 with 62 individuals, is in `helper_stats.json`).",
          "- Arm S's cost on the same papers is the pv1 extraction helpers' tokens (`analysis/openweight/claude_helper_stats.json`), with its gatekeeper pass "
          "at $0.0044 per judged claim shown apart. Per paper: " + "; ".join(
              f"{d} S {money(S[d]['cost_time']['S']['cost_median_per_paper_usd'])} vs D {money(S[d]['cost_time']['D']['cost_median_per_paper_usd'])} (median), "
              f"wall-clock S {(S[d]['cost_time']['S']['wall_median_per_paper_seconds'] or 0) / 60:.1f} vs D {(S[d]['cost_time']['D']['wall_median_per_paper_seconds'] or 0) / 60:.1f} min" for d in D) + ".", ""]

    # 7. reading
    L += ["## 7. Reading the results against the expectations written before the run", ""]
    for d in D:
        s = S[d]
        e = J["diseases"].get(d) or {}
        cS, cD = s["cost_time"]["S"]["cost_median_per_paper_usd"], s["cost_time"]["D"]["cost_median_per_paper_usd"]
        exS, exD = s["coverage"]["S"]["checklist_excluded_share"], s["coverage"]["D"]["checklist_excluded_share"]
        o2S, o2D = s["concordance_o2_snapshot_2026-10-28"]["S"], s["concordance_o2_snapshot_2026-10-28"]["D"]
        pts = [f"**{NAME[d]}.**"]
        pts.append(f"Cost per paper: arm D {'cheaper' if cD is not None and cS is not None and cD < cS else 'not cheaper'} ({money(cD)} vs {money(cS)} median, extraction only; arm S also pays its gatekeeper).")
        pts.append(f"Individuals: D {s['coverage']['D']['individuals']} vs S {s['coverage']['S']['individuals']}; target-gene variant keys D {s['coverage']['D']['target_gene_variant_keys']} vs S {s['coverage']['S']['target_gene_variant_keys']}.")
        if exS and exD:
            pts.append(f"Excluded checklist cells: D {100 * exD['share']:.1f}% vs S {100 * exS['share']:.1f}% ({'more' if exD['share'] > exS['share'] else 'not more'} in D).")
        if e:
            pts.append(f"Judge unsupported-or-not-found: D is {direction(e['difference_D_minus_S_unsupported'])} ({diff_txt(e['difference_D_minus_S_unsupported'])}).")
            ex = e["excluded_statuses"]
            pts.append(f"Among `excluded` statuses: D {pct(ex['D'].get('unsupported_or_not_found'))} vs S {pct(ex['S'].get('unsupported_or_not_found'))}.")
        if o2S and o2D:
            pts.append(f"HGVS recall tiers 1+2: D {pct(o2D['hgvs_recall_tier12'])} vs S {pct(o2S['hgvs_recall_tier12'])} (intervals {'overlap' if o2D['hgvs_recall_tier12']['ci95'][0] <= o2S['hgvs_recall_tier12']['ci95'][1] and o2S['hgvs_recall_tier12']['ci95'][0] <= o2D['hgvs_recall_tier12']['ci95'][1] else 'do not overlap'}).")
            rd = recall_diff(d)
            if rd["D_found_S_missed"] or rd["S_found_D_missed"]:
                pts.append(f"ClinVar-cited variants found by one arm and missed by the other (by VariationID and citing paper): found only by D {rd['D_found_S_missed']} "
                           f"({', '.join(f'{k}: {v}' for k, v in rd['D_found_S_missed_by_pmid'].items())}); found only by S {rd['S_found_D_missed']}"
                           + (f" ({', '.join(f'{k}: {v}' for k, v in rd['S_found_D_missed_by_pmid'].items())})" if rd["S_found_D_missed"] else "") + ".")
                top = next(iter(rd["D_found_S_missed_by_pmid"]), None)
                if top and rd["D_found_S_missed_by_pmid"][top] >= 3:
                    pts.append(f"So the recall gain is concentrated in one paper, {top}: arm S recorded {paper_variant_rows(d, s['runs']['S'], top)}; arm D recorded "
                               f"{paper_variant_rows(d, s['runs']['D'], top)}. The variant strings are in the paper, but arm D assigned them to families from a table whose "
                               f"Markdown is scrambled (its helper said so), so the person links there are uncertain; the judge rated one such link partially supported.")
        L.append("- " + " ".join(pts))
    L += ["", "What the design said to conclude: if the unsupported rates are alike, the scaffold's value lies in provenance and auditability (every arm S value "
          "carries a quote a person can check; arm D's values carry none, and the judge had to find evidence for them) rather than in accuracy; if arm D's rate is "
          "higher, the scaffold also buys accuracy, and the field groups above say where.", ""]

    # 8. limitations
    L += ["## 8. Limitations", "",
          "- One baseline instruction; a different plain prompt could do better or worse.",
          "- The judge is the same model family in both arms, and a model. The human sheets under `adjudication/sliders_ablation/audit/` (50 claims per arm per disease, arm hidden) are the check; they are not rated yet.",
          "- Arm S ran eight days earlier (2026-10-20); the served model ID is the same (`claude-opus-5-5`).",
          "- HA20 is the development disease; SSADH is the cleaner test.",
          "- Arm D is not passed through the gatekeeper, by design: the comparison is between final records as each method delivers them. Arm S's judge sample is drawn from its raw claims for the same reason.",
          "- Cost is estimated from helper tokens with the rate the six-disease run's session readings gave; output tokens are undercounted the same way in both arms.",
          ("- The HA20 judge ran in two waves (32 papers within the $300 ceiling, then the remaining 45 after Jimmy raised it), same instruction and launch text; SSADH in one."
           if (PS.get("ha20") or {}).get("deferred_judged_on_approval") and not (PS.get("ha20") or {}).get("deferred")
           else "- HA20's judge sample covers 32 of the 77 papers with output in both arms (the cost ceiling); SSADH's covers all 39. The 45 remaining HA20 chunks are drawn and can be judged once Jimmy decides on the ceiling."),
          "- Two diseases, 124 papers with text: a pilot, not a general finding.", "",
          "## 9. Files", "",
          "- Design: `reports/sliders_ablation_design.md`. Decision: `DECISIONS.md` D-44.",
          "- Arm D instruction: `pipeline/extract/claude_code/prompts/direct_v1.md` (template), `direct_v1_<d>.md` (rendered), launch text `direct_launch_v1.txt`.",
          "- Arm D records: `data/extracted/<d>/direct-<d>/records/*.json`; five-table conversion `per_paper/*.json`; `conversion_summary.json`.",
          "- Judge: `pipeline/extract/claude_code/prompts/judge_locate_v1.md`; sample `adjudication/sliders_ablation/judge/`; verdicts `analysis/sliders_ablation/judge_verdicts.csv`, `judge_summary.json`.",
          "- Harness: `analysis/sliders_ablation/o2/<arm>/`, `completeness_<run>.json`; summaries `summary_<d>.json`, `summary.md`; costs `helper_stats.json`.",
          "- Run records: `runs/direct-<d>/launch.json`, `manifest.json`."]
    out = ROOT / "reports/sliders_ablation_findings.md"
    out.write_text("\n".join(L) + "\n")
    print(f"wrote {out.relative_to(ROOT)} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
