"""Version 2 of the interim paper: the OMIM half (D-42) and the D-43 correction, as text and supplementary tables.

Every number comes from `data.load()` (the `omimh`, `isoform_cfg` and `danon_norm` keys, read from the
files named in SOURCES). The prose lives here.
"""
from __future__ import annotations

from collections import Counter, defaultdict

from .data import DISEASES, SHORT

NAMES = {"ha20": "A20 haploinsufficiency", "axd": "Alexander disease", "lad1": "LAD-I", "ssadh": "SSADH deficiency", "danon": "Danon disease", "tangier": "Tangier disease"}
STATUSES = ["extracted", "in corpus, no open full text", "not found by search", "excluded at title/abstract", "not in corpus (screened unclear/other)", "held out (bias arm)"]
PLACES = [("allelic-variant narrative", "allelic-variant narrative"), ("phenotype entry (clinical text, not an allelic variant)", "phenotype entry (clinical text)"), ("gene entry only", "gene entry only")]


def CI(r, nd=1):
    if not r or r.get("n") in (0, None):
        return "—"
    return f"{100 * r['share']:.{nd}f}% ({r['k']}/{r['n']}; 95% CI {100 * r['ci95'][0]:.{nd}f}–{100 * r['ci95'][1]:.{nd}f})"


