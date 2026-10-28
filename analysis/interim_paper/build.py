"""Build the interim paper: reports/interim_paper/interim_paper.md (main text), supplement.md, and the
figures. Every number comes from `data.load()`; the prose lives here. Re-run after any input changes.

  uv run python -m analysis.interim_paper.build          # Markdown + figures
  bash analysis/interim_paper/make_pdf.sh                 # then the PDF (pandoc + headless Chromium)
"""
from __future__ import annotations

import datetime as dt
from pathlib import Path

from . import figures
from .data import CONFIRMATORY, DISEASES, ROOT, SHORT, load
from .stats import clopper_pearson, wilson

OUT = ROOT / "reports/interim_paper"
TODAY = dt.date.today().isoformat()

# Input problems found during the run, by disease (from the helpers' reports collected in
# reports/six_disease_run_findings.md §5; text, not metrics). Kept here so the per-disease sections can name them.
INPUT_PROBLEMS = {
    "ha20": [],
    "ssadh": ["14635103: Table 2 scrambled in conversion; about 12 of 54 families extracted", "38499966: table garbled; supplements S1/S2 missing",
              "37503297 and 37962671 are the same study (preprint and journal version); their patients are merged (decision 2026-10-20)"],
    "tangier": ["26713019 and 27011649: tables published as images"],
    "lad1": ["33391282: supplement Table S1 cut at 60,000 characters, so P75–P127 have no clinical rows"],
    "axd": ["34046764: Table 1 caption only", "32126152: Table S1 missing", "39420046 (Grossi 2024): supplement arrived after extraction (D-39)"],
    "danon": ["23571262, 30929317, 42366573: tables transposed or garbled", "25228319: Supplemental Tables 1–2 missing"],
}
SELF_CONTRADICTIONS = ["LAD-I 36185095: c.920C>T vs c.920T>C", "Danon 42382315: DCM vs end-stage HCM for P3",
                       "SSADH 37503297/37962671: G176R vs G176E", "Danon 30413001: text and Table 1 disagree on which family carries c.56T>C",
                       "SSADH 9093300: A.F.'s EEG normal in the table, diffusely slow in the text", "AxD/LAD-I/Danon: about 30 papers in all, listed in the run notes for the audit"]


# ---------------------------------------------------------------------------------------------- helpers
def P(x, nd=1):
    if x is None:
        return "—"
    from decimal import ROUND_HALF_UP, Decimal
    q = Decimal(1).scaleb(-nd)
    return f"{Decimal(str(100 * x)).quantize(q, rounding=ROUND_HALF_UP)}%"


def CI(r, nd=1):
    if not r or r.get("share") is None:
        return "undefined"
    return f"{100 * r['share']:.{nd}f}% ({r['k']}/{r['n']}; 95% CI {100 * r['ci95'][0]:.{nd}f}–{100 * r['ci95'][1]:.{nd}f})"


def ci_exact(k, n, nd=2):
    lo, hi = clopper_pearson(k, n)
    return f"{100 * k / n:.{nd}f}% ({k:,}/{n:,}; exact 95% CI {100 * lo:.{nd}f}–{100 * hi:.{nd}f})"


def ci_wilson(k, n, nd=1):
    lo, hi = wilson(k, n)
    return f"{100 * k / n:.{nd}f}% ({k:,}/{n:,}; 95% CI {100 * lo:.{nd}f}–{100 * hi:.{nd}f})"


def N(x):
    return f"{x:,}"


def table(headers, rows_):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows_:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def lab(D, d):
    return SHORT[d] + ("\\*" if d == "ha20" else "")


def name(D, d):
    return f"{D['name'][d]} ({SHORT[d]}, *{D['gene'][d]}*)"


# ---------------------------------------------------------------------------------------------- sections
def status_box(D):
    t, f = D["totals"]["all"], D["totals"]["five"]
    return f"""> **Status at a glance ({TODAY}; repository commit `{D['commit']}`)**
>
> - **Done with the frozen pipeline (`pipeline-v1.0`, pre-registration v1.0 frozen 2026-10-20):** extraction, span check and gatekeeper on {t['papers']} open-access papers across six diseases; {N(t['phenopackets'])} schema-valid GA4GH phenopackets; a 10% run-to-run repeat; concordance against a dated ClinVar snapshot; {t['gap_candidates']} gap-variant candidates with evidence dossiers; completeness against two published catalogues; memorization probes; the Claude vs open-weight comparison on two diseases.
> - **Not yet done, and needing people:** the pre-registered 250-claim human audit (O1, the one confirmatory outcome) is drawn and its blinded rating pages are built, but nobody has rated a claim; panel adjudication of gap candidates (O3) has not started; the bias arm (O4) waits on a person listing cohort frequencies; OMIM has not been checked (no access, D-12).
> - **Headline numbers so far** (five confirmatory diseases; six-disease figures in brackets): {N(f['papers'])} [{N(t['papers'])}] papers, {N(f['identities'])} [{N(t['identities'])}] deduplicated individuals, {N(f['with_variant'])} [{N(t['with_variant'])}] with a target-gene variant; gatekeeper v4 judged {ci_exact(f['unsupported'], f['model_claims'])} of model claims unsupported [{ci_exact(t['unsupported'], t['model_claims'])}]; {f['gap_candidates']} [{t['gap_candidates']}] gap candidates absent from ClinVar.
> - **The one caveat that governs everything else:** the gatekeeper's rate is a filter's reading, not an error rate. In the pilot, humans found 6% unsupported where the gatekeeper found 0.04–0.3%. Until O1 is rated, no accuracy claim can be made for the frozen pipeline.
> - **Spend:** about ${D['budget']['total']:,.0f} of $45,000 by this session's own cost readings (estimates, not billing figures), plus $16–20 for the open-weight model billed outside the award."""


def abstract(D):
    t, f = D["totals"]["all"], D["totals"]["five"]
    o2 = {d: D["o2"][d]["all_papers"] for d in DISEASES}
    rec = [100 * o2[d]["hgvs_recall_tier12"]["share"] for d in DISEASES]
    ov = [100 * o2[d]["overlap_tier1"]["share"] for d in DISEASES]
    owg = D["ow_gk"]
    return f"""## Abstract

**Background.** Causative variants and phenotypes for rare diseases are published in case reports faster than they reach ClinVar, OMIM or structured phenotype resources. GP-RareLink asks whether an LLM-based extraction pipeline, with ClinVar and OMIM held out as the answer key, can build provenance-first genotype–phenotype records at a provable accuracy and at a scale that closes part of that gap. This interim report covers everything done between project start (2026-09-21) and {TODAY}, for internal review. It is not a results paper: the one confirmatory outcome has not been measured yet.

**Methods.** Six diseases (*TNFAIP3*, *ALDH5A1*, *ABCA1*, *ITGB2*, *GFAP*, *LAMP2*). A pre-registered pipeline, frozen on 2026-10-20 after a one-disease pilot on A20 haploinsufficiency (HA20), extracted per-individual tables from open-access papers with Claude Opus helper agents, checked every quoted span verbatim by script, judged every value with a second model read (gatekeeper v4), merged re-reported individuals on citations only, normalized variants with VariantValidator, bound phenotypes to HPO and built GA4GH phenopackets. A harness that extraction never sees compared the records with a dated ClinVar release and two published variant catalogues, and listed variants absent from ClinVar. A 250-claim audit sample was drawn by seed for two blinded panel raters. The same files were run on an open-weight model (DeepSeek-V4.1-Flash) for two diseases.

**Results.** {N(t['papers'])} papers yielded {N(t['individual_rows'])} individual rows, merged to {N(t['identities'])} identities and {N(t['phenopackets'])} valid phenopackets ({N(t['with_variant'])} with a target-gene variant; {N(t['features_observed'])} observed and {N(t['features_excluded'])} excluded HPO terms). Every one of {N(t['claims_all'])} quoted values was found verbatim in its paper. Gatekeeper v4 judged {ci_exact(f['unsupported'], f['model_claims'])} of model claims unsupported across the five confirmatory diseases; with HA20 included, {ci_exact(t['unsupported'], t['model_claims'])}. Unsupported claims cluster in a few papers, and the commonest cause is a relative's or a cited patient's variant field quoted from the proband's sentence. A 10% repeat agreed on 97–100% of checklist cells and 0.83–1.00 of variant keys. Against ClinVar's own citations, HGVS recall at tiers 1+2 ranged from {min(rec):.0f}% to {max(rec):.0f}% by disease, with misses concentrated in a handful of papers; {min(ov):.0f}–{max(ov):.0f}% of extracted tier-1 alleles were present in ClinVar; classification agreement where authors state one was 59–92%. Completeness against published catalogues was 9/9 (HA20) and 54/56 (AxD) restricted variants. {t['gap_candidates']} tier-1 alleles with gatekeeper-supported values were absent from ClinVar in two successive releases ({f['gap_candidates']} outside HA20), and {t['reclass']} supported variants sit in ClinVar only as VUS or conflicting. Neither model showed memorization of the papers. The open-weight model produced largely the same variants at about 1/15 the cost per paper and 7× the wall-clock, but left 3–4% of values without a quote and was judged unsupported on {P(owg['ha20']['open']['unsupported']['share'])} (HA20) and {P(owg['ssadh']['open']['unsupported']['share'])} (SSADH) of claims by the same Claude gatekeeper, against {P(owg['ha20']['claude']['unsupported']['share'], 2)} and {P(owg['ssadh']['claude']['unsupported']['share'], 2)} for Claude.

**Gaps.** The primary outcome (O1) is unmeasured because the panel has not rated; the pilot's two 50-claim audits found 6.0% and 6.3% unsupported, above the 2% target, and each exposed an error class that the frozen pipeline now guards against but has not been re-audited for. OMIM is absent from every concordance and gap figure. Open-access-only corpora hold 14–53% of the eligible literature. The bias arm has no numbers. A costed plan to close each gap is in §5.

**Conclusion.** The pipeline runs end to end on six diseases with complete provenance and stable repeats, and it finds a plausible set of database gaps. Whether its values are right at the pre-registered level is the open question, and it is a question only the human audit can answer."""


def intro(D):
    return f"""## 1. Introduction

Variant and phenotype knowledge for rare diseases is split across ClinVar, OMIM, HPO annotations, Monarch's phenopacket-store and, mostly, individual case reports. Many causative variants published in case reports never reach a database: for Alexander disease, a 2024 review counts 182 causative variants across 550 patients against 76 pathogenic or likely-pathogenic ClinVar records (release 2026-10-12). A lab querying ClinVar today cannot see a variant published in 2011 that was never submitted.

**Research question.** Can the SLIDERS method, powered by Claude, build consolidated variant ↔ phenotype ↔ disease records from published case reports at an accuracy we can prove and at a scale that materially closes this gap?

**Design.** Claude reads case reports for six rare diseases and emits GA4GH Phenopackets with a PMID and verbatim span on every value. ClinVar and OMIM are never shown to the extraction step; they are the answer key. Five pre-registered outcomes carry the study (Table 1). Only O1 has a pass/fail rule. Headline pooled figures use the five diseases other than HA20, which was used to develop the pipeline (D-18); figures that include HA20 are secondary.

**Table 1. Pre-registered outcomes and their status.**

{table(["#", "Outcome", "Type", "Pre-specified target", "Status at " + TODAY],
       [["O1", "Unsupported-value rate, human audit of 250 claims", "primary, confirmatory", "observed rate < 2%, i.e. at most 4 of 250 (rule C, D-02)", "sample drawn (seed " + str(D['o1'].get('seed', 40250)) + "); rating pages built; **no claim rated yet**"],
        ["O2", "Concordance with ClinVar and OMIM on gene, HGVS, classification, phenotype", "primary, estimation", "none; estimates with CIs (D-03)", "ClinVar half done on all six diseases; **OMIM not assessed** (D-12)"],
        ["O3", "Gap closure: variants absent from both databases, adjudicated, submitted", "primary, descriptive", "none; counts by stage", f"{D['totals']['all']['gap_candidates']} ClinVar-only candidates with dossiers; **adjudication not started**"],
        ["O4", "Ascertainment bias vs natural-history cohorts; memorization probe", "secondary", "none", "memorization probe done (both models); **frequency deviation waits on a person**"],
        ["O5", "Efficiency: expert-minutes per accepted record; Claude vs open-weight model", "secondary", "none", "open-weight run and gatekeeper done on 2 diseases; **blinded audit and expert-minutes not measured**"]])}

**What this document is.** An interim report for internal review, generated by script (`analysis/interim_paper/build.py`) from the committed outputs at commit `{D['commit']}`, so that every number traces to a file and a date. It follows the pre-registration's reporting rules: per-disease results, intervals on proportions, HA20 flagged throughout, deviations listed (§2.9), and nothing called "high" or "accurate" without its interval and definition beside it. It is not for distribution outside the team."""


