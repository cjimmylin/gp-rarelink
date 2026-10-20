# Six-disease run with `pipeline-v1.0`: findings (2026-10-20)

*Runs `pv1-ha20`, `pv1-ssadh`, `pv1-tangier`, `pv1-lad1`, `pv1-axd` and `pv1-danon`, approved by Jimmy Lin under D-37 (up to $1,200, including the 10% repeat). Every number below comes from a script: the per-disease table from `analysis/six_disease/run_summary.py` (output `analysis/six_disease/run_summary_2026-10-20.md`), the repeat from `analysis/six_disease/repeat_summary.py` (`repeat_agreement_2026-10-20.md`), the AxD catalogue from `pipeline/harness/catalogue_grossi2024.py`. Manifests: `runs/pv1-<d>/manifest.json`. No person has rated any claim from this run yet.*

## 1. Summary

- **All six diseases were extracted and audited by the gatekeeper with the frozen pipeline.** 350 papers; 2,948 individual rows; 2,233 variant rows. Every quoted span was found verbatim in its paper (span check: 0 problems in every disease).
- **Gatekeeper v4 judged 294 of 80,948 model claims unsupported (0.36%)** and 2,383 not fully supported (2.94%). By disease the unsupported share ranges from 0.20% (HA20) to 0.61% (Danon).
- **These are not error rates.** In the pilot the gatekeeper found far fewer problems than the human audit did (pre-registration §6.4). The pre-registered measure is the human audit of 250 claims (O1, §7.1), which has not started.
- **The most common cause of an unsupported claim** is a gene or variant field for a relative or a cited patient, quoted from a sentence about the proband. The second is a status resting on hedged wording ("suggested", "typically", "consistent with"); extraction v6 has no hedge rule, which was a known gap when the pipeline was frozen.
- **Unsupported claims cluster in a few papers.** In five of six diseases the three worst papers hold half or more of that disease's unsupported claims.
- **Run-to-run repeat (38 papers):** checklist statuses agree in 97–100% of cells. Variants agree on folded keys at 0.92–1.00 in four diseases and 0.83–0.86 in Tangier and Danon. In both of those, one paper caused the drop, and the two runs recorded the same variants in different notation (§6).
- **Spend:** +$768.87 by session readings for the whole run including the repeat ($780.63 to $1,549.50), against the $1,200 ceiling (`BUDGET.md`).

## 2. What ran

