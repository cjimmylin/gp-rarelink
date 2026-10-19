"""Stage 6 step 1-2: a dated ground-truth snapshot for one gene (POC_DESIGN.md Stage 6).

Harness side only. Downloads, by streaming, the ClinVar tab-delimited release
files and the HPO disease annotations, keeps the rows for one gene (or one
disease), and writes them under a reference root OUTSIDE the repository:

  <root>/<date>/clinvar/variant_summary_<GENE>.tsv     rows whose GeneID is the
        gene's or whose GeneSymbol list names it (both assemblies)
  <root>/<date>/clinvar/submission_summary_<GENE>.tsv  submissions (SCVs) for
        those VariationIDs
  <root>/<date>/clinvar/var_citations_<GENE>.tsv       citations for them
  <root>/<date>/hpo/phenotype_<DISEASE>.hpoa           HPO annotations for the
        disease IDs given (e.g. OMIM:616744)
  <root>/<date>/MANIFEST.json and counts.json

The root comes from --root or GP_RARELINK_REFERENCE_DIR. It must not lie
inside the repository: the extraction guard (pipeline/extract/guard.py)
refuses to run while a populated data/reference/ is readable, so a snapshot
in the checkout would block extraction (DECISIONS.md, 2026-10-19). Only
MANIFEST.json and counts.json are copied into the repo, to --manifest-out.

For each source file the manifest records the URL, the server's Last-Modified
date, the published md5 (where NCBI provides one) checked against the bytes
read, the sha256 of the whole file, and the rows kept. OMIM is not fetched
here: no OMIM API key is in place and its terms are not yet confirmed
(Stage 6 stop-and-ask), so the snapshot is ClinVar and HPO only.

counts.json gives distinct ClinVar VariationIDs for the gene on GRCh38 by
aggregate germline classification, single-gene and multi-gene records
separately, and how many name the disease among their conditions.

  uv run python -m pipeline.harness.snapshot_reference --gene TNFAIP3 --gene-id 7128 \
      --disease-id OMIM:616744 --disease-id MONDO:0800045 --root /home/user/gp-rarelink-reference \
      --manifest-out analysis/poc/reference_snapshot
"""

from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import io
import json
import os
import shutil
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import httpx

CLINVAR = "https://ftp.ncbi.nlm.nih.gov/pub/clinvar/tab_delimited"
HPOA = "https://purl.obolibrary.org/obo/hp/hpoa/phenotype.hpoa"
REPO = Path(__file__).resolve().parents[2]


class Hashing(io.RawIOBase):
    """Wrap an httpx byte stream so the bytes read are hashed (md5 and sha256) and counted."""

    def __init__(self, it):
        self.it, self.buf = it, b""
        self.md5, self.sha = hashlib.md5(), hashlib.sha256()
        self.n = 0

    def readable(self):
        return True

    def readinto(self, b):
        while not self.buf:
            try:
                chunk = next(self.it)
            except StopIteration:
                return 0
            self.md5.update(chunk)
            self.sha.update(chunk)
            self.n += len(chunk)
            self.buf = chunk
        k = min(len(b), len(self.buf))
        b[:k], self.buf = self.buf[:k], self.buf[k:]
        return k


def published_md5(client: httpx.Client, url: str) -> str | None:
    r = client.get(url + ".md5")
    if r.status_code != 200:
        return None
    return r.text.split()[0].strip()


def stream_filter(client, url, keep, out_path, gz):
    """Stream url, write header lines and kept rows to out_path; return the manifest entry."""
    kept = total = 0
    with client.stream("GET", url) as r:
        r.raise_for_status()
        raw = Hashing(r.iter_bytes(1 << 20))
        fh = io.BufferedReader(raw, 1 << 20)
        text = io.TextIOWrapper(gzip.GzipFile(fileobj=fh) if gz else fh, encoding="utf-8", errors="replace", newline="")
        with out_path.open("w", encoding="utf-8", newline="") as out:
            header = None
            for line in text:
                if line.startswith("#"):
                    out.write(line)
                    header = line.lstrip("#").rstrip("\n").split("\t")
                    continue
                total += 1
                if keep(header, line.rstrip("\n").split("\t")):
                    out.write(line)
                    kept += 1
        # drain anything left (gzip trailer) so the hash covers the whole file
        while fh.read(1 << 20):
            pass
        last_modified = r.headers.get("last-modified")
    return {"url": url, "last_modified": last_modified, "bytes": raw.n, "md5": raw.md5.hexdigest(),
            "sha256": raw.sha.hexdigest(), "data_rows_read": total, "rows_kept": kept,
            "kept_file": str(out_path.name)}


