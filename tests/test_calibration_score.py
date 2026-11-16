"""The calibration scoring (D-55) on made-up labels: no real rater or reference data is read."""
from analysis.assessment_plan.calibration_score import FLOOR, score, sittings

REF = {f"U{n:02d}": "unsupported" for n in range(20)} | {f"S{n:02d}": "supported" for n in range(20)}


def labels(caught: int, passed: int, how: str = "unsupported") -> dict[str, str]:
    """A rater who catches the first `caught` unsupported claims and passes the first `passed` supported ones."""
    out = {}
    for n in range(20):
        out[f"U{n:02d}"] = how if n < caught else "supported"
        out[f"S{n:02d}"] = "supported" if n < passed else "unsupported"
    return out


def test_floor_is_both_sides():
    res = score(REF, {"R1": labels(15, 18), "R2": labels(14, 20), "R3": labels(20, 17)})["raters"]
    assert (FLOOR["caught"], FLOOR["passed"]) == (15, 18)
    assert res["R1"]["meets_floor"] is True
    assert res["R2"]["meets_floor"] is False      # one unsupported claim short
    assert res["R3"]["meets_floor"] is False      # one supported claim short


def test_cannot_verify_counts_as_caught_but_not_strictly():
    res = score(REF, {"R1": labels(16, 20, how="cannot_verify")})["raters"]["R1"]
    assert res["caught"] == 16 and res["caught_strict"] == 0 and res["meets_floor"] is True
    lazy = {c: "cannot_verify" for c in REF}       # answering "cannot verify" everywhere fails the supported side
    res = score(REF, {"R1": lazy})["raters"]["R1"]
    assert res["caught"] == 20 and res["passed"] == 0 and res["meets_floor"] is False


def test_unfinished_rater_is_not_given_a_verdict():
    part = {c: v for c, v in list(labels(20, 20).items())[:30]}
    res = score(REF, {"R1": part, "R2": labels(20, 20)})
    assert res["finished"] == ["R2"]
    assert res["raters"]["R1"]["meets_floor"] is None and res["raters"]["R1"]["rated"] == 30
    assert res["pairs"] == {}                      # pairs are counted among finished raters only


def test_capped_kind_and_common_claims_are_counted_apart():
    capped = {f"U{n:02d}" for n in range(5)}
    common = set(REF) - {"U19", "U18"}
    res = score(REF, {"R1": labels(10, 20)}, capped=capped, common=common)["raters"]["R1"]
    assert res["capped_kind"] == {"claims": 5, "caught": 5}
    assert res["other_kinds"] == {"claims": 15, "caught": 5}
    assert res["on_claims_in_all_three_versions"]["unsupported_claims"] == 18


def test_majority_of_the_others_leaves_the_rater_out():
    lab = {"R1": labels(20, 20), "R2": labels(20, 20), "R3": labels(20, 20), "R4": labels(0, 0)}
    res = score(REF, lab)
    assert res["raters"]["R4"]["agrees_with_majority_of_the_others"] == {"claims_with_a_majority": 40, "agrees": 0}
    assert res["raters"]["R1"]["agrees_with_majority_of_the_others"]["agrees"] == 40
    assert res["pairs"]["R1-R2"] == 40 and res["pairs"]["R1-R4"] == 0
    assert res["majority_of_the_finished_raters_vs_reference"] == {"claims": 40, "agrees": 40, "ties": 0}


def test_sittings_split_on_a_ten_minute_gap():
    s = sittings(["2026-11-20T10:00:00.000Z", "2026-11-20T10:01:00.000Z", "2026-11-20T10:02:00.000Z", "2026-11-20T10:30:00.000Z", "2026-11-20T10:31:00.000Z"])
    assert [g["ratings"] for g in s] == [3, 2]
    assert s[0]["minutes"] == 2.0 and s[0]["median_seconds_between_ratings"] == 60
