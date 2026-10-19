"""Stage 6 harness helpers: intervals, ClinVar label parsing, protein check."""

from pipeline.harness.concordance import author_class, protein_check, protein_short, summarise, wilson
from pipeline.harness.snapshot_reference import classify, names_any


def test_wilson_reference_values():
    # Wilson score interval, z = 1.96
    w = wilson(40, 95)
    assert w["share"] == 0.421053 and w["ci95"] == [0.326738, 0.521504]
    assert wilson(0, 0)["ci95"] is None


def test_clinvar_labels():
    assert classify("Pathogenic") == "P"
    assert classify("Pathogenic/Likely pathogenic") == "P/LP"
    assert classify("Likely pathogenic") == "LP"
    assert classify("Conflicting classifications of pathogenicity") == "conflicting"
    assert classify("VUS-mid") == "VUS"
    assert classify("-") == "no germline classification"
    assert names_any("MedGen:CN169374|MONDO:MONDO:0800045,MedGen:C4225218,OMIM:616744", {"MONDO:0800045"})
    assert not names_any("MedGen:CN169374", {"OMIM:616744"})


def test_protein_check_and_author_classes():
    assert protein_short("NP_001257437.1:p.(Leu227Ter)") == "L227*"
    assert protein_short("p.L227X") == "L227*"
    assert protein_short("NP_001257437.1:p.(Phe224SerfsTer4)") == "F224fs"
    assert protein_check({"p.F224Sfs*4"}, "NP_001257437.1:p.(Phe224SerfsTer4)") == "agrees"
    assert protein_check(set(), "p.(Leu227Ter)") == "no stated protein"
    assert protein_check({"p.S376fs"}, "p.(Val377fs)").startswith("differs")
    assert author_class("likely pathogenic") == "P/LP" and author_class("variant of uncertain significance") == "VUS"
    assert summarise({"P/LP", "VUS"}) == "mixed P/LP and VUS" and summarise({"none"}) == "not stated"
