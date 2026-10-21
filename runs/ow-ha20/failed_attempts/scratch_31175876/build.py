import json, os

SCRATCH = "/tmp/openweight_scratch/ow-ha20/31175876"
OUT = "/home/user/gp-rarelink/data/extracted/ha20/ow-ha20/per_paper/31175876.json"
PMID = "31175876"

with open(os.path.join(SCRATCH, "part1.json")) as fh:
    data = json.load(fh)

features = [
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

# (individual label, feature, status, evidence_basis, span or list of spans)
S = "stated for this individual"
rows = [
 ("III.1","oral ulcers","observed",S,"she had occasional mouth ulcers but no genital ulcers"),
 ("III.1","genital ulcers","excluded",S,"but no genital ulcers"),
 ("III.1","uveitis or other ocular inflammation","observed",S,"presented with left-sided focal seizures and hemiparesis, uveitis, and cognitive decline"),
 ("III.1","central nervous system involvement","observed",S,"We report a case of TNFAIP3-mediated autoinflammation manifesting as progressive neuroinflammation."),
 ("III.1","elevated inflammatory markers (CRP/ESR)","observed",S,"She had a modestly increased erythrocyte sedimentation rate of 25 mm/h (normal range, <5 mm/h)"),
 ("III.1","autoantibodies (ANA/other)","excluded",S,"negative autoantibody screen results"),
 ("III.2","oral ulcers","not reported","not reported",None),
 ("III.2","genital ulcers","not reported","not reported",None),
 ("III.2","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("III.2","recurrent fever","not reported","not reported",None),
 ("III.2","arthritis or arthralgia","observed",S,"Her younger sister (subject III.2) had arthritis and a facial malar-type rash from the age of 6 months."),
 ("III.2","uveitis or other ocular inflammation","not reported","not reported",None),
 ("III.2","skin lesions (rash, folliculitis, erythema nodosum)","observed",S,"Her younger sister (subject III.2) had arthritis and a facial malar-type rash from the age of 6 months."),
 ("III.2","autoimmune thyroiditis","not reported","not reported",None),
 ("III.2","type 1 diabetes","not reported","not reported",None),
 ("III.2","autoimmune hepatitis","not reported","not reported",None),
 ("III.2","cytopenia (autoimmune)","not reported","not reported",None),
 ("III.2","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("III.2","central nervous system involvement","not reported","not reported",None),
 ("III.2","recurrent infections","not reported","not reported",None),
 ("III.2","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("III.2","autoantibodies (ANA/other)","not reported","not reported",None),
 ("III.2","growth failure","not reported","not reported",None),
 ("III.2","pericarditis or other serositis","not reported","not reported",None),
 ("III.2","interstitial lung disease","not reported","not reported",None),
 ("III.2","vasculitis","not reported","not reported",None),
 ("II.2","oral ulcers","observed",S,"Subject II.2 had mild oral ulceration."),
 ("II.2","genital ulcers","not reported","not reported",None),
 ("II.2","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("II.2","recurrent fever","not reported","not reported",None),
 ("II.2","arthritis or arthralgia","not reported","not reported",None),
 ("II.2","uveitis or other ocular inflammation","not reported","not reported",None),
 ("II.2","skin lesions (rash, folliculitis, erythema nodosum)","not reported","not reported",None),
 ("II.2","autoimmune thyroiditis","not reported","not reported",None),
 ("II.2","type 1 diabetes","not reported","not reported",None),
 ("II.2","autoimmune hepatitis","not reported","not reported",None),
 ("II.2","cytopenia (autoimmune)","not reported","not reported",None),
 ("II.2","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("II.2","central nervous system involvement","not reported","not reported",None),
 ("II.2","recurrent infections","not reported","not reported",None),
 ("II.2","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("II.2","autoantibodies (ANA/other)","not reported","not reported",None),
 ("II.2","growth failure","not reported","not reported",None),
 ("II.2","pericarditis or other serositis","not reported","not reported",None),
 ("II.2","interstitial lung disease","not reported","not reported",None),
 ("II.2","vasculitis","not reported","not reported",None),
 ("II.4","oral ulcers","not reported","not reported",None),
 ("II.4","genital ulcers","not reported","not reported",None),
 ("II.4","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("II.4","recurrent fever","not reported","not reported",None),
 ("II.4","arthritis or arthralgia","not reported","not reported",None),
 ("II.4","uveitis or other ocular inflammation","not reported","not reported",None),
 ("II.4","skin lesions (rash, folliculitis, erythema nodosum)","not reported","not reported",None),
 ("II.4","autoimmune thyroiditis","not reported","not reported",None),
 ("II.4","type 1 diabetes","not reported","not reported",None),
 ("II.4","autoimmune hepatitis","not reported","not reported",None),
 ("II.4","cytopenia (autoimmune)","not reported","not reported",None),
 ("II.4","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("II.4","central nervous system involvement","not reported","not reported",None),
 ("II.4","recurrent infections","not reported","not reported",None),
 ("II.4","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("II.4","autoantibodies (ANA/other)","not reported","not reported",None),
 ("II.4","growth failure","not reported","not reported",None),
 ("II.4","pericarditis or other serositis","not reported","not reported",None),
 ("II.4","interstitial lung disease","not reported","not reported",None),
 ("II.4","vasculitis","not reported","not reported",None),
 ("II.1","oral ulcers","not reported","not reported",None),
 ("II.1","genital ulcers","not reported","not reported",None),
 ("II.1","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("II.1","recurrent fever","not reported","not reported",None),
 ("II.1","arthritis or arthralgia","not reported","not reported",None),
 ("II.1","uveitis or other ocular inflammation","not reported","not reported",None),
 ("II.1","skin lesions (rash, folliculitis, erythema nodosum)","not reported","not reported",None),
 ("II.1","autoimmune thyroiditis","not reported","not reported",None),
 ("II.1","type 1 diabetes","not reported","not reported",None),
 ("II.1","autoimmune hepatitis","not reported","not reported",None),
 ("II.1","cytopenia (autoimmune)","not reported","not reported",None),
 ("II.1","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("II.1","central nervous system involvement","not reported","not reported",None),
 ("II.1","recurrent infections","not reported","not reported",None),
 ("II.1","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("II.1","autoantibodies (ANA/other)","not reported","not reported",None),
 ("II.1","growth failure","not reported","not reported",None),
 ("II.1","pericarditis or other serositis","not reported","not reported",None),
 ("II.1","interstitial lung disease","not reported","not reported",None),
 ("II.1","vasculitis","not reported","not reported",None),
 ("patient","oral ulcers","observed",S,"The patient presented with recurrent oral inflammation and penile ulceration"),
 ("patient","genital ulcers","observed",S,"The patient presented with recurrent oral inflammation and penile ulceration"),
 ("patient","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("patient","recurrent fever","not reported","not reported",None),
 ("patient","arthritis or arthralgia","not reported","not reported",None),
 ("patient","uveitis or other ocular inflammation","not reported","not reported",None),
 ("patient","skin lesions (rash, folliculitis, erythema nodosum)","not reported","not reported",None),
 ("patient","autoimmune thyroiditis","not reported","not reported",None),
 ("patient","type 1 diabetes","not reported","not reported",None),
 ("patient","autoimmune hepatitis","not reported","not reported",None),
 ("patient","cytopenia (autoimmune)","not reported","not reported",None),
 ("patient","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("patient","central nervous system involvement","excluded",S,"in a 4-year-old nonconsanguineous white male with HA20 without any neurological involvement (Fig 2, I)"),
 ("patient","recurrent infections","not reported","not reported",None),
 ("patient","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("patient","autoantibodies (ANA/other)","not reported","not reported",None),
 ("patient","growth failure","not reported","not reported",None),
 ("patient","pericarditis or other serositis","not reported","not reported",None),
 ("patient","interstitial lung disease","not reported","not reported",None),
 ("patient","vasculitis","not reported","not reported",None),
 ("father of patient","oral ulcers","not reported","not reported",None),
 ("father of patient","genital ulcers","not reported","not reported",None),
 ("father of patient","gastrointestinal ulcers or inflammation","not reported","not reported",None),
 ("father of patient","recurrent fever","not reported","not reported",None),
 ("father of patient","arthritis or arthralgia","not reported","not reported",None),
 ("father of patient","uveitis or other ocular inflammation","not reported","not reported",None),
 ("father of patient","skin lesions (rash, folliculitis, erythema nodosum)","not reported","not reported",None),
 ("father of patient","autoimmune thyroiditis","not reported","not reported",None),
 ("father of patient","type 1 diabetes","not reported","not reported",None),
 ("father of patient","autoimmune hepatitis","not reported","not reported",None),
 ("father of patient","cytopenia (autoimmune)","not reported","not reported",None),
 ("father of patient","lymphoproliferation or lymphadenopathy","not reported","not reported",None),
 ("father of patient","central nervous system involvement","not reported","not reported",None),
 ("father of patient","recurrent infections","not reported","not reported",None),
 ("father of patient","elevated inflammatory markers (CRP/ESR)","not reported","not reported",None),
 ("father of patient","autoantibodies (ANA/other)","not reported","not reported",None),
 ("father of patient","growth failure","not reported","not reported",None),
 ("father of patient","pericarditis or other serositis","not reported","not reported",None),
 ("father of patient","interstitial lung disease","not reported","not reported",None),
 ("father of patient","vasculitis","not reported","not reported",None),
]

checklist = []
for label, feat, status, basis, span in rows:
    checklist.append({
        "pmid": {"value": PMID, "span": "PMID: 31175876"},
        "individual_label_in_paper": {"value": label, "span": None},
        "checklist_feature": {"value": feat, "span": None},
        "status": {"value": status, "span": span},
        "evidence_basis": {"value": basis, "span": None},
    })

# sanity: all 20 features per individual, once
labels_order = ["III.1","III.2","II.2","II.4","II.1","patient","father of patient"]
assert len(checklist) == len(labels_order) * 20, len(checklist)
for lab in labels_order:
    fs = [r["checklist_feature"]["value"] for r in checklist if r["individual_label_in_paper"]["value"] == lab]
    assert fs == features, (lab, fs)
# every non-not-reported row has a span
for r in checklist:
    if r["status"]["value"] != "not reported":
        assert r["status"]["span"], r

data["tables"]["phenotype_checklist"] = checklist

with open(OUT, "w") as fh:
    json.dump(data, fh, indent=2, ensure_ascii=False)
    fh.write("\n")

print("checklist rows:", len(checklist))
print("individuals:", len(data["tables"]["individuals"]))
print("variants:", len(data["tables"]["variants"]))
print("phenotypic_features:", len(data["tables"]["phenotypic_features"]))
print("publications:", len(data["tables"]["publications"]))
