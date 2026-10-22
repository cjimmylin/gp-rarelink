# Writing a disease's phenotype checklist from its key review (v1)

*Written 2026-10-20 for the six-disease run (pre-registration §6.5: "Each disease's checklist is written from its GeneReviews or key review before extraction. It is never written from `phenotype.hpoa`."). Decision D-38 (Jimmy, 2026-10-20): the frozen extraction prompt and schema are instantiated per disease by swapping only the disease name, gene and checklist.*

You write the fixed phenotype checklist for one rare disease. Extraction helpers will later record, for every person in every case report, whether each checklist feature is observed, excluded or not reported. So the checklist should hold the features a reader would most want to know, for each patient, about this disease.

## Inputs

- **The review** (the only source you may use): the Markdown file named in your task.
- **The model checklist**, for format only. This is the checklist for A20 haploinsufficiency:

  > oral ulcers; genital ulcers; gastrointestinal ulcers or inflammation; recurrent fever; arthritis or arthralgia; uveitis or other ocular inflammation; skin lesions (rash, folliculitis, erythema nodosum); autoimmune thyroiditis; type 1 diabetes; autoimmune hepatitis; cytopenia (autoimmune); lymphoproliferation or lymphadenopathy; central nervous system involvement; recurrent infections; elevated inflammatory markers (CRP/ESR); autoantibodies (ANA/other); growth failure; pericarditis or other serositis; interstitial lung disease; vasculitis.

## Rules

1. **Exactly 20 features.** Not 19, not 21.
2. **From the review only.** Every feature must be one the review describes as part of this disease: a clinical sign or symptom, or an abnormal laboratory, imaging or physiological finding that the review names. Do not use your own knowledge of the disease, HPO annotation files, OMIM, ClinVar, Orphanet or any other source. If the review gives fewer than 20 suitable features, stop and say so instead of padding.
3. **Choose for case reports.** Prefer features that:
   - case reports commonly state as present or absent;
   - together span the organ systems the review describes;
   - include the features that define the classic presentation and any that the review says distinguish subtypes, ages of onset or sexes.

   Avoid treatment responses, outcomes such as death or transplant, and diagnostic test results that every patient has by definition (e.g. the causal enzyme or protein defect itself).
4. **Names.** Use short, plain, lower-case clinical names, as in the model. A composite item names its members in parentheses or with "or" (e.g. "seizures or epilepsy"). Keep composites few, and make each member something a paper would name.
5. **Evidence.** For each feature, give one to three quotes copied **exactly** from the review: the shortest contiguous text that shows the feature belongs to the disease. A script will check every quote verbatim against the file.
6. **No overlap.** No two items may describe the same finding, and a narrower item must not sit inside a broader one.

## Output

Write one JSON file (UTF-8) to the output path in your task:

```json
{
  "disease": "<disease key>",
  "source_pmid": "<PMID of the review>",
  "checklist": [
    {"name": "<feature name>", "quotes": ["<verbatim quote>", "..."], "why": "<one short sentence on why it is on the list>"}
  ],
  "left_out": ["<feature the review names that you considered and left out, with a few words why>"],
  "notes": "<anything the reviewer of this checklist should know>"
}
```

`checklist` has exactly 20 entries, in the order you would read them clinically (main presentation first). Then check your own file: it must parse as JSON, hold exactly 20 entries, and every quote must occur verbatim in the review.

Reply in under 120 words: the 20 names, separated by semicolons, and anything you were unsure of.
