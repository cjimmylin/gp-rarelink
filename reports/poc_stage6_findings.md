# Pilot Stage 6: ClinVar snapshot and concordance (HA20, run-2)

*2026-10-19. Harness side only. Every number here comes from `pipeline/harness/snapshot_reference.py` and `pipeline/harness/concordance.py`, run on 2026-10-19 on run-2 (`poc-ha20-run-2`, the extraction of record). Outputs: `analysis/poc/reference_snapshot/2026-10-19/` (MANIFEST.json, counts.json), `analysis/poc/concordance_poc-ha20-run-2.json`, `concordance_variants_poc-ha20-run-2.csv` and `gap_candidates_poc-ha20-run-2.csv`. Intervals are Wilson 95%.*

## 1. Summary

- **Q6 (the harness runs end to end against dated snapshots) is met for ClinVar and HPO.** OMIM is not checked: no API key is in place and its terms are not confirmed (Stage 6 stop-and-ask).
- **Q7 (completeness against a published catalogue) is not measured.** The benchmark named in the design, El Hani 2024 (PMID 38128752), is paywalled from this environment (publisher 403; not in Europe PMC). See §6.
- **Direct ClinVar counts now replace the application's proxies for *TNFAIP3*:**
  - 764 single-gene records on GRCh38 in the release of 2026-10-12;
  - 99 of them pathogenic or likely pathogenic, and 375 VUS.
  - The application gave 542 records, about 58 pathogenic and about 289 VUS (MyVariant.info and ClinVar Miner at application time).
- **Variant presence: 40 of 95 normalized extracted variants are in ClinVar** (42.1%, 32.7–52.2%). 55 are not, and for 41 of those the protein change the paper states matches the one predicted from the normalized cDNA. Those 41 are the first gap candidates for adjudication. They are ClinVar gaps only, since OMIM was not checked.
- **Classification:** of the 20 matched variants the authors call pathogenic or likely pathogenic, ClinVar agrees for 17 (85%, 64–95%).
- **Phenotype:** the extracted phenotypes recall 13 of the 14 HPO terms annotated to HA20 (OMIM:616744). Precision against that annotation is low (24% of individual-term pairs). The annotation is short, so this mostly measures how much the literature reports beyond it, not extraction error (§4).

## 2. The snapshot

| File | Server date | Rows read | Rows kept | md5 checked |
|---|---|---|---|---|
| ClinVar `variant_summary.txt.gz` | 2026-10-12 | 9,302,852 | 1,544 (*TNFAIP3*, both assemblies) | yes |
| ClinVar `submission_summary.txt.gz` | 2026-10-11 | 6,845,753 | 1,108 | yes |
| ClinVar `var_citations.txt` | 2026-10-11 | 5,163,463 | 1,118 | yes |
| HPO `phenotype.hpoa` (version 2026-09-02, HPO 2026-09-01) | 2026-09-02 | 286,652 | 19 (OMIM:616744) | no md5 published |

- **Where it lives.** The content sits outside the repository, under `/home/user/gp-rarelink-reference/2026-10-19/` in this container. Only the manifest and counts are committed, at `analysis/poc/reference_snapshot/2026-10-19/`.
- **Why not `data/reference/`?** `POC_DESIGN.md` Stage 6 says to put the snapshot there and commit the manifest. But the extraction guard (`pipeline/extract/guard.py`) refuses to run while a populated `data/reference/` is readable, and `tests/test_isolation.py` checks the checkout stays runnable. A committed manifest there would block extraction. The design's intent (ground truth out of reach of extraction) wins; logged in `DECISIONS.md`.
- **The container is temporary.** The snapshot content will be gone when this session ends. The script re-creates it, and the md5 and sha256 values in the manifest show whether a re-download matches.

**ClinVar *TNFAIP3* records (GRCh38, distinct VariationID, aggregate germline classification):**

| Classification | Single-gene records | Of which name HA20 as a condition |
|---|---|---|
| Pathogenic | 68 | 15 |
| Likely pathogenic | 27 | 9 |
| Pathogenic/Likely pathogenic | 4 | 2 |
| VUS | 375 | 29 |
| Conflicting | 27 | 7 |
| Likely benign | 217 | 4 |
| Benign | 15 | 1 |
| Benign/Likely benign | 16 | 9 |
| No germline classification | 14 | 0 |
| Not provided | 1 | 0 |
| **Total** | **764** | **76** |

Four further records span *TNFAIP3* and other genes. "Names HA20" means the record's conditions include OMIM:616744 or MONDO:0800045.

## 3. Variants

