"""Public copies of the Majeed review material (D-54), with quotes from held-back papers withheld (D-51).

The working files are local and git-ignored, because six of the run's 24 documents are free
to read but not openly licensed:
  adjudication/majeed/o1m_audit/sample.csv      the audit sample with values and quoted spans
  adjudication/majeed/o3/dossiers/*.json        the evidence dossiers
This script writes what may be committed:
  adjudication/majeed/o1m_audit/sample_public.csv   rows from held-back documents keep their
        identifiers; person label, context, value and span are withheld
  adjudication/majeed/o3/dossiers_public/*.json     only the dossiers that read open documents
        alone, unchanged; a dossier that draws on a held-back document stays local as a whole,
        because its statements paraphrase that paper (listed with its sha256 in the summary)
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
        import hashlib
        dst.mkdir(parents=True, exist_ok=True)
        for old in dst.glob("*.json"):
            old.unlink()
        public, held_back = [], {}
        for f in sorted(src.glob("G-majeed-*.json")):
            d = json.loads(f.read_text())
            c = Counter()
            redact(d, held, c)                                   # counts quotes that come from held-back documents
            papers = {str(x) for x in d.get("papers_read") or []}
            n_quotes = f.read_text().count('"quote"')
            if c or papers & held:
                # a dossier that draws on a held-back document is kept out whole: its statements paraphrase that paper
                held_back[f.stem] = {"papers_read": sorted(papers), "held_back_papers": sorted(papers & held),
                                     "quotes_from_held_back_papers": sum(c.values()),
                                     "sha256": hashlib.sha256(f.read_bytes()).hexdigest()}
            else:
                (dst / f.name).write_text(f.read_text())
                public.append(f.stem)
        summary["dossiers"] = {"written": len(public) + len(held_back), "public": public, "held_back": held_back}
    (ROOT / "d51_review_public.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
