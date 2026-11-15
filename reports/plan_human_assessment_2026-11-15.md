# Human assessment with eight raters: Plan A (registered six) and Plan B (all twelve) (2026-11-15)

*Accepted by Jimmy on 2026-11-15 (D-55): the design and the calibration floor. Plan A or B and the hours per week are left open; the work goes step by step. Numbers come from `analysis/assessment_plan/design.py --date 2026-11-15` (`analysis/assessment_plan/design_2026-11-15.json`), which reads the committed samples and candidate tables. Time figures are planning assumptions unless marked measured; the calibration round replaces them with measured ones. Raters are R1 to R8 here; no names are in the repository. No page is built or published yet.*

## 1. Summary

| | Plan A: registered six | Plan B: all twelve |
|---|---|---|
| Extracted values audited | 250 | 527 |
| ClinVar misses triaged | 50 | 146 |
| Gap candidates adjudicated | 214 | 269 |
| **Entries covered** | **514** | **942** |
| Independent readings collected | 1278 + third readings | 2411 + third readings |
| Hours per rater, planning figure (range) | 21.1 (13.7–41.9) | 28.6 (17.9–56.6) |
| Rater hours in all, planning figure (range) | 169.2 (109.5–334.8) | 228.9 (143.2–453.2) |
| Calendar time at 2, 3, 5 hours per rater per week | 11, 8, 5 weeks | 15, 10, 6 weeks |

Both plans cover every entry that is waiting for a person: the whole audit sample, the whole triage sample and every gap candidate. Gap adjudication is about 76% of the time in Plan A, and its time per candidate is the least certain figure in the plan, which is why the range is wide. Plan B adds 428 entries for about 7.5 more hours per rater, because the six new diseases bring many audit claims and triage items, which are quick, and few gap candidates, which are slow.

**Recommendation: Plan B, in Plan A's order.** All eight do the calibration round; then the registered six, which are the primary result; then the extension five and Majeed with the same raters. After calibration the measured minutes replace the planning figures, and that is the point at which to confirm B or stop at A.

## 2. The design

The same four steps serve both plans. Each rater works alone on a private page that holds only that rater's items, and sees no one else's ratings and no gatekeeper verdict.

**Step 0. Calibration: all eight raters, the same items (about 2.7 hours each).**
- **Audit:** 40 claims with a known answer, half of them unsupported. They come from outside the three audit samples: the pilot's human-labelled claims, and claims the gatekeeper removed, which Jimmy labels first as the reference. The real samples are expected to hold only a few unsupported claims, too few to tell raters apart, so this set is where ability shows.
- **Adjudication:** 6 variants the runs extracted that ClinVar already classifies with settled review status, each with a dossier built the same way. Raters classify them without opening ClinVar.
- **What it gives:** each rater's hit rate on unsupported claims, false-alarm rate, agreement with the reference classification, and minutes per item. Those measured minutes replace the planning figures below.
- **A floor fixed in advance:** a rater who misses more than a set share of the unsupported calibration claims does not serve as one of the two registered raters of a claim; that rater's readings are still collected and reported. The floor (decided, D-55, before any calibration result exists): at least 15 of the 20 unsupported claims caught, and at least 18 of the 20 supported claims passed.

**Step 1. Audit of extracted values: every claim read by 3 raters.**
- The eight raters form 56 different groups of three. Claims are dealt across those groups by a seeded script, so each rater reads the same number of claims and every pair of raters shares the same number.
- **The registered analysis is kept.** For each claim the script names two of its three raters as the registered pair and the third as the tie-breaker, in rotation. The registered result uses the pair's labels and the tie-breaker's only where the pair disagrees, exactly as the frozen plan describes. Rule C (at most 4 unsupported of 250) is unchanged.
- **Beside it, labelled exploratory:** the majority-of-three label, agreement between every pair of raters, and each rater's estimated hit and false-alarm rates.

**Step 2. Triage of ClinVar misses: every item read by 2 raters;** Jimmy settles the items where they differ.

**Step 3. Adjudication of gap candidates: every candidate adjudicated by 2 raters independently.**
- The 28 possible pairs of raters each share the same number of candidates. Each rater works through one disease at a time.
- Where the two differ on the decision (approve, reject, needs discussion) or on the class across the pathogenic / uncertain line, a third rater reads the candidate. Two of the eight raters are panel members. The third reader is a panel member who was not one of the two adjudicators, or a rater who did best in calibration; the exact rule is fixed before adjudication starts.
- Nothing goes to submission without the panel's approval and Jimmy's sign-off; that is unchanged.

### How many raters per claim

For the registered audit of 250 claims, at 1 minute per claim:

| Raters per claim | Claims per rater | Claims shared by each pair of raters | Rater hours in all |
|---|---|---|---|
| 2: two raters, a third only on disagreement (as registered) | 62–63 | 8–9 | 8.3 |
| 3: three raters, every pair overlapping (recommended) | 93–94 | 26–28 | 12.5 |
| 4: four raters | 125 | 53–54 | 16.7 |
| 8: all eight rate every claim | 250 | 250 | 33.3 |

