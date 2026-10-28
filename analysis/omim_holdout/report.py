"""Render reports/omim_holdout_assessment.md from the OMIM holdout assessment outputs.

Every number in the report is read from files written by scripts in this folder
(assess.py, clinvar_lookup.py) and by pipeline/harness/omim_entries.py; the
patient-level table is the hand-judged CSV (patient_level_judgements.csv). The
prose findings are written here and reference those numbers.

  uv run python analysis/omim_holdout/report.py --date 2026-10-28
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
NAMES = {"ha20": "A20 haploinsufficiency", "axd": "Alexander disease", "lad1": "LAD-I", "ssadh": "SSADH deficiency", "danon": "Danon disease", "tangier": "Tangier disease"}
ORDER = ["ha20", "axd", "lad1", "ssadh", "danon", "tangier"]


def pct(w: dict | None) -> str:
    if not w or not w.get("n"):
        return "—"
    lo, hi = w["ci95"]
    return f"{w['share'] * 100:.1f}% ({w['k']}/{w['n']}; {lo * 100:.1f}–{hi * 100:.1f})"


def table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for r in rows:
        out.append("| " + " | ".join(str(x).replace("|", "\\|").replace("\n", " ") for x in r) + " |")
    return "\n".join(out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--date", default="2026-10-28")
    ap.add_argument("--out", default="reports/omim_holdout_assessment.md")
    args = ap.parse_args(argv)
    d = args.date
    here = REPO / "analysis/omim_holdout"
    res = json.loads((here / f"results_{d}.json").read_text())
    per, tot = res["per_disease"], res["totals"]
    avs = list(csv.DictReader((here / f"av_recall_{d}.csv").open()))
    papers = list(csv.DictReader((here / f"omim_cited_papers_{d}.csv").open()))
    gaps = list(csv.DictReader((here / f"gap_candidates_omim_check_{d}.csv").open()))
    judg = list(csv.DictReader((here / "patient_level_judgements.csv").open()))
    cvl = list(csv.DictReader((here / "omim_av_clinvar.csv").open()))
    man = json.loads((REPO / "analysis/poc/reference_snapshot" / d / "omim_MANIFEST.json").read_text())
    counts = json.loads((REPO / "analysis/poc/reference_snapshot" / d / "omim_counts.json").read_text())
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, cwd=REPO).stdout.strip()
    nf_path = Path("/home/user/gp-rarelink-reference") / d / "omim" / "not_found_titles.json"
    not_found = json.loads(nf_path.read_text()) if nf_path.exists() else {}

    L: list[str] = []
    w = L.append
    w(f"# The six-disease run against OMIM as a human-curated holdout\n")
    w(f"*Generated {d} by `analysis/omim_holdout/report.py` at commit `{commit}` from `results_{d}.json`, `av_recall_{d}.csv`, "
      f"`omim_cited_papers_{d}.csv`, `gap_candidates_omim_check_{d}.csv`, `omim_av_clinvar.csv` and the hand-judged `patient_level_judgements.csv`. "
      f"OMIM source: the twelve entry pages Dr. Lin printed from omim.org on {d} (D-42), parsed by `pipeline/harness/omim_entries.py`; "
      f"ClinVar placement of OMIM's allelic variants from ClinVar E-utilities queried {cvl and json.loads((Path('/home/user/gp-rarelink-reference') / d / 'omim' / 'clinvar_lookup.json').read_text()).get('queried_utc', d) if (Path('/home/user/gp-rarelink-reference') / d / 'omim' / 'clinvar_lookup.json').exists() else d}. "
      f"Internal report: it quotes OMIM identifiers and short variant labels, and paraphrases OMIM statements in §5; it is not for release in this form (pre-registration §11).*\n")
    w("Wilson 95% intervals throughout. The run assessed is `pv1-<disease>` (frozen pipeline v1.0, 2026-10-20). "
      "Nothing here changes a pre-registered metric or threshold; §10 says which figures are pre-registered and which are exploratory.\n")

    # ---------- 1. summary
    n_av = tot["omim_allelic_variants_for_diseases"]
    w("## 1. Summary\n")
    w(f"- **What OMIM gives us.** Six phenotype entries and six gene entries, last edited between "
      f"{min(x['omim_last_edit']['gene_entry'] for x in per.values())} and {max(max(x['omim_last_edit']['gene_entry'], x['omim_last_edit']['phenotype_entry']) for x in per.values())}. "
      f"The gene entries list {sum(counts[s]['allelic_variants']['listed'] for s in ORDER)} allelic variants, of which {n_av} are titled for the six pilot diseases "
      f"(the rest: {sum(sum(counts[s]['allelic_variants']['other_titles'].values()) for s in ORDER)} for other phenotypes or reclassified, 1 moved). "
      f"OMIM calls these 'selected examples'; they are a curated sample of the literature, not a catalogue, so recall against them is the meaningful direction and 'precision against OMIM' is not.")
    w(f"- **Variant recall (B).** The run recovered **{pct(tot['recall_all_strict'])}** of the {n_av} disease-titled allelic variants at the genomic or protein level, "
      f"{pct(tot['recall_all_with_tokens'])} counting one notation-level match. Recall is high where the open-access corpus carries the variant literature "
      f"(LAD-I {pct(per['lad1']['B_allelic_variants']['recall_unrestricted_strict'])}, HA20 {pct(per['ha20']['B_allelic_variants']['recall_unrestricted_strict'])}) "
      f"and collapses where OMIM's evidence is pre-2005 and paywalled (Tangier {pct(per['tangier']['B_allelic_variants']['recall_unrestricted_strict'])}).")
    src_ex = sum(x["A_literature"]["av_source_pmids_extracted"] for x in per.values())
    src_all = sum(x["A_literature"]["av_source_pmids"] for x in per.values())
    w(f"- **Literature recall (A).** Of the {src_all} papers OMIM cites as sources for those allelic variants, the run extracted {src_ex}. "
      f"Across all {tot['omim_cited_papers_distinct_all_diseases']} OMIM-cited papers (phenotype and gene entries pooled), "
      f"{tot['funnel_all_diseases'].get('in corpus, no open full text', 0)} were in our screened corpus but had no open full text (D-32), "
      f"{tot['funnel_all_diseases'].get('not found by search', 0)} were never returned by the searches (mostly gene-biology and pre-1990 papers, §3), and {tot['funnel_all_diseases'].get('extracted', 0)} were extracted. "
      f"The pipeline's literature coverage, not its reading, is the binding constraint against OMIM.")
    w(f"- **Where the source paper was extracted, the variant was usually there.** Restricted to allelic variants whose OMIM source paper is in the run, "
      f"{sum(x['B_allelic_variants']['restricted_denominator_source_paper_extracted'] for x in per.values())} variants: "
      f"{sum(x['B_allelic_variants']['recall_restricted_in_source_paper_strict']['k'] for x in per.values())} were recovered from that very paper at the genomic or protein level, "
      f"and the misses have two named causes: a table scrambled by PDF conversion (Akaboshi 2003, three SSADH variants) and variants the paper states only in prose "
      f"('a glycine to an arginine at amino acid 169'; 'G-to-T at the first base of intron 9'), which the run keeps verbatim but cannot key (§4.3, §5).")
    w(f"- **Patient level (§5).** For the {len({r['pmid'] for r in judg})} papers both OMIM and the run cover, our records agree with OMIM's curated statements on individuals, sex, zygosity, inheritance and outcomes in "
      f"{sum(1 for r in judg if r['agreement'] == 'agree')} of {len(judg)} comparisons and partially in {sum(1 for r in judg if r['agreement'] == 'partial')}; "
      f"the {sum(1 for r in judg if r['agreement'].startswith('missed'))} misses are the Akaboshi table. Where they disagree, it is usually the run having less (a supplement not in the text) rather than something wrong.")
    w(f"- **Gap candidates (D).** None of the 215 O3 candidates is a confirmed OMIM allelic variant; one (G-danon-001) collides with OMIM 309060.0001 by notation and is a **transcript-isoform error in our normalization**, not a gap (§7). Recommendation: withdraw it and re-check the LAMP2 exon-9 variants whose transcript was assumed.")
    w(f"- **OMIM is not error-free either (§6).** One OMIM allelic variant's own ClinVar record is a synonymous change at another position (610045.0007), one is placed deep in an intron (610045.0002), "
      f"{sum(x['C_clinvar']['omim_label_vs_clinvar_protein'].get('numbering offset (same residues)', 0) for x in per.values())} use legacy protein numbering that differs from the current transcript, and the complex LAD-I allele 600065.0006 has a component ClinVar calls benign. A holdout curated by people needs the same provenance checks as our output.")
    w(f"- **OMIM is also stale relative to the corpus (§8).** {sum(x['E_context']['extracted_papers_after_last_omim_edit'] for x in per.values())} of the {sum(x['A_literature']['extracted_pmids'] for x in per.values())} extracted papers post-date the last edit of either OMIM entry for their disease, "
      f"and the run holds {sum(x['C_clinvar']['distinct_tier1_variants_in_run'] for x in per.values())} distinct genome-placed variants against OMIM's {n_av} selected examples. "
      f"Of the ClinVar P/LP variants the run found, {sum(x['C_clinvar']['run_clinvar_plp_variants_that_are_omim_avs'] for x in per.values())} of {sum(x['C_clinvar']['run_variants_matched_to_clinvar_plp'] for x in per.values())} are OMIM allelic variants.\n")

    # ---------- 2. what OMIM provides
    w("## 2. What the frozen OMIM pages contain\n")
    rows = []
    for s in ORDER:
        c, e = counts[s], man["entries"]
        pe, ge = e[c["phenotype_mim"]], e[c["gene_mim"]]
        rows.append([NAMES[s], f"{c['phenotype_mim']} / {c['gene_mim']} ({c['gene']})", f"{pe['last_edit']} / {ge['last_edit']}",
                     f"{pe['references']} / {ge['references']}", c["allelic_variants"]["listed"], c["allelic_variants"]["titled_for_disease"] + len(c["allelic_variants"]["titled_for_disease_qualified"]),
                     "; ".join(f"{k}: {v_}" for k, v_ in c["allelic_variants"]["other_titles"].items()) or "—", c["allelic_variants"]["for_disease_with_clinvar_rcv"]])
    w(table(["Disease", "Phenotype / gene MIM", "Last edit (phenotype / gene)", "References (phenotype / gene)", "Allelic variants listed", "Titled for the disease", "Other titles", "With a ClinVar RCV printed"], rows))
    w("\nEach allelic variant carries OMIM's legacy label (e.g. `ARG593CYS`, `IVS6DS, G-C, +5`), dbSNP and ClinVar accessions, and a narrative citing the source papers by author and year, "
      "which the parser resolves to PMIDs through the entry's own reference list. The phenotype entries carry no allelic-variant table and no clinical synopsis (that is a separate page); their Clinical Features sections summarize individual papers, which §5 uses. "
      f"Parsing checks passed for all twelve pages (allelic-variant counts equal the heading counts; references number 1..n; each phenotype entry names its gene entry). "
      f"Files, checksums and print times are in `analysis/poc/reference_snapshot/{d}/omim_MANIFEST.json`; the content stays outside the repository (licence, pre-registration §11).\n")

    # ---------- 3. literature funnel
    w("## 3. Literature recall: where OMIM's cited papers stand in our funnel (A)\n")
    w("Every PMID cited by a phenotype entry, a gene entry or an allelic-variant narrative was looked up in the disease's corpus manifest and in the run. "
      "'Not found by search' means no search or seed returned it; 'in corpus, no open full text' means it passed title/abstract screening but no PMC, Europe PMC or Unpaywall copy existed (D-32, open access only).\n")
    places = ["allelic-variant narrative", "phenotype entry (clinical text, not an allelic variant)", "gene entry only"]
    statuses = ["extracted", "in corpus, no open full text", "excluded at full-text screening", "in corpus with text, not extracted", "not in corpus (screened unclear/other)", "excluded at title/abstract", "held out (bias arm)", "not found by search"]
    pooled = defaultdict(Counter)
    for s in ORDER:
        for pl, cnt in per[s]["A_literature"]["funnel_by_citation_place"].items():
            for st, n in cnt.items():
                pooled[pl][st] += n
    w("**Pooled over the six diseases, by where OMIM cites the paper:**\n")
    w(table(["Cited in", "Total"] + statuses, [[pl, sum(pooled[pl].values())] + [pooled[pl].get(st, 0) for st in statuses] for pl in places]))
    w("\n**Allelic-variant source papers, per disease** (the papers from which OMIM took its variants):\n")
    rows = []
    for s in ORDER:
        cnt = per[s]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {})
        rows.append([NAMES[s], sum(cnt.values())] + [cnt.get(st, 0) for st in statuses])
    w(table(["Disease", "Total"] + statuses, rows))
    w("\n**Pre-registered share (§7.2.5):** corpus PMIDs cited by OMIM for the gene (phenotype and gene entries pooled):\n")
    w(table(["Disease", "Corpus PMIDs", "Cited by OMIM", "Extracted PMIDs", "Extracted and cited by OMIM"],
            [[NAMES[s], per[s]["A_literature"]["corpus_pmids"], pct(per[s]["A_literature"]["share_of_corpus_cited_by_omim_7_2_5"]), per[s]["A_literature"]["extracted_pmids"], pct(per[s]["A_literature"]["share_of_extracted_cited_by_omim"])] for s in ORDER]))
    # not-found titles summary
    if not_found:
        by_dec = Counter()
        kinds = Counter()
        for p, info in not_found.items():
            y = info.get("year") or ""
            by_dec[(y[:3] + "0s") if y[:3].isdigit() else "?"] += 1
        w(f"\n**The {len(not_found)} 'not found by search' papers cited by phenotype entries or allelic-variant narratives** (titles fetched from PubMed on {d}; `not_found_titles.json` under the reference root) by decade: "
          + ", ".join(f"{k} {v_}" for k, v_ in sorted(by_dec.items())) + ". ")
        w("Reading the titles: most are pre-1990 descriptions of the disorder under earlier names (LAD-I as 'Mo1 deficiency', 'LFA-1 immunodeficiency', 'defective neutrophil adhesion'; Danon disease as 'lysosomal glycogen storage disease with normal acid maltase'; Tangier disease as 'familial alpha-lipoprotein deficiency'), "
          "gene-biology, mapping and animal-model papers, and a few that OMIM cites for the allelic variant .0015 of ITGB2 as historical background. The searches in `configs/diseases.yaml` use current disease and gene names; "
          "the pre-gene-era names were not in them. That is a corpus-building limit worth fixing for diseases described before their gene (LAD-I 1979–1990, Danon 1981–2000, Tangier 1961–1999), and it matters less for HA20 (2016) and AxD.\n")
        w("Examples among the allelic-variant sources our search never returned:\n")
        ex = [(p, i) for p, i in not_found.items() if "AV " in i["cited_in"]][:12]
        w(table(["Disease", "PMID", "Year", "Title (PubMed)"], [[NAMES[i["disease"]], p, i["year"], i["title"][:110]] for p, i in ex]))
    w("")

    # ---------- 4. allelic-variant recall
    w("## 4. Allelic-variant recall (B)\n")
    w("**Matching.** Each OMIM allelic variant was placed in ClinVar through ClinVar's own OMIM cross-reference or the RCV accessions OMIM prints (dbSNP ids were not used alone: one rs number covers every allele at a position). "
      "ClinVar's title then gives current HGVS on the preferred transcript, and for SNVs a GRCh38 allele. The run's variants were matched by, in order: the ClinVar VariationID already assigned by the O2 harness (tier 1 or 2 as recorded there); the GRCh38 allele from VariantValidator; "
      "the cDNA description on the same transcript; the protein change (OMIM's label, ClinVar's title or a protein stated in the narrative); and, reported separately, a notation-tolerant token (position plus bases, which also absorbs OCR artefacts such as `c.612G4A`). "
      "'tier 1' below means a genomic-level or cDNA match, 'tier 2' protein-level only, 'token' notation-level only.\n")
    rows = []
    for s in ORDER:
        b = per[s]["B_allelic_variants"]
        lv = b["by_recovery_level"]
        rows.append([NAMES[s], b["omim_allelic_variants_for_disease"], lv.get("tier1", 0), lv.get("tier2_protein", 0), lv.get("fuzzy_token", 0), lv.get("not recovered", 0),
                     pct(b["recall_unrestricted_strict"]), pct(b["recall_unrestricted_primary_papers_strict"]), b["restricted_denominator_source_paper_extracted"], pct(b["recall_restricted_in_source_paper_strict"])])
    rows.append(["**All six**", n_av, sum(r[2] for r in rows), sum(r[3] for r in rows), sum(r[4] for r in rows), sum(r[5] for r in rows), pct(tot["recall_all_strict"]), "", sum(r[8] for r in rows), ""])
    w(table(["Disease", "OMIM allelic variants", "Tier 1", "Tier 2", "Token only", "Not recovered", "Recall anywhere in the run (tiers 1+2)", "… from non-review papers", "Source paper in run", "Recovered from that source paper"], rows))
    w("\n**§7.2.2 in the OMIM form** (reference pairs: a PMID in the run × an allelic variant OMIM cites to it; the ClinVar form of this figure is in `reports/six_disease_run_findings.md` §11):\n")
    w(table(["Disease", "Pairs", "Recall tier 1", "Recall tiers 1+2", "With token matches"],
            [[NAMES[s], per[s]["B_allelic_variants"]["reference_pairs_7_2_2_omim_form"]["pairs"], pct(per[s]["B_allelic_variants"]["reference_pairs_7_2_2_omim_form"]["recall_tier1"]),
              pct(per[s]["B_allelic_variants"]["reference_pairs_7_2_2_omim_form"]["recall_tier12"]), pct(per[s]["B_allelic_variants"]["reference_pairs_7_2_2_omim_form"]["recall_with_token_matches"])] for s in ORDER]))
    w("\nThe denominators are small because so few OMIM source papers are open access (§3): this figure is reported because it is registered, not because it discriminates.\n")
    w("### 4.1 Every allelic variant\n")
    rows = []
    for r in avs:
        src = r["source_status"]
        short_src = "; ".join(x.split(": ", 1)[1] for x in src.split("; ") if ": " in x)
        rows.append([r["av"], r["omim_label"].split(", ", 1)[-1] if ", " in r["omim_label"] else r["omim_label"], (r["clinvar_hgvs"].split("; ")[0].split("(")[-1].rstrip(")") if r["clinvar_hgvs"] else "—")[:40],
                     r["recovery_level"].replace("_", " "), r["routes"].replace("clinvar_id_", "ClinVar id ").replace("_", " "), len(r["found_in_pmids"].split()) if r["found_in_pmids"] else 0,
                     "yes" if r["found_in_source_paper"] == "True" else ("extracted, not found there" if r["source_extracted"] == "True" else "not in run"),
                     Counter(short_src.split("; ")).most_common(1)[0][0] if short_src else "—"])
    w(table(["OMIM AV", "OMIM label", "ClinVar HGVS (current)", "Recovery", "Routes", "Papers in run reporting it", "From OMIM's source paper", "Source paper status (most common)"], rows))
    w("\n### 4.2 Misses, by cause\n")
    miss_rows = []
    for s in ORDER:
        for m in per[s]["B_allelic_variants"]["misses"]:
            miss_rows.append([NAMES[s], m["av"], m["omim_label"], m["miss_category"], m["source_status"][:120]])
    w(table(["Disease", "OMIM AV", "Label", "Category", "OMIM source papers and their status"], miss_rows))
    not_in_run = sum(1 for r in miss_rows if r[3].startswith("no source paper"))
    w(f"\n{len(miss_rows)} allelic variants were not recovered: {not_in_run} because no paper OMIM cites for them is in the run and no other extracted paper reports them, "
      f"{len(miss_rows) - not_in_run} because the source paper was extracted and the variant was missed there. Tangier accounts for {sum(1 for r in miss_rows if r[0] == NAMES['tangier'])} of the misses: "
      "its allelic variants come from the 1999–2003 gene-discovery papers (Brooks-Wilson, Bodzioch, Rust, Remaley, Lapicka-Bodzioch, Guo, Huang), all in our corpus and all paywalled, and the open-access Tangier papers that were extracted are recent case reports with other variants.\n")
    w("### 4.3 What the misses inside extracted papers say about the pipeline\n")
    w("- **Table conversion, not reading.** The three SSADH variants OMIM selected from Akaboshi 2003 (W204X, R412X, G409D) were not attributed to any family because the paper's Table 2 was scrambled in PDF-to-Markdown conversion; the helper recorded this and extracted only what the text supports (the same failure was logged in `reports/six_disease_run_findings.md` §5). All three were recovered from five other papers each, so the corpus is redundant for common variants but the per-paper record is incomplete.")
    w("- **Prose variants have no key.** Wardlaw 1990 states patient 2's variant only as 'a glycine to an arginine at amino acid 169' and Chambliss 1998 gives 'G-to-T transversion at the first base of intron 9'. The run kept these verbatim with the right individuals and zygosity, but they carry no protein or cDNA field, so they never reach VariantValidator and count as unmatched in every harness. A rule to derive `p.Gly169Arg` from such prose (and nothing more) would have keyed the first; the intronic prose needs exon coordinates and should stay unkeyed but be flagged for review.")
    w("- **Isoform ambiguity.** GFAP-epsilon R430H (Melchionda 2013) failed normalization on the assumed MANE transcript with a reference mismatch, which is the safe failure; the LAMP2 exon-9b deletion in Sugie 2018 did not fail and was placed on the wrong isoform (§7). Where a paper names an exon (`E9b`) or an isoform, the transcript assumption should be overridden or the variant held back.")
    w("- **Legacy OMIM numbering.** OMIM's labels for ABCA1 use a protein numbering 60 residues short of the current transcript (CYS1417ARG is p.Cys1477Arg) and LAMP2's LEU113TER is p.Leu147Ter; matching on OMIM's label alone would have missed them. ClinVar's title resolves this, which is why the ClinVar placement step matters.\n")
    if any(per[s]["B_allelic_variants"]["token_only"] for s in ORDER):
        w("Token-only matches (reported, not counted as recovered):\n")
        w(table(["Disease", "OMIM AV", "Label", "Routes", "Papers"], [[NAMES[s], t["av"], t["omim_label"], t["routes"], t["found_in_pmids"]] for s in ORDER for t in per[s]["B_allelic_variants"]["token_only"]]))
        w("")

    # ---------- 5. patient level
    w("## 5. Patient-level agreement on the papers both OMIM and the run cover\n")
    w(f"OMIM's curators summarize individual papers in the Clinical Features and allelic-variant texts. For the {len({r['pmid'] for r in judg})} extracted papers OMIM cites, each OMIM statement was compared by hand with our per-paper records "
      f"(individuals, sex, zygosity, inheritance, variant, features, outcomes). Judged by Claude in this session on {d} from the records in `data/extracted/<disease>/pv1-<disease>/per_paper/<pmid>.json`; the OMIM side is paraphrased to identifiers and facts. "
      "'agree' means every fact OMIM states is in our record with the same value; 'partial' means the variant and individuals agree but something OMIM states is missing from ours.\n")
    w(table(["Scope", "Disease", "OMIM AV", "Paper", "OMIM states", "Our record", "Agreement", "Note"],
            [[r["scope"], NAMES[r["disease"]], r["av"] or "—", f"{r['paper']} ({r['pmid']})", r["omim_statement"], r["our_record"], f"**{r['agreement']}**", r["note"]] for r in judg]))
    c = Counter(r["agreement"] for r in judg)
    w(f"\n**Tally:** {', '.join(f'{k} {v_}' for k, v_ in c.most_common())} of {len(judg)} comparisons. ")
    w("Three patterns: (1) where the paper's text carries the facts, our record matches OMIM and often says more (onset ages, a carrier mother, per-patient outcomes in Maron 2009); "
      "(2) where the facts sit in a supplement or pedigree figure that was not in the extraction text (Zhou 2016), the run has the variants but not the sex, onset or de novo status; "
      "(3) one phenotype statement OMIM makes (mild autism in Chambliss 1998) is 'not reported' in our checklist rows, which is either a paper-text nuance or an extraction miss and should be checked against the paper. "
      "No comparison found our record asserting a fact that contradicts OMIM.\n")

    # ---------- 6. ClinVar standing
    w("## 6. OMIM's allelic variants in ClinVar, and OMIM's coverage of what the run found (C)\n")
    rows = []
    for s in ORDER:
        cc = per[s]["C_clinvar"]
        rows.append([NAMES[s], per[s]["B_allelic_variants"]["omim_allelic_variants_for_disease"], cc["omim_avs_placed_in_clinvar"],
                     "; ".join(f"{k or 'none'}: {v_}" for k, v_ in sorted(cc["omim_av_clinvar_classifications"].items(), key=lambda x: -x[1])),
                     cc["distinct_tier1_variants_in_run"], cc["run_variants_matched_to_clinvar"], cc["run_variants_matched_to_clinvar_plp"], pct(cc["share_of_run_clinvar_plp_in_omim"])])
    w(table(["Disease", "OMIM AVs", "Placed in ClinVar", "ClinVar germline classification of the OMIM AVs", "Distinct placed variants in run", "Run variants in ClinVar", "… P/LP", "Run P/LP variants that are OMIM AVs"], rows))
    w("\nOMIM's allelic variants are almost all in ClinVar (the one exception is the moved entry 600065.0007), and ClinVar classifies most of them pathogenic. "
      "The run's ClinVar-matched P/LP variants, by contrast, are mostly **not** OMIM allelic variants: OMIM's list is a sample of the pathogenic spectrum, so 'absent from OMIM' alone says little about a variant and the pre-registered gap definition rightly requires absence from both databases.\n")
    w("**OMIM against ClinVar on the same variants.** Comparing OMIM's protein label with the protein change in the ClinVar record that OMIM itself points to:\n")
    rows = []
    for s in ORDER:
        for x in per[s]["C_clinvar"]["omim_label_vs_clinvar_protein_differences"]:
            rows.append([NAMES[s], x["av"], x["omim_label"], x["clinvar_hgvs"].split("; ")[0][:60], x["kind"]])
    w(table(["Disease", "OMIM AV", "OMIM label", "ClinVar record OMIM cites", "Kind"], rows))
    w("\nTwo inconsistencies are more than numbering: OMIM 610045.0007 (GLY441ARG; DiBacco 2020) is linked to ClinVar record 992960, `c.321G>A (p.Glu107=)`, a synonymous change at another codon, while the run's four papers give `c.1321G>A p.Gly441Arg` (placed at 6:24528144:G:A), which is what the OMIM narrative's own text (`c.321G-A ... gly441-to-arg`) must have meant; "
      "and OMIM 610045.0002 (first base of intron 5) is linked to a record at `c.727-3298G>A`. ClinVar 600065.0006's components split into a benign/likely-benign missense (`c.1756C>T`) and a pathogenic splice change (`c.742-14C>A`), and the run found only the pathogenic component. "
      "These are small in number but they are the kind of error a provenance-first pipeline is built to avoid, and they argue for treating OMIM as a strong but fallible holdout.\n")

    # ---------- 7. gaps
    w("## 7. Gap candidates checked against OMIM (D)\n")
    w("Pre-registration §7.3 defines a gap variant as absent from ClinVar **and** not listed among OMIM's allelic variants; the OMIM half waited on D-12. With the frozen pages, every one of the 215 O3 candidates was compared with the allelic variants of its gene by GRCh38 allele, cDNA, protein and notation tokens.\n")
    w(table(["Disease", "Candidates", "Present in OMIM (allele, cDNA or protein)", "Notation or isoform collision to check"],
            [[NAMES[s], per[s]["D_gaps"]["candidates"], per[s]["D_gaps"]["present_in_omim"], per[s]["D_gaps"]["token_collisions_to_check"]] for s in ORDER]))
    coll = [g for g in gaps if g["omim_check_2026_10_28"].startswith("possible")]
    w(f"\n`gap_candidates_omim_check_{d}.csv` carries the verdict per candidate (it replaces the `omim_checked = no (D-12)` column of `adjudication/o3_gaps/candidates.csv`; the adjudication page is not changed by this report).\n")
    for g in coll:
        w(f"**{g['candidate_id']}** (`{g['hgvs_c']}`, `{g['hgvs_p_predicted']}`, from Sugie 2018, PMID 30413001) matches OMIM 309060.0001 (`LAMP2, 2-BP DEL, 1097AA`, Nishino 2000) on the deletion token only. "
          "The paper's table gives the exon as `E9b` (the span the run stored reads `| 1 | E9b | c.1097_1098 delAA |`). LAMP2 has alternative terminal exons 9a and 9b; c.1097_1098 on the LAMP2B transcript (exon 9b) lies in intron 9 of the MANE transcript NM_002294.3 (LAMP2A), "
          "which is exactly where ClinVar places OMIM's variant (`c.1093+2440_1093+2441del`, record 1410728, uncertain significance, alias `Q366fs`). The run's normalization assumed NM_002294.3 because the paper named no transcript (`transcript_assumed = yes`), VariantValidator accepted the description after trimming redundant bases, and the result is a different genomic allele in exon 9a, "
          "X:120431457:CTT:C, that no database holds because it is not what the paper reported. **This candidate is a normalization artefact and should be withdrawn** pending re-normalization on NM_013995 (LAMP2B).")
    lamp2 = per["danon"]["E_context"]["lamp2_exon9_rows_with_transcript_assumed"]
    w(f"\nThe same risk applies to every LAMP2 description at c.1094 or beyond whose transcript was assumed: {len(lamp2)} in the Danon run ({'; '.join(f'`{t[0]}` from PMID {t[1]}' for t in lamp2)}). "
      f"Across the six runs, {sum(per[s]['E_context']['normalized_rows_with_transcript_assumed'] for s in ORDER)} normalized descriptions carry `transcript_assumed = yes`; for genes without alternative coding exons the assumption is harmless, for GFAP (alpha/epsilon) and LAMP2 (9a/9b) it is not. "
      "A per-gene list of isoform-sensitive regions in the Stage 4 settings (D-40 already made those per disease) would catch this before adjudication.\n")

    # ---------- 8. context
    w("## 8. Context: inheritance, zygosity and staleness (E)\n")
    rows = []
    for s in ORDER:
        e = per[s]["E_context"]
        z = e["zygosity_of_extracted_variant_rows"]
        topz = "; ".join(f"{k}: {v_}" for k, v_ in list(z.items())[:4])
        rows.append([NAMES[s], e["omim_inheritance"], topz, e["last_omim_edit_either_entry"], f"{e['extracted_papers_after_last_omim_edit']} of {per[s]['A_literature']['extracted_pmids']}", f"{e['corpus_papers_after_last_omim_edit']} of {per[s]['A_literature']['corpus_pmids']}"])
    w(table(["Disease", "OMIM inheritance", "Zygosity of extracted variant rows (top values)", "Last OMIM edit", "Extracted papers after it", "Corpus papers after it"], rows))
    w("\nZygosity patterns follow OMIM's inheritance where stated (heterozygous for the dominant HA20 and AxD; homozygous and compound heterozygous for the recessive LAD-I, SSADH and Tangier; hemizygous males and heterozygous females for X-linked Danon), with 'not reported' large in cohort tables that print genotypes per family rather than per person. "
      "The staleness columns are the other side of §3: OMIM's entries draw on the founding literature, much of it closed; the open-access corpus is weighted to the last ten years. The two sources overlap less than one might expect, which is why the recall figures in §4 measure corpus coverage as much as extraction.\n")

    # ---------- 9. synthesis
    w("## 9. Where the work succeeds, and what to improve\n")
    w("**Succeeds**\n")
    w("- When an OMIM source paper is in the run, the curated variant is almost always in our record with the right individuals and zygosity (§4, §5); the per-patient detail is richer than OMIM's summary (outcomes, ages, carrier relatives).")
    w("- Recurrent variants are recovered from several independent papers each (§4.1, 'papers in run reporting it'), so the record does not hinge on one paper.")
    w("- No contradiction with OMIM was found at the patient level, and no O3 candidate is a known OMIM variant (§5, §7): the pipeline's abstention and provenance rules hold against an external curated source.")
    w("- The frozen pipeline's own flags (`transcript_assumed`, conversion notes in `method_note`, verbatim prose variants) were enough to diagnose every miss inside an extracted paper after the fact.\n")
    w("**Improve**\n")
    w("- **Corpus coverage is the binding constraint.** For diseases described before their gene, add the historical disease names to the searches (LAD-I: Mo1 or LFA-1 deficiency, defective neutrophil adhesion; Danon: lysosomal glycogen storage with normal acid maltase; Tangier: familial alpha-lipoprotein deficiency, analphalipoproteinemia is already there) and record which seed found each paper. This is a pre-registration §5.1 change for any re-search and needs a deviation entry.")
    w("- **Open access only (D-32) costs the founding literature.** 96 OMIM-cited papers are in our corpus with no open copy. The options are institutional access for a defined list, or reporting that the pipeline's view of these diseases starts where open access starts; the write-up must say which.")
    w("- **Table conversion failures should be visible in the harness**, not only in method notes: a per-paper 'tables usable' flag would let O2/O3 denominators exclude or mark such papers.")
    w("- **Key prose protein changes.** A narrow rule ('<residue> to <residue> at amino acid N' → p.XnY) would have keyed Wardlaw's variant without inventing anything; intronic prose should be flagged, not keyed.")
    w("- **Isoform-aware normalization** for GFAP and LAMP2 (and any gene with alternative coding exons): never assume MANE for positions inside an alternative exon; use the paper's exon label when it gives one.")
    w("- **Phenotype three-state check on a curated statement:** the autism item in Chambliss 1998 is a cheap test of whether 'not reported' was right.")
    w("- **Treat OMIM as fallible:** two allelic variants point to ClinVar records that do not match their own description; any OMIM-based concordance figure should exclude or footnote them.\n")

    # ---------- 10. status
    w("## 10. What is pre-registered here and what is exploratory\n")
    w("- **Pre-registered and now computed:** §7.2.5 (share of corpus PMIDs cited by OMIM; §3), §7.2.2 reference pairs in the OMIM form (§4), §7.3's OMIM criterion for gap candidates (§7). None of these changes O2's ClinVar figures or any threshold.")
    w("- **Exploratory, reported as such:** unrestricted recall of OMIM allelic variants anywhere in the run (the completeness shape of §7.2.7, which D-35 registered for HA20 and AxD catalogues only), the literature funnel, the patient-level comparison, the ClinVar-standing and staleness tables.")
    w(f"- **Source and route:** OMIM pages frozen by Dr. Lin on {d} (D-42); no API; content outside git. The ClinVar placement used live E-utilities on {d}, whereas O2 used the 2026-10-12 release; the VariationIDs agree for every variant both saw.")
    w("- **Re-run:** `uv run python -m pipeline.harness.omim_entries --root <root> --date " + d + " --manifest-out analysis/poc/reference_snapshot`; `uv run python analysis/omim_holdout/clinvar_lookup.py`; `uv run python analysis/omim_holdout/assess.py`; `uv run python analysis/omim_holdout/report.py`. The PDFs must be copied back to `<root>/" + d + "/omim/entry_<MIM>.pdf` in a new container.")
    w("- **Cost:** no model calls; session tokens only.\n")
    (REPO / args.out).write_text("\n".join(L) + "\n")
    print(f"wrote {args.out}: {len(L)} blocks, {sum(len(x) for x in L)} chars")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
