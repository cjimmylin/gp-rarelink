# PaperOrchestra — local Claude Code edition

A local port of **PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper
Writing** (Yiwen Song, Yale Song, Tomas Pfister, Jinsung Yoon — Google Cloud AI Research, 2026;
[arXiv:2604.05018](https://arxiv.org/abs/2604.05018), [project page](https://yiwen-song.github.io/paper_orchestra/),
[code](https://github.com/google-research/paper-orchestra), Apache-2.0). This port is based on upstream
commit `ca1b3fa` (2026-05-17).

Upstream calls Gemini / OpenAI APIs. **This version runs every LLM step as a Claude Code
subagent**, so it runs on the Claude subscription of whoever drives the session. It needs no
API keys and no OpenRouter.

## What the pipeline does

Input: *pre-writing* materials — an idea summary and an experimental log (plus optional
figures) — and a venue LaTeX template with written guidelines. Output: a compiled,
citation-verified LaTeX manuscript.

| Step | Upstream agent | Here | What it produces |
|---|---|---|---|
| 1 | Outline Agent | `po-outline` subagent | `outline.json`: plotting plan, literature-search plan (intro = macro context, related work = 2–4 technical clusters with limitation hypotheses), section plan with exhaustive citation hints |
| 2a | Literature Review Agent: discovery (Gemini + Google Search) | `po-lit-discovery` × N in parallel (WebSearch) | candidate papers per search task |
| 2b | Literature Review Agent: Semantic Scholar enrichment | `po.py verify` | every candidate must match a real index record (S2 → Crossref → arXiv; fuzzy-title > 70, published before the cutoff) → `references.bib`, `citation_map.json`, `outline_v1.json` |
| 2c | Literature Review Agent: writer | `po-lit-writer` | Introduction + Related Work citing ≥ 90 % of verified papers |
| 2d | Plotting Agent (PaperBanana: planner → stylist → visualizer → critic × 3 → caption) | `po-plotter` × figures, in parallel with 2a–2c | matplotlib-rendered figures + captions, visually self-critiqued |
| 3 | Section Writing Agent | `po-section-writer` | full draft: method, results tables from the log, all figures, limitations, conclusion |
| 4 | Content Refinement Agent + AgentReview reviewer ensemble | `po-reviewer` × 3 + meta, `po-refiner`, `po.py decide` | up to 3 rounds of "rebuttal via revision"; a round is kept only if the simulated review score rises (or holds with sub-scores net-improved), otherwise the loop reverts and stops |
| 5 | Formatting pass (VLM page inspection) | `po-formatter` | layout fixes checked against rendered pages and page limits |

The orchestration lives in the `/paper-orchestra` skill (`.claude/skills/paper-orchestra/SKILL.md`).
The subagents live in `.claude/agents/po-*.md`. The deterministic steps live in `scripts/po.py`.

## How to run it

In a Claude Code session in this repo:

```
/paper-orchestra  write a paper from <materials dir> with the iclr2025 template into <run dir>, with plotting
```

Or step by step (what the skill does):

```bash
python3 tools/paper-orchestra/scripts/po.py init --materials path/to/raw_materials --template iclr2025 --run path/to/run --plotting
python3 tools/paper-orchestra/scripts/po.py status path/to/run
```

The run directory layout:

```
RUN/config.json  raw_materials/  outline.json  outline_v1.json
RUN/lit/      search_tasks.json batches/ candidates/ registry.json rejected.json citation_map.json
RUN/plots/<figure_id>/  plan.md plot.py critic.json result.json
RUN/latex/    template.tex guidelines.md *.sty references.bib figures/  template_lit.tex draft_v0.tex refined_vK.tex formatted_v1.tex
RUN/review/   vK_r{i}.json vK_meta.json review_vK.json refinement_worklog.json format_review.json
RUN/final_paper.tex  final_paper.pdf
```

**Dependencies:** `latexmk` and `pdflatex` (TeX Live, including the `-latex-extra`, `-science`
and `-bibtex-extra` packages), plus `matplotlib` and `pymupdf`. The verifiers use only the Python standard library.
The skill gives the install commands. Optionally set `SEMANTIC_SCHOLAR_API_KEY` to use
Semantic Scholar, which is upstream's verifier. Without a key, the shared keyless pool is usually
rate-limited, and `po.py` falls back to Crossref and arXiv automatically.

## Preparing raw materials (most of the quality comes from here)

Upstream's benchmark inputs (PaperWritingBench) are:
- **`idea.md`** — the method and theory: the problem, the core idea, formal definitions, the
  contributions, and the design rationale. "Sparse" summaries are fine; the outline agent expands them.
- **`experimental_log.md`** — every number that may appear in the paper: setup (models, data,
  n, prompts, metrics, statistical tests), all result tables with exact values and CIs, ablations,
  and the observations a figure would show, written as standalone factual statements.
  Record the limitations and failed or non-replicating results here too.

Optional additions in this port:
- `figures/` with `captions.json` (`{"file.png": "caption"}`) — for figures you already have;
  use them instead of `--plotting` or alongside it.
- `notes.md` — positioning notes, target venue, the claims you must not make.
- `extra_references.bib` — references you have already verified by hand. They are appended to
  the bibliography and their keys become citable.

## Local adaptations vs upstream (deliberate)

1. **LLM backend:** Claude Code subagents instead of Gemini or OpenAI calls. Web discovery uses
   Claude's WebSearch in place of Gemini Google-Search grounding.
2. **Citation verification:** Semantic Scholar is tried first, as upstream does. Explicit DOIs and
   arXiv IDs from the discovery agent, then Crossref and arXiv title search, act as keyless
   fallbacks. Papers with no index abstract are kept with a clearly labelled web summary instead
   of being dropped; this matters for psychology books and chapters. Use `--strict-abstract`
   for the upstream behaviour.
3. **Figures are drawn by code.** Upstream drew diagrams with an image-generation model. Here
   every plot and diagram is matplotlib code with hard-coded values from the log, so figures
   are exact and reproducible. The PaperBananaBench few-shot retrieval step is dropped because
   that reference pool is not public. The planner, stylist and critic prompts are kept.
4. **Grounding prompt:** upstream's "no prior knowledge at all" rule exists to prevent leakage
   in a reconstruction benchmark. Here it is replaced by `GROUNDING.md`. Claims about our own work
   must come only from the materials, and claims about other work only from the verified
   citation library. Anonymity is optional (`--no-anonymize`).
5. **Limitations are kept.** Upstream's refinement prompt said "Never explicitly state a
   limitation". That line is removed, and documented limitations must stay in the paper.
6. **Added static checks** (`po.py check`) for unknown cite keys, missing figure files and
   unbalanced environments after every LaTeX-writing step, plus a final number spot-check.
7. Upstream's batch-over-dataset runner, Streamlit demo and autoraters (citation F1, SxS
   evaluation) are not ported. The AgentReview reviewer is ported because the refinement loop
   uses it.

## Caveats

- This is a drafting tool. As the upstream ethics statement says, the authors remain
  accountable for every claim, number and citation. Read the whole PDF, and check the
  verified-but-unread citations against the actual papers before submitting.
- The simulated-review score is an LLM judgement used to steer revisions. It is not evidence
  about the paper's quality, so don't report it as such.
- Cost: a full run spawns roughly 25–40 subagents, depending on the number of figures, search
  batches and refinement rounds. Use `--ensemble 1 --max-reflections 1` for a quick draft.

## Files

- `scripts/po.py` — deterministic CLI: `init`, `tasks`, `verify`, `figures`, `render`, `compile`,
  `snapshot`, `pdftext`, `check`, `merge-reviews`, `decide`, `status`.
- `GROUNDING.md` — the integrity rules every agent reads.
- `templates/iclr2025`, `templates/cvpr2025` — vendored from upstream. To add a venue, create a
  folder with `template.tex` (empty sections, `\bibliography{references}`), `guidelines.md`
  (page limit, citation commands, anonymity, figure rules) and the style files.
- `LICENSE` — upstream Apache-2.0 license; `NOTICE.md` — attribution and modifications.
