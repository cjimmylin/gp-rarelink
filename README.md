# GP-RareLink

*Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease*

Rare Genomics Institute and the Stanford OVAL Lab, funded by Anthropic's AI for Science Rare Disease program. The pipeline uses SLIDERS with Claude to build GA4GH Phenopackets from published case reports, then scores them against ClinVar and OMIM.

| Start here | |
|---|---|
| `CONTEXT.md` | Scope, diseases, methods, metrics, budget, timeline (source of truth) |
| `INSTRUCTIONS.md` | Working rules for Claude and collaborators |
| `CLAUDE.md` | Loaded automatically by Claude Code; imports the two files above and the notes below |
| `NOTES_FOR_AGENTS.md` | Current status, next steps, environment limits and lessons from earlier sessions |
| `DECISIONS.md` | Open decisions, dated decision log, pre-registration deviations |
| `BUDGET.md` | Spend against each budget line, with deposits and pre-run estimates |
| `POC_DESIGN.md` | Step-by-step design for the proof-of-concept run on one disease (HA20), written for an agent to execute stage by stage |
| `preregistration/` | Analysis plan for the six-disease study (draft; frozen after the POC) |
| `grant/` | The application as submitted and the award email |
| `background/` | Annotated bibliography, manifest, grant-claim checks, fetch scripts |
| `pipeline/` | Pipeline code: `common/` (run manifests, cost), `extract/` (extraction side, never reads ground truth), `harness/` (concordance, the only reader of `data/reference/`) |
| `configs/` | Price table and run configurations |
| `scripts/` | `install_sliders.sh`: pinned SLIDERS checkout + Anthropic provider patch into the venv |
| `data/literature/<disease>/` | Corpus manifest, seeds and runbook (full text is git-ignored) |
| `tests/` | Ground-truth isolation tests and unit tests (`uv sync && uv run pytest`) |
| `docs/claude-ai-threads.md` | What was worked out in the claude.ai Project chats: setup, environment limits, open items |

**Source of truth.** This repo is canonical. The claude.ai Project "Anthropic Rare Disease" mirrors its documents for chat sessions; edit here, commit, then refresh the mirror (see `DECISIONS.md`, 2026-10-18).

**Private repository.** It holds the grant application and pre-registration material. Licensed data (OMIM), full-text articles and reference snapshots are kept out by `.gitignore`; commit manifests and download scripts instead.

**Status (2026-10-18):** Awarded 2026-08-31 ($45,000 in claude.ai credits). Pilot first (D-18): a proof-of-concept run on A20 haploinsufficiency (`POC_DESIGN.md`). Its code is built and tested offline, but it hasn't run yet; it needs network access and an Anthropic API key. The six-disease pre-registration (draft v0.5) is frozen after the pilot.
