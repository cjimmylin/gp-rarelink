"""Cost estimate for the six-disease run with the frozen pipeline (pre-registration §6.5).

The method follows the plan: HA20's measured cost per input token is scaled by
each corpus's token count, not by paper count. Tokens are estimated as
characters / 4, the same rule as the `tokens` field in fulltext_md/*.meta.json
(no API key, so no exact count). Because every rate and every corpus uses the
same rule, the choice of divisor cancels out of the dollar figures.

Calibration (session list-price readings; estimates, not billing figures):
  smoke_v6   extraction v6 + gatekeeper v4, 20 HA20 papers, the frozen pipeline
             (runs/poc-ha20-v6-smoke/manifest.json). Central rate.
  v5_subset  extraction v5 + gatekeeper v3, the same 20 papers; an upper bound,
             because Stage 6 work overlapped (runs/poc-ha20-v5-subset/manifest.json).
  run2       extraction v3 only, 85 papers (BUDGET.md, runs/poc-ha20-run-2);
             used to split the central rate into extraction and gatekeeper.

Corpora:
  HA20       re-extracted in full with the frozen pipeline (plan §6.5, D-18):
             the 85 papers of run-2, as they now read in fulltext_md/.
  other five every paper included at full-text screening (fulltext_screen ==
             include; plan §5.1, D-05: all eligible accessible reports).
  Supplements have been fetched only for HA20. For the five new corpora the
  estimate adds HA20's supplementary share of characters as an allowance.

Scenarios: 1x (one clean pass), 1.25x (repairs, resumes, orchestration) and
2x (one full re-run after a fix logged under D-07). Optional items are listed
apart: the 10% re-extraction for run-to-run stability (plan §7.6, "if budget
allows") and HPO binding by Sonnet helpers.

  uv run python analysis/cost/six_disease_estimate.py
writes analysis/cost/six_disease_estimate_<date>.json and .md.
"""

from __future__ import annotations

import csv
import json
from datetime import UTC, datetime
from pathlib import Path

LIT = Path("data/literature")
OUT = Path("analysis/cost")
CHARS_PER_TOKEN = 4
DISEASES = ["ha20", "axd", "lad1", "ssadh", "danon", "tangier"]
NAMES = {"ha20": "A20 haploinsufficiency", "axd": "Alexander disease", "lad1": "LAD-I",
         "ssadh": "SSADH deficiency", "danon": "Danon disease", "tangier": "Tangier disease"}
MULTIPLIERS = {"1x": 1.0, "1.25x": 1.25, "2x": 2.0}
# Run-2's reading comes from BUDGET.md ("from $252.27 to $418.07"); its manifest keeps it as text only.
RUN2_USD = round(418.07 - 252.27, 2)
# Budget lines in CONTEXT.md §9.
LINES = {"extraction": 8000, "gatekeeper": 4000}
# HPO binding allowance: no separate reading exists (Stage 4 overlapped other work), so this is
# an assumption: 5% of the extraction cost, shown apart and not added to the totals.
HPO_BINDING_SHARE = 0.05
REPEAT_SHARE = 0.10


def md_chars(disease: str, pmids: list[str], md_dir: str = "fulltext_md") -> tuple[int, list[str]]:
    total, missing = 0, []
    for p in pmids:
        f = LIT / disease / md_dir / f"{p}.md"
        if f.exists():
            total += len(f.read_text(encoding="utf-8"))
        else:
            missing.append(p)
    return total, missing


def manifest(run: str) -> dict:
    return json.loads(Path(f"runs/{run}/manifest.json").read_text())


def eligible(disease: str) -> list[str]:
    rows = csv.DictReader((LIT / disease / "manifest.csv").open(newline=""))
    return [r["pmid"] for r in rows if r.get("fulltext_screen") == "include"]


