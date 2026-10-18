# Decisions

Dated log of project decisions and, once the pre-registration is frozen, every deviation from it (`INSTRUCTIONS.md` §1.4). Newest entries go at the top of each section.

**Pre-registration status:** draft v0.1 (`preregistration/analysis_plan.md`), **not frozen**. Until it is frozen, changes to the draft are revisions, not deviations.

How to use this file:
- **Open decisions** lists what needs Jimmy's call, with options and a recommendation. When one is decided, move it to the decision log with the date and who decided.
- **Decision log** records calls that matter. Claude's own reasonable calls go here too, marked as such (`INSTRUCTIONS.md` §7).
- **Pre-registration deviations** starts empty and is used only after freezing.

---

## Open decisions

### Needed before the pre-registration can be frozen

**D-01 · Project dates and award**
- **Question:** What were the award date and the credits awarded, and when did Month 1 start? These are all blank in `CONTEXT.md`.
- **Why it matters:** the timeline, the budget's remaining balance and the "Month n" labels all depend on them.
- **Recommendation:** fill them in `CONTEXT.md`.

**D-02 · Pass/fail rule for the 250-claim audit (< 2% unsupported)**
- **Options:**
  - **A.** One-sided 95% upper bound < 2%. Passes with at most 1 unsupported claim.
  - **B.** Two-sided 95% upper bound < 2%. Passes only with 0.
  - **C.** Observed rate < 2%. Passes with at most 4.
- **The tradeoff** (from `preregistration/audit_operating_characteristics.py`):
  - With a true error rate of 1%, A passes 29% of the time and C 89%.
  - With a true rate of exactly 2%, A passes 4% of the time and C 44%.
- **Recommendation:** C, with the exact 95% interval always reported beside it. A is the stricter alternative if you prefer certification over power.
- **Constraint:** either way, n = 250 and the 2% target stay as committed.

**D-03 · Concordance success criterion**
- **Question:** The grant sets no numeric concordance threshold. Should the pre-registration add one?
- **Options:** report estimates with CIs only, or pre-specify thresholds per dimension.
- **Recommendation:** estimates with CIs only. ClinVar and OMIM are imperfect references, and the grant made no numeric promise.

**D-04 · What "held-out" means in the bias arm**
- **The ambiguity:** the grant's proposal text says "held-out *diseases* with published natural-history studies"; its metric says "per-disease deviation from held-out natural-history *cohorts*".
- **Options:**
  - Hold out cohort papers within the six pilot diseases. No extra extraction, but LAD-I and Tangier have no comparator yet.
  - Add separate held-out diseases. This draws more on the $4,000 bias line.
- **Recommendation:** within-pilot cohorts, as drafted in §7.4. Confirm with Monica.

**D-05 · Corpus scope**
- **The tension:** the grant estimated ~300 full texts across six diseases. Alexander disease alone likely has more eligible reports than its share, and gap closure needs completeness.
- **Recommendation:** extract all eligible accessible reports. Re-estimate cost after the pilot disease and cap only if needed, by a seeded stratified sample set before extraction.

**D-06 · Pilot / development disease**
- **Recommendation:** A20 haploinsufficiency. It was described in 2016, so the corpus is open-access era, and it has a 65-article systematic review as a completeness check (`elhani2024_ha20_177`).
- **Caveat:** cost per paper may underestimate diseases with long case series.

**D-07 · Pipeline fixes after the freeze**
- **Options:**
  - The frozen pipeline's results are primary; later fixes are reported as a secondary version.
  - The final version is primary.
- **Recommendation:** frozen-primary. Fixes chosen by looking at concordance misses inflate concordance.
- **Note:** this is stricter than the budget's assumption of "re-runs as normalization improves". The re-runs still happen; they just aren't the headline.

**D-08 · Substitute-disease trigger**
- **Question:** What open-access threshold replaces a pilot disease with a substitute?
- **Placeholder for discussion:** fewer than 15 accessible eligible reports, or less than 50% of eligible reports accessible.
- **Constraint:** decided before extraction, on access grounds only.

**D-09 · Registry and timing**
- **Recommendation:** register on OSF, publicly. Freeze before the Month-2 development phase starts.
- **Alternatives:** an embargoed OSF registration, or attaching the plan to a preprint.

**D-10 · Open-weight comparison: model, disease(s), compute**
- **Questions:**
  - Which open-weight model?
  - Run on which disease(s)?
  - How many audited claims per model?
  - Where does it run? The $2,000 line is Claude credits; open-weight compute isn't budgeted.
- **Recommendation:** pick the model by the time of the freeze, on the criteria open weights, long context and tool use. Run it on the pilot disease plus one other.

**D-11 · Panel time**
- **Questions:**
  - Who rates the 250-claim audit (two raters plus a tie-breaker is drafted)?
  - Which optional add-ons can the panel afford: a pre-gatekeeper sample, gatekeeper calibration, a false-abstention check, an open-weight audit sample, discordance triage?
- **Status:** needs the panel's availability. No time estimate is given here because none has been measured.

**D-12 · OMIM access route**
- **The problem:** omim.org blocks automated reading. The archived terms bar redistribution without a license (`grant_claim_checks.md` §13).
- **Options:** request API or download access; read the current terms by hand; or limit OMIM concordance to what can be lawfully obtained.
- **Blocks:** the OMIM half of concordance (O2) and the OMIM gap definition (O3).

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
- **Questions:**
  - How do the budget lines map to the grant's 65% Claude Science / 35% Claude Code split? Only one line, $6,000, is explicitly Claude Code, against ~$16,000 in the split.
  - Do Cowork and Claude Code sessions bill to the grant's Console org or to a claude.ai plan?
  - What counts as a "large share" of a line, requiring Jimmy's approval before a run (25% proposed)?
- **Details:** see `BUDGET.md`.

**D-16 · Release license and verbatim spans**
- **Questions:** Which license applies to released phenopackets and evidence tables? How are verbatim spans from non-open-access papers handled on release?
- **Needed by:** Month 6.

---

## Decision log

### 2026-10-18 · Created this log, `BUDGET.md` and pre-registration draft v0.1
- **Decided by:** Claude Code, at Jimmy's request.
- **What:** The pre-registration draft restates the grant's commitments and proposes defaults (marked [proposed]) for everything the grant left open.
- **Unchanged:** nothing in `CONTEXT.md`, the disease set, the metrics or the thresholds.
- **Reproducibility:** `background/audit_ci_250.py` was re-run and reproduces the bounds in `grant_claim_checks.md` §14.
- **New:** `preregistration/audit_operating_characteristics.py` was added to inform D-02.

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
