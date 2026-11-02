# Session history (moved out of NOTES_FOR_AGENTS.md)

Dated progress entries moved here verbatim on 2026-11-02 so `NOTES_FOR_AGENTS.md` stays under Claude Code's memory-file size limit. Nothing here is current guidance: the reports in `reports/`, the run manifests in `runs/`, `BUDGET.md` and `DECISIONS.md` are the record. Original line numbers in `NOTES_FOR_AGENTS.md` (as of 2026-10-28) are given for each block.

## NOTES_FOR_AGENTS.md lines 13-60

- **Current priority: pilot first (D-18).** A one-disease proof of concept on A20 haploinsufficiency runs now, under `POC_DESIGN.md`, before the pre-registration is frozen. If you are the session executing the pilot, `POC_DESIGN.md` is your protocol; work through its §8 checklist.
- **Phase:** Month 1 ends 2026-10-20 (provisional start 2026-09-21, D-01). The dated calendar is in `CONTEXT.md` §8.
- **Done:**
  - working rules: `CLAUDE.md`, `INSTRUCTIONS.md`, `CONTEXT.md`;
  - the grant application and award email (`grant/`);
  - background literature (`background/`, compiled 2026-10-16 in Cowork);
  - `DECISIONS.md` and `BUDGET.md`;
  - pre-registration draft v0.6 (`preregistration/analysis_plan.md`), not frozen. D-01 to D-07, D-18 and D-26 to D-28 are decided;
  - a digest of the claude.ai Project chats (`docs/claude-ai-threads.md`) and the pre-grant concept chat (`background/origins/`), both added from claude.ai on 2026-10-18;
  - **pilot Stages 0–2, built and tested offline** by the session "Rarelink POC study design" (merged from branch `claude/zealous-meitner-k7moex`). That covers:
    - the `pipeline/` skeleton with isolation guard and tests;
    - the corpus scripts;
    - the SLIDERS Anthropic adapter (`pipeline/extract/sliders_adapter/`);
    - the HA20 config and schema;
    - 24 tests (`uv sync && uv run pytest`).
- **Pilot Stage 3 done (2026-10-18, later):**
  - run-1 covered 85 papers and the repeat 15;
  - every quote was found verbatim;
  - merges: 2 false among the 58 merges of policy v2, now policy v3;
  - variant agreement is below 0.9 because of cohort scope.
  - Report: `reports/poc_stage3_findings.md`. D-22 decided 2026-10-19 (instructions v3, run-2, supplementary files). Session usage reading 240.36 at the end of Stage 3.
- **Pilot Stage 3b done (2026-10-19):**
  - run-2 over all 85 papers is the extraction of record: 64,999 quotes, all verbatim; 799 individuals;
  - repeat variant agreement 0.944 on strings, 0.988 on keys (gate met);
  - fresh merge hand check: 6 false of 93, all from the sex-and-onset route; policy v4 proposed.
  - Report: `reports/poc_stage3b_findings.md`. Session usage reading 460.75.
  - D-23 to D-25 decided by Jimmy, 2026-10-19: merge policy v4; instructions v4 plus input fixes, checked on 10 papers, with no run-3; Stage 5 approved at about $170 after Stage 4.
