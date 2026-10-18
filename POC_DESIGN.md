# GP-RareLink — Proof-of-Concept (POC) Study Design

*Drafted 2026-10-18 (Month 1). Status: **approved by Jimmy on 2026-10-18**
(decisions in §2.4 logged in `DECISIONS.md`). Written so that a future Claude
Code agent can execute it stage by stage without the drafting session's
context.*

> **Notes added when this branch was merged into `main` (2026-10-18).** Read these before Stage 1; where they differ from the text below, they win.
> - **Pilot first (D-18, Jimmy).** This pilot runs before the pre-registration is frozen. The freeze follows the pilot report, so "frozen separately before the Month-2 extraction" below means frozen after this POC and before the six-disease run.
> - **HA20 is a development disease (D-18).** HA20 is re-extracted under the frozen plan, but the six-disease study reports it separately. Headline concordance uses the other five diseases.
> - **ClinVar-cited seeds (D-19, open).** Stage 1 seeds the corpus with ClinVar-cited PMIDs. Keep the `seed_source` tag, and report every pilot result with and without those papers.
> - **Billing (D-17, open).** The award is claude.ai usage credits, which the award email (`grant/AWARD_EMAIL.md`) does not say cover API calls. Model spend through `ANTHROPIC_API_KEY` may bill to the key's account rather than the grant. Log each run in `BUDGET.md` with the account it billed to. Reconcile against that account's usage page, not "the Console" for the grant.
> - **No contact (Jimmy).** No contact with anyone by any channel (`CLAUDE.md`). Draft messages; Jimmy sends them.
> - **Current state of the plan and the open decisions:** `NOTES_FOR_AGENTS.md`, `DECISIONS.md` and `preregistration/analysis_plan.md` (draft v0.5).

This document is the operational protocol for the first end-to-end run of the
GP-RareLink pipeline on one disease. It is **not** the pre-registration; the
pre-registration (`preregistration/`) is frozen separately before the Month-2
extraction across six diseases. The POC exists to de-risk the pipeline, measure
cost, and calibrate the tooling. Its results inform prompts, schemas and
engineering, but they do not change any pre-registered metric, threshold or the
disease set (`INSTRUCTIONS.md` §1.4).

