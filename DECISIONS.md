# Decisions

Dated log of project decisions and, once the pre-registration is frozen, every deviation from it (`INSTRUCTIONS.md` §1.4). Newest entries go at the top of each section.

**Pre-registration status:** draft v0.6 (`preregistration/analysis_plan.md`), **not frozen**. Until it is frozen, changes to the draft are revisions, not deviations. Under D-18 the freeze comes after the pilot report. Still blocking the freeze: D-08 to D-12, D-17 and D-19.

How to use this file:
- **Open decisions** lists what needs Jimmy's call, with options and a recommendation. When one is decided, move it to the decision log with the date and who decided.
- **Decision log** records calls that matter. Claude's own reasonable calls go here too, marked as such (`INSTRUCTIONS.md` §7).
- **Pre-registration deviations** starts empty and is used only after freezing.

---

## Open decisions

### Needed now, for the pilot

**D-17 · How the pipeline calls Claude** (opened 2026-10-18)
- **The problem:**
  - The grant assumed extraction, gatekeeper, concordance and bias runs would call Claude from code. The application gave a Console org ID for API credits.
  - The award email says the credits sit on a claude.ai account and work across chat, Claude Code, Cowork and Claude Science. It doesn't mention API usage.
- **Now urgent:** the pilot's code calls the Anthropic API with an `ANTHROPIC_API_KEY` (pilot decision 2, below). Unless Bailey confirms the award covers API calls, the pilot's model spend (estimated $200–400, ceiling $1,000) bills to whichever account owns the key, not to the grant credits.
- **Why it matters beyond the pilot:** most of the core budget (lines 1–3, 5 and 6) is model runs inside the pipeline. The route also affects two parts of the plan:
  - pinning the model ID and settings (§6.1);
  - the identical-scaffold comparison with an open-weight model (§7.5), which is simplest when both models are called from code.
- **Options:**
  - Run the pipeline's model calls through a claude.ai surface the credits cover, such as Claude Code running the pipeline scripts, or Claude Science. This works only if that surface supports the batch runs and logging the plan needs.
  - Use the API with separate funding not covered by the award.
  - Ask Bailey whether the credits can cover API calls from the pipeline.
- **Recommendation:** Jimmy asks Bailey before adding the key (Claude does not contact anyone). If the answer is slow, the pilot can still go ahead on a separately funded key, logged in `BUDGET.md` with the account it billed to. The pilot's SLIDERS adapter already keeps model calls behind one provider setting, so the route can change later without touching extraction logic.

**D-19 · ClinVar-cited papers as corpus seeds** (opened 2026-10-18)
- **The conflict:** the pilot's Stage 1 adds the PMIDs ClinVar cites for *TNFAIP3* to the corpus search. This is done on the harness side, and the papers are tagged `seed_source = clinvar_citations`. The pre-registration draft (§5.1) excludes ClinVar and OMIM citation lists from corpus building.
- **Why it matters:** papers ClinVar already cites are more likely to agree with ClinVar. Seeding from them inflates concordance and hides gap variants.
- **Recommendation:**
  - For the pilot, keep the ClinVar-seeded papers but report every result with and without them; the tags make this cheap.
  - Use the difference between the two to set the rule for the six-disease study before the freeze.

