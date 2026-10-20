"""Corpus seeds and holdouts for one disease, from configs/diseases.yaml.

Two commands:

  background  Writes data/literature/<disease>/seeds/background_bibliography.csv
              from the background/manifest.csv rows the config lists under
              background_keys (pmid, doi, seed_source = background_bibliography).
              Rows without a PMID are kept with an empty pmid and a note, and
              skipped by build_manifest. Comparator holdouts are never seeded.

  holdouts    After screening, marks the config's comparator papers (bias arm,
              pre-registration §7.4.1, D-04) as out of the extraction corpus in
              manifest.csv: in_extraction_corpus = false, with the reason in
              notes. A holdout that the search did not find is reported, not
              added.

ClinVar and OMIM citation lists are not used (pre-registration §5.1).

  uv run python -m pipeline.extract.corpus.disease_seeds background --disease axd
  uv run python -m pipeline.extract.corpus.disease_seeds holdouts --disease axd
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import yaml

CONFIG = Path("configs/diseases.yaml")


def config(disease: str) -> dict:
    return yaml.safe_load(CONFIG.read_text())["diseases"][disease]


def background(disease: str) -> int:
    cfg = config(disease)
    with Path("background/manifest.csv").open(newline="") as fh:
        rows = {r["key"]: r for r in csv.DictReader(fh)}
    hold = set(cfg.get("holdouts", {}).values())
    out = Path("data/literature") / disease / "seeds" / "background_bibliography.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    written = []
    for k in cfg["background_keys"]:
        r = rows[k]
        if r["pmid"] in hold:
            continue
        written.append({"pmid": r["pmid"], "doi": r["doi"], "seed_source": "background_bibliography",
                        "note": f"{k}" + ("" if r["pmid"] else "; no PMID in background/manifest.csv")})
    with out.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pmid", "doi", "seed_source", "note"])
        w.writeheader()
        w.writerows(written)
    print(json.dumps({"disease": disease, "seeds": len(written), "without_pmid": sum(not r["pmid"] for r in written), "file": str(out)}))
    return 0


def holdouts(disease: str) -> int:
    cfg = config(disease)
    hold = {pmid: key for key, pmid in cfg.get("holdouts", {}).items()}
    path = Path("data/literature") / disease / "manifest.csv"
    rows = list(csv.DictReader(path.open(newline="")))
    cols = list(rows[0].keys())
    marked = []
    for r in rows:
        if r["pmid"] in hold:
            note = f"held out: bias-arm comparator candidate {hold[r['pmid']]} (pre-registration §7.4.1, D-04)"
            if note not in r.get("notes", ""):
                r["notes"] = (r.get("notes", "") + " | " + note).strip(" |")
            r["in_extraction_corpus"] = "false"
            marked.append(r["pmid"])
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols)
        w.writeheader()
        w.writerows(rows)
    print(json.dumps({"disease": disease, "held_out": marked, "not_in_manifest": sorted(set(hold) - set(marked))}))
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=["background", "holdouts"])
    ap.add_argument("--disease", required=True)
    args = ap.parse_args(argv)
    return background(args.disease) if args.cmd == "background" else holdouts(args.disease)


if __name__ == "__main__":
    raise SystemExit(main())