- **Pinned files:** `extract_v6.md`, `gatekeeper_v4.md`, `schema_<d>_v5.json` and `extraction_rules_v1.md`, instantiated per disease under D-38 (disease name, gene and checklist only). Each manifest records the sha256 of the files used and confirms they were unchanged at finish.
- **Helpers:** one Opus extraction helper per paper and one Opus gatekeeper helper per claim chunk (Claude Code route, D-20). Repair-only resumes filled empty spans in a handful of papers. Each repair was checked by a diff showing only the target cells changed. The manifests list them.
- **Order:** HA20, then SSADH, Tangier and LAD-I in parallel, then AxD, then Danon after the five-hour usage reset (Jimmy's choice).

## 3. Results by disease

| Disease | Papers | Individual rows | Variant rows | Model claims judged | Unsupported (95% CI) | Not fully supported (95% CI) | Top 3 papers' share of unsupported |
|---|---|---|---|---|---|---|---|
| HA20 | 85 | 811 | 620 | 23,129 | 46 (0.20%; 0.15–0.27%) | 446 (1.93%; 1.75–2.11%) | 0.37 |
| SSADH | 40 | 421 | 472 | 9,759 | 37 (0.38%; 0.27–0.52%) | 279 (2.86%; 2.54–3.21%) | 0.76 |
| Tangier | 31 | 235 | 82 | 4,830 | 15 (0.31%; 0.17–0.51%) | 217 (4.49%; 3.93–5.12%) | 0.60 |
| LAD-I | 42 | 508 | 411 | 10,864 | 47 (0.43%; 0.32–0.57%) | 377 (3.47%; 3.13–3.83%) | 0.66 |
| AxD | 69 | 463 | 343 | 14,403 | 39 (0.27%; 0.19–0.37%) | 512 (3.55%; 3.26–3.87%) | 0.51 |
| Danon | 83 | 510 | 305 | 17,963 | 110 (0.61%; 0.50–0.74%) | 552 (3.07%; 2.83–3.34%) | 0.55 |
| **All** | **350** | **2,948** | **2,233** | **80,948** | **294 (0.36%)** | **2,383 (2.94%)** | |

"Unsupported" counts unsupported and span-not-found verdicts; "not fully supported" adds partially supported. Intervals are exact. HA20 is a development disease and is reported separately in the study (D-18); it is in the table for completeness.

**Danon** has the highest unsupported share. Three papers hold 60 of its 110:
- 37215540 (35): variant and diagnosis fields for eight family carriers, when the paper names only the proband;
- 30413001 (15): "usually mild" applied to individuals;
- 41560058 (10): five exclusions resting on "typically showed no symptoms", and relatives' gene fields quoted from the proband's sentence.

## 4. Why claims were judged unsupported

**Who the quote is about** (unsupported claims only):

| Disease | this person | named group | other person | cohort in general | unclear |
|---|---|---|---|---|---|
| HA20 | 10 | 9 | 14 | 9 | 4 |
| SSADH | 10 | 0 | 27 | 0 | 0 |
| Tangier | 4 | 0 | 11 | 0 | 0 |
| LAD-I | 7 | 13 | 25 | 2 | 0 |
| AxD | 11 | 0 | 10 | 18 | 0 |
| Danon | 26 | 6 | 21 | 55 | 2 |

**Fields:** `variants.gene_symbol_as_stated` is the top field in five diseases (9 to 22 claims each), almost always a relative's or a cited patient's gene quoted from the proband's sentence. In Danon, `phenotypic_features.status` leads (25), mostly hedged or cohort-level wording.

**Patterns seen across the gatekeeper reports:**
1. **Relatives' variant fields from the proband's sentence.** Extraction v5's rule (variant fields only from this person) holds for the proband but slips for relatives the paper says carry "the same" variant.
2. **Hedged wording recorded as observed or excluded** ("suggested", "suspected", "consistent with", "typically"). Known gap, frozen on purpose (`NOTES_FOR_AGENTS.md`).
3. **Cohort-level statements applied to individuals** ("usually mild", "all patients", "neither").
4. **Ages at presentation recorded as onset or last evaluation.** These are mostly partial verdicts, common in every disease.
5. **"Proximal" muscle weakness** on the checklist when the paper says only "muscle weakness" (partial verdicts, Danon).

These are gatekeeper judgements. Whether a person agrees is what the audit will show.

## 5. Input problems found during the run

These come from helper reports and are not counted in any metric. They affect what the extraction could see.

- **Tables missing or garbled in conversion:** SSADH 14635103 (Table 2 scrambled; about 12 of 54 families extracted), 38499966; AxD 34046764 (Table 1 caption only); Danon 23571262, 30929317, 42366573 (transposed); Tangier 26713019 and 27011649 (tables published as images).
- **Supplements missing:** Danon 25228319 (Supplemental Tables 1–2), AxD 32126152 (Table S1), SSADH 38499966 (S1/S2).
- **Supplement text cut off at 60,000 characters** (`supplementary_to_text.py --max-file-chars`): LAD-I 33391282 Table S1 stops at P74, so P75–P127 have no clinical rows.
- **The same study twice in the SSADH corpus:** 37503297 (Research Square preprint) and 37962671 (the journal version, whose open copy is the same preprint text). Their patients appear twice unless the cross-paper merge joins them.
- **Papers that contradict themselves** (table vs text, abstract vs body): about 30 papers, listed for the human audit and adjudication in the run notes. Examples: LAD-I 36185095 (c.920C>T vs c.920T>C), Danon 42382315 (DCM vs end-stage HCM for P3), SSADH 37503297/37962671 (G176R vs G176E).

## 6. 10% run-to-run repeat

The pre-registration's run-to-run stability check ("re-extract a random 10% of papers and measure agreement, if budget allows"). Each disease's sample is ceil(10%) of its papers, drawn by script (seed 20261020) from papers with at least one individual row. That is 38 papers (`runs/pv1-<d>-repeat/selection.json`), re-extracted with the same pinned files. The gatekeeper was not run on the repeat.

| Disease | Papers | Same individual count | Label Jaccard | Variant (strings) | Variant (keys) | Checklist agreement (cells) | Features (label-free) |
|---|---|---|---|---|---|---|---|
| HA20 | 9 | 7 | 0.69 | 0.67 | 0.94 | 0.996 (1,300) | 0.71 |
| SSADH | 4 | 4 | 1.00 | 1.00 | 1.00 | 1.000 (160) | 0.43 |
| Tangier | 4 | 3 | 0.63 | 0.86 | 0.83 | 0.970 (200) | 0.57 |
| LAD-I | 5 | 3 | 0.88 | 0.55 | 0.92 | 0.998 (440) | 0.64 |
| AxD | 7 | 7 | 0.83 | 0.95 | 1.00 | 0.997 (1,340) | 0.69 |
| Danon | 9 | 7 | 0.87 | 0.65 | 0.86 | 0.996 (680) | 0.59 |

- **Checklist statuses are stable:** 97–100% of cells agree in every disease.
- **Variants agree on folded keys in four diseases** (0.92–1.00). They fall below the pilot's 0.9 guide in Tangier (0.83) and Danon (0.86). In each case one paper is responsible, and both runs recorded the same variants in different notation:
  - Danon 20173215: Case-3's deletion is quoted as "genetic deletion of exons-4–10" in one run and "deletion of exons-4–10" in the other. Exon-level deletions have no folded key, so the strings are compared.
  - Tangier 38538338: one run copied the paper's full-width asterisk ("＊") into the protein field, the other a plain "*".
- **Variant strings agree less than keys** (0.55–1.00). The causes are notation and which sentence was quoted, as in the pilot.
- **Features agree least** (0.43–0.71 label-free). The two runs word features differently and quote them from different places. This is the measure most sensitive to wording, and the pilot saw the same.
- **Individual counts differ in 9 of 38 papers.** The causes are scope calls on relatives and on patients cited from earlier reports, the same issue the pilot found in cohort papers.
- **Span check on the repeat:** 0 problems in four diseases. In two papers (LAD-I 24995649, 122 cells; AxD 40350261, 45 cells) the label spans in child tables were left empty. These are bookkeeping fields the agreement measures don't use, so they were not repaired.
- **Cost:** helper tokens of 6.48 weighted M, about $39 at the HA20 rate (`analysis/cost/helper_tokens.py`).

## 7. AxD completeness catalogue (D-39)

The pre-extraction check dropped Grossi 2024 (PMID 39420046) because Europe PMC answered HTTP 500 for its supplement. The supplement came through after `pv1-axd` finished. Under D-39 (Jimmy, "Use it, log deviation"), `pipeline/harness/catalogue_grossi2024.py` transcribed Supplementary Table 2 on the harness side, outside the repository:
- 553 rows, 550 with a protein change, a cDNA change and a reference PMID;
- 180 distinct protein changes from 187 references;
- **suitable** under the registered check (`catalogue_check.judge`).
- One caveat: `judge()` picked the column "REF" (the reference allele) as its source column, because the header matches "ref". With the intended "Reference (PMID)" column the share of rows with both is 0.995, so the verdict holds either way. The rule itself was left as registered.

Nothing was appended to the paper text `pv1-axd` read. AxD therefore reports completeness under §7.2.7, with this note beside the figure.

## 8. Cost

| Part | Session reading | Helper-token estimate |
|---|---|---|
| HA20 | about +$204 | — |
| SSADH, Tangier, LAD-I (overlapping) | +$220.61 together | $95 + $52 + $87 |
| AxD | +$129.20 | $131 |
| Danon and the 10% repeat | +$210.12 ($1,339.38 to $1,549.50; the Danon-only reading of +$111.99 had lagged) | $167 + $39 |
| **Six-disease run including the repeat** | **+$768.87 ($780.63 to $1,549.50)** | **about $764** |

That leaves $431 under the $1,200 ceiling by the session reading. All figures and their caveats are in `BUDGET.md`.

## 9. What comes next

1. **Stage 4 for the five new diseases** (normalization, HPO and Mondo binding, phenopackets). The scripts still assume HA20: the TNFAIP3 MANE transcript, the HA20 checklist-to-HPO map and the HA20 Mondo rule. They need per-disease settings, as D-38 gave the extraction. Needs Jimmy's decision (§10).
2. **Draw the 250-claim audit sample** (§7.1). It is drawn by script with a recorded seed from the final post-gatekeeper records, before anyone looks at concordance. So it waits on step 1.
3. **Rating page for the panel.** Jimmy sends it; Claude contacts no one.
4. **Concordance (O2)** after the draw.

## 10. Decisions for Jimmy

- **Stage 4 per disease (proposed D-40).** Make normalization, binding and phenopacket building take per-disease settings:
  - gene and MANE transcript, read from VariantValidator;
  - a checklist-to-HPO map per disease, built like HA20's and flagged for review;
  - a Mondo term per disease.
  
  This is code around the pinned files, not the pinned files themselves. It follows the same pattern as D-38. Recommendation: approve. The model-assisted HPO binding is about $28 (D-37 estimate), within the ceiling.
- **The SSADH duplicate study.** Recommendation: keep both papers (both passed screening) and make sure the cross-paper merge joins their patients, with the merge evidence recorded. Report it.
- **The 60,000-character supplement cap.** Recommendation: leave `pv1-lad1` as run (the pipeline is frozen) and report the truncated table as an input limit.
