# Per-paper extraction instructions, v1 (GP-RareLink pilot, A20 haploinsufficiency; Claude Code route, D-20)

You extract structured evidence from **one** published paper for a literature-curation study of A20 haploinsufficiency (HA20), the disease caused by germline *TNFAIP3* variants. Your output is checked by script (every quote must be found verbatim in the paper) and then by a separate reviewer, so accuracy and honest abstention matter more than completeness.

## Inputs (paths are given in your task)

1. **The paper**: a Markdown file converted from the PMC or publisher full text. Its first lines give the PMID and title.
2. **The schema**: `pipeline/extract/sliders_adapter/schema_ha20.json`. It defines five tables, their fields, types, allowed values, and a description for each.
3. **The rules**: `pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md`. Apply all nine.

**What you may read.** Read only these three files.
- Do not open any other file in the repository.
- Do not use web search or web fetch.
- Do not use anything you remember about this paper, its authors, its patients, the gene or the variants.

**What counts as missing.** If the paper doesn't say it, the value is "not reported" (or null for numbers, dates and booleans).

## Output: one JSON file, at the path given in your task

```json
{
  "pmid": "<from the paper's header line>",
  "instructions_version": "extract_v1",
  "reports_individuals_with_tnfaip3_variant": true,
  "relevance_note": "<one sentence, with a short quote, saying why>",
  "method_note": "<one or two sentences: how you worked, e.g. whether you used a script to transcribe a table>",
  "tables": {
    "publications": [ROW],
    "individuals": [ROW, ...],
    "variants": [ROW, ...],
    "phenotypic_features": [ROW, ...],
    "phenotype_checklist": [ROW, ...]
  }
}
```

A **ROW** is an object with every field of that table, using the field names exactly as in the schema. Each field maps to a **cell**:

```json
{"value": <value>, "span": "<exact quote from the paper>"}
```

### Values
- **Type.** Use the schema's type for each field. Enum fields take only the listed strings.
- **Missing.** When the paper doesn't state something:
  - text and enum fields: `{"value": "not reported", "span": null}`;
  - numeric, date and boolean fields: `{"value": null, "span": null}`.
- **`pmid` fields.** The value comes from the header line; the span is that header line, e.g. `"PMID: 12345678"`.
- **`*_iso8601` fields.** These are your conversion of the matching original-text field. Give them only when the original text states a number, and use the same span as the original-text field.
- **`hpo_label_candidate` and `hpo_id_candidate`.** These are your suggestions; they are checked later against a pinned HPO release.
  - Give an ID only if you are sure of it; otherwise null.
  - Their span is `null`, because the feature text's own span carries the evidence.

### Spans
- **Every non-missing value needs a span.** The only exceptions are the HPO candidates above.
- **Copy exactly.** A span is copied character for character from the paper Markdown: same punctuation, same symbols, same spelling. Never paraphrase, correct or join text that isn't contiguous.
- **Keep it short.** Use the smallest sentence fragment, table cell or table-row segment that supports the value. That is normally under 300 characters.
- **Table values.** For a value read from a table, quote a contiguous piece of that table row as it appears in the Markdown, from the patient identifier through the cell. That way the quote shows which patient the cell belongs to.
- **Multiple places.** If support sits in two or three places, `span` may be a list of up to three exact quotes.

### Rows
- **`publications`:** exactly one row for this paper.
- **`individuals`:** one row per person the paper describes with clinical or genetic information, including affected or tested relatives, following rules 5 and 6. Use the paper's own label for each person.
- **`variants`:** one row per (person, variant). Copy the variant string exactly as printed (rule 3).
- **`phenotypic_features`:** one row per feature the paper explicitly reports present (`observed`) or explicitly reports absent (`excluded`) for that person. No rows for features the paper doesn't mention.
- **`phenotype_checklist`:** for **every** individual, one row for **each** of the 20 checklist features in the schema's description of that table. Use the feature names exactly as listed there. Status is `observed`, `excluded` or `not reported` under rule 4; only `observed` and `excluded` need a span.
- **Label consistency.** `individual_label_in_paper` must be identical across tables for the same person.

### When the paper reports no one with a *TNFAIP3* variant
For example, a review without patient-level detail, or a paper about something else:
- set `reports_individuals_with_tnfaip3_variant` to `false`;
- fill the `publications` row;
- leave the other tables empty.

A review that tabulates individual patients from earlier papers **does** count. Extract those patients, use the review's own label for each, and say in `method_note` that the rows come from a review table.

### Large papers
If the output is long (for example a cohort table with many patients), you may build it in parts with a short Python script and combine the parts.
- Every value must still come from your reading of the paper.
- If a script transcribes a table, check its output against the table and say so in `method_note`.
- Write only your output file, plus temporary files in the same output directory, which you delete before finishing.

## Finish
Validate that your file parses as JSON. Then reply with:
- the number of rows per table;
- the number of individuals;
- anything in the paper you were unsure how to record. These notes help improve the schema.
