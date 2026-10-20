# OSF registration: what to enter (for Jimmy)

*Drafted 2026-10-20 by Claude for Dr. Lin to register (D-09: OSF, public, at the freeze). Nothing has been submitted, and no OSF account was used. OSF's forms and template names change, so check them on the day; the steps below say what to enter, not which buttons OSF shows.*

## 1. First, put the two git tags on GitHub

This session could not push tags; GitHub refused them with a 403. Both tags exist locally on commit `ef3133ef1f5685d8a8d3868b9ed45966361fe44e`, which is on branch `claude/gracious-pascal-j7krug`. From a clone:

```
git fetch origin claude/gracious-pascal-j7krug
git tag -a prereg-v1.0 ef3133ef1f5685d8a8d3868b9ed45966361fe44e -m "GP-RareLink pre-registration v1.0, frozen 2026-10-20 (D-36)"
git tag -a pipeline-v1.0 ef3133ef1f5685d8a8d3868b9ed45966361fe44e -m "GP-RareLink frozen pipeline v1.0, 2026-10-20 (D-36)"
git push origin prereg-v1.0 pipeline-v1.0
```

Alternatively, create both tags on GitHub as releases that target that commit. Merging the branch into `main` with a merge commit keeps `ef3133e` in the history, so the tags stay valid after the merge.

## 2. What to register

- **The text:** `preregistration/analysis_plan.md` at commit `ef3133e`, unchanged.
  - sha256 `96c2e7d2e3cc8c3efbbf92b2c1392faf183e26a1bce7e5b7a55f04ba6c27099c`.
  - Upload this file, or a PDF made from it, as the registration document. Edits for formatting only are fine; a change of wording makes the OSF text differ from the tagged text.
- **Suggested supporting files** (the plan cites them; attaching them lets readers check the pinned pipeline without repository access):
  - `POC_DESIGN.md`;
  - the four pinned files: `pipeline/extract/claude_code/prompts/extract_v6.md`, `pipeline/extract/claude_code/prompts/gatekeeper_v4.md`, `pipeline/extract/claude_code/schema_ha20_v5.json` and `pipeline/extract/sliders_adapter/prompts/extraction_rules_v1.md`;
  - `reports/poc_report.md` and `reports/poc_smoke_v6_findings.md` (§10 of the plan, knowledge of the data before registration).
- **Not to attach:** anything under `data/literature/*/fulltext_md/` (full text of papers), and reference snapshots. Licensing is open under D-16.
- **Repository link:** the GitHub repository at tag `prereg-v1.0`. If the repository is private, the link will not open for readers, so rely on the attached files.

## 3. Fields

| Field | Suggested entry |
|---|---|
| Title | GP-RareLink: Literature-Curated, Database-Validated Genotype–Phenotype Records for Rare Disease (pre-registered analysis plan v1.0) |
| Registration type | A template for research on existing data, or an open-ended registration with the plan attached. The plan's sections follow the usual existing-data template (plan §1 note) |
| Description | See §4 below |
| Contributors | Your choice. The plan lists Dr. Jimmy Lin, Prof. Monica Lam, and Drs. Eva Wu, Gabriela Balderrama and Anita Chacko. OSF may email anyone you add, so add only people who have agreed |
| Funding | Anthropic AI for Science Program, Rare Disease program, Basic science track (award 2026-08-31) |
| Embargo | None: public at registration (D-09) |
| Data already collected? | Yes, partly. Literature only; no patient data. Plan §10 states what was seen before registration: the HA20 pilot, which is a development disease reported separately, and the screening of the five other corpora. No extraction has run on the five other diseases |
| Planned start of the main study | After registration. The six-disease run waits on your approval of its cost estimate |

## 4. Description (about 150 words; paste or edit)

> GP-RareLink tests whether SLIDERS, an LLM-based systematic-review method run with Claude, can build GA4GH Phenopacket records (variant, phenotype and disease, with a PMID and verbatim span on every value) from published case reports for six rare diseases: Alexander disease, LAD-I, SSADH deficiency, Danon disease, Tangier disease and A20 haploinsufficiency. ClinVar and OMIM are kept out of extraction and used only as the answer key. The primary outcomes are an unsupported-value rate from a 250-claim human audit (target under 2%), concordance with ClinVar and OMIM, and gap closure: variants absent from both databases, adjudicated by an expert panel and prepared for submission. Secondary outcomes are ascertainment bias against natural-history cohorts, with a memorization probe, and efficiency, including a comparison with an open-weight model. A20 haploinsufficiency was the pilot disease and is reported separately. The pipeline was frozen as `pipeline-v1.0` after a 20-paper smoke run. All results will be reported whether favorable or not.

## 5. After registering

Send me the DOI and the registration date. I will record them in `DECISIONS.md`, under the pre-registration status line, and not in the frozen plan.
