"""Build the rating page for the Stage 5 human audit (POC_DESIGN.md Stage 5 step 3).

Reads the two rating sheets in this folder and writes one self-contained HTML
page (published as a private claude.ai Artifact) where Jimmy rates:
  - the 50 sampled claims (sample.csv): supported / partially supported /
    unsupported, with a note;
  - the 30 model-step HPO bindings (hpo_model_binding_sample.csv): yes / no,
    with a note.

The page shows, for each claim, the value, the person and the quote; and, folded
away, where the quote sits in the paper (the table caption and header row, or
the paragraph), taken from the run-2 Markdown the extraction and the gatekeeper
read. That is the same view the gatekeeper had. In the first pass the
gatekeeper verdict is NOT put in the page: without --second-look this script
never reads gatekeeper.csv, and it fails if the sheet carries a column that
looks like a verdict.

--second-look (POC_DESIGN.md Stage 5 step 3, after the first ratings are in)
adds a tab with every claim the rater did not call supported, plus every claim
where the rater and the gatekeeper disagree on supported vs not. Each shows the
rater's first rating and the gatekeeper's verdict side by side, with the paper
context open, for a final label and a reason.

For the HPO rows it adds the term's definition from the pinned hp.obo.

  uv run python adjudication/poc_audit/make_rating_page.py --out <scratch>/audit_ratings.html
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
RATING_COL = "rating (supported / partially supported / unsupported)"
FIELD_LABELS = {
    "status": "Status",
    "gene_symbol_as_stated": "Gene, as printed",
    "protein_hgvs_as_stated": "Protein change, as printed",
    "cdna_hgvs_as_stated": "cDNA change, as printed",
    "variant_original_string": "Variant, as printed",
    "variant_type_as_stated": "Variant type",
    "zygosity": "Zygosity",
    "pathogenicity_as_stated_by_authors": "Pathogenicity, as the authors state it",
    "functional_evidence_statement": "Functional evidence",
    "parental_testing_statement": "Parental testing",
    "inheritance": "Inheritance",
    "sex": "Sex",
    "is_proband": "Is the proband",
    "ethnicity_or_country": "Ethnicity or country",
    "age_at_onset_iso8601": "Age at onset (converted)",
    "age_at_onset_original_text": "Age at onset, as written",
    "age_at_last_evaluation_iso8601": "Age at last evaluation (converted)",
    "age_at_diagnosis_iso8601": "Age at diagnosis (converted)",
    "consanguinity": "Consanguinity",
    "vital_status": "Vital status",
}
STRATA = {"variant": "Variant field", "feature_observed": "Feature, observed",
          "feature_excluded": "Feature, excluded", "demographic_inheritance": "Demographic or inheritance"}
TABLES = {"variants": "Variant", "phenotypic_features": "Feature", "individuals": "Person"}


def clean_html_cells(s: str) -> str:
    s = re.sub(r"</t[dh]>\s*<t[dh][^>]*>", " | ", s)
    s = re.sub(r"</?tr[^>]*>", "\n", s)
    s = re.sub(r"</p>\s*<p>|<br\s*/?>", " / ", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    return "\n".join(re.sub(r"[ \t]+", " ", ln).strip() for ln in s.splitlines() if ln.strip())


def is_html(s: str) -> bool:
    return bool(re.search(r"</?(td|th|tr|p)\b", s))


def find(md: str, span: str) -> int:
    i = md.find(span)
    if i >= 0:
        return i
    pat = r"\s+".join(re.escape(w) for w in span.split())
    m = re.search(pat, md) if pat else None
    return m.start() if m else -1


def context_for(md: str, span: str) -> tuple[str, str]:
    """Return (kind, excerpt) locating the span in the paper."""
    i = find(md, span)
    if i < 0:
        return "missing", ""
    line_start = md.rfind("\n", 0, i) + 1
    line_end = md.find("\n", i + len(span))
    line_end = len(md) if line_end < 0 else line_end
    line = md[line_start:line_end]
    if line.lstrip().startswith("|"):
        lines = md.split("\n")
        k = md.count("\n", 0, line_start)
        top = k
        while top > 0 and lines[top - 1].lstrip().startswith("|"):
            top -= 1
        caption = ""
        for j in range(top - 1, max(top - 6, -1), -1):
            if lines[j].strip():
                caption = lines[j].strip()
                break
        bottom = md.count("\n", 0, line_end)
        rows = [lines[top]] + (["…"] if top + 2 < k else []) + lines[max(k, top + 2):bottom + 1]
        if top + 1 < k and set(lines[top + 1].replace("|", "").strip()) <= set("-: "):
            pass  # the separator row is not shown
        return "table", "\n".join(([caption] if caption else []) + rows)
    if is_html(md[max(0, i - 2000):i + len(span)]):
        t0 = md.rfind("<table", 0, i)
        tr0 = md.rfind("<tr", 0, i)
        tr1 = md.find("</tr>", i + len(span))
        head = ""
        if t0 >= 0:
            h1 = md.find("</tr>", t0)
            if h1 > 0 and h1 < tr0:
                head = clean_html_cells(md[t0:h1 + 5])
        row = clean_html_cells(md[tr0 if tr0 >= 0 else i: (tr1 + 5) if tr1 > 0 else i + len(span)])
        cap = ""
        if t0 >= 0:
            before = md[max(0, t0 - 600):t0].strip().split("\n")
            cap = before[-1].strip() if before else ""
        return "table", "\n".join(x for x in (cap, head, "…" if head else "", row) if x)
    p0 = md.rfind("\n\n", 0, i)
    p1 = md.find("\n\n", i + len(span))
    p0 = 0 if p0 < 0 else p0 + 2
    p1 = len(md) if p1 < 0 else p1
    para = md[p0:p1]
    if len(para) > 1400:
        a = max(p0, i - 600)
        b = min(p1, i + len(span) + 600)
        para = ("…" if a > p0 else "") + md[a:b] + ("…" if b < p1 else "")
    return "text", para.strip()


def hp_definitions(obo: Path, ids: set[str]) -> dict[str, str]:
    out, cur = {}, None
    for ln in obo.read_text().splitlines():
        if ln.startswith("id: "):
            cur = ln[4:].strip()
        elif ln.startswith("def: ") and cur in ids:
            m = re.match(r'def: "(.*)"', ln)
            out[cur] = (m.group(1) if m else ln[5:]).replace('\\"', '"')
        elif ln == "[Term]":
            cur = None
    return out


def value_text(raw: str) -> str:
    try:
        v = json.loads(raw)
    except (TypeError, ValueError):
        return raw
    if isinstance(v, bool):
        return "yes" if v else "no"
    return v if isinstance(v, str) else json.dumps(v, ensure_ascii=False)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True)
    ap.add_argument("--markdown-dir", default="data/literature/ha20/fulltext_md_run2")
    ap.add_argument("--hp-obo", default="data/ontologies/2026-10-19/hp.obo")
    ap.add_argument("--template", default=str(HERE / "rating_page_template.html"))
    ap.add_argument("--second-look", action="store_true", help="add the step-3 re-read tab (reads the ratings and gatekeeper.csv)")
    ap.add_argument("--run-dir", default="data/extracted/ha20/poc-ha20-run-2")
    args = ap.parse_args(argv)
    rows = list(csv.DictReader((HERE / "sample.csv").open()))
    forbidden = [c for c in rows[0] if re.search(r"gatekeeper|verdict", c, re.I)]
    if forbidden:
        raise SystemExit(f"sample.csv carries {forbidden}; the gatekeeper verdict must stay hidden from the rater")
    claims = []
    for r in rows:
        md_path = ROOT / args.markdown_dir / f"{r['pmid']}.md"
        md = md_path.read_text() if md_path.exists() else ""
        parts = [q for q in r["span"].split(" || ") if q.strip()]
        quotes, contexts = [], []
        for q in parts:
            quotes.append({"text": clean_html_cells(q) if is_html(q) else q, "cleaned": is_html(q)})
            kind, ctx = context_for(md, q)
            if ctx and all(ctx != c["text"] for c in contexts):
                contexts.append({"kind": kind, "text": ctx, "quote": q})
            elif not ctx:
                contexts.append({"kind": "missing", "text": "", "quote": q})
        claims.append({
            "id": r["claim_id"], "n": int(r["n"]), "stratum": STRATA.get(r["stratum"], r["stratum"]),
            "pmid": r["pmid"], "person": r["individual"], "about_kind": TABLES.get(r["table"], r["table"]),
            "about": "" if r["context"] in ("", "not reported") else r["context"],
            "field": FIELD_LABELS.get(r["field"], r["field"].replace("_", " ")), "value": value_text(r["value"]),
            "quotes": quotes, "contexts": [c for c in contexts if c["text"]],
            "context_missing": [c["quote"][:80] for c in contexts if not c["text"]],
        })
    hrows = list(csv.DictReader((HERE / "hpo_model_binding_sample.csv").open()))
    defs = hp_definitions(ROOT / args.hp_obo, {h["hpo_id"] for h in hrows})
    grade = {"model_exact": "exact", "model_close": "close", "model_broader": "broader"}
    hpo = [{"id": f"h{int(h['n']):02d}", "n": int(h["n"]), "pmid": h["pmid"], "phrase": h["feature_text_as_stated"],
            "status": h["status"], "hpo_id": h["hpo_id"], "hpo_label": h["hpo_label"],
            "grade": grade.get(h["method"], h["method"]), "definition": defs.get(h["hpo_id"], "")} for h in hrows]
    second = []
    if args.second_look:
        first_label = {"supported": "supported", "partially supported": "partially_supported", "unsupported": "unsupported"}
        gk = {g["claim_id"]: g for g in csv.DictReader((ROOT / args.run_dir / "gatekeeper.csv").open())}
        by_id = {c["id"]: c for c in claims}
        for r in rows:
            human = first_label.get((r.get(RATING_COL) or "").strip().lower(), "")
            g = gk.get(r["claim_id"], {})
            verdict = g.get("verdict", "")
            if not human:
                continue
            gk_ok = verdict in ("supported", "not_judged")
            if human != "supported" or gk_ok != (human == "supported"):
                second.append({**by_id[r["claim_id"]], "first": {"rating": human, "note": r.get("note", "")},
                               "gk": {"verdict": "supported" if verdict == "not_judged" else verdict,
                                      "source": g.get("source", ""), "reason": g.get("reason", "")}})
    data = json.dumps({"claims": claims, "hpo": hpo, "second": second}, ensure_ascii=False).replace("</", "<\\/")
    page = Path(args.template).read_text().replace("/*__DATA__*/null", data)
    Path(args.out).write_text(page)
    missing = {c["id"]: c["context_missing"] for c in claims if c["context_missing"]}
    print(json.dumps({"claims": len(claims), "hpo": len(hpo), "second_look": [x["id"] for x in second], "quote_parts_not_located": missing,
                      "contexts": {k: sum(x["kind"] == k for c in claims for x in c["contexts"]) for k in ("table", "text")},
                      "definitions": sum(bool(h["definition"]) for h in hpo), "bytes": len(page)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
