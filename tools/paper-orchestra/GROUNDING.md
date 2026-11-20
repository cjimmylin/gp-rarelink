# Grounding & anonymity rules (shared by every PaperOrchestra agent)

Adapted from upstream `UNIVERSAL_NO_LEAKAGE_PROMPT` (utils/prompt_utils.py). Upstream forbids
*all* prior knowledge because PaperWritingBench reconstructs already-published papers. For our
own papers we keep the part of that rule that protects scientific integrity and relax the part
that only protects the benchmark:

## 1. Claims about OUR work come only from the raw materials
- Every statement about our method, data, design, results, numbers, sample sizes, models
  tested, dates, and limitations must be traceable to `idea.md` / `experimental_log.md`
  (or the provided figures). If it is not there, it does not go in the paper.
- Never invent, round differently, "improve", or extrapolate numbers. Copy them exactly. If the
  log gives a CI or an n, keep it with the number.
- Never claim an experiment, baseline, ablation, model, or statistical test that the log does
  not report. Reviewer requests for new experiments are ignored, never promised.
- Keep the hedges the materials use. If the log says a result is exploratory, preliminary,
  underpowered, or did not replicate, the paper says so too.

## 2. Claims about OTHER work come only from the verified citation library
- Cite only keys in `lit/citation_map.json`. Describe a cited work only as far as its title and
  abstract (or labelled summary) in the map support, or, for user-supplied references
  (`extra_references.bib`, no abstract), as far as the raw materials themselves describe it. Do
  not attribute findings to a paper from memory.
- General background knowledge (what a transformer is, what a t-test does) is allowed;
  specific factual claims about the literature need a citation from the map.

## 3. Anonymity (when `config.json` has `"anonymize": true`)
- No author names, affiliations, emails, acknowledgements, grant numbers, repo URLs, or
  "corresponding author". Use the template's author placeholder.
- Refer to our own earlier work in the third person.

## 4. Honesty over polish
- Limitations the materials document must stay in the paper (a Limitations paragraph or
  section is expected). Upstream's refinement prompt said "Never explicitly state a
  limitation"; that instruction is removed here on purpose.
- Prefer the precise, weaker claim to the impressive, unsupported one.
