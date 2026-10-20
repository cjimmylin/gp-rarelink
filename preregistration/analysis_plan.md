# GP-RareLink pre-registration: analysis plan

> **Status: FROZEN v1.0, 2026-10-20.** This text is tagged `prereg-v1.0` in git, and the pipeline it describes is tagged `pipeline-v1.0`. Dr. Lin registers the same text publicly on OSF (D-09); the registration's DOI and date are then recorded in `DECISIONS.md`, not here, so this text stays the registered text. From this version on, any change is a deviation: it needs Dr. Lin's approval and a dated entry in `DECISIONS.md` (§9; `INSTRUCTIONS.md` §1.4).
>
> Prepared by Claude Code at Dr. Jimmy Lin's request, for review by Dr. Lin and Prof. Monica Lam (and by Drs. Wu, Balderrama and Chacko for sections 7.1 and 7.3).
>
> - v0.2 applied decisions D-02 to D-07, made by Dr. Lin on 2026-10-18.
> - v0.3 added the award details (award email of 2026-08-31) and open decision D-17.
> - v0.4 applied D-01 (Month-1 start date) and the re-planned timeline in §12.
> - v0.5 applies D-18: pilot first. The one-disease pilot (`POC_DESIGN.md`) becomes the development phase, A20 haploinsufficiency is reported separately, and the plan is frozen after the pilot. It also notes the pilot's ClinVar-seeded search (D-19).
> - v0.6 applies D-26 to D-28, decided by Dr. Lin on 2026-10-19 from the pilot's Stages 4 and 5: normalization success by description type (§7.2.2); normal findings recorded as the absent abnormality (§6.2); the gatekeeper checks every value, including its link to the person (§6.4).
> - v0.7 folds in the pilot report (`reports/poc_report.md` §10; D-29 to D-31, decided 2026-10-19). It also records the five-disease corpus searches and screening, the Mondo IDs and the dated ClinVar counts (2026-10-19). Changed sections: §4.1, §5.1, §5.2, §6.2 to §6.5, §7.1, §7.2 (matching, D-19 split, new §7.2.7 completeness), §10 and §13. No metric, threshold or disease was changed.
> - v1.0 (2026-10-20) freezes the plan. The pre-freeze smoke run of extraction v6 and gatekeeper v4 met its check (§6.5), and Dr. Lin chose to freeze v6 as tested (D-36). §6.1 records the model and dates; §6.5 the smoke run; §13 the freeze record. No metric, threshold or disease was changed.
> - v0.12 (2026-10-20) settles D-11 (the panel note goes out without asking for hours; optional add-ons only if time is offered) and D-35 (every remaining [proposed] default accepted). No [D-nn] item blocks the freeze any longer; what remains is the v6/v4 smoke run, the git tag and the OSF registration (§13).
> - v0.11 (2026-10-20) applies D-34: the human check of screening stopped at 20 items, all agreeing or unsure, and the screening calls stand (§5.1, §13).
> - v0.10 (2026-10-20) applies D-10: the open-weight comparator is DeepSeek-V4.1-Flash, run on HA20 and SSADH deficiency through an agent harness (§7.5, §13).
> - v0.9 (2026-10-20) applies D-09 (OSF), D-11 (raters), D-12 (OMIM access requested), D-17 (Claude Code route) and D-33 (literature-summary reviews included, flagged), plus the screening-check design and Dr. Lin's approval of the pilot report (§1, §5.1, §5.2, §6.1, §7.1, §7.5, §11, §13).
> - v0.8 applies D-08 (substitute trigger: an absolute count), D-19 (no ClinVar-cited seeds) and D-32 (open access only), decided by Dr. Lin on 2026-10-20 (§4.2, §5.1, §13).
>
> - Items marked **[D-nn]** still need a decision recorded in `DECISIONS.md` before the plan is frozen.
> - Items marked **(D-nn, decided)** are settled; the decision and its date are in `DECISIONS.md`.
> - Items marked **[proposed]** were Claude's defaults. Dr. Lin accepted all of them on 2026-10-20 (D-35); they now read **(D-35, decided)**.
> - Everything else restates commitments already made in `CONTEXT.md` and the grant application. Changing those after freezing is a deviation (`INSTRUCTIONS.md` §1.4).
>
> Until the plan is frozen, edits to this draft are ordinary revisions, not deviations. **Freezing** means: all [D-nn] items resolved, the file tagged in git (e.g. `prereg-v1.0`), and the same text registered publicly on OSF (D-09, decided). Freezing happens after the one-disease pilot (§6.5, D-18) and before any extraction run for the six-disease study.

Structure follows the usual sections of a preregistration for analysis of existing data (study information, data, prior knowledge, variables, analysis plan). Check OSF's current preregistration template at registration (D-09) and re-map sections if needed.

---

## 1. Study information

| | |
|---|---|
| **Title** | GP-RareLink: Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease |
| **Investigators** | Dr. Jimmy Lin (PI, Rare Genomics Institute); Prof. Monica Lam (co-lead, AI methods, Stanford OVAL Lab); adjudication panel Drs. Eva Wu, Gabriela Balderrama, Anita Chacko. *[OVAL contributors to be added by Prof. Lam.]* |
| **Funding** | Anthropic AI for Science Program, Rare Disease program, Basic science track. Awarded 2026-08-31: $45,000 in claude.ai usage credits, covering chat, Claude Code, Cowork and Claude Science (`grant/AWARD_EMAIL.md`). Credits only; no cash. |
| **Project dates** | Six months. Month 1 starts on the date the first credit deposit landed, provisionally 2026-09-21; Month 6 then ends 2027-03-20 (D-01, decided). |
| **Registry** | OSF, public, registered at the freeze, after the pilot report was approved and before the six-disease run (D-09, decided) |

## 2. Background and research question

Variant and phenotype knowledge for rare diseases is split across ClinVar, OMIM, HPO annotations, Monarch's phenopacket-store and, mostly, individual case reports. Many causative variants published in case reports never reach ClinVar or OMIM (`CONTEXT.md` §1; for the scale of the gap see `birgmeier2020_avada` and `wang2025_pubmind`).

**Research question.** Can the SLIDERS method (`joshi2026_sliders`), powered by Claude, build consolidated variant ↔ phenotype ↔ disease records from published case reports at an accuracy we can prove and at a scale that materially closes this gap?

**Design in one paragraph.** Claude, running inside SLIDERS, reads case reports for six rare diseases and emits GA4GH Phenopackets (v2) with a PMID and verbatim span on every value. ClinVar and OMIM are never shown to the extraction step. Instead they are the answer key: we measure concordance with what they already assert, which gives an accuracy estimate without spending adjudicator hours. A human audit of 250 claims measures how often a value is not supported by its cited span. Variants absent from both databases go to the RGI panel and, if approved, become draft ClinVar and OMIM submissions. A bias arm compares literature-derived phenotype frequencies with natural-history cohorts and probes for memorization. An efficiency arm measures expert time and compares Claude with an open-weight model under an identical scaffold.