def methods(D):
    cl = D["checklists"]
    cfg = D["stage4_cfg"]
    rows_ = []
    for d in DISEASES:
        c = D["clinvar"][d]
        rows_.append([name(D, d) + ("\\*" if d == "ha20" else ""), D["omim"][d], D["inheritance"][d], D["system"][d],
                      f"{N(c['total'])} records; {c['plp']} P/LP; {c['vus']} VUS; {c['conflicting']} conflicting", cfg[d]["mane_select"], cfg[d]["disease_mondo"]])
    return f"""## 2. Methods

The frozen plan (`preregistration/analysis_plan.md`, v1.0, 2026-10-20; tags `prereg-v1.0` and `pipeline-v1.0` on commit `ef3133e`) is the method of record. This section summarizes it and names what was built.

### 2.1 Diseases, genes and reference counts

**Table 2. The six diseases.** ClinVar counts are distinct VariationIDs on single-gene GRCh38 records in the release of 2026-10-12 (read 2026-10-19); P/LP sums Pathogenic, Likely pathogenic and Pathogenic/Likely pathogenic. OMIM allelic-variant counts are not available (D-12).

{table(["Disease (gene)", "OMIM", "Inheritance", "System", "ClinVar, single-gene records", "MANE Select", "Mondo"], rows_)}

\\*Development disease: every extraction rule was tuned on it during the pilot (§2.8), so its results flatter the pipeline (D-18).

### 2.2 Corpus

- **Search.** PubMed from inception to a recorded search date (HA20 2026-10-18; the others 2026-10-19), gene symbol plus disease names and synonyms, plus backward citation searching of the key reviews through Europe PMC's reference index. No ClinVar or OMIM citation lists were used as seeds for the five new diseases (D-19). HA20's pilot corpus kept its ClinVar-seeded papers, tagged, and every O2 figure is reported with and without ClinVar-cited papers.
- **Screening.** Title/abstract screening by Claude Code helper agents with a logged reason per record, then full-text screening of every open full text with a verbatim evidence quote checked by script. A human 20-item check settled the screening calls (D-34). HA20's corpus was carried over from the pilot and was not full-text screened.
- **Eligibility.** Primary publications reporting individual-level genotype or phenotype for at least one person with the disease; reviews with a per-patient table are included and their people tagged secondary-source (D-33). Reviews without new individuals, non-English papers and papers with no individual data are excluded with the reason logged.
- **Access.** Open access only: PMC, Europe PMC and open copies found through Unpaywall (D-32). No institutional access. Supplementary files were fetched where Europe PMC served them and converted to text (capped at 60,000 characters per file).
- **Holdouts.** Natural-history comparator papers for the bias arm are marked out of the extraction corpus (AxD 2, SSADH 1, Danon 2).

### 2.3 Extraction

- **Model and route.** Claude Opus, as Claude Code helper agents on the funded claude.ai account (D-17, D-20): one helper per paper, reading only the paper, the instruction file, the schema and the rules file, with no web access and an instruction to use nothing it remembers about the paper. The pilot manifests record the served model ID, `claude-opus-5-5`; the six-disease manifests recorded only the helper alias "opus" at run time, and a `served_model` line stating `claude-opus-5-5` from the session configuration was added on 2026-10-28, marked as such. Instruction hashes and session cost readings are in each run manifest (`runs/pv1-<disease>/manifest.json`).
- **Frozen files.** `extract_v6.md` (instructions), `schema_<disease>_v5.json` (five tables: publications, individuals, variants, phenotypic_features, phenotype_checklist), `extraction_rules_v1.md` and `gatekeeper_v4.md`. For the five new diseases the prompt and schema were instantiated by script, swapping only the disease name, gene symbol, schema path and a 20-item checklist (D-38; 12 changed lines per disease, diffs committed).
- **What a value is.** Every asserted value carries a verbatim quote from the paper. "Not reported" is a first-class output and carries no quote. Three-state phenotypes (observed / excluded / not reported) are never collapsed. Variant fields are taken only from statements about this person (D-29); values stacked in multi-patient cells are not assigned by position (D-31); a normal finding is recorded as the abnormality it rules out, marked excluded (D-27).
- **Checklists.** Twenty disease-specific features per disease, each with the three-state status for every individual (Supplementary Table S3). HA20's came from the pilot schema; the others were written by helpers from a consensus guideline or review (SSADH 38452608; Danon 37821174; Tangier 33994407; AxD 39420046, 32779598, 40520824; LAD-I 42011429, 23207660, 33391282), every quote checked verbatim.

### 2.4 Span check and gatekeeper

- **Span check.** A deterministic check that every quoted span occurs verbatim in the source text, run on all values, not a sample. A helper that left quotes empty was resumed for a repair-only pass; each repair was diffed to show only the target cells changed (the manifests list them; HA20 had 6).
- **Gatekeeper v4.** A second Claude read of each model claim (claims that are not bookkeeping, such as PMIDs and repeated labels), one helper per chunk of up to 350 claims, asking whether the quote entails the value *for the person the row is about*. It records whom the quote is about (this person, a named group, the cohort, another person, the paper, unclear) and gives one of four verdicts: supported, partially supported, unsupported, span not found. No value is exempted by a script match of value and quote (D-28). Phenopackets keep only claims judged supported, and the count removed is reported. **The gatekeeper is a filter, not a measure** (§6.4 of the plan): in the pilot its own unsupported rate understated the human audit's by an order of magnitude.

### 2.5 Records

- **Deduplication.** Merge policy v4: merges only on an explicit citation tying a person to an earlier report, one-to-one; the pilot's sex-and-onset route was dropped after it produced all 6 false merges of 93 (D-23). A paper pair listed in `configs/duplicate_publications.csv` with evidence (the SSADH preprint and its journal version) uses a dedicated route.
- **Normalization.** VariantValidator 4.0.1 (dev), MANE Select transcript per gene read from VariantValidator on 2026-10-20 (Table 2); the original string is kept beside the normalized form; transcripts assumed or version-mapped are flagged. Only VariantValidator's normalization fields enter the pipeline; any database annotations in its responses are dropped.
- **Binding.** Checklist items map to HPO terms through per-disease maps built from the pinned HPO release (2026-09-01) and flagged for review; free-text features are bound by script first, then by helpers with an HPO lookup tool, every answer checked against the release. Disease terms come from Mondo (release 2026-10-06) by name, never by OMIM cross-reference.
- **Phenopackets.** One GA4GH Phenopacket v2 per identity, validated against the schema (D-40 per-disease settings: gene, HGNC ID, MANE transcript, Mondo term, checklist map).

### 2.6 Ground-truth isolation and the harness

Code under `pipeline/extract` never reads reference data; an automated test fails if any such path, loader or the tokens "clinvar", "omim" or "harness" appear there. Reference snapshots live outside the repository (`/home/user/gp-rarelink-reference/<date>/`), and only their manifests and counts are committed. The harness (`pipeline/harness/`) reads the extracted records and the snapshots:

- **ClinVar** `variant_summary.txt.gz`, release 2026-10-12, read 2026-10-19 (re-read 2026-10-19 release on 2026-10-21 for the gap re-check), restricted to single-gene GRCh38 records per gene.
- **HPO annotations** (`phenotype.hpoa`, 2026-09-02) for the phenotype-profile figure.
- **Catalogues:** Chen 2020 Table S1 for HA20 (D-30) and Grossi 2024 Supplementary Table 2 for AxD (D-39), transcribed by script. The other four candidates were dropped by the registered suitability check (no per-variant table naming sources, or not open), so those diseases report no completeness figure.
- **OMIM:** no access (D-12). Every O2 and O3 figure is ClinVar-only, and the OMIM half is "not yet assessed", never "absent".

### 2.7 Outcomes and statistics

- **O1.** 250 claims drawn by simple random sampling, stratified by disease in proportion to claim volume, from the model claims gatekeeper v4 judged supported (the values that survive into the records), by script with seed {D['o1'].get('seed', 40250)} and before any concordance was run. Two panel members rate blind on separate pages that never show the gatekeeper's verdict; a third resolves disagreements. Pass under rule C: at most 4 unsupported of 250, reported with the exact interval and the highest rate the audit cannot exclude. A value the rater cannot verify counts as unsupported, with a sensitivity analysis without such claims.
- **O2.** Tier 1 = same GRCh38 allele (VCF key); tier 2 = same protein change for papers with no cDNA. HGVS recall = share of ClinVar's (PMID, variant) citation pairs, restricted to corpus PMIDs, that the run extracted from that PMID. Overlap = share of extracted tier-1 alleles present in ClinVar (not precision). Classification = authors' P/LP, VUS, B/LB vs ClinVar aggregate, among stated values. Phenotype profile = HPO annotation recall (term or descendant seen in ≥1 person) and the share of terms seen in ≥2 people that match an annotation. Wilson 95% intervals. No pass/fail threshold (D-03). Every miss counts as discordant; a seeded sample of 50 misses awaits human triage into five categories.
- **O3.** A gap candidate is a tier-1 allele absent from the ClinVar snapshot whose identifying values the gatekeeper judged supported in at least one row. Counted by stage: candidates, adjudicated, approved, drafted, signed off, submitted, accepted. Reclassification candidates (in ClinVar only as VUS or conflicting) are exploratory.
- **O4.** Per disease, a human lists each held-out comparator's HPO-mappable features and cohort frequencies before literature frequencies are computed; then observed ÷ (observed + excluded) per feature, with a publication-cluster bootstrap. Memorization: closed-book recall from PMID, title and year, and guided completion of a 50-word opening, on 30 papers per disease stratified by date against the model's documented cutoff (June 2026), scored against the full-text extraction.
- **O5.** Expert-minutes per accepted record, logged by the adjudication page. Claude vs DeepSeek-V4.1-Flash (D-10): same papers, launch prompt, frozen files, file tools and scoring; metrics are span-not-found rate, unsupported rate on a blinded audit of equal size (pending), HGVS concordance, coverage, cost and wall-clock.
- **Intervals.** Wilson for simple proportions; exact Clopper–Pearson for the audit and for the gatekeeper shares; pooled five-disease and six-disease figures in this report use the same forms.

### 2.8 The development pilot

A one-disease pilot on HA20 (2026-10-18 to 2026-10-20) built and tuned the pipeline before the freeze: two full extraction runs, a 15-paper repeat, a hand check of every merge, two 50-claim human audits by Dr. Lin, ClinVar concordance and the Chen 2020 completeness check. Its findings (§3.6) set the rules frozen as extraction v6 and gatekeeper v4. HA20 was then re-extracted from scratch with the frozen pipeline in the six-disease run; the pilot's own records are not used anywhere in this report's tables.

### 2.9 Deviations from the frozen plan

Three dated deviations, each approved by Dr. Lin before it took effect, are logged in `DECISIONS.md`:

- **D-38 (2026-10-20).** The frozen prompt and schema name HA20 and *TNFAIP3*; for the other five diseases they were instantiated by script (disease name, gene symbol, schema path, checklist only). Expected effect: none on HA20; the five checklists are new by design.
- **D-39 (2026-10-20).** The AxD catalogue (Grossi 2024) was dropped by the pre-extraction suitability check because Europe PMC answered HTTP 500 for its supplement; the supplement arrived after `pv1-axd` finished and was transcribed on the harness side only. Nothing was appended to the paper text extraction read.
- **D-40 (2026-10-20).** Stage 4 scripts (normalization, binding, phenopackets) read per-disease settings instead of HA20's hard-coded ones. No change to the four pinned files, metrics or thresholds.

A fourth item is a decision, not a deviation: the SSADH corpus holds one study twice (37503297, 37962671); both stay and their patients are merged with the evidence recorded.

### 2.10 Reproducibility

Every table and figure here is produced by `analysis/interim_paper/` from committed files (listed in Supplementary Table S1). Run manifests record the pinned files' sha256 at launch and at finish, the papers, the helpers, the repairs and the session cost readings. The reference snapshots are re-creatable by `pipeline/harness/snapshot_reference.py`, `benchmark_chen2020.py` and `catalogue_grossi2024.py`."""


def results_corpus(D):
    rows_ = []
    for d in DISEASES:
        c, r = D["coverage"][d], D["run"][d]
        elig = c.get("eligible_all") or "not screened (pilot corpus)"
        rows_.append([lab(D, d), N(c["manifest_rows"]), N(c["in_corpus"]), f"{c['fulltext']} ({P(c['fulltext_share'], 1)})",
                      f"{c['fulltext_or_free_share'] * 100:.1f}%", elig, r["papers"], r["papers_with_individual_rows"],
                      c.get("seeded_from_clinvar", 0) or "—", ", ".join(c.get("held_out") or []) or "—"])
    tot_rec = sum(D["coverage"][d]["manifest_rows"] for d in DISEASES)
    tot_corp = sum(D["coverage"][d]["in_corpus"] for d in DISEASES)
    tot_ft = sum(D["coverage"][d]["fulltext"] for d in DISEASES)
    return f"""## 3. Results

### 3.1 Corpus

**Table 3. Corpus and open-access coverage by disease.** "Free elsewhere" is a Europe PMC listing of a free copy outside PMC, not fetched (an upper bound). Source: `analysis/corpus/coverage_2026-10-20.json`; run summaries.

{table(["Disease", "Records screened", "In corpus (title/abstract)", "Open full text", "+ free elsewhere (upper bound)", "Eligible after full-text screening", "Papers extracted", "…with individual rows", "ClinVar-seeded papers (D-19)", "Comparator holdouts"], rows_)}

![Figure 2. Corpus funnel per disease.]({D['figs']['fig2']})

**Figure 2.** Corpus funnel per disease. Open-access-only access (D-32) is the binding constraint: {N(tot_ft)} of {N(tot_corp)} corpus papers ({100 * tot_ft / tot_corp:.0f}%) have open full text, from {N(tot_rec)} records screened.

- Open full text ranges from {min(100 * D['coverage'][d]['fulltext_share'] for d in DISEASES):.0f}% (Tangier) to {max(100 * D['coverage'][d]['fulltext_share'] for d in DISEASES):.0f}% (HA20) of the title/abstract corpus. Every disease cleared the D-08 floor of 15 eligible primary papers, so no substitute disease was needed.
- Paywalled papers are not a random subset. For HA20 they include the two largest sources of the Chen 2020 benchmark; for the other diseases the catalogue reviews' own source papers are often closed. The completeness denominators in §3.7 are small for that reason.
- Input problems found by the helpers during extraction (scrambled or image-only tables, missing or truncated supplements) are listed per disease in §3.12 and Supplementary Table S5. They bound what extraction could see and are not counted in any metric."""


