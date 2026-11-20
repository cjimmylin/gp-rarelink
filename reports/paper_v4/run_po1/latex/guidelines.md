# GP-RareLink interim report, version 4: writing guidelines

The ICLR 2025 style files are used for layout only. This is an internal interim report, not an ICLR submission. Where a rule below conflicts with the GP-RareLink rules at the top of this file, these win.

## GP-RareLink rules (read first)
* **Not anonymous.** Keep the author block in the template exactly as it is (`\iclrfinalcopy` is set). Refer to the project as "we" or "GP-RareLink".
* **Pending human results.** Every result that depends on human raters is written with the macro `\HR{<id>}`, using only the ids in `raw_materials/pending_human_results.md`. `\HR` is defined in `human_results.tex`, which the template already inputs. Never put `\HR` in a section title. Never invent a value, range or direction for a pending result. Sentences must read correctly whatever the value turns out to be.
* **Spelling:** US English. Dates in ISO form (2026-11-20).
* **Packages already loaded:** `booktabs`, `graphicx`, `fontenc` (T1). Load nothing that needs network access.
* **Length:** main text up to 10 pages; appendices unlimited after the references.

Below are the instructions to help you with the LaTeX paper writing process for ICLR 2025.

## General Setup
* **Document Class:** `\documentclass{article}`
* **Required Packages:**
    ```latex
    \usepackage{iclr2025_conference,times}
    \usepackage{hyperref}
    \usepackage{url}
    % Optional but recommended for math
    \input{math_commands.tex}
    ```
* **Style Files:** You must use `iclr2025_conference.sty` and `iclr2025_conference.bst`.

## Anonymity
* Not applicable: this report is not anonymous (see the GP-RareLink rules above).

## Paper Length
* **Main Text:** Strict upper limit of **10 pages**.
* **Citations:** Unlimited additional pages.
* **Ethics & Reproducibility Statements:** Optional. Do not count toward the page limit (max 1 page each).
* **Acknowledgments:** Do not count toward the page limit.

## Abstract
The abstract must be limited to **one paragraph**.
* **Margins:** Indented 1/2 inch (3 picas) on both left and right-hand margins.
* **Font:** 10-point type, vertical spacing of 11-points.
* **Title:** The word `\textsc{Abstract}` must be centered, in small caps, and in point size 12.
* **Spacing:** Two line spaces precede the abstract.

## Formatting Your Paper
The text must be confined within a rectangle 5.5 inches (33 picas) wide and 9 inches (54 picas) long. The left margin is 1.5 inch (9 picas).
* **Font:** Times New Roman (via `times` package) is preferred.
* **Size:** 10-point type with 11-point vertical spacing.
* **Paragraphs:** Separated by 1/2 line space, with **no indentation**.
* **Paper Title:** 17-point, small caps, left-aligned.

### Headings
* **First Level:** Small caps (`\textsc`), flush left, 12-point. One line space before, 1/2 after.
* **Second Level:** Small caps, flush left, 10-point. One line space before, 1/2 after.
* **Third Level:** Small caps, flush left, 10-point. One line space before, 1/2 after.

## Citations and References
Use the `natbib` package (loaded automatically by the style file).
* **Narrative citation:** Use `\citet{Gomu2024}` $\rightarrow$ "Gomu et al. (2024)".
* **Parenthetical citation:** Use `\citep{Gomu2024}` $\rightarrow$ "(Gomu et al., 2024)".
* **Bibliography:**
    ```latex
    \bibliography{references}
    \bibliographystyle{iclr2025_conference}
    ```

## Figures and Tables
* All artwork must be neat, clean, and legible.
* **Captions:** Lower case (except for first word and proper nouns).
* **Placement:**
    * **Figures:** Caption appears **after** (below) the figure.
    * **Tables:** Caption appears **before** (above) the table.

### Example Code for Figures
```latex
\begin{figure}[h]
\begin{center}
%\framebox[4.0in]{$\;$}
\fbox{\rule[-.5cm]{0cm}{4cm} \rule[-.5cm]{4cm}{0cm}}
\end{center}
\caption{Sample figure caption.}
\end{figure}
```

### Example Code for Tables
```latex
\begin{table}[t]
\caption{Sample table title}
\label{sample-table}
\begin{center}
\begin{tabular}{ll}
\multicolumn{1}{c}{\bf PART}  &\multicolumn{1}{c}{\bf DESCRIPTION}
\\ \hline \\
Dendrite         &Input terminal \\
Axon             &Output terminal \\
Soma             &Cell body (contains cell nucleus) \\
\end{tabular}
\end{center}
\end{table}
```

## Math Notation
* ICLR encourages standardized notation using `\input{math_commands.tex}` (based on the Deep Learning book notation).
* Variables: Italics ($a$, $\va$, $\mA$).
* Random Variables: Roman ($P(\ra)$).
* Sets: Blackboard bold ($\R$, $\sA$).
* Functions: Standard LaTeX ($f(\vx)$).

## Optional Statements
These should appear at the end of the main text, before references.
1.  **Ethics Statement:** (Optional, max 1 page) Address potential concerns (human subjects, sensitive data, bias, etc.).
2.  **Reproducibility Statement:** (Optional, max 1 page) Reference code, proofs, or data processing steps to ensure reproducibility.

## Important Rules
* **Formatting:** Do not modify the width or length of the text rectangle or font sizes.
* **Line Numbers:** Do not refer to line numbers in your text (the style file adds them automatically for review).
* **Appendix:** You may include an appendix at the very end of the main PDF (after references). Use `\appendix` to start this section.
* **Figures Directory:** For consistent compilation, all figures will reside in the `figures` directory. Always include the `figures/` prefix in your `\includegraphics` command (e.g., `figures/figure_1.pdf`).
* **Author Information:** Keep the template's author block unchanged.