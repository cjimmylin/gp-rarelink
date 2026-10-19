# Pilot Stage 3b: run-2 under instructions v3, repeat and merge hand check (A20 haploinsufficiency)

*2026-10-19. Branch `claude/gracious-pascal-j7krug`. Approved by Jimmy under D-22. Route D-20: Claude Code helper agents, Opus, one per paper. HA20 is a development disease (D-18), so none of this is a headline result for the six-disease study.*

Every number below comes from a script in the repo, and the output file is named next to it. Statements about individual papers come from the extraction files and the helpers' notes; those papers are named.

## 1. Summary

- **Run-2 replaces run-1 as the pilot's extraction of record (D-22).** It covered all 85 full-text papers under `extract_v3.md` and `schema_ha20_v3.json`, with the converter fixes and the supplementary files.
  - **Quotes:** all 64,999 quoted values were found verbatim, with 0 problems (`data/extracted/ha20/poc-ha20-run-2/span_check.json`).
  - **People and variants:** 799 individuals. 597 have a TNFAIP3 variant row. Of the 601 TNFAIP3 variant rows, 546 print the variant, giving 308 distinct variant strings (`analysis/poc/extraction_counts_poc-ha20-run-2.json`).
  - **Run-1 for comparison:** 635 individuals, 403 TNFAIP3 variant rows and 241 distinct strings.
- **The supplementary files brought the gain.** In the 21 papers that had supplementary text appended:
  - individuals rose from 151 to 341;
  - run-2 found 100 TNFAIP3 variant keys that run-1 did not, and lost 7.

  In the other 64 papers, the tighter scope rule lowered individuals from 484 to 458, and variants barely changed: 200 keys in common, 6 lost, 2 new (`analysis/poc/compare_runs_poc-ha20-run-1_vs_poc-ha20-run-2.json`).
- **The repeat now meets the stability threshold.** I ran 15 random papers again (seed 20261019) and compared them with run-2. Variant agreement was 0.944 on exact strings and 0.988 on normalized keys, against the 0.9 threshold. Run-1's repeat gave 0.547 and 0.702. Checklist answers agreed in 99.5% of 3,600 cells, and individual labels in common rose from 0.320 to 0.909 (§5).
- **The merge target is still not met.** Three helpers hand-checked all 93 merges made under policy v3, which was not tuned on these pairs. Result: 84 true, **6 false**, 3 cannot tell.
  - All 6 false merges rested only on "same variant, same sex, onset within a year".
  - Every merge resting on a citation was right.
  - Without that sex-and-onset route, the same data give 50 merges, all already checked: 47 true, 3 cannot tell, 0 false (§6).
- **Spend:** the session usage reading rose by $220.39 since the end of Stage 3, from $240.36 to $460.75. The D-22 estimate was about $190, and the stop-and-ask line was $300. Pilot total: $460.75 against the $1,000 ceiling (§8).
- **Decisions for you are in §9.** My recommendation:
  - adopt merge policy v4 (no merging on sex and onset alone);
  - settle six small instruction rules as v4;
  - don't do a run-3; check v4 on a 10-paper mini-run (about $25);
  - then go to Stage 4, and Stage 5 at about the cost of one run.

## 2. What ran

| | Run-2 (`poc-ha20-run-2`) | Repeat (`poc-ha20-run-2-repeat`) |
|---|---|---|
| Papers | all 85 full-text papers | 15, drawn at random from the 78 run-2 papers with individual rows (`runs/poc-ha20-run-2-repeat/selection.json`) |
| Helpers | one Opus helper per paper, each with a private scratch directory | same |
| Instructions | `extract_v3.md`, `schema_ha20_v3.json`, `extraction_rules_v1.md` (hashes in `runs/*/manifest.json`) | identical |
| Inputs | Markdown after the converter fixes (repeated colspan text, nested reference lists), with supplementary text appended for 21 papers; hashes in `runs/poc-ha20-run-2/markdown_sha256.csv` | the same Markdown |
| Usage reading | 252.27 → 418.07 | 418.07 → 460.75 (includes the three hand-check helpers) |

