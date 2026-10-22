import json

PMID = "29682366"
HDR = "PMID: 29682366"

S = {
 "abstract_male": "In this report, we describe a 47-year-old Hispanic male who presented initially for an evaluation of chronic hives following hospitalization due to hive-induced anaphylaxis.",
 "case_open": "A 47-year-old Hispanic male was initially referred to the Mayo Clinic at 34 years of age due to severe episodes of angioedema (occurring every three to four months) and history of chronic urticaria.",
 "onset_urticaria": "The initial onset of urticaria occurred in 2002 while the proband was living in Italy.",
 "early30s": "The individual had a history significant for urticaria and angioedema beginning in his early 30s.",
 "triggers": "The proband reported that episodes of urticaria occur when his skin is exposed to hot or cold temperatures or significant pressure.",
 "treat": "The proband tried numerous treatment modalities to suppress his urticaria, including the following antihistamines: levocetirizine, cetirizine, fexofenadine, and loratadine. Prednisone and steroid injections were the only treatments that cleared the patient's hives; however, treatment with prednisone was eventually stopped due to side effects.",
 "ige": "His elevated levels of IgE suggested that the hives were autoimmune in nature, though the accompanying tryptase elevation led to the consideration of mastocytosis.",
 "bm_normal": "The patient had a normal bone marrow biopsy (differential and aspirate), a complete blood count (CBC) with differential within normal limits, and a normal mast cell panel (CD2, CD25, CD69, and CD117).",
 "antiige": "His anti-IgE receptor antibody was elevated at 18.5% (reference range: <13%) and his C1q complement was elevated at 43 (12\u201322 mg/dL).",
 "tsh": "He also had a normal TSH of 2.0 (>20 years: 0.3\u20134.2 mIU/L) and serum protein electrophoresis that was within normal limits.",
 "tryptase": "His tryptase levels were consistently elevated and ranged from 13.9 and 19.2 (<11.5 ng/mL), indicating mast cell activation.",
 "dx_urticaria": "Due to the absence of mast cells in the bone marrow biopsy, the patient did not meet diagnostic criteria for mastocytosis and was ultimately diagnosed with chronic urticaria.",
 "attacks": "At 37 years of age, the patient began experiencing \u201cattacks\u201d approximately every two weeks, which he described as involving hives, fever, weakness, diaphoresis, and diarrhea.",
 "dizzy": "The patient also experienced episodes of dizziness when standing after walking only a few feet.",
 "abstract_sister_daughter": "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema.",
 "abstract_wes": "Whole exome sequencing of the proband and several family members revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3, denoted as c.65G>A (p.R22Q), in all affected members.",
 "fam_hist": "Upon ascertainment of family history, we found that one of the proband's sisters and his daughter both shared his symptoms of hives and angioedema (Figure 1).",
 "daughter_detail": "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet.",
 "daughter_gym": "She participated in gymnastics but had to discontinue this activity due to swelling of her feet after practice.",
 "daughter_cello": "She has also developed hand swelling after playing the cello.",
 "fig1_arrow": "**Figure 1**: Family pedigree. Standard pedigree symbols are used. An arrow indicates the proband.",
 "methods_dna": "Using genomic DNA extracted from the proband, his mother, sister, and daughter, the Agilent Clinical Research Exome kit was used to target exonic regions and flanking splice junctions of the genome.",
 "wes_variant": "WES of the proband uncovered a novel variant inTNFAIP3 (Chr6(GRCh38): g.137871292G>A; NM_001270507.1: c.65G>A; p.(Arg22Gln)), which could possibly correlate with the proband's disease phenotype.",
 "vus_acmg": "Based on the ACMG 2015 guidelines, the c.65G>A (p.R22Q) variant was classified as a variant of uncertain significance (VUS) [23].",
 "mother_neg": "The proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased), whereas both his daughter and sister (both affected) were heterozygous for the VUS.",
 "gjb2_proband": "Another pathogenic variant was detected inGJB2 (Chr13(GRCh38): g.20189547del; NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2) in the proband and his mother only, which may be associated with his mild hearing loss.",
 "gjb2_mother": "The proband's mother was heterozygous for the c.35delG variant inGJB2while his sister and daughter did not carry this variant.",
 "func_model": "The wild type object stability was 53.12 kcal/mol\u2217\u00c5^2, while the p.R22Q variant results in a net increase in free energy of 0.755 kcal/aa\u2217mol\u2217\u00c5^2, which could be locally destabilizing [17\u201319, 24\u201327].",
 "concl_family": "The proband, his daughter, and his sister who are all affected with chronic urticaria and angioedema each carry the c.65G>A (p.R22Q) variant inTNFAIP3. The variant is absent in the proband's mother who is unaffected.",
 "concl_bm": "Bone marrow biopsy and computerized tomography (CT) scans ruled out visceral involvement by systemic mastocytosis, and the patient was later diagnosed with chronic urticaria.",
 "summary_three": "In summary, we report a novel variant inTNFAIP3in three family members, which potentially correlates with a phenotype of chronic urticaria.",
 "urticaria_def": "Chronic urticaria is a common skin disorder characterized by recurrent hives lasting more than six weeks or hives that recur over several months or years [1, 2].",
 "urticaria_idiopathic": "Chronic urticaria is usually idiopathic, arising spontaneously without a stimulus.",
 "angioedema_def": "Angioedema is a swelling of the deeper epidermal and dermal layers of the skin.",
 "therapy_omalizumab": "Many patients with chronic urticaria improve with anti-IgE therapy (omalizumab), suggesting that inappropriate activation of mast cells and basophils may play a role in disease pathogenesis.",
}

