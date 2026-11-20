# fig_pipeline_overview: plan

Type: conceptual diagram (no data plotted). Sources: `raw_materials/idea.md` (Core idea 1-7),
`raw_materials/experimental_log.md` §1.3, §1.4, §1.5, §1.6, §1.7, §1.8, §1.9, §2.1.2, §2.1.8, §2.5.
Outline entry: `outline.json` → plotting_plan → fig_pipeline_overview.

## Planner: elements, labels, connections

Two horizontal lanes, read left to right, separated by a labelled wall.

### Top lane: "Extraction (pipeline/extract; frozen 2026-10-20, pre-registration v1.0)"
(log §1.5: frozen 2026-10-20, v1.0; §1.8: code under pipeline/extract)

1. **Corpus**: PubMed + backward citation search; title/abstract screening by Sonnet helpers;
   full-text screening; open access only (PMC, Europe PMC, Unpaywall; D-32). (log §1.4, §1.6)
2. **Extraction**: one Claude Opus helper per paper, reading only that paper + the frozen files
   (extract_v6, schema v5, rules v1); five tables; every value = value + verbatim quote + PMID;
   phenotypes observed / excluded / not reported. (idea Core 1-2; log §1.5, §1.6, §1.7)
3. **Span check** (deterministic): every quote found verbatim in the paper. Badge, the only
   number in the figure: "241,730 values, 0 span-check problems (registered six)". (log §1.7;
   §2.1.2 table row "All six": 241,730 values, 0 span-check problems)
4. **Gatekeeper v4**: second Claude read of every claim; verdicts supported / partially
   supported / unsupported / span not found; only supported claims go on. (idea 3; log §1.7)
5. **Stage 4**: reconciliation (citation-only, one-to-one merges, policy v4); VariantValidator
   on MANE Select, original string kept; HPO + Mondo binding (pinned releases). (log §1.7)
6. **Output**: GA4GH Phenopackets v2, schema-validated. (log §1.7)

Arrows 1 → 2 → 3 → 4 → 5 → 6.

### Wall
Dark bar across the full width: "Isolation test: no ClinVar / OMIM in extraction" (log §1.8).
Only arrows that go DOWN cross it. Nothing from the bottom lane points into the top lane; the
reference box points only right, into O2 and O3.

### Bottom lane: "Harness (held-out ground truth, read only after extraction)"
(idea Core 5; log §1.3, §1.8, §1.9)

- **Held-out reference**: dated ClinVar snapshot; OMIM entry pages frozen 2026-10-28 (log §1.3).
- **O2 concordance** with ClinVar (and OMIM) (log §1.9).
- **O3 gap candidates**: absent from ClinVar and OMIM (log §1.9 O3).
- **Evidence dossiers**: verbatim quotes, no proposed classification (log §1.8, §2.1.8).
- **People** (green; no names): O1 audit of gatekeeper-supported claims; triage of ClinVar
  misses; gap adjudication; pointer "see human-assessment figure" (log §1.9, §2.5; idea 7).

Connections: reference → O2; reference → O3; O3 → dossiers → people; O2 → people (misses to
triage).

### Cross-lane arrows (downward through the wall)
- Output (6) → O2 and O3, labelled "phenopackets" (harness reads extracted records, log §1.8).
- Gatekeeper (4) → People, labelled "supported claims" (O1 claim pool = every claim gatekeeper v4
  judged supported, log §1.9). The two routes must cross once; the crossing is drawn as a gap.

No outcome values anywhere (no rates, recalls, counts of candidates, no human results).

## Stylist

- Final size = ICLR text width: 5.5 in wide (template `\textwidth 5.5 true in`), 2.95 in high,
  so 8 pt text stays 8 pt in print. The outline asked for 21:9; that height cannot hold the
  requested box text at ≥ 8 pt, so the rendered figure is about 16:9 (1710 x 945 px at 300 dpi).
- Font: Liberation Sans (Arial metrics), 8 pt body, 8 pt bold box titles, 8 pt lane labels.
- White background. Lane tints: extraction light blue (#E8F2F9) with boxes edged #0072B2;
  harness light orange (#FDF3E1) with boxes edged #E69F00; People box edged #009E73 on
  #E6F5F0. Wall #4D4D4D with white bold text. Span-check badge: white with black edge.
- Arrows dark grey #333333, 0.8 pt, filled heads. No grid, no shadows, no 3-D.
- No caption or "Figure N" inside the image.

## Revisions after critique (box texts as finally drawn)

- Box widths refitted so all six top boxes sit inside the 5.5 in lane (round 1 overflowed it).
- Span check body shortened to "quotes found verbatim" so the badge no longer covers it; the badge
  reads "241,730 values, 0 span-check problems (registered six)" on four lines.
- Gatekeeper title "4 Gatekeeper" with "v4" moved to the body ("v4: Claude re-reads every claim;
  only claims judged 'supported' go on"); Stage 4 reads "VariantValidator (MANE Select), original
  kept".
- The phenopackets route now passes under the supported-claims route through a small gap instead
  of a white halo; O2 and O3 are enclosed together (dashed) as the target of the phenopackets arrow.
