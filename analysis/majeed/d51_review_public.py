"""Public copies of the Majeed review material (D-54), with quotes from held-back papers withheld (D-51).

The working files are local and git-ignored, because six of the run's 24 documents are free
to read but not openly licensed:
  adjudication/majeed/o1m_audit/sample.csv      the audit sample with values and quoted spans
  adjudication/majeed/o3/dossiers/*.json        the evidence dossiers
This script writes what may be committed:
  adjudication/majeed/o1m_audit/sample_public.csv   rows from held-back documents keep their
        identifiers; person label, context, value and span are withheld
  adjudication/majeed/o3/dossiers_public/*.json     every quote from a held-back document is
        replaced by a note giving its length; statements and quotes from open documents stay
  adjudication/majeed/d51_review_public.json        what was withheld, by document

Held-back documents come from analysis/majeed/d51_public_files.json (the run's own D-51 record).

  python3 -I analysis/majeed/d51_review_public.py
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

ROOT = Path("adjudication/majeed")
WITHHELD = "[withheld, D-51: document not openly licensed]"


def redact(node, held: set[str], count: Counter):
    """Replace quotes whose pmid is a held-back document, at any depth."""
    if isinstance(node, dict):
        pm = str(node.get("pmid", ""))
        if "quote" in node and pm in held and isinstance(node["quote"], str):
            count[pm] += 1
            return {**{k: redact(v, held, count) for k, v in node.items() if k != "quote"},
                    "quote": f"[quote withheld, D-51: {len(node['quote'])} characters from a document not openly licensed]"}
        if pm in held and isinstance(node.get("quotes"), list):      # a person entry: its quotes are from that paper
            out = {k: redact(v, held, count) for k, v in node.items() if k != "quotes"}
            out["quotes"] = []
            for q in node["quotes"]:
                if isinstance(q, str):
                    count[pm] += 1
                    out["quotes"].append(f"[quote withheld, D-51: {len(q)} characters from a document not openly licensed]")
                else:
                    out["quotes"].append(redact(q if "pmid" in q else {**q, "pmid": pm}, held, count))
            return out
        return {k: redact(v, held, count) for k, v in node.items()}
    if isinstance(node, list):
        return [redact(x, held, count) for x in node]
    return node


def main() -> int:
    rec = json.loads(Path("analysis/majeed/d51_public_files.json").read_text())
    held = set(rec["held_back_documents"])
    summary = {"rule": "D-51 (2026-11-15)", "held_back_documents": sorted(held)}

    sample = ROOT / "o1m_audit/sample.csv"
    if sample.exists():
        rows = list(csv.DictReader(sample.open(newline="")))
        n = 0
        for r in rows:
            if r["pmid"] in held:
                n += 1
                for k in ("individual", "context", "value", "span"):
                    r[k] = WITHHELD
        with (ROOT / "o1m_audit/sample_public.csv").open("w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            w.writeheader()
            w.writerows(rows)
        summary["audit_sample"] = {"rows": len(rows), "rows_withheld": n}

    src, dst = ROOT / "o3/dossiers", ROOT / "o3/dossiers_public"
    if src.exists():
        dst.mkdir(parents=True, exist_ok=True)
        per, total = {}, Counter()
        for f in sorted(src.glob("G-majeed-*.json")):
            c = Counter()
            d = redact(json.loads(f.read_text()), held, c)
            if c:
                d["d51_note"] = (f"{sum(c.values())} quote(s) from documents not openly licensed ({', '.join(sorted(c))}) are withheld in this "
                                 "public copy; the full dossier is on the adjudication page and in the private copy.")
            (dst / f.name).write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
            per[f.stem] = sum(c.values())
            total.update(c)
        summary["dossiers"] = {"written": len(per), "with_withheld_quotes": sum(1 for v in per.values() if v),
                               "quotes_withheld": sum(total.values()), "quotes_withheld_by_document": dict(sorted(total.items()))}
        # no quote from a held-back document may remain: check every string of every public dossier against the full ones
        leaks = 0
        for f in sorted(src.glob("G-majeed-*.json")):
            full, pub = json.loads(f.read_text()), (dst / f.name).read_text()

            def held_quotes(node, pm=""):
                if isinstance(node, dict):
                    p2 = str(node.get("pmid", pm))
                    for k, v in node.items():
                        if k == "quote" and p2 in held and isinstance(v, str):
                            yield v
                        elif k == "quotes" and p2 in held and isinstance(v, list):
                            for q in v:
                                yield q if isinstance(q, str) else q.get("quote", "")
                        else:
                            yield from held_quotes(v, p2)
                elif isinstance(node, list):
                    for x in node:
                        yield from held_quotes(x, pm)
            for q in held_quotes(full):
                if len(q) > 20 and json.dumps(q, ensure_ascii=False)[1:-1] in pub:
                    leaks += 1
        summary["dossiers"]["held_back_quotes_still_present"] = leaks
    (ROOT / "d51_review_public.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 1 if summary.get("dossiers", {}).get("held_back_quotes_still_present") else 0


if __name__ == "__main__":
    raise SystemExit(main())
