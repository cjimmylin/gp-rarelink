# Comparator listing sheets (bias arm, pre-registration §7.4.2 step 1)

**A person fills these, before any literature frequency is computed.** One CSV per held-out comparator paper. Open the paper yourself; the full text is open access (links below). List every feature the paper gives a cohort frequency for that maps to an HPO term, one row per feature.

| Column | What to enter |
|---|---|
| `comparator_key`, `pmid_or_doi` | pre-filled on the first row; repeat on every row |
| `cohort_n` | the cohort size the paper states |
| `cohort_type` | `clinical` (clinically ascertained) or `genotype-first` (for example a biobank) |
| `feature_as_stated` | the paper's wording |
| `hpo_id`, `hpo_label` | the HPO term (release 2026-09-01) |
| `n_with_feature`, `n_assessed` | the numerator and the number assessed for that feature, as printed; leave `n_assessed` blank if the paper gives only the cohort total |
| `frequency_as_printed` | e.g. "12/20 (60%)" |
| `location_in_paper` | table or page |
| `notes` | anything that limits the comparison |

**Two rules, so the comparison stays clean:**
1. **Don't look at our results first.** Before you finish, don't open the extracted phenopackets, `analysis/exploratory/gpsea/results/` or anything else that shows literature frequencies.
2. **Map features the paper's way.** List what the paper reports, not what you expect the literature to show.

**Sheets and papers** (open access, fetched 2026-10-21; `analysis/bias/comparators_2026-10-21.json`):
- `axd__gagliardi2024_axd_ukb.csv`: Gagliardi 2025, UK Biobank, PMID 39643430, PMC12322464 (genotype-first).
- `ssadh__dibacco2019_ssadh_natural_history.csv`: DiBacco 2019, PMID 30656189, PMC6331944.
- `danon__khedro2025_danon_prospective.csv`: Khedro 2025, PMID 41121270, PMC12542076.
- `ha20__he2026_ha20_multicenter.csv`: He 2026 multicenter preprint, DOI 10.64898/2026.01.01.25342105.

**Paywalled, so left out under D-32:** Mura 2021 (AxD, PMID 34865968), Boucek 2011 (Danon, PMID 21415759) and Aeschlimann 2018 (HA20, PMID 29317407). **No comparator exists for LAD-I or Tangier** (§7.4.1, D-35): the bias arm leaves those two out.

When a sheet is filled, run `uv run python analysis/bias/frequency_deviation.py`.
