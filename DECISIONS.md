# Decisions

Dated log of project decisions and, once the pre-registration is frozen, every deviation from it (`INSTRUCTIONS.md` §1.4). Newest entries go at the top of each section.

**Pre-registration status:** draft v0.5 (`preregistration/analysis_plan.md`), **not frozen**. Until it is frozen, changes to the draft are revisions, not deviations. Under D-18 the freeze comes after the pilot report. Still blocking the freeze: D-08 to D-12, D-17 and D-19.

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
