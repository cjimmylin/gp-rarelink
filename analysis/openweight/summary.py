"""Claude vs open-weight model, run level (pre-registration §7.5, D-10).

For each disease, compares the Claude run (pv1-<d>) with the open-weight run (ow-<d>) on the
papers both runs have output for, and writes analysis/openweight/summary_<d>.json plus one
Markdown table for all diseases (analysis/openweight/summary.md). Registered metrics computed
here (the blinded audit and HGVS concordance are separate):

  span-not-found rate   from each run's span_check.json: asserted values whose quote is not in the
                        paper, plus asserted values with no quote at all, over asserted values;
                        both parts are also given alone. Cells not in the {value, span} shape are
                        counted from the span-check problems.
  coverage              individuals, variant rows, distinct target-gene variants (protein keys,
                        per paper), phenotypic-feature rows, checklist cells marked observed or
                        excluded.
  agreement             per paper, target-gene variant keys (the pilot's comparison): pooled
                        shared / union; checklist status agreement on cells both runs have.
  cost per paper        open-weight: cost the host reported per call, summed (from each paper's
                        log), with failed attempts counted apart; Claude: weighted helper tokens
                        (analysis/openweight/claude_helper_stats.json) at $5.996 per weighted
                        million, the rate the session readings gave for the six-disease run
                        (an estimate, not an invoice).
  wall-clock            per paper, median and total; open-weight from the transcript, Claude
                        from the helper transcript's first to last timestamp.

  uv run python analysis/openweight/summary.py --diseases ha20 ssadh
"""
import argparse
import json
import statistics
from collections import Counter
from pathlib import Path

from pipeline.extract.normalize_variants import is_gene, protein_key
from pipeline.harness.concordance import protein_short

CLAUDE_RATE = 5.996  # $ per weighted million tokens (BUDGET.md, six-disease run)
MISSING = (None, "", "not reported", "not stated", "unknown")


def cv(cell):
    return cell.get("value") if isinstance(cell, dict) else None


def tables(d, run, pmid):
    try:
        return json.loads(Path(f"data/extracted/{d}/{run}/per_paper/{pmid}.json").read_text()).get("tables") or {}
    except (OSError, json.JSONDecodeError):
        return None


def rows(t, name):
    return [r for r in (t.get(name) or []) if isinstance(r, dict)]


def vkeys(t, gene):
    out = set()
    for r in rows(t, "variants"):
        if is_gene(cv(r.get("gene_symbol_as_stated")), gene):
            for f in ("protein_hgvs_as_stated", "variant_original_string"):
                k = protein_key(cv(r.get(f)))
                if k:
                    out.add(protein_short(k))
    return out


def checklist(t):
    return {(str(cv(r.get("individual_label_in_paper"))), str(cv(r.get("checklist_feature")))): str(cv(r.get("status")))
            for r in rows(t, "phenotype_checklist")}


def span_block(d, run, pmids):
    """Span figures on the compared papers only, from the run's claims.csv (one row per asserted
    value: found = exact / lenient / not_found / no_span) and span_check.json's problem list."""
    import csv
    keep = set(pmids)
    found = Counter(r["found"] for r in csv.DictReader(open(f"data/extracted/{d}/{run}/claims.csv")) if r["pmid"] in keep)
    sc = json.loads(Path(f"data/extracted/{d}/{run}/span_check.json").read_text())
    probs = [p for p in sc.get("problems") or [] if p.split(":")[0] in keep]
    asserted = sum(found.values())
    nf, ns = found["not_found"], found["no_span"]
    r = lambda k: round(k / asserted, 5) if asserted else None
    return {"values_asserted": asserted, "quote_not_in_paper": nf, "no_quote": ns,
            "span_not_found_rate": r(nf + ns), "quote_not_in_paper_rate": r(nf), "no_quote_rate": r(ns),
            "cells_not_in_schema_shape": sum(1 for p in probs if "is not a {value, span} cell" in p or "is not an object" in p),
            "outputs_unparseable": sum(1 for p in probs if "does not parse as JSON" in p),
            "span_check_problems": len(probs)}


