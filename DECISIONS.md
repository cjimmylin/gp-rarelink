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

## 2026-10-18 — POC study design drafted; six decisions pending

- **Type:** method / scope
- **Decision:** `POC_DESIGN.md` is the protocol for the first end-to-end run of
  the pipeline on one disease. It is a working document, not the
  pre-registration, and changes nothing pre-registered.
- **Decisions it needs from Jimmy before Stage 2 (see `POC_DESIGN.md` §2.4):**
  1. POC disease = A20 haploinsufficiency (recommended) vs Alexander disease.
  2. Adapt the public SLIDERS code for Claude by adding an Anthropic provider
     (its README, checked 2026-10-18, lists OpenAI and Azure OpenAI only);
     whether to also ask the Lam lab for a Claude-ready branch.
  3. Exclude reviews and meta-analyses from the extraction corpus; use them
     only as seed lists and completeness benchmarks.
  4. OMIM access for the harness: who requests the key and when.
  5. POC audit: 50 claims, which panel member, and whether it counts against
     Month-4 adjudication hours.
  6. POC spend ceiling: $1,000 recommended, hard stop at $1,500.
- **Approved by:** n/a (awaiting Jimmy)

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
