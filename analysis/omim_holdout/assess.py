"""Assess the six-disease run against OMIM as a human-curated holdout (harness/analysis side).

Reads ground truth, so it must never be imported by pipeline.extract. Inputs:
  <root>/<date>/omim/entry_<MIM>.json, allelic_variants.csv   from pipeline/harness/omim_entries.py
  analysis/omim_holdout/omim_av_clinvar.csv                     from clinvar_lookup.py (ClinVar placement of each allelic variant)
  data/literature/<d>/manifest.csv                              corpus manifests (search, screening, access)
  data/extracted/<d>/pv1-<d>/{per_paper,variants_normalized.csv}  the frozen-pipeline run
  analysis/six_disease/o2/o2_variants.csv                        ClinVar-matched extracted variants (snapshot 2026-10-19)
  adjudication/o3_gaps/candidates.csv                            gap candidates (absent from ClinVar 2026-10-12)

What it measures, per disease:
  A. Literature recall: where every paper OMIM cites (phenotype entry, gene entry, allelic-variant narratives)
     stands in our funnel: not found by the search / excluded at title-abstract / in the corpus without open
     full text / excluded at full-text screening / extracted. Pre-registered share (§7.2.5) plus the funnel.
  B. Allelic-variant recall: for each OMIM allelic variant titled for the pilot disease, whether the run
     extracted the same variant, by which route (ClinVar VariationID, GRCh38 allele, cDNA, protein, or a
     notation-tolerant token match), from OMIM's own source paper or elsewhere; §7.2.2 reference pairs in the
     OMIM form (PMID in the run x allelic variant cited to it); completeness-style restricted and unrestricted
     recall (§7.2.7 shape, exploratory for the four diseases without a registered catalogue).
  C. ClinVar standing of OMIM's allelic variants, and OMIM's coverage of the ClinVar P/LP variants the run found.
  D. Gap candidates (O3) checked against OMIM's allelic variants (the §7.3 criterion that was waiting on D-12).
  E. Descriptive context: zygosity patterns against OMIM's inheritance; how much of the corpus post-dates the
     OMIM entries' last edits.
A patient-level comparison table for the papers both OMIM and the run cover is written under the reference
root for a reading pass (it carries OMIM prose); the judgements go in patient_level_judgements.csv by hand.

  uv run python analysis/omim_holdout/assess.py --root /home/user/gp-rarelink-reference --date 2026-10-28
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from pipeline.extract.normalize_variants import MISSING, v
from pipeline.extract.reconcile import is_gene, protein_key
from pipeline.harness.concordance import protein_short, wilson
from pipeline.harness.omim_entries import PILOT

REPO = Path(__file__).resolve().parents[2]
SYNONYMS = {"ITGB2": {"CD18", "ITGB2", "LFA-1 BETA", "CD18 (ITGB2)", "BETA2 INTEGRIN"}, "ALDH5A1": {"ALDH5A1", "SSADH"}, "TNFAIP3": {"TNFAIP3", "A20"},
            "ABCA1": {"ABCA1", "ABC1", "ABCA-1"}, "LAMP2": {"LAMP2", "LAMP-2"}, "GFAP": {"GFAP"}}
LABEL_SUB = re.compile(r"^([A-Z]{3})(\d+)([A-Z]{3})$")
NARR_SUB = re.compile(r"\b(?:c\.)?(\d+)([ACGT])-(?:to-)?([ACGT])\b")
NARR_PROT = re.compile(r"\(([A-Z]\d+(?:[A-Z]|X|\*)|[A-Z][a-z]{2}\d+(?:[A-Z][a-z]{2}|Ter)(?:fs(?:Ter)?\d*)?)\)")
SUBTOK = re.compile(r"(\d+(?:[+-]\d+)?)([acgt])(?:>|4|r|→|/|-|to)([acgt])(?![a-z])")
INDELTOK = re.compile(r"(\d+(?:_\d+)?)(del|ins|dup)")


def cdna_norm(s: str) -> str:
    """'NM_x:c.864+4A>G', 'c864 + 4A > G', 'c.864+4A→G' -> '864+4a>g'."""
    t = s.split(":")[-1].lower().replace(" ", "").replace(" ", "").replace("→", ">").replace("4g", "4g")
    t = re.sub(r"^c\.?", "", t)
    return t


def tokens(s: str) -> tuple[set[str], set[str]]:
    t = cdna_norm(s)
    return ({f"{p}{a}>{b}" for p, a, b in SUBTOK.findall(t)}, {f"{p}{k}" for p, k in INDELTOK.findall(t)})


def pshort(x: str | None) -> str | None:
    if not x:
        return None
    k = protein_key(x) or (x if re.match(r"^[A-Z]\d+", x) else None)
    return protein_short(k) if k else None


def label_keys(label: str, narrative: str) -> tuple[set[str], set[str], set[str]]:
    """Protein keys, cDNA substitution tokens and indel position tokens from OMIM's own label and narrative."""
    prot, subs, indels = set(), set(), set()
    body = label.split(", ", 1)[1] if ", " in label else label
    m = LABEL_SUB.match(body.replace(" ", ""))
    if m:
        k = pshort(f"p.{m.group(1).title()}{m.group(2)}{m.group(3).title()}")
        if k:
            prot.add(k)
    for p, a, b in NARR_SUB.findall(narrative):
        subs.add(f"{p}{a.lower()}>{b.lower()}")
    for tok in NARR_PROT.findall(narrative):
        k = pshort(tok if tok.startswith("p.") else f"p.{tok}")
        if k:
            prot.add(k)
    m = re.match(r"^(\d+)-BP (DEL|INS|DUP), (?:NT)?(\d+)", body)
    if m:
        n, kind, pos = int(m.group(1)), m.group(2).lower(), int(m.group(3))
        indels |= {f"{pos}{kind}", f"{pos}_{pos + n - 1}{kind}"}
        if kind == "ins":
            indels |= {f"{pos}_{pos + 1}ins", f"{pos}dup", f"{pos - n + 1}_{pos}dup"}
    return prot, subs, indels