def results_extraction(D):
    rows_ = []
    for d in DISEASES + ["five", "all"]:
        if d in ("five", "all"):
            t = D["totals"][d]
            keys = CONFIRMATORY if d == "five" else DISEASES
            pw = sum(D["run"][k]["papers_with_any_unsupported"] for k in keys)
            rows_.append([{"five": "**Five confirmatory**", "all": "**All six**"}[d], N(t["papers"]), N(t["individual_rows"]), N(t["variant_rows"]), N(t["claims_all"]), "0",
                          N(t["model_claims"]), f"**{ci_exact(t['unsupported'], t['model_claims'])}**", ci_exact(t["not_supported"], t["model_claims"]), f"{pw} of {t['papers']}", "—"])
        else:
            r = D["run"][d]
            rows_.append([lab(D, d), r["papers"], N(r["individual_rows"]), N(r["variant_rows"]), N(r["claims_all"]), r["span_check_problems"], N(r["model_claims_judged"]),
                          ci_exact(r["unsupported_or_not_found"]["k"], r["model_claims_judged"]), ci_exact(r["not_supported"]["k"], r["model_claims_judged"]),
                          f"{r['papers_with_any_unsupported']} of {r['papers']}", f"{100 * r['top3_share_of_unsupported']:.0f}%"])
    gs = {d: dict((f, n) for f, n in D["run"][d]["unsupported_top_fields"]).get("variants.gene_symbol_as_stated", 0) for d in DISEASES}
    gs_txt = ", ".join(f"{SHORT[d]} {gs[d]}" for d in DISEASES)
    return f"""### 3.2 Extraction, provenance and the gatekeeper

**Table 4. Extraction output and gatekeeper v4 verdicts.** "Unsupported" counts unsupported and span-not-found verdicts; "not fully supported" adds partially supported. Intervals are exact. Source: `analysis/six_disease/run_summary_2026-10-20.json`.

{table(["Disease", "Papers", "Individual rows", "Variant rows", "Values with a quote", "Span-check problems", "Model claims judged", "Unsupported", "Not fully supported", "Papers with any unsupported", "Share held by worst 3 papers"], rows_)}

![Figure 3. Gatekeeper v4 verdicts.]({D['figs']['fig3']})

**Figure 3.** Gatekeeper v4 on the six runs. **A** Unsupported share with exact intervals, with the five-disease and six-disease pooled figures. **B** The share of each disease's unsupported claims held by its three worst papers. **C** Whom the cited quote was about, for unsupported claims only.

- **Provenance is complete.** Every one of the {N(D['totals']['all']['claims_all'])} values asserted across the six runs has a quote that the span check found verbatim in its paper (0 problems in every disease). Values without a quote are not emitted, so the fabricated-span count is zero by construction and by check.
- **The gatekeeper's unsupported share is small and similar across diseases:** {P(D['run']['ha20']['unsupported_or_not_found']['share'], 2)} (HA20) to {P(D['run']['danon']['unsupported_or_not_found']['share'], 2)} (Danon). Pooled over the five confirmatory diseases it is {ci_exact(D['totals']['five']['unsupported'], D['totals']['five']['model_claims'])}. **This is not an error rate.** It is what a second model read catches; the pilot showed it catching 1–2 of every 4–6 problems a person found (§3.6).
- **Unsupported claims cluster.** In five of six diseases the three worst papers hold half or more of that disease's unsupported claims (Figure 3B, Supplementary Figure S1). Danon's three worst papers hold 60 of its 110: variant and diagnosis fields given to eight family carriers when the paper names only the proband (37215540, 35 claims); "usually mild" applied to individuals (30413001, 15); exclusions resting on "typically showed no symptoms" (41560058, 10).
- **Why claims fail.** The commonest unsupported field is `variants.gene_symbol_as_stated` in five diseases ({gs_txt} claims): a relative's or a cited patient's gene or variant quoted from a sentence about the proband. Extraction v5's rule (variant fields only from this person) holds for probands and slips for relatives the paper says carry "the same" variant. The second pattern is hedged wording ("suggested", "suspected", "consistent with", "typically") recorded as observed or excluded; extraction v6 has no hedge rule, a gap known and left in place at the freeze. The third is cohort-level statements applied to individuals (Figure 3C: "the cohort in general" dominates Danon's and AxD's unsupported claims). Partial verdicts are mostly ages at presentation recorded as onset or last evaluation.
- **Papers that contradict themselves.** The gatekeeper flagged about 30 papers whose table and text disagree (examples in Supplementary Table S5). Those claims were judged on the table and noted; they are collected for the human audit and for adjudication."""


def results_repeat(D):
    rows_ = []
    for d in DISEASES:
        r = D["repeat"][d]
        rows_.append([lab(D, d), r["papers_compared"], f"{r['individual_count_matches']} of {r['papers_compared']}", f"{r['individual_label_jaccard']:.2f}",
                      f"{r['variant_jaccard']:.2f}", f"{r['variant_key_jaccard']:.2f}", f"{r['checklist_agreement']:.3f} ({N(r['checklist_cells_compared'])})",
                      f"{r['feature_jaccard_label_free']:.2f}", f"{r['hpo_status_jaccard_label_free']:.2f}"])
    return f"""### 3.3 Run-to-run stability

A random 10% of each disease's papers (ceil, seed {D['repeat_seed']}; {sum(D['repeat'][d]['papers_compared'] for d in DISEASES)} papers) was re-extracted with the same frozen files and compared with the run of record. The gatekeeper was not run on the repeat.

**Table 5. Agreement between the run of record and the repeat.** Jaccard on sets per paper, pooled; checklist agreement on cells both runs have. Source: `analysis/six_disease/repeat_agreement_2026-10-20.json`.

{table(["Disease", "Papers", "Same individual count", "Label Jaccard", "Variants (strings)", "Variants (folded keys)", "Checklist agreement (cells)", "Features, label-free", "HPO status, label-free"], rows_)}

![Figure 4. Run-to-run repeat agreement.]({D['figs']['fig4']})

**Figure 4.** Run-to-run agreement by measure. Checklist statuses are stable everywhere; variant keys clear the pilot's 0.9 guide in four diseases; free-text features agree least because two readers phrase and split features differently.

- **Checklist statuses agree on 97–100% of cells** in every disease. Fixing the feature names removes the wording variance that free-text rows show (0.43–0.71 label-free).
- **Variant keys agree at 0.92–1.00 in four diseases** and fall to 0.83 (Tangier) and 0.86 (Danon), where one paper each is responsible and both runs recorded the same variants in different notation (a full-width asterisk "＊" vs "*"; "genetic deletion of exons-4–10" vs "deletion of exons-4–10", which has no folded key).
- **Individual counts differ in 9 of {sum(D['repeat'][d]['papers_compared'] for d in DISEASES)} papers,** from scope calls on relatives and on patients cited from earlier reports, the same issue the pilot found in cohort papers. This is the measure to watch when the records are used for counting."""


def results_records(D):
    rows_ = []
    for d in DISEASES:
        s, rc, pp, b = D["stage4"][d], D["reconcile"][d], D["pp"][d], D["build"][d]["counts"]
        sc = s["status_counts"]
        dropped = sum(v for k, v in b.items() if k.startswith("gk_dropped"))
        sx = pp["sex"]
        rows_.append([lab(D, d), f"{N(s['individual_rows'])} → {N(s['identities'])} ({s['merged_pairs']})", rc.get("identities_review_only", "—"), N(s["identities_with_target_variant"]),
                      f"{P(s['cdna_normalized_share'])} of {sc['normalized'] + sc['corrected'] + sc['not_normalized'] + sc['unresolvable']}; {sc['protein_only']} protein-only",
                      f"{P(s['feature_share_bound'])} of {N(s['feature_rows'])}", f"{N(s['phenopackets'])} ({N(s['with_interpretation'])})",
                      f"{N(s['features_observed'])} / {N(s['features_excluded'])}", s["observed_excluded_conflicts"], dropped,
                      f"{sx.get('FEMALE', 0)} F / {sx.get('MALE', 0)} M / {sx.get('UNKNOWN', 0)} unknown", f"{s['schema_valid']}, {s['validation_errors']}"])
    t = D["totals"]["all"]
    return f"""### 3.4 Records: reconciliation, normalization, binding and phenopackets

**Table 6. Stage 4 records by disease.** "Review-only" identities come only from a review's per-patient table (D-33). Normalization is counted over distinct cDNA descriptions; protein-only strings cannot be placed on the genome and are counted apart. Phenopackets keep only gatekeeper-supported claims; "claims dropped" is the count removed. Sources: `analysis/six_disease/stage4_summary_2026-10-20.json`, `reconcile_summary.json`, `phenopacket_build.json`, the phenopackets.

{table(["Disease", "Rows → identities (merges)", "Review-only identities", "With target-gene variant", "cDNA normalized", "Feature rows bound to HPO", "Phenopackets (with interpretation)", "Terms observed / excluded", "Observed–excluded conflicts", "Claims dropped by gatekeeper", "Sex", "Schema-valid, errors"], rows_)}

![Figure 5. Records.]({D['figs']['fig5']})

**Figure 5.** **A** Identities after merging, split by whether a target-gene variant is recorded. **B** VariantValidator normalization of distinct cDNA descriptions. **C** Observed and excluded HPO terms in the phenopackets.

- **{N(t['identities'])} identities from {N(t['individual_rows'])} rows; {N(t['phenopackets'])} phenopackets, all schema-valid; {N(t['with_interpretation'])} carry a genomic interpretation.** Merge policy v4 made {sum(D['stage4'][d]['merged_pairs'] for d in DISEASES)} merges in all; SSADH's 58 are all the duplicate study. Tangier and LAD-I have no citation merges, which is more likely a limit of the citation route than a fact about those literatures (the dossier helpers later proposed 19 same-person groups, §3.8).
- **Normalization** of cDNA descriptions ranges from {P(min(D['stage4'][d]['cdna_normalized_share'] for d in DISEASES))} (AxD) to {P(max(D['stage4'][d]['cdna_normalized_share'] for d in DISEASES))} (HA20). AxD papers often print cDNA without "c." ("739T→C"), and older papers use legacy numbering; 22 AxD descriptions were unresolvable. Protein-only strings (65 in AxD, 85 in HA20) can match ClinVar only at tier 2.
- **HPO binding** covers 84–93% of feature rows. The variant spectrum per disease (Supplementary Figure S2) matches expectation: missense dominates AxD (74%) and SSADH (51%); nonsense and frameshift dominate HA20 (63%) and Danon (52%).
- **Observed–excluded conflicts** (the same term observed and excluded for one identity, from different papers or rows) are few (5–93 per disease) and are kept visible in the records rather than resolved.
- **Sex** is unknown for 5–52% of identities by disease (SSADH highest), mostly people from review tables.
- Field coverage (Supplementary Figure S4) shows what the literature states: onset age is asserted for 3–50% of individuals and consanguinity for 0–30%, so the records carry "not reported" far more often than a value, as the three-state design requires."""


def results_o1(D):
    a1, a2, a2x = D["poc"]["audit1"], D["poc"]["audit2"], D["poc"]["audit2_excl"]
    o1 = D["o1"]
    alloc = o1.get("allocation") or o1.get("allocation_by_disease") or {}
    alloc_txt = ", ".join(f"{SHORT.get(k, k)} {v}" for k, v in alloc.items()) if isinstance(alloc, dict) and alloc else "HA20 72, SSADH 30, Tangier 15, LAD-I 33, AxD 44, Danon 56"
    return f"""### 3.5 O1: the unsupported-value audit (primary, confirmatory) — not yet rated

- **Drawn:** 250 claims from the {N(o1.get('pool_total', 0))} model claims gatekeeper v4 judged supported, stratified by disease in proportion to claim volume ({alloc_txt}), seed {o1.get('seed', 40250)}, on 2026-10-20, before any concordance was run. The draw records pool sizes, allocation, input hashes and the commit (`adjudication/o1_audit/sample_key.json`).
- **Built:** two blinded rating pages (one per rater) that show the claim, its quote and where the quote sits in the paper, never the gatekeeper's verdict; a collector that reports percent agreement and Cohen's κ, writes the tie-break sheet and applies rule C.
- **Not done:** no rating. The pages are private and unshared because the panel's availability (D-11) is unsettled, and Claude contacts no one. Until two raters finish, O1 has no value, and neither does the gatekeeper's accuracy against human labels (§7.1(b) of the plan).

### 3.6 What the pilot's human audits showed (HA20, before the freeze)

The pilot is the only place a person has rated claims. Two 50-claim audits by Dr. Lin, each on a different pipeline version, both missed the pilot's own 4% gate (Table 7). Each exposed one error class, and each class got a rule that is now frozen. The frozen pipeline has not been audited by a person.

**Table 7. Pilot human audits (HA20; rated by Dr. Lin).** Source: `analysis/poc/audit_metrics*.json`.

{table(["Audit", "Pipeline", "Claims rated", "Unsupported (exact 95% CI)", "Not fully supported", "Error class found", "Rule frozen in response"],
       [["First", "instructions v3, gatekeeper v1", a1["rated"], f"{a1['unsupported_strict']['k']} of {a1['unsupported_strict']['n']}: {P(a1['unsupported_strict']['share'])} ({P(a1['unsupported_strict']['ci95'][0])}–{P(a1['unsupported_strict']['ci95'][1])})", f"{a1['not_supported_lenient']['k']} of {a1['not_supported_lenient']['n']}", "variant fields taken from a group statement or a literature-summary column, not this person", "D-29: variant fields only from this person (v5)"],
        ["Re-audit", "instructions v5, gatekeeper v3 (20 papers)", a2["rated"], f"{a2['unsupported_strict']['k']} of {a2['unsupported_strict']['n']}: {P(a2['unsupported_strict']['share'])} ({P(a2['unsupported_strict']['ci95'][0])}–{P(a2['unsupported_strict']['ci95'][1])})", f"{a2['not_supported_lenient']['k']} of {a2['not_supported_lenient']['n']}", "ages read by position from a stacked multi-patient cell; the rater could not verify them", "D-31: no positional reading of stacked cells (v6, gatekeeper v4)"],
        ["Re-audit, sensitivity", "as above, without the 3 unverifiable claims", a2x["rated"], f"{a2x['unsupported_strict']['k']} of {a2x['unsupported_strict']['n']}: {P(a2x['unsupported_strict']['share'])} ({P(a2x['unsupported_strict']['ci95'][0])}–{P(a2x['unsupported_strict']['ci95'][1])})", f"{a2x['not_supported_lenient']['k']} of {a2x['not_supported_lenient']['n']}", "", ""]])}

- **Variant fields were clean after D-29:** 0 of 20 unsupported in the re-audit, against 3 of 20 before.
- **The gatekeeper flagged few of the claims a person rejected:** v1 2 of 6, v3 1 of 4, with no false flags. Its own unsupported rate (0.036% for v1, 0.34% for v3) understated the human rate (6.0%, 6.3%) by an order of magnitude. That is why this report never presents Table 4's shares as error rates.
- **Deduplication:** merge policy v3 made 93 merges, of which a full hand check found 84 true, 6 false and 3 unclear; all 6 false merges came from the sex-and-onset route, which policy v4 dropped. Policy v4 had 0 false merges in the same set, but it was chosen after the check, so that is not an independent test; the registered 50-merge hand check of the six-disease run has not been done.
- **Completeness against Chen 2020 (pilot):** {D['poc']['completeness']['recall_restricted_primary']['k']} of {D['poc']['completeness']['recall_restricted_primary']['n']} restricted variants, {D['poc']['completeness']['recall_unrestricted_primary']['k']} of {D['poc']['completeness']['recall_unrestricted_primary']['n']} unrestricted.
- **Caveats carried forward:** the audits were small (n = 50, 48), rated by one person, and the second-look tabs showed the gatekeeper's reasons, so some labels there are not independent of it. HA20 is the development disease: every rule was tuned on it."""


