# Pilot Stage 2: smoke-test findings (HA20, D-20 route)

*Run `poc-ha20-smoke-1`, 2026-10-18. Three papers, each extracted by its own Claude Code helper agent (Opus) under `pipeline/extract/claude_code/prompts/extract_v1.md`. Numbers come from `data/extracted/ha20/poc-ha20-smoke-1/span_check.json`, `runs/poc-ha20-smoke-1/manifest.json` and `runs/poc-ha20-smoke-1/stage3_estimate.json`. The review sheet for the human gate is `reports/poc_review_poc-ha20-smoke-1.md`.*

## What ran

| PMID | Paper | Why chosen | Individuals | Variant rows | Feature rows | Checklist rows |
|---|---|---|---|---|---|---|
| 36727002 | Liu 2023, Front Pediatr | single patient, plus a review table of 15 earlier cases | 18 | 18 | 159 | 360 |
| 35154120 | Rossi 2022, Front Immunol | one family (mother and three daughters) | 5 | 4 | 38 | 100 |
| 41890736 | Yao 2026, Front Immunol | five children, patients as table columns | 5 | 5 | 69 | 100 |

## Automated checks (Stage 2 checks 1–2)

- **Quotes on every value.** All 2,900 asserted values carry a quote and a PMID.
- **Quotes verbatim.** All 2,900 quotes were found in the paper exactly, after whitespace collapsing only; none needed the lenient match, and none were missing.
- **Structure.** 0 problems: every field present, enums valid, labels consistent across tables, all 20 checklist rows for every individual.
- **Isolation.** `data/reference/` was absent during the run, and the isolation tests pass.

## Cost (gate: at most $5 per paper)

- **This run:** the session's own usage reading rose by $12.56 during the run, so at most **$4.19 per paper**. The figure includes the orchestrating session's own work, and it is a list-price estimate, not a billing figure. It passes the gate.
- **Stage 3, same upper bound, 76 papers with full text:**
  - one full run: about $318;
  - two full runs (as `POC_DESIGN.md` Stage 3 specifies): about $636;
  - one full run plus a 15-paper repeat for the stability check: about $381.
- **Not included:** the gatekeeper (Stage 5).
- **Approval:** Stage 3 needs Jimmy's OK, because it exceeds $200.

## What the helpers did well

- **They kept contradictions instead of resolving them.** In 41890736 the paper puts the second-gene (MMACHC) variants in patient 3 in one place and patient 2 in another; the helper recorded neither. Patient 2's oral ulcers are "NO" in the tables but present in the discussion, so it recorded both and said so.
- **They declined to infer.** No "de novo" or "maternal" without the paper saying it (rule 8), even where the trio data imply it. The father in 36727002 carries the variant, but his zygosity was left unstated.
- **They flagged odd text in the paper.** Age inconsistencies, a lab value the authors call "high" that sits inside the reference range, and a likely translation error ("pendulous ulcers").

## Problems to fix before Stage 3 (proposed; decisions marked for Jimmy)

1. **The converter garbles merged table cells. Fix needed.** `jats_to_markdown` flattens rowspan and colspan, so 35154120's patient table came out with rows shifted. The helper recovered the alignment from the prose, but that won't always be possible. The converter should expand merged cells before Stage 3.
2. **Absence inferred from group statements. Jimmy to decide.** Statements like "Pt3 was the only one with recurrent fevers" were used to mark fever as *excluded* in the other patients. "Arthritis NO" in a table was also used to exclude the checklist item "arthritis or arthralgia".
   - *Proposal:* allow a group statement only when it names the group explicitly, and tag such rows as inferred.
   - Never let a narrower absence ("no arthritis") exclude a broader checklist item ("arthritis or arthralgia").
3. **Null vs "not reported."** The instructions said "not reported" for missing text, but the schema says null for some fields, and the helpers chose null. Version 2 of the instructions will follow the schema.
4. **Quote limit.** Three quotes per value truncated treatment summaries. Proposal: up to five for summary fields.
5. **Tables with patients as columns.** Quotes then run from the row label through the patient's cell, e.g. `| Sex | F | M`. This is valid, but an auditor has to count columns. Version 2 will say so explicitly, and the review sheet will show the column header.
6. **Fields missing from the schema:**
   - *age at diagnosis* (given in two of the three papers, with nowhere to put it);
   - *for rows taken from a review table, the cited source reference*. The merge policy (`POC_DESIGN.md` §3.6) needs it to join review rows to the primary paper. The helper put the reference number into the label, e.g. `1 (2)`.

   Adding these two fields keeps the table set unchanged.
7. **Variants in other genes.** One helper recorded an alpha-thalassemia deletion; another omitted the MMACHC variants because their attribution was contradictory.
   - *Proposal:* record other-gene variants only when they are attributed to one person unambiguously.
   - Keep them out of the HA20 variant analyses by gene symbol.
8. **The "original string" for split variant descriptions.** When the paper splits the cDNA, transcript and protein across a sentence, the original-string field held the whole phrase. Proposal: use the shortest contiguous variant mention, and keep the pieces in their own fields.

## Other open items

- **Coverage.** 76 of 153 corpus papers have full text (Q1 gate missed). Unpaywall needs an email address (Jimmy). Paywalled papers need library copies; the list is in `data/literature/ha20/corpus_stats.json`.
- **Screening spot-check.** `data/literature/ha20/study_type_spotcheck.csv` holds 20 rows for Jimmy to label. The gate is at least 18 of 20 agreeing.

## Gate decision needed (Jimmy)

1. Is the smoke output usable? See `reports/poc_review_poc-ha20-smoke-1.md`, especially the tables of features recorded as absent.
2. Decide item 2 above (absence inferred from group statements).
3. Approve the Stage 3 spend. Recommendation: one full run plus a 15-paper repeat for stability (about $381 upper bound), rather than two full runs (about $636). The gatekeeper estimate follows after the run.
4. If coverage matters for the pilot: the Unpaywall email address, and library copies.
