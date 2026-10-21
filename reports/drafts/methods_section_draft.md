# Methods (draft for the manuscript, 2026-10-21)

*Draft by Claude for Jimmy Lin to edit. Every number below comes from the cited files. Citation keys are those in `background/manifest.csv`. The analysis plan was frozen on 2026-10-20 as v1.0 (`preregistration/analysis_plan.md`; git tags `prereg-v1.0` and `pipeline-v1.0` on commit `ef3133e`); deviations are listed at the end. OSF DOI: ______ (to add once registered).*

## Study design

We tested whether an LLM-based systematic-review method can build genotype–phenotype records from published case reports. The method is SLIDERS (`joshi2026_sliders`), developed by Prof. Monica Lam's Stanford OVAL lab, with Claude doing the extraction. We scored the records against ClinVar, which served as ground truth and was never input. The plan was pre-registered before the study's extraction ran. Six rare diseases were fixed by the grant: A20 haploinsufficiency (HA20; *TNFAIP3*), succinic semialdehyde dehydrogenase deficiency (*ALDH5A1*), Tangier disease (*ABCA1*), leukocyte adhesion deficiency type I (LAD-I; *ITGB2*), Alexander disease (AxD; *GFAP*) and Danon disease (*LAMP2*). HA20 served as the development disease in a one-disease pilot (D-18) and is reported separately.

## Literature corpus

- **Search and screening:** per disease, a PubMed search (`configs/diseases.yaml`) plus reference lists of key reviews. Titles and abstracts were screened by model helpers, then full texts with a verbatim evidence quote for each decision, checked by script. A person checked samples at both stages (D-34).
- **Open access only (D-32):** full text came from Europe PMC and PMC as JATS XML, or from Unpaywall-listed open PDFs.
- **Held out:** natural-history and genotype-first cohort papers, kept as bias-arm comparators (§7.4.1).
- **Corpus:** 350 papers were extracted (HA20 85, SSADH 40, Tangier 31, LAD-I 42, AxD 69, Danon 83; `reports/six_disease_run_findings.md` §3).

## Extraction and verification

- **Extraction:** each paper was read by one Claude Opus helper agent through Claude Code (D-20). The helper followed a frozen instruction file (`extract_v6.md`, instantiated per disease under D-38), a JSON schema and a rules file. It emitted tables of publications, individuals, variants, phenotypic features and a disease checklist.
- **Provenance and three-state coding:** every value carries a verbatim span, checked by script against the paper text. Phenotypes are three-state: observed, excluded or not reported.
- **Gatekeeper:** a second Claude read (`gatekeeper_v4.md`) judged every model claim against its span. Verdicts were supported, partially supported, unsupported or span not found. Records keep only supported claims.
- **Run-to-run repeat:** a seeded 10% of papers (38) was extracted again and compared with the first run.

## Records

- **Deduplication:** individuals were deduplicated across papers by a reconciliation policy (v4 with a duplicate-publication route, D-23 and D-40). Every merge records its evidence.
- **Variants:** descriptions were normalized through VariantValidator (`freeman2018_variantvalidator`) on each gene's MANE Select transcript. The original string is kept beside the normalized form.
- **Phenotype and disease terms:** features were bound to HPO (release 2026-09-01), by script and then by model batches for unmatched phrases. Diseases were bound to Mondo by exact name.
- **Phenopackets:** records were written as GA4GH Phenopackets v2 (`jacobsen2022_phenopacket_schema`) and validated: 2,836 phenopackets, all schema-valid (§9 of the findings report).

## Outcomes

- **O1, unsupported values (primary, confirmatory):** a seeded sample of 250 supported claims (seed 40250), rated by two panel members with a third breaking ties, against the < 2% target. *Ratings pending.*
- **O2, concordance with ClinVar (primary, estimation):** against the ClinVar release of 2026-10-12 (snapshot read 2026-10-19), with Wilson 95% intervals. The harness (`pipeline/harness/concordance_o2.py`) measures:
  - gene;
  - HGVS recall over (PMID, VariationID) pairs at tier 1 (same GRCh38 allele) and tier 2 (same protein);
  - classification agreement;
  - condition and HPO-profile overlap.
  Results are also given without ClinVar-cited papers (D-19). OMIM could not be used (no access, D-12).
- **Completeness (secondary, descriptive; §7.2.7):** recall against published variant catalogues, Chen 2020 for HA20 and Grossi 2024 for AxD (D-39), compared at protein and cDNA level.
- **O3, gap closure (primary, descriptive):**
  - *Candidates:* tier-1, gatekeeper-supported variants with no GRCh38 ClinVar allele. 215 were identified (`adjudication/o3_gaps/summary.md`).
  - *Evidence sheets:* model helpers assembled one per candidate from the papers only, with every statement quoted (4,725 quotes, all verbatim) and no classification proposed.
  - *Adjudication:* the RGI panel classifies each candidate under ACMG/AMP (`richards2015_acmg`) on a logged interface.
- **O4, bias and memorization (secondary):**
  - *Frequency deviation:* literature frequencies (observed ÷ assessed) are compared with held-out comparator cohorts, using a publication-cluster bootstrap.
  - *Memorization probe:* black-box, with two probes, closed-book recall from PMID, title and year (`roberts2024_lens_of_time`) and guided passage completion (`golchin2024_time_travel`). It ran on 180 papers stratified by publication date against the model's documented June 2026 cutoff.
- **O5, efficiency and model comparison (secondary):** expert-minutes per accepted record, and Claude against DeepSeek-V4.1-Flash on HA20 and SSADH under a matched agent loop (D-10).
- **Exploratory analyses (§7.6):** GPSEA genotype–phenotype maps (`rekerle2026_gpsea`), the Danon sex difference, and the share of ClinVar *ABCA1* records matched in the literature.

## Deviations from the frozen plan

- **D-38:** the frozen prompt and schema were instantiated per disease (disease name, gene and checklist only).
- **D-39:** the AxD catalogue's supplement was obtained after extraction and used on the scoring side only.
- **D-40:** Stage 4 (normalization, binding, phenopackets) was given per-disease settings.

Each is logged with its reason and Dr. Lin's approval in `DECISIONS.md`.

## Acknowledgement

This work used credits from Anthropic's AI for Science program (award email, 2026-08-31).