Three per claim is recommended. It gives every claim a blind third reading instead of a tie-breaker who knows the claim is disputed, it makes every pair of raters comparable, and it costs little because a claim takes about a minute. All eight on every claim would compare raters best but spends most of its time re-confirming claims everyone agrees on; the calibration set is the cheaper way to compare ability, because half of it is unsupported by construction.

### What calibration can and cannot tell apart

With 20 unsupported calibration claims, a rater's hit rate is known only roughly:

| Unsupported claims caught | Hit rate | 95% interval |
|---|---|---|
| 20 of 20 | 100% | 83%–100% |
| 18 of 20 | 90% | 68%–99% |
| 16 of 20 | 80% | 56%–94% |
| 14 of 20 | 70% | 46%–88% |
| 12 of 20 | 60% | 36%–81% |

So calibration separates a rater who catches nearly everything from one who misses a third or more, and it does not rank raters who are close. A set twice as large would give 36 of 40 an interval of 76%–97%, for twice the calibration time on the audit part. The audit itself adds evidence through each rater's agreement with the other two raters on every claim.

## 3. Plan A: the six registered diseases

| Task | Entries | Raters per entry | Readings | Entries per rater | Shared by each pair of raters | Hours per rater: planning figure (range) |
|---|---|---|---|---|---|---|
| Calibration (all eight, same items) | 40 claims + 6 variants | 8 | 368 | 46 | all | 2.7 |
| Audit of extracted values | 250 | 3 | 750 | 93–94 | 26–28 | 1.6 (0.8–3.1) |
| Triage of ClinVar misses | 50 | 2 | 100 | 12–13 | 1–4 | 0.8 (0.4–1.2) |
| Adjudication of gap candidates | 214 | 2 | 428 | 53–54 | 7–9 | 13.4 (8.9–26.8) |
| Third reading where two adjudicators differ | 86 if 40% differ (43 at 20%, 128 at 60%) | 1 | — | — | — | 2.7 on average (21.4 hours in all) |
| **Total** | **514** | | | | | **21.1 (13.7–41.9)** |

- **What the entries stand for.** The 250 claims are the registered sample of a pool of 78,564 extracted values; the 50 triage items are the registered sample of 263 ClinVar misses; the 214 gap candidates are all of them, resting on 372 reported individuals.
- **If time is short,** the audit and triage are cheap and go first. The table gives how many gap candidates then get two adjudications and a third where needed, if each rater gives a fixed number of hours in all:

| Hours per rater in all | Gap candidates fully adjudicated | Share |
|---|---|---|
| 8 | 38 of 214 | 18% |
| 12 | 92 of 214 | 43% |
| 16 | 145 of 214 | 68% |
| 20 | 198 of 214 | 93% |
| 24 | 214 of 214 | 100% |
| 30 | 214 of 214 | 100% |

With a cap, candidates are taken in a fixed order set before adjudication starts: those with a case report and no flag first, those known only from a review table last.

## 4. Plan B: all twelve diseases

| Task | Entries | Raters per entry | Readings | Entries per rater | Shared by each pair of raters | Hours per rater: planning figure (range) |
|---|---|---|---|---|---|---|
| Calibration (all eight, same items) | 40 claims + 6 variants | 8 | 368 | 46 | all | 2.7 |
| Audit of extracted values | 527 | 3 | 1581 | 197–198 | 56–57 | 3.3 (1.6–6.6) |
| Triage of ClinVar misses | 146 | 2 | 292 | 36–37 | 5–6 | 2.4 (1.2–3.6) |
| Adjudication of gap candidates | 269 | 2 | 538 | 67–68 | 9–11 | 16.8 (11.2–33.6) |
| Third reading where two adjudicators differ | 108 if 40% differ (54 at 20%, 161 at 60%) | 1 | — | — | — | 3.4 on average (26.9 hours in all) |
| **Total** | **942** | | | | | **28.6 (17.9–56.6)** |

- **What is added.** Extension five: 250 claims (sample of 46,363), 46 triage items, 43 gap candidates on 72 individuals. Majeed: 27 claims (sample of 4,971), 50 triage items (sample of 68 misses), 12 gap candidates on 22 individuals.
- **The three studies stay separate in every result.** The same eight raters and the same dealing rule serve all three, but the registered audit, the extension's audit and Majeed's are each scored on their own sample, as the plan, the addendum and D-54 require.
- **Two details.** The extension's triage sample was drawn with 48 items; 2 of them stopped being misses after the NOD2 fallback (D-53) and are left out here. 2 of Majeed's 12 candidates have no dossier until the text of record N88 is available.
- **With a cap on hours:**

| Hours per rater in all | Gap candidates fully adjudicated | Share |
|---|---|---|
| 8 | 0 of 269 | 0% |
| 12 | 47 of 269 | 17% |
| 16 | 100 of 269 | 37% |
| 20 | 154 of 269 | 57% |
| 24 | 207 of 269 | 77% |
| 30 | 269 of 269 | 100% |

