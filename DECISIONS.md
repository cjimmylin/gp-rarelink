# Decisions log

Dated record of project decisions and any deviations from the pre-registration.
Newest entries at the top. Each entry: date, decision, reason, who approved, and
whether it is a **pre-registration deviation** (only possible once the analysis
plan in `preregistration/` is frozen).

| Field | Meaning |
|---|---|
| Date | ISO date the decision was made |
| Type | `process`, `scope`, `method`, `budget`, or `PREREG DEVIATION` |
| Approved by | Jimmy (or the person with authority for that call) |

---

## 2026-10-18 — POC study design approved with six decisions

- **Type:** method / scope
- **Decision:** `POC_DESIGN.md` is the protocol for the first end-to-end run of
  the pipeline on one disease. It is a working document, not the
  pre-registration, and changes nothing pre-registered. Jimmy answered the
  six open decisions (chat, 2026-10-18); the design was updated to match.
  1. **POC disease: A20 haploinsufficiency (*TNFAIP3*).** Alexander disease
     is the natural first disease for the full Month-2 run.
  2. **SLIDERS on Claude: fork the public code and add an Anthropic provider**
     using the official SDK. No contact with the Lam lab for now; offer the
     adapter upstream later (external contact needs separate approval).
  3. **Reviews and meta-analyses are included in the extraction corpus,
     flagged `study_type = review`.** The reconciliation agent must merge
     re-reported patients; rows sourced only from reviews are kept but
     flagged `review_only`. Completeness against El Hani 2024 is computed on
     primary-paper rows only, so the benchmark is not scored against itself.
     If deduplication suffers, exclusion is reconsidered as a logged change.
  4. **OMIM access: Claude drafts the API access request and a summary of
     the current terms for Jimmy to submit.** Nothing is sent without Jimmy.
     Until access arrives, the POC concordance runs against ClinVar only.
  5. **POC audit: Jimmy rates the 50 claims himself.** The adjudication panel
     is held for the 250-claim audit and Month-4 adjudication.
  6. **POC spend ceiling: $1,000, hard stop $1,500.** Drawn from the
     extraction and gatekeeper lines; stop and ask before exceeding $1,000.
- **Approved by:** Jimmy (chat, 2026-10-18)

## 2026-10-18 — Open items blocking Month 1 bookkeeping

- **Type:** process
- **Decision:** none yet; recorded so they are not lost.
- **Items:**
  - `CONTEXT.md` header still has blanks for award date, credits awarded and
    project start (Month 1). Needed to fix the timeline and the budget
    baseline in `BUDGET.md`.
  - Actual spend to date has not been reconciled against the Anthropic Console
    (org `2056f88f-1a7b-4386-abfb-5b0fe9a98e10`).
- **Approved by:** n/a (awaiting Jimmy)

## 2026-10-18 — Git repo is the single source of truth

- **Type:** process
- **Decision:** `cjimmylin/gp-rarelink` (branch `main`) is canonical for every
  project document, script and dataset manifest. The claude.ai Project
  "Anthropic Rare Disease" holds a read-only mirror of the repo's documents so
  chat sessions can see them.
- **Reason:** the instructions require every number to trace to a script, a
  dated input and a commit; only the repo provides that. The Project previously
  held duplicate copies (`CONTEXT.md` and `claude/CONTEXT.md`,
  `claude/INSTRUCTIONS.md`), which would drift.
- **How syncing works:**
  - Edit files in the repo and commit. Then refresh the Project mirror from the
    repo (any Claude session attached to both can do this). Do not edit
    documents in the Project directly.
  - Path mapping: files at the repo root are mirrored under `claude/` in the
    Project (the Project only allows new top-level docs there), e.g.
    `CONTEXT.md` → `claude/CONTEXT.md`. Files in subfolders keep their repo
    path, e.g. `grant/GRANT_APPLICATION.md`, `background/manifest.csv`.
  - `INSTRUCTIONS.md` is mirrored to `claude/INSTRUCTIONS.md` and also serves
    as the Project's custom instructions, which have to be pasted in Project
    settings by hand when the file changes.
  - `CLAUDE.md` is Claude Code–specific and is not mirrored.
- **Approved by:** Jimmy (chat, 2026-10-18)
