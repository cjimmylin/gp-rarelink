# GP-RareLink — Project Context

*Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease*

This file is the reference for what the project is, who is on it, and what we have committed to. It is drawn from our application to **Anthropic's AI for Science Program — Rare Disease program, Basic science research track**. Instructions for how Claude should work are in `INSTRUCTIONS.md`.

> **Award** (full text in `grant/AWARD_EMAIL.md`)
> - **Award date:** 2026-08-31 (date of the award email).
> - **Credits awarded:** $45,000, the full amount requested. They are usage credits on a claude.ai account, covering chat, Claude Code, Cowork and Claude Science, over a six-month project period. The email does not mention API (Console) usage; see `DECISIONS.md` D-17.
> - **Deposits:** half up front, with the first deposit scheduled for 2026-09-21. Top-ups follow toward the total as credits are spent. Each deposit expires six months after it lands.
> - **Project start (Month 1):** the date the first deposit landed, provisionally **2026-09-21** (the scheduled date; replace with the actual date from claude.ai Settings > Usage). Month 6 then ends 2027-03-20. See §8 and `DECISIONS.md` (D-01, decided 2026-10-18).
> - **Account:**
>   - The application gave Anthropic Console org ID `2056f88f-1a7b-4386-abfb-5b0fe9a98e10`.
>   - The award email asked, by 2026-09-14, for the Organization ID of a paid claude.ai account instead.
>   - claude.ai Organization ID the credits were sent to: ______
> - **Training use:** under the updated program rules, whether conversations are used for model training follows the funded account's own privacy settings.
> - **Cohort:** 100 projects covering more than 75 conditions. Several work on phenotype extraction, natural-history curation or variant interpretation, so check for overlap before claiming novelty.

---

## 1. The problem

Rare disease knowledge is fragmented. Variant information sits in ClinVar and OMIM, phenotype vocabulary in HPO, a small share of cases in Monarch's phenopacket-store, and most individual patients only in published case reports. A lab querying ClinVar today cannot see a causative variant published in 2011 that was never submitted, and that family's diagnostic odyssey continues.

There are too many diseases to curate by hand, and the need recurs: a team routinely meets a disease nobody has curated. The goal is a pipeline that can be pointed at any disease on demand and connect genotype to phenotype with provenance a clinician can check.

**Headline example:** Alexander disease has 182 distinct causative variants across 550 published patients, against 72 ClinVar P/LP entries and ~12 OMIM allelic variants (roughly 110 unsubmitted variants).

## 2. Research question

Can the **SLIDERS** method, powered by Claude, build consolidated variant ↔ phenotype ↔ disease records from published case reports, at an accuracy we can prove and at a scale that materially closes this gap?

## 3. Team

| Person | Role on project | Background |
|---|---|---|
| **Dr. Jimmy Lin** (MD, PhD, MHS) | PI; Founder & CEO, Rare Genomics Institute (RGI) | Led computational analysis of the first cancer exome studies (Johns Hopkins); led NCI ClinOmics; CSO at Natera and Freenome; 15 years leading RGI. h-index 32. jimmy.lin@raregenomics.org |
| **Prof. Monica Lam** (PhD) | Co-lead, AI methods | Director, Stanford Open Virtual Assistant Lab (OVAL); NAE member; ACM Fellow. Created WikiChat (Wikimedia 2024 Research Award), STORM, SLIDERS, SatIR (with Mayo Clinic). |
| **Dr. Eva Wu** | Adjudication panel | PhD scientist |
| **Dr. Gabriela Balderrama** | Adjudication panel | PhD scientist |
| **Dr. Anita Chacko** | Adjudication panel | PhD scientist |

**Organizations:** Rare Genomics Institute (raregenomics.org) and the Stanford CS OVAL Lab (oval.cs.stanford.edu).

**Existing RGI–OVAL collaborations (≈1 year):** *AutoOMIM* (generating OMIM entries from literature) and *OpenRare* (using STORM to create Wikipedia-like rare disease entries).

