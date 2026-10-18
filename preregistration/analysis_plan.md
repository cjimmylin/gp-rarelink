# GP-RareLink pre-registration: analysis plan

> **Status: DRAFT v0.3, 2026-10-18. Not frozen.** Prepared by Claude Code at Dr. Jimmy Lin's request, for review by Dr. Lin and Prof. Monica Lam (and by Drs. Wu, Balderrama and Chacko for sections 7.1 and 7.3).
>
> - v0.2 applied decisions D-02 to D-07, made by Dr. Lin on 2026-10-18.
> - v0.3 adds the award details (award email of 2026-08-31) and open decision D-17.
>
> - Items marked **[D-nn]** still need a decision recorded in `DECISIONS.md` before the plan is frozen.
> - Items marked **(D-nn, decided)** are settled; the decision and its date are in `DECISIONS.md`.
> - Items marked **[proposed]** are Claude's defaults. Accept, change or delete each one.
> - Everything else restates commitments already made in `CONTEXT.md` and the grant application. Changing those after freezing is a deviation (`INSTRUCTIONS.md` §1.4).
>
> Until the plan is frozen, edits to this draft are ordinary revisions, not deviations. **Freezing** means: all [D-nn] items resolved, the file tagged in git (e.g. `prereg-v1.0`), and the same text registered with the chosen registry [D-09]. Freezing happens before any extraction run on study-corpus papers, including the development phase in §6.5.

Structure follows the usual sections of a preregistration for analysis of existing data (study information, data, prior knowledge, variables, analysis plan). Check the registry's current template when the venue is chosen [D-09] and re-map sections if needed.

---

## 1. Study information

| | |
|---|---|
| **Title** | GP-RareLink: Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease |
| **Investigators** | Dr. Jimmy Lin (PI, Rare Genomics Institute); Prof. Monica Lam (co-lead, AI methods, Stanford OVAL Lab); adjudication panel Drs. Eva Wu, Gabriela Balderrama, Anita Chacko. *[OVAL contributors to be added by Prof. Lam.]* |
| **Funding** | Anthropic AI for Science Program, Rare Disease program, Basic science track. Awarded 2026-08-31: $45,000 in claude.ai usage credits, covering chat, Claude Code, Cowork and Claude Science (`grant/AWARD_EMAIL.md`). Credits only; no cash. |
| **Project dates** | Month 1 start: *not yet recorded* [D-01]. Six months. |
| **Registry** | *To be decided* [D-09] |

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

| Disease | Gene | OMIM | ORPHA | Inheritance |
|---|---|---|---|---|
| Alexander disease | *GFAP* | 203450 | 58 | AD / de novo |
| Leukocyte adhesion deficiency I | *ITGB2* | 116920 | 2968 | AR |
| A20 haploinsufficiency | *TNFAIP3* | 616744 | 476102 | AD |
| SSADH deficiency | *ALDH5A1* | 271980 | 22 | AR |
| Danon disease | *LAMP2* | 300257 | 34587 | X-linked dominant |
| Tangier disease | *ABCA1* | 205400 | 31150 | AR |

Mondo IDs will be looked up and recorded with the release date when the reference snapshot is taken (§5.2). They are not listed here because they have not yet been verified.

### 4.2 Substitution rule

Substitutes, in this order unless the panel decides otherwise: Blau syndrome (*NOD2*), Majeed syndrome (*LPIN2*), familial LCAT deficiency (*LCAT*), GAMT deficiency (*GAMT*), arterial tortuosity syndrome (*SLC2A10*), PAPA syndrome (*PSTPIP1*).

A pilot disease is replaced only if, after screening (§5.1), its accessible full-text corpus falls below the threshold set in [D-08]. Any substitution is decided and logged in `DECISIONS.md` **before** extraction starts, on access grounds alone. It never depends on extraction or concordance results.

## 5. Data sources and ground-truth isolation

### 5.1 Literature corpus

