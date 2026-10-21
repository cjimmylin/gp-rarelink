"""Check WS3 evidence dossiers (D-41) against their batch and the paper texts.

For every candidate in a batch, its dossier at adjudication/o3_gaps/dossiers/<id>.json must:
  - parse, carry status "pending adjudication" and instructions_version "dossier_v1";
  - have every item in ITEMS, each with a statement; "not reported" or "not applicable"
    items carry no quotes, and every other item carries at least one quote
    (variant_type_and_mechanism may rest on the HGVS alone);
  - quote only papers in the batch, and every quote must be found in that paper's text:
    exact after collapsing whitespace, or lenient (case, Unicode form and Markdown markup
    ignored; counted apart);
  - propose no classification: ACMG criterion codes or "pathogenic"/"benign"/"VUS" wording in
    a statement outside authors_classification is a problem. Quotes are the papers' words
    and are not checked for this.

  python3 -I adjudication/o3_gaps/check_dossiers.py --batch adjudication/o3_gaps/batches/batch_01.json
  python3 -I adjudication/o3_gaps/check_dossiers.py --all      # every batch; writes check_summary.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path("adjudication/o3_gaps")
ITEMS = ("cases", "phenotype_specificity", "segregation", "de_novo", "in_trans", "functional",
         "variant_type_and_mechanism", "computational_predictions", "population_data_in_papers", "authors_classification")
EMPTY = {"not reported", "not applicable"}
CLASS_WORDS = re.compile(r"\b(PVS1|PS[1-4]|PM[1-6]|PP[1-5]|BA1|BS[1-4]|BP[1-7]|likely pathogenic|likely benign|pathogenic|benign|VUS|"
                         r"uncertain significance)\b", re.I)
WS = re.compile(r"\s+")
MARKUP = re.compile(r"[*_`|#]")


def exact(s: str) -> str:
    return WS.sub(" ", s).strip()


def lenient(s: str) -> str:
    s = unicodedata.normalize("NFKC", s).lower()
    return WS.sub(" ", MARKUP.sub(" ", s)).strip()


def quotes_in(d: dict) -> list[tuple[str, dict]]:
    out = [("variant.as_written_in_papers", q) for q in (d.get("variant") or {}).get("as_written_in_papers") or []]
    for name, item in (d.get("items") or {}).items():
        if not isinstance(item, dict):
            continue
        out += [(name, q) for q in item.get("quotes") or []]
        for person in item.get("people") or []:
            out += [(f"{name}.people", q) for q in person.get("quotes") or []]
    return out


def check_batch(batch_path: Path) -> dict:
    b = json.loads(batch_path.read_text())
    texts = {}
    for p, path in b["paper_text"].items():
        t = Path(path).read_text()
        texts[p] = (exact(t), lenient(t))
    problems, n_quotes, n_lenient, written = [], 0, 0, 0
    for c in b["candidates"]:
        cid = c["candidate_id"]
        f = ROOT / "dossiers" / f"{cid}.json"
        if not f.exists():
            problems.append(f"{cid}: dossier missing")
            continue
        try:
            d = json.loads(f.read_text())
        except json.JSONDecodeError as e:
            problems.append(f"{cid}: not valid JSON ({e})")
            continue
        written += 1
        if d.get("candidate_id") != cid:
            problems.append(f"{cid}: candidate_id is {d.get('candidate_id')!r}")
        if d.get("status") != "pending adjudication":
            problems.append(f"{cid}: status must be 'pending adjudication'")
        if d.get("instructions_version") != "dossier_v1":
            problems.append(f"{cid}: instructions_version must be 'dossier_v1'")
        items = d.get("items") or {}
        for name in ITEMS:
            it = items.get(name)
            if not isinstance(it, dict) or not isinstance(it.get("statement"), str) or not it["statement"].strip():
                problems.append(f"{cid}: item {name} missing or without a statement")
                continue
            st = it["statement"].strip()
            nq = len(it.get("quotes") or []) + sum(len(p.get("quotes") or []) for p in it.get("people") or [])
            if st.lower().rstrip(".") in EMPTY:
                if nq:
                    problems.append(f"{cid}: item {name} says '{st}' but has quotes")
            elif nq == 0 and name != "variant_type_and_mechanism":
                problems.append(f"{cid}: item {name} has a statement but no quotes")
            if name != "authors_classification":
                texts_to_check = [st] + [str(p.get(k, "")) for p in it.get("people") or [] for k in ("key_phenotypes", "zygosity_or_genotype", "other_allele")]
                for s in texts_to_check:
                    m = CLASS_WORDS.search(s)
                    if m:
                        problems.append(f"{cid}: item {name} statement uses classification wording '{m.group(0)}'")
                        break
        for note in [d.get("notes_for_panel") or ""] + list(d.get("concerns") or []):
            m = CLASS_WORDS.search(str(note))
            if m:
                problems.append(f"{cid}: notes/concerns use classification wording '{m.group(0)}'")
                break
        for where, q in quotes_in(d):
            n_quotes += 1
            if not isinstance(q, dict) or "pmid" not in q or "quote" not in q:
                problems.append(f"{cid}: {where}: quote must be an object with pmid and quote")
                continue
            p, s = str(q["pmid"]), str(q["quote"])
            if p not in texts:
                problems.append(f"{cid}: {where}: PMID {p} is not a paper of this batch")
                continue
            if not s.strip():
                problems.append(f"{cid}: {where}: empty quote")
            elif exact(s) in texts[p][0]:
                pass
            elif lenient(s) in texts[p][1]:
                n_lenient += 1
            else:
                problems.append(f"{cid}: {where}: quote not found in {p}: {s[:90]!r}")
    return {"batch": b["batch"], "candidates": len(b["candidates"]), "dossiers": written, "quotes": n_quotes,
            "quotes_lenient_only": n_lenient, "problems": problems}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--batch")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--only-mine", action="store_true", help="accepted for the helpers' convenience; same as --batch")
    args = ap.parse_args(argv)
    if args.all:
        res = [check_batch(p) for p in sorted((ROOT / "batches").glob("batch_*.json"))]
        summ = {"batches": len(res), "candidates": sum(r["candidates"] for r in res), "dossiers": sum(r["dossiers"] for r in res),
                "quotes": sum(r["quotes"] for r in res), "quotes_lenient_only": sum(r["quotes_lenient_only"] for r in res),
                "problems": sum(len(r["problems"]) for r in res), "per_batch": res}
        (ROOT / "check_summary.json").write_text(json.dumps(summ, indent=1, ensure_ascii=False) + "\n")
        print(json.dumps({k: v for k, v in summ.items() if k != "per_batch"}))
        for r in res:
            for p in r["problems"]:
                print(r["batch"], p)
        return 1 if summ["problems"] else 0
    if not args.batch:
        ap.error("--batch or --all")
    r = check_batch(Path(args.batch))
    print(json.dumps({k: v for k, v in r.items() if k != "problems"}))
    for p in r["problems"]:
        print(p)
    print("OK" if not r["problems"] else f"{len(r['problems'])} problems")
    return 1 if r["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