## 3. Aims, hypotheses and outcome hierarchy

The five outcomes are the five success metrics in the grant (`CONTEXT.md` §6). Only one has a pre-specified pass/fail target.

| # | Outcome | Type | Pre-specified target |
|---|---|---|---|
| O1 | Unsupported-value rate, human audit of 250 claims (§7.1) | **Primary, confirmatory** | Observed rate < 2%, i.e. at most 4 of 250 (D-02, decided) |
| O2 | Concordance with ClinVar and OMIM on gene, normalized HGVS, classification, phenotype (§7.2) | Primary, estimation | None; estimates with CIs, no pass/fail cut-off (D-03, decided) |
| O3 | Gap closure: variants absent from both databases, adjudicated, prepared, accepted for submission (§7.3) | Primary, descriptive | None (counts by stage) |
| O4 | Ascertainment bias: per-disease deviation from natural-history cohorts, with memorization probe (§7.4) | Secondary | None |
| O5 | Efficiency: expert-minutes per accepted record; Claude vs open-weight model (§7.5) | Secondary | None |

The grant defines success as "high concordance with a low-false-positive workflow; new database findings are upside." All outcomes are reported whether favorable or not (`INSTRUCTIONS.md` §1.5).

**Directional expectations (exploratory, stated in advance):**
- Literature-derived frequencies of severe or early-onset features will be higher than in natural-history or genotype-first cohorts (`wright2024_penetrance`, `gagliardi2024_axd_ukb`).
- Classification concordance will be limited mainly by ClinVar's VUS and conflicting records rather than by extraction error, because case-report authors usually assert causality.
- Proband deduplication and counting will be a weak point (`murugan2026_reasoning_llm_ps4` found Claude Sonnet 4 weakest of five models at proband counting).

## 4. Diseases

### 4.1 Pilot set (fixed by the grant)

| Disease | Gene | Mondo | OMIM | ORPHA | Inheritance |
|---|---|---|---|---|---|
| Alexander disease | *GFAP* | MONDO:0008752 | 203450 | 58 | AD / de novo |
| Leukocyte adhesion deficiency I | *ITGB2* | MONDO:0007293 | 116920 | 2968 † | AR |
| A20 haploinsufficiency | *TNFAIP3* | MONDO:0800045 | 616744 | 476102 | AD |
| SSADH deficiency | *ALDH5A1* | MONDO:0010083 | 271980 | 22 | AR |
| Danon disease | *LAMP2* | MONDO:0010281 | 300257 | 34587 | X-linked dominant |
| Tangier disease | *ABCA1* | MONDO:0008783 | 205400 | 31150 | AR |

Mondo IDs come from the OMIM cross-references in Mondo release 2026-10-06, the release the pilot pinned (§6.2 takes OMIM and ORPHA cross-references from Mondo).

† Mondo cross-references MONDO:0007293 to Orphanet:99842, not to ORPHA 2968 as `CONTEXT.md` and the application give. To check against Orphanet before the freeze; records will use Mondo's cross-reference.

### 4.2 Substitution rule

Substitutes, in this order unless the panel decides otherwise: Blau syndrome (*NOD2*), Majeed syndrome (*LPIN2*), familial LCAT deficiency (*LCAT*), GAMT deficiency (*GAMT*), arterial tortuosity syndrome (*SLC2A10*), PAPA syndrome (*PSTPIP1*).

A pilot disease is replaced only if, after full-text screening (§5.1), fewer than 15 eligible primary reports (case reports, case series or cohorts) have accessible full text (D-08, decided). There is no share threshold: open full text covered 10.6–35.2% of the five new corpora at title/abstract stage (`analysis/corpus/coverage_2026-10-19.md`), so a share rule would have replaced the whole set. Coverage per disease is reported as a limitation, with accessible and inaccessible papers compared by publication decade. Any substitution is decided and logged in `DECISIONS.md` **before** extraction starts, on access grounds alone. It never depends on extraction or concordance results.

## 5. Data sources and ground-truth isolation

### 5.1 Literature corpus

**Search (D-35, decided).** For each disease, search PubMed from database inception to a single search date that is recorded. Queries combine the gene symbol with disease names and synonyms, taken from Mondo, Orphanet and the GeneReviews chapter. Add backward citation searching of the key reviews: `grossi2024_axd_meta`, `almarzanovoa2018_lad1_review`, `elhani2024_ha20_177`, `didiasova2020_ssadh_update`, `brambatti2019_danon_gender`, `koseki2021_tangier_review`. Exact query strings are saved in `data/literature/<disease>/search.md` with the date run and the hit count.

**Not used to build the corpus:** ClinVar and OMIM citation lists, or any index queried by ClinVar variant IDs. A corpus built from database citations would bias concordance upward and gap discovery downward. LitVar (`allot2023_litvar2`) may be queried by gene symbol only, and every PMID records which source found it. After extraction, the harness reports what share of the corpus is cited by ClinVar or OMIM (§7.2.5).

The pilot (§6.5) departed from this rule: it seeded its search with ClinVar-cited PMIDs, tagged so they can be separated. For the six-disease study the rule above stands: no ClinVar-cited seeds (D-19, decided). HA20's existing corpus keeps its tagged papers; when HA20 is re-extracted, papers that came only from ClinVar citations are reported separately. In the pilot, removing every ClinVar-cited paper lowered ClinVar presence from 42.1% to 38.2% of normalized variants (`reports/poc_stage6_findings.md` §3).

**Searches run for the five other diseases (2026-10-19).** The five searches followed this section's rule: no ClinVar or OMIM citation seeds. Each disease's query, filter, search date and hit count are in `configs/diseases.yaml` and `data/literature/<disease>/search.md`. Seeds were of two kinds:
- the background bibliography's papers for the disease;
- the reference lists of the key reviews, taken from Europe PMC's reference index (`seeds_from_references.py`). Some of these lists are partial: Almarza Novoa 2018 gave 8 references. References listed without a PMID are kept for hand resolution.

Two parts of the proposed search were not run:
- the Europe PMC full-text search;
- LitVar.

They are not added (D-35, decided): the PubMed search plus review references is the registered search, and its date is the cut-off.

**Comparator holdouts.** The natural-history comparators of §7.4.1 found by the search are marked out of the extraction corpus in each manifest (`in_extraction_corpus = false`, with the reason), by `pipeline/extract/corpus/disease_seeds.py`.

