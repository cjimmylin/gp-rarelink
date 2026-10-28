# Message to the adjudication panel about the gap-variant adjudication page: draft for Jimmy to send

*Drafted 2026-10-28 by Claude at Jimmy's request. Status: **draft, not sent.** Claude does not contact anyone (`CLAUDE.md`). Facts below come from `adjudication/o3_gaps/` (candidates.csv after D-43, triage_summary.json, check_summary.json), the page template, pre-registration §7.3 and §7.5, and D-13.*

## Before sending (Jimmy)

1. **Pages.** Only adjudicator A's page exists (https://claude.ai/artifact/UUWN2ULAGkYYNQj4zDy9ta, private, store `adjudications`). Pages B and C are built by `adjudication/o3_gaps/make_adjudication_page.py --adjudicator B|C`, but publishing them is a new artifact page, which your 2026-10-21 instruction forbids until you say otherwise. Options: lift that rule for these two pages and Claude builds them; or share page A with one panel member now and the others later. A single page for all three would mix their decisions in one store and is not recommended.
2. **Allocation.** The message proposes one disease group per person (82 / 74 / 59 candidates). Change the names if you prefer another split; "needs discussion" items go to a second panel member and ties to you.
3. **Two items the page still shows as ordinary candidates:** `G-danon-001` is withdrawn (D-43, a transcript error) and `G-lad1-077` cites a ClinVar accession (SCV007539359) that may have landed after the 2026-10-19 snapshot. The page is rebuilt from `candidates.csv` when publishing resumes and will then show the withdrawal; until then the message tells them to skip the first and re-check the second.
4. **The O1 audit rating pages** (A and B, 250 claims) also wait on you to share them. That is a separate message; this one is only about adjudication.
5. Fill the two `[fill]` markers.

---

**To:** Dr. Eva Wu, Dr. Gabriela Balderrama, Dr. Anita Chacko
**Subject:** GP-RareLink: the gap-variant adjudication is ready for you

Dear Eva, Gabriela and Anita,

The six-disease extraction is done and scored against ClinVar and OMIM. It leaves **214 candidate variants** that the literature reports as causal but that are in neither database: no ClinVar record with the same GRCh38 allele (release 2026-10-12) and no OMIM allelic-variant entry (pages frozen 2026-10-28). By disease: LAD-I 82, A20 haploinsufficiency 64, Danon 34, Alexander 17, SSADH deficiency 10, Tangier 7. Together they rest on 373 reported individuals. This is the adjudication step we described in [fill: date of the earlier message], and it is where your judgement decides what goes forward.

**What you will get.** Each of you receives a private web page by separate email. Do not forward the link. The page lists your candidates on the left and shows, for the selected one, an evidence sheet and a decision form on the right. It saves as you go; a "Copy all decisions as text" button is the backup if saving ever fails.

**What is in an evidence sheet.** Each sheet was assembled by a model from the papers only. Every statement carries a verbatim quote and its PMID, and "not reported" means the papers say nothing. The model was not shown ClinVar or OMIM and proposes no classification; every quote was checked against the paper text by script (4,725 quotes, none failed). The sections follow the ACMG/AMP evidence types: the reported individuals (sex, zygosity, the other allele in recessive disease, key phenotypes), phenotype specificity, segregation, de novo status, phase, functional studies, variant type and mechanism, computational predictions and population data as the papers state them, and the authors' own classification. A "concerns" list and a few flags point at things to weigh: a possible double count of the same person across papers, a notation conflict inside a paper, support from reviews only, a stated protein change that disagrees with the cDNA, or a second variant in the same person. The flags are pointers, not verdicts.

**What we ask you to record for each variant.**
1. The ACMG/AMP criteria you apply, each with its strength (Richards et al. 2015; for PP1, BS4 and PP4 the ClinGen 2024 guidance).
2. A classification: pathogenic, likely pathogenic, VUS, likely benign or benign.
3. A decision: **approve** (the record can go forward as a draft ClinVar submission under the curation method, with your classification), **reject** (it should not, for example an extraction or numbering error), or **needs discussion**.
4. A short note where it helps the next reader.

Population frequency is not in the sheets: please check gnomAD yourself; the page links the variant. Before anything is submitted it is re-checked against live ClinVar, and nothing is submitted without my sign-off.

**Two housekeeping points.** Skip `G-danon-001`: it was withdrawn after we found the paper reports it on another LAMP2 transcript. For `G-lad1-077`, the paper cites a ClinVar accession that may have appeared after our snapshot; please check ClinVar before spending time on it.

**Time.** The page logs active minutes per variant while a sheet is open; expert minutes per accepted record is one of the metrics we promised the funder, so please let it run and do not fill in by memory later. We have no estimate yet of the time per variant. Could you each do five first and tell me how long they took? That will set the schedule for the rest.

**Proposed split** (tell me if you would rather swap): Eva, LAD-I (82); Gabriela, A20 haploinsufficiency and SSADH deficiency (74); Anita, Danon, Alexander and Tangier (59). Anything you mark "needs discussion" goes to a second of you, and I will settle ties.

The candidates are ready now; our plan has adjudication in December and January, which spans the holidays. Could you reply with the week you could start and any weeks you will be away?

Thank you,
Jimmy

---

*Sources for the numbers: `adjudication/o3_gaps/candidates.csv` (215 rows, 1 withdrawn), `check_summary.json` (4,725 quotes, 0 problems), `triage_summary.json` (152 flagged), `analysis/poc/reference_snapshot/2026-10-28/omim_counts.json`. Framework references: `richards2015_acmg`, `biesecker2024_clingen_pp1_pp4` in `background/manifest.csv`.*