def supplement_share() -> dict:
    """Share of HA20's current Markdown characters that came from appended supplements."""
    conv = list(csv.DictReader((LIT / "ha20/supplementary/conversion.csv").open(newline="")))
    appended = sum(int(r["chars_out"] or 0) for r in conv if r["status"].startswith("included"))
    total = sum(len(f.read_text(encoding="utf-8")) for f in (LIT / "ha20/fulltext_md").glob("*.md"))
    return {"appended_chars": appended, "ha20_total_chars": total,
            "share_of_total": round(appended / total, 4),
            "ratio_to_main_text": round(appended / (total - appended), 4)}


def main() -> int:
    smoke = manifest("poc-ha20-v6-smoke")
    v5 = manifest("poc-ha20-v5-subset")
    run2 = manifest("poc-ha20-run-2")
    smoke_ids = smoke["notes"]["documents"]
    smoke_chars, m1 = md_chars("ha20", smoke_ids)
    run2_chars, m2 = md_chars("ha20", run2["notes"]["documents"], "fulltext_md_run2")
    assert not m1 and not m2, (m1, m2)
    smoke_usd = smoke["notes"]["session_cost_usd_delta"]
    v5_usd = v5["notes"]["session_cost_usd_delta"]
    # Rates in dollars per million estimated input tokens.
    per_mtok = lambda usd, chars: usd / (chars / CHARS_PER_TOKEN) * 1e6
    rate = {
        "smoke_v6_ext_gk": per_mtok(smoke_usd, smoke_chars),
        "v5_subset_ext_gk_upper": per_mtok(v5_usd, smoke_chars),
        "run2_ext_only": per_mtok(RUN2_USD, run2_chars),
    }
    rate["gatekeeper_only_derived"] = rate["smoke_v6_ext_gk"] - rate["run2_ext_only"]
    split_ext = rate["run2_ext_only"] / rate["smoke_v6_ext_gk"]

    supp = supplement_share()
    corpora = []
    for d in DISEASES:
        ids = run2["notes"]["documents"] if d == "ha20" else eligible(d)
        chars, missing = md_chars(d, ids)
        allowance = 0 if d == "ha20" else round(chars * supp["ratio_to_main_text"])
        tok = (chars + allowance) / CHARS_PER_TOKEN
        corpora.append({"disease": d, "name": NAMES[d], "papers": len(ids), "missing_markdown": missing,
                        "chars": chars, "supplement_allowance_chars": allowance,
                        "est_tokens": round(tok),
                        "central_usd": round(tok / 1e6 * rate["smoke_v6_ext_gk"], 2),
                        "upper_usd": round(tok / 1e6 * rate["v5_subset_ext_gk_upper"], 2)})
    tot_tok = sum(c["est_tokens"] for c in corpora)
    tot_central = tot_tok / 1e6 * rate["smoke_v6_ext_gk"]
    tot_upper = tot_tok / 1e6 * rate["v5_subset_ext_gk_upper"]
    per_paper_check = smoke_usd / len(smoke_ids) * sum(c["papers"] for c in corpora)
    scen = {}
    for k, m in MULTIPLIERS.items():
        c = tot_central * m
        scen[k] = {"central_total": round(c, 2), "upper_total": round(tot_upper * m, 2),
                   "central_extraction": round(c * split_ext, 2),
                   "central_gatekeeper": round(c * (1 - split_ext), 2)}
    out = {
        "generated": datetime.now(UTC).isoformat(timespec="seconds"),
        "method": "pre-registration §6.5: HA20 cost per input token x corpus tokens; tokens = chars/4",
        "calibration": {
            "smoke_v6": {"papers": len(smoke_ids), "chars": smoke_chars, "usd": smoke_usd},
            "v5_subset": {"papers": len(smoke_ids), "chars": smoke_chars, "usd": v5_usd,
                          "note": "upper bound: Stage 6 work overlapped"},
            "run2_extraction": {"papers": len(run2["notes"]["documents"]), "chars": run2_chars, "usd": RUN2_USD},
            "usd_per_million_tokens": {k: round(v, 2) for k, v in rate.items()},
            "extraction_share_of_central": round(split_ext, 4),
        },
        "supplements": supp,
        "corpora": corpora,
        "totals": {"papers": sum(c["papers"] for c in corpora), "est_tokens": tot_tok,
                   "central_usd": round(tot_central, 2), "upper_usd": round(tot_upper, 2),
                   "per_paper_cross_check_usd": round(per_paper_check, 2)},
        "scenarios": scen,
        "optional": {"repeat_10pct_central_usd": round(tot_central * REPEAT_SHARE, 2),
                     "hpo_binding_allowance_usd": round(tot_central * split_ext * HPO_BINDING_SHARE, 2),
                     "hpo_binding_note": f"assumption: {HPO_BINDING_SHARE:.0%} of extraction; no separate reading exists"},
        "budget_lines_usd": LINES,
    }
    today = datetime.now(UTC).date().isoformat()
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / f"six_disease_estimate_{today}.json").write_text(json.dumps(out, indent=2) + "\n")

    f = lambda x: f"${x:,.0f}"
    L = [f"# Six-disease run: cost estimate ({today})", "",
         "*Generated by `analysis/cost/six_disease_estimate.py`. Session list-price readings, not billing figures. "
         "Tokens are characters / 4 throughout, so the divisor cancels out of the dollar figures.*", "",
         "## Rates from the pilot (dollars per million input tokens)", "",
         "| Source | Papers | $ | $/M tokens |", "|---|---|---|---|",
         f"| Smoke run, extraction v6 + gatekeeper v4 (central) | {len(smoke_ids)} | {smoke_usd:.2f} | {rate['smoke_v6_ext_gk']:.2f} |",
         f"| D-29 subset, extraction v5 + gatekeeper v3 (upper bound) | {len(smoke_ids)} | {v5_usd:.2f} | {rate['v5_subset_ext_gk_upper']:.2f} |",
         f"| Run-2, extraction only | {len(run2['notes']['documents'])} | {RUN2_USD:.2f} | {rate['run2_ext_only']:.2f} |",
         "", f"Extraction is {split_ext:.0%} of the central rate and the gatekeeper the rest (run-2's rate against the smoke run's).", "",
         "## Corpora", "",
         f"Supplement allowance for the five new corpora: {supp['ratio_to_main_text']:.1%} of main-text characters (HA20's measured share).", "",
         "| Disease | Papers | Est. tokens (incl. allowance) | Central | Upper |", "|---|---|---|---|---|"]
    for c in corpora:
        L.append(f"| {c['name']} | {c['papers']} | {c['est_tokens']:,} | {f(c['central_usd'])} | {f(c['upper_usd'])} |")
    L += [f"| **Total** | **{out['totals']['papers']}** | **{tot_tok:,}** | **{f(tot_central)}** | **{f(tot_upper)}** |", "",
          f"Cross-check by paper count instead of tokens (smoke run's cost per paper): {f(per_paper_check)}.", "",
          "## Scenarios against the budget lines", "",
          "| Scenario | Total (central) | Extraction | Gatekeeper | Total (upper) |", "|---|---|---|---|---|"]
    for k, s in scen.items():
        L.append(f"| {k} | {f(s['central_total'])} | {f(s['central_extraction'])} of {f(LINES['extraction'])} | "
                 f"{f(s['central_gatekeeper'])} of {f(LINES['gatekeeper'])} | {f(s['upper_total'])} |")
    L += ["", "Optional, not in the totals:",
          f"- 10% re-extraction for run-to-run stability (plan §7.6): about {f(out['optional']['repeat_10pct_central_usd'])};",
          f"- HPO binding by Sonnet helpers: about {f(out['optional']['hpo_binding_allowance_usd'])} ({out['optional']['hpo_binding_note']}).", ""]
    (OUT / f"six_disease_estimate_{today}.md").write_text("\n".join(L))
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
