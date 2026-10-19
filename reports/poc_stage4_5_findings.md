# Pilot Stages 4 and 5, and the instructions-v4 check (A20 haploinsufficiency)

*2026-10-19. Branch `claude/gracious-pascal-j7krug`. Approved by Jimmy under D-23 to D-25. Route D-20: Claude Code helper agents. HA20 is a development disease (D-18), so none of this is a headline result for the six-disease study.*

Every number below comes from a script in the repo; the output file is named next to it. Statements about single papers come from the extraction files and the helpers' notes, and those papers are named.

## 1. Summary

- **Instructions v4 behave as intended (D-24).** On the 10 papers picked for the changed rules, 13 of 13 rule checks moved the way the rule says (`analysis/poc/v4_check_poc-ha20-v4-check.json`). All 11,706 quoted values were found verbatim. As agreed, there is no run-3: run-2 stays the extraction of record.
- **Stage 4: the records convert, but normalization misses its target as worded.**
  - **Phenopackets:** 749, one per merged person, and **all 749 are schema-valid** (`validation_report.json`).
  - **HPO binding:** 88.5% of 4,453 feature rows are bound to a current term in the pinned HPO release (`binding_summary.json`).
  - **Variant normalization:** 128 of 277 distinct variant descriptions normalized or corrected (46.2%). Counting only the 138 that state a cDNA change, it is 92.8%. The Stage 4 check asks for 95% (`normalization_summary.json`). The rest are protein-only (99) or structural (40) descriptions, which cannot be normalized from the text, plus 10 that VariantValidator rejected. §4.1 has the detail; §8 has a proposed rewording.
- **Stage 5: the gatekeeper re-read 22,003 values and found 8 unsupported.**
  - The 22,003 are every run-2 value except bookkeeping fields. 9,848 are text copied from inside their own quote, so a script marks them supported; helpers judged the other 12,155.
  - **Result:** 21,690 supported, 305 partially supported, **8 unsupported**, 0 quotes not found (`gatekeeper_summary.json`).
  - **Shares:** unsupported 0.036% (exact 95% CI 0.016–0.072%); not fully supported, counting partials, 1.42% (1.27–1.59%).
  - **These are the gatekeeper's own reading.** The pre-registered measure is your 50-claim audit, which also calibrates the gatekeeper. It is still waiting for your ratings (§6).
- **The phenopackets were rebuilt** without any claim the gatekeeper did not call supported, as `POC_DESIGN.md` §3.9 requires. That left out 50 feature rows, 69 checklist rows, 10 ages, 15 onsets, 15 pathogenicity statements and 4 zygosity values. All 749 phenopackets remain valid.
- **The commonest gatekeeper flag is a labelling convention, not a reading error.** Normal findings are recorded as the feature with status "excluded" ("normal CRP" excluded). Helpers disagreed on how to judge that: most accepted it, about 40 flags call it partial, and one calls it unsupported. §5.3 proposes a fix for the frozen pipeline.
- **Spend:** the session reading rose from $463.50 to $580.31, so $116.81 covers the v4 check, the Stage 4 helpers and the gatekeeper together. You approved about $195 for these (~$170 + ~$25). Pilot total: $580.31 against the $1,000 ceiling (§7).
- **Needed from you:** ratings for the 50-claim audit and the 30 HPO bindings (§6), and two small decisions (§8).

## 2. What ran

| Step | What | Output |
|---|---|---|
| Merge policy v4 (D-23) | Merges on citations only; matches on sex and onset alone become weak matches listed for review. Tests added. | `data/extracted/ha20/poc-ha20-run-2/merges.csv` (v4), `merges_policy_v3.csv` kept for comparison |
| Input fixes (D-24) | Bold table cells kept; supplement filter v2 (only administrative files skipped); HTML tables to pipe tables; entities decoded | `pipeline/extract/corpus/`, `data/literature/ha20/supplementary/conversion.csv` |
| v4 check | 10 purposive papers under `extract_v4.md` and `schema_ha20_v4.json`, one Opus helper each | `data/extracted/ha20/poc-ha20-v4-check/`, `runs/poc-ha20-v4-check/` |
| Stage 4 | VariantValidator 4.0.1 normalization to MANE Select NM_001270508.2; HPO and Mondo binding against pinned releases (HP 2026-09-01, Mondo 2026-10-06), with four Sonnet helpers for phrases a script could not bind; GA4GH Phenopackets v2 | `variants_normalized.csv`, `hpo_bindings.csv`, `disease_bindings.csv`, `phenopackets/`, `validation_report.json` |
| Stage 5 | 97 chunks of claims, one Opus helper each, under `gatekeeper_v1.md`; claims judged against the run-2 Markdown snapshot | `gatekeeper/*.csv`, `gatekeeper.csv`, `gatekeeper_summary.json`, `runs/poc-ha20-run-2-gatekeeper/` |

