"""Instantiate the frozen extraction prompt and schema for one disease (D-38).

D-38 (Jimmy, 2026-10-20; a pre-registration deviation): the frozen
`extract_v6.md` and `schema_ha20_v5.json` name A20 haploinsufficiency and
TNFAIP3. For each of the other five diseases they are instantiated by script,
swapping only:
  - the disease name (and the HA20 abbreviation where it names the disease);
  - the gene symbol;
  - the schema path in the prompt;
  - the 20-item phenotype checklist, read from configs/checklists/<disease>.json
    (written from the disease's key review, pre-registration §6.5).
Every rule, field name, enum and example stays as frozen. In particular the
field `reports_individuals_with_tnfaip3_variant` keeps its name (it is an
identifier read by downstream scripts), and the transcript example
NM_006290.3 stays as an example of notation.

Each swap is an exact string replacement that must match the expected number of
times, so a change to the frozen files makes this script fail rather than
silently produce something else. After writing, the script checks that no
disease-specific HA20 text is left (apart from the identifiers above and the
prompt's version history) and writes a unified diff against the frozen files.

  uv run python -m pipeline.extract.claude_code.instantiate_disease --disease axd

Writes:
  pipeline/extract/claude_code/prompts/extract_v6_<disease>.md
  pipeline/extract/claude_code/schema_<disease>_v5.json
  pipeline/extract/claude_code/instantiated/<disease>.diff
  pipeline/extract/claude_code/instantiated/<disease>.json  (sha256 of inputs and outputs)
"""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import re
from pathlib import Path

import yaml

BASE = Path("pipeline/extract/claude_code")
PROMPT = BASE / "prompts/extract_v6.md"
SCHEMA = BASE / "schema_ha20_v5.json"
FROZEN_SHA = {  # pre-registration §6.5, tag pipeline-v1.0
    PROMPT: "aa689f24b470d5e6224010f34209fddd95d3ba3f8481f53feea3de3b8b99a409",
    SCHEMA: "f0fdf6b3bfead62e2f617584502b2ee6b36bc0d8b39af026c3007da437b902dd",
}
# Name as it reads in prose. The short form names the checklist ("the fixed <short> checklist").
DISPLAY = {
    "axd": ("Alexander disease", "Alexander disease"),
    "lad1": ("leukocyte adhesion deficiency type I (LAD-I)", "LAD-I"),
    "ssadh": ("succinic semialdehyde dehydrogenase (SSADH) deficiency", "SSADH deficiency"),
    "danon": ("Danon disease", "Danon disease"),
    "tangier": ("Tangier disease", "Tangier disease"),
}
HA20_CHECKLIST = ("oral ulcers; genital ulcers; gastrointestinal ulcers or inflammation; recurrent fever; arthritis or "
                  "arthralgia; uveitis or other ocular inflammation; skin lesions (rash, folliculitis, erythema nodosum); "
                  "autoimmune thyroiditis; type 1 diabetes; autoimmune hepatitis; cytopenia (autoimmune); lymphoproliferation "
                  "or lymphadenopathy; central nervous system involvement; recurrent infections; elevated inflammatory markers "
                  "(CRP/ESR); autoantibodies (ANA/other); growth failure; pericarditis or other serositis; interstitial lung "
                  "disease; vasculitis.")
# Text that may keep HA20 wording after the swap: identifiers, the version history, a notation example.
ALLOWED_LEFTOVERS = [
    "reports_individuals_with_tnfaip3_variant",
    "v5 was checked on 20 HA20 papers under D-29 (`poc-ha20-v5-subset`)",
    "NM_006290.3",
    "ha20-v4 (2026-10-19, D-23 and D-24)",
    "Derived from schema_ha20_v3.json.",
]


def sha(path_or_text) -> str:
    data = path_or_text.read_bytes() if isinstance(path_or_text, Path) else path_or_text.encode()
    return hashlib.sha256(data).hexdigest()


def swap(text: str, old: str, new: str, count: int) -> str:
    n = text.count(old)
    if n != count:
        raise SystemExit(f"expected {count} of {old!r}, found {n}: the frozen file differs from what D-38 was written for")
    return text.replace(old, new)


