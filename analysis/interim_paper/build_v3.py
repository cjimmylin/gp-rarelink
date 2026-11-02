"""Version 3 of the interim paper: a short, approachable highlights version (target: at most 10 pages).

Written from scratch for readers new to the field. Every number is read from `data.load()`, so it traces to
the committed files listed in SOURCES; the prose lives here. Version 2 (`build.py`) remains the full report.

  uv run python -m analysis.interim_paper.build_v3
  bash analysis/interim_paper/make_pdf_v3.sh
"""
from __future__ import annotations

import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from . import figures_v3
from .data import CONFIRMATORY, DISEASES, GENE, INHERITANCE, NAME, ROOT, SHORT, load
from .stats import clopper_pearson

OUT = ROOT / "reports/interim_paper_v3"


def N(x):
    return f"{x:,}"


def P(x, nd=1):
    q = Decimal(1).scaleb(-nd)
    return f"{Decimal(str(100 * x)).quantize(q, rounding=ROUND_HALF_UP)}%"


def CIp(r, nd=1):
    """'57% (43 of 75; 95% interval 46 to 68%)' from a {k, n, share, ci95} record."""
    lo, hi = r["ci95"]
    return f"{P(r['share'], nd)} ({r['k']} of {N(r['n'])}; 95% interval {P(lo, nd)} to {P(hi, nd)})"


def table(headers, rows_):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows_:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def lab(d):
    return SHORT[d] + ("\\*" if d == "ha20" else "")


def release_date(s):
    return figures_v3.release_date(s)


def ablation_cost():
    m = re.search(r"SLIDERS ablation pilot \(D-44[^\n]*?\*\*\$([\d,.]+) by helper tokens", (ROOT / "BUDGET.md").read_text())
    return float(m.group(1).replace(",", "")) if m else None


def example_candidates(D):
    out = []
    for d in DISEASES:
        cands = [r for r in D["gap_candidates"] if r["disease"] == d and r["status"] != "withdrawn"]
        if not cands:
            continue
        best = max(cands, key=lambda r: (int(r["n_papers"]), int(r["n_identities"]), -int(r["candidate_id"].split("-")[-1])))
        written = "; ".join(dict.fromkeys(x.strip() for x in re.split(r"\s*\|+\s*|; ", best["original_strings"]) if x.strip()))
        if len(written) > 60:
            written = written[:57].rstrip() + "..."
        prot = (best["hgvs_p_predicted"] or "—").split(":")[-1]
        out.append([lab(d), f"`{best['hgvs_c']}` ({prot})", f"`{written}`" if written else "—", best["n_papers"], best["n_identities"], best["author_class"] or "not stated"])
    return out


