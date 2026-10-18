"""Run-to-run agreement between two extraction runs on the same papers (Stage 3 check 5).

For the papers present in both runs, compares:
  - individuals: number per paper;
  - variants: Jaccard similarity of the sets of (paper, normalised variant string)
    where the normalisation only collapses whitespace and case;
  - features: Jaccard similarity of the sets of (paper, individual label,
    lower-cased feature text, status);
  - checklist: share of (paper, individual, checklist feature) cells with the
    same status, over cells present in both runs.

Added 2026-10-18 after the first repeat papers showed that strict matching mostly
measures wording (helpers invent different labels for unnamed people, and quote
features or variants from different places in the paper):
  - individual_label_jaccard: labels in common;
  - variant_key_jaccard: variants compared on folded cDNA/protein keys
    (pipeline.extract.reconcile), label-free;
  - hpo_pair_jaccard: (paper, individual, HPO candidate ID) pairs, as POC_DESIGN.md
    Stage 3 check 5 specifies;
  - hpo_status_jaccard_label_free: (paper, HPO candidate ID, status), ignoring labels;
  - feature_jaccard_label_free: (paper, lower-cased feature text, status).
The strict measures above are kept and reported first.

POC_DESIGN.md Stage 3 flags variant agreement below 0.9 as a sign of unstable
prompts. Writes analysis/poc/run_agreement_<a>_vs_<b>.json.

  uv run python analysis/poc/run_agreement.py --disease ha20 --run-a poc-ha20-run-1 --run-b poc-ha20-run-1-repeat
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from pipeline.extract.reconcile import cdna_key, orig_key, protein_key

WS = re.compile(r"\s+")


def v(cell):
    return (cell or {}).get("value")


def norm(s) -> str:
    return WS.sub("", str(s or "")).lower()


def load(run_dir: Path) -> dict[str, dict]:
    return {p.stem: json.loads(p.read_text()) for p in sorted((run_dir / "per_paper").glob("*.json"))}


def vkey(r) -> str | None:
    return (cdna_key(v(r.get("cdna_hgvs_as_stated"))) or cdna_key(v(r.get("variant_original_string")))
            or protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(v(r.get("variant_original_string")))
            or orig_key(v(r.get("variant_original_string"))))


def jaccard(a: set, b: set) -> float | None:
    return round(len(a & b) / len(a | b), 4) if (a | b) else None


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-a", required=True)
    ap.add_argument("--run-b", required=True)
    args = ap.parse_args(argv)
    base = Path("data/extracted") / args.disease
    a, b = load(base / args.run_a), load(base / args.run_b)
    common = sorted(set(a) & set(b))
    per_paper, va, vb, fa, fb = {}, set(), set(), set(), set()
    extra = {k: (set(), set()) for k in ("labels", "vkeys", "hpo_pairs", "hpo_status", "feat_free")}
    cl_same = cl_total = 0
    for p in common:
        ta, tb = a[p]["tables"], b[p]["tables"]
        pva = {(p, norm(v(r["variant_original_string"]))) for r in ta["variants"]}
        pvb = {(p, norm(v(r["variant_original_string"]))) for r in tb["variants"]}
        pfa = {(p, norm(v(r["individual_label_in_paper"])), norm(v(r["feature_text_as_stated"])), v(r["status"])) for r in ta["phenotypic_features"]}
        pfb = {(p, norm(v(r["individual_label_in_paper"])), norm(v(r["feature_text_as_stated"])), v(r["status"])) for r in tb["phenotypic_features"]}
        ca = {(norm(v(r["individual_label_in_paper"])), v(r["checklist_feature"])): v(r["status"]) for r in ta["phenotype_checklist"]}
        cb = {(norm(v(r["individual_label_in_paper"])), v(r["checklist_feature"])): v(r["status"]) for r in tb["phenotype_checklist"]}
        shared = set(ca) & set(cb)
        same = sum(1 for k in shared if ca[k] == cb[k])
        cl_same += same
        cl_total += len(shared)
        va |= pva; vb |= pvb; fa |= pfa; fb |= pfb
        sets = {}
        for side, t in (("a", ta), ("b", tb)):
            sets[side] = {
                "labels": {(p, norm(v(r["individual_label_in_paper"]))) for r in t["individuals"]},
                "vkeys": {(p, k) for r in t["variants"] if (k := vkey(r))},
                "hpo_pairs": {(p, norm(v(r["individual_label_in_paper"])), v(r["hpo_id_candidate"])) for r in t["phenotypic_features"] if v(r.get("hpo_id_candidate"))},
                "hpo_status": {(p, v(r["hpo_id_candidate"]), v(r["status"])) for r in t["phenotypic_features"] if v(r.get("hpo_id_candidate"))},
                "feat_free": {(p, norm(v(r["feature_text_as_stated"])), v(r["status"])) for r in t["phenotypic_features"]},
            }
        for k in extra:
            extra[k][0].update(sets["a"][k]); extra[k][1].update(sets["b"][k])
        per_paper[p] = {
            "individuals": [len(ta["individuals"]), len(tb["individuals"])],
            "variant_jaccard": jaccard(pva, pvb),
            "feature_jaccard": jaccard(pfa, pfb),
            "checklist_agreement": round(same / len(shared), 4) if shared else None,
            "checklist_cells_compared": len(shared),
            "individual_label_jaccard": jaccard(sets["a"]["labels"], sets["b"]["labels"]),
            "variant_key_jaccard": jaccard(sets["a"]["vkeys"], sets["b"]["vkeys"]),
            "hpo_pair_jaccard": jaccard(sets["a"]["hpo_pairs"], sets["b"]["hpo_pairs"]),
            "hpo_status_jaccard_label_free": jaccard(sets["a"]["hpo_status"], sets["b"]["hpo_status"]),
            "feature_jaccard_label_free": jaccard(sets["a"]["feat_free"], sets["b"]["feat_free"]),
        }
    out = {
        "run_a": args.run_a, "run_b": args.run_b, "papers_compared": len(common),
        "variant_jaccard": jaccard(va, vb),
        "feature_jaccard": jaccard(fa, fb),
        "checklist_agreement": round(cl_same / cl_total, 4) if cl_total else None,
        "checklist_cells_compared": cl_total,
        "individual_count_matches": sum(1 for x in per_paper.values() if x["individuals"][0] == x["individuals"][1]),
        "individual_label_jaccard": jaccard(*extra["labels"]),
        "variant_key_jaccard": jaccard(*extra["vkeys"]),
        "hpo_pair_jaccard": jaccard(*extra["hpo_pairs"]),
        "hpo_status_jaccard_label_free": jaccard(*extra["hpo_status"]),
        "feature_jaccard_label_free": jaccard(*extra["feat_free"]),
        "variant_threshold_note": "POC_DESIGN.md Stage 3: variant agreement < 0.9 suggests unstable prompts",
        "per_paper": per_paper,
    }
    dest = Path("analysis/poc") / f"run_agreement_{args.run_a}_vs_{args.run_b}.json"
    dest.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps({k: out[k] for k in out if k != "per_paper"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
