# fig_o2_concordance — plan

## Planner

Plot type: statistical plot (dot-and-whisker, three facets sharing a disease y-axis).

Channels
- y: disease (12 rows). Order top to bottom: registered six (HA20, SSADH, Tangier, LAD-I, AxD,
  Danon), then extension five (GAMT, PAPA, ATS, Blau, LCAT), then Majeed. A blank half-row and a
  thin grey rule separate the three groups.
- x: proportion in percent, axis 0–100% in every facet.
- facet (columns): (1) HGVS recall, tier 1; (2) HGVS recall, tiers 1+2; (3) Overlap, tier 1
  (share of extracted alleles in ClinVar; not precision).
- hue: standing (registered six / extension five, D-52 / Majeed, exploratory).
- whiskers: Wilson 95% intervals exactly as printed in the log (no recomputation for drawing;
  plot.py asserts that the Wilson interval recomputed from n/N rounds to the logged bounds).
- text: n/N to the right of each facet's plotting area, one per row.
- markers: "*" after Danon (figures predate the D-43 re-normalization; O2 not re-run);
  "†" after Blau (D-53 NOD2 legacy-transcript fallback applied). Both explained in the caption.
- No threshold line (D-03: no threshold applies).

Data points (percent, n/N, Wilson 95% CI), copied from experimental_log.md

Registered six — log §2.1.6, first table (run 2026-10-20; ClinVar release 2026-10-12, snapshot 2026-10-19)
| Disease | Tier 1 | Tiers 1+2 | Overlap, tier 1 |
|---|---|---|---|
| HA20 | 26.9 (21/78; 18.3–37.7) | 26.9 (21/78; 18.3–37.7) | 37.9 (39/103; 29.1–47.5) |
| SSADH | 10.1 (16/158; 6.3–15.8) | 14.6 (23/158; 9.9–20.9) | 87.2 (68/78; 78.0–92.9) |
| Tangier | 16.7 (1/6; 3.0–56.4) | 50.0 (3/6; 18.8–81.2) | 56.2 (9/16; 33.2–76.9) |
| LAD-I | 23.3 (14/60; 14.4–35.4) | 31.7 (19/60; 21.3–44.2) | 34.9 (45/129; 27.2–43.4) |
| AxD | 27.5 (14/51; 17.1–40.9) | 66.7 (34/51; 53.0–78.0) | 73.1 (49/67; 61.5–82.3) |
| Danon* | 35.0 (7/20; 18.1–56.7) | 50.0 (10/20; 29.9–70.1) | 47.9 (35/73; 36.9–59.2) |

Extension five — log §2.2, O2 table (snapshot 2026-11-14; ClinVar variant_summary of 09 Nov 2026; Blau with the D-53 fallback)
| Disease | Tier 1 | Tiers 1+2 | Overlap, tier 1 |
|---|---|---|---|
| GAMT | 69.2 (18/26; 50.0–83.5) | 69.2 (18/26; 50.0–83.5) | 90.1 (73/81; 81.7–94.9) |
| PAPA | 57.1 (8/14; 32.6–78.6) | 71.4 (10/14; 45.4–88.3) | 90.9 (10/11; 62.3–98.4) |
| ATS | 80.0 (16/20; 58.4–91.9) | 80.0 (16/20; 58.4–91.9) | 96.3 (26/27; 81.7–99.3) |
| Blau† | 13.6 (3/22; 4.7–33.3) | 13.6 (3/22; 4.7–33.3) | 63.0 (17/27; 44.2–78.5) |
| LCAT | 36.8 (7/19; 19.1–59.0) | 42.1 (8/19; 23.1–63.7) | 46.0 (23/50; 33.0–59.6) |

Majeed (exploratory) — log §2.3, O2 bullet (snapshot 2026-11-15; ClinVar release of 09 Nov 2026)
| Disease | Tier 1 | Tiers 1+2 | Overlap, tier 1 |
|---|---|---|---|
| Majeed | 6.6 (5/76; 2.8–14.5) | 10.5 (8/76; 5.4–19.4) | 50.0 (12/24; 31.4–68.6) |

36 points in all (12 diseases x 3 measures). Nothing else is drawn.

## Stylist

- Size 7.0 x 3.94 in (16:9, double column); white background; DejaVu Sans; all text 8 pt
  (facet titles 8.5 pt), none smaller.
- Colours by standing, shared with fig_gatekeeper_by_run: registered six #0072B2 (blue),
  extension five #E69F00 (orange), Majeed exploratory #009E73 (green). Text and rules dark grey.
- Marker: filled circle, 4.5 pt; whisker 1.1 pt, same colour, no caps.
- Grid: light vertical grid at 0/25/50/75/100%, 0.4 pt #DDDDDD; top/right spines off; y ticks
  only on the first facet.
- Group separators: thin #999999 0.6 pt horizontal rules across each facet.
- Standing legend: one row above the facets (three entries), no frame.
- n/N labels in a narrow strip to the right of each facet (outside the 0–100% axis), grey text.
- Facet titles on two lines each, so they align: "HGVS recall" / "tier 1"; "HGVS recall" / "tiers 1+2"; "Overlap, tier 1" / "(extracted alleles in ClinVar; not precision)".
- Tick labels 0/25/50/75/100 without "%" (the shared x note says Percent), so "100%" no longer crowds the n/N strip.
