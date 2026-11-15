"""Bias arm: literature vs comparator-cohort phenotype frequencies (pre-registration §7.4.2; D-35).

Runs only on comparator sheets a person has filled (analysis/bias/comparator_sheets/*.csv);
rows without hpo_id and n_with_feature are skipped, and a sheet with none is reported as
waiting. Literature frequencies come from the gatekeeper-filtered phenopackets, one per
deduplicated individual. Comparator papers are held out of the corpus, so none of their rows is
counted.

People the comparator also describes through other papers are removed with the tags in
analysis/bias/comparator_overlap/tags_<date>.csv (the newest file is used; see the README there).
The tags are graded, so every comparator is computed on a grid and all of it is reported:
  run set     registered (pv1)  |  with_addendum (pv1 + the D-47 addendum runs pv1a and pv1a2)
  exclusion   none  |  stated  |  stated_probable  |  stated_probable_possible
  records     all_records (every phenopacket, as this script first did)  |  with_disease_term
PRIMARY names the primary analysis (D-48, decided by Jimmy on 2026-11-15, before any sheet was
filled): the registered run, people tagged stated or probable removed, records with a disease
term only. The other cells are reported beside it. A disease without tags is computed with
exclusion "none" only and says why (Alexander disease is left untagged under D-48). Addendum
identities are not deduplicated against the registered run; where runs are combined, a person is
keyed by run and identity (D-50).

Per comparator feature T (HPO, pinned hp.obo):
  observed  the person has an observed term equal to T or a descendant of T;
  excluded  not observed, and an excluded term equal to T or an ancestor of T;
  primary   observed / (observed + excluded), among individuals explicitly assessed;
  secondary observed / all individuals in the analysis.
Cohort frequency: n_with_feature / n_assessed (or / cohort_n when n_assessed is blank).
Reported: per-feature difference (literature minus cohort), and the per-disease mean absolute
deviation (MAD) over features with a defined primary frequency, with a publication-cluster
bootstrap 95% CI (individuals clustered by the first PMID in their phenopacket; 2000
resamples; seed 7425, restarted for every cell of the grid).

  uv run python analysis/bias/frequency_deviation.py
writes analysis/bias/frequency_deviation_<date>.json and .md.
"""
from __future__ import annotations

import csv
import json
import random
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pipeline.harness.concordance import ancestors_or_self, load_obo_parents

HPO = Path("data/ontologies/2026-10-19/hp.obo")  # data-version hp/releases/2026-09-01
SHEETS = Path("analysis/bias/comparator_sheets")
OVERLAP = Path("analysis/bias/comparator_overlap")
SEED, REPS = 7425, 2000
RUN_SETS = {"registered": ("pv1",), "with_addendum": ("pv1", "pv1a", "pv1a2")}
EXCLUSIONS = {
    "none": (),
    "stated": ("in_cohort_stated",),
    "stated_probable": ("in_cohort_stated", "in_cohort_probable"),
    "stated_probable_possible": ("in_cohort_stated", "in_cohort_probable", "in_cohort_possible"),
}
RECORDS = ("all_records", "with_disease_term")
PRIMARY = {"run_set": "registered", "exclusion": "stated_probable", "records": "with_disease_term"}  # D-48, decided 2026-11-15
UNTAGGED = {"axd": "left untagged (D-48): the comparator is UK Biobank carriers, who are not the subjects of case reports"}


def load_tags(root: Path) -> tuple[dict, str | None]:
    files = sorted((root / OVERLAP).glob("tags_2*.csv"))
    if not files:
        return {}, None
    tags = {(r["disease"], r["run"], r["identity"]): r["tag"] for r in csv.DictReader(files[-1].open())}
    return tags, files[-1].name


def load_people(root: Path, disease: str, tags: dict) -> list[dict]:
    """Every phenopacket of the disease in the registered and addendum runs."""
    people = []
    for run in RUN_SETS["with_addendum"]:
        for f in sorted((root / f"data/extracted/{disease}/{run}-{disease}/phenopackets").glob("*.json")):
            d = json.loads(f.read_text())
            obs, exc = set(), set()
            for pf in d.get("phenotypicFeatures") or []:
                (exc if pf.get("excluded") else obs).add(pf["type"]["id"])
            refs = (d.get("metaData") or {}).get("externalReferences") or []
            ident = (d.get("subject") or {}).get("id")
            people.append({"id": d.get("id"), "run": run, "obs": obs, "exc": exc,
                           "cluster": refs[0]["id"] if refs else d.get("id"),
                           "has_disease": bool(d.get("diseases")), "tag": tags.get((disease, run, ident))})
    return people


def status(p: dict, term: str, parents, cache) -> str:
    if any(term in ancestors_or_self(o, parents, cache) for o in p["obs"]):
        return "observed"
    anc = ancestors_or_self(term, parents, cache)
    if any(e in anc for e in p["exc"]):
        return "excluded"
    return "not_reported"


def select(people: list[dict], run_set: str, exclusion: str, records: str) -> list[dict]:
    return [p for p in people
            if p["run"] in RUN_SETS[run_set] and p["tag"] not in EXCLUSIONS[exclusion]
            and (records == "all_records" or p["has_disease"])]