def checklist(disease: str) -> list[str]:
    d = json.loads(Path(f"configs/checklists/{disease}.json").read_text())
    names = [x["name"].strip() for x in d["checklist"]]
    if len(names) != 20 or len(set(names)) != 20:
        raise SystemExit(f"{disease}: the checklist must have 20 distinct names, has {len(names)} ({len(set(names))} distinct)")
    for n in names:
        if ";" in n or not n:
            raise SystemExit(f"{disease}: bad checklist name {n!r}")
    return names


def instantiate(disease: str) -> dict:
    for p, h in FROZEN_SHA.items():
        if sha(p) != h:
            raise SystemExit(f"{p} does not match its frozen sha256")
    gene = yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"][disease]["gene"]
    name, short = DISPLAY[disease]
    items = checklist(disease)

    p = PROMPT.read_text()
    p = swap(p, "A20 haploinsufficiency (HA20), the disease caused by germline *TNFAIP3* variants",
             f"{name}, the disease caused by germline *{gene}* variants", 1)
    p = swap(p, "an HA20 (A20 haploinsufficiency) diagnosis", f"a diagnosis of {name}", 1)
    p = swap(p, "`pipeline/extract/claude_code/schema_ha20_v5.json`", f"`pipeline/extract/claude_code/schema_{disease}_v5.json`", 1)
    p = swap(p, "*TNFAIP3*", f"*{gene}*", 3)

    s = SCHEMA.read_text()
    s = swap(s, "a TNFAIP3 variant or an HA20 diagnosis", f"a {gene} variant or a diagnosis of {name}", 1)
    s = swap(s, "no TNFAIP3 variant or HA20 diagnosis", f"no {gene} variant or diagnosis of {name}", 1)
    s = swap(s, "'A20 haploinsufficiency'", f"'{name}'", 1)
    s = swap(s, "fixed HA20 checklist below", f"fixed {short} checklist below", 1)
    s = swap(s, HA20_CHECKLIST, "; ".join(items) + ".", 1)
    s = swap(s, "TNFAIP3", gene, 3)
    json.loads(s)  # still valid JSON

    for label, text in (("prompt", p), ("schema", s)):
        rest = text
        for ok in ALLOWED_LEFTOVERS:
            rest = rest.replace(ok, "")
        left = re.findall(r".{0,40}(?:TNFAIP3|HA20|\bA20\b).{0,40}", rest, flags=re.IGNORECASE)
        if left:
            raise SystemExit(f"{disease} {label}: HA20 text left after the swap: {left}")

    out_p = BASE / f"prompts/extract_v6_{disease}.md"
    out_s = BASE / f"schema_{disease}_v5.json"
    out_p.write_text(p)
    out_s.write_text(s)
    inst = BASE / "instantiated"
    inst.mkdir(exist_ok=True)
    diff = "".join(difflib.unified_diff(PROMPT.read_text().splitlines(keepends=True), p.splitlines(keepends=True),
                                        str(PROMPT), str(out_p)))
    diff += "".join(difflib.unified_diff(SCHEMA.read_text().splitlines(keepends=True), s.splitlines(keepends=True),
                                         str(SCHEMA), str(out_s)))
    (inst / f"{disease}.diff").write_text(diff)
    changed = sum(1 for line in diff.splitlines() if line.startswith("+") and not line.startswith("+++"))
    record = {"disease": disease, "decision": "D-38", "gene": gene, "name": name, "checklist": items,
              "inputs": {str(PROMPT): sha(PROMPT), str(SCHEMA): sha(SCHEMA),
                         f"configs/checklists/{disease}.json": sha(Path(f"configs/checklists/{disease}.json"))},
              "outputs": {str(out_p): sha(out_p), str(out_s): sha(out_s)},
              "changed_lines": changed}
    (inst / f"{disease}.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True, choices=sorted(DISPLAY))
    args = ap.parse_args(argv)
    r = instantiate(args.disease)
    print(json.dumps({k: r[k] for k in ("disease", "gene", "changed_lines", "outputs")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
