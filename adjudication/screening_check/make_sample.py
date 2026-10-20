"""Human check of screening (pre-registration §5.1; Jimmy, 2026-10-20): the item list.

Two parts, per disease in configs/diseases.yaml:
  A. a random 10% (rounded up) of the title/abstract-stage inclusions
     (in_extraction_corpus = true), seed 20261020. The rater sees title and
     abstract only and gives an independent label (include / exclude / unsure);
     the screening label is not shown.
  B. every full-text-stage exclusion (fulltext_screen = exclude). The rater sees
     the exclusion reason and the helper's verbatim evidence quote, with links to
     the paper, and agrees or disagrees.

Writes adjudication/screening_check/sample.csv (ids and labels only; committed)
and, outside git, <out>/screening_check_items.json with titles, abstracts and
quotes for the rating page (abstracts are publisher text).

  uv run python adjudication/screening_check/make_sample.py --out <scratch>
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import random
from pathlib import Path

import yaml

LIT = Path("data/literature")
HERE = Path(__file__).resolve().parent
SEED = 20261020


def abstracts(disease: str) -> dict[str, dict]:
    out = {}
    for f in sorted((LIT / disease / "screening" / "work").glob("batch_*.jsonl")):
        for line in f.read_text().splitlines():
            if line.strip():
                r = json.loads(line)
                out[r["pmid"]] = r
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="folder outside git for the page data")
    ap.add_argument("--share", type=float, default=0.10)
    args = ap.parse_args(argv)
    cfg = yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"]
    rng = random.Random(SEED)
    sheet, items = [], []
    for d, c in cfg.items():
        rows = list(csv.DictReader((LIT / d / "manifest.csv").open(newline="")))
        abs_ = abstracts(d)
        inc = sorted((r for r in rows if r["in_extraction_corpus"].lower() == "true"), key=lambda r: int(r["pmid"]))
        pick = rng.sample(inc, math.ceil(args.share * len(inc)))
        for r in sorted(pick, key=lambda r: int(r["pmid"])):
            a = abs_.get(r["pmid"], {})
            iid = f"A-{d}-{r['pmid']}"
            sheet.append({"item_id": iid, "part": "A", "disease": d, "pmid": r["pmid"],
                          "screen_label": f"{r['study_type']} / {r['relevance']}"})
            items.append({"id": iid, "part": "A", "disease": c["name"], "gene": c["gene"], "pmid": r["pmid"],
                          "title": r["title"], "year": r["year"], "journal": r["journal"],
                          "abstract": a.get("abstract", ""), "doi": r.get("doi", ""), "pmcid": r.get("pmcid", "")})
        md = LIT / d / "screening_fulltext" / "labels"
        quotes = {}
        for f in sorted(md.glob("*.csv")):
            for lab in csv.DictReader(f.open(newline="")):
                quotes[lab["pmid"]] = lab
        for r in rows:
            if r.get("fulltext_screen") != "exclude":
                continue
            lab = quotes.get(r["pmid"], {})
            iid = f"B-{d}-{r['pmid']}"
            sheet.append({"item_id": iid, "part": "B", "disease": d, "pmid": r["pmid"],
                          "screen_label": f"exclude ({r.get('fulltext_screen_reason', '')})"})
            items.append({"id": iid, "part": "B", "disease": c["name"], "gene": c["gene"], "pmid": r["pmid"],
                          "title": r["title"], "year": r["year"], "journal": r["journal"],
                          "reason": r.get("fulltext_screen_reason", ""), "quote": lab.get("evidence_quote", ""),
                          "note": lab.get("note", ""), "study_type": r.get("fulltext_study_type", ""),
                          "doi": r.get("doi", ""), "pmcid": r.get("pmcid", "")})
    with (HERE / "sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["item_id", "part", "disease", "pmid", "screen_label"])
        w.writeheader()
        w.writerows(sheet)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "screening_check_items.json").write_text(json.dumps(items, indent=1) + "\n")
    print(json.dumps({"seed": SEED, "part_A": sum(s["part"] == "A" for s in sheet),
                      "part_B": sum(s["part"] == "B" for s in sheet),
                      "missing_abstracts": sum(1 for i in items if i["part"] == "A" and not i["abstract"])}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
