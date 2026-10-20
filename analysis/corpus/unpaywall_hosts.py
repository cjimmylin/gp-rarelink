"""Which hosts hold open copies (found by Unpaywall) that this environment could not fetch?

Reads data/literature/<disease>/fulltext/*.meta.json (git-ignored; written by
fetch_fulltext.py) for in-corpus papers without full text, and counts the hosts of
Unpaywall PDF links that failed, by reason (refused or unreachable, not a PDF).
Writes analysis/corpus/unpaywall_hosts_<date>.json and prints the top hosts, so
Jimmy can decide which domains to allow in the environment's network settings.

  uv run python analysis/corpus/unpaywall_hosts.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from urllib.parse import urlparse

import yaml

LIT = Path("data/literature")


def main() -> int:
    diseases = list(yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"])
    hosts: dict[str, Counter] = defaultdict(Counter)
    per_disease = {}
    for d in diseases:
        rows = [r for r in csv.DictReader((LIT / d / "manifest.csv").open(newline=""))
                if r["in_extraction_corpus"].lower() == "true"]
        c = Counter()
        for r in rows:
            m = LIT / d / "fulltext" / f"{r['pmid']}.meta.json"
            if not m.exists():
                continue
            meta = json.loads(m.read_text())
            if meta.get("format"):
                c["fetched_" + ("unpaywall_pdf" if str(meta.get("source", "")).startswith("unpaywall") else "pmc_xml")] += 1
                continue
            errs = [e for e in meta.get("errors", []) if e.startswith("unpaywall ")]
            if errs:
                c["unpaywall_link_failed"] += 1
                for e in errs:
                    url, _, reason = e[len("unpaywall "):].rpartition(": ")
                    hosts[urlparse(url).netloc.lower()][reason] += 1
            elif meta.get("oa_landing_url"):
                c["unpaywall_oa_landing_page_only"] += 1
            else:
                c["no_open_copy_found"] += 1
        per_disease[d] = dict(c)
    ranked = sorted(hosts.items(), key=lambda kv: -sum(kv[1].values()))
    out = {
        "date": datetime.now(UTC).date().isoformat(),
        "per_disease": per_disease,
        "failed_hosts": [{"host": h, "links": sum(c.values()), "reasons": dict(c)} for h, c in ranked],
    }
    path = Path("analysis/corpus") / f"unpaywall_hosts_{out['date']}.json"
    path.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(per_disease, indent=1))
    for h in out["failed_hosts"][:25]:
        print(h["links"], h["host"], h["reasons"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