**Interruption.** At about 02:50 UTC the account reached its five-hour usage limit and 10 gatekeeper helpers stopped. Seven had already written complete files; a script checked each one (every claim once, valid verdicts). The other three were resumed and finished. The session ran on overage (extra usage) from then on; the limit resets at 05:30 UTC.

## 3. Instructions v4 on 10 papers (D-24)

Each paper was chosen because one or more v4 rules apply to it. The table compares run-2 (instructions v3) with the v4 run on the same paper (`analysis/poc/v4_check.py`).

| Paper | Rule | Run-2 → v4 | As intended |
|---|---|---|---|
| 42128528 | Supplement filter v2 keeps the per-patient table | TNFAIP3 rows with a printed variant: 1 → 18 | yes |
| 30526650 | Inherited only when the paper says the parent carries the variant | "inherited maternal" ×2 → "not reported" ×2 | yes |
| 33549127 | Same rule, carrier parents named | 0 → 3 inherited values | yes |
| 37848905 | A 0 count in a group table excludes no one | group-statement exclusions: 26 → 12 | yes |
| 36064566 | Labels for numbered table rows; no guessing which parent | "Table n #k" labels: 0 → 2; guessed mother/father labels: 2 → 0 | yes, yes |
| 33446651 | Leave out a variant the authors call common and non-causal | rows for c.305A>G: 2 → 0; column labels kept (4 → 4) | yes, yes |
| 42572791 | Other genes only when described | other-gene variant rows: 4 → 0 | yes |
| 40574834 | Per-patient reference column; germline mosaic carriers | rows with a source reference: 2 → 42; mosaic rows: 4 → 4 | yes, yes |
| 35958611 | Repeated pedigree labels; carrier parents | "(Family n)" labels: 2 → 3; inherited values: 0 → 5 | yes, yes |
| 41929919 | Literature patients with one fact stay in scope | individuals: 5 → 5 (reported only) | — |

**Variant agreement with run-2 is low on these papers, and that is expected** (`analysis/poc/run_agreement_poc-ha20-run-2_vs_poc-ha20-v4-check.json`).
- **The scores:** variant agreement 0.32 on strings and 0.33 on keys. Checklist answers agree in 98.5% of 2,380 cells, and individual labels in 86%.
- **Why so low:** the papers were picked because v4 changes them, and three of them had their input changed by the D-24 fixes.
  - In 40574834, both runs give 58 TNFAIP3 rows. But run-2 copied protein forms ("p.W85GfsX"), while v4 copied cDNA forms ("c.252delC") from the supplementary table, which is readable now that HTML tables are converted. The keys cannot match without normalization.
  - In 42128528, the per-patient table is new input.
  - In 33446651 and 42572791, the rules removed rows on purpose.
- **What this measures:** this is a check of the rules, not a stability measure. Stability was measured on run-2's random repeat (0.944 on strings), which this does not replace.

## 4. Stage 4: normalization, binding, phenopackets

### 4.1 Variant normalization (VariantValidator 4.0.1, database vvdb_2025_3)

| Status | Distinct descriptions | Variant rows | Meaning |
|---|---|---|---|
| normalized | 102 | 196 | Accepted as given |
| corrected | 26 | 50 | Accepted after a correction VariantValidator reported (e.g. a wrong reference base) |
| protein_only | 99 | 236 | The paper gives only a protein change; no cDNA to normalize |
| not_normalized | 40 | 49 | No cDNA or protein description: copy-number changes, exon deletions, prose |
| unresolvable | 10 | 15 | Rejected by VariantValidator: 4 cite NM_006290.5, which its database does not hold; 2 cite Ensembl transcripts outside its RefSeq set; 3 have syntax errors in the paper's string (e.g. "c.436_437deTC"); 1 crosses an exon boundary |
| **Total** | **277** | **546** | |

