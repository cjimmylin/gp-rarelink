# NOTICE

This directory contains a derivative work of **PaperOrchestra**
(https://github.com/google-research/paper-orchestra, commit ca1b3fa01c2970fc7cda32d16245db38d57b3f56),
Copyright 2026 Google LLC, licensed under the Apache License, Version 2.0 (see `LICENSE`).
Upstream states: "This is not an officially supported Google product."

Vendored unchanged: `templates/iclr2025/*`, `templates/cvpr2025/*` (venue style files carry
their own original notices).

Modified / re-implemented (2026-11, Multi-Alignment repo):
- `scripts/po.py` — re-implements the deterministic parts of upstream
  `methods/agents/literature_review_agent.py`, `utils/scholar_utils.py`, `utils/pdf_utils.py`,
  `autoraters/agent_review.py` (score aggregation) and
  `methods/agents/content_refinement_agent.py` (accept/revert rule); adds Crossref/arXiv
  verification fallbacks and static LaTeX checks; removes all LLM API calls.
- `.claude/agents/po-*.md` (repo root) — adapted from upstream prompts in `methods/prompts/*`,
  `utils/paper_banana_utils.py`, `autoraters/agent_review.py` and the inline prompts of
  `methods/agents/content_refinement_agent.py`, rewritten as Claude Code subagent instructions.
  Notable content changes are listed in `README.md` ("Local adaptations vs upstream").
- `GROUNDING.md` — replaces upstream `UNIVERSAL_NO_LEAKAGE_PROMPT`.

Please cite the original work:

```bibtex
@article{song2026paperorchestra,
  title={PaperOrchestra: A Multi-Agent Framework for Automated AI Research Paper Writing},
  author={Song, Yiwen and Song, Yale and Pfister, Tomas and Yoon, Jinsung},
  journal={arXiv preprint arXiv:2604.05018},
  year={2026}
}
```
