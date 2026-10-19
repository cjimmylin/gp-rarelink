# HPO binding instructions, v1 (GP-RareLink pilot, Stage 4; Claude Code route, D-20)

You map short phenotype phrases, quoted from published case reports, to terms of the Human Phenotype Ontology (HPO). A script will check every answer against the pinned HPO release, so an ID that does not exist, or a name that does not match the ID, is rejected.

## Inputs (paths are given in your task)
- **A batch file** (CSV) with columns `text_id`, `feature_text`, `label_candidate`. `feature_text` is the phrase as printed in the paper. `label_candidate` is an earlier suggestion, which may be empty or wrong.
- **The pinned HPO release**, `hp.obo`. Search it with grep or a short Python script. Each `[Term]` block has `id:`, `name:`, `synonym:` lines and `is_obsolete: true` for obsolete terms.

## What to do for each row
1. Find the HPO term that the phrase supports **fully**, and that is as specific as the phrase allows **but no more specific**.
   - "polyarthritis" → `Polyarthritis` if it exists, otherwise `Arthritis`.
   - "ulcers" with no site → `NONE`, because the site is unknown.
   - "elevated IgM" → the circulating IgM concentration term.
2. Use only current terms. Never pick a term with `is_obsolete: true`.
3. Answer `NONE` when no term fits. Examples:
   - treatments, drugs and procedures;
   - laboratory values without a stated direction or abnormality;
   - diagnoses that are diseases rather than phenotypes (e.g. "Behçet's disease", "HA20");
   - statements of absence of a group ("neither BD symptoms");
   - phrases too vague to place ("GI", "symptoms").
4. The status (observed or excluded) is handled elsewhere. Bind the phenotype named, even when the phrase says it was absent; for example, "no uveitis" → `Uveitis`.
5. Do not use anything you remember about specific papers or patients. Use only the phrase and `hp.obo`.

## Output: one CSV file at the path given in your task
Columns, in this order: `text_id`, `hpo_id`, `hpo_name`, `match`, `note`.
- `hpo_id`: e.g. `HP:0001369`, or `NONE`.
- `hpo_name`: the term's `name:` line copied exactly from `hp.obo` (empty for NONE).
- `match`:
  - `exact`: the phrase is the term's name or a synonym;
  - `close`: same meaning, different wording;
  - `broader`: the term is more general than the phrase, because no exact term exists;
  - `none`.
- `note`: at most 15 words, only when useful (e.g. why NONE).

Write one row for **every** input row. Validate that the file parses as CSV, that every row is present, and that each `hpo_id` exists in `hp.obo` with that exact name. Then reply in under 80 words: rows written, how many NONE, and anything unusual.
