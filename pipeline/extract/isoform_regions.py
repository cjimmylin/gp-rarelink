"""Isoform-sensitive regions for Stage 4 normalization (D-43, 2026-10-28).

Some genes have alternative coding exons, so one cDNA position names different
genomic bases on different transcripts: LAMP2 exons 9a, 9b and 9c, GFAP exon 7A
(the epsilon isoform) against exons 8 and 9 (alpha). When a paper gives a cDNA
description without a transcript, assuming the MANE Select transcript at such a
position can place the variant on the wrong exon. Stage 4 therefore needs, per
gene, the c. position from which the coding isoforms diverge and the
alternative transcripts a paper may mean.

This module computes that position from the RefSeq mRNA records themselves
(NCBI E-utilities efetch, GenBank flat files): each record's exon features and
CDS give the exon boundaries in c. coordinates, and the divergence point is the
first boundary at which the MANE and the alternative transcript differ. The
label patterns that let a paper's own words choose the transcript ("E9b",
"LAMP2B", "epsilon", "exon 7A") are Claude's choices, flagged for review.

Writes the ``isoform_sensitive`` block into configs/stage4/<disease>.json, with
the accessions read, the date and the boundaries used. Other keys are untouched.

  uv run python -m pipeline.extract.isoform_regions
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

EFETCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
OUT = Path("configs/stage4")

# disease: MANE Select (as in the Stage 4 config), alternatives with the words a paper uses for them, words for the MANE isoform
GENES = {
    "danon": {
        "gene": "LAMP2",
        "alternatives": [
            {"transcript": "NM_013995.2", "name": "LAMP2B (exon 9b)", "labels": r"\b(?:E|ex\.?|exon\s*)9b\b|\bLAMP-?2B\b|\bisoform\s*B\b"},
            {"transcript": "NM_001122606.1", "name": "LAMP2C (exon 9c)", "labels": r"\b(?:E|ex\.?|exon\s*)9c\b|\bLAMP-?2C\b|\bisoform\s*C\b"},
        ],
        "mane_labels": r"\b(?:E|ex\.?|exon\s*)9a\b|\bLAMP-?2A\b|\bisoform\s*A\b",
    },
    "axd": {
        "gene": "GFAP",
        "alternatives": [
            {"transcript": "NM_001131019.3", "name": "GFAP-epsilon/delta (exon 7A)", "labels": r"\bepsilon\b|\bdelta\b|GFAP-?[εδ]|\bexon\s*7A\b|\bGFAP-?ε"},
        ],
        "mane_labels": r"\balpha\b|GFAP-?α",
    },
}


def fetch_genbank(accession: str) -> str:
    q = urllib.parse.urlencode({"db": "nuccore", "id": accession, "rettype": "gb", "retmode": "text", "tool": "gp-rarelink", "email": "mail@drjimmylin.com"})
    time.sleep(0.4)
    with urllib.request.urlopen(f"{EFETCH}?{q}", timeout=120) as r:
        return r.read().decode()


def parse_exons(gb: str) -> tuple[str, list[tuple[int, int]], tuple[int, int]]:
    """(versioned accession, exon ranges in transcript coordinates, CDS range) from a GenBank mRNA record."""
    version = re.search(r"^VERSION\s+(\S+)", gb, re.M).group(1)
    feats = re.split(r"\n(?=     \S)", gb[gb.index("FEATURES"):gb.index("ORIGIN")])
    exons, cds = [], None
    for f in feats:
        body = re.sub(r"\n\s{21}", "", f)
        m = re.match(r"^\s*exon\s+(\d+)\.\.(\d+)", body)
        if m:
            exons.append((int(m.group(1)), int(m.group(2))))
        m = re.match(r"^\s*CDS\s+(\d+)\.\.(\d+)", body)
        if m:
            cds = (int(m.group(1)), int(m.group(2)))
    if not exons or not cds:
        raise SystemExit(f"{version}: no exon or CDS features in the record")
    return version, exons, cds


def c_boundaries(exons: list[tuple[int, int]], cds: tuple[int, int]) -> list[int]:
    """Exon end positions in c. coordinates (CDS start = c.1), so transcripts with different 5' UTRs compare."""
    return [end - cds[0] + 1 for _, end in exons]


def divergence(mane: tuple[list[tuple[int, int]], tuple[int, int]], alt: tuple[list[tuple[int, int]], tuple[int, int]]) -> int:
    """First c. position at which the two transcripts' exon structures differ (the position after the last shared exon end)."""
    bm, ba = c_boundaries(*mane), c_boundaries(*alt)
    n = 0
    while n < min(len(bm), len(ba)) and bm[n] == ba[n]:
        n += 1
    return (bm[n - 1] if n else 0) + 1


def main() -> int:
    today = datetime.now(UTC).date().isoformat()
    for disease, spec in GENES.items():
        cfg_path = OUT / f"{disease}.json"
        cfg = json.loads(cfg_path.read_text())
        if cfg["gene"] != spec["gene"]:
            raise SystemExit(f"{disease}: config gene {cfg['gene']} != {spec['gene']}")
        mane_acc = cfg["mane_select"]
        mv, mex, mcds = parse_exons(fetch_genbank(mane_acc))
        alts, from_c = [], None
        for a in spec["alternatives"]:
            av, aex, acds = parse_exons(fetch_genbank(a["transcript"]))
            d = divergence((mex, mcds), (aex, acds))
            from_c = d if from_c is None else min(from_c, d)
            alts.append({**a, "transcript_read": av, "diverges_from_cdna": d, "exon_ends_cdna": c_boundaries(aex, acds)})
        block = {"gene": spec["gene"], "mane": mv, "from_cdna": from_c, "alternatives": alts, "mane_labels": spec["mane_labels"],
                 "mane_exon_ends_cdna": c_boundaries(mex, mcds),
                 "source": f"RefSeq mRNA GenBank records ({mv}; " + "; ".join(a["transcript_read"] for a in alts) + f") read through NCBI E-utilities efetch on {today}; "
                           "divergence computed by pipeline/extract/isoform_regions.py from the exon and CDS features",
                 "rule": "D-43 (2026-10-28): a cDNA description at or beyond from_cdna whose paper names no transcript takes the transcript its own words name "
                         "(labels or mane_labels, case-insensitive, matched against the printed variant, its span and the transcript field); if none matches, "
                         "status isoform_ambiguous and no genomic key. Label patterns are Claude's choices, flagged for review."}
        cfg["isoform_sensitive"] = [block]
        cfg_path.write_text(json.dumps(cfg, indent=2) + "\n")
        print(disease, spec["gene"], mv, "from c.", from_c, [(a["transcript_read"], a["diverges_from_cdna"]) for a in alts])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
