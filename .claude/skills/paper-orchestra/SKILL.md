---
name: paper-orchestra
description: Write a full LaTeX research paper from raw materials (idea.md + experimental_log.md) with the PaperOrchestra multi-agent pipeline (outline → web-grounded, index-verified literature review ∥ plotting → section writing → simulated peer-review refinement → formatting), running entirely on Claude Code subagents. Use when asked to draft, write, or regenerate a paper with PaperOrchestra.
---

# PaperOrchestra (local, Claude Code edition)

Local port of PaperOrchestra (Song et al., 2026, arXiv:2604.05018; code: google-research/paper-orchestra,
Apache-2.0). All LLM work runs as Claude Code subagents on this session's subscription — no API
keys. Deterministic steps use `tools/paper-orchestra/scripts/po.py`. Full docs:
`tools/paper-orchestra/README.md`.

Let `PO=tools/paper-orchestra/scripts/po.py` (run from the repo root) and `RUN` = run directory.

## Subagents
`po-outline`, `po-lit-discovery`, `po-lit-writer`, `po-plotter`, `po-section-writer`,
`po-reviewer`, `po-refiner`, `po-formatter` (definitions in `.claude/agents/`). If a
`subagent_type` is not recognised (agents added mid-session), spawn `general-purpose` with:
"Read `.claude/agents/<name>.md` and follow it exactly as your instructions (ignore its YAML
front matter). Inputs: ...".

Give every subagent its inputs as explicit absolute paths. Run independent subagents in ONE
message so they run in parallel. Check each step's files exist before moving on
(`python3 $PO status $RUN`). Keep the user posted with one line per step.

## Step 0 — set up
1. Confirm raw materials exist: `idea.md` (or `idea_sparse.md`/`idea_dense.md`) and
   `experimental_log.md`; optional `figures/` (+ `figures/captions.json`), `notes.md`,
   `extra_references.bib` (user-curated references, merged into the bib as-is).
   If the user only has scattered notes, first build these two files with them (see README
   "Preparing raw materials") — this is the step that most determines quality.
2. `python3 $PO init --materials <dir> --template <iclr2025|cvpr2025|path> --run $RUN [--plotting] [--cutoff YYYY-MM] [--ensemble 3] [--max-reflections 3] [--no-anonymize]`
   Add `--seed-run <earlier run dir>` to reuse that run's verified citation library (discovery
   agents then re-select from `lit/library_titles.md` and search only for gaps).
   (Needs `latexmk`/`pdflatex`, `matplotlib`, `pymupdf`; install with
   `apt-get install -y texlive-latex-recommended texlive-latex-extra texlive-fonts-recommended texlive-bibtex-extra texlive-science latexmk` and `pip install matplotlib pymupdf` if missing.)

## Step 1 — Outline
Spawn `po-outline` with RUN. Then sanity-check `outline.json` yourself (valid JSON, three keys,
figures only use data in the log).

## Step 2 — Literature review ∥ Plotting (parallel)
1. `python3 $PO tasks $RUN --batches N` (N ≈ ceil(#tasks/8), max 6). Targeted hints that name a
   work already in `raw_materials/extra_references.bib` are not searched; `verify` maps them back
   to the user's keys.
2. In ONE message spawn: one `po-lit-discovery` per batch file (RUN, BATCH) **and**, if
   `use_plotting`, one `po-plotter` per `plotting_plan` entry (RUN, FIGURE_ID,
   MAX_CRITIC_ROUNDS=3).
3. When discovery is done: `python3 $PO verify $RUN` (Semantic Scholar if
   `SEMANTIC_SCHOLAR_API_KEY` is set, else Crossref/arXiv; ~1 s per candidate — run in the
   background for large batches). Look at `lit/rejected.json`: if a must-have targeted
   citation was rejected, re-run discovery for those tasks (ask for DOI/arXiv ids) and
   `verify --resume`.
4. Spawn `po-lit-writer` (RUN) → `latex/template_lit.tex`.
5. When plotters are done: `python3 $PO figures $RUN` → `latex/figures/info.json`. Look at
   each PNG yourself before continuing.

## Step 3 — Section writing
Spawn `po-section-writer` (RUN) → `latex/draft_v0.tex`, compiled.

## Step 4 — Content refinement loop (upstream: 3 rounds, ensemble of 3 reviewers)
For version `v0` (then each candidate `vK`):
1. `python3 $PO compile $RUN/latex/<tex> ` → PDF; `python3 $PO pdftext <pdf> --out $RUN/review/text_vK.txt`.
2. In ONE message spawn `ensemble` × `po-reviewer` (PAPER_TEXT, PAPER_PDF, OUT=`$RUN/review/vK_r{i}.json`).
3. Spawn `po-reviewer` MODE=meta over them → `$RUN/review/vK_meta.json`.
4. `python3 $PO merge-reviews --reviews $RUN/review/vK_r*.json --meta $RUN/review/vK_meta.json --out $RUN/review/review_vK.json`.
   If a reviewer or the meta-reviewer is stopped by a safety classifier (this happens on papers
   about deception, blackmail or scheming), retry a reviewer once at most, never write the review
   yourself, and run `merge-reviews` without `--meta` on the reviews that exist (it merges their
   points mechanically). Tell the user how many reviews each decision rests on; if a decision
   rests on fewer reviews than the comparison round, ask the user which version to keep.

Loop for k = 1..max_reflections, with `CUR` = last accepted version (starts at v0):
- Spawn `po-refiner` (RUN, ROUND=k, CURRENT_TEX, CURRENT_PDF, REVIEW=review_CUR.json) → `latex/refined_vk.tex`.
- If it did not compile → skip to next k (upstream behaviour).
- Review it as above (vk), then
  `python3 $PO decide --old $RUN/review/review_CUR.json --new $RUN/review/review_vk.json --round k --agent-plan $RUN/review/refiner_worklog_vk.json --worklog $RUN/review/refinement_worklog.json`.
- `accept` true → CUR = vk; `continue` false → stop the loop (revert to CUR).

## Step 5 — Formatting
Spawn `po-formatter` (RUN, CURRENT_TEX, CURRENT_PDF of CUR). If `formatted_v1.tex` compiled,
it is final; otherwise CUR is final. Copy final to `$RUN/final_paper.tex` and
`$RUN/final_paper.pdf` (the pdf compiled inside `latex/`).

## Step 6 — Independent fact-check, then human-side checks (not in upstream; do them)
- Spawn a fresh `general-purpose` agent with no stake in the draft to trace every number and claim
  in the final .tex against `experimental_log.md` (same quantity, condition, denominator; dropped
  hedges; project rules in `notes.md`), writing `review/number_check.md` and editing nothing.
  Verify its findings against the log yourself, apply the fixes, recompile, and re-check that the
  main text still fits the page limit (fixes add words).
- `python3 $PO check $RUN/final_paper.tex --map $RUN/lit/citation_map.json` (run from `latex/`
  copy) — zero unknown keys.
- Spot-check every number in tables/abstract against `experimental_log.md`.
- Report to the user: final path, page count, review score trajectory (from
  `review/refinement_worklog.json`), #verified citations, rejected citations worth a manual
  look, and any reviewer weaknesses that need NEW experiments (the pipeline never fabricates
  them; they are the user's to-do list).