def analyse(people: list[dict], rows: list[dict]) -> dict:
    """people carry "st": their status for each row's term, in row order."""
    feats = []
    for j, r in enumerate(rows):
        den = (r.get("n_assessed") or "").strip() or (r.get("cohort_n") or "").strip()
        cf = int(r["n_with_feature"]) / int(den) if den else None
        s = [p["st"][j] for p in people]
        o, e, n = s.count("observed"), s.count("excluded"), len(s)
        prim = o / (o + e) if o + e else None
        feats.append({"hpo_id": r["hpo_id"].strip(), "hpo_label": r.get("hpo_label", ""), "cohort_freq": cf,
                      "lit_observed": o, "lit_excluded": e, "lit_all": n, "lit_primary": prim, "lit_secondary": o / n if n else None,
                      "diff_primary": (prim - cf) if prim is not None and cf is not None else None})
    defined = [j for j, f in enumerate(feats) if f["diff_primary"] is not None]
    mad = sum(abs(feats[j]["diff_primary"]) for j in defined) / len(defined) if defined else None
    clusters = defaultdict(list)
    for p in people:
        clusters[p["cluster"]].append(p)
    keys = sorted(clusters)
    rng = random.Random(SEED)
    boots = []
    for _ in range(REPS if defined and keys else 0):
        sample = [p for k in (rng.choice(keys) for _ in keys) for p in clusters[k]]
        ds = []
        for j in defined:
            s = [p["st"][j] for p in sample]
            o, e = s.count("observed"), s.count("excluded")
            if o + e:
                ds.append(abs(o / (o + e) - feats[j]["cohort_freq"]))
        if ds:
            boots.append(sum(ds) / len(ds))
    boots.sort()
    ci = [boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots)) - 1]] if boots else None
    return {"features": feats, "features_with_primary": len(defined), "mad_primary": mad, "mad_ci95_cluster_bootstrap": ci,
            "clusters": len(keys), "individuals": len(people)}


def people_counts(people: list[dict]) -> dict:
    out = {}
    for name, runs in RUN_SETS.items():
        sub = [p for p in people if p["run"] in runs]
        out[name] = {"all_records": len(sub), "with_disease_term": sum(p["has_disease"] for p in sub),
                     "by_tag": dict(sorted(Counter(p["tag"] or "not_tagged" for p in sub).items()))}
    return out


def main(root: Path = Path(".")) -> int:
    parents, cache = load_obo_parents(root / HPO), {}
    tags, tags_file = load_tags(root)
    tagged_diseases = {k[0] for k in tags}
    out = {"date": datetime.now(UTC).date().isoformat(), "seed": SEED, "reps": REPS, "overlap_tags": tags_file,
           "primary": PRIMARY, "comparators": []}
    for sheet in sorted((root / SHEETS).glob("*.csv")):
        disease, key = sheet.stem.split("__", 1)
        rows = [r for r in csv.DictReader(sheet.open()) if (r.get("hpo_id") or "").startswith("HP:") and (r.get("n_with_feature") or "").strip()]
        people = load_people(root, disease, tags)
        entry = {"disease": disease, "comparator": key,
                 "overlap_tags": "tagged" if disease in tagged_diseases else UNTAGGED.get(disease, "not assessed for this disease"),
                 "people": people_counts(people)}
        if not rows:
            out["comparators"].append(entry | {"status": "waiting for the human listing"})
            continue
        for p in people:
            p["st"] = [status(p, r["hpo_id"].strip(), parents, cache) for r in rows]
        analyses = []
        for run_set in RUN_SETS:
            for exclusion in (EXCLUSIONS if disease in tagged_diseases else ("none",)):
                for records in RECORDS:
                    sub = select(people, run_set, exclusion, records)
                    removed = [p for p in select(people, run_set, "none", records) if p["tag"] in EXCLUSIONS[exclusion]]
                    analyses.append({"run_set": run_set, "exclusion": exclusion, "records": records,
                                     "removed_as_comparator_cohort": len(removed)} | analyse(sub, rows))
        out["comparators"].append(entry | {"status": "computed", "analyses": analyses})
    stamp = out["date"]
    (root / f"analysis/bias/frequency_deviation_{stamp}.json").write_text(json.dumps(out, indent=1) + "\n")
    L = [f"# Literature vs comparator frequencies ({stamp})", "", "*Generated by `analysis/bias/frequency_deviation.py` (§7.4.2).*", "",
         f"Comparator-overlap tags: `{tags_file}`." if tags_file else "Comparator-overlap tags: none found.",
         (f"Primary analysis (D-48, decided 2026-11-15): run set `{PRIMARY['run_set']}`, exclusion `{PRIMARY['exclusion']}`, records `{PRIMARY['records']}`. "
          "The other combinations are reported beside it."), ""]
    for c in out["comparators"]:
        L += [f"## {c['disease']} / {c['comparator']}", "", f"Status: {c['status']}. Overlap tags: {c['overlap_tags']}.", ""]
        L += ["| Run set | Phenopackets | With a disease term | By tag |", "|---|---|---|---|"]
        for name, pc in c["people"].items():
            L.append(f"| {name} | {pc['all_records']} | {pc['with_disease_term']} | " + ", ".join(f"{k} {v}" for k, v in pc["by_tag"].items()) + " |")
        L.append("")
        if c["status"] != "computed":
            continue
        L += ["| Run set | Exclusion | Records | Individuals | Removed | Clusters | Features | MAD | 95% CI |", "|---|---|---|---|---|---|---|---|---|"]
        for a in c["analyses"]:
            ci = a["mad_ci95_cluster_bootstrap"]
            star = " (primary)" if all(a[k] == v for k, v in PRIMARY.items()) else ""
            mad = f"{a['mad_primary']:.3f}" if a["mad_primary"] is not None else "n/a"
            L.append(f"| {a['run_set']}{star} | {a['exclusion']} | {a['records']} | {a['individuals']} | {a['removed_as_comparator_cohort']} | {a['clusters']} | "
                     f"{a['features_with_primary']} | {mad} | " + (f"{ci[0]:.3f}–{ci[1]:.3f}" if ci else "n/a") + " |")
        L.append("")
    (root / f"analysis/bias/frequency_deviation_{stamp}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
