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
| `BUDGET.md` | Credit spend against each budget line |
| `preregistration/` | Analysis plan (draft, not yet frozen) |
| `grant/` | The application as submitted and the award email |
| `background/` | Annotated bibliography, manifest, grant-claim checks, fetch scripts |

**Private repository.** It holds the grant application and pre-registration material. Licensed data (OMIM), full-text articles and reference snapshots are kept out by `.gitignore`; commit manifests and download scripts instead.

**Status:** Month 1 (data and setup). Awarded 2026-08-31 ($45,000 in claude.ai credits). Pre-registration drafted (v0.3, 2026-10-18), waiting on the remaining open decisions in `DECISIONS.md` before it can be frozen.