**Search [proposed].** For each disease, search PubMed and Europe PMC (including full text) from database inception to a single search date that is recorded. Queries combine the gene symbol with disease names and synonyms, taken from Mondo, Orphanet and the GeneReviews chapter. Add backward citation searching of the key reviews: `grossi2024_axd_meta`, `almarzanovoa2018_lad1_review`, `elhani2024_ha20_177`, `didiasova2020_ssadh_update`, `brambatti2019_danon_gender`, `koseki2021_tangier_review`. Exact query strings are saved in `data/literature/<disease>/search.md` with the date run and the hit count.

**Not used to build the corpus:** ClinVar and OMIM citation lists, or any index queried by ClinVar variant IDs. A corpus built from database citations would bias concordance upward and gap discovery downward. LitVar (`allot2023_litvar2`) may be queried by gene symbol only, and every PMID records which source found it. After extraction, the harness reports what share of the corpus is cited by ClinVar or OMIM (§7.2.5).

**Eligibility [proposed].**
- *Include:* primary publications (case reports, case series, cohort papers) that report individual-level genotype and/or phenotype for at least one person with the pilot disease. Any publication year.
- *Exclude from extraction:* reviews with no new individuals (these are used only for citation searching), animal or cell-only studies, conference abstracts, and papers with no English full text. Excluded papers are logged with the reason.
- Papers about the same individuals are **not** excluded. Overlap is handled by patient-level deduplication (§6.3).

**Screening [proposed].** Title/abstract screening, then full-text screening. Claude may screen, but every decision is logged with a reason, and a human checks a random 10% of inclusions and all exclusions made at full-text stage. Each disease gets a PRISMA-style flow count, produced by script.

**Corpus size (D-05, decided).** The grant estimated "roughly 300 full-text reports" across six diseases. Some diseases will have more eligible reports than that share; Alexander disease alone has hundreds of published patients. We extract **all** eligible accessible reports. Cost is re-estimated after the pilot disease, A20 haploinsufficiency (§6.5).

If a cap is then needed for budget reasons, this procedure applies:
- the cap is set before extraction starts on the remaining diseases;
- papers are chosen by stratified random sampling with a recorded seed;
- the cap size and seed are logged in `DECISIONS.md` before sampling;
- the effect on gap closure is stated in every report.

Following this procedure is not a deviation.

**Access and licensing.** Prefer PMC open-access full text. Record the access route for every paper: PMC OA, other open copy, institutional access, or not accessible. Papers we could not access are listed in the manifest (`INSTRUCTIONS.md` §3). Full texts stay out of git (`.gitignore`); only manifests are committed.

### 5.2 Reference data (ground truth; concordance harness only)

All snapshots are taken on one date, as close as possible to the corpus search date, and stored under `data/reference/` with a manifest recording the source URL, release identifier, download date and checksum.

| Source | What | Used for |
|---|---|---|
| ClinVar | Dated release: variant summary, GRCh38 VCF, citation table | O2, O3 |
| OMIM | Allelic variants and clinical synopses for the six phenotype MIMs, **only via a licensed route** [D-12] | O2, O3 |
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

**VariantValidator [proposed].** Only the normalization fields of its response (genomic, transcript and protein HGVS; validation warnings) pass into the pipeline. Any database annotations in the response are dropped before the pipeline sees them.

**Enforcement [proposed].**
1. Code under `pipeline/` never reads `data/reference/`, the comparator papers or the annotation files. An automated test fails if any such path or loader is referenced from `pipeline/`.
2. Every prompt sent to a model is logged with its hash, so any leak can be audited after the fact.
3. Only the concordance harness reads both the extracted records and `data/reference/`.

## 6. Extraction procedure

### 6.1 Models and versions

**Primary extractor and gatekeeper:** Claude Opus. The exact model ID, any sampling parameters and the dates of use are recorded when the pipeline is frozen (§6.5) and not changed afterwards. A model change is a deviation. The model's published training cutoff is recorded too, for the memorization probe (§7.4.3).

**Access route [D-17].** How the pipeline calls Claude is not yet decided: through a claude.ai surface the award credits cover, or through the API. Whichever route is chosen, it must let us record and fix the exact model ID and settings for every call. The route is stated in the frozen plan.

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
- **Phenotypes:** HPO terms, each marked *observed*, *excluded* or *not reported*. "Not reported" is never collapsed into "excluded". Onset age is captured where reported.
- **Disease:** Mondo ID as primary, with OMIM and ORPHA cross-references taken from Mondo (not from OMIM).
- **Individual:** sex, age at report, family identifier as given in the paper.

