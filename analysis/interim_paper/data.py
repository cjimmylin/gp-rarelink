"""Load every input the interim paper uses and derive the numbers it reports.

All inputs are committed files written by earlier scripts (run summaries, O2 and O3 outputs,
Stage 4 summaries, manifests, budget segments). Nothing here calls a model or a network. The
paper text and figures read only the dict this module returns, so a number in the paper traces
to one of the files named in SOURCES.

  from analysis.interim_paper.data import load
  D = load()
"""
from __future__ import annotations

import csv
import glob
import importlib.util
import json
import re
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
CONFIRMATORY = ["ssadh", "tangier", "lad1", "axd", "danon"]  # HA20 is the development disease (D-18)
NAME = {"ha20": "A20 haploinsufficiency", "ssadh": "SSADH deficiency", "tangier": "Tangier disease",
        "lad1": "Leukocyte adhesion deficiency I", "axd": "Alexander disease", "danon": "Danon disease"}
SHORT = {"ha20": "HA20", "ssadh": "SSADH", "tangier": "Tangier", "lad1": "LAD-I", "axd": "AxD", "danon": "Danon"}
GENE = {"ha20": "TNFAIP3", "ssadh": "ALDH5A1", "tangier": "ABCA1", "lad1": "ITGB2", "axd": "GFAP", "danon": "LAMP2"}
OMIM = {"ha20": "616744", "ssadh": "271980", "tangier": "205400", "lad1": "116920", "axd": "203450", "danon": "300257"}
INHERITANCE = {"ha20": "AD", "ssadh": "AR", "tangier": "AR", "lad1": "AR", "axd": "AD / de novo", "danon": "X-linked dominant"}
SYSTEM = {"ha20": "Auto-inflammatory", "ssadh": "Neurometabolic", "tangier": "Lipid metabolism", "lad1": "Immunology",
          "axd": "Neurology", "danon": "Cardiac / neuromuscular"}

SOURCES = {
    "run_summary": "analysis/six_disease/run_summary_2026-10-20.json",
    "repeat": "analysis/six_disease/repeat_agreement_2026-10-20.json",
    "stage4": "analysis/six_disease/stage4_summary_2026-10-28.json",
    "coverage": "analysis/corpus/coverage_2026-10-20.json",
    "o2": "analysis/six_disease/o2/o2_<d>.json",
    "o2_misses": "analysis/six_disease/o2/o2_recall_misses.csv",
    "o2_variants": "analysis/six_disease/o2/o2_variants.csv",
    "completeness": "analysis/six_disease/completeness_pv1-<d>.json",
    "gaps": "adjudication/o3_gaps/summary.json",
    "gap_candidates": "adjudication/o3_gaps/candidates.csv",
    "triage": "adjudication/o3_gaps/triage_summary.json",
    "recheck": "adjudication/o3_gaps/recheck_2026-10-21.json",
    "dossiers": "adjudication/o3_gaps/check_summary.json",
    "merges": "adjudication/o3_gaps/proposed_merges_summary.json",
    "merges_csv": "adjudication/o3_gaps/proposed_merges.csv",
    "reclass": "adjudication/o3_gaps/reclassification_candidates.csv",
    "gpsea": "analysis/exploratory/gpsea/results/summary.json",
    "tangier_share": "analysis/exploratory/tangier_clinvar_share.json",
    "mem_claude": "analysis/bias/memorization/scores_summary.json",
    "mem_ow": "analysis/bias/memorization/openweight_scores_summary.json",
    "mem_sample": "analysis/bias/memorization/sample.csv",
    "bias": "analysis/bias/frequency_deviation_2026-10-21.json",
    "comparators": "analysis/bias/comparators_2026-10-21.json",
    "ow_summary": "analysis/openweight/summary_<d>.json",
    "ow_gk": "analysis/openweight/gatekeeper_compare.json",
    "ow_o2": "analysis/openweight/o2/o2_<d>.json",
    "ow_manifest": "runs/ow-<d>/manifest.json",
    "pv1_manifest": "runs/pv1-<d>/manifest.json",
    "gk_summary": "data/extracted/<d>/pv1-<d>/gatekeeper_v4_summary.json",
    "reconcile": "data/extracted/<d>/pv1-<d>/reconcile_summary.json",
    "build": "data/extracted/<d>/pv1-<d>/phenopacket_build.json",
    "phenopackets": "data/extracted/<d>/pv1-<d>/phenopackets/*.json",
    "clinvar_counts": "analysis/poc/reference_snapshot/2026-10-19/counts[_<GENE>].json",
    "clinvar_counts_recheck": "analysis/poc/reference_snapshot/2026-10-21/counts_<GENE>.json",
    "poc_audit": "analysis/poc/audit_metrics.json, audit_metrics_v5.json, audit_metrics_v5_excluding_uncertain.json",
    "poc_dedup": "analysis/poc/dedup_hand_check_summary_poc-ha20-run-2.json",
    "poc_completeness": "analysis/poc/completeness_poc-ha20-run-2.json",
    "o1_sample": "adjudication/o1_audit/sample_key.json",
    "o2_triage_sample": "adjudication/o2_triage/sample_key.json",
    "checklists": "configs/checklists/<d>.json and schema_ha20_v5.json",
    "stage4_cfg": "configs/stage4/<d>.json",
    "budget_segments": "analysis/cost/spend_segments.csv",
    "budget_lines": "BUDGET.md (Lines table)",
    "catalogue_check": "analysis/catalogue/catalogue_check_2026-10-20.json",
    "smoke_manifest": "runs/poc-ha20-v6-smoke/manifest.json",
    "omim_results": "analysis/omim_holdout/results_2026-10-28.json",
    "omim_av_recall": "analysis/omim_holdout/av_recall_2026-10-28.csv",
    "omim_cited_papers": "analysis/omim_holdout/omim_cited_papers_2026-10-28.csv",
    "omim_gap_check": "analysis/omim_holdout/gap_candidates_omim_check_2026-10-28.csv",
    "omim_judgements": "analysis/omim_holdout/patient_level_judgements.csv",
    "omim_av_clinvar": "analysis/omim_holdout/omim_av_clinvar.csv",
    "omim_counts": "analysis/poc/reference_snapshot/2026-10-28/omim_counts.json",
    "omim_manifest": "analysis/poc/reference_snapshot/2026-10-28/omim_MANIFEST.json",
    "danon_normalization": "data/extracted/danon/pv1-danon/normalization_summary.json (re-run under D-43)",
}


