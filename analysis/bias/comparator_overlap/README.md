# Comparator-cohort overlap tags (bias arm, O4)

*2026-11-15. Covers SSADH deficiency, A20 haploinsufficiency and Danon disease. Alexander disease is left untagged by decision D-48.*

Pre-registration §7.4.2 step 2 computes literature frequencies "over deduplicated individuals, excluding anyone in the comparator cohort". The comparator papers themselves are held out of the corpus, but the same patients also reach the corpus through other papers by the same investigators or clinics. This folder records, for every extracted individual, what the papers say about that.

Nothing here is a literature frequency, and no comparator sheet was filled. The comparator papers were read only for how they define their cohort.

## Files

| File | What it is |
|---|---|
| `paper_evidence.csv` | Hand-curated. One row per paper in the `pv1`, `pv1a` and `pv1a2` runs of the three diseases (228 papers): tag, rule and evidence. |
| `person_overrides.csv` | Hand-curated. People whose tag differs from their paper's (14 rows). |
| `tag_individuals.py` | Checks the two tables and expands them to one tag per phenopacket. |
| `tags_<date>.csv` | Output: one row per phenopacket (1,772 on 2026-11-15: SSADH 464, HA20 781, Danon 527). `frequency_deviation.py` reads the newest file. Every run numbers its identities from 0001, so each row also carries `run_prefixed_id` (for example `pv1a2-SSADH-ID0001`; D-50). |
| `tags_summary_<date>.json` | Output: counts by disease, run and tag, and the result of the quote check. |

Regenerate with `python3 -I analysis/bias/comparator_overlap/tag_individuals.py --date <date>`. Add `--text-dir <folder>` for paper text kept outside the repository; without the text, a quote is counted as not checkable rather than failed.

## The three comparator cohorts

- **SSADH deficiency: DiBacco 2019 (PMID 30656189).** The cohort is the investigators' registry at Boston Children's Hospital: "A total of 133 subjects with confirmed SSADH deficiency are enrolled in the registry; 49 are participating in the longitudinal study." Its feature table covers all 133. An earlier paper by the same group says the registry began in 2001 and takes questionnaires from families and referring physicians (PMID 26268900). The later natural history study recruits its Boston participants from the same registry (PMID 33393837).
- **A20 haploinsufficiency: He 2026 (medRxiv preprint).** "A total of 185 patients from 41 clinics across 7 countries were included". Patients "were referred to the study from rheumatology and immunology clinics"; the NIH patients were approved under "Study 94-HG-0105". The preprint does not say which of its patients were published before. It excludes patients with somatic variants ("Presence of somatic TNFAIP3 pathogenic variants rather than germline variants") and with missense variants.

- **Danon disease: Khedro 2025 (PMID 41121270).** "The cohort was comprised of 8 male pediatric and 1 male young adult patient, enrolled at the University of California, San Diego." The nine were enrolled between January and September 2019; the paper lists them as non-Hispanic and prints each patient's LAMP2 variant.

## Tags

| Tag | Meaning |
|---|---|
| `in_cohort_stated` | The paper or the comparator says the person is in the comparator cohort. |
| `in_cohort_probable` | The person comes from the cohort's own source (the registry investigators' database or studies, or the comparator's protocol) but is not named. |
| `in_cohort_possible` | A comparator investigator or clinic is behind the paper; the paper does not say where the person is held. |
| `outside_cohort` | The paper, or the comparator's own criteria, put the person outside the cohort. |
| `no_link_found` | Nothing links the paper to the comparator cohort. |
| `review_only` | The person is known only through another paper's citation of a paper that has no row here, so the source was not read. |
| `no_disease_term` | The phenopacket has no disease term (relatives, carriers, people whose diagnosis the paper does not state). Both cohorts hold confirmed cases only, so membership cannot be asserted. The tag the record would otherwise carry is in `tag_before_disease_check`. |

## Rules

Each evidence row names one rule. The rule fixes the tag.

| Rule | Tag | When it applies |
|---|---|---|
| `comparator_names_person` | stated | The comparator describes the person (SSADH: the registry subjects who died at 63 and 33). |
| `registry_database_named` | stated | The paper, published before the comparator, says its patients are in the investigators' database and that the database is taken from the registry. |
| `registry_group_database` | probable | A paper by the registry investigators draws on "our database" or "a patient database" without tying it to the registry. |
| `registry_group_study` | probable | Patients recruited by the registry investigators for their own clinical study or trial. |
| `natural_history_study` | probable | Participants of the SSADH natural history study (NCT03758521) or samples from its biorepository. The comparator counted 133 registry subjects; by February 2020 the registry held 143, so some participants joined after the comparator. |
| `same_protocol` | probable | The paper names the protocol the comparator names for the same centre (HA20: NIH 94-HG-0105). |
| `shared_investigator` | possible | A comparator author is among the paper's authors, and the paper gives another source for its patients or none (SSADH, Danon). |
| `comparator_clinic` | possible | The paper's own patients were seen at a hospital that is one of the comparator's clinics. |
| `outside_by_statement` | outside | A paper or the comparator says the person is not in the cohort, or what they say rules it out (Danon: a boy who died before the comparator enrolled anyone; a man far older than its oldest patient). |
| `excluded_by_comparator_criteria` | outside | The person meets one of the comparator's exclusion criteria (HA20: somatic or mosaic variants). |
| `no_link` | no_link_found | None of the above. |

