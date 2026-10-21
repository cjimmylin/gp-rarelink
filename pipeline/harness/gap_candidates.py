"""O3 stage 1: gap-variant candidates and exploratory reclassification candidates (pre-registration §7.3).

Harness side only: it reads the ClinVar snapshot under the reference root (outside the repo).

A *gap variant* (§7.3) is an extracted variant that is
  - normalized to tier 1 (a GRCh38 VCF allele from VariantValidator);
  - supported: at least one variant row giving it has every identifying value judged
    supported by gatekeeper v4. Identifying values are the row's model claims among
    IDENTIFYING (gene, original string, cDNA, protein, transcript, genomic coordinates,
    person label). Rows with any of them partially supported, unsupported or span-not-found
    do not count as support, and are reported apart;
  - absent from ClinVar: no GRCh38 record with the same VCF allele in the snapshot;
  - not an OMIM allelic variant: NOT CHECKED. There is no OMIM access (D-12), and every
    output says so.

Reclassification candidates (§7.3, exploratory): supported tier-1 variants whose ClinVar
record is VUS or conflicting. They are listed with their literature support (papers,
deduplicated people, authors' stated class); "strong" is flagged [proposed] when the
variant has supported rows from >= 2 papers or >= 3 deduplicated people. Exploratory only.

Outputs (adjudication/o3_gaps/):
  candidates.csv                    one row per gap variant (harness side; has no ClinVar content
                                    beyond "absent")
  reclassification_candidates.csv   exploratory list, with ClinVar class and VariationID
  failed_gatekeeper.csv             tier-1 alleles absent from ClinVar whose rows all failed
  evidence_rows.jsonl               per candidate, the supporting variant rows (values and
                                    verbatim spans) and identities: the input for WS3 dossiers.
                                    It holds no ClinVar or OMIM content.
  summary.json, summary.md          counts per disease

  uv run python -m pipeline.harness.gap_candidates --snapshot /home/user/gp-rarelink-reference/2026-10-19
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, is_gene, v
from pipeline.harness.concordance import author_class, protein_check
from pipeline.harness.concordance_o2 import DISEASES, collapse_authors, variant_key
from pipeline.harness.snapshot_reference import classify

IDENTIFYING = ("individual_label_in_paper", "gene_symbol_as_stated", "variant_original_string", "cdna_hgvs_as_stated",
               "protein_hgvs_as_stated", "transcript_as_stated", "genomic_coordinates_as_stated")
CONTEXT_FIELDS = ("zygosity", "inheritance", "parental_testing_statement", "functional_evidence_statement",
                  "pathogenicity_as_stated_by_authors", "acmg_criteria_as_stated", "variant_type_as_stated")
OUT = Path("adjudication/o3_gaps")


def span_of(cell) -> str:
    if not isinstance(cell, dict):
        return ""
    s = cell.get("span")
    if isinstance(s, list):
        return " … ".join(str(x) for x in s if x)
    return str(s or "")


def value_of(cell):
    return cell.get("value") if isinstance(cell, dict) else cell


def clinvar_by_vcf(snap: Path, gene: str) -> dict[str, dict]:
    path = snap / "clinvar" / f"variant_summary_{gene}.tsv"
    rows = csv.DictReader((l.lstrip("#") if i == 0 else l for i, l in enumerate(path.open(encoding="utf-8"))), delimiter="\t")
    out = {}
    for r in rows:
        if r["Assembly"] != "GRCh38" or r["PositionVCF"] in ("", "-1", "na"):
            continue
        out.setdefault(f"{r['Chromosome']}:{r['PositionVCF']}:{r['ReferenceAlleleVCF']}:{r['AlternateAlleleVCF']}", r)
    return out


def cited_pmids(snap: Path, gene: str, disease: str, run_pmids: set[str]) -> set[str]:
    cites = set()
    for l in (snap / "clinvar" / f"var_citations_{gene}.tsv").open(encoding="utf-8"):
        f = l.rstrip("\n").split("\t")
        if not l.startswith("#") and len(f) > 5 and f[4] == "PubMed":
            cites.add(f[5])
    lit = {r["pmid"]: r for r in csv.DictReader((Path("data/literature") / disease / "manifest.csv").open())}
    return {p for p in run_pmids if p in cites or "clinvar_citations" in (lit.get(p, {}).get("seed_sources") or "")}


def one(disease: str, snap: Path) -> tuple[dict, list[dict], list[dict], list[dict], list[dict]]:
    cfg = json.loads(Path(f"configs/stage4/{disease}.json").read_text())
    gene = cfg["gene"]
    run = Path(f"data/extracted/{disease}/pv1-{disease}")
    run_pmids = {p.stem for p in (run / "per_paper").glob("*.json")}
    cv = clinvar_by_vcf(snap, gene)
    cited = cited_pmids(snap, gene, disease, run_pmids)
    norm = {r["variant_key"]: r for r in csv.DictReader((run / "variants_normalized.csv").open())}
    verdict = {(r["pmid"], int(r["row"]), r["field"]): r for r in csv.DictReader((run / "gatekeeper_v4.csv").open()) if r["table"] == "variants"}
    identity = {(r["pmid"], r["individual_label_in_paper"]): r["identity"] for r in csv.DictReader((run / "individuals_reconciled.csv").open())}
    reviews = {r["pmid"] for r in csv.DictReader((Path("data/literature") / disease / "manifest.csv").open())
               if "review" in (r.get("study_type") or "") or "review" in (r.get("fulltext_study_type") or "")}

    alleles: dict[str, dict] = defaultdict(lambda: {"rows_ok": [], "rows_failed": [], "norm": None})
    for p in sorted(run_pmids):
        rows = (json.loads((run / "per_paper" / f"{p}.json").read_text()).get("tables") or {}).get("variants") or []
        for i, r in enumerate(rows):
            if not is_gene(v(r.get("gene_symbol_as_stated")), gene) or v(r.get("variant_original_string")) in MISSING:
                continue
            n = norm.get(variant_key(r), {})
            if not n.get("vcf_grch38"):
                continue
            bad = []
            for f in IDENTIFYING:
                g = verdict.get((p, i, f))
                if g and g["class"] == "model" and g["verdict"] != "supported":
                    bad.append(f"{f}:{g['verdict']}")
            label = str(v(r.get("individual_label_in_paper")))
            rec = {"pmid": p, "row": i, "label": label, "identity": identity.get((p, label), ""),
                   "values": {f: value_of(r.get(f)) for f in IDENTIFYING + CONTEXT_FIELDS},
                   "spans": {f: span_of(r.get(f)) for f in IDENTIFYING + CONTEXT_FIELDS if span_of(r.get(f))},
                   "context_verdicts": {f: verdict[(p, i, f)]["verdict"] for f in CONTEXT_FIELDS if (p, i, f) in verdict and verdict[(p, i, f)]["class"] == "model"},
                   "failed": bad}
            a = alleles[n["vcf_grch38"]]
            a["norm"] = n
            (a["rows_failed"] if bad else a["rows_ok"]).append(rec)

    cands, reclass, failed, evidence = [], [], [], []
    k = 0
    for allele, a in sorted(alleles.items(), key=lambda x: (int(x[0].split(":")[1]), x[0])):
        n = a["norm"]
        rec = cv.get(allele)
        ok = a["rows_ok"]
        pmids = sorted({x["pmid"] for x in ok})
        idents = sorted({x["identity"] or f"{x['pmid']}|{x['label']}" for x in ok})
        stated_prot = {str(x["values"].get("protein_hgvs_as_stated") or "") for x in ok + a["rows_failed"]} - {"", "None", "not reported"}
        base = {"disease": disease, "gene": gene, "vcf_grch38": allele,
                "hgvs_c": n.get("mane_hgvs_transcript") or n.get("hgvs_transcript", ""),
                "hgvs_p_predicted": n.get("mane_hgvs_protein") or n.get("hgvs_protein", ""),
                "normalization_status": n.get("status", ""),
                "original_strings": " | ".join(sorted({str(x["values"].get("variant_original_string")) for x in ok + a["rows_failed"]})),
                "protein_check": protein_check(stated_prot, n.get("mane_hgvs_protein") or n.get("hgvs_protein", "")),
                "pmids": " ".join(pmids), "n_papers": len(pmids), "n_non_review_papers": len(set(pmids) - reviews), "n_rows_supported": len(ok),
                "n_rows_failed_gatekeeper": len(a["rows_failed"]), "n_identities": len(idents),
                "author_class": collapse_authors({author_class(str(x["values"].get("pathogenicity_as_stated_by_authors") or "")) for x in ok}),
                "only_clinvar_cited_papers": bool(pmids) and not (set(pmids) - cited)}
        if rec is None:
            if not ok:
                failed.append({**base, "pmids": " ".join(sorted({x["pmid"] for x in a["rows_failed"]})),
                               "failed_fields": " ; ".join(sorted({f for x in a["rows_failed"] for f in x["failed"]}))})
                continue
            k += 1
            cid = f"G-{disease}-{k:03d}"
            spans = []
            for x in ok:
                s = x["spans"].get("variant_original_string") or x["spans"].get("cdna_hgvs_as_stated") or x["spans"].get("protein_hgvs_as_stated")
                if s:
                    spans.append(f"[{x['pmid']} {x['label']}] {s}")
            cands.append({"candidate_id": cid, **base, "omim_checked": "no (D-12)", "example_spans": " || ".join(spans[:5])})
            evidence.append({"candidate_id": cid, "disease": disease, "gene": gene, "vcf_grch38": allele,
                             "hgvs_c": base["hgvs_c"], "hgvs_p_predicted": base["hgvs_p_predicted"],
                             "protein_check": base["protein_check"], "pmids": pmids, "identities": idents,
                             "rows": [{kk: x[kk] for kk in ("pmid", "row", "label", "identity", "values", "spans", "context_verdicts")} for x in ok]})
        elif ok:
            cls = classify(rec["ClinicalSignificance"])
            if cls in ("VUS", "conflicting"):
                reclass.append({**base, "clinvar_variation_id": rec["VariationID"], "clinvar_class": cls,
                                "clinvar_review_status": rec.get("ReviewStatus", ""),
                                "strong_literature_support_proposed": len(pmids) >= 2 or len(idents) >= 3,
                                "label": "exploratory"})
    tier1 = len(alleles)
    absent = sum(1 for x in alleles if x not in cv)
    summ = {"disease": disease, "gene": gene, "tier1_alleles": tier1, "absent_from_clinvar_before_gatekeeper": absent,
            "gap_candidates": len(cands), "absent_but_every_row_failed_gatekeeper": len(failed),
            "gap_candidates_only_from_clinvar_cited_papers": sum(c["only_clinvar_cited_papers"] for c in cands),
            "gap_candidates_protein_check": dict(Counter("agrees" if c["protein_check"] == "agrees" else c["protein_check"].split(" (")[0] for c in cands)),
            "gap_candidates_only_from_reviews": sum(c["n_non_review_papers"] == 0 for c in cands),
            "gap_candidates_by_papers": dict(Counter(min(c["n_papers"], 3) for c in cands)),
            "gap_candidates_by_author_class": dict(Counter(c["author_class"] for c in cands)),
            "reclassification_candidates": len(reclass),
            "reclassification_strong_proposed": sum(r["strong_literature_support_proposed"] for r in reclass)}
    return summ, cands, reclass, failed, evidence


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--snapshot", required=True)
    ap.add_argument("--diseases", nargs="*", default=DISEASES)
    args = ap.parse_args(argv)
    snap = Path(args.snapshot)
    OUT.mkdir(parents=True, exist_ok=True)
    S, C, R, F, E = [], [], [], [], []
    for d in args.diseases:
        s, c, r, f, e = one(d, snap)
        S.append(s); C += c; R += r; F += f; E += e
    write_csv(OUT / "candidates.csv", C)
    write_csv(OUT / "reclassification_candidates.csv", R)
    write_csv(OUT / "failed_gatekeeper.csv", F)
    with (OUT / "evidence_rows.jsonl").open("w") as fh:
        for e in E:
            fh.write(json.dumps(e, ensure_ascii=False) + "\n")
    today = datetime.now(UTC).date().isoformat()
    snap_date = snap.name
    meta = {"date": today, "snapshot": snap_date, "run_ids": [f"pv1-{d}" for d in args.diseases], "gatekeeper": "gatekeeper_v4.csv",
            "omim": "not checked: no OMIM access (D-12)", "diseases": S,
            "totals": {k: sum(s[k] for s in S) for k in ("tier1_alleles", "absent_from_clinvar_before_gatekeeper", "gap_candidates",
                                                            "absent_but_every_row_failed_gatekeeper", "gap_candidates_only_from_reviews", "reclassification_candidates",
                                                            "reclassification_strong_proposed")}}
    (OUT / "summary.json").write_text(json.dumps(meta, indent=1) + "\n")
    L = [f"# O3 stage 1: gap-variant candidates ({today})", "",
         f"*Generated by `pipeline/harness/gap_candidates.py` from the pv1 runs, gatekeeper v4 and the ClinVar snapshot of {snap_date}. "
         "OMIM allelic variants are not checked (no OMIM access, D-12), so every candidate is a ClinVar gap only. All candidates are *pending adjudication*.*", "",
         "| Disease | Tier-1 alleles | Absent from ClinVar | Gap candidates (gatekeeper-supported) | Every row failed gatekeeper | Candidates only from ClinVar-cited papers | Candidates only from reviews | Reclassification candidates (strong, proposed rule) |",
         "|---|---|---|---|---|---|---|---|"]
    for s in S + [{"disease": "**all**", **meta["totals"], "gap_candidates_only_from_clinvar_cited_papers": sum(s["gap_candidates_only_from_clinvar_cited_papers"] for s in S)}]:
        L.append(f"| {s['disease']} | {s['tier1_alleles']} | {s['absent_from_clinvar_before_gatekeeper']} | {s['gap_candidates']} | "
                 f"{s['absent_but_every_row_failed_gatekeeper']} | {s['gap_candidates_only_from_clinvar_cited_papers']} | {s['gap_candidates_only_from_reviews']} | "
                 f"{s['reclassification_candidates']} ({s['reclassification_strong_proposed']}) |")
    L += ["", "**Protein check** (the paper's stated protein against VariantValidator's prediction from the normalized cDNA; a pre-triage flag, not a verdict):", ""]
    for s in S:
        L.append(f"- {s['disease']}: {', '.join(f'{k} {n}' for k, n in sorted(s['gap_candidates_protein_check'].items()))}")
    L += ["", "**Papers per candidate** (3 means 3 or more):", ""]
    for s in S:
        L.append(f"- {s['disease']}: {', '.join(f'{k}: {n}' for k, n in sorted(s['gap_candidates_by_papers'].items()))}")
    (OUT / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
