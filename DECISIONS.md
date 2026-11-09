# Decisions

Dated log of project decisions and, once the pre-registration is frozen, every deviation from it (`INSTRUCTIONS.md` §1.4). Newest entries go at the top of each section.

**Pre-registration status:** **frozen v1.0, 2026-10-20** (`preregistration/analysis_plan.md`; git tags `prereg-v1.0` and `pipeline-v1.0`). Any change from here on is a deviation, logged below with Jimmy's approval. The tags exist on commit `ef3133e`, which is on the branch; this session's git access refused the tag push (HTTP 403), so Jimmy pushes them (`reports/drafts/osf_registration.md` §1). Left: Jimmy registers the same text on OSF (D-09); record the registration's DOI and date here when it exists.

**OSF registration:** DOI ______, registered ______ (to fill in after Jimmy registers).

How to use this file:
- **Open decisions** lists what needs Jimmy's call, with options and a recommendation. When one is decided, move it to the decision log with the date and who decided.
- **Decision log** records calls that matter. Claude's own reasonable calls go here too, marked as such (`INSTRUCTIONS.md` §7).
- **Pre-registration deviations** starts empty and is used only after freezing.

---

## Open decisions

### Needed before the pre-registration can be frozen

*None. Every decision needed before the freeze is settled (2026-10-20).*

### Needed later

