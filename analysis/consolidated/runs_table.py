"""One table for all twelve diseases: every run from every session, read from the runs' own files.

The six registered diseases, their two corpus-addendum batches and the Majeed run are on
`main`. The five reserve-disease runs (GAMT, PAPA, ATS, Blau, LCAT) were made by another
session and sit on a branch that is not merged yet. This script looks for each run in the
working tree first and, when it is not there, in that branch at the commit it resolves to
(`git archive` into a temporary folder; nothing is checked out or merged).

  git fetch origin claude/affectionate-babbage-tfrjur
  python3 -I analysis/consolidated/runs_table.py --date 2026-11-15

Writes analysis/consolidated/runs_table_<date>.json and reports/consolidated_runs_<date>.md.
Harness-side only: it reads run summaries, ClinVar comparison results and adjudication
tables, and writes nothing under pipeline/ or data/.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import subprocess
import tarfile
import tempfile
from collections import Counter
from pathlib import Path

EXT_REF_DEFAULT = "origin/claude/affectionate-babbage-tfrjur"

# slug, name, gene, group. Order: the registered six (CONTEXT.md §4), then the reserve list in its registered order.
DISEASES = [
    ("ha20", "A20 haploinsufficiency", "TNFAIP3", "registered"),
    ("axd", "Alexander disease", "GFAP", "registered"),
    ("lad1", "Leukocyte adhesion deficiency I", "ITGB2", "registered"),
    ("ssadh", "SSADH deficiency", "ALDH5A1", "registered"),
    ("danon", "Danon disease", "LAMP2", "registered"),
    ("tangier", "Tangier disease", "ABCA1", "registered"),
    ("blau", "Blau syndrome", "NOD2", "extension"),
    ("majeed", "Majeed syndrome", "LPIN2", "exploratory"),
    ("lcat", "Familial LCAT deficiency", "LCAT", "extension"),
    ("gamt", "GAMT deficiency", "GAMT", "extension"),
    ("ats", "Arterial tortuosity syndrome", "SLC2A10", "extension"),
    ("papa", "PAPA syndrome", "PSTPIP1", "extension"),
]
GROUP_LABEL = {
    "registered": "registered (frozen plan v1.0)",
    "extension": "reserve, extension addendum",
    "exploratory": "reserve, exploratory run",
}
RUN_SETS = {
    "registered": [("pv1-{d}", "registered run"), ("pv1a-{d}", "addendum batch 1"), ("pv1a2-{d}", "addendum batch 2")],
    "extension": [("pv1-{d}", "extension run")],
    "exploratory": [("pv1s-{d}", "exploratory run")],
}
O2_FILE = {"registered": "analysis/six_disease/o2/o2_{d}.json", "extension": "analysis/extension/o2/o2_{d}.json",
           "exploratory": "analysis/majeed/o2/o2_{d}.json"}
O3_FILE = {"registered": "adjudication/o3_gaps/candidates.csv", "extension": "adjudication/o3_gaps_ext/candidates.csv",
           "exploratory": "analysis/majeed/o3/candidates.csv"}
# Majeed's dossiers: the committed copies (quotes from held-back papers withheld, D-51); the full ones are local only
O3_DOSSIERS = {"registered": "adjudication/o3_gaps/dossiers", "extension": "adjudication/o3_gaps_ext/dossiers",
               "exploratory": "adjudication/majeed/o3/dossiers_public"}
O1_KEY = {"registered": "adjudication/o1_audit/sample_key.json", "extension": "adjudication/o1x_audit/sample_key.json",
          "exploratory": "adjudication/majeed/o1m_audit/sample_key.json"}
O2T_SAMPLE = {"registered": "adjudication/o2_triage/sample.csv", "extension": "adjudication/o2_triage_ext/sample.csv",
              "exploratory": "adjudication/majeed/o2_triage/sample.csv"}
MAJEED_FIRST_PASS = "data/literature/majeed/extension_first_pass_2026-11-14/manifest.csv"
EXT_PATHS = ["data/extracted", "data/literature", "adjudication", "analysis/extension", "analysis/poc", "runs",
             "preregistration/addendum_extension_v1.md"]


def git(*a: str) -> str:
    return subprocess.run(["git", *a], check=True, capture_output=True, text=True).stdout.strip()


class Trees:
    """Working tree first, then the extension branch at a pinned commit."""

    def __init__(self, ext_ref: str | None):
        self.main = Path(".")
        self.main_commit = git("rev-parse", "HEAD")
        self.ext, self.ext_commit, self.ext_ref = None, None, ext_ref
        if ext_ref:
            try:
                self.ext_commit = git("rev-parse", "--verify", f"{ext_ref}^{{commit}}")
            except subprocess.CalledProcessError:
                return
            if subprocess.run(["git", "merge-base", "--is-ancestor", self.ext_commit, "HEAD"]).returncode == 0:
                self.ext_commit = None          # already merged: everything is in the working tree
                return
            self._tmp = tempfile.TemporaryDirectory(prefix="gprl_ext_")
            self.ext = Path(self._tmp.name)
            have = [p for p in EXT_PATHS if subprocess.run(["git", "cat-file", "-e", f"{self.ext_commit}:{p}"]).returncode == 0]
            blob = subprocess.run(["git", "archive", self.ext_commit, *have], check=True, capture_output=True).stdout
            tarfile.open(fileobj=io.BytesIO(blob)).extractall(self.ext, filter="data")

    def find(self, rel: str) -> tuple[Path | None, str]:
        if (self.main / rel).exists():
            return self.main / rel, "main"
        if self.ext is not None and (self.ext / rel).exists():
            return self.ext / rel, "extension branch"
        return None, "missing"


def jload(p: Path):
    return json.loads(p.read_text())


def rows(p: Path) -> list[dict]:
    with p.open(newline="") as fh:
        return list(csv.DictReader(fh))


def is_open(lic: str) -> bool:
    """The D-51 rule as analysis/majeed/d51_public_files.py applies it: the manifest names a Creative Commons licence."""
    lic = (lic or "").lower()
    return "creative commons" in lic or "creativecommons" in lic or lic.startswith("cc-by") or "(cc by)" in lic or "cc by" in lic


def run_stats(T: Trees, d: str, run_id: str, kind: str) -> dict | None:
    run, src = T.find(f"data/extracted/{d}/{run_id}")
    if run is None:
        return None
    need = ["reconcile_summary.json", "gatekeeper_v4_summary.json", "validation_report.json", "normalization_summary.json",
            "binding_summary.json", "phenopacket_build.json", "span_check.json"]
    missing = [f for f in need if not (run / f).exists()]
    out = {"run_id": run_id, "kind": kind, "source": src, "missing_summaries": missing}
    if missing:
        return out
    rec, gk, val = jload(run / need[0]), jload(run / need[1]), jload(run / need[2])
    norm, bind, build, span = jload(run / need[3]), jload(run / need[4]), jload(run / need[5]), jload(run / need[6])
    papers = sorted(p.stem for p in (run / "per_paper").glob("*.json"))
    n_papers = span["n_papers"]
    # "committed" counts tracked files: a run folder restored from a private copy also holds files that are not public (D-51)
    tracked = (lambda sub_: len([x for x in git("ls-files", str(run / sub_)).split("\n") if x.endswith(".json")])) if src == "main" else None
    out.update(papers=n_papers, papers_committed=tracked("per_paper") if tracked else len(papers),
               paper_ids=sorted(span.get("per_paper", {})) or papers)
    out.update(people_rows=rec["individuals_before_merging"], identities=rec["identities_after_merging"],
               with_gene_variant=rec["identities_with_target_gene_variant"], merged_pairs=rec.get("merged_pairs"))
    out.update(span_found_rate=span["span_found_rate"], span_problems=span["n_problems"])
    m = gk["rates_model_claims"]
    out.update(claims_judged=m["judged"], unsupported=m["unsupported_or_not_found"], not_fully_supported=m["not_supported"],
               claims_not_judged_yet=gk.get("model_claims_not_judged_yet"), missing_chunks=len(gk.get("missing_chunks", [])))
    out.update(variant_descriptions=norm.get("distinct_descriptions", 0), cdna_descriptions=norm.get("cdna_descriptions", 0),
               cdna_share_normalized=norm.get("share_normalized_or_corrected_of_cdna"), mane_select=norm.get("mane_select"))
    out.update(feature_rows=bind["feature_rows"], hpo_share_bound=bind["feature_share_bound"])
    out.update(phenopackets=val["phenopackets"], schema_valid=val["schema_valid"], validation_errors=len(val["errors"]),
               with_interpretation=build["counts"].get("with_interpretation"))
    pk = sorted((run / "phenopackets").glob("*.json"))
    out["phenopackets_committed"] = tracked("phenopackets") if tracked else len(pk)
    out["counted_from_private_copy"] = len(pk) == val["phenopackets"] and out["phenopackets_committed"] != val["phenopackets"]
    if len(pk) == val["phenopackets"]:
        with_dis = with_feat = 0
        for p in pk:
            x = jload(p)
            with_dis += bool(x.get("diseases"))
            with_feat += bool(x.get("phenotypicFeatures"))
        out.update(with_disease_entry=with_dis, with_any_feature=with_feat)
    # run record and licences
    rec_dir, _ = T.find(f"runs/{run_id}")
    out["run_record"] = sorted(p.name for p in rec_dir.iterdir() if p.suffix == ".json") if rec_dir else []
    man, _ = T.find(f"data/literature/{d}/manifest.csv")
    lic = {r["pmid"]: r.get("license", "") for r in rows(man)} if man else {}
    ids = out["paper_ids"]
    out["papers_in_registered_manifest"] = sum(1 for p in ids if p in lic)
    out["licence_open"] = sum(1 for p in ids if is_open(lic.get(p, "")))
    out["licence_other_text"] = sum(1 for p in ids if (lic.get(p, "") or "").strip() and not is_open(lic[p]))
    out["licence_blank"] = sum(1 for p in ids if p in lic and not (lic[p] or "").strip())
    out["not_open_ids"] = sorted(p for p in ids if not is_open(lic.get(p, "")))
    return out


def merge_check(T: Trees) -> dict:
    """What a merge of the extension branch into this tree would hit, without doing it."""
    if not T.ext_commit:
        ext = None
        try:
            ext = git("rev-parse", "--verify", f"{T.ext_ref}^{{commit}}") if T.ext_ref else None
        except subprocess.CalledProcessError:
            pass
        on_main = None
        if ext:
            try:
                on_main = subprocess.run(["git", "merge-base", "--is-ancestor", ext, "origin/main"]).returncode == 0
            except Exception:
                on_main = None
        return {"state": "merged into this tree" if ext else "extension ref not found", "extension_commit": ext,
                "on_origin_main": on_main, "branch": git("rev-parse", "--abbrev-ref", "HEAD")}
    p = subprocess.run(["git", "merge-tree", "--write-tree", "--name-only", "--no-messages", "HEAD", T.ext_commit],
                       capture_output=True, text=True)
    files = [x for x in p.stdout.strip().split("\n")[1:] if x]
    base = git("merge-base", "HEAD", T.ext_commit)
    heads = {}
    for side, ref in (("base", base), ("main", "HEAD"), ("extension", T.ext_commit)):
        txt = git("show", f"{ref}:DECISIONS.md")
        heads[side] = {}
        for line in txt.split("\n"):
            if line.startswith("### "):
                for n in re.findall(r"\bD-(\d+)\b", line):
                    heads[side].setdefault(int(n), line[4:].strip())
    new_main = {n: t for n, t in heads["main"].items() if n not in heads["base"]}
    new_ext = {n: t for n, t in heads["extension"].items() if n not in heads["base"]}
    clash = [{"number": f"D-{n}", "on_main": new_main[n], "on_extension_branch": new_ext[n]} for n in sorted(set(new_main) & set(new_ext))]
    return {"state": "not merged", "merge_base": base, "base_date": git("log", "-1", "--format=%cs", base),
            "commits_only_on_extension": int(git("rev-list", "--count", f"HEAD..{T.ext_commit}")),
            "commits_only_on_main": int(git("rev-list", "--count", f"{T.ext_commit}..HEAD")),
            "conflicted_files": files, "decision_number_clashes": clash,
            "highest_decision_number_on_main": max(heads["main"])}


def wil(w) -> str:
    return "—" if not w or w.get("share") is None else f"{100 * w['share']:.1f}% ({w['k']}/{w['n']})"


def wil_ci(w, nd=2) -> str:
    if not w or w.get("share") is None:
        return "—"
    return f"{100 * w['share']:.{nd}f}% ({w['k']}/{w['n']:,}; {100 * w['ci95'][0]:.{nd}f}–{100 * w['ci95'][1]:.{nd}f})"


def cdna(r) -> str:
    if not r["cdna_descriptions"] or r["cdna_share_normalized"] is None:
        return "no cDNA descriptions"
    return f"{100 * r['cdna_share_normalized']:.1f}% of {r['cdna_descriptions']}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--ext-ref", default=EXT_REF_DEFAULT)
    ap.add_argument("--stores", default=None, help="review_store_counts_<date>.json (ratings found on the review pages)")
    a = ap.parse_args()
    T = Trees(a.ext_ref)
    res = {"date": a.date, "main_commit": T.main_commit, "extension_ref": a.ext_ref, "extension_commit": T.ext_commit,
           "diseases": []}

    for d, name, gene, group in DISEASES:
        D = {"disease": d, "name": name, "gene": gene, "group": group, "runs": []}
        for pat, kind in RUN_SETS[group]:
            st = run_stats(T, d, pat.format(d=d), kind)
            if st:
                D["runs"].append(st)
        ids = [p for r in D["runs"] for p in r.get("paper_ids", [])]
        D["papers_run_total"] = sum(r.get("papers", 0) for r in D["runs"])
        D["papers_distinct"] = len(set(ids))
        D["papers_in_more_than_one_run"] = sorted(p for p, n in Counter(ids).items() if n > 1)
        # corpus
        man, msrc = T.find(f"data/literature/{d}/manifest.csv")
        if group == "exploratory":                     # Majeed: main's manifest, not the extension branch's first pass
            man, msrc = Path(f"data/literature/{d}/manifest.csv"), "main"
        if man and man.exists():
            m = rows(man)
            D["corpus"] = {"source": msrc, "records": len(m),
                           "included_title_abstract": sum(1 for r in m if r.get("in_extraction_corpus", "").lower() in ("true", "1", "yes")),
                           "fulltext_screen": dict(Counter(r.get("fulltext_screen", "") or "not screened at full text" for r in m))}
        # O2
        o2, osrc = T.find(O2_FILE[group].format(d=d))
        if o2:
            o = jload(o2)
            ap_ = o["all_papers"]
            D["o2"] = {"source": osrc, "run_id": o["run_id"], "snapshot_date": o["snapshot_date"], "gene": o["gene_7_2_1"],
                       "hgvs_recall_tier1": ap_["hgvs_recall_tier1"], "hgvs_recall_tier12": ap_["hgvs_recall_tier12"],
                       "overlap_tier1": ap_["overlap_tier1"], "classification_agreement": ap_["classification_agreement_among_stated"],
                       "omim": o.get("omim")}
        # O3
        c3, csrc = T.find(O3_FILE[group])
        if c3:
            cand = [r for r in rows(c3) if r["disease"] == d]
            wd = [r for r in cand if (r.get("status") or "") == "withdrawn"]
            dd, _ = T.find(O3_DOSSIERS[group])
            n_dos = len([p for p in dd.glob(f"G-{d}-*.json")]) if dd else 0
            D["o3"] = {"source": csrc, "candidates": len(cand), "withdrawn": len(wd), "for_panel": len(cand) - len(wd),
                       "dossiers": n_dos, "omim_checked": sorted({r.get("omim_checked", "") for r in cand})}
            pubrec = Path("adjudication/majeed/d51_review_public.json")
            if group == "exploratory" and pubrec.exists() and "dossiers" in jload(pubrec):
                x = jload(pubrec)["dossiers"]          # written counts the local ones too; only some are public (D-51)
                D["o3"].update(dossiers=x["written"], dossiers_public=len(x["public"]))
        # human review samples
        if group in O1_KEY:
            k, ksrc = T.find(O1_KEY[group])
            if k:
                kk = jload(k)
                D["o1_sample"] = {"source": ksrc, "claims": kk["allocation"].get(d, 0), "seed": kk["seed"], "sample_total": sum(kk["allocation"].values())}
            s, ssrc = T.find(O2T_SAMPLE[group])
            if s:
                D["o2_triage"] = {"source": ssrc, "items": sum(1 for r in rows(s) if r.get("disease") == d)}
        res["diseases"].append(D)

    # other runs over the same papers (repeats, open-weight, ablation, pilot)
    other = []
    seen = {r["run_id"] for D in res["diseases"] for r in D["runs"]}
    for root, src in ((T.main, "main"), (T.ext, "extension branch")):
        if root is None:
            continue
        for rd in sorted((root / "runs").iterdir()):
            if not rd.is_dir() or rd.name in seen or any(o["run_id"] == rd.name for o in other):
                continue
            n = None
            for f in ("manifest.json", "launch.json", "selection.json"):
                if (rd / f).exists():
                    x = jload(rd / f)
                    for key in ("n_documents", "n_papers", "papers", "selected", "documents"):
                        v = x.get(key)
                        if isinstance(v, int):
                            n = v
                        elif isinstance(v, (list, dict)):
                            n = len(v)
                        if n is not None:
                            break
                if n is not None:
                    break
            kind = ("10% repeat (run-to-run stability)" if rd.name.endswith("-repeat") else "open-weight comparison (D-10)" if rd.name.startswith("ow-")
                    else "SLIDERS ablation, direct extraction (D-44)" if rd.name.startswith("direct-") else "HA20 pilot (before the freeze)" if rd.name.startswith("poc-") else "other")
            other.append({"run_id": rd.name, "kind": kind, "papers": n, "source": src})
    res["other_runs"] = other

    stores = None
    sp = Path(a.stores) if a.stores else Path(f"analysis/consolidated/review_store_counts_{a.date}.json")
    if sp.exists():
        stores = jload(sp)
        res["review_stores"] = stores

    # totals
    tot = lambda key, groups: sum(r.get(key, 0) or 0 for D in res["diseases"] if D["group"] in groups for r in D["runs"])
    G = {"all twelve": ("registered", "extension", "exploratory"), "registered six, registered runs only": None,
         "registered six, with both addendum batches": ("registered",), "five extension diseases": ("extension",), "Majeed (exploratory)": ("exploratory",)}
    res["totals"] = {}
    for label, groups in G.items():
        if groups is None:
            rr = [r for D in res["diseases"] if D["group"] == "registered" for r in D["runs"] if r["kind"] == "registered run"]
            res["totals"][label] = {k: sum(r.get(k, 0) or 0 for r in rr) for k in ("papers", "people_rows", "identities", "with_gene_variant", "phenopackets", "with_interpretation", "claims_judged")}
            res["totals"][label]["unsupported_k"] = sum(r["unsupported"]["k"] for r in rr)
        else:
            res["totals"][label] = {k: tot(k, groups) for k in ("papers", "people_rows", "identities", "with_gene_variant", "phenopackets", "with_interpretation", "claims_judged")}
            res["totals"][label]["unsupported_k"] = sum(r["unsupported"]["k"] for D in res["diseases"] if D["group"] in groups for r in D["runs"] if "unsupported" in r)

    # papers that sit in more than one disease's runs, and the merge check
    where = {}
    for D in res["diseases"]:
        for r in D["runs"]:
            for p in r.get("paper_ids", []):
                where.setdefault(p, set()).add(D["disease"])
    res["papers_in_more_than_one_disease"] = {p: sorted(v) for p, v in sorted(where.items()) if len(v) > 1}
    res["papers_distinct_all"] = len(where)
    res["merge_check"] = MC = merge_check(T)
    mj_ext = (T.ext / "data/literature/majeed/manifest.csv") if T.ext is not None else Path(MAJEED_FIRST_PASS)
    res["majeed_corpus_on_extension_branch"] = (
        {"records": len(rows(mj_ext)), "included_at_full_text": sum(1 for r in rows(mj_ext) if r.get("fulltext_screen") == "include"),
         "read_from": "extension branch" if T.ext is not None else MAJEED_FIRST_PASS}
        if mj_ext.exists() else None)

    out_json = Path(f"analysis/consolidated/runs_table_{a.date}.json")
    slim = json.loads(json.dumps(res))
    for D in slim["diseases"]:
        for r in D["runs"]:
            r.pop("paper_ids", None)
    out_json.write_text(json.dumps(slim, indent=1, sort_keys=True) + "\n")

    # ---------------------------------------------------------------- report
    L = [f"# All runs, twelve diseases: consolidated table ({a.date})", "",
         f"*Generated by `analysis/consolidated/runs_table.py --date {a.date}` from each run's own summary files; figures in "
         f"`analysis/consolidated/runs_table_{a.date}.json`. Sources: the working tree at commit `{T.main_commit[:7]}`"
         + (f" and, for runs not on it, branch `{a.ext_ref.replace('origin/', '')}` at commit `{T.ext_commit[:7]}` (not merged)" if T.ext_commit else "")
         + ". Gatekeeper shares are a second model read, not an audited error rate; no human audit of any of these runs has been returned. "
         "Every gap candidate is pending adjudication. The registered six-disease results stay primary; addendum, extension and exploratory "
         "runs are shown beside them and are not pooled into them.*", "",
         "## 1. Papers run, by disease", "",
         "| Disease (gene) | Standing | Registered or main run | Addendum batch 1 | Addendum batch 2 | Papers run | Read from |",
         "|---|---|---|---|---|---|---|"]
    for D in res["diseases"]:
        by = {r["kind"]: r for r in D["runs"]}
        first = by.get("registered run") or by.get("extension run") or by.get("exploratory run")
        c = lambda k: str(by[k]["papers"]) if k in by else "—"
        L.append(f"| {D['name']} (*{D['gene']}*) | {GROUP_LABEL[D['group']]} | {first['papers'] if first else '—'} | {c('addendum batch 1')} | "
                 f"{c('addendum batch 2')} | **{D['papers_run_total']}** | {', '.join(sorted({r['source'] for r in D['runs']}))} |")
    t = res["totals"]
    L.append(f"| **All twelve** | | {t['registered six, registered runs only']['papers'] + t['five extension diseases']['papers'] + t['Majeed (exploratory)']['papers']} | "
             f"{sum(r['papers'] for D in res['diseases'] for r in D['runs'] if r['kind'] == 'addendum batch 1')} | "
             f"{sum(r['papers'] for D in res['diseases'] for r in D['runs'] if r['kind'] == 'addendum batch 2')} | **{t['all twelve']['papers']}** | |")
    dup = {D["disease"]: D["papers_in_more_than_one_run"] for D in res["diseases"] if D["papers_in_more_than_one_run"]}
    L += ["", f"Registered six: {t['registered six, registered runs only']['papers']} papers in the registered runs, "
          f"{t['registered six, with both addendum batches']['papers']} with the two addendum batches (D-47). Five extension diseases: "
          f"{t['five extension diseases']['papers']}. Majeed: {t['Majeed (exploratory)']['papers']} documents. "
          + ("No paper appears in two runs of the same disease." if not dup else f"Papers in more than one run of a disease: {dup}."), ""]

    L += ["## 2. Basic statistics, by run", "",
          "| Disease | Run | Papers | People rows | Identities after merging | With a variant in the gene | Phenopackets (schema-valid) | With an interpretation | With a disease term | With any feature | Model claims judged | Unsupported or not found (95% CI) | Not fully supported | cDNA descriptions normalized | Phenotype rows bound to HPO |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for D in res["diseases"]:
        for r in D["runs"]:
            if r["missing_summaries"]:
                L.append(f"| {D['name']} | `{r['run_id']}` | summaries missing: {', '.join(r['missing_summaries'])} |" + " |" * 12)
                continue
            wd = r.get("with_disease_entry")
            pub = f" ({r['phenopackets_committed']} of {r['phenopackets']} files public)" if r["phenopackets_committed"] != r["phenopackets"] else ""
            L.append(f"| {D['name']} | `{r['run_id']}` | {r['papers']} | {r['people_rows']} | {r['identities']} | {r['with_gene_variant']} | "
                     f"{r['phenopackets']} ({r['schema_valid']}){pub} | {r['with_interpretation']} | {wd if wd is not None else 'not counted'} | "
                     f"{r.get('with_any_feature', 'not counted')} | {r['claims_judged']:,} | {wil_ci(r['unsupported'])} | {wil(r['not_fully_supported'])} | "
                     f"{cdna(r)} | {100 * r['hpo_share_bound']:.1f}% of {r['feature_rows']:,} |")
    L += ["", "| Set | Papers | People rows | Identities | With a variant in the gene | Phenopackets | With an interpretation | Model claims judged | Unsupported or not found |",
          "|---|---|---|---|---|---|---|---|---|"]
    for label in G:
        x = t[label]
        L.append(f"| {label} | {x['papers']} | {x['people_rows']:,} | {x['identities']:,} | {x['with_gene_variant']:,} | {x['phenopackets']:,} | "
                 f"{x['with_interpretation']:,} | {x['claims_judged']:,} | {x['unsupported_k']} ({100 * x['unsupported_k'] / x['claims_judged']:.2f}%) |")
    L += ["", "Sums across runs are plain sums. Identities are merged within a run only: nobody has been matched across the registered run and the "
          "addendum batches, or across diseases, and phenopacket IDs restart in every run (D-50), so the summed identities are an upper bound on people. "
          "\"With a disease term\" and \"with any feature\" are counted from the phenopacket files; a record without either holds identity fields only "
          "(relatives, or people whose only claims the gatekeeper removed). Where a run says some files are not public, those two columns were counted "
          "from the full run folder restored from the private copy (D-51); in a checkout without it they read \"not counted\".", ""]

    L += ["## 3. ClinVar comparison (O2) and gap candidates (O3), by disease", "",
          "| Disease | Run compared | ClinVar snapshot | Gene correct | HGVS recall, tiers 1+2 | Overlap, tier 1 | Classification agreement | Gap candidates | Withdrawn | Left for the panel | Evidence dossiers | OMIM checked |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for D in res["diseases"]:
        o, g = D.get("o2"), D.get("o3")
        L.append(f"| {D['name']} | " + (f"`{o['run_id']}` | {o['snapshot_date']} | {wil(o['gene'])} | {wil(o['hgvs_recall_tier12'])} | {wil(o['overlap_tier1'])} | {wil(o['classification_agreement'])}" if o else "not run | — | — | — | — | —")
                 + " | " + (f"{g['candidates']} | {g['withdrawn']} | {g['for_panel']} | {g['dossiers']} of {g['candidates']}"
                            + (f" ({g['dossiers_public']} public)" if "dossiers_public" in g else "") if g else "not run | — | — | —")
                 + f" | {'holdout assessment only (D-42)' if D['group'] == 'registered' else 'no'} |")
    g_all = [D["o3"] for D in res["diseases"] if "o3" in D]
    L += ["", f"Gap candidates in all: {sum(g['candidates'] for g in g_all)}, of which {sum(g['withdrawn'] for g in g_all)} withdrawn and "
          f"{sum(g['for_panel'] for g in g_all)} left for the panel. For the registered six, O2 and O3 cover the registered runs only; "
          "the addendum batches have neither yet (D-47 puts both on the combined set after the 2026-11-30 cut-off). "
          "Overlap is not precision; precision comes from the human audit.", ""]

    L += ["## 4. What is prepared for human assessment, by disease", "",
          "| Disease | Audit sample (claims) | ClinVar-miss triage items | Gap candidates for the panel | Dossiers written |",
          "|---|---|---|---|---|"]
    for D in res["diseases"]:
        o1, o2t, g = D.get("o1_sample"), D.get("o2_triage"), D.get("o3")
        L.append(f"| {D['name']} | " + (f"{o1['claims']} (sample of {o1['sample_total']}, seed {o1['seed']})" if o1 else "none drawn") + " | "
                 + (str(o2t["items"]) if o2t else "none drawn") + " | " + (str(g["for_panel"]) if g else "—") + " | "
                 + (f"{g['dossiers']} of {g['candidates']}" + (f" ({g['dossiers_public']} public)" if g and "dossiers_public" in g else "") if g else "—") + " |")
    if stores:
        L += ["", f"**Ratings entered on the review pages so far** (stores read {stores['read_on']}; `{sp}`):", "",
              "| Study | Page | Published | Documents in the store | With a rating or decision |", "|---|---|---|---|---|"]
        L += [f"| {p['study']} | {p['page']} | {'yes, private' if p.get('published', True) else 'no (local file)'} | "
              f"{p['documents'] if p.get('published', True) else '—'} | {p['with_a_rating'] if p.get('published', True) else '—'} |" for p in stores["pages"]]
        notes = [p["note"] for p in stores["pages"] if p.get("note")]
        L += [""] + [f"- {n}" for n in notes]
    L += ["", "## 5. Other runs over the same papers", "",
          "| Run | What it is | Papers | Read from |", "|---|---|---|---|"]
    L += [f"| `{o['run_id']}` | {o['kind']} | {o['papers'] if o['papers'] is not None else '—'} | {o['source']} |" for o in other]
    L += ["", "These re-read papers already counted in section 1 (repeats, the open-weight comparison, the SLIDERS ablation, the HA20 pilot); "
          "they add no papers.", "",
          "## 6. Run records and licences", "",
          "| Run | Run record files | Papers | Manifest names a Creative Commons licence | Other licence text | Licence field blank | Not in the manifest |", "|---|---|---|---|---|---|---|"]
    for D in res["diseases"]:
        for r in D["runs"]:
            if r["missing_summaries"]:
                continue
            L.append(f"| `{r['run_id']}` | {', '.join(r['run_record']) or 'none'} | {r['papers']} | {r['licence_open']} | {r['licence_other_text']} | "
                     f"{r['licence_blank']} | {r['papers'] - r['papers_in_registered_manifest']} |")
    L += ["", "The licence columns read the `license` field of `data/literature/<disease>/manifest.csv`, the field the D-51 rule uses "
          "(`analysis/majeed/d51_public_files.py`: open means the field names a Creative Commons licence). A blank field means no licence was "
          "recorded, not that the paper has none: the HA20 manifest predates the field, and addendum papers were fetched by hand, so for those "
          "runs the batch reports are the source (batch 1: 5 of 23 included papers open access). \"Other licence text\" is mostly Europe PMC's "
          "text-mining notice, which is not an open licence.", ""]

    # ------------------------------------------------------------ section 7
    ext_runs = [(D, r) for D in res["diseases"] if D["group"] == "extension" for r in D["runs"]]
    not_open = {D["disease"]: r["papers"] - r["licence_open"] for D, r in ext_runs}
    no_manifest = [r["run_id"] for D in res["diseases"] for r in D["runs"] if "manifest.json" not in r["run_record"]]
    mj = next(D for D in res["diseases"] if D["disease"] == "majeed")
    mjr = mj["runs"][0] if mj["runs"] else {}
    add = [r for D in res["diseases"] for r in D["runs"] if r["kind"].startswith("addendum")]
    pub = [p for p in stores["pages"] if p.get("published", True)] if stores else []
    rated = sum(p["with_a_rating"] for p in pub) if stores else None
    cross = res["papers_in_more_than_one_disease"]
    L += ["## 7. State of the consolidation", "",
          f"- **Distinct papers:** {res['papers_distinct_all']} across all runs in section 1"
          + (f"; {len(cross)} appear under more than one disease ({', '.join(f'{p}: {'/'.join(v)}' for p, v in cross.items())})." if cross else "; none appears under two diseases.")]
    if MC["state"] == "merged into this tree":
        L += [f"- **The five extension runs are merged into this branch** (`{MC['branch']}`; extension commit `{MC['extension_commit'][:7]}`; D-54). "
              + ("They are on `main`." if MC["on_origin_main"] else "They are not on `main` yet: that merge waits for Jimmy's word.")
              + " Decision numbers: the extension session's D-47 and D-48 are D-52 and D-53 in `DECISIONS.md`; files that session wrote keep its numbers."]
    if MC["state"] == "not merged":
        L += [f"- **The five extension runs are not on `main`.** Their branch split from `main` on {MC['base_date']} and has "
              f"{MC['commits_only_on_extension']} commits `main` lacks; `main` has {MC['commits_only_on_main']} the branch lacks. "
              f"A merge would stop on {len(MC['conflicted_files'])} files: "
              + ", ".join(f"`{f}`" for f in MC["conflicted_files"] if not f.startswith("data/literature/majeed/"))
              + f", and {sum(1 for f in MC['conflicted_files'] if f.startswith('data/literature/majeed/'))} files under `data/literature/majeed/` "
              "(each session built its own Majeed corpus)."]
        if MC["decision_number_clashes"]:
            L += ["- **Decision numbers used twice.** The two sessions each took the next free number:"]
            L += [f"  - **{c['number']}** on `main`: {c['on_main']}. On the extension branch: {c['on_extension_branch']}." for c in MC["decision_number_clashes"]]
            L += [f"  - The highest number on `main` is D-{MC['highest_decision_number_on_main']}."]
    if any(not_open.values()):
        L += [f"- **Licences (D-51).** By the manifests' licence field, {sum(not_open.values())} of the {sum(r['papers'] for _, r in ext_runs)} extension papers "
              f"name no Creative Commons licence ({', '.join(f'{d} {n}' for d, n in not_open.items() if n)}). Their extraction outputs, with quotes, "
              "were already public on the extension branch" + (", and were merged as they are under D-54, which records the exception; D-51 binds later pushes and D-16 is still to settle."
                 if MC["state"] == "merged into this tree" else ". D-51 (recorded on `main` after most of those pushes) holds back such outputs from further pushes until D-16 is settled.")]
    if no_manifest:
        L += [f"- **Run records.** {len(no_manifest)} runs have a launch record but no `manifest.json` (finish time, document list): "
              + ", ".join(f"`{x}`" for x in no_manifest) + "."]
    if res["majeed_corpus_on_extension_branch"]:
        x = res["majeed_corpus_on_extension_branch"]
        L += [f"- **Majeed syndrome has two histories.** The extension session's first-pass corpus (`{x['read_from']}`) has {x['records']} records and {x['included_at_full_text']} papers "
              "included at full text, and the addendum's own rule dropped it (fewer than 15 eligible primary reports with open full text). On `main` a wider "
              f"search ({mj['corpus']['records']} records) plus copies found by hand gave the {mjr.get('papers')} documents of `pv1s-majeed`, run as exploratory, "
              f"outside the addendum. {mjr.get('papers', 0) - mjr.get('papers_committed', 0)} of those documents' outputs and "
              f"{mjr.get('phenopackets', 0) - mjr.get('phenopackets_committed', 0)} phenopackets are held back from the repository (D-51)."]
    L += [f"- **Addendum batches.** {sum(r['papers'] for r in add)} papers and {sum(r['phenopackets'] for r in add)} phenopackets for the registered six "
          "have no ClinVar comparison, no gap candidates, no audit sample and no matching of people against the registered runs yet (D-47: after the 2026-11-30 cut-off)."]
    if rated is not None:
        L += [f"- **Human ratings returned:** {rated} across the {len(pub)} published review pages (section 4); "
              f"{len(stores['pages']) - len(pub)} more page files are built and not published."]
    L += [""]
    # ------------------------------------------------------------ section 8
    def filled(path: str, col_part: str) -> tuple[int, int]:
        p = Path(path)
        if not p.exists():
            return 0, 0
        x = rows(p)
        cols = [c for c in x[0] if col_part in c.lower()] if x else []
        return len(x), sum(1 for r in x if any((r[c] or "").strip() for c in cols))

    def grp(g):
        return [D for D in res["diseases"] if D["group"] == g]

    W = []
    for g, label in (("registered", "registered six"), ("extension", "extension five"), ("exploratory", "Majeed (exploratory)")):
        o1 = sum(D.get("o1_sample", {}).get("claims", 0) for D in grp(g))
        tr = sum(D.get("o2_triage", {}).get("items", 0) for D in grp(g))
        pc = sum(D.get("o3", {}).get("for_panel", 0) for D in grp(g))
        nd = sum(D.get("o3", {}).get("dossiers", 0) for D in grp(g))
        nc = sum(D.get("o3", {}).get("candidates", 0) for D in grp(g))
        pages = [p for p in (stores["pages"] if stores else []) if p["study"] == label]

        def prep(kind: str, none: str) -> tuple[str, str]:
            mine = [p for p in pages if kind in p["page"]]
            if not stores:
                return none, "stores not read"
            if not mine:
                return none, "—"
            if not all(p.get("published", True) for p in mine):
                return f"{len(mine)} page file{'s' if len(mine) != 1 else ''} built, not published", "—"
            done = sum(p["with_a_rating"] for p in mine)
            return f"{len(mine)} page{'s' if len(mine) != 1 else ''} ({', '.join(p['page'].split(', ')[-1] for p in mine)})" if len(mine) > 1 or ", " in mine[0]["page"] else "1 page", f"{done} returned"
        if o1:
            W.append((label, "Audit of extracted values, two raters each", f"{o1} claims", *prep("audit", "sample drawn, no page")))
        if tr:
            W.append((label, "Triage of ClinVar misses", f"{tr} items", *prep("triage", "sample drawn, no page")))
        W.append((label, "Adjudication of gap candidates", f"{pc} candidates ({nd} of {nc} with a dossier)", *prep("adjudication", "no page")))
    n, k = filled("adjudication/addendum_d47/batch1_claims_to_rate.csv", "human")
    W.append(("addendum batch 1", "Disputed gatekeeper verdicts", f"{n} claims", "CSV sheet", f"{k} rated"))
    n, k = filled("adjudication/addendum_d47/batch1_exclusions_to_rate.csv", "human")
    W.append(("addendum batch 1", "Full-text exclusions to confirm", f"{n} papers", "CSV sheet", f"{k} rated"))
    n, _ = filled(f"analysis/corpus/free_copies/batch2_audit_list_{a.date}.csv", "human")
    W.append(("addendum batch 2", "Items listed for a human look", f"{n} items", "CSV list, no rating sheet yet", "—"))
    n, _ = filled("adjudication/o3_gaps/proposed_merges.csv", "human")
    W.append(("registered six", "Proposed same-person groups among gap candidates", f"{n} groups", "CSV list", "not merged, not reviewed"))
    sheets = sorted(Path("analysis/bias/comparator_sheets").glob("*.csv"))
    done = sum(1 for s in sheets if any((r.get("feature_as_stated") or "").strip() for r in rows(s)))
    W.append(("registered six (bias arm, O4)", "Comparator listing sheets, one per held-out cohort paper", f"{len(sheets)} sheets", "CSV sheets", f"{done} filled"))
    res["human_tasks"] = [dict(zip(("set", "task", "size", "form", "returned"), w)) for w in W]
    out_json.write_text(json.dumps({**slim, "human_tasks": res["human_tasks"]}, indent=1, sort_keys=True) + "\n")
    L += ["## 8. What people are asked to do", "", "| Set | Task | Size | Prepared as | Returned |", "|---|---|---|---|---|"]
    L += [f"| {' | '.join(w)} |" for w in W]
    L += ["", "The open-weight comparison's blinded audit (D-10) has no sample yet; it was to be sized with the raters' time (D-11).", ""]
    readiness = Path(f"analysis/consolidated/readiness_{a.date}.md")
    if readiness.exists():
        L += [readiness.read_text().rstrip(), ""]
    out = Path(f"reports/consolidated_runs_{a.date}.md")
    out.write_text("\n".join(L) + "\n")
    print(out.read_text())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
