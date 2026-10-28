# Locate-and-judge instructions, v1 (GP-RareLink SLIDERS ablation, D-42)

*The support judge of the ablation pilot (`reports/sliders_ablation_design.md` §4.1). Unlike gatekeeper v4, which is handed the extractor's own quote, this judge receives values without any quote and must find the evidence itself. Written 2026-10-28, before the run; not changed afterwards.*

You audit values that were extracted from one published paper. For each value you must find the passage in the paper that supports it **for the person the row is about**, quote that passage, and judge whether it supports the value. You do not re-extract anything, and you do not judge whether the value is the best possible choice.

## Inputs (paths are given in your task)
- **A claims file** (CSV) with columns:
  - `claim_id`;
  - `table`: individuals, variants, phenotypic_features or phenotype_checklist;
  - `individual`: the label of the person the row is about, as the extractor wrote it;
  - `context`: the feature, checklist item or variant the row is about (empty for person-level fields such as sex);
  - `field` and `value`: the extracted field and its value (JSON).
- **The paper**: a Markdown file (a `## Supplementary material` section, if present, is part of it).

## Step 1: find the person
Work out who `individual` is in the paper: the paper's own label, a table row or column, a relative named by relation ("mother of P1"), or the single patient of a case report. If you cannot tell which person the label means, say so in `reason` and judge the claim `not_found`.

## Step 2: find the evidence
Search the paper (text, tables, legends, supplementary material) for the passage that states the value for this person. Copy the best passage **verbatim** into `evidence` (the smallest sentence fragment, table cell or table-row segment that does the work; under 300 characters; exact characters, no paraphrase). If several passages are needed, join them with ` || `. If no passage states anything about this value for this person, leave `evidence` empty.

Record in `about` whom the passage you found is about. Use exactly one of:
- `this_person`: the row's person, by label, by their own table row or column, or by an unambiguous reference;
- `named_group`: a group the paper names that clearly includes this person ("all six patients", "P1–P4", "both sisters");
- `cohort_general`: a statement about the cohort or the study's patients or variants in general, without saying it holds for each of them;
- `other_person`: someone else (another patient, a relative, a person from another paper);
- `paper`: the paper itself;
- `unclear`: you cannot tell;
- `none`: you found no passage.

## Step 3: verdict
- `supported`: the passage, read in its place in the paper, states the value for this person. A value can be supported without copying the paper's words (for example "observed" for a feature the paper says the person has; "male" for "a 4-year-old boy"; "P2Y" for "2 years").
- `partially_supported`: the passage supports part of the value, or supports it only with an extra step the paper does not state. Examples: a range recorded as one number; "fever" recorded as "recurrent fever"; a value read by its position from a cell that stacks several patients' values.
- `unsupported`: the passage does not support the value for this person, or contradicts it. This includes a value about someone else or about a group that does not clearly include this person; a negation missed or invented; a table cell read from the wrong row or column; a status resting only on a hedged phrase ("possible", "suspected", "suggesting"); a variant field (zygosity, inheritance, type, pathogenicity) taken from a statement about the cohort's variants in general or from another person's variant.
- `not_found`: no passage in the paper says anything about this value for this person. For a phenotype marked `excluded`, this means the exclusion rests on silence; for `observed` or a variant field, it means the value does not come from the paper.

Three rules that matter most:
- **Silence is not exclusion.** A feature marked `excluded` is supported only by a passage that says the feature was absent, negative or not found in this person (or in a named group that clearly includes them). A table "–", "0" or "N" supports it only when the legend or text defines that symbol as absent.
- **The person link.** A value that appears word for word in the paper is still `unsupported` when the passage is about another person, another variant, or a whole cohort this person is not clearly part of. Zygosity, inheritance, variant type and pathogenicity must be stated for this person's variant (their own row, column or sentence, or a named group that includes them).
- **Inheritance and de novo.** "de novo" needs stated parental testing; "inherited maternal" needs a statement that the mother carries the variant; otherwise `unsupported`.

## Rules
- Use only the claims file and the paper. Do not use anything you remember about the paper, its patients, the gene or the variants. No web search or web fetch, no git, no other repository file.
- Judge every claim. Be strict but fair.

## Output: one CSV file at the path given in your task
Columns: `claim_id`, `about`, `verdict`, `evidence`, `reason`.
- `reason`: at most 20 words for every verdict that is not `supported`; may be empty for `supported`.
- Write one row for every claim. Check that the file parses as CSV, has every `claim_id` exactly once, and that every `evidence` string occurs verbatim in the paper.

Reply in under 80 words: counts per verdict, and the commonest reason for `unsupported` or `not_found`.
