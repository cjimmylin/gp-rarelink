# -*- coding: utf-8 -*-
"""Build the per-paper extraction JSON for PMID 33101300 (GP-RareLink, extract_v6).

All values come from my reading of the paper. Table row lines are copied from the
paper Markdown itself (leading/trailing whitespace stripped) so that every span is
verbatim.
"""
import json, os, re

PAPER = "/home/user/gp-rarelink/data/literature/ha20/fulltext_md/33101300.md"
OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/33101300.json"
SCRATCH = "/tmp/openweight_scratch/ow-ha20/33101300"

text = open(PAPER, encoding="utf-8").read()
lines = text.split("\n")
def raw(n): return lines[n-1]
def st(n): return lines[n-1].strip()

PMID = "33101300"
PMID_SPAN = "PMID: 33101300"

FAM = {
 1:  ("(1)",    237, "p. Cys243Tyr"),
 2:  ("(2)",    249, "p. Trp85Glyfs*11"),
 3:  ("(2)",    255, "p. His636Glufs*55"),
 4:  ("(2)",    259, "p. Gln737Serfs*79"),
 5:  ("(2)",    279, "p. Phe637Glufs*2"),
 6:  ("(2)",    285, "p. Cys243Tyr"),
 7:  ("(2)",    302, "p. Asn449Thrfs*28"),
 8:  ("(2)",    314, "p. Ala588Valfs*80"),
 9:  ("(2; 3)", 322, "p. Lys417Serfs*4"),
 10: ("(2)",    328, "p. Arg45*"),
 11: ("(4)",    330, "p. Leu227*"),
 12: ("(4)",    348, "p. Phe224Serfs*4"),
 13: ("(4)",    377, "p. Arg271*"),
 14: ("(4)",    381, "p. Thr604Argfs*93"),
 15: ("(4)",    383, "p. Tyr306*"),
 16: ("(4)",    395, "p. Pro268Leufs*19"),
 17: ("(4)",    401, "p. Gln338*"),
 18: ("(5)",    419, "p. Trp85Glyfs*11"),
 19: ("(6)",    428, "p. Val489Alafs*7"),
 20: ("(7)",    436, "p. His636Terfs*1"),
 21: ("(8)",    444, "p. Glu332*"),
 22: ("(9)",    452, "p. Lys91*"),
 23: ("(10)",   470, "p. Gln370Argfs*16"),
 24: ("(10)",   472, "p. Arg439Glnfs*6"),
 25: ("(10)",   484, "p. Trp85*"),
 26: ("(11)",   495, "p. Gln187*"),
 27: ("(11)",   507, "p. Arg 87*"),
 28: ("(12)",   513, "p. Cys478*"),
 29: ("(13)",   517, "p. Asn102Ser"),
 30: ("(14)",   529, "p. Arg183*"),
 33: ("(15)",   535, "p. Lys91*"),
 34: ("(16)",   566, "Deletion of exons " + st(568)),
 35: ("(17)",   570, "p. Arg271*"),
 36: ("(17)",   584, "p. Arg45*"),
 37: ("(18)",   590, "p. Lys303fs"),
 38: ("(19)",   592, "p. Arg271*"),
 39: ("(19)",   598, "p. Asn98Thrfs25"),
 40: ("(20)",   608, "p. Cys200Alafs*16"),
 41: ("(21)",   614, "p. Met476Ile"),
}

