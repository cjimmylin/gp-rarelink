# GP-RareLink: idea summary for version 4 of the interim report

## Problem
Rare-disease knowledge is fragmented. Variants sit in ClinVar and OMIM, phenotype vocabulary in the
Human Phenotype Ontology (HPO), a small share of cases in Monarch's phenopacket-store, and most
individual patients only in published case reports. A laboratory querying ClinVar cannot see a
causative variant that was published in a case report but never submitted. There are too many
diseases to curate by hand, and the need recurs each time a team meets a disease nobody has curated.

## Research question
Can an LLM-based systematic-review method (SLIDERS), run with Claude, build consolidated
variant–phenotype–disease records from published case reports at an accuracy we can demonstrate,
and at a scale that closes part of the gap between the literature and the databases?

## Core idea
1. **Extraction from full text, with provenance on every value.** For each open-access case report,
   Claude reads the full text and writes per-person records (individuals, variants, phenotypic
   features, a disease-specific phenotype checklist). Every extracted value carries a verbatim quote
   from the paper and the paper's PMID. "Not reported" is a first-class output.
2. **Three-state phenotypes.** Each feature is observed, excluded or not reported; not reported is
   never collapsed into excluded.
3. **Gatekeeper.** A second, independent Claude read checks every extracted value against its own
   quote and removes values the quote does not support. The gatekeeper's rate is not an error rate;
   only the human audit measures that.
4. **Reconciliation and standardisation.** A code-writing reconciliation step merges the same person
   across papers (with the evidence for each merge recorded), variants are normalised to HGVS on the
   MANE Select transcript with VariantValidator, features are bound to HPO and diseases to Mondo, and
   the output is GA4GH Phenopackets (v2), validated.
5. **Held-out ground truth.** ClinVar and OMIM are never read by the extraction pipeline (enforced by
   tests). They are used only afterwards, to score concordance (O2) and to find variants absent from
   both databases (gap candidates, O3). This keeps the concordance measurement uncontaminated.
6. **Pre-registration.** The analysis plan, the pipeline's prompts and schema were frozen on
   2026-10-20 before the main runs. Every later change is a dated, approved deviation.
7. **Human assessment last, and calibrated.** People decide what counts: an audit of extracted
   values against their quotes (O1, the primary, confirmatory outcome: fewer than 2% unsupported on a
   250-claim audit), a triage of ClinVar misses, and adjudication of gap candidates before any
   database submission. Raters first take a calibration round on claims with known reference labels.

## Pre-registered outcomes
- **O1** Unsupported-value rate on a 250-claim human audit (primary, confirmatory; target < 2%).
- **O2** Concordance with ClinVar (and OMIM) on gene, normalised HGVS, classification and phenotype.
- **O3** Gap closure: variants absent from both databases, adjudicated and prepared for submission.
- **O4** Ascertainment bias: deviation of literature phenotype frequencies from natural-history cohorts,
  with a memorization probe.
- **O5** Efficiency: expert minutes per accepted record; Claude versus an open-weight model under an
  identical scaffold.

## What this version adds over version 2 (2026-10-28)
- The same frozen pipeline extended to five reserve diseases and run on a twelfth disease (Majeed
  syndrome) as an exploratory case, so the report covers twelve diseases.
- A corpus addendum of free copies found after the freeze, reported beside the registered results,
  never merged into them.
- The human assessment design as now run: nine volunteer raters, a calibration round with a floor fixed
  in advance, then rotating overlapping groups so raters can be compared.
- Every human result written as an explicit placeholder, so the report can circulate now and be
  completed by script when the ratings arrive.

## Contributions (as this report can claim them)
- An end-to-end, provenance-first pipeline from case reports to validated phenopackets, run under a
  frozen pre-registration on twelve rare diseases.
- A database-held-out evaluation design: automatic concordance with ClinVar/OMIM, plus a list of gap
  candidates with evidence dossiers ready for expert adjudication.
- An honest account of what is not yet known: the primary outcome waits on human raters, and pilot
  audits were above the 2% target.
