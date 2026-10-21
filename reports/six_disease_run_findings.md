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

## 9. Stage 4: final records (D-40)

Jimmy approved per-disease Stage 4 settings (D-40) and keeping both SSADH papers with their patients merged (2026-10-20). The table is generated by `analysis/six_disease/stage4_summary.py` (`stage4_summary_2026-10-20.md`).

| Disease | Rows → identities (merges) | Identities with target-gene variant | cDNA descriptions normalized | Phenotype rows bound to HPO | Phenopackets (with interpretation) | Observed / excluded terms | Schema-valid, errors |
|---|---|---|---|---|---|---|---|
| HA20 | 811 → 769 (42) | 558 | 96.7% | 91.6% of 5,079 | 769 (499) | 3,678 / 1,018 | 769, 0 |
| SSADH | 421 → 363 (58) | 243 | 86.5% | 89.8% of 1,683 | 363 (174) | 1,249 / 299 | 363, 0 |
| Tangier | 235 → 235 (0) | 65 | 90.0% | 90.7% of 1,051 | 235 (53) | 745 / 219 | 235, 0 |
| LAD-I | 508 → 508 (0) | 328 | 86.5% | 84.3% of 1,862 | 508 (299) | 1,264 / 299 | 508, 0 |
| AxD | 463 → 456 (7) | 318 | 78.8% | 91.3% of 3,316 | 456 (255) | 2,441 / 529 | 456, 0 |
| Danon | 510 → 505 (5) | 281 | 89.4% | 92.8% of 4,558 | 505 (212) | 3,302 / 1,007 | 505, 0 |

- **Settings per disease** (`configs/stage4/<d>.json`, written by `pipeline/extract/stage4_config.py`):
  - the gene's HGNC ID and MANE Select transcript, read from VariantValidator (TNFAIP3's matches the pilot);
  - the Mondo disease term, found by its exact name in the pinned release;
  - a label rule;
  - a checklist-to-HPO map.
- **Checklist maps:** drafted by five Opus helpers with an HPO lookup tool, then reviewed. Two changes were made in review: sleep apnea was removed from AxD's autonomic exclusions, and the SSADH EEG item got its observed term. All five maps are flagged for review by Jimmy or the panel.
- **Gene names:** the matcher now also accepts other spellings the papers use. "LAMP-2" covers 32 Danon variant rows, "ITGβ2" or "ITGß2" 127 LAD-I rows, "CD18" 21 LAD-I rows, and "SSADH" 14 SSADH rows.
- **Merges:** SSADH's 58 merges are all the duplicate study (37503297 and 37962671). They use a merge route that applies only to paper pairs listed, with evidence, in `configs/duplicate_publications.csv`. Tangier and LAD-I have no citation merges.
- **HPO binding:** a first pass by script, then 22 helper batches for 4,869 distinct unbound phrases (`hpo_binding_v1.md`). Every answer was checked against the pinned HPO release.
- **Normalization:** AxD is lowest at 78.8%. Its papers often print cDNA without "c." (e.g. "739T→C"), and 22 descriptions were unresolvable.
- **The extraction guard holds:** `pipeline/extract` contains no reference-database identifiers. The guard's test rejected a first draft that looked up Mondo by an OMIM number; the Mondo lookup now uses the term's name.

## 10. The 250-claim audit (O1)

- **Drawn** by `analysis/six_disease/make_audit_sample.py`, seed 40250, before any concordance on these runs. It records the seed, pool sizes, allocation, the inputs' sha256 and the commit (`adjudication/o1_audit/sample_key.json`).
- **Pool:** the 78,564 model claims gatekeeper v4 judged supported, which are the values that survive into the records.
- **Allocation by disease:** HA20 72, SSADH 30, Tangier 15, LAD-I 33, AxD 44, Danon 56.
- **Rating pages:** two separate blinded pages, one per rater, each with its own store. They show the claim, its quote and where the quote sits in the paper, never the gatekeeper's verdict. Labels follow §7.1: supported, unsupported, quote not in paper, and can't verify (counted as unsupported, also reported without).
  - Rater A: https://claude.ai/artifact/Jvk4nxzG79u9AchAXvwPe4
  - Rater B: https://claude.ai/artifact/1VVgQNgSpyzDrsApErz8YU
