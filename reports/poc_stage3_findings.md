# Pilot Stage 3: extraction run and repeat (A20 haploinsufficiency)

*2026-10-18. Branch `claude/gracious-pascal-j7krug`. Route D-20 (Claude Code helper agents, Opus), approved under D-21: one full run plus a 15-paper repeat. HA20 is a development disease (D-18), so none of this is a headline result for the six-disease study.*

Every number below comes from a script in the repo. The output file is named next to each number.

## 1. Summary

- **Run-1 covered all 85 full-text papers.**
  - Quotes: all 54,110 quoted values were found verbatim in their paper, with 0 structural problems (`data/extracted/ha20/poc-ha20-run-1/span_check.json`).
  - Content: 635 individuals; 399 have a TNFAIP3 variant row. There are 403 TNFAIP3 variant rows, with 241 distinct variant strings (`analysis/poc/extraction_counts_poc-ha20-run-1.json`).
- **Repeat on 15 random papers** (seed 20261018):
  - Checklist answers agreed in 98.7% of 980 cells.
  - The number of individuals matched in 12 of 15 papers.
  - Variant agreement was 0.55 on exact strings and 0.70 on normalized keys. Both are below the 0.9 that `POC_DESIGN.md` uses as the sign of stable prompts.
  - The disagreement is mostly about scope (which cohort members and relatives to include, and whether to list variants in other genes), not about reading values differently.
  - Leaving out the two papers where the runs chose a different scope, variant agreement on normalized keys is 0.97 (§4).
- **Merging across papers:**
  - Hand check of every merge under policy v2 (58 pairs): 52 true, **2 false**, 4 cannot tell, and 1 missed merge found. The pilot's target was 0 false merges, so **Q5 is not met**.
  - Both false merges rested on citations that name several papers. Policy v3 no longer accepts those: it makes 52 merges with no known false merge. Because v3 was tuned on this same check, that is not an independent estimate (§5).
- **Spend:** the session usage reading rose by $194.43 over Stage 3 ($45.93 to $240.36). D-21 approved about $381 for this stage (§7).
- **Five rule questions need your call before the next run** (§8). My recommendation: settle them, then do one more full run under the revised prompt (about $160) before Stage 4.

## 2. What ran

| | Run-1 (`poc-ha20-run-1`) | Repeat (`poc-ha20-run-1-repeat`) |
|---|---|---|
| Papers | 85 (all with full text, of 161 in the corpus) | 15, drawn at random from the 73 run-1 papers that have individual rows (`runs/poc-ha20-run-1-repeat/selection.json`) |
| Helpers | one Opus helper per paper, each with a private scratch directory | same |
| Instructions | `extract_v2.md`, `schema_ha20_v2.json`, `extraction_rules_v1.md` (hashes in `runs/*/manifest.json`) | identical |
| Usage reading | 45.93 → 206.13 | 206.13 → 240.36 |

**Fixed during the run:**
1. **Missing tables.** The JATS converter dropped tables that publishers place in `<floats-group>`, outside `<body>`. Twelve papers lost all their tables. The fix only appends content, so quotes already extracted stay valid. Three papers had already been extracted without their tables (30170128, 35268369, 41654260). They were re-extracted, and the first outputs are kept in `superseded_missing_tables/`.
2. **Merging.** Four fixes to the merge script, all covered by tests (§5).

## 3. Stage 3 checks (`POC_DESIGN.md`)

| Check | Result |
|---|---|
| 1. Counts | 85 processed, 0 failed. 11 papers report nobody with a TNFAIP3 variant (screening false positives or reviews without patient-level data; list in §6). 635 individuals: 385 described first-hand, 250 taken from tables or summaries of earlier reports. Phenotypic features: 2,975 observed and 1,066 excluded; 435 rows rest on a group statement (D-21). Checklist: 1,350 observed, 337 excluded, 11,013 not reported. |
| 2. Span check ≥ 98% | **Met:** 54,110 of 54,110 found verbatim (100%). Repeat: 8,663 of 8,663. |
| 3. Every variant row has an original string | **Not met as worded:** 34 of 460 variant rows have none. These are rows where the paper ties a TNFAIP3 variant to a person but prints the variant only in a supplement or figure. Proposal in §8. |
| 4. Checklist complete for every individual | **Met:** 0 individuals with missing checklist rows. |
| 5. Run-to-run agreement | Variant agreement is below 0.9 (§4). |
| 6. Merge hand check | 2 false merges under policy v2 (§5). |

## 4. Run-to-run agreement (15 papers)

Source: `analysis/poc/run_agreement_poc-ha20-run-1_vs_poc-ha20-run-1-repeat.json`.

