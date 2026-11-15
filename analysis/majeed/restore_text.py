"""Re-fetch the text of pv1s-majeed's openly available JATS documents in a new container.

The run's Markdown (data/literature/majeed/fulltext_md/) is git-ignored and gone with the
container. The six held-back documents' Markdown is in Jimmy's Drive zip (README there).
This script restores the others that came as JATS XML: it fetches each by the route the
manifest records, compares the sha256 with the manifest's, writes the XML to the git-ignored
fulltext/ folder, and leaves conversion to `pipeline.extract.corpus.to_markdown`. It never
writes the manifest (fetch_fulltext would). Run span_check afterwards: every quote of the run
must still be found, which is the test that the restored text is the text the run read.

  uv run python analysis/majeed/restore_text.py
  uv run python -m pipeline.extract.corpus.to_markdown --disease majeed --no-count --formats nxml --skip-existing
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path

from pipeline.extract.corpus.eutils import Client

BASE = Path("data/literature/majeed")
RUN = Path("data/extracted/majeed/pv1s-majeed")


def main() -> int:
    man = {r["pmid"]: r for r in csv.DictReader((BASE / "manifest.csv").open(newline=""))}
    docs = sorted(json.loads((RUN / "span_check.json").read_text())["per_paper"])
    out = BASE / "fulltext"
    out.mkdir(exist_ok=True)
    client = Client()
    report = []
    for d in docs:
        r = man.get(d)
        if not r or r.get("fulltext_format") != "nxml":
            report.append({"doc": d, "status": "not JATS: restore by hand (PDF or held-back text)"})
            continue
        if (BASE / "fulltext_md" / f"{d}.md").exists():
            report.append({"doc": d, "status": "Markdown already present"})
            continue
        fetch = client.europepmc_fulltext_xml if r["access_status"] == "europepmc_xml" else client.efetch_pmc_xml
        xml = fetch(r["pmcid"])
        if xml is None:
            other = client.efetch_pmc_xml if r["access_status"] == "europepmc_xml" else client.europepmc_fulltext_xml
            xml = other(r["pmcid"])
            route = "other route"
        else:
            route = r["access_status"]
        if xml is None:
            report.append({"doc": d, "status": "no XML from either route"})
            continue
        sha = hashlib.sha256(xml).hexdigest()
        (out / f"{d}.nxml").write_bytes(xml)
        report.append({"doc": d, "status": "fetched", "route": route, "sha256_matches_manifest": sha == r["sha256"]})
    for x in report:
        print(x)
    print({"fetched": sum(x["status"] == "fetched" for x in report),
           "sha256_same": sum(bool(x.get("sha256_matches_manifest")) for x in report)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