def coverage(ts, gene):
    out = Counter()
    for t in ts:
        out["individuals"] += len(rows(t, "individuals"))
        out["variant_rows"] += len(rows(t, "variants"))
        out["target_gene_variant_keys"] += len(vkeys(t, gene))
        out["phenotypic_feature_rows"] += len(rows(t, "phenotypic_features"))
        out["checklist_cells_observed_or_excluded"] += sum(1 for s in checklist(t).values() if s in ("observed", "excluded"))
    return dict(out)


def ow_costs(run, pmids):
    """Cost the host reported for each paper's final attempt (last JSON line of its log) and the
    final attempt's wall-clock. Failed attempts are not in these logs: the key's total spend
    (BUDGET.md) covers them."""
    final, wall = {}, {}
    for p in pmids:
        log = Path(f"runs/{run}/logs/{p}.log")
        last = [l for l in log.read_text(errors="replace").splitlines() if l.startswith('{"usage"')] if log.exists() else []
        if last:
            final[p] = json.loads(last[-1]).get("cost_usd_reported") or 0.0
        t = json.loads(Path(f"runs/{run}/transcripts/{p}.json").read_text())
        wall[p] = (t.get("result") or {}).get("wall_seconds")
    return final, wall


def one(d):
    gene = json.loads(Path(f"configs/stage4/{d}.json").read_text())["gene"]
    cr, orun = f"pv1-{d}", f"ow-{d}"
    pmids = sorted(p.stem for p in Path(f"data/extracted/{d}/{orun}/per_paper").glob("*.json"))
    pairs = [(p, tables(d, cr, p), tables(d, orun, p)) for p in pmids]
    pairs = [(p, c, o) for p, c, o in pairs if c is not None and o is not None]
    shared_v = union_v = only_c = only_o = 0
    cl_shared = cl_agree = 0
    for _, c, o in pairs:
        vc, vo = vkeys(c, gene), vkeys(o, gene)
        shared_v += len(vc & vo); union_v += len(vc | vo); only_c += len(vc - vo); only_o += len(vo - vc)
        cc, co = checklist(c), checklist(o)
        sh = set(cc) & set(co)
        cl_shared += len(sh); cl_agree += sum(cc[k] == co[k] for k in sh)
    used = [p for p, _, _ in pairs]
    hs = [r for r in json.loads(Path("analysis/openweight/claude_helper_stats.json").read_text()) if r["run"] == cr and r["pmid"] in used]
    c_cost = {p: sum(r["weighted_tokens"] for r in hs if r["pmid"] == p) / 1e6 * CLAUDE_RATE for p in used}
    c_wall = {p: sum(r["wall_seconds"] or 0 for r in hs if r["pmid"] == p) for p in used}
    o_cost, o_wall = ow_costs(orun, used)
    tools = Counter(json.loads(Path(f"runs/{orun}/transcripts/{p}.json").read_text()).get("result", {}).get("meta", {}).get("tools_version", "v1")
                    for p in used)
    med = lambda xs: round(statistics.median(xs), 4) if xs else None
    return {"disease": d, "gene": gene, "claude_run": cr, "open_run": orun, "papers_compared": len(used),
            "papers_in_open_run": len(pmids), "open_tools_version": dict(tools),
            "span": {"claude": span_block(d, cr, used), "open": span_block(d, orun, used)},
            "coverage": {"claude": coverage([c for _, c, _ in pairs], gene), "open": coverage([o for _, _, o in pairs], gene)},
            "variant_keys": {"shared": shared_v, "union": union_v, "claude_only": only_c, "open_only": only_o,
                             "jaccard_pooled": round(shared_v / union_v, 4) if union_v else None},
            "checklist": {"cells_shared": cl_shared, "status_agreement": round(cl_agree / cl_shared, 4) if cl_shared else None},
            "cost_usd": {"claude_estimate_total": round(sum(c_cost.values()), 2), "claude_median_per_paper": med(list(c_cost.values())),
                         "open_reported_total": round(sum(o_cost.values()), 4), "open_median_per_paper": med(list(o_cost.values())),
                         "open_papers_with_reported_cost": len(o_cost),
                         "open_note": "final attempts only; the key's total spend, failed attempts included, is in BUDGET.md"},
            "wall_seconds": {"claude_median": med([x for x in c_wall.values() if x]), "claude_total": round(sum(c_wall.values())),
                             "open_median": med([x for x in o_wall.values() if x]), "open_total": round(sum(x or 0 for x in o_wall.values()))}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--diseases", nargs="+", default=["ha20", "ssadh"])
    a = ap.parse_args()
    out = [one(d) for d in a.diseases]
    for s in out:
        Path(f"analysis/openweight/summary_{s['disease']}.json").write_text(json.dumps(s, indent=1) + "\n")
    pc = lambda x: "—" if x is None else f"{100 * x:.2f}%"
    L = ["# Claude vs open-weight model (D-10, pre-registration §7.5)", "",
         "*Generated by `analysis/openweight/summary.py`. Claude: Claude Code helpers (`pv1-<d>`). Open-weight: DeepSeek-V4.1-Flash "
         "(2026-09-10 checkpoint) on OpenRouter, provider pinned to DeepInfra fp8, through `pipeline/extract/openweight/agent.py` "
         "(`ow-<d>`). Same papers, launch prompt, instruction files, schema and rules. Claude cost is an estimate from helper tokens; "
         "open-weight cost is what the host reported. The blinded audit and HGVS concordance are reported separately.*", "",
         "| Measure | " + " | ".join(f"{s['disease']} Claude | {s['disease']} open-weight" for s in out) + " |",
         "|---|" + "---|---|" * len(out)]
    def row(name, f):
        L.append(f"| {name} | " + " | ".join(f"{f(s, 'claude')} | {f(s, 'open')}" for s in out) + " |")
    row("Papers compared", lambda s, k: s["papers_compared"])
    row("Values asserted", lambda s, k: s["span"][k]["values_asserted"])
    row("Span-not-found rate", lambda s, k: pc(s["span"][k]["span_not_found_rate"]))
    row("… quote not in paper", lambda s, k: pc(s["span"][k]["quote_not_in_paper_rate"]))
    row("… no quote given", lambda s, k: pc(s["span"][k]["no_quote_rate"]))
    row("Cells not in schema shape", lambda s, k: s["span"][k]["cells_not_in_schema_shape"])
    for m in ("individuals", "variant_rows", "target_gene_variant_keys", "phenotypic_feature_rows", "checklist_cells_observed_or_excluded"):
        row(m.replace("_", " ").capitalize(), lambda s, k, m=m: s["coverage"][k].get(m, 0))
    row("Cost per paper, median ($)", lambda s, k: s["cost_usd"]["claude_median_per_paper" if k == "claude" else "open_median_per_paper"])
    row("Cost, total ($)", lambda s, k: s["cost_usd"]["claude_estimate_total" if k == "claude" else "open_reported_total"])
    row("Wall-clock per paper, median (s)", lambda s, k: s["wall_seconds"]["claude_median" if k == "claude" else "open_median"])
    L += ["", "| Agreement | " + " | ".join(s["disease"] for s in out) + " |", "|---|" + "---|" * len(out)]
    L.append("| Target-gene variant keys, shared / union | " + " | ".join(
        f"{s['variant_keys']['shared']}/{s['variant_keys']['union']} ({pc(s['variant_keys']['jaccard_pooled'])}); Claude only {s['variant_keys']['claude_only']}, open only {s['variant_keys']['open_only']}" for s in out) + " |")
    L.append("| Checklist status agreement (shared cells) | " + " | ".join(f"{pc(s['checklist']['status_agreement'])} of {s['checklist']['cells_shared']}" for s in out) + " |")
    Path("analysis/openweight/summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