**D-43 · Withdraw G-danon-001 and re-check isoform-sensitive normalizations** (decided 2026-10-28; see the decision log and the deviation entry)
- **Finding:** `G-danon-001` (`NM_002294.3:c.1097_1098del`, Sugie 2018, PMID 30413001) is OMIM 309060.0001 / ClinVar 1410728, reported on LAMP2 exon 9b (the paper's table says `E9b`; LAMP2B, NM_013995). The run assumed the MANE transcript (LAMP2A, exon 9a) because the paper named no transcript, so the candidate's genomic allele X:120431457:CTT:C is an artefact, not a gap. One more LAMP2 description past c.1093 carries `transcript_assumed = yes` (`c.1150G>C`, PMID 25228319). GFAP alpha/epsilon has the same structure; its one case (Melchionda 2013) failed normalization safely.
- **Recommendation:** withdraw G-danon-001 from the gap candidates and the adjudication page; re-normalize the two LAMP2 descriptions on NM_013995 and keep them only where the paper's exon label supports it; add per-gene isoform-sensitive regions to the Stage 4 settings (a Stage 4 change, to be logged as a deviation in the D-40 pattern). Details in `reports/omim_holdout_assessment.md` §7.
- **Decided:** Jimmy Lin, 2026-10-28 ("go with your recommendation on D-43"). Carried out the same day; details under *Pre-registration deviations*.

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

### 2026-11-09 · D-45 decided: collaborator dashboard on GitHub Pages; the no-publishing rule lifted for it

- **Jimmy (chat, 2026-11-09):** up to six recruited experts will review the outputs. He asked for an online dashboard on GitHub Pages to share with them, with the overview, the latest interim paper as PDF and HTML, a deck from the latest data, an overview video, and a link to a platform where experts enter their names and emails and give input; for changes that help a newcomer get up to speed; and to be asked about uncertainties. Four questions were put to him; his answers:
  - **Hosting:** GitHub Pages from this repository (a `site/` folder on `main` deployed by `.github/workflows/pages.yml`; Jimmy enables Pages with Source = GitHub Actions). The page is public to anyone with the link, so this lifts the 2026-10-21 no-publishing rule for the dashboard and the documents it carries, and for nothing else (`CLAUDE.md` amended).
  - **Expert input:** a Google Form that Jimmy creates; Claude drafted the questions (`reports/drafts/expert_input_form.md`). The URL goes in `analysis/dashboard/site_config.json`; until then the page shows a placeholder note.
  - **Video:** a captioned slide video built from the deck plus a word-for-word narration script with timecodes, for Jimmy to record a voice-over (no speech synthesis is available here).
  - **Content beyond the overview, the short paper and the deck:** the version 2 full report and supplement (PDF and HTML), the variant-level list of the 214 unadjudicated candidates, and spend figures by budget line. The option "team and panel names" was not selected, so the dashboard names the PI and the two organizations only; the papers it carries keep their bylines.
- **Built (2026-11-09):** `analysis/dashboard/` (export_deck_data.py → deck.js (pptxgenjs) → build_video.py → build_site.py; `make_all.sh` runs the chain), `reports/deck/`, `reports/video/`, `site/`, `COLLABORATING.md`. Every number on the dashboard, deck and video is read from the same result files as the interim papers. No email address appears on the site (checked by script). The SLIDERS ablation (D-44) is not on the dashboard, per the 2026-11-02 decision.
- **Still Jimmy's:** merge to `main`; enable Pages; create the form and send Claude the link; record the voice-over if wanted; share the link with the experts.

### 2026-10-28 · D-44 decided: SLIDERS ablation pilot on HA20 and SSADH deficiency (exploratory)
- **Context:** Jimmy asked for a small two-disease pilot that does *not* use the SLIDERS framework, to measure what SLIDERS added. Design: `reports/sliders_ablation_design.md`; findings: `reports/sliders_ablation_findings.md` (generated).
- **Jimmy, 2026-10-28 (question tool), the recommended option on all four questions:**
  - **Baseline arm: "Direct extraction".** One Opus Claude Code helper per paper, the same model and route as the six-disease run, given the paper and a plain 60-line instruction (`pipeline/extract/claude_code/prompts/direct_v1.md`) asking for the final per-individual records with the same fields and the same 20-item three-state checklist, with no per-value quotes, no evidence-table schema, no rules file, no gatekeeper and no reconciliation step. The SLIDERS arm is the existing `pv1-ha20` and `pv1-ssadh` output, not re-run.
  - **Diseases: HA20 + SSADH deficiency**, the same 125 papers as the D-10 open-weight comparison. HA20 is the development disease (D-18), so it is the case most favorable to the SLIDERS arm; SSADH is untuned.
  - **Support judge: "Locate-and-judge + audit sheets".** A new Claude judge that first finds the supporting passage and then judges, run on an equal seeded sample from both arms with the SLIDERS arm's quotes hidden and the arm blinded, one helper per paper; plus equal-size human audit sheets (CSV, no pages) for the panel later. Reported as a model reading, never as the error rate.
  - **Budget: Contingency, ceiling $300.** Estimate $110–200 (baseline extraction $90–150, judge $20–50). Stop and ask past $300.
- **Status:** exploratory, added after the freeze. No pinned file, metric, threshold or registered analysis changes; this is not a pre-registration deviation. The report labels every figure exploratory. Both arms are scored against one fresh ClinVar snapshot (2026-10-28), so the SLIDERS arm's registered O2 figures (snapshot 2026-10-19) are not replaced.
- **Inputs:** the git-ignored full text was re-fetched on 2026-10-28 (`analysis/sliders_ablation/input_check.json`): 117 of 125 files are byte-identical to the manifests' sha256, 7 XML files are served by Europe PMC in a changed form, and one SSADH paper's open PDF (9093300) could not be re-fetched. Every pv1 quote is found verbatim in the re-created Markdown of the 124 papers with text (0 problems), so arm D read the same text. Supplements re-appended with the same scripts (every kept file's sha256 and the conversion tables identical); ontology releases match their recorded hashes.
- **Outcome (2026-10-28, same session):** arm D ran on all 124 papers with text (85 HA20, 39 SSADH; 9093300 not re-fetchable), every record parsed, conversion filled nothing, structure clean apart from one HA20 paper that reused a pedigree label (35958611). Harness on both arms against the 2026-10-28 snapshot: HGVS recall identical on HA20 (21/78 both); on SSADH arm D 48/160 vs arm S 24/160, the gain concentrated in one scrambled-table paper (14635103) where arm D assigned variants to families by row position. Arm D marked 7.9% of HA20 checklist cells excluded against arm S's 1.4% (SSADH 0.9% vs 0.7%); arm D's values are less often verbatim (ages 75%/60% vs 98%/100%; authors' pathogenicity 39%/67% vs 83%/92%). Judge (arm-blinded, 812 claims): unsupported-or-not-found HA20 S 1/186 vs D 3/188, SSADH S 3/218 vs D 0/220; the arms are not distinguishable at this sample size. Arm D was not cheaper per paper ($1.50 vs $1.08 HA20, $1.36 vs $1.19 SSADH, medians, before arm S's gatekeeper). Report: `reports/sliders_ablation_findings.md`.
- **Cost and the ceiling:** $271.54 by helper tokens (extraction $197.34, judge $74.20), under the $300 ceiling; both parts ran over the design's estimates. To stay under the ceiling the judge covered all 39 SSADH papers and 32 of 77 HA20 papers (2 pilot papers plus 30 drawn with seed 42283; `adjudication/sliders_ablation/judge/paper_subset.json`). **Open for Jimmy:** whether to judge the 45 remaining HA20 papers (about $49 more, taking the pilot to about $320, past the ceiling), and whether the human audit sheets (`adjudication/sliders_ablation/audit/`, 50 claims per arm per disease) join the O1/O5 rating queue. Nothing registered changed; next free number is D-45 (main used D-42 and D-43 for the OMIM holdout on the same day, so this decision is D-44; earlier commits on this branch call it D-42).
- **Jimmy, 2026-10-28 (chat: "yes for both and also merge to main"):** (1) judge the 45 deferred HA20 papers, accepting that the pilot passes the $300 ceiling (about $320 expected; the ceiling for D-44 is therefore raised to cover it); (2) the human audit sheets in `adjudication/sliders_ablation/audit/` join the O1/O5 rating queue for the panel; (3) merge the branch to `main`. Recorded as his decision; still exploratory, nothing registered changes. **Done the same day:** the 45 remaining HA20 papers were judged with the same instruction (45 helpers, $45.58), so the judge covers all 116 papers with output in both arms (1,339 claims, every id once, 0 problems); pilot total $317.13 by helper tokens (extraction $197.34, judge $119.78). HA20 judge result on all 77 papers: unsupported-or-not-found S 3/451 vs D 4/450, partially supported S 19 vs D 34; SSADH unchanged. Report regenerated.

### 2026-10-28 · D-43 decided: G-danon-001 withdrawn; isoform-sensitive positions added to Stage 4 normalization

- **Jimmy:** "go with your recommendation on D-43".
- **Done:** (1) `G-danon-001` is marked `withdrawn` in `adjudication/o3_gaps/candidates.csv` (new columns `status`, `status_note`; no row removed, because dossiers, batches, flags and the adjudication page key on the candidate id); the same pass copies the OMIM verdict of 2026-10-28 into every row's `omim_checked` (214 absent from OMIM's allelic variants, 1 withdrawn). Script: `adjudication/o3_gaps/apply_omim_check.py`. (2) Stage 4 normalization gained an isoform rule (deviation entry below). (3) The Danon run was re-normalized under the new rule and its phenopackets rebuilt with the pinned ontology releases (checksums match the 2026-10-19 manifest), after waiting out a VariantValidator outage; exactly two descriptions and five records changed, as the deviation entry's outcome bullet records.
- **Not done, on purpose:** the adjudication page is not changed (no publishing, Jimmy 2026-10-21); it still lists G-danon-001, so whoever adjudicates needs the candidates file or a refreshed page once publishing resumes. O2 and O3 are not re-run on a fresh ClinVar snapshot: on the right transcript the withdrawn variant is ClinVar 1410728 (uncertain significance), so it is not a gap either way, and the other candidates' standing rests on the registered 2026-10-12 release.
- **Not changed:** the four pinned extraction files, metrics, thresholds, O2's ClinVar figures, the other five runs.
### 2026-10-28 · D-42 decided: OMIM reference from entry pages frozen by Jimmy; OMIM used as a human-curated holdout

- **Jimmy's action and instruction:** uploaded twelve omim.org entry pages printed to PDF on 2026-10-28 ("These are frozen screenshots from OMIM as of today"): the six phenotype entries (616744, 203450, 116920, 271980, 300257, 205400) and the six gene entries (191163, 137780, 600065, 610045, 309060, 600046). Then: "can you use the omim information as a gold standard human curated hold out source to assess the outputs of our analysis in a comprehensive manner - analyzing where our work is successful, where it can be improved, and providing an extensive analysis".
- **Decided (D-42):** these pages are the project's OMIM reference, dated 2026-10-28, obtained through Jimmy's own omim.org access (a licensed route in the sense of pre-registration §6; it replaces the API route D-12 planned, which stays useful for the clinical synopses and for refreshes). Storage follows §11 and `.gitignore`: the PDFs, their text and every parsed file with OMIM prose live under the reference root outside the repository (`/home/user/gp-rarelink-reference/2026-10-28/omim/`, gone with the container; Jimmy holds the PDFs). The repo holds the manifest and counts (`analysis/poc/reference_snapshot/2026-10-28/omim_MANIFEST.json`, `omim_counts.json`) and tables that carry identifiers only.
- **Used for:** the pre-registered OMIM items that waited on D-12: §7.2.5 corpus overlap, §7.2.2 reference pairs in the OMIM form, and the §7.3 OMIM criterion on the 215 gap candidates; plus an exploratory assessment (literature funnel, allelic-variant recall, patient-level comparison, ClinVar standing of OMIM's variants, staleness). Report: `reports/omim_holdout_assessment.md` (regenerate with `analysis/omim_holdout/report.py`); code in `pipeline/harness/omim_entries.py` and `analysis/omim_holdout/`.
- **Results in brief:** 43 of 75 disease-titled OMIM allelic variants recovered at the genomic or protein level (57.3%; 46.1–67.9), from 85.7% (LAD-I) to 10.5% (Tangier). The binding constraint is literature coverage: of the 84 papers OMIM cites as sources for those variants, 5 were extracted, 38 are in the corpus without an open copy (D-32) and 38 were never returned by the searches (mostly pre-gene-era disease names). Where the source paper was extracted, 8 of 14 variants were recovered from it; the misses are a table scrambled in conversion (Akaboshi 2003) and variants the paper states only in prose. Patient-level comparison on the 9 shared papers: 12 agree, 7 partial, 4 missed (all the Akaboshi table), no contradiction. No gap candidate is a confirmed OMIM variant; G-danon-001 is a transcript-isoform artefact (D-43). OMIM itself has two allelic variants whose own ClinVar records do not match their description (610045.0002, 610045.0007).
- **Not changed:** the frozen pipeline, prompts, metrics and thresholds; O2's ClinVar figures; the adjudication page; `CONTEXT.md` §4 only gains the dated OMIM allelic-variant counts in place of the proxies. The `omim_checked` column of `adjudication/o3_gaps/candidates.csv` still reads `no (D-12)`; the OMIM verdicts are in `analysis/omim_holdout/gap_candidates_omim_check_2026-10-28.csv`.
- **Cost:** no model calls; session tokens only (helpers not used).

### 2026-10-21 · D-13 and D-14 decided; D-10 audit waits on D-11; more open-weight work approved
- **Jimmy, 2026-10-21 (question tool):**
  - **D-13: "Curation (Recommended)".** Our ClinVar submissions use the *curation* collection method, not *literature only*, because the records are panel-adjudicated and carry a classification. This is a change from the grant's wording ("literature-only submissions"), logged here.
  - **D-14: "Apply all (Recommended)".** `CONTEXT.md` now gives Tangier ~100–150 patients, Danon about 100 families and ≥146 confirmed patients, phenopacket-store as 731 gene folders at commit `85ffd78` (2026-10-07), and reads LAD-I's "184" as patients without a reported genotype. LAD-I's ORPHA number stays marked to check (Mondo: Orphanet:99842). Sources: `background/grant_claim_checks.md` §1–5. Disease set unchanged.
  - **D-10 blinded audit: "Wait for D-11 (Recommended)".** Size it with the panel's hours; same raters as O1. Nothing drawn yet.
  - **More model work: "Gatekeeper on open-weight runs" and "Open-weight memorization probe".** Gatekeeper v4 (Claude helpers) over `ow-ha20` and `ow-ssadh`, offered at about $60–90 on the gatekeeper line, so both models' unsupported rates come from the same judge (supplementary to the registered blinded audit). The WS5 probe files run on DeepSeek-V4.1-Flash, about $1–3 on the OpenRouter key.
- **Gatekeeper cost re-estimated, then approved (Jimmy, 2026-10-21: "All papers, ~$135").** Claude's own gatekeeper pass on pv1 cost $0.0044 per judged claim (helper tokens). The open-weight runs have 28,456 claims to judge in 163 chunks (HA20 18,084 in 107; SSADH 10,372 in 56), so about $125–140, above the $60–90 first offered. Gatekeeper line; stop and ask past $160. Same launch prompt, instructions (`gatekeeper_v4.md`, frozen) and one helper per chunk as pv1. Cost reading at launch: $1,739.21 (2026-10-21 21:23 UTC).
- **Outcome (2026-10-21, 21:55 UTC):** all 163 chunks judged, every claim has one verdict (`gatekeeper_merge.py --prefix gatekeeper_v4`). Cost $136.46 on helper tokens, under the $160 stop. Unsupported: open-weight 8.64% (HA20) and 6.14% (SSADH) of model claims, against Claude's 0.20% and 0.38%; claims with a quote only: 2.28% and 2.03% against 0.20% and 0.38%. Most open-weight unsupported claims had no quote. Helpers did not all treat an empty quote the same way, and a Claude judge may not be neutral; both are stated in the report (§6). The open-weight memorization probe ran too ($0.048): no recall of variants, fewer guesses than Claude (§7). Spend on the D-10 extraction corrected to $16.34–$20.35 (`BUDGET.md`).
- **The OpenRouter key is shared** with the other projects in this cloud environment (Multi-Alignment and Multi-Bench sessions ran on 2026-10-21; one mentions kimi-k2.6). Key usage rose from $21.42 at 19:21 UTC to $31.31 at 21:23 UTC with nothing running here. So the key delta in `BUDGET.md` for the D-10 run may include other projects' spend; the run's own cost is re-derived from its token counts.
- **Previous text of the two open items, kept for the record:**

> **D-13 · ClinVar collection method for our submissions**
> - **The problem:** "Literature only" means no added submitter curation and recommends no classification (`clinvar_submission_docs`). Our panel-adjudicated, classified records may fit "curation" better (`grant_claim_checks.md` §12).
> - **Needed by:** before Month-4 adjudication, because it shapes what the panel records.
> - **Note:** the grant says "literature-only submissions", so switching to "curation" is a change to log here.
>
> **D-14 · Correct figures in `CONTEXT.md`**
> - **Proposed edits:**
>   - **Tangier:** change "~200 published patients" to ~100–150 (`koseki2021_tangier_review`).
>   - **Danon:** change ">100 families" to "about 100 families; ≥146 molecularly confirmed patients".
>   - **phenopacket-store:** replace "408 cohorts", which has no published source, with a dated count.
>   - **LAD-I** (new, found 2026-10-18): the impact statement says "genotypes for 184 LAD-I patients whose variants were published but never structured". 184 = 323 − 139, and the source review reports that genotype was *not* reported for those patients. If so, extraction cannot recover them. This affects how LAD-I gap closure is described. Check against `almarzanovoa2018_lad1_review`.
>   - **LAD-I ORPHA number** (new, found 2026-10-19): Mondo release 2026-10-06 cross-references LAD-I (MONDO:0007293) to Orphanet:99842, not to ORPHA 2968 as `CONTEXT.md` and the application give. Check against Orphanet; records will use Mondo's cross-reference (pre-registration §4.1, §6.2).
> - **Scope:** the disease set is unchanged; these are wording and number fixes.

### 2026-10-21 · D-10 hosting: OpenRouter (Jimmy's suggestion; run approved)
- **Jimmy, 2026-10-21:** "I have an openrouter saved already on this account - can you use that?"
- **What fits D-10:** OpenRouter's model id `deepseek/deepseek-v4.1-flash` is the 2026-09-10 checkpoint the plan pins (OpenRouter model list, read 2026-10-21; a later snapshot, `-1017`, exists and is not used). It supports tool calls. OpenRouter is a hosted API whose name, model id and serving date the agent records, as §7.5 requires.
- **Claude's call, for fairness:** many upstream providers serve the model at different precisions (fp4, fp8, unstated). The run pins one fp8 provider with fallbacks off (`OPENWEIGHT_PROVIDER`), and logs which provider served each call. Proposed default: `deepinfra/fp8`.
- **Key (resolved, 2026-10-21):** Jimmy: "there is already a "openrouter.ai" secret in the env document already - can you look". The key is a network secret that the environment's egress proxy adds to requests for openrouter.ai, so the session never sees it and the agent sends no Authorization header. Key limit $50.
- **One-paper pilot (2026-10-21):** PMID 37324276 on HA20, run `ow-ha20-pilot`: 16 calls, all served by DeepInfra, 29 minutes, $0.069. Same 4 variants as pv1; checklist agreement 0.95 on 80 shared cells; 99.4% of quotes found verbatim (`analysis/openweight/compare_ow-ha20-pilot.json`).
- **Run approved by Jimmy, 2026-10-21** ("Run both now (Recommended)"): HA20 (85 papers, `ow-ha20`) then SSADH (40, `ow-ssadh`), 10 papers at a time, through `pipeline/extract/openweight/batch.py`. Stop and ask past $40 of key spend across both, counted from key usage $1.0689 at launch, or if anything breaks.
- **Harness fixes during the run (Claude's call, 2026-10-21; approved by Jimmy, 2026-10-21: "ok, the three harness fixes are approved").** The three are retries, the JSON check (tools v2) and resuming cut-off replies (tools v3).
  - Retries: the client resends a call (up to 3 times, waits 30/60/120 s) after a dropped connection or a 408/429/5xx error, including DeepInfra's in-stream "502 Network connection lost". Ten HA20 papers launched before this failed and are re-run in full.
  - JSON check (tools v2): the frozen instructions say "Validate that your file parses as JSON". The Claude helpers did this with a shell command; the open-weight loop has no shell, and one HA20 paper (38183052) ended with a trailing comma. From now on, a write or edit of a `.json` file tells the model whether the file parses. Transcripts record `tools_version`. Papers whose output does not parse are re-run with v2; HA20 papers that finished under v1 with valid JSON are kept. SSADH runs on v2 throughout. The write-up states this.
  - Cut-off replies (tools v3): four papers (HA20 33101300, 40574834, 41741169; SSADH 9093300) ended with no output file because the model's last reply hit the 65,536-token output limit per call and was cut off before any tool call; the loop took the cut-off text as the final reply. Claude Code asks its helpers to resume when that happens, so the loop now does the same (up to 3 times; the request is logged and counted in `continuations`). The four papers are re-run clean with v3; their failed attempts are archived.
  - Re-runs start clean: before a failed paper is re-run, its scratch files and any partial or invalid output are moved to `runs/ow-ha20/failed_attempts/` (with the failed log and transcript), so the new attempt cannot see the earlier one's work. Two re-runs launched before this check were stopped after a few turns and restarted clean.
  - SSADH was started at 10:05 UTC while the last two HA20 papers were still running, keeping 10 papers in flight in total.
  - Prompt, instruction files, schema, model and provider are unchanged.
- **Result (2026-10-21):** both runs finished; every one of the 125 papers has an output that parses. Key spend $20.35 for both runs, failed attempts included (`BUDGET.md`). Findings: `reports/openweight_comparison_findings.md` (generated by `analysis/openweight/report.py`). Still open for §7.5: the blinded audit of equal-size samples per model, sized with D-11.
- **Cost estimate:** about $7–15 for HA20 + SSADH (125 papers) at that provider's list price. That is inside the ~$50 contingency approved under D-10. A one-paper pilot comes first.

### 2026-10-21 · D-41 decided: model work while human rating waits
- **Context:** Jimmy deferred the human rating (O1 raters, O2 triage, merge hand check, checklist-map review) and asked what model work can go ahead. Plan: `reports/plan_next_work_2026-10-21.md`. He said "go" for all of it and answered three approvals up front.
- **Approved by Jimmy, 2026-10-21:**
  - **WS3 gap-variant evidence dossiers:** charged to the "ClinVar/OMIM reconciliation + concordance harness" line ($6,000). Estimate $40–80; stop and ask past $100.
  - **WS5 memorization probe, Claude side:** charged to the "Ascertainment-bias arm" line ($4,000). Pilot on one disease first, then the other five; stop and ask past $60.
  - **WS7:** add the GPSEA package as an optional uv dependency group for the exploratory genotype–phenotype maps.
- **Also going ahead (no spend, per the plan):** WS1 completeness, WS2 gap candidates, WS4 adjudication page (built, not shared), WS6 bias-arm prep, WS8 open-weight harness on a stub, WS9 drafts.
- **Not changed:** the frozen plan, prompts, metrics and thresholds. Dossiers propose no classification, and helpers never see ClinVar or OMIM content (§5.3). Cost reading at the start: $1,628.03 (2026-10-21 00:50 UTC).

### 2026-10-20 · D-37 decided: six-disease run approved up to $1,200
- **Estimate** (`analysis/cost/six_disease_estimate_2026-10-20.md`, method of pre-registration §6.5):
  - 350 papers, about 3.35M input tokens;
  - one clean pass about $795 (extraction about 70%, gatekeeper 30%);
  - with repairs (1.25×) about $994; upper-bound rate $876–$1,095;
  - one full re-run (2×) about $1,590.
- **Decision (Jimmy, 2026-10-20):** "Up to $1,200". This covers the run with repairs at the upper-bound rate, plus the 10% run-to-run repeat (plan §7.6, about $80). Claude stops and asks before any full re-run, or if the readings pass $1,200.
- **Order:**
  1. Prep steps, at little or no model cost: supplements for the five new corpora; the per-disease checklists, written from each disease's GeneReviews or key review (§6.5); the scripted catalogue check (§7.2.7).
  2. The run itself, disease by disease, with concordance on each as it finishes.
- **Billing lines:** extraction (line 1) and gatekeeper (line 2). Session readings are logged per disease in `BUDGET.md`.

### 2026-10-20 · D-36 decided: freeze extraction v6 as tested; pre-registration frozen v1.0
- **The smoke run** (D-35; `reports/poc_smoke_v6_findings.md`, `runs/poc-ha20-v6-smoke/manifest.json`):
  - extraction v6 and gatekeeper v4 ran on the 20 D-29 papers;
  - the span check found 0 problems in 13,382 values;
  - gatekeeper v4 judged 4,538 claims: 23 unsupported, 75 partial;
  - session readings +$53.50 against an estimate of about $80.
- **The gap it found:** extraction v6 has no rule for hedged phrases, while the gatekeeper has one (since v2). A status that rests only on "suggested" or "possible" is extracted as observed, then judged unsupported (5 of the 23), and so ends as "not reported".
- **Options put to Jimmy:** freeze v6 as tested, or write extraction v7 with the hedge rule and repeat the smoke run (about $55) first.
- **Decision (Jimmy, 2026-10-20):** "Freeze v6 as tested". The gap is listed in the pre-registration as a known behavior (§6.5).
- **Done the same day:**
  - pre-registration v1.0 records the model, sampling settings, training cutoff (June 2026, from Anthropic's models overview, read 2026-10-20) and dates of use (§6.1), plus the smoke run (§6.5) and the freeze record (§13);
  - the commit carrying them is tagged `prereg-v1.0` and `pipeline-v1.0`.
- **Left:** Jimmy's OSF registration (D-09). Registering the tagged text unchanged keeps the two identical.
- **No change** to metrics, thresholds, diseases or the four pinned files.

### 2026-10-20 · D-11 settled without panel hours; D-35 decided: all remaining [proposed] defaults accepted
- **D-11 · Panel time.**
  - Jimmy: "I can send the D-11 without the hours." The panel note no longer asks for hours (`reports/drafts/panel_availability.md`, revised; still Jimmy's to send). The panel's availability is no longer a freeze condition.
  - The rater design stands: two raters and a tie-breaker.
  - Gatekeeper accuracy (§7.1 (b)) comes from the main audit's own ratings.
  - The pre-gatekeeper sample (a), the false-abstention check (c), the open-weight audit sample and discordance triage are done only if panel members offer time. Discordance triage falls back to Jimmy. Anything not done is reported as not done.
- **D-35 · [proposed] defaults.** Jimmy: "settle proposals with defaults." Every item the plan marked [proposed] is accepted as written, now marked (D-35, decided). This includes:
  - the search, eligibility and screening rules;
  - the VariantValidator field filter and the isolation enforcement;
  - the general statistics (Wilson and exact intervals, cluster bootstrap);
  - stratified audit sampling and the rating labels;
  - variant matching tiers and the 2-individual phenotype threshold;
  - the per-disease completeness catalogues, checked by script before extraction;
  - leaving out of the bias arm any disease without a comparator, and the frequency-deviation and memorization-probe designs;
  - 50 hand-checked merges (or all if fewer);
  - no Europe PMC full-text search or LitVar;
  - the smoke run of extraction v6 and gatekeeper v4 on the 20-paper HA20 subset before tagging `pipeline-v1.0`.
- **The discordance triage sample** is set at 50 misses, or all if fewer.
- **Pre-registration draft v0.12.** No [D-nn] item blocks the freeze. Left:
  - the smoke run, about $80 at the D-29 rates (not yet run);
  - the `pipeline-v1.0` and `prereg-v1.0` tags;
  - Jimmy's OSF registration.

### 2026-10-20 · D-34 decided: the screening calls stand after a 20-item human check
- **Jimmy's words:** "I screened 20 - and mostly agree - so let's just do with your calls." Recorded as his decision; this is the first use of D-34.
- **What he rated** (`adjudication/screening_check/ratings.csv`, `ratings_summary.json`, collected from the page's store with `apply_ratings.py`):
  - Part A: 15 abstract-stage inclusions, all Alexander disease. He would include 14 and was unsure of 1 (PMID 9044406), with no exclusions. Agreement 14 of 15 (exact 95% CI 68–100%).
  - Part B: 5 full-text exclusions, all LAD-I. He agreed with all 5 (48–100%).
- **What changes:**
  - The drafted check (a 10% sample of inclusions and every full-text exclusion; 137 and 71 items) stops at these 20 items.
  - The title/abstract and full-text screening labels stand as the corpus decisions.
  - The plan is not frozen, so this is a revision (pre-registration v0.11, §5.1), not a deviation.
- **Limitations stated in every report:**
  - the check covered two diseases and 20 items, by one rater;
  - its intervals are wide;
  - the full-text exclusions of non-English papers and of papers whose per-patient data sit in supplements were not individually reviewed.
- **Freeze:** with this, only the panel's hours (D-11) remain before the freeze.

### 2026-10-20 · Five-disease work merged to `main`
- Jimmy: "merge all to main" (this session). Merged as PR #5 (cjimmylin/gp-rarelink#5), merge commit `15bff47`.
- Checked before merging: 52 tests pass. No full text, PDFs, Markdown conversions, reference snapshots or `.env` are tracked.
- The pre-registration stays unfrozen. It waits on the panel's hours (D-11) and Jimmy's screening check (settled the same day by D-34).

### 2026-10-20 · D-10 decided: DeepSeek-V4.1-Flash on HA20 and SSADH deficiency, agent harness, about $50 from contingency
Jimmy chose the recommended option on all four questions (asked in the session, 2026-10-20; shortlist in `reports/drafts/d10_open_weight_shortlist.md`):
- **Model:** DeepSeek-V4.1-Flash (MIT, 1M context), pinned to the 2026-09-10 checkpoint, on a hosted API.
- **Diseases:** A20 haploinsufficiency plus SSADH deficiency.
- **Budget:** about $50 of open-weight compute from contingency, logged in `BUDGET.md` with the host's invoice. Opening an account with a host is Jimmy's step.
- **Scaffold:** an open-source agent harness given the same instruction files, inputs and file tools as the Claude Code helpers; differences stated in the write-up.
- Pre-registration draft v0.10 (§7.5, §13). The audit size per model is still open, with D-11.

### 2026-10-20 · Full-text screening done for the five new diseases; D-08 met by all five (Claude's run, Jimmy's instruction)
- **What ran:** Jimmy asked for the full-text screening ("do this: Still to do"). Sonnet helpers applied `screen_fulltext_v1.md` (pre-registration §5.1 with D-33) to all 336 open full texts. That is 293 JATS XML papers plus 43 open PDFs, which Docling converted.
- **Quotes:** every decision carries an evidence quote, and all of them were found verbatim in the paper by the import script.
- **Results** (`analysis/corpus/coverage_2026-10-20.md`):

| Disease | Eligible papers with full text | Of which case reports or series |
|---|---|---|
| Alexander disease | 69 | 68 |
| LAD-I | 42 | 38 |
| SSADH deficiency | 40 | 36 |
| Danon disease | 83 | 82 |
| Tangier disease | 31 | 28 |

  Every disease meets D-08 (at least 15 eligible primary reports). No substitution is needed.
- **Exclusions to check:**
  - 71 papers were excluded at full text. Jimmy rates all of them in Part B of the screening-check page.
  - 10 of the 71 were excluded as not in English. Most are Japanese case reports with a GFAP, ITGB2, LAMP2 or ABCA1 variant, which pre-registration §5.1 excludes ("no English full text").
  - Several "aggregate only" exclusions say the per-patient data sit in supplementary tables we did not fetch.
  - Both points are flagged for Jimmy; neither changes the registered rule.
- **Human check:** the screening-check page is https://claude.ai/artifact/1JoRKB2uVCap3XAJUDw3RN. Part A has 137 abstracts, Part B the 71 full-text exclusions.

### 2026-10-20 · Pilot report approved; D-09, D-11, D-12, D-17 and D-33 decided; screening-check design accepted
Jimmy's answers to eight questions (asked in the session, 2026-10-20). Each took the recommended option.
- **Pilot report** (`reports/poc_report.md`): approved as drafted. The Stage 7 gate is passed, and its §10 changes go into the frozen pipeline (pre-registration v0.7 to v0.9).
- **D-17 · How the pipeline calls Claude:** Claude Code helper agents on the funded claude.ai account, as in the pilot (D-20). Each run records the model ID, the instructions' sha256 and the session usage readings. The Bailey draft still goes out, to confirm how overage is billed.
- **D-09 · Registry:** OSF, public, registered at the freeze, before the six-disease run.
- **D-12 · OMIM:** Jimmy submits the drafted API access request (`reports/drafts/omim_access_request.md`). Until access arrives, concordance and the gap definition run on ClinVar, and OMIM is reported as "not yet assessed".
- **D-11 · Audit raters:** two panel members rate and the third breaks ties, as drafted. Hours wait on the panel's availability, so D-11 stays open for those.
- **D-10 · Open-weight comparison:** Claude drafts a shortlist first. D-10 stays open until Jimmy picks a model.
- **D-33 · Literature-summary reviews (new):** reviews whose only patient data are per-patient tables of earlier cases are included in extraction, as in the HA20 pilot. Their people are tagged secondary-source and deduplicated against primary reports, and results are reported with and without them. This changes pre-registration §5.1 eligibility (draft v0.9) and the full-text screening instructions (`screen_fulltext_v1.md`).
- **Screening check:** as drafted in pre-registration §5.1. Jimmy rates a random 10% of title/abstract inclusions per disease, plus every full-text exclusion, on one rating page.

### 2026-10-20 · D-08, D-19 and D-32 decided: absolute substitute trigger, no ClinVar seeds, open access only
Jimmy's answers to four questions (asked in the session, 2026-10-20):
- **D-08 · Substitute-disease trigger: absolute count** (recommended option).
  - A pilot disease is replaced only if, after full-text screening, it has fewer than 15 accessible eligible primary reports (case reports, case series or cohorts).
  - There is no share rule. Coverage per disease is reported as a limitation, with accessible and inaccessible papers compared by publication decade.
  - Evidence as of 2026-10-19 (`analysis/corpus/coverage_2026-10-19.md`): all five new diseases meet the count on fetched full text. Tangier disease only just does, with 17 relevant primary papers.
- **D-19 · ClinVar-cited papers as corpus seeds: not used** (recommended option).
  - Pre-registration §5.1 stands as written for the six-disease study. Every concordance figure is still reported with and without ClinVar-cited papers.
  - The pilot's ClinVar-seeded HA20 corpus stays as run. When HA20 is re-extracted for the six-disease study, the papers that came only from ClinVar citations are reported separately.
- **D-32 · Full-text access: open access only** (new).
  - The study uses openly available full text only: PMC and Europe PMC, plus open copies found through Unpaywall. No institutional or library access.
  - Paywalled papers stay in the manifests as not accessible and are listed in reports.
  - The "institutional access" route in pre-registration §5.1 is removed (draft v0.8).
- **Unpaywall contact address:** Jimmy gave `jimmy.lin@raregenomics.org`. It is stored only in the git-ignored `.env` as `UNPAYWALL_EMAIL` and sent only to api.unpaywall.org.
- **Unpaywall pass (2026-10-20).** It fetched 43 open PDFs across the five diseases (`analysis/corpus/coverage_2026-10-20.md`, `unpaywall_hosts_2026-10-20.json`). Most open copies it found could not be fetched:
  - publisher sites answered with HTTP errors to automated downloads (Wiley, ScienceDirect, Neurology, AHA, OUP and others). This was not worked around;
  - a few hosts are refused by the environment's network policy, mainly www.jci.org (14 links). Jimmy could allow them;
  - PMC's own PDF pages are behind a reCAPTCHA.
  - Under D-08, all five diseases now meet the count provisionally: 24 (Tangier) to 81 (Danon) relevance-"yes" primary papers with full text. Full-text screening decides.
  - The PDFs need conversion before extraction (`to_markdown.py` uses Docling, not yet installed).

### 2026-10-19 · Five-disease corpus searched and screened; dated ClinVar counts; pre-registration v0.7
Jimmy: "Yes. Perform items 1-5" (this session), after Claude listed them. Items 1–4 are done here; the item 5 drafts are in `reports/drafts/`, for Jimmy to send.
- **Searches and screening (Alexander disease, LAD-I, SSADH deficiency, Danon disease, Tangier disease).** Settings: `configs/diseases.yaml`. Per-disease logs: `data/literature/<disease>/search.md`.
  - Claude's calls:
    - no ClinVar or OMIM citation seeds, following pre-registration §5.1 (D-19 stays open; the recommendation is unchanged);
    - searches run from database inception;
    - the Europe PMC full-text search and LitVar were not run;
    - comparator holdouts were marked out of the corpus (pre-registration §7.4.1).
  - Screening was done by Sonnet helper agents with `screen_v2.md` (the disease-neutral form of `screen_v1.md`), each with its own scratch directory.
  - Human check of a 10% sample: not yet done.
- **Full text.** Fetched from Europe PMC and PMC only. Unpaywall was skipped: it needs an email address, and Claude does not send Jimmy's address to a third party without his say. `pipeline/extract/corpus/oa_elsewhere.py` lists, without downloading, which remaining papers Europe PMC shows as free elsewhere. Coverage, from `analysis/corpus/coverage_2026-10-19.md`:

| Disease | Search hits | Records | In corpus | Full text | + free elsewhere (upper bound) | Yes-relevance primary papers with full text | D-08 placeholder on full text |
|---|---|---|---|---|---|---|---|
| ha20 | 716 | 838 | 160 | 85 (53.1%) | 96 (60.0%) | 55 of 95 (57.9%) | met |
| axd | 513 | 539 | 363 | 74 (20.4%) | 135 (37.2%) | 66 of 283 (23.3%) | not met |
| lad1 | 869 | 874 | 274 | 51 (18.6%) | 98 (35.8%) | 30 of 180 (16.7%) | not met |
| ssadh | 254 | 357 | 171 | 52 (30.4%) | 78 (45.6%) | 38 of 135 (28.1%) | not met |
| danon | 408 | 416 | 244 | 86 (35.2%) | 110 (45.1%) | 74 of 203 (36.5%) | not met |
| tangier | 519 | 529 | 284 | 30 (10.6%) | 98 (34.5%) | 17 of 186 (9.1%) | not met |

  "In corpus" counts title and abstract screening only, so full-text screening will lower every denominator. "Free elsewhere" is an upper bound; those papers were not fetched.

- **ClinVar counts.** `CONTEXT.md` §4 now gives direct counts for all six genes from one release (2026-10-12, read 2026-10-19), with the application's figures beside them (`analysis/poc/reference_snapshot/2026-10-19/counts_<GENE>.json`). The snapshot content stays outside the repository.
- **Mondo IDs.** Recorded in pre-registration §4.1. The LAD-I Orphanet mismatch has been added to D-14.
- **Pre-registration v0.7.** This revision folds in the pilot report §10 and the items above (header of `preregistration/analysis_plan.md`). It is a revision, not a deviation: the plan is not frozen. No metric, threshold or disease was changed.

### 2026-10-19 · Pilot Stages 3–7 merged to `main`
- Jimmy: "Merge to main" (this session). Merged as PR #4 (cjimmylin/gp-rarelink#4), merge commit `ca4fb71`; `main` had not moved since PR #3.
- Checked before merging: 45 tests pass; no full-text Markdown, PDFs, reference snapshots or secrets tracked.
- The pilot report still waits for Jimmy's review (Stage 7 gate).

### 2026-10-19 · Pilot report drafted (Stage 7); waiting for Jimmy's review
- `reports/poc_report.md`, generated by `analysis/poc_report.py` from committed outputs. Recommendation: go, with the D-29 and D-31 fixes frozen into the pipeline (Jimmy's choice in the D-31 entry).
- Gates: Q2, Q3, Q6, Q7 (Chen 2020, D-30) and Q8 met; Q1 (53.1%), Q4 (6.0% and 6.3%) and Q5 (policy v3) not met, each stated plainly.
- Changes to freeze, and decisions still open before the freeze, are listed in the report's §10. Stage 8 was not run.
- Stage 7 gate: Jimmy's review. Merging to `main` waits for his say.

### 2026-10-19 · D-31 decided: no positional reading of stacked cells; pilot recommendation "go with fixes"
Jimmy chose the recommended option on both questions (asked in the session, 2026-10-19):
- **D-31 · Stacked cells.** Extraction v6 (`pipeline/extract/claude_code/prompts/extract_v6.md`) no longer assigns stacked values ("18 / 24 / 21 / 57") to people by position; a value is used only when the paper labels it for the person, otherwise "not reported". Gatekeeper v4 (`gatekeeper_v4.md`) treats a positional reading as at most partially supported. Both go into the frozen pipeline; no new pilot run.
- **Stage 7 recommendation:** "go with fixes". The pilot report recommends scale-up to six diseases with the D-29 and D-31 fixes frozen into the pipeline. It states plainly that Q4 was not met in the pilot (6.0% first audit; 6.3% re-audit) and that the pre-registered 250-claim audit of the frozen pipeline decides the false-positive result.

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

### 2026-10-20 · D-38 · Frozen extraction prompt and schema instantiated per disease
- **Registered:** the frozen pipeline is `extract_v6.md`, `gatekeeper_v4.md`, `schema_ha20_v5.json` and `extraction_rules_v1.md` (§6.5). The prompt and schema name A20 haploinsufficiency and TNFAIP3. §6.5 says the six-disease schema generalizes `schema_ha20_v5.json` with a per-disease checklist written from each disease's GeneReviews or key review, but says nothing about the prompt.
- **Change:** for each of the other five diseases, `pipeline/extract/claude_code/instantiate_disease.py` writes `prompts/extract_v6_<disease>.md` and `schema_<disease>_v5.json`. It swaps only:
  - the disease name and gene symbol;
  - the schema path;
  - the 20-item checklist from `configs/checklists/<disease>.json`.

  Every rule, field name, enum and example stays as frozen. The field `reports_individuals_with_tnfaip3_variant` keeps its name. Each swap must match an exact count, the frozen files' sha256 are checked first, and a diff is written to `pipeline/extract/claude_code/instantiated/<disease>.diff`: 12 changed lines per disease. The gatekeeper and the rules file are disease-neutral and used unchanged.
- **Checklists:** written by Opus helpers under `prompts/checklist_from_review_v1.md`. Each has exactly 20 items, so the frozen prompt's "each of the 20 checklist features" stays true. Every quote is checked verbatim against its source by `check_checklist.py`. Sources:
  - SSADH deficiency: 38452608 (2024 consensus guidelines);
  - Danon disease: 37821174 (2023 international consensus);
  - Tangier disease: 33994407 (Koseki 2021).
  - Alexander disease and LAD-I: GeneReviews is behind a reCAPTCHA, and Almarza Novoa 2018 is not open. Their first sources, 39420046 (a genetics meta-analysis) and 42011429 (a treatment consensus), named only 14–16 suitable features, and the helpers stopped rather than pad. Claude's call: two more open reviews or large series each, so each checklist has three sources (recorded in `source_pmid`). AxD: 32779598 and 40520824. LAD-I: 23207660 and 33391282.
- **Reason:** the frozen files cannot run on another disease without naming it. The swap is the smallest change that does.
- **Approved by:** Jimmy Lin, 2026-10-20 ("Approve scripted swap").
- **Expected effect on results:** none on HA20. For the other five, the checklist is new by design (§6.5). Everything else matches the smoke-tested pipeline.
- **Reported where:** the six-disease results report, methods section.


### 2026-10-20 · D-39 · AxD completeness catalogue checked with a supplement fetched after extraction
- **Registered:** §7.2.7 (D-35): "Each candidate's suitability is checked by script before extraction starts; a candidate without a per-variant table naming source papers is dropped, and that disease reports no completeness figure." The AxD candidate is Grossi 2024 (PMID 39420046).
- **What happened:**
  - The pre-extraction check (`analysis/catalogue/catalogue_check_2026-10-20.md`, commit `3622d03`) dropped Grossi 2024. Its per-variant table is in the supplement, and Europe PMC answered HTTP 500 when the supplement was fetched.
  - `pv1-axd` therefore extracted that paper from its main text only.
  - One retry at about 19:32 UTC, after AxD extraction finished, downloaded the three supplement files (recorded in `data/literature/axd/supplementary/manifest.csv`).
- **Change:** the supplement's per-variant table is transcribed on the harness side only, outside the extraction text. If it passes the same suitability check, AxD reports completeness under §7.2.7. Nothing is appended to the paper text `pv1-axd` read, and extraction is not re-run.
- **Reason:** the drop came from a server error, not from the catalogue lacking a suitable table. The catalogue never reaches extraction (§5.3), so using it later cannot affect what was extracted.
- **Approved by:** Jimmy Lin, 2026-10-20 ("Use it, log deviation").
- **Expected effect on results:** AxD gains a completeness figure it would otherwise lack. No effect on extraction, gatekeeper or any other disease.
- **Reported where:** the six-disease results report, beside the AxD completeness figure, saying the catalogue was added after extraction and why.
- **Outcome (2026-10-20):** `pipeline/harness/catalogue_grossi2024.py` transcribed Supplementary Table 2 to the reference root outside the repo. It has 553 rows, 187 references and 180 protein changes, and it is suitable under `catalogue_check.judge`. `judge()` chose the allele column "REF" as the source column; with "Reference (PMID)" the share of rows with both is 0.995. The rule was not changed. Manifest: `analysis/catalogue/grossi2024_manifest_2026-10-20.json`.

### 2026-10-20 · D-40 · Stage 4 (normalization, binding, phenopackets) given per-disease settings
- **Registered:** the audit's claim pool is "every value asserted in the final (post-gatekeeper) records across the six diseases" (§7.1). Records are built by normalization (VariantValidator, MANE Select), HPO and Mondo binding and phenopacket building. At `pipeline-v1.0` those scripts assume HA20: `normalize_variants --mane NM_001270508.2`, `configs/ha20_checklist_hpo.json`, the HA20 Mondo label rule and a TNFAIP3-only HGNC table in `to_phenopackets`.
- **Change:** the Stage 4 scripts read per-disease settings:
  - the gene, its HGNC ID and its MANE Select transcript, read from VariantValidator and recorded with the date;
  - a checklist-to-HPO map per disease, built from the pinned HPO release the way HA20's was, and flagged for review by Jimmy or the panel;
  - a Mondo term per disease, from the pinned Mondo release.

  HA20's settings are its existing ones, so HA20's records are built as before. No change to the four pinned files, metrics or thresholds. The model-assisted HPO binding step uses `hpo_binding_v1.md` unchanged.
- **Reason:** Stage 4 cannot run on another disease without naming its gene, transcript, disease term and checklist terms. This follows the pattern of D-38.
- **Approved by:** Jimmy Lin, 2026-10-20 ("Approve", the recommended option).
- **Also decided (no deviation):** the SSADH corpus holds one study twice (37503297, a preprint; 37962671, the journal version, whose open copy is the same text). Both stay in the corpus; the cross-paper merge joins their patients, with the merge evidence recorded, and the report says so (Jimmy Lin, 2026-10-20, "Keep both, merge patients").
- **Expected effect on results:** none on extraction or the gatekeeper. The five new diseases get records, which the audit draw and concordance need.
- **Reported where:** the six-disease results report, methods section.

Entry format once frozen:

```
### 2026-10-28 · D-43 · Isoform-sensitive positions in Stage 4 normalization; G-danon-001 withdrawn
- **Registered:** §6.2 and the Stage 4 scripts as frozen (with D-40's per-disease settings): a cDNA description whose paper names no transcript is queried on the gene's MANE Select transcript and flagged `transcript_assumed = yes`. §7.3 defines a gap variant as absent from ClinVar and not listed among OMIM's allelic variants.
- **Finding (OMIM holdout, D-42):** LAMP2 has alternative terminal coding exons 9a, 9b and 9c, and GFAP has exon 7A (epsilon) in place of exons 8 and 9. Sugie 2018 (PMID 30413001) prints the Nishino 2000 deletion as `E9b | c.1097_1098 delAA`; the run assumed NM_002294.3 (exon 9a) and produced the genomic allele X:120431457:CTT:C, which no database holds because it is not what the paper reported. That allele was gap candidate `G-danon-001`. On NM_013995 (exon 9b) the description is OMIM 309060.0001 / ClinVar 1410728. GFAP's one case (Melchionda 2013, c.1289G>A on the epsilon isoform) failed normalization safely with a reference mismatch.
- **Change:**
  - `pipeline/extract/isoform_regions.py` reads the RefSeq mRNA records (E-utilities, GenBank features) and computes, per gene, the first c. position at which the MANE and alternative transcripts' exon structures differ: LAMP2 c.1094 (NM_002294.3 vs NM_013995.2 and NM_001122606.1), GFAP c.1172 (NM_002055.5 vs NM_001131019.3). It writes an `isoform_sensitive` block into `configs/stage4/danon.json` and `axd.json` with the accessions, date and exon boundaries used. The label patterns that let a paper's own words name the isoform ("E9b", "LAMP2B", "exon 9A", "epsilon", "exon 7A") are Claude's choices, flagged for review.
  - `pipeline/extract/normalize_variants.py`: for a description with no stated transcript whose first c. position lies at or beyond that point, the paper's words around the variant (the printed string, its span, the transcript field) choose the transcript (`transcript_assumed = isoform_from_label`, reason in the new `isoform_note` column); with no such word the description gets status `isoform_ambiguous`, is not sent to VariantValidator and has no genomic key, with the candidate transcripts in `warnings`. Below the divergence point, and for the four genes without such a block, nothing changes. Unit tests: `tests/test_isoform_rule.py`.
  - `adjudication/o3_gaps/candidates.csv`: `G-danon-001` marked withdrawn (`status`, `status_note`); `omim_checked` filled for all 215 rows from the D-42 check.
- **Reason:** the registered assumption placed a reported variant on the wrong exon and created a false gap candidate; the paper's own exon label resolves it without any outside knowledge, and where the paper gives none the honest output is no genomic key.
- **Approved by:** Jimmy Lin, 2026-10-28 ("go with your recommendation on D-43").
- **Expected effect on results:** two Danon descriptions change (`c.1097_1098delAA` from 30413001 moves to NM_013995.2 and ClinVar's allele; `c.1150G>C` from 25228319, a review that names no transcript, becomes `isoform_ambiguous` and loses its genomic key; the same change stated on NM_013995.1 by 22290069, candidate `G-danon-002`, is untouched). No effect on the other five diseases. O2's Danon tier-1 overlap denominator falls by one placed variant; O3 loses one candidate.
- **Also changed:** `pipeline/extract/to_phenopackets.py` keeps the paper's own transcript description beside the MANE projection when the two differ in cDNA terms (an exon-9b frameshift was otherwise shown only as an intronic change on the MANE transcript with `p.?`).
- **Outcome (re-run of 2026-10-28, 16:06–16:10 UTC, VariantValidator 4.0.1.dev7, 166 calls):** 165 distinct Danon descriptions as before; exactly 2 rows changed against the pre-D-43 file (diff kept in the session scratchpad, summarized here): `c.1097_1098delAA` (30413001) now `isoform_from_label` on NM_013995.2, allele X:120439288:CTT:C (ClinVar 1410728's allele; the MANE projection is `c.1093+2440_1093+2441del`); `c.1150G>C` (25228319) now `isoform_ambiguous`, no genomic key. Status counts: normalized 61 (was 62), corrected 39, protein_only 25, not_normalized 27, unresolvable 12, isoform_ambiguous 1. Phenopackets rebuilt with the pinned ontology releases: 505, all schema-valid, same feature counts; 5 records differ beyond the `created` date: DANON-ID0377 (the Sugie 2018 Family 1 proband) carries the corrected allele, and DANON-ID0023, 0024, 0026 and 0027 (22290069, which names NM_013995.1) gain the LAMP2B description `c.1150G>C p.(Gly384Arg)` next to the MANE projection. The individual from 25228319 shares an identity with a record whose variant was stated with its transcript, so no phenopacket lost an expression. `created` is 2026-10-28 on all 505 files, so the Danon phenopacket directory shows as fully changed in git.
- **Reported where:** `reports/omim_holdout_assessment.md` §7 and the six-disease results report's methods, next revision.

### YYYY-MM-DD · D-nn · Short title
- Registered: what the frozen plan said (section)
- Change:
- Reason:
- Approved by: Jimmy Lin, on YYYY-MM-DD
- Expected effect on results:
- Reported where:
```