**Abstention.** "Not reported" and "insufficient evidence" are valid outputs. A value with no verbatim span is not emitted.

### 6.3 Patient deduplication

The reconciliation agent proposes merges of individuals reported in more than one paper. A merge records its evidence, for example: shared family ID or pedigree, identical genotype plus consistent demographics, overlapping authors or center, or an explicit statement that the patient was previously reported.

Patient-level statistics use deduplicated individuals. Counts are reported with and without merges so the effect of deduplication is visible.

### 6.4 Gatekeeper pass

A second Claude read checks each value strictly against its cited span: is the value entailed by the span (`rashkin2023_ais`)? It does not judge whether the value is plausible. Values that fail are removed or downgraded to "not reported", and the reason is logged.

Before that, a deterministic check confirms that every span occurs verbatim in the source text (after whitespace normalization). This check runs on **all** values, not a sample. Any span not found is reported as a fabricated-span count.

### 6.5 Development phase and pipeline freeze

Prompts, the scaffold and normalization code are developed on a **development set**. The pilot disease is A20 haploinsufficiency (D-06, decided). It was chosen because its corpus is entirely open-access era (described in 2016) and a 65-article systematic review (`elhani2024_ha20_177`) gives a completeness check.

The development set is a random subset of the HA20 corpus: [proposed] 20% of eligible reports, at least 10, drawn by script with a recorded seed.

During development:
- Outputs are checked by humans against the source text and by the span check.
- They are **never** scored against ClinVar or OMIM, which would be tuning on the test set.

At the end of development the pipeline is tagged (`pipeline-v1.0`) and run on the full HA20 corpus, development papers included. A cost estimate for the other five diseases then goes to Dr. Lin for approval before scaling (`INSTRUCTIONS.md` §3).

Cost per paper on HA20 may not carry over to diseases covered by long case series. So the estimate scales HA20's measured cost per input token by each remaining corpus's token count, rather than by paper count. Token counts can be measured without running a model.

A sensitivity analysis excludes HA20.

**Changes after the freeze (D-07, decided).** The frozen pipeline's results are primary. Any later fix (e.g. a normalization bug) is logged in `DECISIONS.md`, the affected analyses are re-run, and both versions are reported. This is stricter than the grant's budget assumed, which allowed re-runs "as normalization improves". The reason is that fixes chosen by looking at concordance misses would inflate concordance.

### 6.6 Validation

Every record is checked against the phenopacket v2 schema and with CohortValidator. The failure rate and failure types are reported. Records that fail are fixed by the pipeline or excluded, with counts.

## 7. Outcomes and analysis

**General [proposed]:**
- All figures are produced by scripts in `analysis/` from dated inputs at a recorded commit.
- Proportions get 95% confidence intervals:
  - Wilson intervals for simple proportions (`brown2001_binomial_ci`);
  - exact Clopper–Pearson for the audit;
  - publication-cluster bootstrap (10,000 resamples, recorded seed) wherever observations are nested within papers.
- Results are reported per disease and pooled.
- There is one confirmatory test (O1), so no multiplicity correction is applied to it. Everything else is estimation and is labeled as such.

### 7.1 O1: Unsupported-value audit (primary, confirmatory)

**Claim pool.** Every value asserted in the final (post-gatekeeper) records across the six diseases, at atomic level. Examples of one claim: one HPO term with its state for one individual; one variant string for one individual; zygosity; sex; onset age; diagnosis; author-asserted pathogenicity. "Not reported" outputs carry no span and are not in the pool.

**Sample.** 250 claims drawn by simple random sampling, stratified by disease in proportion to claim volume [proposed]. The draw is made by script with a recorded seed, after the frozen pipeline has run on all six diseases and before anyone looks at concordance results.

**Rating [proposed].**
- Two panel members rate each claim independently against the source paper, blind to the gatekeeper's verdict. A third resolves disagreements. Cohen's κ is reported.
- Labels:
  - *supported*;
  - *unsupported:* the span does not entail the value;
  - *span not found:* the span is not in the paper.
