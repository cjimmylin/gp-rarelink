"""Open-weight comparison (D-10, §7.5): one paper's extraction by both models, side by side.

Compares the per-paper JSON of a Claude run (default pv1-ha20) and an open-weight run on the
same papers: rows per table, people, target-gene variant keys (protein level, as
concordance.protein_short), checklist statuses, and the span check of each run. Descriptive only;
the registered metrics (span-not-found rate, blinded audit, HGVS concordance, coverage, cost,
wall-clock) are computed on the full run.

  uv run python analysis/openweight/compare_runs.py --disease ha20 --claude pv1-ha20 --open ow-ha20-pilot
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from pipeline.extract.normalize_variants import is_gene, protein_key, v
from pipeline.harness.concordance import protein_short


def load(d, run, pmid):
    return json.loads(Path(f"data/extracted/{d}/{run}/per_paper/{pmid}.json").read_text()).get("tables") or {}


def vkeys(t, gene):
    out = set()
    for r in t.get("variants") or []:
        if is_gene(v(r.get("gene_symbol_as_stated")), gene):
            for f in ("protein_hgvs_as_stated", "variant_original_string"):
                k = protein_key(v(r.get(f)))
                if k:
                    out.add(protein_short(k))
    return out


def checklist(t):
    return {(str(v(r.get("individual_label_in_paper"))), str(v(r.get("checklist_feature")))): str(v(r.get("status")))
            for r in t.get("phenotype_checklist") or []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--disease", required=True)
    ap.add_argument("--claude", required=True)
    ap.add_argument("--open", required=True)
    a = ap.parse_args()
    gene = json.loads(Path(f"configs/stage4/{a.disease}.json").read_text())["gene"]
    papers = sorted(p.stem for p in Path(f"data/extracted/{a.disease}/{a.open}/per_paper").glob("*.json"))
    out = []
    for p in papers:
        c, o = load(a.disease, a.claude, p), load(a.disease, a.open, p)
        rows = {t: (len(c.get(t) or []), len(o.get(t) or [])) for t in sorted(set(c) | set(o))}
        vc, vo = vkeys(c, gene), vkeys(o, gene)
        cc, co = checklist(c), checklist(o)
        shared = set(cc) & set(co)
        out.append({"pmid": p, "rows_claude_open": rows, "variants_claude": sorted(vc), "variants_open": sorted(vo),
                    "variant_jaccard": round(len(vc & vo) / len(vc | vo), 3) if vc | vo else None,
                    "checklist_cells_claude": len(cc), "checklist_cells_open": len(co), "checklist_cells_shared": len(shared),
                    "checklist_status_agreement": round(sum(cc[k] == co[k] for k in shared) / len(shared), 3) if shared else None,
                    "status_counts_claude": dict(Counter(cc.values())), "status_counts_open": dict(Counter(co.values()))})
    for run in (a.claude, a.open):
        sc = json.loads(Path(f"data/extracted/{a.disease}/{run}/span_check.json").read_text())
        out.append({"span_check": run, "span_found_rate": sc.get("span_found_rate"), "n_problems_run": sc.get("n_problems")})
    Path(f"analysis/openweight/compare_{a.open}.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