## 4. Pilot diseases

All six are absent from phenopacket-store's 408 cohorts. Together they span four inheritance modes and six organ systems.

| Disease | Gene | OMIM | ORPHA | Inheritance | System | Why it's in the set |
|---|---|---|---|---|---|---|
| Alexander disease | *GFAP* | 203450 | 58 | AD / de novo | Neurology | 2024 review: 550 patients, 182 causative variants. ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 627 records, 76 P/LP vs 262 VUS (application: 72 P/LP). ~12 OMIM allelic (proxy). Active foundation (United Leukodystrophy Foundation). |
| Leukocyte adhesion deficiency I | *ITGB2* | 116920 | 2968 | AR | Immunology | 323 published cases, genotype reported for only 139: the clearest gap in the set. ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 949 records, 87 P/LP vs 345 VUS (no ClinVar figure in the application). Mondo cross-references Orphanet:99842, not 2968: to check. |
| A20 haploinsufficiency | *TNFAIP3* | 616744 | 476102 | AD | Auto-inflammatory | 177 published patients. ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 764 records, 99 P/LP vs 375 VUS (application: 542 records, ~58 pathogenic vs ~289 VUS). Described 2016, so the corpus is entirely open-access era. |
| SSADH deficiency | *ALDH5A1* | 271980 | 22 | AR | Neurometabolic | ~450 published patients; ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 914 records, 152 P/LP vs 333 VUS (application: 143 P/LP vs 262 VUS); proxy count of 5 OMIM allelic variants. Active patient association. |
| Danon disease | *LAMP2* | 300257 | 34587 | X-linked dominant | Cardiac / neuromuscular | >100 published families; ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 986 records, 154 P/LP vs 292 VUS (application: 162 P/LP vs 345 VUS). Sex-differential severity tests whether genotype–phenotype structure survives extraction. |
| Tangier disease | *ABCA1* | 205400 | 31150 | AR | Lipid metabolism | ~200 published patients; ClinVar (release 2026-10-12, read 2026-10-19; GRCh38, single-gene records): 2,006 records but only 85 P/LP, with 705 VUS (application: 1,302 records, 69 P/LP). Big gene, small pathogenic core: the monogenic series must be separated from unrelated testing. |

**Substitutes** (held in reserve if open-access coverage is thin; also the Stretch extension to 12 diseases): Blau syndrome (*NOD2*), Majeed syndrome (*LPIN2*), familial LCAT deficiency (*LCAT*), GAMT deficiency (*GAMT*), arterial tortuosity syndrome (*SLC2A10*), PAPA syndrome (*PSTPIP1*).

**Caveats on the numbers:** ClinVar counts came from MyVariant.info and ClinVar Miner at application time, and were replaced on 2026-10-19 with direct counts from one ClinVar release (2026-10-12), kept beside the application's figures: A20 haploinsufficiency in `analysis/poc/reference_snapshot/2026-10-19/counts.json` (Jimmy's decision), the other five in `counts_<GENE>.json` in the same folder (`DECISIONS.md`, 2026-10-19). Counts are distinct VariationIDs on single-gene GRCh38 records; P/LP sums Pathogenic, Likely pathogenic and Pathogenic/Likely pathogenic; conflicting records are counted apart from VUS. The six-disease study re-counts from a fresh snapshot taken before extraction. OMIM counts are still proxy lower bounds (no OMIM access, D-12). Patient counts are still the application's; see D-14 for corrections.

## 5. Methodology

