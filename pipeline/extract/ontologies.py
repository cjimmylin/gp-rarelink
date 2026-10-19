"""Pinned ontology releases (HPO, Mondo, ECO, GENO) for Stage 4 (POC_DESIGN.md §3.7).

Ontologies are vocabularies, not ground truth, so the extraction side may read
them. They are downloaded to data/ontologies/<date>/ (git-ignored), with a
committed manifest of URL, release version, size and SHA-256. Disease-phenotype
annotation files (phenotype.hpoa and similar) are never downloaded here: they
encode database assertions (NOTES_FOR_AGENTS.md §6).

  uv run python -m pipeline.extract.ontologies fetch            # today's releases
  uv run python -m pipeline.extract.ontologies fetch --date 2026-10-19

The OBO parser keeps what binding and validation need: id, name, exact and
related synonyms, is_a parents, obsolete flag, replaced_by, and xrefs.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import httpx

SOURCES = {
    "hp": "https://purl.obolibrary.org/obo/hp.obo",
    "mondo": "https://purl.obolibrary.org/obo/mondo.obo",
    "eco": "https://purl.obolibrary.org/obo/eco.obo",    # evidence codes for phenopacket evidence
    "geno": "https://purl.obolibrary.org/obo/geno.obo",  # allelic state terms
}
BASE = Path("data/ontologies")


@dataclass
class Term:
    id: str
    name: str = ""
    synonyms: list[tuple[str, str]] = field(default_factory=list)  # (scope, text)
    parents: list[str] = field(default_factory=list)
    obsolete: bool = False
    replaced_by: list[str] = field(default_factory=list)
    xrefs: list[str] = field(default_factory=list)


@dataclass
class Ontology:
    version: str
    terms: dict[str, Term]

    def ancestors(self, tid: str) -> set[str]:
        seen, stack = set(), list(self.terms[tid].parents) if tid in self.terms else []
        while stack:
            p = stack.pop()
            if p not in seen:
                seen.add(p)
                stack.extend(self.terms[p].parents if p in self.terms else [])
        return seen


SYN = re.compile(r'^synonym: "(.*)" (EXACT|RELATED|NARROW|BROAD)')


def parse_obo(path: Path) -> Ontology:
    version, terms, cur, in_term = "", {}, None, False
    with path.open(encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            if line.startswith("data-version:") and not version:
                version = line.split(":", 1)[1].strip()
            if line.startswith("["):
                in_term = line == "[Term]"
                cur = None
                continue
            if not in_term or not line:
                continue
            key, _, val = line.partition(": ")
            if key == "id":
                cur = Term(id=val.strip())
                terms[cur.id] = cur
            elif cur is None:
                continue
            elif key == "name":
                cur.name = val.strip()
            elif key == "synonym":
                m = SYN.match(line)
                if m:
                    cur.synonyms.append((m.group(2), m.group(1).replace('\\"', '"')))
            elif key == "is_a":
                cur.parents.append(val.split(" ! ")[0].split(" {")[0].strip())
            elif key == "is_obsolete" and val.strip() == "true":
                cur.obsolete = True
            elif key == "replaced_by":
                cur.replaced_by.append(val.strip())
            elif key == "xref":
                cur.xrefs.append(val.split(" ")[0].strip())
    return Ontology(version=version, terms=terms)


def latest_dir() -> Path:
    dirs = sorted(p for p in BASE.iterdir() if p.is_dir()) if BASE.exists() else []
    if not dirs:
        raise SystemExit("no ontology snapshot; run: uv run python -m pipeline.extract.ontologies fetch")
    return dirs[-1]


def load(name: str, snapshot: Path | None = None) -> Ontology:
    return parse_obo((snapshot or latest_dir()) / f"{name}.obo")


def fetch(day: str) -> Path:
    out = BASE / day
    out.mkdir(parents=True, exist_ok=True)
    manifest = {"date": day, "files": {}}
    with httpx.Client(timeout=300, follow_redirects=True, headers={"User-Agent": "gp-rarelink (literature curation)"}) as c:
        for name, url in SOURCES.items():
            r = c.get(url)
            r.raise_for_status()
            path = out / f"{name}.obo"
            path.write_bytes(r.content)
            onto = parse_obo(path)
            final = r.url.copy_with(query=None)  # drop the short-lived signed query string
            manifest["files"][name] = {"url": url, "final_url": str(final), "version": onto.version, "bytes": len(r.content),
                                       "sha256": hashlib.sha256(r.content).hexdigest(), "terms": len(onto.terms)}
            print(f"{name}: {onto.version}, {len(onto.terms)} terms, {len(r.content):,} bytes")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("fetch")
    f.add_argument("--date", default=date.today().isoformat())
    args = ap.parse_args(argv)
    if args.cmd == "fetch":
        fetch(args.date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