**Repair during the run.** In one paper (35958611), all 72 checklist answers marked observed or excluded had no quote. The same helper was asked to add quotes only. A script confirmed that every value and every top-level field is identical before and after, and that only those 72 quotes changed (commit message of the repair).

**Fix made after the run, harness side.**
- **The problem.** Text converted from supplementary Word files prints ">" as "&gt;", for example "c.259C&gt;T". That broke variant keys in the merge script, which read it as "c.259c&gt".
- **The fix.** The key functions in `reconcile.py`, the distinct-variant count and the agreement script now decode entities first. Quotes are untouched and still match the Markdown. A test covers it.

**Run-1 is kept** for comparison. Its Markdown snapshot sits in the local `fulltext_md_run1/` (`runs/poc-ha20-run-1/markdown_sha256.csv`), and its spans still verify against it.

## 3. Stage 3 checks (`POC_DESIGN.md`)

| Check | Run-2 |
|---|---|
| 1. Counts | 85 processed, 0 failed. 7 papers report nobody with a TNFAIP3 variant (run-1: 11); list in §7. 799 individuals: 491 described first-hand, 308 from tables or summaries of earlier reports. Phenotypic features: 3,617 observed, 836 excluded; 240 rest on a group statement (run-1: 435). Checklist: 1,682 observed, 229 excluded, 14,069 not reported. |
| 2. Span check ≥ 98% | **Met:** 64,999 of 64,999 found verbatim. Repeat: every quote verbatim, but 22 provenance flags in one paper (36703223), all the same made-up label "unnamed person 1" given without a quote. No value failed verification. |
| 3. Every variant row with a printed variant has an original string (reworded under D-22) | **Met.** 61 variant rows print no variant and are kept out of variant counts: 55 TNFAIP3, 6 other genes (`analysis/poc/rule_usage_poc-ha20-run-2.json`). |
| 4. Checklist complete for every individual | **Met:** 0 individuals with missing checklist rows. |
| 5. Run-to-run agreement ≥ 0.9 | **Met:** 0.944 on strings, 0.988 on keys (§5). |
| 6. Merge hand check, 0 false merges | **Not met:** 6 false of 93 under policy v3 (§6). |

## 4. What the v3 changes did (run-1 vs run-2)

Source: `analysis/poc/compare_runs_poc-ha20-run-1_vs_poc-ha20-run-2.json`, unless another file is named.

**Supplementary files** (D-22 item 7; `data/literature/ha20/supplementary/README.md`).
- **Coverage:** 59 files were kept for 30 papers, and the text of 36 files was appended to 21 papers.
- **Largest gains:**
  - 33101300: 0 → 89 individuals, a review whose per-patient table is in the supplement;
  - 40574834: 25 → 62, a national survey;
  - 39167656: 4 → 34;
  - 35155270: 4 → 31;
  - 36211342: 0 → 9.
- **Variants:** papers with supplementary text gained 100 TNFAIP3 variant keys and lost 7.

**Scope rule** (D-22 item 1).
- **Effect:** papers without supplements went from 484 to 458 individuals.
- **Biggest change:** 33971891 went from 23 to 3. Run-1 had extracted everyone in that cohort; run-2 extracted only the TNFAIP3 carriers.
- **Other-gene variant rows** fell from 57 to 22.

**Paper flags.**
- **Four papers changed from false to true:** 33101300, 35268369, 36703223 and 42169681.
- **Why:**
  - 33101300 and 36703223 gained per-patient rows from their supplements;
  - 35268369 and 42169681 each describe one patient in a single sentence, which v3 counts as individual-level detail.

**Table symbols and study criteria** (D-22 items 3 and 4). Group-statement exclusions fell from 326 to 151 in phenotypic features and from 129 to 43 in the checklist (`analysis/poc/rule_usage_poc-ha20-run-{1,2}.json`). Helpers left undefined "–" cells as not reported and quoted the legend where one existed. For example, 40859316 quotes "“ − ”means “Negative”" as a second span.

**D-19 split** (`analysis/poc/seed_split_poc-ha20-run-2.json`):

