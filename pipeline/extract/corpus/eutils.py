"""Thin NCBI E-utilities / ID-converter / Europe PMC clients used by the corpus scripts.

Network-only helpers live here so the parsing logic in the sibling modules can
be unit-tested offline. Polite defaults: tool/email identification, NCBI_API_KEY
when set, 3 requests/s without a key, 10/s with one, retries with backoff.
"""

from __future__ import annotations

import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Iterable

import httpx

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
IDCONV = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
PMC_OA = "https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi"
EUROPEPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest"
TOOL = "gp-rarelink"
EMAIL = os.getenv("NCBI_EMAIL", "jimmy.lin@raregenomics.org")


class Unreachable(RuntimeError):
    """The host could not be reached; the caller must stop, not improvise."""


@dataclass
class Client:
    api_key: str | None = os.getenv("NCBI_API_KEY") or None
    timeout: float = 60.0
    max_attempts: int = 4

    def __post_init__(self) -> None:
        self._http = httpx.Client(timeout=self.timeout, follow_redirects=True, headers={"User-Agent": f"{TOOL} ({EMAIL})"})
        self._min_interval = 0.11 if self.api_key else 0.34
        self._last = 0.0

    def _throttle(self) -> None:
        wait = self._min_interval - (time.monotonic() - self._last)
        if wait > 0:
            time.sleep(wait)
        self._last = time.monotonic()

    def get(self, url: str, params: dict | None = None) -> httpx.Response:
        params = dict(params or {})
        if url.startswith(EUTILS):
            params.setdefault("tool", TOOL)
            params.setdefault("email", EMAIL)
            if self.api_key:
                params.setdefault("api_key", self.api_key)
        last_exc: Exception | None = None
        for attempt in range(self.max_attempts):
            self._throttle()
            try:
                r = self._http.get(url, params=params)
                if r.status_code in (429, 500, 502, 503, 504):
                    raise httpx.HTTPStatusError(f"{r.status_code}", request=r.request, response=r)
                return r
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last_exc = exc
                time.sleep(2**attempt)
        raise Unreachable(f"{url}: {last_exc}")

    # ---- PubMed -----------------------------------------------------------
    def esearch_pubmed(self, term: str, mindate: str | None = None, retmax: int = 10000) -> list[str]:
        params = {"db": "pubmed", "term": term, "retmax": retmax, "retmode": "json", "sort": "pub_date"}
        if mindate:
            params.update({"datetype": "pdat", "mindate": mindate, "maxdate": "3000"})
        r = self.get(f"{EUTILS}/esearch.fcgi", params)
        r.raise_for_status()
        data = r.json()["esearchresult"]
        if int(data.get("count", 0)) > retmax:
            raise RuntimeError(f"query returned {data['count']} > retmax {retmax}; raise retmax or narrow the query")
        return list(data.get("idlist", []))

    def efetch_pubmed_xml(self, pmids: Iterable[str]) -> ET.Element:
        ids = ",".join(pmids)
        r = self.get(f"{EUTILS}/efetch.fcgi", {"db": "pubmed", "id": ids, "retmode": "xml"})
        r.raise_for_status()
        return ET.fromstring(r.content)

    # ---- ID conversion ----------------------------------------------------
    def idconv(self, ids: Iterable[str]) -> list[dict]:
        r = self.get(IDCONV, {"ids": ",".join(ids), "format": "json", "tool": TOOL, "email": EMAIL})
        r.raise_for_status()
        return r.json().get("records", [])

    # ---- Full text --------------------------------------------------------
    def pmc_oa_links(self, pmcid: str) -> list[dict]:
        """Return [{'format': 'tgz'|'pdf', 'href': ..., 'license': ...}] from the PMC OA service."""
        r = self.get(PMC_OA, {"id": pmcid})
        r.raise_for_status()
        root = ET.fromstring(r.content)
        err = root.find(".//error")
        if err is not None:
            return []
        out = []
        for rec in root.findall(".//record"):
            lic = rec.get("license")
            for link in rec.findall("link"):
                out.append({"format": link.get("format"), "href": link.get("href"), "license": lic})
        return out

    def europepmc_fulltext_xml(self, pmcid: str) -> bytes | None:
        r = self.get(f"{EUROPEPMC}/{pmcid}/fullTextXML")
        if r.status_code == 404:
            return None
        r.raise_for_status()
        return r.content

    def download(self, url: str) -> bytes:
        r = self.get(url)
        r.raise_for_status()
        return r.content
