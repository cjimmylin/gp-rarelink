Extraction rules (GP-RareLink, v1). These rules apply to every table and every row.

1. Use only the supplied document. Do not use outside knowledge about the gene, the disease, specific variants or specific patients. If the document does not state something, the value is "not reported" (for text fields) or null (for numeric and date fields). Never fill a gap from memory.
2. Every value must be supported by a verbatim quote copied exactly from the document. Do not paraphrase inside the quote. If no exact quote supports a value, do not emit the value.
3. Keep original strings. Record variant descriptions, ages, feature names and labels exactly as printed. Never convert protein-only variant descriptions into cDNA notation, never add a transcript that is not printed, never translate units.
4. Three-state phenotypes: a feature is "observed" only when the document says the person has or had it, and "excluded" only when the document explicitly says it was absent, negative or not found in that person. Silence is "not reported". Never turn silence into "excluded".
5. One row per real person per document. Relatives described in the document are their own rows with is_proband = false unless the document calls them probands. Do not merge people, and do not create a person the document does not describe.
6. Cohort tables: when a table lists many patients, extract each patient row separately with the table's own patient identifier as individual_label_in_paper. Keep the row-to-column alignment of the table; when a cell is empty or marked "-", "NA" or "ND", treat it as not reported.
7. Re-reports: if the document says that any of its patients were described in an earlier publication, record that statement and the citation in the publications table. Do not drop the patient.
8. Do not infer inheritance or zygosity. "de novo" requires that the document states parental testing showed the variant absent in both parents. "heterozygous" requires that the document says so or the gene is described as monoallelic for that person.
9. Prefer "not reported" to a plausible guess. Abstention is correct behaviour.
