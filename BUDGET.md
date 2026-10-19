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
| 2026-10-19 | D-29 re-run: instructions v5 on 20 HA20 papers, gatekeeper v3 on all their values | Extraction, gatekeeper | Run-2 rates (`analysis/poc/pick_v5_subset.py`): $35.84 + $46.77 | $82.61 (Jimmy approved about $110) | **Jimmy, 2026-10-19 (D-29)** | — (the session reading stayed at $614.97 through the run; to be taken again) |
| 2026-10-18 | Pilot (POC) on A20 haploinsufficiency, all model-calling stages | Extraction (mostly), gatekeeper, harness, bias arm | `POC_DESIGN.md` §5. Per-stage rows to be added before each run, after Stage 2 measures per-paper cost | $200–400; ceiling $1,000; hard stop $1,500 | Jimmy (chat, 2026-10-18) | — |

**Pilot billing (D-20).** The pilot runs with Claude Code helper agents, not the API. Its model use is therefore Claude Code usage on whichever claude.ai account runs the session, which counts against the award if that is the funded account (D-15). Each stage logs the session's own list-price usage estimate before and after. Jimmy reconciles the totals against Settings > Usage. If the SLIDERS/API route is used later, D-17 applies to that spend.
