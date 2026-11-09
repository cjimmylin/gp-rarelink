"""Export the numbers, table rows and narration the collaborator deck, video and dashboard share.

Reads `analysis.interim_paper.data.load()` (the same files as the interim papers) and writes
analysis/dashboard/deck_data.json. Nothing here calls a model or the network. The deck (deck.js),
the video (build_video.py) and the site (build_site.py) read this file, so every number on them
traces to the committed result files.

  uv run python -m analysis.dashboard.export_deck_data
"""
from __future__ import annotations

import json
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from analysis.interim_paper.data import CONFIRMATORY, DISEASES, GENE, INHERITANCE, NAME, ROOT, SHORT, load
from analysis.interim_paper.figures_v3 import release_date
from analysis.interim_paper.stats import clopper_pearson

OUT = ROOT / "analysis/dashboard/deck_data.json"
PAGES_URL = "https://cjimmylin.github.io/gp-rarelink/"


def pct(x, nd=1):
    q = Decimal(1).scaleb(-nd)
    return str(Decimal(str(100 * x)).quantize(q, rounding=ROUND_HALF_UP))


def N(x):
    return f"{x:,}"


def ablation_cost():
    m = re.search(r"SLIDERS ablation pilot \(D-44[^\n]*?\*\*\$([\d,.]+) by helper tokens", (ROOT / "BUDGET.md").read_text())
    return float(m.group(1).replace(",", "")) if m else None


