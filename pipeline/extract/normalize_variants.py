"""Normalize extracted TNFAIP3 variants with VariantValidator (POC_DESIGN.md §3.8, Stage 4 step 2).

For each distinct variant description in one run's per-paper JSON (target-gene
rows with a printed variant), builds a query and calls the VariantValidator REST
API. Only normalization fields are kept: the validated transcript HGVS, the
predicted protein consequence, GRCh38 genomic HGVS and VCF key, and the
validation warnings. Database annotations in the response are dropped
(NOTES_FOR_AGENTS.md §6). The original string is always kept.

Query construction, in order:
  1. a cDNA description is taken from cdna_hgvs_as_stated, else from
     variant_original_string, with entities and whitespace removed. Legacy
     substitutions such as "c.A271T" are rewritten to "c.271A>T" (notation
     only; flagged legacy_notation_rewritten);
  2. the transcript is transcript_as_stated when it is a RefSeq NM_ or an
     Ensembl ENST accession; otherwise the MANE Select transcript (--mane,
     default NM_001270508.2, as VariantValidator's gene2transcripts reported for
     TNFAIP3 on 2026-10-19), and the row is flagged transcript_assumed;
  3. no cDNA but a protein change: status protein_only, no call (protein
     changes are never back-translated);
  4. neither (copy-number changes, exon deletions, genomic coordinates without
     a build): status not_normalized, with the reason.

A validated variant is then projected to the MANE Select transcript with a
second call on its GRCh38 genomic description.

Status per distinct description:
  normalized    VariantValidator accepted the description unchanged;
  corrected     accepted, but the validated transcript HGVS differs from the
                query (both kept);
  unresolvable  VariantValidator returned an error or warning instead of a
                result (the warning is kept);
  protein_only, not_normalized   as above.

Responses are cached on disk (data/cache/variantvalidator/, git-ignored) keyed
by the request, so re-runs are free; requests are spaced by --delay seconds.

Writes data/extracted/<disease>/<run_id>/variants_normalized.csv (one row per
distinct description) and normalization_summary.json.

  uv run python -m pipeline.extract.normalize_variants --disease ha20 --run-id poc-ha20-run-2
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
import time
from collections import Counter
from pathlib import Path
from urllib.parse import quote

import httpx

from pipeline.extract.reconcile import is_gene, protein_key

API = "https://rest.variantvalidator.org/VariantValidator/variantvalidator"
CACHE = Path("data/cache/variantvalidator")
MISSING = {None, "", "not reported"}
TX = re.compile(r"\b(N[MR]_\d+(?:\.\d+)?|ENST\d+(?:\.\d+)?)\b")
CDNA = re.compile(r"c\.[^,;()\[\]:/]+", re.IGNORECASE)
LEGACY_SUB = re.compile(r"^c\.([ACGT])(\d+)([ACGT])$", re.IGNORECASE)  # c.A271T -> c.271A>T


def v(cell):
    return (cell or {}).get("value")


def clean(s) -> str:
    return re.sub(r"\s+", "", html.unescape(str(s or "")))


def cdna_of(row: dict) -> tuple[str | None, bool]:
    """cDNA description with whitespace and entities removed; True if legacy notation was rewritten.

    Legacy substitutions printed as c.<ref><position><alt> (e.g. 'c.A271T') are
    rewritten to HGVS ('c.271A>T'); this changes notation only.
    """
    for field in ("cdna_hgvs_as_stated", "variant_original_string"):
        s = v(row.get(field))
        if s in MISSING:
            continue
        m = CDNA.search(clean(s))
        if m:
            c = m.group(0)
            c = "c." + c[2:]  # normalise 'C.' to 'c.'
            lm = LEGACY_SUB.match(c)
            if lm:
                return f"c.{lm.group(2)}{lm.group(1).upper()}>{lm.group(3).upper()}", True
            return c, False
    return None, False


def transcript_of(row: dict) -> str | None:
    for field in ("transcript_as_stated", "cdna_hgvs_as_stated", "variant_original_string"):
        s = v(row.get(field))
        if s not in MISSING:
            m = TX.search(str(s))
            if m:
                return m.group(1)
    return None


class VV:
    def __init__(self, delay: float) -> None:
        self.delay, self.last, self.calls, self.cached = delay, 0.0, 0, 0
        self.client = httpx.Client(timeout=120, headers={"accept": "application/json", "User-Agent": "gp-rarelink (literature curation)"})
        CACHE.mkdir(parents=True, exist_ok=True)

    def get(self, build: str, description: str, select: str) -> dict:
        url = f"{API}/{build}/{quote(description, safe='')}/{quote(select, safe='')}"
        key = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
        if key.exists():
            self.cached += 1
            return json.loads(key.read_text())
        wait = self.delay - (time.time() - self.last)
        if wait > 0:
            time.sleep(wait)
        for attempt in range(4):
            try:
                r = self.client.get(url)
                self.last = time.time()
                if r.status_code == 429:
                    time.sleep(10 * (attempt + 1))
                    continue
                r.raise_for_status()
                data = r.json()
                break
            except (httpx.HTTPError, ValueError) as e:
                if attempt == 3:
                    return {"_error": f"{type(e).__name__}: {e}"}
                time.sleep(5 * (attempt + 1))
        self.calls += 1
        key.write_text(json.dumps({"url": url, "response": data}))
        return {"url": url, "response": data}


def trim(resp: dict) -> dict:
    """Keep normalization fields only; report errors and warnings."""
    data = resp.get("response") or {}
    if "_error" in resp:
        return {"ok": False, "warnings": resp["_error"]}
    keys = [k for k in data if k not in ("flag", "metadata")]
    warnings = []
    for k in keys:
        rec = data[k]
        warnings += rec.get("validation_warnings") or []
        if rec.get("hgvs_transcript_variant"):
            loci = (rec.get("primary_assembly_loci") or {}).get("grch38") or {}
            vcf = loci.get("vcf") or {}
            prot = rec.get("hgvs_predicted_protein_consequence") or {}
            return {"ok": True, "hgvs_transcript": rec["hgvs_transcript_variant"],
                    "hgvs_protein": prot.get("tlr", ""), "hgvs_protein_short": prot.get("slr", ""),
                    "hgvs_genomic_grch38": loci.get("hgvs_genomic_description", ""),
                    "vcf_grch38": f"{vcf.get('chr', '')}:{vcf.get('pos', '')}:{vcf.get('ref', '')}:{vcf.get('alt', '')}" if vcf else "",
                    "gene_symbol": rec.get("gene_symbol", ""), "warnings": " | ".join(warnings),
                    "vv_version": (data.get("metadata") or {}).get("variantvalidator_version", "")}
    return {"ok": False, "warnings": " | ".join(warnings) or f"flag={data.get('flag')}"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--run-id", required=True)
    ap.add_argument("--gene", default="TNFAIP3")
    ap.add_argument("--mane", default="NM_001270508.2")
    ap.add_argument("--delay", type=float, default=1.0)
    args = ap.parse_args(argv)
    run_dir = Path("data/extracted") / args.disease / args.run_id
    distinct: dict[str, dict] = {}
    for p in sorted((run_dir / "per_paper").glob("*.json")):
        for r in (json.loads(p.read_text()).get("tables") or {}).get("variants") or []:
            if not is_gene(v(r.get("gene_symbol_as_stated")), args.gene) or v(r.get("variant_original_string")) in MISSING:
                continue
            orig = str(v(r.get("variant_original_string")))
            (cdna, legacy), tx = cdna_of(r), transcript_of(r)
            prot = protein_key(v(r.get("protein_hgvs_as_stated"))) or protein_key(orig)
            key = f"{tx or ''}|{cdna or ''}|{prot or ''}|{'' if (cdna or prot) else clean(orig).lower()}"
            d = distinct.setdefault(key, {"cdna": cdna, "transcript": tx, "protein": prot, "original": orig, "rows": 0, "pmids": set(),
                                          "legacy": legacy})
            d["rows"] += 1
            d["pmids"].add(p.stem)
    vv, out, c = VV(args.delay), [], Counter()
    for key, d in distinct.items():
        row = {"variant_key": key, "original_string_example": d["original"], "rows": d["rows"], "pmids": " ".join(sorted(d["pmids"])),
               "query": "", "transcript_assumed": "", "legacy_notation_rewritten": "yes" if d["legacy"] else "", "status": "", "hgvs_transcript": "", "hgvs_protein": "",
               "hgvs_genomic_grch38": "", "vcf_grch38": "", "mane_hgvs_transcript": "", "mane_hgvs_protein": "", "warnings": "", "vv_version": ""}
        if d["cdna"]:
            tx = d["transcript"] if d["transcript"] else args.mane
            row["transcript_assumed"] = "" if d["transcript"] else "yes"
            row["query"] = f"{tx}:{d['cdna']}"
            res = trim(vv.get("GRCh38", row["query"], tx))
            if res["ok"]:
                row.update({k: res.get(k, "") for k in ("hgvs_transcript", "hgvs_protein", "hgvs_genomic_grch38", "vcf_grch38", "warnings", "vv_version")})
                same = clean(res["hgvs_transcript"]).lower() == clean(row["query"]).lower()
                row["status"] = "normalized" if same else "corrected"
                if res["hgvs_genomic_grch38"]:
                    mane = trim(vv.get("GRCh38", res["hgvs_genomic_grch38"], args.mane))
                    if mane["ok"]:
                        row["mane_hgvs_transcript"], row["mane_hgvs_protein"] = mane["hgvs_transcript"], mane["hgvs_protein"]
            else:
                row["status"], row["warnings"] = "unresolvable", res["warnings"]
        elif d["protein"]:
            row["status"], row["mane_hgvs_protein"] = "protein_only", d["protein"]
        else:
            row["status"], row["warnings"] = "not_normalized", "no cDNA or protein description (copy-number change, exon deletion or coordinates without build)"
        c[row["status"]] += 1
        c["rows:" + row["status"]] += d["rows"]
        out.append(row)
    with (run_dir / "variants_normalized.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    n = len(out)
    summary = {"run_id": args.run_id, "mane_select": args.mane, "distinct_descriptions": n,
               "status_counts": {k: c[k] for k in ("normalized", "corrected", "protein_only", "not_normalized", "unresolvable")},
               "row_counts": {k[5:]: c[k] for k in c if k.startswith("rows:")},
               "share_normalized_or_corrected": round((c["normalized"] + c["corrected"]) / n, 4) if n else None,
               "share_normalized_or_corrected_of_cdna": round((c["normalized"] + c["corrected"]) / max(1, c["normalized"] + c["corrected"] + c["unresolvable"]), 4),
               "transcript_assumed": sum(1 for r in out if r["transcript_assumed"]),
               "api_calls": vv.calls, "cache_hits": vv.cached,
               "vv_version": next((r["vv_version"] for r in out if r["vv_version"]), "")}
    (run_dir / "normalization_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