**Eligibility (D-35, decided; D-33, decided).**
- *Include:* primary publications (case reports, case series, cohort papers) that report individual-level genotype and/or phenotype for at least one person with the pilot disease. Any publication year.
- *Include, flagged (D-33, decided):* reviews with a per-patient table or list of individuals from earlier papers, as the HA20 pilot did (308 of its 799 people came from such tables). Their people are tagged secondary-source, deduplicated against primary reports (§6.3), and every patient-level result is reported with and without them. Under open access only (D-32), such tables are often the only open record of patients whose original papers are paywalled.
- *Exclude from extraction:* reviews with no new individuals and no per-patient table (these are used only for citation searching), animal or cell-only studies, conference abstracts, and papers with no English full text. Excluded papers are logged with the reason.
- Papers about the same individuals are **not** excluded. Overlap is handled by patient-level deduplication (§6.3).

**Screening (decided by Dr. Lin, 2026-10-20).** Title/abstract screening, then full-text screening. Claude may screen, but every decision is logged with a reason, and a human checks a random 10% of inclusions at title/abstract stage and all exclusions made at full-text stage. Each disease gets a PRISMA-style flow count, produced by script.

- **Full-text screening** uses `pipeline/extract/claude_code/prompts/screen_fulltext_v1.md` and `pipeline/extract/corpus/claude_code_fulltext_screen.py`. Each decision carries a verbatim evidence quote, checked by script against the paper. Done on 2026-10-20 for the five new diseases. Eligible primary reports with open full text: Alexander disease 68, LAD-I 38, SSADH deficiency 36, Danon disease 82, Tangier disease 28 (`analysis/corpus/coverage_2026-10-20.md`). All five meet the D-08 count. Human check (D-34, decided): Dr. Lin rated 20 items. Of 15 abstract-stage inclusions, he would include 14 and was unsure of 1 (exact 95% CI for agreement 68–100%). He agreed with all 5 full-text exclusions he rated (48–100%). Then he accepted the screening calls without rating the rest of the drafted sample (137 abstracts and 71 exclusions). The check is therefore smaller than drafted, and every report states this (`adjudication/screening_check/ratings_summary.json`).

- **Title and abstract screening is done** for all six diseases (2026-10-19 for the five new ones). Claude Code helper agents did it with `screen_v2.md`, the disease-neutral form of the pilot's prompt, logged with its sha256 in each `screening_log.json`.
- "Yes" and "unclear" both go forward to full text. For Tangier disease, papers on heterozygous *ABCA1* carriers with familial HDL deficiency are "unclear", so the full text decides.
- The human 10% check of inclusions is still to do for the five new diseases. For HA20, Jimmy labeled 40 records.

**Corpus size (D-05, decided).** The grant estimated "roughly 300 full-text reports" across six diseases. Some diseases will have more eligible reports than that share; Alexander disease alone has hundreds of published patients. We extract **all** eligible accessible reports. Cost is re-estimated after the pilot disease, A20 haploinsufficiency (§6.5).

If a cap is then needed for budget reasons, this procedure applies:
- the cap is set before extraction starts on the remaining diseases;
- papers are chosen by stratified random sampling with a recorded seed;
- the cap size and seed are logged in `DECISIONS.md` before sampling;
- the effect on gap closure is stated in every report.

Following this procedure is not a deviation.

**Access and licensing (D-32, decided).** Open access only: full text from PMC and Europe PMC, plus open copies found through Unpaywall. No institutional or library access is used. Record the access route for every paper: PMC/Europe PMC, other open copy (with its Unpaywall host type, version and license), or not accessible. Pages behind a bot check (e.g. reCAPTCHA) are not fetched, and hosts the network policy refuses are recorded as not fetched. Papers we could not access are listed in the manifest (`INSTRUCTIONS.md` §3). Full texts stay out of git (`.gitignore`); only manifests are committed.

### 5.2 Reference data (ground truth; concordance harness only)

All snapshots are taken on one date, as close as possible to the corpus search date, with a manifest recording the source URL, release identifier, download date and checksum (`pipeline/harness/snapshot_reference.py`).

**Where snapshots live.** Snapshot content is kept outside the repository checkout, e.g. `/home/user/gp-rarelink-reference/<date>/`. Only manifests and counts are committed, under `analysis/poc/reference_snapshot/<date>/`. The plan first said `data/reference/`, but the extraction guard refuses to run while that folder holds data. Keeping ground truth out of the checkout serves the same purpose (logged in `DECISIONS.md`, 2026-10-19). The six-disease study takes a fresh snapshot on one date before extraction starts. The 2026-10-19 counts are a planning baseline.

| Source | What | Used for |
|---|---|---|
| ClinVar | Dated release: variant summary, GRCh38 VCF, citation table | O2, O3 |
| OMIM | Allelic variants and clinical synopses for the six phenotype MIMs, **only via a licensed route**. Dr. Lin requests API access (D-12, decided). Until access arrives, O2 and O3 run on ClinVar, and the OMIM half is reported as "not yet assessed", never as concordant or absent | O2, O3 |
| HPO disease annotations (`phenotype.hpoa`, dated release) | HPO terms annotated to each OMIM disease | O2 phenotype concordance |
| Natural-history cohort papers (§7.4) | Cohort phenotype frequencies | O4 |

Direct, dated counts per gene (ClinVar records by classification; OMIM allelic variants) are computed from these snapshots by script. They replace the application's provisional counts (`CONTEXT.md` §4).

### 5.3 What the extraction pipeline may and may not see

**Allowed:**
- The paper's full text and supplements
- The target disease name, gene symbol and Mondo/OMIM/ORPHA identifiers
- The HPO ontology and Mondo ontology (terms, labels, synonyms, hierarchy, but not disease–phenotype annotations)
- HGNC, MANE Select / RefSeq transcript definitions
- VariantValidator normalization output
- Few-shot examples built from genes outside the pilot and substitute sets (e.g. phenopacket-store records for other genes)

**Not allowed:**
- ClinVar and OMIM, in any form
- `phenotype.hpoa` and other disease–phenotype annotation files (these encode OMIM and Orphanet content)
- LitVar's ClinVar links
- Outputs or prompts from the RGI–OVAL AutoOMIM project, which is built on OMIM-style content
- Natural-history comparator papers, in extraction prompts or few-shot examples
- Reviews' variant tables, as few-shot examples

**VariantValidator (D-35, decided).** Only the normalization fields of its response (genomic, transcript and protein HGVS; validation warnings) pass into the pipeline. Any database annotations in the response are dropped before the pipeline sees them.

**Enforcement (D-35, decided).**
1. Code under `pipeline/` never reads `data/reference/`, the comparator papers or the annotation files. An automated test fails if any such path or loader is referenced from `pipeline/`.
2. Every prompt sent to a model is logged with its hash, so any leak can be audited after the fact.
3. Only the concordance harness reads both the extracted records and `data/reference/`.

## 6. Extraction procedure

### 6.1 Models and versions

