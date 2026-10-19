"""Copy the ratings saved on the rating page into the two rating sheets.

The rating page (built by make_rating_page.py, published as a private claude.ai
Artifact) saves each rating as a document in its own store: `ratings/<claim_id>`
with {rating, note, updated_at} and `hpo/h<nn>` with {ok, note, updated_at}.
Claude reads the store with the ArtifactData tool (`list` with `out_dir`), which
writes one JSON file per document under <dir>/ratings/ and <dir>/hpo/. This
script reads those files and fills:
  sample.csv                        'rating (...)' and 'note'
  hpo_model_binding_sample.csv      'rater_ok (yes/no)' and 'rater_note'
and keeps the raw documents in ratings_raw.json with the date they were read.
A sheet cell that already holds a value is overwritten only with --overwrite.

  uv run python adjudication/poc_audit/apply_ratings.py --dir <out_dir> --read-on 2026-10-20
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RATING_COL = "rating (supported / partially supported / unsupported)"
LABEL = {"supported": "supported", "partially_supported": "partially supported", "unsupported": "unsupported"}


def load(dirpath: Path) -> dict[str, dict]:
    out = {}
    for p in sorted(dirpath.glob("*.json")):
        doc = json.loads(p.read_text())
        body = doc.get("data", doc)
        out[doc.get("id", p.stem)] = body
    return out


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dir", required=True)
    ap.add_argument("--read-on", required=True, help="date the store was read (ISO)")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args(argv)
    ratings = load(Path(args.dir) / "ratings")
    hpo = load(Path(args.dir) / "hpo")

    def fill(path: Path, key, col, note_col, value_of):
        rows = list(csv.DictReader(path.open()))
        changed = 0
        for r in rows:
            doc = key(r)
            if doc is None:
                continue
            v = value_of(doc)
            if v and (args.overwrite or not r[col].strip()):
                r[col], r[note_col] = v, doc.get("note", "")
                changed += 1
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        return changed, sum(bool(r[col].strip()) for r in rows), len(rows)

    c1 = fill(HERE / "sample.csv", lambda r: ratings.get(r["claim_id"]), RATING_COL, "note",
              lambda d: LABEL.get(d.get("rating", ""), ""))
    c2 = fill(HERE / "hpo_model_binding_sample.csv", lambda r: hpo.get(f"h{int(r['n']):02d}"), "rater_ok (yes/no)", "rater_note",
              lambda d: d.get("ok", "") if d.get("ok") in ("yes", "no") else "")
    (HERE / "ratings_raw.json").write_text(json.dumps({"read_on": args.read_on, "ratings": ratings, "hpo": hpo},
                                                       indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    print(json.dumps({"claims": {"written": c1[0], "rated": c1[1], "of": c1[2]},
                      "hpo": {"written": c2[0], "rated": c2[1], "of": c2[2]}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