def J(rel: str):
    return json.loads((ROOT / rel).read_text())


def rows(rel: str):
    with (ROOT / rel).open(newline="") as fh:
        return list(csv.DictReader(fh))


def git_commit() -> str:
    try:
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    except OSError:
        return "unknown"


def variant_class(expr_p: str, expr_c: str, label: str) -> str:
    """Coarse class of a variant from its normalized protein and cDNA HGVS, else from the paper's label."""
    p, c = (expr_p or "").strip().rstrip("]"), (expr_c or "").strip()
    if not p and not c:
        s = label.lower()
        if re.search(r"\bmb\b|chr\d|arr\[|exon|deletion|duplication|缺失|del\b", s):
            return "structural / copy-number"
        if re.search(r"fs|\*|ter", s):
            return "frameshift or nonsense (unplaced)"
        return "not placed"
    if "fs" in p:
        return "frameshift"
    if "Ter" in p or re.search(r"\*\)?$", p):
        return "nonsense"
    if "Met1" in p and "?" in p:
        return "start loss"
    if "ext" in p:
        return "extension"
    if re.search(r"\(=\)|=\)?$", p):
        return "synonymous"
    if re.search(r"(del|dup|ins)", p):
        return "in-frame indel"
    if re.search(r"c\.[\d_*-]+[+-]\d+", c) or p in ("p.?", "p.(?)") or (not p and c):
        return "splice / intronic"
    if re.search(r"p\.\(?[A-Z][a-z]{2}\d+[A-Z][a-z]{2}\)?$", p) or re.search(r"^p\.?[A-Z]\d+[A-Z]$", p):
        return "missense"
    return "other"


