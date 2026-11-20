# GP-RareLink experimental log for interim paper version 4

*Compiled 2026-11-20 from committed, script-generated sources in the repository. It is the only source of numbers for paper version 4. Every block ends with its source in brackets. Numbers are copied as the source prints them (denominators, intervals and dates included); where this log adds two numbers it says "plain sum". Where two sources disagree, the later one is used and the older one is named as superseded. Papers are cited by PMID, not by author. No human rating of any frozen-pipeline output exists yet; results that wait on people are listed in the final section and must be written as `\HR{<id>}`.*

**Short names used below.** HA20 = A20 haploinsufficiency; AxD = Alexander disease; LAD-I = leukocyte adhesion deficiency type I; SSADH = SSADH deficiency; Danon = Danon disease; Tangier = Tangier disease; Blau = Blau syndrome; LCAT = familial LCAT deficiency; GAMT = GAMT deficiency; ATS = arterial tortuosity syndrome; PAPA = PAPA syndrome; Majeed = Majeed syndrome. "Registered six" = the six diseases of the frozen pre-registration. "Extension five" = the five reserve diseases run under the extension addendum (D-52). "Gatekeeper" = gatekeeper v4, a second Claude read of every model claim. "Unsupported" in gatekeeper figures counts the verdicts *unsupported* and *span not found*; "not fully supported" adds *partially supported*. P/LP = pathogenic or likely pathogenic; VUS = variant of uncertain significance.

**Run names.** `pv1-<d>` = registered run (six-disease run, 2026-10-20) or extension run (2026-11-14/15); `pv1-<d>-repeat` = 10% repeat; `pv1a-<d>` = corpus addendum batch 1; `pv1a2-<d>` = corpus addendum batch 2; `pv1s-majeed` = Majeed exploratory run; `ow-<d>` = open-weight run; `poc-ha20-*` = development pilot before the freeze. [consolidated_runs_2026-11-15.md §1, §5]

---

## 1. Setup

### 1.1 Project, team and question

- GP-RareLink is a six-month project of the Rare Genomics Institute (RGI) and the Stanford Open Virtual Assistant Lab (OVAL), funded by Anthropic's AI for Science program (Rare Disease program, basic science track). PI: Dr. Jimmy Lin. Methods co-lead: Prof. Monica Lam (Stanford OVAL; SLIDERS is from her lab). [CONTEXT.md §3]
- Award: $45,000 (the full request) in claude.ai usage credits, award email dated 2026-08-31. Month 1 starts provisionally on 2026-09-21 (the scheduled date of the first deposit; D-01); Month 6 ends 2027-03-20. [CONTEXT.md Award box, §8; DECISIONS.md D-01]
- Research question: can the SLIDERS method (arXiv 2604.22294), powered by Claude, build consolidated variant ↔ phenotype ↔ disease records from published case reports, at an accuracy that can be proven and at a scale that materially closes the gap between the literature and ClinVar/OMIM? [CONTEXT.md §2]
- How SLIDERS is used: SLIDERS assembles evidence tables from documents, keeps full-text excerpts as direct evidence and provenance, and reconciles evidence across documents with a code-writing agent. The project runs a home-built version of the method with Claude Code helper agents (D-20), not the public SLIDERS code; the public code, pinned and adapted to Claude, is kept for later. This fallback is allowed by the pilot design if reported as such. [CONTEXT.md §5; DECISIONS.md D-20]
- Five pre-registered outcomes. O1: unsupported-value rate in a human audit of 250 claims (primary, confirmatory; the only outcome with a pass/fail rule). O2: concordance with ClinVar and OMIM on gene, HGVS, classification and phenotype (primary, estimation; no threshold, D-03). O3: gap closure, variants absent from both databases, adjudicated and submitted (primary, descriptive). O4: ascertainment bias against natural-history cohorts, with a memorization probe (secondary). O5: efficiency (expert-minutes per accepted record) and Claude vs an open-weight model (secondary). [interim_paper.md §1 Table 1]
- Headline pooled figures for the registered six use the five diseases other than HA20, because HA20 was the development disease on which every extraction rule was tuned (D-18); figures that include HA20 are secondary. [interim_paper.md §1; DECISIONS.md D-18]

### 1.2 The twelve diseases

| Disease (gene) | Standing | Inheritance | OMIM phenotype | Mondo | MANE Select used |
|---|---|---|---|---|---|
| A20 haploinsufficiency (*TNFAIP3*) | registered; development disease | AD | 616744 | MONDO:0800045 | NM_001270508.2 |
| SSADH deficiency (*ALDH5A1*) | registered | AR | 271980 | MONDO:0010083 | NM_001080.3 |
| Tangier disease (*ABCA1*) | registered | AR | 205400 | MONDO:0008783 | NM_005502.4 |
| Leukocyte adhesion deficiency I (*ITGB2*) | registered | AR | 116920 | MONDO:0007293 | NM_000211.5 |
| Alexander disease (*GFAP*) | registered | AD / de novo | 203450 | MONDO:0008752 | NM_002055.5 |
| Danon disease (*LAMP2*) | registered | X-linked dominant | 300257 | MONDO:0010281 | NM_002294.3 |
| Blau syndrome (*NOD2*) | reserve; extension (D-52) | AD | 186580; 609464 | MONDO:0008523 | NM_001370466.1 |
| Familial LCAT deficiency (*LCAT*) | reserve; extension (D-52) | AR | 245900; 136120 | MONDO:0018999 | not stated in the reports read |
| GAMT deficiency (*GAMT*) | reserve; extension (D-52) | AR | 612736 | MONDO:0012999 | not stated in the reports read |
| Arterial tortuosity syndrome (*SLC2A10*) | reserve; extension (D-52) | AR | 208050 | MONDO:0008818 | not stated in the reports read |
| PAPA syndrome (*PSTPIP1*) | reserve; extension (D-52) | AD | 604416 | MONDO:0011462 | not stated in the reports read |
| Majeed syndrome (*LPIN2*) | reserve; exploratory run outside the extension (D-54) | AR | 609628 | MONDO:0012316 | NM_001375808.2 |

- The registered six span four inheritance modes and six organ systems (auto-inflammatory, neurometabolic, lipid metabolism, immunology, neurology, cardiac/neuromuscular). [CONTEXT.md §4; interim_paper.md §2.1 Table 2]
- Scope choices for the extension: Blau counts only patients with Blau syndrome or early-onset sarcoidosis (NOD2 in Crohn disease or common-disease association studies is out of scope); LCAT includes complete and partial deficiency (Norum disease and fish-eye disease); PAPA includes the PSTPIP1-associated inflammatory spectrum, including PAMI. [preregistration/addendum_extension_v1.md §2]
- None of the twelve genes has a folder in Monarch's phenopacket-store: 731 gene folders at commit `85ffd78` (2026-10-07) for the registered six; 735 gene folders and 10,809 phenopackets at commit `ca133e6` (2026-11-04) for all twelve. [CONTEXT.md §4; DECISIONS.md D-52 decision log]
- Majeed syndrome was dropped from the extension by the addendum's registered rule on 2026-11-14 (10 included primary reports with open full text, under the bar of 15). It was later searched more widely and run on 24 documents as an exploratory twelfth disease (D-54). [DECISIONS.md D-52, D-54]

### 1.3 Reference data (ground truth), with dates

ClinVar counts are distinct VariationIDs on single-gene GRCh38 records; P/LP sums Pathogenic, Likely pathogenic and Pathogenic/Likely pathogenic; conflicting records are counted apart from VUS.

| Gene | ClinVar release (snapshot read) | Single-gene records | P/LP | VUS | Conflicting |
|---|---|---|---|---|---|
| *TNFAIP3* | 2026-10-12 (read 2026-10-19) | 764 | 99 | 375 | 27 |
| *ALDH5A1* | 2026-10-12 (read 2026-10-19) | 914 | 152 | 333 | 53 |
| *ABCA1* | 2026-10-12 (read 2026-10-19) | 2,006 | 85 | 705 | 141 |
| *ITGB2* | 2026-10-12 (read 2026-10-19) | 949 | 87 | 345 | 49 |
| *GFAP* | 2026-10-12 (read 2026-10-19) | 627 | 76 | 262 | 36 |
| *LAMP2* | 2026-10-12 (read 2026-10-19) | 986 | 154 | 292 | 66 |

[interim_paper.md §2.1 Table 2; supplement.md Table S2]

- The registered six were re-checked against the next release (19 Oct 2026, snapshot 2026-10-21): records unchanged except *GFAP* 629 (P/LP 76). [supplement.md Table S2]

| Gene (extension and Majeed) | ClinVar release (snapshot) | Single-gene records | P | LP | P/LP | VUS | Conflicting |
|---|---|---|---|---|---|---|---|
| *GAMT* | variant_summary of 09 Nov 2026 (2026-11-14) | 718 | 64 | 64 | 20 | 266 | 4 |
| *LCAT* | 09 Nov 2026 (2026-11-14) | 373 | 18 | 17 | 6 | 153 | 23 |
| *NOD2* | 09 Nov 2026 (2026-11-14) | 1290 | 14 | 4 | 3 | 679 | 143 |
| *PSTPIP1* | 09 Nov 2026 (2026-11-14) | 851 | 4 | — | — | 384 | 48 |
| *SLC2A10* | 09 Nov 2026 (2026-11-14) | 767 | 26 | 14 | 14 | 340 | 62 |

[analysis/poc/reference_snapshot/2026-11-14/counts_<GENE>.json, "single_gene_records"]. Plain sums of P + LP + P/LP: *GAMT* 148, *LCAT* 41, *NOD2* 21, *PSTPIP1* 4, *SLC2A10* 54.

- *LPIN2* (Majeed; snapshot 2026-11-15, ClinVar release of 09 Nov 2026): 1051 single-gene records, 51 P/LP, 455 VUS. [majeed_pv1s_findings.md, ClinVar concordance]
- OMIM: the six phenotype entries and six gene entries for the registered six, printed from omim.org to PDF by Dr. Lin on 2026-10-28 (D-42). They are the project's OMIM reference; content stays outside the repository (OMIM's terms restrict redistribution) and only a manifest with checksums and counts is committed. OMIM's clinical-synopsis pages were not frozen, so OMIM's phenotype half is "not yet assessed". OMIM was not checked for the extension five or Majeed. [interim_paper.md §2.6, §3.7b; DECISIONS.md D-42; extension_report.md §4]
- OMIM allelic variants titled for each registered disease, from the gene entries frozen 2026-10-28: HA20 9 of 9 listed (191163); SSADH 7 of 7 (610045); Tangier 19 of 25 (600046; 4 titled HDL deficiency, 2 reclassified polymorphisms); LAD-I 14 of 15 (600065; 1 moved); AxD 13 of 13 (137780); Danon 13 of 13 (309060). 82 listed in all, 75 titled for the six diseases. OMIM calls them "selected examples", not a catalogue. [interim_paper.md §3.7b, Table 8b]
- HPO annotations (`phenotype.hpoa`, 2026-09-02) are used by the harness only, for the phenotype-profile part of O2. [interim_paper.md §2.6]
- Ontology releases pinned for binding: HPO 2026-09-01, Mondo 2026-10-06 (sha256 in `data/ontologies/2026-10-19/manifest.json`). [interim_paper.md §2.5; NOTES_FOR_AGENTS.md §1]
- Completeness catalogues (harness side only): a 2020 HA20 review's Table S1 (D-30; 32 variants, 89 patients) and the AxD meta-analysis PMID 39420046, Supplementary Table 2 (D-39; 183 variants, 553 patients). The other four registered diseases had no suitable open catalogue and report no completeness figure. [interim_paper.md §2.6, Table 10]

### 1.4 Corpus construction and the open-access rule