**Primary extractor and gatekeeper:** Claude Opus. The exact model ID, any sampling parameters and the dates of use are recorded when the pipeline is frozen (§6.5) and not changed afterwards. A model change is a deviation. The model's published training cutoff is recorded too, for the memorization probe (§7.4.3).

**Recorded at the freeze (2026-10-20):**
- **Model:** the Claude Opus model the Claude Code session served for the smoke run. Its exact ID, as the session reported it, is in `runs/poc-ha20-v6-smoke/manifest.json` (`notes.served_model_reported`). Each six-disease run records the ID its session reports; a different ID is a deviation.
- **Sampling parameters:** none are set on this route. Helpers run with Claude Code's defaults, and the session's effort setting is recorded in each run manifest.
- **Training data cutoff:** June 2026, from Anthropic's models overview (platform.claude.com/docs/en/models/overview, read 2026-10-20). Every paper published before then may have been in training data, which the memorization probe (§7.4.3) takes into account.
- **Dates of use:** the pilot ran 2026-10-18 to 2026-10-20; the six-disease runs record their own dates.

**Access route (D-17, decided).** As in the pilot (D-20): Claude Code helper agents, run in a Claude Code session on the funded claude.ai account. Each run records the model ID the session reports, the instructions' sha256 and the session's usage readings. Per-call token counts are not available on this route, which is why the cost model uses session readings. Whether usage beyond the plan's limits (overage) is covered by the award credits is being confirmed with Anthropic (draft in `reports/drafts/anthropic_credits_question.md`).

**Supporting tools:** VariantValidator, the phenopacket schema validator, and pyphetools CohortValidator (`pyphetools_software`). Each is pinned by version or access date.

### 6.2 Output records

One GA4GH Phenopacket (v2) per individual, plus a per-paper evidence table. Every individual record carries:

- **Provenance:** PMID (or DOI), section, verbatim span and extraction date on every value.
- **Variants:**
  - the original string from the paper;
  - the transcript, flagged as *stated in paper* or *inferred*;
  - VariantValidator-normalized HGVS (transcript-level and GRCh38 genomic), or a recorded normalization failure;
  - zygosity and inheritance, where reported;
  - the author-asserted pathogenicity, as stated (e.g. "pathogenic", "disease-causing", "VUS"), or "not stated".
- **Phenotypes:** HPO terms, each marked *observed*, *excluded* or *not reported*. "Not reported" is never collapsed into "excluded". Onset age is captured where reported. A normal finding is recorded as the abnormality it rules out, marked excluded ("elevated CRP", excluded), with the paper's own words in the span (D-27, decided).
- **Person-level values (D-29, D-31, decided).** A value is recorded for a person only when the paper ties it to that person.
  - Variant fields (zygosity, inheritance, classification) are not taken from statements about a group, the cohort or other papers (D-29).
  - Values in stacked multi-patient cells (e.g. "18 / 24 / 21 / 57") are not assigned to people by position. They are used only when the paper labels them for the person; otherwise the value is "not reported" (D-31).
- **Disease:** Mondo ID as primary, with OMIM and ORPHA cross-references taken from Mondo (not from OMIM).
- **Individual:** sex, age at report, family identifier as given in the paper.

**Abstention.** "Not reported" and "insufficient evidence" are valid outputs. A value with no verbatim span is not emitted.

### 6.3 Patient deduplication

The reconciliation agent proposes merges of individuals reported in more than one paper. A merge records its evidence, for example: shared family ID or pedigree, identical genotype plus consistent demographics, overlapping authors or center, or an explicit statement that the patient was previously reported.

**Merge policy v4 (D-23, decided).** Merges are made only on a citation that ties a person to an earlier report, and one-to-one. A citation naming several papers is not person-specific. The pilot dropped the sex-and-onset route: all 6 false merges of 93 under policy v3 came from it. Recurrent variants and relatives in one family match on sex and onset. Policy v4 had no false merges in the hand-checked set, but it was chosen after that check, so the six-disease study re-checks a random sample of 50 merges by hand, or all if fewer, with a recorded seed (D-35, decided).

Patient-level statistics use deduplicated individuals. Counts are reported with and without merges so the effect of deduplication is visible.

### 6.4 Gatekeeper pass

A second Claude read checks each value strictly against its cited span: is the value entailed by the span (`rashkin2023_ais`)? It does not judge whether the value is plausible. Values that fail are removed or downgraded to "not reported", and the reason is logged. It checks that the span ties the value to this individual (or this paper), not only that the words match. No value is exempted by a script match of value and span (D-28, decided).

Before that, a deterministic check confirms that every span occurs verbatim in the source text (after whitespace normalization). This check runs on **all** values, not a sample. Any span not found is reported as a fabricated-span count.

**Gatekeeper v4 and how its results are reported (from the pilot).**
- **What v4 records.** For each value, v4 records whom the quote is about: this person, a named group, the cohort in general, another person, the paper, or unclear. A quote about another person makes the value unsupported. A value read by position from a stacked cell is at most partially supported (D-31).
- **A filter, not a measure.** In the pilot the gatekeeper's own unsupported rate was 0.036% (v1) and 0.34% (v3). The human audits found 6.0% and 6.3%, and the gatekeeper flagged only 2 of 6 and 1 of 4 of the claims a person did not fully support (`reports/poc_report.md` §4). Its verdicts are therefore never reported as the error rate. Its accuracy against the human labels is reported instead (§7.1 (b)).
- **Phenopackets.** The phenopackets keep only claims the gatekeeper judged supported. The count removed is reported.

### 6.5 Development phase: the one-disease pilot, then the pipeline freeze

Prompts, the scaffold and normalization code are developed in a one-disease pilot on A20 haploinsufficiency (D-06, D-18, decided). The pilot runs under its own protocol (`POC_DESIGN.md`) before this plan is frozen. HA20 was chosen because its corpus is entirely open-access era (described in 2016) and a 65-article systematic review (`elhani2024_ha20_177`) gives a completeness check.

**How the pilot touches the data.** The pilot uses the whole HA20 corpus. It is scored against ClinVar (and OMIM, if access exists) to test the harness end to end. Prompts or schemas may change after its per-variant misses are seen. Because of that:
- **HA20 is a development disease, not a test disease.** In the six-disease study it is re-extracted with the frozen pipeline but reported separately. Headline pooled figures use the other five diseases (§7).
- **The pilot is recorded before freezing.** Its results, including what was seen of HA20's concordance, are summarized in §10.
- **The optional LAD-I stress test** (`POC_DESIGN.md` Stage 9), if it runs, makes those ten papers development papers. The study then reports LAD-I with and without them.

**What the pilot hands to the freeze.** The pilot's findings set:
- the frozen pipeline (`pipeline-v1.0`);
- the final schema and prompts;
- the cost model;
- the open choices listed in `POC_DESIGN.md` §7.

