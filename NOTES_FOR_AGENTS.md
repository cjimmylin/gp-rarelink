# Notes for agents

Lessons from earlier sessions, so the next agent doesn't have to rediscover them. `CLAUDE.md` loads this file automatically.

How to maintain it:
- Add what a future session would need to know. Keep entries short and dated.
- Decisions belong in `DECISIONS.md`, spend in `BUDGET.md` and commitments in `CONTEXT.md`. This file points to those; it doesn't repeat them.

*Last updated 2026-10-19 (later).*

## 1. Where things stand (2026-10-18)

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
  - **D-29 decided and run (2026-10-19):** extraction v5 (variant fields only from this person) and gatekeeper v3 (records who each quote is about) on 20 papers (`poc-ha20-v5-subset`). **Re-audit first pass in (48 of 50): 3 unsupported (6.3%), all from 42128528's stacked supplementary table; variant stratum clean. Waiting on Jimmy:** the second look (`final` collection, 5 claims) and 2 unrated claims on https://claude.ai/artifact/UHTQJ3TyT29HZ25PPdQFN8 (store collection `ratings`; collect with `apply_ratings.py --sample-dir adjudication/poc_audit_v5`, then `audit_metrics.py --run-id poc-ha20-v5-subset --gatekeeper-file gatekeeper_v3.csv --sheet adjudication/poc_audit_v5/sample.csv --out analysis/poc/audit_metrics_v5.json`). Report §10.6. (C032922 stays unsupported: Jimmy, D-30 entry.)
  - **Stage 6 done for ClinVar and HPO (2026-10-19):** `reports/poc_stage6_findings.md`. The snapshot lives outside the repo (`/home/user/gp-rarelink-reference/<date>/`, gone when the container goes; re-create with `pipeline/harness/snapshot_reference.py`); only its manifest and counts are committed. Q7 is met on the Chen 2020 Table S1 benchmark (D-30; El Hani 2024 is paywalled here): 9 of 9 restricted. The benchmark is transcribed by `pipeline/harness/benchmark_chen2020.py` into the same reference root.
  - **Next:** Stage 7 (pilot report), after the re-audit.
  - Report: `reports/poc_stage4_5_findings.md`. Session usage reading 580.31.
- **Pilot progress (2026-10-18, earlier):**
  - **Stage 1 done.** 838 records screened; 153 in the corpus; 76 with full text, which misses the 70% gate (`data/literature/ha20/search.md`).
  - **Stage 2 smoke test done.** Three papers, all 2,900 quotes found verbatim.
  - **Waiting on Jimmy's gate:** the review sheet, the group-absence rule, and Stage 3 spend (`reports/poc_stage2_smoke_findings.md`).
  - **Fix before Stage 3:** the Markdown converter's merged-cell bug, and `extract_v2`.
- **How the pilot runs (D-20).** Claude Code helper agents do the model work. No API key is needed; see the D-20 box at the top of `POC_DESIGN.md`.
- **Network (re-tested 2026-10-18, later the same day).** The research domains are now allowed: NCBI E-utilities, PMC, Europe PMC REST, VariantValidator, ClinVar FTP and purl.obolibrary.org all answer. The europepmc.org website itself still returns 403, but the REST API works.
- **Blocking the pre-registration freeze:** the pilot report (D-18), then D-08 to D-12, D-17 and D-19. Read *Open decisions* in `DECISIONS.md` before starting work.
- **Git:**
  - Everything up to 2026-10-18 is on `main`, merged with Jimmy's approval. Start new work from `main`.
  - Merge to `main` only when Jimmy says so.
  - Branch `claude/zealous-meitner-k7moex` (the pilot-design session) is archived and must not be merged: it commits full-text Markdown. Its one asset, Jimmy's 40 screening labels, was applied here on 2026-10-19.
- **More than one session writes to this repo.** On 2026-10-18 a Claude Code session and claude.ai Project chats committed in parallel, and both created `DECISIONS.md` and `BUDGET.md`. So:
  - run `git fetch origin` (all branches, not just `main`) before starting, and again before merging. On 2026-10-18 two sessions ran pilot Stage 1 in parallel because one checked only `main`;
  - check `list_sessions` for other sessions working on this repo;
  - when files collide, combine both sides; never overwrite one with the other.