- An HPO term more specific than the span justifies counts as unsupported. A less specific (ancestor) term counts as supported.

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

**Secondary audit measures (each needs panel time; see [D-11]):**
- (a) The unsupported rate *before* the gatekeeper, on a separate random sample. This measures what the gatekeeper adds.
- (b) Gatekeeper accuracy against human labels (`huang2024_no_self_correct`, `zheng2023_llm_judge`).
- (c) A false-abstention check: a sample of "not reported" values where the panel checks whether the paper did report the feature.

### 7.2 O2: Concordance with ClinVar and OMIM (primary, estimation)

The matched sets below are built by the harness from the frozen extraction and the dated snapshots.

**Variant matching [proposed].** Extracted variants and reference variants are compared on the same normalized GRCh38 representation (normalized identically on both sides). Matches fall into tiers:
1. exact genomic allele;
2. protein-level only, for papers that give no c. or g. description;
3. unmatched.

The tier is reported for every comparison.

#### 7.2.1 Gene

Share of deduplicated individuals whose recorded causal gene matches the gene OMIM associates with the disease phenotype MIM. Because each corpus is built per disease, this will be near ceiling by design. It is reported, but no weight is placed on it.

#### 7.2.2 Normalized HGVS

The reference pairs are (PMID, variant) pairs from two sources, restricted to corpus PMIDs and pilot genes:
- ClinVar's citation table;
- OMIM allelic-variant references.

Metrics:
- **HGVS concordance (recall form):** the share of reference pairs where the pipeline extracted the same variant (tier 1, and tiers 1+2) from that PMID.
- **Normalization success:** the share of extracted variant strings that VariantValidator normalizes without error, overall and by whether the transcript was stated in the paper.

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
  - the share of terms observed in at least 2 deduplicated individuals [proposed threshold] that match an annotated term.

Reference annotations are known to be incomplete (`connelly2026_fanconi_annotations`), so (b) is descriptive.

#### 7.2.5 Corpus overlap and coverage

Two descriptive numbers:
- the share of corpus PMIDs cited by ClinVar or OMIM for the pilot gene;
- **coverage**, the share of schema fields with an asserted value rather than "not reported", per field.

#### 7.2.6 Discordance triage

ClinVar contains misclassified variants (`wright2021_ddd_clinvar`), and literature nomenclature is often wrong (`lansdon2026_nomenclature_errors`). So:
- The primary concordance figures count **every** miss as discordant.
- A random sample of misses (size set with [D-11]) is then triaged into five categories:
  1. extraction error;
  2. normalization error;
  3. error in the paper (e.g. a typo or legacy numbering);
  4. reference error or ambiguity;
  5. reference citation does not describe the variant.
- The breakdown is secondary and never replaces the primary figure.

**Success criterion (D-03, decided).** The grant gives no numeric concordance threshold, and none is added. Concordance is reported as estimates with 95% CIs, with no pass/fail cut-off, because ClinVar and OMIM are imperfect references (§7.2.6).

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

[proposed] If no suitable comparator is found for a disease by the freeze, the bias arm leaves that disease out and says why.

Candidates from the background bibliography, not yet checked for suitability:

| Disease | Comparator candidates |
|---|---|
| Alexander disease | `mura2021_axd_italian`, `gagliardi2024_axd_ukb` |
| A20 haploinsufficiency | `he2026_ha20_multicenter` (preprint), `aeschlimann2018_ha20_cohort` |
| SSADH deficiency | `dibacco2019_ssadh_natural_history` |
| Danon disease | `boucek2011_danon_natural_history` (cohort part only; it also includes literature cases), `khedro2025_danon_prospective` |
| LAD-I, Tangier | None identified yet |

Most comparators are themselves clinically ascertained, so "cohort truth" is relative. Genotype-first cohorts such as UK Biobank are the closest to unbiased and are reported separately.

#### 7.4.2 Frequency deviation [proposed]

1. For each comparator, a human lists HPO-mappable features and their cohort frequencies **before** literature frequencies are computed.
2. Literature frequency per feature is computed over deduplicated individuals, excluding anyone in the comparator cohort:
   - **primary:** observed ÷ (observed + excluded), i.e. among individuals explicitly assessed;
   - **secondary:** observed ÷ all individuals.
