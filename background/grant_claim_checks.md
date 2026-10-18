# Grant claims checked against the literature

*Checked 2026-10-16 during the background literature search. Keys refer to `manifest.csv` / `bibliography.md`. Nothing here changes the pre-registration or the disease set; items marked **Decision** need Jimmy's call and, if acted on, an entry in `DECISIONS.md`.*

## Numbers that need correcting or rewording

| # | Claim in application / CONTEXT.md | What the sources say | Suggested action |
|---|---|---|---|
| 1 | Pilot diseases are absent from phenopacket-store's **408 cohorts** | No published source gives 408. Counted directly from the `monarch-initiative/phenopacket-store` repository (commit `85ffd78`, 2026-10-07): **731 gene cohort folders, 10,782 phenopacket files**. Latest published figure: 8,182 phenopackets (v0.1.24, GPSEA preprint; `rekerle2026_gpsea`). None of the 12 pilot or substitute genes has a cohort folder, so "absent" still holds. | Replace "408 cohorts" with the dated count; re-count from a tagged release when the reference snapshot is taken. |
| 2 | Tangier disease: **~200 published patients** | Contradicted. GeneReviews says fewer than 100 published cases (`genereviews_tangier`); Koseki 2021 counts ~144 (35 Japan + 109 elsewhere) (`koseki2021_tangier_review`). No source found giving ~200. | Use "~100–150 (Koseki 2021)" or our own count after corpus assembly. |
| 3 | Danon disease: **>100 published families** | Only roughly supported. Closest is "about 100 families" (`sugie2024_danon_history`); 146 molecularly confirmed patients from 83 papers (`brambatti2019_danon_gender`); >500 patients surveyed (`cenacchi2020_danon_review`). | Reword to "about 100 families; ≥146 molecularly confirmed patients". |
| 4 | Alexander disease: **550 patients, 182 variants** (2024 review) | Confirmed in the Results of Grossi 2024 (`grossi2024_axd_meta`), but the abstract and discussion describe 550 differently. | Cite the Results section specifically. |
| 5 | LAD-I: **323 cases, genotype for 139** | Confirmed exactly (`almarzanovoa2018_lad1_review`, literature to 2017). Out of date: Kambli 2020 alone adds 127 patients (`kambli2020_lad_india`). The review also notes 10 cases reported more than once, a ready-made deduplication test. | Present as "as of 2017"; expect a larger gap. |
| 6 | HA20: **177 patients** | Confirmed (`elhani2024_ha20_177`, literature to Aug 2023). Newer: >180 (GeneReviews), ~200 (`li2026_ha20_howitreat`). | Date the figure. |
| 7 | SSADH: **~450 patients** | Confirmed (`didiasova2020_ssadh_update`; GeneReviews "at least 450"). | None. |

## Claims about Claude's performance

| # | Claim | What the sources say | Suggested action |
|---|---|---|---|
| 8 | **97.6% precision** on published HPO extraction (Sonnet 4.5) | Real, from Larsen et al. 2026 (`larsen2026_hpo_mcp`, medRxiv preprint), but: 4 synthetic clinical notes run ≥50 times; tool-augmented condition (80.7% without tools); recall 65.3%; Claude was not top on precision (Grok 4.1 98.2%) or F1 (GPT-5.1). Not case reports. | In any future write-up, state the denominator, the tool condition and the low recall; don't imply transfer to case reports. |
| 9 | **DRBench** fabricated-citation rates 3.0% / 3.2% | Numbers come from Rao, Wong & Callison-Burch 2026 (`rao2026_reference_hallucination`), not from a DRBench paper. Metric is hallucinated URLs (no Wayback record), not fabricated citations in general. 3.0% = claude-3-5-sonnet-search (n = 641 URLs), 3.2% = claude-3-7-sonnet-search (n = 1,735): search-augmented models, not deep-research agents. "DRBench" here means DeepResearch Bench (`du2025_deepresearchbench`), not ServiceNow's DRBench. | Cite Rao et al.; say "hallucinated URLs"; name the models. |
| 10 | **AA-Omniscience**: Opus 46.6% accuracy / 35.9% hallucination vs GPT-5 39% / 81% | Each pair is real but from different model generations: Opus 4.8 (Artificial Analysis page, May 2026) vs GPT-5 (high) (paper, Nov 2025). Leaderboard has since moved. | Compare models from the same snapshot and give the query date. |
| 11 | (Not in grant) | Unfavourable result: on counting probands from genomics papers, Claude Sonnet 4 had the lowest exact-count concordance (73.0%) and stability of 5 models (`murugan2026_reasoning_llm_ps4`). Closely related to our proband deduplication. | Include in related work (rule 5: report unfavourable findings). Worth a targeted check in the Month-2 pilot. |

