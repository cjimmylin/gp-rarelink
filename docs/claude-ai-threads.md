# What was worked out in the claude.ai chats

Digest of every chat in the claude.ai Project "Anthropic Rare Disease" up to
2026-10-18, so Claude Code sessions in this repo know what was already done,
decided and left open. Files those chats produced are already in the repo; this
records the context around them. Where a chat and a repo file disagree, the
repo file wins (see `DECISIONS.md`, 2026-10-18).

Attribution: "Jimmy asked/decided" means it came from Jimmy's own message;
"Claude suggested" means it was advice that Jimmy has not explicitly adopted.

## Thread index

| Date | Chat | Outcome in the repo |
|---|---|---|
| before the grant (undated) | [Building Rare Disease Chatbots with Academic Documents](https://claude.ai/chat/a62443a6-d89b-44a5-9b68-3353a4856a96) | `background/origins/early_concept_conversation.md` |
| 2026-10-16 | [Grant project documentation files](https://claude.ai/chat/31e59abb-5c8b-44f2-bb73-f1f2d3494536) | `INSTRUCTIONS.md`, `CONTEXT.md`, `grant/GRANT_APPLICATION.md` |
| 2026-10-16 | [Remote execution from phone to Mac](https://claude.ai/chat/6f9a298b-3ab4-4b90-a049-5a5832d6e865) | No files; setup notes below |
| 2026-10-16/17 | [Background folder and literature research](https://claude.ai/chat/2a54ad76-f59c-4f19-a81f-c67349ec55df) | `background/` (bibliography, manifest, claim checks, fetch and audit scripts) |
| 2026-10-18 | [Upload project to GitHub](https://claude.ai/chat/dc3a3a8e-c31c-4c94-ab0c-5fb17e671da5) | Repo created; `CLAUDE.md`, `.gitignore`, `README.md` |
| 2026-10-18 | [gp-rarelink repo interaction](https://claude.ai/chat/46c43de7-81d6-436a-8807-34820afaf479) | `DECISIONS.md`, `BUDGET.md`; repo/Project sync rule |
| 2026-10-18 | (this digest) | `docs/claude-ai-threads.md` |

Claude Code work from the same day (pre-registration draft, numbered open decisions, award details) is summarized in `NOTES_FOR_AGENTS.md` and `DECISIONS.md`.

## 1. Project documents (2026-10-16)

- Jimmy asked for instruction and context files for the project folder
  `/Users/jimmylin/Documents/AnthropicRareDisease` on his Mac mini, which then
  held only the grant application (.docx).
- Claude converted the application to `GRANT_APPLICATION.md`, removing the
  email header and checkbox tables and recording the form selections at the
  top: Rare disease program, Basic science track, no biosecurity concerns.
- `INSTRUCTIONS.md` is also meant to be the Project's custom instructions;
  that field has to be pasted by hand in Project settings when the file changes.

## 2. Working from a phone via the Mac mini (2026-10-16)

Claude suggested this setup; it is not a project decision.

- The Mac mini does the work; the phone sends instructions. Requires the
  Claude desktop app open and signed in on the Mac, the chat linked to the Mac
  (open it in the desktop app once), and only the `AnthropicRareDisease`
  folder connected.
- Keep the Mac awake (Energy settings: never sleep, restart after power
  failure; Claude in Login Items). If a task can't reach local files, the Mac
  is asleep, offline or the app has quit.
- Multi-user Mac: works under Fast User Switching while Jimmy's account stays
  logged in; fails if his account is logged out. Suggested automatic login for
  his account (blocked by FileVault) and asking others to switch users rather
  than log out. This was reasoning about macOS, not documented behaviour;
  test once before relying on it.

## 3. Background literature (2026-10-16 → 17)

Details are in `background/README.md` and `background/grant_claim_checks.md`.
Points a coding session needs:

- **Cloud workspaces cannot reach PubMed, PMC, Europe PMC, arXiv,
  bioRxiv/medRxiv, DOI resolvers or publisher sites.** Run
  `background/fetch_papers.sh` (or `fetch_papers.py`) on the Mac or another
  machine with normal internet. Same applies to the Month-1 corpus and
  ClinVar/OMIM snapshots.
- 129 bibliography entries, 64 core; ~92 have an open-access route.
  Identifiers were checked against live pages on 2026-10-16; blanks mean
  "not confirmed", not "does not exist". Confirm on PubMed before citing.
- Several application numbers are contradicted or need dating (Tangier
  "~200 patients", phenopacket-store "408 cohorts", DRBench figures,
  AA-Omniscience comparison, 97.6% HPO precision). These are **open decisions
  for Jimmy**; nothing has been changed in `CONTEXT.md` or the disease set.
- Downloaded papers stay out of git (`.gitignore`); many are free-to-read but
  not openly licensed.
- Gaps found: no literature on detecting the same proband across case
  reports, or on systematic HPO-frequency vs cohort comparisons.

## 4. GitHub repo and Claude Code (2026-10-18)

- Repo: `cjimmylin/gp-rarelink`, private, branch `main`.
- Link the local Mac folder to it without changing files:
  ```bash
  cd ~/Documents/AnthropicRareDisease
  git init -b main
  git remote add origin https://github.com/cjimmylin/gp-rarelink.git
  git fetch origin && git reset origin/main
  ```
  (An old `gitignore` file without the leading dot can be deleted.)
- Collaborators (Stanford OVAL) are added in GitHub → Settings → Collaborators.
- The earlier Project files were moved to match the instructions' layout:
  `INSTRUCTIONS.md` and `CONTEXT.md` at the top, the application under
  `grant/`. `background/download_list.tsv` was rebuilt from the manifest
  (92 entries, identical to the Project copy).

## 5. Repo ↔ Project sync (2026-10-18, decided by Jimmy)

- **The repo is canonical.** The Project mirrors its documents for chat.
  Edit here, commit, then refresh the Project. Full rule and path mapping in
  `DECISIONS.md`.
- Nothing syncs automatically in either direction. Claude Code does not see
  Project docs or chats unless they are committed here, which is why this
  digest exists. Work done in a chat should end with a commit here.

## Open items carried over from the chats

| Item | Where it's tracked |
|---|---|
| Month 1 start date. The award date and credits were recorded in `CONTEXT.md` on 2026-10-18 | `DECISIONS.md` D-01 |
| Spend to date not reconciled. The credits turned out to be claude.ai usage credits, not Console credits | `DECISIONS.md` D-15, `BUDGET.md` |
| Decide how to fix the application numbers flagged in `grant_claim_checks.md` | `DECISIONS.md` D-14; `background/grant_claim_checks.md` |
| Unconfirmed PMIDs/titles in the manifest (`id_notes`) | `background/manifest.csv` |
| PDFs not yet fetched (or fetch status unrecorded) | `background/README.md` |
| Date of the early concept chat unknown | `background/origins/early_concept_conversation.md` |
| Project custom instructions must be re-pasted when `INSTRUCTIONS.md` changes | `DECISIONS.md` |
| Month 1 tasks. The pre-registration is drafted (v0.3, not frozen). Not started: per-disease corpus, direct dated ClinVar/OMIM counts, Monarch/ClinVar outreach drafts | `NOTES_FOR_AGENTS.md` §1–2; `INSTRUCTIONS.md` §6 |

## Keeping this current

After a chat in the Project produces a decision, finding or file, add a row
to the thread index and a short section here (or a `DECISIONS.md` entry if it
is a decision), commit, and refresh the Project mirror.
