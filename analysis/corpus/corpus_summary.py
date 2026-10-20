"""Corpus search, screening and full-text coverage per disease, from the committed files.

For each disease in configs/diseases.yaml (and HA20 for the comparison table):
reads manifest.csv, corpus_stats.json, seeds/, screening/screening_log.json and
oa_elsewhere.json, and writes

  data/literature/<disease>/search.md   (five new diseases only; HA20 keeps its
                                         hand-written pilot log)
  analysis/corpus/coverage_<date>.json  (one row per disease)
  analysis/corpus/coverage_<date>.md    (the same as a table)

"In corpus" is title/abstract screening only (relevance yes or unclear, study type
case report, case series/cohort or review). Full-text screening has not been done,
so the eligible set, and the D-08 denominators, will shrink.

D-08 (decided 2026-10-20): a disease is replaced only if fewer than 15 eligible
primary reports have accessible full text after full-text screening. Until full-text
screening is done, the check here uses relevance-"yes" case reports and series with
fetched full text as a stand-in, labelled as provisional.

  uv run python analysis/corpus/corpus_summary.py
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import yaml

LIT = Path("data/literature")
OUT = Path("analysis/corpus")
D08_MIN_N = 15


def pct(n: int, d: int) -> str:
    return f"{100 * n / d:.1f}%" if d else "n/a"


def summarise(disease: str) -> dict:
    base = LIT / disease
    rows = list(csv.DictReader((base / "manifest.csv").open(newline="")))
    corpus = [r for r in rows if r["in_extraction_corpus"].lower() == "true"]
    text = [r for r in corpus if r.get("fulltext_format")]
    yes = [r for r in corpus if r["relevance"] == "yes"]
    yes_primary = [r for r in yes if r["study_type"] in ("case report", "case series/cohort")]
    stats = json.loads((base / "corpus_stats.json").read_text())
    run = stats["build_manifest_runs"][-1]
    oa = json.loads((base / "oa_elsewhere.json").read_text()) if (base / "oa_elsewhere.json").exists() else None
    free = {r["pmid"] for r in csv.DictReader((base / "oa_elsewhere.csv").open())
            if r["best"] in ("OA", "F")} if (base / "oa_elsewhere.csv").exists() else set()
    seeds = {}
    for f in sorted((base / "seeds").glob("*.csv")):
        seeds[f.name] = sum(1 for _ in csv.DictReader(f.open()))
    held = [r["pmid"] for r in rows if "held out:" in r.get("notes", "")]
    n_text, n_free = len(text), len(free)
    yp_text = sum(1 for r in yes_primary if r.get("fulltext_format"))
    yp_free = sum(1 for r in yes_primary if r["pmid"] in free)
    return {
        "disease": disease,
        "search_date": run["date"],
        "query": run["query"],
        "mindate": run.get("mindate"),
        "query_hits": run["query_hits"],
        "seed_files": seeds,
        "manifest_rows": len(rows),
        "relevance": dict(Counter(r["relevance"] for r in rows)),
        "study_type": dict(Counter(r["study_type"] for r in rows)),
        "in_corpus": len(corpus),
        "in_corpus_by_relevance": dict(Counter(r["relevance"] for r in corpus)),
        "in_corpus_by_study_type": dict(Counter(r["study_type"] for r in corpus)),
        "held_out": held,
        "seeded_from_clinvar": sum("clinvar" in r.get("seed_sources", "") for r in rows),
        "fulltext": n_text,
        "fulltext_share": round(n_text / len(corpus), 4) if corpus else None,
        "access_status_in_corpus": dict(Counter(r.get("access_status") or "not attempted" for r in corpus)),
        "free_elsewhere_listed": n_free if oa else None,
        "fulltext_or_free_share": round((n_text + n_free) / len(corpus), 4) if (corpus and oa) else None,
        "yes_primary": len(yes_primary),
        "yes_primary_fulltext": yp_text,
        "yes_primary_fulltext_or_free": yp_text + yp_free if oa else None,
        "d08_met_provisional": yp_text >= D08_MIN_N,
        "fulltext_screen": dict(Counter(r.get("fulltext_screen") or "pending" for r in corpus)),
        "fulltext_exclusion_reasons": dict(Counter(r.get("fulltext_screen_reason") for r in corpus if r.get("fulltext_screen") == "exclude")),
        "eligible_primary": sum(1 for r in corpus if r.get("fulltext_screen") == "include"
                                and r.get("fulltext_study_type") in ("case report", "case series/cohort")),
        "eligible_literature_table": sum(1 for r in corpus if r.get("fulltext_screen") == "include"
                                         and r.get("fulltext_literature_table") == "yes"),
        "eligible_all": sum(1 for r in corpus if r.get("fulltext_screen") == "include"),
    }


def search_md(s: dict, cfg: dict) -> str:
    seeds = "\n".join(f"| `seeds/{k}` | {v} |" for k, v in s["seed_files"].items())
    held = cfg.get("holdouts") or {}
    held_lines = "\n".join(f"- `{k}` (PMID {p}): {'marked out of the corpus' if p in s['held_out'] else 'not found by the search'}"
                           for k, p in held.items()) or "- none configured (pre-registration §7.4.1: no comparator identified yet)"
    acc = ", ".join(f"{k} {v}" for k, v in sorted(s["access_status_in_corpus"].items(), key=lambda kv: -kv[1]))
    free = ("not checked" if s["free_elsewhere_listed"] is None else
            f"{s['free_elsewhere_listed']} more list a free or open copy outside PMC in Europe PMC (`oa_elsewhere.json`); "
            f"with them, at most {s['fulltext'] + s['free_elsewhere_listed']} of {s['in_corpus']} ({pct(s['fulltext'] + s['free_elsewhere_listed'], s['in_corpus'])}). Not fetched")
    return f"""# {cfg['name']} (*{cfg['gene']}*) corpus search log