def phenopacket_stats(d: str) -> dict:
    files = sorted(glob.glob(str(ROOT / f"data/extracted/{d}/pv1-{d}/phenopackets/*.json")))
    sex = Counter()
    observed = Counter()
    excluded = Counter()
    labels = {}
    classes = Counter()
    n_var_identities = 0
    for f in files:
        p = json.loads(Path(f).read_text())
        sex[p["subject"].get("sex", "UNKNOWN")] += 1
        seen_o, seen_e = set(), set()
        for ft in p.get("phenotypicFeatures", []):
            tid = ft["type"]["id"]
            labels[tid] = ft["type"]["label"]
            (seen_e if ft.get("excluded") else seen_o).add(tid)
        for t in seen_o:
            observed[t] += 1
        for t in seen_e:
            excluded[t] += 1
        gis = [g for i in p.get("interpretations", []) for g in i["diagnosis"].get("genomicInterpretations", [])]
        if gis:
            n_var_identities += 1
        for g in gis:
            vd = g["variantInterpretation"]["variationDescriptor"]
            ex = {e["syntax"]: e["value"] for e in vd.get("expressions", [])}
            classes[variant_class(ex.get("hgvs.p", ""), ex.get("hgvs.c", ""), vd.get("label", ""))] += 1
    top = [(t, labels[t], observed[t], excluded.get(t, 0)) for t, _ in observed.most_common(10)]
    return {"n": len(files), "sex": dict(sex), "top_observed": top, "variant_classes": dict(classes),
            "identities_with_interpretation": n_var_identities}


