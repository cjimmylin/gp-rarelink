# Budget and spend

We committed to report actual spend against every budget line and return
anything unused (`CONTEXT.md` §9). Every spend entry below should trace to a
dated Console usage export or invoice, and to the run (script + commit) that
incurred it.

**Credits requested:** $45,000 · **Credits awarded:** _pending_ ·
**Console org:** `2056f88f-1a7b-4386-abfb-5b0fe9a98e10`

## Summary by line

Budgeted amounts are from the application. "Spent" is filled from the log
below; it is not yet reconciled against the Console (see `DECISIONS.md`,
2026-10-18).

| Line | Budgeted | Spent | Remaining | Notes |
|---|---:|---:|---:|---|
| Extraction across six diseases (incl. re-runs) | $8,000 | — | — | Pilot one disease first |
| Gatekeeper verification pass | $4,000 | — | — | |
| ClinVar/OMIM reconciliation + concordance harness | $6,000 | — | — | |
| Claude Code: pipeline, VariantValidator, dedup, adjudication UI | $6,000 | — | — | |
| Ascertainment-bias arm | $4,000 | — | — | |
| Claude vs open-weight head-to-head | $2,000 | — | — | Published either way |
| **Core subtotal** | **$30,000** | — | — | |
| Stretch: extend to 12 diseases | $9,000 | — | — | Needs Jimmy's approval |
| Contingency | $6,000 | — | — | Each draw logged in `DECISIONS.md` |
| **Total** | **$45,000** | — | — | |

Application split: ~65% Claude Science (~$29,000) / ~35% Claude Code (~$16,000).

## Pre-run estimates

Before any large or repeated run, add an estimate here first.

| Date | Run | Line | Estimated cost | Basis | Approved by |
|---|---|---|---:|---|---|
| 2026-10-18 | POC on one disease (HA20), all model-calling stages | Extraction (mostly), Gatekeeper, Harness, Bias arm | $200–400, ceiling $1,000 | `POC_DESIGN.md` §5; per-stage rows to be added before each run after Stage 2 measures per-paper cost | pending (Jimmy) |

## Spend log

| Date | Line | Amount | Source (Console export / invoice) | Run (script @ commit) | Notes |
|---|---|---:|---|---|---|
