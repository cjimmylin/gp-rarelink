"""Render the direct-extraction baseline instruction for one disease (SLIDERS ablation, D-44).

The template `prompts/direct_v1.md` names the disease, the gene and the 20-item checklist
through three placeholders. The checklist is the same list the frozen schema carries for the
disease: for HA20 it is read from `schema_ha20_v5.json`, for the other diseases from
`configs/checklists/<disease>.json` (the lists the D-38 instantiation used). Nothing else is
disease-specific, and nothing from the frozen `extract_v6.md` rules is added.

  uv run python -m pipeline.extract.claude_code.direct_prompt --disease ha20
    writes prompts/direct_v1_ha20.md and prints its sha256
  uv run python -m pipeline.extract.claude_code.direct_prompt --disease ha20 --launch 37324276 --run-id direct-ha20
    prints the filled launch prompt for one paper (what a helper is given)
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parent
ROOT = BASE.parents[2]
TEMPLATE = BASE / "prompts" / "direct_v1.md"
LAUNCH = BASE / "prompts" / "direct_launch_v1.txt"

# Disease name as it reads in prose, and the gene (CONTEXT.md §4; the same names instantiate_disease.py uses).
DISEASES = {
    "ha20": ("A20 haploinsufficiency (HA20)", "TNFAIP3"),
    "ssadh": ("succinic semialdehyde dehydrogenase (SSADH) deficiency", "ALDH5A1"),
    "tangier": ("Tangier disease", "ABCA1"),
    "lad1": ("leukocyte adhesion deficiency type I (LAD-I)", "ITGB2"),
    "axd": ("Alexander disease", "GFAP"),
    "danon": ("Danon disease", "LAMP2"),
}


def checklist(disease: str) -> list[str]:
    """The disease's 20 checklist features, as the frozen schema lists them."""
    if disease == "ha20":
        schema = json.loads((BASE / "schema_ha20_v5.json").read_text())
        desc = next(t["description"] for t in schema["tables"] if t["name"] == "phenotype_checklist")
        tail = desc.split("Checklist:", 1)[1].split(". (v3", 1)[0]
        return [x.strip().rstrip(".") for x in tail.split(";") if x.strip()]
    cfg = json.loads((ROOT / "configs" / "checklists" / f"{disease}.json").read_text())
    return [item["name"] for item in cfg["checklist"]]


def render(disease: str) -> str:
    name, gene = DISEASES[disease]
    items = checklist(disease)
    text = TEMPLATE.read_text()
    for key, val in (("{DISEASE}", name), ("{GENE}", gene), ("{N_CHECKLIST}", str(len(items))),
                     ("{CHECKLIST}", "\n".join(f"- {x}" for x in items))):
        if key not in text:
            raise ValueError(f"placeholder {key} missing from {TEMPLATE}")
        text = text.replace(key, val)
    return text


def rendered_path(disease: str) -> Path:
    return BASE / "prompts" / f"direct_v1_{disease}.md"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def task_paths(disease: str, pmid: str, run_id: str, scratch: Path) -> dict[str, Path]:
    return {"instructions": rendered_path(disease),
            "paper": ROOT / f"data/literature/{disease}/fulltext_md/{pmid}.md",
            "output": ROOT / f"data/extracted/{disease}/{run_id}/records/{pmid}.json",
            "scratch": scratch}


def launch_text(disease: str, pmid: str, run_id: str, scratch: Path) -> str:
    return LAUNCH.read_text().format(**{k: str(v) for k, v in task_paths(disease, pmid, run_id, scratch).items()})


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True, choices=sorted(DISEASES))
    ap.add_argument("--launch", metavar="PMID", help="print the filled launch prompt for this paper instead of rendering")
    ap.add_argument("--run-id")
    ap.add_argument("--scratch", default="/tmp/direct_scratch")
    a = ap.parse_args(argv)
    if a.launch:
        print(launch_text(a.disease, a.launch, a.run_id or f"direct-{a.disease}", Path(a.scratch) / a.launch))
        return 0
    out = rendered_path(a.disease)
    out.write_text(render(a.disease))
    print(json.dumps({"written": str(out.relative_to(ROOT)), "sha256": sha256(out), "template_sha256": sha256(TEMPLATE),
                      "checklist_items": len(checklist(a.disease))}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