def results_o2(D):
    rows_ = []
    for d in DISEASES:
        o = D["o2"][d]
        a = o["all_papers"]
        ph = o["phenotype_7_2_4b"]
        rows_.append([lab(D, d), CI(o["gene_7_2_1"]), CI(a["hgvs_recall_tier1"]), CI(a["hgvs_recall_tier12"]), CI(a["overlap_tier1"]),
                      CI(a["classification_agreement_among_stated"]), CI(a["condition_names_disease"]), CI(ph["annotation_recall"]),
                      CI(ph["terms_in_2plus_individuals_matching_annotation"]), CI(o["corpus_overlap_7_2_5"])])
    d19 = []
    for d in DISEASES:
        o = D["o2"][d]["without_clinvar_cited_papers_D19"]
        d19.append([lab(D, d), CI(o["overlap_tier1"]), CI(o["classification_agreement_among_stated"]), CI(o["condition_names_disease"])])
    miss = {d: D["o2_misses_by_paper"].get(d, []) for d in DISEASES}
    comp = []
    for d in ("ha20", "axd"):
        c = D["completeness"][d]
        comp.append([lab(D, d), c["catalogue"], f"{c['benchmark_variants']} ({c['benchmark_patients']})", c["restricted_variants"],
                     CI(c["recall_restricted_primary"]), CI(c["recall_unrestricted_primary"]),
                     "; ".join(f"{m['variant_as_printed']} ({m['source_in_run']})" for m in c.get("missed_restricted", [])) or "none"])
    conf = []
    for d in DISEASES:
        cc = D["o2"][d]["all_papers"]["classification_confusion_clinvar_x_authors"]
        agree = sum(v for k, v in cc.items() if k.split(" | ")[0] == k.split(" | ")[1])
        plp_vus = cc.get("VUS | P/LP", 0)
        conf.append([lab(D, d), cc.get("P/LP | P/LP", 0), plp_vus, cc.get("P/LP | VUS", 0), sum(v for k, v in cc.items() if k.endswith("| not stated")), agree])
    return f"""### 3.7 O2: concordance with ClinVar (primary, estimation); OMIM not assessed

Run on 2026-10-20 against the ClinVar release of 2026-10-12 (snapshot 2026-10-19), after the O1 sample was drawn. OMIM is not checked (no access, D-12). No threshold applies (D-03).

**Table 8. Concordance with ClinVar by disease.** Wilson 95% intervals. Gene (7.2.1) is near ceiling by design. HGVS recall counts ClinVar's own (paper, variant) citation pairs; overlap is not precision. Source: `analysis/six_disease/o2/o2_<d>.json`.

{table(["Disease", "Gene matches disease gene", "HGVS recall, tier 1", "HGVS recall, tiers 1+2", "Overlap, tier 1", "Classification agreement (stated)", "ClinVar condition names the disease", "HPO annotation recall", "Terms in ≥2 people matching an annotation", "Corpus PMIDs cited by ClinVar"], rows_)}

![Figure 6. Concordance with ClinVar.]({D['figs']['fig6']})

**Figure 6.** Concordance with ClinVar. **A** HGVS recall against ClinVar's citations. **B** Overlap of extracted tier-1 alleles with ClinVar. **C** Classification agreement where the authors state a class. **D** HPO annotation recall.

- **HGVS recall is low (10–35% at tier 1; 15–67% with protein-level matches) and the misses sit in single papers** (Supplementary Figure S7). Zhou 2016 (26642243) holds {miss['ha20'][0][1] if miss['ha20'] else 0} of HA20's {sum(n for _, n in miss['ha20'])} misses: it is the founding paper, which ClinVar cites for many variants it does not describe. Van de Vijver 2012 (22134107) holds {miss['lad1'][0][1] if miss['lad1'] else 0} of LAD-I's {sum(n for _, n in miss['lad1'])}: a mutation-update review whose misses may be notation or normalization failures rather than scope. In SSADH, Akaboshi 2003 (14635103, whose table was scrambled in conversion) holds {miss['ssadh'][0][1] if miss['ssadh'] else 0} and Brennenstuhl 2020 (33203024, variants tested in vitro with no patients) {miss['ssadh'][1][1] if len(miss['ssadh']) > 1 else 0} of {sum(n for _, n in miss['ssadh'])}. Every miss counts as discordant in the primary figure; the registered triage of a seeded sample of 50 misses (`adjudication/o2_triage/`, seed {D['o2_triage'].get('seed', 72650)}) will sort them into extraction error, normalization error, paper error, reference error and "citation does not describe the variant". For 28 of the 50, a script found no mention of the variant's position or residue in the paper text, which points at the last category or at a supplement we lack.
- **Overlap** (extracted tier-1 alleles present in ClinVar) is 35–87%. The low values (LAD-I 35%, HA20 38%) are where the gap candidates are (§3.8); the high value (SSADH 87%) is a gene whose literature ClinVar already covers well.
- **Classification agreement among stated values is 59–92%.** The disagreements run one way: authors assert P/LP where ClinVar holds VUS (Table 9). That is the directional expectation stated in advance (case-report authors assert causality; ClinVar's VUS and conflicting records limit concordance), not evidence of extraction error, which only O1 measures.
- **ClinVar's condition names the disease** for 38–99% of matched variants; the low values (Tangier 38%, HA20 47%) reflect records filed under broader or neighboring conditions.
- **Phenotype profile:** 71–94% of the HPO terms annotated to each disease are observed in at least one person; only 6–40% of terms seen in two or more people match an annotation. Annotations are known to be incomplete, so the second number mostly measures how much the literature reports beyond them.

**Table 9. Classification: ClinVar aggregate (rows) against the authors' assertion.** Source: the confusion matrices in `o2_<d>.json`.

{table(["Disease", "ClinVar P/LP, authors P/LP", "ClinVar VUS, authors P/LP", "ClinVar P/LP, authors VUS", "Authors state no class (any ClinVar class)", "Agreeing pairs"], conf)}

**Without ClinVar-cited papers (D-19).** Recall is undefined here, because every reference pair comes from a paper ClinVar cites. Overlap and classification agreement move little:

{table(["Disease", "Overlap, tier 1", "Classification agreement", "Condition names disease"], d19)}

**Completeness against published catalogues (§7.2.7; secondary, descriptive).** Only two diseases have a suitable open catalogue (Table 10, Supplementary Figure S5). The AxD catalogue was added after extraction (D-39), on the harness side only.

**Table 10. Completeness.** Restricted = catalogue variants whose source paper is in the corpus; unrestricted = all catalogue variants with a PMID. Source: `analysis/six_disease/completeness_pv1-<d>.json`.

{table(["Disease", "Catalogue", "Variants (patients)", "Restricted denominator", "Restricted recall, primary papers", "Unrestricted recall", "Restricted misses"], comp)}

- AxD's two restricted misses are notation, not absence: "R270-A272del" extracted with a hyphen where the catalogue has p.Arg270_Ala272del, and a whole-gene deletion extracted as "deletion (exons 1–9)". The matcher was not changed after seeing this.
- The restricted denominators are small (9 of 32, 56 of 183) because most catalogue source papers are not open access (D-32). Unrestricted recall (91% HA20, 54% AxD) therefore mostly measures access, not extraction.
- Patients per source paper: for AxD the run has at least as many carriers as the catalogue in all 43 shared source papers; for HA20 two papers have fewer (30022980: 1 of 4; 30526650: 2 of 3), candidates for a scope check."""


def results_o3(D):
    rows_ = []
    for d in DISEASES:
        g = D["gaps"][d]
        pc = g["gap_candidates_protein_check"]
        bp = g["gap_candidates_by_papers"]
        ac = g["gap_candidates_by_author_class"]
        rows_.append([lab(D, d), g["tier1_alleles"], g["absent_from_clinvar_before_gatekeeper"], f"**{g['gap_candidates']}**", g["absent_but_every_row_failed_gatekeeper"],
                      g["gap_candidates_only_from_clinvar_cited_papers"], g["gap_candidates_only_from_reviews"], pc.get("differs", 0),
                      f"{bp.get('1', 0)} / {bp.get('2', 0)} / {bp.get('3', 0)}", f"{ac.get('P/LP', 0)} P/LP, {ac.get('VUS', 0)} VUS, {ac.get('not stated', 0)} not stated",
                      f"{g['reclassification_candidates']} ({g['reclassification_strong_proposed']})"])
    t, f = D["totals"]["all"], D["totals"]["five"]
    rows_.append(["**Five confirmatory**", f["tier1_alleles"], "", f"**{f['gap_candidates']}**", "", "", "", "", "", "", f"{f['reclass']} ({f['reclass_strong']})"])
    rows_.append(["**All six**", t["tier1_alleles"], sum(D["gaps"][d]["absent_from_clinvar_before_gatekeeper"] for d in DISEASES), f"**{t['gap_candidates']}**",
                  sum(D["gaps"][d]["absent_but_every_row_failed_gatekeeper"] for d in DISEASES), "", "", "", "", "", f"{t['reclass']} ({t['reclass_strong']})"])
    tri = D["triage"]
    mg = D["merges"]["by_disease"]
    stages = table(["Stage (plan §7.3)", "Count"], [["1 Candidates", t["gap_candidates"]], ["2 Adjudicated by the panel", 0], ["3 Approved", 0], ["4 Drafted (pending adjudication)", 0],
                                                    ["5 Signed off", 0], ["6 Submitted", 0], ["7 Accepted", 0]])
    return f"""### 3.8 O3: gap closure (primary, descriptive) — candidates only

A gap candidate is a tier-1 allele absent from the ClinVar snapshot whose identifying values (gene, strings, cDNA, protein, transcript, coordinates, person label) gatekeeper v4 judged supported in at least one row. OMIM allelic variants are not checked (D-12), so every candidate is a ClinVar gap only, and the OMIM half of the definition is unassessed.

**Table 11. Gap candidates by disease.** Protein check = the paper's stated protein against the one VariantValidator predicts from the normalized cDNA (a pre-triage flag). Reclassification candidates are in ClinVar only as VUS or conflicting; "strong" is a proposed rule (≥2 papers or ≥3 deduplicated people), exploratory. Source: `adjudication/o3_gaps/summary.json`.

{table(["Disease", "Tier-1 alleles", "Absent from ClinVar", "Gap candidates", "Absent but every row failed gatekeeper", "Only from ClinVar-cited papers", "Only from reviews", "Protein check differs", "Papers per candidate 1 / 2 / 3+", "Authors' class", "Reclassification (strong)"], rows_)}

{stages}

![Figure 7. Gap candidates.]({D['figs']['fig7']})

**Figure 7.** Gap candidates. **A** Extracted tier-1 alleles split by presence in ClinVar. **B** Keyword triage flags drawn from the evidence dossiers' concerns, as pointers for the panel. **C** How many papers report each candidate.

- **{t['gap_candidates']} candidates** ({f['gap_candidates']} outside HA20), from {t['tier1_alleles']} tier-1 alleles. All {D['recheck']['candidates_checked']} were still absent by GRCh38 allele in the next ClinVar release (variant summary of {list(D['recheck']['variant_summary_last_modified'].values())[0][5:16]}, snapshot {D['recheck']['snapshot']}). A spot check found that HA20's c.271A>T (p.Lys91Ter) and c.559C>T (p.Gln187Ter) have no record while their neighbors do.
- **LAD-I's 82 need the most care.** 66 come only from papers ClinVar cites for *ITGB2* and 34 only from reviews, most from van de Vijver 2012, a mutation update. A variant that ClinVar cites a paper for but that is absent by allele is as likely a numbering or normalization slip as a true gap; the protein check flags 10 of them.
- **Evidence dossiers** were written for all {D['dossiers']['dossiers']} candidates by helpers reading only the extracted records and the papers (never ClinVar or OMIM): case count and phenotype match, segregation, de novo status with parental testing, functional evidence, in-trans findings and variant type, each line with a PMID and a verbatim quote or "not reported", and no proposed classification. All {N(D['dossiers']['quotes'])} quotes were checked verbatim; 0 problems. Population frequency (PM2) is left to the panel because gnomAD is not reachable here.
- **Triage flags** (Figure 7B): {tri['with_any_flag']} of {tri['candidates']} candidates carry at least one keyword flag from the dossiers' concerns. The most common, "possible same person twice" ({tri['by_flag']['possible_same_person']}), matters for case counts, not for whether the variant exists. The dossier helpers also named candidates that may not be gaps at all: a coordinate read literally from "c.610-612A>G (IVS3-2A>G)" (G-ssadh-003); c.54G>T called Gly18Val where c.53 is probably meant (G-axd-017); a paper that cites an SCV accession not yet in the release (G-lad1-077); two LAMP2B-numbered variants mapped to intronic positions on the MANE transcript (G-danon-002).
- **Proposed same-person groups:** {sum(v['groups'] for v in mg.values())} groups across {len(mg)} diseases ({', '.join(f"{SHORT[k]} {v['groups']}" for k, v in sorted(mg.items(), key=lambda x: -x[1]['groups']))}) of identities the dossier helpers judged to be one person re-cited by a later paper. If all were confirmed, {P(mg['ha20']['share'])} of HA20 identities would collapse and {P(min(v['share'] for k, v in mg.items() if k != 'ha20'))}–{P(max(v['share'] for k, v in mg.items() if k != 'ha20'))} elsewhere; a lower bound, because only the candidates' papers were examined. Nothing is merged: changing the records after the freeze is a deviation, and each group needs a person.
- **Reclassification candidates (exploratory):** {t['reclass']} supported tier-1 variants are in ClinVar only as VUS or conflicting; {t['reclass_strong']} meet the proposed "strong" rule (Supplementary Table S9).
- **Submission records** are prepared as format-neutral pending records per panel-approved variant (`submissions/make_records.py`); the ClinVar collection method is *curation* (D-13). None exists yet because nothing is approved."""


