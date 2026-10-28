# Direct extraction instructions, v1 (GP-RareLink SLIDERS ablation, D-42)

*The baseline arm of the SLIDERS ablation pilot (`reports/sliders_ablation_design.md`). A plain request for the final records: no evidence tables, no quotes, no rules file. Written 2026-10-28, before the run; not changed afterwards. Rendered per disease by `pipeline/extract/claude_code/direct_prompt.py` from this template.*

You are given one published paper about A20 haploinsufficiency (HA20), the disease caused by *TNFAIP3* variants, converted to Markdown (its first lines give the PMID and title; a `## Supplementary material` section, if present, is part of the paper). Read it and write one JSON file recording what the paper reports about each person it describes who has a *TNFAIP3* variant or a diagnosis of A20 haploinsufficiency (HA20), and about each relative the paper describes in relation to such a person. Other patients in a study (for example people with variants in other genes) get no record.

## Rules

1. Use only the paper. Do not use anything you know or remember about this paper, its patients, the gene or the variants. When the paper does not state something, write `"not reported"` for text and category fields and `null` for numbers, durations and true/false fields.
2. Record strings as the paper prints them: variant descriptions, ages, feature names, labels. Do not convert between notations and do not add a transcript the paper does not print.
3. Phenotypes have three states. `"observed"`: the paper says the person has or had the feature. `"excluded"`: the paper says the feature was absent, negative or not found in that person. Otherwise `"not reported"`.
4. One record per person. Do not merge two people into one record and do not create a person the paper does not describe.

## Output: one JSON file at the path given in your task

```json
{
  "pmid": "<from the paper's header line>",
  "instructions_version": "direct_v1",
  "reports_individuals": true,
  "publication": {
    "first_author": "<surname as printed>",
    "year": <int or null>,
    "study_type": "case report" | "case series/cohort" | "review/meta-analysis" | "other",
    "n_patients_reported": <number of patients with a TNFAIP3 variant the paper describes, as stated, or null>,
    "cohort_size_as_stated": <total number of patients in the study as stated, or null>,
    "cites_prior_report_of_same_patients": <true | false | null>,
    "prior_report_citation": "<the reference given for the earlier description of the same patients, as printed, or 'not reported'>"
  },
  "individuals": [ RECORD, ... ]
}
```

Set `"reports_individuals"` to `false`, fill `publication`, and leave `individuals` empty when the paper describes no such person (for example a review with no patient-level detail).

### RECORD: one object per person

```json
{
  "individual_label_in_paper": "<the paper's own label for the person, e.g. 'P1', 'Patient 3', 'II-2'; the single unnamed patient of a case report is 'patient'; a relative without a label is named by relation, e.g. 'mother of P1'>",
  "family_label_in_paper": "<as printed, or 'not reported'>",
  "is_proband": <true | false | null>,
  "sex": "male" | "female" | "not reported",
  "age_at_onset_original_text": "<as written, or 'not reported'>",
  "age_at_onset_iso8601": "<ISO 8601 duration such as P3M or P12Y when the text gives a number, else null>",
  "age_at_diagnosis_original_text": "...", "age_at_diagnosis_iso8601": "...",
  "age_at_last_evaluation_original_text": "...", "age_at_last_evaluation_iso8601": "...",
  "ethnicity_or_country": "<as stated, or 'not reported'>",
  "consanguinity": "yes" | "no" | "not reported",
  "vital_status": "alive" | "deceased" | "not reported",
  "deceased_age_iso8601": "<duration or null>",
  "cause_of_death": "<as stated, or 'not reported'>",
  "treatment_summary": "<short summary of the treatments reported for this person, or 'not reported'>",
  "disease_label_as_stated": "<the diagnosis the authors give this person, as printed, or 'not reported'>",
  "clinical_diagnosis_basis": "<how the diagnosis was made per the paper, or 'not reported'>",
  "source_reference_in_review": "<only for a person taken from a table or summary of previously published cases: the reference as printed; otherwise 'not reported'>",
  "variants": [ VARIANT, ... ],
  "phenotypic_features": [ FEATURE, ... ],
  "phenotype_checklist": { "<checklist feature>": "observed" | "excluded" | "not reported", ... }
}
```

### VARIANT: one object per variant the paper reports for this person

```json
{
  "gene_symbol_as_stated": "<as printed>",
  "variant_original_string": "<the variant description exactly as printed, e.g. 'c.1727dupC' or 'NM_006290.3:c.653del:p.Leu218TrpfsTer10'; 'not reported' if the paper ties a variant to the person but prints no description>",
  "transcript_as_stated": "<e.g. NM_006290.3, only if printed; else 'not reported'>",
  "cdna_hgvs_as_stated": "<the c. part as printed, or null>",
  "protein_hgvs_as_stated": "<the p. part as printed, or null>",
  "genomic_coordinates_as_stated": "<as printed, with the build if printed, or null>",
  "variant_type_as_stated": "missense" | "nonsense" | "frameshift" | "splice" | "in-frame indel" | "large deletion/CNV" | "other" | "not reported",
  "zygosity": "heterozygous" | "homozygous" | "compound heterozygous" | "hemizygous" | "mosaic" | "not reported",
  "inheritance": "de novo" | "inherited maternal" | "inherited paternal" | "inherited unspecified parent" | "not reported",
  "parental_testing_statement": "<what the paper says about testing the parents, or 'not reported'>",
  "functional_evidence_statement": "<functional assay results reported for this variant, or 'not reported'>",
  "pathogenicity_as_stated_by_authors": "<the authors' own classification as printed, e.g. 'pathogenic', 'VUS'; or 'not reported'>",
  "acmg_criteria_as_stated": "<ACMG codes if printed, e.g. 'PVS1, PS2'; or 'not reported'>"
}
```

### FEATURE: one object per clinical feature the paper reports as present or as absent for this person

```json
{
  "feature_text_as_stated": "<the feature in the paper's own words>",
  "status": "observed" | "excluded",
  "onset_original_text": "<age or time of onset of this feature as written, or null>",
  "onset_iso8601": "<duration when a number is given, else null>",
  "severity_or_detail": "<qualifiers the paper attaches (frequency, severity, laboratory value), or null>",
  "hpo_label_candidate": "<the Human Phenotype Ontology term you believe matches, or null>",
  "hpo_id_candidate": "<its HP:nnnnnnn identifier only if you are sure, else null>"
}
```

Do not list a feature the paper does not mention for the person.

### Checklist: the status of each of these 20 features, for every person

- oral ulcers
- genital ulcers
- gastrointestinal ulcers or inflammation
- recurrent fever
- arthritis or arthralgia
- uveitis or other ocular inflammation
- skin lesions (rash, folliculitis, erythema nodosum)
- autoimmune thyroiditis
- type 1 diabetes
- autoimmune hepatitis
- cytopenia (autoimmune)
- lymphoproliferation or lymphadenopathy
- central nervous system involvement
- recurrent infections
- elevated inflammatory markers (CRP/ESR)
- autoantibodies (ANA/other)
- growth failure
- pericarditis or other serositis
- interstitial lung disease
- vasculitis

Give every item for every record, using these names exactly, with rule 3.

## Finish

Make sure the file parses as JSON and is written to the output path. Then reply, in under 150 words: the number of individuals, whether `reports_individuals` is true, and anything you were unsure how to record.