def names_any(phenotype_ids: str, wanted: set[str]) -> bool:
    """ClinVar PhenotypeIDS lists IDs as 'MONDO:MONDO:0800045,MedGen:C4225383,OMIM:616744', ';' or '|' between conditions."""
    ids = set()
    for x in phenotype_ids.replace("|", ",").replace(";", ",").split(","):
        x = x.strip()
        if x.startswith("MONDO:MONDO:"):
            x = x[len("MONDO:"):]
        ids.add(x)
    return bool(ids & wanted)


def classify(sig: str) -> str:
    s = sig.lower().strip()
    if s in ("", "-"):
        return "no germline classification"
    if s.startswith("vus"):  # ClinVar's newer tiered VUS terms (e.g. VUS-mid)
        return "VUS"
    if "conflicting" in s:
        return "conflicting"
    table = [("pathogenic/likely pathogenic", "P/LP"), ("likely pathogenic", "LP"), ("pathogenic", "P"),
             ("uncertain significance", "VUS"), ("benign/likely benign", "B/LB"), ("likely benign", "LB"),
             ("benign", "B"), ("not provided", "not provided")]
    first = s.split(";")[0].split(",")[0].strip()
    for k, v in table:
        if first.startswith(k):
            return v
    return "other"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--gene", required=True)
    ap.add_argument("--gene-id", required=True)
    ap.add_argument("--disease-id", action="append", required=True, help="condition IDs as in ClinVar PhenotypeIDS / HPO database_id")
    ap.add_argument("--root", default=os.environ.get("GP_RARELINK_REFERENCE_DIR"))
    ap.add_argument("--date", default=date.today().isoformat())
    ap.add_argument("--manifest-out", required=True, help="repo folder for MANIFEST.json and counts.json copies")
    ap.add_argument("--recount", action="store_true", help="recompute counts.json from an existing snapshot; download nothing")
    args = ap.parse_args(argv)
    if not args.root:
        raise SystemExit("give --root or set GP_RARELINK_REFERENCE_DIR")
    root = Path(args.root).resolve()
    if root == REPO or REPO in root.parents:
        raise SystemExit(f"{root} is inside the repository; keep ground truth outside it (extraction guard)")
    snap = root / args.date
    (snap / "clinvar").mkdir(parents=True, exist_ok=True)
    (snap / "hpo").mkdir(parents=True, exist_ok=True)
    gene, gid = args.gene, str(args.gene_id)

    def in_gene(h, f):
        row = dict(zip(h, f))
        return row.get("GeneID") == gid or gene in (row.get("GeneSymbol") or "").split(";")

    manifest = {"date": args.date, "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "gene": gene, "gene_id": gid, "disease_ids": args.disease_id, "files": {},
                "not_fetched": {"omim": "no OMIM API key; terms not confirmed (POC_DESIGN Stage 6 stop-and-ask)"},
                "location_note": "content kept outside the repository under the reference root; only this manifest and counts.json are committed"}
    vs = snap / "clinvar" / f"variant_summary_{gene}.tsv"
    if args.recount:
        manifest = json.loads((snap / "MANIFEST.json").read_text())
        rows = list(csv.DictReader((l.lstrip("#") if i == 0 else l for i, l in enumerate(vs.open(encoding="utf-8"))), delimiter="\t"))
    else:
        manifest, rows = download(args, snap, gene, gid, in_gene, manifest, vs)
    write_counts(args, snap, manifest, rows, gid)
    return 0