# n, family, primary line, continuation lines, [(feature as stated, hpo label)], treatment
PATIENTS = [
 (1,  1,  237, [239], [("Nephrotic syndrome","Nephrotic syndrome")], "Steroids, cyclosporine, MZB, colchicine, PSL"),
 (2,  1,  241, [], [], "PSL, steroids"),
 (3,  1,  243, [], [], "Glucocorticoids"),
 (4,  1,  245, [], [], "Colchicine"),
 (5,  1,  247, [], [], None),
 (6,  2,  249, [251], [], "Adalimumab, PSL, MTX, NSAID, Igratimod"),
 (7,  2,  253, [], [], "PSL"),
 (8,  3,  255, [257], [("Aortic valve insufficiency",None)], "Infliximab, MTX, PSL, NSAIDs, colchicine"),
 (9,  4,  259, [], [("BCG dermatitis",None)], "Etanercept"),
 (10, 4,  261, [], [], "Levothyroxine"),
 (11, 4,  263, [], [("Recurrent stomatitis","Recurrent oral ulcers"),("HD","Hashimoto thyroiditis")], "Levothyroxine"),
 (12, 4,  265, [267], [("HL","Hodgkin lymphoma"),("craniopharyngioma","Craniopharyngioma")], "Levothyroxine"),
 (13, 4,  269, [], [], None),
 (14, 4,  273, [275,277], [("BCG dermatitis",None),("aseptic meningitis","Aseptic meningitis")], "Colchicine"),
 (15, 5,  279, [], [("PFAPA","Periodic fever")], "PSL, MTX, cimetidine"),
 (16, 5,  281, [283], [], None),
 (17, 6,  285, [287], [("Nephrotic syndrome","Nephrotic syndrome")], "MZB, cyclosporine A, PSL, rituximab"),
 (18, 6,  289, [], [], "PSL"),
 (19, 6,  291, [], [], "PSL"),
 (20, 6,  298, [], [], "PSL"),
 (21, 6,  300, [], [], None),
 (22, 7,  302, [304,306], [("Pervasive developmental disorder",None),("infectious mononucleosis","Infectious mononucleosis")], "Acetaminophen during fever"),
 (23, 7,  310, [312], [("Pneumocystis carinii pneumonia","Pneumocystis jirovecii pneumonia")], "Adalimumab or infliximab"),
 (24, 8,  314, [], [], "Colchicine, infliximab"),
 (25, 8,  316, [318,320], [], "No anti-inflammatory treatment"),
 (26, 9,  322, [324,326], [("Autoimmune hepatitis","Autoimmune hepatitis")], "Adalimumab"),
 (27, 10, 328, [], [("Pharyngitis","Pharyngitis")], "Colchicine, PSL"),
 (28, 11, 330, [332,334,336], [("Premature ovarian failure","Premature ovarian insufficiency"),("geographic tongue","Geographic tongue"),("small jaw",None),("tonsillitis","Tonsillitis")], "MTX, thalidomide"),
 (29, 11, 338, [340,342,344], [("Geographic tongue","Geographic tongue"),("dental crowding secondary to small jaw",None)], "Infliximab"),
 (30, 11, 346, [], [("Goiter","Goiter")], "Colchicine"),
 (31, 12, 348, [350,352,354], [("CNS vasculitis","Central nervous system vasculitis"),("idiopathic thrombocytopenic purpura","Immune thrombocytopenia")], "Anakinra, AZA, systemic corticosteroids"),
 (32, 12, 361, [363], [("Membranous nephropathy","Membranous nephropathy")], "Anakinra"),
 (33, 12, 365, [367,369,371], [("Lymphadenopathy","Lymphadenopathy"),("periodontal disease","Periodontitis"),("intermittent arterial hypertension","Hypertension")], "Anakinra"),
 (34, 12, 373, [375], [("Asthma","Asthma"),("enamel loss",None),("uterine fibroids","Uterine leiomyoma")], "Anakinra"),
 (35, 13, 377, [], [], "Colchicine"),
 (36, 13, 379, [], [], None),
 (37, 14, 381, [], [("Lymphadenopathy","Lymphadenopathy")], "Tofacitinib"),
 (38, 15, 383, [385,387], [("Otitis media","Otitis media"),("recurrent urinary tract infections","Recurrent urinary tract infections")], "Infliximab"),
 (39, 15, 389, [391,393], [("Dysmenorrhea","Dysmenorrhea"),("rectal bleeding",None),("asthmatic bronchitis",None),("rosacea","Rosacea")], "Colchicine, AZA, infliximab"),
 (40, 16, 395, [], [], "Colchicine"),
 (41, 16, 397, [], [], "Colchicine"),
 (42, 16, 399, [], [], "Colchicine"),
 (43, 17, 401, [403,405,407,409,411,413,415,417], [("Pulmonary embolism","Pulmonary embolism"),("CNS vasculitis","Central nervous system vasculitis"),("inflammatory fibroepithelial polyp",None)], "Systemic corticosteroids, mesalamine, dapsone, MTX, AZA, colchicine, infliximab, adalimumab, certolizumab, anakinra, canakinumab, tacrolimus, tocilizumab ineffective"),
 (44, 18, 419, [], [], "Adalimumab, PSL"),
 (45, 18, 421, [], [], "PSL"),
 (46, 19, 428, [430,432,434], [("insulin-dependent diabetes","Type 1 diabetes mellitus"),("cytopenia","Cytopenia"),("hepatitis",None),("interstitial lung disease","Interstitial lung disease")], "PSL, sirolimus, tacrolimus, infliximab or rituximab, hematopoietic stem cell transplantation"),
 (47, 20, 436, [], [("Abdominal pain","Abdominal pain")], "Tocilizumab"),
 (48, 20, 438, [], [], "Colchicine"),
 (49, 20, 440, [], [("Abdominal pain","Abdominal pain")], "Tocilizumab"),
 (50, 20, 442, [], [("vomit","Vomiting")], None),
 (51, 21, 444, [446], [("Thrombophlebitis","Thrombophlebitis"),("fatigue","Fatigue")], "Etanercept, colchicine"),
 (52, 21, 448, [], [("Vitiligo","Vitiligo")], "Colchicine"),
 (53, 21, 450, [], [], "Colchicine, mesalazine"),
 (54, 22, 452, [], [("Liver failure",None)], None),
 (55, 22, 454, [456,458,460,462,464], [("Atrophic gastritis","Atrophic gastritis"),("anemia",None),("autoinflammatory pulmonary reaction",None),("repeated genital HSV infections","Recurrent genital herpes")], None),
 (56, 22, 466, [], [], None),
 (57, 22, 468, [], [], None),
 (58, 23, 470, [], [("hepatitis",None)], "Thalidomide"),
 (59, 24, 472, [474,476,478,480,482], [("Liver lesions and splenomegaly",None)], "Mesalazine, MTX, systemic corticosteroids, infliximab, and recombinant human TNF-II"),
 (60, 25, 484, [486,488], [], "Mesalazine, systemic corticosteroids and thalidomide"),
 (61, 26, 495, [497,499,501], [("Hepatomegaly","Hepatomegaly"),("ascites","Ascites"),("pericardial effusion","Pericardial effusion"),("nephritis","Nephritis")], "Etanercept, hydroxychloroquine, PSL, mycophenolate mofetil"),
 (62, 26, 503, [], [], "Etanercept, etiasa, MTX"),
 (63, 26, 505, [], [("Anal fistula","Anal fistula")], None),
 (64, 27, 507, [509,511], [("Interstitial lung disease","Interstitial lung disease")], "Etanercept, PSL"),
 (65, 28, 513, [], [("Lymphadenopathy","Lymphadenopathy")], "PSL, colchicine"),
 (66, 28, 515, [], [("Lymphadenopathy","Lymphadenopathy")], "PSL, colchicine"),
 (67, 29, 517, [519], [], "Glucocorticoid and thalidomide"),
 (68, 29, 521, [523], [], "No anti-inflammatory treatment"),
 (69, 29, 525, [527], [], "No anti-inflammatory treatment"),
 (70, 30, 529, [], [], None),
 (71, 30, 531, [], [], None),
 (72, 30, 533, [], [], None),
 (73, 33, 535, [537], [("Hepatitis",None),("atrophic gastritis","Atrophic gastritis"),("anemia",None)], "Thyroid replacement therapy"),
 (74, 33, 539, [541,543,545,547], [("Atrophic gastritis","Atrophic gastritis"),("anemia",None),("Hepatosteatosis","Hepatic steatosis")], "Thyroid replacement therapy, etanercept, corticosteroids, econazole, mycophenolate, PSL"),
 (75, 33, 549, [551,553], [("Growth delay","Growth delay"),("atrophic gastritis","Atrophic gastritis"),("anemia",None)], "Thyroid replacement therapy"),
 (76, 33, 560, [562,564], [("Growth delay","Growth delay"),("cow's milk allergy",None)], "Thyroid replacement therapy, golimumab, AZA"),
 (77, 34, 566, [568], [], "Adalimumab, MTX"),
 (78, 35, 570, [572,574], [], "Levothyroxine, hydroxychloroquine, thalidomide"),
 (79, 35, 576, [578,580,582], [], None),
 (80, 36, 584, [586], [], "PSL, infliximab, sulfasalazine"),
 (81, 36, 588, [], [], "PSL, cyclosporine"),
 (82, 37, 590, [], [], "Hydroxychloroquine"),
 (83, 38, 592, [594,596], [("Lupus nephritis","Lupus nephritis")], "PSL, mesalazine, recombinant human TNF-II"),
 (84, 39, 598, [600,602,604,606], [], "Hydroxychloroquine, AZA, mycophenolate mofetil ineffective, considering IL-1 blocking therapy"),
 (85, 40, 608, [], [], "No treatment"),
 (86, 40, 610, [], [("Septicemia","Sepsis")], "PSL"),
 (87, 40, 612, [], [("Abdominal pain","Abdominal pain")], None),
 (88, 41, 614, [616], [("Lymphadenopathy","Lymphadenopathy"),("constipation","Constipation")], None),
 (89, 41, 618, [], [], "PSL, acyclovir"),
]