| | All 85 papers | Without papers that came only from ClinVar citations | Without any ClinVar-cited paper (D-19) |
|---|---|---|---|
| Papers counted | 85 | 82 | 68 |
| Distinct normalized extracted variants | 95 | 95 | 76 |
| In ClinVar | 40 (42.1%, 32.7–52.2%) | same | 29 (38.2%, 28.1–49.4%) |
| Matched and P/LP in ClinVar | 25 of 40 | same | 21 of 29 |
| Authors say P/LP, ClinVar agrees | 17 of 20 (85%, 64–95%) | same | 15 of 17 (88%, 66–97%) |
| Matched records naming HA20 | 16 of 40 | same | 11 of 29 |
| Not in ClinVar (gap candidates) | 55 | same | 47 |

- **Matching.** Extracted variants are matched to ClinVar by GRCh38 VCF key (chromosome, position, reference and alternate allele): VariantValidator's key for the extracted variant against ClinVar's own VCF columns. As a cross-check, none of the 55 unmatched variants matches a ClinVar record by cDNA name either.
- **Not placed.** 142 extracted variant descriptions could not be placed on the genome, so they are not in the denominator: 99 give only a protein change, 40 were not normalized, and 3 VariantValidator rejected (Stage 4, D-26).
- **D-19.** Only 3 run-2 papers came into the corpus through ClinVar citations alone, and they add no normalized variant. Removing every ClinVar-cited paper (17) lowers presence from 42% to 38%, in the direction D-19 expected: papers ClinVar cites are more likely to agree with it.
- **Classification cross-tab (matched variants; rows ClinVar, columns the authors):**

| ClinVar \ authors | P/LP | VUS | Other wording | Not stated |
|---|---|---|---|---|
| P | 16 | 1 | 2 | 2 |
| LP | 1 | 0 | 1 | 2 |
| VUS | 2 | 4 | 1 | 2 |
| Conflicting | 0 | 2 | 0 | 1 |
| LB, B/LB | 0 | 1 | 0 | 1 (B/LB stated by authors) |
| No germline classification | 1 | 0 | 0 | 0 |

### 3.1 Gap candidates

Pre-triage by script, comparing the protein change the paper states with the one VariantValidator predicts from the normalized cDNA:

| Pre-triage | Variants |
|---|---|
| Protein agrees: "ClinVar absent (candidate)" | 41 |
| No protein stated: check | 9 |
| Protein differs: check (mostly splice variants, where no protein is predicted; one frameshift off by one codon) | 5 |

- **Not yet triaged by hand.** The design's final triage (extraction error, normalization error, database absent, different classification, literature–database conflict) is a person's job, done with the paper open. It feeds Month-4 adjudication, so the 41 are candidates, not findings.
- **Authors' own classification of the 55:** 32 P/LP, 2 mixed, 4 VUS, 1 B/LB, 5 other wording, 11 not stated.

## 4. Phenotypes

| | All papers | Without any ClinVar-cited paper |
|---|---|---|
| Individuals with observed HPO terms (phenopackets) | 567 | 472 |
| Individual × term pairs matching the HA20 annotation | 826 of 3,463 (23.9%, 22.5–25.3%) | 679 of 2,932 (23.2%) |
| Distinct extracted terms matching | 23 of 574 (4.0%) | 21 of 523 (4.0%) |
| Annotated terms recalled | 13 of 14 (93%, 69–99%) | 12 of 14 (86%) |

- **Matching rule.** An extracted term matches when it is an annotated term or a descendant of one (is_a, HPO 2026-09-01). The one annotated term never recalled is Lupus anticoagulant (HP:0025343).
- **Reading the precision.** HPO annotates HA20 with 14 phenotype terms. The literature reports many more findings per patient (574 distinct terms), so most extracted terms fall outside the annotation. This is a property of the annotation, not a measure of extraction error. The per-claim audit (Stage 5) is the error measure. A useful next step is the reverse view: which frequent extracted terms the annotation lacks, as candidate HPO annotation additions.

## 5. Isolation

- The snapshot was taken after run-2 was tagged and after the D-29 rules (extraction v5, gatekeeper v3) were committed (`05952ea`). Nothing in the extraction or gatekeeper prompts was changed after ClinVar content was seen.
- The harness imports normalization helpers from `pipeline/extract`; the reverse is not allowed, and `tests/test_isolation.py` still passes.

## 6. Open items

1. **The Q7 benchmark (Jimmy).** El Hani 2024 is paywalled here. Options:
   - Jimmy downloads its supplementary patient and variant tables on his machine. They go under the reference root, not the repo, and are transcribed by script or by a separately audited run, as the design says;
   - or a substitute benchmark, which changes the design and needs his decision.
2. **Hand triage of the 55 gap candidates**, with the paper open (feeds adjudication).
3. **OMIM** stays unchecked until the key and terms are in place.
4. **Dedup check against the benchmark** (Stage 6 step 6) waits on item 1.