def table(headers, rows_):
    out = ["| " + " | ".join(headers) + " |", "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows_:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


def lab(d):
    return SHORT[d] + ("\\*" if d == "ha20" else "")


def omim_av_cell(D, d):
    c = D["omimh"]["counts"][d]["allelic_variants"]
    n = c["titled_for_disease"] + len(c["titled_for_disease_qualified"])
    return f"{n} of {c['listed']} listed ({D['omimh']['counts'][d]['gene_mim']})"


def omim_line(D, d):
    """One per-disease results line for §3.12."""
    p = D["omimh"]["per"][d]
    b, a, c = p["B_allelic_variants"], p["A_literature"], p["C_clinvar"]
    live = D["omimh"]["gap_live"][d]
    extra = ""
    if d == "danon":
        extra = (f" G-danon-001 was withdrawn (D-43: reported on LAMP2 exon 9b, normalized on the MANE transcript); the re-normalized run has "
                 f"{D['danon_norm']['status_counts'].get('isoform_ambiguous', 0)} isoform-ambiguous description and {D['danon_norm'].get('transcript_isoform_from_label', 0)} placed by the paper's exon label.")
    return (f"- **OMIM (D-42):** {b['recall_unrestricted_strict']['k']} of {b['omim_allelic_variants_for_disease']} allelic variants recovered ({CI(b['recall_unrestricted_strict'])}); "
            f"{a['av_source_pmids_extracted']} of {a['av_source_pmids']} papers OMIM cites for them were extracted; {c['run_clinvar_plp_variants_that_are_omim_avs']} of the run's {c['run_variants_matched_to_clinvar_plp']} ClinVar P/LP variants are OMIM allelic variants; "
            f"{live} live gap candidates, all absent from OMIM's allelic variants.{extra}")


def results_omim(D):
    om = D["omimh"]
    per, tot, cnt = om["per"], om["totals"], om["counts"]
    # Table: the pages
    pages = []
    for d in DISEASES:
        c = cnt[d]
        av = c["allelic_variants"]
        n_dis = av["titled_for_disease"] + len(av["titled_for_disease_qualified"])
        pages.append([lab(d), f"{c['phenotype_mim']} / {c['gene_mim']}", f"{c['phenotype_entry']['last_edit']} / {c['gene_entry']['last_edit']}",
                      f"{c['phenotype_entry']['references']} / {c['gene_entry']['references']}", av["listed"], n_dis,
                      "; ".join(f"{k}: {v}" for k, v in av["other_titles"].items()) or "—", per[d]["C_clinvar"]["omim_avs_placed_in_clinvar"]])
    # Table: recall
    rec = []
    for d in DISEASES:
        b, a = per[d]["B_allelic_variants"], per[d]["A_literature"]
        lv = b["by_recovery_level"]
        pr = b["reference_pairs_7_2_2_omim_form"]
        rec.append([lab(d), b["omim_allelic_variants_for_disease"], lv.get("tier1", 0), lv.get("tier2_protein", 0), lv.get("fuzzy_token", 0), lv.get("not recovered", 0),
                    CI(b["recall_unrestricted_strict"]), f"{b['restricted_denominator_source_paper_extracted']}: {CI(b['recall_restricted_in_source_paper_strict'])}",
                    f"{pr['pairs']}: {CI(pr['recall_tier12'])}", f"{a['av_source_pmids_extracted']} of {a['av_source_pmids']}", CI(a["share_of_corpus_cited_by_omim_7_2_5"])])
    rec.append(["**All six**", tot["omim_allelic_variants_for_diseases"], sum(r[2] for r in rec), sum(r[3] for r in rec), sum(r[4] for r in rec), sum(r[5] for r in rec),
                f"**{CI(tot['recall_all_strict'])}**", "", "", f"{sum(per[d]['A_literature']['av_source_pmids_extracted'] for d in DISEASES)} of {sum(per[d]['A_literature']['av_source_pmids'] for d in DISEASES)}", ""])
    # pooled funnel by place
    pooled = defaultdict(Counter)
    for d in DISEASES:
        for pl, c in per[d]["A_literature"]["funnel_by_citation_place"].items():
            for st, n in c.items():
                pooled[pl][st] += n
    funnel = [[short, sum(pooled[pl].values())] + [pooled[pl].get(st, 0) for st in STATUSES] for pl, short in PLACES]
    # ClinVar standing of OMIM's variants
    standing = []
    for d in DISEASES:
        c = per[d]["C_clinvar"]
        cls = c["omim_av_clinvar_classifications"]
        plp = sum(v for k, v in cls.items() if k and all(x.strip() in ("Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic") for x in k.split(";")))
        standing.append([lab(d), per[d]["B_allelic_variants"]["omim_allelic_variants_for_disease"], c["omim_avs_placed_in_clinvar"], plp,
                         "; ".join(f"{k or 'none'}: {v}" for k, v in sorted(cls.items(), key=lambda x: -x[1]) if not (k and all(x.strip() in ("Pathogenic", "Likely pathogenic", "Pathogenic/Likely pathogenic") for x in k.split(";")))) or "—",
                         c["distinct_tier1_variants_in_run"], c["run_variants_matched_to_clinvar_plp"], CI(c["share_of_run_clinvar_plp_in_omim"]),
                         f"{per[d]['E_context']['extracted_papers_after_last_omim_edit']} of {per[d]['A_literature']['extracted_pmids']} (last edit {per[d]['E_context']['last_omim_edit_either_entry']})"])
    diffs = [[lab(d), x["av"], x["omim_label"], x["clinvar_hgvs"].split("; ")[0][:60], x["kind"]] for d in DISEASES for x in per[d]["C_clinvar"]["omim_label_vs_clinvar_protein_differences"]]
    misses = [[lab(d), m["av"], m["omim_label"], m["miss_category"]] for d in DISEASES for m in per[d]["B_allelic_variants"]["misses"]]
    jt = om["judg_tally"]
    src_all = sum(per[d]["A_literature"]["av_source_pmids"] for d in DISEASES)
    src_ex = sum(per[d]["A_literature"]["av_source_pmids_extracted"] for d in DISEASES)
    restricted_n = sum(per[d]["B_allelic_variants"]["restricted_denominator_source_paper_extracted"] for d in DISEASES)
    restricted_k = sum(per[d]["B_allelic_variants"]["recall_restricted_in_source_paper_strict"]["k"] for d in DISEASES)
    fa = tot["funnel_all_diseases"]
    dn = D["danon_norm"]
    iso = {d: D["isoform_cfg"][d][0] for d in DISEASES if D["isoform_cfg"][d]}
    n_listed = sum(cnt[d]["allelic_variants"]["listed"] for d in DISEASES)
    n_other = sum(sum(cnt[d]["allelic_variants"]["other_titles"].values()) for d in DISEASES)
    return f"""### 3.7b The OMIM half: OMIM as a human-curated holdout (D-42; added in version 2)

**What OMIM provides.** Dr. Lin printed the six phenotype entries and the six gene entries from omim.org to PDF on {om['date']} and uploaded them; omim.org refuses automated reads from the cloud environment and no API key is in place (D-12), so these pages are the OMIM reference (D-42). A harness script parses each page (titles, cross-references, the phenotype–gene table, the allelic variants with OMIM's legacy labels, dbSNP and ClinVar accessions and the papers each narrative cites, the references, the edit dates); the content stays outside the repository and only a manifest with checksums and counts is committed, because OMIM's terms restrict redistribution. The gene entries list {n_listed} allelic variants, of which {tot['omim_allelic_variants_for_diseases']} are titled for the six diseases ({n_other} for other phenotypes or reclassified, 1 moved). OMIM calls these "selected examples": a curated sample of the literature, not a catalogue. So recall of OMIM's variants is the meaningful direction, "precision against OMIM" is not, and the gap definition's OMIM clause is one-sided. The phenotype entries carry no allelic-variant table and no clinical synopsis (that is a separate page, not frozen), so OMIM's phenotype half is still unassessed.

**Table 8b. The frozen OMIM pages.** Source: `analysis/poc/reference_snapshot/2026-10-28/omim_counts.json`.

{table(["Disease", "Phenotype / gene MIM", "Last edit (phenotype / gene)", "References (phenotype / gene)", "Allelic variants listed", "Titled for the disease", "Other titles", "Placed in ClinVar"], pages)}

**Matching.** Each allelic variant was placed in ClinVar through ClinVar's own OMIM cross-reference or the RCV accessions OMIM prints (queried through E-utilities on {om['date']}; dbSNP ids alone were not used, because one rs number covers every allele at a position). ClinVar's title then gives current HGVS, and the run's variants were matched, in order, by the ClinVar VariationID the O2 harness had assigned, the GRCh38 allele, the cDNA on the same transcript, the protein change, and (reported apart) a notation-tolerant token. OMIM's own labels use legacy protein numbering (ABCA1 labels sit 60 residues below the current transcript; LAMP2 LEU113TER is p.Leu147Ter), so matching through ClinVar's HGVS rather than the label was necessary.

**Table 8c. Recall of OMIM's allelic variants, by disease.** Tier 1 = genomic allele or cDNA; tier 2 = protein change only; token = notation-level only (not counted as recovered). "Source paper in run" is the completeness shape of §7.2.7, restricted to allelic variants whose OMIM source paper was extracted. The §7.2.2 column uses OMIM's allelic-variant citations as reference pairs (a PMID in the run × an allelic variant OMIM cites to it); its denominators are small because so few of OMIM's source papers are open access. Wilson 95% intervals. Source: `analysis/omim_holdout/results_2026-10-28.json`.

{table(["Disease", "OMIM allelic variants", "Tier 1", "Tier 2", "Token", "Not recovered", "Recall anywhere in the run (tiers 1+2)", "Source paper in run: recovered from it", "§7.2.2 OMIM-form pairs: recall", "OMIM source papers extracted", "Corpus PMIDs cited by OMIM (§7.2.5)"], rec)}

![Figure 11. OMIM as a holdout.]({D['figs']['fig11']})

**Figure 11.** OMIM as a holdout. **A** Allelic variants recovered anywhere in the run. **B** Where the papers OMIM cites for its allelic variants stand in our corpus funnel. **C** The share of the run's ClinVar P/LP variants that OMIM lists, which shows how selective OMIM's list is.

- **Recall is {CI(tot['recall_all_strict'])} overall**, from {CI(per['lad1']['B_allelic_variants']['recall_unrestricted_strict'])} (LAD-I) and {CI(per['ha20']['B_allelic_variants']['recall_unrestricted_strict'])} (HA20) to {CI(per['tangier']['B_allelic_variants']['recall_unrestricted_strict'])} (Tangier), whose allelic variants come from the 1999–2003 gene-discovery papers, all in the corpus and all closed.
- **Literature coverage, not reading, is the binding constraint.** Of the {src_all} papers OMIM cites as sources for these variants, {src_ex} were extracted; pooled over every OMIM-cited paper ({tot['omim_cited_papers_distinct_all_diseases']}), {fa.get('in corpus, no open full text', 0)} sit in the screened corpus with no open copy (D-32), {fa.get('not found by search', 0)} were never returned by the searches, and {fa.get('extracted', 0)} were extracted. The never-returned papers are mostly pre-1990 descriptions under earlier disease names (LAD-I as Mo1 or LFA-1 deficiency, Danon disease as lysosomal glycogen storage with normal acid maltase, Tangier disease as familial alpha-lipoprotein deficiency) and gene-biology papers outside the corpus's scope: a search-term gap for diseases described before their gene (§5, G18).

**Table 8d. OMIM-cited papers in our corpus funnel, pooled over the six diseases, by where OMIM cites the paper.** Source: `analysis/omim_holdout/omim_cited_papers_2026-10-28.csv`.

{table(["Cited in", "Total"] + STATUSES, funnel)}

- **Where the source paper was extracted, the variant was usually there:** {restricted_k} of {restricted_n} allelic variants whose OMIM source paper is in the run were recovered from that paper. The misses have named causes: Akaboshi 2003's Table 2 was scrambled in PDF conversion (three SSADH variants, each recovered from five other papers), and two papers state their variant only in prose ("a glycine to an arginine at amino acid 169"; "G-to-T transversion at the first base of intron 9"), which the run keeps verbatim with the right individuals and zygosity but cannot key (Table 8e).
- **Patient level.** For the {om['judg_papers']} papers both OMIM and the run cover, each OMIM statement (individuals, sex, zygosity, inheritance, variant, features, outcomes) was compared by hand with our per-paper records (Supplementary Table S18; judged by Claude, not a panel member): {jt.get('agree', 0)} agree, {jt.get('partial', 0)} partial, {jt.get('missed in source paper', 0) + jt.get('missed (major under-capture)', 0)} missed (all the Akaboshi table), and no record contradicts OMIM. Where they differ, the run usually has less (a supplement not in the extraction text: Zhou 2016's sex, onset and de novo status) rather than something wrong; one OMIM phenotype statement (mild autism in Chambliss 1998) is "not reported" in our rows and should be checked against the paper (G19).

**Table 8e. Allelic variants not recovered, by cause.** Source: `av_recall_2026-10-28.csv`.

{table(["Disease", "OMIM AV", "OMIM label", "Cause"], misses)}

- **OMIM's variants in ClinVar, and OMIM's coverage of what the run found (Table 8f).** All but one OMIM allelic variant (the moved entry 600065.0007) has a ClinVar record, and ClinVar calls most pathogenic. The run's ClinVar-matched P/LP variants are mostly *not* OMIM allelic variants ({sum(per[d]['C_clinvar']['run_clinvar_plp_variants_that_are_omim_avs'] for d in DISEASES)} of {sum(per[d]['C_clinvar']['run_variants_matched_to_clinvar_plp'] for d in DISEASES)}), and the run holds {sum(per[d]['C_clinvar']['distinct_tier1_variants_in_run'] for d in DISEASES)} distinct genome-placed variants against OMIM's {tot['omim_allelic_variants_for_diseases']} selected examples. {sum(per[d]['E_context']['extracted_papers_after_last_omim_edit'] for d in DISEASES)} of the {sum(per[d]['A_literature']['extracted_pmids'] for d in DISEASES)} extracted papers post-date the last edit of either OMIM entry for their disease.
- **OMIM is fallible too.** Two allelic variants point to ClinVar records that do not match their own text: 610045.0007 (GLY441ARG) is linked to a synonymous change at another codon (`c.321G>A p.Glu107=`), while the run's four papers give `c.1321G>A p.Gly441Arg`; 610045.0002 (first base of intron 5) is linked to a deep-intronic record. {len(diffs)} labels differ from ClinVar's protein change, {sum(1 for x in diffs if x[4].startswith('numbering'))} by legacy numbering only. The complex LAD-I allele 600065.0006 has a component ClinVar calls benign. A holdout curated by people needs the same provenance checks as our output.

**Table 8f. OMIM's allelic variants in ClinVar; OMIM's coverage of the run's ClinVar P/LP variants.** Source: `results_2026-10-28.json`, `omim_av_clinvar.csv`.

{table(["Disease", "OMIM AVs", "In ClinVar", "…ClinVar P/LP", "Other ClinVar classes", "Distinct placed variants in run", "Run variants ClinVar P/LP", "…that are OMIM AVs", "Extracted papers after OMIM's last edit"], standing)}

- **Gap candidates against OMIM (§7.3's second clause).** Every one of the {D['totals']['all']['gap_candidates']} O3 candidates was compared with its gene's allelic variants by allele, cDNA, protein and notation token: {om['gap_omim_absent']} are absent from OMIM. One, **G-danon-001** (`NM_002294.3:c.1097_1098del`, Sugie 2018), collided with OMIM 309060.0001 by its deletion token only. The paper's table places the deletion on exon 9b (`E9b`), the LAMP2B isoform; LAMP2 has alternative terminal exons 9a, 9b and 9c, and the run had assumed the MANE transcript (exon 9a) because the paper named none, producing a genomic allele no database holds because it is not what the paper reported. On the right transcript the description is OMIM 309060.0001 / ClinVar 1410728. **It is a normalization artefact, not a gap, and was withdrawn (D-43).**
- **D-43, carried out the same day** (deviation entry in `DECISIONS.md`): a new module computes from the RefSeq mRNA records where each gene's coding isoforms diverge (LAMP2 c.{iso['danon']['from_cdna']}; GFAP c.{iso['axd']['from_cdna']}, exon 7A) and writes it into the Stage 4 settings; normalization now lets the paper's own words choose the transcript at such positions ("E9b", "LAMP2B", "epsilon") and otherwise assigns no genomic key (`isoform_ambiguous`). The Danon run was re-normalized: exactly 2 of {dn['distinct_descriptions']} descriptions changed (the withdrawn one moved to NM_013995.2 and ClinVar's allele; a review's `c.1150G>C`, stated without a transcript, became `isoform_ambiguous`) and the phenopackets were rebuilt with the pinned ontology releases (505, all valid; 5 records differ in content). GFAP's one isoform case (Melchionda 2013) had already failed normalization safely with a reference mismatch. O2 and O3 were not re-run on a fresh ClinVar snapshot: the withdrawn variant is in ClinVar either way, and the other candidates' standing rests on the registered release.
- **OMIM allelic-variant candidates** (a deliverable) now have their reference: an approved gap variant is by construction absent from OMIM's list, and the submission route to OMIM is still to be settled with OMIM (G2)."""


def supplement_omim(D):
    om = D["omimh"]
    S = []
    # S15 per-AV
    rows_ = []
    for r in om["av"]:
        rows_.append([NAMES[r["disease"]], r["av"], r["omim_label"].split(", ", 1)[-1] if ", " in r["omim_label"] else r["omim_label"],
                      (r["clinvar_hgvs"].split("; ")[0].split("(")[-1].rstrip(")") if r["clinvar_hgvs"] else "—")[:40], r["recovery_level"].replace("_", " "),
                      len(r["found_in_pmids"].split()) if r["found_in_pmids"] else 0,
                      "yes" if r["found_in_source_paper"] == "True" else ("extracted, not found there" if r["source_extracted"] == "True" else "not in run"),
                      r["omim_vs_clinvar_protein"]])
    S += ["## Supplementary Table S15. Every OMIM allelic variant titled for the six diseases (D-42)", "",
          "Recovery levels: tier1 = genomic allele or cDNA; tier2 protein = protein change only; fuzzy token = notation-level only (not counted as recovered). Source: `analysis/omim_holdout/av_recall_2026-10-28.csv`.", "",
          table(["Disease", "OMIM AV", "OMIM label", "ClinVar HGVS (current)", "Recovery", "Papers in run reporting it", "From OMIM's source paper", "OMIM label vs ClinVar protein"], rows_), ""]
    # S16 cited papers funnel per disease and place
    per = om["per"]
    rows_ = []
    for d in DISEASES:
        for pl, short in PLACES:
            c = per[d]["A_literature"]["funnel_by_citation_place"].get(pl, {})
            if c:
                rows_.append([NAMES[d], short, sum(c.values())] + [c.get(st, 0) for st in STATUSES])
    S += ["## Supplementary Table S16. OMIM-cited papers in the corpus funnel, by disease and citation place", "",
          "Per-PMID rows with manifest fields are in `analysis/omim_holdout/omim_cited_papers_2026-10-28.csv`.", "",
          table(["Disease", "Cited in", "Total"] + STATUSES, rows_), ""]
    # S17 gap check summary (per disease)
    rows_ = [[NAMES[d], per[d]["D_gaps"]["candidates"], om["gap_live"][d], per[d]["D_gaps"]["present_in_omim"], per[d]["D_gaps"]["token_collisions_to_check"]] for d in DISEASES]
    S += ["## Supplementary Table S17. Gap candidates checked against OMIM's allelic variants (2026-10-28)", "",
          "Per-candidate verdicts are in `analysis/omim_holdout/gap_candidates_omim_check_2026-10-28.csv` and in the `omim_checked` and `status` columns of `adjudication/o3_gaps/candidates.csv`.", "",
          table(["Disease", "Candidates (O3, 2026-10-21)", "Live after D-43", "Present in OMIM (allele, cDNA or protein)", "Notation or isoform collision"], rows_), ""]
    # S18 patient-level judgements
    rows_ = [[r["scope"], NAMES[r["disease"]], r["av"] or "—", f"{r['paper']} ({r['pmid']})", r["omim_statement"], r["our_record"], f"**{r['agreement']}**", r["note"]] for r in om["judg"]]
    S += ["## Supplementary Table S18. Patient-level comparison with OMIM's curated statements on the papers both cover", "",
          f"Judged by Claude in the session of {om['date']} from the per-paper records; the OMIM side is paraphrased to identifiers and facts. 'agree' = every fact OMIM states is in our record with the same value; 'partial' = the variant and individuals agree but something OMIM states is missing from ours. Source: `analysis/omim_holdout/patient_level_judgements.csv`.", "",
          table(["Scope", "Disease", "OMIM AV", "Paper", "OMIM states", "Our record", "Agreement", "Note"], rows_), ""]
    return "\n".join(S)
