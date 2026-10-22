"""Bias arm (pre-registration §7.4.1): fetch the held-out comparator papers, open access only (D-32).

The comparators are natural-history or genotype-first cohort papers held out of the extraction
corpus (configs/diseases.yaml `holdouts`; HA20's candidates from §7.4.1). They are saved under
data/literature/<disease>/holdouts/ (git-ignored), never under fulltext/ or fulltext_md/, so no
extraction step can read them. JATS is converted to Markdown for the human listing (§7.4.2 step 1).

  uv run python analysis/bias/fetch_comparators.py
writes analysis/bias/comparators_<date>.json (access status per paper; no text).
"""
from __future__ import annotations

import json
import os
from datetime import date
from pathlib import Path

import yaml

from pipeline.extract.corpus.eutils import Client
from pipeline.extract.corpus.fetch_fulltext import fetch_one
from pipeline.extract.corpus.jats_to_markdown import jats_to_markdown

BACKGROUND = {  # HA20 has no holdouts block in configs/diseases.yaml (pilot disease); candidates from §7.4.1
    "ha20": {"aeschlimann2018_ha20_cohort": ("29317407", "10.1136/annrheumdis-2017-212403"),
             "he2026_ha20_multicenter": ("", "10.64898/2026.01.01.25342105")},
}


def load_env() -> None:
    p = Path(".env")
    if p.exists():
        for line in p.read_text().splitlines():
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def main() -> int:
    load_env()
    cfg = yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"]
    bg = {r.split(",")[0]: r for r in Path("background/manifest.csv").read_text().splitlines()}
    import csv
    bgrows = {r["key"]: r for r in csv.DictReader(open("background/manifest.csv"))}
    todo = []
    for d, c in cfg.items():
        for key, pmid in (c.get("holdouts") or {}).items():
            r = bgrows.get(key, {})
            todo.append((d, key, pmid, r.get("pmcid", ""), r.get("doi", "")))
    for d, items in BACKGROUND.items():
        for key, (pmid, doi) in items.items():
            todo.append((d, key, pmid, bgrows.get(key, {}).get("pmcid", ""), doi))
    client = Client()
    email = os.environ.get("UNPAYWALL_EMAIL")
    out = []
    for d, key, pmid, pmcid, doi in todo:
        folder = Path(f"data/literature/{d}/holdouts")
        folder.mkdir(parents=True, exist_ok=True)
        if not pmcid and pmid:
            try:
                rec = client.idconv([pmid])
                pmcid = next((x.get("pmcid") for x in rec if x.get("pmcid")), "") or ""
            except Exception as e:  # noqa: BLE001
                pmcid = ""
        meta = fetch_one(client, {"pmid": pmid or key, "pmcid": pmcid, "doi": doi}, folder, email)
        md = None
        nx = folder / f"{pmid or key}.nxml"
        if nx.exists():
            art = jats_to_markdown(nx.read_bytes())
            md = folder / f"{pmid or key}.md"
            md.write_text(art.to_markdown())
        out.append({"disease": d, "key": key, "pmid": pmid, "pmcid": pmcid, "doi": doi, "source": meta.get("source"),
                    "format": meta.get("format"), "license": meta.get("license"), "markdown": bool(md),
                    "errors": meta.get("errors", [])})
        print(out[-1])
    Path(f"analysis/bias/comparators_{date.today().isoformat()}.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
