# fig_gatekeeper_by_run — plan

Type: statistical plot (forest plot, horizontal dot-and-whisker), two panels sharing rows.
Aspect ratio 4:3, double-column width (7.0 x 5.25 in).

## Variables → channels
- y: one row per main run (12) plus two pooled rows (diamonds) under the registered group; 14 rows.
- x (panel a): "unsupported or span not found" share, % (linear).
- x (panel b): "not fully supported" share (unsupported + partially supported), % (linear).
- colour/marker: standing of the run (registered six / extension five / exploratory).
- whiskers: exact (Clopper–Pearson) 95% CI where the log gives one.
- text at right of each row: n model claims judged.

## Data (copied exactly from `raw_materials/experimental_log.md`)

Panel (a) source: §2.0 "Per-run statistics (all 23 runs)" column "Unsupported or not found (95% CI)"
(registered rows identical in §2.1.2 table "Unsupported (exact 95% CI)"). Pooled rows: §2.1.2 bold rows.
Panel (b) source: registered six and pooled rows from §2.1.2 "Not fully supported (exact 95% CI)";
extension five from §2.0 "Not fully supported" column (no CI in the log); Majeed from §2.0
"3.7% (190/5161)" with CI 3.2–4.2 from §2.3 Extraction-and-gatekeeper bullet.

| Row | Run | Group | n judged | (a) % | (a) k/n | (a) CI | (b) % | (b) k/n | (b) CI |
|---|---|---|---|---|---|---|---|---|---|
| HA20 (development) | pv1-ha20 | registered | 23,129 | 0.20 | 46/23,129 | 0.15–0.27 | 1.93 | 446/23,129 | 1.75–2.11 |
| SSADH | pv1-ssadh | registered | 9,759 | 0.38 | 37/9,759 | 0.27–0.52 | 2.86 | 279/9,759 | 2.54–3.21 |
| Tangier | pv1-tangier | registered | 4,830 | 0.31 | 15/4,830 | 0.17–0.51 | 4.49 | 217/4,830 | 3.93–5.12 |
| LAD-I | pv1-lad1 | registered | 10,864 | 0.43 | 47/10,864 | 0.32–0.57 | 3.47 | 377/10,864 | 3.13–3.83 |
| AxD | pv1-axd | registered | 14,403 | 0.27 | 39/14,403 | 0.19–0.37 | 3.55 | 512/14,403 | 3.26–3.87 |
| Danon | pv1-danon | registered | 17,963 | 0.61 | 110/17,963 | 0.50–0.74 | 3.07 | 552/17,963 | 2.83–3.34 |
| Five confirmatory (without HA20), pooled | — | registered pooled | 57,819 | 0.43 | 248/57,819 | 0.38–0.49 | 3.35 | 1,937/57,819 | 3.20–3.50 |
| All six, pooled | — | registered pooled | 80,948 | 0.36 | 294/80,948 | 0.32–0.41 | 2.94 | 2,383/80,948 | 2.83–3.06 |
| GAMT | pv1-gamt | extension (D-52) | 9,981 | 0.63 | 63/9,981 | 0.49–0.81 | 4.8 | 481/9981 | not in log |
| PAPA | pv1-papa | extension (D-52) | 9,146 | 0.35 | 32/9,146 | 0.24–0.49 | 3.5 | 323/9146 | not in log |
| ATS | pv1-ats | extension (D-52) | 6,268 | 0.86 | 54/6,268 | 0.65–1.12 | 3.5 | 218/6268 | not in log |
| Blau | pv1-blau | extension (D-52) | 15,476 | 0.25 | 39/15,476 | 0.18–0.34 | 3.6 | 563/15476 | not in log |
| LCAT | pv1-lcat | extension (D-52) | 7,623 | 0.45 | 34/7,623 | 0.31–0.62 | 7.1 | 545/7623 | not in log |
| Majeed | pv1s-majeed | exploratory | 5,161 | 0.68 | 35/5,161 | 0.47–0.94 | 3.7 | 190/5161 | 3.2–4.2 |

Excluded on purpose: addendum batches (pv1a-*, pv1a2-*), repeats, open-weight and pilot runs;
no 2% target line, no human-audit value (log §2.1.2 "This is not an error rate", §5).

## Style (stylist pass)
- White background, sans-serif (DejaVu Sans), tick/label text 8 pt, group headers 8 pt bold.
- Colour by standing, Okabe–Ito: registered #0072B2, extension #E69F00, exploratory #009E73;
  pooled rows as darker-outlined diamonds in registered blue. Same colour-by-standing mapping as
  fig_o2_concordance.
- Circles for single runs, diamonds for pooled rows; whiskers 1 pt same colour; points without a
  CI in the log drawn as open circles (panel b, extension five) so the missing CI is visible.
- Thin light-grey vertical grid only; thin rules separate the three groups; no legend box —
  group names written as row-group labels on the y-axis side.
- Panel (a) x 0–1.2%; panel (b) x 0–8%. Panel titles "(a) Unsupported or span not found" and
  "(b) Not fully supported (adds partially supported)".
- n judged printed at right of panel (b), column header "n judged".
- Run IDs shown in y labels in small text: "HA20 (development) · pv1-ha20".
- Critic round 1 revisions: wider gap between panels (tick labels "1.2" and "0" collided);
  x-axis labels shortened to "% of model claims judged" (panel titles carry the measure);
  small marker key in panel (b) upper right: filled circle + whisker = run, exact 95% CI;
  open circle = run, no CI in log; diamond = pooled, exact 95% CI.
