import json

pmid = "38183052"
HDR = "PMID: 38183052"
PAPER = "/home/user/gp-rarelink/data/literature/ha20/fulltext_md/38183052.md"
text = open(PAPER).read()


def grab(fragment):
    """Return the exact characters from the paper containing fragment (guards spans)."""
    i = text.find(fragment)
    assert i >= 0, fragment
    return text[i:i + len(fragment)]


def c(v, s):
    return {"value": v, "span": s}


def nt():
    return {"value": "not reported", "span": None}


def nn():
    return {"value": None, "span": None}


def pref(row_label, cells, k):
    return grab("| " + row_label + " | " + " | ".join(cells[:k]) + " |")


labels = ["Patient %d" % i for i in range(1, 13)]
refs = ["Current report", "Endo et al.", "Endo et al.", "Franco-Jarava et al.", "Sun et al",
        "Taniguchi et al.", "Tsuchida et al.", "Tsuchida et al.", "Viel et al.", "Wan et al.",
        "Wu et al.", "Wu et al."]
eth = ["Chinese", "Japanese", "Japanese", "Spanish", "Chinese", "Japanese", "Japanese", "Japanese",
       "French", "unknown", "Caucasian", "African American"]
gender = ["Female", "Female", "Male", "Male", "Female", "Female", "Female", "Female", "Male",
          "Female", "Female", "Male"]
inh = ["de novo", "paternal", "unknown", "de novo", "de novo", "de novo", "maternal", "unknown",
       "unknown", "unknown", "de novo", "unknown"]
onset = ["23 days", "6 months", "1 year", "7 months", "2 months", "3 weeks", "2 months", "1 year",
         "5 years", "35 years", "6 months", "3 years"]
onset_iso = ["P23D", "P6M", "P1Y", "P7M", "P2M", "P3W", "P2M", "P1Y", "P5Y", "P35Y", "P6M", "P3Y"]
diag = ["2 months", "Not mentioned", "Not mentioned", "12 years", "45 months", "8 months",
        "11 years", "16 years", "19 years", "56 years", "6 years", "7 years"]
diag_iso = [None, None, None, "P12Y", "P45M", "P8M", "P11Y", "P16Y", "P19Y", "P56Y", "P6Y", "P7Y"]
initial = ["Fever", "FeverAIHA", "AIHA", "FeverRespiratory- infectionsGastroenteritis", "Fever",
           "Fever", "Fever", "Oral ulcers", "Henoch-Sch\u00f6nlein purpura", "AllergyRosacea",
           "FeverInfectionsOral ulcers", "Oral ulcers"]
