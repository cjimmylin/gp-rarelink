# Memorization probe (a): closed-book recall, v1 (2026-10-21)

This is a test of what you remember from training, not a research task. For each paper below you get only its PubMed ID, title and year. From memory alone, say what the paper reports:
- **variants:** the gene variants it reports in patients, in HGVS-like notation where you can (e.g. `c.559C>T`, `p.Gln187Ter`);
- **phenotypes:** up to 8 key clinical features it reports in those patients, as short clinical terms (HPO labels where you can).

Rules:
- **Use no tools to look anything up.** Do not read files, search, or fetch anything. Answer from memory only. The one tool you may use is Write, once, to save your answer to the output path you are given.
- If you do not remember a paper, say so: give `"recall": "none"` and empty lists. Guessing from the title is allowed only if you mark it `"recall": "guess"`. Use `"recall": "specific"` only for things you believe you remember from the paper itself.
- Do not explain or add commentary.

Output: one JSON object, `{"batch": "<batch name>", "answers": [{"id": "...", "recall": "specific|guess|none", "variants": ["..."], "phenotypes": ["..."]}]}`, with one answer per item in the order given.
