"""Convert a JATS/NLM XML article (PMC .nxml, Europe PMC fullTextXML) to Markdown.

Design goals (POC_DESIGN.md Stage 1 step 3): keep headings, paragraphs, tables
(as GitHub-flavoured Markdown when rectangular, else HTML), figure and table
captions, footnotes attached to tables, supplementary-material labels, and a
compact reference list (re-report citations matter). The output starts with a
header block whose first line is ``PMID: <n>`` because the evidence schema
takes the PMID from there.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

_WS = re.compile(r"[ \t\r\f\v]+")
_NL = re.compile(r"\n{3,}")


def _strip_ns(root: ET.Element) -> None:
    for el in root.iter():
        if isinstance(el.tag, str) and "}" in el.tag:
            el.tag = el.tag.split("}", 1)[1]


def _inline(el: ET.Element | None) -> str:
    """Flatten inline content, keeping sub/sup markers and xref labels."""
    if el is None:
        return ""
    parts: list[str] = []
    if el.text:
        parts.append(el.text)
    for child in el:
        tag = child.tag
        if tag in ("sub",):
            parts.append("_" + _inline(child))
        elif tag in ("sup",):
            parts.append("^" + _inline(child))
        elif tag in ("xref", "bold", "italic", "underline", "sc", "named-content", "ext-link", "uri", "styled-content", "inline-formula", "abbrev", "email", "monospace", "roman"):
            parts.append(_inline(child))
        elif tag in ("break",):
            parts.append(" ")
        elif tag in ("table-wrap", "fig", "boxed-text", "list", "disp-formula", "supplementary-material"):
            pass  # block content handled by the caller
        else:
            parts.append(_inline(child))
        if child.tail:
            parts.append(child.tail)
    return _WS.sub(" ", "".join(parts)).strip()


@dataclass
class Article:
    pmid: str = ""
    pmcid: str = ""
    doi: str = ""
    title: str = ""
    journal: str = ""
    year: str = ""
    authors: list[str] = field(default_factory=list)
    abstract: str = ""
    body_md: str = ""
    back_md: str = ""
    n_tables: int = 0
    n_figures: int = 0

    def to_markdown(self) -> str:
        head = [f"PMID: {self.pmid or 'not reported'}"]
        if self.pmcid:
            head.append(f"PMCID: {self.pmcid}")
        if self.doi:
            head.append(f"DOI: {self.doi}")
        head.append(f"Title: {self.title}")
        head.append(f"Journal: {self.journal}" + (f" ({self.year})" if self.year else ""))
        if self.authors:
            head.append("Authors: " + "; ".join(self.authors))
        out = "\n".join(head) + "\n\n# " + (self.title or "Untitled") + "\n\n"
        if self.abstract:
            out += "## Abstract\n\n" + self.abstract + "\n\n"
        out += self.body_md
        if self.back_md:
            out += "\n\n" + self.back_md
        return _NL.sub("\n\n", out).strip() + "\n"


class Converter:
    def __init__(self) -> None:
        self.n_tables = 0
        self.n_figures = 0

    # ---- tables -----------------------------------------------------------
    def _table_rows(self, table: ET.Element) -> list[list[str]]:
        rows: list[list[str]] = []
        for tr in table.iter("tr"):
            cells = []
            for cell in tr:
                if cell.tag not in ("td", "th"):
                    continue
                text = _inline(cell).replace("|", "\\|")
                span = int(cell.get("colspan", "1") or 1)
                cells.append(text)
                cells.extend([""] * (span - 1))
            rows.append(cells)
        return rows

    def _table_md(self, table: ET.Element) -> str:
        rows = self._table_rows(table)
        if not rows:
            return ""
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        header, body = rows[0], rows[1:]
        lines = ["| " + " | ".join(header) + " |", "|" + "---|" * width]
        lines += ["| " + " | ".join(r) + " |" for r in body]
        return "\n".join(lines)

    def _table_wrap(self, tw: ET.Element) -> str:
        self.n_tables += 1
        label = _inline(tw.find("label"))
        caption = _inline(tw.find("caption"))
        parts = [f"### {label or 'Table'}" + (f": {caption}" if caption else "")]
        table = tw.find(".//table")
        if table is not None:
            parts.append(self._table_md(table))
        foot = tw.find("table-wrap-foot")
        if foot is not None:
            notes = [_inline(p) for p in foot.iter() if p.tag in ("p", "fn")]
            notes = [n for n in notes if n]
            if notes:
                parts.append("Table notes: " + " ".join(dict.fromkeys(notes)))
        return "\n\n".join(p for p in parts if p)

    def _fig(self, fig: ET.Element) -> str:
        self.n_figures += 1
        label = _inline(fig.find("label"))
        caption = _inline(fig.find("caption"))
        return f"**{label or 'Figure'}**" + (f": {caption}" if caption else "")

    def _list(self, lst: ET.Element) -> str:
        items = []
        for li in lst.findall("list-item"):
            items.append("- " + " ".join(_inline(p) for p in li if p.tag in ("p", "label")) or "- " + _inline(li))
        return "\n".join(items)

    # ---- blocks -----------------------------------------------------------
    def _block(self, el: ET.Element, level: int) -> list[str]:
        out: list[str] = []
        tag = el.tag
        if tag == "sec":
            title = _inline(el.find("title"))
            if title:
                out.append("#" * min(level, 6) + " " + title)
            for child in el:
                if child.tag == "title":
                    continue
                out.extend(self._block(child, level + 1))
        elif tag == "p":
            text = _inline(el)
            if text:
                out.append(text)
            for child in el:
                if child.tag in ("table-wrap", "fig", "list", "supplementary-material", "boxed-text"):
                    out.extend(self._block(child, level))
        elif tag == "table-wrap":
            out.append(self._table_wrap(el))
        elif tag == "table-wrap-group":
            for tw in el.findall("table-wrap"):
                out.append(self._table_wrap(tw))
        elif tag == "fig":
            out.append(self._fig(el))
        elif tag == "fig-group":
            for f in el.findall("fig"):
                out.append(self._fig(f))
        elif tag == "list":
            out.append(self._list(el))
        elif tag == "supplementary-material":
            label = _inline(el.find("label")) or "Supplementary material"
            caption = _inline(el.find("caption"))
            out.append(f"**{label}**" + (f": {caption}" if caption else ""))
        elif tag == "boxed-text":
            for child in el:
                out.extend(self._block(child, level))
        elif tag in ("disp-quote", "statement"):
            out.append("> " + _inline(el))
        elif tag in ("title",):
            pass
        else:
            text = _inline(el)
            if text:
                out.append(text)
        return out

    # ---- references -------------------------------------------------------
    def _ref(self, ref: ET.Element) -> str:
        label = _inline(ref.find("label"))
        cit = ref.find(".//element-citation")
        if cit is None:
            cit = ref.find(".//mixed-citation")
        if cit is None:
            return (label + " " if label else "") + _inline(ref)
        if cit.tag == "mixed-citation":
            text = _inline(cit)
        else:
            names = []
            for n in cit.findall(".//name")[:3]:
                surname = _inline(n.find("surname"))
                given = _inline(n.find("given-names"))
                names.append((surname + " " + given).strip())
            if len(cit.findall(".//name")) > 3:
                names.append("et al")
            year = _inline(cit.find("year"))
            title = _inline(cit.find("article-title"))
            source = _inline(cit.find("source"))
            text = ", ".join(x for x in [", ".join(names), year, title, source] if x)
        pmid = ""
        for pid in cit.findall("pub-id"):
            if pid.get("pub-id-type") == "pmid":
                pmid = " PMID:" + _inline(pid)
        rid = ref.get("id", "")
        lab = label or rid
        return f"[{lab}] {text}{pmid}".strip()

    def convert(self, xml_bytes: bytes) -> Article:
        root = ET.fromstring(xml_bytes)
        _strip_ns(root)
        art = root if root.tag == "article" else root.find(".//article")
        if art is None:
            raise ValueError("no <article> element")
        a = Article()
        front = art.find("front")
        if front is not None:
            meta = front.find("article-meta")
            jm = front.find("journal-meta")
            if jm is not None:
                a.journal = _inline(jm.find(".//journal-title"))
            if meta is not None:
                for aid in meta.findall("article-id"):
                    t = aid.get("pub-id-type")
                    if t == "pmid":
                        a.pmid = _inline(aid)
                    elif t in ("pmc", "pmcid"):
                        v = _inline(aid)
                        a.pmcid = v if v.upper().startswith("PMC") else "PMC" + v
                    elif t == "doi":
                        a.doi = _inline(aid)
                a.title = _inline(meta.find(".//title-group/article-title"))
                a.year = _inline(meta.find(".//pub-date/year"))
                for c in meta.findall(".//contrib-group/contrib"):
                    if c.get("contrib-type", "author") != "author":
                        continue
                    name = c.find("name")
                    if name is not None:
                        a.authors.append((_inline(name.find("surname")) + " " + _inline(name.find("given-names"))).strip())
                    else:
                        coll = _inline(c.find("collab"))
                        if coll:
                            a.authors.append(coll)
                abs_el = meta.find("abstract")
                if abs_el is not None:
                    a.abstract = "\n\n".join(self._block(abs_el, 3)) if abs_el.find("sec") is not None else "\n\n".join(x for x in self._block(abs_el, 3) if x)
        body = art.find("body")
        blocks: list[str] = []
        if body is not None:
            for child in body:
                blocks.extend(self._block(child, 2))
        a.body_md = "\n\n".join(b for b in blocks if b)
        back = art.find("back")
        back_blocks: list[str] = []
        if back is not None:
            for child in back:
                if child.tag == "ref-list":
                    title = _inline(child.find("title")) or "References"
                    back_blocks.append("## " + title)
                    back_blocks.extend(self._ref(r) for r in child.findall("ref"))
                elif child.tag in ("sec", "ack", "fn-group", "notes", "app-group", "app"):
                    back_blocks.extend(self._block(child, 2))
        a.back_md = "\n\n".join(b for b in back_blocks if b)
        a.n_tables, a.n_figures = self.n_tables, self.n_figures
        return a


def jats_to_markdown(xml_bytes: bytes) -> Article:
    return Converter().convert(xml_bytes)
