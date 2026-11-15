"""Design and time estimates for the human assessment with eight raters (proposal D-55, 2026-11-15).

Reads the item counts from the committed samples and candidate tables, builds balanced
overlapping assignments for a given number of raters, and prices each plan in rater hours.
It draws no real assignment: item-to-rater lists are drawn later, by seed, once the raters
who pass calibration are known. Raters are R1..R8 here; no names go into the repository.

  python3 -I analysis/assessment_plan/design.py --date 2026-11-15

Writes analysis/assessment_plan/design_<date>.json and reports/plan_human_assessment_<date>.md.
The time figures are planning assumptions except where the text says "measured".
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import sys
from itertools import combinations
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from pipeline.extract.claude_code.gatekeeper_merge import clopper_pearson  # noqa: E402  (pure Python exact interval)

R = 8
SEED = 55250
# minutes per item: (low, planning figure, high)
MIN = {"audit": (0.5, 1.0, 2.0), "triage": (2.0, 4.0, 6.0), "adjudication": (10.0, 15.0, 30.0)}
K = {"audit": 3, "triage": 2, "adjudication": 2}
CAL = {"audit_claims": 40, "adjudication_variants": 6, "onboarding_min": 30}
THIRD = (0.2, 0.4, 0.6)        # share of candidates whose two adjudications disagree and go to a third reader
WEEKLY = (2, 3, 5)             # hours per rater per week
CAPS = (8, 12, 16, 20, 24, 30)  # hours per rater in total


def rows(p: str) -> list[dict]:
    with open(p, newline="") as fh:
        return list(csv.DictReader(fh))


def counts() -> dict:
    """Items per study and task, from the committed files."""
    def key(p):
        return json.loads(Path(p).read_text())
    cand = lambda p: [r for r in rows(p) if (r.get("status") or "") != "withdrawn"]
    reg, ext, maj = cand("adjudication/o3_gaps/candidates.csv"), cand("adjudication/o3_gaps_ext/candidates.csv"), cand("analysis/majeed/o3/candidates.csv")
    ext_miss = {(r["disease"], r["pmid"], r["clinvar_variation_id"]) for r in rows("analysis/extension/o2/o2_recall_misses.csv")}
    ext_tri = rows("adjudication/o2_triage_ext/sample.csv")
    mj_dos = json.loads(Path("adjudication/majeed/d51_review_public.json").read_text())["dossiers"]["written"]
    return {
        "registered six": {"audit": key("adjudication/o1_audit/sample_key.json")["n"], "audit_pool": key("adjudication/o1_audit/sample_key.json")["pool_total"],
                           "triage": len(rows("adjudication/o2_triage/sample.csv")), "misses": len(rows("analysis/six_disease/o2/o2_recall_misses.csv")),
                           "adjudication": len(reg), "identities": sum(int(r["n_identities"]) for r in reg), "with_dossier": len(reg)},
        "extension five": {"audit": key("adjudication/o1x_audit/sample_key.json")["n"], "audit_pool": key("adjudication/o1x_audit/sample_key.json")["pool_total"],
                           "triage": sum(1 for r in ext_tri if (r["disease"], r["pmid"], r["clinvar_variation_id"]) in ext_miss), "triage_drawn": len(ext_tri),
                           "misses": len(ext_miss), "adjudication": len(ext), "identities": sum(int(r["n_identities"]) for r in ext), "with_dossier": len(ext)},
        "Majeed (exploratory)": {"audit": key("adjudication/majeed/o1m_audit/sample_key.json")["n"], "audit_pool": key("adjudication/majeed/o1m_audit/sample_key.json")["pool_total"],
                                 "triage": len(rows("adjudication/majeed/o2_triage/sample.csv")), "misses": len(rows("analysis/majeed/o2/o2_recall_misses.csv")),
                                 "adjudication": len(maj), "identities": sum(int(r["n_identities"]) for r in maj), "with_dossier": mj_dos},
    }


def assign(n: int, raters: int, k: int, seed: int) -> list[tuple[int, ...]]:
    """n items, each to k of the raters, as evenly as possible over raters and over pairs of raters.

    Whole cycles use every k-subset once (perfect balance); the remainder is filled greedily,
    keeping rater loads within one of each other and pair counts as even as possible.
    """
    rng = random.Random(seed)
    combos = list(combinations(range(raters), k))
    out: list[tuple[int, ...]] = []
    for _ in range(n // len(combos)):
        c = combos[:]
        rng.shuffle(c)
        out += c
    load, pair = [0] * raters, {p: 0 for p in combinations(range(raters), 2)}
    for _ in range(n % len(combos)):
        c = combos[:]
        rng.shuffle(c)
        best = min(c, key=lambda s: (max(load[i] + 1 for i in s), max(pair[p] + 1 for p in combinations(s, 2)),
                                     sum(load[i] for i in s), sum(pair[p] for p in combinations(s, 2))))
        out.append(best)
        for i in best:
            load[i] += 1
        for p in combinations(best, 2):
            pair[p] += 1
    rng.shuffle(out)
    return out


def describe(a: list[tuple[int, ...]], raters: int) -> dict:
    load = [0] * raters
    pair = {p: 0 for p in combinations(range(raters), 2)}
    for s in a:
        for i in s:
            load[i] += 1
        for p in combinations(s, 2):
            pair[p] += 1
    return {"items": len(a), "ratings": sum(load), "load_min": min(load), "load_max": max(load),
            "pair_min": min(pair.values()), "pair_max": max(pair.values()), "pairs": len(pair)}


def hours(items_per_rater: float, kind: str) -> tuple[float, float, float]:
    return tuple(round(items_per_rater * m / 60, 1) for m in MIN[kind])  # type: ignore[return-value]


def rng_txt(lo, hi, unit="") -> str:
    return f"{lo}{unit}" if lo == hi else f"{lo}–{hi}{unit}"


def measured_audit_minutes() -> list[dict]:
    """Minutes per rating in the two pilot audit sessions (one rater: the PI), from the stored rating times."""
    import datetime as dt
    out = []
    for f in ("adjudication/poc_audit/ratings_raw.json", "adjudication/poc_audit_v5/ratings_raw.json"):
        ts = []

        def walk(x):
            if isinstance(x, dict):
                if "updated_at" in x:
                    ts.append(dt.datetime.fromisoformat(str(x["updated_at"]).replace("Z", "+00:00")))
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(json.loads(Path(f).read_text()))
        ts.sort()
        out.append({"file": f, "ratings": len(ts), "minutes_total": round((ts[-1] - ts[0]).total_seconds() / 60, 1),
                    "minutes_per_rating": round((ts[-1] - ts[0]).total_seconds() / 60 / len(ts), 2)})
    return out


def plan(name: str, studies: list[str], C: dict) -> dict:
    tot = {t: sum(C[s][t] for s in studies) for t in ("audit", "triage", "adjudication")}
    P = {"name": name, "studies": studies, "items": tot, "entries": sum(tot.values()), "tasks": {}}
    for t in ("audit", "triage", "adjudication"):
        d = describe(assign(tot[t], R, K[t], SEED), R)
        d["hours_per_rater"] = hours(d["ratings"] / R, t)
        d["person_hours"] = tuple(round(d["ratings"] * m / 60, 1) for m in MIN[t])
        P["tasks"][t] = d
    cal_min = CAL["onboarding_min"] + CAL["audit_claims"] * MIN["audit"][1] + CAL["adjudication_variants"] * MIN["adjudication"][1]
    P["calibration_hours_per_rater"] = round(cal_min / 60, 1)
    P["third"] = {str(s): {"candidates": round(s * tot["adjudication"]), "person_hours": round(s * tot["adjudication"] * MIN["adjudication"][1] / 60, 1)} for s in THIRD}
    base = P["calibration_hours_per_rater"] * R + sum(P["tasks"][t]["person_hours"][1] for t in P["tasks"])
    P["person_hours_plan"] = round(base + P["third"]["0.4"]["person_hours"], 1)
    lo = P["calibration_hours_per_rater"] * R + sum(P["tasks"][t]["person_hours"][0] for t in P["tasks"]) + round(0.2 * tot["adjudication"] * MIN["adjudication"][0] / 60, 1)
    hi = P["calibration_hours_per_rater"] * R + sum(P["tasks"][t]["person_hours"][2] for t in P["tasks"]) + round(0.6 * tot["adjudication"] * MIN["adjudication"][2] / 60, 1)
    P["person_hours_range"] = (round(lo, 1), round(hi, 1))
    P["hours_per_rater_plan"] = round(P["person_hours_plan"] / R, 1)
    P["hours_per_rater_range"] = (round(lo / R, 1), round(hi / R, 1))
    P["weeks"] = {str(w): math.ceil(P["hours_per_rater_plan"] / w) for w in WEEKLY}
    # coverage under a cap on each rater's total hours: calibration, audit and triage first, then adjudication
    fixed = P["calibration_hours_per_rater"] * R + P["tasks"]["audit"]["person_hours"][1] + P["tasks"]["triage"]["person_hours"][1]
    per_cand = MIN["adjudication"][1] * (K["adjudication"] + 0.4) / 60
    P["caps"] = {str(h): {"candidates": max(0, min(tot["adjudication"], int((h * R - fixed) / per_cand))),
                          "share": None} for h in CAPS}
    for h in P["caps"]:
        P["caps"][h]["share"] = round(P["caps"][h]["candidates"] / tot["adjudication"], 2)
    return P


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    a = ap.parse_args()
    C = counts()
    A = plan("Plan A", ["registered six"], C)
    B = plan("Plan B", ["registered six", "extension five", "Majeed (exploratory)"], C)
    audit_n = C["registered six"]["audit"]
    options = []
    for k, label in ((2, "two raters, a third only on disagreement (as registered)"), (3, "three raters, every pair overlapping (recommended)"),
                     (4, "four raters"), (8, "all eight rate every claim")):
        d = describe(assign(audit_n, R, k, SEED), R) if k < R else {"items": audit_n, "ratings": audit_n * R, "load_min": audit_n, "load_max": audit_n, "pair_min": audit_n, "pair_max": audit_n}
        options.append({"k": k, "label": label, **d, "person_hours": round(d["ratings"] * MIN["audit"][1] / 60, 1)})
    fewer = {str(r): {t: describe(assign(A["items"][t], r, K[t], SEED), r) for t in ("audit", "adjudication")} for r in (6, 7)}
    half = CAL["audit_claims"] // 2
    precision = [{"correct": k, "of": half, "share": round(k / half, 2), "ci95": [round(x, 2) for x in clopper_pearson(k, half)]} for k in (half, half - 2, half - 4, half - 6, half - 8)]
    double = [round(100 * x) for x in clopper_pearson(int(0.9 * 2 * half), 2 * half)]
    waiting = {"batch1_claims": len(rows("adjudication/addendum_d47/batch1_claims_to_rate.csv")), "batch1_exclusions": len(rows("adjudication/addendum_d47/batch1_exclusions_to_rate.csv")),
               "batch2_items": len(rows("analysis/corpus/free_copies/batch2_audit_list_2026-11-15.csv")), "proposed_merges": len(rows("adjudication/o3_gaps/proposed_merges.csv")),
               "comparator_sheets": len(list(Path("analysis/bias/comparator_sheets").glob("*.csv")))}
    dossier_cost = json.loads(Path("analysis/majeed/review_helper_costs_2026-11-15.json").read_text())["helpers"][0]["estimate_usd_at_opus_helper_rate"] / 10
    res = {"date": a.date, "raters": R, "seed": SEED, "minutes_per_item": MIN, "raters_per_item": K, "calibration": CAL, "counts": C,
           "plan_a": A, "plan_b": B, "audit_options": options, "fewer_raters": fewer, "calibration_precision": precision,
           "measured_audit_minutes": measured_audit_minutes(), "other_waiting_tasks": waiting}
    Path(f"analysis/assessment_plan/design_{a.date}.json").write_text(json.dumps(res, indent=1) + "\n")

    m = res["measured_audit_minutes"]
    L = [f"# Human assessment with eight raters: Plan A (registered six) and Plan B (all twelve) ({a.date})", "",
         f"*A proposal for Jimmy's decision (D-55, open). Numbers come from `analysis/assessment_plan/design.py --date {a.date}` "
         f"(`analysis/assessment_plan/design_{a.date}.json`), which reads the committed samples and candidate tables. "
         "Time figures are planning assumptions unless marked measured; the calibration round replaces them with measured ones. "
         "Raters are R1 to R8 here; no names are in the repository. Nothing in this plan has started, and no page is built or published.*", "",
         "## 1. Summary", "",
         "| | Plan A: registered six | Plan B: all twelve |", "|---|---|---|",
         f"| Extracted values audited | {A['items']['audit']} | {B['items']['audit']} |",
         f"| ClinVar misses triaged | {A['items']['triage']} | {B['items']['triage']} |",
         f"| Gap candidates adjudicated | {A['items']['adjudication']} | {B['items']['adjudication']} |",
         f"| **Entries covered** | **{A['entries']}** | **{B['entries']}** |",
         f"| Independent readings collected | {sum(A['tasks'][t]['ratings'] for t in A['tasks'])} + third readings | {sum(B['tasks'][t]['ratings'] for t in B['tasks'])} + third readings |",
         f"| Hours per rater, planning figure (range) | {A['hours_per_rater_plan']} ({rng_txt(*A['hours_per_rater_range'])}) | {B['hours_per_rater_plan']} ({rng_txt(*B['hours_per_rater_range'])}) |",
         f"| Rater hours in all, planning figure (range) | {A['person_hours_plan']} ({rng_txt(*A['person_hours_range'])}) | {B['person_hours_plan']} ({rng_txt(*B['person_hours_range'])}) |",
         "| Calendar time at " + ", ".join(f"{w}" for w in WEEKLY) + " hours per rater per week | " + ", ".join(f"{A['weeks'][str(w)]}" for w in WEEKLY) + " weeks | "
         + ", ".join(f"{B['weeks'][str(w)]}" for w in WEEKLY) + " weeks |", "",
         "Both plans cover every entry that is waiting for a person: the whole audit sample, the whole triage sample and every gap candidate. "
         f"Gap adjudication is about {round(100 * (A['tasks']['adjudication']['person_hours'][1] + A['third']['0.4']['person_hours']) / A['person_hours_plan'])}% of the time in Plan A, "
         "and its time per candidate is the least certain figure in the plan, which is why the range is wide. "
         f"Plan B adds {B['entries'] - A['entries']} entries for about {round(B['hours_per_rater_plan'] - A['hours_per_rater_plan'], 1)} more hours per rater, "
         "because the six new diseases bring many audit claims and triage items, which are quick, and few gap candidates, which are slow.", "",
         "**Recommendation: Plan B, in Plan A's order.** All eight do the calibration round; then the registered six, which are the primary result; then the extension five and Majeed with the same raters. "
         "After calibration the measured minutes replace the planning figures, and that is the point at which to confirm B or stop at A.", "",
         "## 2. The design", "",
         "The same four steps serve both plans. Each rater works alone on a private page that holds only that rater's items, and sees no one else's ratings and no gatekeeper verdict.", "",
         f"**Step 0. Calibration: all eight raters, the same items (about {A['calibration_hours_per_rater']} hours each).**",
         f"- **Audit:** {CAL['audit_claims']} claims with a known answer, half of them unsupported. They come from outside the three audit samples: the pilot's human-labelled claims, and claims the gatekeeper removed, "
         "which Jimmy labels first as the reference. The real samples are expected to hold only a few unsupported claims, too few to tell raters apart, so this set is where ability shows.",
         f"- **Adjudication:** {CAL['adjudication_variants']} variants the runs extracted that ClinVar already classifies with settled review status, each with a dossier built the same way. Raters classify them without opening ClinVar.",
         "- **What it gives:** each rater's hit rate on unsupported claims, false-alarm rate, agreement with the reference classification, and minutes per item. Those measured minutes replace the planning figures below.",
         "- **A floor fixed in advance:** a rater who misses more than a set share of the unsupported calibration claims does not serve as one of the two registered raters of a claim; that rater's readings are still collected and reported. "
         "The floor is Jimmy's to set before anyone sees calibration results (proposed: at least 15 of 20 unsupported claims caught, and at least 18 of 20 supported claims passed).", "",
         f"**Step 1. Audit of extracted values: every claim read by {K['audit']} raters.**",
         "- The eight raters form 56 different groups of three. Claims are dealt across those groups by a seeded script, so each rater reads the same number of claims and every pair of raters shares the same number.",
         "- **The registered analysis is kept.** For each claim the script names two of its three raters as the registered pair and the third as the tie-breaker, in rotation. "
         "The registered result uses the pair's labels and the tie-breaker's only where the pair disagrees, exactly as the frozen plan describes. Rule C (at most 4 unsupported of 250) is unchanged.",
         "- **Beside it, labelled exploratory:** the majority-of-three label, agreement between every pair of raters, and each rater's estimated hit and false-alarm rates.", "",
         f"**Step 2. Triage of ClinVar misses: every item read by {K['triage']} raters;** Jimmy settles the items where they differ.", "",
         f"**Step 3. Adjudication of gap candidates: every candidate adjudicated by {K['adjudication']} raters independently.**",
         "- The 28 possible pairs of raters each share the same number of candidates. Each rater works through one disease at a time.",
         "- Where the two differ on the decision (approve, reject, needs discussion) or on the class across the pathogenic / uncertain line, a third rater reads the candidate. "
         "The third reader is drawn from the raters who did best in calibration, or is a panel member.",
         "- Nothing goes to submission without the panel's approval and Jimmy's sign-off; that is unchanged.", "",
         "### How many raters per claim", "",
         f"For the registered audit of {audit_n} claims, at {MIN['audit'][1]:g} minute per claim:", "",
         "| Raters per claim | Claims per rater | Claims shared by each pair of raters | Rater hours in all |", "|---|---|---|---|"]
    for o in options:
        L.append(f"| {o['k']}: {o['label']} | {rng_txt(o['load_min'], o['load_max'])} | {rng_txt(o['pair_min'], o['pair_max'])} | {o['person_hours']} |")
    L += ["", "Three per claim is recommended. It gives every claim a blind third reading instead of a tie-breaker who knows the claim is disputed, it makes every pair of raters comparable, "
          "and it costs little because a claim takes about a minute. All eight on every claim would compare raters best but spends most of its time re-confirming claims everyone agrees on; "
          "the calibration set is the cheaper way to compare ability, because half of it is unsupported by construction.", "",
          "### What calibration can and cannot tell apart", "",
          f"With {half} unsupported calibration claims, a rater's hit rate is known only roughly:", "",
          "| Unsupported claims caught | Hit rate | 95% interval |", "|---|---|---|"]
    L += [f"| {p['correct']} of {p['of']} | {round(100 * p['share'])}% | {round(100 * p['ci95'][0])}%–{round(100 * p['ci95'][1])}% |" for p in precision]
    L += ["", "So calibration separates a rater who catches nearly everything from one who misses a third or more, and it does not rank raters who are close. "
          f"A set twice as large would give {int(0.9 * 2 * half)} of {2 * half} an interval of {double[0]}%–{double[1]}%, for twice the calibration time on the audit part. "
          "The audit itself adds evidence through each rater's agreement with the other two raters on every claim.", ""]

    def table(P: dict) -> list[str]:
        T = ["| Task | Entries | Raters per entry | Readings | Entries per rater | Shared by each pair of raters | Hours per rater: planning figure (range) |", "|---|---|---|---|---|---|---|",
             f"| Calibration (all eight, same items) | {CAL['audit_claims']} claims + {CAL['adjudication_variants']} variants | 8 | {8 * (CAL['audit_claims'] + CAL['adjudication_variants'])} | "
             f"{CAL['audit_claims'] + CAL['adjudication_variants']} | all | {P['calibration_hours_per_rater']} |"]
        for t, label in (("audit", "Audit of extracted values"), ("triage", "Triage of ClinVar misses"), ("adjudication", "Adjudication of gap candidates")):
            d = P["tasks"][t]
            T.append(f"| {label} | {d['items']} | {K[t]} | {d['ratings']} | {rng_txt(d['load_min'], d['load_max'])} | {rng_txt(d['pair_min'], d['pair_max'])} | "
                     f"{d['hours_per_rater'][1]} ({d['hours_per_rater'][0]}–{d['hours_per_rater'][2]}) |")
        th = P["third"]
        T.append(f"| Third reading where two adjudicators differ | {th['0.4']['candidates']} if 40% differ ({th['0.2']['candidates']} at 20%, {th['0.6']['candidates']} at 60%) | 1 | — | — | — | "
                 f"{round(th['0.4']['person_hours'] / R, 1)} on average ({th['0.4']['person_hours']} hours in all) |")
        T.append(f"| **Total** | **{P['entries']}** | | | | | **{P['hours_per_rater_plan']} ({rng_txt(*P['hours_per_rater_range'])})** |")
        return T

    reg, ext, maj = C["registered six"], C["extension five"], C["Majeed (exploratory)"]
    L += ["## 3. Plan A: the six registered diseases", ""] + table(A) + ["",
          f"- **What the entries stand for.** The {reg['audit']} claims are the registered sample of a pool of {reg['audit_pool']:,} extracted values; "
          f"the {reg['triage']} triage items are the registered sample of {reg['misses']} ClinVar misses; the {reg['adjudication']} gap candidates are all of them, resting on {reg['identities']} reported individuals.",
          "- **If time is short,** the audit and triage are cheap and go first. The table gives how many gap candidates then get two adjudications and a third where needed, if each rater gives a fixed number of hours in all:", "",
          "| Hours per rater in all | Gap candidates fully adjudicated | Share |", "|---|---|---|"]
    L += [f"| {h} | {A['caps'][str(h)]['candidates']} of {A['items']['adjudication']} | {round(100 * A['caps'][str(h)]['share'])}% |" for h in CAPS]
    L += ["", "With a cap, candidates are taken in a fixed order set before adjudication starts: those with a case report and no flag first, those known only from a review table last.", "",
          "## 4. Plan B: all twelve diseases", ""] + table(B) + ["",
          f"- **What is added.** Extension five: {ext['audit']} claims (sample of {ext['audit_pool']:,}), {ext['triage']} triage items, {ext['adjudication']} gap candidates on {ext['identities']} individuals. "
          f"Majeed: {maj['audit']} claims (sample of {maj['audit_pool']:,}), {maj['triage']} triage items (sample of {maj['misses']} misses), {maj['adjudication']} gap candidates on {maj['identities']} individuals.",
          "- **The three studies stay separate in every result.** The same eight raters and the same dealing rule serve all three, but the registered audit, the extension's audit and Majeed's are each scored on their own sample, as the plan, the addendum and D-54 require.",
          f"- **Two details.** The extension's triage sample was drawn with {ext['triage_drawn']} items; {ext['triage_drawn'] - ext['triage']} of them stopped being misses after the NOD2 fallback (D-53) and are left out here. "
          f"{maj['adjudication'] - maj['with_dossier']} of Majeed's {maj['adjudication']} candidates have no dossier until the text of record N88 is available.",
          "- **With a cap on hours:**", "", "| Hours per rater in all | Gap candidates fully adjudicated | Share |", "|---|---|---|"]
    L += [f"| {h} | {B['caps'][str(h)]['candidates']} of {B['items']['adjudication']} | {round(100 * B['caps'][str(h)]['share'])}% |" for h in CAPS]
    f6, f7 = fewer["6"], fewer["7"]
    L += ["", "## 5. Where the time figures come from", "",
          f"- **Audit, {MIN['audit'][1]:g} minute per claim (range {MIN['audit'][0]:g}–{MIN['audit'][2]:g}).** Measured for one rater only: in the two pilot audit sessions Jimmy entered "
          f"{m[0]['ratings']} ratings in {m[0]['minutes_total']} minutes and {m[1]['ratings']} in {m[1]['minutes_total']} minutes, that is {m[0]['minutes_per_rating']} and {m[1]['minutes_per_rating']} minutes per rating "
          "(`adjudication/poc_audit*/ratings_raw.json`). The planning figure is higher because the volunteers are new to the pages and to some of the diseases.",
          f"- **Triage, {MIN['triage'][1]:g} minutes per item (range {MIN['triage'][0]:g}–{MIN['triage'][2]:g}).** Not measured; an assumption.",
          f"- **Adjudication, {MIN['adjudication'][1]:g} minutes per candidate (range {MIN['adjudication'][0]:g}–{MIN['adjudication'][2]:g}).** Not measured. The only data point is one candidate left open for 31 active minutes on the existing page with no decision entered. "
          "The page logs active minutes per candidate, so the six calibration variants give a first measured figure per rater.",
          f"- **Third readings.** The share of candidates on which two adjudicators differ is unknown; the plan uses 40% and shows 20% and 60%.",
          "- **Totals.** The low end of each range combines the low figure for every task with 20% third readings; the high end combines the high figures with 60%.", "",
          "## 6. If fewer than eight raters pass calibration", "",
          "The dealing rule works for any number of raters. For Plan A:", "",
          "| Raters | Audit claims per rater | Claims shared by each pair | Gap candidates per rater | Candidates shared by each pair |", "|---|---|---|---|---|",
          f"| 8 | {rng_txt(A['tasks']['audit']['load_min'], A['tasks']['audit']['load_max'])} | {rng_txt(A['tasks']['audit']['pair_min'], A['tasks']['audit']['pair_max'])} | "
          f"{rng_txt(A['tasks']['adjudication']['load_min'], A['tasks']['adjudication']['load_max'])} | {rng_txt(A['tasks']['adjudication']['pair_min'], A['tasks']['adjudication']['pair_max'])} |",
          f"| 7 | {rng_txt(f7['audit']['load_min'], f7['audit']['load_max'])} | {rng_txt(f7['audit']['pair_min'], f7['audit']['pair_max'])} | {rng_txt(f7['adjudication']['load_min'], f7['adjudication']['load_max'])} | "
          f"{rng_txt(f7['adjudication']['pair_min'], f7['adjudication']['pair_max'])} |",
          f"| 6 | {rng_txt(f6['audit']['load_min'], f6['audit']['load_max'])} | {rng_txt(f6['audit']['pair_min'], f6['audit']['pair_max'])} | {rng_txt(f6['adjudication']['load_min'], f6['adjudication']['load_max'])} | "
          f"{rng_txt(f6['adjudication']['pair_min'], f6['adjudication']['pair_max'])} |", "",
          "## 7. What this changes in the registered plan", "",
          "- **Registered:** two panel members rate each audit claim and a third resolves disagreements (§7.1); a panel member or Jimmy triages the misses (§7.2.6); the panel adjudicates gap candidates (§7.3). "
          "The extension addendum (§5) already lets volunteer reviewers take part once Jimmy names them.",
          "- **Changed:** eight volunteer raters in rotating groups in place of two fixed raters and a tie-breaker; a calibration round with a floor; a third reading of every audit claim; two independent adjudications of every gap candidate. "
          "For the registered six this is a deviation and is logged as one when Jimmy approves it.",
          "- **Not changed:** the samples, the labels, rule C, the panel's approval and Jimmy's sign-off before any submission, and the separation of the three studies. The registered audit result is still computed from two raters and a tie-breaker per claim.",
          "- **Reported with it:** Cohen's κ was registered for two fixed raters. With rotating pairs it is reported for each pair of raters on the claims they share, with an overall agreement measure across all raters beside it.", "",
          "## 8. Order of work", "",
          "1. Jimmy decides D-55 and tells Claude which rater is R1 to R8 (names stay with him).",
          f"2. Claude builds the calibration set and eight calibration pages; Jimmy labels the {CAL['audit_claims'] // 2} reference claims that have no human label yet, and shares the pages.",
          "3. Raters do calibration. Claude reports each rater's results and measured minutes, applies the floor, draws the assignments by seed and re-prices the plan.",
          "4. Claude builds each rater's audit, triage and adjudication pages; Jimmy shares them. Raters work through the audit and triage first, then adjudication by disease.",
          "5. Third readings, the panel's approval, Jimmy's sign-off.", "",
          f"Model cost is small: six calibration dossiers, about ${6 * dossier_cost:.0f} at the measured rate of ${dossier_cost:.2f} per dossier (ten Majeed dossiers, 2026-11-15); the rest is scripts.", "",
          "## 9. Left out of both plans", "",
          "These also wait for a person and are not priced above:", "",
          f"- **Addendum batch 1:** {waiting['batch1_claims']} disputed gatekeeper verdicts and {waiting['batch1_exclusions']} full-text exclusions to confirm. **Batch 2:** {waiting['batch2_items']} items listed for a human look.",
          f"- **Gap candidates:** {waiting['proposed_merges']} proposed same-person groups to confirm before or during adjudication.",
          f"- **Bias arm:** {waiting['comparator_sheets']} comparator sheets, each filled by someone who has not seen the extracted frequencies.",
          "- **Optional audit add-ons in the frozen plan** (§7.1 a and c: a sample before the gatekeeper, and a check of \"not reported\" values) and the open-weight comparison's blinded audit (§7.5); none has a sample yet. "
          f"With three raters per claim, each 100-claim add-on costs about {round(100 * K['audit'] * MIN['audit'][1] / 60 / R, 1)} hours per rater.", "",
          "## 10. Decisions for Jimmy (D-55)", "",
          "1. **The design:** three raters per audit claim, two per triage item, two per gap candidate with a third reading on disagreement.",
          "2. **Plan A or Plan B,** or B confirmed after calibration as recommended.",
          "3. **The calibration floor,** fixed before any calibration result is seen.",
          "4. **The panel's place.** The frozen plan and the grant have the panel (Drs. Wu, Balderrama and Chacko) approve every record before submission. Are they among the eight? "
          "If so, they are the natural third readers; if not, they approve after the volunteers' adjudications.",
          "5. **Hours per rater per week,** which sets the calendar. The registered window for adjudication is Month 4, 2026-12-21 to 2027-01-20, across the holidays.",
          "6. **Publishing,** when each set of pages is ready.", "",
          "Building pages is publishing, so steps 2 and 4 each need Jimmy's explicit word. The twelve existing pages hold whole samples for two raters and one adjudicator and are replaced by per-rater pages; none has a rating in it.", ""]
    out = Path(f"reports/plan_human_assessment_{a.date}.md")
    out.write_text("\n".join(L) + "\n")
    print(out.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
