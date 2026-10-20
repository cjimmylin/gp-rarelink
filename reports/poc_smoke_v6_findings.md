# Pre-freeze smoke run: extraction v6 and gatekeeper v4 (2026-10-20)

*Run `poc-ha20-v6-smoke`, launched at commit `22f8e59`. It was approved by Jimmy on 2026-10-20 ("Run it now") under D-35, which made it the last step before tagging `pipeline-v1.0` (pre-registration §6.5, §13). The numbers come from `data/extracted/ha20/poc-ha20-v6-smoke/span_check.json` and `gatekeeper_v4_summary.json`, written by `span_check` and `gatekeeper_merge`. The manifest is `runs/poc-ha20-v6-smoke/manifest.json`. This was a smoke run, not an audit; no person rated any claim.*

## 1. What ran

- **Papers:** the same 20 HA20 papers as the D-29 re-run (`runs/poc-ha20-v6-smoke/selection.json`).
- **Pinned files** (sha256, first 12 characters; unchanged from launch to finish):
  - `extract_v6.md` `aa689f24b470`;
  - `gatekeeper_v4.md` `48ec4f05e65f`;
  - `schema_ha20_v5.json` `f0fdf6b3bfea`;
  - `extraction_rules_v1.md` `55ab99df7f17`.
- **Helpers:**
  - 20 Opus extraction helpers, one per paper. One got a repair-only resume: 36064566 had left 272 label spans empty, the same lapse seen in the v5 subset. A diff showed 272 fills and no other change.
  - 24 Opus gatekeeper helpers, one per claim chunk.
- **Cost:** session readings rose from $724.22 to $777.72, so +$53.50 including orchestration, against an estimate of about $80 (`BUDGET.md`).

## 2. Results

**The check the pre-registration set for this run (§6.5) was met.** The span check (`--schema v5`) found 0 problems: 13,382 values over 162 individuals, every span verbatim in its paper.

**Gatekeeper v4** judged all 4,538 model claims (the other 8,844 are bookkeeping fields), with no chunk missing and each claim judged once.

| Verdict | Claims |
|---|---|
| supported | 4,440 |
| partially supported | 75 |
| unsupported | 23 |
| span not found | 0 |

- **Unsupported share:** 0.51% (exact 95% CI 0.32%–0.76%).
- **Not fully supported** (adding partial): 2.16% (1.76%–2.63%).
- **For comparison only:** gatekeeper v3 on the v5 extraction of the same papers gave 0.34% and 2.68%. These are gatekeeper rates, not error rates: in the pilot, the gatekeeper found far fewer problems than the human audit did (`NOTES_FOR_AGENTS.md`, Stage 4–5 lessons). They are not an estimate of the < 2% target, which is measured by the 250-claim human audit (O1).

**Who the quote is about** (`about` against `verdict`):
- `other_person`: 6, all unsupported. Under v3, 20 such claims were judged only partially supported. v4's helpers applied the hard rule consistently this time.
- `cohort_general`: 3, all unsupported.
- `unclear`: 6, all unsupported.
- `named_group`: 554 supported, 6 partial.

## 3. The 23 unsupported claims

| Cause | Claims | Papers |
|---|---|---|
| Variant field (mostly the gene symbol) for a previously reported patient, taken from another patient's sentence or from "reported in several patients" | 9 | 40822695 (7), 41905891 (2) |
| Phenotype status "observed" resting only on a hedged word ("suggested", "possible", 可疑 "suspected") | 5 | 31299923, 31384100, 35958611 (2), 41905891 |
| Phenotype rows for P3 resting on figure legends that the text assigns to P4 (the paper contradicts itself) | 6 | 31299923 |
| Free-text detail adding facts outside the cited spans | 3 | 35154120 |

What these mean for the freeze:
- **The variant rule (v5, D-29) is written down but not always followed.** In two papers, helpers gave earlier patients the gene symbol from a sentence about someone else. The gatekeeper caught all nine. Phenopackets are built only from supported claims (§6.4), so these become "not reported", not wrong values.
- **The extraction prompt has no hedge rule; the gatekeeper does** (gatekeeper v2 onward: a status resting only on a hedged phrase is unsupported). Extraction v6 therefore records "suggested uveitis" as observed, and the gatekeeper then drops it. The end result is the correct three-state output (not reported), but it costs a flag each time. Adding the rule to extraction now would change a pinned file after its only test run. I have not changed it: v6 is frozen as tested, and the gap is listed here as a known behavior. See §5.
- **Stacked-cell abstention (D-31) worked** where it applied: in 42128528, multi-patient cells were used only for labels and whole-family facts, never read by position.

## 4. Partially supported claims (75)

The commonest causes, from the helpers' reasons:
- an age when something was noted, tested or diagnosed, recorded as an onset age (31164164, 33446651, 35154120, 35958611, 40719110, 31299923);
- details in a free-text summary that sit outside the quoted span (36064566, 37388287, 38006337, 39167656);
- joint citations such as "(31, 47)" used as one person's source reference (34899744);
- vital status "alive" inferred from a current age (31164164).

**Papers that contradict themselves** (text against table, or legend against text) were noted by the helpers in 31164164, 31299923, 35958611, 36064566 and 38006337. Those claims were judged on their own spans, and the conflict is recorded in the reason column. They are candidates for the human audit.

## 5. Extraction behaviors to note (seen while checking the extraction, before the gatekeeper)

- **Scope:** v6 does not settle unnamed patients who have no individual facts (42169681).
- **A control carrying a variant was included** (L001 in 40719110).
- **Group statements were applied per person** (36064566). The gatekeeper judged these on the named-group rule.

None of §3–5 is a reason to hold the freeze. The pre-registration's check for this run was the span check, and it was met. The < 2% target is measured by the human audit on the six-disease study, and the frozen route builds phenopackets only from claims the gatekeeper supports. If Jimmy wants the hedge rule in extraction, it can go in now as v7, before tagging. That needs another smoke run (about $55), and the change would be a revision, not a deviation.
