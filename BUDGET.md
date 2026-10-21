# Budget

Actual credit spend against each budget line in the grant (`CONTEXT.md` §9). We committed to report spend per line and return anything unused.

| | |
|---|---|
| Requested | $45,000 |
| Awarded | $45,000, the full request, on 2026-08-31 (`grant/AWARD_EMAIL.md`) |
| Form | Usage credits on a paid claude.ai account. They cover chat, Claude Code, Cowork and Claude Science; the email does not mention API usage (D-17). |
| Account | claude.ai Organization ID: *to confirm* (D-01). The application named a Console org instead. |
| Spend logged to date | None (see "Usage not yet accounted for") |
| Last updated | 2026-10-18 |

## Deposits

Anthropic deposits half the award up front, then tops up toward $45,000 as credits are spent. **Each deposit expires six months after it lands.** Record each deposit as it appears in claude.ai Settings > Usage.

| # | Landed | Amount | Expires | Source |
|---|---|---|---|---|
| 1 | *to confirm* (scheduled 2026-09-21) | *to confirm* (half the award) | six months after landing | Award email; Settings > Usage |

## Lines

"Spent" and "Remaining" will be filled from the ledger below by script once entries exist. Totals are never added up by hand.

| # | Line | Requested | Spent | Remaining | Notes |
|---|---|---:|---:|---:|---|
| 1 | Extraction across six diseases, incl. re-runs as HGVS and negation handling stabilize | $8,000 | — | — | Pilot on A20 haploinsufficiency first (D-06); cost estimate before scaling |
| 2 | Gatekeeper verification pass | $4,000 | — | — | |
| 3 | ClinVar/OMIM reconciliation + concordance harness (full re-runs) | $6,000 | — | — | |
| 4 | Claude Code: pipeline, VariantValidator integration, dedup tooling, adjudication interface | $6,000 | — | — | |
| 5 | Ascertainment-bias arm | $4,000 | — | — | Comparators within the pilot diseases; no extra diseases (D-04) |
| 6 | Claude vs open-weight head-to-head | $2,000 | — | — | Published either way. Open-weight compute not covered (D-10) |
| | **Core subtotal** | **$30,000** | | | |
| 7 | Stretch: extend to all 12 candidate diseases | $9,000 | — | — | Only if the core finishes under budget; needs Jimmy's approval |
| 8 | Contingency | $6,000 | — | — | Each draw logged in `DECISIONS.md` |
| | **Total requested** | **$45,000** | | | |

**Three notes:**
- **One credit pool.** The award is a single pool of claude.ai credits, with no separate Claude Science and Claude Code allocations. The grant's 65% / 35% split (≈ $29,000 / ≈ $16,000) is now only an internal plan. We report per line, as committed (D-15).
- **Pipeline runs.** Lines 1–3, 5 and 6 are model runs inside the pipeline. Whether the credits can pay for them depends on how the pipeline calls Claude (D-17).
- **Expiry.** Unspent credits from a deposit lapse six months after it lands, so time large runs with each deposit's expiry in mind. If the first deposit landed on 2026-09-21, it expires 2027-03-21, the day after Month 6 ends (D-01). Unused credits are still reported, not spent for the sake of it.

## Usage not yet accounted for

Model usage before this file existed was not logged:

| Date | Work | Where it ran | Line |
|---|---|---|---|
| 2026-10-16 | Background literature search (129 entries) and grant-claim checks | Claude Cowork | unassigned |
| 2026-10-18 | Repository setup | Claude Cowork / Claude Code | unassigned |
| 2026-10-18 | Status review; this file, `DECISIONS.md`, pre-registration draft, award details | Claude Code (cloud session "Claude Code repo status") | unassigned |
| 2026-10-18 | Pilot design and code (Stages 0–2) | Claude Code (cloud session "Rarelink POC study design") | line 4 (pipeline) |

The award covers Cowork and Claude Code, so these sessions count against the grant **if** they ran on the funded account.

