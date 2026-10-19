# Gatekeeper instructions, v4 (GP-RareLink; Claude Code route, D-20; POC_DESIGN.md §3.9)

*v2 applied D-27 and D-28 (Jimmy, 2026-10-19): every value is judged, including text copied from its own quote; the quote must tie the value to this person; normal findings, group statements and hedged phrases have stated rules. v3 applies D-29 (Jimmy, 2026-10-19): before judging, you record who the quote is about; variant fields follow the extraction rule for one person's variant; a normal finding recorded in the inverted form is partially supported. v4 applies D-31 (Jimmy, 2026-10-19): a value taken by position from a stacked multi-patient cell is at most partially supported.*

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

## Step 1: who is the quote about? (D-29)
Before you give a verdict, read the span in its place and record in the `about` column who or what it describes. Use exactly one of:
- `this_person`: the row's person, by label, by their own table row or column, or by an unambiguous reference ("our patient" in a single-patient report);
- `named_group`: a group the paper names that clearly includes this person ("all six patients", "P1–P4", "both sisters"), including every patient of the study when the statement covers all of them and this person is one ("none of our patients had uveitis");
- `cohort_general`: a statement about the cohort, the study's variants or patients that does not say it holds for each of them, or an unnamed group ("patients with TNFAIP3 variants often had", "most patients", "the variants included");
- `other_person`: someone else (another patient, a relative, a person from another paper);
- `paper`: the paper itself (publications rows);
- `unclear`: you cannot tell.

Then judge. For a person-level field, `cohort_general`, `other_person` and `unclear` mean the value is `unsupported` for this person, unless the field is about the paper. `named_group` supports a value only under the group rule below.

## The person link (D-28)
Matching words are not enough. A value that appears word for word in its quote is still `unsupported` when the quote, read in place, is about another person, another variant, or a whole cohort that this person is not clearly part of. Check:
- **Variant fields** (gene, cDNA, protein, zygosity, inheritance, pathogenicity, variant type, ACMG criteria, functional evidence): the span must tie the value to this person's variant: the person's own table row or column, or a sentence that names this person or their variant. A sentence about "patients with TNFAIP3 variants" in general does not give one carrier's zygosity or pathogenicity. In particular (D-29):
  - a list of several values for a group ("splice-site, frameshift and nonsense variants") does not give one person's value: `unsupported` for a single value taken from it;
  - a group statement does not hold for a person the paper gives a different or open status elsewhere (variant not identified or not determined, mosaic or somatic, VUS, relative not tested): `unsupported`;
  - a row about a relative takes the proband's variant facts only when the paper states them for the relative.
- **Text copied from a table:** check that the cell is in this person's row and under the column the field names.
- **Stacked cells (D-31).** A cell holding several values separated by ` / ` (one per patient, stacked) supports a value for this person only when the paper labels that value for this person. A value assigned by its position in the stack alone is at most `partially_supported`; say "positional stacked cell" in the reason.
- **Group statements:** a statement about a group supports a value for this person only when the group is named and clearly includes them ("all six patients", "P1–P4"). If the paper's per-patient table gives this person a different value, the table wins: the group-based value is `unsupported`.

## Feature status (observed or excluded)
- The span must say that this person has (observed) or explicitly does not have (excluded) the feature named in `context`.
- A table "–", "0" or "N" supports "excluded" only when a quoted legend defines it.
- **Normal findings (D-27, D-29).** A normal result rules out the abnormality it measures. It can be recorded two ways:
  - the feature is the abnormality, marked excluded ("elevated CRP", excluded), and the span says the finding was normal ("CRP was normal");
  - the feature is the paper's own wording of the normal finding, marked excluded ("normal CRP levels", excluded). This inverted form is `partially_supported` (D-29): the finding is right, but the record says the normal result is absent. Say "inverted normal finding" in the reason.
  - The first form is `supported`.
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
Columns: `claim_id`, `about`, `verdict`, `reason`.
- Give a `reason` of at most 20 words for every verdict that is not `supported`. It may be empty for `supported`.
- Write one row for every claim. Check that the file parses as CSV and has every `claim_id`.

Reply in under 80 words: counts per verdict, and the commonest reason for `unsupported`.
