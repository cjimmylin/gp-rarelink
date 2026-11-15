"""Per-disease Stage 4 settings (D-40): gene, HGNC ID, MANE Select, Mondo terms, checklist map.

  uv run python -m pipeline.extract.stage4_config          # writes configs/stage4/<disease>.json
  from pipeline.extract.stage4_config import load; load("danon")

Facts are read, not typed in:
  - HGNC ID and MANE Select RefSeq transcript from VariantValidator's
    gene2transcripts_v2 (cached by normalize_variants.VV), with the date read;
  - the disease's Mondo term is the one current Mondo term whose name equals the
    disease name below (the names in CONTEXT.md §4, in Mondo's wording; checked by
    script against the pinned Mondo release). The extraction guard forbids
    reference-database identifiers in this directory, so no cross-reference is used.
Choices made here (flagged for review, D-40):
  - the label rule: a stated disease label matching DISEASE_LABEL is bound to the
    disease's Mondo term (HA20's rule, generalized);
  - the group term used as the diagnosis when no disease label is stated: HA20 keeps
    its gene-based group term MONDO:0100222 (pilot choice); the other five have one
    Mondo term for the gene's disease, which is used for both.
HA20's settings reproduce the pilot's defaults exactly.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

DISEASES = {
    #        gene       Mondo name of the disease                     checklist map                          label rule (case-insensitive)
    "ha20": ("TNFAIP3", "autoinflammatory syndrome, familial, Behcet-like 1", "configs/ha20_checklist_hpo.json",
             r"\bHA20\b|A20\s+haploinsufficien|haploinsufficiency\s+of\s+A20|\bAISBL"),
    "ssadh": ("ALDH5A1", "succinic semialdehyde dehydrogenase deficiency", "configs/checklist_hpo/ssadh.json",
              r"succinic\s+semi-?aldehyde\s+dehydrogenase|\bSSADH|4-?hydroxybutyric\s+acid(uria|emia)|gamma-?hydroxybutyric\s+acid(uria|emia)|\bGHB\s+aciduria"),
    "tangier": ("ABCA1", "Tangier disease", "configs/checklist_hpo/tangier.json",
                r"\bTangier|analphalipoproteinemia|familial\s+(high\s+density|HDL)\s+(lipoprotein\s+)?deficiency"),
    "lad1": ("ITGB2", "leukocyte adhesion deficiency 1", "configs/checklist_hpo/lad1.json",
             r"leu[ck]ocyte\s+adhesion\s+deficiency(?!\s*(type\s*)?-?\s*(II|III|2|3)\b)|\bLAD[\s-]*(type\s*)?(I|1)\b(?!I)"),
    "axd": ("GFAP", "Alexander disease", "configs/checklist_hpo/axd.json",
            r"\bAlexander(['’]s)?\s+disease|\bAxD\b"),
    "danon": ("LAMP2", "Danon disease", "configs/checklist_hpo/danon.json",
              r"\bDanon|glycogen\s+storage\s+disease\s+(type\s+)?(IIb|2b)\b|LAMP-?2\s+(cardiomyopathy|deficiency|disease)"),
    # Extension diseases (D-52, recorded as D-47 in the extension session, 2026-11-14). Mondo names checked against release 2026-10-06.
    "blau": ("NOD2", "Blau syndrome", "configs/checklist_hpo/blau.json",
             r"\bBlau|early[\s-]+onset\s+sarcoidosis|juvenile\s+systemic\s+granulomatosis|(pa?ediatric|familial)\s+granulomatous\s+arthritis"),
    "lcat": ("LCAT", "LCAT deficiency", "configs/checklist_hpo/lcat.json",
             r"\bLCAT\s+deficiency|lecithin[\s:-]+cholesterol\s+acyl\s*-?transferase\s+deficiency|fish[\s-]+eye\s+disease|\bNorum"),
    "gamt": ("GAMT", "guanidinoacetate methyltransferase deficiency", "configs/checklist_hpo/gamt.json",
             r"\bGAMT\s+deficiency|guanidino\s*-?acetate\s+(N-)?methyl\s*-?transferase\s+deficiency"),
    "ats": ("SLC2A10", "arterial tortuosity syndrome", "configs/checklist_hpo/ats.json", r"arterial\s+tortuosity\s+syndrome"),
    "papa": ("PSTPIP1", "pyogenic arthritis-pyoderma gangrenosum-acne syndrome", "configs/checklist_hpo/papa.json",
             r"\bPAPA\b|pyogenic\s+(sterile\s+)?arthritis[,\s]+pyoderma|\bPAMI\b|PSTPIP1[\s-]+associated"),
    # Substitute disease, added 2026-11-15 (Jimmy's request; not part of the six-disease study)
    "majeed": ("LPIN2", "Majeed syndrome", "configs/checklist_hpo/majeed.json",
               r"\bMajeed|chronic\s+recurrent\s+multifocal\s+osteomyelitis\W+(and\s+|with\s+)?congenital\s+dyserythropoietic|\bCRMO\W+(and|with)\W+CDA\b|LPIN2[\s-]+(related|deficiency|associated)|\bMJDS\b"),
}
EXTENSION = ("blau", "majeed", "lcat", "gamt", "ats", "papa")
HA20_GROUP = "MONDO:0100222"
OUT = Path("configs/stage4")


def load(disease: str) -> dict:
    return json.loads((OUT / f"{disease}.json").read_text())


def main(argv: list[str] | None = None) -> int:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--diseases", "--disease", dest="diseases", nargs="*", choices=sorted(DISEASES), default=None,
                    help="write only these slugs (default: all, which rewrites every config and its read date; "
                         "the extension used --diseases " + " ".join(EXTENSION) + ", the Majeed run --disease majeed)")
    args = ap.parse_args(argv)
    from pipeline.extract import ontologies
    from pipeline.extract.normalize_variants import VV
    mondo = ontologies.load("mondo", ontologies.latest_dir())
    vv = VV(1.0)
    OUT.mkdir(parents=True, exist_ok=True)
    today = datetime.now(UTC).date().isoformat()
    for d, (gene, dname, cmap, rule) in DISEASES.items():
        if args.diseases and d not in args.diseases:
            continue
        r = vv.get_tool(f"tools/gene2transcripts_v2/{gene}/all/all/GRCh38")
        if "_error" in r:
            raise SystemExit(f"{gene}: {r['_error']}")
        g = next(x for x in r["response"] if x.get("current_symbol") == gene)
        mane = [t["reference"] for t in g["transcripts"] if (t.get("annotations") or {}).get("mane_select") and t["reference"].startswith("NM_")]
        if len(mane) != 1:
            raise SystemExit(f"{gene}: expected one RefSeq MANE Select, got {mane}")
        hits = [t for t in mondo.terms.values() if not t.obsolete and t.id.startswith("MONDO:") and t.name == dname]
        if len(hits) != 1:
            raise SystemExit(f"{dname!r}: expected one Mondo term, got {[t.id for t in hits]}")
        dm = hits[0]
        group = HA20_GROUP if d == "ha20" else dm.id
        cfg = {"disease": d, "gene": gene, "hgnc_id": g["hgnc"], "mane_select": mane[0],
               "gene_source": f"VariantValidator gene2transcripts_v2 ({r.get('url', '')}), read {today}",
               "disease_mondo": dm.id, "disease_mondo_label": dm.name,
               "group_mondo": group, "group_mondo_label": mondo.terms[group].name, "mondo_release": mondo.version,
               "disease_label_rule": rule, "checklist_map": cmap,
               "note": "Generated by pipeline/extract/stage4_config.py (D-40). The label rule and group term are Claude's choices, flagged for review."}
        (OUT / f"{d}.json").write_text(json.dumps(cfg, indent=2) + "\n")
        print(d, gene, cfg["hgnc_id"], cfg["mane_select"], dm.id, dm.name, group)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
