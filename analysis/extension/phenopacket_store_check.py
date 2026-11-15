"""Check that the study genes have no cohort in Monarch's phenopacket-store.

Re-run:
    git clone --depth 1 --filter=blob:none --no-checkout \
        https://github.com/monarch-initiative/phenopacket-store <clone>
    uv run python -m analysis.extension.phenopacket_store_check --clone <clone>

Writes analysis/extension/phenopacket_store_check_<date>.json. Only file names are
read (git ls-tree), so no phenopacket content is downloaded.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
from pathlib import Path

PRIMARY = ["GFAP", "ITGB2", "TNFAIP3", "ALDH5A1", "LAMP2", "ABCA1"]
EXTENSION = ["NOD2", "LPIN2", "LCAT", "GAMT", "SLC2A10", "PSTPIP1"]


def git(clone: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(clone), *args], check=True,
                          capture_output=True, text=True).stdout


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--clone", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=Path("analysis/extension"))
    a = ap.parse_args()

    commit = git(a.clone, "log", "-1", "--format=%H %cs").split()
    folders = [p.split("/", 1)[1] for p in git(a.clone, "ls-tree", "-d", "--name-only",
                                                 "HEAD", "notebooks/").split()]
    files = git(a.clone, "ls-tree", "-r", "--name-only", "HEAD").split("\n")
    phenopackets = [f for f in files if "/phenopackets/" in f and f.endswith(".json")]
    folder_set = {f.upper() for f in folders}
    genes = {}
    for g in PRIMARY + EXTENSION:
        # A gene folder, or any phenopacket file path naming the gene as a whole token.
        pat = re.compile(rf"(^|[/_\-.]){re.escape(g)}([/_\-.]|$)", re.I)
        hits = [f for f in phenopackets if pat.search(f)]
        genes[g] = {"set": "extension" if g in EXTENSION else "primary",
                    "gene_folder": g.upper() in folder_set,
                    "phenopacket_paths_naming_gene": hits}
    out = {
        "checked": dt.date.today().isoformat(),
        "repository": "https://github.com/monarch-initiative/phenopacket-store",
        "commit": commit[0], "commit_date": commit[1],
        "gene_folders": len(folders),
        "phenopacket_files": len(phenopackets),
        "genes": genes,
        "all_absent": not any(v["gene_folder"] or v["phenopacket_paths_naming_gene"]
                              for v in genes.values()),
    }
    a.out_dir.mkdir(parents=True, exist_ok=True)
    path = a.out_dir / f"phenopacket_store_check_{out['checked']}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(path, "all_absent =", out["all_absent"], "folders =", len(folders),
          "phenopackets =", len(phenopackets))


if __name__ == "__main__":
    main()
