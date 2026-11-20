# Notes for the writers of version 4

## What this document is
- Version 4 of the GP-RareLink interim report, for internal review by the team, collaborators and the
  funder (Anthropic's AI for Science program, Rare Disease track). It is not a journal submission; the
  ICLR style files are used for layout only. It supersedes version 2 (full report, 2026-10-28, six
  diseases) and version 3 (eight-page highlights, 2026-11-02).
- It is written now, before the human ratings are in. Every human result is a placeholder
  `\HR{<id>}` (see `pending_human_results.md`). The report must be useful today: what was built,
  what was measured automatically, what people are now doing, and exactly which numbers are pending.
- Audience: clinicians and curators want provenance and denominators; program staff want progress
  against the pre-registered outcomes and spend; a methods reader wants the evaluation design.

## Claims you must not make
- No human result, estimate or direction (O1, O2 triage, O3 adjudication, O4, O5 minutes,
  calibration outcomes). Only `\HR{...}`.
- Do not present the gatekeeper's removal rate as the error rate. Do not present pilot results as
  general findings. Do not say any variant has been or will be submitted: submissions wait on the
  adjudication panel's approval and the PI's sign-off.
- Do not describe the extension five or Majeed as part of the registered study: the registered study
  is the six diseases; the extension is a recorded deviation (D-52); Majeed is exploratory.
- Do not merge the corpus addendum (D-47) into registered figures; report it beside them.
- Do not mention the SLIDERS ablation study (the PI decided it is not additive or conclusive).
- Do not name raters or describe any individual rater. Do not say which kind of claim was capped in
  the calibration set, or the cap's size.
- Do not quote papers verbatim (licensing, D-51).
- Do not repeat the grant application's figures that later checks corrected (see below).

## Grant claims to use only in corrected form (from background/grant_claim_checks.md, checked 2026-10-16)
- phenopacket-store: not "408 cohorts". 731 gene cohort folders and 10,782 phenopacket files at
  repository commit 85ffd78 (2026-10-07); none of the twelve genes has a folder.
- Tangier disease: about 100–150 published patients (Koseki 2021 counts about 144; GeneReviews says
  fewer than 100), not about 200.
- Danon disease: about 100 families; at least 146 molecularly confirmed patients.
- Alexander disease: 550 patients and 182 causative variants, from the Results section of Grossi 2024.
- LAD-I: 323 cases with genotype for 139, as of 2017.
- HA20: 177 patients, literature to August 2023.
- Claude's HPO precision (97.6%, Larsen et al. 2026): four synthetic clinical notes, tool-augmented
  condition (80.7% without tools), recall 65.3%, not case reports; Claude was not top on precision or F1.
- "DRBench" fabricated-citation figures: they are hallucinated-URL rates from Rao, Wong &
  Callison-Burch 2026 for two search-augmented Claude models, not a general fabrication rate.
- An unfavourable result to keep in related work: Claude Sonnet 4 had the lowest exact-count
  concordance (73.0%) of five models at counting probands from genomics papers (Murugan et al. 2026).

## Design points from the literature check (cite the keys given)
- What 250 claims can certify: with 0 unsupported the exact two-sided 95% upper bound is 1.46%; with
  1 it is 2.21%; with 2 it is 2.86% (`audit_ci_250.py`). The pre-registered rule C counts at most 4 of
  250 as meeting the target on the point estimate; the log gives the frozen wording.
- Reference databases are imperfect ground truth: ClinVar holds misclassified variants
  (wright2021_ddd_clinvar) and phenotype annotations are incomplete (connelly2026_fanconi_annotations),
  so ClinVar misses are triaged by people, not all counted as extraction errors.
- LLM self-checking and judging have known biases (huang2024_no_self_correct, zheng2023_llm_judge);
  the gatekeeper checks strictly against the verbatim span (rashkin2023_ais) and is evaluated against
  human labels.

## References
- `extra_references.bib` holds the project's own checked reference list (background/manifest.csv,
  128 entries with a PMID, DOI or arXiv id). Prefer these keys. What each one is about is listed below
  (the "relevance" notes written when the list was checked); describe a reference no further than this.

