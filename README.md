# GP-RareLink

*Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease*

Rare Genomics Institute and the Stanford OVAL Lab, funded by Anthropic's AI for Science Rare Disease program. The pipeline uses SLIDERS with Claude to build GA4GH Phenopackets from published case reports, then scores them against ClinVar and OMIM.

| Start here | |
|---|---|
| `CONTEXT.md` | Scope, diseases, methods, metrics, budget, timeline (source of truth) |
| `INSTRUCTIONS.md` | Working rules for Claude and collaborators |
| `CLAUDE.md` | Loaded automatically by Claude Code; imports the two files above |
| `DECISIONS.md` | Dated decisions and pre-registration deviations |
| `BUDGET.md` | Spend against each budget line, with pre-run estimates |
| `POC_DESIGN.md` | Step-by-step design for the proof-of-concept run on one disease (HA20), written for an agent to execute stage by stage |
| `grant/` | The application as submitted |
| `background/` | Annotated bibliography, manifest, grant-claim checks, fetch scripts |
| `pipeline/` | Pipeline code: `common/` (run manifests, cost), `extract/` (extraction side, never reads ground truth), `harness/` (concordance, the only reader of `data/reference/`) |
| `configs/` | Price table and run configurations |
| `tests/` | Ground-truth isolation tests and unit tests (`uv sync && uv run pytest`) |

**Source of truth.** This repo is canonical. The claude.ai Project "Anthropic Rare Disease" mirrors its documents for chat sessions; edit here, commit, then refresh the mirror (see `DECISIONS.md`, 2026-10-18).

**Private repository.** It holds the grant application and pre-registration material. Licensed data (OMIM), full-text articles and reference snapshots are kept out by `.gitignore`; commit manifests and download scripts instead.

**Status:** Month 1 (data and setup).
