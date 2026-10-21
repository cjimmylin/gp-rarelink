import json, os, sys

PAPER = "/home/user/gp-rarelink/data/literature/ha20/fulltext_md/35760412.md"
OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/35760412.json"
paper = open(PAPER, encoding="utf-8").read()

PMID = "35760412"
SP_PMID = "PMID: 35760412"

def C(v, s=None):
    return {"value": v, "span": s}

MISS_T = C("not reported", None)      # text / enum missing
MISS_N = C(None, None)                # numeric / date missing

# ---------------- publications ----------------
pub = {
 "pmid": C(PMID, SP_PMID),
 "first_author": C("Jo", "Jo Kyo Jin"),
 "year": C(2023, "Clinical and Experimental Pediatrics (2023)"),
 "study_type": C("case report", "A 9-year-old girl presented with a 10-day history of fever and tender cervical and right axillary lymphadenopathy."),
 "n_patients_reported": C(1, "It revealed a nonsense mutation in the tumor necrosis factor (TNF)-\u03b1-induced protein 3 gene, leading to the diagnosis of haploinsufficiency A20 (HA20)"),
 "cohort_size_as_stated": MISS_N,
 "cites_prior_report_of_same_patients": C(False, None),
 "prior_report_citation": MISS_T,
}

# ---------------- individuals ----------------
SP_FIRST = "A 9-year-old girl presented with a 10-day history of fever and tender cervical and right axillary lymphadenopathy."
SP_ONSET = "The patient had been experiencing periodic fever and oral and genital ulcers since the age of 1 month."
SP_FATHER = "Detailed family history revealed that her father had recurrent fever and tonsillitis at preschool age."
SP_SISTER = "her parents and younger sister"

pat = {
 "pmid": C(PMID, SP_PMID),
 "individual_label_in_paper": C("patient", SP_FIRST),
 "family_label_in_paper": MISS_T,
 "is_proband": C(True, "The c.547C>T variation of the proband was present in our patient"),
 "sex": C("female", "A 9-year-old girl"),
 "age_at_onset_original_text": C("the age of 1 month", SP_ONSET),
 "age_at_onset_iso8601": C("P1M", SP_ONSET),
 "age_at_last_evaluation_original_text": C("9 years", "A 9-year-old girl presented with a 10-day history of fever"),
 "age_at_last_evaluation_iso8601": C("P9Y", "A 9-year-old girl presented with a 10-day history of fever"),
 "age_at_diagnosis_original_text": MISS_T,
 "age_at_diagnosis_iso8601": MISS_N,
 "ethnicity_or_country": C("Korea", "only 2 patients, including our case, have been diagnosed with HA20 in Korea"),
 "consanguinity": MISS_T,
 "vital_status": C("alive", "Currently, we are considering treatments with immune suppressants such as steroids and biologics."),
 "deceased_age_iso8601": MISS_N,
 "cause_of_death": MISS_T,
 "treatment_summary": C(
   "tonsillectomy at 5 years of age; antipyretics; antibiotic treatment was ineffective; colchicine was started; considering treatments with immune suppressants such as steroids and biologics",
   ["after tonsillectomy at 5 years of age",
    "Antibiotic treatment was ineffective.",
    "Colchicine was started, and 9 months after treatment, oral and genital ulcers disappeared.",
    "Currently, we are considering treatments with immune suppressants such as steroids and biologics."]),
 "disease_label_as_stated": C("haploinsufficiency A20 (HA20)", "leading to the diagnosis of haploinsufficiency A20 (HA20)"),
 "clinical_diagnosis_basis": C(
   "NGS for genes related to periodic fever and autoinflammatory syndromes; it revealed a nonsense mutation in the tumor necrosis factor (TNF)-\u03b1-induced protein 3 gene, leading to the diagnosis of HA20",
   ["Next-generation sequencing (NGS) for genes related to periodic fever and autoinflammatory syndromes was conducted to identify a possible genetic disorder.",
    "It revealed a nonsense mutation in the tumor necrosis factor (TNF)-\u03b1-induced protein 3 gene, leading to the diagnosis of haploinsufficiency A20 (HA20) (Fig. 1)."]),
 "source_reference_in_review": MISS_T,
}