def parse_row(lineno, n):
    toks = raw(lineno).split()
    for i, t in enumerate(toks):
        if t != str(n):
            continue
        j = i + 1
        if j >= len(toks):
            continue
        aos = ""
        if toks[j] in ("M", "F"):
            sex = toks[j]; j += 1
        else:
            aos = toks[j]; j += 1
            if j >= len(toks) or toks[j] not in ("M", "F"):
                continue
            sex = toks[j]; j += 1
        syms = toks[j:j+10]
        if len(syms) == 10 and all(s in ("+", "-") for s in syms):
            return aos, sex, syms
    return None

COLS = ["RF","Oral","Genital","Ocular","Skin","Vasc","GI","MSD","AITD","RRTI"]
COL_FEATURE = {
 "RF":     ("recurrent fever", "Recurrent fever", "recurrent fever"),
 "Oral":   ("oral ulcers", "Oral ulcer", "oral ulcers"),
 "Genital":("genital ulcers", "Genital ulcer", "genital ulcers"),
 "Ocular": ("ocular involvement", "Uveitis", "uveitis or other ocular inflammation"),
 "Skin":   ("skin lesion", "Skin rash", "skin lesions (rash, folliculitis, erythema nodosum)"),
 "Vasc":   ("vasculitis", "Vasculitis", "vasculitis"),
 "GI":     ("gastrointestinal ulcers", "Gastrointestinal ulcer", "gastrointestinal ulcers or inflammation"),
 "MSD":    ("musculoskeletal disorders", "Arthralgia", "arthritis or arthralgia"),
 "AITD":   ("autoimmune thyroid disorder", "Autoimmune thyroiditis", "autoimmune thyroiditis"),
 "RRTI":   ("recurrent respiratory tract infection", "Recurrent respiratory infections", "recurrent infections"),
}