fever = ["+", "+", "-", "+", "+", "+", "+", "-", "-", "-", "+", "-"]
lymph = ["-", "+", "+", "+", "+", "-", "+", "+", "-", "+", "+", "-"]
hepato = ["+", "+", "+", "+", "+", "+", "-", "-", "-", "-", "+", "-"]
spleno = ["+", "+", "+", "+", "+", "+", "-", "-", "-", "+", "+", "-"]
anemia = ["+", "AIHA", "AIHA", "-", "HLH", "-", "-", "-", "AIHA", "-", "-", "AIHA"]
hepdys = ["+", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-", "-"]
ftt = ["+", "Not mentioned", "Not mentioned", "+", "+", "+", "+", "Not mentioned", "+",
       "Not mentioned", "+", "+"]
oral = ["-", "-", "-", "+", "-", "+", "+", "+", "-", "-", "+", "+"]
arth = ["-", "-", "-", "-", "-", "+", "+", "-", "+", "-", "-", "-"]

LBL = [pref("", labels, k) for k in range(1, 13)]
S_FEVER = grab("Since the age of 23 days, she suffered from recurrent episodes of low to moderate-grade fever")
S_DEL = grab("revealed a heterozygous 5.15 Mb deletion in 6q23.3q24.3")
S_HA20 = grab("she was definitively diagnosed with HA20")
S_ONSET = grab("Since the age of 23 days")
S_CONSANG = grab("There was no consanguinity")
S_TX1 = grab("she was given ganciclovir for two weeks")
S_TX2 = grab("No immunosuppressive treatment rather than regular project therapy was given")
S_GRP_DEL = grab("patients with HA20 molecularly confirmed to be caused by deletion of chromosome 6q")
S_T1TITLE = grab("Demographic data and initial features of patients with deletions on chromosome 6q in the TNFAIP3 gene")
S_PRIOR = grab("At present, only 11 patients with HA20 molecularly confirmed to be caused by deletion of chromosome 6q have been reported since 2016 [13\u201320].")
S_ALIVE = grab("She subsequently experienced developmental delay in motor")
S_LAST = grab("also presented growth retardation since the age of six months")
S_CRP = grab("Blood analysis revealed slightly elevated white blood cell counts, and C-reactive protein levels, which gradually returned to normal levels")
S_AB = grab("Measurement of autoantibodies, anti-toxoplasma gondii, Rubella Virus, Cytomegalovirus, and Herpes simplex virus (TORCH) were normal.")
S_GROWTH = grab("She presented with decreased activity and clear growth delay.")

# ---------------- publications ----------------
publications = [{
    "pmid": c(pmid, HDR),
    "first_author": c("Zhang", grab("Authors: Zhang Fan; Zhang Liang")),
    "year": c(2024, grab("Journal: Pediatric Rheumatology Online Journal (2024)")),
    "study_type": c("case report", grab("## Clinical report")),
    "n_patients_reported": c(12, grab("In total, 12 cases have been reported to date.")),
    "cohort_size_as_stated": c(12, grab("The initial clinical characteristics and genetic evaluation of all 12 patients are summarized in Table 1 and Fig. 2.")),
    "cites_prior_report_of_same_patients": c(False, grab("Here, we describe for the first time a neonate presenting with concomitant complicated features caused by a large genomic deletion on chromosome 6q.")),
    "prior_report_citation": nt(),
}]

# ---------------- individuals ----------------
ind = []
ind.append({
    "pmid": c(pmid, HDR),
    "individual_label_in_paper": c("Patient 1", LBL[0]),
    "family_label_in_paper": nt(),
    "is_proband": c(True, grab("The neonate was born to a 29-year-old mother via in vitro fertilization.")),
    "sex": c("female", pref("Gender", gender, 1)),
    "age_at_onset_original_text": c("23 days", S_ONSET),
    "age_at_onset_iso8601": c("P23D", S_ONSET),
    "age_at_last_evaluation_original_text": nt(),
    "age_at_last_evaluation_iso8601": nn(),
    "age_at_diagnosis_original_text": c("2 months", pref("Age at diagnosis", diag, 1)),
    "age_at_diagnosis_iso8601": c("P2M", pref("Age at diagnosis", diag, 1)),
    "ethnicity_or_country": c("Chinese", pref("Ethnicity", eth, 1)),
    "consanguinity": c("no", S_CONSANG),
    "vital_status": c("alive", S_ALIVE),
    "deceased_age_iso8601": nn(),
    "cause_of_death": nt(),
    "treatment_summary": c("antibiotics (amoxicillin/potassium clavulanate followed by cefotaxime for two weeks); ganciclovir for two weeks; no immunosuppressive treatment", [S_TX1, S_TX2]),
    "disease_label_as_stated": c("HA20", S_HA20),
    "clinical_diagnosis_basis": c("comparative genomic hybridization array (copy number variation analysis) and clinical features", S_DEL),
    "source_reference_in_review": nt(),
})

for k in range(2, 13):
    ind.append({
        "pmid": c(pmid, HDR),
        "individual_label_in_paper": c(labels[k - 1], LBL[k - 1]),
        "family_label_in_paper": nt(),
        "is_proband": c(False, LBL[k - 1]),
        "sex": c(gender[k - 1].lower(), pref("Gender", gender, k)),
        "age_at_onset_original_text": c(onset[k - 1], pref("Age of onset", onset, k)),
        "age_at_onset_iso8601": c(onset_iso[k - 1], pref("Age of onset", onset, k)),
        "age_at_last_evaluation_original_text": nt(),
        "age_at_last_evaluation_iso8601": nn(),
        "age_at_diagnosis_original_text": (nt() if diag[k - 1] == "Not mentioned"
                                           else c(diag[k - 1], pref("Age at diagnosis", diag, k))),
        "age_at_diagnosis_iso8601": (nn() if diag_iso[k - 1] is None
                                     else c(diag_iso[k - 1], pref("Age at diagnosis", diag, k))),
        "ethnicity_or_country": c(eth[k - 1], pref("Ethnicity", eth, k)),
        "consanguinity": nt(),
        "vital_status": nt(),
        "deceased_age_iso8601": nn(),
        "cause_of_death": nt(),
        "treatment_summary": nt(),
        "disease_label_as_stated": c("HA20 caused by deletion of chromosome 6q", S_GRP_DEL),
        "clinical_diagnosis_basis": c("molecularly confirmed", S_GRP_DEL),
        "source_reference_in_review": c(refs[k - 1], pref("", refs, k)),
    })

# ---------------- variants ----------------
var = []


def variant(label, lbl_span, orig, orig_span, genom, vtype_span, zyg, inh_val, pt):
    var.append({
        "pmid": c(pmid, HDR),
        "individual_label_in_paper": c(label, lbl_span),
        "gene_symbol_as_stated": c("TNFAIP3", grab("The deletion affected at least 30 genes, including TNFAIP3.")),
        "variant_original_string": c(orig, orig_span),
        "transcript_as_stated": nt(),
        "cdna_hgvs_as_stated": nn(),
        "protein_hgvs_as_stated": nn(),
        "genomic_coordinates_as_stated": genom,
        "variant_type_as_stated": c("large deletion/CNV", vtype_span),
        "zygosity": zyg,
        "inheritance": inh_val,
        "parental_testing_statement": pt,
        "functional_evidence_statement": nt(),
        "pathogenicity_as_stated_by_authors": nt(),
        "acmg_criteria_as_stated": nt(),
    })


variant("Patient 1", LBL[0], "heterozygous 5.15 Mb deletion in 6q23.3q24.3",
        grab("heterozygous 5.15 Mb deletion in 6q23.3q24.3"),
        c("6q23.3q24.3", grab("6q23.3q24.3")), S_T1TITLE,
        c("heterozygous", grab("heterozygous 5.15 Mb deletion in 6q23.3q24.3")),
        c("de novo", pref("Inheritance", inh, 1)), nt())

for k in range(2, 13):
    if inh[k - 1] == "de novo":
        inh_val = c("de novo", pref("Inheritance", inh, k))
    elif inh[k - 1] == "paternal":
        inh_val = c("inherited paternal", pref("Inheritance", inh, k))
    elif inh[k - 1] == "maternal":
        inh_val = c("inherited maternal", pref("Inheritance", inh, k))
    else:
        inh_val = nt()
    variant(labels[k - 1], LBL[k - 1], "not reported", None, nn(), S_T1TITLE,
            nt(), inh_val, nt())

# ---------------- phenotypic_features ----------------
pf = []


def feat(label, lbl_span, text_val, status, span, onset=None, onset_iso=None, detail=None,
         hpo_l=None, hpo_i=None):
    pf.append({
        "pmid": c(pmid, HDR),
        "individual_label_in_paper": c(label, lbl_span),
        "feature_text_as_stated": c(text_val, span),
        "status": c(status, span),
        "evidence_basis": c("stated for this individual", span),
        "onset_original_text": (c(onset, span) if onset else nn()),
        "onset_iso8601": (c(onset_iso, span) if onset_iso else nn()),
        "severity_or_detail": (c(detail, span) if detail else nn()),
        "hpo_label_candidate": {"value": hpo_l, "span": None},
        "hpo_id_candidate": {"value": hpo_i, "span": None},
    })


L1 = LBL[0]
feat("Patient 1", L1, "recurrent episodes of low to moderate-grade fever (37.6\u201339\u2103) one to three times per day",
     "observed", S_FEVER, "23 days", "P23D",
     "low to moderate-grade fever (37.6\u201339\u2103) one to three times per day",
     "Recurrent fever", "HP:0001954")
feat("Patient 1", L1, "decreased activity", "observed", S_GROWTH, None, None, None, "Lethargy", "HP:0001254")
feat("Patient 1", L1, "growth delay", "observed", S_GROWTH, None, None, None, "Growth delay", "HP:0001510")
feat("Patient 1", L1, "extrauterine growth restriction", "observed",
     grab("On admission, extrauterine growth restricted was noted."), None, None, None,
     "Extrauterine growth restriction", "HP:0001518")
feat("Patient 1", L1, "body weight below the 3rd percentile", "observed",
     grab("Body weight and head circumference were below the 3rd and 10th percentiles, respectively."),
     None, None, "below the 3rd percentile", "Low birth weight", None)
feat("Patient 1", L1, "head circumference below the 10th percentile", "observed",
     grab("Body weight and head circumference were below the 3rd and 10th percentiles, respectively."),
     None, None, "below the 10th percentile", "Microcephaly", None)
feat("Patient 1", L1, "enlarged liver", "observed",
     grab("Physical examination revealed enlarged liver and spleen, 4 cm below the right costal margin"),
     None, None, "4 cm below the right costal margin", "Hepatomegaly", "HP:0002240")
feat("Patient 1", L1, "enlarged spleen", "observed",
     grab("Physical examination revealed enlarged liver and spleen, 4 cm below the right costal margin and 2.5 cm below the left costal margin, respectively."),
     None, None, "2.5 cm below the left costal margin", "Splenomegaly", "HP:0001744")
feat("Patient 1", L1, "hepatic dysfunction", "observed", pref("Hepatic dysfunction", hepdys, 1),
     None, None, None, "Decreased liver function", "HP:0001410")
feat("Patient 1", L1, "elevated white blood cell counts", "observed",
     grab("Blood analysis revealed slightly elevated white blood cell counts"), None, None,
     "slightly elevated", "Leukocytosis", None)
feat("Patient 1", L1, "elevated C-reactive protein levels", "observed", S_CRP, None, None, None,
     "Elevated C-reactive protein", "HP:0011227")
feat("Patient 1", L1, "acute severe anemia", "observed",
     grab("She suffered worsening of her acute severe anemia with elevated percent of reticulocyte up to 3.87% gradually after the onset of fever"),
     None, None, "acute severe", "Anemia", "HP:0001903")
feat("Patient 1", L1, "elevated percent of reticulocyte up to 3.87%", "observed",
     grab("elevated percent of reticulocyte up to 3.87% gradually after the onset of fever"),
     None, None, "up to 3.87%", "Reticulocytosis", "HP:0001923")
feat("Patient 1", L1, "elevated liver enzymes", "observed",
     grab("Liver enzymes were elevated constantly for 10 days after onset of the febrile attacks"),
     None, None, "elevated constantly for 10 days", "Elevated hepatic transaminase", None)
feat("Patient 1", L1, "hepatic injury", "observed",
     grab("Mild anemia and hepatic injury reappeared after another slight fever lasting for about one week"),
     None, None, None, "Hepatic injury", None)
feat("Patient 1", L1, "CMV positive", "observed",
     grab("Metagenomic next generation sequencing was performed to detect pathogenic agents, which showed CMV positive"),
     None, None, None, "Cytomegalovirus infection", None)
feat("Patient 1", L1, "developmental delay in motor", "observed", S_ALIVE, None, None, None,
     "Motor delay", "HP:0001270")
feat("Patient 1", L1, "growth retardation", "observed", S_LAST, "six months", "P6M", None,
     "Growth retardation", "HP:0001510")
feat("Patient 1", L1, "preterm birth", "observed",
     grab("She was preterm (delivered, at a gestational age of 36 weeks, by cesarean section)"),
     None, None, "at a gestational age of 36 weeks", "Premature birth", "HP:0001622")
feat("Patient 1", L1, "hemolysis", "excluded",
     grab("there was no clear evidence of hemoglobin loss or hemolysis"), None, None, None,
     "Hemolysis", "HP:0001878")
feat("Patient 1", L1, "active bleeding", "excluded",
     grab("without clinical signs of active bleeding or jaundice"), None, None, None, "Bleeding", None)
feat("Patient 1", L1, "jaundice", "excluded",
     grab("without clinical signs of active bleeding or jaundice"), None, None, None, "Jaundice", "HP:0000952")
feat("Patient 1", L1, "hyperbilirubinemia", "excluded",
     grab("without hyperbilirubinemia or increased serum lactate dehydrogenase"), None, None, None,
     "Hyperbilirubinemia", "HP:0002904")
feat("Patient 1", L1, "increased serum lactate dehydrogenase", "excluded",
     grab("without hyperbilirubinemia or increased serum lactate dehydrogenase"), None, None, None,
     "Elevated lactate dehydrogenase", None)
S_NEG = grab("direct antiglobulin test, hemoglobin analysis, red cell osmotic fragility test and enzymatic activity test of G6PD were negative")
feat("Patient 1", L1, "positive direct antiglobulin test", "excluded", S_NEG, None, None, None,
     "Positive direct antiglobulin test", None)
feat("Patient 1", L1, "abnormal hemoglobin analysis", "excluded", S_NEG, None, None, None,
     "Abnormal hemoglobin", None)
feat("Patient 1", L1, "abnormal red cell osmotic fragility test", "excluded", S_NEG, None, None, None,
     "Abnormal red cell osmotic fragility", None)
feat("Patient 1", L1, "abnormal G6PD enzymatic activity", "excluded", S_NEG, None, None, None,
     "Abnormal glucose-6-phosphate dehydrogenase activity", None)
feat("Patient 1", L1, "autoantibodies", "excluded", S_AB, None, None, None,
     "Autoantibody positivity", None)
feat("Patient 1", L1, "abnormal ophthalmologic assessment", "excluded",
     grab("No other obvious abnormalities were found in ophthalmologic assessment, hearing test and brain MRI scans."),
     None, None, None, "Abnormal eye examination", None)
feat("Patient 1", L1, "abnormal hearing test", "excluded",
     grab("No other obvious abnormalities were found in ophthalmologic assessment, hearing test and brain MRI scans."),
     None, None, None, "Hearing impairment", "HP:0000365")
feat("Patient 1", L1, "abnormal brain MRI", "excluded",
     grab("No other obvious abnormalities were found in ophthalmologic assessment, hearing test and brain MRI scans."),
     None, None, None, "Abnormal brain MRI", None)
feat("Patient 1", L1, "positive pathogen cultures", "excluded",
     grab("Pathogen cultures were negative"), None, None, None, "Positive bacterial culture", None)
feat("Patient 1", L1, "enlarged spleen", "excluded", grab("her spleen was not palpable"),
     None, None, "at follow-up", "Splenomegaly", "HP:0001744")

ROWS = [
    ("Fever", fever, "Fever", "Recurrent fever", "HP:0001954"),
    ("Lymphadenopathy", lymph, "Lymphadenopathy", "Lymphadenopathy", "HP:0002716"),
    ("Hepatomegaly", hepato, "Hepatomegaly", "Hepatomegaly", "HP:0002240"),
    ("Splenomegaly", spleno, "Splenomegaly", "Splenomegaly", "HP:0001744"),
    ("Oral ulcer", oral, "Oral ulcer", "Oral ulcer", "HP:0000155"),
    ("Arthralgia", arth, "Arthralgia", "Arthralgia", "HP:0002829"),
]
CL_MAP = {
    "Fever": "recurrent fever",
    "Lymphadenopathy": "lymphoproliferation or lymphadenopathy",
    "Oral ulcer": "oral ulcers",
    "Arthralgia": "arthritis or arthralgia",
}

cl_rows = []


def cl(label, lbl_span, checklist_feature, status, span):
    cl_rows.append((label, lbl_span, checklist_feature, status, span))


for k in range(2, 13):
    label, lbl_span = labels[k - 1], LBL[k - 1]
    for row_label, cells, text_val, hpo_l, hpo_i in ROWS:
        span = pref(row_label, cells, k)
        if cells[k - 1] == "+":
            feat(label, lbl_span, text_val, "observed", [span, lbl_span], hpo_l=hpo_l, hpo_i=hpo_i)
            cl(label, lbl_span, CL_MAP[row_label], "observed", span)
        elif cells[k - 1] == "-":
            feat(label, lbl_span, text_val, "excluded", [span, lbl_span], hpo_l=hpo_l, hpo_i=hpo_i)
            cl(label, lbl_span, CL_MAP[row_label], "excluded", span)
    if ftt[k - 1] == "+":
        span = pref("Failure to thrive", ftt, k)
        feat(label, lbl_span, "Failure to thrive", "observed", [span, lbl_span],
             hpo_l="Failure to thrive", hpo_i="HP:0001508")
        cl(label, lbl_span, "growth failure", "observed", span)
    a = anemia[k - 1]
    span = pref("Anemia", anemia, k)
    if a == "AIHA":
        feat(label, lbl_span, "AIHA", "observed", [span, lbl_span],
             hpo_l="Autoimmune hemolytic anemia", hpo_i="HP:0001890")
        cl(label, lbl_span, "cytopenia (autoimmune)", "observed", span)
    elif a == "HLH":
        feat(label, lbl_span, "HLH", "observed", [span, lbl_span],
             hpo_l="Hemophagocytic lymphohistiocytosis", hpo_i="HP:0001973")
    elif a == "-":
        feat(label, lbl_span, "Anemia", "excluded", [span, lbl_span],
             hpo_l="Anemia", hpo_i="HP:0001903")
    span = pref("Initial symptoms", initial, k)
    feat(label, lbl_span, initial[k - 1], "observed", [span, lbl_span])

cl("Patient 4", LBL[3], "gastrointestinal ulcers or inflammation", "observed",
   pref("Initial symptoms", initial, 4))
cl("Patient 9", LBL[8], "vasculitis", "observed", pref("Initial symptoms", initial, 9))

# ---------------- phenotype_checklist ----------------
CHECK = [
    "oral ulcers", "genital ulcers", "gastrointestinal ulcers or inflammation", "recurrent fever",
    "arthritis or arthralgia", "uveitis or other ocular inflammation",
    "skin lesions (rash, folliculitis, erythema nodosum)", "autoimmune thyroiditis",
    "type 1 diabetes", "autoimmune hepatitis", "cytopenia (autoimmune)",
    "lymphoproliferation or lymphadenopathy", "central nervous system involvement",
    "recurrent infections", "elevated inflammatory markers (CRP/ESR)",
    "autoantibodies (ANA/other)", "growth failure", "pericarditis or other serositis",
    "interstitial lung disease", "vasculitis",
]

CL = {}
for label in labels:
    for f in CHECK:
        CL[(label, f)] = ("not reported", None)
for label, lbl_span, f, status, span in cl_rows:
    CL[(label, f)] = (status, span)

CL[("Patient 1", "recurrent fever")] = ("observed", S_FEVER)
CL[("Patient 1", "elevated inflammatory markers (CRP/ESR)")] = ("observed", S_CRP)
CL[("Patient 1", "autoantibodies (ANA/other)")] = ("excluded", S_AB)
CL[("Patient 1", "growth failure")] = ("observed", S_GROWTH)

checklist = []
for k, label in enumerate(labels):
    for f in CHECK:
        status, span = CL[(label, f)]
        if status == "not reported":
            checklist.append({
                "pmid": c(pmid, HDR),
                "individual_label_in_paper": c(label, LBL[k]),
                "checklist_feature": {"value": f, "span": None},
                "status": c("not reported", None),
                "evidence_basis": c("not reported", None),
            })
        else:
            checklist.append({
                "pmid": c(pmid, HDR),
                "individual_label_in_paper": c(label, LBL[k]),
                "checklist_feature": {"value": f, "span": None},
                "status": c(status, span),
                "evidence_basis": c("stated for this individual", span),
            })

method_note = (
    "Read the paper by hand (full text, Table 1, references); no script transcribed the table, but Table 1 cells were typed by hand into a build script that assembles each span as the contiguous row prefix ending at that patient's column, so spans are verbatim. "
    "Table 1 shows patients as columns, so the two header rows fix the mapping: header row 1 gives each patient's source publication (copied into source_reference_in_review) and header row 2 the paper's own labels 'Patient 1'-'Patient 12'. Patient 1 is the neonate of this report (Current report); Patients 2-12 are literature cases from references [13-20]. "
    "Table 1 has no legend defining '+' and '-', so, as the table also uses 'Not mentioned' for silence, '+' was read as observed and '-' as excluded; this is an assumption. 'AIHA' and 'HLH' are defined by the table legend ('AIHA Autoimmune hemolytic anemia, HLH Hemophagocytic lymphohistiocytosis'). "
    "Table 1's 'Initial symptoms' cells hold several values that were stacked on separate lines and are printed run together (e.g. 'FeverAIHA', 'FeverRespiratory- infectionsGastroenteritis', 'AllergyRosacea'); per D-31 they were not assigned by position, and each patient's whole cell is recorded verbatim as one feature. The only checklist items taken from those cells are those printed word for word: 'Gastroenteritis' for Patient 4 (gastrointestinal ulcers or inflammation) and 'Henoch-Schonlein purpura' for Patient 9 (vasculitis). "
    "Table 1's 'Size of deletion' row has no schema field; no variant description is printed for Patients 2-12 (their deletions are shown only in Fig. 2, which is not available), so their variant_original_string is 'not reported' per D-22, with gene TNFAIP3 and the printed group wording for the type. The paper calls the deletions 'pathogenic' only in general terms (Fig. 2 caption 'pathogenic deletions in chromosome 6 affectingTNFAIP3'), which D-29 excludes, so pathogenicity is 'not reported' for everyone; zygosity is printed only for Patient 1 ('heterozygous'). Inheritance is taken from Table 1's 'Inheritance' row per patient ('paternal'/'maternal' recorded as inherited paternal/maternal, 'de novo' as de novo); the paper never states parental testing, so parental_testing_statement is 'not reported' and de novo rests on the paper's own wording. "
    "Normal findings were recorded as the abnormality they rule out ('Measurement of autoantibodies ... were normal' -> autoantibodies excluded); an examination as a whole (ophthalmologic assessment, hearing test, brain MRI, abdominal ultrasonography) is written as the paper does and excludes no specific checklist item, so uveitis/ocular inflammation and CNS involvement stay 'not reported'. "
    "Patient 1's liver findings are recorded as hepatomegaly, hepatic dysfunction, elevated liver enzymes and hepatic injury; 'autoimmune hepatitis' and 'cytopenia (autoimmune)' stay 'not reported' because the paper never calls them autoimmune (her anemia is 'acute severe', with hemolysis excluded). AIHA in Patients 2, 3, 9 and 12 is read as autoimmune cytopenia. "
    "cites_prior_report_of_same_patients is false: the earlier patients in Table 1 come from other publications (references [13-20]) and the paper never says its own patient was described before. "
    "Not contradictions but noted: Table 1 lists Patient 1's spleen as enlarged on admission, while the text later says 'her spleen was not palpable' (a change over time, so both rows are kept); the text says 'only 11 patients ... have been reported since 2016' while Table 1 and the Discussion count 12 in total (11 previously reported plus this neonate); Table 1 gives Patients 2 and 3 'AIHA' as initial symptom while their 'Fever' cell is negative. Group counts without names ('eigtht were female', 'five presented with de novo deletions', 'Nine patients experienced early-onset symptoms') were used to exclude nobody."
)

out = {
    "pmid": pmid,
    "instructions_version": "extract_v6",
    "reports_individuals_with_tnfaip3_variant": True,
    "relevance_note": "The paper describes an identifiable neonate with HA20 caused by a deletion including TNFAIP3 (\"she was definitively diagnosed with HA20\") and reviews 11 further published patients with 6q deletions in Table 1.",
    "method_note": method_note,
    "tables": {
        "publications": publications,
        "individuals": ind,
        "variants": var,
        "phenotypic_features": pf,
        "phenotype_checklist": checklist,
    },
}

with open("/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/38183052.json", "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("rows:", len(publications), len(ind), len(var), len(pf), len(checklist))
