"""Check a checklist-to-HPO map against its checklist and the pinned HPO release (D-40).

  uv run python -m pipeline.extract.check_checklist_map --disease danon \
      --map configs/checklist_hpo/danon.json --checklist configs/checklists/danon.json

Checks:
  - the map has exactly the checklist's item names as keys (the names the schema uses);
  - every term exists in the pinned HPO release and is not obsolete;
  - each item has an 'observed' term or null, an 'excluded' list and a 'note';
Exits non-zero on any error.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from pipeline.extract import ontologies


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--disease", required=True)
    ap.add_argument("--map", required=True)
    ap.add_argument("--checklist", required=True)
    a = ap.parse_args(argv)
    hp = ontologies.load("hp", ontologies.latest_dir())
    m = json.loads(Path(a.map).read_text())
    names = [x["name"] for x in json.loads(Path(a.checklist).read_text())["checklist"]]
    items = m.get("items") or {}
    errors, warnings = [], []
    if set(items) != set(names):
        errors.append(f"keys differ from checklist: missing {sorted(set(names) - set(items))}, extra {sorted(set(items) - set(names))}")
    if m.get("hpo_release") != hp.version:
        errors.append(f"hpo_release {m.get('hpo_release')} != pinned {hp.version}")
    for name, it in items.items():
        if set(it) - {"observed", "excluded", "note"} or "excluded" not in it or "observed" not in it or not it.get("note"):
            errors.append(f"{name}: needs exactly observed, excluded, note")
            continue
        for tid in ([it["observed"]] if it["observed"] else []) + list(it["excluded"]):
            if tid not in hp.terms:
                errors.append(f"{name}: {tid} not in HPO {hp.version}")
            elif hp.terms[tid].obsolete:
                errors.append(f"{name}: {tid} is obsolete")
        if not it["excluded"] and not it["observed"]:
            errors.append(f"{name}: no terms at all")
    print(json.dumps({"disease": a.disease, "map": a.map, "items": len(items), "errors": errors, "warnings": warnings}, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
