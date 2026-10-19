# Supplementary files (HA20 pilot, D-22 item 7)

Fetched 2026-10-19 from Europe PMC (`/rest/<PMCID>/supplementaryFiles`) by
`pipeline/extract/corpus/fetch_supplementary.py`; converted and appended to the
paper Markdown by `pipeline/extract/corpus/supplementary_to_text.py`.
The files themselves are in `files/` (git-ignored) and are never committed or
redistributed. `manifest.csv` (one row per file, with size, SHA-256 and the
paper's licence class) and `conversion.csv` (what was appended) are committed.

## Licensing check

Licence class of the 85 full-text papers, read from each paper's JATS licence
statement (`manifest.csv`, column `licence_class`):

| Licence class | Papers |
|---|---|
| CC BY | 59 |
| CC BY-NC | 12 |
| text-and-data-mining terms (non-CC) | 9 |
| CC BY-NC-ND | 5 |

Every class allows text mining for academic research, which is the only use
here: the files are read by extraction helpers, and only short verbatim
quotes appear in the committed extraction outputs, as for the main text. For
the non-commercial and no-derivatives licences this is non-commercial
research use, and no adapted version of the files is distributed. The
text-and-data-mining class covers PMC's text-mining licence and Nature's terms
for author manuscripts; both permit text and data mining for academic
research.

## What was fetched

- Papers with at least one document or table file kept: 30 of 85.
- File statuses: kept 59; zip_without_document_files 44; none (HTTP 200) 11; skipped_too_large 1.
  "zip_without_document_files" means the zip held only figures or media.
- Conversion, filter v1 (used by run-2, 2026-10-19): included_full 33; skipped_no_TNFAIP3_or_A20_mention 23;
  included_excerpt 3. Files that never mention TNFAIP3, A20 or HA20 were not appended. That also dropped
  a per-patient variant table that never names the gene (42128528) and some case-report lab tables.
  Papers with a "## Supplementary material" section: 21. Run-2's Markdown is kept locally in
  `../fulltext_md_run2/`, with checksums in `runs/poc-ha20-run-2/markdown_sha256.csv`.
- Conversion, filter v2 (D-24, 2026-10-19; current `conversion.csv`):
  - every file is kept except administrative ones (conflict-of-interest forms, reporting checklists,
    peer-review files, data-sharing statements);
  - pandoc's HTML tables become pipe tables, and lines stacked in one cell are joined with " / ";
  - entities are decoded.

  Result: included_full 52; included_excerpt 2; skipped_administrative 5. Papers with a supplementary
  section: 30.
- The supplement of 39167656 (21 MB PDF) was fetched with a 30 MB cap; the default cap is 15 MB.
  One file remains skipped as too large: a 50 MB figure-data PDF of 37342083.
