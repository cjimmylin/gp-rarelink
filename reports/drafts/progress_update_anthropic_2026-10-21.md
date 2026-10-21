# Progress update for Anthropic's AI for Science program (draft, 2026-10-21)

*Draft by Claude for Jimmy Lin to edit and send. Claude has sent nothing. Figures come from the repository files named. Spend figures are list-price session readings and helper-token estimates; they are provisional until the account questions in D-15 and D-17 are settled.*

---

**GP-RareLink: progress at the end of Month 1 (Dr. Jimmy Lin, Rare Genomics Institute; Prof. Monica Lam, Stanford OVAL)**

**Where we are.** Extraction and verification are finished for all six pilot diseases. The analysis plan was frozen on 2026-10-20, before the six-disease run, after a one-disease pilot on A20 haploinsufficiency.

**What we measured so far**
- **Corpus and records:**
  - 350 open-access case-report papers extracted, with 2,948 individual rows and 2,233 variant rows;
  - 2,836 GA4GH Phenopackets, all schema-valid;
  - every value carries a verbatim quote from its paper, and every quote was found verbatim by script.
- **Second-read verification:** an automated second read judged 294 of 80,948 claims unsupported (0.36%). This is not our error rate: in the pilot the automated read caught far fewer problems than human raters did. The pre-registered measure is a human audit of 250 claims against the < 2% target, which is ready and awaiting panel ratings.
- **Concordance with ClinVar:** gene concordance is near ceiling. HGVS recall against ClinVar's own citations is low, at 10–35% of (paper, variant) pairs at the allele level, and concentrated in a few papers. A human triage of 50 misses is ready.
- **Completeness:**
  - HA20 (Chen 2020): 9 of 9 catalogue variants whose source papers we had;
  - Alexander disease (Grossi 2024): 54 of 56; the two misses are notation differences.
- **Gap closure:** 215 variants extracted from the literature have no ClinVar record with the same GRCh38 allele. An evidence sheet is ready for each one, with 4,725 verbatim quotes and no proposed classification, and the panel's adjudication page is built. OMIM could not be checked (no access).
- **Memorization:** a black-box probe of 180 papers found no recall of the papers' variants or text beyond guesses and formulaic phrases. Only 10 corpus papers postdate the model's cutoff, so the before/after comparison is weak.
- **Exploratory:** the extracted Danon cohort reproduces the published male/female severity difference (GPSEA, BH-corrected).

**What's next.**
- Panel ratings (audit and gap-variant adjudication);
- the bias arm against held-out cohort papers;
- the Claude vs open-weight comparison, once the hosted account is open (the agent loop is built and tested);
- ClinVar submissions after panel sign-off.

**Spend** (list-price readings of this project's Claude Code session):
- about $1,628 to date;
- of which the six-disease extraction and verification run was about $833 (lines 1–2);
- evidence sheets for the gap variants about $64 (line 3);
- the memorization probe about $5 (line 5).

We report spend per line, as committed, and will return what is unused.

Results will be published whether favorable or not.