def load_run(slug: str, gene: str) -> dict:
    run = REPO / "data" / "extracted" / slug / f"pv1-{slug}"
    idx = {"vcf": defaultdict(set), "prot": defaultdict(set), "cdna": defaultdict(set), "sub": defaultdict(set), "indel": defaultdict(set),
           "raw": defaultdict(set), "rows": [], "pmids": set(), "n_tier1_variants": 0, "zygosity": Counter(), "per_pmid_vcf": defaultdict(set),
           "per_pmid_prot": defaultdict(set), "per_pmid_cdna": defaultdict(set), "individuals": defaultdict(list), "variants": defaultdict(list),
           "transcript_assumed": []}
    for r in csv.DictReader((run / "variants_normalized.csv").open()):
        pm = set(r["pmids"].split())
        if r["transcript_assumed"] and r["hgvs_transcript"]:
            idx["transcript_assumed"].append((r["hgvs_transcript"], r["pmids"]))
        if r["vcf_grch38"]:
            idx["vcf"][r["vcf_grch38"]] |= pm
            idx["n_tier1_variants"] = len(idx["vcf"])
            for p in pm:
                idx["per_pmid_vcf"][p].add(r["vcf_grch38"])
        for field in ("mane_hgvs_protein", "hgvs_protein"):
            k = pshort(r[field]) if r[field] else None
            if k:
                idx["prot"][k] |= pm
                for p in pm:
                    idx["per_pmid_prot"][p].add(k)
        parts = r["variant_key"].split("|")
        if len(parts) >= 3 and parts[2]:
            k = pshort(parts[2])
            if k:
                idx["prot"][k] |= pm
                for p in pm:
                    idx["per_pmid_prot"][p].add(k)
        for c in (r["mane_hgvs_transcript"], r["hgvs_transcript"], parts[1] if len(parts) > 1 else ""):
            if c:
                n = cdna_norm(c)
                idx["cdna"][n] |= pm
                for p in pm:
                    idx["per_pmid_cdna"][p].add(n)
                s_, i_ = tokens(c)
                for t in s_:
                    idx["sub"][t] |= pm
                for t in i_:
                    idx["indel"][t] |= pm
    for p in sorted((run / "per_paper").glob("*.json")):
        idx["pmids"].add(p.stem)
        doc = json.loads(p.read_text())
        tables = doc.get("tables") or {}
        idx["individuals"][p.stem] = tables.get("individuals") or []
        for r in tables.get("variants") or []:
            g = str(v(r.get("gene_symbol_as_stated")) or "")
            if not (is_gene(g, gene) or g.upper() in SYNONYMS.get(gene, set())):
                continue
            idx["variants"][p.stem].append(r)
            idx["zygosity"][str(v(r.get("zygosity")) or "not reported").lower()] += 1
            for field in ("variant_original_string", "cdna_hgvs_as_stated", "protein_hgvs_as_stated"):
                s = v(r.get(field))
                if s in MISSING:
                    continue
                s = str(s)
                idx["raw"][s.lower()].add(p.stem)
                s_, i_ = tokens(s)
                for t in s_:
                    idx["sub"][t].add(p.stem)
                for t in i_:
                    idx["indel"][t].add(p.stem)
                k = pshort(s)
                if k:
                    idx["prot"][k].add(p.stem)
                    idx["per_pmid_prot"][p.stem].add(k)
                n = cdna_norm(s)
                if re.match(r"^\d", n):
                    idx["cdna"][n].add(p.stem)
                    idx["per_pmid_cdna"][p.stem].add(n)
    return idx