CHECKLIST = [
 "oral ulcers",
 "genital ulcers",
 "gastrointestinal ulcers or inflammation",
 "recurrent fever",
 "arthritis or arthralgia",
 "uveitis or other ocular inflammation",
 "skin lesions (rash, folliculitis, erythema nodosum)",
 "autoimmune thyroiditis",
 "type 1 diabetes",
 "autoimmune hepatitis",
 "cytopenia (autoimmune)",
 "lymphoproliferation or lymphadenopathy",
 "central nervous system involvement",
 "recurrent infections",
 "elevated inflammatory markers (CRP/ESR)",
 "autoantibodies (ANA/other)",
 "growth failure",
 "pericarditis or other serositis",
 "interstitial lung disease",
 "vasculitis",
]

# feature text in the Other-manifestations column -> checklist items it evidences
OTHER_TO_CHECKLIST = {
 "Autoimmune hepatitis": ["autoimmune hepatitis"],
 "CNS vasculitis": ["central nervous system involvement"],
 "aseptic meningitis": ["central nervous system involvement"],
 "idiopathic thrombocytopenic purpura": ["cytopenia (autoimmune)"],
 "cytopenia": ["cytopenia (autoimmune)"],
 "Lymphadenopathy": ["lymphoproliferation or lymphadenopathy"],
 "recurrent urinary tract infections": ["recurrent infections"],
 "repeated genital HSV infections": ["recurrent infections"],
 "insulin-dependent diabetes": ["type 1 diabetes"],
 "interstitial lung disease": ["interstitial lung disease"],
 "pericardial effusion": ["pericarditis or other serositis"],
 "ascites": ["pericarditis or other serositis"],
 "Growth delay": ["growth failure"],
 "Atrophic gastritis": ["gastrointestinal ulcers or inflammation"],
 "atrophic gastritis": ["gastrointestinal ulcers or inflammation"],
}

