# fig_human_assessment — plan (diagram)

Source: `raw_materials/experimental_log.md` §4 (D-55 design), §4.1 (calibration set, floor),
§4.2 (main assessment), §4.3 (Plan A / Plan B table), §7 (rule C: at most 4 of 250).
Design only: no results, no rater names, no capped kind or cap size, no pending human result.

## Planner: elements, labels, connections (left to right)

### Stage 1 band — "Stage 1: Calibration (due 2026-11-22)"  [log §4 Status]
1. Box "Reference labels": "PI labels 99 candidate claims from the registered runs, blind to the
   gatekeeper"  [§4.1 Reference labels; 99 = 60+15+24]
2. Box "Fixed set rule (+2 recorded amendments)" → "40 claims: 20 unsupported, 20 supported,
   from 39 papers"  [§4.1 Set rule, amendments, Final set]. Capped kind / cap size NOT shown.
3. Nine identical rater icons R1 … R9 (3×3), note: "same 40 claims, each in own order; no
   reference label, gatekeeper verdict or source pool shown"  [§4.1 Rater pages]
4. Diamond "Floor": "≥15 of 20 unsupported caught AND ≥18 of 20 supported passed"  [§4.1 Floor]
5. Decision box: "PI decides after calibration: who goes on; Plan A or Plan B"  [§4 bullet 2]
Arrows 1→2→3→4→5.

### Branches from the decision node (into Stage 2)  [§4.3 table]
- Plan A (registered six): 250 audit claims · 50 ClinVar misses · 214 gap candidates
- Plan B (all twelve): 527 audit claims · 146 ClinVar misses · 269 gap candidates

### Stage 2 band — "Stage 2: Main assessment"  [§4.2]
Three parallel tracks fed by the chosen plan:
(a) Audit: ring of 9 nodes with three overlapping triangles (rotating groups of three).
    "Each claim read by 3 raters in rotating, overlapping groups of three (84 groups with nine
    raters); equal loads; every pair shares claims. Script names a registered pair +
    tie-breaker per claim. Rule C: at most 4 of 250 unsupported."
(b) Triage of ClinVar misses: "2 raters per item; PI settles differences."
(c) Gap adjudication: "2 raters per candidate; a third where they differ on the decision or
    across the pathogenic / uncertain line."
All three → final box "Panel approval + PI sign-off before any submission record
(nothing submitted yet)".

Numbers drawn (complete list): 2026-11-22, 99, 40, 20, 20, 39, 9 (R1–R9), 15 of 20, 18 of 20,
250/50/214, 527/146/269, 3 raters, 84 groups, nine raters, 4 of 250, 2 raters, third.

## Stylist
- White background, no axes, no grid; sans-serif (DejaVu Sans), body text 8 pt, headers 9 pt bold.
- Okabe–Ito palette, edges in full colour, fills as light tints:
  calibration boxes #0072B2 (blue); rater icons #56B4E9 (sky); floor diamond #E69F00 (orange);
  PI decision #CC79A7 (purple); Plan A #0072B2, Plan B #D55E00 (consistent with figures that
  contrast registered six vs all twelve); audit track #009E73 (green); triage #E69F00;
  adjudication #D55E00; final sign-off box #000000 edge, grey fill.
- Stage bands as very light grey rounded panels with the stage title top-left.
- Arrows thin dark grey (#444444), solid; plan branches labelled directly.
- Double-column width 7 in; canvas 7 × 4.5 in (taller than 16:9, about 16:10, so every label fits at 8 pt without overflow; revised in critic round 1). No caption or "Figure N" inside the image.
- Layout: Stage 1 band on top (left to right); a connector from the floor diamond wraps down to the PI decision node at the left of the Stage 2 band; decision branches to Plan A / Plan B boxes; both feed three stacked track boxes (audit lane tallest, with a 9-node ring and three overlapping triangles); tracks collect into the sign-off box at right. Stage 2 title placed right of the connector. plot.py prints OVERFLOW if any text leaves its box.
