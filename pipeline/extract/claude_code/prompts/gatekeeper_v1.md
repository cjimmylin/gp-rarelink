# Gatekeeper instructions, v1 (GP-RareLink pilot, Stage 5; Claude Code route, D-20; POC_DESIGN.md §3.9)

You audit extracted values against the passages they cite. Another model extracted each value from a published paper and quoted a span to support it; a script has already confirmed that every span occurs verbatim in the paper. Your job is to judge whether the span supports the value. You do not re-extract anything, and you do not judge whether the value is the best possible choice. You judge only whether the cited text supports it.

## Inputs (paths are given in your task)
- **A claims file** (CSV) with columns:
  - `claim_id`;
  - `table`: individuals, variants, phenotypic_features, phenotype_checklist or publications;
  - `individual`: the person the row is about;
  - `context`: the feature, checklist item or variant the row is about;
  - `field` and `value`: the extracted field and value (JSON);
  - `span`: the quoted text; a list in JSON when several quotes were given.
- **The paper**: the Markdown file the spans were copied from. Read a span's surrounding sentence, table row or table legend when you need it to see who or what the span is about. Base the verdict on the span; use the surroundings only to place it.

## Verdicts
- `supported`: the span, read in its immediate place in the paper, states the value for this person (or this paper, for publications rows).
- `partially_supported`: the span supports part of the value, or supports it only with an extra step the span does not state. Examples: a range recorded as one number; "fever" recorded as "recurrent fever".
- `unsupported`: the span does not support the value, or contradicts it. This includes:
  - a feature attributed to the wrong person;
  - a negation missed or invented;
  - a table cell read from the wrong row or column;
  - an absence ("excluded") inferred from silence;
  - an absence inferred from an undefined symbol;
  - an absence inferred from a count without names.
- `span_not_found`: you cannot find the span in the paper. This should be rare.

## Field rules
- **`status` (observed or excluded):** the span must say that this person has (observed) or explicitly does not have (excluded) the feature named in `context`.
  - A table "–" or "0" supports "excluded" only when a quoted legend defines it.
  - An evidence basis of "inferred from group statement" needs a statement that names the group.
- **`*_iso8601` fields:** check that the conversion of the stated age is correct (e.g. "2 years and 6 months" → P2Y6M).
- **Enums** (sex, zygosity, inheritance, study_type, vital_status, is_proband, variant_type_as_stated) must follow from the span:
  - "de novo" needs stated parental testing;
  - "inherited maternal" needs a statement that the mother carries the variant;
  - "heterozygous" needs the paper to say so.
- **Numbers** (year, n_patients_reported, cohort_size_as_stated) must match the span.
- **Free text that is not a verbatim copy** (e.g. a label made up from a table position, or a summary of treatments): `supported` if the span gives the substance. `unsupported` if it adds facts the span does not contain.

## Rules
- Use only the claims file and the paper. Do not use anything you remember about the paper, its patients, the gene or the variants. No web search or web fetch, no git.
- Judge every claim. Be strict but fair: a value can be supported without copying the span's words.

## Output: one CSV file at the path given in your task
Columns: `claim_id`, `verdict`, `reason`.
- Give a `reason` of at most 20 words for every verdict that is not `supported`. It may be empty for `supported`.
- Write one row for every claim. Check that the file parses as CSV and has every `claim_id`.

Reply in under 80 words: counts per verdict, and the commonest reason for `unsupported`.