Pilot model work in this session (D-20), from the session's own list-price usage readings, which include orchestration:
- **Stage 1 screening (838 abstracts, nine Sonnet helpers):** from $19.63 to $31.46 (2026-10-18, 20:28 → 20:38 UTC).
- **Stage 2 smoke test (three papers, Opus helpers):** from $31.46 to $44.02 (`runs/poc-ha20-smoke-1/manifest.json`).
- **Stage 3 run-1 (85 papers, Opus helpers, three re-extractions):** from $45.93 to $206.13 (`runs/poc-ha20-run-1/manifest.json`), about $1.88 per paper.
- **Stage 3 repeat (15 papers) plus merge hand check (two Opus helpers) and merge-script fixes:** from $206.13 to $240.36 (`runs/poc-ha20-run-1-repeat/manifest.json`).
- **Stage 3 total:** $194.43 against the ~$381 approved under D-21 (`reports/poc_stage3_findings.md` §7).
- **Stage 3b preparation (D-22: converter fixes, supplementary files, instructions v3):** from $240.36 to $252.27.
- **Stage 3b run-2 (85 papers, Opus helpers, one repair-only resume):** from $252.27 to $418.07 (`runs/poc-ha20-run-2/manifest.json`), about $1.95 per paper.
- **Stage 3b repeat (15 papers) plus merge hand check (three Opus helpers):** from $418.07 to $460.75 (`runs/poc-ha20-run-2-repeat/manifest.json`).
- **Stage 3b total:** $220.39 against the ~$190 estimated under D-22 and the $300 stop-and-ask line (`reports/poc_stage3b_findings.md` §8). Pilot total so far: $460.75 against the $1,000 ceiling.
- **D-23 and D-24 preparation (merge policy v4, input fixes, instructions v4):** from $460.75 to $463.50.
- **v4 check (10 papers, Opus helpers), Stage 4 HPO binding (four Sonnet helpers) and Stage 5 gatekeeper (97 Opus helpers):** from $463.50 to $580.31, $116.81 together, against ~$195 approved under D-24 and D-25. They overlapped in one window (2026-10-19 02:08–03:02 UTC) and cannot be split (`runs/poc-ha20-v4-check/manifest.json`, `runs/poc-ha20-run-2-gatekeeper/manifest.json`).
- **Overage:** from about 02:50 UTC on 2026-10-19 the account was past its five-hour usage limit and the session ran on overage (extra usage). If overage bills differently from the grant credits, this matters for D-17.
- **Pilot total so far:** $580.31 against the $1,000 ceiling (`reports/poc_stage4_5_findings.md` §7).
- **After the audit (D-26 to D-28 work and the gatekeeper v2 re-check on 50 claims):** from $580.31 to $610.19 (the re-check itself from $593.02, `runs/poc-ha20-gatekeeper-v2-recheck/manifest.json`). Pilot total so far: $610.19 against the $1,000 ceiling.
- **D-29 re-run, Stage 6 and the re-audit (overlapping):** from $614.97 to $673.89, $58.92 together, against the $82.61 estimate for the re-run alone (`runs/poc-ha20-v5-subset/manifest.json`). The reading stayed at $614.97 from about 09:17 to past 09:36 UTC while helpers ran. Pilot total so far: $673.89 against the $1,000 ceiling (`reports/poc_report.md` §8).
- **Items 1–5 after the pilot (2026-10-19): five-disease screening, plus scripts and documents.**
  - 2,715 abstracts were screened by 30 Sonnet helpers. Full-text fetching, the ClinVar counts and the coverage lookup are scripts with no model calls.
  - The readings were $673.89 at 12:16 UTC and $685.10 at 14:10 UTC, before screening began. At 14:24 and 14:27 UTC, after all 30 helpers had finished, it still read $685.10, so the reading has frozen again and the screening cost is not yet captured.
  - At HA20's screening rate ($11.83 for 838 abstracts) it would be about $38. That is inside the $50–100 put to Jimmy with the items.
  - Take a fresh reading in the next session and log the difference here. This is not pilot spend; it is corpus building for the six-disease study.
  - Next reading: $689.74 at 02:48 UTC on 2026-10-20, after the Unpaywall pass and the decisions. The abstract screening therefore shows as at most $4.64 above the $685.10 frozen reading. That is less than the HA20 rate predicts, so the reading probably missed part of it; the estimate stays about $38.
- **Full-text screening (2026-10-20):**
  - 336 papers were screened by 37 Sonnet helpers (31 batches for XML papers, then 6 for papers converted from PDF). One more helper was launched as a duplicate by mistake and stopped before it wrote anything.
  - The same window covers the Docling PDF conversion, which ran on the CPU with no model calls, and the screening-check page.
  - Readings: $689.74 at 02:48 UTC to $717.13 at 03:15 UTC, so +$27.39 including orchestration. That is within the $30–60 estimated before the run.
