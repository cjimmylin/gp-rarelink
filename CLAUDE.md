# GP-RareLink — Claude Code project memory

Claude Code loads this file automatically at the start of every session.
The full rules live in the two files imported below; keep them as the single
source of truth rather than duplicating text here.

@INSTRUCTIONS.md
@CONTEXT.md

Current status, environment limits and lessons from earlier sessions live in the
file below. Read it before starting, and update it when you learn something a
future session would need.

@NOTES_FOR_AGENTS.md

Work done earlier in claude.ai chats (setup, environment limits such as the
cloud workspace being unable to reach PubMed/PMC, and open items) is
summarised in `docs/claude-ai-threads.md`. Read it at the start of a session.

## Quick reminders for coding sessions

These restate the rules from INSTRUCTIONS.md that matter most while writing code.
If anything here seems to conflict with INSTRUCTIONS.md, INSTRUCTIONS.md wins.

- **Ground-truth isolation.** Code under `pipeline/` (extraction) must never read
  from `data/reference/`. Only the concordance harness may read reference data.
  If a change would make ClinVar/OMIM content reachable from extraction prompts,
  few-shot examples or reconciliation logic, stop and flag it.
- **No fabrication.** Every extracted value needs a real PMID/DOI and a verbatim
  span. "Not reported" is a valid output; never fill gaps from model memory.
- **Three-state HPO.** observed / excluded / not reported. Never collapse
  "not reported" into "excluded".
- **Re-runnable.** Numbers in reports come from scripts with dated inputs and a
  commit hash. Commit after each meaningful step with a descriptive message.
- **Budget.** Before any large or repeated model run, estimate cost and the
  budget line it draws on; pilot on one disease first; log actual spend in
  `BUDGET.md`.
- **Pre-registration.** Changes to metrics, thresholds or disease set after
  freezing go in `DECISIONS.md` as dated deviations, and need Jimmy's approval.
- **No patient data.** Literature only.
- **Secrets.** API keys go in `.env` (git-ignored), never in code or commits.
- **Stop and ask Jimmy** before contacting external parties, submitting to a
  public database, large spend, or changing anything pre-registered.
- **Publishing (Jimmy, 2026-10-21; amended by D-45 on 2026-11-09 and D-46 on 2026-11-10).** The 2026-10-21 rule was "No publishing at all until you hear from me differently": no new or updated artifact pages, no posts, no public releases or uploads. Two carve-outs since. **D-45 (2026-11-09):** the collaborator dashboard on GitHub Pages (`site/`, deployed from `main`) and the documents it carries. **D-46 (2026-11-10, Jimmy: "Make gp-rarelink public."):** the repository itself is public (Jimmy flips the setting himself; no session tool can). From then on **everything committed to any branch is published the moment it is pushed**, so: never commit full-text articles, supplementary files or anything else we may not redistribute (the corpus stays git-ignored; a run that stores tool results must redact paper text before commit, see `analysis/openweight/redact_paper_text.py`); write nothing into the repo that Jimmy has not already put there about himself or the team; and everything else (artifact pages, posts, uploads elsewhere) stays unpublished, with Jimmy sharing links himself.
- **No contact (Jimmy, 2026-10-18).** Claude does not contact anyone by any
  channel: collaborators (including Prof. Lam and the panel), database
  maintainers, foundations or Anthropic. Draft messages for Jimmy to send;
  never send them.