**Extraction (SLIDERS).** SLIDERS (https://arxiv.org/abs/2604.22294) is an LLM-based systematic-review method that assembles evidence tables from documents and keeps full-text excerpts as direct evidence and provenance. Its core is an evidence reconciliation agent that writes code to reconcile extracted evidence: joining information fragmented across documents, resolving inconsistencies between excerpts, and merging overlapping findings into one table.

**Claude's tasks inside SLIDERS:**
- Claude Opus reads case reports and emits **GA4GH Phenopackets** (phenotype, genotype, interpretation).
- Extract HGVS variant descriptions from non-standard prose.
- Extract **three-state phenotypic features**: observed / excluded / not reported.
- Resolve proband identity across papers (the same patient reported more than once) via the code-writing reconciliation agent.
- Bind findings to **HPO** and **Mondo** terms.
- **Gatekeeper pass:** a second Claude read audits every claim against its cited span.
- **Claude Code** builds the pipeline, the concordance harness, deduplication tooling, VariantValidator integration and the adjudication interface. **Claude Science** keeps every number re-runnable.

**Validation tooling.** HGVS normalized through **VariantValidator**; records checked with **CohortValidator**.

**ClinVar and OMIM are ground truth, not input.** We measure concordance on gene, HGVS normalization, classification and phenotype association against what those databases already assert. This gives a large, automatically scored accuracy estimate with no adjudicator hours used. **The design is pre-registered before extraction.**

**Closing the gap.** Variants absent from both ClinVar and OMIM are adjudicated by the RGI panel, then offered as **ClinVar literature-only submissions** and **OMIM allelic-variant candidates**, each with phenotype evidence and provenance. Adjudicator hours go here, where they are decisive.

**Aggregation.** Per gene, a genotype–phenotype map: which variant classes associate with which phenotype profiles, with denominators and per-publication provenance. Where a gene's ClinVar record is dominated by unrelated-testing noise (e.g., *NOD2* ~23 pathogenic of 1,055; *PSTPIP1* ~7 of 730), separating the monogenic allelic series is itself a test.

**Ascertainment-bias arm.** Against held-out diseases with published natural-history studies, measure how far literature-derived phenotype frequencies deviate from cohort truth, with a per-disease memorization probe.

**Why Claude (as argued in the application).** Its error profile suits provenance-first curation: lowest fabricated-citation rates on DRBench (3.0% and 3.2% of ten systems), top ranks on AA-Omniscience (which rewards declining over guessing), and 97.6% precision on published HPO extraction (Sonnet 4.5). Abstention is a first-class output of our design.

## 6. Success metrics (pre-registered)

1. **Concordance** with ClinVar and OMIM on gene, normalized HGVS, classification and phenotype, with confidence intervals.
2. **False positives:** < 2% of extracted values unsupported by their cited span, audited on 250 claims; abstention when evidence is thin.
3. **Gap closure:** variants absent from both databases adjudicated, prepared and accepted for submission.
4. **Bias:** per-disease deviation from held-out natural-history cohorts, with memorization probe.
5. **Efficiency:** expert-minutes per accepted record; Claude vs an open-weight model under an identical scaffold.

Success = high concordance with a low-false-positive workflow. New database findings are upside.

## 7. Deliverables

- GA4GH Phenopackets for the six pilot diseases
- ClinVar literature-only submissions
- OMIM allelic-variant candidates
- Per-gene genotype–phenotype maps
- Concordance and ascertainment-bias results, **published whether favourable or not**
- Open-source pipeline

## 8. Timeline (6 months)

| Month | Work |
|---|---|
| 1 | Obtain disease literature (~300 full-text reports), OMIM, ClinVar and related reference data; replace proxy counts with direct counts; pre-register; contact Monarch and ClinVar maintainers |
| 2 | Extraction using SLIDERS with Claude |
| 3 | Concordance analysis against ClinVar and OMIM |
| 4 | Adjudication of gap variants |
| 5 | Prepare submissions; bias analysis |
| 6 | Write up results for publication and review |

### Provisional dates and re-plan (D-01 and D-18, 2026-10-18)

The table above is the timeline as committed in the application. Dates assume Month 1 started on 2026-09-21; shift them if the first deposit landed on a different day. The re-plan absorbs Month-1 work that was still undone when Month 1 ended. Under D-18, a one-disease pilot on A20 haploinsufficiency (`POC_DESIGN.md`) runs first, and the pre-registration is frozen after the pilot report.

| Month | Dates | Work after the re-plan |
|---|---|---|
| 1 | 2026-09-21 to 2026-10-20 | Setup, background literature, pre-registration draft, pilot design and code |
| 2 | 2026-10-21 to 2026-11-20 | The pilot on A20 haploinsufficiency and its report. In parallel: corpus search and screening for the other five diseases, reference snapshots and dated counts, open-access check, outreach drafts. Then freeze the pre-registration |
| 3 | 2026-11-21 to 2026-12-20 | Extraction on all six diseases with the frozen pipeline (HA20 reported separately); concordance on each disease as it finishes |
| 4 | 2026-12-21 to 2027-01-20 | Adjudication of gap variants; audit ratings. Spans the December holidays, so check panel availability (D-11) |
| 5 | 2027-01-21 to 2027-02-20 | Submissions after sign-off; bias analysis; model comparison |
| 6 | 2027-02-21 to 2027-03-20 | Write-up. The first deposit expires 2027-03-21 |

## 9. Budget (requested $45,000)

Split: ~65% Claude Science (~$29,000) / ~35% Claude Code (~$16,000).

| Line | Est. |
|---|---|
| Extraction across six diseases, incl. re-runs as HGVS and negation handling stabilize | $8,000 |
| Gatekeeper verification pass (second read of every value vs its span) | $4,000 |
| ClinVar/OMIM reconciliation + concordance harness (re-run in full as normalization improves) | $6,000 |
| Claude Code: pipeline, VariantValidator integration, dedup tooling, adjudication interface | $6,000 |
| Ascertainment-bias arm | $4,000 |
| Claude vs open-weight model head-to-head (published either way) | $2,000 |
| **Core subtotal** | **$30,000** |
| Stretch: extend to all 12 candidate diseases | $9,000 |
| Contingency | $6,000 |

Cost is driven by multipliers, not corpus size: SLIDERS is agentic and re-reads context many times per document, every value is extracted and then re-verified, and concordance needs full re-runs. We committed to **report actual spend against every line and return anything unused.**

## 10. Commitments and boundaries

- **Literature only.** The pilot uses published literature only. RGI's consented cohort (WGS/WES with de-identified medical records) is **out of scope** for this grant, so no human-subjects determination is on the critical path. It is the natural validation set for follow-on work.
- **Human sign-off before any submission** to ClinVar or OMIM.
- **Provenance on every claim** (PMID + verbatim span).
- **Publish results whether favourable or not.**
- **Biosecurity:** none of pathogen research, drug resistance, toxicology or synthetic biology.
- Grant credits do not exempt us from Anthropic's Usage Policy.
- Anthropic treats the application as non-confidential.
- Acknowledge Anthropic's AI for Science program in any publication that used these credits (award email, 2026-08-31).

## 11. RGI assets relevant to follow-on work

- 15 years of operational service: 1,200+ families, 33 countries, 410+ sequencing/research projects, $5.26M in sequencing funded.
- Initial partner in Illumina's iHope program (2016–present).
- **RareShare:** 10,000+ members across 1,000+ rare-disease communities, a route to put draft records in front of people living with the condition.
- Dedicated family advocates from first contact through program completion.

## 12. Key resources

| Resource | Use |
|---|---|
| ClinVar | Ground truth for concordance; target for literature-only submissions |
| OMIM | Ground truth for concordance; target for allelic-variant candidates |
| Monarch phenopacket-store | Existing coverage (408 cohorts; pilot diseases absent) |
| HPO | Phenotype terms |
| Mondo, Orphanet | Disease identifiers |
| GA4GH Phenopacket schema | Output format |
| VariantValidator | HGVS normalization |
| CohortValidator | Phenopacket record checks |
| MyVariant.info, ClinVar Miner | ClinVar counts |
| PubMed / PMC open access | Case report corpus |
| SLIDERS (arXiv 2604.22294) | Extraction and reconciliation method |
