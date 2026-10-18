# Per-paper extraction instructions, v2 (GP-RareLink pilot, A20 haploinsufficiency; Claude Code route, D-20)

*Changes from v1 come from the smoke test (`reports/poc_stage2_smoke_findings.md`) and from decision D-21; they are marked "(v2)".*

You extract structured evidence from **one** published paper for a literature-curation study of A20 haploinsufficiency (HA20), the disease caused by germline *TNFAIP3* variants. Your output is checked by script (every quote must be found verbatim in the paper) and then by a separate reviewer, so accuracy and honest abstention matter more than completeness.

## Inputs (paths are given in your task)

1. **The paper**: a Markdown file converted from the PMC or Europe PMC full text. Its first lines give the PMID and title. (v2) Merged table cells are now repeated in every row they cover, so each table row carries its own patient label.
2. **The schema**: `pipeline/extract/claude_code/schema_ha20_v2.json`. It defines five tables, their fields, types, allowed values, and a description for each.
3. **The rules**: `pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md`. Apply all nine.

**What you may read.** Read only these three files.
- Do not open any other file in the repository.
- Do not use web search or web fetch.
- Do not use anything you remember about this paper, its authors, its patients, the gene or the variants.

**What counts as missing.** If the paper doesn't say it, the value is missing (see "Values" below).

## Output: one JSON file, at the path given in your task

```json
{
  "pmid": "<from the paper's header line>",
  "instructions_version": "extract_v2",
  "reports_individuals_with_tnfaip3_variant": true,
  "relevance_note": "<one sentence, with a short quote, saying why>",
  "method_note": "<how you worked, e.g. whether a script transcribed a table; list any contradictions you found in the paper>",
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
- **Missing values (v2).** Follow each field's schema description.
  - Where the description says "null", use `{"value": null, "span": null}`.
  - Otherwise, text and enum fields take `{"value": "not reported", "span": null}`, and numeric, date and boolean fields take `{"value": null, "span": null}`.
- **`pmid` fields.** The value comes from the header line; the span is that header line, e.g. `"PMID: 12345678"`.
- **`*_iso8601` fields.** These are your conversion of the matching original-text field. Give them only when the original text states a number, and use the same span as the original-text field.
- **`hpo_label_candidate` and `hpo_id_candidate`.** These are your suggestions. Give an ID only if you are sure of it; otherwise null. Their span is `null`.
- **`checklist_feature`.** The span is `null`, because the names come from the schema.
- **Age at diagnosis (v2).** Record it in `age_at_diagnosis_*`. Don't put it in onset or last evaluation.

### Spans
- **Every non-missing value needs a span**, except the fields listed just above.
- **Copy exactly.** A span is copied character for character from the paper Markdown, including unusual spaces and symbols. Never paraphrase, correct or join text that isn't contiguous.
- **Keep it short.** Use the smallest sentence fragment, table cell or table-row segment that supports the value. That is normally under 300 characters.
- **Tables with patients as rows.** Quote a contiguous piece of the row from the patient label through the cell.
- **Tables with patients as columns (v2).** Quote the row from its row label through that patient's cell, e.g. `| Sex | F | M` for the second patient column. Name the column header once in `method_note`.
- **Multiple places (v2).** If support sits in several places, `span` may be a list of exact quotes:
  - up to **five** for `treatment_summary`, `functional_evidence_statement`, `parental_testing_statement` and `clinical_diagnosis_basis`;
  - up to **three** for any other field.

### Rows
- **`publications`:** exactly one row for this paper.
- **`individuals`:** one row per person the paper describes with clinical or genetic information, including affected or tested relatives, following rules 5 and 6. Use the paper's own label for each person.
  - **(v2)** People taken from a table or summary of previously published cases (for example a literature table in a case report, or a review) are their own rows. Fill `source_reference_in_review` with the reference the paper gives for each, verbatim.
- **`variants`:** one row per (person, variant).
  - **(v2)** `variant_original_string` is the **shortest** contiguous text giving the variant, not a whole sentence. Put the transcript, cDNA and protein parts in their own fields.
  - **(v2)** Record a variant in another gene only when the paper attributes it to one person unambiguously. If the attribution is contradictory, leave it out and say so in `method_note`.
- **`phenotypic_features`:** one row per feature the paper explicitly reports present (`observed`) or explicitly reports absent (`excluded`) for that person. No rows for features the paper doesn't mention.
- **`phenotype_checklist`:** for **every** individual, one row for **each** of the 20 checklist features in the schema's description of that table, using the names exactly as listed there. Status is `observed`, `excluded` or `not reported` under rule 4.
- **Label consistency.** `individual_label_in_paper` must be identical across tables for the same person.

### Absence and evidence basis (v2, decision D-21)
- **`evidence_basis` is required** on every `phenotypic_features` row, and on every checklist row whose status is not `not reported`.
- **Group statements.** You may mark a feature `excluded` for a person from a statement about a group **only when the statement names the group explicitly**, e.g. "only Pt3 of the four patients had recurrent fevers". Such rows take `evidence_basis = "inferred from group statement"`.
  - Counts without names ("arthritis in 2/4") do not exclude anyone.
- **Narrow and broad features.** A narrower absence never excludes a broader checklist item. "No arthritis" does not exclude "arthritis or arthralgia"; leave that item `not reported` unless arthralgia is also addressed. The same applies to other composite items, e.g. "skin lesions (rash, folliculitis, erythema nodosum)".
- **Contradictions inside the paper.** If the paper says both that a person has a feature and that they don't:
  - emit both `phenotypic_features` rows, each with its own span;
  - set that checklist item to `not reported`;
  - list the contradiction in `method_note`.

### When the paper reports no one with a *TNFAIP3* variant
For example, a review without patient-level detail, or a paper about something else:
- set `reports_individuals_with_tnfaip3_variant` to `false`;
- fill the `publications` row;
- leave the other tables empty.

### Large papers
If the output is long, you may build it in parts with a short Python script and combine the parts.
- Every value must still come from your reading of the paper.
- If a script transcribes a table, check its output against the table and say so in `method_note`.
- Use only your own scratch directory (given in your task) for temporary files.

## Finish
1. Validate that your file parses as JSON.
2. Check every span occurs verbatim in the paper.
3. Check every row has every schema field.
4. Reply with:
   - the number of rows per table;
   - the number of individuals;
   - anything you were unsure how to record.