| Measure | Value |
|---|---|
| Checklist cells with the same status (only where both runs used the same label) | 0.987 (980 cells) |
| Papers with the same number of individuals | 12 / 15 |
| Variant strings, Jaccard (`POC_DESIGN.md` measure) | 0.547 |
| Variants on normalized cDNA/protein keys | 0.702 |
| (individual, HPO candidate) pairs (`POC_DESIGN.md` measure) | 0.421 |
| (HPO candidate, status), ignoring labels | 0.757 |
| Individual labels in common | 0.320 |

**Causes, from the per-paper rows:**
- **Cohort scope.** The instructions say "one row per person the paper describes". Most helpers read that as the TNFAIP3 carriers and their relatives, but some included every cohort member.
  - 33971891: run-1 extracted all 23 people in the cohort; the repeat extracted 3.
- **Variants in other genes.** In 36325013, run-1 listed 19 lupus-risk alleles from a table; the repeat did not.
- **Effect of these two papers.** Leaving out 33971891 and 36325013, the two scope cases, variant agreement rises from 0.547 to 0.705 on exact strings and from 0.702 to **0.973** on normalized keys. Checklist agreement stays at 0.987. Source: `analysis/poc/run_agreement_..._excluding_33971891_36325013.json`.
- **Different spellings of the same variant.** For example, "C200A fs*16" and "C596_598 del A" for the same sister. On normalized keys, 35958611 and 41905891 agree completely; on exact strings they do not.
- **Invented labels.** Where the paper gives no label, each run made up its own ("14-year-old English boy" vs "The first case of allogeneic HCT"). Checklist and HPO comparisons that join on labels then see different people.
  - 35958611 and 41654260 share no labels, so no checklist cells could be compared.

Where scope and labels agree, the two runs mostly read the same values. The fixes belong in the instructions, not the model (§8, items 1–2).

## 5. Merging the same patient across papers

The script is `pipeline/extract/reconcile.py`. It is deterministic, makes no model call, and reads only the extraction output and the papers' own reference lists; it never reads ClinVar or OMIM.

**Changes made during Stage 3** (all on 2026-10-18, each tested):
1. **References from the XML.** Reference lists are now read from the JATS XML, because some papers' Markdown flattens nested reference lists into one paragraph.
2. **Policy v2: one-to-one matching.** Policy v1 let a review row that cites a family join every relative with the same variant into one person. v2 merges a candidate only when each row is the other's unique best match in that paper, and never puts two rows from one paper into one identity.
3. **Notation and gene names.** Protein changes printed without "p." ("Leu227Ter") now match, and "A20/TNFAIP3" counts as TNFAIP3.
4. **Merge order.** Pairs where both rows are first-hand are joined first. A review that lists one girl twice, under two citations, no longer blocks the merge of the two primary reports.

**Hand check** (`analysis/poc/dedup_hand_check_poc-ha20-run-1.csv`, summary in `..._summary_...json`):
- **Who checked:** two Opus helpers read both papers behind each of the 56 policy-v2 merges. I checked the 2 merges added later, and the missed merge was confirmed from the paper text.
- **Result:** of 58 merged pairs, 52 are true, 2 false and 4 cannot tell. All 52 merges resting on a citation pointed to the right paper. The other 6 rested on a paper-level statement or on matching sex and onset.
- **False merge 1 (pair 41):** the citing paper cites a female patient to three papers at once, "(2, 12, 22)", and the merge picked the wrong one.
- **False merge 2 (pair 55):** the patient's citation also names two papers, "(15, 16)". The review's own text attributes another family's features to that variant.
- **Cannot tell:** three of the four involve Zhou 2016 (26642243), whose per-patient data are in a supplement we do not have.
- **Missed merge:** one (Li 2019 P1 and Li 2020 patient 7), now merged by change 4.

**Policy v3**, my call during development:
- An explicit citation counts only if it names one paper.
- Reference numbers are read only from bracketed groups, so a printed volume(issue) is no longer taken for reference numbers.
- Run-1 under v3: 635 individuals become **585 identities** through 52 merges (`reconcile_summary.json`). 78 candidate pairs are left as one-to-many and 223 as weak matches for audit.
- None of the 52 merges is a known false merge (49 true, 3 cannot tell). But v3 was changed after seeing this check, so its false-merge rate needs measuring on pairs it was not tuned on: the next run, or the six-disease study.
- v2 tables are kept as `merges_policy_v2.csv`.

**The Zhou 2016 ↔ Aeschlimann 2018 check from `POC_DESIGN.md` could not be run.** Aeschlimann 2018 (29317407) is paywalled and not in the full-text corpus. The hand check above covers every merge instead.

## 6. Other findings

