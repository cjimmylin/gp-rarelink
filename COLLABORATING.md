# Collaborating on GP-RareLink

*For experts joining the project for internal review. Written 2026-11-09. The public-facing version of this orientation, with the papers, deck and video, is the dashboard built from `site/`.*

## What the project is, in three sentences

GP-RareLink reads the published literature on six rare genetic diseases with a language model (Claude), turns each paper into structured per-individual records (GA4GH phenopackets) in which every value carries a verbatim quote from its source, and then checks those records against ClinVar, OMIM and published catalogues, which the model never sees. The aim is to measure how accurate such a pipeline is, and to find variants that are published but missing from the databases. It is funded by Anthropic's AI for Science program and run by the Rare Genomics Institute with the Stanford Open Virtual Assistant Lab.

## Where to start

1. **The dashboard** (`site/index.html`, or the GitHub Pages address once enabled): the guided path, the six-minute captioned video, the short paper, the deck, the candidate list and the input form.
2. **The short paper** (`reports/interim_paper_v3/`): eight pages for readers new to the field.
3. **The full report and supplement** (`reports/interim_paper/`): every table, interval and method; the gap list in its section 5.
4. **The frozen plan** (`preregistration/analysis_plan.md`, v1.0, 2026-10-20): what we committed to measure and how.

## How the repository is organized

| Folder | What is in it |
|---|---|
| `pipeline/` | The extraction pipeline and the comparison harness. Code under `pipeline/extract/` can never read the reference data; a test enforces it. |
| `configs/` | Per-disease settings: search terms, the 20-item clinical checklists, record-building settings. |
| `data/literature/<disease>/` | Corpus manifests: which papers were found, screened, read, and why. Full texts are not committed. |
| `data/extracted/<disease>/pv1-<disease>/` | The extraction of record: per-paper tables, gatekeeper verdicts, phenopackets. |
| `analysis/` | Every number in every report, computed by script with dated inputs. |
| `adjudication/` | The audit sample and rating pages, the gap-candidate dossiers and the adjudication page. |
| `reports/` | Findings reports, the interim papers, the deck and video, and message drafts. |
| `preregistration/` | The frozen analysis plan. |
| `DECISIONS.md`, `BUDGET.md`, `NOTES_FOR_AGENTS.md` | Numbered decisions and deviations; spend by budget line; working notes. |

## What we need from you

| Role | What you would do | Effort |
|---|---|---|
| Audit rater | Rate 250 extracted values against their quoted evidence on a blinded web page; two raters and a tie-breaker | 10 to 15 hours per rater |
| Adjudicator | Review the candidate variants from their dossiers and decide whether the evidence supports a submission | 10 to 15 minutes per candidate |
| Cohort reader | Fill a comparator sheet of clinical-feature frequencies from a natural-history paper, without looking at our records | 1 to 2 hours per sheet |
| Methods or domain reviewer | Read the paper or the report and tell us what is wrong, missing or unclear | 1 to 3 hours |

Tell us who you are and how you would like to contribute through the form linked from the dashboard.

## Ground rules that apply to everyone

- **Literature only.** No patient data is used or wanted.
- **Provenance on every claim.** A value without a quote is not allowed in the records; a claim without a source is not allowed in the reports.
- **The answer key is held out.** Nobody feeds ClinVar or OMIM content into the extraction step.
- **Nothing is submitted to ClinVar or OMIM without expert adjudication and the PI's sign-off.**
- **Results are reported whether favourable or not.** The pre-registered test may fail; if it does, the report will say so.
- **Internal review.** The dashboard is shared with invited collaborators; please do not redistribute the documents yet.

## Reproducing a number

Every number in the reports comes from a script in `analysis/`. The interim papers regenerate with `uv run python -m analysis.interim_paper.build` (full) and `uv run python -m analysis.interim_paper.build_v3` (short); the deck, video and dashboard with `bash analysis/dashboard/make_all.sh`. Supplementary Table S1 of the full report lists the input file behind each figure.
