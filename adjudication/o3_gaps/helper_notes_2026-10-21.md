# Dossier helpers' flags for the panel (WS3, 2026-10-21)

*The dossier helpers each ended with a short report to the coordinator. This file keeps the points that matter for adjudication, by batch, as the helpers reported them. They are model output: each is also recorded, with quotes, in the candidate's dossier under `concerns`. Nothing here is checked further. Every candidate stays pending adjudication.*

## Candidates that may not be gaps at all (check first)

- **G-ssadh-003.** PMID 27896081 writes "c.610-612A>G (IVS3-2A>G)", which points to c.610-2A>G. Normalization read the string literally as c.610-612T>G (6:24504257:T:G), whose reference base contradicts the paper's A. The coordinate is probably wrong.
- **G-axd-017.** The paper writes c.54G>T but calls it Gly18Val. On NM_002055.5, c.54G>T is silent at codon 18. The same paper calls the earlier report's c.53G>T "the same variant", so c.54 is probably a typo for c.53. The VCF may point to the wrong base.
- **G-lad1-077.** PMID 42625796 gives an NCBI accession, SCV007539359, for the variant. It may already be in ClinVar after the 2026-10-19 snapshot. Re-check before adjudicating.
- **G-danon-002.** The paper numbers the variant on NM_013995.1 (LAMP2B, exon 9B) as c.1150G>C p.Gly384Arg. The batch maps it to NM_002294.3 as intronic c.1093+2493G>C. The same applies to c.1097_1098del (exon 9b) in batch_17. The transcript mapping needs confirming.
- **G-danon-004.** This candidate joins c.1054delG (33680117) and c.1052delG (33933120). The merge holds only if positions 1052–1054 are a run of Gs. The stated protein, p.V352Ffs*5, differs from the predicted one.
- **G-lad1-038.** This candidate joins c.942_943insAACA (P58) and c.945_946insAAAC (P118), both normalized to c.943_946dup. P118's stated protein end differs from the predicted one.
- **G-lad1-020.** The paper's "c.1622_1657del36 (cDNA)" may not be the genomic change shown. The batch has c.1628_1657+6del.
- **G-danon-034.** PMID 30413001's text and its Table 1 disagree on which family carries c.56T>C, and the table labels c.56T>C "Frame shift".

## Same person under several identities (counts of people may be too high)

- **G-tangier-004 and G-tangier-007:** the same patient (TANGIER-ID0055), with "two heterozygous variants" and phase not shown.
- **G-axd-003:** four identities, probably two people (ID0449 = ID0214; ID0450 = ID0430, the Mura 2021 patient).
- **G-danon-031:** 33530800 case 1 (ID0137) is very likely 37215540 III-1 (ID0232); case 2 matches III-6, who is not in the batch.
- **G-danon-009:** 35669483 Pt 1 (ID0211) and 37568080 III-1 (ID0196) are very likely the same boy.
- **G-danon-035:** DANON-ID0497 is a citation of DANON-ID0252.
- **c.418del (batch_17):** DANON-ID0121, ID0472 and ID0320 are very likely one woman.
- **c.453del (batch_17):** DANON-ID0409 and ID0468 both cite Bottillo 2016.
- **LAD-I, PMID 22134107 (van de Vijver 2012):**
  - people are database accession numbers, and some are relatives counted as separate identities (G-lad1-025, -033, -072, -081);
  - several may be the same patients as in 33391282 (Madkaikar, an author of both papers: G-lad1-021, -023, -078) or in 24995649 (G-lad1-076).
- **LAD-I, 33391282:** 30 of its patients were reported before (PMID 25703682) without names, and four of the five c.1224+4A>G carriers come from PMID 25876705.
- **SSADH:** PMIDs 37503297 and 37962671 are the same preprint (merged correctly, decision 2026-10-19). In 42218553, patients 1–9 were published before, in a Chinese-language series not in the corpus.
- **G-tangier-003:** TANGIER-ID0229 is only a citation of Fasano 2012 (PMID 22959828).

## Carriers the papers report but the batch does not attach

- **G-tangier-001:** five relatives (siblings DC, RC and CC, and two sons).
- **G-danon-011:** an affected mother and three daughters.
- **G-danon-031:** seven relatives in 37215540.
- **G-danon-009:** Pt 2 to Pt 6 in 35669483.
- **G-axd-012:** the affected mother.
- **G-lad1-042:** an affected brother who died untested.
- **c.573del (batch_17):** two affected sisters in 19057086.
- **G-ssadh-003:** possibly Latzer preprint #48, if the variant is c.610-2A>G.

## Papers that contradict themselves (for the panel's reading)

- **Tangier 27853448:** cardiomyopathy statement contradicts the echocardiogram finding.
- **Danon 41854324:** PS2 claimed for a maternally inherited variant; the splicing figure cited is an echocardiography panel.
- **Danon 30413001:** family counts differ between places (8 vs 10).
- **LAD-I 33391282:** zygosity marks are inconsistent; Table S1 is cut off in the converted text (known input problem).
- **LAD-I 36185095:** c.920T>C vs c.920C>T.
- **AxD 38540409 vs 41443241:** the two papers disagree on the age at death of the same patient.
- **HA20 42012563:** P22 is male in Table 1 but female in the supplementary tables.

## Evidence that is thin by nature

- **Review-table rows with no case description:** about 34 LAD-I candidates rest only on van de Vijver 2012, a mutation update. The same holds for some Danon entries (c.940del, c.808dup, Bottillo c.453del).
- **Other genes in the same person:**
  - G-ha20-017: PIK3R1, HBB, SERPINA1 and VPS37A;
  - G-danon (41815899): BBS1, DCHS1, VWF, RYR2 and CYP4V2;
  - G-lad1-077: ALG2;
  - G-lad1-039: a second homozygous ITGB2 variant.
- **De novo claims without described parental testing:** G-danon-022 and G-danon-023, and 30413001 for its probands as a group.
