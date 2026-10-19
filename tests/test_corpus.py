import xml.etree.ElementTree as ET
from pathlib import Path

from pipeline.extract.corpus.jats_to_markdown import jats_to_markdown
from pipeline.extract.corpus.pubmed_parse import parse_pubmed_xml, study_type_from_pubtypes

FIX = Path(__file__).parent / "fixtures"


def test_jats_to_markdown_keeps_header_tables_captions_and_refs():
    art = jats_to_markdown((FIX / "sample_jats.xml").read_bytes())
    md = art.to_markdown()
    assert md.startswith("PMID: 99999999\n")
    assert "PMCID: PMC9999999" in md and "DOI: 10.1000/test.1" in md
    assert "# A novel TNFAIP3 variant in a family" in md
    assert "## Abstract" in md and "two patients with a heterozygous variant" in md
    assert "## Case presentation" in md
    assert "c.1245_1248delTTTA (p.Phe415fs)" in md and "NM_006290.3" in md
    assert "### Table 1: Clinical features" in md
    assert "| Patient | Sex | Oral ulcers | Fever |" in md
    assert "| II-1 | F | + | - |" in md and "| I-2 | M | + | ND |" in md
    assert "Table notes: ND, not determined." in md
    assert "**Figure 1**: Pedigree of the family." in md
    assert "## References" in md and "[1] Zhou Q, 2016, Loss-of-function mutations in TNFAIP3, Nat Genet PMID:26642243" in md
    assert art.authors == ["Doe Jane", "Roe Richard"] and art.year == "2021"
    assert art.n_tables == 1 and art.n_figures == 1


def test_pubmed_xml_parse_and_provisional_type():
    xml = b"""<PubmedArticleSet><PubmedArticle><MedlineCitation><PMID>26642243</PMID><Article>
      <Journal><Title>Nature genetics</Title><JournalIssue><PubDate><Year>2016</Year></PubDate></JournalIssue></Journal>
      <ArticleTitle>Loss-of-function mutations in TNFAIP3 leading to A20 haploinsufficiency</ArticleTitle>
      <Abstract><AbstractText>Text.</AbstractText></Abstract>
      <AuthorList><Author><LastName>Zhou</LastName><ForeName>Qing</ForeName></Author></AuthorList>
      <Language>eng</Language>
      <PublicationTypeList><PublicationType>Journal Article</PublicationType><PublicationType>Case Reports</PublicationType></PublicationTypeList>
      </Article></MedlineCitation><PubmedData><ArticleIdList><ArticleId IdType="doi">10.1038/ng.3459</ArticleId><ArticleId IdType="pmc">PMC4777523</ArticleId></ArticleIdList></PubmedData></PubmedArticle></PubmedArticleSet>"""
    recs = parse_pubmed_xml(ET.fromstring(xml))
    assert len(recs) == 1
    r = recs[0]
    assert r.pmid == "26642243" and r.doi == "10.1038/ng.3459" and r.pmcid == "PMC4777523"
    assert r.first_author == "Zhou" and r.year == "2016"
    assert study_type_from_pubtypes(r.publication_types) == "case report"
    assert study_type_from_pubtypes(["Journal Article", "Systematic Review"]) == "review/meta-analysis"
    assert study_type_from_pubtypes(["Journal Article"]) is None


ROWSPAN_JATS = b"""<?xml version="1.0"?>
<article><front><article-meta><article-id pub-id-type="pmid">1</article-id>
<title-group><article-title>T</article-title></title-group></article-meta></front>
<body><table-wrap><label>Table 1</label><table>
<thead><tr><th></th><th>Gender</th><th>Manifestations</th><th>Therapy</th></tr></thead>
<tbody>
<tr><td rowspan="2">Pt 1</td><td rowspan="2">F</td><td>Oral ulcers</td><td>None</td></tr>
<tr><td>Thyroiditis</td><td>L-Thyroxine</td></tr>
<tr><td>Pt 2</td><td>F</td><td colspan="2">Diabetes</td></tr>
</tbody></table></table-wrap></body></article>"""


def test_rowspan_and_colspan_keep_rows_aligned():
    md = jats_to_markdown(ROWSPAN_JATS).to_markdown()
    rows = [l for l in md.splitlines() if l.startswith("| ") and "---" not in l]
    assert rows[1] == "| Pt 1 | F | Oral ulcers | None |"
    # the second row of Pt 1 keeps the patient label and gender instead of shifting left
    assert rows[2] == "| Pt 1 | F | Thyroiditis | L-Thyroxine |"
    # a colspan repeats its text in every column it covers (since 2026-10-19)
    assert rows[3] == "| Pt 2 | F | Diabetes | Diabetes |"


FLOATS_JATS = b"""<?xml version="1.0"?>
<article><front><article-meta><article-id pub-id-type="pmid">2</article-id>
<title-group><article-title>T</article-title></title-group></article-meta></front>
<body><sec><title>Case</title><p>Clinical details are in <xref ref-type="table" rid="t1">Table 1</xref>.</p></sec></body>
<back><ref-list><ref id="r1"><mixed-citation>Ref one.</mixed-citation></ref></ref-list></back>
<floats-group>
<table-wrap id="t1"><label>Table 1</label><caption><p>Patients</p></caption><table>
<tr><th>Patient</th><th>Variant</th></tr><tr><td>P1</td><td>c.811C&gt;T</td></tr></table></table-wrap>
<fig id="f1"><label>Figure 1</label><caption><p>Pedigree.</p></caption></fig>
</floats-group></article>"""


def test_tables_in_floats_group_are_kept():
    art = jats_to_markdown(FLOATS_JATS)
    md = art.to_markdown()
    assert "### Table 1: Patients" in md
    assert "| P1 | c.811C>T |" in md
    assert "**Figure 1**: Pedigree." in md
    # floating tables sit after the body text and before the references
    assert md.index("Clinical details") < md.index("### Table 1") < md.index("## References")
    assert art.n_tables == 1 and art.n_figures == 1


NESTED_REFS_JATS = b"""<?xml version="1.0"?>
<article xmlns:xlink="http://www.w3.org/1999/xlink"><front><article-meta><article-id pub-id-type="pmid">3</article-id>
<title-group><article-title>T</article-title></title-group></article-meta></front>
<body><p>Text.</p></body>
<back><sec><title>References</title><ref-list>
<ref id="bib1"><mixed-citation><named-content content-type="citation-string">Zhou Q. Loss-of-function mutations in TNFAIP3. 2016.</named-content><ext-link ext-link-type="pmid" xlink:href="26642243"/></mixed-citation></ref>
<ref id="bib2"><label>2</label><mixed-citation>Aeschlimann FA. A20 haploinsufficiency. 2018.</mixed-citation></ref>
</ref-list></sec></back></article>"""


def test_nested_reference_list_keeps_one_line_per_reference():
    md = jats_to_markdown(NESTED_REFS_JATS).to_markdown()
    assert "[1] Zhou Q. Loss-of-function mutations in TNFAIP3. 2016. PMID:26642243" in md
    assert "[2] Aeschlimann FA. A20 haploinsufficiency. 2018." in md
