"""Rating sheets for a person: the disputed batch-1 gatekeeper claims and the six full-text exclusions.

Reads adjudication/addendum_d47/batch1_audit_items.csv (written by batch1_review.py) and the
committed run outputs, and writes two sheets with empty columns for the rater:

  adjudication/addendum_d47/batch1_claims_to_rate.csv      one row per disputed claim, with the
      extracted value, the quote it cites, the gatekeeper verdict(s) and reason
  adjudication/addendum_d47/batch1_exclusions_to_rate.csv  the six papers excluded at full-text
      screening, with the helper's reason, quote and note (pre-registration 5.1)

Labels for the rater: supported / partially_supported / unsupported for claims; agree / disagree
for exclusions. The papers are in Jimmy's Drive folder; nothing here is new paper text (the
quotes are the ones already committed with the extraction).

  python3 -I analysis/corpus/free_copies/batch1_rating_sheets.py
"""
import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AD = ROOT / "adjudication/addendum_d47"


def val(c):
    return c.get("value") if isinstance(c, dict) else c


def main() -> None:
    items = list(csv.DictReader((AD / "batch1_audit_items.csv").open()))
    titles = {(r["disease"], r["pmid"]): r for r in csv.DictReader((ROOT / "reports/paywalled_papers_2026-11-14.csv").open())}
    rows = []
    for it in items:
        if not it["claim_id"]:
            continue
        run = ROOT / f"data/extracted/{it['disease']}/pv1a-{it['disease']}"
        c = next(r for r in csv.DictReader((run / "gatekeeper_v4.csv").open()) if r["claim_id"] == it["claim_id"])
        row = json.loads((run / f"per_paper/{c['pmid']}.json").read_text())["tables"][c["table"]][int(c["row"])]
        cell = row.get(c["field"]) or {}
        t = titles[(it["disease"], it["pmid"])]
        rows.append({"why_listed": it["kind"], "disease": it["disease"], "pmid": it["pmid"], "paper": f"{t['first_author']} {t['year']}",
                     "claim_id": it["claim_id"], "individual": str(val(row.get("individual_label_in_paper")) or ""),
                     "about_feature": str(val(row.get("checklist_feature")) or val(row.get("feature_text_as_stated")) or ""),
                     "field": f"{c['table']}.{c['field']}", "extracted_value": c["value"], "quote_cited": (cell.get("span") or "") if isinstance(cell, dict) else "",
                     "gatekeeper_verdict_of_record": c["verdict"], "gatekeeper_about": c.get("about", ""), "gatekeeper_reason": c.get("reason", ""),
                     "other_helper_verdict": it["other_verdict"], "human_verdict": "", "human_note": ""})
    with (AD / "batch1_claims_to_rate.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    ex = []
    for it in items:
        if not it["kind"].startswith("full-text exclusion"):
            continue
        s = next(r for r in csv.DictReader((ROOT / f"data/literature/{it['disease']}/addendum_d47/screening.csv").open()) if r["pmid"] == it["pmid"])
        t = titles[(it["disease"], it["pmid"])]
        ex.append({"disease": it["disease"], "pmid": it["pmid"], "paper": f"{t['first_author']} {t['year']}", "title": t["title"], "pubmed": t["pubmed_url"],
                   "helper_decision": s["decision"], "exclusion_reason": s["exclusion_reason"], "evidence_quote": s["evidence_quote"], "helper_note": s.get("note", ""),
                   "human_agrees (agree/disagree)": "", "human_note": ""})
    with (AD / "batch1_exclusions_to_rate.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(ex[0]))
        w.writeheader()
        w.writerows(ex)
    print(len(rows), "claims and", len(ex), "exclusions to rate")


if __name__ == "__main__":
    main()
