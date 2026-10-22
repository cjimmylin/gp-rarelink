"""Exploratory (pre-registration §7.6): what share of ClinVar ABCA1 records corresponds to
variants reported in the Tangier disease literature corpus?

Reads analysis/six_disease/o2/o2_variants.csv (concordance_o2.py, snapshot 2026-10-19) and the
dated per-gene counts (analysis/poc/reference_snapshot/2026-10-19/counts_ABCA1.json). A ClinVar
record "corresponds" when the pv1-tangier extraction matched it at tier 1 (same GRCh38 allele)
or tier 2 (same protein change, for protein-only descriptions; may name several records).
The denominator is every single-gene GRCh38 ABCA1 record; P/LP is the share among P/LP records.
This is a lower bound of literature correspondence: the corpus is open-access Tangier papers
only (D-32), and ABCA1 is also tested for HDL deficiency and cardiovascular panels.

  python3 -I analysis/exploratory/tangier_clinvar_share.py
"""
import csv
import json
from pathlib import Path

rows = [r for r in csv.DictReader(open("analysis/six_disease/o2/o2_variants.csv")) if r["disease"] == "tangier"]
counts = json.load(open("analysis/poc/reference_snapshot/2026-10-19/counts_ABCA1.json"))
sg = counts["single_gene_records"]
total = sg["total"] if isinstance(sg, dict) and "total" in sg else None
by_class = sg.get("by_classification", {}) if isinstance(sg, dict) else {}
plp_total = sum(v for k, v in by_class.items() if k in ("P", "LP", "P/LP"))
matched = [r for r in rows if r["tier"] in ("1", "2")]
vid_class = {}
for r in matched:
    for v in r["clinvar_variation_id"].split():
        vid_class[v] = r["clinvar_class"]
plp = sum(1 for c in vid_class.values() if c in ("P", "LP", "P/LP"))
out = {"date_snapshot": counts["date"], "clinvar_release_last_modified": counts["last_modified"],
       "abca1_single_gene_records": total, "abca1_plp_records": plp_total,
       "records_matched_by_tangier_literature": len(vid_class),
       "share_of_all_records": round(len(vid_class) / total, 4) if total else None,
       "plp_records_matched": plp, "share_of_plp_records": round(plp / plp_total, 4) if plp_total else None,
       "matched_by_class": {c: sum(1 for x in vid_class.values() if x == c) for c in sorted(set(vid_class.values()))},
       "extracted_tangier_variants": len(rows), "extracted_not_in_clinvar": sum(r["tier"].startswith("unmatched") for r in rows),
       "label": "EXPLORATORY (§7.6)"}
Path("analysis/exploratory/tangier_clinvar_share.json").write_text(json.dumps(out, indent=1) + "\n")
print(json.dumps(out, indent=1))
