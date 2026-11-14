# Extension cost re-estimate after the GAMT pilot (D-47)

*2026-11-14, after `pv1-gamt` finished extraction and gatekeeper v4. Session readings are `get_session` cost readings for session_015Q6ZxH1ewYFQKq1axGZYx4; they include orchestration and can lag.*

| Item | Value |
|---|---|
| Session reading before pv1-gamt launch | $57.20 (~23:27 UTC) |
| Session reading after gatekeeper merge | $132.86 (~23:45 UTC, may lag) |
| pv1-gamt cost by readings | about $76: 23 extraction helpers, 2 label-span repairs, 43 gatekeeper helpers, 5 blind re-judges |
| Per paper (readings) | about $3.30 |
| Extraction by helper tokens (`analysis/cost/helper_tokens.py`) | 8.93 weighted M tokens, about $54 at $5.996 per weighted M (about $2.30 per paper) |
| Papers still to extract | 186 (blau 68, lcat 50, ats 34, papa 34) |
| Projection, central | 186 x $3.30 = about $610, plus Stage 4, 10% repeats and dossiers (about $150): total extension about $900 including the $132 spent |
| Projection, upper | $5 per paper: total about $1,300 |
| Ceiling (D-47) | $1,500 on line 7 |

Decision: proceed with the other four diseases; check the running total before each disease and stop and ask if it would pass $1,500.

**Gatekeeper integrity check.** Five chunks whose helpers reported script-assisted table checks (39006040_1, _3, _4; 42885896_5, _8) were re-judged blind into `data/extracted/gamt/pv1-gamt/gatekeeper_v4_rejudge/` with an explicit rule that scripts may only locate text (D-28). Agreement 1,749 of 1,750 claims (99.94%); the one difference (C010690) was stricter in the first pass. The first-pass verdicts stand.
