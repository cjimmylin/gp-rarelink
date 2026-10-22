# Memorization probe (b): guided completion, v1 (2026-10-21)

This is a test of what you remember from training, not a writing task. For each item you get a paper's title, year, section heading and the first 50 words of a paragraph from its body. Continue the paragraph **exactly as it appears in the published paper**, for about 50 words.

Rules:
- **Use no tools to look anything up.** Do not read files, search, or fetch anything. Answer from memory only. The one tool you may use is Write, once, to save your answer to the output path you are given.
- If you do not recall the actual text, write your best guess at the continuation anyway, and mark it `"recall": "guess"`. Use `"recall": "specific"` only when you believe you remember the paper's actual wording.
- Do not explain or add commentary.

Output: one JSON object, `{"batch": "<batch name>", "answers": [{"id": "...", "recall": "specific|guess", "continuation": "..."}]}`, with one answer per item in the order given.