*Generated by `analysis/corpus/corpus_summary.py` from this folder's files on {datetime.now(UTC).date().isoformat()}. Re-running the scripts reproduces the numbers, subject to database changes since the search date.*

## PubMed query

```
{s['query']}
```

- **Run:** {s['search_date']}, by `pipeline/extract/corpus/build_manifest.py` with the disease's query and filter in `configs/diseases.yaml`.
- **Dates:** {'from ' + s['mindate'] if s['mindate'] else 'database inception to the search date'} (pre-registration §5.1).
- **Hits:** {s['query_hits']}.

## Seeds

| File | Rows |
|---|---|
{seeds}

- `background_bibliography.csv`: this disease's entries in `background/manifest.csv`, minus comparator holdouts (`disease_seeds.py background`).
- `refs_*.csv`: reference lists of the key reviews from the Europe PMC references API (`seeds_from_references.py`). These lists can be partial.
- **Not used:** ClinVar or OMIM citation lists (pre-registration §5.1). Papers seeded from ClinVar: {s['seeded_from_clinvar']}. The Europe PMC full-text search and LitVar were not run.

**Manifest:** {s['manifest_rows']} records.

## Screening (title and abstract)

- **Route:** Claude Code helper agents (Sonnet), batches of up to 100 records, each with its own scratch directory, following `pipeline/extract/claude_code/prompts/screen_v2.md` with this disease's block from `configs/diseases.yaml`. Prompt hash in `screening/screening_log.json`.
- **Relevance:** {', '.join(f'{k} {v}' for k, v in sorted(s['relevance'].items()))}.
- **In the extraction corpus:** {s['in_corpus']} (relevance yes or unclear; case report, case series/cohort or review).
  - by relevance: {', '.join(f'{k} {v}' for k, v in sorted(s['in_corpus_by_relevance'].items()))};
  - by study type: {', '.join(f'{k} {v}' for k, v in sorted(s['in_corpus_by_study_type'].items()))}.