- **Transcripts:** 76 descriptions named no transcript, so MANE Select was assumed. 24 named a transcript without a version, and the latest version from VariantValidator's gene-to-transcript list was used. Both are flagged per row.
- **Database fields:** only normalization fields are kept from VariantValidator responses. No ClinVar or other database annotation is stored (pre-registration §5.3).
- **The Stage 4 check is not met as worded.** It asks for 95% normalized or corrected; the result is 46.2% of all descriptions and 92.8% of those with a cDNA. Protein-only and structural descriptions cannot reach that status from the text, so the check as written cannot be met on this literature. The 10 unresolvable ones could be repaired:
  - the 4 NM_006290.5 and 2 Ensembl strings, by mapping to a transcript VariantValidator holds;
  - the 3 typos, by recording a corrected query next to the original string.

  Done together, that would give up to 137 of 138; the exon-boundary case needs a person to read it (§8, item 1).

### 4.2 HPO and Mondo binding

| Binding method (4,453 phenotypic feature rows) | Rows |
|---|---|
| Helper's HPO ID verified against the pinned release (exact ID) | 2,449 |
| Exact name or synonym match (label) | 657 |
| Obsolete ID replaced | 1 |
| ID current but name not matched (kept, flagged) | 24 |
| Model step, exact / close / broader | 60 / 461 / 288 |
| Broader term on an excluded row, dropped (it would overstate the exclusion) | 54 |
| No suitable term | 459 |
| **Bound** | **3,940 (88.5%)** |

- **The model step.** Four Sonnet helpers looked up unbound phrases in the pinned `hp.obo`. An answer was used only if the ID exists, is current, and the name the helper copied equals the term's name.
- **Rater check:** 30 model bindings are sampled for you (`adjudication/poc_audit/hpo_model_binding_sample.csv`, seed 20261019).
- **Diseases** (799 individuals):
  - 468 name HA20 and are bound to MONDO:0800045, whose Mondo cross-references are OMIM:616744 and Orphanet:476102;
  - 20 bind to another Mondo term by exact name;
  - 192 state no disease;
  - 119 state a label with no exact Mondo match.

  Binding the HA20 label to MONDO:0800045 rather than the gene group term MONDO:0100222 was my call, flagged for review.

### 4.3 Phenopackets

| | Ungated build | Final build (gatekeeper applied) |
|---|---|---|
| Phenopackets (one per merged person, policy v4) | 749 | 749 |
| Schema-valid | 749 | **749** |
| Observed / excluded features | 3,523 / 759 | 3,463 / 730 |
| With a genomic interpretation | 492 | 492 |
| Variants with normalized expressions / original string only | 227 / 294 | 227 / 294 |
| Excluded terms dropped because an observed term entails them | 36 | 32 |

- **Validation:** no errors. The warnings are 631 observed and 131 excluded terms whose ancestor is also listed; they are kept, since each has its own quote.
- **Three-state:** excluded terms come only from rows marked excluded. "Not reported" stays in the evidence tables, because a phenopacket cannot express it.
- **The lenient build:** keeping partial verdicts and dropping only unsupported ones gives 3,523 observed and 757 excluded (`phenopackets_gk_lenient_build.json`).

## 5. Stage 5: the gatekeeper

### 5.1 What was judged

| Class | Claims | How judged |
|---|---|---|
| Bookkeeping (PMID fields, labels repeated in child tables) | 42,996 | Not judged |
| Verbatim (free text found inside its own quote; the quote is verbatim in the paper) | 9,848 | Supported by construction |
| Model (statuses, enums, numbers, age conversions, text not found in its quote) | 12,155 | One Opus helper per chunk, `gatekeeper_v1.md` |

**Result** (`gatekeeper_summary.json`):

| | All judged values (22,003) | Helper-judged only (12,155) |
|---|---|---|
| Unsupported or quote not found | 8 (0.036%; 0.016–0.072%) | 8 (0.066%; 0.028–0.130%) |
| Not fully supported, counting partials | 313 (1.42%; 1.27–1.59%) | 313 (2.58%; 2.30–2.87%) |

