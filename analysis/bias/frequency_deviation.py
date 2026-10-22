"""Bias arm: literature vs comparator-cohort phenotype frequencies (pre-registration §7.4.2; D-35).

Runs only on comparator sheets a person has filled (analysis/bias/comparator_sheets/*.csv);
rows without hpo_id and n_with_feature are skipped, and a sheet with none is reported as
waiting. Literature frequencies come from the gatekeeper-filtered pv1 phenopackets, one per
deduplicated individual. Comparator papers are held out of the corpus, so none of their rows is
counted; people the comparator also describes through other papers cannot be detected and are
not removed (say so in any report).

Per comparator feature T (HPO, pinned hp.obo):
  observed  the person has an observed term equal to T or a descendant of T;
  excluded  not observed, and an excluded term equal to T or an ancestor of T;
  primary   observed / (observed + excluded), among individuals explicitly assessed;
  secondary observed / all individuals in the disease's phenopackets.
Cohort frequency: n_with_feature / n_assessed (or / cohort_n when n_assessed is blank).
Reported: per-feature difference (literature minus cohort), and the per-disease mean absolute
deviation (MAD) over features with a defined primary frequency, with a publication-cluster
bootstrap 95% CI (individuals clustered by the first PMID in their phenopacket; 2000
resamples; seed 7425).

  uv run python analysis/bias/frequency_deviation.py
writes analysis/bias/frequency_deviation_<date>.json and .md.
"""
from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pipeline.harness.concordance import ancestors_or_self, load_obo_parents

HPO = Path("data/ontologies/2026-10-19/hp.obo")  # data-version hp/releases/2026-09-01
SHEETS = Path("analysis/bias/comparator_sheets")
SEED, REPS = 7425, 2000


def load_people(disease: str) -> list[dict]:
    people = []
    for f in sorted(Path(f"data/extracted/{disease}/pv1-{disease}/phenopackets").glob("*.json")):
        d = json.loads(f.read_text())
        obs, exc = set(), set()
        for pf in d.get("phenotypicFeatures") or []:
            (exc if pf.get("excluded") else obs).add(pf["type"]["id"])
        refs = (d.get("metaData") or {}).get("externalReferences") or []
        people.append({"id": d.get("id"), "obs": obs, "exc": exc, "cluster": refs[0]["id"] if refs else d.get("id")})
    return people


def status(p: dict, term: str, parents, cache) -> str:
    if any(term in ancestors_or_self(o, parents, cache) for o in p["obs"]):
        return "observed"
    anc = ancestors_or_self(term, parents, cache)
    if any(e in anc for e in p["exc"]):
        return "excluded"
    return "not_reported"


def lit_freq(people: list[dict], term: str, parents, cache) -> tuple[int, int, int]:
    s = [status(p, term, parents, cache) for p in people]
    return s.count("observed"), s.count("excluded"), len(s)


def main() -> int:
    parents, cache = load_obo_parents(HPO), {}
    out = {"date": datetime.now(UTC).date().isoformat(), "seed": SEED, "reps": REPS, "comparators": []}
    for sheet in sorted(SHEETS.glob("*.csv")):
        disease, key = sheet.stem.split("__", 1)
        rows = [r for r in csv.DictReader(sheet.open()) if (r.get("hpo_id") or "").startswith("HP:") and (r.get("n_with_feature") or "").strip()]
        if not rows:
            out["comparators"].append({"disease": disease, "comparator": key, "status": "waiting for the human listing"})
            continue
        people = load_people(disease)
        feats = []
        for r in rows:
            den = (r.get("n_assessed") or "").strip() or (r.get("cohort_n") or "").strip()
            cf = int(r["n_with_feature"]) / int(den) if den else None
            o, e, n = lit_freq(people, r["hpo_id"].strip(), parents, cache)
            prim = o / (o + e) if o + e else None
            feats.append({"hpo_id": r["hpo_id"].strip(), "hpo_label": r.get("hpo_label", ""), "cohort_freq": cf,
                          "lit_observed": o, "lit_excluded": e, "lit_all": n, "lit_primary": prim, "lit_secondary": o / n if n else None,
                          "diff_primary": (prim - cf) if prim is not None and cf is not None else None})
        defined = [f for f in feats if f["diff_primary"] is not None]
        mad = sum(abs(f["diff_primary"]) for f in defined) / len(defined) if defined else None
        clusters = defaultdict(list)
        for p in people:
            clusters[p["cluster"]].append(p)
        keys = sorted(clusters)
        rng = random.Random(SEED)
        boots = []
        for _ in range(REPS):
            sample = [p for k in (rng.choice(keys) for _ in keys) for p in clusters[k]]
            ds = []
            for f in defined:
                o, e, _ = lit_freq(sample, f["hpo_id"], parents, cache)
                if o + e:
                    ds.append(abs(o / (o + e) - f["cohort_freq"]))
            if ds:
                boots.append(sum(ds) / len(ds))
        boots.sort()
        ci = [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]] if boots else None
        out["comparators"].append({"disease": disease, "comparator": key, "status": "computed", "features": feats,
                                   "features_with_primary": len(defined), "mad_primary": mad, "mad_ci95_cluster_bootstrap": ci,
                                   "clusters": len(keys), "individuals": len(people)})
    stamp = out["date"]
    Path(f"analysis/bias/frequency_deviation_{stamp}.json").write_text(json.dumps(out, indent=1) + "\n")
    L = [f"# Literature vs comparator frequencies ({stamp})", "", "*Generated by `analysis/bias/frequency_deviation.py` (§7.4.2).*", ""]
    for c in out["comparators"]:
        if c["status"] != "computed":
            L.append(f"- {c['disease']} / {c['comparator']}: {c['status']}")
        else:
            ci = c["mad_ci95_cluster_bootstrap"]
            L.append(f"- {c['disease']} / {c['comparator']}: {c['features_with_primary']} features; MAD {c['mad_primary']:.3f}"
                     + (f" (95% CI {ci[0]:.3f}–{ci[1]:.3f})" if ci else ""))
    Path(f"analysis/bias/frequency_deviation_{stamp}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
