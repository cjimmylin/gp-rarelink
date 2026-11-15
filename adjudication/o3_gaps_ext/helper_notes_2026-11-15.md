# Dossier helpers' notes, D-47 extension (2026-11-15)

These are the concerns the six dossier helpers reported back, summarised by Claude. They are model-written pointers for the panel, not verdicts. Each one is also in the `concerns` field of the dossier it names, and that dossier carries the verbatim quotes. `check_dossiers.py --all` result: 41 dossiers, 789 quotes, all verbatim, 0 problems.

Candidate ids changed after D-48 re-ran the gap step: the Blau ids below are the current ones (the former G-blau-002 to 005 are now 003, 004, 005 and 008).

## Withdrawn (D-48)

- **G-blau-008 (formerly G-blau-005):** every paper writes c.1538T>C (M513T), which is legacy NM_022162 numbering. The candidate was read on MANE as p.Leu513Pro. On MANE numbering it would be c.1457T>C (Met486Thr). Claude reached the same conclusion from the protein check; see `reports/extension_report.md` §4. P9 in 41673771 carries the same stated variant and is not linked to this candidate, consistent with the same numbering problem.
- **G-lcat-001 (withdrawn):** sits on chromosome 4 because paper 31684177 stated NM_012108.3, which is not an LCAT transcript. The paper's change is p.(Ile202Thr). The same paper's Table 1 and Results give the siblings' LCAT activity values in opposite order.

## Contradictions inside papers

- **G-blau-001** (38927735): the abstract has c.1412G>T p.(Arg471Leu), the body c.1412G>C p.(Arg471Pro). The family also carries an NLRC4 nonsense variant, and uveitis appears only in members who carry both. Two of the triplets are monozygotic. The authors classify the variant as a VUS.
- **G-lcat-003:** c.1138T>C predicts p.(Cys380Arg), but the paper writes "Arginine to Cysteine at the codon 380". Its gnomAD figure covers "both variants" together.
- **G-lcat-008** (25984174): the text calls Case 2 homozygous; Table 1 says heterozygous.
- **G-lcat-017:** review 34256778 gives c.490C>T in its text and Table 3, but its case description says Arg140His (G to A). Only 34316822 clearly carries c.490C>T.
- **G-lcat-008, G-lcat-025:** protein numbers are 24 residues lower than predicted, which fits mature-protein numbering; the papers don't say so.
- **G-lcat-025:** the same patient appears in 25984174 and 36387451, with conflicting ages (referred at 27; diagnosed at 30).
- **G-ats-001** (39456956): the abstract says de novo, the results say the parents are untested. On phase, "four of the reads contained both variants", yet the authors conclude trans.
- **G-papa-001** (32477554): an intronic c.562+114C>G is described as "in the exon region". It is always seen together with two other intronic variants. The father carries it without symptoms. PAPA-ID0119 (review 34745107) is very probably the same person as PAPA-ID0044 and was not merged.
- **G-gamt-006:** table protein p.Trp87fs*1 vs predicted p.(Trp87Ter).
- **G-gamt-008:** the abstract calls both variants novel; the case report says the other allele was reported before.

## New Blau candidates after D-48 (helper notes)

- **G-blau-007 (D512V):** both parents Sanger-negative (parentage not stated as confirmed); an NF-κB reporter result is cited but its data are not shown. The paper says the patient is the D512V case of Matsuda 2020 (PMID 32647028), which it says wrongly listed polyarthritis and renal calcification for her.
- **G-blau-009 (c.1808A>G):** one row of a review table (32637927) citing Toral-López 2018, with no sex, zygosity, protein or transcript; the legacy-numbering placement cannot be confirmed from this paper. The primary report is needed.
- **G-blau-002 (H480R):** two affected siblings; three more affected relatives not genotyped; absent from 250 in-house exomes; no functional data.
- **G-blau-006 (P507S):** one sporadic case; "de novo" is the authors' belief with untested parents; no functional data.

## Same person counted more than once (not merged by the pipeline)

- **GAMT:** the review rows in 42885896 duplicate primary-report patients: G-gamt-001's siblings (GAMT-ID0265/0266/0267 = 0062/0063/0064), and G-gamt-002's patient (GAMT-ID0361 = 0035).
- **PAPA:** PAPA-ID0119 = PAPA-ID0044 (above).
- **Blau:** the 20-year-old in 36915122 and P9 in 41673771 may be one person (unresolved).

## Thin or table-only evidence

- **LCAT:** 14 of the 20 batch-05 candidates appear only as table rows in review 34256778, with no case description. Ten of them come from its "unclassified patients" table, and three of those have every clinical field "Unk". Some of its Table 1 reference numbers don't match its reference list.
- **G-lcat-018 / G-lcat-019:** adjacent bases in the same person, phase not reported; possibly one complex allele, so adjudicate them together.
- **G-blau-004 / G-blau-005 (M491L, H496P):** come only from Table S2 of a 13-patient treatment cohort (41673771).
- **G-gamt-004, -005, -006:** come only from supplementary table rows in 42885896, with no case description (the pipeline did not class that paper as a review, so the "only from reviews" count is 0 for GAMT).