- **Before the panel can rate:** Jimmy shares each page with one panel member, at a level that lets them use the page (not view-only), so their ratings save. Claude contacts no one.
- **After both have rated:** a tie-breaker page for the third member shows only the disagreements. Then O1 is scored under rule C (pass at 4 or fewer unsupported of 250), with the exact interval and gatekeeper accuracy against the human labels (§7.1 (b)).

## 11. Concordance with ClinVar (O2, §7.2)

Run on 2026-10-20 against the ClinVar snapshot of 2026-10-19 (release 2026-10-12), after the O1 sample was drawn. Generated by `pipeline/harness/concordance_o2.py`; files in `analysis/six_disease/o2/`. OMIM is not checked (no access, D-12). No pass/fail threshold (D-03).

*Generated by `pipeline/harness/concordance_o2.py` (pre-registration §7.2). Estimates with Wilson 95% intervals; no pass/fail threshold (D-03). OMIM not checked (D-12). Overlap is not precision; precision comes from the O1 audit.*

| Disease | Gene (7.2.1) | HGVS recall, tier 1 | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement | Condition names disease | HPO annotation recall | Terms in ≥2 people matching | PMIDs ClinVar cites |
|---|---|---|---|---|---|---|---|---|---|
| ha20 | 99.8% (558/559; 99.0–100.0) | 26.9% (21/78; 18.3–37.7) | 26.9% (21/78; 18.3–37.7) | 37.9% (39/103; 29.1–47.5) | 82.8% (24/29; 65.5–92.4) | 47.4% (27/57; 35.0–60.1) | 92.9% (13/14; 68.5–98.7) | 6.1% (19/309; 4.0–9.4) | 20.0% (17/85; 12.9–29.7) |
| ssadh | 100.0% (243/243; 98.4–100.0) | 10.1% (16/158; 6.3–15.8) | 14.6% (23/158; 9.9–20.9) | 87.2% (68/78; 78.0–92.9) | 91.8% (45/49; 80.8–96.8) | 98.8% (83/84; 93.6–99.8) | 94.1% (32/34; 80.9–98.4) | 40.0% (52/130; 32.0–48.6) | 45.0% (18/40; 30.7–60.2) |
| tangier | 98.5% (65/66; 91.9–99.7) | 16.7% (1/6; 3.0–56.4) | 50.0% (3/6; 18.8–81.2) | 56.2% (9/16; 33.2–76.9) | 80.0% (8/10; 49.0–94.3) | 37.5% (6/16; 18.5–61.4) | 70.8% (17/24; 50.8–85.1) | 15.3% (15/98; 9.5–23.7) | 16.1% (5/31; 7.1–32.6) |
| lad1 | 100.0% (328/328; 98.8–100.0) | 23.3% (14/60; 14.4–35.4) | 31.7% (19/60; 21.3–44.2) | 34.9% (45/129; 27.2–43.4) | 70.0% (7/10; 39.7–89.2) | 90.4% (47/52; 79.4–95.8) | 70.6% (12/17; 46.9–86.7) | 14.4% (17/118; 9.2–21.9) | 16.7% (7/42; 8.3–30.6) |
| axd | 99.7% (318/319; 98.2–99.9) | 27.5% (14/51; 17.1–40.9) | 66.7% (34/51; 53.0–78.0) | 73.1% (49/67; 61.5–82.3) | 58.6% (17/29; 40.7–74.5) | 85.6% (95/111; 77.9–90.9) | 84.2% (16/19; 62.4–94.5) | 13.5% (36/267; 9.9–18.1) | 39.1% (27/69; 28.5–50.9) |
| danon | 97.9% (281/287; 95.5–99.0) | 35.0% (7/20; 18.1–56.7) | 50.0% (10/20; 29.9–70.1) | 47.9% (35/73; 36.9–59.2) | 78.9% (15/19; 56.7–91.5) | 89.6% (43/48; 77.8–95.5) | 87.1% (27/31; 71.1–94.9) | 15.9% (40/251; 11.9–21.0) | 18.1% (15/83; 11.3–27.7) |

### Without ClinVar-cited papers (D-19)