- **Search.** PubMed from inception to a recorded date (HA20 2026-10-18; the other registered five 2026-10-19; the extension five 2026-11-14), gene symbol plus disease names and synonyms, with a case/patient/family filter, plus backward citation searching of key reviews through Europe PMC. No ClinVar or OMIM citation list was used as a seed for the five registered diseases after HA20 or for the extension (D-19). HA20's pilot corpus kept its ClinVar-seeded papers (92 of 160 corpus papers), tagged, and every O2 figure is reported with and without ClinVar-cited papers. [interim_paper.md §2.2, Table 3; addendum_extension_v1.md §3; DECISIONS.md D-19]
- **Screening.** Title/abstract screening by Claude Code helper agents (Sonnet) with a logged reason per record; full-text screening of every open full text with a verbatim evidence quote checked by script. HA20's corpus was carried over from the pilot and not full-text screened. [interim_paper.md §2.2; DECISIONS.md 2026-10-20 full-text screening entry]
- **Human screening check (D-34, 2026-10-20).** Dr. Lin rated 20 items: 15 abstract-stage inclusions (all AxD), agreeing with 14 and unsure of 1 (agreement 14 of 15, exact 95% CI 68–100%); 5 full-text exclusions (all LAD-I), agreeing with all 5 (48–100%). The drafted check (137 and 71 items) stopped there and the helpers' labels stand. Limits: two diseases, 20 items, one rater; non-English and supplement-only exclusions were not individually reviewed. [DECISIONS.md D-34]
- **Eligibility.** Primary publications with individual-level genotype or phenotype for at least one person with the disease; reviews with a per-patient table are included and their people tagged secondary-source (D-33). Reviews without new individuals, non-English papers and papers without individual data are excluded with the reason logged. [interim_paper.md §2.2]
- **Access (D-32, 2026-10-20).** Open access only: PMC, Europe PMC and open copies found through Unpaywall; no institutional access; pages behind a bot check are not fetched. Supplementary files were fetched where Europe PMC served them (and, for the extension, from NLM's PMC Cloud Service as a fallback) and converted to text, capped at 60,000 characters per file. [interim_paper.md §2.2; DECISIONS.md D-32, D-52 decision log]
- **Substitute trigger (D-08).** A disease is replaced only if it has fewer than 15 accessible eligible primary reports after full-text screening; every registered disease cleared it, so no substitute was used. [DECISIONS.md D-08; interim_paper.md §3.1]
- **Holdouts.** Natural-history comparator papers for the bias arm are kept out of the extraction corpus: AxD 2 (PMIDs 34865968, 39643430), SSADH 1 (30656189), Danon 2 (21415759, 41121270). [interim_paper.md §2.2, Table 3]
- **Corpus addendum (D-47).** Free copies found after the freeze are run as separately reported batches (§2.4); subscription-only papers stay out. [DECISIONS.md D-47]

### 1.5 Pre-registration and the frozen pipeline

- Pre-registration v1.0 (`preregistration/analysis_plan.md`) was frozen on 2026-10-20 (D-36), after the HA20 pilot report; git tags `prereg-v1.0` and `pipeline-v1.0` are on commit `ef3133e`. The session could not push the tags (HTTP 403); pushing them and the OSF registration are left to Dr. Lin, and `DECISIONS.md` still shows the OSF DOI as blank. [DECISIONS.md header, D-36; interim_paper.md §2]
- The four pinned files: `extract_v6.md` (instructions), `gatekeeper_v4.md`, `schema_ha20_v5.json` (five tables: publications, individuals, variants, phenotypic_features, phenotype_checklist) and `extraction_rules_v1.md`. [interim_paper.md §2.3; DECISIONS.md D-38]
- Known gap frozen on purpose (D-36): extraction v6 has no rule for hedged wording, while the gatekeeper has one; in the pre-freeze smoke run 5 of 23 unsupported claims were hedged statuses. The smoke run (20 HA20 papers): 0 span-check problems in 13,382 values; gatekeeper v4 judged 4,538 claims, 23 unsupported, 75 partial. [DECISIONS.md D-36]
- Per-disease instantiation (D-38): for every disease after HA20 a script swaps only the disease name, gene symbol, schema path and a 20-item checklist (12 changed lines per disease, diffs committed). [DECISIONS.md D-38]
- Checklists: 20 disease-specific features per disease, each with a three-state status for every individual, written by Opus helpers from open consensus guidelines or reviews, every quote checked verbatim (registered sources: SSADH 38452608; Danon 37821174; Tangier 33994407; AxD 39420046, 32779598, 40520824; LAD-I 42011429, 23207660, 33391282; HA20 from the pilot schema; Majeed from three openly licensed reviews, one item with no HPO term of its scope marked unmapped). [interim_paper.md §2.3; majeed_pv1s_findings.md Corpus]
- Results from `pipeline-v1.0` are primary; later fixes are logged, re-run and reported alongside (D-07). [DECISIONS.md D-07]

### 1.6 Models and how runs were executed

- **Route (D-17, D-20).** Claude Code helper agents in a Claude Code session on the funded claude.ai account, no API key: one helper per paper for extraction, one per chunk of up to 350 claims for the gatekeeper. Each helper reads only its paper, the instruction file, the schema and the rules file, with no web access and an instruction to use nothing it remembers about the paper. [interim_paper.md §2.3, §2.4; DECISIONS.md D-20]
- **Extractor and gatekeeper model:** Claude Opus. The pilot manifests record the served model ID `claude-opus-5-5`; the six registered-run manifests recorded only the helper alias "opus" at run time, and a `served_model` line stating `claude-opus-5-5` from the session configuration was added on 2026-10-28, marked as such. No sampling parameters are set on this route. Training-data cutoff recorded at the freeze: June 2026. [interim_paper.md §2.3; preregistration/analysis_plan.md §6.1]
- **Other helper roles:** screening by Sonnet helpers (registered six, Majeed); full-text screening of addendum batches by Opus helpers; HPO binding by script first, then helpers with an HPO lookup; evidence dossiers and checklists by Opus helpers. [DECISIONS.md 2026-10-20 screening entries; addendum_d47_batch1_findings.md What was run; majeed_pv1s_findings.md]
- **Open-weight comparator:** DeepSeek-V4.1-Flash (2026-09-10 checkpoint) through OpenRouter, provider pinned to DeepInfra fp8 with fallbacks off, in an agent loop with file tools (`pipeline/extract/openweight/agent.py`), same papers, launch prompt and frozen files. [openweight_comparison_findings.md §1]
- **Tools pinned:** VariantValidator 4.0.1 (dev; `4.0.1.dev7`), PDF conversion with Docling (2.140.0 for addendum batch 2), GPSEA 0.10.0 for exploratory maps. [interim_paper.md §2.5, §3.11; DECISIONS.md D-43 outcome; 2026-11-15 "set 1C" entry]
- **Cost tracking** is by session cost readings (list price, including helper agents) or by helper tokens; neither is a billing figure. [BUDGET.md Lines]

### 1.7 What a record is

- Every asserted value carries a PMID (or a record identifier) and a verbatim quote; a deterministic span check confirms every quote occurs verbatim in the source text, on all values. "Not reported" is a first-class output and carries no quote; a value with no quote is not emitted. [interim_paper.md §2.3, §2.4]
- Phenotypes are three-state (observed / excluded / not reported) and "not reported" is never collapsed into "excluded". A normal finding is recorded as the abnormality it rules out, marked excluded (D-27). Variant fields are taken only from statements about this person (D-29). Values stacked in multi-patient cells are not assigned by position (D-31). [interim_paper.md §2.3; preregistration/analysis_plan.md §6.2]
- Gatekeeper v4 asks whether the quote entails the value for the person the row is about, records whom the quote is about (this person, a named group, the cohort, another person, the paper, unclear), and gives one of four verdicts (supported, partially supported, unsupported, span not found). No value is exempted by a script match of value and quote (D-28). Phenopackets keep only claims judged supported. [interim_paper.md §2.4]
- Deduplication (merge policy v4): merges only on an explicit citation tying a person to an earlier report, one-to-one; the pilot's sex-and-onset route was dropped after it produced all 6 false merges of 93 (D-23). [interim_paper.md §2.5]
- Normalization: VariantValidator on the gene's MANE Select transcript; the original string is kept beside the normalized form; assumed or version-mapped transcripts are flagged; only VariantValidator's normalization fields enter the pipeline. Since D-43, where a gene has alternative coding exons (LAMP2 9a/9b/9c, divergence at c.1094; GFAP exon 7A, divergence at c.1172) and the paper names no transcript, the paper's own exon or isoform label chooses the transcript, else the description gets no genomic key (`isoform_ambiguous`). Blau only (D-53): after a reference mismatch on MANE, a description is sent once more on NM_022162.3. [interim_paper.md §2.5; DECISIONS.md D-43, D-53]
- Binding: checklist items to HPO through per-disease maps from the pinned HPO release (flagged for review); free-text features by script, then by helpers, every answer checked against the release; disease terms from Mondo by name, never by OMIM cross-reference. Output: one GA4GH Phenopacket v2 per identity, validated against the schema. [interim_paper.md §2.5]

### 1.8 Ground-truth isolation

- Code under `pipeline/extract` never reads reference data; an automated test fails if any such path or loader, or the tokens "clinvar", "omim" or "harness", appear there. Reference snapshots live outside the repository; only manifests and counts are committed. The harness (`pipeline/harness/`) reads extracted records and snapshots. [interim_paper.md §2.6]
- Leak paths kept out of extraction: corpus seeds from ClinVar/OMIM citation lists; disease–phenotype annotation files; LitVar's ClinVar links; database annotations in VariantValidator responses; natural-history comparator papers; tuning prompts against ClinVar/OMIM. [NOTES_FOR_AGENTS.md §6]
- Evidence dossiers for gap candidates were written by helpers reading only the extracted records and the papers, never ClinVar or OMIM, and propose no classification. [interim_paper.md §3.8]

### 1.9 Outcome definitions and statistics

- **O1.** Claim pool = every model claim gatekeeper v4 judged supported (the values that survive into the records). 250 claims by simple random sampling stratified by disease in proportion to claim volume, drawn by script with a recorded seed before any concordance is run. Labels: supported, unsupported, span not found; a value the rater cannot verify counts as unsupported, with a sensitivity analysis without such claims. Raters see the claim, its quote and the paper, never the gatekeeper's verdict. [interim_paper.md §2.7; preregistration/analysis_plan.md §7.1]
- **Rule C (D-02).** O1 passes if at most 4 of 250 audited claims are unsupported (observed rate below 2%). Operating characteristics (computed 2026-10-18): P(pass) is 0.99, 0.89, 0.68, 0.44 and 0.13 at true rates of 0.5%, 1%, 1.5%, 2% and 3%. Rule A (one-sided 95% upper bound < 2%, at most 1 of 250) would pass a true 1% pipeline only 29% of the time. Every report gives the exact 95% interval, states the highest rate the audit cannot exclude, and never presents a pass as proof that the true rate is below 2%. [preregistration/analysis_plan.md §7.1, §8; DECISIONS.md D-02]
- **What 250 claims can certify:** with 0 unsupported the exact 95% upper bound is 1.46% (two-sided) / 1.19% (one-sided); with 1, 2.21% / 1.88%; with 2, 2.86% / 2.50%. [background/grant_claim_checks.md item 14]
- **O2.** Tier 1 = same GRCh38 allele (VCF key); tier 2 = same protein change for papers with no cDNA. HGVS recall = share of ClinVar's (PMID, variant) citation pairs, restricted to corpus PMIDs, that the run extracted from that PMID. Overlap = share of extracted tier-1 alleles present in ClinVar (not precision). Classification agreement = authors' stated class against the ClinVar aggregate, among stated values. Phenotype profile = HPO annotation recall (term or descendant seen in ≥1 person) and share of terms seen in ≥2 people that match an annotation. Wilson 95% intervals. Every miss counts as discordant; a seeded sample of 50 misses awaits human triage into five categories. [interim_paper.md §2.7]
- **O3.** A gap candidate is a tier-1 allele absent from the ClinVar snapshot whose identifying values the gatekeeper judged supported in at least one row and (since 2026-10-28, registered six only) not listed among OMIM's allelic variants for the gene. Counted by stage: candidates, adjudicated, approved, drafted, signed off, submitted, accepted. ClinVar submissions will use the *curation* collection method, not *literature only* (D-13, 2026-10-21). [interim_paper.md §2.7, §3.8; DECISIONS.md D-13]
- **O4.** Per disease, a person lists each held-out comparator's HPO-mappable features and cohort frequencies before any literature frequency is computed; then observed ÷ (observed + excluded) per feature with a publication-cluster bootstrap (2,000 resamples, seed 7425). Since D-48 the primary analysis uses the registered run, records with a disease term only, and removes people tagged as stated or probable members of the comparator cohort. Memorization probe: closed-book recall from PMID, title and year, and guided completion of a 50-word opening, on 30 papers per disease stratified by date against the June 2026 cutoff. [interim_paper.md §2.7, §3.9; DECISIONS.md D-48]
- **O5.** Expert-minutes per accepted record, logged by the adjudication page. Claude vs DeepSeek-V4.1-Flash (D-10) under an identical scaffold; registered measure: unsupported rate on a blinded human audit of equal-size samples (not yet drawn). [interim_paper.md §2.7]
- **Intervals.** Wilson for simple proportions; exact Clopper–Pearson for the audit and the gatekeeper shares. [interim_paper.md §2.7]

### 1.10 The development pilot (HA20, 2026-10-18 to 2026-10-20, before the freeze)

- Two full extraction runs, a 15-paper repeat, a hand check of every merge, two 50-claim human audits by Dr. Lin, ClinVar concordance and a completeness check. Its findings set the rules frozen as extraction v6 and gatekeeper v4. HA20 was then re-extracted from scratch with the frozen pipeline; the pilot's records are not used in any result table. [interim_paper.md §2.8]

| Pilot gate | Threshold | Result |
|---|---|---|
| Q1 open-access corpus | ≥ 70% with full text | 53.1% (85 of 160): not met |
| Q2 verbatim provenance | every value has PMID + span | 64,999 values, 100% verbatim: met |
| Q3 valid phenopackets, normalized HGVS | 100% valid; ≥ 95% cDNA normalized or flagged | 749 of 749; 97.8%: met |
| Q4 unsupported values | span match ≥ 98%; human ≤ 4% (n = 50) | 100%; 6.0% and 6.3%: not met |
| Q5 deduplication | 0 false merges in the hand check | policy v3: 6 of 93: not met; v4: 0 of 50 (not independent) |
| Q6 concordance harness | table with CIs vs dated snapshots | met (ClinVar, HPO) |
| Q7 completeness | restricted recall ≥ 80% | 9 of 9: met |
| Q8 cost | six-disease projection ≤ $8,000 | $1,676–4,189: met |

[supplement.md Table S14]

### 1.11 Figures from the grant application that must not be repeated

| Application claim | Corrected statement |
|---|---|
| Tangier "~200 patients" | Sources say fewer than 100 (GeneReviews) to about 144 (a 2021 review); use "~100–150" (D-14) |
| Danon ">100 families" | "About 100 families; ≥146 molecularly confirmed patients" (D-14) |
| "408 phenopacket-store cohorts" | No published source; 731 gene folders at commit `85ffd78`, 2026-10-07 (D-14) |
| LAD-I "genotypes for 184 patients published but never structured" | Probably the patients *without* a reported genotype (323 cases to 2017, genotype for 139), which extraction cannot recover (D-14) |
| AxD "72 ClinVar P/LP entries; ~12 OMIM allelic variants" | 76 P/LP (release 2026-10-12, read 2026-10-19); 13 OMIM allelic variants (gene entry frozen 2026-10-28) |
| "97.6% precision on HPO extraction (Sonnet 4.5)" | A medRxiv preprint: 4 synthetic clinical notes run ≥50 times, tool-augmented condition (80.7% without tools), recall 65.3%, not top on precision or F1; not case reports |
| "DRBench" fabricated-citation rates 3.0% / 3.2% | Hallucinated-URL rates for two search-augmented Claude 3.x models (n = 641 and 1,735 URLs) in a 2026 study on DeepResearch Bench; not fabricated citations in general |
| AA-Omniscience comparison | Each pair is real but from different model generations; compare models from one snapshot with its date |
| "ClinVar literature-only submissions" | Submissions will use the *curation* collection method (D-13) |

- Unfavourable related result to keep: on counting probands from genomics papers, Claude Sonnet 4 had the lowest exact-count concordance (73.0%) and stability of five models. [NOTES_FOR_AGENTS.md §5; background/grant_claim_checks.md items 1–11; CONTEXT.md §4]
- Internal inconsistencies of the application: "held-out diseases" vs "held-out cohorts" (resolved by D-04 as comparator cohorts within the registered diseases); the budget's 65% / 35% split does not match its lines (D-15); the application named a Console org but the award is claude.ai credits that may not cover API calls (D-17). [NOTES_FOR_AGENTS.md §5]

---

## 2. Results

### 2.0 Twelve-disease totals (all runs, 2026-11-15)

| Set | Papers | People rows | Identities | With a variant in the gene | Phenopackets | With an interpretation | Model claims judged | Unsupported or not found |
|---|---|---|---|---|---|---|---|---|
| all twelve | 665 | 5,326 | 5,172 | 3,245 | 5,172 | 2,523 | 149,442 | 675 (0.45%) |
| registered six, registered runs only | 350 | 2,948 | 2,836 | 1,793 | 2,836 | 1,492 | 80,948 | 294 (0.36%) |
| registered six, with both addendum batches | 432 | 3,509 | 3,397 | 2,008 | 3,397 | 1,665 | 95,787 | 418 (0.44%) |
| five extension diseases | 209 | 1,653 | 1,617 | 1,096 | 1,617 | 758 | 48,494 | 222 (0.46%) |
| Majeed (exploratory) | 24 | 164 | 158 | 141 | 158 | 100 | 5,161 | 35 (0.68%) |

- 665 paper-runs across all runs of the twelve diseases; 660 distinct papers, because 4 papers appear under more than one disease (33042144: HA20/Majeed/PAPA; 37138899: LCAT/Tangier; 37848905: Blau/HA20; 40476138: LCAT/Tangier). No paper appears in two runs of the same disease. Main or registered runs 583, addendum batch 1 23, batch 2 59. [consolidated_runs_2026-11-15.md §1, §2, §7]
- Sums across runs are plain sums. Identities are merged within a run only: nobody has been matched across the registered run and the addendum batches, or across diseases, and phenopacket IDs restart in every run (D-50), so summed identities are an upper bound on people. Every phenopacket is schema-valid. [consolidated_runs_2026-11-15.md §2]
- Gap candidates in all: 272, of which 3 withdrawn and 269 left for the panel (registered six 215/1/214; extension five 45/2/43; Majeed 12/0/12). [consolidated_runs_2026-11-15.md §3]
- Gatekeeper shares are a second model read, not an audited error rate. No human audit of any of these runs has been returned; every gap candidate is pending adjudication; registered results stay primary and the addendum, extension and exploratory runs are shown beside them, never pooled into them. [consolidated_runs_2026-11-15.md header]

**Per-run statistics (all 23 runs).**

| Disease | Run | Papers | People rows | Identities | With a variant in the gene | Phenopackets | With an interpretation | With a disease term | With any feature | Model claims judged | Unsupported or not found (95% CI) | Not fully supported | cDNA descriptions normalized | Phenotype rows bound to HPO |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HA20 | `pv1-ha20` | 85 | 811 | 769 | 558 | 769 | 499 | 447 | 606 | 23,129 | 0.20% (46/23,129; 0.15–0.27) | 1.9% (446/23129) | 96.7% of 152 | 91.6% of 5,079 |
| HA20 | `pv1a-ha20` | 1 | 3 | 3 | 1 | 3 | 1 | 1 | 3 | 49 | 0.00% (0/49; 0.00–7.25) | 0.0% (0/49) | no cDNA descriptions | 100.0% of 7 |
| HA20 | `pv1a2-ha20` | 2 | 9 | 9 | 7 | 9 | 5 | 9 | 9 | 220 | 3.18% (7/220; 1.29–6.45) | 8.6% (19/220) | 100.0% of 3 | 91.3% of 46 |
| AxD | `pv1-axd` | 69 | 463 | 456 | 318 | 456 | 255 | 226 | 303 | 14,403 | 0.27% (39/14,403; 0.19–0.37) | 3.6% (512/14403) | 78.8% of 104 | 91.3% of 3,316 |
| AxD | `pv1a-axd` | 3 | 7 | 7 | 3 | 7 | 3 | 1 | 5 | 309 | 1.29% (4/309; 0.35–3.28) | 2.6% (8/309) | 100.0% of 2 | 93.2% of 88 |
| AxD | `pv1a2-axd` | 26 | 196 | 196 | 123 | 196 | 109 | 165 | 136 | 5,947 | 0.24% (14/5,947; 0.13–0.39) | 3.5% (207/5947) | 60.0% of 20 | 87.3% of 1,495 |
| LAD-I | `pv1-lad1` | 42 | 508 | 508 | 328 | 508 | 299 | 326 | 302 | 10,864 | 0.43% (47/10,864; 0.32–0.57) | 3.5% (377/10864) | 86.5% of 170 | 84.3% of 1,862 |
| LAD-I | `pv1a-lad1` | 6 | 28 | 28 | 12 | 28 | 11 | 23 | 15 | 880 | 0.80% (7/880; 0.32–1.63) | 3.9% (34/880) | 100.0% of 9 | 85.3% of 191 |
| LAD-I | `pv1a2-lad1` | 6 | 41 | 41 | 14 | 41 | 6 | 29 | 11 | 997 | 0.90% (9/997; 0.41–1.71) | 3.4% (34/997) | 100.0% of 1 | 69.1% of 236 |
| SSADH | `pv1-ssadh` | 40 | 421 | 363 | 243 | 363 | 174 | 311 | 216 | 9,759 | 0.38% (37/9,759; 0.27–0.52) | 2.9% (279/9759) | 86.5% of 141 | 89.8% of 1,683 |
| SSADH | `pv1a-ssadh` | 3 | 14 | 14 | 0 | 14 | 0 | 13 | 12 | 349 | 0.00% (0/349; 0.00–1.05) | 7.2% (25/349) | no cDNA descriptions | 95.2% of 83 |
| SSADH | `pv1a2-ssadh` | 9 | 87 | 87 | 17 | 87 | 8 | 63 | 39 | 1,700 | 0.82% (14/1,700; 0.45–1.38) | 2.6% (44/1700) | 85.7% of 14 | 98.6% of 347 |
| Danon | `pv1-danon` | 83 | 510 | 505 | 281 | 505 | 212 | 322 | 445 | 17,963 | 0.61% (110/17,963; 0.50–0.74) | 3.1% (552/17963) | 89.3% of 112 | 92.8% of 4,558 |
| Danon | `pv1a2-danon` | 5 | 22 | 22 | 10 | 22 | 8 | 8 | 19 | 1,018 | 0.29% (3/1,018; 0.06–0.86) | 3.0% (31/1018) | 50.0% of 2 | 85.5% of 282 |
| Tangier | `pv1-tangier` | 31 | 235 | 235 | 65 | 235 | 53 | 175 | 135 | 4,830 | 0.31% (15/4,830; 0.17–0.51) | 4.5% (217/4830) | 90.0% of 20 | 90.7% of 1,051 |
| Tangier | `pv1a-tangier` | 10 | 63 | 63 | 4 | 63 | 4 | 47 | 50 | 1,262 | 4.75% (60/1,262; 3.65–6.08) | 9.5% (120/1262) | no cDNA descriptions | 79.9% of 308 |
| Tangier | `pv1a2-tangier` | 11 | 91 | 91 | 24 | 91 | 18 | 48 | 74 | 2,108 | 0.28% (6/2,108; 0.10–0.62) | 6.6% (140/2108) | 100.0% of 11 | 88.2% of 516 |
| Blau | `pv1-blau` | 68 | 513 | 507 | 358 | 507 | 295 | 238 | 433 | 15,476 | 0.25% (39/15,476; 0.18–0.34) | 3.6% (563/15476) | 97.4% of 38 | 90.5% of 3,530 |
| Majeed | `pv1s-majeed` | 24 | 164 | 158 | 141 | 158 (131 of 158 files public) | 100 | 113 | 132 | 5,161 | 0.68% (35/5,161; 0.47–0.94) | 3.7% (190/5161) | 91.3% of 46 | 71.1% of 1,067 |
| LCAT | `pv1-lcat` | 50 | 283 | 282 | 162 | 282 | 106 | 119 | 212 | 7,623 | 0.45% (34/7,623; 0.31–0.62) | 7.1% (545/7623) | 91.3% of 69 | 90.5% of 1,691 |
| GAMT | `pv1-gamt` | 23 | 380 | 365 | 279 | 365 | 197 | 313 | 332 | 9,981 | 0.63% (63/9,981; 0.49–0.81) | 4.8% (481/9981) | 95.1% of 122 | 95.7% of 2,021 |
| ATS | `pv1-ats` | 34 | 157 | 152 | 84 | 152 | 51 | 103 | 109 | 6,268 | 0.86% (54/6,268; 0.65–1.12) | 3.5% (218/6268) | 100.0% of 45 | 93.2% of 1,707 |
| PAPA | `pv1-papa` | 34 | 320 | 311 | 213 | 311 | 109 | 211 | 275 | 9,146 | 0.35% (32/9,146; 0.24–0.49) | 3.5% (323/9146) | 72.2% of 18 | 92.7% of 2,117 |

[consolidated_runs_2026-11-15.md §2]. "With a disease term" and "with any feature" are counted from the phenopacket files; a record without either holds identity fields only (relatives, or people whose only claims the gatekeeper removed). The cDNA denominators here are the `cdna_descriptions` field of each run's `normalization_summary.json` (see §2.1.4 for the interim paper's different denominators).

