"""Export the deep-dive deck spec (slides, tables, figures and narration) for the long collaborator video.

The deck follows the full interim report (version 2) section by section. Every number is read from
`analysis.interim_paper.data.load()`, the same files as the papers; the prose lives here. Output:
analysis/dashboard/deep_dive_data.json, rendered by deck_long.js and narrated by build_video.py.

  uv run python -m analysis.dashboard.export_deep_dive
"""
from __future__ import annotations

import json
import re
from datetime import date
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from PIL import Image

from analysis.interim_paper.data import CONFIRMATORY, DISEASES, GENE, INHERITANCE, NAME, ROOT, SHORT, SYSTEM, load
from analysis.interim_paper.figures_v3 import release_date
from analysis.interim_paper.stats import clopper_pearson

OUT = ROOT / "analysis/dashboard/deep_dive_data.json"
PAGES_URL = "https://cjimmylin.github.io/gp-rarelink/"
FIG_V2 = ROOT / "reports/interim_paper/figures"
FIG_V3 = ROOT / "reports/interim_paper_v3/figures"


def pct(x, nd=1):
    q = Decimal(1).scaleb(-nd)
    return str(Decimal(str(100 * x)).quantize(q, rounding=ROUND_HALF_UP))


def N(x):
    return f"{int(x):,}"


def kn(r, nd=0):
    """'57% (43 of 75)' for a {k, n, share} record."""
    return f"{pct(r['share'], nd)}% ({r['k']} of {N(r['n'])})"


def spoken_kn(r, nd=0):
    return f"{pct(r['share'], nd)} percent, {r['k']} of {N(r['n'])}"


def ablation_cost():
    m = re.search(r"SLIDERS ablation pilot \(D-44[^\n]*?\*\*\$([\d,.]+) by helper tokens", (ROOT / "BUDGET.md").read_text())
    return float(m.group(1).replace(",", "")) if m else None


def fig(path: Path):
    w, h = Image.open(path).size
    return {"path": str(path), "w": w, "h": h}


