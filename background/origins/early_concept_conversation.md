# Origins: early concept conversation

An early chat between Jimmy Lin and Claude that came before GP-RareLink. It explored using academic papers to build rare-disease chatbots and having an LLM write cited review articles from a set of PDFs. The idea later became the funded project. It was added to the repo on 2026-10-18 as a historical record. The chat itself is undated; it predates the grant application.

> **Do not cite anything below without checking it first.** The papers and software in turn 6 were given from memory, and no PMID or DOI was checked. At least some of the titles, author lists or years are probably wrong. Under INSTRUCTIONS.md §1.1 nothing in this file is a source. For verified literature, use `background/bibliography.md` and `background/manifest.csv`.

## From that concept to the funded design

| Early idea (this conversation) | What GP-RareLink does instead | Where it's specified |
|---|---|---|
| A chatbot that answers questions about one rare disease | Structured, consolidated records (GA4GH Phenopackets), not a chat interface | CONTEXT.md §5, §7 |
| An LLM writes a narrative review from a set of PDFs | SLIDERS builds evidence tables from case reports, and an agent reconciles them | CONTEXT.md §5 |
| "Provide a source for each assertion" | PMID + verbatim span on every value; a gatekeeper pass re-checks each claim against its span; < 2% unsupported, audited on 250 claims | CONTEXT.md §5–6; INSTRUCTIONS.md §2 |
| Convert PDFs to text before giving them to the LLM | Prefer PMC open-access full text (XML or text); log papers we couldn't access | INSTRUCTIONS.md §3; background/README.md |
| "Expert validation" by clinicians | RGI adjudication panel (Wu, Balderrama, Chacko) signs off before anything is submitted | CONTEXT.md §3, §10 |
| "Continuous learning" / keep it up to date | A pipeline that can be pointed at any disease on demand; ClinVar/OMIM submissions close the gap upstream | CONTEXT.md §1, §5 |
| Human oversight because LLMs make errors | Abstention as a first-class output; ClinVar/OMIM used as ground truth for concordance (never as input); memorization probe | INSTRUCTIONS.md §1 |
| Symptom checker / treatment recommendations | **Dropped.** Out of scope: literature curation only, no clinical decision support, no patient data | CONTEXT.md §10 |

---

## Transcript

Lightly formatted. Wording is as in the original chat.

### 1. User
> What are ways to use academic documents to build chatbots for rare diseases?

**Claude** — gave ten approaches: (1) build a structured knowledge base from papers, clinical guidelines and studies; (2) NLP/text mining with domain vocabulary and entity recognition, and training language models on the processed text; (3) question answering by semantic similarity between queries and the documents; (4) dialogue flows modelled on expert consultation; (5) symptom-checker integration (decision tree or probabilistic model); (6) treatment recommendations from compiled protocols; (7) clinical-trial information; (8) continuous learning to add new findings; (9) expert validation with specialist clinicians; (10) multi-language support.

### 2. User
> Is it better to keep PDFs as is for llm use or make into text?

**Claude** — generally convert to text: easier processing, less layout noise (headers, footers, page numbers), more consistent tokenization, easier cleaning, smaller files, easier search and indexing. Caveats: keep the document's structure, use OCR for scanned PDFs, and preserve important figures and tables some other way.

### 3. User
> How are the best way to write a scholarly academic review articles with a set of known papers?

**Claude** — twelve steps: define scope and objectives; organize the papers (spreadsheet or reference manager, noting findings, methods, conclusions); analyse themes, contradictions, gaps and trends; build an outline (by theme, chronology or method); write the introduction; synthesize rather than summarize, and evaluate critically; discuss implications and future research; conclude; cite consistently; revise and get feedback; use tables and figures; follow journal guidelines.

### 4. User
> Is there a way to have an llm write a review article given a set of PDFs of academic papers?

**Claude** — yes, as an assistant: convert and clean the PDFs; summarize each paper; identify themes across papers; compare findings and find gaps and contradictions; propose an outline; draft sections with citations; critical analysis and future directions; polish; **human oversight to check every fact**; format for the journal. Check journal policies on disclosing AI use.

### 5. User
> Is there a way to write the article to provide source for each assertion based of the articles?

**Claude** — yes: extract assertions with their citations; store them as **assertion–source pairs** in a structured database; require a citation for every claim when generating; consistent in-text citations; **cross-reference each assertion against the original source**; cite every supporting paper; cite each side when findings conflict; quote directly for key ideas; cluster citations; generate the reference list automatically; check that citations and references match; human review. Example:

> "Recent studies have shown that treatment X is effective in reducing symptoms of disease Y (Smith et al., 2022; Jones, 2023). However, its long-term efficacy remains debated, with some researchers reporting sustained benefits over a 5-year period (Johnson, 2021), while others found diminishing returns after 2 years (Brown & Green, 2022)."

*(Placeholder citations, illustrative only.)*

### 6. User
> Are there any academic papers that talk about the process? Or existing software that does this already?

**Claude** — listed the items below. **⚠ Unverified, from memory; treat as likely inaccurate until checked:**

- Papers: "Automated scientific literature review: A systematic review of methods" (Bannach-Brown et al., 2019, *PLoS ONE*); "Machine learning for systematic review automation: A systematic review" (O'Connor et al., 2018, *Systematic Reviews*); "Artificial Intelligence for Systematic Reviews: A Scoping Review" (Tsafnat et al., 2021, *J Clin Epidemiol*).
- Software: ASReview (open-source ML screening), Covidence (review management and extraction), RobotReviewer (ML extraction from trial reports), SWIFT-Review (Sciome; text-mining prioritization), Scholarcy (AI summarizer).
- Caveat given at the time: these tools help human reviewers rather than writing reviews on their own; check with recent databases or a systematic-review librarian.

### 7. User
> Can you write a prompt for an llm to identify existing methods and software as above?

**Claude** — gave this prompt:

> "Please provide a comprehensive overview of existing methods and software tools for automating or assisting with the process of writing academic review articles. Include the following in your response:
>
> 1. Academic papers discussing automated or AI-assisted methods for literature review and academic writing. For each paper, provide: Title; Authors; Year of publication; Journal or conference; A brief summary of the key points or contributions
> 2. Existing software tools or platforms designed to assist in this process. For each tool, include: Name of the tool; Developer or company behind it; Primary features and capabilities; Whether it's open-source or commercial; Any notable strengths or limitations
> 3. Emerging trends or promising new approaches in this field
> 4. Any significant challenges or limitations in current automated methods for academic review writing
> 5. Potential ethical considerations or guidelines related to using AI or automation in academic writing
>
> Please organize your response clearly, using appropriate headings and subheadings. Cite sources where possible, but note that I understand you may not have access to the most recent information and some details might need verification.
>
> After providing this overview, please suggest areas where further research or development could be particularly valuable in advancing automated academic review writing."

*(Retrospective note: a prompt that asks a model to list papers from memory is the setup that produced the unverified citations in turn 6. GP-RareLink's design — verified IDs, verbatim spans, abstention — was built to rule that failure out.)*