father = {
 "pmid": C(PMID, SP_PMID),
 "individual_label_in_paper": C("father of patient", SP_FATHER),
 "family_label_in_paper": MISS_T,
 "is_proband": C(False, SP_FATHER),
 "sex": C("male", "her father had recurrent fever and tonsillitis at preschool age"),
 "age_at_onset_original_text": C("preschool age", SP_FATHER),
 "age_at_onset_iso8601": MISS_N,
 "age_at_last_evaluation_original_text": MISS_T,
 "age_at_last_evaluation_iso8601": MISS_N,
 "age_at_diagnosis_original_text": MISS_T,
 "age_at_diagnosis_iso8601": MISS_N,
 "ethnicity_or_country": MISS_T,
 "consanguinity": MISS_T,
 "vital_status": MISS_T,
 "deceased_age_iso8601": MISS_N,
 "cause_of_death": MISS_T,
 "treatment_summary": MISS_T,
 "disease_label_as_stated": MISS_T,
 "clinical_diagnosis_basis": MISS_T,
 "source_reference_in_review": MISS_T,
}

sister = dict(father)
sister.update({
 "individual_label_in_paper": C("sister of patient", SP_SISTER),
 "is_proband": C(False, SP_SISTER),
 "sex": C("female", SP_SISTER),
 "age_at_onset_original_text": MISS_T,
})

individuals = [pat, father, sister]

# ---------------- variants ----------------
variants = [{
 "pmid": C(PMID, SP_PMID),
 "individual_label_in_paper": C("patient", SP_FIRST),
 "gene_symbol_as_stated": C("TNFAIP3", "the TNFAIP3 (c.547C>T, p.Arg183^*) gene mutation is already known to cause HA20"),
 "variant_original_string": C("c.547C>T", "The c.547C>T variation of the proband was present in our patient"),
 "transcript_as_stated": MISS_T,
 "cdna_hgvs_as_stated": C("c.547C>T", "the TNFAIP3 (c.547C>T, p.Arg183^*) gene mutation"),
 "protein_hgvs_as_stated": C("p.Arg183^*", "the TNFAIP3 (c.547C>T, p.Arg183^*) gene mutation"),
 "genomic_coordinates_as_stated": MISS_N,
 "variant_type_as_stated": C("nonsense", "It revealed a nonsense mutation in the tumor necrosis factor (TNF)-\u03b1-induced protein 3 gene"),
 "zygosity": MISS_T,
 "inheritance": MISS_T,
 "parental_testing_statement": C("We recommended NGS for her parents and younger sister, but her parents refused.", "We recommended NGS for her parents and younger sister, but her parents refused."),
 "functional_evidence_statement": MISS_T,
 "pathogenicity_as_stated_by_authors": C("known to cause HA20", "the TNFAIP3 (c.547C>T, p.Arg183^*) gene mutation is already known to cause HA20"),
 "acmg_criteria_as_stated": MISS_T,
}]

# ---------------- phenotypic_features ----------------
def F(label, feature, status, basis, span, onset=None, onset_iso=None, detail=None, hpo=None, hpo_id=None):
    return {
     "pmid": C(PMID, SP_PMID),
     "individual_label_in_paper": C(label, span if isinstance(span, str) else span[0]),
     "feature_text_as_stated": C(feature, span),
     "status": C(status, span),
     "evidence_basis": C(basis, span),
     "onset_original_text": C(onset, span if onset else None) if onset else MISS_N,
     "onset_iso8601": C(onset_iso, span) if onset_iso else MISS_N,
     "severity_or_detail": C(detail, span) if detail else MISS_N,
     "hpo_label_candidate": C(hpo, None),
     "hpo_id_candidate": C(hpo_id, None),
    }

