# Decisions

Dated log of project decisions and, once the pre-registration is frozen, every deviation from it (`INSTRUCTIONS.md` §1.4). Newest entries go at the top of each section.

**Pre-registration status:** draft v0.3 (`preregistration/analysis_plan.md`), **not frozen**. Until it is frozen, changes to the draft are revisions, not deviations. Still blocking the freeze: D-01, D-08 to D-12, and D-17.

How to use this file:
- **Open decisions** lists what needs Jimmy's call, with options and a recommendation. When one is decided, move it to the decision log with the date and who decided.
- **Decision log** records calls that matter. Claude's own reasonable calls go here too, marked as such (`INSTRUCTIONS.md` §7).
- **Pre-registration deviations** starts empty and is used only after freezing.

---

## Open decisions

### Needed before the pre-registration can be frozen

**D-01 · Project start (Month 1)**
- **Already settled:** award date 2026-08-31 and $45,000 awarded (see the log below).
- **Still open:** when Month 1 starts. The award email gives a "six-month project period" but no start date.
- **Options:**
  - **The date the first deposit landed** (scheduled 2026-09-21).
    - Months then run from the 21st to the 20th, and Month 6 ends around 2027-03-20, when the first deposit expires.
    - Under this choice, today (2026-10-18) is the end of Month 1. Month-1 work (corpus, reference snapshots, freezing the plan) is behind and would run into Month 2.
  - **When project work began** (2026-10-16, the background literature search).
    - The timeline in `CONTEXT.md` §8 then fits as written.
    - But Month 6 runs about four weeks past the first deposit's expiry, so any of the first half still unspent by then lapses.
- **Recommendation:** the date the first deposit landed. It matches Anthropic's six-month window and the credit expiry, so our progress reports line up with theirs. Then re-plan Month 2 to absorb the unfinished Month-1 work.
- **Please also confirm:**
  - the date and amount of the first deposit, as shown in claude.ai Settings > Usage;
  - the claude.ai Organization ID it went to.

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
- **Recommendation:** pick the model by the time of the freeze, on the criteria open weights, long context and tool use. Run it on A20 haploinsufficiency (the pilot disease) plus one other.
- **Depends on D-17:** an identical scaffold needs both models to be called the same way.

**D-11 · Panel time**
- **Questions:**
  - Who rates the 250-claim audit (two raters plus a tie-breaker is drafted)?
  - Which optional add-ons can the panel afford: a pre-gatekeeper sample, gatekeeper calibration, a false-abstention check, an open-weight audit sample, discordance triage?
- **Status:** needs the panel's availability. No time estimate is given here because none has been measured.

**D-12 · OMIM access route**
- **The problem:** omim.org blocks automated reading. The archived terms bar redistribution without a license (`grant_claim_checks.md` §13).
- **Options:** request API or download access; read the current terms by hand; or limit OMIM concordance to what can be lawfully obtained.
- **Blocks:** the OMIM half of concordance (O2) and the OMIM gap definition (O3).

**D-17 · How the pipeline calls Claude** (opened 2026-10-18)
- **The problem:**
  - The grant assumed extraction, gatekeeper, concordance and bias runs would call Claude from code. The application gave a Console org ID for API credits.
  - The award email says the credits sit on a claude.ai account and work across chat, Claude Code, Cowork and Claude Science. It doesn't mention API usage.
- **Why it matters:** most of the core budget (lines 1–3, 5 and 6) is model runs inside the pipeline. The route also affects two parts of the plan:
  - pinning the model ID and settings (§6.1);
  - the identical-scaffold comparison with an open-weight model (§7.5), which is simplest when both models are called from code.
- **Options:**
  - Run the pipeline's model calls through a claude.ai surface the credits cover, such as Claude Code running the pipeline scripts, or Claude Science. This works only if that surface supports the batch runs and logging the plan needs.
  - Use the API with separate funding not covered by the award.
  - Ask Bailey whether the credits can cover API calls from the pipeline.
- **Recommendation:** Jimmy asks Bailey first (Claude does not contact anyone). Meanwhile, the pipeline keeps all model calls behind one small interface, so the access route can change without touching extraction logic.

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