- **Pilot Stages 4 and 5 done, v4 checked (2026-10-19):**
  - v4 check: 13 of 13 rule checks as intended; run-2 stays the extraction of record;
  - Stage 4: 749 phenopackets, all valid; HPO binding 88.5%; normalization 92.8% of cDNA descriptions (check not met as worded, D-26);
  - Stage 5: 8 unsupported and 305 partial of 22,003 judged values; phenopackets rebuilt without claims not judged supported.
  - Human audit (Jimmy, first pass): 2 of 50 unsupported (4.0%, the Q4 limit), 6 partial. The gatekeeper flagged none of his 8; v2 (D-28) flags 2. D-26 repairs: 135 of 138 cDNA descriptions normalized. Report §10.
  - **Audit ratings (collected 2026-10-19):** the 50 claims and 30 HPO bindings were rated on the private rating page https://claude.ai/artifact/WKu5hAmopKibygDb2tte6P (built by `adjudication/poc_audit/make_rating_page.py`; ratings save to the page's store). To collect them: `ArtifactData` `list` of `ratings` and `hpo` with `out_dir`, then `adjudication/poc_audit/apply_ratings.py`, then `analysis/poc/audit_metrics.py`. D-26 to D-28 decided 2026-10-19. The step-3 second look is done (`final` collection): **Q4 not met, 3 of 50 unsupported (6.0%)**; D-29 (fixes and a re-run) is open, report §10.5.
  - **D-29 decided and run (2026-10-19):** extraction v5 (variant fields only from this person) and gatekeeper v3 (records who each quote is about) on 20 papers (`poc-ha20-v5-subset`). **Re-audit done (48 of 50 rated): final 3 unsupported (6.3%), all stacked-table readings Jimmy could not verify; 0 of 45 without them; variant stratum clean. D-31 (stacked cells) open.** Page: https://claude.ai/artifact/UHTQJ3TyT29HZ25PPdQFN8 (store collection `ratings`; collect with `apply_ratings.py --sample-dir adjudication/poc_audit_v5`, then `audit_metrics.py --run-id poc-ha20-v5-subset --gatekeeper-file gatekeeper_v3.csv --sheet adjudication/poc_audit_v5/sample.csv --out analysis/poc/audit_metrics_v5.json`). Report §10.6. (C032922 stays unsupported: Jimmy, D-30 entry.)
  - **Stage 6 done for ClinVar and HPO (2026-10-19):** `reports/poc_stage6_findings.md`. The snapshot lives outside the repo (`/home/user/gp-rarelink-reference/<date>/`, gone when the container goes; re-create with `pipeline/harness/snapshot_reference.py`); only its manifest and counts are committed. Q7 is met on the Chen 2020 Table S1 benchmark (D-30; El Hani 2024 is paywalled here): 9 of 9 restricted. The benchmark is transcribed by `pipeline/harness/benchmark_chen2020.py` into the same reference root.
  - **Stage 7 drafted (2026-10-19):** `reports/poc_report.md` (regenerate with `uv run python analysis/poc_report.py`). Recommendation: go with fixes (D-31 entry). Extraction v6 and gatekeeper v4 are the frozen-pipeline candidates, not yet run. Merged to `main` on Jimmy's instruction (PR #4, 2026-10-19). **Waiting on Jimmy:** review of the pilot report.
  - **Next after his review:** fold the report's §10 into the pre-registration, done 2026-10-20: report approved, D-08 to D-12, D-17, D-19, D-32, D-33 decided (pre-registration v0.10); freeze after the panel hours and the screening check.
  - Report: `reports/poc_stage4_5_findings.md`. Session usage reading 580.31.
- **Items 1–5 after the pilot (2026-10-19, Jimmy: "Yes. Perform items 1-5"):**
  - **Corpus searches and title/abstract screening are done for the five other diseases** (`configs/diseases.yaml`; `data/literature/<disease>/search.md`, generated by `analysis/corpus/corpus_summary.py`).
    - Counts per disease are in `analysis/corpus/coverage_2026-10-19.md`. Holdouts are marked out: 2 for axd, 1 for ssadh, 2 for danon.
    - Human 10% check and full-text screening not done.
  - **Open full text is far below HA20's** (`analysis/corpus/coverage_2026-10-20.md`, after the Unpaywall pass). D-08, D-19 and D-32 were decided 2026-10-20.
  - **Dated ClinVar counts** for all six genes are in `CONTEXT.md` §4 (`analysis/poc/reference_snapshot/2026-10-19/counts_<GENE>.json`).
  - **Pre-registration v0.7.**
  - **Message drafts** in `reports/drafts/`, for Jimmy to send.
