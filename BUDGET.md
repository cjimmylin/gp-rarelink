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
| 2026-10-18 | Pilot Stage 3: extraction over 76 full-text HA20 papers (D-20 route) | Extraction | Smoke test: at most $4.19/paper (`runs/poc-ha20-smoke-1/stage3_estimate.json`) | one run ~$318; two runs ~$636; one run + 15-paper repeat ~$381 (upper bounds) | **pending Jimmy** (> $200 rule in `POC_DESIGN.md` Stage 3) | — |
| 2026-10-18 | Pilot (POC) on A20 haploinsufficiency, all model-calling stages | Extraction (mostly), gatekeeper, harness, bias arm | `POC_DESIGN.md` §5. Per-stage rows to be added before each run, after Stage 2 measures per-paper cost | $200–400; ceiling $1,000; hard stop $1,500 | Jimmy (chat, 2026-10-18) | — |

**Pilot billing (D-20).** The pilot runs with Claude Code helper agents, not the API. Its model use is therefore Claude Code usage on whichever claude.ai account runs the session, which counts against the award if that is the funded account (D-15). Each stage logs the session's own list-price usage estimate before and after. Jimmy reconciles the totals against Settings > Usage. If the SLIDERS/API route is used later, D-17 applies to that spend.
