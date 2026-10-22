"""Draft submission records for panel-approved gap variants (O3 stage 4, §7.3). All PENDING.

Format-neutral on purpose: ClinVar's collection method, assertion criteria and template for a
literature-curation submitter are still open (D-13; question drafted in
reports/drafts/clinvar_literature_submissions.md). Each record gathers what any submission will
need, from the repository only, so it can be mapped to the confirmed format later:
  variant      gene, HGNC id, MANE transcript HGVS c. and p., GRCh38 VCF allele
  condition    Mondo id and label (configs/stage4); OMIM and ORPHA numbers as CONTEXT.md §4 gives
               them (LAD-I's ORPHA number is under check, D-14)
  evidence     PMIDs; individuals (deduplicated identities) with sex, zygosity as stated,
               inheritance as stated, and observed / excluded HPO terms from their phenopackets
  assessment   the panel's classification, ACMG/AMP criteria, notes, adjudicator id and date,
               read from an export of the adjudication page's store
  status       always "pending adjudication sign-off" here; Dr. Lin's sign-off (§7.3 stage 5) is
               recorded by hand in the record, and nothing is submitted from this script.
Only candidates with decision "approve" in the export are written.

  python3 -I submissions/make_records.py --adjudications <out_dir of ArtifactData list 'adjudications'>
writes submissions/pending/<candidate_id>.json and submissions/pending/index.csv.
"""
from __future__ import annotations

import argparse
import csv
import json
from datetime import date
from pathlib import Path

CONTEXT_IDS = {  # CONTEXT.md §4 (pilot disease table)
    "ha20": ("616744", "476102"), "lad1": ("116920", "2968"), "ssadh": ("271980", "22"),
    "danon": ("300257", "34587"), "tangier": ("205400", "31150"), "axd": ("203450", "58"),
}


def load_adjudications(d: Path) -> dict[str, dict]:
    out = {}
    for f in sorted(d.rglob("G-*.json")):
        doc = json.loads(f.read_text())
        out[f.stem] = doc.get("data", doc)
    return out


def person(disease: str, identity: str) -> dict:
    f = Path(f"data/extracted/{disease}/pv1-{disease}/phenopackets/{identity}.json")
    if not f.exists():
        return {"identity": identity, "phenopacket": None}
    d = json.loads(f.read_text())
    obs = sorted({p["type"]["id"] + " " + p["type"].get("label", "") for p in d.get("phenotypicFeatures") or [] if not p.get("excluded")})
    exc = sorted({p["type"]["id"] + " " + p["type"].get("label", "") for p in d.get("phenotypicFeatures") or [] if p.get("excluded")})
    return {"identity": identity, "sex": (d.get("subject") or {}).get("sex", "UNKNOWN_SEX"),
            "references": [r["id"] for r in (d.get("metaData") or {}).get("externalReferences") or []],
            "observed": obs, "excluded": exc}


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--adjudications", required=True)
    ap.add_argument("--out", default="submissions/pending")
    a = ap.parse_args(argv)
    adj = load_adjudications(Path(a.adjudications))
    cands = {c["candidate_id"]: c for c in csv.DictReader(open("adjudication/o3_gaps/candidates.csv"))}
    ev = {e["candidate_id"]: e for e in map(json.loads, open("adjudication/o3_gaps/evidence_rows.jsonl"))}
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for cid, r in sorted(adj.items()):
        if r.get("decision") != "approve" or cid not in cands:
            continue
        c, e = cands[cid], ev[cid]
        cfg = json.loads(Path(f"configs/stage4/{c['disease']}.json").read_text())
        omim, orpha = CONTEXT_IDS[c["disease"]]
        zyg = sorted({str(x["values"].get("zygosity")) for x in e["rows"]} - {"None", "not reported"})
        inh = sorted({str(x["values"].get("inheritance")) for x in e["rows"]} - {"None", "not reported"})
        rec = {"candidate_id": cid, "status": "pending adjudication sign-off", "prepared": date.today().isoformat(),
               "variant": {"gene": c["gene"], "hgnc_id": cfg["hgnc_id"], "hgvs_c": c["hgvs_c"], "hgvs_p": c["hgvs_p_predicted"],
                           "vcf_grch38": c["vcf_grch38"], "as_written": c["original_strings"]},
               "condition": {"mondo": cfg["disease_mondo"], "label": cfg["disease_mondo_label"], "omim": omim, "orpha": orpha},
               "evidence": {"pmids": e["pmids"], "zygosity_as_stated": zyg, "inheritance_as_stated": inh,
                            "individuals": [person(c["disease"], i) for i in e["identities"]],
                            "dossier": f"adjudication/o3_gaps/dossiers/{cid}.json"},
               "assessment": {"classification": r.get("classification", ""), "criteria": r.get("criteria", {}),
                              "notes": r.get("note", ""), "adjudicator": r.get("adjudicator", ""), "decided_at": r.get("updated_at", ""),
                              "active_seconds": r.get("active_seconds")},
               "clinvar_recheck": "re-check against live ClinVar on the day of submission (§7.3)",
               "signoff": {"by": "", "date": ""}}
        (out / f"{cid}.json").write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n")
        index.append({"candidate_id": cid, "gene": c["gene"], "hgvs_c": c["hgvs_c"], "classification": rec["assessment"]["classification"],
                      "pmids": " ".join(e["pmids"]), "status": rec["status"]})
    with (out / "index.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["candidate_id", "gene", "hgvs_c", "classification", "pmids", "status"])
        w.writeheader(); w.writerows(index)
    print(json.dumps({"adjudicated": len(adj), "approved_records_written": len(index)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
