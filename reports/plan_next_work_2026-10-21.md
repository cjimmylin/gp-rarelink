# Plan: model work while human rating waits (2026-10-21)

*Written for Jimmy, and for the next session after context compaction. Status and numbers come from `reports/six_disease_run_findings.md` and the files it cites. Nothing here changes the pre-registration. Anything marked **needs Jimmy** waits for his word.*

## 1. Where things stand

- **Done (`pipeline-v1.0`, six diseases):**
  - extraction, gatekeeper v4 and the 10% repeat;
  - Stage 4 records (D-40): 2,836 phenopackets, all valid;
  - O1 audit sample drawn (250 claims, seed 40250);
  - O2 concordance run against the 2026-10-19 ClinVar snapshot.
- **Deferred to later (human work, Jimmy's call 2026-10-21):**
  - O1 ratings: two raters, then a tie-breaker.
    - Rater A: https://claude.ai/artifact/Jvk4nxzG79u9AchAXvwPe4
    - Rater B: https://claude.ai/artifact/1VVgQNgSpyzDrsApErz8YU
  - O2 triage of 50 misses (`adjudication/o2_triage/sample.csv`).
  - The 50-merge hand check (D-35).
  - Review of the five checklist-to-HPO maps (`configs/checklist_hpo/`).
- **Spend:**
  - six-disease run line (D-37): +$832.70 by session reading, of a $1,200 ceiling;
  - session reading $1,613.33 at 2026-10-20 22:25 UTC.
- **Jimmy's own open items:**
  - push tags `prereg-v1.0` and `pipeline-v1.0`;
  - OSF registration;
  - send the drafts in `reports/drafts/`;
  - refresh the claude.ai Project mirror.

## 2. Work that needs no human now

Ordered by value for the effort. "Model spend" means helper agents. Every estimate is a guess until measured: take a session reading before and after, and compare it with `analysis/cost/helper_tokens.py`.

### WS1. Completeness against published catalogues (§7.2.7). Scripts only

- **What:** generalize `pipeline/harness/completeness.py` (built for HA20's Chen 2020 table) and run it for HA20 (`pv1-ha20`, Chen 2020) and AxD (`pv1-axd`, Grossi 2024; D-39). The other four diseases report no completeness figure, as registered (their catalogues were dropped, or there is none).
- **Inputs:**
  - Chen 2020: `<ref root>/2026-10-19/benchmarks/`;
  - Grossi 2024: `<ref root>/2026-10-20/catalogues/grossi2024_axd_table2.csv`.
  - Both sit outside the repo. If the container is new, re-create them: `benchmark_chen2020.py`, `catalogue_grossi2024.py`.
- **Output:** `analysis/six_disease/completeness_<d>.json` and a report section. Restricted recall, unrestricted recall, recall in the variant's own source paper, and patients per source paper.
- **Cost:** none. **Needs Jimmy:** no.

### WS2. Gap closure, stage 1: candidates (O3, §7.3). Scripts only

- **What:** list gap variants exactly as §7.3 defines them:
  - tier-1 normalized;
  - every supporting value supported by the gatekeeper;
  - no ClinVar record with the same GRCh38 allele.
  - OMIM can't be checked (D-12), and the report must say so.
- **Size:** O2 found 221 tier-1 alleles absent from ClinVar before the gatekeeper filter: HA20 64, SSADH 10, Tangier 7, LAD-I 84, AxD 18, Danon 38.
- **Also:** list the "reclassification candidates" (in ClinVar only as VUS or conflicting, with strong literature support), labeled exploratory.
- **Output:** `adjudication/o3_gaps/candidates.csv`, with variant, PMIDs, people, quoted spans and the pre-triage protein check.
- **Cost:** none. **Needs Jimmy:** no.

### WS3. Gap closure, stage 2: evidence dossiers for the panel. Model work

- **What:** one dossier per candidate, so the panel adjudicates fast (this feeds O5's expert-minutes). An Opus helper per batch reads the extracted records and the papers and fills an ACMG/AMP evidence sheet:
  - case count and phenotype match (PP4);
  - segregation (PP1);
  - de novo with parental testing (PS2/PM6);
  - functional evidence (PS3/BS3);
  - in-trans findings (PM3);
  - variant type (PVS1 relevance).
- **Rules:**
  - each line carries a PMID and a verbatim quote, or "not reported";
  - the helper proposes no classification; the panel decides;
  - no population-frequency data, because gnomAD is not reachable; PM2 is left for the panel;
  - ClinVar and OMIM content is never shown to the helper (§5.3). The dossier is built from the papers and our extraction only.
- **Output:** `adjudication/o3_gaps/dossiers/<variant>.json` plus a CSV, each marked *pending adjudication*.
- **Cost:** about 221 variants in about 12 batches, roughly $40–80.
- **Budget line:** "ClinVar/OMIM reconciliation" ($6,000) or contingency. **Needs Jimmy:** approve the spend and the line.

### WS4. Adjudication interface (grant deliverable; O5 expert-minutes). Claude Code

- **What:** a private Artifact page where a panel member opens a gap variant, reads the dossier, records ACMG criteria and a classification, and approves or rejects. Active minutes are logged per record (§7.5). Built like the rating pages, with a `db` store and one page per adjudicator if blinding is wanted.
- **Cost:** orchestration only, from the Claude Code line ($6,000). **Needs Jimmy:** no to build it; yes before anyone is invited (he shares the pages).

### WS5. Memorization probe, Claude side (O4, §7.4.3). Model work

- **What:** a stratified sample of corpus papers per disease, split by publication date relative to the training cutoff of the model the helpers run on. Find the cutoff in the provider's documentation, with the date read; don't assume it.
  - **(a) Closed-book recall:** given only PMID, title and year, list the variants and key phenotypes. Scored against our full-text extraction, never against ClinVar.
  - **(b) Guided completion:** given the opening of a passage, continue it. Overlap with the true text is scored by script.
- **Constraint:** helpers must not open the paper or the repo. The prompt forbids file and web tools, and the transcript is checked for tool calls afterwards; any probe that used a tool is discarded and reported.
- **Cost:** about 30 papers per disease × 2 probes, short calls: roughly $20–40.
- **Budget line:** "Ascertainment-bias arm" ($4,000). **Needs Jimmy:** approve the spend. The open-weight half waits on the D-10 host.

### WS6. Bias arm preparation (O4, §7.4.1–7.4.2). Scripts, light model use

- **What:**
  - confirm the held-out comparator papers are open and fetched (holdouts: 2 AxD, 1 SSADH, 2 Danon; HA20 has candidates; LAD-I and Tangier have none);
  - build the sheet where **a human** lists each comparator's HPO-mappable features and cohort frequencies (§7.4.2 step 1 requires a human, before literature frequencies are computed);
  - write the frequency-deviation script (three-state: observed ÷ assessed is primary), with the publication-cluster bootstrap. It is not run until the human sheets are in.
- **Cost:** none. **Needs Jimmy:** later, for the human listing.

### WS7. Exploratory analyses (§7.6). Scripts

- **Per-gene genotype–phenotype maps** with GPSEA and its multiple-testing correction. This adds the `gpsea` package to the uv project.
- **Danon sex difference:** does the extracted cohort reproduce the male/female severity gap? It is a reproduction check, since the papers overlap.
- **Tangier:** the share of ClinVar ABCA1 records that match literature-reported Tangier patients.
- All labeled exploratory. **Cost:** none. **Needs Jimmy:** no.

### WS8. Open-weight comparison harness (O5, D-10). Claude Code, run blocked

- **What:** build the agent harness that gives DeepSeek-V4.1-Flash the same instruction files, inputs and file tools as the Claude helpers, and test it on a stub without spending.
- **Blocked:** the run waits on Jimmy opening the hosted-API account (D-10). Compute is about $50 from contingency.

### WS9. Writing. Model work, small

- A methods section for the manuscript, from the frozen plan and the deviations D-38 to D-40.
- A progress update for Anthropic's program: metrics so far and spend per line. It is a draft for Jimmy to send; Claude sends nothing.

## 3. Not doing without Jimmy's approval (would be deviations or re-runs)

- **Re-extracting papers with known input problems:** scrambled tables (SSADH 14635103, AxD 34046764, Danon 42366573), missing supplements, and LAD-I 33391282's truncated supplement.
- **Notation repairs for pv1 normalization**, like the pilot's D-26 query corrections. AxD's cDNA printed without "c." is the main case (78.8% normalized).
- **Any change to the frozen prompts.** This includes the known hedge gap: extraction v6 has no hedge rule.

## 4. Recommended order

1. WS1 and WS2 now: scripts, no spend, and they unblock WS3.
2. WS7: scripts, no spend.
3. WS4: build the adjudication page.
4. WS3 and WS5 once Jimmy approves their spend: about $60–120 together.
5. WS6 and WS8 prep. WS9 drafts whenever useful.

## 5. For the next session (after compaction)

- **Read first:**
  - this plan;
  - `NOTES_FOR_AGENTS.md` §1 (latest entries at the end of the 2026-10-20 block);
  - `reports/six_disease_run_findings.md`;
  - `DECISIONS.md` (next free decision number: D-42).
- **Reference root:** `/home/user/gp-rarelink-reference/`, outside the repo, with dated folders 2026-10-19 (ClinVar, HPO annotations, Chen 2020) and 2026-10-20 (Grossi catalogue). It disappears with the container. Re-create it:
  - `pipeline/harness/snapshot_reference.py --per-gene`;
  - `pipeline/harness/benchmark_chen2020.py`;
  - `pipeline/harness/catalogue_grossi2024.py`.
- **Isolation:** nothing under `pipeline/extract` may read the reference root or name OMIM (the test enforces this). Harness code goes in `pipeline/harness`.
- **Helpers:** at most 20 at once. Give each its own scratch directory and commit outputs as they land. Run the span check before any gatekeeper prep. Take a session cost reading before and after each stage.
- **Commit trailer:** `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and the `Claude-Session:` line. Branch `claude/gracious-pascal-j7krug`. Merge to `main` only on Jimmy's word.
