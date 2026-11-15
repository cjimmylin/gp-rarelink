"""Which pv1s-majeed outputs may be pushed under D-51 (2026-11-15).

D-51: until D-16 is settled, no session pushes extraction outputs (quotes) from
papers that are free to read but not openly licensed. The run directory
data/extracted/majeed/pv1s-majeed/ is git-ignored; this script lists the files
that may be added with `git add -f`, and writes analysis/majeed/d51_public_files.json
(what is public, what is held back and why).

Open = the manifest's licence names a Creative Commons licence, or (records with
no PMID) the document states one; see OPEN_NOPMID. Everything else is held back.

  python3 analysis/majeed/d51_public_files.py          # print the list
  python3 analysis/majeed/d51_public_files.py --add    # also git add -f them
"""
from __future__ import annotations

import csv
import json
import subprocess
import sys
from pathlib import Path

RUN = Path("data/extracted/majeed/pv1s-majeed")
OPEN_NOPMID = {"N88": "CC BY-NC (stated in the document)"}       # N66 names no licence: held back
SUMMARIES = ["reconcile_summary.json", "normalization_summary.json", "binding_summary.json", "gatekeeper_v4_summary.json",
             "gatekeeper_v4_prep.json", "phenopacket_build.json", "validation_report.json", "span_check.json"]


def main() -> int:
    man = {r["pmid"]: r for r in csv.DictReader(open("data/literature/majeed/manifest.csv"))}
    docs = [p.stem for p in (RUN / "per_paper").glob("*.json")]
    open_ids, held = {}, {}
    for d in sorted(docs):
        lic = (man.get(d, {}).get("license") or "").lower()
        if d in OPEN_NOPMID:
            open_ids[d] = OPEN_NOPMID[d]
        elif "creative commons" in lic or "creativecommons" in lic or lic.startswith("cc-by") or "(cc by)" in lic:
            open_ids[d] = man[d]["license"][:80]
        else:
            held[d] = man.get(d, {}).get("license") or man.get(d, {}).get("access_status") or "no licence named"
    files = [RUN / "per_paper" / f"{d}.json" for d in open_ids]
    files += [p for p in (RUN / "gatekeeper_v4").glob("*.csv") if p.stem.rsplit("_", 1)[0] in open_ids]
    pp_public, pp_held = [], []
    for p in sorted((RUN / "phenopackets").glob("*.json")):
        refs = {ev["reference"]["id"].split(":", 1)[1] for ev in _evidence(json.loads(p.read_text()))}
        (pp_public if refs <= set(open_ids) else pp_held).append(p)
    files += pp_public + [RUN / s for s in SUMMARIES if (RUN / s).exists()]
    out = {"rule": "D-51 (2026-11-15)", "open_documents": open_ids, "held_back_documents": held,
           "phenopackets_public": len(pp_public), "phenopackets_held_back": len(pp_held),
           "held_back_files": "claims.csv, gatekeeper_v4.csv, gatekeeper_v4_claims.csv, individuals_reconciled.csv, merges.csv, "
                              "variants_normalized.csv, hpo_bindings.csv, disease_bindings.csv, hpo_model_bindings/, gatekeeper_v4_set_aside/, "
                              "and every per-paper, gatekeeper-chunk and phenopacket file that quotes a held-back document",
           "public_files": sorted(str(f) for f in files)}
    Path("analysis/majeed/d51_public_files.json").write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "public_files"}, indent=1, ensure_ascii=False), f"\n{len(files)} files")
    redact_candidates(set(open_ids))
    if "--add" in sys.argv:
        subprocess.run(["git", "add", "-f", *map(str, files)], check=True)
    return 0


def redact_candidates(open_ids: set[str], path: Path = Path("analysis/majeed/o3/candidates.csv")) -> None:
    """Keep only example spans from open documents in the O3 candidate table (evidence_rows.jsonl stays git-ignored)."""
    if not path.exists():
        return
    rows = list(csv.DictReader(path.open(newline="")))
    for r in rows:
        parts = [x for x in (r.get("example_spans") or "").split(" || ") if x]
        before = sum(int(x[1:].split(" ", 1)[0]) for x in parts if "withheld, D-51]" in x)  # idempotent re-runs
        spans = [x for x in parts if "withheld, D-51]" not in x]
        kept = [x for x in spans if x.startswith("[") and x[1:].split(" ", 1)[0] in open_ids]
        n = before + len(spans) - len(kept)
        r["example_spans"] = " || ".join(kept + ([f"[{n} span(s) from held-back papers withheld, D-51]"] if n else []))
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


def _evidence(x):
    if isinstance(x, dict):
        if "reference" in x and isinstance(x["reference"], dict) and "id" in x["reference"]:
            yield x
        for v in x.values():
            yield from _evidence(v)
    elif isinstance(x, list):
        for v in x:
            yield from _evidence(v)


if __name__ == "__main__":
    raise SystemExit(main())
