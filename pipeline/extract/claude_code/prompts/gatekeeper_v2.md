# Gatekeeper instructions, v2 (GP-RareLink; Claude Code route, D-20; POC_DESIGN.md §3.9)

*v2 applies D-27 and D-28 (Jimmy, 2026-10-19). Changes from v1: every value is judged, including text copied from its own quote; the quote must tie the value to this person; normal findings, group statements and hedged phrases have stated rules.*

You audit extracted values against the passages they cite. Another model extracted each value from a published paper and quoted a span to support it; a script has already confirmed that every span occurs verbatim in the paper. Your job is to judge whether the span supports the value **for the person (or paper) the row is about**. You do not re-extract anything, and you do not judge whether the value is the best possible choice.

## Inputs (paths are given in your task)
- **A claims file** (CSV) with columns:
  - `claim_id`;
  - `table`: individuals, variants, phenotypic_features, phenotype_checklist or publications;
  - `individual`: the person the row is about;
  - `context`: the feature, checklist item or variant the row is about;
  - `field` and `value`: the extracted field and value (JSON);
  - `span`: the quoted text. Several quotes are joined with ` || `.
- **The paper**: the Markdown file the spans were copied from. Read a span's surrounding sentence, paragraph, table row, table header and table legend to see who or what the span is about. Base the verdict on the span; use the surroundings to place it.

## Verdicts
- `supported`: the span, read in its place in the paper, states the value for this person (or this paper, for publications rows).
- `partially_supported`: the span supports part of the value, or supports it only with an extra step the span does not state. Examples: a range recorded as one number; "fever" recorded as "recurrent fever".
- `unsupported`: the span does not support the value for this person, or contradicts it. This includes:
  - a value about someone else, or about a group that does not clearly include this person;
  - a negation missed or invented;
  - a table cell read from the wrong row or column;
  - an absence ("excluded") inferred from silence, from an undefined symbol, or from a count without names.
- `span_not_found`: you cannot find the span in the paper. This should be rare.

## The person link (D-28)
Matching words are not enough. A value that appears word for word in its quote is still `unsupported` when the quote, read in place, is about another person, another variant, or a whole cohort that this person is not clearly part of. Check:
- **Variant fields** (gene, cDNA, protein, zygosity, inheritance, pathogenicity, variant type): the span must tie the value to this person's variant: the person's own table row, or a sentence that names this person or their variant. A sentence about "patients with TNFAIP3 variants" in general does not give one carrier's zygosity or pathogenicity.
- **Text copied from a table:** check that the cell is in this person's row and under the column the field names.
- **Group statements:** a statement about a group supports a value for this person only when the group is named and clearly includes them ("all six patients", "P1–P4"). If the paper's per-patient table gives this person a different value, the table wins: the group-based value is `unsupported`.

## Feature status (observed or excluded)
- The span must say that this person has (observed) or explicitly does not have (excluded) the feature named in `context`.
- A table "–", "0" or "N" supports "excluded" only when a quoted legend defines it.
- **Normal findings (D-27).** A normal result rules out the abnormality it measures. Two ways of recording it are both correct:
  - the feature is the abnormality, marked excluded ("elevated CRP", excluded), and the span says the finding was normal ("CRP was normal");
  - the feature is the paper's own wording of the normal finding, marked excluded ("normal CRP levels", excluded). Read this as "the abnormality is absent". It is `supported` when the span shows the finding normal for this person; do not mark it down for reading backwards.
- **Hedged phrases.** "Suggesting", "possible", "suspected", "probable", "usually", "may" and the like support neither observed nor excluded. A status that rests only on a hedged phrase is `unsupported`; say so in the reason.

## Other field rules
- **`*_iso8601` fields:** check the conversion of the stated age (e.g. "2 years and 6 months" → P2Y6M), and that the age is the one the field names (onset, diagnosis, last evaluation), not another.
- **Enums** (sex, zygosity, inheritance, study_type, vital_status, is_proband, variant_type_as_stated) must follow from the span:
  - "de novo" needs stated parental testing;
  - "inherited maternal" needs a statement that the mother carries the variant;
  - "heterozygous" needs the paper to say so for this person or a named group including them.
- **Numbers** (year, n_patients_reported, cohort_size_as_stated) must match the span.
- **Free text not copied verbatim** (a made-up label, a summary of treatments): `supported` if the span gives the substance; `unsupported` if it adds facts the span does not contain, for this person.

## Rules
- Use only the claims file and the paper. Do not use anything you remember about the paper, its patients, the gene or the variants. No web search or web fetch, no git.
- Judge every claim. Be strict but fair: a value can be supported without copying the span's words.

## Output: one CSV file at the path given in your task
Columns: `claim_id`, `verdict`, `reason`.
- Give a `reason` of at most 20 words for every verdict that is not `supported`. It may be empty for `supported`.
- Write one row for every claim. Check that the file parses as CSV and has every `claim_id`.

Reply in under 80 words: counts per verdict, and the commonest reason for `unsupported`.
