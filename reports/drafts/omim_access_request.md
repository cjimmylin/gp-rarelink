# OMIM API access request — draft for Jimmy to submit

*Drafted 2026-10-18 by Claude per `DECISIONS.md` (2026-10-18, decision 4).
Status: **draft, not sent.** The cloud session that drafted it could not reach
omim.org, so the terms summary below must be completed by reading
https://www.omim.org/help/agreement and the API registration page
(https://www.omim.org/api) by hand before submission. Items marked [verify]
are placeholders, not facts.*

## 1. Terms summary (to complete by hand, with the date read)

| Point | What the current terms say | Read on |
|---|---|---|
| Automated access | [verify: whether scripted downloads/API use require registration or a licence] | |
| Storage of content | [verify: whether a local, dated, non-redistributed snapshot of gene-level allelic variant entries is permitted for research] | |
| Redistribution | [verify: confirmed barred without a licence per `background/grant_claim_checks.md` #13] | |
| Attribution | [verify: required citation form for OMIM in publications] | |
| Academic / non-profit API tier | [verify: eligibility and rate limits] | |

Until this table is filled from the live pages, nothing from OMIM is stored in
`data/reference/`.

## 2. Request text (API key registration form or email to OMIM)

Subject: API access request — Rare Genomics Institute, literature-curation research project

Dear OMIM team,

I am requesting API access for a research project at the Rare Genomics Institute
(RGI, a US non-profit) in collaboration with the Stanford Open Virtual Assistant
Lab, funded by Anthropic's AI for Science program. The project, GP-RareLink,
extracts genotype–phenotype records from published case reports for six rare
diseases (Alexander disease, leukocyte adhesion deficiency I, A20
haploinsufficiency, SSADH deficiency, Danon disease, Tangier disease) and
measures their concordance with OMIM and ClinVar.

How we would use OMIM:
- Read the gene entries and allelic-variant lists for six genes (GFAP, ITGB2,
  TNFAIP3, ALDH5A1, LAMP2, ABCA1) and the corresponding phenotype entries, via
  the API, on a handful of dated occasions during the project.
- Store those responses locally as a dated snapshot that only our concordance
  harness reads. The snapshot is not committed to any public repository and is
  not redistributed; only aggregate concordance statistics and our own
  literature-derived records are published.
- OMIM content is never used as input to the extraction step; it is the
  reference we score against.
- Where our adjudication panel confirms variants that are absent from OMIM, we
  intend to offer them to OMIM as allelic-variant candidates with full
  provenance (PMID and verbatim evidence), following whatever submission route
  you prefer.

Expected volume: fewer than [verify: e.g. 500] API calls over six months.

Principal investigator: Dr. Jimmy Lin, MD, PhD, MHS, Founder and CEO, Rare
Genomics Institute (jimmy.lin@raregenomics.org).

We will cite OMIM as required and are happy to provide any further information.

Kind regards,
Jimmy Lin

## 3. After approval

- Put the key in `.env` as `OMIM_API_KEY` on the harness machine only.
- `pipeline/harness/snapshot_reference.py --omim` records the request date,
  endpoint and checksums in `data/reference/<date>/MANIFEST.json`.
- Add an entry to `DECISIONS.md` with the approval date and any conditions.
