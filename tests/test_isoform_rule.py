"""D-43: isoform-sensitive positions in Stage 4 normalization (no network)."""

from pipeline.extract.isoform_regions import c_boundaries, divergence
from pipeline.extract.normalize_variants import isoform_rule, label_text

LAMP2_RULES = [{"gene": "LAMP2", "mane": "NM_002294.3", "from_cdna": 1094,
                "alternatives": [{"transcript": "NM_013995.2", "name": "LAMP2B (exon 9b)", "labels": r"\b(?:E|ex\.?|exon\s*)9b\b|\bLAMP-?2B\b"},
                                 {"transcript": "NM_001122606.1", "name": "LAMP2C (exon 9c)", "labels": r"\b(?:E|ex\.?|exon\s*)9c\b|\bLAMP-?2C\b"}],
                "mane_labels": r"\b(?:E|ex\.?|exon\s*)9a\b|\bLAMP-?2A\b"}]

# exon ends and CDS as read from the RefSeq mRNA records on 2026-10-28 (transcript coordinates)
LAMP2A = ([(1, 191), (192, 310), (311, 524), (525, 683), (684, 868), (869, 991), (992, 1055), (1056, 1220), (1221, 6535)], (128, 1360))
LAMP2B = ([(1, 244), (245, 363), (364, 577), (578, 736), (737, 921), (922, 1044), (1045, 1108), (1109, 1273), (1274, 4073)], (181, 1413))
GFAP_A = ([(1, 475), (476, 536), (537, 632), (633, 794), (795, 920), (921, 1141), (1142, 1185), (1186, 1271), (1272, 5501)], (15, 1313))
GFAP_E = ([(1, 475), (476, 536), (537, 632), (633, 794), (795, 920), (921, 1141), (1142, 1185), (1186, 1774)], (15, 1310))


def test_divergence_from_exon_structures():
    assert c_boundaries(*LAMP2A)[:8] == c_boundaries(*LAMP2B)[:8] == [64, 183, 397, 556, 741, 864, 928, 1093]
    assert divergence(LAMP2A, LAMP2B) == 1094   # exon 9a vs 9b
    assert divergence(GFAP_A, GFAP_E) == 1172   # exons 8-9 vs exon 7A


def test_rule_does_not_apply_below_the_boundary_or_in_the_shared_intron():
    assert isoform_rule("c.1093del", "", LAMP2_RULES) == (None, "")
    assert isoform_rule("c.1093+2440_1093+2441del", "", LAMP2_RULES) == (None, "")
    assert isoform_rule("c.928G>A", "exon 9b", LAMP2_RULES) == (None, "")
    assert isoform_rule("", "", LAMP2_RULES) == (None, "")


def test_label_selects_the_transcript():
    tx, note = isoform_rule("c.1097_1098delAA", "| 1 | E9b | c.1097_1098 delAA |", LAMP2_RULES)
    assert tx == "NM_013995.2" and "LAMP2B" in note
    tx, note = isoform_rule("c.1150G>C", "LAMP2B c.1150G>C", LAMP2_RULES)
    assert tx == "NM_013995.2"
    tx, note = isoform_rule("c.1150G>C", "exon 9A", LAMP2_RULES)
    assert tx == "NM_002294.3" and "MANE" in note
    tx, note = isoform_rule("c.*12A>G", "exon 9c", LAMP2_RULES)   # 3' UTR lies beyond every coding boundary
    assert tx == "NM_001122606.1"


def test_no_label_is_ambiguous():
    tx, note = isoform_rule("c.1150G>C", "c.1150 G>C missense", LAMP2_RULES)
    assert tx is None and note.startswith("ambiguous") and "NM_013995.2" in note and "D-43" in note


def test_label_text_reads_values_and_spans():
    row = {"variant_original_string": {"value": "c.1097_1098 delAA", "span": "| 1 | E9b | c.1097_1098 delAA |"},
           "transcript_as_stated": {"value": "not reported", "span": None},
           "cdna_hgvs_as_stated": {"value": "c.1097_1098 delAA", "span": ["| 1 | E9b | c.1097_1098 delAA |"]}}
    t = label_text(row)
    assert "E9b" in t and "not reported" not in t
