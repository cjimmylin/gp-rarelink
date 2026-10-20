"""Build one rater's page for the O1 audit (pre-registration §7.1; D-11 rater design).

Two panel members rate the same 250 claims independently; a third resolves
disagreements. Each rater gets a separate page (a separate private Artifact with its
own store), so neither can see the other's ratings. The page never shows the
gatekeeper's verdict or reasons: this script reads only sample.csv, and refuses a
sheet with a verdict-like column.

Labels (§7.1): supported / unsupported / span not found, plus "can't verify", which
§7.1 counts as unsupported and reports a sensitivity analysis without.

For each claim the page shows the value, the person, the quote and, folded away,
where the quote sits in the paper (table caption and header, or the paragraph),
from the same Markdown the extraction read (data/literature/<disease>/fulltext_md).

  uv run python adjudication/o1_audit/make_rating_page.py --rater A --out <scratch>/o1_rater_A.html
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "adjudication" / "poc_audit"))
from make_rating_page import FIELD_LABELS, clean_html_cells, context_for, is_html, value_text  # noqa: E402

TABLES = {"variants": "Variant", "phenotypic_features": "Feature", "phenotype_checklist": "Checklist item",
          "individuals": "Person", "publications": "Paper"}
DISEASE = {"ha20": "A20 haploinsufficiency", "ssadh": "SSADH deficiency", "tangier": "Tangier disease",
           "lad1": "LAD-I", "axd": "Alexander disease", "danon": "Danon disease"}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rater", required=True, help="A, B or C (C: tie-breaker, built later from the disagreements)")
    ap.add_argument("--out", required=True)
    ap.add_argument("--sample-dir", default=str(HERE))
    ap.add_argument("--template", default=str(HERE / "rating_page_template.html"))
    a = ap.parse_args(argv)
    rows = list(csv.DictReader((Path(a.sample_dir) / "sample.csv").open()))
    forbidden = [c for c in rows[0] if re.search(r"gatekeeper|verdict|reason|about", c, re.I)]
    if forbidden:
        raise SystemExit(f"sample.csv carries {forbidden}; the gatekeeper verdict must stay hidden from raters")
    claims, md_cache = [], {}
    for r in rows:
        path = ROOT / r["paper_text"]
        md = md_cache.setdefault(str(path), path.read_text() if path.exists() else "")
        parts = [q for q in r["span"].split(" || ") if q.strip()]
        quotes, contexts = [], []
        for q in parts:
            quotes.append({"text": clean_html_cells(q) if is_html(q) else q, "cleaned": is_html(q)})
            kind, ctx = context_for(md, q)
            if ctx and all(ctx != c["text"] for c in contexts):
                contexts.append({"kind": kind, "text": ctx, "quote": q})
            elif not ctx:
                contexts.append({"kind": "missing", "text": "", "quote": q})
        field = FIELD_LABELS.get(r["field"], r["field"].replace("_", " "))
        claims.append({
            "id": r["item_id"], "n": int(r["n"]), "stratum": DISEASE.get(r["disease"], r["disease"]),
            "pmid": r["pmid"], "person": r["individual"], "about_kind": TABLES.get(r["table"], r["table"]),
            "about": "" if r["context"] in ("", "not reported") else r["context"],
            "field": field, "value": value_text(r["value"]),
            "quotes": quotes, "contexts": [c for c in contexts if c["text"]],
            "context_missing": [c["quote"][:80] for c in contexts if not c["text"]],
        })
    title = f"O1 claim audit, rater {a.rater}"
    data = {"claims": claims, "hpo": [], "second": [], "store_key": f"o1-audit-rater-{a.rater}-v1"}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = (Path(a.template).read_text().replace("/*__DATA__*/null", blob)
            .replace("<title>O1 Claim Audit</title>", f"<title>O1 Audit Rater {a.rater}</title>")
            .replace("<h1>O1 claim audit</h1>", f"<h1>{title}</h1>"))
    Path(a.out).write_text(page)
    missing = {c["id"]: c["context_missing"] for c in claims if c["context_missing"]}
    print(json.dumps({"rater": a.rater, "claims": len(claims), "quote_parts_not_located": len(missing),
                      "contexts": {k: sum(x["kind"] == k for c in claims for x in c["contexts"]) for k in ("table", "text")},
                      "bytes": len(page)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