- **2026-10-20 (Jimmy: "do this: Still to do", plus eight answers):**
  - **Decisions:** pilot report approved; D-09, D-11 (rater design), D-12, D-17 and D-33 decided; D-10 shortlist in `reports/drafts/d10_open_weight_shortlist.md`. Pre-registration draft v0.9. D-10 decided (DeepSeek-V4.1-Flash; HA20 + SSADH; agent harness; ~$50 contingency). Still blocking the freeze: the panel's hours (D-11). The screening check was settled by D-34.

## NOTES_FOR_AGENTS.md lines 62-68

  - **Full-text screening** runs as Sonnet helpers with `screen_fulltext_v1.md`, through `claude_code_fulltext_screen.py export/import`. Import checks every evidence quote verbatim.
  - **Human check:** the screening-check page is https://claude.ai/artifact/1JoRKB2uVCap3XAJUDw3RN, with store collections `abstract_check` and `exclusion_check`. It is built by `adjudication/screening_check/make_sample.py` and `make_page.py`.
- **Pilot progress (2026-10-18, earlier):**
  - **Stage 1 done.** 838 records screened; 153 in the corpus; 76 with full text, which misses the 70% gate (`data/literature/ha20/search.md`).
  - **Stage 2 smoke test done.** Three papers, all 2,900 quotes found verbatim.
  - **Waiting on Jimmy's gate:** the review sheet, the group-absence rule, and Stage 3 spend (`reports/poc_stage2_smoke_findings.md`).
  - **Fix before Stage 3:** the Markdown converter's merged-cell bug, and `extract_v2`.

## NOTES_FOR_AGENTS.md lines 72-72

  - **Smoke run** `poc-ha20-v6-smoke`: span check clean, gatekeeper v4 judged 23 of 4,538 claims unsupported, +$53.50 (`reports/poc_smoke_v6_findings.md`).

## NOTES_FOR_AGENTS.md lines 78-81

  - **HA20 done (`pv1-ha20`, 2026-10-20):** 85 papers, span check clean, gatekeeper v4 judged 46 of 23,129 model claims unsupported (0.20%) and 400 partial. Manifest `runs/pv1-ha20/manifest.json`; cost reading in `BUDGET.md` (provisional).
  - **SSADH, Tangier, LAD-I and AxD done (2026-10-20):** unsupported 37 of 9,759 (0.38%), 15 of 4,830 (0.31%), 47 of 10,864 (0.43%), 39 of 14,403 (0.27%). Manifests in `runs/pv1-<d>/manifest.json`. Run spend $553.60 after AxD (`BUDGET.md`). Danon next; Jimmy chose to start it after the five-hour usage reset (20:00 UTC) rather than run on overage.
  - **Danon done and the 10% repeat done (2026-10-20):** Danon 110 of 17,963 unsupported (0.61%; three papers hold 60). All six: 294 of 80,948 (0.36%). Repeat (38 papers, seed 20261020): checklist 97-100% agreement; variant keys 0.83-1.00, the two dips are notation only. Run spend +$768.87 of $1,200. Report: `reports/six_disease_run_findings.md`; tables by `analysis/six_disease/run_summary.py` and `repeat_summary.py`.
  - **D-40 done (2026-10-20):** per-disease Stage 4 settings (`configs/stage4/`, `pipeline/extract/stage4_config.py`), checklist-to-HPO maps (`configs/checklist_hpo/`), 2,836 phenopackets, all valid. Report §9 (`reports/six_disease_run_findings.md`).

## NOTES_FOR_AGENTS.md lines 120-120

  - **The session cost reading lagged again:** +$111.99 for Danon at 20:40, but Danon plus the repeat read +$210.12 at 20:55 against $206 on token estimates. Check against `helper_tokens.py`.