| Subset | Papers | Individuals | TNFAIP3 variant rows | Distinct TNFAIP3 strings |
|---|---|---|---|---|
| All | 85 | 799 | 601 | 308 |
| Without papers found only through ClinVar citations | 82 | 797 | 599 | 307 |
| With no ClinVar-seeded paper at all | 68 | 636 | 476 | 260 |

## 5. Run-to-run agreement (15 papers)

Source: `analysis/poc/run_agreement_poc-ha20-run-2_vs_poc-ha20-run-2-repeat.json`.

| Measure | Run-2 vs repeat | Run-1 vs repeat |
|---|---|---|
| Variant strings, Jaccard (`POC_DESIGN.md` measure) | **0.944** | 0.547 |
| Variants on normalized cDNA/protein keys | **0.988** | 0.702 |
| Checklist cells with the same status (only where both runs used the same label) | 0.995 (3,600 cells) | 0.987 (980 cells) |
| Papers with the same number of individuals | 13 / 15 | 12 / 15 |
| Individual labels in common | 0.909 | 0.320 |
| (individual, HPO candidate) pairs (`POC_DESIGN.md` measure) | 0.750 | 0.421 |
| Feature text and status, ignoring labels | 0.606 | — |

**The two papers where the counts differ:**
- **41929919 (5 vs 3).** Run-2 included two earlier-published patients that the Discussion mentions briefly ("ref (12) patient", "ref (7) patient"); the repeat did not. This is a scope question about literature patients (§9, item 5).
- **37342083 (33 vs 35).** Both runs labelled the literature patients "Table 2 column k", but the repeat made more rows for relatives given only as a group ("sisters", "three other family members").

**Labels still drift in one way.**
- **The case:** for 36064566, both runs found the same nine people. Run-2 called the literature rows "Table 3 row 1" and a parent "mother of Patient two"; the repeat used the table's number column ("1") and "parent of Patient two", because the paper says only "parents".
- **The fix:** a numbering-column rule and a relation-word rule would remove this (§9, item 4).

**Free-text features still differ in wording** (0.61), for example "Fever" against "recurrent fever". HPO terms are bound in Stage 4, and that should be compared again there.

## 6. Merging the same patient across papers

**Hand check** (`analysis/poc/dedup_hand_check_poc-ha20-run-2.csv`, summary in `..._summary_poc-ha20-run-2.json`):
- **How it ran:** three Opus helpers checked all 93 merges made by policy v3. Policy v3 was set during Stage 3 and not changed since, so this is the independent measure that the Stage 3 report called for.
- **Result:** 84 true, 6 false, 3 cannot tell. The 0-false-merge target is not met.

| Route the script used | True | False | Cannot tell |
|---|---|---|---|
| Explicit citation (the row cites one paper, which resolves to the other PMID) | 42 | 0 | 2 |
| Paper-level prior-report citation | 5 | 0 | 1 |
| Same variant, same sex, onset within a year | 37 | **6** | 0 |

**The six false merges** make four distinct wrong joins, because two people were each wrongly joined twice:

| Pair | Wrong join | What the papers say |
|---|---|---|
| 8 and 33 | the Shigemura 2016 patient (27175295 patient 1; 33101300 row 1) ↔ 40574834 P41 | 40574834 ties Shigemura 2016 to a different family (F5, P13) |
| 22 and 47 | Li 2019's Chinese patient (31299923 P1; 33101300 row 61) ↔ 40574834 P39 | P39 is Japanese and cited to Imai 2020 |
| 49 | 33101300 row 80 ↔ 40859316 Patient 3 | p.R45* in two different families; Patient 3 is de novo |
| 76 | 36211342 Patient 5 ↔ 39845949 case 12 | two relatives in one family sharing c.2209delC |

- **Missed evidence.** According to the hand-check helpers, four of the six would have been blocked if 40574834's per-patient "reference" column had gone into `source_reference_in_review`. The extraction helper put those references in its method note instead.
- **Cannot tell (3).** Two are rows standing for the whole Zhou 2016 Family 5. The third is a review row that mixes two members of one family.

