"""Bind extracted phenotypes to HPO and diseases to Mondo (POC_DESIGN.md Stage 4 step 3).

Reads one run's per-paper JSON and the pinned ontology snapshot
(pipeline/extract/ontologies.py). No model call; the rows this script cannot
bind are written out for a constrained model-assisted step or left unbound.

Phenotypic feature rows (observed or excluded), in order:
  exact_id      the helper's hpo_id_candidate exists, is not obsolete, and its
                name or an EXACT synonym equals the helper's label candidate or
                the feature text (case and punctuation folded);
  replaced      the candidate ID is obsolete and has a replaced_by term whose
                name matches as above;
  label         no usable ID, but the label candidate or the feature text equals
                the name or an EXACT synonym of one current term;
  id_unverified the candidate ID exists and is current but its name matches
                neither label nor text (kept with this flag; needs review);
  unbound       none of the above. Lexical candidates (up to 5 current terms
                whose name or EXACT synonym contains every word of the label
                candidate) are listed for review or a constrained model step.

Model-assisted step (--model-bindings, Stage 4 step 3): unbound phrases are
sent to helper agents under pipeline/extract/claude_code/prompts/hpo_binding_v1.md,
which look terms up in the pinned hp.obo and answer an ID or NONE. Each answer
is accepted only if the ID exists in the pinned release, is not obsolete, and
the name the helper copied equals the term's name; then the row's method is
model_exact, model_close or model_broader (as the helper graded the match).
NONE becomes no_suitable_term; an answer that fails the check becomes
model_rejected and the row stays unbound.

Checklist rows use the fixed mapping in configs/ha20_checklist_hpo.json.

Disease: the stated disease label is matched to a Mondo name or EXACT synonym.
Labels naming A20 haploinsufficiency or HA20 are bound to the disease term
given by --ha20-mondo (default MONDO:0800045, 'autoinflammatory syndrome,
familial, Behcet-like 1', whose Mondo cross-references are the disease IDs in
CONTEXT.md). Mondo's gene-based grouping term for TNFAIP3 disease
(MONDO:0100222) is recorded as the group term. Claude's call of 2026-10-19,
flagged for review.

Writes, under data/extracted/<disease>/<run_id>/:
  hpo_bindings.csv      one row per phenotypic_features row
  disease_bindings.csv  one row per individual
  binding_summary.json  counts by method

  uv run python -m pipeline.extract.bind_ontologies --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter
from pathlib import Path

from pipeline.extract import ontologies

FOLD = re.compile(r"[^a-z0-9]+")
HA20_LABEL = re.compile(r"\bHA20\b|A20\s+haploinsufficien|haploinsufficiency\s+of\s+A20|\bAISBL", re.IGNORECASE)


def v(cell):
    return (cell or {}).get("value")


def fold(s) -> str:
    return FOLD.sub(" ", str(s or "").lower()).strip()


def names(term: ontologies.Term) -> set[str]:
    return {fold(term.name)} | {fold(s) for scope, s in term.synonyms if scope == "EXACT"}


class Index:
    def __init__(self, onto: ontologies.Ontology) -> None:
        self.onto = onto
        self.by_name: dict[str, set[str]] = {}
        for t in onto.terms.values():
            if t.obsolete:
                continue
            for n in names(t):
                self.by_name.setdefault(n, set()).add(t.id)

    def exact(self, text) -> str | None:
        hits = self.by_name.get(fold(text), set())
        return next(iter(hits)) if len(hits) == 1 else None

    def candidates(self, text, k: int = 5) -> list[str]:
        words = [w for w in fold(text).split() if len(w) > 2]
        if not words:
            return []
        out = []
        for n, ids in self.by_name.items():
            if all(w in n.split() for w in words):
                out.extend(sorted(ids))
        return sorted(set(out), key=lambda i: (len(self.onto.terms[i].name), i))[:k]


def bind_feature(row: dict, idx: Index) -> dict:
    hp = idx.onto.terms
    cid, clabel, text = v(row.get("hpo_id_candidate")), v(row.get("hpo_label_candidate")), v(row.get("feature_text_as_stated"))
    wanted = {fold(clabel), fold(text)} - {""}
    if cid and cid in hp:
        t = hp[cid]
        if not t.obsolete and names(t) & wanted:
            return {"hpo_id": cid, "hpo_label": t.name, "method": "exact_id"}
        if t.obsolete:
            for r in t.replaced_by:
                if r in hp and names(hp[r]) & wanted:
                    return {"hpo_id": r, "hpo_label": hp[r].name, "method": "replaced"}
    for cand in (clabel, text):
        tid = idx.exact(cand)
        if tid:
            return {"hpo_id": tid, "hpo_label": hp[tid].name, "method": "label"}
    if cid and cid in hp and not hp[cid].obsolete:
        return {"hpo_id": cid, "hpo_label": hp[cid].name, "method": "id_unverified"}
    cands = idx.candidates(clabel or text)
    return {"hpo_id": "", "hpo_label": "", "method": "unbound",
            "candidates": "; ".join(f"{c} {hp[c].name}" for c in cands)}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--ha20-mondo", default="MONDO:0800045")
    ap.add_argument("--group-mondo", default="MONDO:0100222")
    ap.add_argument("--checklist-map", default="configs/ha20_checklist_hpo.json")
    ap.add_argument("--model-bindings", nargs="*", default=[], help="helper output CSVs (text_id, hpo_id, hpo_name, match, note)")
    ap.add_argument("--model-keymap", help="CSV mapping text_id to the folded feature text")
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    snap = ontologies.latest_dir()
    hp, mondo = ontologies.load("hp", snap), ontologies.load("mondo", snap)
    hidx, midx = Index(hp), Index(mondo)
    checklist = json.loads(Path(args.checklist_map).read_text())
    for item in checklist["items"].values():
        for tid in [item["observed"], *item["excluded"]]:
            if tid and (tid not in hp.terms or hp.terms[tid].obsolete):
                raise SystemExit(f"checklist map term {tid} is missing or obsolete in {hp.version}")
    model = {}
    if args.model_bindings:
        keymap = {r["text_id"]: r["norm_text"] for r in csv.DictReader(Path(args.model_keymap).open())}
        for path in args.model_bindings:
            for r in csv.DictReader(Path(path).open()):
                key = keymap.get(r["text_id"])
                if key is None:
                    continue
                hid, hname = (r.get("hpo_id") or "").strip(), (r.get("hpo_name") or "").strip()
                if hid.upper() == "NONE" or not hid:
                    model[key] = {"hpo_id": "", "hpo_label": "", "method": "no_suitable_term"}
                elif hid in hp.terms and not hp.terms[hid].obsolete and hp.terms[hid].name == hname:
                    grade = (r.get("match") or "").strip().lower()
                    model[key] = {"hpo_id": hid, "hpo_label": hname,
                                  "method": f"model_{grade}" if grade in ("exact", "close", "broader") else "model_close"}
                else:
                    model[key] = {"hpo_id": "", "hpo_label": "", "method": "model_rejected"}
    feat_rows, dis_rows, c = [], [], Counter()
    for p in sorted((run_dir / "per_paper").glob("*.json")):
        t = json.loads(p.read_text()).get("tables") or {}
        for i, r in enumerate(t.get("phenotypic_features") or []):
            b = bind_feature(r, hidx)
            if b["method"] == "unbound" and model:
                m = model.get(re.sub(r"\s+", " ", str(v(r.get("feature_text_as_stated")) or "").strip().lower()))
                if m:
                    b = dict(m, candidates=b.get("candidates", ""))
            c[f"features:{b['method']}"] += 1
            feat_rows.append({"pmid": p.stem, "row": i, "individual_label_in_paper": v(r.get("individual_label_in_paper")),
                              "feature_text_as_stated": v(r.get("feature_text_as_stated")), "status": v(r.get("status")),
                              "hpo_id_candidate": v(r.get("hpo_id_candidate")) or "", "hpo_label_candidate": v(r.get("hpo_label_candidate")) or "",
                              "hpo_id": b["hpo_id"], "hpo_label": b["hpo_label"], "method": b["method"], "candidates": b.get("candidates", "")})
        for r in t.get("individuals") or []:
            label = v(r.get("disease_label_as_stated"))
            if label in (None, "", "not reported"):
                mid, method = "", "not_stated"
            elif HA20_LABEL.search(str(label)):
                mid, method = args.ha20_mondo, "ha20_label_rule"
            else:
                mid = midx.exact(label) or ""
                method = "label" if mid else "unbound"
            c[f"disease:{method}"] += 1
            dis_rows.append({"pmid": p.stem, "individual_label_in_paper": v(r.get("individual_label_in_paper")),
                             "disease_label_as_stated": label or "", "mondo_id": mid,
                             "mondo_label": mondo.terms[mid].name if mid in mondo.terms else "", "method": method})
    with (run_dir / "hpo_bindings.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(feat_rows[0].keys()))
        w.writeheader()
        w.writerows(feat_rows)
    with (run_dir / "disease_bindings.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(dis_rows[0].keys()))
        w.writeheader()
        w.writerows(dis_rows)
    n_feat = sum(v_ for k, v_ in c.items() if k.startswith("features:"))
    summary = {"run_id": args.run_id, "hpo_release": hp.version, "mondo_release": mondo.version,
               "ha20_mondo": args.ha20_mondo, "ha20_mondo_label": mondo.terms[args.ha20_mondo].name,
               "ha20_mondo_xrefs": mondo.terms[args.ha20_mondo].xrefs,
               "group_mondo": args.group_mondo, "group_mondo_label": mondo.terms[args.group_mondo].name,
               "checklist_map": args.checklist_map, "feature_rows": n_feat,
               "counts": dict(sorted(c.items())),
               "model_bindings": args.model_bindings,
               "feature_share_bound": round(sum(v_ for k, v_ in c.items() if k.startswith("features:")
                                                and k.split(":", 1)[1] not in ("unbound", "no_suitable_term", "model_rejected")) / n_feat, 4) if n_feat else None}
    (run_dir / "binding_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
