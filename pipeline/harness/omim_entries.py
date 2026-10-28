"""OMIM reference from entry pages frozen by Dr. Lin (2026-10-28; D-42).

Harness side only: this module reads ground truth and must never be imported
by ``pipeline.extract``.

Dr. Lin printed twelve omim.org entry pages to PDF on 2026-10-28 (the six
phenotype entries and the six gene entries of the pilot diseases) and
uploaded them to the Claude Code session. omim.org refuses automated reads
from the cloud environment (HTTP 403) and no API key is in place (D-12), so
these printouts are the OMIM reference. OMIM's terms restrict redistribution,
so the PDFs, their text and every parsed file that carries OMIM prose stay
under the reference root OUTSIDE the repository (the same root as the
ClinVar snapshot); only a manifest and counts are copied into the repo.

Input:   <root>/<date>/omim/entry_<MIM>.pdf          one per entry
Output:  <root>/<date>/omim/entry_<MIM>.txt          pdftotext -layout
         <root>/<date>/omim/entry_<MIM>.json         full parse (OMIM content)
         <root>/<date>/omim/allelic_variants.csv     one row per allelic variant
         <root>/<date>/omim/references.csv           one row per cited reference
         <manifest-out>/<date>/omim_MANIFEST.json    files, checksums, dates,
                                                      identifiers, counts (committed)
         <manifest-out>/<date>/omim_counts.json      per-disease counts (committed)

Parsed from each page: the MIM number and kind (# phenotype, * gene), the
preferred title and symbol, alternative titles, external identifiers
(ORPHA, MONDO, DO, ICD10CM, SNOMEDCT), HGNC symbol and cytogenetic location
(gene entries), the phenotype-gene relationship table, the section headings
present, the allelic variants (number, title, OMIM's variant label, dbSNP
and ClinVar ids, and the narrative with its author-year citations resolved
to PMIDs through the entry's own reference list), the numbered references
with PMIDs and DOIs, the creation date, the last contributor update and the
last edit, and the allelic-variant numbers a phenotype entry cites in its
text.

Checks that stop the script: the allelic variants parsed must equal the
count OMIM prints in the section heading; the references must number 1..n
without gaps; each pilot phenotype entry must name its gene entry and each
gene entry its phenotype entry (CONTEXT.md §4).

  uv run python -m pipeline.harness.omim_entries --root /home/user/gp-rarelink-reference \
      --date 2026-10-28 --manifest-out analysis/poc/reference_snapshot
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import subprocess
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# slug: phenotype MIM, gene symbol, gene MIM, allelic-variant titles that name the pilot disease
PILOT = {
    "ha20": ("616744", "TNFAIP3", "191163", ("AUTOINFLAMMATORY SYNDROME, FAMILIAL, BEHCET-LIKE 1",)),
    "axd": ("203450", "GFAP", "137780", ("ALEXANDER DISEASE",)),
    "lad1": ("116920", "ITGB2", "600065", ("LEUKOCYTE ADHESION DEFICIENCY 1", "LEUKOCYTE ADHESION DEFICIENCY, TYPE I")),
    "ssadh": ("271980", "ALDH5A1", "610045", ("SUCCINIC SEMIALDEHYDE DEHYDROGENASE DEFICIENCY",)),
    "danon": ("300257", "LAMP2", "309060", ("DANON DISEASE",)),
    "tangier": ("205400", "ABCA1", "600046", ("TANGIER DISEASE",)),
}
KIND = {"#": "phenotype", "*": "gene", "+": "gene_and_phenotype", "%": "phenotype_locus", "": "other"}
SECTIONS = {"Description", "Clinical Features", "Other Features", "Biochemical Features", "Inheritance", "Mapping",
            "Cytogenetics", "Pathogenesis", "Molecular Genetics", "Genotype/Phenotype Correlations", "Diagnosis",
            "Clinical Management", "Population Genetics", "Animal Model", "History", "Nomenclature", "Heterogeneity",
            "Gene Function", "Gene Structure", "Cloning and Expression", "Evolution", "Gene Therapy",
            "Prenatal Diagnosis", "Gene Family", "Biochemical Features", "See Also:"}
HEADER = re.compile(r"^(\d{1,2}/\d{1,2}/\d{2}, \d{1,2}:\d{2} [AP]M)\s+Entry - ([#*%+^]?)\s*(\d{6}) - (.+?) - OMIM - \(OMIM\.ORG\)\s*$")
FOOTER = re.compile(r"^https://www\.omim\.org/entry/\d+\s+\d+/\d+\s*$")
XREF_LINE = re.compile(r"^((?:SNOMEDCT|ICD10CM|ICD9CM|ORPHA|DO|MONDO|UMLS):\s*[^;]+;?\s*)+$")
ROW = re.compile(r"^\s*(?P<loc>(?:\d{1,2}|X|Y|XY)[pq][\w.\-]*|Chr\.\S+)?\s*(?P<phen>\S.*?)\s{2,}(?P<mim>\d{6})\s{2,}"
                 r"(?P<inh>.*?)\s{2,}(?P<key>[1-4])(?:\s{2,}(?P<gene>\S+)\s{2,}(?P<gmim>\d{6}))?\s*$")
AV_HEAD = re.compile(r"ALLELIC VARIANTS\s*\(?\s*(\d+)\s+Selected Examples?\)?:?")
AV_ITEM = re.compile(r"^\s*\.(\d{4})\s+(\S.*)$")
REF_ITEM = re.compile(r"^\s*(\d+)\.\s+(.*)$")
PMID = re.compile(r"\[PubMed:\s*(\d+)\]")
DOI = re.compile(r"https?://doi\.org/(\S+?)\]")
PARTICLE = r"(?:(?:van|de|der|den|von|da|del|di|le|la|du|dos|das)\s)*"
CITE = re.compile(r"(?<![\w'])(" + PARTICLE + r"[A-Z][\w'’\-]+(?:\s(?:and|&)\s" + PARTICLE + r"[A-Z][\w'’\-]+)?)"
                  r"\s(?:et al\.\s)?\(((?:\d{4}[a-z]?)(?:,\s*\d{4}[a-z]?)*)\)")
AVREF = re.compile(r"(\d{6})\.(\d{4})(?:\s*-\s*(\d{6})\.(\d{4}))?")
US_DATE = re.compile(r"(\d{1,2})/(\d{1,2})/(\d{4})")


def iso(us: str) -> str:
    m = US_DATE.search(us)
    return f"{int(m.group(3)):04d}-{int(m.group(1)):02d}-{int(m.group(2)):02d}" if m else us


def sha(p: Path, algo: str) -> str:
    h = hashlib.new(algo)
    h.update(p.read_bytes())
    return h.hexdigest()


def pdf_info(p: Path) -> dict:
    out = subprocess.run(["pdfinfo", str(p)], capture_output=True, text=True, check=True).stdout
    info = dict(line.split(":", 1) for line in out.splitlines() if ":" in line)
    return {"pages": int(info.get("Pages", "0").strip()), "creation_date": info.get("CreationDate", "").strip(),
            "pdf_title": info.get("Title", "").strip()}


def parse_entry(pdf: Path) -> dict:
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    pdf.with_suffix(".txt").write_text(text)
    raw = text.replace("\f", "\n").splitlines()
    head = None
    lines: list[str] = []
    printed = None
    for ln in raw:
        m = HEADER.match(ln)
        if m:
            head = head or m
            continue
        if FOOTER.match(ln):
            continue
        pm = re.match(r"^\s*Printed:\s*(.+?)\s*$", ln)
        if pm:
            printed = pm.group(1)
            continue
        lines.append(ln.rstrip())
    if not head:
        raise SystemExit(f"{pdf}: no OMIM page header found")
    browser_time, prefix, mim, title_full = head.group(1), head.group(2), head.group(3), head.group(4)
    title, _, symbol = title_full.partition("; ")
    e: dict = {"mim": mim, "kind": KIND.get(prefix, "other"), "prefix": prefix, "title": title.strip(),
               "symbol": symbol.strip() or None, "title_full": title_full, "browser_print_time_local": browser_time,
               "printed_footer": printed, "alternative_titles": [], "xrefs": {}, "hgnc_symbol": None,
               "cytogenetic_location": None, "genomic_coordinates": None, "relationships": [], "sections": [],
               "allelic_variants": [], "allelic_variants_listed": None, "references": [], "cited_allelic_variants": [],
               "created": None, "created_by": None, "last_contributor_update": None, "last_contributor": None,
               "last_edit": None, "last_editor": None, "parse_warnings": []}
    stripped = [ln.strip() for ln in lines]

    def find(pred, start=0):
        for i in range(start, len(stripped)):
            if pred(stripped[i]):
                return i
        return None

    # alternative titles: the block after the heading, up to the first blank line
    i = find(lambda s: s == "Alternative titles; symbols")
    if i is not None:
        j = i + 1
        while j < len(stripped) and not stripped[j]:
            j += 1
        while j < len(stripped) and stripped[j]:
            e["alternative_titles"].append(stripped[j])
            j += 1
    i_text = find(lambda s: s == "TEXT")
    i_refs = find(lambda s: s == "REFERENCES")
    if i_text is None or i_refs is None:
        raise SystemExit(f"{pdf}: TEXT or REFERENCES heading not found")
    for s in stripped[:i_text]:
        if XREF_LINE.match(s):
            for part in s.split(";"):
                if ":" in part:
                    k, vals = part.split(":", 1)
                    e["xrefs"].setdefault(k.strip(), []).extend(x.strip() for x in vals.split(",") if x.strip())
        m = re.match(r"^HGNC Approved Gene Symbol:\s*(\S+)", s)
        if m:
            e["hgnc_symbol"] = m.group(1)
        m = re.match(r"^Cytogenetic location:\s*(\S+)\s+Genomic coordinates \((GRCh\d+)\)\s*:\s*(\S+)", s)
        if m:
            e["cytogenetic_location"], e["genomic_coordinates"] = m.group(1), f"{m.group(2)} {m.group(3)}"
    # relationship table
    i = find(lambda s: s in ("Phenotype-Gene Relationships", "Gene-Phenotype Relationships"))
    if i is None:
        e["parse_warnings"].append("no relationship table")
    else:
        j = i + 1
        while j < i_text and ("Location" not in lines[j]):
            j += 1
        j += 1  # the row after the 'Location ... MIM number' header line
        while j < i_text:
            if not stripped[j]:
                if e["relationships"]:
                    break
                j += 1
                continue
            m = ROW.match(lines[j])
            if m:
                e["relationships"].append({"location": m.group("loc"), "phenotype": m.group("phen").strip(),
                                           "phenotype_mim": m.group("mim"), "inheritance": m.group("inh").strip(),
                                           "mapping_key": m.group("key"), "gene": m.group("gene"), "gene_mim": m.group("gmim")})
            elif e["relationships"]:
                e["relationships"][-1]["phenotype"] += " " + stripped[j]  # wrapped phenotype name
            else:
                raise SystemExit(f"{pdf}: cannot parse relationship row: {lines[j]!r}")
            j += 1
    # sections and allelic variants in the body
    i_av = find(lambda s: bool(AV_HEAD.search(s)), i_text)
    body_end = i_av if i_av is not None and i_av < i_refs else i_refs
    for s in stripped[i_text + 1:body_end]:
        if s in SECTIONS:
            e["sections"].append(s)
    body_text = " ".join(x for x in stripped[i_text + 1:body_end] if x)
    seen = set()
    for a, b, c, d in AVREF.findall(body_text):
        ids = [f"{a}.{b}"]
        if c and c == a and int(d) >= int(b):
            ids = [f"{a}.{k:04d}" for k in range(int(b), min(int(d), int(b) + 200) + 1)]
        for x in ids:
            if x not in seen:
                seen.add(x)
                e["cited_allelic_variants"].append(x)
    # references
    refs: list[list[str]] = []
    for s in stripped[i_refs + 1:]:
        if s.startswith("Contributors:") or s.startswith("Creation Date:") or s.startswith("Edit History:"):
            break
        m = REF_ITEM.match(s)
        if m and (not refs or int(m.group(1)) == len(refs) + 1):
            refs.append([m.group(1), m.group(2)])
        elif refs and s:
            refs[-1][1] += " " + s
    for n, body in refs:
        pm = PMID.search(body)
        dm = DOI.search(body)
        pre = body.split("[PubMed")[0].split("[Full Text")[0]
        ym = re.search(r"(?:,|\)|\.)\s*((?:1[89]|20)\d{2})\.", pre)
        years = re.findall(r"\b((?:1[89]|20)\d{2})\b", pre)
        e["references"].append({"n": int(n), "first_author": body.split(",")[0].strip(), "year": ym.group(1) if ym else (years[-1] if years else None),
                                "pmid": pm.group(1) if pm else None, "doi": dm.group(1) if dm else None, "text": body})
    if [r["n"] for r in e["references"]] != list(range(1, len(e["references"]) + 1)):
        raise SystemExit(f"{pdf}: references do not number 1..n")
    index: dict[tuple[str, str], list[dict]] = {}
    for r in e["references"]:
        index.setdefault((r["first_author"].lower(), r["year"] or ""), []).append(r)

    def resolve(narrative: str) -> list[dict]:
        out = []
        for who, yrs in CITE.findall(narrative):
            surname = re.split(r"\s(?:and|&)\s", who)[0].strip().lower()
            for y in [x.strip() for x in yrs.split(",")]:
                hits = index.get((surname, y[:4]), [])
                out.append({"text": f"{who} ({y})", "surname": surname, "year": y[:4], "ref_nos": [h["n"] for h in hits],
                            "pmids": sorted({h["pmid"] for h in hits if h["pmid"]}), "ambiguous": len(hits) > 1,
                            "unresolved": not hits})
        return out

    # allelic variants
    if i_av is not None and i_av < i_refs:
        e["allelic_variants_listed"] = int(AV_HEAD.search(stripped[i_av]).group(1))
        items: list[list[str]] = []
        for s in stripped[i_av + 1:i_refs]:
            m = AV_ITEM.match(s)
            if m:
                items.append([m.group(1), m.group(2)])
            elif items and s:
                items[-1].append(s)
        for it in items:
            num, title_, rest = it[0], it[1].strip(), it[2:]
            av = {"av": f"{mim}.{num}", "number": num, "title": title_, "label": None, "rsids": [], "clinvar_rcvs": [],
                  "narrative": "", "citations": [], "status": "active"}
            up = title_.upper()
            if up.startswith("MOVED TO"):
                av["status"] = "moved"
            elif up.startswith("REMOVED FROM"):
                av["status"] = "removed"
            elif "RECLASSIFIED" in up:
                av["status"] = "reclassified"
            elif "POLYMORPHISM" in up:
                av["status"] = "polymorphism"
            elif "UNKNOWN SIGNIFICANCE" in up:
                av["status"] = "unknown_significance"
            k = 0
            if rest and re.match(r"^[A-Z][A-Z0-9\-]*,\s", rest[0]):
                av["label"] = rest[0]
                k = 1
            elif av["status"] == "active":
                e["parse_warnings"].append(f"{av['av']}: no variant label line")
            if k < len(rest) and re.match(r"^(SNP|ClinVar|gnomAD):", rest[k]):
                av["rsids"] = sorted(set(re.findall(r"rs\d+", rest[k])))
                av["clinvar_rcvs"] = re.findall(r"RCV\d+", rest[k])
                k += 1
            av["narrative"] = " ".join(rest[k:])
            av["citations"] = resolve(av["narrative"])
            av["citation_pmids"] = sorted({p for c in av["citations"] for p in c["pmids"]})
            e["allelic_variants"].append(av)
        if len(e["allelic_variants"]) != e["allelic_variants_listed"]:
            raise SystemExit(f"{pdf}: parsed {len(e['allelic_variants'])} allelic variants, heading says {e['allelic_variants_listed']}")
    # dates
    for idx, s in enumerate(stripped):
        m = re.match(r"^Contributors:\s+(.+?)\s+-\s+updated\s*:\s*(\S+)", s)
        if m and not e["last_contributor_update"]:
            e["last_contributor"], e["last_contributor_update"] = m.group(1), iso(m.group(2))
        m = re.match(r"^Creation Date:\s+(.+?)\s*:\s*(\d{1,2}/\d{1,2}/\d{4})", s)
        if m:
            e["created_by"], e["created"] = m.group(1), iso(m.group(2))
        m = re.match(r"^Edit History:\s+(\w+)\s*:\s*(\d{1,2}/\d{1,2}/\d{4})", s)
        if m:
            e["last_editor"], e["last_edit"] = m.group(1), iso(m.group(2))
    return e


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--root", default="/home/user/gp-rarelink-reference")
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--manifest-out", default="analysis/poc/reference_snapshot")
    args = ap.parse_args(argv)
    root = Path(args.root).resolve()
    if REPO in root.parents or root == REPO:
        raise SystemExit("the reference root must lie outside the repository")
    folder = root / args.date / "omim"
    pdfs = sorted(folder.glob("entry_*.pdf"))
    if not pdfs:
        raise SystemExit(f"no entry_<MIM>.pdf under {folder}")
    entries = {}
    for pdf in pdfs:
        e = parse_entry(pdf)
        e["file"] = {"name": pdf.name, "bytes": pdf.stat().st_size, "md5": sha(pdf, "md5"), "sha256": sha(pdf, "sha256"), **pdf_info(pdf)}
        entries[e["mim"]] = e
        (folder / f"entry_{e['mim']}.json").write_text(json.dumps(e, indent=1))
    # consistency with CONTEXT.md §4
    for slug, (pmim, gene, gmim, _) in PILOT.items():
        if pmim in entries:
            rel = entries[pmim]["relationships"]
            if not any(r["gene_mim"] == gmim and r["gene"] == gene for r in rel):
                raise SystemExit(f"{slug}: phenotype entry {pmim} does not name {gene} ({gmim}) in its relationship table")
        if gmim in entries:
            if entries[gmim]["hgnc_symbol"] != gene:
                raise SystemExit(f"{slug}: gene entry {gmim} HGNC symbol is {entries[gmim]['hgnc_symbol']}, expected {gene}")
            if not any(r["phenotype_mim"] == pmim for r in entries[gmim]["relationships"]):
                raise SystemExit(f"{slug}: gene entry {gmim} does not list phenotype {pmim}")
    # flat files under the reference root (OMIM content; never committed)
    with (folder / "allelic_variants.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["gene", "gene_mim", "av", "status", "title", "label", "rsids", "clinvar_rcvs", "citation_pmids", "citations", "narrative"])
        for e in entries.values():
            for av in e["allelic_variants"]:
                w.writerow([e["hgnc_symbol"], e["mim"], av["av"], av["status"], av["title"], av["label"] or "", "|".join(av["rsids"]),
                            "|".join(av["clinvar_rcvs"]), "|".join(av["citation_pmids"]),
                            "|".join(c["text"] + ("?" if c["unresolved"] else "*" if c["ambiguous"] else "") for c in av["citations"]), av["narrative"]])
    with (folder / "references.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["mim", "kind", "n", "first_author", "year", "pmid", "doi"])
        for e in entries.values():
            for r in e["references"]:
                w.writerow([e["mim"], e["kind"], r["n"], r["first_author"], r["year"] or "", r["pmid"] or "", r["doi"] or ""])
    # committed manifest: identifiers, dates, checksums and counts; no OMIM prose
    man_entries = {}
    for mim, e in sorted(entries.items()):
        avs = e["allelic_variants"]
        man_entries[mim] = {
            "kind": e["kind"], "title": e["title"], "symbol": e["symbol"], "alternative_titles": e["alternative_titles"],
            "hgnc_symbol": e["hgnc_symbol"], "cytogenetic_location": e["cytogenetic_location"], "genomic_coordinates": e["genomic_coordinates"],
            "xrefs": e["xrefs"], "relationships": e["relationships"], "sections": e["sections"],
            "created": e["created"], "last_contributor_update": e["last_contributor_update"], "last_edit": e["last_edit"],
            "references": len(e["references"]), "references_with_pmid": sum(1 for r in e["references"] if r["pmid"]),
            "cited_allelic_variants_in_text": len(e["cited_allelic_variants"]),
            "allelic_variants_listed": e["allelic_variants_listed"],
            "allelic_variants_by_status": dict(Counter(a["status"] for a in avs)) if avs else {},
            "allelic_variants_by_title": dict(Counter(a["title"] for a in avs)) if avs else {},
            "allelic_variants_with_clinvar_rcv": sum(1 for a in avs if a["clinvar_rcvs"]),
            "allelic_variants_with_dbsnp": sum(1 for a in avs if a["rsids"]),
            "allelic_variant_citations": {"total": sum(len(a["citations"]) for a in avs),
                                          "resolved_to_pmid": sum(1 for a in avs for c in a["citations"] if c["pmids"]),
                                          "ambiguous": sum(1 for a in avs for c in a["citations"] if c["ambiguous"]),
                                          "unresolved": sum(1 for a in avs for c in a["citations"] if c["unresolved"])},
            "parse_warnings": e["parse_warnings"], "file": e["file"], "browser_print_time_local": e["browser_print_time_local"],
            "printed_footer": e["printed_footer"]}
    manifest = {
        "date": args.date, "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "source": "Browser print-to-PDF of https://www.omim.org/entry/<MIM> by Dr. Jimmy Lin on 2026-10-28 (page header gives his local time), "
                  "uploaded to the Claude Code session the same day. omim.org answers HTTP 403 to the cloud environment and no API key is in place (D-12).",
        "decision": "D-42",
        "licence_note": "OMIM content is not redistributed (pre-registration §11; .gitignore). The PDFs, their text and the parsed JSON/CSV stay under the "
                        "reference root outside the repository; this manifest and omim_counts.json carry identifiers, dates, checksums and counts only.",
        "location_note": f"content under {folder} (gone with the container; Dr. Lin holds the PDFs). Re-create with "
                         "pipeline/harness/omim_entries.py after copying the PDFs back as entry_<MIM>.pdf.",
        "method": "pdftotext -layout, parsed by script (pipeline/harness/omim_entries.py); allelic-variant counts checked against the section heading; "
                  "reference numbering checked contiguous; phenotype<->gene relationship tables checked against CONTEXT.md §4.",
        "entries": man_entries}
    # per-disease counts, with the §7.2.5 corpus overlap (descriptive)
    counts = {}
    for slug, (pmim, gene, gmim, titles) in PILOT.items():
        if pmim not in entries or gmim not in entries:
            counts[slug] = {"note": "entry missing"}
            continue
        pe, ge = entries[pmim], entries[gmim]
        avs = ge["allelic_variants"]
        for_disease = [a for a in avs if a["title"].upper() in titles]
        qualified = [a for a in avs if a["title"].upper() not in titles and any(a["title"].upper().startswith(t + ",") for t in titles)]
        other = [a for a in avs if a not in for_disease and a not in qualified]
        cited = {"phenotype_entry": {r["pmid"] for r in pe["references"] if r["pmid"]},
                 "gene_entry": {r["pmid"] for r in ge["references"] if r["pmid"]},
                 "allelic_variant_narratives": {p for a in for_disease + qualified for p in a["citation_pmids"]}}
        cited["union"] = cited["phenotype_entry"] | cited["gene_entry"]
        mpath = REPO / "data" / "literature" / slug / "manifest.csv"
        overlap = {}
        if mpath.exists():
            rows = {r["pmid"]: r for r in csv.DictReader(mpath.open())}
            corpus = {p for p, r in rows.items() if r["in_extraction_corpus"].strip().lower() == "true"}
            run_dir = REPO / "data" / "extracted" / slug / f"pv1-{slug}" / "per_paper"
            extracted = {p.stem for p in run_dir.glob("*.json")} if run_dir.exists() else set()
            overlap = {"corpus_pmids": len(corpus), "extracted_pmids": len(extracted)}
            for name, s in cited.items():
                overlap[name] = {"omim_cited_pmids": len(s), "in_manifest": len(s & set(rows)), "in_corpus": len(s & corpus),
                                 "extracted": len(s & extracted),
                                 "share_of_corpus_cited": round(len(s & corpus) / len(corpus), 4) if corpus else None,
                                 "share_of_extracted_cited": round(len(s & extracted) / len(extracted), 4) if extracted else None}
        counts[slug] = {
            "phenotype_mim": pmim, "gene": gene, "gene_mim": gmim,
            "phenotype_entry": {"last_edit": pe["last_edit"], "last_contributor_update": pe["last_contributor_update"],
                                "references": len(pe["references"]), "references_with_pmid": len(cited["phenotype_entry"])},
            "gene_entry": {"last_edit": ge["last_edit"], "last_contributor_update": ge["last_contributor_update"],
                           "references": len(ge["references"]), "references_with_pmid": len(cited["gene_entry"])},
            "allelic_variants": {"listed": ge["allelic_variants_listed"], "titled_for_disease": len(for_disease),
                                 "titled_for_disease_qualified": [a["title"] for a in qualified],
                                 "other_titles": dict(Counter(a["title"] for a in other)),
                                 "for_disease_with_clinvar_rcv": sum(1 for a in for_disease + qualified if a["clinvar_rcvs"]),
                                 "for_disease_without_clinvar_rcv": sum(1 for a in for_disease + qualified if not a["clinvar_rcvs"]),
                                 "for_disease_with_dbsnp": sum(1 for a in for_disease + qualified if a["rsids"]),
                                 "for_disease_with_resolved_citation": sum(1 for a in for_disease + qualified if a["citation_pmids"])},
            "corpus_overlap_7_2_5": overlap}
    out = REPO / args.manifest_out / args.date
    out.mkdir(parents=True, exist_ok=True)
    (out / "omim_MANIFEST.json").write_text(json.dumps(manifest, indent=1))
    (out / "omim_counts.json").write_text(json.dumps(counts, indent=1))
    print(json.dumps(counts, indent=1))
    for mim, e in sorted(entries.items()):
        print(mim, e["kind"], e["title"], "| refs", len(e["references"]), "| AVs", e["allelic_variants_listed"], "| last edit", e["last_edit"],
              "| warnings", e["parse_warnings"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