P = "P1"; M = "mother of P1"; D = "daughter of P1"; SIS = "sister of P1"


def c(value, span):
    return {"value": value, "span": span}


def miss(span=False):
    return {"value": "not reported", "span": None}


def num_miss():
    return {"value": None, "span": None}


rows_publications = [{
    "pmid": c(PMID, HDR),
    "first_author": c("Harris", "Authors: Harris Antoneicka L; Blackburn Patrick R; Richter John E; Gass Jennifer M; Caulfield Thomas R; Mohammad Ahmed N; Atwal Paldeep S"),
    "year": c(2018, "Journal: Case Reports in Genetics (2018)"),
    "study_type": c("case report", "In this report, we describe a 47-year-old Hispanic male"),
    "n_patients_reported": c(3, S["summary_three"]),
    "cohort_size_as_stated": num_miss(),
    "cites_prior_report_of_same_patients": {"value": False, "span": S["concl_family"]},
    "prior_report_citation": miss(),
}]

rows_individuals = [
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(P, "A 47-year-old Hispanic male was initially referred to the Mayo Clinic at 34 years of age"),
  "family_label_in_paper": c("Family 1", "**Figure 1**: Family pedigree."),
  "is_proband": {"value": True, "span": S["fig1_arrow"]},
  "sex": c("male", "A 47-year-old Hispanic male was initially referred to the Mayo Clinic at 34 years of age"),
  "age_at_onset_original_text": c("early 30s", S["early30s"]),
  "age_at_onset_iso8601": num_miss(),
  "age_at_last_evaluation_original_text": c("47 years", "we describe a 47-year-old Hispanic male who presented initially for an evaluation of chronic hives following hospitalization due to hive-induced anaphylaxis."),
  "age_at_last_evaluation_iso8601": c("P47Y", "we describe a 47-year-old Hispanic male who presented initially for an evaluation of chronic hives following hospitalization due to hive-induced anaphylaxis."),
  "age_at_diagnosis_original_text": miss(),
  "age_at_diagnosis_iso8601": num_miss(),
  "ethnicity_or_country": c("Hispanic", "we describe a 47-year-old Hispanic male who presented initially for an evaluation of chronic hives following hospitalization due to hive-induced anaphylaxis."),
  "consanguinity": miss(),
  "vital_status": miss(),
  "deceased_age_iso8601": num_miss(),
  "cause_of_death": miss(),
  "treatment_summary": c("levocetirizine, cetirizine, fexofenadine, and loratadine; Prednisone and steroid injections were the only treatments that cleared the patient's hives; however, treatment with prednisone was eventually stopped due to side effects.", [S["treat"], S["therapy_omalizumab"]]),
  "disease_label_as_stated": c("chronic urticaria", S["dx_urticaria"]),
  "clinical_diagnosis_basis": c("clinical evaluation and diagnosis; WES identified a TNFAIP3 variant of uncertain significance", [S["dx_urticaria"], S["wes_variant"], S["vus_acmg"]]),
  "source_reference_in_review": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(M, "The proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased)"),
  "family_label_in_paper": c("Family 1", "**Figure 1**: Family pedigree."),
  "is_proband": {"value": False, "span": S["fig1_arrow"]},
  "sex": c("female", "The proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased)"),
  "age_at_onset_original_text": miss(),
  "age_at_onset_iso8601": num_miss(),
  "age_at_last_evaluation_original_text": miss(),
  "age_at_last_evaluation_iso8601": num_miss(),
  "age_at_diagnosis_original_text": miss(),
  "age_at_diagnosis_iso8601": num_miss(),
  "ethnicity_or_country": miss(),
  "consanguinity": miss(),
  "vital_status": miss(),
  "deceased_age_iso8601": num_miss(),
  "cause_of_death": miss(),
  "treatment_summary": miss(),
  "disease_label_as_stated": c("unaffected", "The variant is absent in the proband's mother who is unaffected."),
  "clinical_diagnosis_basis": c("clinical history and genetic testing (WES) with parental testing: 'the proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased)'", [S["mother_neg"], S["methods_dna"]]),
  "source_reference_in_review": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(D, "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet."),
  "family_label_in_paper": c("Family 1", "**Figure 1**: Family pedigree."),
  "is_proband": {"value": False, "span": S["fig1_arrow"]},
  "sex": c("female", "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet."),
  "age_at_onset_original_text": miss(),
  "age_at_onset_iso8601": num_miss(),
  "age_at_last_evaluation_original_text": c("12 years of age at the time of evaluation", "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet."),
  "age_at_last_evaluation_iso8601": c("P12Y", "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet."),
  "age_at_diagnosis_original_text": miss(),
  "age_at_diagnosis_iso8601": num_miss(),
  "ethnicity_or_country": miss(),
  "consanguinity": miss(),
  "vital_status": miss(),
  "deceased_age_iso8601": num_miss(),
  "cause_of_death": miss(),
  "treatment_summary": c("had to discontinue this activity due to swelling of her feet after practice", S["daughter_gym"]),
  "disease_label_as_stated": c("chronic urticaria and severe angioedema", "both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema"),
  "clinical_diagnosis_basis": c("genetic testing", S["abstract_wes"]),
  "source_reference_in_review": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(SIS, "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema."),
  "family_label_in_paper": c("Family 1", "**Figure 1**: Family pedigree."),
  "is_proband": {"value": False, "span": S["fig1_arrow"]},
  "sex": c("female", "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema."),
  "age_at_onset_original_text": miss(),
  "age_at_onset_iso8601": num_miss(),
  "age_at_last_evaluation_original_text": c("41-year-old", "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema."),
  "age_at_last_evaluation_iso8601": c("P41Y", "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema."),
  "age_at_diagnosis_original_text": miss(),
  "age_at_diagnosis_iso8601": num_miss(),
  "ethnicity_or_country": miss(),
  "consanguinity": miss(),
  "vital_status": miss(),
  "deceased_age_iso8601": num_miss(),
  "cause_of_death": miss(),
  "treatment_summary": miss(),
  "disease_label_as_stated": c("chronic urticaria and severe angioedema", "both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema"),
  "clinical_diagnosis_basis": c("genetic testing", S["abstract_wes"]),
  "source_reference_in_review": miss(),
 },
]

