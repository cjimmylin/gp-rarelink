# GP-RareLink interim report, version 4 (2026-11-20)

**The paper:** `run_po1/final_paper.pdf` (35 pages; main text pages 1–10), source `run_po1/final_paper.tex`
(= `run_po1/latex/final_v1.tex`). Internal review draft. It covers all twelve diseases, keeps the registered
six apart from the extension five, Majeed and the corpus addendum, and writes every human result as a boxed
"pending" marker.

**Do not send it to the calibration raters before calibration closes (2026-11-22):** it states the calibration
set's 20/20 split and names the commonest kind of unsupported claim in the gatekeeper runs.

## How it was made
- Written with the local Claude Code port of PaperOrchestra (`tools/paper-orchestra/`, `.claude/skills/paper-orchestra`,
  `.claude/agents/po-*`; copied from cjimmylin/multi-alignment at c27a6e47; Apache-2.0, see its NOTICE.md).
- Materials in `materials/`: `idea.md`, `experimental_log.md` (compiled from committed reports, each block names its
  source), `notes.md` (claims not to make, corrected grant figures, the checked references' descriptions),
  `pending_human_results.md` (the 29 placeholder ids), `extra_references.bib` (from `background/manifest.csv` by
  `analysis/paper_v4/manifest_to_bib.py`).
- Template `template/`: the ICLR 2025 style files for layout only, authors shown, and `human_results.tex` defining `\HR{id}`.
- Run `run_po1/`: outline → 22 web search tasks (69 new papers matched to Semantic Scholar/Crossref/arXiv records,
  1 rejected) and 5 figures drawn by code from the log → draft → three simulated reviews (4, 5, 5) → one refinement
  round, rejected by the tool's rule (merged score 5 → 4; clarity and presentation +1; `latex/refined_v1.pdf` kept on
  file) → formatting → an independent fact-check (`review/number_check.md`: 2,694 table numbers checked, 0 wrong;
  16 of 17 findings applied, the 17th is the circulation advice above).
- The simulated review scores are a model's judgement used to steer revisions, not evidence of quality.

## When the human results come in
1. Score them with the scripts named in `materials/pending_human_results.md` (calibration: `analysis/assessment_plan/calibration_score.py`).
2. Put the paper-level values (never per-rater results) in a JSON file, e.g. `{"cal_raters_finished": "9"}`.
3. `python3 -I analysis/paper_v4/fill_human_results.py VALUES.json reports/paper_v4/run_po1/latex/human_results.tex`
4. `python3 tools/paper-orchestra/scripts/po.py compile reports/paper_v4/run_po1/latex/final_v1.tex`, then copy the PDF to `final_paper.pdf`.
5. Re-read every sentence that holds a filled value: the text was written to read correctly whatever the value, but
   the discussion may need updating once results exist.
