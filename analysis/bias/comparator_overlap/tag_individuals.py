"""Bias arm (O4): tag every extracted individual by whether the comparator cohort also holds them.

Pre-registration §7.4.2 step 2 computes literature frequencies "over deduplicated individuals,
excluding anyone in the comparator cohort". The comparator papers are held out of the corpus, but
the same people also reach the corpus through other papers. This script turns two hand-curated
evidence tables into one tag per phenopacket:

  paper_evidence.csv     one row per paper in the pv1, pv1a and pv1a2 runs (tag, rule, evidence)
  person_overrides.csv   people whose tag differs from their paper's (tag, rule, evidence)

Tags (README.md has the rules behind each):
  in_cohort_stated     the paper or the comparator says the person is in the comparator cohort
  in_cohort_probable   the person comes from the cohort's own source, without being named
  in_cohort_possible   shared investigator or clinic; the paper does not say where the person is held
  outside_cohort       the paper or the comparator's own criteria put the person outside it
  no_link_found        nothing links the paper to the comparator cohort
  review_only          known only through another paper's citation of a paper that has no row here
  no_disease_term      the phenopacket carries no disease term, so membership cannot be asserted

How a phenopacket gets its tag:
  1. Every row of individuals_reconciled.csv for the identity takes its person override if there
     is one, else (first-hand rows only) its paper's tag.
  2. A review-only row without an override inherits the tag of a cited paper it resolved to
     (source_pmids_resolved) when that paper has a row in paper_evidence.csv.
  3. The identity takes the strongest tag among its rows, in the order
     stated > probable > outside > possible > no_link_found; with no tagged row it is review_only.
  4. A phenopacket without a disease term is tagged no_disease_term; the tag it would otherwise
     carry is kept in tag_before_disease_check.

Checks: every run paper has exactly one evidence row; every override matches a reconciled row;
every evidence quote is looked up in the text it is said to come from, when that text is in the
container (data/literature/<d>/fulltext_md, the holdouts folder, extra --text-dir folders, or the
committed extraction spans). Quotes that cannot be looked up here are counted, not failed.

Reads run outputs, the two tables and (for the quote check) paper text. Reads nothing under
data/reference/ and is not imported by pipeline/.

  python3 -I analysis/bias/comparator_overlap/tag_individuals.py --date 2026-11-15 \
      [--text-dir <folder with <disease>/<pmid>.md or pv1_<disease>/<pmid>.md> ...]
writes tags_<date>.csv and tags_summary_<date>.json beside this file.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
RUNS = ("pv1", "pv1a", "pv1a2")
COMPARATOR = {"ssadh": "dibacco2019_ssadh_natural_history", "ha20": "he2026_ha20_multicenter"}
HOLDOUT_TEXT = {"ssadh": ["30656189.md"], "ha20": ["he2026_ha20_multicenter.txt", "he2026_flat.txt"]}
STRENGTH = ["in_cohort_stated", "in_cohort_probable", "outside_cohort", "in_cohort_possible", "no_link_found"]
RULES = {
    "comparator_names_person": "in_cohort_stated",
    "registry_database_named": "in_cohort_stated",
    "registry_group_database": "in_cohort_probable",
    "registry_group_study": "in_cohort_probable",
    "natural_history_study": "in_cohort_probable",
    "same_protocol": "in_cohort_probable",
    "shared_investigator": "in_cohort_possible",
    "comparator_clinic": "in_cohort_possible",
    "outside_by_statement": "outside_cohort",
    "excluded_by_comparator_criteria": "outside_cohort",
    "no_link": "no_link_found",
}


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def committed_spans(disease: str, pmid: str) -> set[str]:
    out: set[str] = set()

    def walk(x) -> None:
        if isinstance(x, dict):
            s = x.get("span")
            if isinstance(s, str):
                out.add(norm(s))
            elif isinstance(s, list):
                out.update(norm(i) for i in s if isinstance(i, str))
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    for run in RUNS:
        f = ROOT / f"data/extracted/{disease}/{run}-{disease}/per_paper/{pmid}.json"
        if f.exists():
            walk(json.loads(f.read_text()))
    return out


def paper_text(disease: str, pmid: str, text_dirs: list[Path]) -> str | None:
    cands = [ROOT / f"data/literature/{disease}/fulltext_md/{pmid}.md"]
    for t in text_dirs:
        cands += [t / disease / f"{pmid}.md", t / f"pv1_{disease}" / f"{pmid}.md", t / f"{pmid}.md"]
    for f in cands:
        if f.exists():
            return norm(f.read_text())
    return None


def check_quote(disease: str, pmid: str, source: str, quote: str, text_dirs: list[Path]) -> str:
    """found | not_found | not_checkable"""
    if not quote or source in ("pubmed_authors", "pubmed_affiliation"):
        return "not_checkable"
    q = norm(quote)
    if source == "comparator":
        for name in HOLDOUT_TEXT[disease]:
            f = ROOT / f"data/literature/{disease}/holdouts/{name}"
            if f.exists():
                return "found" if q in norm(f.read_text()) else "not_found"
        return "not_checkable"
    target = source.split(":", 1)[1] if source.startswith("other_paper:") else pmid
    text = paper_text(disease, target, text_dirs)
    if text is not None:
        return "found" if q in text else "not_found"
    spans = committed_spans(disease, target)
    if any(q in s or s in q and len(s) > 40 for s in spans):
        return "found"
    return "not_checkable"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--text-dir", action="append", default=[], type=Path)
    a = ap.parse_args()

    papers = {}
    for r in csv.DictReader((HERE / "paper_evidence.csv").open()):
        key = (r["disease"], r["pmid"])
        assert key not in papers, f"duplicate evidence row {key}"
        assert RULES.get(r["rule"]) == r["tag"], f"rule {r['rule']} does not give tag {r['tag']} ({key})"
        assert r["comparator_key"] == COMPARATOR[r["disease"]], key
        papers[key] = r
    overrides = {}
    for r in csv.DictReader((HERE / "person_overrides.csv").open()):
        key = (r["disease"], r["run"], r["pmid"], r["individual_label_in_paper"])
        assert key not in overrides, f"duplicate override {key}"
        assert RULES.get(r["rule"]) == r["tag"], f"rule {r['rule']} does not give tag {r['tag']} ({key})"
        overrides[key] = r

    quote_check = Counter()
    quote_problems = []
    for kind, rows in (("paper", papers.values()), ("person", overrides.values())):
        for r in rows:
            res = check_quote(r["disease"], r["pmid"], r["quote_source"], r["evidence_quote"], a.text_dir)
            if r["evidence_quote"] and r["quote_source"] not in ("pubmed_authors", "pubmed_affiliation"):
                quote_check[res] += 1
                if res != "found":
                    quote_problems.append({"table": kind, "disease": r["disease"], "pmid": r["pmid"], "result": res})

    out_rows, used_overrides = [], set()
    summary: dict = {"date": a.date, "by_disease_run_tag": {}, "papers_by_tag": {}, "papers_without_full_text": {}}
    for disease, comparator_key in COMPARATOR.items():
        run_pmids = set()
        for run in RUNS:
            run_dir = ROOT / f"data/extracted/{disease}/{run}-{disease}"
            pm = {f.stem for f in (run_dir / "per_paper").glob("*.json")}
            run_pmids |= pm
            missing = sorted(p for p in pm if (disease, p) not in papers)
            assert not missing, f"{disease} {run}: papers without an evidence row: {missing}"
            by_id = defaultdict(list)
            for r in csv.DictReader((run_dir / "individuals_reconciled.csv").open()):
                by_id[r["identity"]].append(r)
            for f in sorted((run_dir / "phenopackets").glob("*.json")):
                pk = json.loads(f.read_text())
                ident = pk["subject"]["id"]
                rows = by_id.get(ident)
                assert rows, f"{f}: no reconciled row"
                cands = []  # (tag, rule, via, pmid)
                for r in rows:
                    okey = (disease, run, r["pmid"], r["individual_label_in_paper"])
                    if okey in overrides:
                        o = overrides[okey]
                        used_overrides.add(okey)
                        cands.append((o["tag"], o["rule"], "person_override", r["pmid"]))
                    elif r["review_only"] != "True":
                        p = papers[(disease, r["pmid"])]
                        cands.append((p["tag"], p["rule"], "paper", r["pmid"]))
                    else:
                        for src in re.findall(r"\d{5,9}", r.get("source_pmids_resolved") or ""):
                            if (disease, src) in papers:
                                p = papers[(disease, src)]
                                cands.append((p["tag"], p["rule"], "cited_source", src))
                if cands:
                    tag, rule, via, pmid = min(cands, key=lambda c: STRENGTH.index(c[0]))
                else:
                    tag, rule, via, pmid = "review_only", "", "none", ""
                has_disease = bool(pk.get("diseases"))
                out_rows.append({
                    "disease": disease, "comparator_key": comparator_key, "run": run, "identity": ident,
                    "phenopacket_id": pk.get("id", ""), "has_disease_term": "yes" if has_disease else "no",
                    "tag": tag if has_disease else "no_disease_term", "tag_before_disease_check": tag,
                    "rule": rule, "via": via, "evidence_pmid": pmid,
                    "first_hand_pmids": ";".join(sorted({r["pmid"] for r in rows if r["review_only"] != "True"})),
                    "review_pmids": ";".join(sorted({r["pmid"] for r in rows if r["review_only"] == "True"})),
                })
        extra = sorted(p for (d, p) in papers if d == disease and p not in run_pmids)
        assert not extra, f"{disease}: evidence rows for papers in no run: {extra}"
        summary["papers_by_tag"][disease] = dict(Counter(r["tag"] for (d, _), r in papers.items() if d == disease))
        summary["papers_without_full_text"][disease] = sorted(p for (d, p), r in papers.items() if d == disease and r["full_text_available"] == "no")
    unused = sorted(set(overrides) - used_overrides)
    assert not unused, f"overrides that match no reconciled row: {unused}"

    for r in out_rows:
        d = summary["by_disease_run_tag"].setdefault(r["disease"], {}).setdefault(r["run"], Counter())
        d[r["tag"]] += 1
    for d in summary["by_disease_run_tag"].values():
        for run in list(d):
            d[run] = dict(sorted(d[run].items())) | {"all": sum(d[run].values())}
    with_term = [r for r in out_rows if r["has_disease_term"] == "yes"]
    summary["with_disease_term_by_disease_run_tag"] = {}
    for r in with_term:
        d = summary["with_disease_term_by_disease_run_tag"].setdefault(r["disease"], {}).setdefault(r["run"], Counter())
        d[r["tag"]] += 1
    for d in summary["with_disease_term_by_disease_run_tag"].values():
        for run in list(d):
            d[run] = dict(sorted(d[run].items())) | {"all": sum(d[run].values())}
    summary["no_disease_term_would_have_been"] = dict(Counter(
        f"{r['disease']}|{r['tag_before_disease_check']}" for r in out_rows if r["has_disease_term"] == "no"))
    summary["via"] = dict(Counter(r["via"] for r in out_rows))
    summary["evidence_rows"] = {"papers": len(papers), "person_overrides": len(overrides)}
    summary["quote_check"] = dict(quote_check) | {"problems": quote_problems}

    cols = list(out_rows[0])
    with (HERE / f"tags_{a.date}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)
    (HERE / f"tags_summary_{a.date}.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 1 if quote_check.get("not_found") else 0


if __name__ == "__main__":
    raise SystemExit(main())