**Sensitivity analysis: no merging on sex and onset alone** (`reconcile.py --no-sex-onset-merges`; outputs `*_without_sex_onset` next to the v3 files):
- **Merges:** 50 instead of 93, all already hand-checked: 47 true, 3 cannot tell, 0 false.
- **Distinct people:** 749 instead of 719. Some of the 30 extra are the same patient counted twice, since 37 of the dropped merges were true.
- **Caveat:** this option was chosen after seeing the check, so its 0 false merges is not an independent estimate. The next measure is the six-disease study.

## 7. Other findings

**Papers flagged false in run-2** (7): 26945335, 33499153, 33619160, 34447369, 35321008, 35753512 and 38373653. They are reviews without patient-level data or off-topic papers. For example, 38373653 is a DNASE2 case report.

**Rules the helpers applied unevenly** (`analysis/poc/rule_usage_poc-ha20-run-2.json`; papers named from the extraction files):
- **Inheritance from a carrier parent.**
  - *Recorded as inherited from the carrier parent:* 30526650, 35154120, 40071725 and 41905891 record "inherited maternal" or "inherited paternal" when the paper only shows that a parent carries the same variant.
  - *Recorded as not reported:* 27175295, 30402268, 31175876, 32719680, 33549127, 35958611 and 37342083 leave the same situation "not reported", because the paper never says "inherited".
  - 26 TNFAIP3 rows carry an inherited value in total.
- **Zero counts in group tables.**
  - 37848905 marked six features excluded for both HA20 patients because the HA20 column of a count table showed 0.
  - 42682521 declined to do the same with a 0 count.
  - The rule says counts without names exclude no one, but it does not mention a 0 count.
- **Labels the rules don't cover:**
  - patients as table columns: "Table 2 column k" (37342083, 33446651; both runs agreed on it);
  - table numbering columns: "Table 3 row 1" vs "1";
  - the same pedigree label in two families: "IV:1 (Family 2)" (35958611);
  - role words used as labels: "patient" vs "proband" (29682366).
- **Variant rows without content.**
  - Other-gene variants named but never described: 42572791 (PIK3R1, HBB, SERPINA1, VPS37A) and 32719680 (STRA8, UEVLD).
  - A common TNFAIP3 SNP the authors dismiss: 33446651, c.305A>G.
- **Mosaic carriers.**
  - 40574834 includes two mosaic carriers the authors excluded, plus their tested-negative relatives.
  - 39167656 lists somatic variants found in lymphoma.
  - v3 does not say whether these are in scope.

**Input gaps** (no model cost to fix; they change the Markdown, so they belong to the next run, not to run-2). Counts are from `analysis/poc/input_gaps_poc-ha20-run-2.json`:
- **Supplementary-file filter.**
  - *What was skipped:* the filter kept only files that mention TNFAIP3, A20 or HA20. It therefore skipped 42128528's per-patient table, which lists each patient's variant but never names the gene. It also skipped admission-lab tables for case reports (30526650, 33446651) and an immunophenotyping table (33971891).
  - *What was correctly dropped:* forms, checklists, gene lists, primers and figure-only PDFs.
  - *Proposed filter v2:* keep every file except administrative forms.
- **Entities.** Pandoc writes ">" as "&gt;" and emits complex tables as HTML. The merge keys now handle entities (§2); the converter should decode them too.
- **Bold.** The converter drops bold in table cells. 41929919's legend says bold marks abnormal values, and that information is lost.
- **Image-only tables.** 6 of 157 tables in 3 papers (32443356, 31384100, 35486341) are images in the XML, so there is no text to extract. This needs OCR, which is out of scope.
- **Missing supplements.** For 44 papers, the Europe PMC supplementary zip held no document files, and for 11 more it held nothing. The two zips I opened (26642243, Zhou 2016; 41179737) held only figure images, so those supplements are probably only at the publisher.
- **Blank cells in the source.** 34011076's literature table leaves follow-on cells blank in the XML itself, so 16 rows have no family, variant or reference. This is not a converter bug.

