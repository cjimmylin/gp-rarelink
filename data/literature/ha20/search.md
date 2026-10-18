# HA20 corpus search log (pilot, Stage 1)

All steps were run on 2026-10-18 in a Claude Code cloud session, after the research domains were allowed. The numbers below are copied from the outputs named in each section; re-running the scripts reproduces them, subject to database changes since that date.

## PubMed query

```
("A20 haploinsufficiency"[tiab] OR HA20[tiab] OR "TNFAIP3"[tiab] OR TNFAIP3[Gene Name]) AND ("case reports"[pt] OR "case report"[tiab] OR patient*[tiab] OR cohort[tiab] OR family[tiab] OR families[tiab])
```

- **Dates:** publication date from 2015/01/01 (`datetype=pdat`).
- **Hits:** 715 on 2026-10-18 (`corpus_stats.json` → `build_manifest_runs[0].query_hits`).
- **Change from the runbook query:** `AND humans[mh]` was dropped. On the same day, the runbook's query returned 556 hits and the HA20-specific alternative returned 236. The MeSH filter excludes recent papers that aren't indexed yet, and relevance is decided at screening anyway.

## Seeds

| File | Source | PMIDs |
|---|---|---|
| `seeds/background_bibliography.csv` | HA20 entries of `background/manifest.csv` | 5 (one has no PMID) |
| `seeds/refs_elhani2024.csv` | Reference list of El Hani 2024 (PMID 38128752), Europe PMC references API | 80 (4 without PMID in `refs_elhani2024_unresolved.csv`) |
| `seeds/refs_li2026.csv` | Reference list of Li 2026 (PMID 42169681), same API | 59 |
| `seeds/clinvar_citations.csv` | PMIDs cited by ClinVar records for `TNFAIP3[gene]` (790 records), E-utilities elink; built on the harness side, only PMIDs kept (D-19) | 105 |

**Not obtained:**
- **GeneReviews HA20 references.** Europe PMC holds no reference list for the chapter (PMID 39715316), and the NCBI Bookshelf page returned a reCAPTCHA bot check.
- **13 NCBI Bookshelf records** among the seeds (GeneReviews and similar chapters, including 39715316). The PubMed parser reads journal articles only.

**Result:** `manifest.csv` has 838 rows. 63 papers came only from ClinVar's citations.

## Screening (title and abstract)

- **Route:** D-20, with nine Claude Code helper agents (Sonnet), one per batch of up to 100 records. They followed `pipeline/extract/claude_code/prompts/screen_v1.md`; its hash is recorded in `screening/screening_log.json`.
- **Output:** labels in `screening/labels/`, merged by `claude_code_screen import`.
- **Scratch-file collision:** the helpers shared one scratch directory and some used generic file names, so one helper (batch 06) briefly read another's temporary file. That helper detected the mismatch and re-labelled the 25 affected records itself. A check afterwards compared every label's stated reason with its own title and abstract. Of 838 labels, 16 matched another paper's text better than their own; all 16 were reviewed by hand, and every one describes its own paper. No label was changed. Future runs should give each helper its own scratch directory.
- **In the extraction corpus:** 153 papers (study type case report, case series/cohort or review, and relevance yes or unclear).
  - by study type: 64 case reports, 63 case series/cohorts, 26 reviews;
  - by relevance: 105 yes, 48 unclear;
  - 4 of these 153 came only from ClinVar's citations.
- **Excluded despite unclear relevance:** 9 papers screened as study type "other" (letters, editorials, association studies). They are listed in `manifest.csv`.
- **Spot-check:** `study_type_spotcheck.csv` holds 20 rows (10 included, 10 excluded, seed 20261018) for the human check. The gate is at least 18 of 20 agreeing.

## Full text

- **The PMC open-access web service is gone.** It answered 404 at both its old and new hosts, so the fetcher fell back to Europe PMC full-text XML.
- **Europe PMC quirk:** it answers 500, not 404, for articles it has no full text for. Those papers are recorded as not available.
- **Unpaywall was not used.** It needs an email address; `UNPAYWALL_EMAIL` is unset and needs Jimmy's choice of address.
- **Coverage:** 76 of 153 corpus papers (49.7%) have full text. 76 are recorded as paywalled (DOI known, no open copy found this way) and 1 as not found (`corpus_stats.json`).
  - **Q1 gate (at least 70%) not met.** Per `POC_DESIGN.md` Stage 1, the pilot continues on what is available.
  - The paywalled list in `corpus_stats.json` is the starting point for a library request.
- **Markdown:** 76 papers converted. About 750,000 tokens in total (median 9,171; max 25,491), estimated as characters ÷ 4 because no API key is available to count exactly.