- **Off-topic papers.** 11 of 85 papers report nobody with a TNFAIP3 variant: 26945335, 33101300, 33499153, 33619160, 34447369, 35268369, 35321008, 35753512, 36703223, 38373653 and 42169681. Three are clear screening false positives:
  - 35321008: anakinra in SJIA, CAPS and other diseases;
  - 36703223: Middle-East exome cohort;
  - 38373653: a DNASE2 case report.
  The other eight are reviews or cohorts that mention HA20 only at group level. Of the 74 papers flagged true, one (36211342) has no individual rows, because its per-patient table is in a supplement.
- **Supplements.** 19 helper notes say patient-level data sit in supplementary tables that were not fetched. This will limit completeness more than extraction accuracy will.
- **Converter gaps, still open:**
  - text of cells spanning several columns is not repeated across them, so two papers' merged header cells came through blank;
  - nested reference lists are flattened;
  - three papers have image-only tables.
  The first two will be fixed before the next run. The image-only tables would need OCR, which is out of scope.
- **Classification circularity.** One paper (40822695) gives ClinVar records as the basis of its pathogenicity calls. For classification concordance, the harness should flag variants whose stated class comes from ClinVar.
- **D-19 split** (`analysis/poc/seed_split_poc-ha20-run-1.json`):

  | Subset | Papers | Individuals | Distinct TNFAIP3 strings |
  |---|---|---|---|
  | All | 85 | 635 | 241 |
  | Without papers found only through ClinVar citations | 82 | 634 | 241 |
  | With no ClinVar-seeded paper at all | 68 | 486 | 186 |

- **Rule 8 (de novo).** All 22 TNFAIP3 variants marked de novo carry a parental-testing statement. A few helpers said "de novo" because the authors did, without described testing. The audit sample should check these.

## 7. Spend

| Reading (session usage, list-price estimate) | USD |
|---|---|
| Before Stage 3 | 45.93 |
| After run-1 (85 papers, 3 re-extractions) | 206.13 |
| After repeat, hand check and merge fixes | 240.36 |
| **Stage 3 total** | **194.43** |
| Approved under D-21 (one run plus 15-paper repeat, upper bound) | ~381 |

- **What the readings cover:** this session's own work as well as the helpers, so they are upper bounds for the helpers. Run-1 works out at about $1.88 per paper (160.20 / 85), under the smoke-test bound of $4.19.
- **How to compare:** these are estimates. Reconcile them against claude.ai Settings > Usage (D-17).
- **Pilot to date:** the whole session stands at $240.36, against the pilot ceiling of $1,000.

## 8. Decisions needed (recommendations first)

These change the extraction instructions. The pre-registration is not frozen, so they are revisions, not deviations. Each would be logged as a D-number once you decide.

1. **Cohort scope.** *Recommend:*
   - Extract every person with a TNFAIP3 variant or an HA20 diagnosis, plus relatives the paper describes in relation to them (tested or affected).
   - For other cohort members, record only their number.
   - This is the main cause of run-to-run disagreement.
2. **Labels for unnamed people.** *Recommend:* a fixed pattern built from the paper's own wording plus position, e.g. "Table 2 row 3" or "Discussion, ref [12] patient", so that two runs produce the same label.
3. **"–" cells in tables.** *Recommend:*
   - Record "excluded" only when the paper's legend or text defines the symbol as absent or negative, and quote that legend as a second span.
   - Otherwise keep "not reported", as rule 6 says now.
   - Helpers split on this. 35958611 had such a legend; 38034538 and 38183052 did not.
4. **Study inclusion or exclusion criteria as evidence.** *Recommend:* do not use them for phenotype rows. "Patients with autoimmune hepatitis were excluded" says nothing about one person's features. One paper (41179737) used it that way.
5. **Variant rows without a printed variant.** *Recommend:*
   - Keep these rows, since they record that the paper ties a TNFAIP3 variant to a person.
   - Leave them out of variant counts and concordance.
   - Reword check 3 to "every variant row with a printed variant has an original string".

Also proposed, needing your OK because they cost credits or touch new hosts:

6. **Next run.** A full re-run (`poc-ha20-run-2`) under the revised instructions and the converter fixes, with its own 15-paper repeat. About $160 + $30 at run-1's rate. Its merge output gets a fresh hand check, which also measures policy v3 independently. This replaces run-1 as the pilot's extraction of record.
7. **Supplementary files.** Fetch them for open-access papers (Europe PMC supplementary files), after a licensing check, to recover the per-patient tables that 19 papers keep there. No model cost to fetch; extraction cost rises with the added text.
8. **Then Stage 4 and Stage 5.**
   - Stage 4 (variant normalization through VariantValidator, HPO and Mondo binding, phenopackets) is mostly scripts.
   - Stage 5 (gatekeeper re-read of every value plus your 50-claim audit) needs an estimate after run-2. My working figure is about the cost of one extraction run.
