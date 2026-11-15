"""NOD2 legacy-numbering sensitivity analysis for Blau syndrome (D-47 extension; not a pipeline change).

Under the registered rule (pipeline v1.0, normalize_variants), a cDNA description with no stated
transcript is read on the MANE Select transcript, NM_001370466.1 (1013 aa). Much of the Blau
literature numbers NOD2 on the older NM_022162 transcript (1040 aa; the familiar R334W is
c.1000C>T there), so those descriptions fail with a reference mismatch on MANE and stay
unplaced.

This script reports what a revised rule would give: for each Blau description that the
registered run left `unresolvable` with `transcript_assumed = yes` and a ReferenceMismatchError
on MANE, it asks VariantValidator again on NM_022162.3 and, when that succeeds, projects the
result onto MANE. VariantValidator still checks the reference base, so a description written on
neither transcript fails again. It writes a separate file and changes nothing in the registered
run. Adopting the revised rule would be a deviation and needs Jimmy's approval.

  uv run python -m analysis.extension.nod2_legacy_sensitivity
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from pipeline.extract.normalize_variants import VV, trim

RUN = Path("data/extracted/blau/pv1-blau")
OUT = Path("analysis/extension/nod2")
MANE = "NM_001370466.1"
LEGACY = "NM_022162.3"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = list(csv.DictReader((RUN / "variants_normalized.csv").open()))
    vv = VV(delay=1.0)
    out, n_try, n_ok = [], 0, 0
    for r in rows:
        r = dict(r)
        r["revised_rule"] = ""
        if (r["status"] == "unresolvable" and r["transcript_assumed"] == "yes"
                and r["query"].startswith(MANE + ":") and "ReferenceMismatch" in r["warnings"]):
            n_try += 1
            q = LEGACY + ":" + r["query"].split(":", 1)[1]
            res = trim(vv.get("GRCh38", q, LEGACY))
            if res.get("ok"):
                mane = trim(vv.get("GRCh38", res["hgvs_genomic_grch38"], MANE))
                r.update({"query": q, "status": "normalized", "hgvs_transcript": res["hgvs_transcript"],
                          "hgvs_protein": res["hgvs_protein"], "hgvs_genomic_grch38": res["hgvs_genomic_grch38"],
                          "vcf_grch38": res["vcf_grch38"], "warnings": res["warnings"], "vv_version": res["vv_version"],
                          "mane_hgvs_transcript": mane.get("hgvs_transcript", "") if mane.get("ok") else "",
                          "mane_hgvs_protein": mane.get("hgvs_protein", "") if mane.get("ok") else "",
                          "revised_rule": f"legacy transcript {LEGACY} assumed after a reference mismatch on {MANE}"})
                n_ok += 1
            else:
                r["revised_rule"] = f"tried {LEGACY}: {res.get('warnings', '')[:200]}"
        out.append(r)
    fields = list(out[0].keys())
    with (OUT / "variants_normalized_revised.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(out)
    reg = sum(1 for r in rows if r["status"] in ("normalized", "corrected"))
    rev = sum(1 for r in out if r["status"] in ("normalized", "corrected"))
    cdna = sum(1 for r in rows if r["status"] != "protein_only")
    summary = {"run_id": "pv1-blau", "distinct_descriptions": len(rows), "non_protein_only": cdna,
               "registered_rule_normalized": reg, "revised_rule_candidates": n_try,
               "revised_rule_placed_on_legacy": n_ok, "revised_rule_normalized": rev,
               "legacy_transcript": LEGACY, "mane_select": MANE,
               "api_calls": vv.calls, "cache_hits": vv.cached,
               "note": "Sensitivity analysis only; the registered run is unchanged. The revised rule is a proposed deviation."}
    (OUT / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")
    print(json.dumps(summary, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