## 5. Where the time figures come from

- **Audit, 1 minute per claim (range 0.5–2).** Measured for one rater only: in the two pilot audit sessions Jimmy entered 87 ratings in 56.7 minutes and 50 in 18.3 minutes, that is 0.65 and 0.37 minutes per rating (`adjudication/poc_audit*/ratings_raw.json`). The planning figure is higher because the volunteers are new to the pages and to some of the diseases.
- **Triage, 4 minutes per item (range 2–6).** Not measured; an assumption.
- **Adjudication, 15 minutes per candidate (range 10–30).** Not measured. The only data point is one candidate left open for 31 active minutes on the existing page with no decision entered. The page logs active minutes per candidate, so the six calibration variants give a first measured figure per rater.
- **Third readings.** The share of candidates on which two adjudicators differ is unknown; the plan uses 40% and shows 20% and 60%.
- **Totals.** The low end of each range combines the low figure for every task with 20% third readings; the high end combines the high figures with 60%.

## 6. If fewer than eight raters pass calibration

The dealing rule works for any number of raters. For Plan A:

| Raters | Audit claims per rater | Claims shared by each pair | Gap candidates per rater | Candidates shared by each pair |
|---|---|---|---|---|
| 8 | 93–94 | 26–28 | 53–54 | 7–9 |
| 7 | 107–108 | 35–36 | 61–62 | 10–11 |
| 6 | 125 | 49–52 | 71–72 | 14–15 |

## 7. What this changes in the registered plan

- **Registered:** two panel members rate each audit claim and a third resolves disagreements (§7.1); a panel member or Jimmy triages the misses (§7.2.6); the panel adjudicates gap candidates (§7.3). The extension addendum (§5) already lets volunteer reviewers take part once Jimmy names them.
- **Changed:** eight volunteer raters in rotating groups in place of two fixed raters and a tie-breaker; a calibration round with a floor; a third reading of every audit claim; two independent adjudications of every gap candidate. For the registered six this is a deviation and is logged as one when Jimmy approves it.
- **Not changed:** the samples, the labels, rule C, the panel's approval and Jimmy's sign-off before any submission, and the separation of the three studies. The registered audit result is still computed from two raters and a tie-breaker per claim.
- **Reported with it:** Cohen's κ was registered for two fixed raters. With rotating pairs it is reported for each pair of raters on the claims they share, with an overall agreement measure across all raters beside it.

## 8. Order of work

1. Jimmy decides D-55 (done for the design and the floor) and keeps the list of which rater is R1 to R8.
2. Claude draws 60 candidate calibration claims; Jimmy labels them on a reference page, blind to the gatekeeper; the first 20 he finds unsupported and the first 20 he finds supported, in a seeded order, are the calibration set. Claude builds the eight calibration pages and Jimmy shares them.
3. Raters do calibration. Claude reports each rater's results and measured minutes, applies the floor, draws the assignments by seed and re-prices the plan.
4. Claude builds each rater's audit, triage and adjudication pages; Jimmy shares them. Raters work through the audit and triage first, then adjudication by disease.
5. Third readings, the panel's approval, Jimmy's sign-off.

Model cost is small: six calibration dossiers, about $3 at the measured rate of $0.49 per dossier (ten Majeed dossiers, 2026-11-15); the rest is scripts.

## 9. Left out of both plans

These also wait for a person and are not priced above:

- **Addendum batch 1:** 42 disputed gatekeeper verdicts and 6 full-text exclusions to confirm. **Batch 2:** 54 items listed for a human look.
- **Gap candidates:** 19 proposed same-person groups to confirm before or during adjudication.
- **Bias arm:** 4 comparator sheets, each filled by someone who has not seen the extracted frequencies.
- **Optional audit add-ons in the frozen plan** (§7.1 a and c: a sample before the gatekeeper, and a check of "not reported" values) and the open-weight comparison's blinded audit (§7.5); none has a sample yet. With three raters per claim, each 100-claim add-on costs about 0.6 hours per rater.

## 10. Decided and still open (D-55)

1. **The design: decided** (Jimmy, 2026-11-15). Three raters per audit claim, two per triage item, two per gap candidate with a third reading on disagreement.
2. **The calibration floor: decided** (Jimmy, 2026-11-15), before any calibration result exists.
3. **The panel:** two of the eight raters are panel members (Jimmy, 2026-11-15). Still to fix before adjudication starts: who gives the third reading when a panel member is one of the two adjudicators, and what counts as the panel's approval.
4. **Plan A or Plan B: open.** The order of work is the same for both, so it is confirmed after calibration.
5. **Hours per rater per week: open.** Jimmy: the work goes gradually. The registered window for adjudication is Month 4, 2026-12-21 to 2027-01-20, across the holidays.
6. **Publishing:** his explicit word for each set of pages, as they are ready.

Building pages is publishing, so steps 2 and 4 each need Jimmy's explicit word. The twelve existing pages hold whole samples for two raters and one adjudicator and are replaced by per-rater pages; none has a rating in it.