## NOTES_FOR_AGENTS.md lines 133-133

  - **SLIDERS ablation pilot done (2026-10-28, D-44, exploratory; PR #16, merged to `main` on Jimmy's instruction):** arm D = direct extraction (one Opus helper per paper, plain 60-line prompt `pipeline/extract/claude_code/prompts/direct_v1.md`, no quotes, no rules, no gatekeeper) on the 124 HA20 + SSADH papers with text, converted to the five-table shape by `direct_to_tables.py` and scored with the same harness as pv1 on a fresh 2026-10-28 snapshot; arm-blinded locate-and-judge judge (`judge_locate_v1.md`) on a seeded sample from both arms. Design `reports/sliders_ablation_design.md`; findings `reports/sliders_ablation_findings.md` (regenerate: `summary.py`, then `report.py` in `analysis/sliders_ablation/`); cost $317.13 by helper tokens (extraction $197.34; judge $119.78 over all 116 papers after Jimmy raised the $300 ceiling). Jimmy approved (2026-10-28, "yes for both and also merge to main") judging the 45 deferred HA20 papers past the ceiling, queuing the human audit sheets in `adjudication/sliders_ablation/audit/` with O1/O5, and the merge to `main`.

## NOTES_FOR_AGENTS.md lines 139-139

  - On `main`: PR #3 (pilot Stages 1–2), PR #4 (Stages 3–7), PR #5 (five-disease corpus, screening, D-08 to D-12, D-17, D-19, D-32, D-33, pre-registration v0.10), PR #6 (D-34, v0.11), PR #7 (D-11, D-35, v0.12), PR #8 (smoke run, freeze v1.0, D-36; merged with a merge commit so the tagged commit `ef3133e` is in `main`'s history), PR #9 (six-disease run, concordance, D-41 work, D-10 open-weight comparison, D-13, D-14; merged 2026-10-22), PR #10 (budget spend by line; merged 2026-10-24), PR #11 (notes only; merged 2026-10-24) and PR #12 (interim paper for internal review; merged 2026-10-27), PR #15 (OMIM holdout assessment, D-42; D-43 withdrawal, isoform rule and Danon re-normalization; merged 2026-10-28 on Jimmy's instruction "merge to main") and PR #16 (SLIDERS ablation pilot, D-44; merged 2026-10-28), PR #17 (interim paper version 2 with the OMIM work throughout; panel adjudication-page draft; merged 2026-10-28 on Jimmy's instruction "merge to main"), all merged with Jimmy's approval. Start new work from `main`.

## NOTES_FOR_AGENTS.md lines 148-171

## 2. Next steps, in order, once unblocked

1. **Network access and the API key** (§3; D-17 for billing). Everything below depends on them.
2. **The pilot, `POC_DESIGN.md` Stages 1–7:**
   - corpus (runbook: `data/literature/ha20/README.md`);
   - three-paper smoke test;
   - two full extraction runs;
   - phenopackets;
   - gatekeeper, plus the 50-claim audit rated by Jimmy;
   - ClinVar concordance and completeness;
   - the pilot report.
   Stay within the approved ceiling: $1,000, hard stop $1,500 (`BUDGET.md`).
3. **Apply the merge-time notes** at the top of `POC_DESIGN.md`:
   - report pilot results with and without ClinVar-seeded papers (D-19);
   - remember HA20 is a development disease (D-18);
   - log spend with the account it billed to (D-17).
4. **In parallel, for the six-disease study:**
   - corpus search for the other five diseases (pre-registration §5.1);
   - reference snapshots and dated per-gene counts to replace the provisional numbers in `CONTEXT.md` §4;
   - open-access coverage per disease (feeds D-08);
   - outreach drafts to the Monarch and ClinVar maintainers, for Jimmy to send.
5. **After the pilot report:** fold its findings into the pre-registration (`POC_DESIGN.md` §7 lists what it hands over), resolve the remaining open decisions, and freeze.

Offered but not yet requested: a draft introduction for the program's Discourse cohort thread.

## NOTES_FOR_AGENTS.md lines 203-203

**Cowork had the same limits.** The Cowork workspace used on 2026-10-16 couldn't reach PubMed, PMC, Europe PMC, arXiv or publisher sites either. The background papers were downloaded on Jimmy's own machine with `background/fetch_papers.sh` (`background/README.md`).
