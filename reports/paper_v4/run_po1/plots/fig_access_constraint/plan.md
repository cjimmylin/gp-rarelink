# Plan: fig_access_constraint

Title (outline): "Literature access, not reading, bounds what the run can recover".
Type: statistical plot, two panels, 16:9, double-column (7.0 x 3.94 in).
Sources: `raw_materials/experimental_log.md` §2.1.1 (Corpus table) and §2.1.7 (OMIM holdout
table and the "Literature coverage, not reading, is the binding constraint" bullet).

## Panel (a): corpus funnel per registered disease (log §2.1.1 table)

Horizontal grouped bars. y = disease (top to bottom in the log's order: HA20, SSADH, Tangier,
LAD-I, AxD, Danon); within each disease four bars top to bottom; x = number of papers.

| Disease | In corpus (title/abstract) | Open full text (share of corpus) | Eligible after full-text screening | Papers extracted |
|---|---|---|---|---|
| HA20 (development) | 160 | 85 (53.1%) | not screened (pilot corpus) | 85 |
| SSADH | 171 | 59 (34.5%) | 40 | 40 |
| Tangier | 284 | 39 (13.7%) | 31 | 31 |
| LAD-I | 274 | 59 (21.5%) | 42 | 42 |
| AxD | 363 | 83 (22.9%) | 69 | 69 |
| Danon | 244 | 96 (39.3%) | 83 | 83 |

- HA20's eligible bar is absent; its slot carries the text "not screened (pilot corpus)".
- Value label at the end of every bar; the open-full-text label also gives the share, e.g.
  "85 (53.1%)".
- y tick label for HA20: "HA20 (dev.)" to mark it as the development disease (log: "HA20 (development)").

## Panel (b): OMIM holdout (log §2.1.7)

(b, top) Dot-and-whisker: x = OMIM allelic-variant recall anywhere in the run (tiers 1+2), %,
0 to 100; whisker = Wilson 95% CI as printed in the log. y = disease in the same order as (a),
then a pooled row ("All six") with a diamond marker, separated by a thin line.

| Row | k/n | Recall % | 95% CI |
|---|---|---|---|
| HA20 | 8/9 | 88.9 | 56.5–98.0 |
| SSADH | 4/7 | 57.1 | 25.0–84.2 |
| Tangier | 2/19 | 10.5 | 2.9–31.4 |
| LAD-I | 12/14 | 85.7 | 60.1–96.0 |
| AxD | 9/13 | 69.2 | 42.4–87.3 |
| Danon | 8/13 | 61.5 | 35.5–82.3 |
| All six (pooled) | 43/75 | 57.3 | 46.1–67.9 |

Direct label "k/n" beside each point.

(b, bottom) One stacked horizontal bar, total 84 = OMIM's source papers for these variants
(log §2.1.7 bullet; "5 of 84" also in the table's All-six row):
- extracted: 5
- in the corpus without an open copy: 38
- never returned by the searches: 38
- not in corpus (screened unclear/other): 3
Segment counts labelled; legend-like labels below the bar.

## Style (stylist pass)

- White background, no 3-D, sans-serif (DejaVu Sans), all text >= 8 pt at 7.0 in width.
- Okabe-Ito palette, one meaning per colour across both panels:
  - in corpus (title/abstract): light grey #BBBBBB
  - open full text: #0072B2 (blue)
  - eligible after full-text screening: #56B4E9 (sky blue)
  - extracted: #009E73 (green), used for "extracted" in both panels
  - in corpus without an open copy: #E69F00 (orange)
  - never returned by the searches: #D55E00 (vermillion)
  - not in corpus (screened unclear/other): #999999 (grey)
  - recall points: #000000, pooled diamond #000000
- Panel (a) legend at the top (4 entries, one row), no y-grid, light x-grid.
- Panel titles "(a) ..." and "(b) ..." as short axis titles; no caption or "Figure N" in the image.
- Top and right spines removed.