def main():
    D = load()
    t, t5 = D["totals"]["all"], D["totals"]["five"]
    om = D["omimh"]
    cv = D["clinvar"]
    run, rep, s4, rc, gaps, o2 = D["run"], D["repeat"], D["stage4"], D["reconcile"], D["gaps"], D["o2"]
    placed = sum(gaps[d]["tier1_alleles"] for d in DISEASES)
    in_clinvar = sum(D["o2_tiers"][d].get("1", 0) for d in DISEASES)
    plp = sum(v for d in DISEASES for k, v in D["o2_tier1_classes"][d].items() if k in ("P", "LP", "P/LP"))
    absent = placed - in_clinvar
    live = t["gap_candidates_live"]
    rec = {d: om["per"][d]["B_allelic_variants"]["recall_unrestricted_strict"] for d in DISEASES}
    rec_all = om["totals"]["recall_all_strict"]
    cov = {d: D["coverage"][d] for d in DISEASES}
    a1, a2 = D["poc"]["audit1"]["unsupported_strict"], D["poc"]["audit2"]["unsupported_strict"]
    u5 = clopper_pearson(t5["unsupported"], t5["model_claims"])
    dropped = {d: sum(v for k, v in D["build"][d]["counts"].items() if k.startswith("gk_dropped")) for d in DISEASES}
    dropped_all = sum(dropped.values())
    merges_all = sum(s4[d]["merged_pairs"] for d in DISEASES)
    rep_papers = sum(rep[d]["papers_compared"] for d in DISEASES)
    rep_same = sum(rep[d]["individual_count_matches"] for d in DISEASES)
    cv_date = release_date(cv["axd"]["release"])
    src_all = sum(om["per"][d]["A_literature"]["av_source_pmids"] for d in DISEASES)
    src_ex = sum(om["per"][d]["A_literature"]["av_source_pmids_extracted"] for d in DISEASES)
    restricted_n = sum(om["per"][d]["B_allelic_variants"]["restricted_denominator_source_paper_extracted"] for d in DISEASES)
    restricted_k = sum(om["per"][d]["B_allelic_variants"]["recall_restricted_in_source_paper_strict"]["k"] for d in DISEASES)
    funnel = {}
    for d in DISEASES:
        for st, n in om["per"][d]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {}).items():
            funnel[st] = funnel.get(st, 0) + n
    fa = om["totals"]["funnel_all_diseases"]
    jt = om["judg_tally"]
    ow, owg = D["ow"], D["ow_gk"]
    mem_c, mem_o = D["mem"]["claude"]["by_stratum"], D["mem"]["open"]["by_stratum"]
    mem_papers = sum(v["papers"] for v in mem_c.values())
    tri = D["triage"]
    gp = D["gpsea"]["diseases"]
    ts = D["tangier_share"]
    b = D["budget"]
    abl = ablation_cost()
    comp = D["completeness"]
    cost_ratio = round(ow["ha20"]["cost_usd"]["claude_median_per_paper"] / ow["ha20"]["cost_usd"]["open_median_per_paper"])
    time_ratio = round(ow["ha20"]["wall_seconds"]["open_median"] / ow["ha20"]["wall_seconds"]["claude_median"])
    screened_all = sum(cov[d]["manifest_rows"] for d in DISEASES)
    corpus_all = sum(cov[d]["in_corpus"] for d in DISEASES)
    open_all = sum(cov[d]["fulltext"] for d in DISEASES)
    o2a = {d: o2[d]["all_papers"] for d in DISEASES}

    figures = {
        "workflow": fig(FIG_V3 / "fig1_workflow.png"), "checks": fig(FIG_V3 / "fig2_checks.png"), "coverage3": fig(FIG_V3 / "fig3_coverage.png"), "gaps3": fig(FIG_V3 / "fig4_gaps.png"),
        "corpus": fig(FIG_V2 / "fig2_corpus.png"), "gatekeeper": fig(FIG_V2 / "fig3_gatekeeper.png"), "repeat": fig(FIG_V2 / "fig4_repeat.png"), "records": fig(FIG_V2 / "fig5_records.png"),
        "concordance": fig(FIG_V2 / "fig6_concordance.png"), "gaps": fig(FIG_V2 / "fig7_gaps.png"), "openweight": fig(FIG_V2 / "fig8_openweight.png"), "memorization": fig(FIG_V2 / "fig9_memorization.png"),
        "budget": fig(FIG_V2 / "fig10_budget.png"), "omim": fig(FIG_V2 / "fig11_omim.png"), "spectrum": fig(FIG_V2 / "figS2_variant_spectrum.png"), "completeness": fig(FIG_V2 / "figS5_completeness.png"),
        "gpsea": fig(FIG_V2 / "figS6_gpsea_danon.png"), "misses": fig(FIG_V2 / "figS7_o2_misses.png"), "concentration": fig(FIG_V2 / "figS1_concentration.png"),
    }

    def lab(d):
        return SHORT[d] + ("*" if d == "ha20" else "")

    S = []  # slides

    def add(type_, title, narration, **kw):
        S.append({"type": type_, "title": title, "narration": re.sub(r"\s+", " ", narration).strip(), **kw})

    # ------------------------------------------------------------------ Part 0: opening
    add("title", "Reading the rare-disease literature with a language model, and checking its work",
        "Welcome to the GP-RareLink deep dive. This is the long version of the project overview: about three quarters of an hour, following the full interim report section by section. "
        "GP-RareLink is run by the Rare Genomics Institute with the Stanford Open Virtual Assistant Lab and funded by Anthropic's AI for Science program. "
        "The project reads published case reports on six rare genetic diseases with a language model, turns them into structured per-individual records in which every value carries a quote from its source, "
        "and then checks those records against ClinVar and OMIM, which the model never sees. What you will hear is an interim report for internal review. The numbers are real and traceable; the conclusions are provisional, and the report says plainly which questions remain open.",
        kicker="GP-RareLink · deep dive for collaborators", subtitle=f"Interim report, version 2, in about 45 minutes · {date.today().isoformat()}",
        note="Rare Genomics Institute with the Stanford Open Virtual Assistant Lab · funded by Anthropic's AI for Science program · internal review")
    add("bullets", "What this talk covers",
        "The talk has four parts. Part one sets out the problem and the question, and the five outcomes we committed to measure before the main run. Part two walks through the methods: how the corpus was built, how the model reads a paper, how every value is checked twice, how records are made, and how the answer key is kept behind a firewall. "
        "Part three is the results, in the order of the report: the corpus, extraction and the gatekeeper, stability, the records, the human audit that has not yet happened, concordance with ClinVar, the OMIM holdout, the gap candidates, the bias arm, the open-weight comparison, the exploratory analyses, one slide per disease, and spend. "
        "Part four is what it all means, the gaps in the study and a costed plan to close them, and what we are asking of you. If you prefer to read, the dashboard has the eight-page paper and the full report with every table and interval.",
        bullets=["Part 1. The problem, the question, and the five pre-registered outcomes", "Part 2. Methods: corpus, extraction, two checks on every value, records, the firewall and the harness",
                 "Part 3. Results, in the report's order: corpus, gatekeeper, stability, records, the unrated audit, ClinVar, OMIM, gap candidates, bias and memorization, the open-weight model, exploratory analyses, each disease, spend",
                 "Part 4. What it means, the gaps and a costed plan, and what we need from you", "Everything here is on the dashboard: the papers, this deck with its notes, the candidate list and the input form"])

    # ------------------------------------------------------------------ Part 1
    add("section", "Part 1. The problem and the question", "Part one. The problem and the question.", kicker="GP-RareLink deep dive")
    add("bullets", "A variant published once, and then lost",
        f"Here is the problem in one example. For Alexander disease, a 2024 review counts 182 distinct causative variants in 550 published patients. ClinVar, the public database laboratories query when they interpret a test, holds {cv['axd']['plp']} pathogenic or likely pathogenic records for the gene in the release of {cv_date}. "
        "The rest were published, once, and never submitted. A laboratory testing the next child searches ClinVar and finds nothing. The knowledge exists, but it is scattered across thousands of papers in prose and tables that no database can query, and hand curation has never kept up. "
        "The project asks whether a language model, reading with strict rules, can do the first pass of curation at an accuracy we can measure rather than assume, and whether that closes a meaningful part of the gap.",
        bullets=[f"Alexander disease: 182 causative variants in 550 published patients (2024 review) against {cv['axd']['plp']} pathogenic or likely-pathogenic ClinVar records for GFAP (release {cv_date})",
                 "Knowledge sits in ClinVar and OMIM for variants, HPO for phenotype vocabulary, Monarch's phenopacket store for a few cohorts, and in case reports for most individual patients",
                 "A lab querying ClinVar today cannot see a causative variant published in 2011 that was never submitted; that family's diagnostic odyssey continues",
                 "Too many diseases to curate by hand; the need recurs every time a team meets a disease nobody has curated",
                 "The question: can the SLIDERS method, powered by Claude, build variant-phenotype-disease records from case reports at an accuracy we can prove, at a scale that materially closes the gap?"])
    add("cards", "Three design choices that make the answer checkable",
        "Three design choices make the answer checkable. First, quote everything: a value without a verbatim quote from the paper is not allowed, a script confirms every quote is really in the text, and not reported is a valid answer, so a paper's silence is never turned into a no. "
        "Second, hold out the answer key: ClinVar and OMIM are never shown to the model, code that reads papers cannot read them, a test in the repository fails if it could, and the comparison happens afterwards in a separate harness. "
        "Third, decide the rules first: the prompts, the forms and the analysis plan were frozen on the twentieth of October 2026, after a one-disease pilot, and every change since is logged as a numbered deviation approved by the principal investigator.",
        numbered=True, cards=[["Quote everything", "A value with no verbatim quote is not allowed. A script looks up every quote in the paper. \"Not reported\" is a first-class answer; three-state phenotypes (observed, excluded, not reported) are never collapsed."],
                              ["Hold out the answer key", "ClinVar and OMIM are never shown to the model. Code that reads papers cannot read reference data; an automated test fails if it could. Comparisons run afterwards in a separate harness."],
                              ["Decide the rules first", "Prompts, forms and the analysis plan were frozen on 2026-10-20 after a one-disease pilot (tags prereg-v1.0 and pipeline-v1.0). Changes since are numbered deviations approved by the PI."]])
    add("table", "Five pre-registered outcomes, and where each stands",
        f"The plan registers five outcomes. O1, the only confirmatory one, is a human audit of {D['o1']['n']} extracted values against their quoted evidence; it passes if at most four are unsupported. The sample is drawn and the blinded rating pages are built, but no claim has been rated. "
        "O2 is concordance with ClinVar and OMIM on gene, variant, classification and phenotype, reported as estimates with intervals and no pass or fail. The ClinVar half is done for all six diseases and the OMIM half was done on the twenty-eighth of October against frozen entry pages. "
        f"O3 is gap closure: {live} candidates are listed with dossiers, none adjudicated. O4 is ascertainment bias against natural-history cohorts, with a memorization probe; the probe is done, the frequency comparison waits on a person. O5 is efficiency and the comparison with an open-weight model; the run and gatekeeper are done on two diseases, the blinded audit is not.",
        head=["#", "Outcome", "Type", "Pre-specified target", "Status"], colW=[0.5, 3.0, 1.5, 1.9, 2.1], fontSize=10,
        rows=[["O1", f"Unsupported-value rate, human audit of {D['o1']['n']} claims", "primary, confirmatory", "under 2%: at most 4 of 250 (rule C)", "sample drawn, pages built; no claim rated"],
              ["O2", "Concordance with ClinVar and OMIM: gene, HGVS, classification, phenotype", "primary, estimation", "none; estimates with intervals", "ClinVar done (6 diseases); OMIM variant half done 2026-10-28; OMIM phenotype half not assessed"],
              ["O3", "Gap closure: variants absent from both databases, adjudicated, submitted", "primary, descriptive", "counts by stage", f"{live} candidates with dossiers; adjudication not started"],
              ["O4", "Ascertainment bias vs natural-history cohorts; memorization probe", "secondary", "none", "probe done (both models); frequency deviation waits on a person"],
              ["O5", "Expert-minutes per record; Claude vs open-weight model", "secondary", "none", "open-weight run and gatekeeper done (2 diseases); blinded audit and minutes not measured"]],
        note="Only O1 has a pass/fail rule. Headline pooled figures use the five diseases other than HA20, the development disease.")

    # ------------------------------------------------------------------ Part 2: methods
    add("section", "Part 2. Methods", "Part two. Methods.", kicker="GP-RareLink deep dive", subtitle="Corpus · extraction · two checks on every value · records · the firewall and the harness · outcomes and statistics · the pilot and the deviations")
    add("table", "Six diseases, six organ systems, four inheritance modes",
        "The six diseases were chosen to span inheritance modes and organ systems, and all are absent from the main public collection of phenopackets. A20 haploinsufficiency is autosomal dominant and auto-inflammatory; SSADH deficiency is recessive and neurometabolic; Tangier disease is recessive and a lipid disorder; "
        "leukocyte adhesion deficiency type one is recessive and immunological; Alexander disease is dominant, usually de novo, and a leukodystrophy; Danon disease is X-linked and cardiac and neuromuscular. "
        "The ClinVar counts are distinct variants on single-gene records in one dated release, and the OMIM counts are the allelic variants on each gene's entry page, frozen on the twenty-eighth of October. OMIM calls its list selected examples, so it is a sample, not a catalogue. "
        "A20 haploinsufficiency was the development disease: every extraction rule was tuned on it during the pilot, so its results flatter the pipeline and the other five form the confirmatory set.",
        head=["Disease", "Gene", "Inheritance", "System", f"ClinVar records; P/LP; VUS ({cv_date})", "OMIM allelic variants (gene entry)"], colW=[2.2, 0.9, 1.3, 1.5, 1.9, 1.2], fontSize=10,
        rows=[[NAME[d] + (" (development)" if d == "ha20" else ""), GENE[d], INHERITANCE[d], SYSTEM[d], f"{N(cv[d]['total'])}; {cv[d]['plp']}; {cv[d]['vus']}", f"{rec[d]['n']}"] for d in DISEASES],
        note="ClinVar: distinct VariationIDs on single-gene GRCh38 records; P/LP sums Pathogenic, Likely pathogenic and Pathogenic/Likely pathogenic. OMIM lists \"selected examples\", not an exhaustive catalogue.")
    add("bullets", "Building the corpus",
        f"The corpus came from PubMed searches from inception to a recorded date, gene symbol plus disease names and synonyms, with backward citation searching of the key reviews. No ClinVar or OMIM citation lists were used as seeds for the five new diseases. "
        "Screening ran in two passes: title and abstract screening by model helpers with a logged reason per record, then full-text screening of every open full text with a verbatim evidence quote checked by script; a twenty-item human check settled the screening calls. "
        "Eligible papers report individual-level genotype or phenotype for at least one person with the disease; reviews with a per-patient table are included and their people tagged as secondary-source. "
        f"Access was open access only: PubMed Central, Europe PMC and open copies found through Unpaywall, with no institutional subscriptions. In all, {N(screened_all)} records were screened, {N(corpus_all)} entered the corpus, and {N(open_all)} had open full text. Natural-history papers for the bias arm were held out of the extraction corpus.",
        figure="corpus", figureWidth=5.4, caption="The corpus funnel per disease: screened, in corpus, open full text, extracted.",
        bullets=["Search: PubMed from inception, gene symbol plus disease synonyms, backward citation searching of key reviews; no ClinVar or OMIM seeds for the five new diseases (D-19)",
                 "Screening: title/abstract by model helpers with a logged reason, then full-text screening with a verbatim quote checked by script; a 20-item human check (D-34)",
                 "Eligibility: individual-level genotype or phenotype for at least one person; reviews with per-patient tables included and tagged (D-33)",
                 f"Access: open access only (D-32). {N(screened_all)} records screened, {N(corpus_all)} in corpus, {N(open_all)} with open full text",
                 "Holdouts: natural-history comparator papers kept out of extraction (AxD 2, SSADH 1, Danon 2)"])
    add("bullets", "Extraction: one reader per paper, a quote per value",
        "Extraction runs as Claude Code helper agents on the funded account: one helper per paper, reading only the paper, the instruction file, the schema and the rules file, with no web access and an instruction to use nothing it remembers about the paper. "
        "The frozen files are the extraction instructions version six, a five-table schema covering publications, individuals, variants, phenotypic features and a phenotype checklist, a rules file, and the gatekeeper instructions version four. For the five new diseases the prompt and schema were instantiated by script, swapping only the disease name, the gene symbol, the schema path and a twenty-item checklist. "
        "Every asserted value carries a verbatim quote; not reported carries no quote; three-state phenotypes are never collapsed; variant fields are taken only from statements about this person; values stacked in multi-patient cells are never assigned by position; and a normal finding is recorded as the abnormality it rules out, marked excluded. "
        "Each disease has twenty disease-specific checklist features, each with a three-state status for every individual, written from a consensus guideline or review with every quote checked.",
        bullets=["Model and route: Claude Opus as Claude Code helper agents (claude-opus-5-5), one per paper; the helper sees only the paper, the instructions, the schema and the rules; no web access; no memory of the paper allowed",
                 "Frozen files: extract_v6, schema_<disease>_v5 (publications, individuals, variants, phenotypic_features, phenotype_checklist), extraction_rules_v1, gatekeeper_v4; per-disease instantiation swaps only name, gene, schema path and checklist (D-38)",
                 "What a value is: a verbatim quote for every asserted value; \"not reported\" is first class; three states never collapsed; variant fields only from statements about this person (D-29); no positional reading of stacked cells (D-31); a normal finding recorded as the abnormality excluded (D-27)",
                 "Checklists: 20 disease-specific features with three-state status per individual, written from a guideline or review, every quote checked verbatim"])
    add("bullets", "Two checks on every value: the span check and the gatekeeper",
        "Every value is checked twice. The span check is deterministic: it looks up every quoted span in the source text and demands a verbatim match, on all values, not a sample. A helper that left quotes empty was resumed for a repair-only pass, and each repair was diffed to show that only the target cells changed. "
        "The gatekeeper is a second model read. For each claim that is not bookkeeping, a helper asks whether the quote entails the value for the person the row is about. It records whom the quote is actually about, this person, a named group, the cohort, another person, the paper, or unclear, and gives one of four verdicts: supported, partially supported, unsupported, or span not found. "
        "No value is exempted because its text matches its quote. Phenopackets keep only claims judged supported, and the count removed is reported. One sentence from the plan matters more than any other here: the gatekeeper is a filter, not a measure. In the pilot its own unsupported rate understated the human audit's by an order of magnitude.",
        bullets=["Span check: every quoted span must occur verbatim in the source text; run on all values; repair-only resumes are diffed cell by cell",
                 "Gatekeeper v4: a second Claude read of each model claim in chunks of up to 350, asking whether the quote entails the value for this person",
                 "Records whom the quote is about: this person, a named group, the cohort in general, another person, the paper, unclear",
                 "Four verdicts: supported, partially supported, unsupported, span not found. No script match exempts a value (D-28)",
                 "Phenopackets keep only supported claims; the number removed is reported",
                 "The gatekeeper is a filter, not a measure: in the pilot it understated the human audit by an order of magnitude"])
    add("bullets", "From rows to records",
        "The extracted rows become records in four steps. Deduplication merges only on an explicit citation tying a person to an earlier report, one to one; the pilot's sex-and-onset route was dropped after it produced all six false merges of ninety-three. "
        "Normalization runs every variant through VariantValidator on the MANE Select transcript for the gene, keeps the original string beside the normalized form, flags transcripts that were assumed or version-mapped, and passes only normalization fields, never database annotations. "
        "Binding maps checklist items to HPO terms through per-disease maps built from a pinned HPO release, binds free-text features first by script and then by helpers with a lookup tool, and takes disease terms from Mondo by name, never through an OMIM cross-reference. "
        "The output is one GA4GH phenopacket per identity, validated against the schema, with per-disease settings for gene, transcript, Mondo term and checklist map.",
        bullets=["Deduplication (merge policy v4): merge only on an explicit citation to an earlier report, one-to-one; a listed duplicate-publication pair (SSADH preprint and journal version) uses a dedicated route",
                 "Normalization: VariantValidator 4.0.1, MANE Select transcript per gene; original string kept beside the normalized form; assumed or version-mapped transcripts flagged; only normalization fields enter, never database annotations",
                 "Binding: checklist items to HPO through per-disease maps from the pinned release (2026-09-01); free-text features by script then helpers with a lookup tool; disease terms from Mondo (2026-10-06) by name",
                 "Phenopackets: one GA4GH Phenopacket v2 per identity, schema-validated, per-disease settings (D-40)"])
    add("figure", "The whole workflow, with the six-disease numbers",
        "Putting it together: the five blue boxes are the reading side, run by the frozen pipeline. Papers go to one reader each; every value gets a quote; the script checks every quote; the gatekeeper re-reads every claim; the surviving claims become records. "
        "The dashed orange line is the firewall. Below it, in grey, is the answer key the reader never sees: a dated ClinVar release, the OMIM entry pages frozen on the twenty-eighth of October, and two published variant catalogues. The comparison harness reads the records and the answer key and lists what the databases are missing. "
        "The orange box on the right is what has not happened: the blinded human audit and the expert adjudication of the candidates. That is where you come in, and we will return to it at the end.",
        figure="workflow", caption="Blue: the reading side, run by the frozen pipeline. Grey: reference data and scoring, which only the harness reads. Orange: steps that need people.")
    add("bullets", "The firewall and the harness",
        "Ground-truth isolation is enforced, not promised. Code under the extraction package never reads reference data, and an automated test fails if any such path, loader, or even the tokens ClinVar, OMIM or harness appear there. Reference snapshots live outside the repository, and only their manifests and counts are committed. "
        "The harness reads the extracted records and the snapshots. For ClinVar that is the variant summary file of the twelfth of October release, restricted to single-gene records on the current genome build. For phenotypes it uses the HPO annotation file. Two published catalogues serve as completeness benchmarks, Chen 2020 for A20 haploinsufficiency and Grossi 2024 for Alexander disease; the other four candidate catalogues failed the registered suitability check. "
        "For OMIM, the principal investigator printed the six phenotype and six gene entry pages on the twenty-eighth of October; a harness script parses them, and each allelic variant was placed in ClinVar through ClinVar's own OMIM cross-references. OMIM's clinical synopsis pages were not frozen, so OMIM's phenotype half is not yet assessed.",
        bullets=["An automated test fails if code under pipeline/extract can reach reference data, or even contains the tokens \"clinvar\", \"omim\" or \"harness\"",
                 "Reference snapshots live outside the repository; only manifests and counts are committed",
                 f"ClinVar: variant_summary of the {cv_date} release, single-gene GRCh38 records per gene; the same release re-read on 2026-10-21 for the gap re-check",
                 "HPO annotations (phenotype.hpoa, 2026-09-02) for the phenotype-profile figure",
                 "Catalogues: Chen 2020 Table S1 for HA20 (D-30); Grossi 2024 Supplementary Table 2 for AxD (D-39); four other candidates failed the suitability check",
                 f"OMIM: twelve entry pages frozen by the PI on {om['date']} (D-42), parsed by the harness; allelic variants placed in ClinVar through ClinVar's OMIM cross-references; clinical synopses not frozen, so OMIM's phenotype half is \"not yet assessed\""])
    add("bullets", "Outcomes and statistics, as registered",
        f"The statistics follow the registered plan. For O1, {D['o1']['n']} claims were drawn by simple random sampling stratified by disease from the claims the gatekeeper judged supported, by script with a fixed seed and before any concordance was run. Two panel members rate blind on pages that never show the gatekeeper's verdict; a third resolves disagreements; the pass rule is at most four unsupported. "
        "For O2, tier one is the same genomic allele; tier two is the same protein change where a paper gives no cDNA. HGVS recall is the share of ClinVar's own paper-and-variant citation pairs, restricted to corpus papers, that the run extracted from that paper. Overlap is the share of extracted alleles present in ClinVar, which is not precision. Classification compares the authors' call with ClinVar's aggregate among stated values. Intervals are Wilson for proportions and exact for the audit and the gatekeeper shares. "
        "For O3, a gap candidate is a tier-one allele absent from the ClinVar snapshot, with identifying values the gatekeeper judged supported in at least one row, and, since the OMIM check, not listed among OMIM's allelic variants. For O4, a person lists each comparator's cohort frequencies before any literature frequency is computed. For O5, the open-weight model runs the same papers, prompts and scoring.",
        fontSize=11.5,
        bullets=[f"O1: {D['o1']['n']} claims, simple random sampling stratified by disease, seed 40250, drawn before any concordance; two blinded raters and a tie-breaker; pass if at most 4 unsupported (rule C); a value the rater cannot verify counts as unsupported",
                 "O2: tier 1 = same GRCh38 allele; tier 2 = same protein change where no cDNA is given. HGVS recall = share of ClinVar's (PMID, variant) citation pairs in corpus papers that the run extracted. Overlap = share of extracted tier-1 alleles present in ClinVar (not precision). Classification = authors' call vs ClinVar aggregate",
                 "O3: a gap candidate = tier-1 allele absent from the ClinVar snapshot, gatekeeper-supported in at least one row, and not among OMIM's allelic variants (D-42). Counted by stage: candidates, adjudicated, approved, drafted, signed off, submitted, accepted",
                 "O4: a person lists each held-out comparator's HPO-mappable features and cohort frequencies first; then observed ÷ (observed + excluded) per feature with a publication-cluster bootstrap. Memorization: closed-book recall and guided completion on 30 papers per disease, stratified by date against the training cutoff",
                 "O5: expert-minutes per accepted record (logged by the adjudication page); Claude vs DeepSeek-V4.1-Flash on identical papers, prompts, frozen files and scoring",
                 "Intervals: Wilson for simple proportions; exact Clopper-Pearson for the audit and the gatekeeper shares"])
    add("bullets", "The development pilot, and four deviations since the freeze",
        f"A one-disease pilot on A20 haploinsufficiency ran from the eighteenth to the twentieth of October: two full extraction runs, a fifteen-paper repeat, a hand check of every merge, two fifty-claim human audits by the principal investigator, ClinVar concordance and the Chen 2020 completeness check. Its findings set the rules frozen as extraction version six and gatekeeper version four. The disease was then re-extracted from scratch with the frozen pipeline; the pilot's own records are not used anywhere in the report. "
        "Four dated deviations followed, each approved before it took effect. D-38 instantiated the frozen prompt and schema per disease. D-39 transcribed the Alexander disease catalogue on the harness side after its supplement arrived late. D-40 made the record-building scripts read per-disease settings. "
        "And D-43, found through the OMIM holdout, added isoform-sensitive positions to normalization: where a gene has alternative coding exons and a paper names no transcript, the paper's own exon label chooses the transcript, or the variant gets no genomic key. We will see the case that forced it.",
        bullets=[f"Pilot on HA20, 2026-10-18 to 2026-10-20: two full runs, a 15-paper repeat, every merge hand-checked, two 50-claim human audits ({pct(a1['share'])}% and {pct(a2['share'])}% unsupported), ClinVar concordance, Chen 2020 completeness. HA20 then re-extracted from scratch with the frozen pipeline",
                 "D-38 (2026-10-20): frozen prompt and schema instantiated per disease by script (name, gene, schema path, checklist only)",
                 "D-39 (2026-10-20): the AxD catalogue's supplement arrived after extraction; transcribed on the harness side only",
                 "D-40 (2026-10-20): Stage 4 scripts read per-disease settings instead of HA20's hard-coded ones",
                 "D-43 (2026-10-28): isoform-sensitive positions in normalization (LAMP2 exons 9a/9b/9c, GFAP exon 7A); found through the OMIM holdout; the Danon run re-normalized and one candidate withdrawn",
                 "Decisions, not deviations: the SSADH preprint and journal version both stay with their patients merged; D-42 adopted the frozen OMIM pages as the OMIM reference"])

    # ------------------------------------------------------------------ Part 3: results
    add("section", "Part 3. Results", "Part three. Results, in the order of the report.", kicker="GP-RareLink deep dive",
        subtitle="Corpus · extraction and the gatekeeper · stability · records · the unrated audit · ClinVar · OMIM · gap candidates · bias and memorization · the open-weight model · exploratory analyses · each disease · spend")
    add("table", "Corpus and open-access coverage by disease",
        f"The corpus table shows the binding constraint of the whole study. Across the six diseases, {N(screened_all)} records were screened and {N(corpus_all)} entered the corpus, but only {N(open_all)} had open full text, from {pct(min(c['fulltext_share'] for c in cov.values()), 0)} percent for Tangier disease to {pct(cov['ha20']['fulltext_share'], 0)} percent for A20 haploinsufficiency. "
        f"Every disease cleared the registered floor of fifteen eligible primary papers, so no substitute disease was needed, and {N(t['papers'])} papers were extracted in all. "
        "But paywalled papers are not a random subset. For A20 haploinsufficiency they include the two largest sources of the Chen 2020 benchmark, and for the other diseases the catalogue reviews' own source papers are often closed. Keep this in mind for every completeness and recall figure that follows: they are measured on what could be read.",
        head=["Disease", "Records screened", "In corpus", "Open full text", "Eligible after full-text screen", "Papers extracted"], colW=[2.0, 1.4, 1.2, 1.7, 1.5, 1.2], fontSize=10.5,
        rows=[[lab(d), N(cov[d]["manifest_rows"]), N(cov[d]["in_corpus"]), f"{cov[d]['fulltext']} ({pct(cov[d]['fulltext_share'], 0)}%)", "not screened (pilot corpus)" if d == "ha20" else str(cov[d]["eligible_all"]), str(run[d]["papers"])] for d in DISEASES]
             + [["All six", N(screened_all), N(corpus_all), f"{N(open_all)} ({pct(open_all / corpus_all, 0)}%)", "", N(t["papers"])]],
        note="*HA20: development disease; its corpus was carried over from the pilot and kept its ClinVar-seeded papers, tagged (D-19). Open access only (D-32); no institutional access.")
    add("table", "Extraction output and the gatekeeper's verdicts",
        f"Now the extraction itself. {N(t['papers'])} papers produced {N(t['individual_rows'])} individual rows and {N(t['variant_rows'])} variant rows, and {N(t['claims_all'])} values with a quote. The span check found every one of those quotes verbatim in its paper: zero problems in every disease, so the fabricated-span count is zero by construction and by check. "
        f"The gatekeeper judged {N(t['model_claims'])} model claims. It found {N(t['unsupported'])} unsupported, which is {pct(t['unsupported'] / t['model_claims'], 2)} percent; on the five confirmatory diseases, {pct(t5['unsupported'] / t5['model_claims'], 2)} percent, with an exact interval from {pct(u5[0], 2)} to {pct(u5[1], 2)}. "
        f"Per disease the share runs from {pct(min(run[d]['unsupported_or_not_found']['share'] for d in DISEASES), 2)} to {pct(max(run[d]['unsupported_or_not_found']['share'] for d in DISEASES), 2)} percent. Adding partially supported verdicts gives about three percent not fully supported. And the failures cluster: in five of six diseases the three worst papers hold half or more of that disease's unsupported claims. This is the filter's reading, and it is not an error rate.",
        head=["Disease", "Papers", "Individual rows", "Values with a quote", "Span problems", "Model claims judged", "Unsupported", "Not fully supported", "Papers with any", "Worst 3 papers' share"], colW=[1.15, 0.65, 0.95, 1.05, 0.75, 1.0, 0.95, 1.05, 0.75, 0.7], fontSize=9.5,
        rows=[[lab(d), run[d]["papers"], N(run[d]["individual_rows"]), N(run[d]["claims_all"]), run[d]["span_check_problems"], N(run[d]["model_claims_judged"]), f"{pct(run[d]['unsupported_or_not_found']['share'], 2)}%", f"{pct(run[d]['not_supported']['share'], 2)}%",
               f"{run[d]['papers_with_any_unsupported']} of {run[d]['papers']}", f"{pct(run[d]['top3_share_of_unsupported'], 0)}%"] for d in DISEASES]
             + [["Five confirmatory", t5["papers"], N(t5["individual_rows"]), N(t5["claims_all"]), 0, N(t5["model_claims"]), f"{pct(t5['unsupported'] / t5['model_claims'], 2)}%", f"{pct(t5['not_supported'] / t5['model_claims'], 2)}%", "", ""],
                ["All six", t["papers"], N(t["individual_rows"]), N(t["claims_all"]), 0, N(t["model_claims"]), f"{pct(t['unsupported'] / t['model_claims'], 2)}%", f"{pct(t['not_supported'] / t['model_claims'], 2)}%", "", ""]],
        note="\"Unsupported\" counts unsupported and span-not-found verdicts; \"not fully supported\" adds partially supported. The gatekeeper is a filter, not a measure: this is not an error rate.", noteY=4.6)
    top_field = {d: run[d]["unsupported_top_fields"][0][0].split(".")[-1] for d in DISEASES}
    add("bullets", "Why claims fail",
        f"Why do claims fail? The commonest unsupported field in five diseases is the gene symbol on a variant row: a relative's or a cited patient's variant written into the proband's row from a sentence that mentions both. Extraction version five's rule, variant fields only from this person, holds for probands and slips for relatives the paper says carry the same variant. "
        "The second pattern is hedged wording, suggested, suspected, consistent with, typically, recorded as observed or excluded; extraction version six has no hedge rule, a gap known and left in place at the freeze. The third is cohort-level statements applied to individuals; the cohort in general dominates the unsupported claims in Danon and Alexander disease. "
        f"Danon's three worst papers hold {sum(n for _, n in run['danon']['top3_papers_unsupported'])} of its {run['danon']['unsupported_or_not_found']['k']} unsupported claims: variant and diagnosis fields given to eight family carriers when the paper names only the proband, usually mild applied to individuals, and exclusions resting on typically showed no symptoms. "
        "The gatekeeper also flagged about thirty papers whose table and text disagree; those claims were judged on the table, noted, and collected for the human audit.",
        figure="gatekeeper", figureWidth=5.0, fontSize=10.5, caption="A: unsupported share with exact intervals. B: share of each disease's unsupported claims held by its worst three papers. C: whom the cited quote was about, for unsupported claims.",
        bullets=[f"Commonest unsupported field in five diseases: the variant row's gene symbol, quoted from a sentence about the proband but applied to a relative or a cited patient (HA20 {run['ha20']['unsupported_top_fields'][0][1]}, SSADH {run['ssadh']['unsupported_top_fields'][0][1]}, Tangier {run['tangier']['unsupported_top_fields'][0][1]}, LAD-I {run['lad1']['unsupported_top_fields'][0][1]}, AxD {run['axd']['unsupported_top_fields'][0][1]} claims)",
                 "Hedged wording (\"suggested\", \"suspected\", \"consistent with\", \"typically\") recorded as observed or excluded; extraction v6 has no hedge rule, known at the freeze",
                 "Cohort-level statements applied to individuals: \"the cohort in general\" dominates Danon's and AxD's unsupported claims",
                 f"Danon's three worst papers hold {sum(n for _, n in run['danon']['top3_papers_unsupported'])} of {run['danon']['unsupported_or_not_found']['k']}: carriers given the proband's variant; \"usually mild\" applied to individuals; exclusions from \"typically showed no symptoms\"",
                 "About 30 papers contradict themselves (table vs text); judged on the table, noted, collected for the human audit"])
    add("bullets", "Run-to-run stability",
        f"How stable is the reading? A random ten percent of each disease's papers, {rep_papers} in all, was re-extracted with the same frozen files and compared with the run of record. Checklist statuses agree on {pct(min(rep[d]['checklist_agreement'] for d in DISEASES), 0)} to {pct(max(rep[d]['checklist_agreement'] for d in DISEASES), 0)} percent of cells in every disease: fixing the feature names removes the wording variance that free-text rows show. "
        f"Variant keys agree at {pct(min(rep[d]['variant_key_jaccard'] for d in DISEASES), 0)} to {pct(max(rep[d]['variant_key_jaccard'] for d in DISEASES), 0)} percent; the two lowest, Tangier and Danon, are each one paper where both runs recorded the same variants in different notation. "
        f"Individual counts differ in {rep_papers - rep_same} of {rep_papers} papers, from scope calls on relatives and on patients cited from earlier reports, the same issue the pilot found in cohort papers. That is the measure to watch when the records are used for counting people.",
        figure="repeat", figureWidth=5.6, caption="Agreement by measure. Checklist statuses are stable everywhere; variant keys clear 0.9 in four diseases; free-text features agree least.",
        bullets=[f"{rep_papers} papers (10% per disease, seed 20261020) re-extracted with the same frozen files; gatekeeper not run on the repeat",
                 f"Checklist statuses: {pct(min(rep[d]['checklist_agreement'] for d in DISEASES), 0)} to {pct(max(rep[d]['checklist_agreement'] for d in DISEASES), 0)}% of cells agree in every disease",
                 f"Variant keys: {pct(min(rep[d]['variant_key_jaccard'] for d in DISEASES), 0)} to {pct(max(rep[d]['variant_key_jaccard'] for d in DISEASES), 0)}%; the dips (Tangier, Danon) are notation only (a full-width asterisk; \"genetic deletion of exons 4 to 10\" vs \"deletion of exons 4 to 10\")",
                 f"Same individual count in {rep_same} of {rep_papers} papers; the differences are scope calls on relatives and on patients cited from earlier reports",
                 "Free-text features agree least (label-free Jaccard 0.43 to 0.71): two readers phrase and split features differently"])
    add("table", "Records: from rows to phenopackets",
        f"The records table. {N(t['individual_rows'])} rows became {N(t['identities'])} identities after {merges_all} merges, and {N(t['identities'])} phenopackets, all schema-valid, {N(t['with_interpretation'])} of them carrying a genomic interpretation. SSADH deficiency's {s4['ssadh']['merged_pairs']} merges are all the duplicate study; Tangier and LAD-I have no citation merges at all, which is more likely a limit of the citation route than a fact about those literatures. "
        f"Normalization of cDNA descriptions ranges from {pct(min(s4[d]['cdna_normalized_share'] for d in DISEASES), 0)} percent in Alexander disease, where papers print cDNA without the c prefix and use legacy numbering, to {pct(max(s4[d]['cdna_normalized_share'] for d in DISEASES), 0)} percent. Protein-only strings can match ClinVar only at tier two. "
        f"HPO binding covers {pct(min(s4[d]['feature_share_bound'] for d in DISEASES), 0)} to {pct(max(s4[d]['feature_share_bound'] for d in DISEASES), 0)} percent of feature rows. The records hold {N(t['features_observed'])} observed and {N(t['features_excluded'])} excluded terms; conflicts, the same term observed and excluded for one identity from different papers, are few and are kept visible rather than resolved. The gatekeeper removed {N(dropped_all)} claims before the records were built.",
        head=["Disease", "Rows → identities (merges)", "Review-only", "With gene variant", "cDNA normalized", "Feature rows bound", "Phenopackets (with interpretation)", "Observed / excluded terms", "Conflicts", "Claims dropped"], colW=[0.95, 1.35, 0.8, 0.9, 0.95, 0.9, 1.2, 1.05, 0.5, 0.4], fontSize=9.5,
        rows=[[lab(d), f"{N(s4[d]['individual_rows'])} → {N(s4[d]['identities'])} ({s4[d]['merged_pairs']})", rc[d].get("identities_review_only", "—"), N(s4[d]["identities_with_target_variant"]),
               f"{pct(s4[d]['cdna_normalized_share'], 0)}%; {s4[d]['status_counts'].get('protein_only', 0)} protein-only", f"{pct(s4[d]['feature_share_bound'], 0)}%", f"{N(s4[d]['phenopackets'])} ({N(s4[d]['with_interpretation'])})",
               f"{N(s4[d]['features_observed'])} / {N(s4[d]['features_excluded'])}", s4[d]["observed_excluded_conflicts"], dropped[d]] for d in DISEASES],
        note=f"All {N(t['phenopackets'])} phenopackets are schema-valid. \"Review-only\" identities come only from a review's per-patient table (D-33). Protein-only strings cannot be placed on the genome and match ClinVar only at tier 2.", noteY=4.8)
    add("bullets", "The variant spectrum matches expectation",
        "A sanity check on the records: the variant spectrum per disease matches what the biology predicts. Missense variants dominate Alexander disease, a gain-of-function leukodystrophy, and SSADH deficiency, while nonsense and frameshift variants dominate A20 haploinsufficiency and Danon disease, which are loss-of-function diseases. "
        "The most frequently observed features per disease are also the expected ones: oral ulcers and recurrent fever in A20 haploinsufficiency, developmental delay and seizures in SSADH deficiency, low HDL cholesterol in Tangier disease, leukocytosis and omphalitis in LAD-I, white matter abnormality in Alexander disease, left ventricular hypertrophy in Danon disease. "
        "And the records carry not reported far more often than a value, as the three-state design requires: onset age is asserted for a minority of individuals and consanguinity for very few. Sex is unknown for a sizeable share of identities, mostly people from review tables.",
        figure="spectrum", figureWidth=5.6, caption="Coarse variant classes per disease, from the normalized HGVS in the phenopackets.",
        bullets=[f"Missense dominates AxD ({pct(D['pp']['axd']['variant_classes'].get('missense', 0) / max(1, sum(D['pp']['axd']['variant_classes'].values())), 0)}%) and SSADH ({pct(D['pp']['ssadh']['variant_classes'].get('missense', 0) / max(1, sum(D['pp']['ssadh']['variant_classes'].values())), 0)}%); nonsense and frameshift dominate HA20 and Danon",
                 "Most-observed features are the expected ones: " + "; ".join(f"{SHORT[d]}: {D['pp'][d]['top_observed'][0][1]}" for d in DISEASES),
                 "\"Not reported\" far outnumbers values for onset age and consanguinity, as the three-state design requires",
                 "Sex unknown for " + ", ".join(f"{SHORT[d]} {D['pp'][d]['sex'].get('UNKNOWN_SEX', 0) + D['pp'][d]['sex'].get('UNKNOWN', 0)}" for d in DISEASES) + " identities, mostly from review tables",
                 "Observed-excluded conflicts are few and kept visible in the records rather than resolved"])
    add("bullets", "O1 is not yet measured; what the pilot's audits showed",
        f"Now the most important slide in the results. The primary outcome, the human audit of {D['o1']['n']} claims, has not been measured. The sample is drawn, the two blinded rating pages are built, and no claim has been rated. "
        f"What we do have are the pilot's two audits, before the pipeline was frozen. The first, fifty claims from the second pilot run, found {a1['k']} unsupported, {pct(a1['share'])} percent, all variant fields taken from a group statement or a summary table. The gatekeeper of the day flagged none of them. The second, after fixes, {a2['n']} claims rated from a twenty-paper re-run, found {a2['k']} unsupported again, {pct(a2['share'])} percent, all ages read by position from stacked multi-patient cells that the rater could not verify. "
        f"Each audit exposed an error class, and each class now has a rule in the frozen pipeline. But nothing has been re-audited by a person since. So the machine's {pct(t5['unsupported'] / t5['model_claims'], 2)} percent sits far below the humans' six, and until the audit is rated no accuracy claim can be made for the frozen pipeline.",
        figure="checks", figureWidth=5.4, fontSize=11, caption="Blue: the gatekeeper's verdicts per disease run. Orange: two human audits of the pilot's output, before the fixes they produced were frozen in. Dashed: the 2% target.",
        bullets=[f"O1: {D['o1']['n']} claims drawn (seed 40250), blinded pages built for two raters and a tie-breaker; no claim rated",
                 f"Pilot audit 1 (run-2, 50 claims): {a1['k']} unsupported ({pct(a1['share'])}%), all variant fields from a group statement or summary table; gatekeeper v1 flagged none",
                 f"Pilot audit 2 (v5 re-run, {a2['n']} rated): {a2['k']} unsupported ({pct(a2['share'])}%), all ages read by position from stacked cells the rater could not verify",
                 "Each audit produced a frozen rule (D-29: variant fields only from this person; D-31: no positional reading of stacked cells); none has been re-audited by a person",
                 "The gatekeeper flagged 2 of 6 and 1 of 4 of the claims a person rejected, with no false flags: a filter, not a measure"])
    add("table", "O2: concordance with ClinVar, by disease",
        f"Concordance with ClinVar. Gene agreement is near ceiling by design. HGVS recall, the share of ClinVar's own citation pairs in our papers that the run extracted, is low: at tier one from {pct(min(o2a[d]['hgvs_recall_tier1']['share'] for d in DISEASES), 0)} to {pct(max(o2a[d]['hgvs_recall_tier1']['share'] for d in DISEASES), 0)} percent, and from {pct(min(o2a[d]['hgvs_recall_tier12']['share'] for d in DISEASES), 0)} to {pct(max(o2a[d]['hgvs_recall_tier12']['share'] for d in DISEASES), 0)} percent when protein-level matches are allowed. "
        f"Overlap, the share of our placed variants that ClinVar already holds, runs from {pct(min(o2a[d]['overlap_tier1']['share'] for d in DISEASES), 0)} percent in LAD-I to {pct(max(o2a[d]['overlap_tier1']['share'] for d in DISEASES), 0)} percent in SSADH deficiency, a well-covered gene. "
        f"Where authors state a classification, it agrees with ClinVar's aggregate {pct(min(o2a[d]['classification_agreement_among_stated']['share'] for d in DISEASES), 0)} to {pct(max(o2a[d]['classification_agreement_among_stated']['share'] for d in DISEASES), 0)} percent of the time, and the disagreements run almost entirely in one direction: authors say pathogenic, ClinVar says uncertain. HPO annotation recall, whether each annotated feature was seen in at least one person, is high. The denominators matter: Tangier's recall rests on six citation pairs.",
        head=["Disease", "Gene matches", "HGVS recall, tier 1", "HGVS recall, tiers 1+2", "Overlap, tier 1", "Classification agreement", "ClinVar condition names the disease", "HPO annotation recall"], colW=[0.95, 1.0, 1.25, 1.25, 1.2, 1.2, 1.1, 1.05], fontSize=9.5,
        rows=[[lab(d), kn(o2a[d]["gene_7_2_1"] if "gene_7_2_1" in o2a[d] else o2[d]["gene_7_2_1"], 0), kn(o2a[d]["hgvs_recall_tier1"]), kn(o2a[d]["hgvs_recall_tier12"]), kn(o2a[d]["overlap_tier1"]), kn(o2a[d]["classification_agreement_among_stated"]), kn(o2a[d]["condition_names_disease"]),
               kn(o2[d]["phenotype_7_2_4b"]["annotation_recall"])] for d in DISEASES],
        note="HGVS recall counts ClinVar's own (paper, variant) citation pairs restricted to corpus papers; overlap is not precision. Every miss counts as discordant until the registered human triage of 50 sampled misses is done.", noteY=4.6)
    miss_top = {d: D["o2_misses_by_paper"].get(d, [("—", 0)])[0] for d in DISEASES}
    add("bullets", "Reading the concordance figures",
        "How to read those numbers. HGVS recall is low, but it measures something specific: whether the run extracted, from a given paper, a variant that ClinVar cites to that paper. The misses concentrate in a handful of papers. In SSADH deficiency two papers hold almost all of them: Akaboshi 2003, whose table was scrambled in PDF conversion so that only a dozen of fifty-four families were extracted, and Brennenstuhl 2020, which tested variants in vitro and describes no patients. In LAD-I one review, a mutation update whose people are database accession numbers, holds thirty-seven of forty-one misses. "
        "These are scope and input problems more than reading errors, but that is a hypothesis until the registered triage of fifty sampled misses is done by a person. Overlap is not precision: a variant absent from ClinVar may be a real gap or a notation difference. "
        "Classification disagreement runs in one direction, consistent with an expectation stated before registration: authors call variants pathogenic that ClinVar still lists as uncertain.",
        figure="concordance", figureWidth=5.0, fontSize=10.5, caption="A: HGVS recall against ClinVar's citations. B: overlap of extracted alleles with ClinVar. C: classification agreement where authors state a class. D: HPO annotation recall.",
        bullets=["HGVS recall asks a narrow question: did the run extract, from this paper, the variant ClinVar cites to it? Misses concentrate in a few papers per disease",
                 f"SSADH: {miss_top['ssadh'][1]} misses in one paper (Akaboshi 2003, table scrambled in conversion) and most of the rest in Brennenstuhl 2020 (in-vitro variants, no patients)",
                 f"LAD-I: {miss_top['lad1'][1]} of its misses in one review (van de Vijver 2012) whose \"people\" are accession numbers",
                 "Overlap is not precision: an absent variant may be a real gap or a notation difference; the gap candidates below carry both possibilities until adjudicated",
                 "Classification disagreement runs one way, as expected before registration: authors say P/LP, ClinVar says VUS",
                 "A seeded sample of 50 misses awaits human triage into five categories (extraction, normalization, citation does not describe the variant, scope, other)"])
    add("bullets", "Completeness against two published catalogues",
        f"Two expert catalogues give the strongest completeness check we have. For A20 haploinsufficiency, Chen 2020's table: {kn(comp['ha20']['recall_restricted_primary'], 0)} of the catalogue's variants whose source paper was in the corpus were recovered. For Alexander disease, Grossi 2024's supplementary table: {kn(comp['axd']['recall_restricted_primary'], 0)}, and the two misses are notation. "
        "Where the pipeline read the source paper, it found the variant. The unrestricted figures are lower only because most of the catalogues' source papers are paywalled, which is the access constraint again. "
        "The other four diseases have no registered catalogue: their candidate catalogues had no per-variant table naming sources, or were not open. Extending catalogue-based completeness to those diseases is one of the cheapest ways to strengthen the study, and it needs no model spend to speak of.",
        figure="completeness", figureWidth=5.6, caption="Completeness against the two published catalogues: restricted to variants whose source paper is in the corpus, and unrestricted.",
        bullets=[f"HA20 vs Chen 2020 Table S1 (D-30): {kn(comp['ha20']['recall_restricted_primary'], 0)} restricted; {kn(comp['ha20']['recall_unrestricted_primary'], 0)} unrestricted",
                 f"AxD vs Grossi 2024 Supplementary Table 2 (D-39): {kn(comp['axd']['recall_restricted_primary'], 0)} restricted; the two misses are notation; the catalogue's genomic column matched nothing as printed and was not used",
                 "Restricted = catalogue variants whose source paper is in the corpus; unrestricted = all catalogue variants with a PMID. The gap between them is paywalled papers",
                 "No registered catalogue for SSADH, Tangier, LAD-I or Danon (suitability check failed); finding one per disease is a cheap way to strengthen the study"])
    n_listed = sum(om["counts"][d]["allelic_variants"]["listed"] for d in DISEASES)
    add("bullets", "The OMIM holdout: the source and the matching",
        f"OMIM entered the study on the twenty-eighth of October, when the principal investigator printed the six phenotype entries and the six gene entries to PDF, because omim.org refuses automated reads from our environment and no API key is in place. A harness script parses each page: titles, cross-references, the allelic variants with OMIM's legacy labels, their dbSNP and ClinVar accessions, the papers each narrative cites, and the edit dates. The content stays outside the repository because OMIM's terms restrict redistribution. "
        f"The gene entries list {n_listed} allelic variants, {om['totals']['omim_allelic_variants_for_diseases']} of them titled for our six diseases. OMIM calls these selected examples: a curated sample of the literature, not a catalogue. So recall of OMIM's variants is the meaningful direction, and precision against OMIM is not. "
        "Matching went through ClinVar. Each allelic variant was placed in ClinVar through ClinVar's own OMIM cross-reference or the accessions OMIM prints; ClinVar's title then gives current HGVS. That was necessary because OMIM's own labels use legacy protein numbering: ABCA1 labels sit sixty residues below the current transcript, and a LAMP2 label reads leucine 113 where the current numbering is 147.",
        bullets=[f"Twelve omim.org entry pages frozen by the PI on {om['date']} (D-42); parsed by the harness; content kept outside the repository, only a checksummed manifest committed",
                 f"{n_listed} allelic variants listed on the six gene entries; {om['totals']['omim_allelic_variants_for_diseases']} titled for the six diseases; OMIM calls them \"selected examples\"",
                 "Recall of OMIM's variants is meaningful; \"precision against OMIM\" is not; the gap definition's OMIM clause is one-sided",
                 "Matching through ClinVar: OMIM cross-references and RCV accessions → ClinVar VariationID → current HGVS → match by allele, cDNA, protein, then a notation-tolerant token (reported apart)",
                 "OMIM labels use legacy protein numbering (ABCA1 labels 60 residues below the current transcript; LAMP2 LEU113TER is p.Leu147Ter); dbSNP ids alone were not used because one rs covers every allele at a position",
                 "Phenotype entries carry no allelic-variant table and no clinical synopsis; the synopsis pages are not frozen, so OMIM's phenotype half is \"not yet assessed\""])
    add("table", "Recall of OMIM's allelic variants, by disease",
        f"The result: the run recovered {spoken_kn(rec_all)} of the variants OMIM lists for these diseases, with a Wilson interval from {pct(rec_all['ci95'][0], 0)} to {pct(rec_all['ci95'][1], 0)} percent. "
        f"By disease it runs from {spoken_kn(rec['ha20'])} for A20 haploinsufficiency and {spoken_kn(rec['lad1'])} for LAD-I down to {spoken_kn(rec['tangier'])} for Tangier disease, whose allelic variants come from the gene-discovery papers of 1999 to 2003, all in the corpus and all closed. "
        f"The column that explains the pattern is on the right: of the {src_all} papers OMIM cites as sources for these variants, {src_ex} were extracted. Where the source paper was in the run, the variant was recovered from it {restricted_k} times out of {restricted_n}; the misses have named causes.",
        head=["Disease", "OMIM allelic variants", "Recovered (tiers 1+2)", "Not recovered", "Recall, Wilson 95%", "OMIM source papers extracted", "Corpus papers cited by OMIM"], colW=[1.3, 1.2, 1.3, 1.1, 1.6, 1.3, 1.2], fontSize=10.5,
        rows=[[lab(d), rec[d]["n"], rec[d]["k"], rec[d]["n"] - rec[d]["k"], f"{pct(rec[d]['share'], 0)}% ({pct(rec[d]['ci95'][0], 0)} to {pct(rec[d]['ci95'][1], 0)})",
               f"{om['per'][d]['A_literature']['av_source_pmids_extracted']} of {om['per'][d]['A_literature']['av_source_pmids']}", kn(om["per"][d]["A_literature"]["share_of_corpus_cited_by_omim_7_2_5"], 0)] for d in DISEASES]
             + [["All six", rec_all["n"], rec_all["k"], rec_all["n"] - rec_all["k"], f"{pct(rec_all['share'], 0)}% ({pct(rec_all['ci95'][0], 0)} to {pct(rec_all['ci95'][1], 0)})", f"{src_ex} of {src_all}", ""]],
        note="Tier 1 = genomic allele or cDNA; tier 2 = protein change only. Token-level matches are not counted as recovered.")
    add("bullets", "What the OMIM holdout taught",
        f"Four lessons. First, coverage, not reading, is the binding constraint: pooled over every paper OMIM cites for these diseases, {fa.get('in corpus, no open full text', 0)} sit in our screened corpus with no open copy, {fa.get('not found by search', 0)} were never returned by our searches, and {fa.get('extracted', 0)} were extracted. The never-returned papers are mostly pre-1990 descriptions under earlier names for the disease: LAD-I as Mo1 or LFA-1 deficiency, Danon disease as lysosomal glycogen storage with normal acid maltase, Tangier disease as familial alpha-lipoprotein deficiency. A search-term gap for diseases described before their gene. "
        f"Second, where the source paper was read, the variant was usually there: {restricted_k} of {restricted_n}, and the misses are a table scrambled in PDF conversion and two variants stated only in prose, a glycine to an arginine at amino acid 169, which the record keeps verbatim but cannot key. "
        f"Third, at the patient level, for the {om['judg_papers']} papers both OMIM and the run cover, our records agreed with OMIM's curated statements {jt.get('agree', 0)} times, were partial {jt.get('partial', 0)} times, and contradicted none; where they differ, the run usually has less, not something wrong. "
        "Fourth, OMIM is fallible too: two allelic variants link to ClinVar records that do not match their own text, and ten labels differ from ClinVar's protein change, nine by legacy numbering. A holdout curated by people needs the same provenance checks as our output.",
        figure="omim", figureWidth=5.0, fontSize=10.5, caption="A: allelic variants recovered. B: where OMIM's source papers stand in our corpus funnel. C: the share of the run's ClinVar P/LP variants that OMIM lists.",
        bullets=[f"Of the {om['totals']['omim_cited_papers_distinct_all_diseases']} papers OMIM cites for these diseases: {fa.get('extracted', 0)} extracted, {fa.get('in corpus, no open full text', 0)} in corpus but paywalled, {fa.get('not found by search', 0)} never returned (mostly pre-1990 papers under earlier disease names)",
                 f"Where the source paper was read: {restricted_k} of {restricted_n} variants recovered from it; misses = a scrambled table and variants stated only in prose",
                 f"Patient level, {om['judg_papers']} shared papers: {jt.get('agree', 0)} agree, {jt.get('partial', 0)} partial, {jt.get('missed in source paper', 0) + jt.get('missed (major under-capture)', 0)} missed (all the scrambled table), none contradicted",
                 f"OMIM lists {om['totals']['omim_allelic_variants_for_diseases']} selected examples; the run holds {N(placed)} genome-placed variants, and most of its ClinVar P/LP variants are not OMIM allelic variants",
                 "OMIM is fallible: two allelic variants (610045.0002, 610045.0007) link to ClinVar records that contradict their text; 10 labels differ from ClinVar's protein change, 9 by legacy numbering"])
    add("bullets", "D-43: the candidate that was our own mistake",
        "The OMIM check also caught an error of ours, and the story is worth a minute. Every one of the 215 gap candidates was compared with its gene's allelic variants by allele, cDNA, protein and notation token. One Danon candidate, a two-base deletion from Sugie 2018, collided with an OMIM allelic variant by its deletion token only. "
        "The paper's table places the deletion on exon 9b, the LAMP2B isoform. LAMP2 has alternative terminal exons 9a, 9b and 9c, and because the paper named no transcript the run had assumed the standard one, exon 9a. That produced a genomic allele no database holds, because it is not what the paper reported. On the right transcript, the variant is OMIM 309060.0001 and a ClinVar record. "
        "It was a normalization artefact, not a gap, and it was withdrawn the same day under deviation D-43. A new module now computes from the RefSeq records where each gene's coding isoforms diverge, and normalization lets the paper's own words choose the transcript at such positions, or assigns no genomic key. The Danon run was re-normalized; exactly two of 165 descriptions changed. Scoring against two independent references found an error that scoring against one could not.",
        bullets=["All 215 candidates compared with OMIM's allelic variants by allele, cDNA, protein and notation token: 214 absent, 1 token collision",
                 "G-danon-001 (NM_002294.3:c.1097_1098del, Sugie 2018): the paper's table says exon 9b (LAMP2B); the run had assumed the MANE transcript (exon 9a); the resulting allele exists in no database because it is not what the paper reported",
                 "On the right transcript it is OMIM 309060.0001 and ClinVar 1410728: a normalization artefact, withdrawn (D-43)",
                 "Fix: isoform-sensitive positions computed from RefSeq mRNA records (LAMP2 c.1094 onward; GFAP c.1172, exon 7A); the paper's exon or isoform label chooses the transcript, else no genomic key (\"isoform_ambiguous\")",
                 "Danon re-normalized: 2 of 165 descriptions changed; phenopackets rebuilt (505, all valid); GFAP's one isoform case had already failed normalization safely",
                 "Two independent references caught what one could not"])
    add("stats", "O3: the gap, in numbers",
        f"Now the gap itself. Across the six diseases the papers yielded {N(placed)} distinct variants placed on the genome. {N(in_clinvar)} are in ClinVar, {N(plp)} of them classified pathogenic or likely pathogenic. {absent} are absent from ClinVar in two successive releases. "
        f"After dropping the alleles whose every supporting row failed the gatekeeper, checking each against OMIM, and withdrawing the isoform artefact, {live} candidates remain. Each has an evidence dossier written by helpers and checked by script: every paper reporting it, every quote, found verbatim, the individuals, the authors' own classification, and flags for the panel. "
        f"Separately, {t['reclass']} variants that papers classify as pathogenic sit in ClinVar only as uncertain or conflicting, {t['reclass_strong']} of them with evidence the harness judged strong enough to propose a reclassification. All of these are candidates. Nothing is submitted without adjudication and the principal investigator's sign-off.",
        tiles=[[N(placed), "distinct variants placed on the genome (GRCh38)"], [N(in_clinvar), f"in ClinVar; {N(plp)} as pathogenic or likely pathogenic"], [str(absent), "absent from ClinVar in two successive releases"],
               [str(live), "candidates after the gatekeeper, the OMIM check and one withdrawal, each with a dossier", True], [f"{N(D['dossiers']['quotes'])}", "quotes in the dossiers, all found verbatim"], [f"{t['reclass']} ({t['reclass_strong']} strong)", "in ClinVar only as VUS or conflicting while papers say pathogenic"]],
        note="Candidate = tier-1 allele absent from the ClinVar snapshot, gatekeeper-supported in at least one row, not among OMIM's allelic variants. None adjudicated.")
    add("table", "Gap candidates by disease, and what the flags say",
        f"By disease, the candidate list is dominated by LAD-I with {gaps['lad1']['gap_candidates']} and A20 haploinsufficiency with {gaps['ha20']['gap_candidates']}; SSADH deficiency, a well-covered gene, contributes {gaps['ssadh']['gap_candidates']} and Tangier {gaps['tangier']['gap_candidates']}. "
        f"The LAD-I list needs care: {gaps['lad1']['gap_candidates_only_from_clinvar_cited_papers']} of its {gaps['lad1']['gap_candidates']} candidates come only from papers ClinVar itself cites, most of them from one mutation update whose people are database accession numbers, and the protein check flags {gaps['lad1']['gap_candidates_protein_check'].get('differs', 0)}. Many may be numbering or normalization slips rather than gaps. "
        f"Model-written flags on the dossiers mark {tri['with_any_flag']} of the 215 candidates for the panel's attention: possible same person reported twice, carriers not attached to a case, notation conflicts, protein mismatches, review-only sources, mosaic or somatic calls. These are leads for adjudication, not verdicts.",
        head=["Disease", "Tier-1 alleles", "Candidates (live)", "In one paper only", "Only from reviews", "Only from ClinVar-cited papers", "Protein check differs", "Reclassification candidates (strong)"], colW=[1.1, 1.0, 1.1, 1.1, 1.1, 1.3, 1.1, 1.2], fontSize=10.5,
        rows=[[lab(d), gaps[d]["tier1_alleles"], om["gap_live"][d], gaps[d]["gap_candidates_by_papers"].get("1", 0), gaps[d]["gap_candidates_only_from_reviews"], gaps[d]["gap_candidates_only_from_clinvar_cited_papers"], gaps[d]["gap_candidates_protein_check"].get("differs", 0),
               f"{gaps[d]['reclassification_candidates']} ({gaps[d]['reclassification_strong_proposed']})"] for d in DISEASES]
             + [["All six", placed, live, sum(gaps[d]["gap_candidates_by_papers"].get("1", 0) for d in DISEASES), sum(gaps[d]["gap_candidates_only_from_reviews"] for d in DISEASES), sum(gaps[d]["gap_candidates_only_from_clinvar_cited_papers"] for d in DISEASES),
                sum(gaps[d]["gap_candidates_protein_check"].get("differs", 0) for d in DISEASES), f"{t['reclass']} ({t['reclass_strong']})"]],
        note=f"Triage flags (model-written, not verified): {', '.join(f'{k.replace(chr(95), chr(32))} {v}' for k, v in sorted(tri['by_flag'].items(), key=lambda x: -x[1]))}; {tri['with_any_flag']} of 215 candidates carry at least one.", noteY=4.45)
    add("bullets", "Where the found variants stand, and what a candidate looks like",
        "The bar chart shows each disease's genome-placed variants split by their standing in ClinVar: pathogenic or likely pathogenic in dark blue, another classification in light blue, candidates in orange, and absent but not a candidate in grey. "
        "A typical candidate is a frameshift or nonsense variant reported in one or two papers, with the authors calling it pathogenic. The dossier gives the panel everything in one place: the normalized description, how each paper wrote it, the quotes, the individuals, zygosity where stated, the authors' classification, and the flags. "
        "The dashboard lists all of them with PubMed links, and the adjudication page, built and private, is ready for the panel. Two cautions. The list is a lower bound set by open access. And it is not yet a list of real gaps: adjudication will sort real gaps from notation differences, duplicates and carriers.",
        figure="gaps3", figureWidth=5.2, fontSize=10.5, caption="Each bar: one disease's genome-placed variants. Orange: candidates awaiting the panel.",
        bullets=["Dark blue: in ClinVar as P/LP. Light blue: in ClinVar with another classification. Orange: candidates. Grey: absent but not a candidate (evidence failed the second read, or withdrawn)",
                 "A dossier per candidate: normalized description, the papers' own strings, every quote (verbatim-checked), individuals, zygosity where stated, authors' classification, flags",
                 "The dashboard lists every candidate with PubMed links; the private adjudication page is ready for the panel",
                 "Lower bound: open access only. Not yet gaps: adjudication sorts real gaps from notation, duplicates and carriers",
                 f"Helpers also proposed {sum(v['groups'] for v in D['merges']['by_disease'].values())} same-person groups across the dossiers, not merged; if confirmed, up to a few percent of identities would collapse"])
    add("bullets", "O4: the memorization probe",
        f"The bias arm has two parts. The memorization probe asks whether the model could be extracting facts it remembers from training rather than facts it reads. {mem_papers} papers, thirty per disease, were stratified by publication date against the model's documented training cutoff of June 2026: {mem_c['after']['papers']} after, {mem_c['recent']['papers']} recent, {mem_c['older']['papers']} older. Two black-box probes ran identically on both models: closed-book recall from the PMID, title and year, and guided completion of a fifty-word opening, scored against the full-text extraction, never against ClinVar. "
        f"In the {mem_c['after']['papers']} post-cutoff papers neither model produced a specific recall or a correct variant. Across all strata Claude claimed specific recall for {mem_c['older']['cb_specific']} of {mem_papers} papers, all older and for phenotypes only; the few variant hits were recurrent variants labelled as guesses. The completions with longer matching runs are formulaic consent sentences. "
        "The probe is small and will grow as post-cutoff papers accumulate, and black-box probes can miss memorization that changes extraction without surfacing as recall. But it gives no sign of memorization.",
        figure="memorization", figureWidth=5.2, fontSize=11, caption="Memorization probe on both models: neither reproduces the papers' variants or text; differences between strata are small and in no consistent direction.",
        bullets=[f"{mem_papers} papers (30 per disease) by date vs the June 2026 cutoff: {mem_c['after']['papers']} after, {mem_c['recent']['papers']} recent, {mem_c['older']['papers']} older; closed-book recall and guided completion; scored against the extraction, never ClinVar",
                 f"After cutoff: Claude {mem_c['after']['cb_specific']} specific recalls, {mem_c['after']['cb_variant_hits']} variant hits; DeepSeek {mem_o['after']['cb_specific']} and {mem_o['after']['cb_variant_hits']}",
                 f"All strata: Claude claimed specific recall for {mem_c['older']['cb_specific'] + mem_c['recent']['cb_specific'] + mem_c['after']['cb_specific']} of {mem_papers} papers (all older, phenotypes only); variant hits were recurrent variants labelled guesses",
                 f"Completion: longest matching run {mem_c['older']['cp_max_longest_run']} words, in formulaic consent sentences; mean 5-gram share under 1%",
                 "Small after-cutoff stratum; black-box probes cannot see memorization that never surfaces as recall"])
    comps = sorted(Path(x).stem for x in (ROOT / "analysis/bias/comparator_sheets").glob("*.csv"))
    add("bullets", "O4: the frequency comparison has not started",
        f"The second part of the bias arm, the frequency deviation, has no numbers yet. The design is simple and deliberately human-first: for each disease, a person lists the held-out natural-history cohort's HPO-mappable features and their cohort frequencies, without looking at our literature frequencies; only then does a script compute observed over observed plus excluded per feature in our records, with a publication-cluster bootstrap, and report the deviation. "
        f"{len(comps)} open comparators are fetched and a listing sheet exists for each: A20 haploinsufficiency, Alexander disease, Danon disease and SSADH deficiency. Three candidate comparators are paywalled and left out, and LAD-I and Tangier disease have no comparator, so they are out of the bias arm by decision. The script is written and tested on synthetic input only. What it needs is one to two hours of a person per sheet.",
        bullets=["Design: a person lists each comparator's HPO-mappable features and cohort frequencies before any literature frequency is computed",
                 "Then observed ÷ (observed + excluded) per feature in our records, with a 2,000-resample publication-cluster bootstrap (seed 7425)",
                 "Comparators fetched, with listing sheets: " + "; ".join(c.replace("__", ": ") for c in comps),
                 "Three candidate comparators are paywalled (D-32); LAD-I and Tangier have no comparator and are out of the bias arm (D-35)",
                 "Script written and tested on synthetic input only; needs 1 to 2 hours of a person per sheet"])
    add("table", "O5: Claude against an open-weight model on identical inputs",
        f"The efficiency outcome. Expert-minutes per accepted record cannot be measured until adjudication starts. The model comparison is done for two diseases: DeepSeek V4.1 Flash, an open-weight model, ran the same {ow['ha20']['papers_compared']} A20 and {ow['ssadh']['papers_compared']} SSADH papers with the same launch prompt, frozen instruction files and schema, through an agent loop with file tools; the outputs went through the same span check, reconciliation, normalization and harness, and the same gatekeeper judged both runs. "
        f"The two models found largely the same variants: {ow['ha20']['variant_keys']['shared']} of {ow['ha20']['variant_keys']['union']} in the union for A20, {ow['ssadh']['variant_keys']['shared']} of {ow['ssadh']['variant_keys']['union']} for SSADH. The open model cost about one {cost_ratio}th as much per paper and took {time_ratio} times as long. "
        f"Where it differed was provenance. Claude left no value without a quote; the open model left {pct(ow['ha20']['span']['open']['no_quote_rate'])} and {pct(ow['ssadh']['span']['open']['no_quote_rate'])} percent without one, which the rules forbid. The gatekeeper judged {pct(owg['ha20']['open']['unsupported']['share'])} and {pct(owg['ssadh']['open']['unsupported']['share'])} percent of its claims unsupported, against {pct(owg['ha20']['claude']['unsupported']['share'], 2)} and {pct(owg['ssadh']['claude']['unsupported']['share'], 2)} for Claude.",
        head=["Disease", "Papers", "Values asserted (Claude / open)", "Values with no quote", "Judged unsupported", "…among claims with a quote", "Variant keys shared / union", "Checklist agreement", "Cost per paper, median", "Minutes per paper, median"], colW=[0.8, 0.6, 1.2, 0.95, 1.0, 1.0, 1.0, 0.9, 0.85, 0.7], fontSize=9.5,
        rows=[[lab(d), ow[d]["papers_compared"], f"{N(ow[d]['span']['claude']['values_asserted'])} / {N(ow[d]['span']['open']['values_asserted'])}", f"0 / {N(ow[d]['span']['open']['no_quote'])} ({pct(ow[d]['span']['open']['no_quote_rate'])}%)",
               f"{pct(owg[d]['claude']['unsupported']['share'], 2)}% / {pct(owg[d]['open']['unsupported']['share'], 2)}%", f"{pct(owg[d]['claude']['by_span']['quote']['unsupported']['share'], 2)}% / {pct(owg[d]['open']['by_span']['quote']['unsupported']['share'], 2)}%",
               f"{ow[d]['variant_keys']['shared']} / {ow[d]['variant_keys']['union']} ({pct(ow[d]['variant_keys']['jaccard_pooled'], 0)}%)", f"{pct(ow[d]['checklist']['status_agreement'])}%", f"${ow[d]['cost_usd']['claude_median_per_paper']:.2f} / ${ow[d]['cost_usd']['open_median_per_paper']:.2f}",
               f"{ow[d]['wall_seconds']['claude_median'] / 60:.0f} / {ow[d]['wall_seconds']['open_median'] / 60:.0f}"] for d in ("ha20", "ssadh")],
        note="DeepSeek-V4.1-Flash (2026-09-10 checkpoint) on OpenRouter, provider pinned to DeepInfra fp8; same launch prompt, frozen files, file tools and scoring. Claude's cost is an estimate from helper tokens; the open model's is the host's reported price for final attempts.", noteY=3.3)
    add("bullets", "Reading the comparison, and its cautions",
        "Three readings and two cautions. The readings: the method transfers, in that a much cheaper model finds the same variants; the provenance rules bind differently on different models, in that the open model drops quotes the rules require; and quote-level provenance is the cheapest place to see the difference. "
        "Most of the gap in unsupported rates is claims with no quote at all, but claims with a quote were also judged unsupported several times as often. "
        "The cautions: the judge is Claude, which may not be neutral between a Claude and a non-Claude extraction, and the gatekeeper helpers did not all treat empty quotes the same way. The registered measure is a blinded human audit of equal samples from each model, and it waits on the same panel decision as the primary audit. The scaffolds also differed slightly, as the plan requires us to state: the open-weight loop had no shell and no repair passes, and three harness fixes landed during its run, approved and logged. Two diseases, one model, one provider: not a general finding.",
        figure="openweight", figureWidth=5.0, fontSize=10.5, caption="Claude vs the open-weight model on the registered metrics measured so far.",
        bullets=["Variants: largely the same set found; HGVS recall against ClinVar overlaps within the intervals",
                 f"Provenance: Claude left no value without a quote; the open model left {pct(ow['ha20']['span']['open']['no_quote_rate'])}% and {pct(ow['ssadh']['span']['open']['no_quote_rate'])}% without one, and some cells broke the schema shape",
                 "Support, as the same Claude gatekeeper reads it: most of the gap is claims with no quote, but claims with a quote were also judged unsupported several times as often",
                 "Cautions: the judge is Claude; helpers did not all treat empty quotes alike (236 HA20 and 144 SSADH empty-quote claims were judged supported against the row's quote)",
                 f"Cost and time: about 1/{cost_ratio} of the cost per paper, {time_ratio}× the wall-clock, with waits after dropped connections (about 50 retries per 125 papers)",
                 "Scaffold differences stated: no shell, no repair passes, three logged harness fixes during the run. Two diseases, one model, one provider"])
    gp_rows = []
    for d in DISEASES:
        for name, a in gp[d]["analyses"].items():
            sig = a.get("significant_bh_0.05", 0)
            sig_terms = "; ".join(f"{x['hpo_label']} ({x['group_truncating'] if 'group_truncating' in x else ''})" for x in a.get("top", []) if x.get("p_bh", 1) <= 0.05)
            gp_rows.append([lab(d), name.replace("_", " "), gp[d]["patients"], a.get("terms_tested", 0), sig, sig_terms or "—"])
    add("table", "Exploratory: genotype-phenotype tests with GPSEA",
        "Two exploratory analyses, flagged as such. First, genotype-phenotype tests with GPSEA, Fisher exact tests with Benjamini-Hochberg correction, in a separate project. Variant effects come from each phenopacket's own normalized HGVS, only individuals with a placed variant and at least one phenotype enter, and zygosity for untyped calls is an analysis assumption only; the records keep not reported. "
        "In A20 haploinsufficiency, Alexander disease, SSADH deficiency and LAD-I, no term survives correction, and Tangier has too few phased genotypes to test. Danon disease reproduces the published sex difference: males, who are hemizygous, far more often show proximal muscle weakness and left ventricular hypertrophy than heterozygous females. "
        "The papers overlap with the published series, so this is a reproduction check, not an independent replication, and the truncating-versus-missense arrhythmia signal rests on a handful of missense carriers and is a lead only.",
        head=["Disease", "Comparison", "Individuals", "Terms tested", "Significant (BH 0.05)", "Significant terms"], colW=[0.9, 2.6, 0.9, 0.9, 1.1, 2.6], fontSize=9.5,
        rows=gp_rows, note="Fisher exact tests, Benjamini-Hochberg at 0.05 (GPSEA 0.10.0). Zygosity for untyped calls is an analysis assumption; a feature not reported is not counted as excluded. Exploratory.", noteY=4.45)
    add("bullets", "Exploratory: Tangier in ClinVar; deduplication limits",
        f"Second, a look at what ClinVar's ABCA1 record actually contains. Of {N(ts['abca1_single_gene_records'])} single-gene ABCA1 records in ClinVar, only {ts['records_matched_by_tangier_literature']} match variants extracted from the thirty-one Tangier papers, and of the {ts['abca1_plp_records']} pathogenic or likely pathogenic records, {ts['plp_records_matched']}. Most of the gene's ClinVar records come from testing unrelated to Tangier disease. Separating the monogenic allelic series from that noise is itself one of the tests the grant proposed, and it is a lower bound because the corpus is open access only. "
        "Two negative results on deduplication. The planned LAD-I benchmark against the duplicate cases in Almarza Novoa 2018 is not computable: the review's open supplement flags only one overlap and names no case pairs. And the citation-only merge route found no merges at all in Tangier and LAD-I, which is more likely a limit of the route than a fact about those literatures; the dossier helpers later proposed nineteen same-person groups across the candidates, which await a person.",
        bullets=[f"ClinVar ABCA1: {N(ts['abca1_single_gene_records'])} single-gene records, {ts['abca1_plp_records']} P/LP; {ts['records_matched_by_tangier_literature']} records ({pct(ts['share_of_all_records'])}%) and {ts['plp_records_matched']} P/LP records ({pct(ts['share_of_plp_records'])}%) match the Tangier literature",
                 f"{ts['extracted_not_in_clinvar']} of {ts['extracted_tangier_variants']} extracted Tangier variants are not in ClinVar; most ABCA1 records come from unrelated testing",
                 "LAD-I deduplication benchmark not computable: the review's supplement names no case pairs",
                 "No citation merges in Tangier or LAD-I: a limit of the citation route; 19 proposed same-person groups await a person",
                 "Both analyses exploratory (plan §7.6); the Tangier figure is a lower bound (open access only)"])
    # per-disease slides
    notable = {
        "ha20": ["Development disease: every rule was tuned on its pilot runs; 92 of 160 corpus papers were ClinVar-seeded (D-19). Treat its figures as an upper bound",
                 f"Completeness vs Chen 2020: {kn(comp['ha20']['recall_restricted_primary'], 0)} restricted; most catalogue source papers are paywalled",
                 "12 proposed same-person groups, the most of any disease: HA20 reviews re-cite the same families"],
        "ssadh": ["Duplicate study: the preprint and journal version are both in the corpus, their patients merged with evidence recorded; the papers disagree on G176R vs G176E for one variant",
                  "O2 misses are two papers: a table scrambled in conversion (about 12 of 54 families extracted) and an in-vitro study with no patients",
                  "Highest overlap with ClinVar of the six; only 10 candidates: a well-covered gene"],
        "tangier": ["Smallest corpus and lowest open-access share; many old papers with tables as images",
                    f"Only {s4['tangier']['identities_with_target_variant']} of {s4['tangier']['identities']} identities carry an ABCA1 variant: {rc['tangier'].get('identities_review_only', 0)} come from review tables and many older reports give no genotype",
                    "ClinVar ABCA1 is dominated by unrelated testing; no comparator, no catalogue; GPSEA could not run"],
        "lad1": ["The gap list is dominated by one review (van de Vijver 2012) whose people are accession numbers; many candidates may be numbering slips",
                 "Input problem: one supplement cut at 60,000 characters, so patients P75 to P127 have no clinical rows",
                 "Gene-name spelling (ITGβ2, ITGß2, CD18) covers 148 variant rows; the matcher accepts them"],
        "axd": [f"Lowest normalization ({pct(s4['axd']['cdna_normalized_share'], 0)}%): cDNA printed without \"c.\", legacy numbering; {s4['axd']['status_counts'].get('protein_only', 0)} protein-only strings match ClinVar only at tier 2",
                f"Completeness vs Grossi 2024: {kn(comp['axd']['recall_restricted_primary'], 0)} restricted; the two misses are notation",
                "Missense dominates, as expected for a gain-of-function leukodystrophy; GPSEA found no hotspot difference"],
        "danon": [f"Highest gatekeeper unsupported share ({pct(run['danon']['unsupported_or_not_found']['share'], 2)}%): three papers hold {sum(n for _, n in run['danon']['top3_papers_unsupported'])} of {run['danon']['unsupported_or_not_found']['k']}",
                  "Sex difference reproduced (GPSEA): males more often show myopathy and hypertrophy; a reproduction check",
                  "D-43: one candidate withdrawn as an isoform artefact; LAMP2B-numbered variants need the panel's attention"],
    }
    for d in DISEASES:
        pp = D["pp"][d]
        top3 = "; ".join(f"{lbl} {pct(n / pp['n'], 0)}%" for _, lbl, n, _ in pp["top_observed"][:3])
        classes = sorted(pp["variant_classes"].items(), key=lambda x: -x[1])[:3]
        tot_cls = max(1, sum(pp["variant_classes"].values()))
        cls_txt = ", ".join(f"{k} {pct(v / tot_cls, 0)}%" for k, v in classes)
        omp = om["per"][d]
        add("bullets", f"{NAME[d]} ({GENE[d]})" + (" — development disease" if d == "ha20" else ""),
            f"{NAME[d]}. {N(cov[d]['manifest_rows'])} records screened, {cov[d]['in_corpus']} in the corpus, {cov[d]['fulltext']} with open full text, {run[d]['papers']} papers extracted. "
            f"{N(s4[d]['individual_rows'])} rows became {N(s4[d]['identities'])} identities, {N(s4[d]['identities_with_target_variant'])} with a variant in the gene; the most observed features are {top3.replace('%', ' percent')}. "
            f"The gatekeeper judged {pct(run[d]['unsupported_or_not_found']['share'], 2)} percent of claims unsupported. Against ClinVar, HGVS recall at tiers one and two was {spoken_kn(o2a[d]['hgvs_recall_tier12'])} and overlap {spoken_kn(o2a[d]['overlap_tier1'])}. "
            f"{om['gap_live'][d]} candidates are absent from both databases, and {spoken_kn(rec[d])} of OMIM's listed variants were recovered. "
            + " ".join(notable[d][:2]).replace("%", " percent") + ".",
            fontSize=11.5,
            bullets=[f"Corpus: {N(cov[d]['manifest_rows'])} screened; {cov[d]['in_corpus']} in corpus; {cov[d]['fulltext']} open full text ({pct(cov[d]['fulltext_share'], 0)}%); {run[d]['papers']} papers extracted. ClinVar ({cv_date}): {N(cv[d]['total'])} records, {cv[d]['plp']} P/LP",
                     f"Records: {N(s4[d]['individual_rows'])} rows → {N(s4[d]['identities'])} identities ({s4[d]['merged_pairs']} merges); {N(s4[d]['identities_with_target_variant'])} with a {GENE[d]} variant; {N(s4[d]['phenopackets'])} phenopackets, {N(s4[d]['with_interpretation'])} with an interpretation; most observed: {top3}",
                     f"Variants: {s4[d]['distinct_variant_descriptions']} distinct descriptions; cDNA normalized {pct(s4[d]['cdna_normalized_share'], 0)}%; classes {cls_txt}",
                     f"Gatekeeper: {pct(run[d]['unsupported_or_not_found']['share'], 2)}% unsupported ({run[d]['unsupported_or_not_found']['k']} of {N(run[d]['model_claims_judged'])}); {run[d]['papers_with_any_unsupported']} of {run[d]['papers']} papers. Repeat ({rep[d]['papers_compared']} papers): checklist {pct(rep[d]['checklist_agreement'], 1)}%, variant keys {pct(rep[d]['variant_key_jaccard'], 0)}%",
                     f"ClinVar: HGVS recall tier 1 {kn(o2a[d]['hgvs_recall_tier1'])}, tiers 1+2 {kn(o2a[d]['hgvs_recall_tier12'])}; overlap {kn(o2a[d]['overlap_tier1'])}; classification agreement {kn(o2a[d]['classification_agreement_among_stated'])}",
                     f"Gaps and OMIM: {om['gap_live'][d]} live candidates of {gaps[d]['tier1_alleles']} placed alleles; {gaps[d]['reclassification_candidates']} reclassification candidates; OMIM {rec[d]['k']} of {rec[d]['n']} recovered, {omp['A_literature']['av_source_pmids_extracted']} of {omp['A_literature']['av_source_pmids']} OMIM source papers extracted",
                     *notable[d]])
    add("table", "Spend by budget line",
        f"Spend. By this session's own usage readings, about {N(b['total'])} dollars of the 45,000 dollar award had been used by {b['reading_at'][:10]}, about four percent. Extraction and the gatekeeper account for most of it. The readings are estimates, not billing figures: they sometimes froze for an hour, stages overlapped, and whether this session runs on the funded account is still being confirmed. "
        f"Measured unit costs on this route: about two dollars per paper for extraction and under half a cent per judged claim for the gatekeeper; the six-disease run with its ten percent repeat came in well under its 1,200 dollar ceiling. The open-weight compute was billed outside the award, about {D['ow_manifest']['ha20']['key_spend_both_runs_usd']['spent']:.0f} dollars. "
        + (f"A separate exploratory pilot in another session cost about {N(round(abl))} dollars and is not covered in this talk. " if abl else "")
        + "The large remaining costs of the project are human hours, which the award does not fund.",
        head=["Line", "Budget line", "Requested", "Spent (estimate)", "Share"], colW=[0.6, 4.6, 1.3, 1.4, 1.1], fontSize=10,
        rows=[[l["n"], l["name"], f"${l['requested']:,.0f}", f"${l['spent']:,.2f}", f"{pct(l['spent'] / l['requested'])}%"] for l in b["lines"]]
             + [["—", "Not yet assigned to a line", "", f"${b['unassigned']:,.2f}", ""], ["", "Total, this session's readings", "$45,000", f"${b['total']:,.2f}", f"{pct(b['total'] / 45000)}%"]],
        note=f"Session usage readings at list price, including helper agents; not billing figures (D-15). Open-weight compute (${D['ow_manifest']['ha20']['key_spend_both_runs_usd']['spent']:.0f}) billed outside the award." + (f" An exploratory pilot in a separate session (about ${N(round(abl))}) is not covered here." if abl else ""), noteY=4.6)

    # ------------------------------------------------------------------ Part 4
    add("section", "Part 4. What it means, the gaps, and what we need from you", "Part four. What it means, the gaps in the study, and what we need from you.", kicker="GP-RareLink deep dive")
    add("cards", "What the data say, and what they do not",
        f"What the data say. The pipeline runs end to end on six diseases at the scale the grant projected, with provenance that holds on every value and repeats that are stable where the schema fixes the vocabulary. It produces {N(t['phenopackets'])} valid phenopackets, a ClinVar comparison with intervals on every figure, an OMIM check against a human-curated holdout, and {live} candidate gaps that two successive ClinVar releases confirm are absent. "
        f"What the data do not say: nothing here establishes the accuracy of the frozen pipeline. The gatekeeper's figure is a filter's reading; the only human-rated figures come from the pilot, before the rules those audits produced were frozen. Against OMIM the run recovered {pct(rec_all['share'], 0)} percent of the listed variants, but the misses are mostly papers the pipeline could not read, so that figure measures corpus coverage as much as extraction. "
        f"The gatekeeper's value is in the records, not the metric: it removed {N(dropped_all)} claims before the phenopackets were built, and its reasons name the failure modes a person should look for first.",
        numbered=True, lastAccent=True,
        cards=[["What the data say", f"End to end on six diseases at the projected scale ({N(t['papers'])} papers against \"roughly 300\"); provenance holds on every value; checklist repeats are stable; {N(t['phenopackets'])} valid phenopackets; intervals on every concordance figure; {live} candidates absent from two ClinVar releases and from OMIM. Three directional expectations stated before registration are consistent with what was seen."],
               ["What the data do not say", f"Nothing establishes the frozen pipeline's accuracy. The gatekeeper's {pct(t5['unsupported'] / t5['model_claims'], 2)}% is a filter's reading; the human figures ({pct(a1['share'])}%, {pct(a2['share'])}%) are from the pilot. OMIM recall ({pct(rec_all['share'], 0)}%) measures coverage as much as extraction. Low ClinVar recall awaits triage. Two diseases, one open-weight model, one judge model."],
               ["What the gatekeeper is for", f"The records, not the metric: it removed {N(dropped_all)} claims before the phenopackets were built, and its reasons name the failure modes to look for first (relatives' variant fields, hedged wording, cohort statements). O1 will give its accuracy against human labels, which is the number to report."]])
    add("cards", "What the OMIM holdout adds",
        "The OMIM holdout gave three things the ClinVar scoring could not. A direction: where OMIM's source paper was in the run, the curated variant was almost always in our record with the right individuals and zygosity, and the per-patient detail was richer than OMIM's summary; where it was not, the cause was access or search, not reading. "
        "A correction: the OMIM check caught a candidate that was a transcript-isoform artefact, which the ClinVar check could not see because the wrong allele was absent from ClinVar too; the fix is now in the pipeline. "
        "And a caution: OMIM itself carries legacy numbering and two allelic variants linked to the wrong ClinVar records, so any concordance figure against OMIM should footnote them, and a holdout curated by people deserves the same provenance checks as our output.",
        numbered=True, lastAccent=True,
        cards=[["A direction", "Where OMIM's source paper was read, the curated variant was almost always in our record with the right individuals and zygosity, with richer per-patient detail than OMIM's summary. Where it was not, the cause was access or search, not reading."],
               ["A correction", "The OMIM check caught a candidate that was a transcript-isoform artefact of our normalization; the ClinVar check could not see it because the wrong allele was absent from ClinVar too. The fix (D-43) is in the pipeline."],
               ["A caution", "OMIM carries legacy numbering and two allelic variants linked to the wrong ClinVar records. Concordance figures against OMIM should footnote them; a human-curated holdout needs the same provenance checks as a machine's output."]])
    add("table", "Gaps, part 1: what needs people",
        f"The report lists nineteen gaps, each with what it blocks, who acts, and a rough cost. The first six need people, not models. The primary audit is unrated: two panel members rate {D['o1']['n']} claims, roughly ten to fifteen hours each, and a third breaks ties; it unlocks the only confirmatory outcome and the gatekeeper's accuracy against human labels. "
        f"OMIM's phenotype half is unassessed: freezing the six clinical synopsis pages and one harness run would close it. The {live} candidates are unadjudicated: ten to fifteen minutes each. The fifty ClinVar misses await triage: two to four hours. The blinded open-weight audit needs the same raters. And the bias arm needs four comparator sheets, one to two hours each.",
        head=["#", "Gap", "What it blocks", "Who acts", "Rough cost"], colW=[0.5, 2.5, 2.4, 1.9, 1.7],
        rows=[["G1", f"O1 human audit not rated ({D['o1']['n']} claims)", "The primary outcome; gatekeeper accuracy vs human labels; any accuracy claim", "PI shares the two rater pages; two panel members rate; a third breaks ties", "8 to 25 panel hours; $0 model"],
              ["G2", "OMIM's phenotype half not assessed; OMIM read from frozen pages, not an API", "Phenotype concordance against OMIM's clinical synopses; the OMIM submission route", "PI freezes the six synopsis pages (or the API request lands); one harness run", "$0 model; about a day of scripting"],
              ["G3", f"{live} gap candidates not adjudicated", "Approved variants, submission drafts, expert-minutes, the gap-closure deliverable", "PI shares the adjudication page; the panel reviews the dossiers; PI signs off", f"{live} × 10 to 15 min ≈ 36 to 54 panel hours"],
              ["G4", "O2 miss triage not done (50 sampled misses)", "Whether low ClinVar recall is extraction error, normalization, or citations that do not describe the variant", "A panel member or the PI, on the private triage page", "2 to 4 hours"],
              ["G5", "Blinded Claude vs open-weight audit not drawn", "The registered O5 accuracy measure; the only neutral check on the gatekeeper's reading", "Size with the panel's hours; draw by seed; same raters, blind to model", "about 7 to 20 panel hours for n = 100"],
              ["G6", "Bias arm has no numbers", "Per-disease frequency deviation; the ascertainment-bias deliverable", "A person fills four comparator sheets without looking at literature frequencies; then the script runs", "4 sheets × 1 to 2 hours"]],
        fontSize=8.5, note="From the full report's section 5 (Table 16). Hours are guesses until the adjudication page logs real minutes.", noteY=4.95)
    add("table", "Gaps, part 2: access, inputs, notation, bookkeeping",
        "The remaining gaps are about access, inputs, notation and bookkeeping. Open access only leaves fourteen to fifty-three percent of each corpus readable, so completeness and the gap count are lower bounds; adding institutional access would be a deviation and a re-run of a few hundred papers at about two dollars each. "
        "Three extraction gaps were frozen on purpose and should wait for the audit's number: no hedge rule, relatives' variant fields from the proband's sentence, and cohort statements applied to individuals. About ten papers had conversion problems, and notation issues like legacy numbering and variants stated only in prose block tier-one matching. "
        "Thirty-eight of the eighty-four papers OMIM cites for its variants were never returned by our searches because they use pre-gene-era disease names, a search-term gap. And several bookkeeping items wait on the principal investigator: the pre-registration tags and OSF registration, the budget reconciliation, and the drafted messages to Monarch and ClinVar.",
        head=["#", "Gap", "What it blocks", "Who acts", "Rough cost"], colW=[0.5, 2.6, 2.3, 1.9, 1.7], fontSize=8.5,
        rows=[["G7", f"Open access only: {pct(min(c['fulltext_share'] for c in cov.values()), 0)} to {pct(max(c['fulltext_share'] for c in cov.values()), 0)}% of each corpus readable", "Completeness denominators; recall of the paywalled literature; the gap count is a lower bound", "None within the rules; institutional access would be a deviation and a re-run", "about $2 per paper plus gatekeeper; ~300 papers ≈ $600 to 900"],
              ["G8", "Extraction gaps frozen on purpose: no hedge rule; relatives' variant fields; cohort statements", "A share of unsupported claims; would need a v7 and a deviation", "Wait for O1; if it fails or shows these classes, propose v7 and re-run", "full re-run ≈ $800 to 1,000"],
              ["G9", "Input conversion problems in about 10 papers (scrambled or image tables, truncated supplements)", "Recall in those papers; several O2 misses", "Fix the converter or refetch; re-extract under a logged deviation", "$40 to 60 for 12 papers"],
              ["G10", "Notation and normalization: legacy numbering, protein-only strings, variants stated only in prose", "Tier-1 matching: recall, overlap, candidates for those variants", "Harness-side query corrections; a narrow rule for prose protein changes", "$0 model; 1 to 2 days"],
              ["G18", "Historical disease names absent from the searches (38 of 84 OMIM source papers never returned)", "Corpus recall of the founding literature for LAD-I, Danon and Tangier", "Add the names to the search configuration and re-search; a deviation", "$0 search; screening ≈ $0.05 per record"],
              ["G11-G19", "Same-person groups unmerged; HPO maps unreviewed; probe underpowered; minutes unmeasured; budget unreconciled; tags and OSF pending; drafts unsent", "Deduplicated counts; HPO review; the public timestamp on the freeze; outreach", "Mostly the PI; a few person-hours", "hours"]],
        note="Items G8 to G10 and G18 change the frozen pipeline or corpus and should wait for the audit's measured failure rate.", noteY=5.0)
    add("table", "A recommended order",
        "The recommended order puts the no-cost human steps first and holds any change to the frozen pipeline until the audit gives a measured failure rate. Step one: settle the panel and share the audit pages, drawing the open-weight audit sample at the same time. Step two: freeze the OMIM synopsis pages or submit the API request, push the pre-registration tags, register on OSF, send the drafts; no cost, long lead times. "
        "Step three: triage the fifty ClinVar misses and the LAD-I candidates first, because they tell us whether low recall and the biggest gap list are real before the panel spends hours on them. Step four: the small human tasks that each unblock a registered figure, the comparator sheets, the checklist maps, the merge groups. "
        "Only after the audit reads: decide on version seven and a re-run, the input repairs, the notation repairs and the historical-name re-search. Then the panel adjudicates the remaining candidates, and submissions follow sign-off. Steps one to four cost no model spend and about sixty to one hundred and ten panel hours in all.",
        head=["Step", "Do", "Why first"], colW=[0.6, 4.6, 3.8], fontSize=10.5,
        rows=[["1", "Settle the panel (D-11) and share the O1 pages; draw the O5 audit sample at the same time (G1, G5)", "Unblocks the primary outcome and the only neutral check on the gatekeeper"],
              ["2", "Freeze the OMIM synopsis pages or submit the API request (G2); push the tags; register on OSF; send the drafts (G16, G17)", "No cost; long lead times start now"],
              ["3", f"Triage the 50 O2 misses and LAD-I's {gaps['lad1']['gap_candidates']} candidates first (G4, part of G3)", "Tells us whether low recall and the biggest gap list are real before the panel spends hours on them"],
              ["4", "Fill the four comparator sheets (G6); review the checklist maps (G12); confirm the merge groups (G11)", "Small human tasks that each unblock a registered figure"],
              ["5", "Only after O1 reads: decide on v7 and a re-run (G8), the input repairs (G9), the notation repairs (G10), the historical-name re-search (G18)", "Changes to the frozen pipeline are deviations and should answer a measured failure, not an expected one"],
              ["6", "Panel adjudication of the remaining candidates (G3), then drafts and sign-off", "Months 4 to 5 per plan; the dossiers and the page are ready"]],
        note="Steps 1 to 4 cost no model spend and about 60 to 110 panel hours in all, most of it adjudication. Nothing in steps 1 to 4 touches the frozen pipeline.", noteY=4.6)
    add("bullets", "Limitations of this report",
        "The limitations, stated as the report states them. There is no human-rated accuracy for the frozen pipeline; every support figure is a model's reading of a model's output. The development disease is in every table, flagged, but its rules were tuned on its own papers. OMIM is a sample and only its variant half is in; the patient-level comparison was judged by Claude, not a panel member. "
        "Open access only: the corpora hold fourteen to fifty-three percent of the eligible literature. Cost figures are session estimates with frozen readings and overlapping stages. Helper-reported problems are model output, recorded as such and not verified by a person. "
        "And one more, which the report states about itself: the author of the report is the pipeline's author. Claude Code built the pipeline, ran it, and generated the report and this talk from its outputs. The numbers are reproducible from the committed files; the framing is not independent of the system it describes. That is one more reason the human audit decides.",
        bullets=["No human-rated accuracy for the frozen pipeline: every support figure is a model's reading of a model's output",
                 "HA20 is in every table, flagged; its rules were tuned on its own papers. Quote the five-disease figures",
                 "OMIM is a sample, and only its variant half is in; the patient-level comparison was judged by Claude, not a panel member",
                 f"Open access only: {pct(min(c['fulltext_share'] for c in cov.values()), 0)} to {pct(max(c['fulltext_share'] for c in cov.values()), 0)}% of the eligible literature; completeness and recall are measured on what was accessible",
                 "Cost figures are session estimates with frozen readings and overlapping stages; the open-weight key is shared",
                 "Helper-reported problems (input conversion, self-contradicting papers, likely non-gaps) are model output, not verified by a person",
                 "The author of the report is the pipeline's author: the numbers are reproducible from the committed files; the framing is not independent of the system it describes"])
    add("table", "What we need from you",
        f"Which brings us to you. Four roles, each unlocking a registered result or a deliverable. Audit raters: rate {D['o1']['n']} extracted values against their quoted evidence on a blinded web page, two raters and a tie-breaker, ten to fifteen hours each; this is the primary outcome and the first true accuracy figure. "
        f"Adjudicators: review the {live} candidate variants from their dossiers and decide whether the evidence supports a submission, ten to fifteen minutes per candidate; this is the gap-closure deliverable. Cohort readers: fill a comparator sheet of clinical-feature frequencies from a natural-history paper without looking at our records, one to two hours per sheet; this is the bias arm. "
        "And methods or domain reviewers: read the paper or the report and tell us what is wrong, missing or unclear from your field's point of view. Everything is published literature; there is no patient data. The dashboard has a short form where you can tell us who you are and how you would like to contribute.",
        head=["Role", "What you would do", "Effort", "What it unlocks"], colW=[1.6, 3.6, 1.6, 2.2], fontSize=11, rowH=0.56,
        rows=[["Audit rater", f"Rate {D['o1']['n']} extracted values against their quoted evidence on a blinded web page; two raters and a tie-breaker", "10 to 15 hours per rater", "The primary outcome: the first true accuracy figure"],
              ["Adjudicator", f"Review the {live} candidate variants from their dossiers and decide whether the evidence supports a submission", "10 to 15 minutes per candidate", "ClinVar literature-only submissions and OMIM candidates"],
              ["Cohort reader", "Fill a comparator sheet of clinical-feature frequencies from a natural-history paper, without looking at our records", "1 to 2 hours per sheet", "The ascertainment-bias arm"],
              ["Methods or domain reviewer", "Read the short paper or the full report and tell us what is wrong, missing or unclear, from your field's point of view", "1 to 3 hours", "A better study before anything is submitted"]],
        note="Tell us who you are and how you would like to contribute through the form on the dashboard. Everything is published literature; there is no patient data.", noteY=4.6)
    add("closing", "Thank you",
        "Thank you for listening. Everything in this talk, the short paper, the full report and its supplement, this deck with its notes, the candidate list and the form, is on the dashboard. Every number traces to a file in the project repository at a stated commit, and the report says plainly which questions are still open: the human audit, the access decision, and the adjudication of the candidates. "
        "We look forward to working with you.",
        lines=["The dashboard holds the short paper, the full report and supplement, this deck, the videos, the candidate list and the form.", PAGES_URL,
               f"Every number in this talk comes from the project repository at commit {D['commit']}. Still open: the human audit, the access decision, the adjudication of the candidates."])

    words = sum(len(s["narration"].split()) for s in S)
    spec = {"title": "GP-RareLink deep dive: the interim report in about 45 minutes", "footer": "GP-RareLink · deep dive for collaborators · internal review", "date": date.today().isoformat(),
            "commit": D["commit"], "output": "reports/deck/gp_rarelink_deep_dive.pptx", "pages_url": PAGES_URL, "figures": figures, "slides": S}
    OUT.write_text(json.dumps(spec, indent=1))
    print(f"wrote {OUT}: {len(S)} slides, {words:,} narration words (about {words / 150:.0f} min at 150 wpm)")


if __name__ == "__main__":
    main()