| Disease | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement |
|---|---|---|---|
| ha20 | — | 33.3% (29/87; 24.3–43.8) | 85.7% (18/21; 65.4–95.0) |
| ssadh | — | 83.3% (40/48; 70.4–91.3) | 93.5% (29/31; 79.3–98.2) |
| tangier | — | 57.1% (8/14; 32.6–78.6) | 85.7% (6/7; 48.7–97.4) |
| lad1 | — | 40.0% (12/30; 24.6–57.7) | 62.5% (5/8; 30.6–86.3) |
| axd | — | 69.4% (34/49; 55.5–80.5) | 66.7% (14/21; 45.4–82.8) |
| danon | — | 41.5% (22/53; 29.3–54.9) | 80.0% (12/15; 54.8–93.0) |

**Reading the results:**
- **Gene (7.2.1)** is near ceiling, as expected for corpora built per disease.
- **HGVS recall (7.2.2) is low**: 10–35% at tier 1, 15–67% with protein-level matches. It counts every (paper, variant) pair ClinVar cites against what the run extracted from that paper.
  - The misses cluster in single papers. Zhou 2016 (HA20) holds 52 of HA20's 57 misses. It is the founding paper, which ClinVar cites for many variants it does not describe.
  - van de Vijver 2012 (LAD-I) holds 37 of 41. It is a mutation-update review, so its misses may be notation or normalization failures rather than scope.
  - In SSADH, Akaboshi 2003 (whose table was scrambled in conversion, §5) holds 68 of 135, and Brennenstuhl 2020 (variants tested in vitro, no patients) 53.
- **Triage:** every miss counts as discordant in the primary figure. The registered triage sample of 50 misses (seed 72650; `adjudication/o2_triage/sample.csv`) will sort them into the five §7.2.6 categories. It needs a panel member, or Jimmy.
- **Overlap** (the share of extracted variants found in ClinVar) is not precision. Gap variants are expected; precision comes from O1.
- **D-19:** recall cannot be computed without ClinVar-cited papers, since its reference pairs come from them. Overlap and classification agreement are given both ways.
- **HPO profile (7.2.4 b):** 71–94% of annotated terms are seen in at least one person. Only 6–40% of terms seen in 2 or more people match an annotated term. Annotations are known to be incomplete, so this is descriptive.

### Completeness against published catalogues (§7.2.7, 2026-10-21)