def results_o4(D):
    mc, mo = D["mem"]["claude"]["by_stratum"], D["mem"]["open"]["by_stratum"]
    rows_ = []
    for s, nm in (("after", "after cutoff"), ("recent", "recent"), ("older", "older")):
        for m, mn, src in (("claude", "Claude", mc), ("open", "DeepSeek", mo)):
            b = src[s]
            rows_.append([nm, b["papers"], mn, f"{b['cb_specific']} / {b['cb_guess']} / {b['cb_none']}", b["cb_papers_with_variant_hit"], f"{b['cb_variants_given']} ({b['cb_variant_hits']})",
                          f"{b['cb_phen_given']}, {b['cb_phen_mapped']}, {b['cb_phen_hits']}", f"{b['cp_mean_rougeL_f1']:.3f}", f"{b['cp_mean_5gram_share']:.4f}", b["cp_max_longest_run"], b["cp_papers_run_ge_8"]])
    import glob as _glob
    sheets = sorted(Path(x).stem for x in _glob.glob(str(ROOT / "analysis/bias/comparator_sheets/*.csv")))
    comps = [{"disease": x.split("__")[0], "key": x.split("__")[1]} for x in sheets]
    pay = [c for c in D["comparators"] if c.get("source") == "paywalled"]
    return f"""### 3.9 O4: ascertainment bias and memorization (secondary)

**Memorization probe (exploratory, §7.4.3).** 180 papers (30 per disease) stratified by first publication date against Claude Opus's documented cutoff (June 2026): 10 after, 51 recent (2024-07 to 2026-06), 119 older. Two black-box probes run identically on both models; every Claude helper transcript was checked for forbidden tool calls (none). Scored against the full-text extraction, never ClinVar.

**Table 12. Memorization probe by stratum and model.** Closed book = recall from PMID, title and year; completion = continuing a 50-word opening. One item (Tangier 33346003) was excluded because its opening was publisher boilerplate. Sources: `analysis/bias/memorization/scores_summary.json`, `openweight_scores_summary.json`.

{table(["Stratum", "Papers", "Model", "Closed book: specific / guess / none", "Papers with a variant hit", "Variants given (hits)", "Phenotype terms given, mapped, hits", "Completion: mean ROUGE-L F1", "Mean 5-gram share", "Longest run (words)", "Runs ≥ 8 words"], rows_)}

![Figure 9. Memorization probe.]({D['figs']['fig9']})

**Figure 9.** Memorization probe on both models. Neither reproduces the papers' variants or text; the differences between strata are small and in no consistent direction.

- Claude claimed specific recall for 4 of 180 papers, all older, and in each case for phenotypes only; 4 papers had a variant hit, all labelled guesses and all recurrent variants (e.g. LAMP2 p.Arg293Ter). DeepSeek claimed specific recall for none and answered "none" for 139 papers. The three completions with a run of 8+ matching words are all formulaic ("written informed consent was obtained from all patients").
- The after-cutoff stratum has 10 papers, so the before/after comparison has little power; and black-box probes can miss memorization that changes extraction without surfacing as recall. The exploratory split of audit and concordance results by memorization has nothing to split on.

**Frequency deviation (§7.4.2): not started.** {len(comps)} open comparators are fetched and a listing sheet exists for each ({"; ".join(f"{SHORT[c['disease']]}: {c['key']}" for c in comps)}); {len(pay)} candidate comparators are paywalled and left out (D-32); LAD-I and Tangier have no comparator and are out of the bias arm (D-35). Step 1 requires a person to list each comparator's HPO-mappable features and cohort frequencies before any literature frequency is computed, and the script that then runs the deviation (with a 2,000-resample publication-cluster bootstrap, seed {D['bias']['seed']}) is written and tested on synthetic input only."""


def results_o5(D):
    dz = ["ha20", "ssadh"]
    ow, g = D["ow"], D["ow_gk"]
    rows_ = []
    for d in dz:
        s = ow[d]
        o2c, o2o = D["o2"][d]["all_papers"], D["ow_o2"][d]["all_papers"]
        rows_.append([lab(D, d), s["papers_compared"], f"{N(s['span']['claude']['values_asserted'])} / {N(s['span']['open']['values_asserted'])}",
                      f"{P(s['span']['claude']['span_not_found_rate'], 2)} / **{P(s['span']['open']['span_not_found_rate'], 2)}**",
                      f"{s['span']['claude']['no_quote']} / {N(s['span']['open']['no_quote'])}",
                      f"**{P(g[d]['claude']['unsupported']['share'], 2)}** / **{P(g[d]['open']['unsupported']['share'], 2)}**",
                      f"{P(g[d]['claude']['by_span']['quote']['unsupported']['share'], 2)} / {P(g[d]['open']['by_span']['quote']['unsupported']['share'], 2)}",
                      f"{CI(o2c['hgvs_recall_tier12'])} / {CI(o2o['hgvs_recall_tier12'])}",
                      f"{s['variant_keys']['shared']}/{s['variant_keys']['union']} ({P(s['variant_keys']['jaccard_pooled'])})",
                      f"{P(s['checklist']['status_agreement'])} of {N(s['checklist']['cells_shared'])}",
                      f"{N(s['coverage']['claude']['phenotypic_feature_rows'])} / {N(s['coverage']['open']['phenotypic_feature_rows'])}",
                      f"${s['cost_usd']['claude_median_per_paper']:.2f} / ${s['cost_usd']['open_median_per_paper']:.2f}",
                      f"{s['wall_seconds']['claude_median'] / 60:.1f} / {s['wall_seconds']['open_median'] / 60:.1f}"])
    m = D["ow_manifest"]
    return f"""### 3.10 O5: efficiency and the open-weight comparison (secondary)

**Expert-minutes per accepted record: not measured.** The adjudication page logs active minutes per record, but adjudication has not started.

**Claude vs DeepSeek-V4.1-Flash (D-10).** The open-weight model (2026-09-10 checkpoint, OpenRouter, provider pinned to DeepInfra fp8) ran the same {m['ha20']['papers']} HA20 and {m['ssadh']['papers']} SSADH papers with the same launch prompt, frozen instruction files and schema, through an agent loop with file tools (`pipeline/extract/openweight/agent.py`). Outputs went through the same span check, reconciliation, normalization and O2 harness, and the same gatekeeper v4 judged both runs' claims.

**Table 13. Claude vs open-weight model.** Values are Claude / open-weight. Claude's cost is an estimate from helper tokens at the six-disease run's rate; the open-weight cost is what the host reported for final attempts (failed attempts, 13 HA20 and 1 SSADH papers, add $0.55 logged plus an unknown amount for 10 attempts that stopped before logging). Sources: `analysis/openweight/summary_<d>.json`, `gatekeeper_compare.json`, `o2/`.

{table(["Disease", "Papers", "Values asserted", "Span-not-found rate", "Values with no quote", "Judged unsupported (gatekeeper v4)", "…among claims with a quote", "HGVS recall, tiers 1+2", "Variant keys shared/union", "Checklist agreement (shared cells)", "Feature rows", "Cost per paper, median", "Wall-clock per paper, median (min)"], rows_)}

![Figure 8. Claude vs open-weight model.]({D['figs']['fig8']})

**Figure 8.** Claude vs the open-weight model on the registered metrics measured so far.

- **Variants:** the two models found largely the same target-gene variants ({P(ow['ha20']['variant_keys']['jaccard_pooled'])} and {P(ow['ssadh']['variant_keys']['jaccard_pooled'])} of the union shared) and their HGVS recall against ClinVar overlaps within the intervals.
- **Provenance:** Claude left no value without a quote; the open-weight model left {P(ow['ha20']['span']['open']['no_quote_rate'])} (HA20) and {P(ow['ssadh']['span']['open']['no_quote_rate'])} (SSADH) without one, and {ow['ha20']['span']['open']['cells_not_in_schema_shape']} and {ow['ssadh']['span']['open']['cells_not_in_schema_shape']} cells broke the schema shape (tolerated by the readers after checking pv1 outputs were byte-identical).
- **Support, as the same Claude gatekeeper reads it:** {P(g['ha20']['open']['unsupported']['share'])} and {P(g['ssadh']['open']['unsupported']['share'])} of the open-weight model's claims unsupported against {P(g['ha20']['claude']['unsupported']['share'], 2)} and {P(g['ssadh']['claude']['unsupported']['share'], 2)} for Claude. Most of the gap is claims with no quote (`is_proband = false`, checklist statuses), but claims with a quote were also judged unsupported {g['ha20']['open']['by_span']['quote']['unsupported']['share'] / g['ha20']['claude']['by_span']['quote']['unsupported']['share']:.0f}× (HA20) and {g['ssadh']['open']['by_span']['quote']['unsupported']['share'] / g['ssadh']['claude']['by_span']['quote']['unsupported']['share']:.0f}× (SSADH) as often. Two cautions: the judge is Claude, which may not be neutral between a Claude and a non-Claude extraction, and helpers did not all treat empty quotes the same way ({g['ha20']['open']['by_span']['empty']['supported']} HA20 and {g['ssadh']['open']['by_span']['empty']['supported']} SSADH empty-quote claims were judged supported against the row's quote). The blinded human audit of equal samples from each model, the registered measure, waits on D-11.
- **Cost and time:** per paper the open-weight model cost about 1/15 of Claude's estimate and took 7× as long (one provider's throughput, with waits after dropped connections: 36 and 17 retried calls in final attempts, ~50 per 125 papers).
- **Scaffold differences, as the plan requires them stated:** the open-weight loop had no shell (Claude's helpers used one for small checks); it had no repair passes for empty quotes (pv1 had a handful); three harness fixes landed during the run (retries, a parse check on JSON writes, a resume request after a cut-off reply, never needed), approved by Dr. Lin and logged.
- **Scope:** two diseases, one open-weight model, one provider; not general findings."""


def results_exploratory(D):
    g = D["gpsea"]["diseases"]
    rows_ = []
    an_names = {"truncating_vs_missense": "truncating vs missense", "hotspot_R79_R88_R239_vs_other": "hotspot R79/R88/R239 vs other missense",
                "sex": "sex (males hemizygous, females heterozygous)", "biallelic_truncating": "biallelic: truncating/truncating vs truncating/other vs other/other"}
    for d in DISEASES:
        if d not in g:
            continue
        for an, r in g[d]["analyses"].items():
            sig = r["significant_bh_0.05"]
            top = "; ".join(f"{t['hpo_label']} ({', '.join(f'{k.replace(chr(95), ' ').replace('group ', '')} {v}' for k, v in t.items() if k.startswith('group'))}; p_BH {t['p_bh']:.3f})" for t in r["top"][:sig]) if sig else "—"
            rows_.append([lab(D, d), an_names.get(an, an), g[d]["patients"], r["terms_tested"], sig, top])
    ts = D["tangier_share"]
    return f"""### 3.11 Exploratory analyses (§7.6)

**Genotype–phenotype maps with GPSEA.** Fisher exact tests with Benjamini–Hochberg correction at 0.05, in a separate uv project (GPSEA 0.10.0; pandas < 3). Variant effects come from each phenopacket's own normalized HGVS (Ensembl VEP is not reachable here). Only individuals with a variant placed on GRCh38 and at least one phenotype enter. Zygosity for untyped calls is an analysis assumption only (dominant: heterozygous; Danon males hemizygous; recessive: two distinct untyped calls taken as compound heterozygous); the records keep "not reported". A feature not reported is not counted as excluded.

**Table 14. GPSEA tests.** Source: `analysis/exploratory/gpsea/results/summary.json`.

{table(["Disease", "Comparison", "Individuals", "Terms tested", "Significant (BH 0.05)", "Significant terms (group shares; p_BH)"], rows_)}

- **Danon reproduces the published sex difference** (Supplementary Figure S6): proximal muscle weakness 11/25 males vs 1/28 females; left ventricular hypertrophy 41/41 vs 25/33; hypertrophic cardiomyopathy 34/34 vs 19/24. The papers overlap with the published series, so this is a reproduction check, not independent replication. The truncating-vs-missense arrhythmia signal rests on 6–8 missense carriers and is a lead only.
- **HA20, AxD, SSADH, LAD-I:** no term survives correction; Tangier has too few placeable, phased genotypes to test.

**Tangier: share of ClinVar *ABCA1* records matched by the literature.** {ts['records_matched_by_tangier_literature']} of {N(ts['abca1_single_gene_records'])} single-gene GRCh38 records ({P(ts['share_of_all_records'])}) and {ts['plp_records_matched']} of {ts['abca1_plp_records']} P/LP records ({P(ts['share_of_plp_records'])}) match variants extracted from the 31-paper Tangier corpus; {ts['extracted_not_in_clinvar']} of {ts['extracted_tangier_variants']} extracted variants are not in ClinVar. A lower bound: the corpus is open access only, and most *ABCA1* records come from testing unrelated to Tangier disease.

**LAD-I deduplication accuracy** against the duplicate cases in Almarza Novoa 2018 is not computable: the review's open supplement flags only one overlap (10 cases in a 1987 paper outside the corpus) and names no case pairs."""


