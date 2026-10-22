"""Build one adjudicator's page for the O3 gap variants (pre-registration §7.3, §7.5; WS4, D-41).

The page lists the gap-variant candidates, shows each one's evidence dossier
(adjudication/o3_gaps/dossiers/<id>.json, written under dossier_instructions_v1.md and
checked by check_dossiers.py), and records the adjudicator's ACMG/AMP criteria,
classification, decision (approve / reject / needs discussion), notes and active
minutes per record. Each adjudicator gets a separate page and store. The store
collection is `adjudications`, one document per candidate_id.

  python3 -I adjudication/o3_gaps/make_adjudication_page.py --adjudicator A --out <scratch>/o3_adjudicator_A.html
  python3 -I adjudication/o3_gaps/make_adjudication_page.py --adjudicator A --only-with-dossier --out ...

The page carries no ClinVar or OMIM content beyond "no ClinVar record with this allele
in the snapshot" (the definition of a candidate). Pages are not shared with anyone by
Claude: Jimmy shares them.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adjudicator", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--only-with-dossier", action="store_true")
    a = ap.parse_args(argv)
    cands = list(csv.DictReader((HERE / "candidates.csv").open()))
    meta = {}
    for b in sorted((HERE / "batches").glob("batch_*.json")):
        doc = json.loads(b.read_text())
        for c in doc["candidates"]:
            meta[c["candidate_id"]] = {"disease_name": doc["disease_name"], "inheritance": doc["inheritance"]}
    summary = json.loads((HERE / "summary.json").read_text())
    triage = {}
    if (HERE / "triage.csv").exists():  # pre-adjudication pointers from triage_flags.py
        for t in csv.DictReader((HERE / "triage.csv").open()):
            triage[t["candidate_id"]] = json.loads(t["evidence"] or "{}")
    out, missing = [], 0
    for c in cands:
        f = HERE / "dossiers" / f"{c['candidate_id']}.json"
        dossier = json.loads(f.read_text()) if f.exists() else None
        if dossier is None:
            missing += 1
            if a.only_with_dossier:
                continue
        out.append({"id": c["candidate_id"], "disease": c["disease"], "gene": c["gene"],
                    "disease_name": meta.get(c["candidate_id"], {}).get("disease_name", c["disease"]),
                    "inheritance": meta.get(c["candidate_id"], {}).get("inheritance", ""),
                    "hgvs_c": c["hgvs_c"], "hgvs_p": c["hgvs_p_predicted"], "vcf": c["vcf_grch38"],
                    "pmids": c["pmids"].split(), "n_identities": int(c["n_identities"]),
                    "original_strings": c["original_strings"], "protein_check": c["protein_check"],
                    "only_reviews": c.get("n_non_review_papers") == "0", "flags": triage.get(c["candidate_id"], {}),
                    "dossier": dossier})
    order = ["ssadh", "tangier", "lad1", "axd", "danon", "ha20"]  # HA20 last: development disease (D-18)
    out.sort(key=lambda c: (order.index(c["disease"]) if c["disease"] in order else 99, c["id"]))
    data = {"title": f"Gap-variant adjudication, adjudicator {a.adjudicator}", "adjudicator": a.adjudicator,
            "snapshot": summary["snapshot"], "store_key": f"o3-adjudication-{a.adjudicator}-v1", "candidates": out}
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")
    page = (HERE / "adjudication_page_template.html").read_text().replace("/*__DATA__*/null", blob)
    page = page.replace("<title>Gap Variant Adjudication</title>", f"<title>Gap Variant Adjudication {a.adjudicator}</title>")
    Path(a.out).write_text(page)
    print(json.dumps({"adjudicator": a.adjudicator, "candidates": len(out), "without_dossier": missing,
                      "bytes": len(page.encode())}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