def funnel_status(m: dict | None, extracted: bool, holdout: bool) -> str:
    if extracted:
        return "extracted"
    if holdout:
        return "held out (bias arm)"
    if m is None:
        return "not found by search"
    if m.get("relevance") == "no":
        return "excluded at title/abstract"
    if m.get("in_extraction_corpus", "").lower() != "true":
        return "not in corpus (screened unclear/other)"
    acc = m.get("access_status", "")
    if acc in ("paywalled", "not_found", ""):
        return "in corpus, no open full text"
    if m.get("fulltext_screen", "").lower() in ("no", "exclude", "excluded"):
        return "excluded at full-text screening"
    return "in corpus with text, not extracted"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="/home/user/gp-rarelink-reference")
    ap.add_argument("--date", default="2026-10-28")
    ap.add_argument("--out", default="analysis/omim_holdout")
    args = ap.parse_args(argv)
    folder = Path(args.root) / args.date / "omim"
    out = REPO / args.out
    avs = list(csv.DictReader((folder / "allelic_variants.csv").open()))
    cv_rows = list(csv.DictReader((out / "omim_av_clinvar.csv").open()))
    # ClinVar records per allelic variant: keep those ClinVar itself ties to the OMIM number or that an RCV OMIM prints
    # resolves to; a dbSNP id covers every allele at the position (c.715C>T and c.715C>G share one rs), so rsID-only
    # hits are used only when no other route found a record.
    cv_by_av = defaultdict(list)
    for r in cv_rows:
        if r["variation_id"] and ("omim_xref" in r["routes"] or "rcv" in r["routes"]):
            cv_by_av[r["av"]].append(r)
    for r in cv_rows:
        if r["variation_id"] and r["av"] not in cv_by_av:
            cv_by_av[r["av"]].append(r)
    o2 = defaultdict(list)
    for r in csv.DictReader((REPO / "analysis/six_disease/o2/o2_variants.csv").open()):
        o2[r["disease"]].append(r)
    gaps = list(csv.DictReader((REPO / "adjudication/o3_gaps/candidates.csv").open()))
    holdouts = {}
    try:
        import yaml
        cfg = yaml.safe_load((REPO / "configs/diseases.yaml").read_text())
        for s, d in cfg["diseases"].items():
            holdouts[s] = set((d.get("holdouts") or {}).values())
    except Exception:
        pass

    results, av_rows, paper_rows, gap_rows, patient_rows = {}, [], [], [], []
    all_av_vids = set()
    for slug, (pmim, gene, gmim, titles) in PILOT.items():
        pe = json.loads((folder / f"entry_{pmim}.json").read_text())
        ge = json.loads((folder / f"entry_{gmim}.json").read_text())
        man = {r["pmid"]: r for r in csv.DictReader((REPO / "data/literature" / slug / "manifest.csv").open())}
        run = load_run(slug, gene)
        o2_by_vid = defaultdict(list)
        for r in o2[slug]:
            for vid in r["clinvar_variation_id"].split():
                o2_by_vid[vid].append(r)
        # --- A. literature funnel
        cited = defaultdict(set)  # pmid -> which OMIM places cite it
        for r in pe["references"]:
            if r["pmid"]:
                cited[r["pmid"]].add("phenotype entry")
        for r in ge["references"]:
            if r["pmid"]:
                cited[r["pmid"]].add("gene entry")
        dis_avs = [a for a in avs if a["gene_mim"] == gmim and (a["title"].upper() in titles or any(a["title"].upper().startswith(t + ",") for t in titles))]
        for a in dis_avs:
            for p in a["citation_pmids"].split("|"):
                if p:
                    cited[p].add(f"AV {a['av']}")
        ref_meta = {r["pmid"]: r for e in (pe, ge) for r in e["references"] if r["pmid"]}
        funnel, funnel_place = Counter(), defaultdict(Counter)
        for p, places in sorted(cited.items()):
            st = funnel_status(man.get(p), p in run["pmids"], p in holdouts.get(slug, set()))
            funnel[st] += 1
            place = ("allelic-variant narrative" if any(x.startswith("AV ") for x in places) else
                     "phenotype entry (clinical text, not an allelic variant)" if "phenotype entry" in places else "gene entry only")
            funnel_place[place][st] += 1
            m = man.get(p, {})
            paper_rows.append({"disease": slug, "pmid": p, "first_author": ref_meta.get(p, {}).get("first_author", ""), "year": ref_meta.get(p, {}).get("year", "") or m.get("year", ""),
                               "cited_in": "; ".join(sorted(places)), "funnel_status": st, "relevance": m.get("relevance", ""), "in_corpus": m.get("in_extraction_corpus", ""),
                               "access_status": m.get("access_status", ""), "fulltext_screen": m.get("fulltext_screen", ""), "seed_sources": m.get("seed_sources", ""),
                               "study_type": m.get("study_type", "")})
        corpus = {p for p, r in man.items() if r["in_extraction_corpus"].lower() == "true"}
        # --- B. allelic-variant recall
        av_results = []
        for a in dis_avs:
            prot, subs, indels = label_keys(a["label"], a["narrative"])
            vids = {r["variation_id"] for r in cv_by_av.get(a["av"], [])}
            all_av_vids |= vids
            cv_c, cv_p, snv_keys, classes = set(), set(), set(), set()
            for r in cv_by_av.get(a["av"], []):
                t = r["clinvar_title"]
                m = re.search(r":c\.([^\s]+)", t)
                if m:
                    cv_c.add(cdna_norm("c." + m.group(1)))
                    s_, i_ = tokens("c." + m.group(1))
                    subs |= s_
                    indels |= i_
                m = re.search(r"\(p\.([^)]+)\)", t)
                if m:
                    k = pshort("p." + m.group(1))
                    if k:
                        cv_p.add(k)
                if r["grch38_ref"] and r["grch38_alt"] and len(r["grch38_ref"]) == 1 and len(r["grch38_alt"]) == 1 and r["grch38_start"] == r["grch38_stop"]:
                    snv_keys.add(f"{r['grch38_chr']}:{r['grch38_start']}:{r['grch38_ref']}:{r['grch38_alt']}")
                if r["classification"]:
                    classes.add(r["classification"])
            label_prot = next(iter(label_keys(a["label"], "")[0]), None)
            cv_prot1 = sorted(cv_p)[0] if cv_p else None
            if label_prot and cv_prot1:
                lm, cm = re.match(r"^([A-Z*])(\d+)(.*)$", label_prot), re.match(r"^([A-Z*])(\d+)(.*)$", cv_prot1)
                consistency = ("same" if label_prot == cv_prot1 else
                               "numbering offset (same residues)" if lm and cm and lm.group(1) == cm.group(1) and lm.group(3) == cm.group(3) else
                               "different change")
            else:
                consistency = "no protein-level label on one side"
            prot |= cv_p
            hits = {}  # route -> set of pmids
            for vid in vids:
                for r in o2_by_vid.get(vid, []):
                    hits.setdefault(f"clinvar_id_tier{r['tier']}", set()).update(r["pmids"].split())
            for k in snv_keys:
                if k in run["vcf"]:
                    hits.setdefault("grch38_allele", set()).update(run["vcf"][k])
            for c in cv_c:
                if c in run["cdna"]:
                    hits.setdefault("cdna", set()).update(run["cdna"][c])
            for k in prot:
                if k in run["prot"]:
                    hits.setdefault("protein", set()).update(run["prot"][k])
            for t in subs:
                if t in run["sub"]:
                    hits.setdefault("substitution_token", set()).update(run["sub"][t])
            for t in indels:
                if t in run["indel"]:
                    hits.setdefault("indel_token", set()).update(run["indel"][t])
            strict_routes = {k for k in hits if k in ("clinvar_id_tier1", "grch38_allele", "cdna")}
            prot_routes = {k for k in hits if k in ("clinvar_id_tier2", "protein")}
            fuzzy_routes = {k for k in hits if k in ("substitution_token", "indel_token")}
            level = "tier1" if strict_routes else "tier2_protein" if prot_routes else "fuzzy_token" if fuzzy_routes else "not recovered"
            found_pmids = set().union(*hits.values()) if hits else set()
            src = {p for p in a["citation_pmids"].split("|") if p}
            src_status = {p: funnel_status(man.get(p), p in run["pmids"], p in holdouts.get(slug, set())) for p in sorted(src)}
            src_extracted = {p for p in src if p in run["pmids"]}
            primary_found = {p for p in found_pmids if man.get(p, {}).get("study_type", "") != "review/meta-analysis"}
            miss = ""
            if level == "not recovered":
                miss = "source paper extracted; variant missed there" if src_extracted else (
                    "no source paper in the run; variant not reported elsewhere in the extracted corpus")
            row = {"disease": slug, "av": a["av"], "omim_label": a["label"], "omim_title": a["title"], "clinvar_variation_ids": " ".join(sorted(vids, key=int)),
                   "clinvar_hgvs": "; ".join(sorted({r["clinvar_title"] for r in cv_by_av.get(a["av"], [])})), "clinvar_classification": "; ".join(sorted(classes)),
                   "recovery_level": level, "routes": "; ".join(sorted(hits)), "found_in_pmids": " ".join(sorted(found_pmids)),
                   "found_in_primary_paper": bool(primary_found), "omim_source_pmids": " ".join(sorted(src)),
                   "source_status": "; ".join(f"{p}: {s}" for p, s in src_status.items()), "source_extracted": bool(src_extracted),
                   "found_in_source_paper": bool(found_pmids & src), "miss_category": miss,
                   "omim_label_protein": label_prot or "", "clinvar_protein": cv_prot1 or "", "omim_vs_clinvar_protein": consistency}
            av_rows.append(row)
            av_results.append(row)
            if src_extracted:
                for p in sorted(src_extracted):
                    ours = [r for r in run["variants"][p]]
                    patient_rows.append({"disease": slug, "av": a["av"], "pmid": p, "omim_label": a["label"], "omim_narrative": a["narrative"],
                                         "our_variant_rows": " || ".join(f"{v(r.get('individual_label_in_paper'))}: {v(r.get('variant_original_string'))} / {v(r.get('protein_hgvs_as_stated'))} / zyg={v(r.get('zygosity'))} / inh={v(r.get('inheritance'))}" for r in ours),
                                         "our_individuals": " || ".join(f"{v(i.get('individual_label_in_paper'))} ({v(i.get('sex'))}; {v(i.get('ethnicity_or_country'))}; fam {v(i.get('family_label_in_paper'))})" for i in run["individuals"][p])})
        # §7.2.2 OMIM-form reference pairs: PMID in the run x allelic variant cited to it
        pairs = []
        for a, row in zip(dis_avs, av_results):
            for p in (x for x in a["citation_pmids"].split("|") if x and x in run["pmids"]):
                found_here = set(row["found_in_pmids"].split())
                t1 = row["recovery_level"] == "tier1" and p in found_here
                t12 = row["recovery_level"] in ("tier1", "tier2_protein") and p in found_here
                any_ = row["recovery_level"] != "not recovered" and p in found_here
                pairs.append({"pmid": p, "av": a["av"], "t1": t1, "t12": t12, "any": any_})
        n = len(av_results)
        restricted = [r for r in av_results if r["source_extracted"]]
        strict = lambda r: r["recovery_level"] in ("tier1", "tier2_protein")  # noqa: E731
        anyrec = lambda r: r["recovery_level"] != "not recovered"  # noqa: E731
        # --- C. ClinVar standing / OMIM coverage of our ClinVar P/LP
        our_plp_vids = {vid for r in o2[slug] if r["tier"] in ("1", "2") and r["clinvar_class"] in ("P", "LP", "P/LP") for vid in r["clinvar_variation_id"].split()}
        our_matched_vids = {vid for r in o2[slug] if r["tier"] in ("1", "2") for vid in r["clinvar_variation_id"].split()}
        dis_vids = {vid for r in av_results for vid in r["clinvar_variation_ids"].split()}
        # --- D. gap candidates vs OMIM
        gap_hits, gap_token = 0, 0
        for g in [x for x in gaps if x["disease"] == slug]:
            keys_c = {cdna_norm(g["hgvs_c"])} if g["hgvs_c"] else set()
            keys_p = {pshort(g["hgvs_p_predicted"])} - {None} if g["hgvs_p_predicted"] else set()
            s_tok, i_tok = set(), set()
            for s in (g["hgvs_c"], *g["original_strings"].split(" | ")):
                a_, b_ = tokens(s)
                s_tok |= a_
                i_tok |= b_
            matched = []
            for a, row in zip(dis_avs, av_results):
                prot, subs, indels = label_keys(a["label"], a["narrative"])
                cv_c = set()
                for r in cv_by_av.get(a["av"], []):
                    m = re.search(r":c\.([^\s]+)", r["clinvar_title"])
                    if m:
                        cv_c.add(cdna_norm("c." + m.group(1)))
                        a_, b_ = tokens("c." + m.group(1))
                        subs |= a_
                        indels |= b_
                    m = re.search(r"\(p\.([^)]+)\)", r["clinvar_title"])
                    if m and pshort("p." + m.group(1)):
                        prot.add(pshort("p." + m.group(1)))
                snv = {f"{r['grch38_chr']}:{r['grch38_start']}:{r['grch38_ref']}:{r['grch38_alt']}" for r in cv_by_av.get(a["av"], [])
                       if r["grch38_ref"] and r["grch38_alt"] and len(r["grch38_ref"]) == 1 and len(r["grch38_alt"]) == 1}
                why = []
                if g["vcf_grch38"] in snv:
                    why.append("grch38 allele")
                if keys_c & cv_c:
                    why.append("cdna")
                if keys_p & prot:
                    why.append("protein")
                if s_tok & subs:
                    why.append("substitution token")
                if i_tok & indels:
                    why.append("indel token")
                if why:
                    matched.append(f"{a['av']} ({', '.join(why)})")
            firm = [m_ for m_ in matched if any(k in m_ for k in ("grch38 allele", "cdna", "protein"))]
            gap_hits += bool(firm)
            gap_token += bool(matched) and not firm
            verdict = ("present in OMIM: " + "; ".join(firm) if firm else
                       "possible notation or isoform collision (token match only; check the transcript): " + "; ".join(matched) if matched else
                       "absent from OMIM allelic variants (entries frozen 2026-10-28)")
            gap_rows.append({"candidate_id": g["candidate_id"], "disease": slug, "hgvs_c": g["hgvs_c"], "hgvs_p_predicted": g["hgvs_p_predicted"],
                             "original_strings": g["original_strings"], "omim_check_2026_10_28": verdict})
        # --- E. context
        years = [int(man[p]["year"]) for p in run["pmids"] if p in man and man[p].get("year", "").isdigit()]
        last_edit = max(x for x in (pe["last_edit"], ge["last_edit"]) if x)
        corpus_years = [int(r["year"]) for p, r in man.items() if p in corpus and r.get("year", "").isdigit()]
        results[slug] = {
            "gene": gene, "phenotype_mim": pmim, "gene_mim": gmim,
            "omim_last_edit": {"phenotype_entry": pe["last_edit"], "gene_entry": ge["last_edit"], "phenotype_entry_last_contributor_update": pe["last_contributor_update"],
                               "gene_entry_last_contributor_update": ge["last_contributor_update"]},
            "A_literature": {"omim_cited_pmids_distinct": len(cited), "funnel": dict(funnel),
                             "funnel_by_citation_place": {k: dict(v_) for k, v_ in funnel_place.items()},
                             "share_of_corpus_cited_by_omim_7_2_5": wilson(len(set(cited) & corpus), len(corpus)),
                             "share_of_extracted_cited_by_omim": wilson(len(set(cited) & run["pmids"]), len(run["pmids"])),
                             "corpus_pmids": len(corpus), "extracted_pmids": len(run["pmids"]),
                             "av_source_pmids": len({p for a in dis_avs for p in a["citation_pmids"].split("|") if p}),
                             "av_source_pmids_extracted": len({p for a in dis_avs for p in a["citation_pmids"].split("|") if p and p in run["pmids"]})},
            "B_allelic_variants": {
                "omim_allelic_variants_for_disease": n,
                "by_recovery_level": dict(Counter(r["recovery_level"] for r in av_results)),
                "by_route": dict(Counter(x for r in av_results for x in r["routes"].split("; ") if x)),
                "recall_unrestricted_strict": wilson(sum(strict(r) for r in av_results), n),
                "recall_unrestricted_with_token_matches": wilson(sum(anyrec(r) for r in av_results), n),
                "recall_unrestricted_primary_papers_strict": wilson(sum(strict(r) and r["found_in_primary_paper"] for r in av_results), n),
                "restricted_denominator_source_paper_extracted": len(restricted),
                "recall_restricted_strict": wilson(sum(strict(r) for r in restricted), len(restricted)),
                "recall_restricted_in_source_paper_strict": wilson(sum(strict(r) and r["found_in_source_paper"] for r in restricted), len(restricted)),
                "recall_restricted_in_source_paper_with_token_matches": wilson(sum(anyrec(r) and r["found_in_source_paper"] for r in restricted), len(restricted)),
                "reference_pairs_7_2_2_omim_form": {"pairs": len(pairs), "recall_tier1": wilson(sum(p["t1"] for p in pairs), len(pairs)),
                                                    "recall_tier12": wilson(sum(p["t12"] for p in pairs), len(pairs)),
                                                    "recall_with_token_matches": wilson(sum(p["any"] for p in pairs), len(pairs))},
                "misses": [{"av": r["av"], "omim_label": r["omim_label"], "miss_category": r["miss_category"], "source_status": r["source_status"]} for r in av_results if r["recovery_level"] == "not recovered"],
                "token_only": [{"av": r["av"], "omim_label": r["omim_label"], "routes": r["routes"], "found_in_pmids": r["found_in_pmids"]} for r in av_results if r["recovery_level"] == "fuzzy_token"]},
            "C_clinvar": {"omim_avs_placed_in_clinvar": sum(1 for r in av_results if r["clinvar_variation_ids"]),
                          "omim_av_clinvar_classifications": dict(Counter(r["clinvar_classification"] or "no ClinVar record" for r in av_results)),
                          "run_variants_matched_to_clinvar": len(our_matched_vids), "run_variants_matched_to_clinvar_plp": len(our_plp_vids),
                          "run_clinvar_plp_variants_that_are_omim_avs": len(our_plp_vids & dis_vids),
                          "share_of_run_clinvar_plp_in_omim": wilson(len(our_plp_vids & dis_vids), len(our_plp_vids)),
                          "distinct_tier1_variants_in_run": run["n_tier1_variants"],
                          "omim_label_vs_clinvar_protein": dict(Counter(r["omim_vs_clinvar_protein"] for r in av_results)),
                          "omim_label_vs_clinvar_protein_differences": [{"av": r["av"], "omim_label": r["omim_label"], "clinvar_hgvs": r["clinvar_hgvs"], "kind": r["omim_vs_clinvar_protein"]}
                                                                        for r in av_results if r["omim_vs_clinvar_protein"] in ("numbering offset (same residues)", "different change")]},
            "D_gaps": {"candidates": sum(1 for x in gaps if x["disease"] == slug), "present_in_omim": gap_hits, "token_collisions_to_check": gap_token},
            "E_context": {"omim_inheritance": "; ".join(sorted({r["inheritance"] for r in pe["relationships"] if r["phenotype_mim"] == pmim})),
                          "zygosity_of_extracted_variant_rows": dict(run["zygosity"].most_common()),
                          "extracted_papers_after_last_omim_edit": sum(1 for y in years if y > int(last_edit[:4])),
                          "corpus_papers_after_last_omim_edit": sum(1 for y in corpus_years if y > int(last_edit[:4])),
                          "last_omim_edit_either_entry": last_edit,
                          "normalized_rows_with_transcript_assumed": len(run["transcript_assumed"]),
                          "lamp2_exon9_rows_with_transcript_assumed": [t for t in run["transcript_assumed"]
                                                                       if gene == "LAMP2" and re.search(r"c\.(\d+)", t[0]) and int(re.search(r"c\.(\d+)", t[0]).group(1)) >= 1094]}}
    # write
    def dump(name: str, rows: list[dict]):
        with (out / name).open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
    dump(f"av_recall_{args.date}.csv", av_rows)
    dump(f"omim_cited_papers_{args.date}.csv", paper_rows)
    dump(f"gap_candidates_omim_check_{args.date}.csv", gap_rows)
    with (folder / "patient_level_material.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(patient_rows[0].keys()))
        w.writeheader()
        w.writerows(patient_rows)
    totals = {"omim_allelic_variants_for_diseases": sum(r["B_allelic_variants"]["omim_allelic_variants_for_disease"] for r in results.values()),
              "recovered_strict": sum(1 for r in av_rows if r["recovery_level"] in ("tier1", "tier2_protein")),
              "recovered_with_tokens": sum(1 for r in av_rows if r["recovery_level"] != "not recovered"),
              "gap_candidates_present_in_omim": sum(r["D_gaps"]["present_in_omim"] for r in results.values()),
              "gap_candidates_token_collisions_to_check": sum(r["D_gaps"]["token_collisions_to_check"] for r in results.values()),
              "omim_cited_papers_distinct_all_diseases": len({(r["disease"], r["pmid"]) for r in paper_rows}),
              "funnel_all_diseases": dict(Counter(r["funnel_status"] for r in paper_rows))}
    totals["recall_all_strict"] = wilson(totals["recovered_strict"], totals["omim_allelic_variants_for_diseases"])
    totals["recall_all_with_tokens"] = wilson(totals["recovered_with_tokens"], totals["omim_allelic_variants_for_diseases"])
    (out / f"results_{args.date}.json").write_text(json.dumps({"date": args.date, "per_disease": results, "totals": totals}, indent=1))
    print(json.dumps(totals, indent=1))
    for slug, r in results.items():
        b = r["B_allelic_variants"]
        print(slug, "AVs", b["omim_allelic_variants_for_disease"], b["by_recovery_level"], "| funnel", r["A_literature"]["funnel"], "| gaps in OMIM", r["D_gaps"]["present_in_omim"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