**Progress log** (update when a stage's gate is met):

| Stage | Status | Date | Notes |
|---|---|---|---|
| 0 Setup and guardrails | done | 2026-10-18 | `pyproject.toml`, `pipeline/{common,extract,harness}`, `configs/prices.yaml` (prices unverified against the live page; `verified_on` is null), isolation tests and runtime guard, 14 tests passing with `uv run pytest`. One distribution with three subpackages rather than separate packages; the boundary is enforced by tests and the guard. |
| 1 Corpus assembly | scripts ready, **not run** | 2026-10-18 | `pipeline/extract/corpus/` (manifest builder, Haiku study-type classifier, full-text fetcher, JATS→Markdown, stats) with offline tests; runbook in `data/literature/ha20/README.md`; seed list from the background bibliography; OMIM request drafted in `reports/drafts/omim_access_request.md`. Blocked here: the cloud environment's network policy denies NCBI, Europe PMC, Unpaywall and omim.org. Run on the Mac mini or allow those hosts in the environment settings. |
| 2 SLIDERS on Claude | adapter done, **smoke test not run** | 2026-10-18 | Patch `pipeline/extract/sliders_adapter/0001-anthropic-provider.patch` on upstream commit `b66094d`, installed by `scripts/install_sliders.sh`; config `configs/sliders_ha20.yaml`; pinned schema complete (no completion call); extraction rules v1; run wrapper with run manifest and usage/cost capture; 24 tests pass incl. wire-payload tests against a fake Messages API. Blocked here: no `ANTHROPIC_API_KEY` in the environment and no full text yet. |

Everything here is subordinate to `INSTRUCTIONS.md` and `CONTEXT.md`. If a step
below conflicts with them, they win; stop and flag it.

---

## 0. How to use this document

- Work through the stages in §4 in order. Each stage has **Goal, Inputs,
  Steps, Outputs, Checks, Gate, Cost, Stop-and-ask**. Do not start a stage
  until the previous stage's gate is met or the failure is logged.
- Every stage that produces a number produces it from a script with a dated
  input and a commit hash. Never hand-compute a figure into a report.
- Commit after every meaningful step. Commit messages name the stage
  (`poc(stage-3): ...`).
- Log every decision that matters in `DECISIONS.md`; log every model run's
  estimate and actual spend in `BUDGET.md`.
- Network: the claude.ai cloud container used to draft this could not reach
  PubMed/PMC, arXiv, NCBI FTP, VariantValidator or OMIM (see
  `background/README.md`). Stages 1, 3 and 6 need a machine with normal
  internet access (the Mac mini was used before). If a fetch fails because the
  host is unreachable, **stop and report; never substitute content from memory**.
- Items marked **[verify]** are specifics the drafting session could not
  confirm online (tool class names, endpoint paths, file names). Verify them
  against the live documentation before relying on them, and remove the tag.

---

## 1. POC objectives and what "done" means

The POC answers eight questions. Each maps to a measured output and a gate in
§4. Gates are POC-specific engineering thresholds, not the pre-registered
success metrics in `CONTEXT.md` §6.

| # | Question | Measured by | POC gate |
|---|---|---|---|
| Q1 | Can we assemble a dated, manifest-backed open-access corpus for one disease? | Stage 1 manifest | ≥ 70 % of seed publications obtained as full text |
| Q2 | Can SLIDERS + Claude turn case reports into per-proband evidence tables with verbatim provenance? | Stage 3 run | Run completes; every non-null cell carries PMID + span |
| Q3 | Do the records convert to valid GA4GH Phenopackets with normalized HGVS? | Stage 4 | 100 % schema-valid; ≥ 95 % of HGVS normalized or flagged with a reason |
| Q4 | What share of extracted values are unsupported by their span? | Stage 5 (automated span check + 50-claim human audit) | Automated span match ≥ 98 %; human-audited unsupported rate ≤ 4 % (point estimate, n = 50) |
| Q5 | Does proband deduplication across papers work? | Stage 3 reconciliation + hand check | Known re-reported patients merged with recorded evidence; 0 false merges in the hand-checked set |
| Q6 | Does the concordance harness run end-to-end against dated ClinVar/OMIM snapshots? | Stage 6 | Produces the concordance table with CIs; no gate on the value |
| Q7 | How complete is extraction relative to a published catalogue? | Stage 6 completeness | ≥ 80 % recall of distinct variants attributable to papers we ingested |
| Q8 | What does it cost, and does it project within budget? | Stage 7 | Measured $/paper and $/proband; six-disease projection ≤ the $8,000 extraction line |

**Done** = all eight measured, written up in `reports/poc_report.md` by
`analysis/poc_report.py`, with the go/no-go recommendation for Month-2
scale-up and the list of pipeline changes to make before freezing the
pre-registration.

The gate for Q4 is deliberately looser than the pre-registered 2 % target:
50 claims cannot certify 2 % (`background/audit_ci_250.py`; with 0 errors in 50
the exact 95 % upper bound is ~7 %). The POC audit is for calibrating the
gatekeeper and catching systematic error classes, not for certifying the
target. The 250-claim audit stays as pre-registered.

---

## 2. Scope decisions

### 2.1 POC disease: A20 haploinsufficiency (HA20, *TNFAIP3*) — recommended

| Criterion | HA20 | Why it matters for a POC |
|---|---|---|
| Corpus size | 177 patients to Aug 2023 (`elhani2024_ha20_177`); ~200 by 2026 (`li2026_ha20_howitreat`). Expect 60–100 primary publications. | Small enough to run several times within a few hundred dollars |
| Open access | Disease described in 2016 (`zhou2016_ha20_original`); the entire corpus is open-access era | Best chance of clearing the Q1 gate without licensing work |
| Completeness benchmark | El Hani 2024 systematic review (177 patients, variant table) and He 2026 multicentre cohort (`he2026_ha20_multicenter`) | Gives Q7 a denominator (scored on primary-paper rows only, since reviews are also ingested; §2.4-3) |
| Deduplication test | The Zhou 2016 families were re-reported in Aeschlimann 2018 (`aeschlimann2018_ha20_cohort`) and consolidated in El Hani 2024 | Natural Q5 test case without a second disease |
| Ground truth | 542 ClinVar records, ~58 P/LP vs ~289 VUS (application-time proxies); OMIM 616744 (phenotype), *TNFAIP3* gene entry 191163 | Enough P/LP for a meaningful concordance table; the VUS mass tests the "monogenic series vs testing noise" separation |
| Variant mix | Mostly truncating (frameshift, nonsense), some missense and splice | Easier HGVS than a missense-heavy gene; see the caveat below |
| Inheritance | AD, de novo and familial | Families with several affected relatives per paper test proband vs relative handling |

**Caveat.** HA20 does not exercise autosomal-recessive compound heterozygosity
or a paywall-heavy pre-2010 corpus. Those are covered by the optional stress
test in §4 Stage 9 (ten LAD-I papers, which include the ten re-reported cases
noted by `almarzanovoa2018_lad1_review`), to be run only if Stages 1–8 pass and
budget allows.

Alternative considered: Alexander disease (best catalogue, `grossi2024_axd_meta`,
550 patients / 182 variants) but with a large, partly paywalled corpus from
2001 onward. It is the right first disease for the full Month-2 run after the
POC proves the pipeline, not for the POC itself.

### 2.2 In scope

- One disease, end to end: corpus → SLIDERS evidence tables → phenopackets →
  gatekeeper → concordance against dated ClinVar and OMIM snapshots →
  completeness vs the published catalogue → cost accounting → report.
- A 50-claim human audit rated by Jimmy, which doubles as gatekeeper
  calibration.
- A light, black-box memorization probe (Stage 8), because HA20 is well
  represented in training data and Q7 could look too good.

### 2.3 Out of scope for the POC

- The other five diseases (Month 2).
- The 250-claim audit, ascertainment-bias arm, Claude vs open-weight
  comparison, adjudication of gap variants, and any submission drafting.
  The scaffold must keep a provider abstraction so the open-weight comparison
  can later reuse it unchanged (SLIDERS already has one; see Stage 2).
- Any patient data. Literature only.
- Contacting Monarch, ClinVar, OMIM, patient foundations, or the SLIDERS
  authors. The OMIM access request is drafted by Claude but submitted by
  Jimmy (§2.4-4).

### 2.4 Decisions (made by Jimmy, 2026-10-18; logged in `DECISIONS.md`)

1. **POC disease = HA20** (§2.1).
2. **Adapt SLIDERS for Claude by forking and adding an Anthropic provider.**
   The public SLIDERS code (https://github.com/stanford-oval/sliders, MIT,
   `pip install sliders-genie`) documents OpenAI and Azure OpenAI providers
   only (checked 2026-10-18 via the README). Build the adapter with the
   official `anthropic` SDK, keep it small, and offer it upstream to Prof.
   Lam's lab later. Do not contact the Lam lab for this without separate
   approval.
3. **Reviews and meta-analyses are included in the extraction corpus,
   flagged `study_type = review`.** They are sources like any other for
   extraction, but: (i) rows whose only source is a review are kept and
   flagged `review_only`; (ii) the reconciliation agent treats a review row
   as a re-report to be merged into the primary report whenever the review
   cites it (§3.6); (iii) completeness against El Hani 2024 (Stage 6) is
   computed on primary-paper rows only, so the benchmark is never scored
   against its own ingestion. If deduplication quality suffers (Stage 3
   check 6), exclusion is reconsidered as a logged change.
4. **OMIM access: Claude drafts the API access request and a summary of the
   current terms for Jimmy to submit** (Stage 1 step 5). Nothing is sent
   without Jimmy. Until access arrives, the POC concordance runs against
   ClinVar only and OMIM is added when the key exists.
5. **POC audit: 50 claims, rated by Jimmy** (§4 Stage 5). The adjudication
   panel is held for the 250-claim audit and Month-4 adjudication.
6. **POC spend ceiling: $1,000, hard stop at $1,500.** Drawn from the
   extraction ($8,000) and gatekeeper ($4,000) lines as itemized in §5. Stop
   and ask before exceeding $1,000; nothing runs past $1,500 without
   re-approval.

---

## 3. Architecture

### 3.1 Data flow

```
seed lists (reviews, PubMed query, ClinVar var_citations)      [Stage 1]
        │
        ▼
data/literature/ha20/manifest.csv  ──►  fetch OA full text  ──►  data/literature/ha20/fulltext/<pmid>.md
        │                                                                     │
        │                                                                     ▼
        │                                             SLIDERS (Claude provider, pinned schema)   [Stage 3]
        │                                                                     │
        │                                     evidence tables (CSV/SQLite) with span + PMID per cell
        │                                                                     │
        │                                                   ┌─────────────────┴──────────────────┐
        │                                                   ▼                                    ▼
        │                                  normalize variants (VariantValidator)      gatekeeper pass        [Stages 4, 5]
        │                                  bind HPO/Mondo, build phenopackets         (claim vs span audit)
        │                                                   │                                    │
        │                                                   ▼                                    ▼
        │                                     data/extracted/ha20/phenopackets/*.json     data/extracted/ha20/gatekeeper.csv
        │                                                   │
        │                        ════════════ isolation boundary (pipeline/extract never crosses) ════════════
        │                                                   │
        ▼                                                   ▼
data/reference/<date>/ (ClinVar, OMIM, HPO, Mondo, literature benchmarks)  ──►  pipeline/harness/   [Stage 6]
                                                                                        │
                                                                                        ▼
                                                                           analysis/poc/*.csv  ──►  reports/poc_report.md  [Stage 7]
```

### 3.2 Ground-truth isolation (non-negotiable)

- `pipeline/extract/` (everything upstream of the boundary) must never read
  `data/reference/`, import from `pipeline/harness/`, or receive ClinVar/OMIM
  content in prompts, few-shot examples, schemas or reconciliation code.
- `pipeline/harness/` is the only code that reads `data/reference/`.
- `tests/test_isolation.py` enforces this statically (greps `pipeline/extract/`
  for `data/reference`, `harness`, `clinvar`, `omim` outside comments) and at
  run time (the extraction entry point refuses to start if
  `GP_RARELINK_REFERENCE_DIR` is set or `data/reference` is readable from its
  working directory; keep reference data outside the extraction container or
  mount it read-denied).
- **Developer-side leak.** While debugging extraction, do not look up specific
  variants in ClinVar/OMIM to "fix" an extraction. Concordance output is read
  only at aggregate level until the extraction run is tagged (Stage 3 output
  is immutable once tagged `poc-ha20-run-N`). Per-variant mismatch triage
  happens after tagging; any prompt or schema change prompted by it is logged
  in `DECISIONS.md` and triggers a fresh tagged run.
- The model's training memory is also a leak path. Extraction prompts
  instruct the model to use only the supplied document, and the Stage 8 probe
  estimates how much it already knows.

### 3.3 Repository layout for the POC

Create only what a stage needs (`INSTRUCTIONS.md` §5).

```
pipeline/
  extract/                 # never reads data/reference
    corpus/
      build_manifest.py    # seed lists → manifest.csv with access status
      fetch_fulltext.py    # PMC OA / Europe PMC / publisher free → fulltext/<pmid>.{xml,pdf}
      to_markdown.py       # JATS XML → Markdown (tables kept); PDF → Markdown via Docling
    sliders_adapter/
      anthropic_provider.py  # Claude provider for SLIDERS (Stage 2)
      schema_ha20.json       # pinned evidence-table schema (§3.5)
      prompts/               # extraction and reconciliation prompt additions, versioned
      run_sliders.py         # wraps sliders.run.run_sliders with run manifest + cost log
    normalize_variants.py  # VariantValidator calls, MANE transcript, original string kept
    bind_ontologies.py     # HPO / Mondo grounding with pinned releases
    to_phenopackets.py     # evidence tables → GA4GH Phenopacket v2 JSON
    validate.py            # schema + pyphetools cohort validation
    gatekeeper.py          # second-read audit of every claim vs its span
    span_check.py          # automated verbatim-span verification
  harness/                 # the only code that reads data/reference
    snapshot_reference.py  # dated ClinVar / OMIM / HPO / Mondo downloads + checksums
    concordance.py         # variant, classification, condition, phenotype concordance + CIs
    completeness.py        # recall vs literature benchmark tables
    dedup_check.py         # known re-reported patients → merge audit
pipeline/common/
    run_manifest.py        # run_id, commit, model, prompt hashes, token usage, cost
    cost.py                # token → $ using the price table pinned in configs/prices.yaml
configs/
    prices.yaml            # model prices with the date they were read
    sliders_ha20.yaml      # SLIDERS config used for the POC
data/
  literature/ha20/         # manifest.csv committed; fulltext/ git-ignored
  extracted/ha20/          # evidence tables, phenopackets, gatekeeper output (committed, small)
  reference/<YYYY-MM-DD>/  # git-ignored; manifest + checksums committed
runs/<run_id>/             # run manifests and logs (committed, no full text)
analysis/poc/              # harness outputs (CSV) and poc_report.py
reports/poc_report.md      # generated
tests/
    test_isolation.py
    test_to_phenopackets.py
    test_span_check.py
adjudication/poc_audit/    # 50-claim audit sheet and ratings
```

### 3.4 Models, settings and provider abstraction

- **Extraction, reconciliation, gatekeeper:** Claude Opus, model ID
  `claude-opus-5-5` (the current Opus as of the price table read
  2026-10-06; re-check `configs/prices.yaml` at run time). Adaptive thinking
  (default on this model), `output_config.effort` = `high` for extraction and
  reconciliation, `medium` for the relevance gate and span checks. Streaming
  for long outputs. Fallback `fallbacks: "default"` with beta
  `server-side-fallback-2026-07-01` so a safety-classifier refusal does not
  silently drop a document; log every fallback in the run manifest.
- **Cheaper second opinion (optional):** `claude-sonnet-5-5` for a
  gatekeeper cross-check, to measure self-preference of an Opus gatekeeper
  auditing Opus output (`background/grant_claim_checks.md` #16). Not a
  replacement; a measurement.
- **Determinism:** no temperature control on these models; run the full
  extraction twice on the final configuration and report run-to-run agreement
  on variants and HPO terms (Stage 3 check 5).
- **Prompt caching:** SLIDERS re-reads documents many times. Put the stable
  instruction block and the document first and the per-table question last,
  with a cache breakpoint after the document, and verify
  `usage.cache_read_input_tokens > 0` on the second call of each document.
  Report cache hit rate in the run manifest.
- **Provider abstraction:** SLIDERS selects the provider from
  `SLIDERS_LLM_PROVIDER`. The adapter adds `anthropic` as a value and leaves
  the OpenAI paths untouched, so the Month-5 open-weight comparison can plug an
  open-weight model into the same scaffold.

### 3.5 Pinned SLIDERS evidence schema (draft)

SLIDERS can take a pinned schema (`schema={"tables": [...]}`) instead of
inducing one. Pin it so runs are comparable. Draft for HA20; the Stage 2
smoke test refines field descriptions but not the table set.

```json
{
  "tables": [
    {"name": "publications",
     "fields": ["pmid", "doi", "first_author", "year", "journal", "study_type",
                {"name": "n_patients_reported", "data_type": "int"},
                {"name": "cites_prior_report_of_same_patients", "data_type": "bool",
                 "description": "True if the paper states that some patients were reported before; capture the cited reference in prior_report_citation"},
                "prior_report_citation"]},
    {"name": "individuals",
     "fields": ["pmid", "individual_label_in_paper", "family_label_in_paper",
                {"name": "is_proband", "data_type": "bool"},
                {"name": "sex", "enum_values": ["male", "female", "not reported"]},
                "age_at_onset_original_text", "age_at_onset_iso8601",
                "age_at_last_evaluation_original_text", "age_at_last_evaluation_iso8601",
                "ethnicity_or_country", "consanguinity",
                {"name": "vital_status", "enum_values": ["alive", "deceased", "not reported"]},
                "deceased_age_iso8601", "cause_of_death",
                "treatment_summary", "disease_label_as_stated", "clinical_diagnosis_basis"]},
    {"name": "variants",
     "fields": ["pmid", "individual_label_in_paper", "gene_symbol_as_stated",
                "variant_original_string", "transcript_as_stated",
                "cdna_hgvs_as_stated", "protein_hgvs_as_stated", "genomic_coordinates_as_stated",
                {"name": "variant_type_as_stated", "enum_values": ["missense", "nonsense", "frameshift", "splice", "in-frame indel", "large deletion/CNV", "other", "not reported"]},
                {"name": "zygosity", "enum_values": ["heterozygous", "homozygous", "compound heterozygous", "hemizygous", "mosaic", "not reported"]},
                {"name": "inheritance", "enum_values": ["de novo", "inherited maternal", "inherited paternal", "inherited unspecified parent", "not reported"]},
                "parental_testing_statement", "functional_evidence_statement",
                "pathogenicity_as_stated_by_authors", "acmg_criteria_as_stated"]},
    {"name": "phenotypic_features",
     "fields": ["pmid", "individual_label_in_paper", "feature_text_as_stated",
                {"name": "status", "enum_values": ["observed", "excluded"],
                 "description": "Only rows for features the paper explicitly reports as present or explicitly reports as absent. Never emit a row for a feature the paper does not mention."},
                "onset_original_text", "onset_iso8601", "severity_or_detail",
                "hpo_label_candidate", "hpo_id_candidate"]},
    {"name": "phenotype_not_reported_checklist",
     "fields": ["pmid", "individual_label_in_paper", "checklist_feature",
                {"name": "status", "enum_values": ["observed", "excluded", "not reported"]}],
     "description": "For a fixed list of ~20 HA20 core features (oral ulcers, genital ulcers, GI ulcers, recurrent fever, arthritis, uveitis, autoimmune thyroiditis, etc.), the three-state status per individual. This table is what makes 'not reported' explicit."}
  ]
}
```

Rules baked into the schema descriptions and the prompt additions
(`pipeline/extract/sliders_adapter/prompts/`):

1. Use only the supplied document. Do not use outside knowledge of the gene,
   the disease or the variant. If the paper does not state it, write
   "not reported".
2. Every cell carries a verbatim span (SLIDERS does this natively) and the
   PMID. The span must be copied exactly; no paraphrase.
3. Keep original strings. Never convert protein-only descriptions into cDNA
   HGVS; record what the paper says and let normalization happen downstream.
4. Three-state phenotypes: "observed" and "excluded" only when explicit;
   everything else is "not reported". Never collapse "not reported" into
   "excluded".
5. One row per individual per paper; family members are individuals with
   `is_proband = false` unless the paper calls them probands.
6. Flag re-reports: if the paper says patients were described before, capture
   the citation; the reconciliation agent uses it as merge evidence.

### 3.6 Deduplication (reconciliation) rules

SLIDERS' reconciliation agent writes SQL to merge rows. Constrain it with an
explicit merge policy, versioned under `prompts/`:

- Candidate merge key: same gene, same normalized variant (after Stage 4) or
  identical original string, plus at least one of: same family label, same
  sex and age at onset within tolerance, explicit "previously reported" citation
  linking the two PMIDs, or overlapping author list with the same centre.
- Each merge writes a row to `data/extracted/ha20/merges.csv` with the two
  (pmid, individual_label) pairs, the evidence used, and a confidence label
  (`explicit_citation`, `strong_match`, `weak_match`). `weak_match` merges are
  kept separate in the phenopacket output and listed for the human audit.
- Never merge across different variants unless an explicit citation says they
  are the same patient (papers do correct variants).
- Review rows (`study_type = review`): when a review's table cites a PMID for
  a patient and that PMID is in the corpus, merge the review row into the
  primary row with confidence `explicit_citation` and keep the primary paper's
  spans as the record of record. A review row with no matching primary row
  stays as its own individual flagged `review_only`, and its PMID in the
  phenopacket is the review's.
- Report: number of individuals before and after merging, by confidence label.

### 3.7 Phenopacket construction

- Library: the `phenopackets` Python package (protobuf bindings for schema
  v2) and `pyphetools` for cohort validation **[verify current package names,
  versions and the `CohortValidator` API]**.
- One phenopacket per merged individual. `id` = `ha20-<run_id>-<n>`;
  `subject.sex`, `subject.timeAtLastEncounter` from the evidence table;
  `phenotypicFeatures[]` with HPO term, `excluded: true` for excluded
  features, `onset` when stated; `interpretations[]` with
  `diagnosis.disease` = Mondo ID for HA20 (with OMIM 616744 and ORPHA 476102
  cross-references) and `genomicInterpretations[]` carrying a
  `variantInterpretation.variationDescriptor` with HGVS expressions (c., p.,
  g. on GRCh38), the MANE Select transcript, `allelicState`, and the original
  string kept in `variationDescriptor.description`; `metaData` with resources
  (HPO, Mondo, HGNC, NCBI Gene versions) and `externalReferences` with the
  PMID(s).
- Provenance: each phenotypic feature and each genomic interpretation carries
  an `evidence[]` entry with `reference.id = PMID:<n>` and the verbatim span
  in `reference.description`, plus extraction date.
- "Not reported" cannot be expressed inside a phenopacket except by omission.
  The evidence tables (`phenotype_not_reported_checklist`) remain the primary
  three-state record; the phenopacket is derived. The report says so.
- Pin releases: HPO `hp.json` and Mondo `mondo.json` releases are downloaded
  by `snapshot_reference.py` (they are ontologies, not ground truth, so the
  extraction side may read a copy placed under `data/ontologies/<date>/`,
  never under `data/reference/`).

### 3.8 Variant normalization

- `normalize_variants.py` calls the VariantValidator REST API
  (`https://rest.variantvalidator.org/`; endpoint pattern and rate limits
  **[verify from https://openvar.github.io/variantValidator/]**) with
  GRCh38 and MANE Select transcript selection; falls back to a local Docker
  install if the public API throttles.
- Inputs: `cdna_hgvs_as_stated` with `transcript_as_stated` if present, else
  the MANE Select transcript for *TNFAIP3* (`NM_001270507.2` is the MANE
  Select at the time of drafting **[verify]**), else `genomic_coordinates_as_stated`.
- Outputs per variant: normalized c./p./g. HGVS, transcript, VCF-style key
  (`chr:pos:ref:alt`, GRCh38), VariantValidator warnings, and a status in
  {`normalized`, `corrected` (VariantValidator changed the description; both
  kept), `protein_only` (cannot normalize to cDNA without inference; kept as
  protein HGVS only), `unresolvable` (reason)}.
- Protein-only variants are not back-translated. They enter the harness as
  protein-level matches only, reported separately.

### 3.9 Gatekeeper pass

- Unit of work: one (table, row, field, value, span, PMID) claim.
- Prompt: given the claim and the source chunk containing the span, answer
  `supported` / `unsupported` / `partially_supported` / `span_not_found`
  strictly on the verbatim span; no outside knowledge; one-sentence reason.
- Model: `claude-opus-5-5`, effort `medium`; optional Sonnet cross-check.
- Output: `data/extracted/ha20/gatekeeper.csv`. Claims not `supported` are
  excluded from the phenopackets (kept in the evidence table with the flag)
  and counted in the Stage 5 metrics.
- Calibration: the 50 human-audited claims are scored against the gatekeeper
  verdicts; report gatekeeper precision/recall for "unsupported" relative to
  the human labels.

### 3.10 Concordance harness

Reads only `data/reference/<date>/`. Inputs: the tagged extraction output and
the snapshot. Outputs under `analysis/poc/`.

| Measure | Definition | Denominator |
|---|---|---|
| Variant presence | extracted variant (VCF key or normalized g.HGVS) matches a ClinVar variation for *TNFAIP3* | distinct normalized extracted variants |
| Classification concordance | ClinVar germline classification (P/LP vs VUS vs B/LB vs conflicting) for matched variants, cross-tabulated with the authors' stated pathogenicity | matched variants |
| Condition concordance | ClinVar condition(s) for the matched variant include HA20 (MedGen/OMIM 616744/Mondo) | matched variants |
| OMIM allelic variant presence | matched to the *TNFAIP3* allelic variant list (191163.00xx) by HGVS | distinct extracted variants (only if OMIM access is in place) |
| Phenotype concordance | extracted HPO terms per individual vs HPO annotations for OMIM:616744 in `phenotype.hpoa`; report term-level precision and recall with the ancestor-closure rule stated | individuals × terms |
| Gap candidates | extracted variants absent from both ClinVar and OMIM, with PMIDs and spans | distinct extracted variants |

All proportions reported with Wilson 95 % intervals and the snapshot date.
Misses are triaged into {extraction error, normalization error, database
absent, database different classification, literature-vs-database conflict}
after tagging (§3.2), with the triage table committed.

### 3.11 Run manifest and cost accounting

Every model-calling script writes `runs/<run_id>/manifest.json`:

```json
{"run_id": "poc-ha20-run-1", "stage": 3, "started": "...", "finished": "...",
 "git_commit": "...", "dirty_tree": false,
 "model": "claude-opus-5-5", "effort": "high", "provider": "anthropic",
 "sliders_version": "...", "schema_sha256": "...", "prompt_sha256": {"extract": "...", "reconcile": "..."},
 "input_manifest_sha256": "...", "n_documents": 0, "corpus_tokens": 0,
 "usage": {"input_tokens": 0, "cache_read_input_tokens": 0, "cache_creation_input_tokens": 0, "output_tokens": 0},
 "cost_usd": 0.0, "price_table": "configs/prices.yaml@<commit>", "fallbacks": [], "errors": []}
```

`pipeline/common/cost.py` computes `cost_usd` from `usage` and
`configs/prices.yaml` (which records the prices and the date they were read).
After each run, append a row to `BUDGET.md` → Spend log. Reconcile against the
Console export at the end of the POC.

---

## 4. Stages

Time estimates assume one agent session per stage with Jimmy reviewing gates.
Total: roughly 3–4 weeks of calendar time, mostly waiting on access and the
human audit.

### Stage 0 — Setup and guardrails (½ day)

**Goal.** A runnable skeleton with isolation tests before any model call.

**Steps.**
1. Create the layout in §3.3 for Stage 0–2 only. Python ≥ 3.11, `uv` for
   environments, `pyproject.toml` with `pipeline` and `harness` as separate
   packages (so the import boundary is explicit).
2. Add `.env.example` (`ANTHROPIC_API_KEY`, `NCBI_API_KEY`, `OMIM_API_KEY`,
   `GP_RARELINK_REFERENCE_DIR`); confirm `.env` and `data/reference/`,
   `data/literature/*/fulltext/`, `data/ontologies/` are git-ignored.
3. Write `tests/test_isolation.py` (§3.2) and `pipeline/common/run_manifest.py`,
   `pipeline/common/cost.py`, `configs/prices.yaml` (Opus 5.5 $4 / $20 per
   MTok, cache read $0.20, cache write per the pricing page; Sonnet 5.5
   $2 / $10; date read). Re-read the pricing page on a networked machine and
   record the date.
4. `uv run pytest` passes.

**Outputs.** Skeleton, tests, `configs/prices.yaml`.
**Gate.** Tests pass; `git status` clean after commit.
**Cost.** $0 model spend.
**Stop-and-ask.** None.

### Stage 1 — Corpus assembly (1–2 days, networked machine)

**Goal.** A dated manifest of HA20 primary publications with access status
and full text for every open-access paper.

**Inputs.** Seed lists: reference lists of `elhani2024_ha20_177`,
`genereviews_ha20`, `li2026_ha20_howitreat`, `he2026_ha20_multicenter`;
PubMed query (`("A20 haploinsufficiency" OR HA20 OR "TNFAIP3"[Gene]) AND
(case reports[pt] OR "case report" OR cohort OR patients)` with date
≥ 2015-01-01; adjust and record the exact string and date); ClinVar
`var_citations.txt` PMIDs for *TNFAIP3* **[note: this file is ClinVar
content; only the harness may read it, so the seed PMIDs it contributes are
written to the manifest by `harness/seed_from_clinvar.py` and tagged
`seed_source = clinvar_citations`; the PMID list itself is not ground truth
and is safe to use for corpus discovery, but keep the code on the harness
side]**.

**Steps.**
1. `build_manifest.py`: union the seeds, resolve PMID ↔ PMC ID ↔ DOI via
   NCBI E-utilities (ID converter), classify `study_type` (case report, case
   series/cohort, review/meta-analysis, functional only, other) from title and
   abstract with a cheap model call (`claude-haiku-5-5`, log cost) **and**
   a human spot-check of 20 rows, and set `in_extraction_corpus = study_type
   in {case report, case series/cohort, review/meta-analysis}` (decision
   §2.4-3; functional-only and other papers are excluded).
2. `fetch_fulltext.py`: for each in-corpus paper try, in order, PMC OA
   subset (JATS XML via the OA web service), Europe PMC full-text XML,
   publisher free PDF; record `access_status` ∈ {pmc_oa_xml, europepmc_xml,
   publisher_pdf, paywalled, not_found} and the retrieval date and checksum.
   Respect licences: store, do not redistribute; commit the manifest, not the
   text.
3. `to_markdown.py`: JATS XML → Markdown keeping headings, tables and figure
   captions (tables carry most variant and phenotype data); PDFs → Markdown
   via Docling (what SLIDERS uses). Write `fulltext/<pmid>.md` plus a
   `fulltext/<pmid>.meta.json` with the source format and token count
   (`messages.count_tokens`, never a local tokenizer guess).
4. Paywalled papers: list them in the manifest; ask Jimmy whether the Stanford
   or RGI library can supply copies for local use (no redistribution). Do not
   scrape.
5. OMIM access request (decision §2.4-4): on a networked machine, read the
   current OMIM terms and API registration page by hand, then write
   `reports/drafts/omim_access_request.md` containing (a) a dated summary of
   the terms as they apply to storing a gene-level allelic-variant snapshot
   for a research harness with no redistribution, and (b) the request text
   for Jimmy to submit under RGI. Do not submit it.

**Outputs.** `data/literature/ha20/manifest.csv` (committed),
`fulltext/` (git-ignored), `data/literature/ha20/corpus_stats.json` (counts
by study type and access status, token totals; committed).

**Checks.**
- Every in-corpus row has a PMID or DOI and an access status.
- Token total per paper is recorded; flag papers > 150k tokens for chunking
  attention.
- 20-row human spot-check of study-type classification: ≥ 18/20 agree.

**Gate.** Q1: ≥ 70 % of in-corpus papers have full text. If below, record the
shortfall and the paywalled list in `DECISIONS.md`; continue the POC on what
is available (the gate is about the full study's feasibility, not the POC's).

**Cost.** Haiku classification of ~150 abstracts: well under $1. Log it anyway.
**Stop-and-ask.** Library copies of paywalled papers; any bulk download whose
terms are unclear.

### Stage 2 — SLIDERS on Claude: adapter and smoke test (2–3 days)

**Goal.** SLIDERS runs with Claude as the provider on three HA20 papers and
emits the pinned tables with spans.

**Steps.**
1. Install SLIDERS from source (`git clone https://github.com/stanford-oval/sliders`;
   `uv sync`) and read its provider code to find the abstraction behind
   `SLIDERS_LLM_PROVIDER`. Record the commit hash in `configs/sliders_ha20.yaml`.
2. Implement `anthropic_provider.py` with the official `anthropic` Python SDK
   (`client.messages.create` / `.stream`, adaptive thinking default, effort
   via `output_config`, `fallbacks: "default"` with its beta header, usage
   captured per call and summed into the run manifest). Structured outputs
   (`output_config.format`) where SLIDERS expects JSON back; never prefill.
   Keep the change small enough to offer upstream.
3. Run the SLIDERS unit tests with the new provider; add a test that runs one
   small document end to end.
4. Smoke test: three papers (one single-patient case report, one family, one
   cohort table paper) with `schema_ha20.json`, `debug=True`, question:
   "For each individual with a TNFAIP3 variant reported in these documents,
   record the individual, variant, inheritance and every phenotypic feature
   explicitly reported as present or absent." Inspect
   `intermediate_tables/*/01_pre_reconciliation.csv` through
   `05_final_table.csv` by hand.
5. Iterate on schema descriptions and prompt additions until the three
   papers' individuals, variants and features are captured with spans. Log
   each prompt version (hash) and what changed.
6. Measure cache hit rate and cost for the three papers; extrapolate to the
   corpus and write the Stage 3 estimate into `BUDGET.md` → Pre-run estimates.

**Outputs.** Provider adapter, `schema_ha20.json`, prompts v1,
`runs/poc-ha20-smoke-*/manifest.json`, Stage 3 cost estimate.

**How to run the smoke test once Stage 1 has produced Markdown and the key is
in `.env`:**

```bash
scripts/install_sliders.sh                      # once per machine
uv run python -m pipeline.extract.sliders_adapter.run_sliders \
  --docs data/literature/ha20/fulltext_md --run-id poc-ha20-smoke-1 --max-docs 3 --debug
uv run python -m pipeline.extract.span_check --run-id poc-ha20-smoke-1   # Stage 2 check 2 (to be written)
```
Pick the three documents by copying them into a separate directory if the
first three Markdown files are not one case report, one family and one cohort
table paper.

**Checks.**
- Every non-null cell in the final tables has a span and PMID.
- Spans found verbatim in the Markdown (`span_check.py` on the smoke output):
  100 % on three papers, or fix before Stage 3.
- No "not reported" collapsed into "excluded" on hand inspection.
- Isolation tests still pass.

**Gate.** Smoke output judged usable by Jimmy (or a panel member) on the three
papers; cost estimate per paper ≤ $5 (if higher, tune effort/caching first;
if still higher, ask before Stage 3).

**Cost.** Expect < $30 across iterations.
**Stop-and-ask.** Any sign that SLIDERS needs changes larger than a provider
adapter; any wish to contact the Lam lab (not approved yet).

### Stage 3 — Full extraction run (1 day compute, 1 day review)

**Goal.** One tagged, reproducible extraction over the whole HA20 corpus,
run twice.

**Steps.**
1. Add the estimate to `BUDGET.md` (Stage 2 step 6) and get Jimmy's OK if it
   exceeds $200.
2. `run_sliders.py --corpus data/literature/ha20/manifest.csv --schema
   schema_ha20.json --config configs/sliders_ha20.yaml --run-id poc-ha20-run-1`.
   Documents in manifest order; one document per SLIDERS ingestion unit;
   reconciliation across the whole corpus with the merge policy (§3.6).
3. Repeat as `poc-ha20-run-2` with identical configuration.
4. Tag the repo `poc-ha20-run-1` and `poc-ha20-run-2`; commit the evidence
   tables and `merges.csv` under `data/extracted/ha20/<run_id>/`.
5. Log actual spend from the manifests into `BUDGET.md`.

**Outputs.** Evidence tables (CSV + SQLite), `merges.csv`, run manifests.

**Checks.**
1. Counts: papers processed / failed; individuals before and after merging;
   distinct variants; features by status. All from `analysis/poc/extraction_counts.py`.
2. Span check ≥ 98 % verbatim matches (the rest listed).
3. Every variant row has an `original_string`.
4. "not reported" present in the checklist table for every individual.
5. Run-to-run agreement (run-1 vs run-2): Jaccard on distinct variant original
   strings and on (individual, HPO candidate) pairs; report both. No gate, but
   < 0.9 on variants means the prompts are unstable; note it for Stage 7.
6. Dedup hand check: the Zhou 2016 ↔ Aeschlimann 2018 overlap. List the
   merged pairs and confirm each against the papers' own statements. 0 false
   merges; missed merges listed.

**Gate.** Q2 and Q5 checks pass or failures are logged with cause.
**Cost.** Estimate from Stage 2; ballpark for ~80 papers × ~12k tokens with a
~10× re-read multiplier at Opus 5.5 prices: ~$40–80 input + ~$20–40 output per
run, so ~$100–250 for two runs. Treat as an order of magnitude until Stage 2
measures it.
**Stop-and-ask.** Spend above the approved estimate; a refusal or fallback
pattern affecting many documents.

### Stage 4 — Normalization, ontology binding, phenopackets (1–2 days)

**Goal.** Valid phenopackets with normalized variants from run-1.

**Steps.**
1. `snapshot_reference.py --ontologies-only`: download the HPO and Mondo
   releases of the day into `data/ontologies/<date>/` with checksums (these
   are allowed on the extraction side).
2. `normalize_variants.py` on the distinct variants of run-1 (§3.8); cache
   responses on disk keyed by input string so re-runs are free.
3. `bind_ontologies.py`: map `hpo_label_candidate`/`hpo_id_candidate` to the
   pinned HPO release (exact ID if valid and label matches; else label match;
   else a model call constrained to choose among top-k lexical candidates
   from the pinned release, with "no suitable term" allowed). Map the disease
   to Mondo with OMIM/ORPHA cross-references. Record the binding method per
   row.
4. `to_phenopackets.py` (§3.7).
5. `validate.py`: schema validation via the `phenopackets` bindings plus
   `pyphetools` cohort validation (HPO term validity, obsolete terms,
   redundant ancestor terms, allelic requirement for AD) **[verify API]**.
   Fix converter bugs; never edit a phenopacket by hand.

**Outputs.** `data/extracted/ha20/<run_id>/variants_normalized.csv`,
`hpo_bindings.csv`, `phenopackets/*.json`, `validation_report.json`.

**Checks.**
- 100 % of phenopackets schema-valid.
- Normalization status distribution: ≥ 95 % `normalized` or `corrected`;
  `protein_only` and `unresolvable` listed with reasons.
- HPO binding: share bound by exact ID, by label, by model; share "no
  suitable term". Sample 30 model-bound terms for a human check.
- Three-state preserved: no `excluded` feature in a phenopacket without an
  `excluded` row in the evidence table.

**Gate.** Q3 thresholds met.
**Cost.** Binding model calls: small (Sonnet or Haiku; log). VariantValidator: free.
**Stop-and-ask.** VariantValidator public API limits that require a local
install (not a decision, but tell Jimmy if it delays the stage).

### Stage 5 — Gatekeeper and 50-claim human audit (2 days compute/prep; audit time depends on the rater)

**Goal.** Measure the unsupported-value rate at POC scale and calibrate the
gatekeeper.

**Steps.**
1. `gatekeeper.py` over every claim in run-1 (§3.9). Log spend.
2. Build the audit sample with `analysis/poc/make_audit_sample.py`: 50 claims
   stratified 20 variant fields, 20 phenotypic features (10 observed, 10
   excluded), 10 demographic/inheritance fields; random with a recorded seed;
   oversample nothing. Each row shows the value, the span, the PMID and a
   link to the paper section; the gatekeeper verdict is hidden from the rater.
3. Jimmy (decision §2.4-5) labels each claim supported / unsupported /
   partially supported on the span alone, with a note. Disagreements with the
   gatekeeper and any "partially" are re-read by Jimmy with the full
   paragraph in view and the final label recorded with a reason.
4. `analysis/poc/audit_metrics.py`: unsupported rate with exact 95 % CI;
   gatekeeper vs human confusion matrix; list of error classes (e.g. negation
   missed, table row misaligned, family member attributed to proband).

**Outputs.** `gatekeeper.csv`, `adjudication/poc_audit/sample.csv`,
`ratings.csv`, `analysis/poc/audit_metrics.json`.

**Checks.** The gate below; plus: every unsupported claim traced to an error
class and a proposed fix (prompt, schema, converter), recorded for Stage 7.

**Gate.** Q4: automated span match ≥ 98 %; human unsupported rate ≤ 4 %
(point estimate). If above 4 %, the POC continues (the measurements in
Stages 6–7 are still needed) but the report's recommendation must include
the fixes and a re-run before Month 2.
**Cost.** Gatekeeper: roughly one short call per claim; for a few thousand
claims at Opus 5.5 with cached document chunks, expect $20–60. Measure.
**Stop-and-ask.** None beyond scheduling Jimmy's audit time.

### Stage 6 — Reference snapshot and concordance (1 day, networked machine)

**Goal.** Dated ground-truth snapshots and the first concordance and
completeness tables.

**Steps.**
1. `snapshot_reference.py --date <today>`: ClinVar monthly release files
   from the NCBI FTP `tab_delimited/` directory (`variant_summary.txt.gz`,
   `var_citations.txt.gz`, `submission_summary.txt.gz` **[verify file names
   against the directory README]**) filtered to *TNFAIP3* (GeneID 7128),
   plus `phenotype.hpoa` from HPO, Mondo release, and, if access is in place,
   the OMIM entry 191163 allelic variant list via the OMIM API. Write
   `data/reference/<date>/MANIFEST.json` (URLs, release dates, checksums,
   row counts) and commit the manifest only.
2. Record the direct counts this produces (ClinVar records for *TNFAIP3* by
   classification; OMIM allelic variants) in `data/reference/<date>/counts.json`
   and cite them in the report with the date. These replace the application's
   proxy counts for HA20 (`CONTEXT.md` §4 caveat).
3. Place the literature benchmark under `data/reference/<date>/benchmarks/`:
   the variant and patient tables from El Hani 2024 (transcribed by script
   from the paper's supplementary data if machine-readable; otherwise by a
   model extraction run **outside** the extraction pipeline, with its own
   gatekeeper pass and a 20-row human check, because this table is scored
   against and must itself be reliable).
4. `harness/concordance.py --run poc-ha20-run-1 --reference data/reference/<date>` (§3.10).
5. `harness/completeness.py`: recall of distinct benchmark variants computed
   on extraction rows sourced from primary papers only (rows whose source is
   a review are excluded from the numerator, because El Hani 2024 is itself
   in the corpus; §2.4-3), with the denominator restricted to benchmark
   variants whose source PMIDs are in our full-text corpus; report the
   unrestricted recall and the review-inclusive recall too, labelled.
6. `harness/dedup_check.py`: compare merged individuals with the benchmark's
   patient count per PMID where available.
7. After tagging and running, triage every miss (§3.10) and commit the table.

**Outputs.** `data/reference/<date>/MANIFEST.json`, `counts.json`,
`analysis/poc/concordance.csv`, `completeness.csv`, `miss_triage.csv`,
`gap_candidates.csv`.

**Checks.** Harness never imported by `pipeline/extract` (tests); every
proportion has a denominator and a CI; snapshot date on every table.

**Gate.** Q6 (harness runs) and Q7 (restricted recall ≥ 80 %).
**Cost.** Benchmark transcription run: small; log it. Everything else: $0.
**Stop-and-ask.** None if OMIM access is still pending (run ClinVar-only and
say so). Do not store OMIM content until the terms are confirmed by hand and
Jimmy has the key.

### Stage 7 — Cost accounting and POC report (1 day)

**Goal.** The report that decides Month-2 scale-up.

**Steps.**
1. Reconcile `BUDGET.md` spend-log rows against a Console usage export for
   the POC dates; note any discrepancy.
2. `analysis/poc_report.py` assembles `reports/poc_report.md` from the
   committed CSV/JSON outputs only. Sections: corpus (Q1), extraction and
   stability (Q2, run-1 vs run-2), phenopackets (Q3), provenance and audit
   (Q4, with the error-class table and gatekeeper calibration), dedup (Q5),
   concordance (Q6, with the dated counts), completeness (Q7), cost (Q8:
   $/paper, $/proband, $/claim, cache hit rate, six-disease projection using
   each disease's expected paper count from `CONTEXT.md` §4 and the measured
   per-paper cost, with a stated multiplier range), memorization probe
   (Stage 8 if run), limitations, and the recommendation with the list of
   changes to make before freezing the pre-registration.
3. Report unfavourable results as plainly as favourable ones
   (`INSTRUCTIONS.md` §1.5), including the Murugan 2026 proband-counting
   concern if the dedup results bear on it.
4. Commit; mirror to the claude.ai Project per `DECISIONS.md` (2026-10-18).

**Outputs.** `reports/poc_report.md`, updated `BUDGET.md`, a `DECISIONS.md`
entry with the go/no-go and the pipeline changes.
**Gate.** Jimmy's review.
**Cost.** $0.
**Stop-and-ask.** The go/no-go itself.

### Stage 8 — Memorization probe, light version (optional, ½ day)

**Goal.** Estimate how much the extraction model already knows about HA20
variants without documents, so Q7 can be interpreted.

**Steps.**
1. Closed-book query to `claude-opus-5-5` (no documents, same effort):
   "List every TNFAIP3 variant reported in patients with A20
   haploinsufficiency, with the PMID of the first report." Repeat 5 times;
   record all answers.
2. Score against the run-1 extracted set and against the ClinVar snapshot
   (harness side): share of closed-book variants that are real (appear in
   either), share of extracted variants the model produced closed-book, and
   the PMID accuracy of the closed-book citations.
3. Split by publication year (pre/post the model's training cutoff as
   published) and report both halves, because membership signals confound
   with date (`background/grant_claim_checks.md` #15).

**Outputs.** `analysis/poc/memorization_probe.json`.
**Interpretation.** High closed-book recall does not invalidate extraction
(every extracted value still has a span) but it means Q7 overstates what the
pipeline would achieve on an obscure disease; say so in the report. This is a
pilot of the Month-5 probe, not a replacement.
**Cost.** < $5.

### Stage 9 — AR / paywall stress test (optional; only after Stages 1–8 pass)

Ten LAD-I (*ITGB2*) papers chosen to include compound-heterozygous cases and
the re-reported cases noted in `almarzanovoa2018_lad1_review`. Same pipeline,
same checks as Stages 3–5 at reduced scale, no human audit. Purpose: confirm
that zygosity, two-variant individuals and consanguinity fields behave before
Month 2. Budget: ≤ $50. Needs Jimmy's OK (it touches a second pilot disease,
though it is not a change to the disease set).

---

## 5. Budget for the POC

Estimates to be replaced by Stage 2 measurements; every run adds a row to
`BUDGET.md` → Pre-run estimates before it starts and → Spend log after.

| Item | Line in `CONTEXT.md` §9 | Estimate | Basis |
|---|---|---|---|
| Stage 1 study-type classification | Extraction | < $1 | ~150 abstracts on Haiku 5.5 |
| Stage 2 smoke tests and prompt iteration | Extraction | ≤ $30 | 3 papers × ~10 iterations |
| Stage 3 two full runs | Extraction | $100–250 | §4 Stage 3 ballpark; measure in Stage 2 |
| Stage 4 HPO binding calls | Extraction | ≤ $10 | thousands of short calls, cached candidates |
| Stage 5 gatekeeper | Gatekeeper | $20–60 | one short call per claim, document chunks cached |
| Stage 6 benchmark transcription | Reconciliation/harness | ≤ $10 | one review's tables |
| Stage 8 probe | Ascertainment-bias arm | < $5 | 5 closed-book calls |
| Stage 9 stress test | Extraction | ≤ $50 | 10 papers, one run |
| Claude Code sessions building the pipeline | Claude Code | tracked from Console, not estimable per token here | |
| **Model-call total** | | **≈ $200–400**, ceiling $1,000 (§2.4-6) | |

Prices used: `claude-opus-5-5` $4 / $20 per MTok input/output, cache read
$0.20; `claude-sonnet-5-5` $2 / $10; `claude-haiku-5-5` $0.10 / $0.50
(price table cached 2026-10-06 in the Claude API reference; re-read the live
pricing page in Stage 0 and record the date in `configs/prices.yaml`). The
Message Batches API halves cost for non-interactive stages (gatekeeper, HPO
binding); use it there if latency does not matter. Prompt caching is the main
lever for SLIDERS' repeated reads.

The six-disease projection in the report should show the measured per-paper
figure, the multiplier range, and the application's $8,000 line side by side.

---

## 6. Risks and how the POC handles them

| Risk | Signal | Handling |
|---|---|---|
| SLIDERS needs more than a provider adapter to run on Claude (e.g. OpenAI-specific structured output or tool calling assumptions) | Stage 2 tests fail or need deep changes | Stop and ask; fallback is a minimal SLIDERS-style scaffold (chunk → gated extraction with spans → code-writing reconciliation) built in-house with the same pinned schema, documented as a deviation from "SLIDERS" in the report |
| Open-access coverage below 70 % | Stage 1 gate | Record; ask about library copies; the full study's substitute-disease rule still applies in Month 1 |
| Model fills gaps from memory | Stage 5 audit finds values with no span or with spans that do not say what the value says; Stage 8 shows high closed-book recall | Tighten prompts; make the gatekeeper stricter; report it |
| Gatekeeper agrees with extractor out of self-preference | Stage 5 calibration shows low recall for "unsupported" | Sonnet cross-check; stricter span-only prompt; consider a differently-prompted second gatekeeper |
| Proband over- or under-merging | Stage 3 check 6 | Merge policy tuning; weak merges kept separate; report |
| Reviews in the corpus inflate individual counts or create duplicate records | `review_only` rows numerous; Stage 3 check 6 misses merges that a citation makes explicit | Merge review rows on cited PMIDs (§3.6); report counts with and without review-only rows; reconsider exclusion as a logged change |
| HGVS normalization failures on protein-only or legacy descriptions | Stage 4 status distribution | Keep original strings; protein-level matching in the harness; no inference |
| Reference databases themselves wrong or incomplete | Stage 6 triage finds literature-vs-database conflicts | Triage categories, not "extraction error" by default (`background/grant_claim_checks.md` #17) |
| OMIM access not available in time | Stage 6 | ClinVar-only concordance for the POC, OMIM added when access arrives; say so |
| Rate limits or refusals | Run manifest `fallbacks`/`errors` | Retries with backoff; fallback logging; never skip a document silently |
| Spend overrun | `BUDGET.md` running total | Hard stop at the ceiling; ask |
| Ground-truth leak during debugging | Any ClinVar/OMIM lookup while editing extraction code | §3.2 rules; tests; tagged runs |

---

## 7. What the POC must hand to the pre-registration

The pre-registration is written after the POC and frozen before Month 2.
From the POC it takes:

- The final pinned schema and prompt hashes.
- The definition of each concordance measure and the matching rule for
  variants (VCF key on GRCh38; protein-level fallback reported separately).
- The HPO ancestor-closure rule for phenotype concordance.
- The merge policy and how weak merges are counted.
- The triage categories for concordance misses.
- Whether the 2 % false-positive target is judged on the point estimate or
  the upper confidence bound (`background/grant_claim_checks.md` #14) — a
  decision for Jimmy, informed but not made by the POC.
- The cost model (measured $/paper, multiplier range) for the six-disease
  estimate.
- The memorization-probe design, informed by Stage 8.

The POC's HA20 run is reported as a pilot. HA20 is re-extracted from scratch
under the frozen plan with the final pipeline in Month 2; the pilot run is not
reused as a study result.

---

## 8. Checklist for the executing agent

Before starting:
- [ ] Read `CLAUDE.md`, `INSTRUCTIONS.md`, `CONTEXT.md`, `DECISIONS.md`, `BUDGET.md`, this file.
- [ ] Read the §2.4 decisions (logged in `DECISIONS.md`, 2026-10-18) and follow them; raise anything that needs changing with Jimmy before deviating.
- [ ] Confirm the machine can reach PubMed/PMC, NCBI FTP, VariantValidator, HPO/Mondo releases (and OMIM if applicable); if not, do only the stages that need no network.
- [ ] `ANTHROPIC_API_KEY` in `.env`; `uv run pytest` passes.

For every stage:
- [ ] Estimate first (`BUDGET.md`), run, log actual spend.
- [ ] Commit outputs and the run manifest; tag full extraction runs.
- [ ] Run `tests/test_isolation.py` before and after.
- [ ] Record decisions and deviations in `DECISIONS.md`.
- [ ] Write numbers only from scripts; cite the script, input date and commit.

Never:
- [ ] Fabricate a PMID, span, variant or count.
- [ ] Put ClinVar/OMIM content on the extraction side.
- [ ] Collapse "not reported" into "excluded".
- [ ] Hand-edit a phenopacket or an evidence table.
- [ ] Contact an external party, submit anything, or exceed the spend ceiling without Jimmy.