- **Human check:** not yet done. `screening/study_type_spotcheck.csv` holds 20 rows (seed 20261018) for it; pre-registration §5.1 asks for a random 10% of inclusions.
- **Full-text screening:** not yet done. It will remove some papers, especially "unclear" ones.

## Comparator holdouts (bias arm, pre-registration §7.4.1)

{held_lines}

## Full text

- **Fetched:** {s['fulltext']} of {s['in_corpus']} corpus papers ({pct(s["fulltext"], s["in_corpus"])}): JATS XML from Europe PMC or PMC, or an open PDF found through Unpaywall (`fetch_fulltext.py`). Access status in the corpus: {acc}.
- **Unpaywall** open PDFs were fetched on 2026-10-20 (D-32: open access only). Of the papers still without full text, {free}.
- **Relevance yes, primary papers** (case reports and series): {s['yes_primary']}; with full text {s['yes_primary_fulltext']} ({pct(s['yes_primary_fulltext'], s['yes_primary'])}).
- **Full-text screening** (`screen_fulltext_v1.md`; `screening_fulltext/screening_log.json`): {', '.join(f'{k} {v}' for k, v in sorted(s['fulltext_screen'].items()))}. Exclusion reasons: {', '.join(f'{k} {v}' for k, v in sorted(s['fulltext_exclusion_reasons'].items())) or 'none'}.
- **Eligible with full text:** {s['eligible_all']} papers, of which {s['eligible_primary']} primary reports (case reports and series) and {s['eligible_literature_table']} with a per-patient literature table (D-33).
- **D-08 (decided: at least {D08_MIN_N} eligible primary reports with accessible full text):** {('met' if s['eligible_primary'] >= D08_MIN_N else 'not met') if not s['fulltext_screen'].get('pending') else 'pending (' + str(s['fulltext_screen'].get('pending')) + ' papers not yet screened)'} ({s['eligible_primary']} eligible primary reports).
"""


def main() -> int:
    cfg = yaml.safe_load(Path("configs/diseases.yaml").read_text())["diseases"]
    OUT.mkdir(parents=True, exist_ok=True)
    out = []
    for d in ["ha20", *cfg]:
        s = summarise(d)
        out.append(s)
        if d in cfg:
            (LIT / d / "search.md").write_text(search_md(s, cfg[d]))
    today = datetime.now(UTC).date().isoformat()
    (OUT / f"coverage_{today}.json").write_text(json.dumps(out, indent=2) + "\n")
    lines = [
        f"# Corpus and full-text coverage by disease ({today})",
        "",
        ("*Generated by `analysis/corpus/corpus_summary.py`. \"In corpus\" is after title/abstract screening only. "
         "\"Free elsewhere\" is a Europe PMC listing of a free or open copy outside PMC, not fetched. HA20's corpus was "
         "seeded partly from ClinVar citations (D-19); the other five were not.*"),
        "",
        "| Disease | Search hits | Records | In corpus | Full text | + free elsewhere (upper bound) | Eligible after full-text screening (primary) | D-08 (≥ 15 primary) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for s in out:
        fe = "n/a" if s["free_elsewhere_listed"] is None else f"{s['fulltext'] + s['free_elsewhere_listed']} ({pct(s['fulltext'] + s['free_elsewhere_listed'], s['in_corpus'])})"
        lines.append(f"| {s['disease']} | {s['query_hits']} | {s['manifest_rows']} | {s['in_corpus']} | {s['fulltext']} ({pct(s['fulltext'], s['in_corpus'])}) | {fe} | "
                     + (f"{s['eligible_all']} ({s['eligible_primary']})" if s['eligible_all'] else "not screened") + " | "
                     + ("pending" if s['fulltext_screen'].get('pending') or not s['eligible_all'] else ('met' if s['eligible_primary'] >= D08_MIN_N else 'not met')) + " |")
    (OUT / f"coverage_{today}.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