- **The repo is canonical; the claude.ai Project only mirrors it** (Jimmy's decision, in `DECISIONS.md`). After changing documents here, tell Jimmy the Project mirror needs a refresh. Claude Code sessions have no access to the Project.

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

## 3. Cloud environment

**Hosts the network policy refuses** (the proxy answers 403 to CONNECT; tested twice on 2026-10-18):
- `eutils.ncbi.nlm.nih.gov` and `ftp.ncbi.nlm.nih.gov` (PubMed, ClinVar)
- `www.ebi.ac.uk` (Europe PMC)
- `export.arxiv.org`
- `rest.variantvalidator.org`
- `api.monarchinitiative.org`
- `omim.org`
- `purl.obolibrary.org` (HPO and Mondo downloads)

**What works:**
- `pypi.org` (pip)
- `raw.githubusercontent.com`
- `git push` and `git fetch` to GitHub
- (`github.com` web pages return 403 to curl.)

**Domains the pilot needs.** The pilot session listed these for Jimmy to allow on 2026-10-18: `eutils.ncbi.nlm.nih.gov`, `www.ncbi.nlm.nih.gov`, `pmc.ncbi.nlm.nih.gov`, `ftp.ncbi.nlm.nih.gov`, `www.ebi.ac.uk`, `europepmc.org`, `api.unpaywall.org`, `rest.variantvalidator.org`, `www.omim.org`, `api.omim.org`, `purl.obolibrary.org`, `raw.githubusercontent.com`, `objects.githubusercontent.com`.
- Publisher PDFs found through Unpaywall sit on arbitrary hosts, so some will still be refused. The pipeline records those as not fetched.
- `api.anthropic.com` is already reachable. The API key is a separate environment secret (`ANTHROPIC_API_KEY`); it was not set as of 2026-10-18.

**Checking and fixing:**
- `curl -sS "$HTTPS_PROXY/__agentproxy/status"` lists recent refusals.
- The fix is Jimmy's: in the cloud environment's settings, open Network access and add the hosts under Allowed domains (https://code.claude.com/docs/en/cloud-environments#network-access).
- Settings changes reach only sessions started afterwards.

**The safety check on Bash can error temporarily.** On 2026-10-18 the safety check that approves Bash commands returned no verdict several times in a row. That is an error, not a refusal. Retry once; if it keeps failing, use the Read, Edit and Grep tools and the GitHub connector, which don't need it.
- Until then, don't work around a block with mocked data or data recalled from memory.
- Never disable TLS verification or unset the proxy.

**Cowork had the same limits.** The Cowork workspace used on 2026-10-16 couldn't reach PubMed, PMC, Europe PMC, arXiv or publisher sites either. The background papers were downloaded on Jimmy's own machine with `background/fetch_papers.sh` (`background/README.md`).

**Pilot lessons (2026-10-18):**
- **Give every helper agent its own scratch directory.** Nine screening helpers shared one, and generic file names collided. One helper read another's file; it caught this itself, and a reason-vs-text check confirmed no labels were wrong.
- **The PMC OA web service is gone.** It answers 404 at both hosts. Europe PMC `fullTextXML` serves the same JATS, but answers 500 (not 404) when it has no full text; `eutils.py` handles both.
- **NCBI Bookshelf pages (GeneReviews) sit behind a reCAPTCHA**, and PubMed book records aren't parsed. Don't count on GeneReviews reference lists.
- **`jats_to_markdown` flattens rowspan and colspan**, which shifts table rows. Fix it before running extraction at scale.
- **Session usage readings include helper agents.** `get_session` cost rises with helper work, so take a reading before and after each stage.
- **Stage 3 lessons (2026-10-18):**
  - **Missing tables.** Check converted Markdown for missing tables: compare `table-wrap` counts in the XML with `### Table` counts in the Markdown. Publishers put tables in `<floats-group>`.
  - **Scope.** Helpers given "one row per person the paper describes" choose different scopes in cohort papers. Most extract TNFAIP3 carriers only; some extract everyone. This, not reading errors, drove run-to-run disagreement.
  - **Merging.** Merges must be one-to-one. A review row citing a family will otherwise join relatives into one person. Citations naming several papers ("(2, 12, 22)") are not person-specific.
  - **Reference lists.** Read them from the JATS XML, not the Markdown. Some papers nest them inside a section, and the Markdown flattens them.
  - **Commits.** Commit helper outputs as they land; the stop hook asks for it anyway. A helper may rewrite its file after you commit it, so check `git status` again before pushing.
- **Stage 3b lessons (2026-10-19):**
  - **Run span_check before the run ends.** One helper left every checklist quote empty (35958611). A repair-only resume of the same helper fixed it; diff the values before and after to prove nothing else changed.
  - **Supplementary text needs care.** Pandoc writes ">" as "&gt;" and complex tables as HTML. A gene-name relevance filter drops per-patient tables that never name the gene. Europe PMC zips often hold only figures.
  - **The sex-and-onset merge route is unsafe.** Recurrent variants and relatives in one family match on sex and onset. Citation-based merges were all correct.
  - **Helpers apply unwritten rules unevenly:** inheritance from a carrier parent, 0 counts in group tables, labels for table columns and numbering columns. Write the rule down rather than hoping for consistency.
  - **Running about 13 helpers at once worked.** That was 85 papers in about 50 minutes of wall time. A helper writes its file before its final checks, so expect rewrites after the first commit.
- **Stage 4–5 lessons (2026-10-19):**
  - **A word match is not support.** Three audit failures had values copied from their own quote but about another person or the whole cohort. Never mark a value supported by script (D-28).
  - **The second-look tab shows the gatekeeper's reasons, so labels changed there are not independent of it.** Two of Jimmy's final labels repeat v1's wording. Say so when reporting gatekeeper agreement.
  - **Don't trust the gatekeeper's rate as an error rate.** It found 0.036% unsupported where the human audit found 4%; even v2 caught 2 of 8. Report gatekeeper accuracy against human labels instead.
  - **Ratings via an artifact page work.** The `db` store keeps them; read with `ArtifactData list` + `out_dir`, then `apply_ratings.py`. Keep gatekeeper verdicts out of the first-pass page.
  - **The five-hour usage limit stops helpers mid-task.** Many had already written their output; check each file is complete before trusting it. Resume the rest with SendMessage to the same helper. `get_session` → `rate_limit_info` shows when the account is past the limit and running on overage (it matters for D-17).
  - **The session cost reading can freeze for most of an hour.** It stuck at 463.50 from about 02:08 to 02:58 UTC. Take a reading at the end too, and say when stages overlap.
  - **Helpers skip quotes on repeated labels.** In the v5 subset, four of 20 helpers left `individual_label_in_paper` spans empty in child tables (and one left 38 checklist quotes empty). Run `span_check` with the run's own `--schema` (it defaults to v2 and then reports every v5 field as a problem) before gatekeeper prep, because prep numbers claims and a later repair shifts the ids.
  - **Gatekeepers soften hard rules they think too strict.** Gatekeeper v3 says a quote about another person makes the value unsupported; helpers recorded `other_person` but judged 20 such claims partially supported. Expect it, and count `about` against `verdict` in the summary.
  - **Never put a reference snapshot in `data/reference/` in the checkout.** The extraction guard then refuses to run. Use a root outside the repo.
  - **scipy is not in the uv project.** `pipeline/extract/claude_code/gatekeeper_merge.py` has a pure-Python exact interval (`share`); reuse it rather than adding a dependency.
  - **Write gatekeeper conventions down.** Helpers split on "normal X" recorded as excluded (D-27). Any convention the extraction uses must be stated in the gatekeeper instructions too.
  - **The gatekeeper finds papers that contradict themselves** (table vs text). Those claims were judged supported with a note; collect them for the human audit.

**Python:**
- The pipeline is a `uv` project (`pyproject.toml`, `uv.lock`, Python ≥ 3.11). Run `uv sync && uv run pytest`.
- `requirements.txt` covers only the two audit scripts (scipy, which isn't preinstalled; numpy and pandas are).

## 4. Working with Jimmy

- **No contact with anyone** (`CLAUDE.md`). Draft messages; never send them. This includes questions for Prof. Lam or for Bailey at Anthropic: list the question for Jimmy instead.
- **He wants a recommendation, not a survey of options.** He decides in short messages, e.g. "go with your recommendations on D-02 through D-07". Record each one in `DECISIONS.md` as his decision, dated, stating exactly what was accepted.
- **He gives facts in pieces.** For example, the award email came first and its sent date in a later message. Record what's given and mark the rest *to confirm*. Never infer a date or amount and present it as fact.
- **Decision numbers (D-nn) are never reused or renumbered.** The next free number is **D-31**. Decisions recorded by the pilot session before the merge have no D-number; they are in the decision log as "Pilot study design approved with six decisions".
- **Revisions vs deviations.** Until the pre-registration is frozen, a change is a revision: bump the draft version and note it in the file header and in `DECISIONS.md`. After freezing, any change is a deviation and needs Jimmy's approval.

## 5. Grant claims not to repeat uncritically

The application and `CONTEXT.md` contain figures that later checks found wrong or shaky. Don't copy them into new writing without the correction.

**Patient and cohort counts:**

| Claim | Correction |
|---|---|
| Tangier: "~200 patients" | Sources say fewer than 100 to about 144 (D-14) |
| Danon: ">100 families" | "About 100 families; ≥146 molecularly confirmed patients" (D-14) |
| "408 phenopacket-store cohorts" | No published source. 731 gene folders at repo commit `85ffd78`, 2026-10-07 (D-14) |
| LAD-I: "genotypes for 184 patients published but never structured" | Probably the patients *without* a reported genotype (D-14) |

**Claude benchmark claims** (DRBench, AA-Omniscience, "97.6% HPO precision"): use the corrected wording in `background/grant_claim_checks.md` §8–10.

**Inconsistencies inside the grant:**
- The bias arm says "held-out diseases" in one place and "held-out cohorts" in another. Resolved by D-04.
- The budget's 65% / 35% product split doesn't match its lines (D-15).
- The application asked for credits on a Console (API) org, but the award is claude.ai credits that may not cover API calls (D-17).

**An unfavorable result to keep in related work:** Claude Sonnet 4 was the weakest of five models at counting probands (`murugan2026_reasoning_llm_ps4`).

## 6. Ground-truth leak paths beyond `data/reference/`

These come from pre-registration §5.3. Keep all of them out of `pipeline/`:
- building the corpus from ClinVar or OMIM citation lists, or querying any index by ClinVar variant ID;
- `phenotype.hpoa` and other disease–phenotype annotation files, which encode OMIM and Orphanet content;
- LitVar's links to ClinVar;
- prompts or outputs from the AutoOMIM project;
- database annotations in VariantValidator responses (pass only the normalization fields);
- natural-history comparator papers, which are held out for the bias arm;
- ClinVar-cited PMIDs as corpus seeds. The pilot does this on the harness side with tags (`seed_source = clinvar_citations`); report results with and without those papers (D-19);
- scoring prompt or scaffold changes against ClinVar or OMIM during development (D-07). Tune only against the papers themselves.

## 7. Conventions that worked

- **Citations.** Cite literature by its key in `background/manifest.csv`, and check by script that every cited key exists. Never add a reference from memory. A blank identifier in the manifest means "not confirmed", not "doesn't exist".
- **Numbers.** Every number in a document comes from a script in the repo, with the run date given. Example: the audit table in the pre-registration comes from `preregistration/audit_operating_characteristics.py`.
- **Dates and spelling.** Use ISO dates throughout, and US English for new documents.
- **Pre-registration markers.** Tag open items `[D-nn]`, settled items `(D-nn, decided)`, and Claude's own defaults `[proposed]`.
- **Commits.** Commit after each step. Say in the message what changed, and what deliberately didn't (e.g. "No changes to CONTEXT.md, metrics or thresholds").