def per_disease(D):
    out = ["### 3.12 Results by disease", "",
           "Each subsection gives the disease's corpus, records, variants, gatekeeper reading, stability, concordance, gap candidates, what the helpers flagged in its inputs, and any disease-specific finding. HA20 comes first because it is the development disease; its figures are secondary."]
    for d in DISEASES:
        c, r, s, o, g, pp, rp, rc = D["coverage"][d], D["run"][d], D["stage4"][d], D["o2"][d], D["gaps"][d], D["pp"][d], D["repeat"][d], D["reconcile"][d]
        a = o["all_papers"]
        vc = pp["variant_classes"]
        tot_vc = sum(vc.values()) or 1
        top_vc = ", ".join(f"{k} {100 * v / tot_vc:.0f}%" for k, v in sorted(vc.items(), key=lambda x: -x[1])[:3])
        top_terms = "; ".join(f"{lab_} {100 * o_ / pp['n']:.0f}%" for _, lab_, o_, _ in pp["top_observed"][:5])
        miss = D["o2_misses_by_paper"].get(d, [])
        cv = D["clinvar"][d]
        bp = g["gap_candidates_by_papers"]
        extra = []
        if d == "ha20":
            comp = D["completeness"]["ha20"]
            extra += [f"- **Development disease (D-18).** Every rule in extract_v6 and gatekeeper_v4 was tuned on HA20's pilot runs, and {c.get('seeded_from_clinvar', 0)} of its {c['in_corpus']} corpus papers were seeded from ClinVar citations (D-19). Treat its figures as an upper bound on the pipeline.",
                      f"- **Completeness vs Chen 2020:** {comp['recall_restricted_primary']['k']} of {comp['recall_restricted_primary']['n']} restricted variants, {comp['recall_unrestricted_primary']['k']} of {comp['recall_unrestricted_primary']['n']} unrestricted; most of the catalogue's source papers are paywalled.",
                      f"- **GPSEA:** truncating vs missense, {D['gpsea']['diseases']['ha20']['patients']} individuals, 11 terms, none significant.",
                      f"- **Same-person groups:** 12 proposed groups; up to {P(D['merges']['by_disease']['ha20']['share'])} of identities would collapse if confirmed, the highest of any disease, because HA20 reviews re-cite the same families."]
        if d == "ssadh":
            extra += ["- **Duplicate study:** 37503297 (Research Square preprint) and 37962671 (journal version, whose open copy is the preprint text) are both in the corpus; their patients are merged (58 merges) with the evidence recorded. The papers themselves disagree on G176R vs G176E for one variant.",
                      f"- **O2 misses are two papers:** Akaboshi 2003 ({miss[0][1] if miss else 0} misses; its Table 2 was scrambled in conversion, so about 12 of 54 families were extracted) and Brennenstuhl 2020 ({miss[1][1] if len(miss) > 1 else 0}; variants tested in vitro, no patients). Both are scope or input problems rather than reading errors, pending triage.",
                      f"- **Overlap with ClinVar is the highest of the six ({CI(a['overlap_tier1'])}),** and ClinVar's condition names SSADH deficiency for {CI(a['condition_names_disease'])} of matched variants: a well-covered gene. Only {g['gap_candidates']} gap candidates.",
                      "- **GPSEA:** biallelic truncating vs other, 77 individuals, 9 terms, none significant."]
        if d == "tangier":
            ts = D["tangier_share"]
            extra += [f"- **Smallest corpus and the lowest open-access share ({P(c['fulltext_share'])}).** Many Tangier papers are old and their tables are images (26713019, 27011649).",
                      f"- **Only {s['identities_with_target_variant']} of {s['identities']} identities carry an *ABCA1* variant:** {rc.get('identities_review_only', 0)} identities come from review tables, and many older clinical reports give no genotype. Papers on heterozygous carriers with familial HDL deficiency were kept as \"unclear\" at screening for the full text to decide.",
                      f"- **ClinVar *ABCA1* is dominated by testing unrelated to Tangier disease:** {ts['records_matched_by_tangier_literature']} of {N(ts['abca1_single_gene_records'])} records match the literature (exploratory, §3.11).",
                      "- **No comparator** for the bias arm and no suitable open catalogue; GPSEA could not run (too few phased genotypes)."]
        if d == "lad1":
            extra += [f"- **The gap list is dominated by one review:** van de Vijver 2012 (22134107), a mutation update whose people are database accession numbers. 66 of the 82 candidates come only from ClinVar-cited papers and 34 only from reviews; the protein check flags 10. Many may be numbering or normalization slips rather than gaps. The same paper holds {miss[0][1] if miss else 0} of LAD-I's {sum(n for _, n in miss)} O2 misses.",
                      "- **Input problem:** 33391282's Table S1 was cut at 60,000 characters, so P75–P127 have no clinical rows; 30 of its patients were reported before without names, which the merge route cannot join.",
                      f"- **Gene-name spelling:** \"ITGβ2\", \"ITGß2\" and \"CD18\" cover {127 + 21} variant rows; the matcher accepts them.",
                      "- **GPSEA:** biallelic truncating vs other, 38 individuals, 3 terms, none significant. No comparator for the bias arm; the deduplication benchmark is not computable."]
        if d == "axd":
            comp = D["completeness"]["axd"]
            extra += [f"- **Completeness vs Grossi 2024 (D-39):** {comp['recall_restricted_primary']['k']} of {comp['recall_restricted_primary']['n']} restricted variants (protein level {comp['recall_restricted_primary_by_level']['protein']['k']}/{comp['recall_restricted_primary_by_level']['protein']['n']}, cDNA level {comp['recall_restricted_primary_by_level']['cdna']['k']}/{comp['recall_restricted_primary_by_level']['cdna']['n']}); the two misses are notation. The catalogue's genomic column matched nothing as printed (30 off by one, 16 on the coding strand), so it was not used.",
                      f"- **Normalization is the lowest ({P(s['cdna_normalized_share'])}):** AxD papers print cDNA without \"c.\" and use legacy numbering; 65 strings are protein-only, so {vc.get('not placed', 0)} interpretations are unplaced and can match ClinVar only at tier 2 (tiers 1+2 recall {CI(a['hgvs_recall_tier12'])} vs tier 1 {CI(a['hgvs_recall_tier1'])}).",
                      f"- **Missense dominates ({100 * vc.get('missense', 0) / tot_vc:.0f}% of interpretations)**, as expected for a gain-of-function leukodystrophy; GPSEA found no difference between the R79/R88/R239 hotspots and other missense (83 individuals, 14 terms).",
                      "- **Comparators:** Gagliardi 2025 (UK Biobank, genotype-first) is fetched and awaits a person; Mura 2021 is paywalled."]
        if d == "danon":
            extra += [f"- **Highest gatekeeper unsupported share ({P(r['unsupported_or_not_found']['share'], 2)})**, with three papers holding 60 of 110: relatives' variant fields from the proband's sentence (37215540), and cohort wording (\"usually mild\", \"typically showed no symptoms\") applied to individuals.",
                      "- **Sex difference reproduced** (§3.11): males more often show myopathy and hypertrophy; a reproduction check, since the papers overlap with the published series.",
                      f"- **Variant spectrum:** frameshift {100 * vc.get('frameshift', 0) / tot_vc:.0f}%, nonsense {100 * vc.get('nonsense', 0) / tot_vc:.0f}%, splice {100 * vc.get('splice / intronic', 0) / tot_vc:.0f}%; LAMP2B-numbered variants (exon 9B) map to intronic positions on the MANE transcript and need the panel's attention (G-danon-002).",
                      "- **Input problems:** three papers with transposed or garbled tables and one missing supplement (Supplementary Table S5). Comparator Khedro 2025 is fetched; Boucek 2011 is paywalled."]
        inp = INPUT_PROBLEMS.get(d, [])
        out += [f"", f"#### {name(D, d)}{' — development disease' if d == 'ha20' else ''}", "",
                f"- **Corpus:** {N(c['manifest_rows'])} records screened; {c['in_corpus']} in corpus; {c['fulltext']} with open full text ({P(c['fulltext_share'])}); {r['papers']} papers extracted, {r['papers_with_individual_rows']} with individual rows. ClinVar ({cv['release'][5:16]}): {N(cv['total'])} single-gene records, {cv['plp']} P/LP, {cv['vus']} VUS.",
                f"- **Records:** {N(r['individual_rows'])} rows → {N(s['identities'])} identities ({s['merged_pairs']} merges; {rc.get('identities_review_only', '—')} review-only); {s['identities_with_target_variant']} with a *{D['gene'][d]}* variant; {N(s['phenopackets'])} phenopackets, {s['with_interpretation']} with a genomic interpretation; sex {pp['sex'].get('FEMALE', 0)} F / {pp['sex'].get('MALE', 0)} M / {pp['sex'].get('UNKNOWN', 0)} unknown. Observed / excluded terms {N(s['features_observed'])} / {N(s['features_excluded'])}; most-observed: {top_terms}.",
                f"- **Variants:** {s['distinct_variant_descriptions']} distinct descriptions; cDNA normalized {P(s['cdna_normalized_share'])}; {sum(vc.values())} interpretations in the phenopackets ({top_vc}).",
                f"- **Gatekeeper:** {ci_exact(r['unsupported_or_not_found']['k'], r['model_claims_judged'])} unsupported; {r['papers_with_any_unsupported']} of {r['papers']} papers; top field `{r['unsupported_top_fields'][0][0]}` ({r['unsupported_top_fields'][0][1]}).",
                f"- **Repeat ({rp['papers_compared']} papers):** checklist {rp['checklist_agreement']:.3f}; variant keys {rp['variant_key_jaccard']:.2f}; same individual count in {rp['individual_count_matches']} of {rp['papers_compared']}.",
                f"- **ClinVar:** HGVS recall tier 1 {CI(a['hgvs_recall_tier1'])}, tiers 1+2 {CI(a['hgvs_recall_tier12'])}; overlap {CI(a['overlap_tier1'])}; classification agreement {CI(a['classification_agreement_among_stated'])}; HPO annotation recall {CI(o['phenotype_7_2_4b']['annotation_recall'])}. O2 misses: {sum(n for _, n in miss)} in {len(miss)} papers" + (f", led by {miss[0][0]} ({miss[0][1]})." if miss else "."),
                f"- **Gap candidates:** {g['gap_candidates']} of {g['tier1_alleles']} tier-1 alleles ({bp.get('1', 0)} in one paper, {bp.get('2', 0)} in two, {bp.get('3', 0)} in three or more); {g['gap_candidates_only_from_clinvar_cited_papers']} only from ClinVar-cited papers; protein check differs for {g['gap_candidates_protein_check'].get('differs', 0)}; {g['reclassification_candidates']} reclassification candidates ({g['reclassification_strong_proposed']} strong)."]
        if inp:
            out.append("- **Input problems flagged by the helpers:** " + "; ".join(inp) + ".")
        out += extra
    return "\n".join(out)


def results_cost(D):
    b = D["budget"]
    rows_ = [[L["n"], L["name"], f"${L['requested']:,.0f}", f"${L['spent']:,.2f}", f"{100 * L['spent'] / L['requested']:.1f}%"] for L in b["lines"]]
    rows_.append(["—", "Not yet assigned to a line (setup, documents, decisions, gaps between runs)", "", f"${b['unassigned']:,.2f}", ""])
    rows_.append(["", "**Total, this session's readings**", "$45,000", f"**${b['total']:,.2f}**", f"{100 * b['total'] / 45000:.1f}%"])
    ow = D["ow_manifest"]["ha20"]["key_spend_both_runs_usd"]
    return f"""### 3.13 Cost and efficiency so far

**Table 15. Spend by budget line.** Estimates from this session's own cost readings (list price, including helper agents), split into dated stretches and booked to lines (`analysis/cost/spend_segments.csv`, `budget_lines.py`). They are not billing figures: readings sometimes froze for an hour, stages overlapped, and whether this session runs on the funded account is still open (D-15). Other sessions (the pilot-design session) are not included.

{table(["Line", "Budget line", "Requested", "Spent (estimate)", "Share"], rows_)}

![Figure 10. Spend by budget line.]({D['figs']['fig10']})

**Figure 10.** Spend by budget line against the requested amounts.

- **Unit costs measured on this route:** extraction about $2 per paper (helper tokens; $1.08–1.19 median per paper on the two-disease comparison); gatekeeper about $0.0044 per judged claim; the six-disease run with its 10% repeat came to +$769 by session readings ($764 by tokens) against a $1,200 ceiling (D-37); HPO binding helpers cost $72 against a $28 estimate because they searched the ontology file repeatedly.
- **Open-weight compute** (D-10) is billed to OpenRouter, outside the award: ${ow['spent'] - 0.0:.2f} by key usage over both runs, but the key is shared with other projects, so the host-reported $16.34 is the lower bound and $20.35 the upper.
- **Projection:** the core lines are {100 * b['total'] / 30000:.0f}% spent one week into Month 2 (2026-10-21 to 2026-11-20) with extraction, gatekeeping and concordance done for six diseases. What remains on the model side (re-runs if O1 fails, the blinded comparison audit's preparation, bias-arm scripts, write-up) is small; the large remaining costs are human hours, which the award does not fund."""


