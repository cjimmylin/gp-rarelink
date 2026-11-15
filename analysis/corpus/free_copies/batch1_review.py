"""Review checks on the D-47 addendum batch 1 runs (pv1a-<d>), 2026-11-15.

Recomputes, from committed outputs, the figures the review section of
reports/addendum_d47_batch1_findings.md cites, and writes:

  analysis/corpus/free_copies/batch1_review_<date>.json     all figures
  adjudication/addendum_d47/batch1_audit_items.csv          claims and decisions for a person to check
  analysis/corpus/free_copies/batch1_inputs_<date>.csv      sha256 of every input PDF and converted Markdown
                                                            (only when the git-ignored files are present)

Parts that need files outside git are skipped when those files are absent, and the
values already in the JSON are kept:
  - input hashes, conversion coverage and quote coverage need data/literature/<d>/fulltext{,_md}/;
  - the helper write-method counts need this session's helper transcripts (--transcripts DIR).

  uv run python analysis/corpus/free_copies/batch1_review.py --date 2026-11-15 [--transcripts DIR]
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from pipeline.extract.reconcile import is_gene  # noqa: E402

GENES = {"ha20": "TNFAIP3", "axd": "GFAP", "lad1": "ITGB2", "ssadh": "ALDH5A1", "tangier": "ABCA1"}
MISSING = {None, "", "not reported", "not stated"}
WORD = re.compile(r"[a-z]{5,}")


def val(cell):
    return cell.get("value") if isinstance(cell, dict) else cell


def norm(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def screening() -> dict:
    out = {}
    for d in GENES:
        for r in csv.DictReader((ROOT / f"data/literature/{d}/addendum_d47/screening.csv").open()):
            out[(d, r["pmid"])] = r
    return out


def local_inputs(scr: dict, date: str) -> dict | None:
    """Hashes, conversion coverage and quote coverage. None if the git-ignored files are not all here."""
    status = {(r["disease"], r["pmid"]): r for r in csv.DictReader((ROOT / "analysis/corpus/free_copies/status_2026-11-14.csv").open())}
    meta = {(r["disease"], r["pmid"]): r for r in csv.DictReader((ROOT / "reports/paywalled_papers_2026-11-14.csv").open())}
    rows, cov = [], {}
    for (d, p), s in sorted(scr.items()):
        pdf, md = ROOT / f"data/literature/{d}/fulltext/{p}.pdf", ROOT / f"data/literature/{d}/fulltext_md/{p}.md"
        mj = md.with_suffix(".meta.json")
        if not (pdf.exists() and md.exists() and mj.exists()):
            return None
        m = md.read_text()
        info = subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout
        pages = (re.search(r"Pages:\s+(\d+)", info) or [None, ""])[1]
        pw = set(WORD.findall(subprocess.run(["pdftotext", str(pdf), "-"], capture_output=True, text=True).stdout.lower()))
        share = round(len(pw & set(WORD.findall(m.lower()))) / len(pw), 3) if pw else None
        q = None
        pp = ROOT / f"data/extracted/{d}/pv1a-{d}/per_paper/{p}.json"
        if pp.exists():
            mn, spans = norm(m), set()

            def walk(x):
                if isinstance(x, dict):
                    if isinstance(x.get("span"), str) and x["span"].strip():
                        spans.update(norm(part) for part in x["span"].split(" || "))
                    for v in x.values():
                        walk(v)
                elif isinstance(x, list):
                    for v in x:
                        walk(v)
            walk(json.loads(pp.read_text()))
            mask = bytearray(len(mn))
            for sp in spans:
                i = mn.find(sp)
                while sp and i != -1:
                    mask[i:i + len(sp)] = b"\x01" * len(sp)
                    i = mn.find(sp, i + 1)
            q = round(sum(mask) / len(mn), 3)
        html = ROOT / f"data/literature/free_copies/{d}/{p}.html"
        mm = json.loads(mj.read_text())
        rows.append({"disease": d, "pmid": p, "screening": s["decision"], "europepmc_availability": meta[(d, p)]["europepmc_availability"],
                     "source_host": status[(d, p)]["source_host"], "pdf_sha256": sha(pdf), "pdf_bytes": pdf.stat().st_size, "pdf_pages": pages,
                     "markdown_sha256": sha(md), "markdown_chars": len(m), "converter": mm.get("converter", ""), "tokens_estimate": mm.get("tokens", ""),
                     "share_pdf_words_in_markdown": share, "share_markdown_quoted": q if q is not None else "",
                     "note": f"PDF printed from the saved web page (html sha256 {sha(html)}) in headless Chromium" if html.exists() else ""})
        cov[f"{d}:{p}"] = {"share_pdf_words_in_markdown": share, "share_markdown_quoted": q, "availability": meta[(d, p)]["europepmc_availability"], "screening": s["decision"]}
    with (ROOT / f"analysis/corpus/free_copies/batch1_inputs_{date}.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    inc = {k: v for k, v in cov.items() if v["screening"] == "include"}
    return {"papers": cov,
            "below_0_9_words": sorted(k for k, v in cov.items() if v["share_pdf_words_in_markdown"] is not None and v["share_pdf_words_in_markdown"] < 0.9),
            "included_by_availability": dict(Counter(v["availability"] for v in inc.values())),
            "max_share_quoted": max(v["share_markdown_quoted"] for v in inc.values()),
            "included_with_10pct_or_more_quoted": sorted(k for k, v in inc.items() if v["share_markdown_quoted"] >= 0.10),
            "included_free_to_read_with_10pct_or_more_quoted": sorted(k for k, v in inc.items() if v["share_markdown_quoted"] >= 0.10 and v["availability"] == "F")}


def transcripts(tdir: Path) -> dict:
    """How each gatekeeper helper wrote its verdict file, and whether any helper left its allowed files."""
    allowed = re.compile(r"(pipeline/extract/claude_code/prompts/|pipeline/extract/claude_code/schema_|extraction_rules_v1\.md|/fulltext_md/|scratchpad/helpers/|data/ontologies/2026-10-19/hp\.obo|/pv1a-[a-z0-9]+/(per_paper|gatekeeper_v4|hpo_model_bindings)/|/addendum_d47/labels/)")
    roles, outside, gk = Counter(), [], []
    for f in sorted(tdir.glob("agent-*.jsonl")):
        role, out, calls, results, order = None, None, {}, {}, []
        for line in f.open():
            try:
                o = json.loads(line)
            except ValueError:
                continue
            c = (o.get("message") or {}).get("content")
            if role is None and o.get("type") == "user" and isinstance(c, str):
                role = next((k for k, t in (("extraction", "extraction helper"), ("gatekeeper", "gatekeeper helper"), ("screening", "screening helper"), ("hpo", "HPO binding helper")) if t in c), "other")
                m = re.search(r"Output (?:file|CSV): (\S+)", c)
                out = m.group(1) if m else None
            if isinstance(c, list):
                for b in c:
                    if not isinstance(b, dict):
                        continue
                    if b.get("type") == "tool_use":
                        calls[b["id"]] = (b["name"], b.get("input") or {})
                        order.append(b["id"])
                    elif b.get("type") == "tool_result":
                        results[b.get("tool_use_id")] = json.dumps(b.get("content"))
        if role in (None, "other"):
            continue
        roles[role] += 1
        denied = wrote_explicit = wrote_script = False
        for i in order:
            name, inp = calls[i]
            cmd = str(inp.get("command") or "")
            if name in ("WebFetch", "WebSearch") or (name == "Bash" and re.search(r"\b(curl|wget)\b|(^|[;&|\s])git\s", cmd)):
                outside.append((f.name, name))
            p = str(inp.get("file_path") or inp.get("path") or "")
            if name in ("Read", "Grep", "Glob", "Write", "Edit") and p and not allowed.search(p):
                outside.append((f.name, p))
            if role == "gatekeeper" and out:
                if name == "Write" and p == out:
                    wrote_explicit = True
                if name == "Bash" and os.path.basename(out) in cmd:
                    if "denied" in results.get(i, "").lower()[:600]:
                        denied = True
                    elif re.search(r"DictWriter|writerow|open\(", cmd):
                        wrote_script = True
        if role == "gatekeeper":
            gk.append({"chunk": os.path.basename(out)[:-4], "helper": f.name[6:14], "script_refused": denied,
                       "final_file_written": "row by row (Write)" if wrote_explicit else "by script" if wrote_script else "unknown"})
    return {"helpers_by_role": dict(roles), "helpers_outside_allowed_files_or_tools": outside,
            "gatekeeper_helpers": gk, "gatekeeper_helpers_with_refused_script": sum(g["script_refused"] for g in gk),
            "gatekeeper_final_file_by_script": sum(g["final_file_written"] == "by script" for g in gk)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True)
    ap.add_argument("--transcripts", type=Path)
    a = ap.parse_args()
    out_json = ROOT / f"analysis/corpus/free_copies/batch1_review_{a.date}.json"
    res = json.loads(out_json.read_text()) if out_json.exists() else {}
    res["date"] = a.date
    scr = screening()

    li = local_inputs(scr, a.date)
    if li is not None:
        res["inputs"] = li
    if a.transcripts and a.transcripts.is_dir():
        res["helper_transcripts"] = transcripts(a.transcripts)

    packets, alias, labels, unsup = {}, {}, {}, {}
    for d, gene in GENES.items():
        run = ROOT / f"data/extracted/{d}/pv1a-{d}"
        ps = [json.loads(Path(f).read_text()) for f in glob.glob(str(run / "phenopackets/*.json"))]
        ids = {os.path.basename(f) for f in glob.glob(str(run / "phenopackets/*.json"))}
        reg = {os.path.basename(f) for f in glob.glob(str(ROOT / f"data/extracted/{d}/pv1-{d}/phenopackets/*.json"))}
        packets[d] = {"phenopackets": len(ps), "with_disease_entry": sum(bool(p.get("diseases")) for p in ps),
                      "with_interpretation": sum(bool(p.get("interpretations")) for p in ps),
                      "without_any_phenotypic_feature": sum(not p.get("phenotypicFeatures") for p in ps),
                      "ids_also_used_in_registered_run": len(ids & reg)}
        miss = Counter()
        n = 0
        for f in glob.glob(str(run / "per_paper/*.json")):
            for r in json.loads(Path(f).read_text())["tables"].get("variants", []):
                if val(r.get("variant_original_string")) in MISSING:
                    continue
                n += 1
                if not is_gene(val(r.get("gene_symbol_as_stated")), gene):
                    miss[f"{os.path.basename(f)[:-5]}:{val(r.get('gene_symbol_as_stated'))}"] += 1
        alias[d] = {"printed_variant_rows": n, "not_recognized_as_target_gene": dict(miss)}
        db = list(csv.DictReader((run / "disease_bindings.csv").open()))
        labels[d] = {"individuals_with_a_stated_label": sum(r["disease_label_as_stated"] not in MISSING for r in db),
                     "stated_but_unbound": [f"{r['pmid']}:{r['disease_label_as_stated']}" for r in db if r["method"] == "unbound"]}
        gkrows = [r for r in csv.DictReader((run / "gatekeeper_v4.csv").open()) if r["verdict"] == "unsupported"]
        unsup[d] = {"by_paper": dict(Counter(r["pmid"] for r in gkrows)), "by_table_field": dict(Counter(f"{r['table']}.{r['field']}" for r in gkrows))}
    res.update(phenopackets=packets, gene_symbol=alias, disease_labels=labels, gatekeeper_unsupported=unsup)

    # Tangier: the same initials in more than one paper (candidates for the same person; not confirmed)
    seen = defaultdict(set)
    for f in glob.glob(str(ROOT / "data/extracted/tangier/pv1a-tangier/per_paper/*.json")):
        for r in json.loads(Path(f).read_text())["tables"]["individuals"]:
            m = re.fullmatch(r"([A-Z])([a-z]?)[a-z]*\.?\s*([A-Z])([a-z]?)[a-z]*\.?", str(val(r["individual_label_in_paper"])).strip())
            if m:
                seen["".join(m.groups()).lower()].add(os.path.basename(f)[:-5])
    # keyed on the label's letters as printed ('C. No.' -> 'cno', 'C.N.' -> 'cn'), so the two spellings stay apart
    res["tangier_initials_in_several_papers"] = {k: sorted(v) for k, v in sorted(seen.items()) if len(v) > 1}

    # audit items
    items = []
    tg = ROOT / "data/extracted/tangier/pv1a-tangier"
    claims = {r["claim_id"]: r for r in csv.DictReader((tg / "gatekeeper_v4_claims.csv").open())}
    paper = json.loads((tg / "per_paper/198431.json").read_text())["tables"]
    for chunk in ("198431_1", "198431_2"):
        for r in csv.DictReader((tg / f"gatekeeper_v4/{chunk}.csv").open()):
            c = claims[r["claim_id"]]
            row = paper[c["table"]][int(c["row"])]
            what = str(val(row.get("checklist_feature")) or val(row.get("feature_text_as_stated")) or "")
            if re.fullmatch(r"low LDL( cholesterol)?", what) and c["field"] in ("status", "feature_text_as_stated"):
                items.append({"kind": "same sentence judged two ways (Assmann 1977, low LDL excluded in heterozygotes)", "disease": "tangier", "pmid": "198431",
                              "chunk": chunk, "claim_id": r["claim_id"], "individual": str(val(row.get("individual_label_in_paper"))),
                              "verdict_of_record": r["verdict"], "about": r["about"], "other_verdict": ""})
    for d in GENES:
        run = ROOT / f"data/extracted/{d}/pv1a-{d}"
        for f in sorted(glob.glob(str(run / "gatekeeper_v4_set_aside/*.first_attempt.csv"))):
            chunk = os.path.basename(f).replace(".first_attempt.csv", "")
            first = {r["claim_id"]: r["verdict"] for r in csv.DictReader(open(f))}
            for r in csv.DictReader((run / f"gatekeeper_v4/{chunk}.csv").open()):
                if first.get(r["claim_id"]) != r["verdict"]:
                    items.append({"kind": "two helpers disagree", "disease": d, "pmid": chunk.split("_")[0], "chunk": chunk, "claim_id": r["claim_id"],
                                  "individual": "", "verdict_of_record": r["verdict"], "about": r["about"], "other_verdict": first.get(r["claim_id"], "")})
    for g in res.get("helper_transcripts", {}).get("gatekeeper_helpers", []):
        d = next((d for d in GENES if (ROOT / f"data/extracted/{d}/pv1a-{d}/gatekeeper_v4/{g['chunk']}.csv").exists()), "")
        aside = ROOT / f"data/extracted/{d}/pv1a-{d}/gatekeeper_v4_set_aside/{g['chunk']}.first_attempt.csv"
        if g["script_refused"] and not aside.exists():
            items.append({"kind": "helper's script was refused; chunk judged once only", "disease": d, "pmid": g["chunk"].split("_")[0], "chunk": g["chunk"],
                          "claim_id": "", "individual": "", "verdict_of_record": "", "about": "", "other_verdict": ""})
    for (d, p), s in sorted(scr.items()):
        if s["decision"] == "exclude":
            items.append({"kind": f"full-text exclusion to check by a person (pre-registration 5.1): {s['exclusion_reason']}", "disease": d, "pmid": p, "chunk": "",
                          "claim_id": "", "individual": "", "verdict_of_record": "exclude", "about": "", "other_verdict": ""})
    items = [dict(t) for t in {tuple(sorted(i.items())) for i in items}]
    items.sort(key=lambda i: (i["kind"], i["disease"], i["pmid"], i["chunk"], i["claim_id"]))
    dest = ROOT / "adjudication/addendum_d47"
    dest.mkdir(parents=True, exist_ok=True)
    with (dest / "batch1_audit_items.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["kind", "disease", "pmid", "chunk", "claim_id", "individual", "verdict_of_record", "about", "other_verdict"])
        w.writeheader()
        w.writerows(items)
    res["audit_items"] = dict(Counter(i["kind"].split(":")[0] for i in items))
    ldl = [i for i in items if i["kind"].startswith("same sentence")]
    res["assmann1977_low_ldl_excluded"] = dict(Counter(f"{i['chunk']}:{i['verdict_of_record']}" for i in ldl))
    out_json.write_text(json.dumps(res, indent=1, sort_keys=True) + "\n")
    brief = {k: res[k] for k in ("phenopackets", "gene_symbol", "disease_labels", "audit_items", "assmann1977_low_ldl_excluded", "tangier_initials_in_several_papers")}
    print(json.dumps(brief, indent=0)[:3800])


if __name__ == "__main__":
    main()