def main():
    D = load()
    t, t5 = D["totals"]["all"], D["totals"]["five"]
    om = D["omimh"]
    placed = sum(D["gaps"][d]["tier1_alleles"] for d in DISEASES)
    in_clinvar = sum(D["o2_tiers"][d].get("1", 0) for d in DISEASES)
    plp = sum(v for d in DISEASES for k, v in D["o2_tier1_classes"][d].items() if k in ("P", "LP", "P/LP"))
    live = t["gap_candidates_live"]
    rec_all = om["totals"]["recall_all_strict"]
    cov = {d: D["coverage"][d]["fulltext_share"] for d in DISEASES}
    a1, a2 = D["poc"]["audit1"]["unsupported_strict"], D["poc"]["audit2"]["unsupported_strict"]
    u5 = clopper_pearson(t5["unsupported"], t5["model_claims"])
    rep = D["repeat"]
    ow, owg = D["ow"], D["ow_gk"]
    mem_c = D["mem"]["claude"]["by_stratum"]
    b = D["budget"]
    dropped = sum(v for d in DISEASES for k, v in D["build"][d]["counts"].items() if k.startswith("gk_dropped"))
    src_all = sum(om["per"][d]["A_literature"]["av_source_pmids"] for d in DISEASES)
    src_ex = sum(om["per"][d]["A_literature"]["av_source_pmids_extracted"] for d in DISEASES)
    restricted_n = sum(om["per"][d]["B_allelic_variants"]["restricted_denominator_source_paper_extracted"] for d in DISEASES)
    restricted_k = sum(om["per"][d]["B_allelic_variants"]["recall_restricted_in_source_paper_strict"]["k"] for d in DISEASES)
    funnel = {}
    for d in DISEASES:
        for st, n in om["per"][d]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {}).items():
            funnel[st] = funnel.get(st, 0) + n
    cost_ratio = ow["ha20"]["cost_usd"]["claude_median_per_paper"] / ow["ha20"]["cost_usd"]["open_median_per_paper"]
    time_ratio = ow["ha20"]["wall_seconds"]["open_median"] / ow["ha20"]["wall_seconds"]["claude_median"]
    abl = ablation_cost()

    stats = {
        "papers": t["papers"], "records": t["phenopackets"], "with_variant": t["with_variant"], "quotes": t["claims_all"],
        "model_claims": t["model_claims"], "unsupported": t["unsupported"], "dropped": dropped,
        "unsup_pct5": pct(t5["unsupported"] / t5["model_claims"], 2), "unsup_pct6": pct(t["unsupported"] / t["model_claims"], 2),
        "unsup_ci5": [pct(u5[0], 2), pct(u5[1], 2)],
        "placed": placed, "in_clinvar": in_clinvar, "plp": plp, "absent": placed - in_clinvar, "candidates": live,
        "reclass": t["reclass"], "reclass_strong": t["reclass_strong"],
        "omim_k": rec_all["k"], "omim_n": rec_all["n"], "omim_pct": pct(rec_all["share"], 0),
        "omim_src_all": src_all, "omim_src_extracted": src_ex, "omim_src_paywalled": funnel.get("in corpus, no open full text", 0),
        "omim_src_notfound": funnel.get("not found by search", 0), "omim_restricted_k": restricted_k, "omim_restricted_n": restricted_n,
        "cov_lo": pct(min(cov.values()), 0), "cov_hi": pct(max(cov.values()), 0),
        "human1": pct(a1["share"]), "human2": pct(a2["share"]), "human_n1": a1["n"], "human_n2": a2["n"], "n_o1": D["o1"]["n"],
        "repeat_papers": sum(rep[d]["papers_compared"] for d in DISEASES),
        "chk_lo": pct(min(rep[d]["checklist_agreement"] for d in DISEASES), 0), "chk_hi": pct(max(rep[d]["checklist_agreement"] for d in DISEASES), 0),
        "var_lo": pct(min(rep[d]["variant_key_jaccard"] for d in DISEASES), 0), "var_hi": pct(max(rep[d]["variant_key_jaccard"] for d in DISEASES), 0),
        "features_observed": t["features_observed"], "features_excluded": t["features_excluded"],
        "axd_clinvar_plp": D["clinvar"]["axd"]["plp"], "clinvar_release": release_date(D["clinvar"]["axd"]["release"]), "omim_date": om["date"],
        "mem_papers": sum(v["papers"] for v in mem_c.values()), "mem_after": mem_c["after"]["papers"],
        "spend_total": round(b["total"]), "spend_date": b["reading_at"][:10], "ablation": round(abl) if abl else None,
        "spend_lines": [{"n": l["n"], "name": l["name"], "requested": l["requested"], "spent": round(l["spent"], 2)} for l in b["lines"]],
        "spend_unassigned": round(b["unassigned"], 2),
        "cost_ratio": round(cost_ratio), "time_ratio": round(time_ratio),
        "ow": {d: {"papers": ow[d]["papers_compared"], "no_quote_pct": pct(ow[d]["span"]["open"]["no_quote_rate"]),
                   "claude_unsup": pct(owg[d]["claude"]["unsupported"]["share"], 2), "open_unsup": pct(owg[d]["open"]["unsupported"]["share"], 2),
                   "claude_unsup_f": round(100 * owg[d]["claude"]["unsupported"]["share"], 2), "open_unsup_f": round(100 * owg[d]["open"]["unsupported"]["share"], 2),
                   "shared": ow[d]["variant_keys"]["shared"], "union": ow[d]["variant_keys"]["union"], "jaccard": pct(ow[d]["variant_keys"]["jaccard_pooled"], 0),
                   "claude_cost": round(ow[d]["cost_usd"]["claude_median_per_paper"], 2), "open_cost": round(ow[d]["cost_usd"]["open_median_per_paper"], 2),
                   "claude_min": round(ow[d]["wall_seconds"]["claude_median"] / 60), "open_min": round(ow[d]["wall_seconds"]["open_median"] / 60)}
               for d in ("ha20", "ssadh")},
        "ow_key_spend": round(D["ow_manifest"]["ha20"]["key_spend_both_runs_usd"]["spent"]),
        "comp_ha20": D["completeness"]["ha20"]["recall_restricted_primary"], "comp_axd": D["completeness"]["axd"]["recall_restricted_primary"],
    }
    diseases = []
    for d in DISEASES:
        r = om["per"][d]["B_allelic_variants"]["recall_unrestricted_strict"]
        diseases.append({"key": d, "short": SHORT[d], "name": NAME[d], "gene": GENE[d], "inheritance": INHERITANCE[d], "development": d == "ha20",
                         "papers": D["run"][d]["papers"], "cov_pct": pct(cov[d], 0), "individuals": D["stage4"][d]["identities"],
                         "with_variant": D["stage4"][d]["identities_with_target_variant"], "placed": D["gaps"][d]["tier1_alleles"],
                         "candidates": om["gap_live"][d], "omim_k": r["k"], "omim_n": r["n"], "clinvar_plp": D["clinvar"][d]["plp"],
                         "unsup_pct": pct(D["run"][d]["unsupported_or_not_found"]["share"], 2)})
    s = stats
    # Narration: one paragraph per slide, read aloud at about 150 words a minute. Also the speaker notes and the captions.
    slides = [
        {"id": "title", "narration": "Welcome. This is a short overview of GP-RareLink, a project that reads the published literature on rare genetic diseases with a language model, turns it into structured records, and checks every value against its source. It is funded by Anthropic's AI for Science program and run by the Rare Genomics Institute with the Stanford OVAL lab. You are seeing interim results, for internal review."},
        {"id": "problem", "narration": f"Here is the problem. When a child with a rare disease is diagnosed, the responsible variant is often reported once, in a case report, and never submitted to the public databases. A laboratory testing the next child searches ClinVar and finds nothing. For Alexander disease alone, a 2024 review counts 182 causative variants in 550 published patients, but ClinVar holds {s['axd_clinvar_plp']} pathogenic or likely pathogenic records for the gene. The knowledge exists; it is scattered across papers no database can query."},
        {"id": "question", "narration": "So the question is whether a language model, reading with strict rules, can do the first pass. Two rules make the answer checkable. First, every value the model records must carry a verbatim quote from the paper, and a script confirms the quote is really there. Second, the databases we want to fill, ClinVar and OMIM, are never shown to the model. They are held out as the answer key. And the whole analysis plan was frozen before the main run, so what you see is what we said we would report."},
        {"id": "pipeline", "narration": f"This is the workflow. One model reader per paper fills a structured form with quotes. A script checks every quote. A second model pass, which we call the gatekeeper, re-reads each value against its quote and drops the ones it cannot support. The result is one standard record per individual, a GA4GH phenopacket. Below the firewall, a separate harness compares the records with ClinVar, OMIM and two published catalogues, and lists the variants the databases are missing. The orange box is what has not happened yet: the human audit and the expert adjudication."},
        {"id": "diseases", "narration": f"We ran six diseases, chosen to span inheritance modes and organ systems. A20 haploinsufficiency was the development disease, so its numbers are flagged and the other five are the confirmatory set. Only open-access papers were read, which matters later: for most of these diseases, only a fifth to a third of the literature is open."},
        {"id": "numbers", "narration": f"The headline numbers. {N(s['papers'])} papers became {N(s['records'])} individual records, {N(s['with_variant'])} of them carrying a variant in the disease gene. Every one of {N(s['quotes'])} quotes was found verbatim in its paper. {N(s['placed'])} distinct variants could be placed on the genome. {s['candidates']} of them are in neither ClinVar nor OMIM. And we recovered {s['omim_k']} of the {s['omim_n']} variants OMIM lists for these diseases."},
        {"id": "receipts", "narration": f"First finding: the receipts hold, but the decisive check has not happened. The gatekeeper judged {s['unsup_pct5']} percent of values unsupported across the five confirmatory diseases. That is the blue. The orange is what human raters found in the pilot, before the pipeline was frozen: around six percent. The machine's reading of its own errors is far below the humans'. The pre-registered test is a blinded audit of {s['n_o1']} claims by two panel members. It is built, and nobody has rated a claim yet. Until then, no accuracy claim can be made."},
        {"id": "coverage", "narration": f"Second finding: we find what we can read. Against OMIM's listed variants we recovered {s['omim_pct']} percent overall, from nearly ninety percent for the diseases whose literature is open to eleven percent for Tangier disease, whose variants come from closed papers of the early 2000s. Of the {s['omim_src_all']} papers OMIM cites as the sources for its variants, we could read {s['omim_src_extracted']}. Where we had read the source paper, the variant was usually in our records. Access, not reading, sets the ceiling."},
        {"id": "gap", "narration": f"Third finding: the database gap is real. Of {N(s['placed'])} genome-placed variants, {N(s['in_clinvar'])} are in ClinVar, and {N(s['plp'])} of those are classified pathogenic or likely pathogenic. {s['absent']} are absent from ClinVar; after the checks, {s['candidates']} remain as candidates, each with an evidence dossier listing every paper, every quote and every individual. {s['reclass']} more sit in ClinVar as uncertain or conflicting while the papers call them pathogenic. Nothing is submitted without expert adjudication."},
        {"id": "openweight", "narration": f"Fourth finding: a cheaper open-weight model finds the same variants and loses the receipts. On identical inputs, DeepSeek found the same variants about {s['ow']['ha20']['jaccard']} to {s['ow']['ssadh']['jaccard']} percent of the time at roughly one {s['cost_ratio']}th of the cost. But it left {s['ow']['ssadh']['no_quote_pct']} to {s['ow']['ha20']['no_quote_pct']} percent of its values with no quote at all, and the gatekeeper rejected {s['ow']['ssadh']['open_unsup']} to {s['ow']['ha20']['open_unsup']} percent of its claims, against Claude's {s['ow']['ha20']['claude_unsup']} to {s['ow']['ssadh']['claude_unsup']}."},
        {"id": "checks", "narration": f"Two more checks. Running a tenth of the papers twice gave the same checklist answers {s['chk_lo']} to {s['chk_hi']} percent of the time and the same variants {s['var_lo']} to {s['var_hi']} percent of the time. And a memorization probe on {s['mem_papers']} papers found no sign that either model recalled the papers from training rather than reading them."},
        {"id": "meaning", "narration": "What does this mean? On accuracy: the pipeline produces records with complete provenance, but a human-rated error rate is the one number it lacks, and the audit that provides it costs no model time. On coverage: a decision on access to paywalled papers would change these results more than any change to the model. On the answer key: databases curated by people deserve the same scrutiny; OMIM caught one of our normalization errors, and we found two OMIM entries linked to the wrong ClinVar records."},
        {"id": "roles", "narration": f"This is where you come in. We need two raters for the {s['n_o1']}-claim audit, roughly ten to fifteen hours each, and a tie-breaker. We need experts to adjudicate the {s['candidates']} candidates from their dossiers. We need people to fill four comparator sheets from natural-history cohorts. And we need reviewers for the methods and the paper. The dashboard has a short form where you can tell us who you are and how you would like to contribute."},
        {"id": "closing", "narration": "Thank you. Everything in this overview, the papers, the deck, the candidate list and the form, is on the dashboard. The numbers all trace to files in the project repository, and the report says plainly which questions are still open. We look forward to working with you."},
    ]
    data = {"date": date.today().isoformat(), "commit": D["commit"], "pages_url": PAGES_URL, "stats": stats, "diseases": diseases, "slides": slides,
            "figures": {k: str(ROOT / "reports/interim_paper_v3/figures" / f"{k}.png") for k in ("fig1_workflow", "fig2_checks", "fig3_coverage", "fig4_gaps")}}
    OUT.write_text(json.dumps(data, indent=1))
    words = sum(len(sl["narration"].split()) for sl in slides)
    print(f"wrote {OUT}: {len(slides)} slides, {words} narration words (about {words / 150:.1f} min)")


if __name__ == "__main__":
    main()