GROUP_ZYG = "The remaining 89 patients from 39 families were reported with heterozygous loss-of-function mutations in TNFAIP3"
GROUP_LOF = "reported with heterozygous loss-of-function mutations in TNFAIP3"
GENE_SPAN = "mutations in TNFAIP3"
DIS_LABEL_SPAN = "89 patients from 39 families with a genetic diagnosis of HA20"
DX_BASIS_SPAN = "the HA20 patients should be reported with the TNFAIP3 gene mutation by genetic analysis"

def cell(value, span):
    return {"value": value, "span": span}
def mt():
    return {"value": "not reported", "span": None}
def mn():
    return {"value": None, "span": None}

def spans_for(pline, conts, value):
    out = [st(pline)]
    first = re.split(r"[ ,;]", value.strip())[0]
    for c in conts:
        if first and first in st(c):
            out.append(st(c)); break
    seen, res = set(), []
    for s in out:
        if s not in seen:
            seen.add(s); res.append(s)
    return res

def iso(aos):
    if aos and re.fullmatch(r"\d+(\.\d+)?", aos):
        return "P" + aos + "Y"
    return None

publications = [{
 "pmid": cell(PMID, PMID_SPAN),
 "first_author": cell("Chen", "Authors: Chen Yu; Ye Zhenghao; Chen Liping; Qin Tingting; Seidler Ursula; Tian De'an; Xiao Fang"),
 "year": cell(2020, "Journal: Frontiers in Immunology (2020)"),
 "study_type": cell("review/meta-analysis", "We reviewed the HA20 cases in previous literature and summarized the clinical features"),
 "n_patients_reported": cell(89, GROUP_ZYG),
 "cohort_size_as_stated": cell(89, "A total of 89 patients from 39 families with a genetic diagnosis of HA20 were included"),
 "cites_prior_report_of_same_patients": cell(True, "We reviewed the HA20 cases in previous literature and summarized the clinical features"),
 "prior_report_citation": mt(),
}]

individuals, variants, features, checklist_rows, report = [], [], [], [], []

