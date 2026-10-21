"""WS5 memorization probe, Claude side (pre-registration §7.4.3; D-41): sample and probe batches.

Per disease, papers of the pv1 extraction corpus are split by first publication date
relative to the helper model's training cutoff. Claude Opus 5.5: training data cutoff and
reliable knowledge cutoff both "Jun 2026" (platform.claude.com models overview, read
2026-10-21), so "after" means first published 2026-07-01 or later.
Dates: the earliest pub-date with a month in the paper's JATS XML; else the manifest year,
and a 2026 paper without a month is "ambiguous" and left out.

Strata and sample (seeded): every "after" paper; up to 12 "recent" papers (2024-07-01 to
2026-06-30); "older" papers to fill the disease to 30. Two probes, black-box only, so the
open-weight model can run the identical files later:
  (a) closed_book   PMID, title and year only; the model lists the variants and key
                    phenotypes the paper reports, or says it does not know.
  (b) completion    title and the first 50 words of a passage from the paper body (the
                    first paragraph of >= 80 words in a case, patient, clinical or results
                    section; else the first such paragraph after the abstract); the model
                    continues it. The true next 50 words are kept for scoring, never shown.

  python3 -I analysis/bias/memorization/make_probes.py --seed 20261021
writes analysis/bias/memorization/sample.csv, batches/<disease>_<probe>.json and
targets/<disease>_completion.json (the hidden continuations).
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import os
import random
import re
from pathlib import Path

DISEASES = ["ha20", "ssadh", "tangier", "lad1", "axd", "danon"]
CUTOFF = (2026, 7)          # first month after the documented cutoff (Jun 2026)
RECENT_FROM = (2024, 7)
ROOT = Path("analysis/bias/memorization")
SECTION_PREF = re.compile(r"case|patient|clinical|result|report|proband|famil", re.I)
SKIP_SECTION = re.compile(r"abstract|reference|table|figure|supplement|acknowledg|funding|conflict|author|method|material|data avail|ethic|approval|consent|enrol|statistic|study design", re.I)
WORDS_PROMPT, WORDS_TARGET, MIN_WORDS = 50, 50, 80


def pub_date(d: str, pmid: str, man: dict) -> tuple[int, int | None]:
    f = Path(f"data/literature/{d}/fulltext/{pmid}.nxml")
    if f.exists():
        x = f.read_text(errors="replace")
        ds = []
        for m in re.finditer(r"<pub-date[^>]*>(.*?)</pub-date>", x, re.S):
            y = re.search(r"<year>(\d{4})", m.group(1))
            mo = re.search(r"<month>(\d+)", m.group(1))
            if y:
                ds.append((int(y.group(1)), int(mo.group(1)) if mo else None))
        full = [t for t in ds if t[1]]
        if full:
            return min(full)
        if ds:
            return (min(ds)[0], None)
    return (int(man.get(pmid, {}).get("year") or 0), None)


def stratum(date: tuple[int, int | None]) -> str:
    y, mo = date
    if y == CUTOFF[0] and mo is None:
        return "ambiguous"
    ym = (y, mo or 1)
    if ym >= CUTOFF:
        return "after"
    return "recent" if ym >= RECENT_FROM else "older"


def clean(s: str) -> str:
    s = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", s)     # links
    s = re.sub(r"[*_`]", "", s)
    s = re.sub(r"\[\d+(?:[,–-]\s*\d+)*\]", "", s)     # [12], [3-5]
    return re.sub(r"\s+", " ", s).strip()


def passage(md: str) -> tuple[str, str, str] | None:
    """(section heading, prompt words, target words) or None."""
    section, cands = "", []
    for block in re.split(r"\n\s*\n", md):
        b = block.strip()
        if b.startswith("#"):
            section = b.lstrip("#").strip()
            continue
        if not b or b.startswith("|") or b.startswith("<") or SKIP_SECTION.search(section):
            continue
        w = clean(b).split()
        if len(w) >= MIN_WORDS and section:
            cands.append((section, w))
    if not cands:
        return None
    pref = [c for c in cands if SECTION_PREF.search(c[0])]
    sec, w = (pref or cands)[0]
    if len(w) < WORDS_PROMPT + 20:
        return None
    return sec, " ".join(w[:WORDS_PROMPT]), " ".join(w[WORDS_PROMPT:WORDS_PROMPT + WORDS_TARGET])


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--per-disease", type=int, default=30)
    ap.add_argument("--recent", type=int, default=12)
    a = ap.parse_args(argv)
    (ROOT / "batches").mkdir(parents=True, exist_ok=True)
    (ROOT / "targets").mkdir(parents=True, exist_ok=True)
    rows = []
    for d in DISEASES:
        rng = random.Random(f"{a.seed}-{d}")
        man = {r["pmid"]: r for r in csv.DictReader(open(f"data/literature/{d}/manifest.csv"))}
        papers = sorted(os.path.basename(p)[:-5] for p in glob.glob(f"data/extracted/{d}/pv1-{d}/per_paper/*.json"))
        by = {"after": [], "recent": [], "older": [], "ambiguous": []}
        dates = {}
        for p in papers:
            dates[p] = pub_date(d, p, man)
            by[stratum(dates[p])].append(p)
        pick = list(by["after"])
        rec = sorted(by["recent"]); rng.shuffle(rec)
        pick += rec[:a.recent]
        old = sorted(by["older"]); rng.shuffle(old)
        pick += old[:max(0, a.per_disease - len(pick))]
        closed, comp, targets = [], [], {}
        for p in pick:
            m = man.get(p, {})
            s = stratum(dates[p])
            item = {"id": f"{d}-{p}", "pmid": p, "title": m.get("title", ""), "year": m.get("year", "")}
            closed.append(item)
            md_path = Path(f"data/literature/{d}/fulltext_md/{p}.md")
            pas = passage(md_path.read_text()) if md_path.exists() else None
            if pas:
                comp.append({**item, "section": pas[0], "opening": pas[1]})
                targets[item["id"]] = pas[2]
            rows.append({"disease": d, "pmid": p, "stratum": s, "year": dates[p][0], "month": dates[p][1] or "",
                         "first_author": m.get("first_author", ""), "has_passage": bool(pas)})
        for probe, items in (("closed_book", closed), ("completion", comp)):
            (ROOT / "batches" / f"{d}_{probe}.json").write_text(json.dumps(
                {"batch": f"{d}_{probe}", "probe": probe, "prompt_file": f"analysis/bias/memorization/prompts/{probe}_v1.md",
                 "items": items}, indent=1, ensure_ascii=False) + "\n")
        (ROOT / "targets" / f"{d}_completion.json").write_text(json.dumps(targets, indent=1, ensure_ascii=False) + "\n")
        print(d, {k: len(v) for k, v in by.items()}, "sampled", len(pick), "with passage", len(comp))
    with (ROOT / "sample.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    (ROOT / "sample_meta.json").write_text(json.dumps({
        "seed": a.seed, "cutoff": "Jun 2026 (Claude Opus 5.5; training data and reliable knowledge cutoff; "
        "platform.claude.com/docs/en/about-claude/models/overview, read 2026-10-21)",
        "after_from": "2026-07", "recent_from": "2024-07", "per_disease": a.per_disease, "recent_max": a.recent}, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
