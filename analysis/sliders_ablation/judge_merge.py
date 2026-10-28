"""Merge and summarize the locate-and-judge verdicts of the SLIDERS ablation (D-44, design §4.1).

Inputs:
  adjudication/sliders_ablation/judge/judge_key.json        id -> arm, source claim, group, hidden span
  adjudication/sliders_ablation/judge/verdicts/<chunk>.csv  one helper's verdicts per chunk
                                                            (claim_id, about, verdict, evidence, reason)
  data/extracted/<d>/pv1-<d>/gatekeeper_v4.csv              gatekeeper v4 verdicts, for arm S's sampled claims
  data/literature/<d>/fulltext_md/<pmid>.md                 to check that each quoted evidence occurs verbatim

Every judged claim gets exactly one verdict; the script fails if a chunk is missing, an id is judged
twice or not at all, or a verdict is not one of the four allowed values (--allow-missing reports
instead, for progress checks). "Unsupported" below counts unsupported and not_found; both are also
given alone. Intervals are exact (Clopper-Pearson) for shares; the D minus S difference carries a
Newcombe 95% interval (the Wilson-score method for two independent proportions).

Writes analysis/sliders_ablation/judge_verdicts.csv (one row per judged claim, arm revealed) and
judge_summary.json, and prints the per-disease table.

  uv run python analysis/sliders_ablation/judge_merge.py
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.claude_code.gatekeeper_merge import clopper_pearson, share

ROOT = Path(__file__).resolve().parents[2]
VERDICTS = ("supported", "partially_supported", "unsupported", "not_found")
WS = re.compile(r"\s+")
MARKUP = re.compile(r"[*_`|#]")


def norm(s: str) -> str:
    return WS.sub(" ", MARKUP.sub(" ", unicodedata.normalize("NFKC", s).lower())).strip()


def wilson_bounds(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return max(0.0, c - h), min(1.0, c + h)


def newcombe(k1: int, n1: int, k2: int, n2: int) -> dict:
    """95% interval for p1 - p2 (Newcombe 1998, method 10)."""
    if not n1 or not n2:
        return {"diff": None, "ci95": None}
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson_bounds(k1, n1)
    l2, u2 = wilson_bounds(k2, n2)
    d = p1 - p2
    lo = d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return {"diff": round(d, 6), "ci95": [round(lo, 6), round(hi, 6)]}


def block(rows: list[dict]) -> dict:
    n = len(rows)
    c = Counter(r["verdict"] for r in rows)
    out = {"n": n, "verdicts": {v: c.get(v, 0) for v in VERDICTS}}
    if n:
        out["unsupported_or_not_found"] = share(c["unsupported"] + c["not_found"], n)
        out["unsupported_only"] = share(c["unsupported"], n)
        out["not_found_only"] = share(c["not_found"], n)
        out["not_fully_supported"] = share(n - c["supported"], n)
        out["about"] = dict(Counter(r["about"] for r in rows))
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", default="adjudication/sliders_ablation/judge")
    ap.add_argument("--out", default="analysis/sliders_ablation")
    ap.add_argument("--allow-missing", action="store_true")
    a = ap.parse_args(argv)
    jdir = ROOT / a.dir
    key = {k["judge_id"]: k for k in json.loads((jdir / "judge_key.json").read_text())}
    chunks = sorted({k["chunk"] for k in key.values()})
    verdicts: dict[str, dict] = {}
    missing_chunks, problems = [], []
    for ch in chunks:
        f = jdir / "verdicts" / f"{ch}.csv"
        if not f.exists():
            missing_chunks.append(ch)
            continue
        for r in csv.DictReader(f.open()):
            cid = (r.get("claim_id") or "").strip()
            if cid not in key:
                problems.append(f"{ch}: verdict for unknown id {cid}")
                continue
            if key[cid]["chunk"] != ch:
                problems.append(f"{ch}: id {cid} belongs to chunk {key[cid]['chunk']}")
                continue
            if cid in verdicts:
                problems.append(f"{ch}: id {cid} judged twice")
                continue
            v = (r.get("verdict") or "").strip()
            if v not in VERDICTS:
                problems.append(f"{ch}: id {cid} verdict {v!r} not allowed")
                continue
            verdicts[cid] = {"about": (r.get("about") or "").strip(), "verdict": v, "evidence": r.get("evidence") or "",
                             "reason": r.get("reason") or ""}
    unjudged = [cid for cid, k in key.items() if cid not in verdicts and k["chunk"] not in missing_chunks]
    if (missing_chunks or unjudged or problems) and not a.allow_missing:
        raise SystemExit(json.dumps({"missing_chunks": missing_chunks, "unjudged": len(unjudged), "problems": problems[:20]}, indent=1))
    # gatekeeper v4 verdicts for arm S's sampled claims
    gk: dict[tuple[str, str], dict] = {}
    for d in sorted({k["disease"] for k in key.values()}):
        f = ROOT / f"data/extracted/{d}/pv1-{d}/gatekeeper_v4.csv"
        if f.exists():
            for r in csv.DictReader(f.open()):
                gk[(d, r["claim_id"])] = {"verdict": r["verdict"], "about": r.get("about", "")}
    texts: dict[tuple[str, str], str] = {}
    rows = []
    for cid, k in key.items():
        v = verdicts.get(cid)
        if not v:
            continue
        g = gk.get((k["disease"], k.get("source_claim_id", ""))) if k["arm"] == "S" else None
        ev_found = None
        if v["evidence"]:
            tk = (k["disease"], k["pmid"])
            if tk not in texts:
                p = ROOT / f"data/literature/{k['disease']}/fulltext_md/{k['pmid']}.md"
                texts[tk] = norm(p.read_text()) if p.exists() else ""
            ev_found = all(norm(x) in texts[tk] for x in v["evidence"].split(" || ") if x.strip()) if texts[tk] else None
        span_overlap = None
        if k["arm"] == "S" and v["evidence"] and k.get("span"):
            e, s = norm(v["evidence"]), norm(k["span"])
            span_overlap = bool(e and s and (e in s or s in e))
        rows.append({"judge_id": cid, **{x: k[x] for x in ("arm", "disease", "pmid", "table", "row", "field", "value", "individual", "context", "group")},
                     "source_claim_id": k.get("source_claim_id", ""), "about": v["about"], "verdict": v["verdict"], "evidence": v["evidence"],
                     "evidence_found_in_paper": ev_found, "reason": v["reason"],
                     "gatekeeper_v4_verdict": g["verdict"] if g else "", "judge_evidence_overlaps_extractor_span": span_overlap})
    out = ROOT / a.out
    out.mkdir(parents=True, exist_ok=True)
    with (out / "judge_verdicts.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    summary = {"judged": len(rows), "missing_chunks": missing_chunks, "unjudged": len(unjudged), "problems": problems, "diseases": {}}
    for d in sorted({r["disease"] for r in rows}):
        rd = [r for r in rows if r["disease"] == d]
        arms = {arm: [r for r in rd if r["arm"] == arm] for arm in ("S", "D")}
        kS = sum(r["verdict"] in ("unsupported", "not_found") for r in arms["S"])
        kD = sum(r["verdict"] in ("unsupported", "not_found") for r in arms["D"])
        entry = {"arms": {arm: block(rs) for arm, rs in arms.items()},
                 "difference_D_minus_S_unsupported": newcombe(kD, len(arms["D"]), kS, len(arms["S"])),
                 "by_group": {g: {arm: block([r for r in arms[arm] if r["group"] == g]) for arm in arms} for g in ("variant", "phenotype", "other")},
                 "excluded_statuses": {arm: block([r for r in arms[arm] if r["field"] == "status" and r["value"] == '"excluded"']) for arm in arms},
                 "observed_statuses": {arm: block([r for r in arms[arm] if r["field"] == "status" and r["value"] == '"observed"']) for arm in arms},
                 "evidence_quoted_found_in_paper": {arm: dict(Counter(str(r["evidence_found_in_paper"]) for r in arms[arm])) for arm in arms},
                 "arm_S_judge_vs_gatekeeper_v4": dict(Counter(f"judge={r['verdict']}|gk={r['gatekeeper_v4_verdict'] or 'none'}" for r in arms["S"])),
                 "arm_S_judge_evidence_overlaps_extractor_span": dict(Counter(str(r["judge_evidence_overlaps_extractor_span"]) for r in arms["S"])),
                 "top_fields_unsupported": {arm: dict(Counter(f"{r['table']}.{r['field']}" for r in arms[arm] if r["verdict"] in ("unsupported", "not_found")).most_common(6)) for arm in arms}}
        summary["diseases"][d] = entry
    (out / "judge_summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    pc = lambda b: "—" if not b or b.get("share") is None else f"{100 * b['share']:.1f}% ({b['k']}/{b['n']}; {100 * b['ci95'][0]:.1f}–{100 * b['ci95'][1]:.1f})"
    for d, e in summary["diseases"].items():
        print(f"{d}: S unsupported {pc(e['arms']['S'].get('unsupported_or_not_found'))} | D unsupported {pc(e['arms']['D'].get('unsupported_or_not_found'))} | "
              f"D-S {e['difference_D_minus_S_unsupported']}")
    if missing_chunks or unjudged:
        print(f"missing chunks: {len(missing_chunks)}; unjudged ids: {len(unjudged)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