- `joshi2026_sliders` (methods; 2026) SLIDERS: Systematic Reviews via Automated Evidence Synthesis and Reconciliation. The project's extraction method: question-specific evidence tables with verbatim excerpts as provenance, plus a code-writing reconciliation agent that merges and de-conflicts extractions.
- `shao2024_storm` (methods; 2024) Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models. STORM, the Lam lab's retrieval-grounded long-form synthesis system and the engine behind the RGI-OVAL OpenRare collaboration.
- `semnani2023_wikichat` (methods; 2023) WikiChat: Stopping the Hallucination of Large Language Model Chatbots by Few-Shot Grounding on Wikipedia. Lam lab's grounding-plus-claim-verification design; precedent for the gatekeeper pass.
- `larsen2026_hpo_mcp` (methods; 2026) Extraction of Human Phenotype Ontology (HPO) Concepts from Clinical Notes Utilizing LLMs with Model Context Protocol (MCP). Source of the grant's 97.6% Sonnet 4.5 HPO precision (Table 1, tool-augmented, 4 synthetic clinical notes; recall 65.3%). HPO lookup via MCP is reusable for HPO grounding.
- `garcia2025_raghpo` (methods; 2025) Improving automated deep phenotyping through large language models using retrieval-augmented generation. RAG-HPO benchmarked on 112 published case reports (our input type); best F1 0.78 with Llama-3.1-70B. Ready open-weight HPO baseline.
- `groza2024_gpt_hpo` (methods; 2024) An evaluation of GPT models for phenotype concept recognition. Monarch-group evaluation: GPT-4 HPO recognition was non-deterministic and needed in-context HPO labels. Supports repeat runs and ontology grounding.
- `yang2024_phenogpt` (methods; 2024) Enhancing phenotype recognition in clinical notes using large language models: PhenoBCBERT and PhenoGPT. Fine-tuned LLM HPO recognizer; possible comparator.
- `luo2021_phenotagger` (methods; 2021) PhenoTagger: a hybrid method for phenotype concept recognition using human phenotype ontology. Standard pre-LLM HPO tagger baseline.
- `shyr2026_rarephenix` (methods; 2026) An AI framework for end-to-end rare disease phenotyping from clinical notes using large language models. RARE-PHENIX: chained extraction, HPO standardization and prioritization; recent pipeline comparator (clinical notes, not literature).
- `caufield2024_spires` (methods; 2024) Structured prompt interrogation and recursive extraction of semantics (SPIRES): a method for populating knowledge bases using zero-shot learning. OntoGPT/SPIRES: schema-driven LLM extraction grounded to HPO and Mondo; closest Monarch-stack prior art for filling phenopacket fields.
- `reese2026_llm_vs_exomiser` (methods; 2026) Systematic benchmarking demonstrates large language models have not reached the diagnostic accuracy of traditional rare-disease decision support tools. LLMs run on ~5,200 phenopacket-derived cases from the literature (o1-preview top-1 23.6% vs Exomiser 35.5%). Shows phenopackets as evaluation currency and a memorization risk.
- `nguyen2026_llm_rd_metaanalysis` (methods; 2026) Diagnostic Accuracy of Large Language Models for Rare Diseases: A Systematic Review and Meta-Analysis. All 19 system-dataset pairs rated high risk of bias, mainly from data leakage: direct support for the memorization probe.
- `wei2022_tmvar3` (methods; 2022) tmVar 3.0: an improved variant concept recognition and normalization tool. Standard variant recognizer/normalizer; baseline for HGVS extraction recall.
- `allot2023_litvar2` (methods; 2023) Tracking genetic variants in the biomedical literature using LitVar 2.0. Variant-to-paper index (~15M variants) useful for corpus building. It links to ClinVar, so keep it out of the extraction step.
- `birgmeier2020_avada` (methods; 2020) AVADA: toward automated pathogenic variant evidence retrieval directly from the full-text literature. Full-text variant retrieval recovered 59% of HGMD disease-causing variants; reports >60,000 likely disease-causing HGMD variants absent from ClinVar. Best prior estimate of the gap.
- `wang2025_pubmind` (methods; 2025) PubMind: Literature-Based Genetic Variant Extraction and Functional Annotation Using LLMs. LLM (Llama-3.3-70B) variant extraction at PubMed/PMC scale; ~10% of mapped variants overlap ClinVar. Closest analogue to our concordance question.
- `li2025_autopm3` (methods; 2025) AutoPM3: enhancing variant interpretation via LLM-driven PM3 evidence extraction from scientific literature. Text2SQL over tables plus RAG over text for ACMG PM3 evidence; flags supplementary tables as a hard case for variant extraction.
- `murugan2026_reasoning_llm_ps4` (methods; 2026) Performance Characteristics of Reasoning LLMs for Evidence Extraction from Clinical Genomics Literature. Unfavourable for Claude: on counting probands (PS4), Claude Sonnet 4 had the lowest exact-count concordance (73.0% vs 91.1% best) and lowest stability. Closely related to our proband dedup and counting.
- `saadat2026_functional_evidence` (methods; 2026) Large Language Models for Variant-Centric Functional Evidence Mining. ClinGen-derived benchmark for LLM functional-evidence mining with a curator-assist pipeline; no Claude tested.
- `ma2026_aicura` (methods; 2026) AI-CURA, an automated LLM workflow for high-accuracy genetic variant classification. Peer-reviewed precedent for LLM literature-evidence variant classification, including reanalysis of ClinVar conflicting variants.
- `gartlehner2024_llm_extraction` (methods; 2024) Data extraction for evidence synthesis using a large language model: a proof-of-concept study. Claude 2 reached 96.3% accuracy on 160 data elements from 10 RCTs: earliest Claude-specific SR-extraction evidence (small sample).
- `kataoka2025_gpt4o_o3_extraction` (methods; 2025) Automating the data extraction process for systematic reviews using GPT-4o and o3. o3 ~75% accuracy; numeric fields worse than text. A warning for extracting ages, counts and variant positions.
- `cao2025_ottosr` (methods; 2025) Automation of Systematic Reviews with Large Language Models. otto-SR end-to-end SR automation (93.1% extraction accuracy vs 79.7% human workflow); main comparator to SLIDERS.
- `rao2026_reference_hallucination` (methods; 2026) Detecting and Correcting Reference Hallucinations in Commercial LLMs and Deep Research Agents. Actual source of the grant's 'DRBench 3.0%/3.2%' figures (hallucinated-URL rates for search-augmented Claude 3.5/3.7 Sonnet). See grant_claim_checks.md.
- `du2025_deepresearchbench` (methods; 2025) DeepResearch Bench: A Comprehensive Benchmark for Deep Research Agents. The 100-task benchmark whose agent outputs Rao et al. analysed.
- `jackson2025_aa_omniscience` (methods; 2025) AA-Omniscience: Evaluating Cross-Domain Knowledge Reliability in Large Language Models. Knowledge/hallucination benchmark that rewards abstention. The grant's Opus figure comes from a later Artificial Analysis page; see grant_claim_checks.md.
- `jacobsen2022_phenopacket_schema` (standards; 2022) The GA4GH Phenopacket schema defines a computable representation of clinical data. The v2 output schema every extracted record must follow.
- `ladewig2023_phenopackets_primer` (standards; 2023) GA4GH Phenopackets: A Practical Introduction. Practical guide for designing the extraction schema around phenopacket fields.
- `danis2023_phenopacket_tools` (standards; 2023) Phenopacket-tools: Building and validating GA4GH Phenopackets. Citable paper for phenopacket validation (there is no dedicated pyphetools/CohortValidator paper).
- `danis2025_phenopacket_store` (standards; 2025) A corpus of GA4GH phenopackets: case-level phenotyping for genomic diagnostics and discovery. phenopacket-store resource paper (v0.1.19: 6,668 phenopackets, 959 publications), hand-curated with pyphetools. Prior art, possible human-curated reference, and a memorization risk.
- `rekerle2026_gpsea` (standards; 2026) GA4GH phenopacket-driven characterization of genotype-phenotype correlations in Mendelian disorders. GPSEA: statistical genotype-phenotype testing on phenopacket cohorts. Ready-made engine for the per-gene genotype-phenotype maps.
- `gargano2024_hpo` (standards; 2024) The Human Phenotype Ontology in 2024: phenotypes around the world. Current HPO citation; the vocabulary for three-state phenotype coding.
- `vasilevsky2025_mondo` (standards; 2025) Mondo: integrating disease terminology across communities. First peer-reviewed Mondo paper; Mondo IDs are our primary disease identifiers.
- `lucano2026_orphanet` (standards; 2026) The Orphanet Nomenclature and Classification of rare diseases: a standard terminology for improved patient recognition and data interoperability. Most recent Orphanet description; for ORPHA cross-references.
- `rath2012_orphanet` (standards; 2012) Representation of rare diseases in health information systems: the Orphanet approach to serve a wide range of end users. Older peer-reviewed Orphanet citation, if a published reference is required.
- `freeman2018_variantvalidator` (standards; 2018) VariantValidator: Accurate validation, mapping, and formatting of sequence variation descriptions. The HGVS normalization tool in the pipeline.
- `freeman2024_vv_literature` (standards; 2024) Standardizing variant naming in literature with VariantValidator to increase diagnostic rates. Directly supports our premise: non-standard variant names in papers hide evidence from databases.
- `dendunnen2016_hgvs` (standards; 2016) HGVS Recommendations for the Description of Sequence Variants: 2016 Update. Baseline HGVS nomenclature citation.
- `hart2024_hgvs2024` (standards; 2024) HGVS Nomenclature 2024: improvements to community engagement, usability, and computability. Current HGVS version; cite alongside den Dunnen 2016.
- `morales2022_mane` (standards; 2022) A joint NCBI and EMBL-EBI transcript set for clinical genomics and research. MANE Select: the transcript set we state for every HGVS string.
- `lansdon2026_nomenclature_errors` (standards; 2026) Universal presence of gene/variant nomenclature errors in journal manuscript submissions. All 52 audited Genetics in Medicine submissions had nomenclature errors; justifies keeping the original string next to the normalized one.
- `landrum2025_clinvar` (standards; 2025) ClinVar: updates to support classifications of both germline and somatic variants. Latest ClinVar paper; ground truth and submission target.
- `amberger2019_omim` (standards; 2019) OMIM.org: leveraging knowledge across phenotype-gene relationships. Most recent OMIM NAR paper; ground truth for allelic variants.
- `hamosh2021_omim` (standards; 2021) Online Mendelian Inheritance in Man (OMIM): Victor McKusick's magnum opus. Newer OMIM overview, optional companion to Amberger 2019.
- `putman2024_monarch` (standards; 2024) The Monarch Initiative in 2024: an analytic platform integrating phenotypes, genes and diseases across species. Latest Monarch paper; Monarch hosts phenopacket-store and is an outreach target.
- `philippakis2015_mme` (standards; 2015) The Matchmaker Exchange: a platform for rare disease gene discovery. Matchmaker Exchange background, cited in the impact statement.
- `richards2015_acmg` (standards; 2015) Standards and guidelines for the interpretation of sequence variants: a joint consensus recommendation of the ACMG and AMP. Classification framework for the adjudication panel.
- `biesecker2024_clingen_pp1_pp4` (standards; 2024) ClinGen guidance for use of the PP1/BS4 co-segregation and PP4 phenotype specificity criteria for sequence variant pathogenicity classification. How segregation and phenotype-specificity evidence from case reports should be weighed at adjudication.
- `yang2017_clinvar_discordance` (standards; 2017) Sources of discordance among germ-line variant classifications in ClinVar. Literature-only entries were 8.8% of submissions but 31.4% of outlier classifications: key caution for our submissions.
- `wright2021_ddd_clinvar` (standards; 2021) Evaluating variants classified as pathogenic in ClinVar in the DDD Study. ClinVar is an imperfect ground truth; matters for interpreting discordance.
- `harrison2017_clinvar_conflicts` (standards; 2017) Clinical laboratories collaborate to resolve differences in variant interpretations submitted to ClinVar. Background on reconciling conflicting classifications.
- `grossi2024_axd_meta` (diseases; 2024) A systematic review and meta-analysis of GFAP gene variants in Alexander disease. Source of the grant's 550 patients / 182 variants (Results section). Most complete patient-level GFAP catalogue; benchmark for extraction completeness.
- `prust2011_axd_onset` (diseases; 2011) GFAP mutations, age at onset, and clinical subtypes in Alexander disease. 30 new plus 185 published cases; defines Type I/II. Standard genotype-phenotype reference.
- `messing2025_axd_14variants` (diseases; 2025) Genotype-phenotype association for 14 GFAP variants in Alexander disease. Per-variant onset and survival across 231 cases; variant-level concordance check.
- `mura2021_axd_italian` (diseases; 2021) Alexander disease evolution over time: data from an Italian cohort of pediatric-onset patients. Longitudinal cohort (21 patients): natural-history comparator for the bias arm.
- `gagliardi2024_axd_ukb` (diseases; 2024) Analysis of GFAP variants in UK Biobank suggests underdiagnosis or incomplete penetrance of adult-onset Alexander disease. Genotype-first comparator: 106 P/LP GFAP carriers in ~470,000 UK Biobank exomes, milder/under-recognized phenotypes. Directly relevant to the ascertainment-bias arm.
- `genereviews_axd` (diseases; 2020) Alexander Disease (GeneReviews; posted 2002, updated 12 Nov 2020). Clinical reference for phenotype vocabulary and diagnostic criteria.
- `almarzanovoa2018_lad1_review` (diseases; 2018) Leukocyte adhesion deficiency-I: a comprehensive review of all published cases. Source of 323 cases / 139 genotyped. Gives denominators for genotype completeness and severity-specific survival; 10 duplicate-reported cases are a ready dedup test.
- `kambli2020_lad_india` (diseases; 2020) Clinical and genetic spectrum of a large cohort of patients with leukocyte adhesion deficiency type 1 and 3: a multicentric study from India. 127 LAD-I patients, 57 ITGB2 variants (35 novel), published after the 2018 review: tests whether extraction picks up newer literature.
- `qasim2009_lad_hsct` (diseases; 2009) Allogeneic hematopoietic stem-cell transplantation for leukocyte adhesion deficiency. Outcomes for 36 transplanted children.
- `booth2025_lad_gene_therapy` (diseases; 2025) Lentiviral gene therapy for severe leukocyte adhesion deficiency type 1. Current treatment context.
- `elhani2024_ha20_177` (diseases; 2024) A20 haploinsufficiency: a systematic review of 177 cases. Source of 177 patients (65 articles, PRISMA); per-phenotype counts are the literature baseline for the bias arm.
- `zhou2016_ha20_original` (diseases; 2016) Loss-of-function mutations in TNFAIP3 leading to A20 haploinsufficiency cause an early-onset autoinflammatory disease. Original description of HA20.
- `aeschlimann2018_ha20_cohort` (diseases; 2018) A20 haploinsufficiency (HA20): clinical phenotypes and disease course of patients with a newly recognised NF-kB-mediated autoinflammatory disease. 16 patients from 7 families followed over time.
- `li2026_ha20_howitreat` (diseases; 2026) How I treat: haploinsufficiency of A20. Current review: ~200 reported cases, ~100 pathogenic variants.
- `he2026_ha20_multicenter` (diseases; 2026) Multicenter international cohort study of HA20 reveals novel genetic architecture and phenotypic evolution. 185-patient Chinese/US cohort: largest cohort comparator for the bias arm.
- `genereviews_ha20` (diseases; 2024) Haploinsufficiency of A20 (GeneReviews; posted 19 Dec 2024). Clinical reference; reports >180 individuals from 97 families.
- `didiasova2020_ssadh_update` (diseases; 2020) Succinic semialdehyde dehydrogenase deficiency: an update. Source of the ~450 published patients figure.
- `dibacco2019_ssadh_natural_history` (diseases; 2019) Age-related phenotype and biomarker changes in SSADH deficiency. Registry of 133 patients (49 longitudinal): main cohort comparator for the bias arm.
- `tokatlylatzer2023_ssadh_genotype` (diseases; 2023) Phenotypic correlates of structural and functional protein impairments resultant from ALDH5A1 variants. 58 patients, 32 variants: genotype-phenotype reference.
- `tokatlylatzer2024_ssadh_guidelines` (diseases; 2024) Consensus guidelines for the diagnosis and management of succinic semialdehyde dehydrogenase deficiency. Current consensus reference.
- `pearl2003_ssadh_series` (diseases; 2003) Succinic semialdehyde dehydrogenase deficiency in children and adults. Early case series.
- `genereviews_ssadh` (diseases; 2025) Succinic Semialdehyde Dehydrogenase Deficiency (GeneReviews; posted 2004, updated 9 Jan 2025). Clinical reference; states at least 450 individuals reported.
- `boucek2011_danon_natural_history` (diseases; 2011) Natural history of Danon disease. 82 patients from 36 families plus 63 literature cases; documents male/female severity difference.
- `brambatti2019_danon_gender` (diseases; 2019) Danon disease: gender differences in presentation and outcomes. 146 patients from 83 papers; median age at composite outcome 21 (male) vs 38 (female). Target structure the extraction must reproduce.
- `cenacchi2020_danon_review` (diseases; 2020) Danon disease: review of natural history and recent advances. Survey of >500 reported patients.
- `sugie2024_danon_history` (diseases; 2024) History and perspective of LAMP-2 deficiency (Danon disease). States about 100 families worldwide (closest source for the grant's '>100 families').
- `sugie2018_danon_japan` (diseases; 2018) [Japanese nationwide survey of Danon disease; exact title not confirmed]. National survey cohort; possible comparator.
- `khedro2025_danon_prospective` (diseases; 2025) Danon disease in male patients: a prospective natural history study. Prospective natural history (9 males).
- `genereviews_danon` (diseases; 2024) Danon Disease (GeneReviews; posted 2020, revised 23 May 2024). Clinical reference.
- `koseki2021_tangier_review` (diseases; 2021) Current diagnosis and management of Tangier disease. Counts ~144 reported cases (35 Japan, 109 elsewhere); contradicts the grant's ~200.
- `puntoni2012_tangier` (diseases; 2012) Tangier disease: epidemiology, pathophysiology, and management. Review.
- `mercan2018_tangier_neuropathy` (diseases; 2018) Peripheral neuropathy in Tangier disease: a literature review and assessment. Literature review of 54 neuropathy cases.
- `schaefer2016_hdl_deficiency` (diseases; 2016) Diagnosis and treatment of high density lipoprotein deficiency. Cardiovascular disease rates by age.
- `genereviews_tangier` (diseases; 2019) Tangier Disease (GeneReviews; posted 21 Nov 2019). Clinical reference; states fewer than 100 cases published.
- `wouters2014_blau` (diseases; 2014) Blau syndrome, the prototypic auto-inflammatory granulomatous disease. Key Blau syndrome (NOD2) review.
- `rose2015_blau_cohort` (diseases; 2015) Blau syndrome: cross-sectional data from a multicentre study of clinical, radiological and functional outcomes. Blau prospective cohort comparator.
- `ferguson2021_majeed` (diseases; 2021) Majeed Syndrome: A Review of the Clinical, Genetic and Immunologic Features. Key Majeed syndrome (LPIN2) review.
- `vitali2022_lcat` (diseases; 2022) A systematic review of the natural history and biomarkers of primary LCAT deficiency. 146 FLD + 53 fish-eye disease patients; LCAT literature/natural-history baseline.
- `stockleripsiroglu2014_gamt` (diseases; 2014) Guanidinoacetate methyltransferase (GAMT) deficiency: outcomes in 48 individuals and recommendations for diagnosis, treatment and monitoring. GAMT outcomes series; GeneReviews: Creatine Deficiency Disorders NBK3794 (PMID 20301745).
- `beyens2018_ats` (diseases; 2018) Arterial tortuosity syndrome: 40 new families and literature review. Key arterial tortuosity syndrome (SLC2A10) review.
- `hajialigol2022_papa` (diseases; 2022) Systematic review of PAPA and PAPA-like syndromes. 93 PAPA patients (PSTPIP1); see also Wang Y et al., Front Immunol 2021;12:735851 (PMID 34745107).
- `almail2024_reporting_gaps` (bias; 2024) Consensus reporting guidelines to address gaps in descriptions of ultra-rare genetic conditions. Phenotype detail was superficial or absent in most first reports: case-report phenotype spectra are incomplete, so 'not reported' must stay separate from 'excluded'.
- `vandersluijs2019_arid1b` (bias; 2019) The ARID1B spectrum in 143 patients: from nonsyndromic intellectual disability to Coffin-Siris syndrome. Worked example of ascertainment-driven spectrum differences; notes forms without an explicit 'absent' option undercount features.
- `wright2024_penetrance` (bias; 2024) Guidance for estimating penetrance of monogenic disease-causing variants in population cohorts. Framework for why phenotype-first (literature) cohorts overstate severity and penetrance versus genotype-first cohorts.
- `felker2025_allofus_genotype_first` (bias; 2025) Genotype-first assessment of presentation and penetrance of NF1, ADPKD, and Marfan syndrome within the All of Us Research Program cohort. Model design for comparing literature spectra with a genotype-first cohort.
- `connelly2026_fanconi_annotations` (bias; 2026) A custom phenotypic profile for Fanconi anemia: addressing gaps in existing disease annotations. OMIM and Orphanet share few HPO terms for one disease: reference annotations are incomplete, so not every concordance gap is an extraction error.
- `shi2024_mink_prob` (bias; 2024) Detecting Pretraining Data from Large Language Models. Min-K% Prob membership test. Needs token log-probabilities, so usable on the open-weight model but not on Claude: an asymmetry to design around.
- `duan2024_mia_llm` (bias; 2024) Do Membership Inference Attacks Work on Large Language Models?. Caution: apparent membership signals often reflect date shift. The memorization probe must control for publication date.
- `golchin2024_time_travel` (bias; 2024) Time Travel in LLMs: Tracing Data Contamination in Large Language Models. Black-box guided-completion probe; adaptable to Claude and the open-weight model identically.
- `roberts2024_lens_of_time` (bias; 2024) Data Contamination Through the Lens of Time. Uses training cutoffs as a natural experiment: supports a pre- vs post-cutoff case-report split.
- `xu2024_contamination_survey` (bias; 2024) Benchmark Data Contamination of Large Language Models: A Survey. Survey for justifying the choice of probe.
- `white2025_livebench` (bias; 2025) LiveBench: A Challenging, Contamination-Limited LLM Benchmark. Precedent for refreshed post-cutoff evaluation items.
- `li2026_medical_memorization` (bias; 2026) Memorization in large language models in medicine: prevalence, characteristics, and implications. Main biomedical memorization study.
- `rashkin2023_ais` (bias; 2023) Measuring Attribution in Natural Language Generation Models. AIS framework: a formal definition of 'supported by the cited span', the gatekeeper's audit criterion.
- `gao2023_alce` (bias; 2023) Enabling Large Language Models to Generate Text with Citations. Citation recall/precision metrics automatable with NLI or LLM judges.
- `min2023_factscore` (bias; 2023) FActScore: Fine-grained Atomic Evaluation of Factual Precision in Long Form Text Generation. Atomic-claim checking maps onto the 250-claim audit unit (one claim per extracted value).
- `gero2023_self_verification` (bias; 2023) Self-Verification Improves Few-Shot Clinical Information Extraction. Closest prior design to the gatekeeper: the LLM cites evidence spans for its extractions, then verifies them.
- `dhuliawala2024_cove` (bias; 2024) Chain-of-Verification Reduces Hallucination in Large Language Models. Verification-question pattern usable inside the gatekeeper.
- `huang2024_no_self_correct` (bias; 2024) Large Language Models Cannot Self-Correct Reasoning Yet. Counter-evidence: ungrounded self-correction can hurt. The gatekeeper should check against the verbatim span, and be calibrated against human labels.
- `chung2025_verifact` (bias; 2025) VeriFact: Verifying Facts in LLM-Generated Clinical Text with Electronic Health Records. Template for validating an LLM claim-checker against clinician labels.
- `wu2025_sourcecheckup` (bias; 2025) An automated framework for assessing how well LLMs cite relevant medical references. Biomedical evidence that LLM citations often don't support the statements they're attached to.
- `zheng2023_llm_judge` (bias; 2023) Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. Documents self-enhancement bias: relevant when Claude audits Claude; consider cross-model or human-calibrated auditing.
- `croxford2025_clinical_llm_judge` (bias; 2025) Evaluating clinical AI summaries with large language models as judges. Clinical LLM-as-judge validated against a human instrument.
- `brown2001_binomial_ci` (bias; 2001) Interval Estimation for a Binomial Proportion. Use Wilson/Jeffreys intervals, not Wald, for the <2% unsupported-value rate.
- `hanley1983_zero_numerators` (bias; 1983) If nothing goes wrong, is everything all right? Interpreting zero numerators. Rule of three: 0 errors in 250 claims gives a 95% upper bound of ~1.2%. Sets what the 250-claim audit can and cannot certify.
- `newman1995_small_numerators` (bias; 1995) If almost nothing goes wrong, is almost everything all right? Interpreting small numerators. Extends the rule of three to small non-zero error counts.
- `chen2025_bionlp_benchmark` (bias; 2025) Benchmarking large language models for biomedical natural language processing applications and recommendations. Closed vs open models across 12 biomedical NLP benchmarks; key prior result for the head-to-head.
- `yin2025_llm_disease_genes` (bias; 2025) Can large language models reliably extract human disease genes from full-text scientific literature?. Task closest to ours: GPT-4o vs Claude Opus 4 vs DeepSeek-V3 extracting gene/disease/phenotype from full text; disease and phenotype fields error-prone for all.
- `dorfner2024_open_vs_commercial_radiology` (bias; 2024) Comparing commercial and open-source large language models for labeling chest radiograph reports. Gap closes under few-shot prompting with the same setup: supports the identical-scaffold rule.
- `zhang2024_open_vs_commercial_summarization` (bias; 2024) Closing the gap between open source and commercial large language models for medical evidence summarization. Fine-tuning narrows the gap; context if the open-weight arm is fine-tuned (it shouldn't be, under an identical scaffold).
- `stachura2025_open_weight_bioasq` (bias; 2025) Are smaller open-weight LLMs closing the gap to proprietary models for biomedical question answering?. Recent QA comparison including Claude 3.5/3.7.
- `konig2019_registry_dedup` (bias; 2019) De-duplicating patient records from three independent data sources reveals the incidence of rare neuromuscular disorders in Germany. Record-linkage deduplication across rare-disease sources (registries, not publications).
- `shivakumar2026_cohort_reliance` (bias; 2026) Addressing cohort reliance in rare diseases literature: a scoping review of myositis research. A few cohorts reused across many papers: supports explicit cross-paper patient deduplication.
- `wang2025_blau_review` (diseases; 2025) Blau Syndrome (Juvenile Systemic Granulomatosis): State-Of-The-Art Review. Blau syndrome state-of-the-art review; key review for the extension (D-47).
- `biagiotti2025_gamt_review` (diseases; 2025) GAMT Deficiency: Clinical Presentation, Treatment, Diagnosis, Animal Models, Preclinical and Clinical Developments. GAMT deficiency review; key review for the extension (D-47).
- `genovese2020_papa_spectrum` (diseases; 2020) PAPA spectrum disorders. PAPA-spectrum disorders review; key review for the extension (D-47).
- `satoh2024_pg_genetics` (diseases; 2024) Genetic mutations in pyoderma gangrenosum, hidradenitis suppurativa, and associated autoinflammatory syndromes: Insights into pathogenic mechanisms and shared pathways. Review of genetic variants in pyoderma gangrenosum and associated autoinflammatory syndromes incl. PAPA; key review for the extension (D-47).
