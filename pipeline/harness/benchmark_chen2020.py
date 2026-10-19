"""Stage 6 step 3 (D-30): transcribe the Chen 2020 Table S1 benchmark by script.

D-30 (Jimmy, 2026-10-19) replaces El Hani 2024, which is paywalled from the
cloud environment, with Chen et al. 2020 (PMID 33101300, PMC7546856, CC BY),
Supplementary Table S1: 89 HA20 patients in families, each family with the
protein change and the reference it was taken from.

Reads the supplementary PDF (Data_Sheet_2.PDF, fetched at Stage 3b) through
pdftotext -layout and parses:
  family rows   "<family> (<refs>)  <protein change>  <first patient> ..."
  patient ids   the integers in the Patient column (1-89)
  references    the numbered list at the end, with DOIs
It resolves each reference DOI to a PMID with NCBI E-utilities (esearch
"<doi>[doi]"). Output, under the reference root (outside the repo):
  <root>/<date>/benchmarks/chen2020_tableS1.csv  one row per family
  <root>/<date>/benchmarks/chen2020_refs.csv     reference number, DOI, PMID
and a manifest (counts, source sha256) copied to --manifest-out.

The script stops if the patients do not number 1..89 without gaps, so a
parsing slip cannot pass silently.

  uv run python -m pipeline.harness.benchmark_chen2020 \
      --pdf data/literature/ha20/supplementary/files/33101300/Data_Sheet_2.PDF \
      --root /home/user/gp-rarelink-reference --date 2026-10-19 --manifest-out analysis/poc/reference_snapshot
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

from pipeline.extract.corpus.eutils import EUTILS, Client

FAMILY = re.compile(r"^\s*(\d+)\s*\(([\d;,\s]+)\)\s+(.+?)\s{2,}(\d+)\s{2,}")
PATIENT = re.compile(r"^\s{15,}(\d+)\s{2,}(?:[\d.]+\s+)?[MF]\s")
REF = re.compile(r"^(\d+)\.\s+(.*)")
DOI = re.compile(r"doi:\s*([^\s]+(?:\s*\n?[^\s]*)?)", re.I)


def parse(text: str) -> tuple[list[dict], dict[int, str]]:
    lines = text.splitlines()
    body, refs_start = lines, None
    for i, l in enumerate(lines):
        if l.strip() == "References":
            body, refs_start = lines[:i], i
            break
    fams, cur = [], None
    for i, l in enumerate(body):
        m = FAMILY.match(l)
        if m:
            variant = " ".join(m.group(3).split())
            nxt = next((x.strip() for x in body[i + 1:i + 4] if x.strip()), "")
            if variant.lower().startswith("deletion of exons") and re.match(r"^\d+\s*[–-]\s*\d+$", nxt):
                variant += " " + nxt  # "Deletion of exons" / "2–3" wraps onto the next line
            cur = {"family": int(m.group(1)), "refs": [int(x) for x in re.split(r"[;,\s]+", m.group(2).strip()) if x],
                   "variant_as_printed": variant, "patients": [int(m.group(4))]}
            fams.append(cur)
            continue
        p = PATIENT.match(l)
        if p and cur:
            cur["patients"].append(int(p.group(1)))
    refs = {}
    if refs_start is not None:
        block = "\n".join(lines[refs_start + 1:])
        entries, last = [], 0
        for e in re.split(r"\n(?=\d+\.\s)", block):
            m = REF.match(e.strip())
            if m and int(m.group(1)) == last + 1:  # a new numbered reference
                entries.append(e)
                last += 1
            elif entries:  # a wrapped line that starts with a number (e.g. a page range "735.")
                entries[-1] += "\n" + e
        for e in entries:
            m = REF.match(e.strip())
            flat = " ".join(e.split())
            d = re.search(r"doi:\s*(\S+(?:\s\S+)?)", flat, re.I)
            doi = d.group(1).replace(" ", "") if d else ""
            doi = re.sub(r"[.;,]+$", "", doi)
            refs[int(m.group(1))] = doi
    return fams, refs


def protein_key(s: str) -> str:
    """'p. Arg 87*' -> 'R87*'; 'p. Lys303fs' -> 'K303fs'; 'Deletion of exons 2–3' -> 'del ex2-3'."""
    from pipeline.harness.concordance import protein_short

    t = " ".join(s.split())
    if t.lower().startswith("deletion of exons"):
        return "del ex" + re.sub(r"\s*[–-]\s*", "-", t[len("deletion of exons"):].strip())
    t = t.replace("p. ", "p.").replace(" ", "")
    t = re.sub(r"fs(\d)", r"fs*\1", t)
    return protein_short(t)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--pdf", required=True)
    ap.add_argument("--root", required=True)
    ap.add_argument("--date", required=True)
    ap.add_argument("--manifest-out", required=True)
    args = ap.parse_args(argv)
    pdf = Path(args.pdf)
    text = subprocess.run(["pdftotext", "-layout", str(pdf), "-"], capture_output=True, text=True, check=True).stdout
    fams, refs = parse(text)
    pts = sorted(p for f in fams for p in f["patients"])
    if pts != list(range(1, 90)):
        missing = sorted(set(range(1, 90)) - set(pts))
        dup = sorted({p for p in pts if pts.count(p) > 1})
        raise SystemExit(f"patients do not number 1..89: missing {missing}, duplicated {dup}")
    client = Client()
    pmid = {}
    for n, doi in sorted(refs.items()):
        if not doi:
            pmid[n] = ""
            continue
        r = client.get(f"{EUTILS}/esearch.fcgi", {"db": "pubmed", "term": f"{doi}[doi]", "retmode": "json"})
        r.raise_for_status()
        ids = r.json()["esearchresult"]["idlist"]
        pmid[n] = ids[0] if len(ids) == 1 else ""
    out = Path(args.root) / args.date / "benchmarks"
    out.mkdir(parents=True, exist_ok=True)
    with (out / "chen2020_tableS1.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["family", "refs", "ref_pmids", "variant_as_printed", "protein_key", "patients", "n_patients"])
        w.writeheader()
        for f in fams:
            w.writerow({"family": f["family"], "refs": ";".join(map(str, f["refs"])),
                        "ref_pmids": ";".join(pmid.get(r, "") for r in f["refs"]),
                        "variant_as_printed": f["variant_as_printed"], "protein_key": protein_key(f["variant_as_printed"]),
                        "patients": ";".join(map(str, f["patients"])), "n_patients": len(f["patients"])})
    with (out / "chen2020_refs.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["ref", "doi", "pmid"])
        for n in sorted(refs):
            w.writerow([n, refs[n], pmid[n]])
    manifest = {"benchmark": "Chen 2020 Table S1 (PMID 33101300, PMC7546856, CC BY)", "decision": "D-30", "date": args.date,
                "source_pdf": str(pdf), "source_sha256": hashlib.sha256(pdf.read_bytes()).hexdigest(),
                "families": len(fams), "patients": len(pts), "references": len(refs),
                "references_resolved_to_pmid": sum(bool(v) for v in pmid.values()),
                "distinct_protein_keys": len({protein_key(f["variant_as_printed"]) for f in fams}),
                "method": "pdftotext -layout, parsed by script; DOIs resolved by NCBI esearch"}
    (out / "chen2020_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    dest = Path(args.manifest_out) / args.date
    dest.mkdir(parents=True, exist_ok=True)
    shutil.copy(out / "chen2020_MANIFEST.json", dest / "chen2020_MANIFEST.json")
    print(json.dumps(manifest, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
