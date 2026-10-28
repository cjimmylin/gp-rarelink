"""Normalize extracted target-gene variants (TNFAIP3 by default; per disease from configs/stage4, D-40) with VariantValidator (POC_DESIGN.md §3.8, Stage 4 step 2).

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
     TNFAIP3 on 2026-10-19), and the row is flagged transcript_assumed = yes.
     A transcript printed without a version number gets the latest version
     VariantValidator lists for that accession (transcript_assumed = version);
  3. no cDNA but a protein change: status protein_only, no call (protein
     changes are never back-translated);
  4. neither (copy-number changes, exon deletions, genomic coordinates without
     a build): status not_normalized, with the reason.

A validated variant is then projected to the MANE Select transcript with a
second call on its GRCh38 genomic description.

Repairs (D-26, decided 2026-10-19), each flagged on the row:
  - an Ensembl transcript (ENST) is sent to VariantValidator's Ensembl
    endpoint instead of the RefSeq one;
  - a versioned transcript VariantValidator does not hold (e.g. NM_006290.5)
    is retried with the latest version it lists for that accession
    (transcript_assumed = version_mapped);
  - a cDNA string listed in configs/hgvs_query_corrections.csv (obvious
    notation typos, each with its reason) is queried in corrected form; the
    extracted string is kept in query_corrected_from.

Isoform-sensitive positions (D-43, decided 2026-10-28). Some genes have
alternative coding exons (LAMP2 exons 9a/9b/9c, GFAP exon 7A), so a cDNA
position at or beyond the point where the isoforms diverge names different
genomic bases on different transcripts. When a paper gives no transcript and
the position lies in such a region (configs/stage4/<disease>.json,
"isoform_sensitive", computed by pipeline/extract/isoform_regions.py), the
paper's own words decide: a label naming an alternative isoform or exon
("E9b", "LAMP2B", "epsilon", "exon 7A") selects that transcript, a label
naming the MANE isoform keeps it (transcript_assumed = isoform_from_label,
the reason in isoform_note); with no label the description gets status
isoform_ambiguous and no genomic key, and the candidates are listed in
warnings. Below the divergence point nothing changes.

Status per distinct description:
  normalized    VariantValidator accepted the description unchanged;
  corrected     accepted, but the validated transcript HGVS differs from the
                query (both kept);
  unresolvable  VariantValidator returned an error or warning instead of a
                result (the warning is kept);
  isoform_ambiguous  no transcript stated and the position lies where the
                gene's coding isoforms diverge (D-43); not queried;
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
API_ENSEMBL = "https://rest.variantvalidator.org/VariantValidator/variantvalidator_ensembl"
CACHE = Path("data/cache/variantvalidator")
MISSING = {None, "", "not reported"}
TX = re.compile(r"\b(N[MR]_\d+(?:\.\d+)?|ENST\d+(?:\.\d+)?)\b")
CDNA = re.compile(r"c\.[^,;()\[\]:/]+", re.IGNORECASE)
LEGACY_SUB = re.compile(r"^c\.([ACGT])(\d+)([ACGT])$", re.IGNORECASE)  # c.A271T -> c.271A>T


def v(cell):
    return cell.get("value") if isinstance(cell, dict) else None  # a cell not in {value, span} shape reads as missing


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


def isoform_rule(cdna: str, labels: str, rules: list[dict]) -> tuple[str | None, str]:
    """D-43: choose the transcript for a description whose paper names none, when its position lies where coding isoforms diverge.

    Returns (transcript, note). transcript is None when the rule does not apply (note "") or when the
    paper gives no isoform label either (note starts with "ambiguous").
    """
    m = re.match(r"^c\.(\*?)(-?\d+)", cdna or "")
    if not m or int(m.group(2)) < 1 and not m.group(1):
        return None, ""
    pos = 10 ** 6 if m.group(1) else int(m.group(2))  # c.* positions (3' UTR) lie beyond every coding boundary
    for rule in rules:
        if pos < int(rule["from_cdna"]):
            continue
        for alt in rule.get("alternatives", []):
            if re.search(alt["labels"], labels, re.I):
                return alt["transcript"], f"isoform from the paper's label: {alt['name']} ({alt['transcript']})"
        if rule.get("mane_labels") and re.search(rule["mane_labels"], labels, re.I):
            return rule["mane"], f"isoform from the paper's label: MANE Select ({rule['mane']})"
        alts = ", ".join(a["transcript"] for a in rule.get("alternatives", []))
        return None, (f"ambiguous: {cdna} lies at or beyond c.{rule['from_cdna']}, where {rule['gene']} coding isoforms diverge "
                      f"(MANE {rule['mane']}; alternatives {alts}); the paper names no transcript or isoform, so no genomic key is assigned (D-43)")
    return None, ""


def label_text(r: dict) -> str:
    """The words a paper prints around a variant: the printed variant, its span, the transcript field and its span, the cDNA span."""
    parts = []
    for field in ("variant_original_string", "transcript_as_stated", "cdna_hgvs_as_stated"):
        cell = r.get(field)
        if isinstance(cell, dict):
            val, span = cell.get("value"), cell.get("span")
            if val not in MISSING:
                parts.append(str(val))
            if isinstance(span, str):
                parts.append(span)
            elif isinstance(span, list):
                parts += [str(x) for x in span]
    return " ".join(parts)


def latest_versions(vv: "VV", gene: str) -> dict[str, str]:
    """Unversioned accession -> latest versioned accession known to VariantValidator for the gene."""
    resp = vv.get_tool(f"tools/gene2transcripts_v2/{gene}/all/all/GRCh38")
    best: dict[str, str] = {}
    for g in resp.get("response") or []:
        for t in g.get("transcripts") or []:
            ref = t.get("reference", "")
            if "." in ref:
                acc, ver = ref.rsplit(".", 1)
                if acc not in best or int(ver) > int(best[acc].rsplit(".", 1)[1]):
                    best[acc] = ref
    return best


class VV:
    def __init__(self, delay: float) -> None:
        self.delay, self.last, self.calls, self.cached = delay, 0.0, 0, 0
        self.client = httpx.Client(timeout=120, headers={"accept": "application/json", "User-Agent": "gp-rarelink (literature curation)"})
        CACHE.mkdir(parents=True, exist_ok=True)

    def get_tool(self, path: str) -> dict:
        return self._fetch(f"https://rest.variantvalidator.org/VariantValidator/{path}")

    def get(self, build: str, description: str, select: str) -> dict:
        base = API_ENSEMBL if description.startswith("ENST") else API
        return self._fetch(f"{base}/{build}/{quote(description, safe='')}/{quote(select, safe='')}")

    def _fetch(self, url: str) -> dict:
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
    ap.add_argument("--corrections", default="configs/hgvs_query_corrections.csv")
    ap.add_argument("--no-config", action="store_true", help="ignore configs/stage4/<disease>.json")
    args = ap.parse_args(argv)
    cfg_path = Path("configs/stage4") / f"{args.disease}.json"
    rules: list[dict] = []
    if cfg_path.exists() and not args.no_config:  # D-40: gene and MANE Select per disease
        cfg = json.loads(cfg_path.read_text())
        args.gene, args.mane = cfg["gene"], cfg["mane_select"]
        rules = cfg.get("isoform_sensitive", [])  # D-43
    corrections = {}
    if args.corrections and Path(args.corrections).exists():
        corrections = {r["cdna_as_extracted"]: r for r in csv.DictReader(Path(args.corrections).open())}
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
                                          "legacy": legacy, "labels": set()})
            d["rows"] += 1
            d["pmids"].add(p.stem)
            d["labels"].add(label_text(r))
    vv, out, c = VV(args.delay), [], Counter()
    versions = latest_versions(vv, args.gene)
    for key, d in distinct.items():
        row = {"variant_key": key, "original_string_example": d["original"], "rows": d["rows"], "pmids": " ".join(sorted(d["pmids"])),
               "query": "", "query_corrected_from": "", "transcript_assumed": "", "legacy_notation_rewritten": "yes" if d["legacy"] else "", "status": "", "hgvs_transcript": "", "hgvs_protein": "",
               "hgvs_genomic_grch38": "", "vcf_grch38": "", "mane_hgvs_transcript": "", "mane_hgvs_protein": "", "warnings": "", "vv_version": "",
               "isoform_note": ""}
        ambiguous = False
        if d["cdna"]:
            tx = d["transcript"] if d["transcript"] else args.mane
            row["transcript_assumed"] = "" if d["transcript"] else "yes"
            if not d["transcript"] and rules:  # D-43
                chosen, note = isoform_rule(d["cdna"], " ".join(sorted(d["labels"])), rules)
                if chosen:
                    tx, row["transcript_assumed"], row["isoform_note"] = chosen, "isoform_from_label", note
                elif note:
                    ambiguous, row["isoform_note"] = True, note
        if ambiguous:
            row["status"], row["warnings"], row["query"] = "isoform_ambiguous", row["isoform_note"], f"{args.mane}:{d['cdna']} (not sent)"
        elif d["cdna"]:
            if tx and "." not in tx and tx in versions:  # printed without a version number
                tx = versions[tx]
                row["transcript_assumed"] = "version"
            cdna = d["cdna"]
            if cdna in corrections:
                row["query_corrected_from"] = cdna
                cdna = corrections[cdna]["cdna_query"]
            row["query"] = f"{tx}:{cdna}"
            res = trim(vv.get("GRCh38", row["query"], tx))
            acc = tx.rsplit(".", 1)[0]
            if not res["ok"] and "not in our database" in res.get("warnings", "") and versions.get(acc) and versions[acc] != tx:
                tx = versions[acc]
                row["transcript_assumed"] = "version_mapped"
                row["query"] = f"{tx}:{cdna}"
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
               "status_counts": {k: c[k] for k in ("normalized", "corrected", "protein_only", "not_normalized", "unresolvable", "isoform_ambiguous")},
               "row_counts": {k[5:]: c[k] for k in c if k.startswith("rows:")},
               "share_normalized_or_corrected": round((c["normalized"] + c["corrected"]) / n, 4) if n else None,
               "share_normalized_or_corrected_of_cdna": round((c["normalized"] + c["corrected"]) / max(1, c["normalized"] + c["corrected"] + c["unresolvable"]), 4),
               "transcript_assumed": sum(1 for r in out if r["transcript_assumed"] == "yes"),
               "transcript_version_assumed": sum(1 for r in out if r["transcript_assumed"] == "version"),
               "transcript_version_mapped": sum(1 for r in out if r["transcript_assumed"] == "version_mapped"),
               "transcript_isoform_from_label": sum(1 for r in out if r["transcript_assumed"] == "isoform_from_label"),
               "isoform_rules": [{"gene": x["gene"], "from_cdna": x["from_cdna"], "alternatives": [a["transcript"] for a in x["alternatives"]]} for x in rules],
               "query_corrected": sum(1 for r in out if r["query_corrected_from"]),
               "cdna_descriptions": c["normalized"] + c["corrected"] + c["unresolvable"],
               "api_calls": vv.calls, "cache_hits": vv.cached,
               "vv_version": next((r["vv_version"] for r in out if r["vv_version"]), "")}
    (run_dir / "normalization_summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