## Design points for the pre-registration (Month 1)

12. **ClinVar "literature only" submissions — Decision.** ClinVar's documentation defines this collection method as variants described in the literature with no additional submitter curation, and recommends not providing a classification (`clinvar_submission_docs`). Literature-only entries are over-represented among outlier classifications (`yang2017_clinvar_discordance`). Our panel-adjudicated records with classifications may fit the **"curation"** collection method better. Needs Jimmy's call before submissions are drafted.

13. **OMIM licensing.** omim.org blocks automated reading; the archived terms bar copying or redistribution without a license (`omim_terms`). Read the current terms by hand (and consider requesting API/download access) before storing an OMIM snapshot in `data/reference/`.

14. **What 250 claims can certify** (computed by `audit_ci_250.py`). With 0 unsupported claims the exact 95% upper bound is 1.46% (two-sided) / 1.19% (one-sided); with 1 it is 2.21% / 1.88%; with 2 it is already 2.86% / 2.50%. So "< 2%" is only demonstrable with ≤ 1 error (one-sided) if success is defined on the upper bound; if it is defined on the point estimate (≤ 4 errors), the interval reaches ~4%. The pre-registration should say which, without changing the 250-claim size or the 2% target.

15. **Memorization probe must be black-box to be fair.** Log-probability probes such as Min-K% (`shi2024_mink_prob`) can run on the open-weight model but not on Claude. Guided-completion (`golchin2024_time_travel`) and pre- vs post-training-cutoff splits (`roberts2024_lens_of_time`) work identically for both. Membership signals are easily confounded by publication date (`duan2024_mia_llm`), so the probe should control for it. phenopacket-store and literature-derived benchmarks are themselves likely in training data (`nguyen2026_llm_rd_metaanalysis`).

16. **Gatekeeper calibration.** Ungrounded self-correction can lower accuracy (`huang2024_no_self_correct`) and LLM judges favour their own outputs (`zheng2023_llm_judge`). A Claude gatekeeper auditing Claude should check strictly against the verbatim span (`rashkin2023_ais`, `gero2023_self_verification`) and be calibrated on human-labelled claims; the 250-claim human audit can double as that calibration set.

17. **Reference databases are imperfect ground truth.** ClinVar contains misclassified P variants (`wright2021_ddd_clinvar`) and OMIM/Orphanet phenotype annotations are incomplete (`connelly2026_fanconi_annotations`). Concordance misses should be triaged, not all counted as extraction errors; the pre-registration should say how.

## Novelty check

No paper was found that generates GA4GH phenopackets from published case reports with an LLM. phenopacket-store was hand-curated with pyphetools (`danis2025_phenopacket_store`); Monarch's LLM work uses phenopackets as inputs (`reese2026_llm_vs_exomiser`) or does ontology-grounded extraction without phenopacket output (`caufield2024_spires`). Closest neighbours are PubMind (`wang2025_pubmind`) and Yin et al. 2025 (`yin2025_llm_disease_genes`). Re-search PubMed directly before claiming novelty in a manuscript.
