# Majeed syndrome: the extension session's first-pass corpus (2026-11-14)

Two sessions built a Majeed syndrome corpus within a day of each other. The files in this folder are the first one, exactly as the extension session committed them on branch `claude/affectionate-babbage-tfrjur` (PubMed query with the shared case/patient filter and one key review; 204 records). Under the extension addendum's eligibility rule (§2: at least 15 eligible primary reports with open full text) this corpus had 10, so Majeed syndrome was dropped from the registered extension (`DECISIONS.md`, D-52).

The corpus one level up (`data/literature/majeed/`) is the second: a wider search with every available method, plus copies found by hand, made at Jimmy's request on 2026-11-15. The exploratory run `pv1s-majeed` used that one. At the merge of 2026-11-15 the two sets of files collided on 14 paths; the later corpus stays in place and this one was moved here so that neither overwrites the other.

- `manifest.csv`, `corpus_stats.json`, `oa_elsewhere.*`, `study_type_spotcheck.csv`, `screening/`, `screening_fulltext/`, `seeds/refs_ferguson2021.csv`: the first-pass files, unchanged.
- `config_entry.yaml`: the Majeed entry of `configs/diseases.yaml` as that session wrote it. No script reads it.
- `stage4_config.json`: that session's `configs/stage4/majeed.json` (same gene and transcript; a shorter disease-label rule). No script reads it.

Nothing here is read by the pipeline or by any report script.