def main():
    D = load()
    figs = figures_v3.make_all(D)
    t, t5 = D["totals"]["all"], D["totals"]["five"]
    om = D["omimh"]
    today = date.today().isoformat()
    dropped = sum(v for d in DISEASES for k, v in D["build"][d]["counts"].items() if k.startswith("gk_dropped"))
    placed = sum(D["gaps"][d]["tier1_alleles"] for d in DISEASES)
    in_clinvar = sum(D["o2_tiers"][d].get("1", 0) for d in DISEASES)
    plp = sum(v for d in DISEASES for k, v in D["o2_tier1_classes"][d].items() if k in ("P", "LP", "P/LP"))
    absent = placed - in_clinvar
    live = t["gap_candidates_live"]
    cv_date = release_date(D["clinvar"]["ssadh"]["release"])
    cov = {d: D["coverage"][d]["fulltext_share"] for d in DISEASES}
    cov_lo, cov_hi = min(cov.values()), max(cov.values())
    rec = {d: om["per"][d]["B_allelic_variants"]["recall_unrestricted_strict"] for d in DISEASES}
    rec_all = om["totals"]["recall_all_strict"]
    best_rec = max(DISEASES, key=lambda d: rec[d]["share"])
    worst_rec = min(DISEASES, key=lambda d: rec[d]["share"])
    src_all = sum(om["per"][d]["A_literature"]["av_source_pmids"] for d in DISEASES)
    src_ex = sum(om["per"][d]["A_literature"]["av_source_pmids_extracted"] for d in DISEASES)
    restricted_n = sum(om["per"][d]["B_allelic_variants"]["restricted_denominator_source_paper_extracted"] for d in DISEASES)
    restricted_k = sum(om["per"][d]["B_allelic_variants"]["recall_restricted_in_source_paper_strict"]["k"] for d in DISEASES)
    funnel = {}
    for d in DISEASES:
        for st, n in om["per"][d]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {}).items():
            funnel[st] = funnel.get(st, 0) + n
    paywalled, notfound = funnel.get("in corpus, no open full text", 0), funnel.get("not found by search", 0)
    rep = D["repeat"]
    rep_papers = sum(rep[d]["papers_compared"] for d in DISEASES)
    chk_lo, chk_hi = min(rep[d]["checklist_agreement"] for d in DISEASES), max(rep[d]["checklist_agreement"] for d in DISEASES)
    var_lo, var_hi = min(rep[d]["variant_key_jaccard"] for d in DISEASES), max(rep[d]["variant_key_jaccard"] for d in DISEASES)
    a1, a2 = D["poc"]["audit1"]["unsupported_strict"], D["poc"]["audit2"]["unsupported_strict"]
    u5 = clopper_pearson(t5["unsupported"], t5["model_claims"])
    u6 = clopper_pearson(t["unsupported"], t["model_claims"])
    comp_ha20 = D["completeness"]["ha20"]["recall_restricted_primary"]
    comp_axd = D["completeness"]["axd"]["recall_restricted_primary"]
    ow = D["ow"]
    owg = D["ow_gk"]
    mem_c, mem_o = D["mem"]["claude"]["by_stratum"], D["mem"]["open"]["by_stratum"]
    mem_papers = sum(v["papers"] for v in mem_c.values())
    after_c, after_o = mem_c["after"], mem_o["after"]
    b = D["budget"]
    abl = ablation_cost()
    reclass, reclass_strong = t["reclass"], t["reclass_strong"]
    n_o1 = D["o1"]["n"]
    cost_ratio = ow["ha20"]["cost_usd"]["claude_median_per_paper"] / ow["ha20"]["cost_usd"]["open_median_per_paper"]
    time_ratio = ow["ha20"]["wall_seconds"]["open_median"] / ow["ha20"]["wall_seconds"]["claude_median"]

    # ---------------------------------------------------------------- tables
    glossary = table(["Term", "What it is", "Its role here"], [
        ["ClinVar", "A public database (NIH) where laboratories and researchers deposit genetic variants with a classification such as *pathogenic* or *uncertain significance*", "Half of the answer key; the target for new submissions"],
        ["OMIM", "A curated encyclopedia of genes and genetic diseases, written by experts, which lists selected example variants for each disease", "The other half of the answer key"],
        ["HPO", "The Human Phenotype Ontology: a standard vocabulary of about 19,000 clinical features (\"seizures\", \"hepatomegaly\")", "The language the records use for clinical features"],
        ["HGVS", "The standard way to write a genetic variant, for example `c.1097_1098del`, always relative to a named transcript", "How variants are written and compared"],
        ["Phenopacket", "A standard machine-readable file (GA4GH) describing one individual: features, variants, diagnosis, with sources", "The output: one per individual"],
        ["Gatekeeper", "Our name for a second model pass that re-reads every extracted value against its quoted evidence", "A filter on the records, and a first estimate of error"],
    ])
    rows = []
    for d in DISEASES:
        c = D["coverage"][d]
        s4 = D["stage4"][d]
        rows.append([lab(d), f"*{GENE[d]}*", INHERITANCE[d], f"{D['run'][d]['papers']} ({P(c['fulltext_share'], 0)})", N(s4["identities"]), N(s4["identities_with_target_variant"]),
                     D["gaps"][d]["tier1_alleles"], om["gap_live"][d], f"{rec[d]['k']} of {rec[d]['n']}", D["clinvar"][d]["plp"]])
    rows.append(["**Five confirmatory**", "", "", N(t5["papers"]), N(t5["identities"]), N(t5["with_variant"]), N(t5["tier1_alleles"]), t5["gap_candidates_live"],
                 f"{sum(rec[d]['k'] for d in CONFIRMATORY)} of {sum(rec[d]['n'] for d in CONFIRMATORY)}", N(sum(D["clinvar"][d]["plp"] for d in CONFIRMATORY))])
    rows.append(["**All six**", "", "", N(t["papers"]), N(t["identities"]), N(t["with_variant"]), N(placed), live, f"{rec_all['k']} of {rec_all['n']}", N(sum(D["clinvar"][d]["plp"] for d in DISEASES))])
    diseases_tbl = table(["Disease", "Gene", "Inheritance", "Papers read (open-access share of the corpus)", "Individuals", "…with a variant in the gene", "Distinct variants placed on the genome",
                          "…absent from ClinVar and OMIM (candidates)", "OMIM's listed variants recovered", "ClinVar pathogenic or likely pathogenic records for the gene"], rows)
    ow_rows = []
    for d in ("ha20", "ssadh"):
        s, g = ow[d], owg[d]
        ow_rows.append([lab(d), s["papers_compared"], f"0% / {P(s['span']['open']['no_quote_rate'])}", f"{P(g['claude']['unsupported']['share'], 2)} / {P(g['open']['unsupported']['share'], 2)}",
                        f"{s['variant_keys']['shared']} of {s['variant_keys']['union']} ({s['variant_keys']['jaccard_pooled']:.2f})", f"${s['cost_usd']['claude_median_per_paper']:.2f} / ${s['cost_usd']['open_median_per_paper']:.2f}",
                        f"{s['wall_seconds']['claude_median'] / 60:.0f} / {s['wall_seconds']['open_median'] / 60:.0f}"])
    ow_tbl = table(["Disease", "Papers", "Values with no quote at all (Claude / open)", "Values judged unsupported by the second read (Claude / open)", "Variants found by both (shared of union; Jaccard)",
                    "Median cost per paper (Claude estimate / open, reported)", "Median minutes per paper (Claude / open)"], ow_rows)
    cand_tbl = table(["Disease", "Variant, normalized (predicted protein change)", "As written in the paper", "Papers", "Individuals", "What the authors called it"], example_candidates(D))
    next_tbl = table(["Step", "Who", "Effort", "What it unlocks"], [
        [f"Rate the {n_o1}-claim audit sample on the blinded pages, two raters and a tie-breaker", "Two panel members, then a third", "roughly 10 to 15 hours per rater", "The primary outcome; the first true accuracy figure for the frozen pipeline; how well the gatekeeper tracks human judgement"],
        ["Rate a blinded sample of the open-weight model's output at the same sitting", "The same raters", "a few hours", "A neutral Claude-versus-open-model comparison instead of a model grading models"],
        ["Decide on institutional or text-mining access to paywalled papers", "Dr. Lin (a deviation from the frozen plan)", "a decision, then about $600 to $900 of model time to read roughly 300 more papers", "Completeness; recovery of OMIM's and the catalogues' source papers; a less lower-bound gap count"],
        [f"Adjudicate the {N(live)} candidates from their dossiers; sign off; draft submissions", "The panel, then Dr. Lin", "roughly 10 to 15 minutes per candidate, 35 to 55 hours in all", "ClinVar literature-only submissions and OMIM candidates: the gap-closure deliverable"],
        ["Fill four comparator sheets from natural-history cohorts, without looking at our frequencies", "One person", "1 to 2 hours per sheet", "The ascertainment-bias arm: how far literature-derived frequencies sit from cohort truth"],
        ["Push the pre-registration tags and register on OSF; send the drafted messages to Monarch and ClinVar", "Dr. Lin", "under an hour", "A public timestamp on the frozen plan; the outreach promised for Month 1"],
    ])

    md = f"""# GP-RareLink in brief: reading the rare-disease literature with a language model, and checking its work

## Interim highlights for internal review (version 3)

*Rare Genomics Institute and the Stanford Open Virtual Assistant Lab. PI: Dr. Jimmy Lin. Methods co-lead: Prof. Monica Lam. Adjudication panel: Drs. Eva Wu, Gabriela Balderrama and Anita Chacko. Funded by Anthropic's AI for Science program. Drafted by Claude Code on {today} from the repository's committed outputs (commit `{D['commit']}`), for readers who are new to the field. Version 2 of the interim report (58 pages, 2026-10-28) holds every table, interval and method; this version keeps the parts that matter most and says plainly what they mean. Internal review only; not for distribution.*

> **Six things to take away**
>
> 1. **It runs at scale, with receipts.** {N(t['papers'])} open-access papers on six rare diseases became {N(t['phenopackets'])} standard patient records, {N(t['with_variant'])} of them carrying a variant in the disease gene. Every value points to a quote from its paper, and every one of {N(t['claims_all'])} quotes was found there word for word.
> 2. **Accuracy is promising but not yet proven.** A second model read judged {P(t5['unsupported'] / t5['model_claims'], 2)} of values unsupported across the five confirmatory diseases ({P(t['unsupported'] / t['model_claims'], 2)} with the development disease included). The only human-rated figures, from the pilot before the pipeline was frozen, were {P(a1['share'])} and {P(a2['share'])}. The decisive {n_o1}-claim human audit is built and waiting for raters.
> 3. **What limits completeness is what we are allowed to read.** Only {P(cov_lo, 0)} to {P(cov_hi, 0)} of each disease's papers have open full text. We recovered {rec_all['k']} of the {rec_all['n']} variants OMIM lists for these diseases ({P(rec_all['share'], 0)}); nearly all the misses are variants whose source papers we could not read or that our searches never returned.
> 4. **The database gap is real and sizeable.** The papers yielded {N(placed)} distinct variants placed on the genome. {N(live)} are in neither ClinVar nor OMIM, each with an evidence dossier, waiting for the panel. {reclass} more sit in ClinVar as uncertain or conflicting while the papers call them pathogenic.
> 5. **A cheaper open model finds the same variants but drops the receipts.** DeepSeek-V4.1-Flash and Claude found the same variants {ow['ha20']['variant_keys']['jaccard_pooled']:.0%} to {ow['ssadh']['variant_keys']['jaccard_pooled']:.0%} of the time (shared over union) at about 1/{cost_ratio:.0f} of the cost, but left {P(ow['ssadh']['span']['open']['no_quote_rate'], 0)} to {P(ow['ha20']['span']['open']['no_quote_rate'], 0)} of its values with no quote and was judged unsupported {P(owg['ssadh']['open']['unsupported']['share'], 1)} to {P(owg['ha20']['open']['unsupported']['share'], 1)} of the time, against Claude's {P(owg['ha20']['claude']['unsupported']['share'], 1)} to {P(owg['ssadh']['claude']['unsupported']['share'], 1)}.
> 6. **It has been cheap so far.** About ${b['total']:,.0f} of the $45,000 award by this session's own cost readings to {b['reading_at'][:10]}{f', plus about ${abl:,.0f} for a separate exploratory pilot not covered here' if abl else ''}. The expensive parts, human rating and adjudication, are the ones that have not happened.

## 1. The problem, in one page

When a child with a rare disease finally gets a genetic diagnosis, the variant responsible is often reported in a case report and then forgotten. A laboratory testing the next child searches ClinVar, the public database of variant classifications, and finds nothing, because nobody ever submitted the 2011 paper's finding. The family's diagnostic odyssey continues. For Alexander disease alone, a 2024 review counts 182 causative variants in 550 published patients, against {D['clinvar']['axd']['plp']} pathogenic or likely-pathogenic ClinVar records for the gene (release {cv_date}).

The knowledge exists; it is scattered across thousands of papers, written in prose and tables that no database can query. Curating it by hand has never kept up, and there are thousands of rare diseases. The question this project asks is whether a large language model, reading with strict rules, can do the first pass: turn case reports into structured records of *which variant, in which person, with which clinical features*, each value tied to the sentence it came from, at an accuracy we can measure rather than assume. The method is SLIDERS, an evidence-first systematic-review approach from the Stanford OVAL lab, with Claude doing the reading.

Two design choices follow from "an accuracy we can measure". First, the databases we would like to fill, ClinVar and OMIM, are kept out of the model's sight and used only afterwards as an answer key. Second, the whole analysis plan was written down and frozen before the main run (pre-registered, 2026-10-20), so the numbers below are the ones we said we would report, not the ones that looked best.

**Table 1. Six terms used in this report.**

{glossary}

## 2. How the pipeline works

![Figure 1]({figs['fig1']})

**Figure 1. The workflow, with the numbers from the six-disease run.** The reading side (blue) never sees the answer key (grey). Steps that need people (orange) have not started.

Five rules shape everything the pipeline does:

- **Quote everything.** A value with no verbatim quote from the paper is not allowed. A script then looks up every quote in the paper text; a quote that cannot be found is a failure, not a near miss.
- **"Not reported" is a valid answer.** Clinical features are recorded in three states: observed, explicitly excluded, or not reported. A paper's silence is never turned into a "no".
- **Read twice.** A second model pass (the gatekeeper) re-reads every value against its quote and asks whether the quote really supports it for that person. Claims it rejects are dropped before records are built. It is a filter, not a referee: a model checking a model can share the model's blind spots, which is why a human audit is the primary outcome.
- **Keep the answer key behind a firewall.** Code that reads papers cannot read ClinVar or OMIM; a test in the repository fails if it ever could. Comparisons happen in a separate harness afterwards.
- **Decide the rules first.** The prompts, forms and analysis plan were frozen after a one-disease pilot. Changes since are logged as numbered deviations; the ones that matter here are per-disease instantiation of the frozen prompt, a catalogue that arrived after extraction, per-disease settings for building records, and a transcript-isoform rule described in section 5.

The output for each individual is a GA4GH phenopacket: features as HPO terms with their three-state status, the variant written in HGVS on a named transcript and placed on the genome by VariantValidator, the paper's PMID, and the quoted evidence. Where the same person appears in several papers, records are merged only on an explicit citation, never on a resemblance.

## 3. What we ran

Six diseases were chosen to span inheritance modes and organ systems, all absent from the main public collection of phenopackets. A20 haploinsufficiency (HA20) was used to develop and pilot the pipeline, so its numbers are flagged throughout and the five others form the confirmatory set. Only open-access papers were read, by decision: no institutional subscriptions. The corpus came from PubMed searches, screening by model with a logged reason per record, and full-text screening with a verbatim evidence quote for every call.

**Table 2. The six diseases at a glance.** HA20\\* is the development disease. "Placed on the genome" means the variant could be written unambiguously on the GRCh38 reference, which is what makes it comparable with ClinVar. ClinVar counts are from the release of {cv_date}.

{diseases_tbl}

## 4. What we found

### 4.1 The receipts hold, but the decisive check has not happened

Every one of the {N(t['claims_all'])} quoted values was found verbatim in its paper. The gatekeeper then judged {N(t['model_claims'])} model claims and found {N(t['unsupported'])} unsupported: {P(u6[0], 2)} to {P(u6[1], 2)} as a 95% interval, and {P(u5[0], 2)} to {P(u5[1], 2)} on the five confirmatory diseases. Unsupported claims cluster in a few papers per disease, and the commonest cause is specific: a relative's or a cited patient's variant written into the proband's row from a sentence that mentions both. Running a tenth of the papers a second time ({rep_papers} papers) gave the same checklist answers {P(chk_lo, 0)} to {P(chk_hi, 0)} of the time and the same variants {P(var_lo, 0)} to {P(var_hi, 0)} of the time; where the two runs differed, it was mostly over how many individuals a cohort paper describes.

![Figure 2]({figs['fig2']})

**Figure 2. The machine's reading of its own errors is far below the humans' reading from the pilot.** Blue: the share of values the gatekeeper judged unsupported in each disease run. Orange: the share two human audits found unsupported in the pilot's output, before the fixes those audits produced were frozen into the pipeline. The pre-registered target is under 2%.

That is the good news, and here is the caveat that governs it. In the pilot, two audits of 50 claims each, rated by a person ({a2['n']} rated in the second), found {P(a1['share'])} and {P(a2['share'])} of values unsupported while the gatekeeper of the day found under 0.4%. The gatekeeper has been improved since and the pipeline was fixed for the error classes those audits exposed, but nothing has been re-audited by a person. The pre-registered test is a blinded audit of {n_o1} claims by two panel members, pass if at most 4 are unsupported. The sample is drawn, the rating pages are built, and no claim has been rated. Until that happens, the {P(t5['unsupported'] / t5['model_claims'], 2)} is a filter's reading, not an accuracy.

### 4.2 We find what we can read

How complete are the records? Two independent checks say the same thing. Against two published expert catalogues, the pipeline recovered {comp_ha20['k']} of {comp_ha20['n']} variants whose source paper it had read for HA20 and {comp_axd['k']} of {comp_axd['n']} for Alexander disease. Against OMIM, whose twelve entry pages for these diseases were frozen on {om['date']} and used as a human-curated holdout, it recovered {CIp(rec_all, 0)} of the variants OMIM lists, from {P(rec[best_rec]['share'], 0)} for {SHORT[best_rec]} down to {P(rec[worst_rec]['share'], 0)} for {SHORT[worst_rec]}.

![Figure 3]({figs['fig3']})

**Figure 3. Coverage, not reading, sets the ceiling.** **A** For each disease, the share of its papers we could read (open access) beside the share of OMIM's listed variants we recovered. **B** Of the {src_all} papers OMIM cites as the sources for those variants, where each stands in our corpus.

The pattern in Figure 3 is the main lesson of the OMIM check. Where OMIM's source paper was one we had read, the variant was in our records {restricted_k} times out of {restricted_n}, and the misses have named causes (a table scrambled in PDF conversion; a variant stated only in prose, "a glycine to an arginine at amino acid 169", which the record keeps verbatim but cannot place). Where it was not, the cause was access or search: {paywalled} of the {src_all} source papers sit in our corpus behind a paywall, and {notfound} were never returned, mostly pre-1990 descriptions under earlier names for the disease, before its gene was known. Tangier disease, whose OMIM variants all come from closed gene-discovery papers of 1999 to 2003, is the extreme case. Everything downstream, the completeness figures and the gap count, is therefore a lower bound set by open access.

### 4.3 Hundreds of published variants are in neither database

Across the six diseases the papers yielded {N(placed)} distinct variants that could be placed on the genome. {N(in_clinvar)} are in ClinVar, {N(plp)} of them classified pathogenic or likely pathogenic. {N(absent)} are not in ClinVar at all; after dropping those whose only evidence failed the gatekeeper, checking each against OMIM's lists, and withdrawing one that turned out to be our own normalization error, {N(live)} candidates remain. Each has a dossier: every paper reporting it, every quote, the individuals, the authors' own classification, and model-written flags for the panel (possible duplicates of the same patient, carriers, notation conflicts).

![Figure 4]({figs['fig4']})

**Figure 4. Where the variants we found stand in ClinVar.** Each bar is one disease's genome-placed variants. The orange segment is the candidate list awaiting adjudication.

**Table 3. One candidate per disease, the one reported in the most papers.** These are examples, not a ranking; nothing has been adjudicated.

{cand_tbl}

A second list is quieter but may matter as much: {reclass} variants that papers classify as pathogenic sit in ClinVar as uncertain or conflicting, {reclass_strong} of them with evidence the harness judged strong enough to propose a reclassification. Both lists are candidates. Nothing is submitted anywhere without the panel's adjudication and Dr. Lin's sign-off.

### 4.4 A cheaper open model finds the same variants and loses the receipts

The same papers, prompts, forms and scoring were run on an open-weight model, DeepSeek-V4.1-Flash, for two diseases, to answer a question the grant promised to answer either way: does the method depend on the model?

**Table 4. Claude Opus against an open-weight model on identical inputs.** The open model's cost is the host's reported price; Claude's is an estimate from usage readings. Unsupported rates come from the same gatekeeper, which is itself Claude, so the comparison is not neutral until the planned blinded human audit of both outputs is done.

{ow_tbl}

The open model found nearly the same set of variants at about 1/{cost_ratio:.0f} of the cost and {time_ratio:.0f} times the wall-clock. What it lost was provenance: {P(ow['ssadh']['span']['open']['no_quote_rate'], 0)} to {P(ow['ha20']['span']['open']['no_quote_rate'], 0)} of its values came with no quote at all, which the rules forbid, and the gatekeeper rejected {P(owg['ssadh']['open']['unsupported']['share'], 1)} to {P(owg['ha20']['open']['unsupported']['share'], 1)} of its claims. If the human audit confirms the gatekeeper's reading, the practical lesson is that the same provenance rules bind differently on different models, and that quote-level provenance is the cheapest place to see it.

### 4.5 The model did not recall the papers from memory

A model that has seen a paper during training could "extract" facts it remembers rather than facts it reads, and the answer key would then be contaminated from the other side. {mem_papers} papers were probed, stratified by publication date around the model's training cutoff, with two tests: asked about each paper without its text, and asked to continue a passage. In the {after_c['papers']} papers published after the cutoff, neither Claude nor the open model produced a single specific recall or a correct variant ({after_c['cb_variant_hits']} and {after_o['cb_variant_hits']} variant hits), and the continuation test found no verbatim runs. The probe is small and will grow as post-cutoff papers accumulate, but it gives no sign of memorization.

## 5. What this means

**On accuracy.** The pipeline produces records with complete provenance, stable across repeat runs, with a second model read that removed {N(dropped)} claims before the records were built. What it has not yet produced is a human-rated error rate for the frozen pipeline. The pilot's audits found roughly 6% where the machine found under 0.4%, and each exposed an error class the pipeline now guards against; whether the guards worked is exactly what the {n_o1}-claim audit measures. That audit is the single most valuable thing the project can do next, and it costs no model time.

**On coverage.** Reading is not the bottleneck; access is. With {P(cov_lo, 0)} to {P(cov_hi, 0)} of each corpus open, the completeness figures and the candidate list are lower bounds, and the diseases whose founding literature is oldest and most closed (Tangier, LAD-I) are the ones the databases most need. A decision on institutional or text-mining access would change these results more than any change to the model.

**On the answer key.** Databases curated by people deserve the same scrutiny as records written by a machine. OMIM lists selected examples rather than a catalogue, so recall against it is meaningful and precision is not. Two of its entries link to ClinVar records that contradict their own text, and its labels use legacy numbering. In the other direction, the OMIM check caught one of our candidates as a normalization artefact: a deletion reported on an alternative exon of *LAMP2* that we had placed on the standard transcript, producing a genomic position no database holds because it was not what the paper reported. The fix, letting the paper's own words choose the transcript, is now in the pipeline. Scoring against two independent references found an error that scoring against one could not.

## 6. What happens next

The order below puts the no-cost human steps first, holds any change to the frozen pipeline until the audit gives a measured failure rate, and leaves adjudication, the longest task, for the months the plan assigned to it.

**Table 5. Next steps, who does them, and what each unlocks.** Hours are estimates; no time per claim has been measured yet.

{next_tbl}

Spend to {b['reading_at'][:10]} was about ${b['total']:,.0f} of the $45,000 award, by this session's own usage readings rather than billing figures{f', with about ${abl:,.0f} more for an exploratory pilot run in a separate session that this report does not cover' if abl else ''}. Extraction and the second read on all six diseases account for about ${sum(l['spent'] for l in b['lines'] if l['n'] in ('1', '2')):,.0f} of that; the open-weight runs cost ${D['ow_manifest']['ha20']['key_spend_both_runs_usd']['spent']:.0f} outside the award.

## 7. How to read these numbers

- **No accuracy claim is made for the frozen pipeline.** Every error rate in section 4.1 is a model's reading of a model's output; the human figures are from the pilot.
- **HA20 developed the pipeline.** Its rules were tuned on its own papers, so five-disease figures are the ones to quote.
- **Open access only.** Completeness, recall and the gap count are measured on what could be read.
- **OMIM is a sample.** Recall against its listed variants is meaningful; "precision against OMIM" is not, and OMIM's phenotype descriptions were not assessed.
- **Costs are estimates** from session usage readings, not invoices.
- **The author of this draft built the pipeline.** Claude Code wrote the code, ran it and generated this report from its outputs. The numbers are reproducible from the committed files; the framing is not independent of the system it describes, which is one more reason the human audit decides.

## 8. Where the details are

Version 2 of the interim report (`reports/interim_paper/`) has every table, interval, per-disease section, the seventeen-item gap list with costs, and the supplement. The frozen plan is `preregistration/analysis_plan.md` (v1.0, tags `prereg-v1.0` and `pipeline-v1.0`). Decisions and deviations are numbered in `DECISIONS.md`; spend by budget line is in `BUDGET.md`. The records are in `data/extracted/<disease>/pv1-<disease>/phenopackets/`, the candidate dossiers in `adjudication/o3_gaps/`, and this document regenerates with `uv run python -m analysis.interim_paper.build_v3`.
"""
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "interim_paper_v3.md").write_text(md)
    (OUT / "README.md").write_text(f"""# Interim paper, version 3 (short highlights; internal review)

- `interim_paper_v3.md`: the text, five tables and four figures, written for readers new to the field.
- `interim_paper_v3.pdf`: rendered (`bash analysis/interim_paper/make_pdf_v3.sh`).
- `figures/`: PNG figures.

Generated on {today} at commit `{D['commit']}` by `uv run python -m analysis.interim_paper.build_v3`. Every number is read from the same files as version 2 (`reports/interim_paper/`, Supplementary Table S1). Version 2 is the full report; this one is the short one. Nothing here is published.
""")
    print(f"wrote {OUT / 'interim_paper_v3.md'} ({len(md):,} chars); figures: {len(figs)}")


if __name__ == "__main__":
    main()