**Other runs over the same papers (they add no papers):** 10% repeats `pv1-<d>-repeat` (HA20 9, AxD 7, LAD-I 5, SSADH 4, Danon 9, Tangier 4; Blau 7, LCAT 5, GAMT 3, ATS 4, PAPA 4 papers); open-weight `ow-ha20` (85) and `ow-ssadh` (40); HA20 pilot runs before the freeze (`poc-ha20-run-1` 85, `poc-ha20-run-2` 85, two 15-paper repeats, `poc-ha20-v5-subset` 20, `poc-ha20-v6-smoke` 20, `poc-ha20-v4-check` 10, `poc-ha20-smoke-1` 3). [consolidated_runs_2026-11-15.md §5]

### 2.1 The registered six (frozen pipeline, runs of 2026-10-20)

#### 2.1.1 Corpus

| Disease | Records screened | In corpus (title/abstract) | Open full text | + free elsewhere (upper bound) | Eligible after full-text screening | Papers extracted | …with individual rows | ClinVar-seeded papers (D-19) | Comparator holdouts |
|---|---|---|---|---|---|---|---|---|---|
| HA20 (development) | 838 | 160 | 85 (53.1%) | 60.0% | not screened (pilot corpus) | 85 | 77 | 92 | — |
| SSADH | 357 | 171 | 59 (34.5%) | 46.8% | 40 | 40 | 40 | — | 30656189 |
| Tangier | 529 | 284 | 39 (13.7%) | 35.6% | 31 | 31 | 31 | — | — |
| LAD-I | 874 | 274 | 59 (21.5%) | 36.5% | 42 | 42 | 42 | — | — |
| AxD | 539 | 363 | 83 (22.9%) | 38.8% | 69 | 69 | 69 | — | 34865968, 39643430 |
| Danon | 416 | 244 | 96 (39.3%) | 47.1% | 83 | 83 | 83 | — | 21415759, 41121270 |

- 421 of 1,496 corpus papers (28%) have open full text, from 3,553 records screened. Open full text ranges from 14% (Tangier) to 53% (HA20) of the title/abstract corpus. Every disease cleared the D-08 floor of 15 eligible primary papers. [interim_paper.md §3.1, Table 3, Figure 2]
- Eligible papers with full text that are case reports or series: AxD 68 of 69, LAD-I 38 of 42, SSADH 36 of 40, Danon 82 of 83, Tangier 28 of 31. 71 papers were excluded at full text, 10 of them as not in English (mostly Japanese case reports). [DECISIONS.md 2026-10-20 full-text screening entry]
- "Free elsewhere" is a Europe PMC listing of a free copy outside PMC, not fetched (an upper bound). Paywalled papers are not a random subset: for HA20 they include the two largest sources of its completeness catalogue, and for the other diseases the catalogue reviews' own source papers are often closed. [interim_paper.md §3.1]

#### 2.1.2 Extraction, provenance and the gatekeeper

| Disease | Papers | Individual rows | Variant rows | Values with a quote | Span-check problems | Model claims judged | Unsupported (exact 95% CI) | Not fully supported (exact 95% CI) | Papers with any unsupported | Share held by worst 3 papers |
|---|---|---|---|---|---|---|---|---|---|---|
| HA20 (development) | 85 | 811 | 620 | 67,863 | 0 | 23,129 | 0.20% (46/23,129; 0.15–0.27) | 1.93% (446/23,129; 1.75–2.11) | 15 of 85 | 37% |
| SSADH | 40 | 421 | 472 | 31,370 | 0 | 9,759 | 0.38% (37/9,759; 0.27–0.52) | 2.86% (279/9,759; 2.54–3.21) | 7 of 40 | 76% |
| Tangier | 31 | 235 | 82 | 16,762 | 0 | 4,830 | 0.31% (15/4,830; 0.17–0.51) | 4.49% (217/4,830; 3.93–5.12) | 7 of 31 | 60% |
| LAD-I | 42 | 508 | 411 | 36,280 | 0 | 10,864 | 0.43% (47/10,864; 0.32–0.57) | 3.47% (377/10,864; 3.13–3.83) | 12 of 42 | 66% |
| AxD | 69 | 463 | 343 | 40,773 | 0 | 14,403 | 0.27% (39/14,403; 0.19–0.37) | 3.55% (512/14,403; 3.26–3.87) | 14 of 69 | 51% |
| Danon | 83 | 510 | 305 | 48,682 | 0 | 17,963 | 0.61% (110/17,963; 0.50–0.74) | 3.07% (552/17,963; 2.83–3.34) | 23 of 83 | 55% |
| **Five confirmatory (without HA20)** | 265 | 2,137 | 1,613 | 173,867 | 0 | 57,819 | **0.43% (248/57,819; 0.38–0.49)** | 3.35% (1,937/57,819; 3.20–3.50) | 63 of 265 | — |
| **All six** | 350 | 2,948 | 2,233 | 241,730 | 0 | 80,948 | **0.36% (294/80,948; 0.32–0.41)** | 2.94% (2,383/80,948; 2.83–3.06) | 78 of 350 | — |

[interim_paper.md §3.2, Table 4]