def download(args, snap, gene, gid, in_gene, manifest, vs):
    with httpx.Client(timeout=httpx.Timeout(120.0), follow_redirects=True) as client:
        vs = snap / "clinvar" / f"variant_summary_{gene}.tsv"
        e = stream_filter(client, f"{CLINVAR}/variant_summary.txt.gz", in_gene, vs, gz=True)
        e["md5_published"] = published_md5(client, f"{CLINVAR}/variant_summary.txt.gz")
        manifest["files"]["variant_summary"] = e
        rows = list(csv.DictReader((l.lstrip("#") if i == 0 else l for i, l in enumerate(vs.open(encoding="utf-8"))), delimiter="\t"))
        var_ids = {r["VariationID"] for r in rows}

        def in_vars(h, f):
            row = dict(zip(h, f))
            return row.get("VariationID") in var_ids

        for name, gz in (("submission_summary.txt.gz", True), ("var_citations.txt", False)):
            stem = name.split(".")[0]
            e = stream_filter(client, f"{CLINVAR}/{name}", in_vars, snap / "clinvar" / f"{stem}_{gene}.tsv", gz=gz)
            e["md5_published"] = published_md5(client, f"{CLINVAR}/{name}")
            manifest["files"][stem] = e
        ids = set(args.disease_id)
        e = stream_filter(client, HPOA, lambda h, f: bool(f) and f[0] in ids,
                          snap / "hpo" / f"phenotype_{'_'.join(i.replace(':', '') for i in args.disease_id)}.hpoa", gz=False)
        e["md5_published"] = None
        manifest["files"]["phenotype_hpoa"] = e
    for k, e in manifest["files"].items():
        if e.get("md5_published") and e["md5_published"] != e["md5"]:
            raise SystemExit(f"{k}: md5 mismatch (published {e['md5_published']}, read {e['md5']})")
        e["md5_checked"] = bool(e.get("md5_published"))
    for line in (snap / "hpo").glob("*.hpoa"):
        for l in line.open():
            if l.startswith("#") and ("date" in l.lower() or "version" in l.lower()):
                manifest["files"]["phenotype_hpoa"].setdefault("header", []).append(l.strip())
    return manifest, rows


def write_counts(args, snap, manifest, rows, gid):

    g38 = {}
    for r in rows:
        if r.get("Assembly") == "GRCh38":
            g38.setdefault(r["VariationID"], r)
    single = {v: r for v, r in g38.items() if r["GeneID"] == gid}
    multi = {v: r for v, r in g38.items() if v not in single}
    dis = set(args.disease_id)

    def names_disease(r):
        return names_any(r.get("PhenotypeIDS", ""), dis)

    counts = {"date": args.date, "source": "ClinVar variant_summary.txt.gz", "last_modified": manifest["files"]["variant_summary"]["last_modified"],
              "assembly": "GRCh38", "unit": "distinct VariationID",
              "single_gene_records": {"total": len(single), "by_classification": dict(Counter(classify(r["ClinicalSignificance"]) for r in single.values()))},
              "multi_gene_records": {"total": len(multi), "by_classification": dict(Counter(classify(r["ClinicalSignificance"]) for r in multi.values()))},
              "single_gene_naming_disease": {"total": sum(names_disease(r) for r in single.values()),
                                             "by_classification": dict(Counter(classify(r["ClinicalSignificance"]) for r in single.values() if names_disease(r)))},
              "classification_rule": "first term of the aggregate germline ClinicalSignificance; 'conflicting' if it says so",
              "hpo_annotations_kept": manifest["files"]["phenotype_hpoa"]["rows_kept"],
              "omim": "not counted (no access in place)"}
    (snap / "MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (snap / "counts.json").write_text(json.dumps(counts, indent=2) + "\n")
    dest = Path(args.manifest_out) / args.date
    dest.mkdir(parents=True, exist_ok=True)
    for n in ("MANIFEST.json", "counts.json"):
        shutil.copy(snap / n, dest / n)
    print(json.dumps(counts, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