for (n, fam, pline, conts, others, tx) in PATIENTS:
    parsed = parse_row(pline, n)
    assert parsed, "parse failed for patient %s" % n
    aos, sex, syms = parsed
    ref, hline, var = FAM[fam]
    famspan = st(hline)
    prow = [st(pline)] + [st(c) for c in conts][:1]
    lbl_span = st(pline)

    individuals.append({
     "pmid": cell(PMID, PMID_SPAN),
     "individual_label_in_paper": cell(str(n), lbl_span),
     "family_label_in_paper": cell(str(fam), famspan),
     "is_proband": {"value": False, "span": None},
     "sex": cell({"M": "male", "F": "female"}[sex], lbl_span),
     "age_at_onset_original_text": cell(aos if aos else "not reported", lbl_span if aos else None),
     "age_at_onset_iso8601": {"value": iso(aos), "span": lbl_span if aos else None},
     "age_at_last_evaluation_original_text": mt(),
     "age_at_last_evaluation_iso8601": mn(),
     "age_at_diagnosis_original_text": mt(),
     "age_at_diagnosis_iso8601": mn(),
     "ethnicity_or_country": mt(),
     "consanguinity": mt(),
     "vital_status": mt(),
     "deceased_age_iso8601": mn(),
     "cause_of_death": mt(),
     "treatment_summary": cell(tx if tx else "not reported", prow if tx else None),
     "disease_label_as_stated": cell("HA20", DIS_LABEL_SPAN),
     "clinical_diagnosis_basis": cell("genetic analysis", DX_BASIS_SPAN),
     "source_reference_in_review": cell(ref, famspan),
    })

    varspans = [st(hline)]
    if n == 77:
        varspans = [st(566), st(568),
                    "A large deletion mutation of exons 2\u20133 of TNFAIP3 located in the OTU coding region was not shown on the schematic diagram because no exact mutation locus was identified in the case report (13)."]
    variants.append({
     "pmid": cell(PMID, PMID_SPAN),
     "individual_label_in_paper": cell(str(n), lbl_span),
     "gene_symbol_as_stated": cell("TNFAIP3", GENE_SPAN),
     "variant_original_string": cell(var, varspans),
     "transcript_as_stated": mt(),
     "cdna_hgvs_as_stated": mn(),
     "protein_hgvs_as_stated": {"value": var if var.startswith("p.") else None,
                                "span": varspans if var.startswith("p.") else None},
     "genomic_coordinates_as_stated": mn(),
     "variant_type_as_stated": {"value": "large deletion/CNV" if n == 77 else "not reported",
                                "span": varspans if n == 77 else None},
     "zygosity": cell("heterozygous", GROUP_ZYG),
     "inheritance": mt(),
     "parental_testing_statement": mt(),
     "functional_evidence_statement": mt(),
     "pathogenicity_as_stated_by_authors": cell("loss-of-function", GROUP_LOF),
     "acmg_criteria_as_stated": mt(),
    })

    observed = set()
    for key, sym in zip(COLS, syms):
        if sym == "+":
            ftext, hpo, chk = COL_FEATURE[key]
            observed.add(chk)
            features.append({
             "pmid": cell(PMID, PMID_SPAN),
             "individual_label_in_paper": cell(str(n), lbl_span),
             "feature_text_as_stated": cell(ftext, [lbl_span]),
             "status": cell("observed", [lbl_span]),
             "evidence_basis": cell("stated for this individual", None),
             "onset_original_text": mn(),
             "onset_iso8601": mn(),
             "severity_or_detail": mn(),
             "hpo_label_candidate": {"value": hpo, "span": None},
             "hpo_id_candidate": {"value": None, "span": None},
            })
    for (ftext, hpo) in others:
        sp = spans_for(pline, conts, ftext)
        features.append({
         "pmid": cell(PMID, PMID_SPAN),
         "individual_label_in_paper": cell(str(n), lbl_span),
         "feature_text_as_stated": cell(ftext, sp),
         "status": cell("observed", sp),
         "evidence_basis": cell("stated for this individual", None),
         "onset_original_text": mn(),
         "onset_iso8601": mn(),
         "severity_or_detail": mn(),
         "hpo_label_candidate": {"value": hpo, "span": None},
         "hpo_id_candidate": {"value": None, "span": None},
        })
        for chk in OTHER_TO_CHECKLIST.get(ftext, []):
            observed.add(chk)

    for item in CHECKLIST:
        hit = item in observed
        checklist_rows.append({
         "pmid": cell(PMID, PMID_SPAN),
         "individual_label_in_paper": cell(str(n), lbl_span),
         "checklist_feature": cell(item, None),
         "status": cell("observed" if hit else "not reported", None),
         "evidence_basis": cell("stated for this individual" if hit else "not reported", None),
        })

    report.append("%2d fam%-5s aos=%-5s %s %s others=%s" % (n, fam, aos, sex, "".join(syms), [o[0] for o in others]))