- **Provenance is complete.** Every one of the 241,730 values asserted across the six runs has a quote the span check found verbatim in its paper (0 problems in every disease). Values without a quote are not emitted, so the fabricated-span count is zero by construction and by check. A helper that left quotes empty was resumed for a repair-only pass; each repair was diffed to show only the target cells changed (HA20 had 6). [interim_paper.md §2.4, §3.2]
- **This is not an error rate.** The gatekeeper share is what a second model read catches; in the pilot the gatekeeper caught 1–2 of every 4–6 problems a person found (§2.1.5). [interim_paper.md §3.2]
- **Unsupported claims cluster.** In five of six diseases the three worst papers hold half or more of that disease's unsupported claims. Danon's three worst papers hold 60 of its 110: variant and diagnosis fields given to eight family carriers when the paper names only the proband (PMID 37215540, 35 claims); cohort wording about typical severity applied to individuals (30413001, 15); exclusions resting on cohort wording about typical absence of symptoms (41560058, 10). [interim_paper.md §3.2]
- **Why claims fail.** The commonest unsupported field is `variants.gene_symbol_as_stated` in five diseases (HA20 17, SSADH 16, Tangier 9, LAD-I 14, AxD 21, Danon 22 claims): a relative's or a cited patient's gene or variant quoted from a sentence about the proband. The second pattern is hedged wording recorded as observed or excluded (the frozen gap, D-36). The third is cohort-level statements applied to individuals; "the cohort in general" dominates Danon's and AxD's unsupported claims. Partial verdicts are mostly ages at presentation recorded as onset or last evaluation. [interim_paper.md §3.2]
- Whom the quote was about, unsupported claims only: HA20 other person 14, this person 10, cohort general 9, named group 9, unclear 4; SSADH other person 27, this person 10; Tangier other person 11, this person 4; LAD-I other person 25, named group 13, this person 7, cohort general 2; AxD cohort general 18, this person 11, other person 10; Danon cohort general 55, this person 26, other person 21, named group 6, unclear 2. Danon's top unsupported field is `phenotypic_features.status` (25). [supplement.md Table S4]
- **Papers that contradict themselves.** The gatekeeper flagged about 30 papers whose table and text disagree; those claims were judged on the table and noted, and are collected for the human audit and adjudication. [interim_paper.md §3.2]
- Gatekeeper removed 1,060 claims before the phenopackets were built (plain sum of Table 6's "claims dropped": HA20 207, SSADH 151, Tangier 117, LAD-I 100, AxD 221, Danon 264). [interim_paper.md §3.4 Table 6, §4]

#### 2.1.3 Run-to-run stability (10% repeat)

A random 10% of each disease's papers (ceil, seed 20261020; 38 papers) was re-extracted with the same frozen files. The gatekeeper was not run on the repeat.

| Disease | Papers | Same individual count | Label Jaccard | Variants (strings) | Variants (folded keys) | Checklist agreement (cells) | Features, label-free | HPO status, label-free |
|---|---|---|---|---|---|---|---|---|
| HA20 | 9 | 7 of 9 | 0.69 | 0.67 | 0.94 | 0.996 (1,300) | 0.71 | 0.68 |
| SSADH | 4 | 4 of 4 | 1.00 | 1.00 | 1.00 | 1.000 (160) | 0.43 | 0.71 |
| Tangier | 4 | 3 of 4 | 0.62 | 0.86 | 0.83 | 0.970 (200) | 0.57 | 0.69 |
| LAD-I | 5 | 3 of 5 | 0.88 | 0.55 | 0.92 | 0.998 (440) | 0.64 | 0.69 |
| AxD | 7 | 7 of 7 | 0.83 | 0.95 | 1.00 | 0.997 (1,340) | 0.69 | 0.67 |
| Danon | 9 | 7 of 9 | 0.87 | 0.65 | 0.86 | 0.996 (680) | 0.59 | 0.64 |

- Checklist statuses agree on 97–100% of cells in every disease; free-text rows agree less (0.43–0.71 label-free) because two readers phrase and split features differently. Variant keys agree at 0.92–1.00 in four diseases and 0.83 (Tangier) and 0.86 (Danon), where one paper each recorded the same variants in different notation. Individual counts differ in 9 of 38 papers, from scope calls on relatives and on patients cited from earlier reports. [interim_paper.md §3.3, Table 5]

#### 2.1.4 Records: reconciliation, normalization, binding and phenopackets

| Disease | Rows → identities (merges) | Review-only identities | With target-gene variant | cDNA normalized (interim paper's denominator) | Feature rows bound to HPO | Phenopackets (with interpretation) | Terms observed / excluded | Observed–excluded conflicts | Claims dropped by gatekeeper | Sex | Schema-valid, errors |
|---|---|---|---|---|---|---|---|---|---|---|---|
| HA20 | 811 → 769 (42) | 282 | 558 | 96.7% of 195; 85 protein-only | 91.6% of 5,079 | 769 (499) | 3,678 / 1,018 | 93 | 207 | 348 F / 246 M / 175 unknown | 769, 0 |
| SSADH | 421 → 363 (58) | 43 | 243 | 86.5% of 147; 15 protein-only | 89.8% of 1,683 | 363 (174) | 1,249 / 299 | 10 | 151 | 90 F / 85 M / 188 unknown | 363, 0 |
| Tangier | 235 → 235 (0) | 140 | 65 | 90.0% of 31; 17 protein-only | 90.7% of 1,051 | 235 (53) | 745 / 219 | 13 | 117 | 88 F / 119 M / 28 unknown | 235, 0 |
| LAD-I | 508 → 508 (0) | 194 | 328 | 86.5% of 185; 7 protein-only | 84.3% of 1,862 | 508 (299) | 1,264 / 299 | 5 | 100 | 129 F / 146 M / 233 unknown | 508, 0 |
| AxD | 463 → 456 (7) | 175 | 318 | 78.9% of 116; 65 protein-only | 91.3% of 3,316 | 456 (255) | 2,441 / 529 | 40 | 221 | 149 F / 160 M / 147 unknown | 456, 0 |
| Danon (re-normalized under D-43) | 510 → 505 (5) | 164 | 281 | 89.3% of 140; 25 protein-only | 92.8% of 4,558 | 505 (212) | 3,302 / 1,007 | 48 | 264 | 221 F / 243 M / 41 unknown | 505, 0 |

[interim_paper.md §3.4, Table 6]

- **Denominator conflict, unresolved by the sources:** the interim paper prints the cDNA-normalized percentages over 195, 147, 31, 185, 116 and 140 descriptions; the consolidated table (2026-11-15), which reads the `cdna_descriptions` field of each run's normalization summary, prints the same percentages over 152, 141, 20, 170, 104 and 112 (AxD 78.8% there, 78.9% in the interim paper). The run summary file for HA20 holds `cdna_descriptions: 152` and `share_normalized_or_corrected_of_cdna: 0.9671`. Use the consolidated denominators, or give the percentage alone. [consolidated_runs_2026-11-15.md §2; data/extracted/ha20/pv1-ha20/normalization_summary.json]
- 2,836 identities from 2,948 rows; 2,836 phenopackets, all schema-valid; 1,492 with a genomic interpretation; 12,679 observed and 3,371 excluded HPO terms. Merge policy v4 made 112 merges; SSADH's 58 are all the duplicate study (PMIDs 37503297 preprint and 37962671 journal version, both kept, patients merged with evidence; the two versions disagree on one variant's amino acid). Tangier and LAD-I have no citation merges, more likely a limit of the citation route than a fact about those literatures. [interim_paper.md Abstract, §3.4, §3.12 SSADH; DECISIONS.md D-40]
- Phenopackets with a disease term in the registered runs: HA20 447, AxD 226, LAD-I 326, SSADH 311, Danon 322, Tangier 175 (consolidated table); 485 of the 2,836 registered records (17%) hold identity fields only (neither a feature nor an interpretation). [consolidated_runs_2026-11-15.md §2; addendum_d47_batch2_findings.md point 2]
- Normalization of cDNA descriptions ranges from 78.9% (AxD) to 96.7% (HA20). AxD papers often print cDNA without "c." and use legacy numbering; 22 AxD descriptions were unresolvable. Protein-only strings (65 AxD, 85 HA20) can match ClinVar only at tier 2. HPO binding covers 84–93% of feature rows. [interim_paper.md §3.4]
- Variant spectrum: missense dominates AxD (74% of interpretations) and SSADH (51%); nonsense and frameshift dominate HA20 (63%) and Danon (52%). Distinct variant descriptions: HA20 280, SSADH 162, Tangier 48, LAD-I 192, AxD 181, Danon 165. [interim_paper.md §3.4, §3.12]
- Observed–excluded conflicts (same term observed and excluded for one identity) are 5–93 per disease and are kept visible. Sex is unknown for 5–52% of identities by disease (SSADH highest). Onset age is asserted for 3–50% of individuals and consanguinity for 0–30%, so the records carry "not reported" far more often than a value. [interim_paper.md §3.4]
- **D-43 re-normalization of Danon (2026-10-28):** 165 distinct descriptions; exactly 2 changed (one moved to NM_013995.2 by the paper's own exon label; one from a review that names no transcript became `isoform_ambiguous`); status counts normalized 61 (was 62), corrected 39, protein_only 25, not_normalized 27, unresolvable 12, isoform_ambiguous 1; 505 phenopackets rebuilt, all valid, same feature counts, 5 records differ in content. GFAP's one isoform case had already failed normalization safely. [DECISIONS.md D-43 deviation, outcome]
- **Most-observed features:** HA20 oral ulcer 43%, recurrent fever 27%; SSADH global developmental delay 25%, seizure 20%; Tangier decreased circulating HDL-C 21%, angina pectoris 14%; LAD-I increased total leukocyte count 32%, neonatal omphalitis 12%; AxD abnormal cerebral white matter morphology 19%, seizure 16%; Danon left ventricular hypertrophy 39%, hypertrophic cardiomyopathy 28%. [interim_paper.md §3.12]

#### 2.1.5 O1 sample (drawn) and what the pilot's human audits showed

- **O1 drawn, not rated:** 250 claims from the 78,564 model claims gatekeeper v4 judged supported, stratified by disease (HA20 72, SSADH 30, Tangier 15, LAD-I 33, AxD 44, Danon 56), seed 40250, drawn 2026-10-20 before any concordance was run; pool sizes, allocation, input hashes and commit recorded (`adjudication/o1_audit/sample_key.json`). [interim_paper.md §3.5]
- **The pilot audits are the only human ratings of extracted claims.** Both were on HA20, before the freeze, rated by Dr. Lin, each on a different pipeline version, and both missed the pilot's own 4% gate:

| Audit | Pipeline | Claims rated | Unsupported (exact 95% CI) | Not fully supported | Error class found | Rule frozen in response |
|---|---|---|---|---|---|---|
| First | instructions v3, gatekeeper v1 | 50 | 3 of 50: 6.0% (1.3%–16.5%) | 6 of 50 | variant fields taken from a group statement or a literature-summary column | D-29: variant fields only from this person |
| Re-audit | instructions v5, gatekeeper v3 (20 papers) | 48 | 3 of 48: 6.3% (1.3%–17.2%) | 4 of 48 | ages read by position from a stacked multi-patient cell; rater could not verify them | D-31: no positional reading of stacked cells |
| Re-audit, sensitivity | as above, without the 3 unverifiable claims | 45 | 0 of 45: 0.0% (0.0%–7.9%) | 1 of 45 | | |

[interim_paper.md §3.6, Table 7]

- Variant fields were clean after D-29: 0 of 20 unsupported in the re-audit, against 3 of 20 before. [interim_paper.md §3.6]
- The gatekeeper flagged few of the claims a person rejected: v1 2 of 6, v3 1 of 4, with no false flags. Its own unsupported rate (0.036% for v1, 0.34% for v3) understated the human rate (6.0%, 6.3%) by an order of magnitude. [interim_paper.md §3.6]
- Deduplication: merge policy v3 made 93 merges; a full hand check found 84 true, 6 false, 3 unclear; all 6 false merges came from the sex-and-onset route, which v4 dropped. v4 had 0 false merges in the same set, but it was chosen after the check, so that is not an independent test; the registered 50-merge hand check of the six-disease run has not been done. [interim_paper.md §3.6]
- Caveats: n = 50 and 48, one rater, and the second-look tabs showed the gatekeeper's reasons, so some labels there are not independent of it. HA20 is the development disease. The frozen pipeline has not been audited by a person. [interim_paper.md §3.6]
- Measured rating time (one rater): 87 ratings in 56.7 minutes and 50 in 18.3 minutes in the two pilot audit sessions, 0.65 and 0.37 minutes per rating. [plan_human_assessment_2026-11-15.md §5]

#### 2.1.6 O2: concordance with ClinVar (run 2026-10-20; release 2026-10-12, snapshot 2026-10-19)

| Disease | Gene matches disease gene | HGVS recall, tier 1 | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement (stated) | ClinVar condition names the disease | HPO annotation recall | Terms in ≥2 people matching an annotation | Corpus PMIDs cited by ClinVar |
|---|---|---|---|---|---|---|---|---|---|
| HA20 | 99.8% (558/559; 99.0–100.0) | 26.9% (21/78; 18.3–37.7) | 26.9% (21/78; 18.3–37.7) | 37.9% (39/103; 29.1–47.5) | 82.8% (24/29; 65.5–92.4) | 47.4% (27/57; 35.0–60.1) | 92.9% (13/14; 68.5–98.7) | 6.1% (19/309; 4.0–9.4) | 20.0% (17/85; 12.9–29.7) |
| SSADH | 100.0% (243/243; 98.4–100.0) | 10.1% (16/158; 6.3–15.8) | 14.6% (23/158; 9.9–20.9) | 87.2% (68/78; 78.0–92.9) | 91.8% (45/49; 80.8–96.8) | 98.8% (83/84; 93.6–99.8) | 94.1% (32/34; 80.9–98.4) | 40.0% (52/130; 32.0–48.6) | 45.0% (18/40; 30.7–60.2) |
| Tangier | 98.5% (65/66; 91.9–99.7) | 16.7% (1/6; 3.0–56.4) | 50.0% (3/6; 18.8–81.2) | 56.2% (9/16; 33.2–76.9) | 80.0% (8/10; 49.0–94.3) | 37.5% (6/16; 18.5–61.4) | 70.8% (17/24; 50.8–85.1) | 15.3% (15/98; 9.5–23.7) | 16.1% (5/31; 7.1–32.6) |
| LAD-I | 100.0% (328/328; 98.8–100.0) | 23.3% (14/60; 14.4–35.4) | 31.7% (19/60; 21.3–44.2) | 34.9% (45/129; 27.2–43.4) | 70.0% (7/10; 39.7–89.2) | 90.4% (47/52; 79.4–95.8) | 70.6% (12/17; 46.9–86.7) | 14.4% (17/118; 9.2–21.9) | 16.7% (7/42; 8.3–30.6) |
| AxD | 99.7% (318/319; 98.2–99.9) | 27.5% (14/51; 17.1–40.9) | 66.7% (34/51; 53.0–78.0) | 73.1% (49/67; 61.5–82.3) | 58.6% (17/29; 40.7–74.5) | 85.6% (95/111; 77.9–90.9) | 84.2% (16/19; 62.4–94.5) | 13.5% (36/267; 9.9–18.1) | 39.1% (27/69; 28.5–50.9) |
| Danon | 97.9% (281/287; 95.5–99.0) | 35.0% (7/20; 18.1–56.7) | 50.0% (10/20; 29.9–70.1) | 47.9% (35/73; 36.9–59.2) | 78.9% (15/19; 56.7–91.5) | 89.6% (43/48; 77.8–95.5) | 87.1% (27/31; 71.1–94.9) | 15.9% (40/251; 11.9–21.0) | 18.1% (15/83; 11.3–27.7) |

Wilson 95% intervals. No threshold applies (D-03). These figures predate the D-43 re-normalization of the Danon run, which moved one placed Danon variant and unplaced another; O2 was not re-run (D-43). [interim_paper.md §3.7, Table 8; DECISIONS.md D-43 decision log]

- **HGVS recall is low (10–35% at tier 1; 15–67% with protein-level matches) and the misses sit in single papers.** The founding HA20 paper (PMID 26642243) holds 52 of HA20's 57 misses: ClinVar cites it for many variants it does not describe. A LAD-I mutation-update review (22134107) holds 37 of LAD-I's 41. In SSADH, a 2003 paper whose table was scrambled in conversion (14635103) holds 68 and a 2020 paper testing variants in vitro with no patients (33203024) 53 of 135. AxD misses: 17 in 10 papers; Danon 10 in 5; Tangier 3 in 3. [interim_paper.md §3.7, §3.12]
- **Triage sample:** 50 misses drawn with seed 72650 (`adjudication/o2_triage/`) from 263 misses, to be sorted by a person into five categories. For 28 of the 50, a script found no mention of the variant's position or residue in the paper text, which points to "citation does not describe the variant" or a missing supplement. [interim_paper.md §3.7; plan_human_assessment_2026-11-15.md §3]
- **Overlap** (extracted tier-1 alleles present in ClinVar) is 35–87%; low values (LAD-I 35%, HA20 38%) are where the gap candidates are. **Classification agreement** among stated values is 59–92%, and the disagreements run one way: authors assert P/LP where ClinVar holds VUS (the directional expectation stated in advance; not evidence of extraction error). **ClinVar's condition names the disease** for 38–99% of matched variants (Tangier 38%, HA20 47% reflect records filed under broader conditions). **Phenotype profile:** 71–94% of annotated HPO terms observed in at least one person; only 6–40% of terms seen in two or more people match an annotation. [interim_paper.md §3.7]

| Disease | ClinVar P/LP, authors P/LP | ClinVar VUS, authors P/LP | ClinVar P/LP, authors VUS | Authors state no class | Agreeing pairs |
|---|---|---|---|---|---|
| HA20 | 17 | 2 | 1 | 27 | 24 |
| SSADH | 38 | 3 | 1 | 34 | 45 |
| Tangier | 3 | 1 | 1 | 6 | 8 |
| LAD-I | 5 | 3 | 0 | 42 | 7 |
| AxD | 14 | 4 | 2 | 82 | 17 |
| Danon | 14 | 3 | 0 | 29 | 15 |

[interim_paper.md §3.7, Table 9]

**Without ClinVar-cited papers (D-19).** Recall is undefined (every reference pair comes from a paper ClinVar cites):

| Disease | Overlap, tier 1 | Classification agreement | Condition names disease |
|---|---|---|---|
| HA20 | 33.3% (29/87; 24.3–43.8) | 85.7% (18/21; 65.4–95.0) | 48.9% (23/47; 35.3–62.8) |
| SSADH | 83.3% (40/48; 70.4–91.3) | 93.5% (29/31; 79.3–98.2) | 97.6% (41/42; 87.7–99.6) |
| Tangier | 57.1% (8/14; 32.6–78.6) | 85.7% (6/7; 48.7–97.4) | 33.3% (4/12; 13.8–60.9) |
| LAD-I | 40.0% (12/30; 24.6–57.7) | 62.5% (5/8; 30.6–86.3) | 100.0% (15/15; 79.6–100.0) |
| AxD | 69.4% (34/49; 55.5–80.5) | 66.7% (14/21; 45.4–82.8) | 87.2% (41/47; 74.8–94.0) |
| Danon | 41.5% (22/53; 29.3–54.9) | 80.0% (12/15; 54.8–93.0) | 90.0% (27/30; 74.4–96.5) |

[interim_paper.md §3.7]

**Completeness against published catalogues (secondary, descriptive).**

| Disease | Catalogue | Variants (patients) | Restricted denominator | Restricted recall, primary papers | Unrestricted recall | Restricted misses |
|---|---|---|---|---|---|---|
| HA20 | 2020 review, Table S1 (D-30) | 32 (89) | 9 | 100.0% (9/9; 70.1–100.0) | 90.6% (29/32; 75.8–96.8) | none |
| AxD | PMID 39420046, Suppl. Table 2 (D-39) | 183 (553) | 56 | 96.4% (54/56; 87.9–99.0) | 53.8% (91/169; 46.3–61.2) | 2 (PMIDs 36425948, 26478912) |

- Restricted = catalogue variants whose source paper is in the corpus. AxD's two restricted misses are notation, not absence (a deletion extracted with a hyphen in place of the HGVS underscore, and a whole-gene deletion extracted by exon range); the matcher was not changed after seeing this. AxD at protein level 52/56, cDNA level 36/56. Restricted denominators are small because most catalogue source papers are not open access, so unrestricted recall mostly measures access. For AxD the run has at least as many carriers as the catalogue in all 43 shared source papers. The AxD catalogue was added after extraction, on the harness side only (D-39). [interim_paper.md §3.7, Table 10, §3.12 AxD]
- Exploratory: 16 of 2,006 single-gene *ABCA1* ClinVar records (0.8%) and 7 of 85 P/LP records (8.2%) match variants extracted from the 31-paper Tangier corpus; 19 of 35 extracted variants are not in ClinVar. [interim_paper.md §3.11]

#### 2.1.7 OMIM as a human-curated holdout (D-42; 2026-10-28)

| Disease | OMIM allelic variants | Tier 1 | Tier 2 | Token only | Not recovered | Recall anywhere in the run (tiers 1+2) | Source paper in run: recovered from it | OMIM source papers extracted | Corpus PMIDs cited by OMIM |
|---|---|---|---|---|---|---|---|---|---|
| HA20 | 9 | 8 | 0 | 0 | 1 | 88.9% (8/9; 56.5–98.0) | 6: 100.0% (6/6; 61.0–100.0) | 1 of 4 | 3.1% (5/160; 1.3–7.1) |
| SSADH | 7 | 3 | 1 | 0 | 3 | 57.1% (4/7; 25.0–84.2) | 5: 0.0% (0/5; 0.0–43.4) | 2 of 4 | 10.5% (18/171; 6.8–16.0) |
| Tangier | 19 | 0 | 2 | 0 | 17 | 10.5% (2/19; 2.9–31.4) | 0: — | 0 of 11 | 11.6% (33/284; 8.4–15.9) |
| LAD-I | 14 | 12 | 0 | 0 | 2 | 85.7% (12/14; 60.1–96.0) | 2: 50.0% (1/2; 9.5–90.5) | 1 of 44 | 4.7% (13/274; 2.8–7.9) |
| AxD | 13 | 8 | 1 | 0 | 4 | 69.2% (9/13; 42.4–87.3) | 0: — | 0 of 9 | 5.8% (21/363; 3.8–8.7) |
| Danon | 13 | 7 | 1 | 1 | 4 | 61.5% (8/13; 35.5–82.3) | 1: 100.0% (1/1; 20.7–100.0) | 1 of 12 | 6.1% (15/244; 3.8–9.9) |
| **All six** | 75 | 38 | 5 | 1 | 31 | **57.3% (43/75; 46.1–67.9)** | | 5 of 84 | |

[interim_paper.md §3.7b, Table 8c; omim_holdout_assessment.md §1]

- Counting the one notation-level match, recall is 58.7% (44/75; 47.4–69.1). [omim_holdout_assessment.md §1]
- Each allelic variant was placed in ClinVar through ClinVar's own OMIM cross-references or the RCV accessions OMIM prints (E-utilities, 2026-10-28), never by dbSNP id alone; OMIM labels use legacy protein numbering (ABCA1 labels sit 60 residues below the current transcript; LAMP2 LEU113TER is p.Leu147Ter). [interim_paper.md §3.7b]
- **Literature coverage, not reading, is the binding constraint.** Of the 84 papers OMIM cites as sources for these variants, 5 were extracted, 38 are in the corpus without an open copy, 38 were never returned by the searches, 3 not in corpus (screened unclear/other). Pooled over every OMIM-cited paper (288): 96 sit in the screened corpus with no open copy, 160 were never returned by the searches, 9 were extracted. The never-returned papers are mostly pre-1990 descriptions under earlier disease names and gene-biology papers outside scope. [interim_paper.md §3.7b, Table 8d; DECISIONS.md D-42]
- Where the source paper was extracted, 8 of 14 allelic variants were recovered from it; the misses are a table scrambled in PDF conversion (three SSADH variants, each recovered from five other papers) and two variants stated only in prose, kept verbatim with the right individuals and zygosity but with no key. [interim_paper.md §3.7b]
- **Patient level** (9 papers both cover; judged by Claude, not a panel member): 12 of 23 comparisons agree, 7 partial, 4 missed (all the scrambled SSADH table), none contradicts OMIM. Where they differ the run usually has less (a supplement not in the extraction text). One OMIM phenotype statement (mild autism in a 1998 SSADH source paper) is "not reported" in the run's rows, to be checked against the paper. [interim_paper.md §3.7b]
- **Tangier:** all 17 unrecovered allelic variants have no source paper in the run (1999–2003 gene-discovery papers, in the corpus and closed). [interim_paper.md §3.7b, Table 8e]
- OMIM's variants in ClinVar: every allelic variant but one (the moved 600065.0007) has a ClinVar record. The run's ClinVar-matched P/LP variants are mostly not OMIM allelic variants (39 of 193); the run holds 466 distinct genome-placed variants against OMIM's 75. Per disease, run P/LP variants that are OMIM allelic variants: HA20 26.9% (7/26), SSADH 5.5% (3/55), Tangier 28.6% (2/7), LAD-I 33.3% (12/36), AxD 25.0% (9/36), Danon 18.2% (6/33). 51 of the 350 extracted papers post-date the last edit of either OMIM entry for their disease. [interim_paper.md §3.7b, Table 8f]
- **OMIM is fallible too:** two allelic variants point to ClinVar records that do not match their own text (610045.0007 GLY441ARG linked to a synonymous change at another codon, while four extracted papers give c.1321G>A p.Gly441Arg; 610045.0002 linked to a deep-intronic record); 10 labels differ from ClinVar's protein change, 9 by legacy numbering only; the complex LAD-I allele 600065.0006 has a component ClinVar calls benign. [interim_paper.md §3.7b]
- **Gap candidates against OMIM:** all 215 checked by allele, cDNA, protein and notation token; 214 absent from OMIM; one, G-danon-001 (NM_002294.3:c.1097_1098del, PMID 30413001), collided with OMIM 309060.0001 by its deletion token. The paper places the deletion on LAMP2 exon 9b; the run had assumed the MANE transcript (exon 9a) because the paper named none. On the right transcript it is OMIM 309060.0001 / ClinVar 1410728 (uncertain significance). Withdrawn as a normalization artefact (D-43). [interim_paper.md §3.7b; DECISIONS.md D-43]
- OMIM's phenotype half (clinical synopses) is not assessed: the synopsis pages were not frozen. [interim_paper.md §3.7b]

#### 2.1.8 O3: gap candidates (stage 1 only)

| Disease | Tier-1 alleles | Absent from ClinVar | Gap candidates | Absent but every row failed gatekeeper | Only from ClinVar-cited papers | Only from reviews | Protein check differs | Papers per candidate 1 / 2 / 3+ | Authors' class | Reclassification (strong) |
|---|---|---|---|---|---|---|---|---|---|---|
| HA20 | 103 | 64 | **64** | 0 | 6 | 0 | 8 | 43 / 14 / 7 | 43 P/LP, 4 VUS, 14 not stated | 12 (6) |
| SSADH | 78 | 10 | **10** | 0 | 2 | 0 | 1 | 6 / 4 / 0 | 6 P/LP, 0 VUS, 4 not stated | 15 (4) |
| Tangier | 16 | 7 | **7** | 0 | 1 | 0 | 1 | 7 / 0 / 0 | 4 P/LP, 0 VUS, 3 not stated | 6 (0) |
| LAD-I | 129 | 84 | **82** | 2 | 66 | 34 | 10 | 76 / 6 / 0 | 4 P/LP, 0 VUS, 78 not stated | 7 (2) |
| AxD | 67 | 18 | **17** | 1 | 2 | 1 | 3 | 15 / 2 / 0 | 8 P/LP, 3 VUS, 6 not stated | 8 (2) |
| Danon | 73 | 38 | **35** | 3 | 7 | 0 | 2 | 27 / 6 / 2 | 16 P/LP, 0 VUS, 19 not stated | 5 (1) |
| **Five confirmatory** | 363 | | **151** | | | | | | | 41 (9) |
| **All six** | 466 | 221 | **215** | 6 | | | | | | 53 (15) |

[interim_paper.md §3.8, Table 11]

- Candidates by stage: 215 candidates (214 live after the OMIM check and D-43); adjudicated, approved, drafted, signed off, submitted, accepted: 0 each. Live by disease: HA20 64, SSADH 10, Tangier 7, LAD-I 82, AxD 17, Danon 34. [interim_paper.md §3.8; consolidated_runs_2026-11-15.md §3]
- All 215 were still absent by GRCh38 allele in the next ClinVar release (19 Oct 2026, snapshot 2026-10-21). [interim_paper.md §3.8]
- "Protein check" compares the paper's stated protein with the one VariantValidator predicts from the normalized cDNA (a pre-triage flag). Reclassification candidates are supported variants in ClinVar only as VUS or conflicting; "strong" (≥2 papers or ≥3 deduplicated people) is a proposed, exploratory rule. [interim_paper.md §3.8]
- **LAD-I's 82 need the most care:** 66 come only from papers ClinVar cites for *ITGB2* and 34 only from reviews, most from one mutation-update review (22134107) whose people are database accession numbers; a variant ClinVar cites a paper for but that is absent by allele is as likely a numbering or normalization slip as a true gap. [interim_paper.md §3.8, §3.12 LAD-I]
- **Evidence dossiers** for all 215 (case count and phenotype match, segregation, de novo status with parental testing, functional evidence, in-trans findings, variant type; each line with a PMID and a verbatim quote or "not reported"; no proposed classification): 4,725 quotes, all verbatim, 0 problems. Population frequency (PM2) is left to the panel because gnomAD is not reachable from the environment. [interim_paper.md §3.8]
- **Triage flags:** 152 of 215 candidates carry at least one keyword flag from the dossiers' concerns; the commonest, "possible same person twice" (77), matters for case counts, not for whether the variant exists. The dossier helpers named candidates that may not be gaps: G-ssadh-003 (a coordinate read literally from mixed exon/intron notation), G-axd-017 (c.54G>T called Gly18Val where c.53 is probably meant), G-lad1-077 (the paper cites an SCV accession not yet in the release), G-danon-002 (LAMP2B-numbered variants mapped to intronic MANE positions). [interim_paper.md §3.8]
- **Proposed same-person groups:** 19 groups in 4 diseases (HA20 12, Danon 5, AxD 1, LAD-I 1); if all were confirmed, 3.8% of HA20 identities would collapse and 0.2%–1.2% elsewhere (a lower bound; only the candidates' papers were examined). Nothing is merged: changing records after the freeze is a deviation and each group needs a person. [interim_paper.md §3.8]
- The 214 live candidates rest on 372 reported individuals. [plan_human_assessment_2026-11-15.md §3]
- Submission records are prepared as format-neutral pending records per panel-approved variant (`submissions/make_records.py`); none exists because nothing is approved. [interim_paper.md §3.8]

#### 2.1.9 O4: memorization probe and the state of the bias arm

**Memorization probe (exploratory).** 180 papers (30 per disease) stratified by first publication date against Claude Opus's documented cutoff (June 2026): 10 after, 51 recent (2024-07 to 2026-06), 119 older. Two black-box probes, run identically on both models; every Claude helper transcript was checked for forbidden tool calls (none). Scored against the full-text extraction, never ClinVar. One item (Tangier 33346003) excluded because its opening was publisher boilerplate.

| Stratum | Papers | Model | Closed book: specific / guess / none | Papers with a variant hit | Variants given (hits) | Phenotype terms given, mapped, hits | Completion: mean ROUGE-L F1 | Mean 5-gram share | Longest run (words) | Runs ≥ 8 words |
|---|---|---|---|---|---|---|---|---|---|---|
| after cutoff | 10 | Claude | 0 / 6 / 4 | 0 | 0 (0) | 24, 20, 12 | 0.158 | 0.0000 | 4 | 0 |
| after cutoff | 10 | DeepSeek | 0 / 3 / 7 | 0 | 0 (0) | 9, 1, 1 | 0.137 | 0.0000 | 4 | 0 |
| recent | 51 | Claude | 0 / 44 / 7 | 2 | 9 (2) | 163, 132, 68 | 0.190 | 0.0042 | 7 | 0 |
| recent | 51 | DeepSeek | 0 / 11 / 40 | 1 | 4 (1) | 26, 2, 1 | 0.154 | 0.0017 | 6 | 0 |
| older | 119 | Claude | 4 / 95 / 20 | 2 | 3 (2) | 306, 248, 153 | 0.190 | 0.0061 | 11 | 3 |
| older | 119 | DeepSeek | 0 / 27 / 92 | 2 | 9 (2) | 68, 31, 23 | 0.148 | 0.0021 | 7 | 0 |

[interim_paper.md §3.9, Table 12]

- Claude claimed specific recall for 4 of 180 papers, all older, each for phenotypes only; 4 papers had a variant hit, all labelled guesses and all recurrent variants. DeepSeek claimed specific recall for none and answered "none" for 139 papers. The three completions with a run of 8+ matching words are all formulaic consent statements. Totals over 180 papers: Claude specific 4 / guess 145 / none 31, variants given 12 (4 hits), phenotype terms 493 / 233 matching; DeepSeek 0 / 41 / 139, 13 (3), 103 / 25. Neither model reproduced the papers' variants or text. The after-cutoff stratum has 10 papers (little power); black-box probes can miss memorization that changes extraction without surfacing as recall; the open-weight checkpoint's cutoff is not known, so its strata carry no meaning. [interim_paper.md §3.9; openweight_comparison_findings.md §7]

**Frequency deviation: not started (waits on a person).** Four open comparators are fetched and a listing sheet exists for each (AxD: UK Biobank genotype-first cohort; Danon: prospective cohort PMID 41121270; HA20: a multicentre preprint; SSADH: natural-history registry PMID 30656189); 3 candidate comparators are paywalled and left out (D-32); LAD-I and Tangier have no comparator and are out of the bias arm (D-35). The deviation script is written and tested on synthetic input only. [interim_paper.md §3.9]

- **Comparator-overlap tags (2026-11-15; D-48).** Tags cover 1,772 phenopackets (SSADH 464, HA20 781, Danon 527). Registered SSADH: of 311 records with a disease term, 115 are probable members of the comparator registry (94 from its natural history study and biorepository), 108 possible, 63 no link. Registered HA20: 9 probable, 87 possible. Danon: nobody tagged as in the cohort. AxD left untagged on purpose (its open comparator is UK Biobank carriers). Effect of D-48 on the primary denominators: SSADH 363 → 311 with a disease term → 196 after removal; HA20 769 → 447 → 438; Danon 505 → 322, no one removed. Batch 2 SSADH: of 63 records with a disease term, 2 stated, 49 probable, 4 possible, 2 outside, 6 citation-only. No comparator sheet is filled and no literature frequency has been computed. [addendum_d47_batch2_findings.md For the bias arm; DECISIONS.md D-48]

#### 2.1.10 Claude vs open-weight model (D-10; HA20 and SSADH, run 2026-10-21)

Values are Claude / open-weight. Claude's cost is an estimate from helper tokens; the open-weight cost is what the host reported for final attempts.

| Disease | Papers | Values asserted | Span-not-found rate | Values with no quote | Judged unsupported (gatekeeper v4) | …among claims with a quote | HGVS recall, tiers 1+2 | Variant keys shared/union | Checklist agreement (shared cells) | Feature rows | Cost per paper, median | Wall-clock per paper, median (min) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| HA20 | 85 | 67,863 / 55,317 | 0.00% / 3.86% | 0 / 2,003 | 0.20% / 8.64% | 0.20% / 2.28% | 26.9% (21/78; 18.3–37.7) / 19.2% (15/78; 12.0–29.3) | 261/294 (88.8%) | 95.9% of 10,720 | 5,079 / 2,753 | $1.08 / $0.07 | 2.9 / 20.9 |
| SSADH | 40 | 31,370 / 33,521 | 0.00% / 2.98% | 0 / 991 | 0.38% / 6.14% | 0.38% / 2.03% | 14.6% (23/158; 9.9–20.9) / 15.2% (24/158; 10.4–21.6) | 157/166 (94.6%) | 97.6% of 6,716 | 1,683 / 1,439 | $1.19 / $0.07 | 2.9 / 19.2 |

[interim_paper.md §3.10, Table 13; openweight_comparison_findings.md §2]

| Gatekeeper v4 measure | HA20 Claude | HA20 open-weight | SSADH Claude | SSADH open-weight |
|---|---|---|---|---|
| Model claims judged | 23,129 | 18,084 | 9,759 | 10,372 |
| Supported | 22,683 | 15,250 | 9,480 | 9,020 |
| Partially supported | 400 | 1,240 | 242 | 715 |
| Unsupported | 46 | 1,563 | 37 | 637 |
| Span not found | 0 | 31 | 0 | 0 |
| Unsupported rate (exact 95% CI) | 0.20% (0.15–0.27) | 8.64% (8.24–9.06) | 0.38% (0.27–0.52) | 6.14% (5.69–6.62) |
| Anything but supported | 1.93% (1.75–2.11) | 15.67% (15.14–16.21) | 2.86% (2.54–3.21) | 13.04% (12.39–13.70) |
| Claims with an empty quote | 0 | 1,503 | 0 | 591 |
| …judged unsupported | 0 | 1,185 | 0 | 438 |
| Unsupported rate, claims with a quote | 0.20% (0.15–0.27) | 2.28% (2.06–2.52) | 0.38% (0.27–0.52) | 2.03% (1.76–2.33) |
| Papers with an unsupported claim | 15 | 71 | 7 | 37 |

[openweight_comparison_findings.md §6]

- Other measures (Claude / open-weight): tier-1 overlap HA20 37.9% (39/103) / 41.1% (37/90; 31.5–51.4), SSADH 87.2% (68/78) both; classification agreement HA20 82.8% (24/29) / 90.0% (18/20; 69.9–97.2), SSADH 91.8% (45/49) / 88.5% (46/52; 77.0–94.6); individuals HA20 811 / 742, SSADH 421 / 467; identities 769 / 716, 363 / 407; quote given but not in the paper 0 / 133 (HA20), 0 / 8 (SSADH); cells not in the schema's {value, span} shape 0 / 45, 0 / 6; cost all papers $101.42 / $10.25 (HA20), $52.79 / $5.54 (SSADH). [openweight_comparison_findings.md §2]
- The two models found largely the same target-gene variants (Claude only 28, open-weight only 5 in HA20; 4 and 5 in SSADH); their HGVS recall overlaps within the intervals. The open-weight model wrote 54% (HA20) and 86% (SSADH) as many phenotypic-feature rows as Claude. Median open-weight cost per paper was 1/15 (HA20) and 1/18 (SSADH) of Claude's estimate; counted with failed attempts the open-weight runs cost $16.34 to $20.35 for 125 papers against Claude's $154.21 estimate. The median open-weight paper took 7.3× (HA20) and 6.7× (SSADH) as long. Claims with a quote were judged unsupported 11× (HA20) and 5× (SSADH) Claude's rate. [openweight_comparison_findings.md §3, §5]
- Commonest open-weight failures (from the gatekeeper helpers' reasons): `is_proband` = false with no quote; checklist statuses with no quote; a gene symbol quoted from a background sentence; an age at examination given as onset; parents' variant fields quoted from the proband's sentence; hedged findings recorded as observed. [openweight_comparison_findings.md §6]
- Cautions: the judge is Claude, which may not be neutral between a Claude and a non-Claude extraction; helpers did not all treat empty quotes the same way (236 HA20 and 144 SSADH empty-quote claims were judged supported against the row's quote), so the open-weight unsupported rate is, if anything, a little low; the blinded human audit (the registered measure) is not drawn. [openweight_comparison_findings.md §6; interim_paper.md §3.10]
- Scaffold differences, as the plan requires them stated: the open-weight loop had file tools only (no shell); no repair passes for empty quotes; three harness fixes landed during the run (retries after dropped connections; a JSON parse check on writes, v2; a resume request after a cut-off reply, v3, never needed), approved by Dr. Lin on 2026-10-21. Final outputs by harness version: HA20 v1 72, v2 10, v3 3; SSADH v2 39, v3 1. 13 HA20 and 1 SSADH paper were re-run from a clean start; retried calls in final attempts HA20 36, SSADH 17. One-paper pilot (PMID 37324276): same 4 variants as Claude, checklist agreement 0.95 on 80 shared cells, $0.069. Scope: two diseases, one open-weight model, one provider; not general findings. [openweight_comparison_findings.md §4; DECISIONS.md D-10 hosting entry]

#### 2.1.11 Exploratory genotype–phenotype maps (GPSEA)

Fisher exact tests with Benjamini–Hochberg correction at 0.05; only individuals with a GRCh38-placed variant and at least one phenotype; zygosity for untyped calls is an analysis assumption only (the records keep "not reported").

| Disease | Comparison | Individuals | Terms tested | Significant (BH 0.05) |
|---|---|---|---|---|
| HA20 | truncating vs missense | 217 | 11 | 0 |
| SSADH | biallelic truncating/truncating vs truncating/other vs other/other | 77 | 9 | 0 |
| Tangier | biallelic, as above | 16 | 0 | 0 |
| LAD-I | biallelic, as above | 38 | 3 | 0 |
| AxD | hotspot R79/R88/R239 vs other missense | 83 | 14 | 0 |
| Danon | truncating vs missense | 130 | 9 | 2: arrhythmia (truncating 57/59, missense 4/7; p_BH 0.035); ventricular arrhythmia (45/47 vs 3/6; p_BH 0.035) |
| Danon | sex (males hemizygous, females heterozygous) | 130 | 10 | 3: proximal muscle weakness (female 1/28, male 11/25; p_BH 0.005); left ventricular hypertrophy (25/33 vs 41/41; p_BH 0.005); hypertrophic cardiomyopathy (19/24 vs 34/34; p_BH 0.031) |

- Danon reproduces the published sex difference; the papers overlap with the published series, so this is a reproduction check, not independent replication. The truncating-vs-missense arrhythmia signal rests on 6–8 missense carriers and is a lead only. Tangier has too few placeable, phased genotypes to test. LAD-I deduplication accuracy against a review's duplicate cases is not computable. [interim_paper.md §3.11, Table 14]

#### 2.1.12 Input problems the helpers reported (registered six)

- SSADH: PMID 14635103 Table 2 scrambled in conversion (about 12 of 54 families extracted); 38499966 table garbled, supplements S1/S2 missing. Tangier: 26713019 and 27011649 tables published as images. LAD-I: 33391282 supplement Table S1 cut at 60,000 characters, so patients P75–P127 have no clinical rows; 30 of its patients were reported before without names. AxD: 34046764 Table 1 caption only; 32126152 Table S1 missing; 39420046 supplement arrived after extraction (D-39). Danon: 23571262, 30929317, 42366573 tables transposed or garbled; 25228319 supplemental tables 1–2 missing. Gene-name spellings "ITGβ2", "ITGß2" and "CD18" cover 148 LAD-I variant rows; the matcher accepts them. These are helper-reported and not verified by a person; they bound what extraction could see and are not counted in any metric. [interim_paper.md §3.1, §3.12]

### 2.2 The extension five (D-52; runs of 2026-11-14 to 2026-11-15)

- Pre-registered as an addendum (`preregistration/addendum_extension_v1.md`, v1.0, 2026-11-14) committed before any extension extraction; same frozen pipeline instantiated per disease (D-38), same Stage 4 (D-40, D-43). Not extended: O4 (bias arm), the open-weight comparison, the OMIM assessment and the completeness catalogue. Results are reported beside, never merged into, the registered six; any pooled 12-disease figure is exploratory. [addendum_extension_v1.md; DECISIONS.md D-52]
- Eligible primary reports with open full text after full-text screening: GAMT 22, PAPA 32, ATS 34, Blau 66, LCAT 47 (all above the bar of 15); papers included and run: Blau 68, LCAT 50, ATS 34, PAPA 34, GAMT 23 (209). Supplements were fetched from Europe PMC or, when its endpoint failed (2026-11-14), from NLM's PMC Cloud Service. [DECISIONS.md D-52 decision log]

| Disease | Papers | People extracted | Identities | With a variant in the gene | Phenopackets (valid) | Gatekeeper unsupported or not found (95% CI) |
|---|---|---|---|---|---|---|
| GAMT | 23 | 380 | 365 | 279 | 365 (0 errors) | 0.63% (63/9981; 0.49–0.81) |
| PAPA | 34 | 320 | 311 | 213 | 311 (0 errors) | 0.35% (32/9146; 0.24–0.49) |
| ATS | 34 | 157 | 152 | 84 | 152 (0 errors) | 0.86% (54/6268; 0.65–1.12) |
| Blau | 68 | 513 | 507 | 358 | 507 (0 errors) | 0.25% (39/15476; 0.18–0.34) |
| LCAT | 50 | 283 | 282 | 162 | 282 (0 errors) | 0.45% (34/7623; 0.31–0.62) |

[extension_report.md §1]

| Disease | Papers repeated (seed 20261020) | Variant agreement (strings) | Variant agreement (normalized keys) | Feature agreement | Checklist agreement | cDNA descriptions normalized | Phenotype rows bound to HPO |
|---|---|---|---|---|---|---|---|
| GAMT | 3 | 0.93 | 0.98 | 0.72 | 0.99 | 95.1% of 122 | 95.7% |
| PAPA | 4 | 0.90 | 1.00 | 0.80 | 0.99 | 72.2% of 18 | 92.7% |
| ATS | 4 | 1.00 | — | 0.72 | 1.00 | 100.0% of 45 | 93.2% |
| Blau | 7 | 0.82 | 0.93 | 0.63 | 0.99 | 97.4% of 38 | 90.5% |
| LCAT | 5 | 0.75 | 1.00 | 0.53 | 0.98 | 91.3% of 69 | 90.5% |

- Blau and LCAT fall below the 0.9 flag for string-level variant agreement; normalized keys agree better (LCAT 1.00, Blau 0.93): most differences are in how a description was copied, the rest in which people a review table was taken to cover (Blau 36915122: 16 vs 19 people). [extension_report.md §2]
- Child-table label quotes were filled by script (copied from the person's own individuals row only when exactly one row has that label; logged); label claims are bookkeeping claims the gatekeeper does not judge. No `isoform_sensitive` block was added for GAMT or PSTPIP1. [DECISIONS.md D-52 decision log]

**O2 (snapshot 2026-11-14; ClinVar variant_summary of 09 Nov 2026; Blau with the D-53 fallback).**

| Disease | Gene | HGVS recall, tier 1 | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement | Condition names disease | HPO annotation recall | Terms in ≥2 people matching | PMIDs ClinVar cites |
|---|---|---|---|---|---|---|---|---|---|
| GAMT | 100.0% (279/279; 98.6–100.0) | 69.2% (18/26; 50.0–83.5) | 69.2% (18/26; 50.0–83.5) | 90.1% (73/81; 81.7–94.9) | 87.5% (14/16; 64.0–96.5) | 97.3% (73/75; 90.8–99.3) | 83.3% (25/30; 66.4–92.7) | 30.8% (36/117; 23.1–39.6) | 47.8% (11/23; 29.2–67.0) |
| PAPA | 98.6% (213/216; 96.0–99.5) | 57.1% (8/14; 32.6–78.6) | 71.4% (10/14; 45.4–88.3) | 90.9% (10/11; 62.3–98.4) | 87.5% (7/8; 52.9–97.8) | 90.5% (19/21; 71.1–97.3) | 81.2% (13/16; 57.0–93.4) | 9.9% (16/161; 6.2–15.5) | 23.5% (8/34; 12.4–40.0) |
| ATS | 96.6% (84/87; 90.3–98.8) | 80.0% (16/20; 58.4–91.9) | 80.0% (16/20; 58.4–91.9) | 96.3% (26/27; 81.7–99.3) | 90.0% (9/10; 59.6–98.2) | 92.3% (24/26; 75.9–97.9) | 80.9% (38/47; 67.5–89.6) | 25.1% (42/167; 19.2–32.2) | 20.6% (7/34; 10.3–36.8) |
| Blau | 99.2% (358/361; 97.6–99.7) | 13.6% (3/22; 4.7–33.3) | 13.6% (3/22; 4.7–33.3) | 63.0% (17/27; 44.2–78.5) | 78.9% (15/19; 56.7–91.5) | 90.5% (19/21; 71.1–97.3) | 85.7% (18/21; 65.4–95.0) | 10.2% (24/236; 6.9–14.7) | 22.1% (15/68; 13.8–33.3) |
| LCAT | 100.0% (162/162; 97.7–100.0) | 36.8% (7/19; 19.1–59.0) | 42.1% (8/19; 23.1–63.7) | 46.0% (23/50; 33.0–59.6) | 60.0% (3/5; 23.1–88.2) | 80.0% (24/30; 62.7–90.5) | 100.0% (12/12; 75.8–100.0) | 15.5% (16/103; 9.8–23.8) | 26.0% (13/50; 15.9–39.6) |

[extension_report.md §3; analysis/extension/o2/o2_summary.md]

- Without ClinVar-cited papers (overlap; classification): GAMT 90.1% (73/81); 87.5% (14/16). PAPA 85.7% (6/7); 87.5% (7/8). ATS 95.5% (21/22); 100.0% (8/8). Blau 64.0% (16/25); 76.5% (13/17). LCAT 41.2% (7/17); 60.0% (3/5). [analysis/extension/o2/o2_summary.md]
- **Blau and NOD2 numbering (D-53).** Under the registered rule 19 Blau cDNA descriptions failed on MANE (NM_001370466.1) with a reference mismatch because the papers use legacy NM_022162.3 numbering; with the fallback all 19 place, each agreeing with the paper's own protein, 27 residues higher. Registered rule vs fallback: HGVS recall tier 1 4.5% (1/22) vs 13.6% (3/22); overlap 61.5% (8/13) vs 63.0% (17/27); classification 72.7% (8/11) vs 78.9% (15/19); cDNA normalized 18 → 37 of 38. Of the 19 recall misses that remain, 17 come from papers whose extraction holds only protein changes in legacy numbering (27 residues above ClinVar's MANE numbering): numbering misses, not reading errors. [extension_report.md §3; DECISIONS.md D-53 deviation] (The D-53 decision-log entry says "20 of the 21 misses"; that count was written before the fallback's re-run and is superseded by the report's 17 of 19.)

**O3 stage 1.**

| Disease | Tier-1 alleles | Absent from ClinVar | Gap candidates | Withdrawn (D-53) | Left for the panel | Registered rule (before D-53) | Only from ClinVar-cited papers | Only from reviews |
|---|---|---|---|---|---|---|---|---|
| GAMT | 81 | 8 | 8 | 0 | 8 | 8 | 0 | 0 |
| PAPA | 11 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| ATS | 27 | 1 | 1 | 0 | 1 | 1 | 0 | 0 |
| Blau | 27 | 10 | 9 | 1 | 8 | 5 | 1 | 0 |
| LCAT | 50 | 27 | 26 | 1 | 25 | 26 | 17 | 18 |

[extension_report.md §4]

- 45 candidates, 2 withdrawn, 43 left for the panel. ClinVar re-check against the same snapshot: 45 checked, 0 now in ClinVar. OMIM not checked. Evidence dossiers 45 of 45; 869 quotes, all verbatim, 0 problems. [extension_report.md §4]
- **Withdrawn (D-53, 2026-11-15; decided by Claude under Dr. Lin's delegation):** G-blau-008 (16:50711530:T:C): legacy c.1538T>C (p.Met513Thr) read on MANE, where the reference base also matches, gives p.Leu513Pro, which no paper describes; on MANE the stated allele is c.1457T>C p.Met486Thr. G-lcat-001 (4:67583648:T:C): placed on chromosome 4 because the paper (PMID 31684177) states a transcript (NM_012108.3) that is not an LCAT transcript; the paper's change is p.Ile202Thr in LCAT. Rows and dossiers are kept. [extension_report.md §4]
- LCAT: 17 of 26 candidates come only from papers ClinVar cites and 18 only from reviews (mostly table rows of one systematic review, PMID 34256778, with no case description). [extension_report.md §4]
- Candidates rest on 72 individuals. [plan_human_assessment_2026-11-15.md §4]
- **O1X audit sample:** 250 claims, seed 47250, from a pool of 46,363, drawn after all five runs and gatekeeper passes and before any extension concordance was computed; allocation GAMT 51, PAPA 48, ATS 33, Blau 80, LCAT 38. **O2X triage sample:** all 48 misses (fewer than 50), seed 72650; 2 stopped being misses after the D-53 fallback, leaving 46 in the assessment plan. [extension_report.md §5; DECISIONS.md D-52; plan_human_assessment_2026-11-15.md §4]
- Open items the helpers raised: SURF patients with NOD2 variants and a healthy-control carrier (41357180); people with a diagnosis but no variant in several Blau and LCAT papers; a PDF-only paper whose genetic supplementary tables were unavailable (38180755); a duplicate-publication pair in GAMT (38020815, 39006040). [extension_report.md §6]
- Five extension runs have a launch record but no `manifest.json` (finish time, document list). [consolidated_runs_2026-11-15.md §7]

### 2.3 Majeed syndrome (exploratory; run `pv1s-majeed`, 2026-11-15)

- **Corpus.** 1319 PubMed records from every search method (PubMed with Mondo synonyms and no case filter, Europe PMC including full text, OpenAlex, LitVar2 by gene symbol only, backward references, forward citations and similar articles); 131 passed title/abstract screening; 79 had open full text, including copies found by hand; 22 eligible after full-text screening (17 primary reports). Run on 24 documents: the eligible PubMed papers plus two eligible records with no PMID (N66, a 2011 conference abstract; N88, a 2025 paper); a preprint of a paper already in the set was left out. 5 of the 20 eligible papers before the hand-found copies were found only through full-text search (cohort papers or reviews whose abstract does not name the disease). No ClinVar or OMIM citation list was used. [majeed_pv1s_findings.md Corpus; DECISIONS.md 2026-11-15 Majeed search entry] (The search entry's "70 had open full text; 20 eligible; 61 corpus papers have no open copy" is superseded by the report's figures after the hand-found copies: 79, 22, and 52.)
- **Extraction and gatekeeper.** Span check 100.0% verbatim, 0 problems after one repair-only resume. 164 rows, 158 identities after 6 merges; 141 with an LPIN2 variant row. Gatekeeper v4 on 5161 model claims: supported 4971, partially supported 155, unsupported 35; unsupported or not found 0.7% (35/5161; 95% CI 0.5–0.9); not fully supported 3.7% (190/5161; 95% CI 3.2–4.2). Four gatekeeper chunks were judged again by fresh helpers because the first helpers assigned verdicts with a script; the re-judgement changed verdicts (e.g. 14 spine-involvement exclusions became partially supported because whole-body MRI was not done in most patients). [majeed_pv1s_findings.md]
- **Stage 4.** 62 distinct variant descriptions; 67.7% normalized or corrected (91.3% of cDNA descriptions) on MANE NM_001375808.2; HPO 71.1% of feature rows bound; 158 phenopackets, all schema-valid; 100 with an interpretation; 5 observed/excluded conflicts. [majeed_pv1s_findings.md]
- **O2 (snapshot 2026-11-15, ClinVar release of 09 Nov 2026).** Gene correct 100.0% (141/141; 97.3–100.0); overlap 50.0% (12/24; 31.4–68.6); HGVS recall tier 1 6.6% (5/76; 2.8–14.5), tiers 1+2 10.5% (8/76; 5.4–19.4), low mainly because ClinVar cites some corpus papers for variants those papers do not report; classification agreement 62.5% (5/8; 30.6–86.3); condition names the disease 100.0% (19/19; 83.2–100.0). OMIM not checked. [majeed_pv1s_findings.md]
- **O3 stage 1.** 12 gatekeeper-supported alleles absent from ClinVar and 1 reclassification candidate (NM_001375808.2:c.2207G>A p.(Arg736His), ClinVar conflicting). ClinVar re-check (same 09 Nov 2026 release, the newest available): none of the 12 in ClinVar. Candidates rest on 22 individuals.

| Candidate | HGVS (MANE) | Predicted protein | Protein check | Papers | Authors' class |
|---|---|---|---|---|---|
| G-majeed-001 | c.2534del | p.(Gly845GlufsTer9) | agrees | N88 | P/LP |
| G-majeed-002 | c.2349del | p.(Glu784ArgfsTer8) | agrees | 41113563 | P/LP |
| G-majeed-003 | c.2327+3A>G | p.? | no stated protein | 41113563 | P/LP |
| G-majeed-004 | c.2241_2243delinsGG | p.(Tyr747TerfsTer) | differs (stated Y747*, predicted Y747fs) | 27252506 41113563 | not stated |
| G-majeed-005 | c.2206C>T | p.(Arg736Cys) | agrees | 33993107 41113563 | P/LP |
| G-majeed-006 | c.2174+4_2174+5del | p.? | no stated protein | 33993107 41113563 | VUS |
| G-majeed-007 | c.2144_2145dup | p.(Ile716ValfsTer2) | agrees | 39255247 | P/LP |
| G-majeed-008 | c.2041del | p.(Trp681GlyfsTer14) | agrees | 33993107 41113563 | P/LP |
| G-majeed-009 | c.1966A>G | p.(Asn656Asp) | agrees | N88 | P/LP |
| G-majeed-010 | c.1961G>A | p.(Gly654Asp) | agrees | 33993107 41113563 | VUS |
| G-majeed-011 | c.1693_1694del | p.(Glu565LysfsTer15) | agrees | 39255247 | P/LP |
| G-majeed-012 | c.1620+5G>C | p.? | no stated protein | 33993107 41113563 | P/LP |

[majeed_pv1s_findings.md; DECISIONS.md D-54 decision log; plan_human_assessment_2026-11-15.md §4]

- **Review material (D-54).** Audit sample 27 claims (seed 54250; pool 4,971; size = the extension audit's sampling fraction applied to Majeed's pool), too small for any pass/fail rule; triage sample 50 of the run's 68 ClinVar misses (seed 72650); dossiers for 10 of 12 candidates (235 quotes, all verbatim); G-majeed-001 and G-majeed-009 rest on record N88 alone, whose text could not be restored (the publisher answers automated requests with a challenge page). Majeed's ClinVar comparison and gap candidates were computed and read before its audit sample was drawn, unlike the registered and extension audits. [DECISIONS.md D-54]
- **Licences (D-51).** 18 documents openly licensed, 6 not; their extraction outputs and the 27 phenopackets that quote them are kept out of the repository (131 phenopackets public); 4 of the 10 dossiers are public. [majeed_pv1s_findings.md; consolidated_runs_2026-11-15.md §3]
- **Limits.** No human audit; 52 corpus papers have no open copy, including the founding reports; several patients appear in more than one paper and identity counts are upper bounds. [majeed_pv1s_findings.md Limits]

### 2.4 Corpus addendum of free copies (D-47), reported beside the registered results

- **Why.** 1,075 papers passed title/abstract screening for the registered six but had no full text; for 212 of them Europe PMC lists a free or open-access copy outside PMC. On 2026-11-14 a headless browser (no user-agent spoofing; challenge pages recorded and not interacted with) saved 29; of the other 183, 131 stopped at a challenge page (PMC reCAPTCHA, Cloudflare on europepmc.org and most large publishers), 7 gave HTTP errors and 45 gave no PDF from the listed links; 69 of the 183 have a PMC copy that is free to read but whose publisher withholds the XML. [DECISIONS.md D-47 deviation]
- **Rules.** Same frozen pipeline (D-38, D-40, D-43; pinned HPO and Mondo, sha256 checked); Docling PDF conversion; screening decisions kept apart from the registered manifest; separate runs; no `pv1-<d>` file changed; every registered outcome stays computed on the registered corpus; the O1 sample is not redrawn, so addendum claims are covered by the gatekeeper only; no O2, O3, audit sample or matching of people against the registered runs yet (after the 2026-11-30 cut-off); no supplements fetched for addendum papers. [DECISIONS.md D-47; addendum_d47_batch1_findings.md; consolidated_runs_2026-11-15.md §7]

**Batch 1 (`pv1a-<d>`; the 29 browser-saved copies; 2026-11-15; tables as corrected the same day).**

| Disease | Free copies saved | Included | Values quoted, all verbatim | Individual rows | Judged claims | Unsupported (exact 95% CI) | Not fully supported | Phenopackets (with interpretation) |
|---|---|---|---|---|---|---|---|---|
| HA20 | 2 | 1 | 189 | 3 | 49 | 0 (0.0%–7.3%) | 0.0% | 3 (1) |
| AxD | 3 | 3 | 781 | 7 | 309 | 4: 1.3% (0.4%–3.3%) | 2.6% | 7 (3) |
| LAD-I | 7 | 6 | 2454 | 28 | 880 | 7: 0.8% (0.3%–1.6%) | 3.9% | 28 (11) |
| SSADH | 3 | 3 | 1092 | 14 | 349 | 0: 0.0% (0.0%–1.1%) | 7.2% | 14 (0) |
| Tangier | 14 | 10 | 4483 | 63 | 1262 | 60: 4.8% (3.6%–6.1%) | 9.5% | 63 (4) |
| **Total** | **29** | **23** | **8999** | **115** | **2849** | **71: 2.5%** | | **115 (19)** |

[addendum_d47_batch1_findings.md Results, Follow-up]

- Superseded: the first batch-1 figures (8,366 quoted values; 2,653 judged claims, 71 unsupported, 2.7%; 106 phenopackets, 11 with an interpretation) changed after the publisher PDF of one open-access LAD-I paper (PMID 32154133) replaced a web page without its tables (5 individuals without variants → 14 individuals, 5 now with ITGB2 variants) and after D-49. [addendum_d47_batch1_findings.md Follow-up; DECISIONS.md D-47 amendments]
- Six exclusions: 30838383 (review without new individuals), 9312170, 8432861, 36876364 (not the disease), 12373902, 33380124 (not English). No person has checked them. [addendum_d47_batch1_findings.md Results, Review item 6]
- Of 115 phenopackets: 85 with a disease entry, 30 without any phenotypic feature, 19 with an interpretation. Most of the gain is phenotype-only: 14 of the 23 included papers print no variant (1970s–1980s Tangier papers predating gene discovery, enzyme- or urine-diagnosed SSADH, an MRI-only AxD case). [addendum_d47_batch1_findings.md What to take, Follow-up]
- **Unsupported claims concentrate in Tangier** (60 of 1,262), from one pattern: values for a named person inferred from statements about a group in 1970s biochemistry papers (two 1977 papers 25 each, a 1982 paper 9, a 1999 paper 1). The four AxD unsupported claims are hedged MRI statuses (the frozen gap). LAD-I's seven are variant fields recorded for a carrier mother from a sentence about the patient. The gatekeeper caught these and phenopackets drop them, but the extraction made them. [addendum_d47_batch1_findings.md]
- **Gatekeeper procedure.** Of 31 gatekeeper helpers, 11 had a verdict-writing script refused (10 chunks); the final verdict file was written by a helper's own script in 20 cases and row by row in 11. Seven chunks were judged twice (802 claims, 796 agreeing; second judgment is the record, always stricter where they differ). Three chunks with a refused script their helpers did not report were judged once only. In one 1977 Tangier paper split into two chunks, the same sentence was judged unsupported (25 claims) in one chunk and supported (11) in the other; all 36 are left for a person. [addendum_d47_batch1_findings.md Process notes, Review]
- **Not deduplicated:** seven printed labels recur in two Tangier papers each, so at least seven of the 63 Tangier records repeat a person. Two Tangier scans kept fewer than 90% of the PDF's words (78% and 82%). [addendum_d47_batch1_findings.md Review]
- Cost about $61 by session readings ($2.65 per included paper). [addendum_d47_batch1_findings.md; addendum_d47_batch2_findings.md Cost]

**Batch 2 (`pv1a2-<d>`; 72 free copies downloaded on 2026-11-14 in Chrome driven by Claude computer use, no CAPTCHA solved; routes PMC 69, publisher free 2, repository 1; run 2026-11-15).**

| Disease | Free copies received | Included | Values quoted, all verbatim | Individual rows | Judged claims | Unsupported (exact 95% CI) | Not fully supported | Phenopackets (with interpretation) |
|---|---|---|---|---|---|---|---|---|
| HA20 | 3 | 2 | 697 | 9 | 220 | 7: 3.2% (1.3%–6.4%) | 8.6% | 9 (5) |
| AxD | 31 | 26 | 17253 | 196 | 5947 | 14: 0.2% (0.1%–0.4%) | 3.5% | 196 (109) |
| Danon | 5 | 5 | 2509 | 22 | 1018 | 3: 0.3% (0.1%–0.9%) | 3.0% | 22 (8) |
| LAD-I | 7 | 6 | 3188 | 41 | 997 | 9: 0.9% (0.4%–1.7%) | 3.4% | 41 (6) |
| SSADH | 13 | 9 | 6020 | 87 | 1700 | 14: 0.8% (0.5%–1.4%) | 2.6% | 87 (8) |
| Tangier | 13 | 11 | 6946 | 91 | 2108 | 6: 0.3% (0.1%–0.6%) | 6.6% | 91 (18) |
| **Total** | **72** | **59** | **36613** | **446** | **11990** | **53: 0.4%** | | **446 (154)** |

[addendum_d47_batch2_findings.md Results]

- Superseded: 153 interpretations when the report was written; 154 after the D-49 Stage 4 re-run of Tangier on 2026-11-15. Addendum total (plain sum): 115 + 446 = 561 phenopackets, 19 + 154 = 173 with an interpretation; 82 papers. [addendum_d47_batch2_findings.md; consolidated_runs_2026-11-15.md §7]
- Strict reading: in 45 claims the helper recorded that the quote was about another person but judged "partially supported" where gatekeeper v4 says unsupported (Tangier 43, HA20 2). Counted strictly, batch 2 has 98 of 11,990 unsupported (0.8%): Tangier 49 of 2,108 (2.3%), HA20 9 of 220 (4.1%); the same strict count on the registered run gives 0.5% (393 of 80,948). The first version of the report counted 12 such claims, not 45. [addendum_d47_batch2_findings.md point 3, Review; DECISIONS.md D-47]
- HA20's 7 unsupported: three hedged liver-histology statuses and four pathogenicity values taken from an abstract sentence about the study's variants as a group. [addendum_d47_batch2_findings.md point 3]
- **A quarter of the records hold identity fields only:** 322 of 446 carry a disease term; 158 have no phenotypic feature; 115 have neither a feature nor an interpretation (SSADH 47 of 87, LAD-I 28 of 41, AxD 20, Tangier 17, Danon 3, HA20 0): 26% identity-only, against 17% in the registered run (485 of 2,836) and 19% in batch 1 (20 of 106, counted before the batch-1 correction). 21 of the 59 included papers have no variant row. [addendum_d47_batch2_findings.md points 1–2]
- **Not deduplicated:** reconcile merged nobody in any batch-2 run (PDF-converted papers carry no JATS reference list); several papers re-tabulate earlier published patients; known duplicates inside the batch were not merged. Patient counts must not be added to registered counts without deduplication by hand. [addendum_d47_batch2_findings.md point 4]
- **Conversion damage:** four papers keep less than 90% of their PDF words (one at 79% lost its abstract, introduction and methods); ">" printed as "." in cDNA strings in at least four papers; "+"/"−" printed as "1"/"2" in four papers, where helpers recorded cells as not reported; four scrambled or rotated tables; per-patient supplement data lost for four papers. Of 118 variant descriptions, 40 normalized (plain sum of the Stage 4 column). [addendum_d47_batch2_findings.md Conversion, point 5]
- Gatekeeper procedure: 8 chunks judged twice after refused bulk-write scripts (1,192 claims, 1,191 agreeing). Span repairs by repair-only resumes in 5 papers; `span_check` then 0 problems. 23 observed/excluded conflicts. A re-run of every scripted step reproduced every output byte-identically; 36 claims drawn from all-supported chunks were read against their quotes and none looked wrongly supported. Quotes reproduce a median 17% of each paper's converted text, at most 36%. [addendum_d47_batch2_findings.md Process notes, Review]
- Cost about $153.69 by session readings (about $2.60 per included paper); at the final reading the account's seven-day limit had been reached and overage was in use. 111 papers remain not retrieved. [addendum_d47_batch2_findings.md Cost, Not done]

### 2.5 What is prepared for people, and what has come back

| Disease | Audit sample (claims) | ClinVar-miss triage items | Gap candidates for the panel | Dossiers written |
|---|---|---|---|---|
| HA20 | 72 (sample of 250, seed 40250) | 14 | 64 | 64 of 64 |
| AxD | 44 (seed 40250) | 4 | 17 | 17 of 17 |
| LAD-I | 33 (seed 40250) | 8 | 82 | 82 of 82 |
| SSADH | 30 (seed 40250) | 23 | 10 | 10 of 10 |
| Danon | 56 (seed 40250) | 1 | 34 | 35 of 35 |
| Tangier | 15 (seed 40250) | 0 | 7 | 7 of 7 |
| Blau | 80 (sample of 250, seed 47250) | 21 | 8 | 9 of 9 |
| Majeed | 27 (sample of 27, seed 54250) | 50 | 12 | 10 of 12 (4 public) |
| LCAT | 38 (seed 47250) | 11 | 25 | 26 of 26 |
| GAMT | 51 (seed 47250) | 8 | 8 | 8 of 8 |
| ATS | 33 (seed 47250) | 4 | 1 | 1 of 1 |
| PAPA | 48 (seed 47250) | 4 | 1 | 1 of 1 |

[consolidated_runs_2026-11-15.md §4]

- Twelve review pages (O1 rater A and B, O2 triage, O3 adjudicator A, for each of the registered six, the extension five and Majeed) are published as private pages; stores read 2026-11-15: 0 ratings on any page (one gap document was opened for about 31 active minutes with nothing entered). The registered gap page predates D-42/D-43 and still lists the withdrawn G-danon-001. These pages are to be replaced by per-rater pages under D-55. [consolidated_runs_2026-11-15.md §4, §9; plan_human_assessment_2026-11-15.md §10]
- Also waiting for a person: addendum batch 1, 42 disputed gatekeeper verdicts and 6 full-text exclusions; batch 2, 54 items listed for a human look; 19 proposed same-person groups; 4 comparator listing sheets (0 filled); the open-weight blinded audit (no sample yet). [consolidated_runs_2026-11-15.md §8]

---

## 3. Deviations, decisions and corrections after the freeze (D-38 onward)

Every deviation was approved by Dr. Lin before it took effect unless the row says otherwise. Decision numbers are never reused; D-52 and D-53 were recorded as D-47 and D-48 in the extension session and renumbered at the merge (D-54), so files that session wrote still use the old numbers.

| Date | No. | Kind | What changed | Why | Effect |
|---|---|---|---|---|---|
| 2026-10-20 | D-36 | decision (freeze) | Extraction v6 and gatekeeper v4 frozen as tested; pre-registration v1.0; tags on commit `ef3133e` | Smoke run passed; the missing hedge rule is listed as a known behaviour rather than fixed | Hedged "observed" statuses are dropped by the gatekeeper and end as "not reported" |
| 2026-10-20 | D-37 | decision | Six-disease run approved up to $1,200 (estimate $795 one clean pass; $994 with repairs) | Cost estimate from the smoke run's cost per input token | Run including the 10% repeat came to +$768.87 by session readings |
| 2026-10-20 | D-38 | deviation | Frozen prompt and schema instantiated per disease by script (disease name, gene, schema path, 20-item checklist; 12 changed lines) | The frozen files name HA20 and *TNFAIP3* | None on HA20; checklists new by design |
| 2026-10-20 | D-39 | deviation | AxD catalogue (PMID 39420046 supplement) used for completeness although dropped by the pre-extraction check | The drop came from a Europe PMC HTTP 500, not from an unsuitable table; transcribed on the harness side only | AxD gains a completeness figure (54/56); nothing reaches extraction |
| 2026-10-20 | D-40 | deviation | Stage 4 reads per-disease settings (gene, HGNC ID, MANE transcript, Mondo term, checklist-to-HPO map) | Stage 4 hard-coded HA20 | None on extraction or the gatekeeper; five diseases get records |
| 2026-10-21 | D-13 | decision | ClinVar submissions use the *curation* collection method, not *literature only* | Records will be panel-adjudicated and carry a classification | Changes the grant's wording |
| 2026-10-21 | D-14 | correction | Patient counts and the phenopacket-store figure in the project context corrected (§1.11) | Sources contradict the application | Disease set unchanged |
| 2026-10-21 | D-41 | decision | Model work while human rating waits: gap dossiers, memorization probe, GPSEA, completeness, bias-arm prep | Human rating deferred | No change to the frozen plan |
| 2026-10-21 | D-10 | decision | Open-weight run hosted on OpenRouter (DeepInfra fp8); three harness fixes during the run; gatekeeper v4 also run on both open-weight runs | Fairness: one pinned provider and precision; same judge for both models | §2.1.10 |
| 2026-10-28 | D-42 | decision | OMIM reference = the twelve entry pages Dr. Lin froze on 2026-10-28 (replaces the API route of D-12); OMIM used as a human-curated holdout | omim.org refuses automated reads; no API key | OMIM half of O2 and the OMIM clause of O3 assessed; clinical synopses still not assessed |
| 2026-10-28 | D-43 | deviation | Isoform-sensitive positions in Stage 4 normalization (LAMP2 from c.1094, GFAP from c.1172); G-danon-001 withdrawn; phenopackets keep the paper's own transcript description beside the MANE projection | The OMIM holdout exposed a variant placed on the wrong LAMP2 isoform, creating a false gap candidate | Danon re-normalized: 2 of 165 descriptions changed, 5 records differ; O3 214 live candidates; O2 not re-run |
| 2026-11-09 / 2026-11-10 | D-45, D-46 | decisions (release) | Collaborator dashboard on GitHub Pages; the repository is made public (2026-11-10) | Expert reviewers; Pages needs a public repository | Everything committed is public; paper text was redacted from 141 open-weight transcripts before the switch (4,383 tool results, 12.7 million characters) |
| 2026-11-14 | D-47 | deviation | Corpus addendum: free copies found after the freeze, run as separately reported batches with the frozen pipeline (cut-off 2026-11-30); amended to run batch 1 (29 papers) and batch 2 (72 papers hand-fetched with Claude computer use) on 2026-11-15 | The registered fetch missed open copies because of automated-access refusals | +82 papers, +561 phenopackets beside the registered results; registered figures unchanged; no O2/O3 on the addendum yet |
| 2026-11-14 | D-52 | deviation | Six reserve diseases added as an extension under a separate addendum committed before extraction; Majeed dropped by the addendum's rule (fewer than 15 eligible primary reports) | More volunteer reviewers; the application's Stretch line | Five extension diseases, 209 papers, reported apart; pooled 12-disease figures exploratory |
| 2026-11-15 | D-48 | deviation | O4 counts only records with a disease term and removes comparator-cohort members tagged stated or probable; other cells reported beside | The plan did not say how cohort membership is established; healthy relatives inflated denominators | Decided before any comparator sheet was filled or frequency computed; SSADH 363 → 311 → 196, HA20 769 → 447 → 438, Danon 505 → 322 |
| 2026-11-15 | D-49 | deviation | Stage 4 recognizes the old symbol ABC1 as ABCA1 | Variant rows of 1999–2000 Tangier papers were lost to nomenclature | None on the registered runs (0 of 2,233 variant rows); addendum Tangier gains interpretations (batch 1 1 → 4; batch 2 17 → 18) |
| 2026-11-15 | D-50 | decision | Phenopacket IDs prefixed with the run whenever runs are combined | Every run numbers identities from 0001 | Files unchanged |
| 2026-11-15 | D-51 | decision | No session pushes extraction outputs (quotes) from further papers that are free to read but not openly licensed until D-16 (release licence) is settled | Quotes cover up to 23% (batch 1) and 36% (batch 2) of a paper's text | Majeed: 6 documents' outputs and 27 phenopackets held back; 43 extension papers with no Creative Commons licence merged as they were, as a recorded exception |
| 2026-11-15 | D-53 | deviation (decided by Claude under Dr. Lin's delegation) | NOD2 legacy-transcript fallback for Blau; G-blau-008 and G-lcat-001 withdrawn | Most Blau papers number NOD2 on NM_022162 (27 residues above MANE) | Blau cDNA normalized 18 → 37 of 38; recall 1/22 → 3/22; candidates 5 → 9 (1 withdrawn); registered-rule figures reported beside |
| 2026-11-15 | D-54 | deviation | Majeed assessed by people as an exploratory twelfth disease with its own samples; extension decisions renumbered | Dr. Lin wants all twelve assessed together | Majeed reported on its own; audit too small for a decision rule; its O2/O3 seen before its audit sample was drawn |
| 2026-11-15, 2026-11-16 | D-55 | deviation | Volunteer raters in rotating groups with a calibration round and a floor, in place of two fixed raters and a tie-breaker; nine raters from 2026-11-16 | Several people of variable ability are available; overlap lets ability be compared and gives every audit claim a blind third reading | Registered pair and rule C kept per claim; κ reported per pair of raters; §4 |

[DECISIONS.md decision log and Pre-registration deviations (D-13, D-14, D-36 to D-43, D-45 to D-55); addendum_d47_batch1_findings.md; addendum_d47_batch2_findings.md]

---

## 4. The human assessment design (D-55)

- **Status.** Accepted by Dr. Lin on 2026-11-15: the design and the calibration floor. Calibration is in two sittings: the audit part (40 claims) first, before audit and triage; the adjudication part (6 variants with a settled ClinVar classification, classified without opening ClinVar) just before adjudication. Nine raters take the calibration round (as of 2026-11-16); two of them are members of the adjudication panel. No rater's identity is recorded in the repository. **Calibration is due Sunday 2026-11-22.** [DECISIONS.md D-55 entries of 2026-11-15 and 2026-11-16]
- **After calibration Dr. Lin decides** who goes on to the main work (2026-11-16: he is not sure all nine will pass) and Plan A (registered six) or Plan B (all twelve), by how many pass. The registered six come first under either plan. Plans are then re-priced with the raters' measured minutes and the number who go on. The floor and the scoring do not move with the results; a rater below the floor is not made a registered rater. [DECISIONS.md Open decisions D-55; D-55 log]

### 4.1 Calibration set

- **Reference labels.** Candidate claims came from the six registered runs, outside the registered audit sample (claims the gatekeeper removed and claims it kept), only from papers whose text restores exactly; at most one claim per paper and two per field per disease in each pool. Dr. Lin labelled every candidate on a private page, blind to the gatekeeper's verdict and to the source pool. Three draws: 60 (36 removed by the gatekeeper, 24 kept), 15 (9, 6), 24 (20, 4). [DECISIONS.md D-55 log]
- **His labels over all 99:** 64 supported, 29 unsupported, 5 cannot verify, 1 quote not in paper. Against the gatekeeper (not shown to him): of the 65 claims it had removed, 26 unsupported, 34 supported, 4 not verifiable, 1 quote not in paper; of the 34 it had kept, 30 supported, 3 unsupported, 1 not verifiable. These are not error rates: candidates were chosen for variety, from papers whose text restores exactly, and labelled by one person. [adjudication/calibration/reference_labels_2026-11-16.json; DECISIONS.md D-55 log]
- **His sittings (measured):** 60 ratings in 59.6 minutes (median 51 seconds between ratings); 15 in 17.2 minutes (median 73 s); 24 in 16.3 minutes (median 35 s). None of his earlier labels changed between exports. [adjudication/calibration/reference_labels_2026-11-16.json; DECISIONS.md D-55 log]
- **Set rule, fixed before any label existed:** the first 20 claims he labels unsupported and the first 20 he labels supported, in a seeded item order; "cannot verify" and "quote not in paper" are not used; a second draw if fewer than 20 come out unsupported (after 60 there were 18). [DECISIONS.md D-55 log]
- **First amendment (Dr. Lin, 2026-11-16, "Rebalance it"):** one kind of claim filled half of the unsupported side by the first rule, so that kind is capped among the 20 unsupported claims, the freed places going to other claims he labelled unsupported in item order; the supported side and the floor are unchanged. The kind and the cap are recorded privately (sha256 committed), because naming them would hint at the answers. A third draw of 24 candidates outside the capped kind was made for this; it gave enough. **Second amendment (Dr. Lin, 2026-11-16, "Swap the two repeats"):** on each side, a claim with the same paper and quote as an earlier claim of that side is skipped (two pairs had arisen because the third draw allowed papers of earlier draws). Both amendments were made after his reference labels were seen and before any rater saw anything, and are to be reported wherever calibration results are reported. [DECISIONS.md D-55 log]
- **Final set:** 40 claims, 20 unsupported and 20 supported by his label, from 39 papers; by disease AxD 8, Danon 6, HA20 5, LAD-I 7, SSADH 8, Tangier 6; 59 candidates not used. 35 of the 40 are shared by all three versions of the set (all 20 supported and 15 of the 20 unsupported), so results can also be given on those 35. Candidates, seed, reference labels and set-rule files stay out of the public repository until calibration ends; their sha256 values are committed. [adjudication/calibration/reference_labels_2026-11-16.json; DECISIONS.md D-55 log]
- **Rater pages:** one private page per rater (R1 to R9), the same 40 claims in each rater's own order, numbered R<n>-01 to R<n>-40 (the candidates' own numbers are hidden); each shows the claim, its quote and the passage of the paper, never a reference label, gatekeeper verdict or source pool. All nine stores were read once after publishing: empty. [DECISIONS.md D-55 log]
- **How a rating counts (fixed 2026-11-16, before any rater entered one):** an unsupported claim is caught when the rater labels it "unsupported", "quote not in paper" or "cannot verify" (the strict count without "cannot verify" reported beside it); a supported claim is passed only when labelled "supported"; the floor applies only to a rater who rated all 40. Reported beside the floor: the same counts on the 35 shared claims, the capped kind apart from the others, each rater's agreement with the majority of the other raters, agreement between each pair, minutes per rating. Per-rater results stay private until Dr. Lin decides. [DECISIONS.md D-55 log]
- **Floor (fixed before any calibration result):** a rater serves as one of the two registered raters of a claim only after catching at least 15 of the 20 unsupported calibration claims and passing at least 18 of the 20 supported ones. A rater below the floor may still rate; those readings are reported and not used for the registered result. [DECISIONS.md D-55 log]
- **What 20 unsupported claims can resolve:** 20 of 20 caught gives 83%–100% (95% interval); 18 of 20, 68%–99%; 16, 56%–94%; 14, 46%–88%; 12, 36%–81%. A set twice as large would give 36 of 40 an interval of 76%–97%. [plan_human_assessment_2026-11-15.md §2]

### 4.2 Main assessment

- **Audit:** every claim read by 3 raters, dealt across all groups of three by a seeded script (56 groups with eight raters; 84 with nine), equal loads, every pair sharing claims. For each claim the script names two of its three raters as the registered pair and the third as tie-breaker; the registered result uses the pair's labels and the tie-breaker's only where they disagree; rule C unchanged. Majority-of-three labels, pairwise agreement and each rater's estimated hit and false-alarm rates are exploratory. Cohen's κ, registered for two fixed raters, is reported per pair on shared claims, with an all-rater agreement measure beside it. [plan_human_assessment_2026-11-15.md §2, §7; DECISIONS.md D-55 deviation]
- **Triage of ClinVar misses:** every item read by 2 raters; Dr. Lin settles items where they differ. **Gap adjudication:** every candidate adjudicated by 2 raters independently; a third reads it where they differ on the decision (approve, reject, needs discussion) or on the class across the pathogenic / uncertain line. Nothing goes to submission without the panel's approval and Dr. Lin's sign-off. Still to fix before adjudication: who gives the third reading when a panel member is one of the two adjudicators, and what counts as the panel's approval. [plan_human_assessment_2026-11-15.md §2; DECISIONS.md Open decisions]
- **Kept as registered:** the samples and seeds, the labels, blinding to the gatekeeper, rule C, and the registered result computed from a named pair and tie-breaker per claim. The three studies (registered, extension, Majeed) are scored separately. [DECISIONS.md D-55 deviation; plan_human_assessment_2026-11-15.md §4]

### 4.3 Plan A and Plan B (planning figures, not measurements)

| | Plan A: registered six | Plan B: all twelve |
|---|---|---|
| Extracted values audited | 250 | 527 (250 + 250 extension + 27 Majeed) |
| ClinVar misses triaged | 50 | 146 (50 + 46 + 50) |
| Gap candidates adjudicated | 214 | 269 (214 + 43 + 12) |
| Entries covered | 514 | 942 |
| Independent readings (eight raters) | 1278 + third readings | 2411 + third readings |
| Hours per rater, eight raters (range) | 21.1 (13.7–41.9) | 28.6 (17.9–56.6) |
| Rater hours in all, eight raters (range) | 169.2 (109.5–334.8) | 228.9 (143.2–453.2) |
| Calendar time at 2, 3, 5 hours per rater per week (eight raters) | 11, 8, 5 weeks | 15, 10, 6 weeks |
| Hours per rater, nine raters (range) | 19.1 (12.5–37.5) | 25.7 (16.2–50.7) |
| Hours per rater, seven / six / five raters | 23.8 / 27.3 / 32.2 | 32.3 / 37.2 / 44.2 |

[plan_human_assessment_2026-11-15.md §1, §4; DECISIONS.md Open decisions D-55 (figures by number of raters computed 2026-11-16, not written to a report)]

- Planning time per item: audit 1 minute per claim (range 0.5–2; the only measurement is the pilot, 0.37 and 0.65 minutes per rating, one rater); triage 4 minutes (range 2–6, assumed); adjudication 15 minutes per candidate (range 10–30, assumed; the only data point is one candidate left open for 31 active minutes with no decision); third readings on 40% of candidates (20% and 60% shown). Calibration about 2.7 hours per rater. Gap adjudication is about 76% of Plan A's time. [plan_human_assessment_2026-11-15.md §1, §5]
- Person-hours in all barely change with the number of raters (Plan A 171.9 with nine against 169.2 with eight), because only calibration is per rater. With nine, each pair of raters shares 20 or 21 audit claims in Plan A against 26 to 28 with eight. The plan report is written for eight raters and is to be regenerated for the final number before any audit assignment is drawn. [DECISIONS.md Open decisions D-55]
- Eight-rater detail, Plan A: audit 93–94 claims per rater (26–28 shared per pair), 1.6 h (0.8–3.1); triage 12–13 items, 0.8 h (0.4–1.2); adjudication 53–54 candidates (7–9 shared per pair), 13.4 h (8.9–26.8); third readings 86 if 40% differ, 2.7 h per rater on average. With a cap on hours per rater, candidates fully adjudicated in Plan A: 8 h 38 of 214; 12 h 92; 16 h 145; 20 h 198; 24 h 214. Plan B: 8 h 0 of 269; 12 h 47; 16 h 100; 20 h 154; 24 h 207; 30 h 269. [plan_human_assessment_2026-11-15.md §3, §4]
- The registered adjudication window is Month 4 (2026-12-21 to 2027-01-20), across the holidays; hours per rater per week are not known. Model cost of the assessment is small (six calibration dossiers about $3 at $0.49 per dossier). [plan_human_assessment_2026-11-15.md §8, §10; DECISIONS.md Open decisions]

---

## 5. Limitations and failures recorded in the sources

Numbers are given in §2 with their sources; this section lists each limitation once, with the key figure.

- **No human-rated accuracy for the frozen pipeline.** Every support figure for it is a model's reading of a model's output; O1 is drawn and unrated, so no accuracy claim can be made. [interim_paper.md Status box, §6]
- **The pilot's two human audits missed the 2% target** (6.0%, 3/50; 6.3%, 3/48); each exposed an error class the frozen pipeline now guards against but has not been re-audited for. Even a pass under rule C would leave a true rate near 2% unexcluded. [interim_paper.md Abstract, §4]
- **The gatekeeper rate is not an error rate:** in the pilot humans found about 6% unsupported where the gatekeeper found 0.04–0.3%, and it flagged 2 of 6 and 1 of 4 of the claims a person rejected; a Claude judge may favour Claude's outputs. Dr. Lin's calibration reference labels disagree with the gatekeeper in both directions (34 of 65 removed claims labelled supported; 3 of 34 kept claims labelled unsupported), which is not an error rate either. [interim_paper.md §3.6; background/grant_claim_checks.md item 16; DECISIONS.md D-55]
- **Uneven gatekeeper procedure in later runs:** verdict files often written by the helpers' own scripts (batch 1: 20 of 31); double judging agreed (batch 1 796/802; batch 2 1,191/1,192) but does not show every claim was judged one by one; three batch-1 chunks with refused scripts were judged once; 45 batch-2 "other person" claims softened to partially supported (strict rate 0.8% vs 0.4%); one sentence judged both ways in two chunks; Majeed's script-judged chunks changed on re-judging. [addendum batch reports; majeed_pv1s_findings.md]
- **Frozen extraction gaps:** no hedge rule (D-36); relatives' variant fields quoted from the proband's sentence; cohort statements applied to individuals. They drive the higher addendum rates (batch 1 Tangier 4.8%; batch 2 HA20 3.2%). [interim_paper.md §3.2, §5 G8]
- **Low, concentrated HGVS recall against ClinVar** (registered tiers 1+2 from 14.6% to 66.7%; Blau 13.6%; Majeed 10.5%), untriaged; overlap is not precision. [interim_paper.md §3.7; consolidated_runs_2026-11-15.md §3]
- **Open access only (D-32):** 14–53% of each registered corpus has open full text; the gap count is a lower bound; 38 of the 84 papers OMIM cites for its allelic variants were never returned by the searches (pre-gene-era disease names), and Tangier's OMIM recall is 10.5%; 131 addendum papers stopped at challenge pages and 111 remain not retrieved; Majeed's founding reports and record N88 could not be fetched; one SSADH open PDF (9093300) could not be re-fetched on 2026-10-28. [interim_paper.md §3.1, §3.7b, §5 G7, G18; DECISIONS.md D-47, D-54; addendum_d47_batch2_findings.md]
- **Conversion and input problems** in about 10 registered papers and OCR or symbol damage in addendum PDFs, all helper-reported and unverified by a person. [interim_paper.md §5 G9; addendum_d47_batch2_findings.md Conversion]
- **Notation and normalization:** cDNA without "c.", legacy numbering (ABCA1, NOD2, LAMP2B), protein-only strings, variants stated only in prose; three gap candidates proved to be placement artefacts (G-danon-001, G-blau-008, G-lcat-001); `gap_candidates.py` has no on-gene check. [interim_paper.md §5 G10; DECISIONS.md D-43, D-52 log, D-53]
- **Deduplication is the weak point:** 9 of 38 repeat papers differ in individual count; 19 proposed same-person groups unmerged; 6 false merges of 93 in the pilot; the registered 50-merge hand check not done; addendum records neither deduplicated nor matched to the registered runs; summed identities are an upper bound on people. [interim_paper.md §3.8, §4; consolidated_runs_2026-11-15.md §2]
- **HA20 is the development disease** (rules tuned on it; 92 of 160 corpus papers ClinVar-seeded), so its figures flatter the pipeline. [interim_paper.md §3.12]
- **OMIM:** a curated sample; only its variant half assessed; patient-level comparison judged by Claude; OMIM's own legacy numbering and two mislinked allelic variants. [interim_paper.md §3.7b, §6]
- **Bias arm:** no numbers yet; no comparator for LAD-I and Tangier; 3 comparators paywalled; many SSADH literature individuals probably in the comparator registry; 10 post-cutoff papers in the memorization probe. [interim_paper.md §3.9; DECISIONS.md D-48]
- **Open-weight comparison:** Claude judge, no blinded human audit, two diseases, one model, one provider. [openweight_comparison_findings.md]
- **Licences (D-16, D-46, D-51):** the repository is public and committed outputs carry verbatim quotes; no licence for records and code is settled; many addendum and 43 extension papers are not openly licensed; Majeed's 6 non-open documents are held back; unredacted open-weight transcripts remain in the history of 2026-10-21 to 2026-11-10 unless Dr. Lin rewrites it. [DECISIONS.md D-16, D-46, D-51, D-54; consolidated_runs_2026-11-15.md §6–7]
- **Records and registration:** registered manifests recorded only the alias "opus" at run time; five extension runs lack a `manifest.json`; the registered gap page still lists G-danon-001; the pre-registration tags are not pushed and the OSF registration is not made. [interim_paper.md §2.3, §5 G16; consolidated_runs_2026-11-15.md §7; DECISIONS.md header]
- **Costs are session estimates** with frozen or lagging readings; whether the sessions ran on the funded account is open (D-15); the account ran on overage at several readings (D-17). [BUDGET.md]
- **The drafts' author is the pipeline's author:** Claude Code built and ran the pipeline and generated the reports; the numbers are reproducible, the framing is not independent. [interim_paper.md §6]

---

## 6. Budget (estimates from session cost readings, not billing figures)

| # | Line | Requested | Spent (estimate) | Remaining |
|---|---|---:|---:|---:|
| 1 | Extraction across six diseases, incl. re-runs | $8,000 | $1,246.47 | $6,753.53 |
| 2 | Gatekeeper verification pass | $4,000 | $644.61 | $3,355.39 |
| 3 | ClinVar/OMIM reconciliation + concordance harness | $6,000 | $124.78 | $5,875.22 |
| 4 | Claude Code: pipeline, VariantValidator integration, dedup tooling, adjudication interface | $6,000 | $15.46 | $5,984.54 |
| 5 | Ascertainment-bias arm | $4,000 | $55.17 | $3,944.83 |
| 6 | Claude vs open-weight head-to-head | $2,000 | $0.00 | $2,000.00 |
| | Core subtotal | $30,000 | $2,086.49 | $27,913.51 |
| 7 | Stretch: extend to all 12 candidate diseases | $9,000 | $596.93 | $8,403.07 |
| 8 | Contingency | $6,000 | $252.62 | $5,747.38 |
| | Total (includes $327.04 not assigned to a line) | $45,000 | $3,263.08 | $41,736.92 |

[BUDGET.md Lines, reading of 2026-11-15 16:41 UTC]

- Spent is an estimate from chained session cost readings (list price, including helper agents), split by line in `analysis/cost/spend_segments.csv`; it is not a billing figure, readings sometimes freeze or lag, and whether the sessions ran on the funded account is open (D-15). The ledger of billing figures is empty. Unassigned $327.04 (setup, documents, decisions, gaps between runs). The Contingency figure is an exploratory side study that is outside this paper by the PI's decision. [BUDGET.md]
- Not counted in the table: OpenRouter spend for the open-weight model (billed outside the award: $16.34–$20.35 for the two runs, plus about $0.19 for the pilot and $0.048 for the open-weight memorization probe; the key is shared with other projects, so key-usage deltas are upper bounds); the Majeed search session ($19.92 at the 2026-11-15 budget pass); the consolidation session of 2026-11-15 (no counter; its two helpers about $5.50 by helper tokens, $4.88 of it for the ten Majeed dossiers); claude.ai chats and Cowork sessions. [BUDGET.md]
- Superseded: the interim paper's total of $1,861.06 (reading of 2026-10-24) is superseded by $3,263.08 (2026-11-15). [interim_paper.md §3.13; BUDGET.md]
- Unit costs measured: extraction about $2 per paper by session readings ($1.08 and $1.19 median per paper by helper tokens on HA20 and SSADH); gatekeeper about $0.0044 per judged claim; the six registered runs cost $603 for extraction plus gatekeeper over 350 documents ($1.72 per paper; $1.35–2.38 by disease); the six-disease run with its 10% repeat +$768.87 by session readings against the $1,200 ceiling; HPO binding helpers $72 against a $28 estimate. [interim_paper.md §3.13; DECISIONS.md D-47 cost; BUDGET.md pre-run estimates]
- Per-run spend: gap dossiers (registered) $64.10 and memorization probe (Claude) $5.34 by helper tokens; gatekeeper on the open-weight runs $136.46 by helper tokens; extension five $596.93 by session readings (D-52 ceiling $1,500); Majeed run about $92 by helper tokens (ceiling $120) plus about $20 for its search screening; addendum batch 1 about $61 and batch 2 about $153.69 by session readings; pilot total $673.89 by session readings against its $1,000 ceiling (to the end of the pilot report). [BUDGET.md; extension_report.md §7; majeed_pv1s_findings.md; addendum batch reports]
- The award's six-month window: the first deposit, if it landed on 2026-09-21, expires 2027-03-21. Unused credits are reported, not spent for the sake of it. [BUDGET.md three notes]

---

## 7. Pending human results

**These results are not in.** As of 2026-11-20 the calibration round is in progress (nine raters invited, due 2026-11-22) and no calibration result is reported in this version; no audit claim of the frozen pipeline had been rated, no ClinVar miss had been triaged and no gap candidate had been adjudicated; no comparator sheet has been filled and no expert-minutes have been logged. The paper must not state, estimate, round or imply any of them, and must write each one as `\HR{<id>}` with the id exactly as listed below. Everything measured (designs, sample sizes, seeds, page counts, the reference labels' counts, the planning figures) is in the sections above and is written as normal numbers. [reports/paper_v4/materials/pending_human_results.md]

| id | What it will hold | Comes from |
|---|---|---|
| `cal_raters_finished` | Raters who rated all 40 calibration claims, of 9 invited | calibration pages |
| `cal_raters_pass` | Raters who met the floor (≥15 of 20 unsupported caught and ≥18 of 20 supported passed) | `calibration_score.py` |
| `cal_caught_median` | Median unsupported claims caught, of 20, among finished raters | `calibration_score.py` |
| `cal_passed_median` | Median supported claims passed, of 20, among finished raters | `calibration_score.py` |
| `cal_majority_agree` | Claims (of 40) on which the majority of finished raters agrees with the reference label | `calibration_score.py` |
| `cal_minutes_median` | Median minutes per calibration claim across finished raters | `calibration_score.py` |
| `plan_choice` | Plan A (registered six) or Plan B (all twelve), chosen by the PI after calibration | DECISIONS.md |
| `raters_main` | Raters who go on to the main assessment | DECISIONS.md |
| `o1_unsupported_n` | Registered audit: claims unsupported, of 250 | O1 audit pages |
| `o1_unsupported_pct` | The same as a percentage | O1 audit pages |
| `o1_unsupported_ci` | Its exact 95% interval | O1 audit pages |
| `o1_rule_c` | Whether the pre-registered decision rule C is met (at most 4 of 250 unsupported) | O1 audit pages |
| `o1_kappa_range` | Range of Cohen's kappa over pairs of raters on shared claims | O1 audit pages |
| `o1_gatekeeper_sens` | Share of human-unsupported claims the gatekeeper had also removed | O1 audit pages |
| `o1_by_disease` | Unsupported claims by disease (table) | O1 audit pages |
| `o1x_unsupported` | Extension audit (O1X), five reserve diseases: unsupported of 250 | O1X pages (Plan B only) |
| `o1m_unsupported` | Majeed audit: unsupported of 27 | Majeed pages (Plan B only) |
| `o2_triage_breakdown` | Registered triage of 50 ClinVar misses: counts by cause (extraction miss, conversion loss, not in paper, ClinVar error, other) | O2 triage page |
| `o2x_triage_breakdown` | Extension triage of 48 misses, the same counts | O2X page (Plan B only) |
| `o2m_triage_breakdown` | Majeed triage of 50 misses, the same counts | Majeed page (Plan B only) |
| `o3_adjudicated` | Gap candidates adjudicated, of the candidates left for the panel | O3 pages |
| `o3_accepted` | Candidates the panel accepts as a true gap variant with phenotype evidence | O3 pages |
| `o3_class_split` | Accepted candidates by classification (pathogenic / likely pathogenic / uncertain) | O3 pages |
| `o3_submissions` | Records prepared for submission after panel sign-off (none is submitted before that) | submissions/ |
| `o4_deviation` | Per-disease deviation of literature phenotype frequencies from the comparator cohorts (table) | comparator sheets, filled by a person |
| `o5_minutes_per_record` | Expert minutes per accepted record | adjudication page timings |
| `o5_openweight_audit` | Blinded human audit of the open-weight run: unsupported of the sampled claims | not yet built |
| `add_b1_ratings` | Addendum batch 1: the 42 disputed claims and 6 exclusions, as rated by a person | addendum sheets |
| `add_b2_audit` | Addendum batch 2: the 54-claim audit list, as rated | addendum sheets |
