# Human results that are not in yet (placeholders)

*Written 2026-11-20 for paper version 4. Every result below depends on people who have not finished
rating. The paper must not state, estimate, round or imply any of them. Wherever the text needs one,
it writes the LaTeX macro `\HR{<id>}` with the id exactly as listed. Until a value exists, the macro
prints a boxed "pending: <id>" marker. When the ratings come in, a script fills
`latex/human_results.tex` and the same sentences then print the real value.*

Rules for writers:
- Use only the ids below. Never invent an id, a value, a range, a direction ("likely low") or a
  comparison with a pending value.
- Write the sentence so it reads correctly whatever the value turns out to be: "The audit found
  \HR{o1_unsupported_n} of 250 claims unsupported (\HR{o1_unsupported_pct}; 95% CI \HR{o1_unsupported_ci})",
  never "only \HR{...}".
- A whole table cell may be a placeholder. A table of pending results is fine; label it "pending" in its caption.
- What is already measured (designs, sample sizes, seeds, page counts, the reference labels' counts, the
  planning figures) is in `experimental_log.md` and is written as normal numbers.

| id | What it will hold | Comes from |
|---|---|---|
| `cal_raters_finished` | Raters who rated all 40 calibration claims, of 9 invited | calibration pages |
| `cal_raters_pass` | Raters who met the floor (≥15 of 20 unsupported caught and ≥18 of 20 supported passed) | `calibration_score.py` |
| `cal_caught_median` | Median unsupported claims caught, of 20, among finished raters | `calibration_score.py` |
| `cal_passed_median` | Median supported claims passed, of 20, among finished raters | `calibration_score.py` |
| `cal_majority_agree` | Claims (of 40) on which the majority of finished raters agrees with the reference label | `calibration_score.py` |
| `cal_minutes_median` | Median minutes per calibration claim across finished raters | `calibration_score.py` |
| `plan_choice` | Plan A (registered six) or Plan B (all twelve), chosen by the PI after calibration | DECISIONS.md |
| `raters_main` | Raters who go on to the main assessment | DECISIONS.md |
| `o1_unsupported_n` | Registered audit: claims unsupported, of 250 | O1 audit pages |
| `o1_unsupported_pct` | The same as a percentage | O1 audit pages |
| `o1_unsupported_ci` | Its exact 95% interval | O1 audit pages |
| `o1_rule_c` | Whether the pre-registered decision rule C is met (at most 4 of 250 unsupported) | O1 audit pages |
| `o1_kappa_range` | Range of Cohen's kappa over pairs of raters on shared claims | O1 audit pages |
| `o1_gatekeeper_sens` | Share of human-unsupported claims the gatekeeper had also removed | O1 audit pages |
| `o1_by_disease` | Unsupported claims by disease (table) | O1 audit pages |
| `o1x_unsupported` | Extension audit (O1X), five reserve diseases: unsupported of 250 | O1X pages (Plan B only) |
| `o1m_unsupported` | Majeed audit: unsupported of 27 | Majeed pages (Plan B only) |
| `o2_triage_breakdown` | Registered triage of 50 ClinVar misses: counts by cause (extraction miss, conversion loss, not in paper, ClinVar error, other) | O2 triage page |
| `o2x_triage_breakdown` | Extension triage of 48 misses, the same counts | O2X page (Plan B only) |
| `o2m_triage_breakdown` | Majeed triage of 50 misses, the same counts | Majeed page (Plan B only) |
| `o3_adjudicated` | Gap candidates adjudicated, of the candidates left for the panel | O3 pages |
| `o3_accepted` | Candidates the panel accepts as a true gap variant with phenotype evidence | O3 pages |
| `o3_class_split` | Accepted candidates by classification (pathogenic / likely pathogenic / uncertain) | O3 pages |
| `o3_submissions` | Records prepared for submission after panel sign-off (none is submitted before that) | submissions/ |
| `o4_deviation` | Per-disease deviation of literature phenotype frequencies from the comparator cohorts (table) | comparator sheets, filled by a person |
| `o5_minutes_per_record` | Expert minutes per accepted record | adjudication page timings |
| `o5_openweight_audit` | Blinded human audit of the open-weight run: unsupported of the sampled claims | not yet built |
| `add_b1_ratings` | Addendum batch 1: the 42 disputed claims and 6 exclusions, as rated by a person | addendum sheets |
| `add_b2_audit` | Addendum batch 2: the 54-claim audit list, as rated | addendum sheets |