**Classification circularity.** 40822695 gives ClinVar RCV numbers as the basis of its pathogenicity calls. The concordance harness should flag it, as noted in Stage 3.

## 8. Spend

| Reading (session usage, list-price estimate) | USD |
|---|---|
| End of Stage 3 | 240.36 |
| Run-2 start (after D-22 work: converter fixes, supplementary files, instructions v3) | 252.27 |
| After run-2 (85 papers and one repair) | 418.07 |
| After the repeat (15 papers) and the merge hand check (three helpers) | 460.75 |
| **Stage 3b total** | **220.39** |
| D-22 estimate (run-2 ~$160 + repeat and hand check ~$30) | ~190 |

- **Against the estimate:** run-2 cost $165.80, about $1.95 per paper including orchestration, close to run-1's $1.88. The overrun on the estimate is mostly the supplementary text and the three hand-check helpers. Spend stayed under the $300 stop-and-ask line.
- **What the readings cover:** this session's own work as well as the helpers, so they are upper bounds for the helpers. Reconcile against claude.ai Settings > Usage (D-17).
- **Pilot to date:** $460.75 against the $1,000 ceiling (hard stop $1,500).
- **Weekly limit:** the session metadata shows the account at "allowed_warning" on its seven-day usage limit. Further large runs could be slowed until it resets.

## 9. Decisions needed (recommendations first)

The pre-registration is not frozen, so these are revisions. Each would get a D-number once you decide; the next free number is D-23.

1. **Merge policy v4.** *Recommend:*
   - stop merging on "same variant, same sex, onset within a year" alone, and list those pairs for audit instead;
   - also tell helpers to put a per-patient reference column into `source_reference_in_review`.

   On run-2 this gives 50 merges with no known false merge, at the cost of some patients counted twice (749 vs 719 identities). Under-merging inflates patient counts, while a false merge hides a distinct patient, so for gap-finding the second error is worse.
2. **Inheritance from a carrier parent.** *Recommend:* allow "inherited maternal" or "inherited paternal" when the paper states that the named parent carries the same variant, with that statement quoted. Otherwise leave it "not reported". "De novo" still needs stated parental testing (rule 8). Helpers split on this (§7).
3. **Zero counts in group tables.** *Recommend:* a 0 in a count table excludes no one, like any count without names. Text that names the group ("none of the patients had uveitis") still excludes.
4. **Labels.** *Recommend four additions:*
   - patients as table columns become "Table n column k";
   - a table's patient-numbering column becomes "Table n #k", whatever the column is called;
   - the same label in two families becomes "<label> (Family n)";
   - a relative the paper names only as a parent or sibling, without sex, becomes "parent of X" or "sibling of X", never a guessed "mother" or "brother".
5. **Literature patients mentioned in passing.** *Recommend:* in scope only when the paper gives at least one individual-level fact about that person beyond the diagnosis (sex, age, variant or a feature).
6. **Variant rows.** *Recommend:*
   - no rows for other-gene variants the paper names but does not describe;
   - no rows for common variants the authors dismiss as non-causal;
   - germline mosaic carriers are in scope, with zygosity "mosaic";
   - variants found only in tumour tissue are not.
7. **Input fixes for the next run** (no model cost): supplementary filter v2, entity decoding and bold in the converter. These change the Markdown, so I would not patch run-2. They go into the pipeline that gets frozen.
8. **No run-3.** *Recommend:*
   - **Extraction of record:** run-2, merged under policy v4.
   - **Check v4 first:** check items 2–7 on a 10-paper mini-run with its own spot comparison against run-2, about $25, before the six-disease extraction.
   - **Why no full re-run:** the run-2 repeat already meets the stability threshold, and the v4 items are small clarifications.
9. **Then Stage 4 and Stage 5.**
   - **Stage 4** (VariantValidator normalization, HPO and Mondo binding, phenopackets) is mostly scripts, and the network now allows VariantValidator.
   - **Stage 5** is the gatekeeper re-read of all 64,999 values against their quotes, plus your 50-claim audit. I estimate it at about the cost of one extraction run, roughly $170, since each helper re-reads one paper and its extraction.
