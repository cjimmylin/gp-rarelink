"""Offline parsing of PubMed efetch XML into manifest rows."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class PubmedRecord:
    pmid: str
    title: str = ""
    abstract: str = ""
    journal: str = ""
    year: str = ""
    first_author: str = ""
    doi: str = ""
    pmcid: str = ""
    publication_types: list[str] = field(default_factory=list)
    languages: list[str] = field(default_factory=list)


def _text(el: ET.Element | None) -> str:
    if el is None:
        return ""
    return "".join(el.itertext()).strip()


def parse_pubmed_xml(root: ET.Element) -> list[PubmedRecord]:
    records: list[PubmedRecord] = []
    for art in root.findall(".//PubmedArticle"):
        med = art.find("MedlineCitation")
        if med is None:
            continue
        pmid = _text(med.find("PMID"))
        rec = PubmedRecord(pmid=pmid)
        a = med.find("Article")
        if a is not None:
            rec.title = _text(a.find("ArticleTitle"))
            rec.abstract = "\n".join(_text(t) for t in a.findall("Abstract/AbstractText"))
            rec.journal = _text(a.find("Journal/Title"))
            rec.year = _text(a.find("Journal/JournalIssue/PubDate/Year")) or _text(a.find("Journal/JournalIssue/PubDate/MedlineDate"))[:4]
            first = a.find("AuthorList/Author")
            if first is not None:
                rec.first_author = _text(first.find("LastName")) or _text(first.find("CollectiveName"))
            rec.publication_types = [_text(pt) for pt in a.findall("PublicationTypeList/PublicationType")]
            rec.languages = [_text(l) for l in a.findall("Language")]
        for aid in art.findall("PubmedData/ArticleIdList/ArticleId"):
            kind = aid.get("IdType")
            if kind == "doi" and not rec.doi:
                rec.doi = _text(aid)
            elif kind == "pmc" and not rec.pmcid:
                rec.pmcid = _text(aid)
        records.append(rec)
    return records


REVIEW_TYPES = {"Review", "Systematic Review", "Meta-Analysis"}
CASE_TYPES = {"Case Reports"}


def study_type_from_pubtypes(pubtypes: list[str]) -> str | None:
    """Cheap first pass from MeSH publication types; None means 'ask the classifier'."""
    s = set(pubtypes)
    if s & REVIEW_TYPES:
        return "review/meta-analysis"
    if s & CASE_TYPES:
        return "case report"
    return None
