# GP-RareLink pre-registration addendum: extension to the six reserve diseases

*Version 1.0, 2026-11-14. Approved by Dr. Jimmy Lin on 2026-11-14 (D-47). Committed before any extraction on these diseases. It adds to the frozen plan (`preregistration/analysis_plan.md` v1.0, tags `prereg-v1.0` / `pipeline-v1.0`, commit `ef3133e`) and changes nothing in it. The primary results stay those of the six registered diseases. Everything below is reported apart from them, and pooled 12-disease figures, where given, are labeled exploratory.*

## 1. Why

The application named six reserve diseases and a Stretch budget line to "extend to all 12 candidate diseases" (`CONTEXT.md` §4, §9). The frozen plan lists the same six only as substitutes (§4.2), and none was needed (D-08). Jimmy reported more volunteer reviewers and decided on 2026-11-14 to run the six reserve diseases through the same pipeline, so that people review all 12 diseases' records and gap candidates together (D-47).

## 2. Diseases

In the registered order (§4.2). Identifiers are from Mondo release 2026-10-06, the release the pipeline pins (`data/ontologies/2026-10-19/manifest.json`).

| Slug | Disease | Gene | Mondo | OMIM | ORPHA | Inheritance |
|---|---|---|---|---|---|---|
| blau | Blau syndrome (early-onset sarcoidosis) | *NOD2* | MONDO:0008523 | 186580; 609464 | 90340; 90341 | AD |
| majeed | Majeed syndrome | *LPIN2* | MONDO:0012316 | 609628 | 77297 | AR |
| lcat | Familial LCAT deficiency, complete (Norum disease) and partial (fish-eye disease) | *LCAT* | MONDO:0018999 | 245900; 136120 | 650 (79293; 79292) | AR |
| gamt | GAMT deficiency | *GAMT* | MONDO:0012999 | 612736 | 382 | AR |
| ats | Arterial tortuosity syndrome | *SLC2A10* | MONDO:0008818 | 208050 | 3342 | AR |
| papa | PAPA syndrome and the PSTPIP1-associated inflammatory spectrum (PAPA-spectrum disorders, including PAMI) | *PSTPIP1* | MONDO:0011462 | 604416 | 69126 | AD |

**Eligibility, checked before extraction:**
- **Absent from phenopacket-store:** none of the 12 genes has a cohort folder or a phenopacket path there (commit `ca133e6`, 2026-11-04; `analysis/extension/phenopacket_store_check_2026-11-14.json`).
- **At least 15 eligible primary reports with open full text** after full-text screening, the D-08 bar. A disease that fails is dropped from the extension and reported as dropped, with its counts. There is no further substitute.

**Scope choices, stated now:**
- **Blau syndrome:** papers on *NOD2* in Crohn disease or other common-disease association studies are out of scope. Only patients with Blau syndrome or early-onset sarcoidosis count. This disease tests whether the pipeline separates a monogenic allelic series from unrelated testing.
- **Familial LCAT deficiency:** both complete and partial deficiency are in scope, because one gene and one allelic series cause both.
- **PAPA:** the PAPA spectrum is in scope, because the same papers describe both, including PAMI (PSTPIP1-associated myeloid-related proteinemia inflammatory syndrome).

## 3. What is the same as the frozen plan

- **Corpus (§5.1, D-35, D-19, D-32):**
  - PubMed from inception, with the shared case/patient/family filter in `configs/diseases.yaml`, plus backward citation searching of each disease's key review.
  - No ClinVar or OMIM citation lists as seeds.
  - Open access only: PMC, Europe PMC and open copies found through Unpaywall.
- **Screening:**
  - Title/abstract and full-text screening by helper agents, with the prompts the first six used (`screen_v2.md`, `screen_fulltext_v1.md`).
  - Every full-text decision carries a verbatim quote.
- **Extraction:**
  - The frozen pipeline v1.0: `extract_v6`, `gatekeeper_v4`, `schema_ha20_v5` and `extraction_rules_v1`.
  - Instantiated per disease exactly as D-38 did (disease name, gene and 20-item checklist only), by `instantiate_disease.py`.
  - Opus helpers, one per paper.