rows_variants = [
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(P, "WES of the proband uncovered a novel variant inTNFAIP3"),
  "gene_symbol_as_stated": c("TNFAIP3", "WES of the proband uncovered a novel variant inTNFAIP3"),
  "variant_original_string": c("c.65G>A", "NM_001270507.1: c.65G>A; p.(Arg22Gln)"),
  "transcript_as_stated": c("NM_001270507.1", "NM_001270507.1: c.65G>A; p.(Arg22Gln)"),
  "cdna_hgvs_as_stated": c("c.65G>A", "NM_001270507.1: c.65G>A; p.(Arg22Gln)"),
  "protein_hgvs_as_stated": c("p.(Arg22Gln)", "NM_001270507.1: c.65G>A; p.(Arg22Gln)"),
  "genomic_coordinates_as_stated": c("Chr6(GRCh38): g.137871292G>A", "Chr6(GRCh38): g.137871292G>A; NM_001270507.1: c.65G>A; p.(Arg22Gln)"),
  "variant_type_as_stated": c("missense", "Currently, there is no known association between missense variants inTNFAIP3 and familial chronic urticaria with angioedema."),
  "zygosity": c("heterozygous", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "inheritance": c("not reported", None),
  "parental_testing_statement": c("The proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased)", S["mother_neg"]),
  "functional_evidence_statement": c("in silico molecular modeling: the p.R22Q variant results in a net increase in free energy of 0.755 kcal/aa\u2217mol\u2217\u00c5^2, which could be locally destabilizing", [S["func_model"], "The positively charged ring is dissipated in the Gln22 structure, which would indicate that the effect noted above may be eliminated, potentially contributing to the altered TNFAIP3 function."]),
  "pathogenicity_as_stated_by_authors": c("variant of uncertain significance (VUS)", S["vus_acmg"]),
  "acmg_criteria_as_stated": c("ACMG 2015 guidelines", S["vus_acmg"]),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(D, "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "gene_symbol_as_stated": c("TNFAIP3", "Whole exome sequencing of the proband and several family members revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3"),
  "variant_original_string": c("c.65G>A (p.R22Q)", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "transcript_as_stated": miss(),
  "cdna_hgvs_as_stated": c("c.65G>A", "both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema"),
  "protein_hgvs_as_stated": c("p.R22Q", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "genomic_coordinates_as_stated": miss(),
  "variant_type_as_stated": c("missense", "Currently, there is no known association between missense variants inTNFAIP3 and familial chronic urticaria with angioedema."),
  "zygosity": c("heterozygous", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "inheritance": c("not reported", None),
  "parental_testing_statement": miss(),
  "functional_evidence_statement": miss(),
  "pathogenicity_as_stated_by_authors": c("variant of uncertain significance (VUS)", "Whole exome sequencing of the proband and several family members revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3"),
  "acmg_criteria_as_stated": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(SIS, "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "gene_symbol_as_stated": c("TNFAIP3", "Whole exome sequencing of the proband and several family members revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3"),
  "variant_original_string": c("c.65G>A (p.R22Q)", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "transcript_as_stated": miss(),
  "cdna_hgvs_as_stated": c("c.65G>A", "both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema"),
  "protein_hgvs_as_stated": c("p.R22Q", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "genomic_coordinates_as_stated": miss(),
  "variant_type_as_stated": c("missense", "Currently, there is no known association between missense variants inTNFAIP3 and familial chronic urticaria with angioedema."),
  "zygosity": c("heterozygous", "both his daughter and sister (both affected) were heterozygous for the VUS"),
  "inheritance": c("not reported", None),
  "parental_testing_statement": miss(),
  "functional_evidence_statement": miss(),
  "pathogenicity_as_stated_by_authors": c("variant of uncertain significance (VUS)", "Whole exome sequencing of the proband and several family members revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3"),
  "acmg_criteria_as_stated": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(P, "Another pathogenic variant was detected inGJB2"),
  "gene_symbol_as_stated": c("GJB2", "Another pathogenic variant was detected inGJB2"),
  "variant_original_string": c("c.35del", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "transcript_as_stated": c("NM_004004.5", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "cdna_hgvs_as_stated": c("c.35del", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "protein_hgvs_as_stated": c("p.Gly12Valfs\u22172", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "genomic_coordinates_as_stated": c("Chr13(GRCh38): g.20189547del", "Chr13(GRCh38): g.20189547del; NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "variant_type_as_stated": c("frameshift", "The c.35delG variant inGJB2has been reported previously in association with autosomal recessive nonsyndromic hearing loss"),
  "zygosity": c("heterozygous", "The proband's mother was heterozygous for the c.35delG variant inGJB2while his sister and daughter did not carry this variant."),
  "inheritance": c("not reported", None),
  "parental_testing_statement": c("The proband's mother was heterozygous for the c.35delG variant inGJB2while his sister and daughter did not carry this variant.", S["gjb2_mother"]),
  "functional_evidence_statement": miss(),
  "pathogenicity_as_stated_by_authors": c("pathogenic", "Another pathogenic variant was detected inGJB2"),
  "acmg_criteria_as_stated": miss(),
 },
 {
  "pmid": c(PMID, HDR),
  "individual_label_in_paper": c(M, "Another pathogenic variant was detected inGJB2 (Chr13(GRCh38): g.20189547del; NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2) in the proband and his mother only"),
  "gene_symbol_as_stated": c("GJB2", "Another pathogenic variant was detected inGJB2"),
  "variant_original_string": c("c.35del", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "transcript_as_stated": c("NM_004004.5", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "cdna_hgvs_as_stated": c("c.35del", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "protein_hgvs_as_stated": c("p.Gly12Valfs\u22172", "NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "genomic_coordinates_as_stated": c("Chr13(GRCh38): g.20189547del", "Chr13(GRCh38): g.20189547del; NM_004004.5: c.35del; p.Gly12Valfs\u22172; exon 2"),
  "variant_type_as_stated": c("frameshift", "The c.35delG variant inGJB2has been reported previously in association with autosomal recessive nonsyndromic hearing loss"),
  "zygosity": c("heterozygous", "The proband's mother was heterozygous for the c.35delG variant inGJB2"),
  "inheritance": c("not reported", None),
  "parental_testing_statement": c("The proband's mother was heterozygous for the c.35delG variant inGJB2while his sister and daughter did not carry this variant.", S["gjb2_mother"]),
  "functional_evidence_statement": miss(),
  "pathogenicity_as_stated_by_authors": c("pathogenic", "Another pathogenic variant was detected inGJB2"),
  "acmg_criteria_as_stated": miss(),
 },
]

# phenotypic_features
pf = []
def add(label, feat, status, basis, span, onset=None, onset_iso=None, sev=None, hpo=None, hpid=None):
    pf.append({
        "pmid": c(PMID, HDR),
        "individual_label_in_paper": c(label, span if isinstance(span, str) else span[0]),
        "feature_text_as_stated": c(feat, span),
        "status": c(status, span),
        "evidence_basis": c(basis, span if isinstance(span, str) else span[0]),
        "onset_original_text": c(onset, span) if onset else num_miss(),
        "onset_iso8601": c(onset_iso, span) if onset_iso else num_miss(),
        "severity_or_detail": c(sev, span) if sev else num_miss(),
        "hpo_label_candidate": {"value": hpo, "span": None},
        "hpo_id_candidate": {"value": hpid, "span": None},
    })

# P1
add(P, "chronic urticaria", "observed", "stated for this individual", S["dx_urticaria"], hpo="Chronic urticaria", hpid="HP:0001025")
add(P, "hives", "observed", "stated for this individual", S["attacks"], sev="episodes occur when his skin is exposed to hot or cold temperatures or significant pressure", hpo="Urticaria", hpid="HP:0001025")
add(P, "angioedema", "observed", "stated for this individual", S["case_open"], onset="34 years of age", onset_iso="P34Y", sev="severe episodes (occurring every three to four months)", hpo="Angioedema", hpid="HP:0002273")
add(P, "fever", "observed", "stated for this individual", S["attacks"], onset="37 years of age", onset_iso="P37Y", sev="\u201cattacks\u201d approximately every two weeks", hpo="Fever", hpid="HP:0001945")
add(P, "diarrhea", "observed", "stated for this individual", S["attacks"], hpo="Diarrhea", hpid="HP:0002014")
add(P, "weakness", "observed", "stated for this individual", S["attacks"], hpo="Asthenia", hpid="HP:0025406")
add(P, "diaphoresis", "observed", "stated for this individual", S["attacks"], hpo="Hyperhidrosis", hpid="HP:0000975")
add(P, "dizziness when standing", "observed", "stated for this individual", S["dizzy"], hpo="Orthostatic hypotension", hpid="HP:0001278")
add(P, "elevated IgE", "observed", "stated for this individual", S["ige"], hpo="Elevated circulating IgE", hpid="HP:0410251")
add(P, "elevated tryptase", "observed", "stated for this individual", S["tryptase"], sev="ranged from 13.9 and 19.2 (<11.5 ng/mL)", hpo="Elevated circulating tryptase", hpid=None)
add(P, "elevated anti-IgE receptor antibody", "observed", "stated for this individual", S["antiige"], sev="elevated at 18.5% (reference range: <13%)", hpo=None, hpid=None)
add(P, "elevated C1q complement", "observed", "stated for this individual", S["antiige"], sev="elevated at 43 (12\u201322 mg/dL)", hpo=None, hpid=None)
add(P, "mild hearing loss", "observed", "stated for this individual", S["gjb2_proband"], hpo="Hearing impairment", hpid="HP:0000365")
add(P, "anaphylaxis", "observed", "stated for this individual", S["abstract_male"], sev="hospitalization due to hive-induced anaphylaxis", hpo="Anaphylaxis", hpid="HP:0025300")
add(P, "mastocytosis", "excluded", "stated for this individual", [S["dx_urticaria"], S["concl_bm"]], hpo=None, hpid=None)
add(P, "normal bone marrow biopsy", "excluded", "stated for this individual", S["bm_normal"], hpo=None, hpid=None)
add(P, "normal complete blood count (CBC) with differential", "excluded", "stated for this individual", S["bm_normal"], hpo=None, hpid=None)
add(P, "normal TSH", "excluded", "stated for this individual", S["tsh"], sev="2.0 (>20 years: 0.3\u20134.2 mIU/L)", hpo=None, hpid=None)

# mother
add(M, "chronic urticaria and angioedema", "excluded", "stated for this individual", S["concl_family"], hpo=None, hpid=None)
# daughter
add(D, "hives", "observed", "stated for this individual", S["daughter_detail"], hpo="Urticaria", hpid="HP:0001025")
add(D, "swelling of her hands and feet", "observed", "stated for this individual", S["daughter_detail"], hpo="Peripheral edema", hpid="HP:0011273")
add(D, "swelling of her feet after practice", "observed", "stated for this individual", S["daughter_gym"], sev="had to discontinue gymnastics", hpo="Edema of the lower limbs", hpid=None)
add(D, "hand swelling after playing the cello", "observed", "stated for this individual", S["daughter_cello"], hpo="Edema of the upper limbs", hpid=None)
# sister
add(SIS, "hives", "observed", "stated for this individual", S["fam_hist"], hpo="Urticaria", hpid="HP:0001025")
add(SIS, "angioedema", "observed", "stated for this individual", S["fam_hist"], hpo="Angioedema", hpid="HP:0002273")

# phenotype_checklist
CHECKLIST = ["oral ulcers", "genital ulcers", "gastrointestinal ulcers or inflammation", "recurrent fever",
 "arthritis or arthralgia", "uveitis or other ocular inflammation", "skin lesions (rash, folliculitis, erythema nodosum)",
 "autoimmune thyroiditis", "type 1 diabetes", "autoimmune hepatitis", "cytopenia (autoimmune)",
 "lymphoproliferation or lymphadenopathy", "central nervous system involvement", "recurrent infections",
 "elevated inflammatory markers (CRP/ESR)", "autoantibodies (ANA/other)", "growth failure",
 "pericarditis or other serositis", "interstitial lung disease", "vasculitis"]

LABELSPAN = {
 P: "A 47-year-old Hispanic male was initially referred to the Mayo Clinic at 34 years of age",
 M: "The proband's mother was found to be negative for the p.R22Q variant (the proband's father was deceased)",
 D: "The proband's daughter, who was 12 years of age at the time of evaluation, had episodes of hives and swelling of her hands and feet.",
 SIS: "Interestingly, both the individual's 41-year-old sister and 12-year-old daughter were also affected with chronic urticaria and severe angioedema.",
}

STATUS = {
 P: {"skin lesions (rash, folliculitis, erythema nodosum)": ("observed", "stated for this individual", S["fig1_arrow"]),
     "autoantibodies (ANA/other)": ("observed", "stated for this individual", S["antiige"])},
 D: {"skin lesions (rash, folliculitis, erythema nodosum)": ("observed", "stated for this individual", S["fig1_arrow"])},
 SIS: {"skin lesions (rash, folliculitis, erythema nodosum)": ("observed", "stated for this individual", S["fig1_arrow"])},
 M: {},
}

rows_checklist = []
for label in [P, M, D, SIS]:
    for feat in CHECKLIST:
        if feat in STATUS[label]:
            st, basis, span = STATUS[label][feat]
        else:
            st, basis, span = "not reported", "not reported", None
        rows_checklist.append({
            "pmid": c(PMID, HDR),
            "individual_label_in_paper": c(label, LABELSPAN[label]),
            "checklist_feature": {"value": feat, "span": None},
            "status": {"value": st, "span": span},
            "evidence_basis": {"value": basis, "span": None},
        })

out = {
 "pmid": PMID,
 "instructions_version": "extract_v6",
 "reports_individuals_with_tnfaip3_variant": True,
 "relevance_note": "The report ties an in-scope person to a TNFAIP3 variant: \u201cWES of the proband uncovered a novel variant inTNFAIP3 (Chr6(GRCh38): g.137871292G>A; NM_001270507.1: c.65G>A; p.(Arg22Gln))\u201d, found in the proband and two affected relatives, though the authors classify it as a VUS and do not diagnose HA20.",
 "method_note": "Case report of one family; no tables and no supplementary files, so all cells come from the narrative text and were transcribed by hand (no script). Four in-scope people: proband (called only 'the proband'/'the patient' in the text, so labelled 'P1' by label rule 5/6), his mother, daughter and sister. The deceased father is mentioned but described only as deceased, with no individual-level fact beyond that and no variant, so he has no row. No relative is named as a variant carrier for the father. The paper never uses a family number; 'Family 1' was entered only because the schema requires a value and the pedigree is Figure 1 (a made-up label) - this is a guess and should be checked. Figure 1 itself is not available in the Markdown, so the pedigree cannot be read; the arrow ('An arrow indicates the proband') is the only basis for is_proband. Zygosity 'heterozygous' for the proband rests on the abstract sentence 'revealed a heterozygous variant of uncertain significance in exon 2 ofTNFAIP3 ... in all affected members' (a named group that includes him), not on his own sentence; the abstract also calls the variant 'in exon 2'. Inheritance was left 'not reported' for everyone: the mother is negative and the father was deceased and untested, so neither 'de novo' nor 'inherited' is stated; the parents' p.R22Q carrier status could not be checked (not assessed). Variant type 'missense' is taken from the general statements 'no known association between missense variants inTNFAIP3' and the title ('a Missense Variant'), which do not name a group of people; it is recorded anyway because the variant is described as a semiconservative amino acid substitution p.(Arg22Gln)/p.R22Q, and this derivation from the protein change is flagged as an uncertainty. For the daughter and sister the cDNA string 'c.65G>A' has no individual-level span: the paper only says the p.R22Q variant (or the variant of uncertain significance in the abstract) was found in them. Gene symbol for those rows is quoted from the abstract sentence. GJB2 rows are included because the paper attributes that variant unambiguously to the proband and his mother; its frameshift class is taken from the printed 'fs' protein notation, and the proband's GJB2 zygosity was not printed (the 'heterozygous' statement names only the mother). Checklist statuses: 'skin lesions (rash, folliculitis, erythema nodosum)' was marked observed for the proband, daughter and sister from the title phrase 'a Family with Chronic Urticaria and Angioedema' (urticaria is a rash); this is debatable and could be 'not reported'. The proband's 'fever' in his attacks was not counted as 'recurrent fever' in the checklist because recurrence is not stated, so that item is 'not reported' while a phenotypic_features row records the fever. 'autoantibodies (ANA/other)' was marked observed for the proband from 'His anti-IgE receptor antibody was elevated at 18.5%'. The c.65G>A part of the proband's variant was entered as 'not reported' for the daughter and sister: the paper ties it to them only as 'the p.R22Q variant' / 'the VUS'. Normal/negative findings were recorded per D-27 as the abnormality ruled out (mastocytosis, normal bone marrow biopsy, normal CBC, normal TSH) with the paper's own words as span. No contradictions were found between sections. No group statements were used to exclude any checklist feature. Two additional fields are recorded although the paper states them only for the variant in general rather than for this person: the missense class and the ACMG-based VUS classification (the VUS sentence names only the c.65G>A (p.R22Q) variant, which is the proband's).",
 "tables": {
   "publications": rows_publications,
   "individuals": rows_individuals,
   "variants": rows_variants,
   "phenotypic_features": pf,
   "phenotype_checklist": rows_checklist,
 },
}

path = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/29682366.json"
with open(path, "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)

print({k: len(v) for k, v in out["tables"].items()})