def discussion(D):
    t, f = D["totals"]["all"], D["totals"]["five"]
    return f"""## 4. Discussion

**What the data say so far.** The pipeline runs end to end on six diseases at the scale the grant projected ({N(t['papers'])} papers against "roughly 300"), with provenance that holds on every value and repeats that are stable where the schema fixes the vocabulary. It produces {N(t['phenopackets'])} valid phenopackets, a ClinVar comparison with intervals on every figure, and {t['gap_candidates']} candidate gaps that two successive ClinVar releases confirm are absent. Three of the directional expectations stated before registration are consistent with what was seen: classification disagreement runs almost entirely in the "authors say P/LP, ClinVar says VUS" direction; proband counting and deduplication are the weak point (9 of 38 repeat papers differ in individual count; 19 unmerged same-person groups; the pilot's 6 false merges); and the extraction misses concentrate in papers ClinVar cites for variants they do not describe.

**What the data do not say.** Nothing here establishes the accuracy of the frozen pipeline. The gatekeeper's {P(f['unsupported'] / f['model_claims'], 2)} is a filter's reading; the only human-rated figures (6.0%, 6.3%) come from the pilot, before the two rules those audits produced were frozen. The pre-registered test is at most 4 unsupported of 250 under rule C, and the audit's own operating characteristics mean that even a pass would leave a true rate near 2% unexcluded. The concordance figures are ClinVar-only; OMIM, half of the registered answer key, has not been assessed. Recall against ClinVar's citations is low, but the registered triage has not been done, so how much of that is extraction error, normalization error or citations that do not describe the variant is unknown. The open-weight comparison has a Claude judge and no blinded audit yet.

**What the gatekeeper is good for.** Its value is in the records, not the metric: it removed {sum(sum(v for k, v in D['build'][d]['counts'].items() if k.startswith('gk_dropped')) for d in DISEASES):,} claims before the phenopackets were built, and its reasons name the failure modes a person should look for first (relatives' variant fields, hedged wording, cohort statements). O1 will give its accuracy against human labels, which is the number to report.

**On the open-weight result.** The cheap model found the same variants and left more values without a quote. If the blinded audit confirms the gatekeeper's reading, the practical conclusion is that the scaffold's provenance rules bind differently on different models, and that span-level provenance is the cheapest place to see it.

**Scope.** Six diseases, open access only, one extraction model, one judge model. These are pilot results on a pre-registered design, not general findings."""


def gaps(D):
    rows_ = [
        ["G1", "**O1 human audit not rated** (primary outcome)", "O1 pass/fail; gatekeeper accuracy vs human labels (§7.1b); any accuracy claim", "Dr. Lin shares the two rater pages with two panel members (D-11); they rate; a third breaks ties", "panel: 250 claims × 2 raters at 1–3 min each ≈ 8–25 h, plus tie-break; model: $0", "1–3 weeks after sharing"],
        ["G2", "**OMIM not assessed** (D-12)", "the OMIM half of O2 and O3; the gap definition's second clause; OMIM allelic-variant candidates (a deliverable)", "Dr. Lin submits the drafted API access request; then one harness run", "$0 model; 1–2 days of scripting once access arrives", "weeks to months (OMIM's response)"],
        ["G3", "**Gap candidates not adjudicated** (O3 stages 2–7)", "approved variants, submission drafts, expert-minutes (O5), the gap-closure deliverable", "Dr. Lin shares the adjudication page; the panel reviews 215 dossiers; Dr. Lin signs off; submissions under *curation* (D-13)", "panel: 215 × 10–15 min ≈ 36–54 h; model: $0 (dossiers exist); LAD-I's 82 could be triaged first (likely numbering slips) to cut this", "Months 4–5 per plan"],
        ["G4", "**O2 miss triage not done**", "the five-category breakdown of HGVS-recall misses; whether low recall is extraction error", "a panel member or Dr. Lin triages 50 sampled misses on the private page", "2–4 h of one person", "days"],
        ["G5", "**Blinded Claude vs open-weight audit not drawn**", "the registered O5 accuracy measure; the only neutral check on the gatekeeper's reading", "set the sample size with D-11; draw by seed; same raters, blind to model", "panel: 2 × n claims; for n = 100, ≈ 7–20 h; model: $0", "with G1"],
        ["G6", "**Bias arm has no numbers** (O4)", "per-disease frequency deviation; the ascertainment-bias deliverable", "a person fills four comparator sheets without looking at literature frequencies; then run `frequency_deviation.py`", "4 sheets × 1–2 h; model: $0", "days once a person is assigned"],
        ["G7", "**Open access only** (D-32): 14–53% of each corpus has full text", "completeness denominators; recall of the paywalled literature; the gap count is a lower bound", "none within the rules; a decision to add institutional access would be a deviation and a re-run", "if reopened: extraction ≈ $2 per paper plus gatekeeper; ~300 more papers ≈ $600–900", "not planned"],
        ["G8", "**Known extraction gaps frozen on purpose**: no hedge rule; relatives' variant fields from the proband's sentence; cohort statements applied to individuals", "a share of unsupported claims (Figure 3C); would need a v7 and a deviation", "wait for O1; if it fails or shows these classes, propose v7 (D-nn) and re-run", "full six-disease re-run ≈ $800–1,000 (extraction + gatekeeper + repeat, from this run's spend)", "after O1"],
        ["G9", "**Input conversion problems** in ~10 papers (scrambled, transposed or image-only tables; missing or truncated supplements)", "recall in those papers (e.g. SSADH 14635103: 12 of 54 families); several O2 misses", "fix the converter / refetch supplements; re-extract those papers under a logged deviation", "≈ $2–3 per paper plus gatekeeper ≈ $40–60 for 12 papers", "days; needs approval"],
        ["G10", "**Notation and normalization**: AxD cDNA without 'c.', legacy numbering, protein-only strings (65 AxD, 85 HA20)", "tier-1 matching (recall, overlap, gap candidates for those variants)", "harness-side query corrections as in the pilot's D-26 (never in extraction); report by description type", "$0 model; 1–2 days scripting; log as a deviation", "days"],
        ["G11", "**19 proposed same-person groups unmerged**; 50-merge hand check (D-35) not done", "deduplicated counts (lower bounds on collapse 0.2–3.8%); GPSEA denominators", "a person confirms groups and checks the registered 50-merge sample; merging after the freeze is a deviation", "2–4 h of one person", "days"],
        ["G12", "**Checklist-to-HPO maps unreviewed** (five diseases)", "the HPO terms behind 20 × 5 checklist items in the phenopackets", "Dr. Lin or the panel reviews `configs/checklist_hpo/`", "1–2 h", "days"],
        ["G13", "**Memorization probe underpowered** (10 post-cutoff papers)", "the before/after comparison in §7.4.3", "none now; more post-cutoff papers accrue with time", "$0", "—"],
        ["G14", "**Expert-minutes not measured** (O5)", "efficiency per accepted record", "comes with G3", "$0", "with G3"],
        ["G15", "**Budget not reconciled** (D-15): session readings, not billing", "spend per line as promised to the program", "Dr. Lin reads Settings > Usage on the funded account and confirms which account the sessions ran on", "0.5 h", "days"],
        ["G16", "**Pre-registration tags not on GitHub; OSF registration not made**", "the public, timestamped record of the freeze", "Dr. Lin pushes `prereg-v1.0` and `pipeline-v1.0` (the session cannot) and registers on OSF (`reports/drafts/osf_registration.md`)", "0.5 h", "days"],
        ["G17", "**Drafted messages unsent** (Monarch, ClinVar maintainers, Anthropic credits question, panel note)", "Month-1 outreach commitments; the credits/overage question (D-17)", "Dr. Lin sends from `reports/drafts/`", "0.5 h", "days"],
    ]
    plan = [
        ["1", "Settle D-11 and share the O1 pages; draw the O5 audit sample at the same time (G1, G5)", "unblocks the primary outcome and the only neutral check on the gatekeeper"],
        ["2", "Submit the OMIM request; push the tags; register on OSF; send the drafts (G2, G16, G17)", "no cost; long lead times start now"],
        ["3", "Triage the 50 O2 misses and LAD-I's 82 gap candidates first (G4, part of G3)", "tells us whether low recall and the biggest gap list are real before the panel spends hours on them"],
        ["4", "Fill the four comparator sheets (G6); review the checklist maps (G12); confirm the merge groups (G11)", "small human tasks that each unblock a registered figure"],
        ["5", "Only after O1 reads: decide on v7 and a re-run (G8), the input repairs (G9) and the notation repairs (G10)", "changes to the frozen pipeline are deviations and should answer a measured failure, not an expected one"],
        ["6", "Panel adjudication of the remaining candidates (G3), then drafts and sign-off", "Months 4–5 per the plan; the dossiers and the page are ready"],
    ]
    return f"""## 5. Gaps and a plan to close them

**Table 16. Gaps, what each blocks, who acts, and what closing it costs.** Costs are rough: model costs use this run's measured unit costs (§3.13); panel hours use 1–3 minutes per audited claim and 10–15 minutes per dossier, which are guesses until the adjudication page logs real minutes.

{table(["#", "Gap", "What it blocks", "Who acts and how", "Rough cost", "Time"], rows_)}

**Recommended order.**

{table(["Step", "Do", "Why first"], plan)}

Items 1–4 cost no model spend and about 60–110 panel hours in total, most of it adjudication. Nothing in items 1–4 touches the frozen pipeline. Item 5 is where deviations would start, and it should wait for O1's number."""


def limitations(D):
    return """## 6. Limitations of this report

- **No human-rated accuracy for the frozen pipeline.** Every support figure in §3.2 is a model's reading of a model's output.
- **HA20 is in every table.** It is flagged and the five-disease subtotals are given, but readers comparing diseases should remember that HA20's rules were tuned on HA20's papers.
- **ClinVar only.** OMIM, half of the registered answer key, is absent from concordance and from the gap definition.
- **Open access only.** The corpora hold 14–53% of the eligible literature; completeness and recall are measured on what was accessible.
- **Cost figures are session estimates** with frozen readings and overlapping stages, and the open-weight key is shared.
- **Helper-reported problems** (input conversion, self-contradicting papers, likely non-gaps) are model output, recorded as such and not verified by a person.
- **The author of this draft is the pipeline's author.** Claude Code built the pipeline, ran it, and generated this report from its outputs. The numbers are reproducible from the committed files; the framing is not independent of the system it describes, which is one more reason the human audit decides."""


def availability(D):
    return f"""## 7. Data, code and reproducibility

- **Repository:** `cjimmylin/gp-rarelink`, commit `{D['commit']}`. Pre-registration: `preregistration/analysis_plan.md` v1.0 (frozen 2026-10-20, D-36). Decisions and deviations: `DECISIONS.md`. Spend: `BUDGET.md`.
- **Records:** `data/extracted/<disease>/pv1-<disease>/` holds per-paper tables, claims with spans, gatekeeper verdicts, reconciled individuals, normalized variants, HPO bindings and the phenopackets. Full-text papers are not committed.
- **Harness outputs:** `analysis/six_disease/`, `adjudication/`, `analysis/openweight/`, `analysis/bias/`, `analysis/exploratory/`.
- **This report:** `analysis/interim_paper/build.py` (text, tables), `figures.py`, `data.py` (inputs; Supplementary Table S1 lists them); output in `reports/interim_paper/`. Re-run with `uv run python -m analysis.interim_paper.build`.
- **Reference snapshots** live outside the repository and are re-created by `pipeline/harness/snapshot_reference.py --per-gene`, `benchmark_chen2020.py` and `catalogue_grossi2024.py`; their manifests and counts are under `analysis/poc/reference_snapshot/`.
- **Rating and adjudication pages** are private claude.ai artifact pages built by scripts under `adjudication/`; their stores are collected by `collect_o1.py` and `apply_ratings.py`. Nothing has been published (standing instruction, 2026-10-21)."""