pheno = [
 F("patient", "periodic fever", "observed", "stated for this individual",
   [SP_ONSET, "Initially, the fever recurred every 1 or 2 months; however, after tonsillectomy at 5 years of age, it recurred every 3 or 4 months."],
   onset="the age of 1 month", onset_iso="P1M", detail="recurred every 3 or 4 months", hpo="Recurrent fever"),
 F("patient", "oral ulcers", "observed", "stated for this individual",
   [SP_ONSET, "Colchicine was started, and 9 months after treatment, oral and genital ulcers disappeared."],
   onset="the age of 1 month", onset_iso="P1M", hpo="Oral ulcer"),
 F("patient", "genital ulcers", "observed", "stated for this individual",
   [SP_ONSET, "Colchicine was started, and 9 months after treatment, oral and genital ulcers disappeared."],
   onset="the age of 1 month", onset_iso="P1M", hpo="Genital ulcer"),
 F("patient", "tender cervical and right axillary lymphadenopathy", "observed", "stated for this individual", SP_FIRST, hpo="Lymphadenopathy"),
 F("patient", "diarrhea", "observed", "stated for this individual",
   "She experienced diarrhea during fever and a skin rash appeared after the resolution of fever.", detail="during fever"),
 F("patient", "skin rash", "observed", "stated for this individual",
   "She experienced diarrhea during fever and a skin rash appeared after the resolution of fever.",
   detail="appeared after the resolution of fever", hpo="Skin rash"),
 F("patient", "anal ulcer", "observed", "stated for this individual", "Moreover, an anal ulcer developed.", hpo="Anal ulcer"),
 F("patient", "necrotizing lymphadenitis", "observed", "stated for this individual",
   "Axillary lymph node biopsy was performed, which demonstrated necrotizing lymphadenitis suggestive of Kikuchi disease."),
 F("patient", "white blood cell (WBC) count, erythrocyte sedimentation rate (ESR), and C-reactive protein (CRP) levels became elevated",
   "observed", "stated for this individual",
   "During fever, white blood cell (WBC) count, erythrocyte sedimentation rate (ESR), and C-reactive protein (CRP) levels became elevated.",
   hpo="Elevated inflammatory marker"),
 F("patient", "positive ANA", "observed", "stated for this individual",
   "| ANA | 1:640, Positive |  | 1:320, Positive |", detail="1:640", hpo="Antinuclear antibody positivity"),
 F("patient", "positive ANCA", "excluded", "stated for this individual", "| ANCA | Negative |  | Negative |"),
 F("patient", "positive anti-RNP antibody", "excluded", "stated for this individual", "| Anti-RNP Ab | Negative |  | Negative |"),
 F("patient", "positive anti-Smith antibody", "excluded", "stated for this individual", "| Anti-Smith Ab | Negative |  | Negative |"),
 F("patient", "positive anti-Ro antibody", "excluded", "stated for this individual", "| Anti-Ro | Negative |  | Negative |"),
 F("patient", "positive anti-La antibody", "excluded", "stated for this individual", "| Anti-La | Negative |  | Negative |"),
 F("patient", "uveitis", "excluded", "stated for this individual",
   "After the diagnosis of HA20, an ophthalmic examination was performed and no uveitis was observed."),
 F("father of patient", "recurrent fever", "observed", "stated for this individual", SP_FATHER, hpo="Recurrent fever"),
 F("father of patient", "recurrent diarrhea", "excluded", "stated for this individual",
   "However, he did not have a history of recurrent diarrhea or arthritis."),
 F("father of patient", "arthritis", "excluded", "stated for this individual",
   "However, he did not have a history of recurrent diarrhea or arthritis."),
]

# ---------------- phenotype_checklist ----------------
CHECK = ["oral ulcers","genital ulcers","gastrointestinal ulcers or inflammation","recurrent fever",
 "arthritis or arthralgia","uveitis or other ocular inflammation","skin lesions (rash, folliculitis, erythema nodosum)",
 "autoimmune thyroiditis","type 1 diabetes","autoimmune hepatitis","cytopenia (autoimmune)",
 "lymphoproliferation or lymphadenopathy","central nervous system involvement","recurrent infections",
 "elevated inflammatory markers (CRP/ESR)","autoantibodies (ANA/other)","growth failure",
 "pericarditis or other serositis","interstitial lung disease","vasculitis"]

pat_status = {
 "oral ulcers": "observed", "genital ulcers": "observed",
 "gastrointestinal ulcers or inflammation": "observed",
 "recurrent fever": "observed",
 "skin lesions (rash, folliculitis, erythema nodosum)": "observed",
 "lymphoproliferation or lymphadenopathy": "observed",
 "elevated inflammatory markers (CRP/ESR)": "observed",
 "autoantibodies (ANA/other)": "observed",
}
father_status = {"recurrent fever": "observed"}

