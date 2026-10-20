# Full-text screening instructions, v1 (GP-RareLink; any pilot disease)

*Second screening stage, after title/abstract screening (`screen_v2.md`). It applies the eligibility rule of pre-registration §5.1 (draft v0.9, with D-33: reviews with per-patient tables of earlier cases are included and flagged) to the full text. The disease, its gene and what does not count as the disease are given in your task, from `configs/diseases.yaml`.*

You are screening full-text papers for a literature corpus on **the disease named in your task**, caused by variants in **the gene named in your task**.

You get a list of Markdown files, one per paper. Each starts with `PMID:` and a title. Read each paper far enough to decide; you do not need to read the reference list. Use only the paper's text. Do not use outside knowledge about specific papers, authors, patients or variants, and do not look anything up.

## The rule (pre-registration §5.1)

**Include** a paper if it reports **individual-level** genotype and/or phenotype for **at least one person with the disease**, either as a primary publication (case report, case series or cohort paper) or as a review with a per-patient table of earlier cases (D-33; see below).
- "Individual-level" means something is said about a specific person: a patient described in the text, or a row in a per-patient table. Aggregate figures only ("12 of 40 patients had seizures") are not individual-level.
- "Person with the disease": a patient diagnosed with the disease, or a person with a germline variant in the gene that the paper presents as causing the disease in that person. Apply the "not this disease" list in your task.
- Genotype is not required. A patient with the disease described clinically or pathologically, with no variant reported, still counts (for example, papers from before the gene was known).
- A paper that re-describes patients reported before still counts, if it gives individual-level data. Overlap is handled later.
- A review, meta-analysis or guideline counts if it adds **new** individuals of its own (for example, "we report a new patient and review the literature"), **or** if it has a per-patient table (or per-patient list) of individuals from earlier papers. Set `literature_table` to `yes` in that case. These people are flagged as secondary-source later.

**Exclude** otherwise, with exactly one reason:
- `not_disease`: no person in the paper has the disease (another condition, a carrier relative only, or a different disease with a similar name).
- `no_individual_data`: people with the disease are discussed only in aggregate, with nothing said about any one person.
- `review_no_new_individuals`: a review, meta-analysis or guideline that adds no new individuals and has no per-patient table or list of earlier individuals (aggregate summaries only).
- `functional_only`: laboratory, cell or animal work with no individual patient data.
- `not_english`: the main text is not in English.
- `unusable_text`: the file is empty, garbled or not the paper named in the title.

## Fields

Write one row per paper:
- `pmid`: from the file name.
- `decision`: `include` or `exclude`.
- `exclusion_reason`: one reason from the list above if excluded; empty if included.
- `study_type`: from the full text, one of `case report`, `case series/cohort`, `review/meta-analysis`, `functional only`, `other` (the same definitions as `screen_v2.md`).
- `n_individuals`: the number of individuals with the disease the paper describes individually, as a whole number. Write `0` if none, and `unclear` if you cannot count them from the text. Do not estimate.
- `has_genotype`: `yes` if at least one such individual has a variant in the gene reported, otherwise `no`.
- `literature_table`: `yes` if the paper has a per-patient table of individuals from **earlier** papers (a literature summary), otherwise `no`. Record it whatever the decision.
- `evidence_quote`: one verbatim passage from the paper, at most 300 characters, that best supports the decision. Copy it exactly, character for character, from the Markdown file (a sentence, a table row or a heading). It will be checked by script against the file.
- `note`: optional, one short sentence. Use it when the decision was close.

## Output

Write a CSV with header `pmid,decision,exclusion_reason,study_type,n_individuals,has_genotype,literature_table,evidence_quote,note`, one row per file and none missing. Quote every field that contains a comma or a quote mark, doubling inner quote marks, as CSV requires. Use the label strings exactly as written above, in lower case.

Write the CSV to the path you are given, keep any scratch files in the scratch directory you are given, and do not change any other file. When done, report the number of rows written and the counts per decision and exclusion reason.