**Where flags fall.** Fields with the most flags (partial or unsupported, of judged):
- feature status 72/4,453;
- checklist status 69/1,911;
- clinical diagnosis basis 36/410;
- functional evidence statement 17/144;
- feature detail 16/1,269;
- feature onset 16/241;
- pathogenicity statement 15/390;
- treatment summary 14/409;
- age at last evaluation 10/154;
- the "cites earlier report" flag 8/43.

### 5.2 The 8 unsupported values

| Paper | Field | Error class | Already fixed? |
|---|---|---|---|
| 30526650 (×2) | inheritance "inherited maternal" | Carrier status inferred: the mother was never tested | Yes: v4 gives "not reported" (§3) |
| 37324276 (×2) | arthralgia "excluded" for P2 and P5 | A group statement contradicted by the paper's own per-patient table | No; proposed rule below |
| 31175876 | "normal C-reactive protein levels" excluded | Labelling convention (§5.3); the meaning is right | Convention fix proposed |
| 33971891 | "usually normal CRP" excluded | A hedged phrase read as an absence | No |
| 39125844 | treatment summary | Treatment of the proband's relatives given to the proband | No |
| 41634270 | treatment summary for patient #9 | Adds conditioning details stated only in Methods, for all patients | No |

All 8 are left out of the final phenopackets. The two treatment summaries and the two inheritance values never enter a phenopacket in any case.

### 5.3 The partial verdicts, and one gatekeeper inconsistency

The flags were grouped by a keyword rule on the helper's reason (`analysis/poc/gatekeeper_flags.py`). The groups are approximate and only describe the flags; the rule is in the script, and every flag is listed with its reason in `gatekeeper_summary.json`.

| Group (313 flags) | Flags | Typical case |
|---|---|---|
| Detail outside the quote | 80 | The value adds a true detail from the next sentence ("trio WES", a gene panel) |
| More specific than the quote | 75 | "fever" → "recurrent fever"; "cytopenia" → "autoimmune cytopenia"; "oral/genital ulcers" split into two items; an initial diagnosis read as a feature |
| Normal finding labelled as the feature, status excluded | 41 | "normal ESR" excluded, "RF negative" excluded |
| Age or timing | 30 | A range recorded as one age; age at presentation used as age at diagnosis |
| Absence or fact inferred | 11 | A normal chest CT read as "no interstitial lung disease" |
| Hedged phrase | 7 | "suggesting panniculitis" recorded as observed |
| Another person | 6 | |
| Contradicted by the paper | 3 | |
| Other | 60 | |

**The labelling convention.**
- **What happens:** the extraction records a normal finding with the paper's words as the feature and status "excluded", meaning the abnormality is absent.
- **How helpers judged it:**
  - At least six helpers said they accepted it, on the same reasoning (e.g. 33815380, 36467491, 40719110).
  - About 40 flags, from other helpers, call it partial because the label read literally says the opposite.
  - One helper called it unsupported (31175876).
- **Where the meaning lands:** the HPO binding carries the abnormality (e.g. "Elevated C-reactive protein level", excluded), so the phenopackets are right. But because the gatekeeper was inconsistent, the final build drops some correct exclusions.
- **This is a gap in my instructions, not in the extraction.** Proposal in §8, item 2.

**Papers that contradict themselves.** Helpers found several papers whose table and text disagree, e.g.:
- the Figure 2 legend in 31299923 names a patient that the text and Table 2 do not;
- in 34011076, Table 1 lists genital ulcers and a rash, while the text says there were none.

Others are 34030699, 35958611, 39125844, 40859316 and 32714711. In each case the claim matched its own quote and was judged supported, with the conflict noted in the reason. These belong in the human audit's error discussion, not in the unsupported count.

**A flag that could mislead merging.**
- In 35753512, 35486341 and 36211342, the paper-level "cites an earlier report of the same patients" flag is true, but the earlier report covers patients with other genes, not the TNFAIP3 carrier.
- None of these papers produced a merge under policy v4 (`merges.csv`: 0 merged pairs involving them). So no record was joined in error.
- The flag should be per patient in the frozen schema; it is already per patient where v4 adds the reference column.

## 6. Waiting for you: the two rating sheets