out = {
 "pmid": PMID,
 "instructions_version": "extract_v6",
 "reports_individuals_with_tnfaip3_variant": True,
 "relevance_note": "The paper pools previously published HA20 cases and tabulates every patient individually (\"A total of 89 patients from 39 families with a genetic diagnosis of HA20 were included\", Table S1), giving each patient's TNFAIP3 variant and clinical features.",
 "method_note": (
  "Built with a Python script (scratch dir /tmp/openweight_scratch/ow-ha20/33101300); table row lines are copied from the paper Markdown (leading spaces stripped), so all spans are verbatim. "
  "Table S1 is one row per patient (Patient 1-89). Its Family (Ref.) and Amino acid alteration cells are printed only on the first row of each family, so they were propagated to the other patients of that family (family_label_in_paper, source_reference_in_review, variant). "
  "The '+'/'-' symbols of Table S1 are nowhere defined in the paper or its legend, so nothing is recorded as 'excluded': every '-' cell is 'not reported'. '/' cells (treatment, initial diagnosis, other manifestations) are likewise undefined and treated as 'not reported'. No stacked ' / ' cells were found in this paper. "
  "The paper never says which individual patients belong to the OTU+ZnF / OTU / ZnF groups, so group statements such as \"Patients in the OTU group did not present with musculoskeletal disorders\" could not be applied to any individual. "
  "Zygosity 'heterozygous' and pathogenicity 'loss-of-function' were taken from the sentence about the named group of 89 patients (\"The remaining 89 patients from 39 families were reported with heterozygous loss-of-function mutations in TNFAIP3\") - a judgement call; variant_type_as_stated is 'not reported' for all patients because the paper lists mutation classes only for the cohort as a whole, except patient 77, whose printed variant is 'Deletion of exons 2-3' and whose sentence calls it 'A large deletion mutation of exons 2-3 of TNFAIP3'. "
  "Checklist mapping of the paper's own column names: musculoskeletal disorders -> arthritis or arthralgia; autoimmune thyroid disorder -> autoimmune thyroiditis; ocular involvement -> uveitis or other ocular inflammation; recurrent respiratory tract infection -> recurrent infections. From the Other-manifestations column: lymphadenopathy -> lymphoproliferation or lymphadenopathy; insulin-dependent diabetes -> type 1 diabetes; cytopenia and idiopathic thrombocytopenic purpura -> cytopenia (autoimmune); interstitial lung disease -> interstitial lung disease; pericardial effusion and ascites -> pericarditis or other serositis; growth delay -> growth failure; CNS vasculitis and aseptic meningitis -> central nervous system involvement; recurrent urinary tract infections and repeated genital HSV infections -> recurrent infections; atrophic gastritis -> gastrointestinal ulcers or inflammation; autoimmune hepatitis -> autoimmune hepatitis. Plain 'anemia', 'hepatitis', 'liver failure', 'septicemia', 'otitis media' and features named only in the Initial diagnosis column (psoriasis, Henoch Schonlein purpura, Graves' disease) were not mapped onto checklist items. "
  "In the converted file 'insufficiency' of patient 8's 'Aortic valve insufficiency' and patient 77's '2-3' are split across two lines; the values are given joined. "
  "Paper-internal inconsistencies noted: the abstract gives the OTU+ZnF onset IQR as 1-10 while Table 1 gives '6 (1.165-7)'; the abstract gives p = 0.006 for the BD comparison while the Results give p = 0.001; Table S2 prints '30%(0/30)' for p.His636Glufs*55 and '2%(0/50)' for p.Arg439Glnfs*6; Table 3 prints '69(11/16)' for glucocorticoid; the text cites Table S2 where Table 3 is meant."
 ),
 "tables": {
  "publications": publications,
  "individuals": individuals,
  "variants": variants,
  "phenotypic_features": features,
  "phenotype_checklist": checklist_rows,
 },
}

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
    fh.write("\n")
with open(os.path.join(SCRATCH, "review.txt"), "w", encoding="utf-8") as fh:
    fh.write("\n".join(report) + "\n")

print("rows:", {k: len(v) for k, v in out["tables"].items()})

bad = []
def check(v, where):
    if isinstance(v, str):
        if v not in text:
            bad.append((where, v[:80]))
    elif isinstance(v, list):
        for s in v:
            check(s, where)
    elif isinstance(v, dict):
        for kk, vv in v.items():
            check(vv, where + "." + kk)

for tname, rows in out["tables"].items():
    for i, r in enumerate(rows):
        for fname, fv in r.items():
            check(fv.get("span"), "%s[%d].%s" % (tname, i, fname))
check(out["relevance_note"], "relevance_note")
print("bad spans:", len(bad))
for b in bad[:30]:
    print("   ", b)