An identity seen in several papers takes its strongest tag, in the order stated, probable, outside, possible, no link. A review-only row inherits the tag of the paper it cites when reconciliation resolved the citation to a paper with a row here.

## How the papers were checked

- **SSADH (52 papers).** PubMed author lists were compared with the comparator's seven authors. For the 43 papers whose full text is in the container, every sentence naming a registry, a database, the natural history study, a trial or how patients were recruited was read. Nine papers have no text here (`full_text_available = no`); they were judged from the PubMed record and the committed extraction quotes.
- **HA20 (88 papers).** PubMed affiliations were compared with the comparator's affiliation list; every match was checked by hand, because several were hospitals with similar names. For matched papers the text was read for where the patients were seen. Papers without a match were not read further.
- **Danon (88 papers).** PubMed author lists and affiliations were compared with the comparator's authors and its one centre: two papers, both from the Colorado group, share an author with it (one of them has a co-author at the comparator's centre), and no other paper comes from that centre. The 81 texts in the container were searched for the centre, the Colorado group, a registry, a natural history study and the gene-therapy trial; seven papers have no text here. Because the comparator prints its patients' variants, the corpus was also searched for them (see *Limits*).
- **Quotes.** Every quoted sentence was cut from the text by script and is looked up again by `tag_individuals.py`: 50 of 50 found on 2026-11-15. Each is a single sentence, from a paper whose extraction output was already in the repository or from an openly licensed comparator (D-51). Evidence taken from a PubMed author list or affiliation is marked as such and is not a quote from the paper.

## Limits

- Only two people can be matched to the comparator one to one. Everyone else is tagged through their paper, so a "probable" paper may hold people who are not in the cohort, and a "no link" paper may hold people who are.
- The SSADH registry takes questionnaires from families worldwide. A patient published by an unrelated clinic may still be in it; no paper would say so.
- The HA20 preprint does not list its patients or its 41 clinics. The clinic list used here is its author affiliation list, and the preprint's supplement was not read. Missense-only patients were not separated, although the comparator excludes them.
- 301 people with a disease term are `review_only` (SSADH 41, HA20 161, Danon 99, across the runs): their source papers are outside the corpus, so nothing could be read about where they were seen.
- **Danon, variants.** The comparator prints its nine patients' variants, so the corpus was searched for them. Two are recurrent point variants (c.877C>T in two of its patients, c.718C>T in one) and also occur in the corpus: in papers from Japan, Czechia, China, Greece and Iran with no link to the comparator, and in a review table (PMID 38351728) that cites three United States patients from papers of 2010 to 2013 (those three records carry no disease term). A shared recurrent variant is not evidence that it is the same person, so none of these is tagged as in the cohort; a person checking should start with those three rows. The comparator's other three point variants were not found, and its two deletions (exons 4 to 6; 286 kb covering the whole gene) match no deletion in the corpus by extent.
- **Rows cited from a comparator.** No review row cites one of the three comparators in use. Rows that cite the paywalled comparator candidates, which are not used (Aeschlimann 2018: 16 rows; Boucek 2011: 3; Mura 2021: 1), are left as they are.
- The tags follow the identities as extracted. Addendum identities (`pv1a`, `pv1a2`) are not deduplicated against the registered run.
- Alexander disease is not tagged (D-48): its open comparator, `gagliardi2024_axd_ukb`, is UK Biobank carriers, who are not the subjects of case reports. `frequency_deviation.py` says so in its output.

## Use in O4

Decided by Jimmy on 2026-11-15 (D-48, with a deviation entry in `DECISIONS.md`), before any comparator sheet was filled: the **primary analysis** uses the registered run, counts only records with a disease term, and removes people tagged `in_cohort_stated` or `in_cohort_probable`. `analysis/bias/frequency_deviation.py` reports beside it the same analysis with nobody removed, with only `stated` removed and with `possible` removed as well, each also on all records and on the registered run plus the addendum.

| Registered run, records with a disease term | All | Removed in the primary analysis | Left |
|---|---|---|---|
| SSADH deficiency | 311 | 115 | 196 |
| A20 haploinsufficiency | 447 | 9 | 438 |
| Danon disease | 322 | 0 | 322 |