**D-31 · Stacked multi-patient table cells** (opened 2026-10-19)
- **The finding:** in the re-audit (`reports/poc_stage4_5_findings.md` §10.7), all 3 unsupported claims are values read by position from one supplementary table whose cells stack several patients' values ("18 / 24 / 21 / 57"). Jimmy could not verify them and judged them uncertain. The v4 rule allows such positional reading when the number of values equals the number of people.
- **Recommendation:** extraction v6 drops positional reading. A stacked value is recorded only when the paper labels it for that person; otherwise "not reported", with the reason in `method_note`. Gatekeeper v4 treats a positional reading as at most partially supported. Both go into the frozen pipeline; no new pilot run (the 250-claim audit is the measure).
- **Cost of the change:** some lost recall in papers that publish per-family stacked tables (42128528's Supplementary File 1 is the example).

### Needed before the pre-registration can be frozen

**D-08 · Substitute-disease trigger**
- **Question:** What open-access threshold replaces a pilot disease with a substitute?
- **Placeholder for discussion:** fewer than 15 accessible eligible reports, or less than 50% of eligible reports accessible.
- **Constraint:** decided before extraction, on access grounds only.

**D-09 · Registry and timing**
- **Recommendation:** register on OSF, publicly. Freeze after the pilot report and before the six-disease run (D-18).
- **Alternatives:** an embargoed OSF registration, or attaching the plan to a preprint.

**D-10 · Open-weight comparison: model, disease(s), compute**
- **Questions:**
  - Which open-weight model?
  - Run on which disease(s)?
  - How many audited claims per model?
  - Where does it run? The $2,000 line is Claude credits; open-weight compute isn't budgeted.
- **Recommendation:** pick the model by the time of the freeze, on the criteria open weights, long context and tool use. Run it on A20 haploinsufficiency (the pilot disease) plus one other.
- **Depends on D-17:** an identical scaffold needs both models to be called the same way.

**D-11 · Panel time**
- **Questions:**
  - Who rates the 250-claim audit (two raters plus a tie-breaker is drafted)?
  - Which optional add-ons can the panel afford: a pre-gatekeeper sample, gatekeeper calibration, a false-abstention check, an open-weight audit sample, discordance triage?
- **Status:** needs the panel's availability. No time estimate is given here because none has been measured.
- **Pilot:** Jimmy rates the pilot's 50 claims himself (pilot decision 5). The panel is reserved for the 250-claim audit and Month-4 adjudication.

**D-12 · OMIM access route**
- **The problem:** omim.org blocks automated reading. The archived terms bar redistribution without a license (`grant_claim_checks.md` §13).
- **Options:** request API or download access; read the current terms by hand; or limit OMIM concordance to what can be lawfully obtained.
- **Blocks:** the OMIM half of concordance (O2) and the OMIM gap definition (O3).
- **Progress:** the pilot session drafted the access request (`reports/drafts/omim_access_request.md`), for Jimmy to submit (pilot decision 4). Its terms table is blank because omim.org was unreachable. Until access arrives, the pilot's concordance is ClinVar-only.

### Needed later

**D-13 · ClinVar collection method for our submissions**
- **The problem:** "Literature only" means no added submitter curation and recommends no classification (`clinvar_submission_docs`). Our panel-adjudicated, classified records may fit "curation" better (`grant_claim_checks.md` §12).
- **Needed by:** before Month-4 adjudication, because it shapes what the panel records.
- **Note:** the grant says "literature-only submissions", so switching to "curation" is a change to log here.

**D-14 · Correct figures in `CONTEXT.md`**
- **Proposed edits:**
  - **Tangier:** change "~200 published patients" to ~100–150 (`koseki2021_tangier_review`).
  - **Danon:** change ">100 families" to "about 100 families; ≥146 molecularly confirmed patients".
  - **phenopacket-store:** replace "408 cohorts", which has no published source, with a dated count.
  - **LAD-I** (new, found 2026-10-18): the impact statement says "genotypes for 184 LAD-I patients whose variants were published but never structured". 184 = 323 − 139, and the source review reports that genotype was *not* reported for those patients. If so, extraction cannot recover them. This affects how LAD-I gap closure is described. Check against `almarzanovoa2018_lad1_review`.
- **Scope:** the disease set is unchanged; these are wording and number fixes.

**D-15 · Budget tracking**
- **Answered by the award email:** the credits are one pool on a claude.ai account, covering chat, Claude Code, Cowork and Claude Science. Cowork and Claude Code sessions on the funded account draw on that pool. There are no separate Claude Science and Claude Code allocations.
- **Still open:**
  - Are this project's Cowork and Claude Code sessions, including this one, running on the funded account?
  - The grant's 65% / 35% split is now only an internal plan. Recommendation: keep reporting per budget line, as committed, and drop the split unless Anthropic asks for it.
  - Is the plan's included usage consumed before the credits? The email calls them "extra usage credits". This changes what counts as spend; check the usage-credits help article linked in the email.
  - What counts as a "large share" of a line, requiring Jimmy's approval before a run (25% proposed)?
- **Details:** see `BUDGET.md`.

**D-16 · Release license and verbatim spans**
- **Questions:** Which license applies to released phenopackets and evidence tables? How are verbatim spans from non-open-access papers handled on release?
- **Needed by:** Month 6.

---

## Decision log

### 2026-10-19 · Re-audit second look done: final 3 of 48 unsupported (6.3%); D-31 opened
- **Second look:** two labels changed (C006555 to supported; C011145 to partial). The three stacked-table claims stay unsupported; Jimmy: he "could not clearly assess" those tables and thinks them uncertain. Two claims stay unrated (n = 48).
- **Final, gated:** 3 of 48 unsupported (6.3%, exact 95% CI 1.3–17.2%); Q4 not met. Sensitivity without the three uncertain claims: 0 of 45. No variant field is unsupported (0 of 20, against 3 of 20 in the first audit).
- **Gatekeeper v3:** flagged 1 of 4 not-fully-supported claims, no false flags.
- Opened D-31 (stacked cells). Files: `analysis/poc/audit_metrics_v5.json`, `audit_metrics_v5_excluding_uncertain.json`, report §10.7. No changes to metrics or thresholds.

### 2026-10-19 · D-30 decided: Chen 2020 Table S1 replaces El Hani 2024 as the Q7 benchmark; C032922 stays unsupported; HA20 counts updated
Jimmy's answers to three questions (asked in the session, 2026-10-19):
- **D-30 · Q7 benchmark: Chen 2020 Table S1** (PMID 33101300, PMC7546856, CC BY). It replaces El Hani 2024 (`POC_DESIGN.md` Stage 6 step 3), which is paywalled from the cloud environment. This changes the pilot design; the pre-registration is not frozen, so it is a revision, not a deviation.
  - Recommended option was Jimmy downloading El Hani; he chose the substitute. Trade-offs, as put to him: Chen 2020 is smaller (89 patients, 32 distinct protein-level variants, 21 source papers) and is itself in the corpus; its table was extracted in run-2.
  - Handled as the design handles El Hani: the numerator counts only rows from primary papers (not reviews, not Chen 2020); the restricted denominator keeps benchmark variants with a source paper in the run. Transcribed by script (`pipeline/harness/benchmark_chen2020.py`); the patients number 1–89 without gaps, which the script checks.
  - Results: `reports/poc_stage6_findings.md` §6.
- **C032922 stays unsupported** as Jimmy rated it ("Keep unsupported"). The audit stands at 3 of 50 unsupported (6.0%); Q4 is not met.
- **CONTEXT.md §4, HA20 row:** the ClinVar figures are replaced with the direct count (release 2026-10-12: 764 records, 99 P/LP, 375 VUS), with the application's figures kept beside them. The other five rows wait for their snapshots.

### 2026-10-19 · Stage 6 run on ClinVar and HPO; snapshot kept outside the repo (Claude's calls)
- **Snapshot location.** `POC_DESIGN.md` Stage 6 says to write the snapshot under `data/reference/<date>/` and commit its manifest. The extraction guard refuses to run while a populated `data/reference/` is readable, so a committed manifest there would block every later extraction run. The snapshot content is kept outside the repository (a reference root given to the harness), and only `MANIFEST.json` and `counts.json` are committed, under `analysis/poc/reference_snapshot/<date>/`. The intent of the design (ground truth out of extraction's reach) is unchanged.
- **Direct counts for *TNFAIP3*** (ClinVar release 2026-10-12, GRCh38, distinct VariationID): 764 single-gene records; 99 P/LP (68 P, 27 LP, 4 P/LP); 375 VUS; 76 name HA20. These replace the application's provisional figures (542 records, about 58 pathogenic, about 289 VUS). `CONTEXT.md` §4 is not edited here; the six-disease counts will be taken together.
- **OMIM not fetched** (no key; terms unconfirmed). **Q7 not measured:** the El Hani 2024 benchmark is paywalled from the cloud environment.
- Results: `reports/poc_stage6_findings.md`. No changes to metrics, thresholds or extraction prompts.

### 2026-10-19 · D-29 decided: fixes and a 20-paper re-run after the Q4 miss
Jimmy: "go with your recommendations on D-29" (this session, 2026-10-19). Accepted as recommended (`reports/poc_stage4_5_findings.md` §10.5):
- **Extraction instructions v5** gain a variant-field rule: zygosity, inheritance, variant type, pathogenicity, ACMG criteria and functional evidence come only from this person's own row, column or sentence, or from a statement about a named group that includes them, with nothing in the paper giving this person a different or undetermined status. Otherwise "not reported". v5 already held D-27.
- **Gatekeeper v3:** the gatekeeper first records who the quote is about, then judges the person link from that. A normal finding recorded in the inverted form ("normal CRP", excluded) is partially supported, matching Jimmy's final labels and D-27's preferred form.
- **Re-run:** v5 and gatekeeper v3 on 20 run-2 papers drawn at random (seed 29; 14 cohort or review papers, 6 case reports; `analysis/poc/pick_v5_subset.py`, `runs/poc-ha20-v5-subset/selection.json`). Then a fresh 50-claim audit drawn with a new seed, rated by Jimmy with the gatekeeper hidden on the first pass. Estimate $82.61 (planning figure from run-2 readings), within the rough $110 Jimmy approved.
- **Run-2 stays the extraction of record** for Stage 6 concordance, which starts now. The 250-claim audit stays the pre-registered measure.
- **C032922:** Jimmy kept it unsupported (D-30 entry).

### 2026-10-19 · Audit second look done: Q4 not met (3 of 50 unsupported); D-29 opened
- **Jimmy's second look** (10 claims, with the full paragraph and the v1 gatekeeper verdict in view) changed 7 labels. Final: 44 supported, 3 partial, 3 unsupported.
- **Q4:** human unsupported rate 6.0% (exact 95% CI 1.3–16.5%; 5.0% weighted by stratum pool), above the ≤ 4% limit. The automated span match is 100%. Per the Stage 5 gate rule the pilot continues to Stages 6 and 7.
- **Gatekeepers against the final labels:** v1 and v2 each agree on 46 of 50 and flag 2 of the 6 not-fully-supported claims; neither calls any of the 3 unsupported claims unsupported. v1's agreement is not independent, since Jimmy saw its reasons.
- **Opened D-29** (fixes and a re-run). Files: `adjudication/poc_audit/sample.csv`, `ratings_raw.json`, `analysis/poc/audit_metrics*.json`, report §10.5.
- **Unchanged:** the metrics, thresholds and pre-registration text; run-2 and its phenopackets.

### 2026-10-19 · Jimmy's 40 human screening labels applied; the pilot-design branch is archived
- **Handoff.** The pilot-design session (branch `claude/zealous-meitner-k7moex`) reported that Jimmy decided there, on 2026-10-19, to stop pipeline work on that branch and archive it unmerged; this thread owns Stage 3 onward. Its one asset is `data/literature/ha20/spotcheck_human_labels_2026-10-19.csv`: study type for 20 papers and HA20 relevance for 20, confirmed by Jimmy in chat after Claude read each abstract.
- **Applied on Jimmy's instruction ("apply", this session).** `pipeline/extract/corpus/apply_human_labels.py` writes them to `manifest.csv` as human labels, which outrank agent labels.
  - 24 rows changed. Study type agreed with this branch's screening on 17 of 40; the in/out-of-corpus decision on 39 of 40.
  - **30488325 leaves the extraction corpus:** Jimmy labelled it TNFAIP3-other. It had been added at the Stage 1 reconciliation, is paywalled and was never extracted, so no result changes.
- **Statistics refreshed:** 160 papers in the corpus, 85 with full text (53.1%), now counting the reconciliation additions (`data/literature/ha20/search.md`).
- **Unchanged:** run-2, the phenopackets, every result and decision downstream of Stage 1.

### 2026-10-19 · D-26, D-27 and D-28 decided; four HPO ratings recounted
Jimmy chose the recommended option on each question (asked in the session, 2026-10-19), after rating the 50-claim audit sample and 27 of the 30 HPO bindings.
- **D-26 · The normalization check counts descriptions that state a cDNA change.**
  - The Stage 4 check (`POC_DESIGN.md`) is measured over distinct descriptions that state a cDNA change. Protein-only and structural descriptions are reported separately, each with its status.
  - The frozen pipeline fixes the repairable rejections: a transcript VariantValidator does not hold is mapped to one it does, and a typo gets a corrected query recorded beside the original string.
  - Pre-registration §7.2.2 reports normalization success by description type (draft v0.6).
- **D-27 · Normal findings are recorded as the absent abnormality.**
  - For the six-disease run, when a feature is excluded because a finding is normal, the feature is the abnormality ("elevated CRP", excluded), and the quote keeps the paper's words ("CRP was normal").
  - Gatekeeper v2 states this convention, and two rules the Stage 5 flags showed were missing: a per-patient table outranks a group statement, and a hedged phrase supports neither observed nor excluded.
  - No re-run on HA20; run-2 stays the extraction of record.
- **D-28 · The gatekeeper checks every value, including the link to the person.**
  - No value is marked supported by script because it appears in its quote. Every value except bookkeeping fields goes to the gatekeeper. At HA20 scale that is 9,848 more claims on top of 12,155, about 80% more gatekeeper work.
  - The gatekeeper checks that the quote ties the value to this person (or this paper), not only that the words match.
  - Before the six-disease run, gatekeeper v2 is re-checked against Jimmy's 50 ratings.
  - Pre-registration §6.4 says so (draft v0.6).
  - **Why:** in Jimmy's audit the gatekeeper called all 8 of his not-fully-supported claims supported, and 3 of the 8 had been marked supported by script.
- **HPO recount.** Jimmy's "no" on h02, h04, h23 and h25 counts as yes: the term is right, and the objection was to how normal findings are recorded (D-27). HPO model bindings accepted: 23 of 27 rated (3 left unrated).

### 2026-10-19 · Pilot Stages 4 and 5 done, instructions v4 checked (Claude's calls; audit ratings pending)
- **Ran as approved under D-23 to D-25.** Results: `reports/poc_stage4_5_findings.md`. Open questions were D-26 and D-27 (decided the same day, with D-28).
  - **v4 check:** 13 of 13 rule checks as intended on the 10 purposive papers; all 11,706 quotes verbatim. Run-2 stays the extraction of record (no run-3).
  - **Stage 4:** 749 phenopackets, all schema-valid; HPO binding 88.5% of 4,453 feature rows; normalization 128 of 277 distinct descriptions (92.8% of those with a cDNA), below the Stage 4 check as worded (D-26).
  - **Stage 5:** of 22,003 judged values, 21,690 supported, 305 partially supported, 8 unsupported (0.036%, exact 95% CI 0.016–0.072%), 0 quotes not found. The 50-claim human audit and the 30-binding HPO check wait for Jimmy's ratings.
  - **Spend:** session reading $463.50 → $580.31; $116.81 for the v4 check, Stage 4 helpers and Stage 5 together, against ~$195 approved.
- **Claude's calls:**
  - **Disease binding:** labels naming HA20 are bound to MONDO:0800045 (cross-references OMIM:616744, Orphanet:476102), with the gene group term MONDO:0100222 recorded; flagged for review.
  - **Model-assisted HPO binding:** Sonnet helpers looked terms up in the pinned `hp.obo`; an answer is used only if the ID is current and the copied name matches; a broader term is never used for an excluded row.
  - **Gatekeeper classes:** bookkeeping fields are not judged; free text found inside its own verbatim quote is supported by construction; everything else went to helpers.
  - **Phenopackets leave out claims not judged supported** (`POC_DESIGN.md` §3.9). A lenient build that drops only unsupported claims is kept as a summary for sensitivity.
  - **Interruption:** at the five-hour usage limit, 10 gatekeeper helpers stopped; 7 had written complete files (checked by script), 3 were resumed. The session ran on overage from about 02:50 UTC.
- **Unchanged:** metrics, thresholds, the pre-registration, and the extraction instructions of record.

### 2026-10-19 · D-23, D-24 and D-25 decided: merge policy v4, instructions v4 with a 10-paper check, Stage 5 approved
- **Decided by Jimmy (2026-10-19), accepting all recommendations** from Stage 3b (`reports/poc_stage3b_findings.md` §9). He answered four questions in the session's question form. These are revisions, because the pre-registration is not frozen.
- **D-23 · Merge policy v4.**
  - Patients in different papers are merged only on a citation, either row-level or paper-level.
  - "Same variant, same sex, onset within a year" no longer merges; those pairs are listed for audit.
  - Helpers put a per-patient reference column into `source_reference_in_review`.
  - The basis: in run-2 that route made all 6 false merges (37 true, 6 false), and citation merges had none (47 true, 3 cannot tell).
  - Caveat: chosen after seeing the check, so the six-disease study must measure it again.
- **D-24 · Extraction instructions v4, input fixes and a 10-paper check; no run-3.**
  1. **Inheritance:** "inherited maternal/paternal" is allowed when the paper states that the named parent carries the same variant, with that statement quoted. "De novo" still needs stated parental testing (rule 8). This was asked as a separate question; the alternative was to keep the strict reading.
  2. **Zero counts:** a 0 in a count table excludes no one; text naming the group still excludes.
  3. **Labels:** "Table n column k" for patients as columns; "Table n #k" for a patient-numbering column; "<label> (Family n)" for a label repeated across families; "parent of X" or "sibling of X" when the paper gives no sex.
  4. **Literature patients:** in scope only with at least one individual-level fact beyond the diagnosis.
  5. **Variant rows:** none for other-gene variants that are named but not described, or for common variants the authors dismiss. Germline mosaic carriers are in scope (zygosity "mosaic"); tumour-only variants are not.
  6. **Inputs:** supplementary filter v2 (keep every file except administrative forms); entities decoded and bold kept in the converter.
  7. **Runs:** run-2, merged under D-23, stays the extraction of record. v4 is checked on a 10-paper mini-run (about $25) before the six-disease extraction.
- **D-25 · Stage 5 approved, at about $170.** This is the gatekeeper re-read of every run-2 value against its quote, plus Jimmy's 50-claim audit. It runs after Stage 4, which is scripts only.

### 2026-10-19 · Pilot Stage 3b done: run-2, repeat, merge hand check (Claude's calls)
- **Ran as approved under D-22.**
  - **Run-2:** all 85 papers under instructions v3.
  - **Repeat:** 15 papers, seed 20261019, drawn from the 78 run-2 papers with individual rows.
  - **Hand check:** all 93 policy-v3 merges.
  - **Results:** `reports/poc_stage3b_findings.md`. Open questions are D-23 to D-25.
- **Claude's calls during the run:**
  - **Repair, 35958611:** 72 checklist answers had no quote. The same helper added quotes only, and a script confirmed every value unchanged.
  - **Supplementary filter kept as it was, mid-run:** filter v1 skipped one per-patient table that never names the gene (42128528). I kept v1 so all 85 papers read inputs made the same way, and proposed v2 for the next run (D-24).
  - **Entity decoding:** "&gt;" from converted Word files broke variant keys. Decoding was added on the harness side, in the merge keys, the counts and the agreement script; quotes are unchanged.
  - **Sensitivity option:** a sensitivity option was added to `reconcile.py`. After D-23 it became `--policy v4`, the default, with `--policy v3` to reproduce v3.
- **Unchanged:** metrics, thresholds, the pre-registration, the merge policy default, and the extraction prompts and schema.

### 2026-10-19 · D-22 decided: extraction instructions v3, run-2, supplementary files
- **Decided by Jimmy (2026-10-19), accepting all seven recommendations** from Stage 3 (`reports/poc_stage3_findings.md` §8). These are revisions, because the pre-registration is not frozen.
  1. **Cohort scope.** Extract people with a TNFAIP3 variant or an HA20 diagnosis, plus relatives the paper describes in relation to them (tested or affected). For other cohort members, record only their number.
  2. **Labels.** Give people the paper leaves unnamed a fixed label pattern built from the paper's own wording and position.
  3. **"–" cells.** A "–" cell is "excluded" only when the paper's legend or text defines the symbol as absent or negative, and that definition is quoted as a second span. Otherwise it stays "not reported" (rule 6).
  4. **Study criteria.** Study inclusion or exclusion criteria are never phenotype evidence.
  5. **Variant rows without a printed variant.** Keep them, but leave them out of variant counts and concordance. Stage 3 check 3 becomes "every variant row with a printed variant has an original string".
  6. **Run-2.** `poc-ha20-run-2` runs over all 85 papers under instructions v3 and the converter fixes. It gets its own 15-paper repeat and a fresh merge hand check, which also measures merge policy v3 independently. Estimated cost is about $190 at run-1's rate. Run-2 becomes the pilot's extraction of record.
  7. **Supplements.** Fetch supplementary files for open-access papers after a licensing check.
- **Stages 4 and 5** follow run-2. The gatekeeper estimate comes after run-2.
- **How it was implemented (Claude, 2026-10-19; flagged for Jimmy's review):** `extract_v3.md` and `schema_ha20_v3.json`.
  - **Field added:** `publications.cohort_size_as_stated` records the out-of-scope members as a number (item 1).
  - **Labels:** one fixed six-step order (item 2).
  - **Table symbols:** the rule applies to "-", "–", "0", "N" and similar symbols, not only "–" (item 3). So unexplained 1/0 tables, as in 41991504 during run-1, now give "not reported".
  - **Relevance flag:** follows the scope, meaning "describes at least one identifiable in-scope person".
  - **Other genes:** for in-scope people, risk alleles and polygenic-score variants are not listed. This is my reading of item 1 (one Stage 3 scope difference was 19 lupus-risk alleles in 36325013). Say if you want them kept.
  - **Inputs:** run-2 reads the re-converted Markdown with the converter fixes and the supplementary sections. Run-1's Markdown is kept locally, with checksums committed, so run-1 quotes still verify (100%).
- **Why:** Stage 3 found the helpers read values consistently but chose different scopes. The repeat agreed on 98.7% of checklist cells. Variant agreement was 0.547 on strings and 0.702 on folded keys, rising to 0.973 on keys without the two papers where scope differed.

### 2026-10-18 · Pilot Stage 3 done; merge policy v3 (Claude's calls)
- **Stage 3 ran as approved under D-21:** run-1 over all 85 full-text papers, plus a 15-paper repeat (seed 20261018), drawn from the 73 run-1 papers with individual rows. Results and open questions are in `reports/poc_stage3_findings.md`; the instruction changes are proposed as D-22.
- **Claude's calls during the run:**
  - **Converter fix:** the JATS converter now keeps tables placed in `<floats-group>`. 12 papers had lost their tables. Three papers already extracted without tables were re-extracted, and the first outputs are kept.
  - **Repeat draw:** the repeat sample excludes papers with no individual rows, because those would agree trivially.
  - **Merge script** (`pipeline/extract/reconcile.py`): reads reference lists from the JATS XML; matches protein changes printed without "p." and gene names such as "A20/TNFAIP3". Policy changes:
    - v2 merges one-to-one only, never puts two rows from one paper in one identity, and joins first-hand pairs first.
    - v3 accepts an explicit citation only when it names one paper.
  - **Agreement script:** gained label-free and normalized-key measures. The strict `POC_DESIGN.md` measures are reported first.
- **Hand check:** all 58 policy-v2 merges were checked: 52 true, 2 false, 4 cannot tell; one missed merge was found and fixed. Both false merges rested on multi-paper citations, which v3 rejects. v3 was tuned on this check, so its false-merge rate must be measured on run-2.
- **Unchanged:** metrics, thresholds, the pre-registration, extraction prompts and schema.

### 2026-10-18 · D-21 decided: smoke test accepted; group-statement rule; Stage 3 spend approved
- **Decided by:** Jimmy ("approve and merge"), replying to the three gate questions in `reports/poc_stage2_smoke_findings.md`. Recorded as approving all three as recommended; Jimmy to correct if he meant less.
- **Smoke output usable:** the Stage 2 human gate is passed.
- **Group-statement rule:** a feature may be marked absent from a group statement only when the paper names the group explicitly (e.g. "only Pt3 of the four"). Such rows are tagged as inferred. A narrower absence never excludes a broader checklist item (e.g. "no arthritis" does not exclude "arthritis or arthralgia").
- **Stage 3 spend:** one full extraction run plus a 15-paper repeat for stability, estimated at about $381 at most (`runs/poc-ha20-smoke-1/stage3_estimate.json`), within the pilot ceiling. The gatekeeper (Stage 5) is estimated separately after the run.
- **Merge:** the branch is merged into `main`.

### 2026-10-18 · Parallel Stage 1 runs reconciled (Claude's call)
- **What happened:** two sessions ran Stage 1 on the same day without knowing about each other.
  - The pilot session (branch `claude/zealous-meitner-k7moex`) ran 18:00–18:36 UTC: 584 records, 123 in the corpus, 61 with full text.
  - This session ran from 20:22 UTC: 838 records, 153 in the corpus, 76 with full text.
  - This session synced with `main` only and missed the other branch.
- **How they compare:**
  - 583 of the pilot's 584 records are in this session's manifest; the exception is the GeneReviews chapter, which has no usable full text.
  - The corpora share 114 papers. This session has 39 more; the pilot has 9 more.
  - One of the pilot's extra 9 is clearly relevant: 31767699, an HA20 letter with no abstract that this session's screening labelled "other".
  - The pilot fetched 4 full texts this session lacked (31767699, 33619160, 33864888, 42889152), through `efetch db=pmc`.
- **Call:**
  - Stage 3 runs on the union of both corpora's papers that have full text (80).
  - The 9 pilot-only papers are added to this manifest with a note.
  - The pilot's `efetch db=pmc` fallback is ported so the 4 texts are fetched reproducibly here.
  - The pilot branch's committed full-text Markdown files are **not** brought over; full text stays out of git.
- **Still on the pilot branch, not merged:** its manifest and labels, its spot-check sheets (Jimmy was labelling them in that session), its Bookshelf parser, and the committed full-text Markdown, which should be removed before that branch is ever merged.

### 2026-10-18 · Decisions recorded in the pilot session, carried over from its branch
These were recorded on `claude/zealous-meitner-k7moex` between 18:22 and 18:36 UTC and are copied here so they aren't lost. Where a later decision supersedes one, that is noted.
- **Unblocking Stage 1** (Jimmy, chat):
  - The research hosts were allowed. omim.org still refuses automated reads (HTTP 403).
  - `jimmy.lin@raregenomics.org` may be sent as the tool-identification contact to NCBI E-utilities and Unpaywall. It lives in the environment (`NCBI_EMAIL`, `UNPAYWALL_EMAIL`), not in code.
  - Jimmy will read the OMIM terms and register for API access this week. Until then, concordance is ClinVar-only.
  - The 20-row study-type spot-check was deferred, with the Stage 1 gate provisional until it is filled.
- **Model steps on Claude Code credits only; no API key for now** (Jimmy, chat):
  - Classification ran inside Claude Code on Jimmy's credits.
  - The smoke test and all extraction were to wait for an API key. **Superseded by D-20**: extraction now runs with Claude Code agents.
  - The entry also says "the grant's credits are Console API credits". **Corrected by the award email**: the credits are claude.ai usage credits (see `CONTEXT.md` and D-17).
- **Stage 1 gate Q1 not met on first pass; corpus rule tightened** (reported to Jimmy):
  - 61 of 123 papers had full text (49.6%). 11 more are open access on hosts the cloud can't reach; 42 are paywalled.
  - A relevance label was added to the corpus rule; this session's screening uses the same idea.
- **POC proceeds on the open-access corpus; no spend until a key exists** (Jimmy, chat):
  - No library request and no local fetch of unreachable PDFs for now; coverage is revisited when the six-disease run is planned.
  - When a key exists, a scripted classifier re-labels the manifest so the corpus is re-runnable.
  - The spot-checks are done in chat with Jimmy.
  - **"No spend until a key exists" is superseded by D-20 and D-21.**

### 2026-10-18 · D-20 decided: the pilot runs with Claude Code agents, no API key
- **Decided by:** Jimmy ("yes - run the pilot this way now and record it as D-20").
- **Decision:** the HA20 pilot's model work is done by Claude Code helper agents inside a Claude Code session, not through the Anthropic API. That covers study-type screening, per-paper extraction into the pinned schema, the gatekeeper and the memorization probe. Everything without a model stays as scripts: corpus fetch, span check, merging, normalization, phenopackets and concordance. The route is described at the top of `POC_DESIGN.md`.
- **Why:** no API key is needed, and Claude Code is covered by the award's claude.ai credits. That avoids the API billing question (D-17) for the pilot, provided the session runs on the funded account (D-15).
- **What it gives up:**
  - **Not the SLIDERS code.** This is a home-built version of the SLIDERS method, which `POC_DESIGN.md` §6 already allows as a fallback if reported as such.
  - **Looser model pinning.** The model is chosen per helper agent (Opus) and the model actually served is recorded, but settings can't be fixed as tightly as API calls allow.
  - **Coarser cost tracking.** Cost is session-level, not per call, so "$ per paper" is an estimate.
  - **No open-weight comparison in this scaffold.** Claude Code can't host an open-weight model.
- **Kept for later:** the SLIDERS Anthropic adapter (`pipeline/extract/sliders_adapter/`), for when D-17 is settled. Running both routes on the same HA20 papers would show what SLIDERS adds.
- **Isolation:**
  - Helper agents get only their paper, the schema and the extraction rules. Their prompts are saved and hashed.
  - `data/reference/` stays absent while extraction runs, so the guard holds.
  - The ClinVar-cited seed list (D-19) is built outside the repo, and only PMIDs are written into it.
- **Status:** a change of method for the pilot only. Nothing pre-registered changes.

### 2026-10-18 · D-18 decided: pilot first, on A20 haploinsufficiency
- **Decided by:** Jimmy ("can we first do a pilot for 1 specific disease as proof of concept first NOW", then "yes" to recording it).
- **Decision:** run the one-disease proof of concept in `POC_DESIGN.md` now, before freezing the pre-registration and before the six-disease study.
- **Sequence:**
  1. the pilot (`POC_DESIGN.md` Stages 0–7);
  2. the pilot report, with a go/no-go;
  3. update and freeze the pre-registration;
  4. the six-disease run.
- **A20 haploinsufficiency in the full study:** HA20 is re-extracted under the frozen plan but reported separately. Headline (pooled) concordance uses the other five diseases, because the pipeline will have been tuned on HA20, including after seeing its ClinVar disagreements.
- **What this replaces:**
  - the order in the D-01 re-plan, where Month 2 froze the plan first and then ran development. The pilot now comes first and the freeze follows its report;
  - D-06's development set of 20% of the HA20 corpus. The pilot uses the whole HA20 corpus.
- **Commitment check:** `CONTEXT.md` says the design is pre-registered before extraction. A one-disease pilot before the freeze is consistent with that if:
  - it is reported as a pilot;
  - it is listed in the plan's prior-knowledge section;
  - HA20 is kept out of the headline results.
- **Branches combined:** the pilot branch (`claude/zealous-meitner-k7moex`) was merged into `main` with this decision, so the next pilot session starts with both lines of work.
- **Status:** not a pre-registration deviation; the plan is not frozen.

### 2026-10-18 · D-01 decided: Month 1 starts on the date the first deposit landed
- **Decided by:** Jimmy, accepting Claude's recommendation ("go with your recommendation on D-01").
- **Start date:** provisionally **2026-09-21**, the scheduled deposit date. Replace it with the actual landing date from claude.ai Settings > Usage once Jimmy confirms it.
- **Provisional calendar:** months run from the 21st to the 20th, and Month 6 ends 2027-03-20, the day before the first deposit expires. The full calendar is in `CONTEXT.md` §8.
- **Why:** it matches Anthropic's six-month project period and the credit expiry, so our reports line up with theirs.
- **Consequence:** Month 1 ends 2026-10-20 with most Month-1 work undone.
- **Re-plan** (proposed by Claude under this decision; the Months 2–3 split can be adjusted):
  - **Month 2:** finish the Month-1 work first, then the A20 haploinsufficiency development phase and pilot run. Month-1 work means the corpus search and screening, reference snapshots and dated counts, the open-access check, outreach drafts and freezing the pre-registration.
  - **Month 3:** extraction on the other five diseases, with concordance run on each disease as it finishes. The two overlap, instead of extraction taking all of Month 2.
  - **Months 4–6:** unchanged.
- **Still to confirm:**
  - the actual date and amount of the first deposit;
  - the claude.ai Organization ID it went to.
- **Status:** not a pre-registration deviation; the plan is not frozen.

### 2026-10-18 · Parallel work combined on `main`
- **Decided by:** Jimmy ("ok to merge to main").
- **What happened:** two lines of work ran in parallel on 2026-10-18.
  - Branch `claude/gracious-pascal-j7krug` (Claude Code) added the pre-registration draft, this file's open decisions, the award details and `NOTES_FOR_AGENTS.md`.
  - `main` (claude.ai Project chats) added its own `DECISIONS.md` and `BUDGET.md`, the repo-as-source-of-truth decision, the chat digest `docs/claude-ai-threads.md` and `background/origins/`.
- **How they were combined:** `main` was merged into the branch and the branch into `main`. Both sides' entries are kept: `main`'s two decision entries are below, and its budget notes are folded into `BUDGET.md`.
- **Follow-up for Jimmy:** the claude.ai Project mirror needs a refresh with the new files. This session has no access to the Project.

### 2026-10-18 · Pilot Stages 1 and 2 built offline; model runs deferred (from the pilot session; merged in)
- **Decided by:** Claude (pilot session), for Jimmy's information.
- **Status:** Stage 0 is complete. Stages 1 and 2 are implemented and unit-tested, but their network- and model-dependent steps have not run.
  - The cloud environment denies NCBI E-utilities, PMC, Europe PMC, Unpaywall, omim.org and VariantValidator, and holds no `ANTHROPIC_API_KEY`.
  - Either allow those hosts and add the key in the environment settings, or run the runbook in `data/literature/ha20/README.md` and the Stage 2 smoke test on the Mac mini.
  - No spend has occurred.
- **SLIDERS adaptation** (pilot decision 2 follow-through):
  - The public code is pinned at upstream commit `b66094d` (2026-04-14) and patched with an `anthropic` provider built on `langchain-anthropic` over the official SDK.
  - Structured output uses Claude's JSON-schema mode, because current models reject forced tool calls.
  - Sampling parameters are dropped and `effort` is set per role.
  - Server-side refusal fallbacks and automatic prompt caching are on by default.
  - The patch is self-contained, so it can be offered upstream later.
- **Schema** (`POC_DESIGN.md` §3.5 follow-through): the pinned schema is fully specified, so SLIDERS skips its schema-completion model call. The three-state checklist table carries "not reported" explicitly.

### 2026-10-18 · Pilot study design approved with six decisions (from the pilot session; merged in)
- **Decided by:** Jimmy (chat, 2026-10-18).
- **Decision:** `POC_DESIGN.md` is the protocol for the first end-to-end run of the pipeline on one disease. It is a working document, not the pre-registration, and changes nothing pre-registered. Jimmy answered six open decisions and the design was updated to match:
  1. **POC disease: A20 haploinsufficiency (*TNFAIP3*).** Alexander disease is the natural first disease for the full Month-2 run.
  2. **SLIDERS on Claude: fork the public code and add an Anthropic provider** using the official SDK. No contact with the Lam lab for now; offer the adapter upstream later (external contact needs separate approval).
  3. **Reviews and meta-analyses are included in the extraction corpus, flagged `study_type = review`.** The reconciliation agent must merge re-reported patients; rows sourced only from reviews are kept but flagged `review_only`. Completeness against El Hani 2024 is computed on primary-paper rows only, so the benchmark is not scored against itself. If deduplication suffers, exclusion is reconsidered as a logged change.
  4. **OMIM access: Claude drafts the API access request and a summary of the current terms for Jimmy to submit.** Nothing is sent without Jimmy. Until access arrives, the POC concordance runs against ClinVar only.
  5. **POC audit: Jimmy rates the 50 claims himself.** The adjudication panel is held for the 250-claim audit and Month-4 adjudication.
  6. **POC spend ceiling: $1,000, hard stop $1,500.** Drawn from the extraction and gatekeeper lines; stop and ask before exceeding $1,000.
- **How these connect to the rest of this file** (added at merge):
  - decision 4 is reflected under D-12, and decision 5 under D-11;
  - decision 2 is where D-17 bites, because the adapter calls the API;
  - decision 3 differs from the pre-registration draft's *proposed* exclusion of reviews (§5.1). That proposal will follow what the pilot shows.

### 2026-10-18 · Award details recorded (D-01 partly resolved)
- **Source:** award email from Bailey (Anthropic AI for Science program), sent 2026-08-31, saved as `grant/AWARD_EMAIL.md`. The sent date was confirmed by Jimmy.
- **Recorded in `CONTEXT.md`:**
  - award date 2026-08-31;
  - $45,000 awarded (the full request) as claude.ai usage credits;
  - the first half deposited up front (first deposit scheduled 2026-09-21), then top-ups as credits are spent, with each deposit expiring six months after it lands;
  - publications must acknowledge the program.
- **Follow-on changes:** D-01 narrowed to the Month-1 start; D-15 partly answered; D-17 opened (how the pipeline calls Claude).

### 2026-10-18 · D-02 to D-07 decided
- **Decided by:** Jimmy Lin, accepting Claude's recommendations as written in `DECISIONS.md` that day.
- **Applied in:** pre-registration draft v0.2.
- **Status:** the plan is not frozen, so none of these is a deviation.

**D-02 · Pass/fail rule for the 250-claim audit: observed rate < 2%**
- **Decision:** O1 passes with at most 4 unsupported claims out of 250. n = 250 and the 2% target are unchanged.
- **Why:** the stricter rule (one-sided 95% upper bound < 2%) passes a pipeline with a true 1% error rate only 29% of the time (`preregistration/audit_operating_characteristics.py`).
- **Accepted cost:** a pipeline sitting exactly at 2% would pass about 44% of the time.
- **Safeguard:** every report gives the exact 95% interval and never presents a pass as proof that the true rate is below 2%.
- **Plan section:** §7.1.

**D-03 · Concordance success criterion: no numeric threshold**
- **Decision:** concordance is reported as estimates with 95% CIs and no pass/fail cut-off.
- **Why:** the grant made no numeric promise, and ClinVar and OMIM are imperfect references.
- **Plan section:** §7.2.

**D-04 · "Held-out" in the bias arm: comparator cohorts within the six pilot diseases**
- **Decision:** natural-history or genotype-first cohort papers for each pilot disease are held out of the extraction corpus and used as comparators. No extra diseases are added.
- **Why:** this matches the grant's metric wording ("held-out natural-history cohorts") and the $4,000 bias line. The proposal text's "held-out diseases" is the other possible reading.
- **Follow-ups:**
  - Jimmy to get Prof. Lam's confirmation of the reading before the freeze (Claude does not contact anyone).
  - LAD-I and Tangier have no comparator yet; if none is found, they are left out of the bias arm and the report says why.
- **Plan section:** §7.4.1.

**D-05 · Corpus scope: all eligible accessible reports**
- **Decision:** extract every eligible accessible report. Cost is re-estimated after the pilot disease. If a cap is needed, it is applied by seeded stratified sampling, set and logged here before extraction on the remaining diseases.
- **Why:** gap closure needs completeness; the grant's "~300 full texts" was an estimate.
- **Plan section:** §5.1.

**D-06 · Pilot / development disease: A20 haploinsufficiency**
- **Decision:** A20 haploinsufficiency is the pilot and development disease.
- **Why:** the corpus is open-access era (described 2016), and a 65-article systematic review (`elhani2024_ha20_177`) serves as a completeness check.
- **Caveat handled:** cost per paper may not carry over to diseases with long case series, so the scaling estimate uses cost per input token × each corpus's token count, not paper count.
- **Plan section:** §6.5.

**D-07 · Pipeline fixes after the freeze: frozen version is primary**
- **Decision:** results from `pipeline-v1.0` are primary. Later fixes are logged here, re-run, and reported alongside.
- **Why:** fixes chosen by looking at concordance misses would inflate concordance.
- **Note:** this is stricter than the budget's assumption of "re-runs as normalization improves". The re-runs still happen; they just aren't the headline.
- **Plan section:** §6.5.

### 2026-10-18 · Created this log, `BUDGET.md` and pre-registration draft v0.1
- **Decided by:** Claude Code, at Jimmy's request.
- **What:** The pre-registration draft restates the grant's commitments and proposes defaults (marked [proposed]) for everything the grant left open.
- **Unchanged:** nothing in `CONTEXT.md`, the disease set, the metrics or the thresholds.
- **Reproducibility:** `background/audit_ci_250.py` was re-run and reproduces the bounds in `grant_claim_checks.md` §14.
- **New:** `preregistration/audit_operating_characteristics.py` was added to inform D-02.

### 2026-10-18 · Git repo is the single source of truth (from a claude.ai Project chat; merged in from `main`)
- **Decided by:** Jimmy (chat, 2026-10-18).
- **Decision:** `cjimmylin/gp-rarelink` (branch `main`) is canonical for every project document, script and dataset manifest. The claude.ai Project "Anthropic Rare Disease" holds a read-only mirror of the repo's documents so chat sessions can see them.
- **Why:** the instructions require every number to trace to a script, a dated input and a commit; only the repo provides that. The Project previously held duplicate copies (`CONTEXT.md` and `claude/CONTEXT.md`, `claude/INSTRUCTIONS.md`), which would drift.
- **How syncing works:**
  - Edit files in the repo and commit. Then refresh the Project mirror from the repo (any Claude session attached to both can do this). Do not edit documents in the Project directly.
  - Path mapping: files at the repo root are mirrored under `claude/` in the Project (the Project only allows new top-level docs there), e.g. `CONTEXT.md` → `claude/CONTEXT.md`. Files in subfolders keep their repo path, e.g. `grant/GRANT_APPLICATION.md`, `background/manifest.csv`.
  - `INSTRUCTIONS.md` is mirrored to `claude/INSTRUCTIONS.md` and also serves as the Project's custom instructions. Those have to be pasted into Project settings by hand when the file changes.
  - `CLAUDE.md` is specific to Claude Code and is not mirrored.

### 2026-10-18 · Open items blocking Month-1 bookkeeping (from a claude.ai Project chat; merged in from `main`)
- **Raised:**
  - `CONTEXT.md` had blanks for the award date, credits awarded and project start (Month 1).
  - Spend to date had not been reconciled against the Anthropic Console org `2056f88f-1a7b-4386-abfb-5b0fe9a98e10`.
- **Status at merge (2026-10-18):**
  - The award date and credits are now recorded (see "Award details recorded" above). The Month-1 start is D-01.
  - The award turned out to be claude.ai usage credits, not Console credits, so spend is reconciled from claude.ai Settings > Usage instead (D-15). The Console matters only if D-17 adds an API route.

### 2026-10-18 · Repository set up for Claude Code (recorded after the fact from the initial commit)
- **Decided by:** Jimmy, with Claude.
- **Repository:** private.
- **Kept out of git by `.gitignore`:** licensed data (OMIM), full-text articles, reference snapshots, anything patient-like, and secrets. Manifests and download scripts are committed instead.
- **Single source of truth:** `CLAUDE.md` imports `INSTRUCTIONS.md` and `CONTEXT.md`.

### 2026-10-16 · Background literature conventions (Cowork; recorded after the fact)
- **Decided by:** Claude (Cowork).
- **Verification rule:** an identifier is listed only if it was confirmed on a fetched page or a search result; a blank means "not confirmed", never "doesn't exist".
- **Downloads:** papers are downloaded locally by script and not committed, because many are not CC-licensed.
- **No changes:** the grant-claim checks change nothing pre-registered; the items needing a call are carried into D-12, D-13 and D-14 above.

---

## Pre-registration deviations

None. The pre-registration is not frozen yet.

Entry format once frozen:

```
### YYYY-MM-DD · D-nn · Short title
- Registered: what the frozen plan said (section)
- Change:
- Reason:
- Approved by: Jimmy Lin, on YYYY-MM-DD
- Expected effect on results:
- Reported where:
```
