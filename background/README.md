# background/ — GP-RareLink literature

Background literature for GP-RareLink, compiled 2026-10-16 (Month 1). 129 entries across four themes, 64 marked core.

| File | What it is |
|---|---|
| `bibliography.md` | Annotated bibliography by theme; ★ = read first |
| `manifest.csv` | Same entries, machine-readable: IDs, access status, download URL, where each ID was verified, notes |
| `grant_claim_checks.md` | Where the literature confirms, corrects or complicates numbers and claims in the application, plus design points for the pre-registration |
| `fetch_papers.py` | Downloads every open-access paper in the manifest into `papers/<theme>/` |
| `audit_ci_250.py` | Confidence bounds for the 250-claim audit (used in `grant_claim_checks.md` §14) |
| `origins/early_concept_conversation.md` | The early chat (before the grant) where the idea started, with a map to the funded design. Historical only; its citations are unverified |

| Theme | Entries | Core |
|---|---|---|
| Methods (SLIDERS, LLM phenotype/variant extraction, SR extraction, grant-cited benchmarks) | 26 | 12 |
| Standards and ground truth (Phenopackets, HPO, Mondo, HGVS/VariantValidator/MANE, ClinVar, OMIM, ACMG) | 29 | 19 |
| Pilot diseases and substitutes (reviews, natural-history cohorts, GeneReviews) | 42 | 17 |
| Bias, memorization, grounding and evaluation | 32 | 16 |

## Getting the PDFs

The cloud workspace this was built in cannot reach PubMed, PMC, Europe PMC, arXiv, bioRxiv/medRxiv or publisher sites, so no PDFs are included yet. On any machine with normal internet access:

```bash
cd background
./fetch_papers.sh                   # bash + curl only (what was run on the Mac mini)
# or: python3 fetch_papers.py [--dry-run] [--theme diseases]
```

`fetch_papers.sh` reads `download_list.tsv` (generated from `manifest.csv`); `fetch_papers.py` reads the manifest directly. Both use only standard tools. It tries arXiv, then Europe PMC (PDF, falling back to full-text XML), then the publisher/repository URL, and only for rows marked open access. About 92 of 129 entries have an open-access route; GeneReviews chapters and policy pages are logged as "read online"; paywalled items are skipped. Results go to `download_log.csv`, which doubles as the record of papers we could not access (INSTRUCTIONS.md §3, Licensing).

**Licensing:** many files are free to read but not CC-licensed (bronze OA, repository copies). Keep `papers/` out of the public pipeline repository; the manifest and bibliography are fine to publish.

## How identifiers were verified

Every PMID, PMCID, DOI and arXiv ID was confirmed on a fetched page or a search result on 2026-10-16, and `verified_at` records where. PubMed and PMC article pages were behind bot checks during the search, so some PMCIDs come from OpenAlex links or search-result titles; these are flagged in `id_notes`. Blank fields mean "not confirmed", never "doesn't exist". Before citing any entry in a manuscript, confirm it on PubMed.

Open items:
- PMIDs not confirmed for several 2024–2026 papers (see `id_notes`); five non-paper entries (software, policy pages, a poster, one Tangier review) have no identifiers.
- Exact titles not confirmed for five substitute-disease papers (bracketed in the title field).
- `tokatlylatzer2023_ssadh_genotype` has two candidate PMIDs; `danis2025_phenopacket_store` has one repository record marked "withdrawn" that looks like a stale duplicate.
- Natural-history registry records (NCT02714764, NCT03758521) were not read.
- No literature was found on detecting the same proband across case reports, or on systematic HPO-frequency vs cohort comparisons across diseases; both look like real gaps.

## Not in scope here

The six-disease case-report corpora (~300 full texts) are a separate Month-1 task and belong in `data/literature/` with per-disease manifests. ClinVar/OMIM snapshots belong in `data/reference/` and must stay out of anything the extraction pipeline reads.