3. Report the per-feature difference (literature minus cohort) and the per-disease mean absolute deviation, with a publication-cluster bootstrap CI. This is where the three-state coding matters (`almail2024_reporting_gaps`).

#### 7.4.3 Memorization probe [proposed]

The probe must work identically on Claude and the open-weight model, so it is black-box only (`grant_claim_checks.md` §15). Per disease, a stratified sample of corpus papers is drawn, split by publication date relative to each model's training cutoff (`roberts2024_lens_of_time`). Two probes:

- **(a) Closed-book recall.** Given only PMID, title and year, the model lists the variants and key phenotypes the paper reports. Overlap is scored against the full-text extraction (not against ClinVar).
- **(b) Guided completion** (`golchin2024_time_travel`). Given the opening of a passage, the model continues it. Overlap with the true text is measured.

Probe scores are compared before vs after the cutoff, adjusting for publication year, because date shift confounds membership signals (`duan2024_mia_llm`). Exploratory: whether audit and concordance results differ between high- and low-memorization papers.

Log-probability probes (`shi2024_mink_prob`) may be run on the open-weight model as a supplement, but are not used for the comparison.

### 7.5 O5: Efficiency and model comparison (secondary)

**Expert time.** The adjudication interface logs active minutes per record. The headline metric is expert-minutes per accepted record, where an accepted record is a gap-variant record approved by the panel. Audit minutes per claim are reported separately.

**Claude vs open-weight model [D-10].** Both models run on the same papers with the same scaffold, prompts, chunking, tools and inputs. If the open-weight model's context window forces smaller chunks, both models use them. No fine-tuning.

Metrics:
- span-not-found rate (all values);
- unsupported rate on a blinded audit sample of equal size for each model;
- HGVS concordance (§7.2.2);
- coverage;
- cost per paper (Claude: API cost; open-weight: compute cost at a stated rate);
- wall-clock time.

Results are published either way. Still to decide: which model, which disease(s), audit size, and where the open-weight model runs. The grant's $2,000 line covers Claude credits only. The comparison also depends on [D-17], because an identical scaffold needs both models to be called the same way.

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
- **No extraction has been run.** No pilot papers have been processed by the pipeline, which does not yet exist.
- **AutoOMIM.** The team has worked with OMIM-style content through the AutoOMIM collaboration, which is why §5.3 excludes it.
- **The grant mentions "our own internal experience"** with Claude's precision. This is not used as evidence here.

## 11. Data, code and licensing

- **Pipeline code** is released open source (`CONTEXT.md` §7).
- **Phenopackets and evidence tables** are released after adjudication. The license is undecided, and so is how verbatim spans from non-open-access papers are handled [D-16].
- **OMIM content** is not redistributed. Storage depends on the licensing route [D-12].
- **ClinVar snapshots** are re-downloadable. The repo holds the download script and manifest, not the files.
- **No patient data** of any kind is used.
- **Acknowledgment.** Every publication that used the award credits acknowledges Anthropic's AI for Science program (award email, 2026-08-31).

## 12. Timeline (relative to Month 1 start [D-01])

| When | Step |
|---|---|
| Month 1 | Resolve [D-nn]; corpus search and screening; reference snapshots and dated counts; freeze and register this plan |
| Month 2 | Development phase on A20 haploinsufficiency → `pipeline-v1.0` → full HA20 run → cost estimate approved → extraction on the other five diseases; audit sample drawn |
| Month 3 | Concordance (O2); audit ratings (O1) |
| Month 4 | Gap-variant adjudication (O3); efficiency logging (O5) |
| Month 5 | Submissions after sign-off; bias arm and memorization probe (O4); model comparison |
| Month 6 | Write-up; all results published whether favorable or not |

## 13. Decisions needed before freezing

See `DECISIONS.md` → *Open decisions*. Still blocking this plan: D-01, D-08 to D-12, and D-17. D-02 to D-07 were decided on 2026-10-18. D-13 to D-16 can follow, but D-13 should be settled before Month-4 adjudication begins.
