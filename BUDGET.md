# Budget

Actual credit spend against each budget line in the grant (`CONTEXT.md` §9). We committed to report spend per line and return anything unused.

| | |
|---|---|
| Requested | $45,000 (≈ $29,000 Claude Science / ≈ $16,000 Claude Code) |
| Awarded | *Not recorded yet* (see D-01) |
| Credits applied to | Anthropic Console org in `CONTEXT.md` |
| Spend logged to date | None (see "Usage not yet accounted for") |
| Last updated | 2026-10-18 |

## Lines

"Spent" will be filled from the ledger below by script once entries exist. Totals are never added up by hand.

| # | Line | Requested | Product | Spent | Notes |
|---|---|---|---|---|---|
| 1 | Extraction across six diseases, incl. re-runs as HGVS and negation handling stabilize | $8,000 | to confirm | — | Pilot on A20 haploinsufficiency first (D-06); cost estimate before scaling |
| 2 | Gatekeeper verification pass | $4,000 | to confirm | — | |
| 3 | ClinVar/OMIM reconciliation + concordance harness (full re-runs) | $6,000 | to confirm | — | |
| 4 | Claude Code: pipeline, VariantValidator integration, dedup tooling, adjudication interface | $6,000 | Claude Code | — | |
| 5 | Ascertainment-bias arm | $4,000 | to confirm | — | Comparators within the pilot diseases; no extra diseases (D-04) |
| 6 | Claude vs open-weight head-to-head | $2,000 | to confirm | — | Open-weight compute not covered (D-10) |
| | **Core subtotal** | **$30,000** | | | |
| 7 | Stretch: extend to all 12 candidate diseases | $9,000 | to confirm | — | Only if the core finishes under budget |
| 8 | Contingency | $6,000 | — | — | |
| | **Total requested** | **$45,000** | | | |

**Mapping gap (D-15).** The grant splits credits 65% Claude Science / 35% Claude Code, but only line 4 ($6,000) is explicitly Claude Code, against ≈ $16,000 in the split. Before the first progress report we need to know which lines, or parts of lines, count as Claude Code, so that spend is reported the same way it was requested.

## Usage not yet accounted for

Model usage before this file existed was not logged:

| Date | Work | Where it ran | Line |
|---|---|---|---|
| 2026-10-16 | Background literature search (129 entries) and grant-claim checks | Claude Cowork | unassigned |
| 2026-10-18 | Repository setup | Claude Cowork / Claude Code | unassigned |
| 2026-10-18 | Status review; this file, `DECISIONS.md`, pre-registration draft | Claude Code (cloud session) | unassigned |

**Questions for Jimmy (D-15):**
1. Do Cowork and Claude Code sessions draw on the grant's Console org credits, or on a claude.ai plan? If on a plan, they don't count against the grant and we log them here only for transparency.
2. If they do draw on grant credits, the Console usage page for the org is the source for the figures. Which line should Month-1 setup and literature work be booked to? None fits exactly. Line 4 is the closest for repository work; the literature search fits no line.

## Ledger

One row per run or billing period. Figures come from the Console usage export or API usage reports, never from estimates. Link the commit or script that made the run.

| Date | Line | What ran (script / commit) | Model | Input tokens | Output tokens | Cost (USD) | Source of figure | Logged by |
|---|---|---|---|---|---|---|---|---|
| | | *(no entries yet)* | | | | | | |

## Pre-run estimates

Before any large or repeated model run, add an estimate here and get it approved if needed. Afterwards, add the actual figure to the ledger and compare.

**Approval rule (proposed; confirm in D-15).** Ask Jimmy before any single run expected to use more than 25% of a line's remaining balance, and before scaling extraction from the pilot disease to all six.

Estimate method for scaling extraction:
1. Measure cost per input token on the pilot disease (A20 haploinsufficiency), with all passes included: extraction, reconciliation, gatekeeper and re-runs.
2. Multiply by each remaining corpus's token count. Scaling by tokens rather than papers accounts for diseases covered by long case series.
3. Note the price source and date.

| Date | Run | Line | Basis | Estimate (USD) | Approved by | Actual (USD) |
|---|---|---|---|---|---|---|
| | *(none yet; first expected: Month-2 pilot extraction on A20 haploinsufficiency)* | | | | | |