def budget() -> dict:
    spec = importlib.util.spec_from_file_location("budget_lines", ROOT / "analysis/cost/budget_lines.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    spent, total, when = mod.allocate()
    lines = []
    for line in (ROOT / "BUDGET.md").read_text().splitlines():
        m = re.match(r"^\| (\d) \| ([^|]+)\| \$([\d,]+) \| [^|]* \| [^|]* \|", line)
        if m:
            lines.append({"n": m.group(1), "name": m.group(2).strip(), "requested": float(m.group(3).replace(",", "")),
                          "spent": spent.get(m.group(1), 0.0)})
    segs = rows("analysis/cost/spend_segments.csv")
    return {"lines": lines, "unassigned": spent.get("unassigned", 0.0), "total": total, "reading_at": when, "segments": segs}


def load() -> dict:
    D = {"commit": git_commit(), "diseases": DISEASES, "confirmatory": CONFIRMATORY, "name": NAME, "short": SHORT,
         "gene": GENE, "omim": OMIM, "inheritance": INHERITANCE, "system": SYSTEM, "sources": SOURCES}
    rs = J(SOURCES["run_summary"])
    D["run"] = {x["disease"]: x for x in rs["diseases"]}
    D["run_date"] = rs["date"]
    rp = J(SOURCES["repeat"])
    D["repeat"] = {x["disease"]: x for x in rp["diseases"]}
    D["repeat_seed"] = rp["seed"]
    D["stage4"] = {x["disease"]: x for x in J(SOURCES["stage4"])["diseases"]}
    D["coverage"] = {x["disease"]: x for x in J(SOURCES["coverage"])}
    D["o2"] = {d: J(SOURCES["o2"].replace("<d>", d)) for d in DISEASES}
    D["completeness"] = {d: J(SOURCES["completeness"].replace("<d>", d)) for d in ("ha20", "axd")}
    g = J(SOURCES["gaps"])
    D["gaps"] = {x["disease"]: x for x in g["diseases"]}
    D["gaps_meta"] = {k: v for k, v in g.items() if k != "diseases"}
    D["gap_candidates"] = rows(SOURCES["gap_candidates"])
    D["triage"] = J(SOURCES["triage"])
    D["recheck"] = J(SOURCES["recheck"])
    D["dossiers"] = J(SOURCES["dossiers"])
    D["merges"] = J(SOURCES["merges"])
    D["merges_rows"] = rows(SOURCES["merges_csv"])
    D["reclass"] = rows(SOURCES["reclass"])
    D["gpsea"] = J(SOURCES["gpsea"])
    D["tangier_share"] = J(SOURCES["tangier_share"])
    D["mem"] = {"claude": J(SOURCES["mem_claude"]), "open": J(SOURCES["mem_ow"])}
    D["mem_sample"] = rows(SOURCES["mem_sample"])
    D["bias"] = J(SOURCES["bias"])
    D["comparators"] = J(SOURCES["comparators"])
    D["ow"] = {d: J(SOURCES["ow_summary"].replace("<d>", d)) for d in ("ha20", "ssadh")}
    D["ow_gk"] = J(SOURCES["ow_gk"])
    D["ow_o2"] = {d: J(SOURCES["ow_o2"].replace("<d>", d)) for d in ("ha20", "ssadh")}
    D["ow_manifest"] = {d: J(SOURCES["ow_manifest"].replace("<d>", d)) for d in ("ha20", "ssadh")}
    D["pv1_manifest"] = {d: J(SOURCES["pv1_manifest"].replace("<d>", d)) for d in DISEASES}
    D["gk"] = {d: J(SOURCES["gk_summary"].replace("<d>", d)) for d in DISEASES}
    D["reconcile"] = {d: J(SOURCES["reconcile"].replace("<d>", d)) for d in DISEASES}
    D["build"] = {d: J(SOURCES["build"].replace("<d>", d)) for d in DISEASES}
    D["pp"] = {d: phenopacket_stats(d) for d in DISEASES}
    cv = {}
    for d in DISEASES:
        gene = GENE[d]
        f = "analysis/poc/reference_snapshot/2026-10-19/counts.json" if gene == "TNFAIP3" else f"analysis/poc/reference_snapshot/2026-10-19/counts_{gene}.json"
        c = J(f)
        b = c["single_gene_records"]["by_classification"]
        c2 = J(f"analysis/poc/reference_snapshot/2026-10-21/counts_{gene}.json")
        b2 = c2["single_gene_records"]["by_classification"]
        cv[d] = {"total": c["single_gene_records"]["total"], "plp": b.get("P", 0) + b.get("LP", 0) + b.get("P/LP", 0),
                 "vus": b.get("VUS", 0), "conflicting": b.get("conflicting", 0),
                 "naming_disease": c.get("single_gene_naming_disease", {}).get("total"),
                 "release": c["last_modified"], "total_recheck": c2["single_gene_records"]["total"],
                 "plp_recheck": b2.get("P", 0) + b2.get("LP", 0) + b2.get("P/LP", 0), "release_recheck": c2["last_modified"]}
    D["clinvar"] = cv
    D["poc"] = {"audit1": J("analysis/poc/audit_metrics.json"), "audit2": J("analysis/poc/audit_metrics_v5.json"),
                "audit2_excl": J("analysis/poc/audit_metrics_v5_excluding_uncertain.json"),
                "dedup": J(SOURCES["poc_dedup"]), "completeness": J(SOURCES["poc_completeness"])}
    D["o1"] = J(SOURCES["o1_sample"])
    D["o2_triage"] = J(SOURCES["o2_triage_sample"])
    D["smoke"] = J(SOURCES["smoke_manifest"])
    # checklists
    cl = {}
    schema = J("pipeline/extract/claude_code/schema_ha20_v5.json")
    desc = [t for t in schema["tables"] if t["name"] == "phenotype_checklist"][0]["description"]
    cl["ha20"] = {"source_pmid": "pilot schema (schema_ha20_v5.json)",
                  "items": [s.strip() for s in desc.split("Checklist:")[1].rstrip(".").split(";")]}
    for d in CONFIRMATORY:
        c = J(f"configs/checklists/{d}.json")
        cl[d] = {"source_pmid": str(c["source_pmid"]), "items": [x["name"] for x in c["checklist"]]}
    D["checklists"] = cl
    D["stage4_cfg"] = {d: J(f"configs/stage4/{d}.json") for d in DISEASES}
    D["catalogue_check"] = J(SOURCES["catalogue_check"])
    # O2 misses by paper
    miss = Counter()
    for r in rows(SOURCES["o2_misses"]):
        miss[(r["disease"], r["pmid"])] += 1
    byd = defaultdict(list)
    for (d, p), n in miss.items():
        byd[d].append((p, n))
    D["o2_misses_by_paper"] = {d: sorted(v, key=lambda x: -x[1]) for d, v in byd.items()}
    # O2 variants: tiers and ClinVar classes among tier-1 matches
    tiers = defaultdict(Counter)
    cls = defaultdict(Counter)
    for r in rows(SOURCES["o2_variants"]):
        tiers[r["disease"]][r["tier"]] += 1
        if r["tier"] == "1":
            cls[r["disease"]][r["clinvar_class"]] += 1
    D["o2_tiers"] = {d: dict(tiers[d]) for d in DISEASES}
    D["o2_tier1_classes"] = {d: dict(cls[d]) for d in DISEASES}
    D["budget"] = budget()
    # OMIM holdout (D-42) and D-43
    om = J(SOURCES["omim_results"])
    judg = rows(SOURCES["omim_judgements"])
    gapcheck = {r["candidate_id"]: r for r in rows(SOURCES["omim_gap_check"])}
    status = Counter(r["status"] for r in D["gap_candidates"])
    live = Counter(r["disease"] for r in D["gap_candidates"] if r["status"] != "withdrawn")
    withdrawn = [r for r in D["gap_candidates"] if r["status"] == "withdrawn"]
    omim_absent = sum(1 for r in D["gap_candidates"] if r["omim_checked"].startswith("absent"))
    D["omimh"] = {"per": om["per_disease"], "totals": om["totals"], "date": om["date"], "av": rows(SOURCES["omim_av_recall"]),
                  "papers": rows(SOURCES["omim_cited_papers"]), "gapcheck": gapcheck, "judg": judg,
                  "judg_tally": dict(Counter(r["agreement"] for r in judg)), "judg_papers": len({r["pmid"] for r in judg}),
                  "counts": J(SOURCES["omim_counts"]), "manifest": J(SOURCES["omim_manifest"]), "av_clinvar": rows(SOURCES["omim_av_clinvar"]),
                  "gap_status": dict(status), "gap_live": {d: live.get(d, 0) for d in DISEASES}, "withdrawn": withdrawn, "gap_omim_absent": omim_absent}
    D["isoform_cfg"] = {d: D["stage4_cfg"][d].get("isoform_sensitive", []) for d in DISEASES}
    D["danon_norm"] = J("data/extracted/danon/pv1-danon/normalization_summary.json")
    # derived totals
    def tot(keys, fn):
        return sum(fn(k) for k in keys)
    D["totals"] = {}
    for label, keys in (("all", DISEASES), ("five", CONFIRMATORY)):
        r = {k: D["run"][k] for k in keys}
        s4 = {k: D["stage4"][k] for k in keys}
        D["totals"][label] = {
            "papers": tot(keys, lambda k: r[k]["papers"]),
            "individual_rows": tot(keys, lambda k: r[k]["individual_rows"]),
            "variant_rows": tot(keys, lambda k: r[k]["variant_rows"]),
            "claims_all": tot(keys, lambda k: r[k]["claims_all"]),
            "model_claims": tot(keys, lambda k: r[k]["model_claims_judged"]),
            "unsupported": tot(keys, lambda k: r[k]["unsupported_or_not_found"]["k"]),
            "not_supported": tot(keys, lambda k: r[k]["not_supported"]["k"]),
            "identities": tot(keys, lambda k: s4[k]["identities"]),
            "with_variant": tot(keys, lambda k: s4[k]["identities_with_target_variant"]),
            "phenopackets": tot(keys, lambda k: s4[k]["phenopackets"]),
            "with_interpretation": tot(keys, lambda k: s4[k]["with_interpretation"]),
            "features_observed": tot(keys, lambda k: s4[k]["features_observed"]),
            "features_excluded": tot(keys, lambda k: s4[k]["features_excluded"]),
            "gap_candidates": tot(keys, lambda k: D["gaps"][k]["gap_candidates"]),
            "gap_candidates_live": tot(keys, lambda k: D["omimh"]["gap_live"][k]),
            "tier1_alleles": tot(keys, lambda k: D["gaps"][k]["tier1_alleles"]),
            "reclass": tot(keys, lambda k: D["gaps"][k]["reclassification_candidates"]),
            "reclass_strong": tot(keys, lambda k: D["gaps"][k]["reclassification_strong_proposed"]),
        }
    return D


if __name__ == "__main__":
    D = load()
    print(json.dumps(D["totals"], indent=1))
    print(json.dumps({d: D["pp"][d]["variant_classes"] for d in DISEASES}, indent=1))
    print(json.dumps({d: D["pp"][d]["sex"] for d in DISEASES}))
    print(json.dumps({d: D["pp"][d]["top_observed"][:3] for d in DISEASES}, indent=0)[:1500])
