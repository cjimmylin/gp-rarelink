# Screening instructions, v1 (GP-RareLink pilot, A20 haploinsufficiency)

You are screening PubMed records for a literature corpus on **A20 haploinsufficiency (HA20)**: the autoinflammatory disease caused by heterozygous germline loss-of-function variants in *TNFAIP3*.

You get one JSONL file. Each line is one paper: `pmid`, `title`, `abstract`, `publication_types`, `year`, `journal`, `languages`. Use only that text. Do not use outside knowledge about specific papers, authors, patients or variants, and do not look anything up.

For every line, assign two labels.

## 1. `study_type` (exactly one)

- `case report`: one patient, or one family, described clinically.
- `case series/cohort`: several unrelated patients described with clinical detail. This includes registry studies, multicentre studies, and cohort papers that list patients individually.
- `review/meta-analysis`: a narrative or systematic review, meta-analysis or guideline, including reviews that also add a few new patients.
- `functional only`: laboratory, cell or animal work with no new patient descriptions.
- `other`: anything else. Examples: editorials, letters without patients, methods papers, genetic association studies (GWAS, SNP case-control) that report no individual patients, and cancer or somatic-mutation studies.

## 2. `relevance`: does the paper report at least one individual with HA20?

- `yes`: the title or abstract describes at least one person with A20 haploinsufficiency, or with a germline (constitutional, inherited or de novo) *TNFAIP3* variant presented as causing disease in that person. Reviews of HA20 that tabulate patients also count as `yes`.
- `no`: the paper is about something else. Examples:
  - *TNFAIP3* polymorphisms or risk alleles in lupus, rheumatoid arthritis or other common diseases, without individual patients;
  - somatic *TNFAIP3* mutations in lymphoma or other cancers;
  - A20 protein biology with no patients;
  - "HA20" used to mean something other than A20 haploinsufficiency.
- `unclear`: the abstract is missing or too vague to tell. For example, a germline *TNFAIP3* variant in a patient where it isn't clear whether it is presented as disease-causing, or no abstract at all with a title that could fit. When in doubt between `yes` and `unclear`, choose `unclear`; when in doubt between `no` and `unclear`, choose `unclear`. Unclear papers are checked again in full text, so this costs little, while a wrong `no` loses a paper.

## Output

Write a CSV with header `pmid,study_type,relevance,reason`, one row per input line and none missing.
- `reason` is one short sentence quoting or pointing to the words in the title or abstract that decided the labels.
- Quote fields that contain commas.
- Use the label strings exactly as written above, in lower case.

Write the CSV to the path you are given, and do not change any other file. When done, report the number of rows written and the counts per label.