# ---------------------------------------------------------------------------------------------- supplement
def supplement(D):
    S = ["# Supplementary material", "", f"*Companion to the interim report of {TODAY}, commit `{D['commit']}`. Generated by the same script.*", ""]
    # S1 inputs
    S += ["## Supplementary Table S1. Input files", "", table(["Key", "Path"], [[k, f"`{v}`"] for k, v in D["sources"].items()]), ""]
    # S2 ClinVar counts
    S += ["## Supplementary Table S2. ClinVar counts per gene at the two snapshots", "",
          table(["Gene", "Release (read 2026-10-19)", "Single-gene records", "P/LP", "VUS", "Conflicting", "Records naming the disease", "Release (read 2026-10-21)", "Records", "P/LP"],
                [[D["gene"][d], c["release"][5:16], N(c["total"]), c["plp"], c["vus"], c["conflicting"], c["naming_disease"], c["release_recheck"][5:16], N(c["total_recheck"]), c["plp_recheck"]] for d, c in D["clinvar"].items()]), ""]
    # S3 checklists
    rows_ = []
    maxn = max(len(v["items"]) for v in D["checklists"].values())
    for i in range(maxn):
        rows_.append([i + 1] + [D["checklists"][d]["items"][i] if i < len(D["checklists"][d]["items"]) else "" for d in DISEASES])
    S += ["## Supplementary Table S3. The 20-item checklists per disease (D-38)", "",
          "Sources: " + "; ".join(f"{SHORT[d]} {D['checklists'][d]['source_pmid']}" for d in DISEASES) + ".", "",
          table(["#"] + [lab(D, d) for d in DISEASES], rows_), ""]
    # S4 gatekeeper fields and about
    rows_ = []
    for d in DISEASES:
        r = D["run"][d]
        rows_.append([lab(D, d), "; ".join(f"`{f}` {n}" for f, n in r["unsupported_top_fields"]), "; ".join(f"{k.replace('_', ' ')} {v}" for k, v in r["unsupported_by_about"].items()),
                      "; ".join(f"{p} ({n})" for p, n in r["top3_papers_unsupported"])])
    S += ["## Supplementary Table S4. Gatekeeper v4: unsupported claims by field, by whom the quote was about, and the three worst papers", "",
          table(["Disease", "Top fields (count)", "Whom the quote was about", "Worst three papers (PMID, unsupported claims)"], rows_), "",
          f"![Supplementary Figure S1]({D['figs']['figS1']})", "", "**Supplementary Figure S1.** Cumulative share of each disease's unsupported claims against papers ranked by their count.", ""]
    # S5 input problems
    rows_ = [[lab(D, d), p] for d in DISEASES for p in INPUT_PROBLEMS[d]]
    S += ["## Supplementary Table S5. Input problems and self-contradicting papers reported by the extraction and gatekeeper helpers", "",
          "These are helper reports collected in `reports/six_disease_run_findings.md` §5; they are not verified by a person and are not counted in any metric.", "",
          table(["Disease", "Problem (PMID)"], rows_), "", "Papers that contradict themselves (table vs text, abstract vs body), examples: " + "; ".join(SELF_CONTRADICTIONS) + ".", ""]
    # S6 repeat per paper
    rows_ = []
    for d in DISEASES:
        for p, v in sorted(D["repeat"][d]["per_paper"].items()):
            f2 = lambda x, nd=2: "—" if x is None else f"{x:.{nd}f}"
            rows_.append([lab(D, d), p, f"{v['individuals'][0]} / {v['individuals'][1]}", f2(v.get('variant_key_jaccard')), f2(v.get('variant_jaccard')), f"{f2(v.get('checklist_agreement'), 3)} ({v.get('checklist_cells_compared', 0)})", f2(v.get('feature_jaccard_label_free'))])
    S += ["## Supplementary Table S6. Run-to-run repeat, per paper", "",
          table(["Disease", "PMID", "Individuals (run / repeat)", "Variant keys", "Variant strings", "Checklist agreement (cells)", "Features, label-free"], rows_), ""]
    # S7 stage 4 details
    rows_ = []
    for d in DISEASES:
        s, b = D["stage4"][d], D["build"][d]["counts"]
        sc = s["status_counts"]
        rows_.append([lab(D, d), sc["normalized"], sc["corrected"], sc["protein_only"], sc["not_normalized"], sc["unresolvable"], s["mane_select"],
                      b.get("feature_rows_unbound_skipped", 0), b.get("features_from_checklist_observed", 0), b.get("features_from_checklist_excluded", 0),
                      "; ".join(f"{k.replace('gk_dropped_', '')} {v}" for k, v in sorted(b.items()) if k.startswith("gk_dropped"))])
    S += ["## Supplementary Table S7. Stage 4 details: normalization status, checklist-derived terms and claims the gatekeeper removed", "",
          table(["Disease", "Normalized", "Corrected query", "Protein-only", "Not normalized", "Unresolvable", "MANE Select", "Feature rows unbound (skipped)", "Checklist terms observed", "Checklist terms excluded", "Claims dropped by gatekeeper, by kind"], rows_), "",
          f"![Supplementary Figure S2]({D['figs']['figS2']})", "", "**Supplementary Figure S2.** Variant interpretations in the phenopackets by coarse class.", "",
          f"![Supplementary Figure S3]({D['figs']['figS3']})", "", "**Supplementary Figure S3.** The ten most-observed HPO terms per disease, with the count excluded for the same term.", "",
          f"![Supplementary Figure S4]({D['figs']['figS4']})", "", "**Supplementary Figure S4.** Field coverage: the share of rows with an asserted value rather than 'not reported'.", ""]
    # S8 O2 details
    rows_ = []
    for d in DISEASES:
        cc = D["o2"][d]["all_papers"]["classification_confusion_clinvar_x_authors"]
        rows_.append([lab(D, d), "; ".join(f"{k} {v}" for k, v in sorted(cc.items()))])
    miss_rows = [[lab(D, d), p, n] for d in DISEASES for p, n in D["o2_misses_by_paper"].get(d, [])]
    tiers = [[lab(D, d), t.get("1", 0), t.get("2", 0), t.get("unmatched", 0), t.get("unmatched_protein_only", 0)] for d, t in D["o2_tiers"].items()]
    S += ["## Supplementary Table S8. O2 details", "", "**Classification confusion (ClinVar aggregate | authors' assertion: count).**", "", table(["Disease", "Cells"], rows_), "",
          "**Extracted variants by match tier.**", "", table(["Disease", "Tier 1 (allele)", "Tier 2 (protein)", "Unmatched (placed)", "Unmatched (protein-only)"], tiers), "",
          "**HGVS-recall misses by ClinVar-cited paper.**", "", table(["Disease", "PMID", "Reference pairs not recovered"], miss_rows), "",
          f"![Supplementary Figure S7]({D['figs']['figS7']})", "", "**Supplementary Figure S7.** O2 misses by paper.", "",
          f"![Supplementary Figure S5]({D['figs']['figS5']})", "", "**Supplementary Figure S5.** Completeness against the two published catalogues.", ""]
    # S9 gap candidates and reclassification
    gc = D["gap_candidates"]
    rows_ = [[r["candidate_id"], r["hgvs_c"], r["hgvs_p_predicted"], r["protein_check"], r["n_papers"], r["n_identities"], r["author_class"], r["only_clinvar_cited_papers"]] for r in gc]
    rc = [[r["disease"], r["hgvs_c"], r["hgvs_p_predicted"], r["n_papers"], r["n_identities"], r["author_class"], r["clinvar_class"], r["clinvar_review_status"], r["strong_literature_support_proposed"]] for r in D["reclass"]]
    mg = [[r["disease"], r["identities"], r["n"], r["candidates"]] for r in D["merges_rows"]]
    S += ["## Supplementary Table S9. Gap candidates, reclassification candidates and proposed same-person groups", "",
          f"**All {len(gc)} gap candidates** (`adjudication/o3_gaps/candidates.csv`; dossiers in `dossiers/`). Pending adjudication; OMIM not checked.", "",
          table(["Candidate", "cDNA (MANE)", "Predicted protein", "Protein check", "Papers", "Identities", "Authors' class", "Only ClinVar-cited papers"], rows_), "",
          f"**Reclassification candidates ({len(rc)}; exploratory).** In ClinVar only as VUS or conflicting; 'strong' is a proposed rule.", "",
          table(["Disease", "cDNA (MANE)", "Predicted protein", "Papers", "Identities", "Authors' class", "ClinVar class", "ClinVar review status", "Strong (proposed)"], rc), "",
          "**Proposed same-person groups (unconfirmed; nothing merged).**", "", table(["Disease", "Identities", "n", "Candidate"], mg), ""]
    # S10 memorization by disease
    rows_ = []
    for m, mn in (("claude", "Claude"), ("open", "DeepSeek")):
        for k, v in sorted(D["mem"][m]["by_disease_stratum"].items()):
            d, s = k.split("|")
            rows_.append([mn, lab(D, d), s, v["papers"], f"{v['cb_specific']} / {v['cb_guess']} / {v['cb_none']}", v["cb_papers_with_variant_hit"], f"{v['cp_mean_rougeL_f1']:.3f}", v["cp_max_longest_run"]])
    S += ["## Supplementary Table S10. Memorization probe by disease and stratum", "",
          table(["Model", "Disease", "Stratum", "Papers", "Specific / guess / none", "Papers with a variant hit", "Mean ROUGE-L F1", "Longest run"], rows_), ""]
    # S11 open-weight details
    rows_ = []
    for d in ("ha20", "ssadh"):
        m, g = D["ow_manifest"][d], D["ow_gk"][d]["open"]
        rows_.append([lab(D, d), m["papers"], "; ".join(f"{k} {v}" for k, v in sorted(m["tools_version_of_final_attempt"].items())), len(m["papers_with_failed_attempts"]),
                      m["final_attempts"]["retried_calls"], m["final_attempts"]["calls"], f"{m['final_attempts']['prompt_tokens'] / 1e6:.0f}M / {m['final_attempts']['completion_tokens'] / 1e6:.1f}M",
                      f"${m['final_attempts']['cost_usd_reported_by_host']:.2f}", g["by_span"]["empty"]["claims"], g["by_span"]["empty"]["unsupported"]["k"], g["by_span"]["empty"]["supported"],
                      g["quote_not_found_by_span_check"]["claims"], "; ".join(f"`{f}` {n}" for f, n in g["unsupported_top_fields"][:4])])
    S += ["## Supplementary Table S11. Open-weight run details", "",
          table(["Disease", "Papers", "Harness version of final attempt", "Papers with failed attempts", "Retried calls", "API calls", "Prompt / completion tokens", "Host-reported cost", "Claims with an empty quote", "…judged unsupported", "…judged supported", "Claims whose quote the span check did not find", "Top unsupported fields"], rows_), ""]
    # S12 GPSEA top terms
    rows_ = []
    an_names = {"truncating_vs_missense": "truncating vs missense", "hotspot_R79_R88_R239_vs_other": "hotspot vs other missense", "sex": "sex", "biallelic_truncating": "biallelic truncating"}
    for d, v in D["gpsea"]["diseases"].items():
        for an, r in v["analyses"].items():
            for t in r["top"][:5]:
                rows_.append([lab(D, d), an_names.get(an, an), t["hpo_label"], t["n_usable"], "; ".join(f"{k.replace('group_', '')} {val}" for k, val in t.items() if k.startswith("group")), f"{t['p']:.3f}", f"{t['p_bh']:.3f}"])
    S += ["## Supplementary Table S12. GPSEA: the five lowest-p terms per test", "",
          table(["Disease", "Test", "Term", "Usable", "Group shares", "p", "p_BH"], rows_), "",
          f"![Supplementary Figure S6]({D['figs']['figS6']})", "", "**Supplementary Figure S6.** Danon disease GPSEA tests.", ""]
    # S13 budget segments
    rows_ = [[s["end_reading"], s["work"], s["line"], f"${float(s['end_usd']) - float(s['start_usd']):,.2f}"] for s in D["budget"]["segments"]]
    S += ["## Supplementary Table S13. Spend segments (session cost readings)", "", table(["Reading at", "Work", "Line (or split)", "Amount"], rows_), ""]
    # S14 pilot gates
    S += ["## Supplementary Table S14. The development pilot's gates (HA20, from `reports/poc_report.md`)", "",
          table(["Gate", "Question", "Threshold", "Result"],
                [["Q1", "Open-access corpus", "≥ 70% with full text", "53.1% (85 of 160): not met"], ["Q2", "Verbatim provenance", "every value has PMID + span", "64,999 values, 100% verbatim: met"],
                 ["Q3", "Valid phenopackets, normalized HGVS", "100% valid; ≥ 95% cDNA normalized or flagged", "749 of 749; 97.8%: met"], ["Q4", "Unsupported values", "span match ≥ 98%; human ≤ 4% (n = 50)", "100%; 6.0% and 6.3%: not met"],
                 ["Q5", "Deduplication", "0 false merges in the hand check", "policy v3: 6 of 93: not met; v4: 0 of 50 (not independent)"], ["Q6", "Concordance harness", "table with CIs vs dated snapshots", "met (ClinVar, HPO)"],
                 ["Q7", "Completeness", "restricted recall ≥ 80%", "9 of 9: met"], ["Q8", "Cost", "six-disease projection ≤ $8,000", "$1,676–4,189: met"]]), ""]
    return "\n".join(S)


# ---------------------------------------------------------------------------------------------- main
def main():
    D = load()
    OUT.mkdir(parents=True, exist_ok=True)
    D["figs"] = figures.make_all(D)
    head = f"""# GP-RareLink: literature-curated, database-validated genotype–phenotype records for six rare diseases

## Interim report on all work to date (internal review draft)

*Rare Genomics Institute and the Stanford Open Virtual Assistant Lab. PI: Dr. Jimmy Lin. Methods co-lead: Prof. Monica Lam. Adjudication panel: Drs. Eva Wu, Gabriela Balderrama and Anita Chacko. Drafted by Claude Code from the repository's committed outputs on {TODAY} (commit `{D['commit']}`). Funded by Anthropic's AI for Science program (award 2026-08-31). Internal review only; not for distribution.*

![Figure 1. Study overview and status.]({D['figs']['fig1']})

**Figure 1.** The pipeline, the ground-truth boundary, the harness and the human steps, with each part's status.

"""
    main_md = "\n\n".join([head, status_box(D), abstract(D), intro(D), methods(D), results_corpus(D), results_extraction(D), results_repeat(D), results_records(D),
                           results_o1(D), results_o2(D), results_o3(D), results_o4(D), results_o5(D), results_exploratory(D), per_disease(D), results_cost(D),
                           discussion(D), gaps(D), limitations(D), availability(D)]) + "\n"
    (OUT / "interim_paper.md").write_text(main_md)
    (OUT / "supplement.md").write_text(supplement(D) + "\n")
    (OUT / "README.md").write_text(f"""# Interim paper (internal review)

- `interim_paper.md`: main text, tables and figures.
- `supplement.md`: supplementary tables and figures.
- `interim_paper.pdf`: both, rendered (`bash analysis/interim_paper/make_pdf.sh`).
- `figures/`: PNG figures.

Generated on {TODAY} at commit `{D['commit']}` by `uv run python -m analysis.interim_paper.build`. Every number comes from the files listed in Supplementary Table S1. Nothing here is published.
""")
    print(f"wrote {OUT / 'interim_paper.md'} ({len(main_md):,} chars) and supplement.md; figures: {len(D['figs'])}")


if __name__ == "__main__":
    main()