| Sheet | Rows | What to fill in |
|---|---|---|
| `adjudication/poc_audit/sample.csv` | 50 claims: 20 variant fields, 10 observed and 10 excluded features, 10 demographic or inheritance fields (seed 20261019; pools in `sample_key.json`) | Column "rating": supported / partially supported / unsupported, on the quote alone, plus a note. The gatekeeper verdict is hidden. |
| `adjudication/poc_audit/hpo_model_binding_sample.csv` | 30 model-step HPO bindings | "rater_ok": yes / no, plus a note |

**After your ratings:**
- `analysis/poc/audit_metrics.py` scores them: the human unsupported rate with an exact interval, and the Q4 gate (unsupported ≤ 4% at n = 50). The automated span match is already met at 100%.
- It also produces the gatekeeper-vs-human confusion matrix and a list of disagreements.
- Per `POC_DESIGN.md` Stage 5 step 3, disagreements and partials come back to you once, with the full paragraph, for a final label.

## 7. Spend

| Reading (session usage, list-price estimate) | USD |
|---|---|
| End of Stage 3b report | 460.75 |
| Start of the v4 check (after D-23 and D-24 work) | 463.50 |
| After the v4 check, Stage 4 and Stage 5 | 580.31 |
| **This report's work** | **≈119.56** (116.81 since the v4 check started) |
| Approved: Stage 5 ~$170 (D-25) + v4 check ~$25 (D-24) | ~195 |

- **Why the work cannot be split:** the v4 check, the Stage 4 binding helpers and the gatekeeper overlapped in one window (02:08–03:02 UTC). The 463.50 reading did not refresh again until about 02:58 UTC. Details are in both run manifests.
- **Against the estimate:** the gatekeeper came in well under the ~$170 estimated from run-2's per-paper rate. Most claims needed no model call, and each helper read one paper once.
- **What the readings cover:** this session's own work as well as the helpers', so they are upper bounds. Reconcile against claude.ai Settings > Usage (D-17).
- **Overage:** from about 02:50 UTC the session ran on overage after the five-hour limit. If overage bills differently from the grant credits, it matters for D-17.
- **Pilot to date:** $580.31 against the $1,000 ceiling (hard stop $1,500).

## 8. Decisions needed (recommendations first)

The pre-registration is not frozen, so these are revisions. The next free decision number is D-26.

1. **Reword the normalization check.**
   - *Recommend:* measure it over descriptions that state a cDNA change, and report protein-only and structural descriptions separately with their status.
   - *For the frozen pipeline:* also fix the two repairable causes of rejection: map transcripts VariantValidator does not hold to the current RefSeq version, and record a corrected query beside the original string for typos.
   - *Why:* as worded, the target counts descriptions that cannot be normalized from the text, so no extraction can meet it.
   - *Effect:* on run-2 it would read 128/138 (92.8%) now, and up to 137/138 after the fixes.
2. **Normal findings and the gatekeeper.**
   - *Recommend:* in the instructions for the six-disease run, when a feature is excluded because a finding is normal, write the abnormality as the feature ("elevated CRP") and keep the paper's words in the quote. Also state the convention in gatekeeper v2, along with two rules the flags showed were missing: a per-patient table outranks a group statement, and a hedged phrase supports neither observed nor excluded.
   - *What not to do:* no re-run on HA20.
   - *Why:* it removes the largest group of flags at its source, and makes the gatekeeper consistent before the 250-claim audit.

**Not a decision, for the record.** The final phenopackets follow `POC_DESIGN.md` §3.9 and leave out partially supported claims. The lenient build is reported alongside as a sensitivity check.

## 9. Next

- Your ratings (§6), then `audit_metrics.py` and the re-read step.
- Stage 6 (ClinVar concordance and completeness, harness side only) and Stage 7 (pilot report).

## 10. Update, 2026-10-19: the human audit, D-26 to D-28 and gatekeeper v2

Every number here comes from `analysis/poc/audit_metrics.py` (output files named below), the gatekeeper merge, or `normalize_variants.py`.

### 10.1 Jimmy's audit (first pass, before the step-3 second look)

Jimmy rated all 50 claims and 27 of the 30 HPO bindings on a private rating page (`adjudication/poc_audit/make_rating_page.py`). The gatekeeper's verdicts were hidden from him. Ratings: `adjudication/poc_audit/sample.csv`, `ratings_raw.json`; scores: `analysis/poc/audit_metrics.json`.