checklist = []
for label, statuses in (("patient", pat_status), ("father of patient", father_status), ("sister of patient", {})):
    for feat in CHECK:
        st = statuses.get(feat, "not reported")
        basis = "stated for this individual" if st != "not reported" else "not reported"
        checklist.append({
         "pmid": C(PMID, SP_PMID),
         "individual_label_in_paper": C(label, None),
         "checklist_feature": C(feat, None),
         "status": C(st, None),
         "evidence_basis": C(basis, None),
        })

out = {
 "pmid": PMID,
 "instructions_version": "extract_v6",
 "reports_individuals_with_tnfaip3_variant": True,
 "relevance_note": "Single case report of a girl with HA20; the paper states: \"It revealed a nonsense mutation in the tumor necrosis factor (TNF)-\u03b1-induced protein 3 gene, leading to the diagnosis of haploinsufficiency A20 (HA20)\".",
 "method_note": ("Case report of one girl with HA20; one in-scope relative with individual-level facts (father: "
   "'her father had recurrent fever and tonsillitis at preschool age') and one relative described in relation to her "
   "without individual-level detail (younger sister, NGS recommended). Her mother is never described individually "
   "(only inside 'her parents', whose testing was refused), so no 'parent of patient' row was made, to avoid duplicating the father. "
   "A previously published patient cited as reference [8] ('only 2 patients, including our case, have been diagnosed with HA20 in Korea [8]') "
   "got no row: the paper gives no individual-level description of that person. The 89-patient review [4] and the 26-study review [5] are cited at group level only. "
   "Table 1 has time points (not patients) as columns, so no stacked-cell problem arose; values were transcribed by script from the Markdown and checked against the table. "
   "Judgements: the anal ulcer was mapped to checklist item 'gastrointestinal ulcers or inflammation' (perianal/anal ulcer); "
   "checklist item 'uveitis or other ocular inflammation' was left 'not reported' because the paper excludes only uveitis (narrower than the composite), "
   "while the narrower fact 'no uveitis' is recorded in phenotypic_features; similarly the father's 'did not have ... arthritis' does not exclude the composite "
   "'arthritis or arthralgia'. Routine negative antibodies in Table 1 are recorded as excluded abnormalities (e.g. 'positive ANCA'). "
   "The c.547C>T variant is described for the patient only; zygosity and inheritance are 'not reported' because the parents refused testing. "
   "'known to cause HA20' was recorded as the authors' pathogenicity statement for this exact variant. "
   "publications.cohort_size_as_stated is null: the authors state no total number of study patients. "
   "cites_prior_report_of_same_patients = false (no statement that these patients were reported earlier). No contradictions found in the paper."),
 "tables": {
   "publications": [pub],
   "individuals": individuals,
   "variants": variants,
   "phenotypic_features": pheno,
   "phenotype_checklist": checklist,
 }
}

# ---------------- validation ----------------
def spans_of(o):
    res = []
    if isinstance(o, dict):
        for k, v in o.items():
            res += spans_of(v)
    elif isinstance(o, list):
        for v in o:
            res += spans_of(v)
    return res

bad = []
def check(node, path=""):
    if isinstance(node, dict):
        for k, v in node.items():
            check(v, path + "/" + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            check(v, path + "/" + str(i))
    else:
        return

# collect all span strings explicitly
def walk(obj):
    if isinstance(obj, dict):
        if set(obj.keys()) == {"value", "span"}:
            s = obj["span"]
            if isinstance(s, str):
                yield s
            elif isinstance(s, list):
                for x in s:
                    yield x
            return
        for v in obj.values():
            yield from walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from walk(v)

for s in walk(out):
    if s not in paper:
        bad.append(s)

# schema field completeness
schema = json.load(open("/home/user/gp-rarelink/pipeline/extract/claude_code/schema_ha20_v5.json", encoding="utf-8"))
for t in schema["tables"]:
    name = t["name"]
    fields = [f["name"] for f in t["fields"]]
    for row in out["tables"][name]:
        missing = [f for f in fields if f not in row]
        extra = [f for f in row if f not in fields]
        if missing or extra:
            bad.append("FIELD PROBLEM %s: missing=%s extra=%s" % (name, missing, extra))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as fh:
    json.dump(out, fh, ensure_ascii=False, indent=1)
json.load(open(OUT, encoding="utf-8"))

print("span failures:", len(bad))
for b in bad:
    print(repr(b))
for k, v in out["tables"].items():
    print(k, len(v))