- **Checklists (D-38):**
  - 20 features per disease, written by a helper from the disease's open key review or reviews in the corpus, every quote checked verbatim by `check_checklist.py`.
  - Never written from phenotype annotation files or databases.
- **Run checks:** a 10% repeat run (seed 20261020, as before) and the span check.
- **Gatekeeper v4:** records keep only claims the gatekeeper judged supported.
- **Stage 4 (D-40, D-43):** reconciliation, VariantValidator normalization on the MANE Select transcript, HPO and Mondo binding with the pinned releases, and phenopackets.
  - The isoform rule applies to any gene with alternatively spliced coding exons. Each new gene is checked for them before Stage 4, and the check is recorded.
- **Ground-truth isolation (§5.3):** unchanged. The ClinVar snapshot is taken outside the checkout before extraction and read only by the harness.

## 4. Outcomes for the extension

- **O1, unsupported-value audit.**
  - A separate sample of 250 claims, drawn with the same design as §7.1: the post-gatekeeper claim pool of the six extension diseases, stratified by disease in proportion to pool size.
  - Seed 47250, drawn after all six extension runs finish and before any of their concordance results are looked at.
  - Same rating rules, same decision rule (C: at most 4 unsupported of 250) and same reporting of the exact interval.
  - Reported as the extension's audit, next to and never merged into the registered O1.
- **O2, concordance with ClinVar (§7.2).**
  - The same harness (`concordance_o2.py`), on a fresh ClinVar snapshot dated before extraction starts.
  - Gene-level counts are recorded with the release date.
  - The 50-miss triage sample is drawn with seed 72650, as before.
  - OMIM concordance is not run for the extension. The OMIM reference is pages Jimmy freezes by hand (D-42); if he freezes the six new entries, an OMIM assessment follows as a dated deviation.
- **Completeness against a published catalogue (§7.2.7):** not registered for the extension, so no completeness figure is reported. If a catalogue is checked later, it is labeled exploratory.
- **O3, gap closure:**
  - Same rules (`gap_candidates.py`), candidate IDs `G-<slug>-NNN`, evidence dossiers built with `dossier_instructions_v1.md`, and the ClinVar re-check before adjudication.
  - The extension's candidates are written to their own folder and adjudicated with the first six's under the same panel procedure.
  - No submission without the panel's sign-off.
- **O4, ascertainment bias and memorization:** not extended. D-04 keeps the comparators within the registered six, so no natural-history papers are held out of the extension corpora.
- **O5, efficiency and model comparison:**
  - Expert-minutes per accepted record are recorded for extension candidates as for the others.
  - The open-weight comparison is not extended.

## 5. Human review

- **Screening check:** the full-text screening check is prepared as for the first six (10% of abstract inclusions and every full-text exclusion; seed 20261020). It is rated by a person only if Jimmy asks for it. Otherwise the helpers' decisions stand, as under D-34, and that limitation is reported.
- **Reviewers:** volunteer reviewers take part under the rules D-11 sets for the panel. Who counts as a rater for O1 and an adjudicator for O3 is decided by Jimmy before rating starts, and recorded in `DECISIONS.md`.
- **Review pages:** none is published by Claude under the no-publishing rule. Claude prepares the data; Jimmy decides how pages are shared.

## 6. Budget and order

- **Budget:** line 7 (Stretch, $9,000), ceiling $1,500 for all six diseases (D-47).
- **Order:** one disease runs end to end through the gatekeeper first, and the cost is re-estimated before the other five. Claude stops and asks if the estimate or the running total passes the ceiling.

## 7. Known before registration

- Disease names, genes and identifiers, and the background references already in `background/manifest.csv`.
- PubMed hit counts for broad queries, which Claude ran on 2026-11-14 to find key reviews.
- From the first six: the pipeline's known frozen gaps (no hedge rule, G8), low HGVS recall concentrated in a few papers, and the failure modes in `reports/six_disease_run_findings.md`.

- The application's ClinVar figures for two genes (*NOD2* about 23 pathogenic of 1,055; *PSTPIP1* about 7 of 730; `CONTEXT.md` §5).

No extraction output, fresh ClinVar count or concordance figure for the six new genes had been looked at by this session.