*Source: `analysis/six_disease/completeness_pv1-ha20.json` and `completeness_pv1-axd.json`, from `pipeline/harness/completeness.py` (generalized 2026-10-21; the pilot's output on `poc-ha20-run-2` is unchanged by the rewrite). Secondary and descriptive; no threshold. Only HA20 and AxD have a suitable catalogue (D-35); the other four report no figure, as registered.*

| Disease | Catalogue | Variants (patients) | Restricted recall, primary papers | Unrestricted recall, primary papers |
|---|---|---|---|---|
| ha20 | Chen 2020 Table S1 (D-30) | 32 (89) | 9 of 9 (100%; 70.1–100) | 29 of 32 (90.6%; 75.8–96.8) |
| axd | Grossi 2024 Suppl. Table 2 (D-39, added after extraction) | 183 (553) | 54 of 56 (96.4%; 87.9–99.0) | 91 of 169 (53.8%; 46.3–61.2) |

- **AxD, by level:** protein 52 of 56; cDNA 36 of 56. AxD papers often print cDNA without "c.", so the cDNA level finds fewer.
- **AxD, the two misses are notation, not absence:** "R270-A272del" (26478912) is extracted with a hyphen where the catalogue has p.Arg270_Ala272del, and the whole-gene deletion p.Met1_Met432del (36425948) is extracted as "deletion (exons 1–9)". The matcher was not changed after seeing this, so the figure stays 54 of 56.
- **AxD, not used:** the catalogue's genomic column. Of 47 distinct alleles whose cDNA VariantValidator also normalized, none match as printed: 30 are one position off and 16 are on the coding strand.
- **AxD, outside both denominators:** 14 variants (47 patients) with no PMID source, mostly "patient from internal database" and three Web of Science IDs.
- **Restricted denominators are small** because most catalogue source papers are not open (D-32): 9 of 32 variants for HA20, 56 of 183 for AxD.
- **Patients per source paper:** for AxD, the run has at least as many carriers as the catalogue in all 43 source papers it shares (107 catalogue patients, 253 run carriers; papers describe relatives and others the catalogue did not take). For HA20, two papers have fewer run carriers than catalogue patients: 30022980 (1 of 4) and 30526650 (2 of 3). They are candidates for the merge or scope check.

### O3 stage 1: gap-variant candidates (§7.3, 2026-10-21)

*Source: `adjudication/o3_gaps/summary.md` and `summary.json`, from `pipeline/harness/gap_candidates.py`. All candidates are pending adjudication.*

- **Definition, as registered:** tier-1 allele; absent from the 2026-10-19 ClinVar snapshot by GRCh38 allele; at least one variant row whose identifying values (gene, strings, cDNA, protein, transcript, coordinates, person label) gatekeeper v4 all judged supported. **OMIM is not checked (D-12)**, so these are ClinVar gaps only.
- **Count:** 215 candidates from 466 tier-1 alleles, of which 221 were absent from ClinVar. In 6 the rows all failed the gatekeeper (`failed_gatekeeper.csv`).
  - Per disease: HA20 64, SSADH 10, Tangier 7, LAD-I 82, AxD 17, Danon 35.
- **Spot check:** HA20's c.271A>T (p.Lys91Ter) and c.559C>T (p.Gln187Ter) have no GRCh38 record in the snapshot, while their neighbors (c.268–270, c.556) do. The gaps hold up for these two.
- **LAD-I needs care:**
  - 66 of its 82 candidates come only from papers ClinVar cites for *ITGB2*, and 34 only from reviews. Most come from van de Vijver 2012, a mutation update.
  - A variant cited but absent by allele may be a numbering or normalization slip rather than a true gap. The protein check flags 10 LAD-I candidates whose stated protein differs from the protein predicted from the cDNA.
- **Reclassification candidates (exploratory):** 53 supported tier-1 variants are in ClinVar only as VUS or conflicting. 15 meet the proposed "strong" rule (at least 2 papers or 3 deduplicated people).
- **Next:** the WS3 evidence dossiers (D-41) are built from `evidence_rows.jsonl` and the papers. That file holds no ClinVar or OMIM content.

### Memorization probe, Claude side (§7.4.3, exploratory; D-41; 2026-10-21)

*Source: `analysis/bias/memorization/scores_summary.md`, `scores.csv` and `tool_check.json`, from `make_probes.py` (seed 20261021), `check_transcripts.py` and `score_probes.py`. Scored against the pv1 full-text extraction, never against ClinVar or OMIM.*

- **Design:**
  - 180 papers, 30 per disease, split by first publication date against the helper model's documented cutoff (Claude Opus 5.5: training data and reliable knowledge cutoff Jun 2026, per the models overview read 2026-10-21);
  - strata: 10 papers after the cutoff (every one in the corpus), 51 recent (2024-07 to 2026-06), 119 older;
  - two black-box probes, written so the open-weight model can run the same files later (D-10): closed-book recall from PMID, title and year; and continuation of a 50-word passage opening;
  - every helper transcript was checked: each made only its allowed calls, Write of its answer and at most one Read of its own batch file.
- **Closed-book recall:**
  - "Specific" recall was claimed for 4 of 180 papers, all older, and in each case for phenotypes only, naming no variant;
  - 4 papers had a variant hit, all labelled guesses, including recurrent variants such as LAMP2 p.Arg293Ter. No stratum shows more.
- **Completion:**
  - mean word-level ROUGE-L F1 is 0.16 after the cutoff, 0.19 recent and 0.19 older; 5-gram share is under 0.015 in every stratum;
  - runs of 8 or more matching words occur in 3 older papers, and all three are formulaic ("approved by the institutional review board", "written informed consent was obtained from all patients", "recurrent life threatening bacterial and fungal infections");
  - one item was excluded after the first scoring run: the passage chosen for Tangier 33346003 was Elsevier's "Journal Pre-proof" notice, which the model reproduced word for word. That is publisher boilerplate, not the paper's text.
- **Reading:** neither probe shows the model recalling these papers' variants or their text. Two caveats:
  - only 10 papers postdate the cutoff, so the before/after comparison has little power;
  - the probes are black-box, so they can miss memorization that changes extraction without surfacing as recall.
  The exploratory question of whether audit and concordance results differ by memorization has nothing to split on here.
- **Cost:** 12 helpers, 0.89M weighted tokens, about $5 on the bias-arm line (D-41 ceiling $60).

### Exploratory analyses (§7.6, labeled exploratory; 2026-10-21)

**Genotype–phenotype maps with GPSEA.**
- *Source:* `analysis/exploratory/gpsea/results/` (`summary.json` and one CSV per analysis), from `gp_maps.py`. GPSEA 0.10.0 runs in its own uv project because it needs pandas < 3 and pipeline-v1.0 is locked to 3.0.6. HPO is pinned at 2026-09-01 (hp.json, sha256 prefix a7b3a012e7b4).
- *Annotation:* Ensembl VEP is not reachable here, so variant effects come from each phenopacket's own VariantValidator HGVS; no external call is made.
- *Method:* Fisher exact test with GPSEA's IfHpoFilter and Benjamini–Hochberg correction at 0.05. A feature that is not reported is not counted as excluded.
- *Zygosity is an analysis assumption here only; the records leave it unset when the paper does.* Rules and per-disease counts are in `summary.json`:
  - **Dominant:** heterozygous. Danon males are taken as hemizygous and females as heterozygous.
  - **Recessive:** two distinct unstated calls are taken as compound heterozygous; a lone unstated call is left out.
- *Who is included:* only individuals with a variant placed on GRCh38 and at least one phenotype. For example, 217 of HA20's 499 phenopackets with a variant.

| Disease | Analysis | Individuals | Terms tested | Significant (BH 0.05) |
|---|---|---|---|---|
| ha20 | truncating vs missense | 217 | 11 | 0 |
| axd | hotspot R79/R88/R239 vs other missense | 83 | 14 | 0 |
| danon | truncating vs missense | 130 | 9 | 2: arrhythmia 57/59 vs 4/7, ventricular arrhythmia 45/47 vs 3/6 (both p_BH 0.035) |
| danon | sex | 130 | 10 | 3: proximal muscle weakness, male 11/25 vs female 1/28; left ventricular hypertrophy 41/41 vs 25/33 (both p_BH 0.0046); hypertrophic cardiomyopathy 34/34 vs 19/24 (p_BH 0.031) |
| ssadh | biallelic, truncating vs other | 77 | 9 | 0 |
| tangier | biallelic, truncating vs other | 16 | 0 | — |
| lad1 | biallelic, truncating vs other | 38 | 3 | 0 |

- **Danon sex difference:** the extracted cohort reproduces the published pattern, with males more often showing myopathy and hypertrophy. This is a reproduction check, not independent replication, because the papers overlap with the published series.
- **Danon truncating vs missense:** the missense group is small (6–9 people), so read it as a lead only.
- **Tangier and LAD-I:** too few placeable, phased genotypes to test.

**Tangier: share of ClinVar ABCA1 records matched in the literature.**
- *Source:* `analysis/exploratory/tangier_clinvar_share.json`, from `tangier_clinvar_share.py`, using O2's tier-1 and tier-2 matches.
- 16 of 2,006 single-gene GRCh38 ABCA1 records (0.8%), and 7 of the 85 P/LP records (8.2%), match variants extracted from the Tangier corpus.
- Of the 35 extracted Tangier variants, 19 are not in ClinVar.
- This is a lower bound: the corpus is 31 open-access papers (D-32), and most ABCA1 records come from testing unrelated to Tangier disease.

## 12. Cost to date

The six-disease run, the repeat and Stage 4 together come to +$832.70 by session reading ($780.63 to $1,613.33, at 22:25 UTC), against the $1,200 ceiling.
- **Stage 4 helpers** (checklist maps and HPO binding): 12.08 weighted M tokens, about $72. That is above the $28 the D-37 estimate gave for HPO binding: the binding helpers searched `hp.obo` many times per batch.

## 13. Next

*Model work done 2026-10-21 under D-41: completeness, gap candidates, evidence dossiers, the adjudication page, the memorization probe, bias-arm prep, exploratory maps and the open-weight agent loop (§11 and `reports/plan_next_work_2026-10-21.md`). What remains needs people:*

1. Jimmy shares the two rater pages with two panel members (D-11).
1a. Jimmy shares the adjudication page (https://claude.ai/artifact/UUWN2ULAGkYYNQj4zDy9ta) when the panel starts O3; read `adjudication/o3_gaps/helper_notes_2026-10-21.md` first.
1b. A person fills the four comparator sheets (`analysis/bias/comparator_sheets/README.md`) without looking at literature frequencies first.
1c. Jimmy opens the hosted account for the open-weight comparison (D-10).
2. Triage of the 50 sampled O2 misses (a panel member if one offers time, otherwise Jimmy, §7.2.6).
3. Optional: review the five checklist-to-HPO maps (`configs/checklist_hpo/`).