**Pilot outcome (2026-10-19; `reports/poc_report.md`).** The recommendation is "go, with fixes" (Jimmy, D-31 entry).
- **Met:** Q2, Q3, Q6, Q7 and Q8.
- **Not met:** Q1 (open-access coverage 53.1% against 70%), Q4 (human audit 3 of 50 unsupported, 6.0%, then 3 of 48, 6.3%, against the pilot's 4% limit) and Q5 (policy v3).

The candidates for `pipeline-v1.0` (sha256, first 12 characters, from the report) are:

| File | sha256 |
|---|---|
| `pipeline/extract/claude_code/prompts/extract_v6.md` | `aa689f24b470` |
| `pipeline/extract/claude_code/prompts/gatekeeper_v4.md` | `48ec4f05e65f` |
| `pipeline/extract/claude_code/schema_ha20_v5.json` | `f0fdf6b3bfea` |
| `pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md` | `55ab99df7f17` |

- **Smoke run done (2026-10-20; `reports/poc_smoke_v6_findings.md`).** As D-35 required, extraction v6 and gatekeeper v4 were run on the same 20-paper HA20 subset as the D-29 re-run before tagging `pipeline-v1.0`.
  - **The check was met:** the span check found 0 problems in 13,382 values (162 individuals).
  - **Gatekeeper v4** judged 4,538 claims: 23 unsupported and 75 partially supported. These are gatekeeper rates, not an estimate of the audit target (O1).
  - **One known gap is frozen as tested (D-36):** extraction v6 has no rule for hedged phrases ("suggested", "possible"), while the gatekeeper does. A status that rests only on a hedge is recorded as observed, then judged unsupported, and so becomes "not reported" in the phenopackets (§6.4).
  - The files tagged `pipeline-v1.0` are the four in the table above, with those hashes.
  - The six-disease schema generalizes `schema_ha20_v5.json` with a per-disease checklist. Each disease's checklist is written from its GeneReviews or key review before extraction. It is never written from `phenotype.hpoa`.
- **Normalization carries the D-26 repairs.** Success is reported by description type.

**Six-disease scale-up and cost.** The pilot projected extraction at $1,676–$4,189 for about 859 papers, by scaling patient counts at HA20's ratio. The screened corpora (§5.1) replace that projection. The revised estimate goes to Dr. Lin before the run.

A cost estimate for the six-disease run then goes to Dr. Lin for approval before scaling (`INSTRUCTIONS.md` §3). Cost per paper on HA20 may not carry over to diseases covered by long case series, so the estimate scales HA20's measured cost per input token by each corpus's token count, rather than by paper count. Token counts can be measured without running a model.

**Changes after the freeze (D-07, decided).** The frozen pipeline's results are primary. Any later fix (e.g. a normalization bug) is logged in `DECISIONS.md`, the affected analyses are re-run, and both versions are reported. This is stricter than the grant's budget assumed, which allowed re-runs "as normalization improves". The reason is that fixes chosen by looking at concordance misses would inflate concordance.

### 6.6 Validation

Every record is checked against the phenopacket v2 schema and with CohortValidator. The failure rate and failure types are reported. Records that fail are fixed by the pipeline or excluded, with counts.

## 7. Outcomes and analysis

**General (D-35, decided):**
- All figures are produced by scripts in `analysis/` from dated inputs at a recorded commit.
- Proportions get 95% confidence intervals:
  - Wilson intervals for simple proportions (`brown2001_binomial_ci`);
  - exact Clopper–Pearson for the audit;
  - publication-cluster bootstrap (10,000 resamples, recorded seed) wherever observations are nested within papers.
- Results are reported per disease. Headline pooled figures use the five diseases other than A20 haploinsufficiency, which was used to develop the pipeline (§6.5, D-18). HA20 is reported separately, and pooled figures that include it are given as a secondary analysis.
- There is one confirmatory test (O1), so no multiplicity correction is applied to it. Everything else is estimation and is labeled as such.

### 7.1 O1: Unsupported-value audit (primary, confirmatory)

**Claim pool.** Every value asserted in the final (post-gatekeeper) records across the six diseases, at atomic level. Examples of one claim: one HPO term with its state for one individual; one variant string for one individual; zygosity; sex; onset age; diagnosis; author-asserted pathogenicity. "Not reported" outputs carry no span and are not in the pool.

**Sample.** 250 claims drawn by simple random sampling, stratified by disease in proportion to claim volume (D-35, decided). The draw is made by script with a recorded seed, after the frozen pipeline has run on all six diseases and before anyone looks at concordance results.

**Rating (D-35, decided).**
- Two panel members rate each claim independently against the source paper, blind to the gatekeeper's verdict. A third resolves disagreements. Cohen's κ is reported (D-11, decided 2026-10-20; hours and optional add-ons wait on the panel's availability).
- Labels:
  - *supported*;
  - *unsupported:* the span does not entail the value;
  - *span not found:* the span is not in the paper.
- An HPO term more specific than the span justifies counts as unsupported. A less specific (ancestor) term counts as supported.
- **Additions from the pilot:**
  - a value the rater cannot verify from its quote and the paper counts as unsupported, because it should have been an abstention. A sensitivity analysis without such claims is reported beside it;
  - raters work on a rating page that shows the claim, its quote and the paper, never the gatekeeper's verdict or reasons;
  - any second look that shows gatekeeper reasons is reported separately, because labels changed there are not independent of the gatekeeper.

**Decision rule (D-02, decided): rule C.** O1 passes if the observed unsupported rate is below 2%, i.e. at most 4 unsupported claims out of 250.

The grant fixed n = 250 and the < 2% target but not how they combine. The rules considered, as computed by `preregistration/audit_operating_characteristics.py` on 2026-10-18:

| Rule | Passes with at most | P(pass) if true rate 0.5% | 1% | 1.5% | 2% | 3% |
|---|---|---|---|---|---|---|
| A: one-sided 95% CP upper bound < 2% | 1 of 250 | 0.64 | 0.29 | 0.11 | 0.04 | 0.00 |
| B: two-sided 95% CP upper bound < 2% | 0 of 250 | 0.29 | 0.08 | 0.02 | 0.01 | 0.00 |
| C: observed rate < 2% | 4 of 250 | 0.99 | 0.89 | 0.68 | 0.44 | 0.13 |

Rules A and B certify the target but often fail a good pipeline: rule A passes a pipeline with a true 1% rate only 29% of the time. Rule C was chosen because it gives a good pipeline a fair chance of passing. The cost is that it would pass a pipeline sitting exactly at 2% about 44% of the time.

To keep that limit visible, every report:
- gives the observed rate with its exact 95% interval (`background/audit_ci_250.py`);
- states the highest rate the audit cannot exclude;
- never describes a pass as proof that the true rate is below 2%.

**Secondary audit measures (D-11, decided 2026-10-20).** (b) comes from the main audit's own blinded ratings and needs no extra panel time, so it is always reported. (a) and (c) are done only if panel members offer time beyond the main audit. If they are not done, the report says so.
- (a) The unsupported rate *before* the gatekeeper, on a separate random sample. This measures what the gatekeeper adds.
- (b) Gatekeeper accuracy against human labels (`huang2024_no_self_correct`, `zheng2023_llm_judge`).
- (c) A false-abstention check: a sample of "not reported" values where the panel checks whether the paper did report the feature.

### 7.2 O2: Concordance with ClinVar and OMIM (primary, estimation)

The matched sets below are built by the harness from the frozen extraction and the dated snapshots.

**Variant matching (D-35, decided).** Extracted variants and reference variants are compared on the same normalized GRCh38 representation (normalized identically on both sides). Matches fall into tiers:
1. exact genomic allele;
2. protein-level only, for papers that give no c. or g. description;
3. unmatched.

The tier is reported for every comparison.

**As built in the pilot (`pipeline/harness/concordance.py`).**
- **Tier 1.** Tier 1 matches the GRCh38 VCF key (chromosome, position, reference and alternate allele). On the extracted side the key comes from VariantValidator; on the ClinVar side, from ClinVar's own VCF columns. Records are restricted to single-gene records for the pilot gene.
- **Unplaced descriptions.** Descriptions that cannot be placed on the genome (protein only, not normalized, rejected) are counted and reported, but are not in the denominator.
- **Gap pre-triage.** Before hand triage, each unmatched variant gets a pre-triage label by script: whether the protein change the paper states agrees with the one predicted from the normalized cDNA.
- **D-19 split.** Every O2 figure is reported for all papers and again without any paper ClinVar cites for the gene. For the five new diseases no paper enters through ClinVar citations, so the split measures only ClinVar-cited papers the search found itself.

#### 7.2.1 Gene

Share of deduplicated individuals whose recorded causal gene matches the gene OMIM associates with the disease phenotype MIM. Because each corpus is built per disease, this will be near ceiling by design. It is reported, but no weight is placed on it.

#### 7.2.2 Normalized HGVS

The reference pairs are (PMID, variant) pairs from two sources, restricted to corpus PMIDs and pilot genes:
- ClinVar's citation table;
- OMIM allelic-variant references.

Metrics:
- **HGVS concordance (recall form):** the share of reference pairs where the pipeline extracted the same variant (tier 1, and tiers 1+2) from that PMID.
- **Normalization success:** the share of extracted variant strings that VariantValidator normalizes without error, counted over strings that state a cDNA change, and by whether the transcript was stated in the paper. Strings that give only a protein change, or a structural change (copy number, exon deletion, prose), are reported separately with their status (D-26, decided).

The share of extracted variants found in ClinVar is reported only as *overlap*. It is not precision, because gap variants are expected; precision comes from the audit (O1).

#### 7.2.3 Classification

For extracted variants matched to a ClinVar record:
- the author-asserted pathogenicity is collapsed to P/LP, VUS or B/LB (plus "not stated");
- this is compared with ClinVar's aggregate germline classification, collapsed the same way, with conflicting records counted as VUS.

Reported as a confusion matrix plus percent agreement among stated values. This measures literature–ClinVar agreement as much as extraction accuracy; extraction accuracy of the asserted label is covered by O1.

#### 7.2.4 Phenotype association

- **(a) Variant → disease.** For matched variants, the share whose ClinVar condition, or whose OMIM allelic-variant entry, corresponds to the pilot disease (mapped through Mondo cross-references).
- **(b) Disease phenotype profile, ontology-aware.** Matching counts the same term or a descendant. Two numbers:
  - the share of HPO terms annotated to the OMIM disease (`phenotype.hpoa`) that are observed in at least one extracted individual;
  - the share of terms observed in at least 2 deduplicated individuals (D-35, decided) that match an annotated term.

Reference annotations are known to be incomplete (`connelly2026_fanconi_annotations`), so (b) is descriptive.

#### 7.2.5 Corpus overlap and coverage

Two descriptive numbers:
- the share of corpus PMIDs cited by ClinVar or OMIM for the pilot gene;
- **coverage**, the share of schema fields with an asserted value rather than "not reported", per field.

#### 7.2.6 Discordance triage

ClinVar contains misclassified variants (`wright2021_ddd_clinvar`), and literature nomenclature is often wrong (`lansdon2026_nomenclature_errors`). So:
- The primary concordance figures count **every** miss as discordant.
- A random sample of 50 misses, or all if fewer, with a recorded seed, is then triaged into five categories (D-11, D-35, decided). The triage is done by a panel member if one offers time, otherwise by Dr. Lin. If neither has time, the breakdown is reported as not done:
  1. extraction error;
  2. normalization error;
  3. error in the paper (e.g. a typo or legacy numbering);
  4. reference error or ambiguity;
  5. reference citation does not describe the variant.
- The breakdown is secondary and never replaces the primary figure.

**Success criterion (D-03, decided).** The grant gives no numeric concordance threshold, and none is added. Concordance is reported as estimates with 95% CIs, with no pass/fail cut-off, because ClinVar and OMIM are imperfect references (§7.2.6).

#### 7.2.7 Completeness against a published variant catalogue (from the pilot, D-30)

**What it measures.** This is recall against a variant catalogue published by people, not against a database. The method is the pilot's (`pipeline/harness/completeness.py`):
- **Transcription.** The catalogue's per-variant table is transcribed by script, with a check that its rows are complete.
- **Comparison level.** Variants are compared at the level the catalogue prints. The pilot's catalogue printed protein changes only.
- **Restricted recall.** Denominator: catalogue variants with a source paper in the extracted corpus. Numerator: variants found in rows from primary papers, which excludes reviews and the catalogue itself. Wilson 95% CI.
- **Also reported:** unrestricted recall; recall in the variant's own source paper; patients per source paper against the run's carriers.

**Outcome type.** This is a secondary, descriptive outcome with no threshold. The pilot's ≥ 80% gate (Q7) was a development gate only.

**The catalogue is fixed per disease before extraction (D-35, decided).** Each candidate's suitability is checked by script before extraction starts; a candidate without a per-variant table naming source papers is dropped, and that disease reports no completeness figure. Each candidate must have a per-variant table naming its source papers:

| Disease | Candidate catalogue |
|---|---|
| Alexander disease | `grossi2024_axd_meta` (open, PMC) |
| LAD-I | `almarzanovoa2018_lad1_review` (repository copy; its online supplement lists published cases) |
| SSADH deficiency | `tokatlylatzer2023_ssadh_genotype` (open, PMC) |
| Danon disease | none open yet; `brambatti2019_danon_gender` is paywalled |
| Tangier disease | `koseki2021_tangier_review` (open, publisher) |
| A20 haploinsufficiency | Chen 2020 Table S1 (D-30) |

A disease with no suitable open catalogue reports no completeness figure and says why. The candidates' reference lists were search seeds (§5.1), so their source papers are more likely to be in the corpus. That widens the restricted denominator; it does not make a variant easier to find. A catalogue is used only on the harness side: it is never shown to extraction, and never used as a few-shot example (§5.3).

### 7.3 O3: Gap closure (primary, descriptive)

**Definition.** A *gap variant* is an extracted variant that meets all of the following:
- normalized to tier 1;
- every supporting value passed the gatekeeper;
- no ClinVar record has the same GRCh38 allele in the snapshot;
- it is not listed among OMIM allelic variants for the gene.

**Stages counted per disease:**
1. Candidates
2. Adjudicated by the panel (ACMG/AMP framework, `richards2015_acmg`; ClinGen PP1/PP4 guidance, `biesecker2024_clingen_pp1_pp4`)
3. Approved
4. Drafted, marked *pending adjudication* until approved
5. Signed off by Dr. Lin
6. Submitted
7. Accepted by ClinVar or OMIM, as of the end of Month 6

Candidates are re-checked against live ClinVar at submission time and the date is recorded. Variants found in ClinVar only as VUS or conflicting, but with strong literature support, are reported separately as exploratory "reclassification candidates".

The ClinVar collection method ("literature only" vs "curation") affects what an approved record contains [D-13].

### 7.4 O4: Ascertainment bias and memorization (secondary)

#### 7.4.1 Comparators (D-04, decided)

The grant wording is ambiguous. The proposal text says "held-out *diseases* with published natural-history studies"; the metric says "per-disease deviation from held-out natural-history *cohorts*".

Reading adopted: for each pilot disease, natural-history or genotype-first cohort papers are held out of the extraction corpus and used as comparators. No extra diseases are added. Dr. Lin will obtain Prof. Lam's confirmation of this reading before the plan is frozen.

(D-35, decided) If no suitable comparator is found for a disease by the freeze, the bias arm leaves that disease out and says why.

Candidates from the background bibliography, not yet checked for suitability:

| Disease | Comparator candidates |
|---|---|
| Alexander disease | `mura2021_axd_italian`, `gagliardi2024_axd_ukb` |
| A20 haploinsufficiency | `he2026_ha20_multicenter` (preprint), `aeschlimann2018_ha20_cohort` |
| SSADH deficiency | `dibacco2019_ssadh_natural_history` |
| Danon disease | `boucek2011_danon_natural_history` (cohort part only; it also includes literature cases), `khedro2025_danon_prospective` |
| LAD-I, Tangier | None identified yet |

Most comparators are themselves clinically ascertained, so "cohort truth" is relative. Genotype-first cohorts such as UK Biobank are the closest to unbiased and are reported separately.

#### 7.4.2 Frequency deviation (D-35, decided)

1. For each comparator, a human lists HPO-mappable features and their cohort frequencies **before** literature frequencies are computed.
2. Literature frequency per feature is computed over deduplicated individuals, excluding anyone in the comparator cohort:
   - **primary:** observed ÷ (observed + excluded), i.e. among individuals explicitly assessed;
   - **secondary:** observed ÷ all individuals.
3. Report the per-feature difference (literature minus cohort) and the per-disease mean absolute deviation, with a publication-cluster bootstrap CI. This is where the three-state coding matters (`almail2024_reporting_gaps`).

#### 7.4.3 Memorization probe (D-35, decided)

The probe must work identically on Claude and the open-weight model, so it is black-box only (`grant_claim_checks.md` §15). Per disease, a stratified sample of corpus papers is drawn, split by publication date relative to each model's training cutoff (`roberts2024_lens_of_time`). Two probes:

- **(a) Closed-book recall.** Given only PMID, title and year, the model lists the variants and key phenotypes the paper reports. Overlap is scored against the full-text extraction (not against ClinVar).
- **(b) Guided completion** (`golchin2024_time_travel`). Given the opening of a passage, the model continues it. Overlap with the true text is measured.

Probe scores are compared before vs after the cutoff, adjusting for publication year, because date shift confounds membership signals (`duan2024_mia_llm`). Exploratory: whether audit and concordance results differ between high- and low-memorization papers.

Log-probability probes (`shi2024_mink_prob`) may be run on the open-weight model as a supplement, but are not used for the comparison.

### 7.5 O5: Efficiency and model comparison (secondary)

**Expert time.** The adjudication interface logs active minutes per record. The headline metric is expert-minutes per accepted record, where an accepted record is a gap-variant record approved by the panel. Audit minutes per claim are reported separately.

**Claude vs open-weight model (D-10, decided 2026-10-20).** Comparator: DeepSeek-V4.1-Flash (MIT license; 1,048,576-token context; read from its Hugging Face card on 2026-10-20), pinned to the 2026-09-10 checkpoint and called on a hosted API whose name, model ID and serving date are recorded. Diseases: A20 haploinsufficiency and SSADH deficiency. Scaffold: an open-source agent harness given the same instruction files, inputs and file tools as the Claude Code helpers (D-17); the write-up states every remaining difference. Compute: about $50 from contingency, logged with the host's invoice. Both models run on the same papers with the same scaffold, prompts, chunking, tools and inputs. If the open-weight model's context window forces smaller chunks, both models use them. No fine-tuning.

Metrics:
- span-not-found rate (all values);
- unsupported rate on a blinded audit sample of equal size for each model;
- HGVS concordance (§7.2.2);
- coverage;
- cost per paper (Claude: API cost; open-weight: compute cost at a stated rate);
- wall-clock time.

Results are published either way. Still to decide: the audit sample size per model (with D-11). The grant's $2,000 line covers Claude credits only. Claude runs as Claude Code helper agents (D-17). The open-weight model therefore needs an agent harness with the same instructions, file tools and inputs, and the write-up must say how the two scaffolds differ. Next step (Dr. Lin, 2026-10-20): Claude drafts a shortlist of open-weight models (open license, long context, tool use) with hosting options and cost. Dr. Lin picks one before the freeze; it runs on HA20 plus one other disease.

### 7.6 Exploratory analyses (labeled as such in any report)

- **Per-gene genotype–phenotype maps** with denominators and per-publication provenance, using GPSEA (`rekerle2026_gpsea`) with its multiple-testing correction.
- **Danon disease sex difference.** Does the extracted cohort reproduce the published male/female severity difference (`brambatti2019_danon_gender`; overlapping papers make this a reproduction check, not independent replication)?
- **Tangier disease.** Of ClinVar *ABCA1* records, what share corresponds to literature-reported Tangier patients versus unrelated testing?
- **Deduplication accuracy** against the duplicate-reported LAD-I cases identified in `almarzanovoa2018_lad1_review`. That review is not given to the pipeline.
- **Run-to-run stability.** Re-extract a random 10% of papers and measure agreement (`groza2024_gpt_hpo`), if budget allows.

## 8. What would count as success, partial success or failure

- **O1** passes if at most 4 of 250 audited claims are unsupported (D-02). A fail is reported as a fail, and a pass is reported with its 95% interval.
- **O2** and **O3** are reported as estimates and counts. The write-up does not call concordance "high" without the CI and the pre-specified definition beside it.
- **Pilot vs general.** Results on six diseases are pilot results and are not presented as general findings (`INSTRUCTIONS.md` §4).

## 9. Deviations and versioning

After freezing, any change to diseases, metrics, thresholds, sampling, models or analysis is logged in `DECISIONS.md` (Pre-registration deviations) with the date, reason, who approved it (Dr. Lin) and its expected effect. Reports list every deviation. Where feasible, both the registered and the revised analysis are reported.

## 10. Knowledge of the data before registration

Stated so readers can judge the risk of data-informed choices.

- **Aggregate ClinVar counts per gene** (MyVariant.info, ClinVar Miner) and **proxy OMIM counts** were seen at application time. No variant-level comparison between literature and ClinVar/OMIM has been made for any pilot gene.
- **Review figures** for patient and variant counts were read and checked on 2026-10-16 (`background/grant_claim_checks.md`). The fact-check found two figures contradicted or only roughly supported (Tangier, Danon). It also found that "408 phenopacket-store cohorts" has no published source. Since then, a further check found that the impact statement's "genotypes for 184 LAD-I patients whose variants were published but never structured" equals 323 − 139. By the fact-check's reading of `almarzanovoa2018_lad1_review`, those 184 are the patients *without* a reported genotype. This needs checking against the review [D-14]; it affects what gap closure can mean for LAD-I.
- **The HA20 pilot (2026-10-18 to 2026-10-19).** The pilot extracted 85 open-access HA20 papers twice, plus a 20-paper re-run, and every result was seen before this plan was frozen. That includes the following (`reports/poc_report.md`):
  - **ClinVar concordance for *TNFAIP3*:** 40 of 95 normalized variants in ClinVar; 17 of 20 author P/LP calls agree with ClinVar; 55 gap candidates.
  - **HPO concordance:** 13 of 14 annotated terms recalled.
  - **Completeness:** against Chen 2020.
  - **Audits:** two human audits.

  The only prompt change made after ClinVar content was seen is D-31 (extraction v6, gatekeeper v4). It came from the re-audit's stacked-cell failures, which compare values with their quotes, not from any ClinVar miss. The D-29 prompts were committed before the snapshot (`reports/poc_stage6_findings.md` §5). HA20 stays a development disease (§6.5).
- **The other five diseases (2026-10-19).** For each of these the following were seen:
  - their PubMed titles and abstracts, during screening;
  - their open-access full-text counts (§5.1);
  - their aggregate ClinVar counts by classification (`analysis/poc/reference_snapshot/2026-10-19/counts_<GENE>.json`, release 2026-10-12).

  No variant from those diseases' papers has been extracted, and no literature-to-ClinVar comparison has been made for their genes.
- **AutoOMIM.** The team has worked with OMIM-style content through the AutoOMIM collaboration, which is why §5.3 excludes it.
- **The grant mentions "our own internal experience"** with Claude's precision. This is not used as evidence here.

## 11. Data, code and licensing

- **Pipeline code** is released open source (`CONTEXT.md` §7).
- **Phenopackets and evidence tables** are released after adjudication. The license is undecided, and so is how verbatim spans from non-open-access papers are handled [D-16].
- **OMIM content** is not redistributed. Storage follows the terms of the API access Dr. Lin requests (D-12).
- **ClinVar snapshots** are re-downloadable. The repo holds the download script and manifest, not the files.
- **No patient data** of any kind is used.
- **Acknowledgment.** Every publication that used the award credits acknowledges Anthropic's AI for Science program (award email, 2026-08-31).

## 12. Timeline (D-01, decided)

Month 1 starts on the date the first credit deposit landed, provisionally 2026-09-21; the dates below shift if the actual landing date differs. Pilot first (D-18): the one-disease pilot runs in Month 2, and this plan is frozen after the pilot report. Extraction then overlaps with concordance in Month 3 (`CONTEXT.md` §8).

| When | Dates (provisional) | Step |
|---|---|---|
| Month 1 | 2026-09-21 to 2026-10-20 | Setup; background literature; this plan drafted; pilot design and code built (`POC_DESIGN.md` Stages 0–2) |
| Month 2 | 2026-10-21 to 2026-11-20 | The pilot on A20 haploinsufficiency (`POC_DESIGN.md` Stages 1–7) and its report. In parallel: corpus search and screening for the other five diseases, reference snapshots and dated counts. Then resolve the remaining [D-nn], fold in the pilot's findings, and freeze and register this plan |
| Month 3 | 2026-11-21 to 2026-12-20 | `pipeline-v1.0` on all six diseases (HA20 re-extracted and reported separately); concordance (O2) on each disease as it finishes; audit sample drawn once all six are done |
| Month 4 | 2026-12-21 to 2027-01-20 | Audit ratings (O1); gap-variant adjudication (O3); efficiency logging (O5) |
| Month 5 | 2027-01-21 to 2027-02-20 | Submissions after sign-off; bias arm and memorization probe (O4); model comparison |
| Month 6 | 2027-02-21 to 2027-03-20 | Write-up; all results published whether favorable or not |

## 13. Decisions and the freeze record

See `DECISIONS.md` → *Open decisions*. D-01 to D-07 and D-18 were decided on 2026-10-18, D-22 to D-31 on 2026-10-19, and D-08 to D-12, D-17, D-19 and D-32 to D-35 on 2026-10-20. Dr. Lin approved the pilot report as drafted on 2026-10-20.

No [D-nn] item blocks the freeze. D-11 was settled on 2026-10-20: the panel is asked without a request for hours, and optional add-ons depend on time offered. Every [proposed] default was accepted (D-35).

Freeze record (2026-10-20):
1. **Done:** the smoke run of extraction v6 and gatekeeper v4 on the 20-paper HA20 subset (§6.5). The span check found 0 problems; the session readings rose by $53.50 against an estimate of about $80. Dr. Lin chose to freeze v6 as tested (D-36).
2. **Done:** the pinned files are tagged `pipeline-v1.0` and this text `prereg-v1.0`, both on the same commit.
3. **Dr. Lin's step:** register this text publicly on OSF (D-09). The registration's DOI and date go into `DECISIONS.md`.

Full-text screening is done (§5.1).

D-13 to D-16 can follow, but D-13 should be settled before Month-4 adjudication begins.