- **Pre-freeze smoke run (2026-10-20; extraction v6 + gatekeeper v4 on the 20 D-29 papers):**
  - 20 Opus extraction helpers (one repair-only resume) and 24 Opus gatekeeper helpers (`runs/poc-ha20-v6-smoke/manifest.json`).
  - Readings: $724.22 at 04:27 UTC (before launch) to $777.72 at about 04:44 UTC (after the merge), so +$53.50 including orchestration. The estimate was about $80; the D-29 run on the same papers read +$58.92.

For scale, the two Claude Code sessions' own metadata reported about $10 ("Claude Code repo status") and about $17 ("Rarelink POC study design") as of about 18:00 UTC on 2026-10-18. These are list-price estimates the sessions report about themselves, not billing figures; the ledger needs figures from Settings > Usage.

**Questions for Jimmy (D-15):**
1. Did these sessions run on the funded claude.ai account?
2. Is the plan's included usage used before the credits? The email calls them "extra usage credits". If so, only usage beyond the plan's limits shows as credit spend.
3. Which line should Month-1 setup and literature work be booked to? None fits exactly. Line 4 is the closest for repository work; the literature search fits no line.

## Ledger

One row per run or billing period. Figures come from claude.ai Settings > Usage on the funded account (or, if D-17 adds an API route, from that account's usage report), never from estimates. Link the commit or script that made the run.

| Date | Line | What ran (script / commit) | Model | Input tokens | Output tokens | Cost (USD) | Source of figure | Logged by |
|---|---|---|---|---|---|---|---|---|
| | | *(no entries yet)* | | | | | | |

## Pre-run estimates

Before any large or repeated model run, add an estimate here and get it approved if needed. Afterwards, add the actual figure to the ledger and compare.

**Approval rule (proposed; confirm in D-15).** Ask Jimmy before any single run expected to use more than 25% of a line's remaining balance, and before scaling extraction from the pilot disease to all six. The pilot has its own approved ceiling (below).

Estimate method for scaling extraction:
1. Measure cost per input token on the pilot disease (A20 haploinsufficiency), with all passes included: extraction, reconciliation, gatekeeper and re-runs.
2. Multiply by each remaining corpus's token count. Scaling by tokens rather than papers accounts for diseases covered by long case series.
3. Note the price source and date.

| Date | Run | Line | Basis | Estimate (USD) | Approved by | Actual (USD) |
|---|---|---|---|---|---|---|
| 2026-10-18 | Pilot Stage 3: extraction over 76 full-text HA20 papers (D-20 route) | Extraction | Smoke test: at most $4.19/paper (`runs/poc-ha20-smoke-1/stage3_estimate.json`) | one run ~$318; two runs ~$636; one run + 15-paper repeat ~$381 (upper bounds, 76 papers; the reconciled corpus has 80, about +$17) | **Jimmy, 2026-10-18 (D-21): one run + 15-paper repeat** | — (session readings: +$194.43, an estimate; see above) |
| 2026-10-18 | Pilot Stage 3b: run-2 over 85 papers under revised instructions, plus a 15-paper repeat and a merge hand check | Extraction | Run-1 rate, about $1.88/paper from session readings | ~$160 + ~$30 | **Jimmy, 2026-10-19 (D-22)** | — (session readings: +$220.39 incl. $11.91 preparation, an estimate; see above) |
| 2026-10-19 | Pilot Stage 5: gatekeeper re-read of every run-2 value | Gatekeeper | Run-2 rate, about $1.95/paper | ~$170 | **Jimmy, 2026-10-19 (D-25)** | — (session readings: +$116.81 together with the v4 check and Stage 4 binding, an estimate; see above) |
| 2026-10-19 | Instructions v4 check: 10-paper mini-run | Extraction | Run-2 rate | ~$25 | **Jimmy, 2026-10-19 (D-24)** | — (included in the $116.81 above) |
| 2026-10-19 | Gatekeeper v2 re-check on the 50 audit claims (28 papers) | Gatekeeper | Run-2 gatekeeper, about $1 per helper | ~$30 | **Jimmy, 2026-10-19 (D-28)**, within the Stage 5 approval | — (session readings: +$17.17 including orchestration, an estimate) |
| 2026-10-19 | D-29 re-run: instructions v5 on 20 HA20 papers, gatekeeper v3 on all their values | Extraction, gatekeeper | Run-2 rates (`analysis/poc/pick_v5_subset.py`): $35.84 + $46.77 | $82.61 (Jimmy approved about $110) | **Jimmy, 2026-10-19 (D-29)** | — (session readings: +$58.92, $614.97 to $673.89, including concurrent Stage 6 and re-audit work; an estimate) |
| 2026-10-19 | Title and abstract screening for the five other diseases (2,715 records, Sonnet helpers) | Extraction (corpus building; no closer line) | HA20 screening rate, $11.83 per 838 abstracts | about $38 (range given to Jimmy: $50–100) | **Jimmy, 2026-10-19 ("Yes. Perform items 1-5")** | — (reading frozen at $685.10; see above) |
| 2026-10-20 | Full-text screening of the five new corpora (336 open full texts, Sonnet helpers) | Extraction (corpus building) | about 2.6M tokens of full text; HA20-style helper overhead | $30–60 | **Jimmy, 2026-10-20 ("do this: Still to do")** | — (session readings +$27.39, $689.74 to $717.13; an estimate) |
| 2026-10-20 | Six-disease run with `pipeline-v1.0`: extraction v6 + gatekeeper v4 on 350 papers (HA20 85 re-extracted; 265 eligible in the five new corpora) | Extraction (~70%), gatekeeper (~30%) | Smoke run's cost per input token × each corpus's tokens (chars/4), with a supplement allowance for the five new corpora (`analysis/cost/six_disease_estimate_2026-10-20.md`) | $795 one clean pass; $994 with repairs (1.25×); $1,590 with one full re-run (2×); upper-bound rate $876–$1,751. Optional: 10% repeat ~$80, HPO binding ~$28 | **Jimmy, 2026-10-20 (D-37): up to $1,200, incl. the 10% repeat; stop and ask before any full re-run** | HA20 part (`pv1-ha20`, 85 papers, extraction + 6 repairs + 121 gatekeeper helpers; estimate $250): session readings +$127.46, $780.63 to $908.09 (2026-10-20). Later reading $984.42 at 18:03 UTC, with no new helper work launched after the HA20 gatekeeper finished: HA20 about +$203.79 ($780.63 to $984.42; includes five checklist helpers and orchestration; an estimate). SSADH, Tangier and LAD-I (`pv1-ssadh`, `pv1-tangier`, `pv1-lad1`; estimates $125, $57, $88): their helper work overlapped and the session reading froze at $996.30 from about 18:10 to past 18:34 UTC, so per-disease readings are not separable. Helper-token estimates priced at HA20's ratio (`analysis/cost/helper_tokens.py`): SSADH ~$95, Tangier ~$52, LAD-I ~$87. Reading $1,205.03 at 18:49 UTC after all three finished: **six-disease run so far +$424.40 ($780.63 to $1,205.03)**, against $438 from the token estimates (HA20 $204 + $234). AxD (`pv1-axd`, 69 papers, estimate $119): reading $1,334.23 at 19:22 UTC, **+$129.20** ($1,205.03 to $1,334.23; AxD ran alone; helper-token estimate $131). **Six-disease run so far +$553.60 ($780.63 to $1,334.23).** Danon (`pv1-danon`, 83 papers, estimate $157): launch reading $1,339.38 at 20:01 UTC (+$5.15 of orchestration between AxD and Danon), reading $1,451.37 at 20:40 UTC, **+$111.99** (Danon ran alone). This is provisional: the helper-token estimate is $167, and the reading has lagged before; re-read before the findings report. **Six-disease run so far +$670.74 ($780.63 to $1,451.37)**, or about $725 on token estimates. 10% repeat (`pv1-<d>-repeat`, 38 papers, estimate ~$80): helper-token estimate $39. Reading $1,549.50 at 20:55 UTC: Danon plus the repeat +$210.12 ($1,339.38 to $1,549.50), against $167 + $39 = $206 on token estimates, so the Danon-only reading had lagged. **Six-disease run including the repeat: +$768.87 ($780.63 to $1,549.50); $431 left under the $1,200 ceiling.** D-40 Stage 4 (checklist-to-HPO maps and HPO binding helpers; estimate ~$28 for binding): helper-token estimate $72 (12.08 weighted M; `analysis/cost/helper_tokens.py`), above the estimate because the binding helpers searched hp.obo many times per batch. Reading $1,613.33 at 22:25 UTC: **+$832.70 for the whole run so far ($780.63 to $1,613.33); $367 left under the ceiling** |
| 2026-10-21 | D-41 model work: WS3 evidence dossiers (215 gap candidates, 20 Opus helpers) and WS5 memorization probe, Claude side (180 papers, 12 Opus helpers) | WS3: line 3 (ClinVar/OMIM reconciliation); WS5: line 5 (ascertainment bias) | WS3: pilot batch (7 candidates, $3.36) scaled by paper size; WS5: pilot on HA20 ($0.84) | WS3 $40–80 (plan), about $100–106 after the pilot; WS5 $20–40 | **Jimmy, 2026-10-21 (D-41): WS3 stop past $100; WS5 stop past $60** | Helper-token estimates (`analysis/cost/helper_tokens.py`, $5.996 per weighted M): **WS3 $64.10** (10.69 weighted M; all 215 dossiers, 4,725 quotes verbatim); **WS5 $5.34** (0.89 weighted M). The session reading froze at $1,628.03 from about 00:50 UTC on 2026-10-21 through this work, so it gives no figure; re-read later. Orchestration and the no-model work (WS1, WS2, WS4 page, WS7 GPSEA) are not in these figures |
| 2026-10-21 | D-10 open-weight pilot: DeepSeek-V4.1-Flash (2026-09-10 checkpoint) via OpenRouter, provider DeepInfra fp8, one HA20 paper (37324276), plus two stopped attempts | Contingency (D-10, ~$50) | none (pilot) | — | Jimmy, D-10 (2026-10-20); OpenRouter route suggested by Jimmy 2026-10-21 | OpenRouter key usage $0.876 → $1.067 (**+$0.19** today, including the stopped attempts); the completed pilot itself reported $0.069 (16 calls, 0.91M prompt + 0.13M completion tokens, 29 min). Billed to OpenRouter, not to the Claude credits |
| 2026-10-20 | Pre-freeze smoke run: extraction v6 + gatekeeper v4 on the 20 D-29 papers (span check only) | Extraction, gatekeeper | D-29 run's session readings: +$58.92 for the same 20 papers (incl. overlapping work) | about $80 | **Jimmy, 2026-10-20 ("Run it now")** | — (session readings +$53.50, $724.22 to $777.72; an estimate) |
| 2026-10-20 | Open-weight comparison (D-10): DeepSeek-V4.1-Flash on HA20 and SSADH deficiency | Contingency (open-weight compute is outside the $2,000 Claude line) | OpenRouter prices read 2026-10-20; 300K–1M input tokens per paper | about $50 | **Jimmy, 2026-10-20 (D-10)**; run approved 2026-10-21 ("Run both now"), stop past $40 | **Ran 2026-10-21 (`ow-ha20`, 85 papers; `ow-ssadh`, 40), billed to OpenRouter, not to the award.** Key usage $1.0689 → $21.4237: **+$20.35** for both runs, failed and stopped attempts included (`runs/ow-<d>/manifest.json`). Final attempts only, as the host reported them: HA20 $10.25, SSADH $5.54. With the pilot row above, D-10 has used about $20.55 of its ~$50. Claude side: no new helpers; orchestration is Claude Code usage in this session (reading $1,736.91 at 19:23 UTC on 2026-10-21, against $1,628.03 at 00:50 UTC; the +$108.88 also covers the D-41 helpers and is not separable) |
| 2026-10-18 | Pilot (POC) on A20 haploinsufficiency, all model-calling stages | Extraction (mostly), gatekeeper, harness, bias arm | `POC_DESIGN.md` §5. Per-stage rows to be added before each run, after Stage 2 measures per-paper cost | $200–400; ceiling $1,000; hard stop $1,500 | Jimmy (chat, 2026-10-18) | — |

**Pilot billing (D-20).** The pilot runs with Claude Code helper agents, not the API. Its model use is therefore Claude Code usage on whichever claude.ai account runs the session, which counts against the award if that is the funded account (D-15). Each stage logs the session's own list-price usage estimate before and after. Jimmy reconciles the totals against Settings > Usage. If the SLIDERS/API route is used later, D-17 applies to that spend.