| | Claims | Plain rate (exact 95% CI) | Weighted by stratum pool |
|---|---|---|---|
| Supported | 42 | | |
| Partially supported | 6 | | |
| Unsupported | 2 | 4.0% (0.5–13.7%) | 3.3% |
| Not fully supported | 8 | 16.0% (7.2–29.1%) | 12.5% |

- **Q4 gate:** the automated span match is 100%, and the human unsupported rate is 4.0%, exactly at the ≤ 4% point-estimate limit. The gate is met on the first pass, at its edge. The second look may move it.
- **By stratum:** both unsupported claims are variant fields.
  - C049428: "pathogenic" was given to the mother of P3 from a sentence about the whole cohort; she has low-level somatic mosaicism.
  - C048990: P1's zygosity was taken from a group statement, although P1's variant is undetermined.
- **Excluded features:** 3 of the 10 sampled were rated partly. Two of them record a negative investigation or consultation as the feature.
- **Weighting:** the sample has fixed counts per stratum, so excluded features (a small pool) are over-represented. The weighted figures correct for that; they are point estimates only.
- **HPO model bindings:** 23 of 27 accepted (85%, CI 66–96%), after Jimmy recounted four normal-finding rows as yes (D-27 handles the convention). 3 were left unrated.

### 10.2 The gatekeeper against the audit

| Gatekeeper | Agreement with Jimmy (supported vs not) | Of his 8 not-fully-supported claims, flagged | False flags |
|---|---|---|---|
| v1, as run on all of run-2 | 40/50 | 0 | 2 |
| v2, re-check on the same 50 claims (`gatekeeper_v2_recheck.csv`) | 44/50 | 2 | 0 |

- **v1 missed all 8.** In 3 of them no model judged the claim: the value appears word for word in its quote, so a script had marked it supported. Its 2 false flags were normal findings recorded as excluded, which Jimmy accepts.
- **The gatekeeper's whole-run rate understates the problem.** Its 0.036% unsupported rate over run-2 (§5.1) is far below the human 4.0% and should not be cited as an error rate.
- **v2 does better but is still weak.** It has no script shortcut and checks the person link (D-28), and it states the normal-finding rule (D-27). It flagged C049428 and C038628 as partial. It still called C048990 supported, and 5 of Jimmy's partials too.
- **This was not an independent test.** v2's rules were written after seeing these ratings, so its true performance on new claims is likely no better than this.
- **What it means:** the gatekeeper cannot stand in for the human audit. The pre-registered 250-claim audit stays the measure of the false-positive rate. The pre-registration's "gatekeeper accuracy against human labels" (§7.1(b)) is the right way to report it.

### 10.3 Decisions taken (Jimmy, 2026-10-19; `DECISIONS.md`)

- **D-26:** the normalization check counts descriptions that state a cDNA change, with repairs.
  - The repairs: Ensembl transcripts go to VariantValidator's Ensembl endpoint; NM_006290.5 (not held) is mapped to NM_006290.4; two notation typos are queried in corrected form (`configs/hgvs_query_corrections.csv`), with the extracted string kept.
  - Result: **135 of 138 (97.8%)**, so the check is met as reworded. Three remain for a person to read: one length mismatch and two reference mismatches.
  - Phenopackets rebuilt: still 749, all schema-valid. Variants with normalized expressions rose from 227 to 239.
- **D-27:** for the six-disease run, a normal finding is recorded as the absent abnormality, with the paper's words in the quote. Gatekeeper v2 states this.
- **D-28:** no script shortcut in the gatekeeper; every value is judged, including its link to the person. That is about 80% more gatekeeper work.
- **Pre-registration:** draft v0.6 applies all three (§6.2, §6.4, §7.2.2).

### 10.4 Still open

- **The step-3 second look:** 10 claims, on the rating page's second tab. Then the final labels go through `audit_metrics.py`, for both v1 and v2.
- **The gatekeeper's weak recall** needs a design answer before the freeze. Options for the pilot report include a claim-level read with the person named in the question, a second independent gatekeeper, or accepting it as a pre-filter and relying on the audit. That decision is for after the second look.
- **Spend:** the re-check (28 short helper reads) has no reading yet; the session reading did not refresh during the turn. Normalization repairs cost no model calls.
