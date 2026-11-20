#!/usr/bin/env python3
# Copyright 2026 Google LLC (original PaperOrchestra logic, Apache-2.0)
# Modified 2026 for the Multi-Alignment repo: the LLM calls were removed and
# replaced by Claude Code subagents (see ../README.md). This file keeps only
# the deterministic parts of the upstream pipeline:
#   - search-task collection from outline.json   (literature_review_agent.py)
#   - Semantic Scholar verification + cutoff filter (scholar_utils.py,
#     literature_review_agent.py)
#   - BibTeX / citation_map generation and citation injection into the outline
#   - LaTeX compilation and PDF page snapshots    (pdf_utils.py)
#   - review-ensemble score averaging             (autoraters/agent_review.py)
#   - accept / revert rule of the refinement loop (content_refinement_agent.py)
"""PaperOrchestra helper CLI (deterministic steps only).

Usage: python3 tools/paper-orchestra/scripts/po.py <command> [args]
Run `po.py -h` or `po.py <command> -h` for details.
"""

import argparse
import datetime
import difflib
import glob
import html
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TOOL_ROOT = os.path.dirname(HERE)

IDEA_NAMES = ["idea.md", "idea_sparse.md", "idea_dense.md"]
LOG_NAMES = ["experimental_log.md"]
IMG_EXT = (".png", ".jpg", ".jpeg", ".pdf")
SCORE_AXES = {
    "Originality": (1, 4),
    "Quality": (1, 4),
    "Clarity": (1, 4),
    "Significance": (1, 4),
    "Soundness": (1, 4),
    "Presentation": (1, 4),
    "Contribution": (1, 4),
    "Overall": (1, 10),
    "Confidence": (1, 5),
}


# --------------------------------------------------------------------------- utils
def jload(path, default=None):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        if default is not None:
            return default
        raise


def jdump(obj, path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, ensure_ascii=False)


def first_existing(d, names):
    for n in names:
        p = os.path.join(d, n)
        if os.path.exists(p):
            return p
    return None


def cfg(run):
    return jload(os.path.join(run, "config.json"))


# --------------------------------------------------------------------------- init
def cmd_init(a):
    run = a.run
    mat = os.path.abspath(a.materials)
    tpl = a.template
    if not os.path.isdir(tpl):
        cand = os.path.join(TOOL_ROOT, "templates", tpl)
        if os.path.isdir(cand):
            tpl = cand
    tpl = os.path.abspath(tpl)
    for p, what in [(mat, "materials dir"), (tpl, "template dir")]:
        if not os.path.isdir(p):
            sys.exit(f"error: {what} not found: {p}")
    if not first_existing(mat, IDEA_NAMES):
        sys.exit(f"error: no idea file ({' / '.join(IDEA_NAMES)}) in {mat}")
    if not first_existing(mat, LOG_NAMES):
        sys.exit(f"error: no experimental_log.md in {mat}")
    for n in ["template.tex", "guidelines.md"]:
        if not os.path.exists(os.path.join(tpl, n)):
            sys.exit(f"error: template dir lacks {n}: {tpl}")
    if os.path.exists(run) and os.listdir(run) and not a.force:
        sys.exit(f"error: run dir {run} exists and is not empty (use --force)")

    os.makedirs(run, exist_ok=True)
    raw = os.path.join(run, "raw_materials")
    if os.path.exists(raw):
        shutil.rmtree(raw)
    shutil.copytree(mat, raw)
    latex = os.path.join(run, "latex")
    if os.path.exists(latex):
        shutil.rmtree(latex)
    shutil.copytree(tpl, latex)
    os.makedirs(os.path.join(latex, "figures"), exist_ok=True)
    for d in ["lit/batches", "lit/candidates", "plots", "review"]:
        os.makedirs(os.path.join(run, d), exist_ok=True)

    provided = []
    fig_src = os.path.join(raw, "figures")
    if os.path.isdir(fig_src):
        caps = jload(os.path.join(fig_src, "captions.json"), {})
        for fn in sorted(os.listdir(fig_src)):
            if fn.lower().endswith(IMG_EXT):
                shutil.copy(os.path.join(fig_src, fn), os.path.join(latex, "figures", fn))
                provided.append({"name": fn, "caption": caps.get(fn, ""), "source": "provided"})

    seeded = 0
    if a.seed_run:
        # Reuse another run's verified library: entries keep their index record but lose their
        # section tags; discovery agents re-select them by exact title (no new lookup needed).
        seed = jload(os.path.join(a.seed_run, "lit", "registry.json"), {})
        for p_ in seed.values():
            p_["sections"] = []
        jdump(seed, os.path.join(run, "lit", "registry.json"))
        with open(os.path.join(run, "lit", "library_titles.md"), "w", encoding="utf-8") as f:
            f.write("# Already-verified papers (reuse by EXACT title; no search needed)\n\n")
            for p_ in sorted(seed.values(), key=lambda x: x["title"].lower()):
                f.write(f"- {p_['title']} ({p_['year']})\n")
        seeded = len(seed)

    conf = {
        "seed_run": os.path.abspath(a.seed_run) if a.seed_run else None,
        "seeded_papers": seeded,
        "created": datetime.datetime.now().isoformat(timespec="seconds"),
        "materials_dir": mat,
        "template_dir": tpl,
        "idea_file": os.path.relpath(first_existing(raw, IDEA_NAMES), run),
        "experimental_log_file": os.path.relpath(first_existing(raw, LOG_NAMES), run),
        "research_cutoff": a.cutoff or datetime.datetime.now().strftime("%Y-%m"),
        "use_plotting": a.plotting,
        "review_ensemble": a.ensemble,
        "max_reflections": a.max_reflections,
        "anonymize": not a.no_anonymize,
        "provided_figures": provided,
    }
    jdump(conf, os.path.join(run, "config.json"))
    print(json.dumps(conf, indent=2))


# --------------------------------------------------------------------------- tasks
def collect_search_tasks(outline):
    """Port of HybridLiteratureAgent._collect_search_tasks."""
    tasks = []
    plan = outline.get("intro_related_work_plan", {})
    intro = plan.get("introduction_strategy", {})
    for d in intro.get("search_directions", []):
        tasks.append({
            "section": "Introduction",
            "focus": d,
            "context": f"Hook: {intro.get('hook_hypothesis', '')}. Gap: {intro.get('problem_gap_hypothesis', '')}",
            "search_type": "exploration",
        })
    rw = plan.get("related_work_strategy", {})
    for sub in rw.get("subsections", []):
        qs = sub.get("limitation_search_queries", []) or [
            f"{sub.get('subsection_title', '')} {sub.get('methodology_cluster', '')}"
        ]
        for q in qs:
            tasks.append({
                "section": f"Related Work: {sub.get('subsection_title', 'General')}",
                "focus": q,
                "context": f"Mission: {sub.get('sota_investigation_mission', '')}. Hypothesis: {sub.get('limitation_hypothesis', '')}",
                "search_type": "exploration",
            })
    for sec in outline.get("section_plan", []):
        st = sec.get("section_title", "Unknown Section")
        for sub in sec.get("subsections", []):
            sbt = sub.get("subsection_title", "General")
            ctx = " ".join(sub.get("content_bullets", []))
            for h in sub.get("citation_hints", []):
                tasks.append({
                    "section": f"{st} - {sbt}",
                    "focus": h,
                    "context": f"Must-have citation for section covering: {ctx}",
                    "search_type": "targeted",
                })
    seen, out = set(), []
    for t in tasks:
        k = f"{t['section']}:{t['focus']}"
        if k in seen:
            continue
        seen.add(k)
        t["task_id"] = f"T{len(out) + 1:03d}"
        out.append(t)
    return out


def user_bib(run):
    p = os.path.join(run, "raw_materials", "extra_references.bib")
    return parse_bib(open(p, encoding="utf-8").read()) if os.path.exists(p) else {}


def match_user_key(focus, user):
    """Return the user-bib key a targeted hint refers to. A hint "Author (Exact Title)" must match
    the title closely; similar-looking titles of other papers must not match."""
    m = re.search(r"\((.+)\)\s*$", focus.strip())
    cand = norm_title(m.group(1) if m else focus)
    best, hi = None, 0.0
    for k, v in user.items():
        t = norm_title(v.get("title", ""))
        if not t:
            continue
        if t == cand or (len(t) > 25 and t in norm_title(focus)):
            return k
        r = difflib.SequenceMatcher(None, t, cand).ratio()
        if r > hi:
            best, hi = k, r
    return best if hi > 0.9 else None


def cmd_tasks(a):
    run = a.run
    outline = jload(os.path.join(run, "outline.json"))
    tasks = collect_search_tasks(outline)
    user = user_bib(run)
    covered = []
    if user and not a.search_user_refs:
        keep = []
        for t in tasks:
            k = match_user_key(t["focus"], user) if t["search_type"] == "targeted" else None
            if k:
                covered.append(dict(t, user_key=k))
            else:
                keep.append(t)
        tasks = keep
    jdump(covered, os.path.join(run, "lit", "tasks_covered_by_user_bib.json"))
    jdump(tasks, os.path.join(run, "lit", "search_tasks.json"))
    bdir = os.path.join(run, "lit", "batches")
    for f in glob.glob(os.path.join(bdir, "*.json")):
        os.remove(f)
    # batch by focus so identical hints (cited in several sections) are searched once
    foci = sorted({t["focus"] for t in tasks})
    n = max(1, min(a.batches, len(foci)))
    groups = [set(foci[i::n]) for i in range(n)]
    batches = [[t for t in tasks if t["focus"] in g] for g in groups]
    if covered:
        print(f"{len(covered)} targeted hints already covered by extra_references.bib (not searched)")
    for i, b in enumerate(batches, 1):
        jdump(b, os.path.join(bdir, f"batch_{i}.json"))
    n_t = sum(t["search_type"] == "targeted" for t in tasks)
    print(f"{len(tasks)} search tasks ({n_t} targeted, {len(tasks) - n_t} exploration) "
          f"-> {len(batches)} batches in {bdir}")


# --------------------------------------------------------------------------- S2
S2_URL = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "title,authors,venue,year,abstract,citationCount,journal,publicationDate,externalIds"


def s2_get(params, retries=6):
    key = os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    url = S2_URL + "?" + urllib.parse.urlencode(params)
    for i in range(retries):
        req = urllib.request.Request(url, headers={"x-api-key": key} if key else {})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return json.loads(r.read().decode())
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504):
                time.sleep(2 * (i + 1))
                continue
            return None
        except Exception:
            time.sleep(2 * (i + 1))
    return None


def ratio(a, b):
    return 100 * difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()


def date_ok(p_date, p_year, cutoff):
    """Port of s2_title_search.is_date_valid (strictly before cutoff month)."""
    if not cutoff:
        return True
    try:
        cy, cm = map(int, cutoff.split("-")[:2])
        cut = datetime.datetime(cy, cm, 1)
        if p_date:
            try:
                return datetime.datetime.strptime(p_date, "%Y-%m-%d") < cut
            except ValueError:
                pass
        if p_year:
            return p_year < cy or (p_year == cy and cm > 1)
        return True
    except Exception:
        return True


S2_STATE = {"disabled": False, "fails": 0}


def pick_best(title, year_hint, cutoff, recs):
    best, hi = None, 0
    for r in recs:
        if not r.get("title"):
            continue
        if not date_ok(r.get("publicationDate"), r.get("year"), cutoff):
            continue
        s = ratio(title, r["title"])
        if year_hint and r.get("year") == year_hint:
            s += 10
        if s > hi:
            hi, best = s, r
    return (best, hi) if hi > 70 else (None, hi)


def s2_title_search(title, year_hint, cutoff):
    """Upstream logic: top-3 S2 hits, fuzzy title ratio > 70 (+10 for year match)."""
    if S2_STATE["disabled"]:
        return None, "s2_disabled"
    data = s2_get({"query": title, "limit": 3, "fields": S2_FIELDS},
                  retries=6 if os.environ.get("SEMANTIC_SCHOLAR_API_KEY") else 2)
    if not data:
        S2_STATE["fails"] += 1
        if S2_STATE["fails"] >= 3:
            S2_STATE["disabled"] = True
            print("  ! Semantic Scholar keeps rate-limiting (no SEMANTIC_SCHOLAR_API_KEY?); "
                  "falling back to Crossref/arXiv for the rest of this run")
        return None, "s2_no_response"
    S2_STATE["fails"] = 0
    best, hi = pick_best(title, year_hint, cutoff, data.get("data", []) or [])
    return (best, f"s2_match_{hi:.0f}") if best else (None, f"s2_no_match_{hi:.0f}")


def http_json(url, timeout=25):
    req = urllib.request.Request(url, headers={"User-Agent": "paper-orchestra-local/1.0 (research tool)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def strip_tags(s):
    s = re.sub(r"<jats:title>.*?</jats:title>", "", s or "", flags=re.S)
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def crossref_to_rec(it):
    parts = ((it.get("issued") or {}).get("date-parts") or [[None]])[0]
    year = parts[0] if parts else None
    pdate = "-".join(f"{x:02d}" if i else str(x) for i, x in enumerate(parts)) if len(parts) == 3 and all(parts) else None
    venue = (it.get("container-title") or [""])[0]
    return {
        "title": re.sub(r"\s+", " ", (it.get("title") or [""])[0]).strip(),
        "authors": [{"name": f"{a.get('given', '')} {a.get('family', '')}".strip() or a.get("name", "")}
                    for a in it.get("author", []) or []],
        "venue": venue or it.get("publisher", ""),
        "year": year,
        "publicationDate": pdate,
        "abstract": strip_tags(it.get("abstract", "")),
        "citationCount": it.get("is-referenced-by-count", 0),
        "journal": {"name": venue, "volume": it.get("volume"), "pages": it.get("page")}
        if it.get("type") == "journal-article" else None,
        "externalIds": {"DOI": it.get("DOI")},
    }


CR_SEL = "title,author,issued,container-title,DOI,abstract,is-referenced-by-count,type,volume,page,publisher"


def crossref_title_search(title, year_hint, cutoff):
    try:
        q = urllib.parse.urlencode({"query.bibliographic": title, "rows": 5, "select": CR_SEL})
        items = http_json(f"https://api.crossref.org/works?{q}")["message"]["items"]
    except Exception as e:
        return None, f"crossref_error_{type(e).__name__}"
    best, hi = pick_best(title, year_hint, cutoff, [crossref_to_rec(i) for i in items])
    return (best, f"crossref_match_{hi:.0f}") if best else (None, f"crossref_no_match_{hi:.0f}")


def crossref_doi(doi, title, cutoff):
    try:
        it = http_json(f"https://api.crossref.org/works/{urllib.parse.quote(doi)}")["message"]
    except Exception as e:
        return None, f"doi_error_{type(e).__name__}"
    rec = crossref_to_rec(it)
    if title and ratio(title, rec["title"]) < 60:
        return None, f"doi_title_mismatch_{ratio(title, rec['title']):.0f}"
    if not date_ok(rec.get("publicationDate"), rec.get("year"), cutoff):
        return None, "doi_after_cutoff"
    return rec, "crossref_doi"


def arxiv_query(params):
    import xml.etree.ElementTree as ET
    ns = {"a": "http://www.w3.org/2005/Atom"}
    url = "https://export.arxiv.org/api/query?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "paper-orchestra-local/1.0"})
    root = ET.fromstring(urllib.request.urlopen(req, timeout=25).read())
    recs = []
    for e in root.findall("a:entry", ns):
        t = re.sub(r"\s+", " ", e.findtext("a:title", "", ns)).strip()
        if not t or t == "Error":
            continue
        pub = e.findtext("a:published", "", ns)[:10]
        aid = e.findtext("a:id", "", ns).rsplit("/abs/", 1)[-1]
        recs.append({
            "title": t,
            "authors": [{"name": a.findtext("a:name", "", ns)} for a in e.findall("a:author", ns)],
            "venue": "arXiv preprint arXiv:" + re.sub(r"v\d+$", "", aid),
            "year": int(pub[:4]) if pub else None,
            "publicationDate": pub or None,
            "abstract": re.sub(r"\s+", " ", e.findtext("a:summary", "", ns)).strip(),
            "citationCount": 0,
            "journal": None,
            "externalIds": {"ArXiv": re.sub(r"v\d+$", "", aid)},
        })
    return recs


def arxiv_id(aid, title, cutoff):
    try:
        recs = arxiv_query({"id_list": aid, "max_results": 1})
    except Exception as e:
        return None, f"arxiv_error_{type(e).__name__}"
    if not recs:
        return None, "arxiv_id_not_found"
    rec = recs[0]
    if title and ratio(title, rec["title"]) < 60:
        return None, f"arxiv_title_mismatch_{ratio(title, rec['title']):.0f}"
    if not date_ok(rec.get("publicationDate"), rec.get("year"), cutoff):
        return None, "arxiv_after_cutoff"
    return rec, "arxiv_id"


def arxiv_title_search(title, year_hint, cutoff):
    try:
        q = re.sub(r"[^\w\s]", " ", title)
        recs = arxiv_query({"search_query": f'ti:"{q}"', "max_results": 5})
    except Exception as e:
        return None, f"arxiv_error_{type(e).__name__}"
    best, hi = pick_best(title, year_hint, cutoff, recs)
    return (best, f"arxiv_match_{hi:.0f}") if best else (None, f"arxiv_no_match_{hi:.0f}")


def resolve(c, year_hint, cutoff):
    """Verification chain. Every accepted paper must resolve to a real index record:
    explicit DOI / arXiv id from the discovery agent first, then the upstream S2 title
    search, then Crossref and arXiv title search as keyless fallbacks."""
    title = c.get("title") or ""
    tried = []
    doi = (c.get("doi") or "").strip()
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", doi)
    if doi:
        rec, why = crossref_doi(doi, title, cutoff)
        if rec:
            return rec, why
        tried.append(why)
    aid = (c.get("arxiv_id") or "").strip()
    if aid:
        rec, why = arxiv_id(aid, title, cutoff)
        if rec:
            return rec, why
        tried.append(why)
    for fn in (s2_title_search, crossref_title_search, arxiv_title_search):
        rec, why = fn(title, year_hint, cutoff)
        if rec:
            return rec, why
        tried.append(why)
    return None, ";".join(tried)


def norm_title(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


STOP = {"the", "a", "an", "in", "on", "at", "for", "to", "of", "and", "is", "are", "with", "by", "study"}


def gen_key(authors, year, title):
    """Port of HybridLiteratureAgent._generate_key."""
    first = authors[0]["name"].split()[-1] if authors else "Unknown"
    first = re.sub(r"[^a-zA-Z]", "", first).capitalize() or "Unknown"
    words = re.sub(r"[^a-zA-Z0-9\s]", "", (title or "").lower()).split()
    mean = [w.capitalize() for w in words if w not in STOP]
    return f"{first}{year or 'nd'}{''.join(mean[:2]) or 'Paper'}"


GREEK = {"α": "alpha", "β": "beta", "γ": "gamma", "δ": "delta", "ε": "epsilon", "θ": "theta",
         "λ": "lambda", "μ": "mu", "π": "pi", "ρ": "rho", "σ": "sigma", "τ": "tau", "φ": "phi",
         "χ": "chi", "ψ": "psi", "ω": "omega", "Δ": "Delta", "Σ": "Sigma", "Ω": "Omega"}


def latex_safe(s):
    """Make index text safe for pdflatex with the default OT1 encoding: Greek -> math,
    Latin-1 accents kept (utf8 inputenc handles them), other accented letters decomposed."""
    import unicodedata
    out, in_math = [], False
    for ch in s:
        if ch == "$":
            in_math = not in_math
            out.append(ch)
        elif ch in GREEK:
            out.append(f"\\{GREEK[ch]} " if in_math else f"$\\{GREEK[ch]}$")
        elif ord(ch) < 256 or ch in "–—‘’“”…":
            out.append(ch)
        else:
            base = unicodedata.normalize("NFKD", ch).encode("ascii", "ignore").decode()
            out.append(base)
    return "".join(out)


def bib_escape(s):
    s = latex_safe(str(s or ""))
    for ch in ["&", "%", "#", "_"]:
        s = s.replace(ch, "\\" + ch)
    return s


def cmd_verify(a):
    """Semantic Scholar enrichment of discovered candidates + bib/citation_map/outline_v1."""
    run = a.run
    conf = cfg(run)
    cutoff = a.cutoff or conf.get("research_cutoff")
    tasks = {t["task_id"]: t for t in jload(os.path.join(run, "lit", "search_tasks.json"), [])}
    reg_path = os.path.join(run, "lit", "registry.json")
    rej_path = os.path.join(run, "lit", "rejected.json")
    keep = a.resume or bool(conf.get("seed_run"))
    registry = jload(reg_path, {}) if keep else {}
    rejected = jload(rej_path, []) if a.resume else []
    checked = {norm_title(r["candidate_title"]) for r in rejected} | set(registry)

    items = []
    for f in sorted(glob.glob(os.path.join(run, "lit", "candidates", "*.json"))):
        for res in jload(f, []):
            t = tasks.get(res.get("task_id"), {})
            sec = res.get("section") or t.get("section", "Unknown")
            for c in res.get("candidates", []) or []:
                items.append((c, sec, res.get("task_id")))
    print(f"{len(items)} candidates from {len(glob.glob(os.path.join(run, 'lit', 'candidates', '*.json')))} files; cutoff {cutoff}")

    for i, (c, sec, tid) in enumerate(items, 1):
        title = c.get("title") or ""
        nt = norm_title(title)
        if not nt or nt in checked:
            # still record that this section wants an already-registered paper
            if nt in registry and sec not in registry[nt]["sections"]:
                registry[nt]["sections"].append(sec)
            continue
        checked.add(nt)
        try:
            yh = int(c.get("year")) if c.get("year") else None
        except (TypeError, ValueError):
            yh = None
        time.sleep(a.sleep)
        s2, why = resolve(c, yh, cutoff)
        if not s2:
            rejected.append({"candidate_title": title, "task_id": tid, "section": sec, "reason": why})
            continue
        abstract_source = "index"
        if not (s2.get("abstract") or "").strip():
            # Upstream drops papers without an abstract. Crossref often lacks abstracts for
            # books/chapters (common in psychology), so we fall back to the discovery agent's
            # web-sourced summary, clearly labelled, unless --strict-abstract is set.
            summ = (c.get("summary") or "").strip()
            if a.strict_abstract or not summ:
                rejected.append({"candidate_title": title, "task_id": tid, "section": sec,
                                 "reason": "no_abstract", "matched_title": s2.get("title")})
                continue
            s2["abstract"] = "[Summary from web search, not the published abstract] " + summ
            abstract_source = "web_summary"
        if not s2.get("authors") and c.get("authors"):
            # some index records (old journal articles) carry no author field
            names = c["authors"] if isinstance(c["authors"], list) else re.split(r"\s*(?:;| and )\s*", str(c["authors"]))
            s2["authors"] = [{"name": n.strip()} for n in names if n.strip()]
        fnt = norm_title(s2["title"])
        if fnt in registry:
            if sec not in registry[fnt]["sections"]:
                registry[fnt]["sections"].append(sec)
            continue
        ab = (s2.get("abstract") or "").strip()
        if len(ab) > 1500:
            ab = ab[:1500] + "... [Truncated]"
        j = s2.get("journal") or {}
        registry[fnt] = {
            "citation_key": gen_key(s2.get("authors") or [], s2.get("year") or yh, s2["title"]),
            "title": re.sub(r"\s+", " ", s2["title"]).strip(),
            "authors": [x["name"] for x in s2.get("authors") or []],
            "venue": s2.get("venue") or "arXiv",
            "year": s2.get("year") or yh,
            "abstract": ab,
            "citation_count": s2.get("citationCount") or 0,
            "sections": [sec],
            "reason": c.get("reason", ""),
            "journal": j.get("name"),
            "volume": j.get("volume"),
            "pages": j.get("pages"),
            "publication_date": s2.get("publicationDate"),
            "external_ids": s2.get("externalIds") or {},
            "verified_by": why,
            "abstract_source": abstract_source,
        }
        print(f"  [{i}/{len(items)}] + {s2['title'][:90]} ({why})")
        if i % 10 == 0:
            jdump(registry, reg_path)
            jdump(rejected, rej_path)
    jdump(registry, reg_path)
    jdump(rejected, rej_path)
    build_bib(run, registry)
    print(f"verified {len(registry)} papers; rejected {len(rejected)} (see {rej_path})")


def parse_bib(text):
    """Minimal BibTeX reader for user-supplied references: key -> {title, author, year, note}."""
    out = {}
    for m in re.finditer(r"@\w+\s*\{\s*([^,\s]+)\s*,(.*?)\n\}", text, re.S):
        key, body = m.group(1), m.group(2)
        f = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{((?:[^{}]|\{[^{}]*\})*)\}", body):
            f[fm.group(1).lower()] = re.sub(r"[{}]", "", fm.group(2)).strip()
        out[key] = f
    return out


PUBLISHERS = r"\b(Springer|Wiley|Erlbaum|Routledge|Press|Elsevier Science|Academic Press)\b"
MAX_AUTHORS = 10


def bib_authors(names):
    """Clean author list: unescape, drop junk entries, brace corporate authors, cap long lists."""
    out = []
    for n in names:
        n = html.unescape(str(n)).strip().strip(":").strip()
        if not n or not re.search(r"[A-Za-z]", n):
            continue
        if n.isupper() and len(n) > 4:  # some index records give names in capitals
            n = " ".join(w if len(w.strip(".")) <= 1 else w.capitalize() for w in n.split())
        n = bib_escape(n)
        if n.endswith("Team") or (re.search(r"(AI|Inc\.|Lab)$", n) and len(n.split()) <= 2):
            n = "{" + n + "}"
        out.append(n)
    if len(out) > MAX_AUTHORS:
        out = out[:MAX_AUTHORS] + ["others"]
    return " and ".join(out) or "Unknown"


def bib_title(title):
    t = html.unescape(title)
    t = re.sub(r"χ\s*2\b", lambda m: r"$\chi^2$", t)
    t = re.sub(r'"([^"]+)"', r"``\1''", t)
    t = t.replace("“", "``").replace("”", "''")
    return bib_escape(t)


def build_bib(run, registry):
    extra = os.path.join(run, "raw_materials", "extra_references.bib")
    extra_text = open(extra, encoding="utf-8").read() if os.path.exists(extra) else ""
    user = parse_bib(extra_text)
    user_titles = {norm_title(v.get("title", "")) for v in user.values()}
    dup = [k for k, p in registry.items() if k in user_titles]
    for k in dup:  # user-supplied copy wins over the web-discovered one
        registry.pop(k)
    if dup:
        print(f"dropped {len(dup)} discovered papers already in extra_references.bib")
    papers = sorted(registry.values(), key=lambda p: p["citation_key"])
    seen, entries, cmap = set(), [], {}
    for p in papers:
        base = key = p["citation_key"]
        suf = "a"
        while key in seen:
            key = base + suf
            suf = chr(ord(suf) + 1)
        p["citation_key"] = key
        seen.add(key)
        authors = bib_authors(p["authors"])
        doi = (p.get("external_ids") or {}).get("DOI") or ""
        is_book = not p.get("journal") and ("/978-" in doi or re.search(PUBLISHERS, p.get("venue") or ""))
        is_arxiv = not p.get("journal") and str(p.get("venue") or "").lower().startswith("arxiv")
        typ = "book" if is_book else ("article" if p.get("journal") else ("misc" if is_arxiv else "inproceedings"))
        e = f"@{typ}{{{key},\n  title={{{{{bib_title(p['title'])}}}}},\n  author={{{authors}}},\n"
        if is_book:
            e += f"  publisher={{{bib_escape(html.unescape(p['venue']))}}},\n"
        elif is_arxiv:
            e += f"  howpublished={{{bib_escape(html.unescape(p['venue']))}}},\n"
        elif p.get("journal"):
            e += f"  journal={{{bib_escape(html.unescape(p['journal']))}}},\n"
        else:
            e += f"  booktitle={{{bib_escape(html.unescape(p['venue']))}}},\n"
        e += f"  year={{{p['year']}}}"
        if p.get("volume"):
            e += f",\n  volume={{{bib_escape(p['volume'])}}}"
        if p.get("pages"):
            e += f",\n  pages={{{bib_escape(p['pages'])}}}"
        if doi:
            e += f",\n  doi={{{doi}}}"
        e += "\n}"
        entries.append(e)
        cmap[key] = {k: p[k] for k in ["citation_key", "title", "authors", "venue", "year", "abstract"]}
        cmap[key]["sections"] = p["sections"]
    bib = "\n\n".join(entries)
    if extra_text:
        bib += "\n\n% ---- user-supplied references (raw_materials/extra_references.bib) ----\n" + extra_text
        for k, f in user.items():
            if k in cmap:
                print(f"  ! user key {k} collides with a discovered key; the user entry wins")
            cmap[k] = {"citation_key": k, "title": f.get("title", ""),
                       "authors": [a.strip() for a in f.get("author", "").split(" and ") if a.strip()],
                       "venue": f.get("journal") or f.get("booktitle") or f.get("howpublished", ""),
                       "year": f.get("year", ""),
                       "abstract": "[User-supplied reference; no abstract. What the paper may say about it is "
                                   "limited to what the raw materials state.] " + f.get("note", ""),
                       "sections": ["user"]}
    with open(os.path.join(run, "latex", "references.bib"), "w", encoding="utf-8") as f:
        f.write(bib + "\n")
    jdump(cmap, os.path.join(run, "lit", "citation_map.json"))
    jdump(registry, os.path.join(run, "lit", "registry.json"))

    # inject citation candidates into the outline (port of _inject_citations_into_outline)
    outline = jload(os.path.join(run, "outline.json"))
    by_sec = {}
    for p in registry.values():
        for s in p["sections"]:
            by_sec.setdefault(s, []).append(p["citation_key"])
    for t in jload(os.path.join(run, "lit", "tasks_covered_by_user_bib.json"), []):
        if t.get("user_key") in cmap:
            by_sec.setdefault(t["section"], []).append(t["user_key"])
            cmap[t["user_key"]]["sections"] = sorted(set(cmap[t["user_key"]]["sections"]) | {t["section"]})
    jdump(cmap, os.path.join(run, "lit", "citation_map.json"))
    plan = outline.get("intro_related_work_plan", {})
    plan.get("introduction_strategy", {})["citation_candidates"] = sorted(set(by_sec.get("Introduction", [])))
    for sub in plan.get("related_work_strategy", {}).get("subsections", []):
        sub["citation_candidates"] = by_sec.get(f"Related Work: {sub.get('subsection_title', 'General')}", [])
    for sec in outline.get("section_plan", []):
        for sub in sec.get("subsections", []):
            sub["citation_candidates"] = by_sec.get(
                f"{sec.get('section_title', 'Unknown Section')} - {sub.get('subsection_title', 'General')}", [])
            sub.pop("citation_hints", None)
    jdump(outline, os.path.join(run, "outline_v1.json"))
    print(f"wrote latex/references.bib ({len(entries)} entries), lit/citation_map.json, outline_v1.json")


# --------------------------------------------------------------------------- figures
def cmd_figures(a):
    run = a.run
    figdir = os.path.join(run, "latex", "figures")
    info = [f for f in cfg(run).get("provided_figures", [])]
    names = {f["name"] for f in info}
    for meta in sorted(glob.glob(os.path.join(run, "plots", "*", "result.json"))):
        m = jload(meta)
        if m.get("image") and os.path.exists(os.path.join(figdir, m["image"])) and m["image"] not in names:
            info.append({"name": m["image"], "caption": m.get("caption", ""), "source": "plotting_agent",
                         "figure_id": m.get("figure_id")})
    jdump(info, os.path.join(figdir, "info.json"))
    print(json.dumps(info, indent=2))


def cmd_render(a):
    """Run a matplotlib script in a clean process; it must save to the given output path."""
    env = dict(os.environ, MPLBACKEND="Agg", PO_OUT=os.path.abspath(a.out))
    script = os.path.abspath(a.script)
    r = subprocess.run([sys.executable, script], cwd=os.path.dirname(script),
                       env=env, capture_output=True, text=True, timeout=300)
    if r.returncode != 0 or not os.path.exists(a.out):
        print(r.stdout[-3000:], r.stderr[-3000:])
        sys.exit(f"render failed (exit {r.returncode}); output {'missing' if not os.path.exists(a.out) else 'present'}")
    print(f"rendered {a.out}")


# --------------------------------------------------------------------------- LaTeX
def cmd_compile(a):
    tex = os.path.abspath(a.tex)
    d, base = os.path.dirname(tex), os.path.splitext(os.path.basename(tex))[0]
    pdf = os.path.join(d, base + ".pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    cmd = ["latexmk", "-pdf", "-interaction=nonstopmode", "-halt-on-error", "-f", "-quiet", os.path.basename(tex)]
    try:
        subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=a.timeout)
    except subprocess.TimeoutExpired:
        print("compile timed out")
    log = ""
    if os.path.exists(os.path.join(d, base + ".log")):
        log = open(os.path.join(d, base + ".log"), encoding="latin-1").read()
    errors = re.findall(r"^! .*(?:\n.*){0,3}", log, re.M)
    undef_c = sorted(set(re.findall(r"Citation [`']([^']+)' .*undefined", log)))
    undef_r = sorted(set(re.findall(r"Reference [`']([^']+)' .*undefined", log)))
    missing = sorted(set(re.findall(r"File [`']([^']+)' not found", log)))
    overfull = len(re.findall(r"Overfull \\hbox", log))
    pages = None
    if os.path.exists(pdf):
        try:
            import pymupdf
            pages = pymupdf.open(pdf).page_count
        except Exception:
            m = re.search(r"Output written on .* \((\d+) page", log)
            pages = int(m.group(1)) if m else None
    rep = {"ok": os.path.exists(pdf), "pdf": pdf if os.path.exists(pdf) else None, "pages": pages,
           "errors": errors[:8], "undefined_citations": undef_c, "undefined_references": undef_r,
           "missing_files": missing, "overfull_hboxes": overfull}
    if a.out and rep["ok"]:
        shutil.copy(pdf, a.out)
        rep["copied_to"] = a.out
    if not a.keep_aux:
        subprocess.run(["latexmk", "-c", os.path.basename(tex)], cwd=d, capture_output=True)
    print(json.dumps(rep, indent=2))
    sys.exit(0 if rep["ok"] else 1)


def cmd_snapshot(a):
    import pymupdf
    os.makedirs(a.outdir, exist_ok=True)
    for f in glob.glob(os.path.join(a.outdir, "page_*.png")):
        os.remove(f)
    doc = pymupdf.open(a.pdf)
    out = []
    for i, page in enumerate(doc, 1):
        p = os.path.join(a.outdir, f"page_{i:02d}.png")
        page.get_pixmap(dpi=a.dpi).save(p)
        out.append(p)
    print("\n".join(out))


def cmd_pdftext(a):
    import pymupdf
    text = "".join(p.get_text() for p in pymupdf.open(a.pdf))
    if a.out:
        with open(a.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"wrote {len(text)} chars to {a.out}")
    else:
        print(text)


def cmd_check(a):
    """Static checks: unknown cite keys, missing figure files, unbalanced environments."""
    tex = open(a.tex, encoding="utf-8").read()
    body = re.sub(r"(?<!\\)%.*", "", tex)
    cmap = jload(a.map, {}) if a.map else {}
    keys = set()
    for grp in re.findall(r"\\[cC]ite[a-zA-Z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}", body):
        keys.update(k.strip() for k in grp.split(",") if k.strip())
    unknown = sorted(k for k in keys if cmap and k not in cmap)
    d = os.path.dirname(os.path.abspath(a.tex))
    figs = re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]*)\}", body)
    missing = []
    for f in figs:
        p = os.path.join(d, f)
        if not (os.path.exists(p) or any(os.path.exists(p + e) for e in IMG_EXT)):
            missing.append(f)
    envs = {}
    for kind, name in re.findall(r"\\(begin|end)\{([^}]*)\}", body):
        envs[name] = envs.get(name, 0) + (1 if kind == "begin" else -1)
    unbalanced = {k: v for k, v in envs.items() if v != 0}
    info_p = os.path.join(d, "figures", "info.json")
    unused = []
    if os.path.exists(info_p):
        unused = [f["name"] for f in jload(info_p, []) if f["name"] not in " ".join(figs)]
    rep = {"cited_keys": len(keys), "unknown_cite_keys": unknown, "missing_figures": missing,
           "unused_figures": unused, "unbalanced_environments": unbalanced,
           "uncited_in_map": len([k for k in cmap if k not in keys]) if cmap else None}
    print(json.dumps(rep, indent=2))
    sys.exit(1 if (unknown or missing or unbalanced) else 0)


# --------------------------------------------------------------------------- reviews
def cmd_merge_reviews(a):
    """Port of perform_review_agentreview's ensemble aggregation: the meta-review supplies
    the text fields; each numeric axis is the rounded mean of the valid ensemble scores."""
    reviews = [jload(p) for p in a.reviews]
    meta = jload(a.meta) if a.meta and os.path.exists(a.meta) else None
    out = dict(meta or reviews[0])
    if not meta:
        # No meta-review: keep every reviewer's points (exact duplicates removed), labelled.
        for fld in ["Strengths", "Weaknesses", "Questions", "Limitations"]:
            merged, seen = [], set()
            for i, r in enumerate(reviews, 1):
                items = r.get(fld) or []
                if isinstance(items, str):
                    items = [items]
                for it in items:
                    key = re.sub(r"\W+", " ", str(it).lower()).strip()
                    if key and key not in seen:
                        seen.add(key)
                        merged.append(f"[Reviewer {i}] {it}")
            out[fld] = merged
        out["Summary"] = " ".join(f"[Reviewer {i}] {r.get('Summary', '')}" for i, r in enumerate(reviews, 1))
        decisions = [r.get("Decision") for r in reviews]
        out["Decision"] = max(set(decisions), key=decisions.count)
        out.pop("Thought", None)
        out["_meta_review"] = "none (mechanical merge of the ensemble)"
    for axis, (lo, hi) in SCORE_AXES.items():
        vals = []
        for r in reviews:
            try:
                v = int(round(float(r.get(axis))))
                if lo <= v <= hi:
                    vals.append(v)
            except (TypeError, ValueError):
                pass
        if vals:
            out[axis] = int(round(sum(vals) / len(vals)))
    out["_ensemble_sources"] = a.reviews
    jdump(out, a.out)
    print(json.dumps({k: out.get(k) for k in SCORE_AXES}, indent=2))


def scores(r):
    s = {}
    for k in SCORE_AXES:
        try:
            s[k] = float(r.get(k, 0))
        except (TypeError, ValueError):
            s[k] = 0.0
    return s


def cmd_decide(a):
    """Port of ContentRefinementAgent's accept/revert rule."""
    old, new = scores(jload(a.old)), scores(jload(a.new))
    axes = [k for k in SCORE_AXES if k not in ("Overall", "Confidence")]
    deltas = {k: new[k] - old[k] for k in axes}
    gain = sum(v for v in deltas.values() if v > 0)
    drop = -sum(v for v in deltas.values() if v < 0)
    if new["Overall"] > old["Overall"]:
        outcome, accept, cont = "ACCEPTED_SCORE_INCREASE", True, True
    elif new["Overall"] < old["Overall"]:
        outcome, accept, cont = "REJECTED_SCORE_DECREASE", False, False
    elif drop > gain:
        outcome, accept, cont = "REJECTED_DEGRADATION", False, False
    else:
        outcome, accept, cont = "ACCEPTED_NEUTRAL_IMPROVEMENT", True, True
    entry = {"round": a.round, "scores_before": old, "scores_after": new, "deltas": deltas,
             "total_gain": gain, "total_drop": drop, "outcome": outcome,
             "accept": accept, "continue": cont}
    if a.agent_plan and os.path.exists(a.agent_plan):
        entry["agent_plan"] = jload(a.agent_plan, {})
    if a.worklog:
        wl = jload(a.worklog, {})
        wl[f"v{a.round}"] = entry
        jdump(wl, a.worklog)
    print(json.dumps(entry, indent=2))


# --------------------------------------------------------------------------- status
def cmd_status(a):
    run = a.run
    ex = lambda *p: os.path.exists(os.path.join(run, *p))
    c = cfg(run)
    steps = [
        ("1 outline", ex("outline.json")),
        ("2a search tasks", ex("lit", "search_tasks.json")),
        ("2b candidates", bool(glob.glob(os.path.join(run, "lit", "candidates", "*.json")))),
        ("2c verified + bib", ex("outline_v1.json") and ex("lit", "citation_map.json")),
        ("2d intro+related work", ex("latex", "template_lit.tex")),
        ("2e figures", ex("latex", "figures", "info.json") or not c.get("use_plotting")),
        ("3 draft", ex("latex", "draft_v0.tex")),
        ("4 review v0", ex("review", "review_v0.json")),
    ]
    for i in range(1, c.get("max_reflections", 3) + 1):
        steps.append((f"4 refine v{i}", ex("latex", f"refined_v{i}.tex")))
    steps += [("5 format", ex("review", "format_review.json")), ("final", ex("final_paper.pdf"))]
    for name, done in steps:
        print(f"[{'x' if done else ' '}] {name}")


# --------------------------------------------------------------------------- main
def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = p.add_subparsers(dest="cmd", required=True)

    s = sp.add_parser("init", help="create a run directory from raw materials + LaTeX template")
    s.add_argument("--materials", required=True, help="dir with idea.md and experimental_log.md [figures/]")
    s.add_argument("--template", required=True, help="template dir or name under templates/ (iclr2025, cvpr2025)")
    s.add_argument("--run", required=True, help="output run directory")
    s.add_argument("--cutoff", help="literature cutoff YYYY-MM (default: current month)")
    s.add_argument("--plotting", action="store_true", help="generate figures with the plotting agent")
    s.add_argument("--ensemble", type=int, default=3, help="reviewers per review round (upstream: 3)")
    s.add_argument("--max-reflections", type=int, default=3, help="content refinement rounds (upstream: 3)")
    s.add_argument("--no-anonymize", action="store_true", help="do not force double-blind anonymity")
    s.add_argument("--seed-run", help="another run dir whose verified citation library is reused")
    s.add_argument("--force", action="store_true")
    s.set_defaults(f=cmd_init)

    s = sp.add_parser("tasks", help="collect literature search tasks from outline.json")
    s.add_argument("run")
    s.add_argument("--batches", type=int, default=4)
    s.add_argument("--search-user-refs", action="store_true",
                   help="also search targeted hints already covered by raw_materials/extra_references.bib")
    s.set_defaults(f=cmd_tasks)

    s = sp.add_parser("verify", help="verify candidates on Semantic Scholar; build bib + citation_map + outline_v1")
    s.add_argument("run")
    s.add_argument("--cutoff")
    s.add_argument("--sleep", type=float, default=1.1, help="seconds between S2 calls")
    s.add_argument("--resume", action="store_true", help="keep existing registry/rejections")
    s.add_argument("--strict-abstract", action="store_true",
                   help="upstream behaviour: drop papers whose index record has no abstract")
    s.set_defaults(f=cmd_verify)

    s = sp.add_parser("figures", help="collect figure files + captions into latex/figures/info.json")
    s.add_argument("run")
    s.set_defaults(f=cmd_figures)

    s = sp.add_parser("render", help="run a matplotlib script (it reads output path from $PO_OUT)")
    s.add_argument("script")
    s.add_argument("out")
    s.set_defaults(f=cmd_render)

    s = sp.add_parser("compile", help="compile a .tex with latexmk and report problems")
    s.add_argument("tex")
    s.add_argument("--out", help="copy the resulting PDF here")
    s.add_argument("--timeout", type=int, default=240)
    s.add_argument("--keep-aux", action="store_true")
    s.set_defaults(f=cmd_compile)

    s = sp.add_parser("snapshot", help="render PDF pages to PNGs")
    s.add_argument("pdf")
    s.add_argument("outdir")
    s.add_argument("--dpi", type=int, default=100)
    s.set_defaults(f=cmd_snapshot)

    s = sp.add_parser("pdftext", help="extract PDF text")
    s.add_argument("pdf")
    s.add_argument("--out")
    s.set_defaults(f=cmd_pdftext)

    s = sp.add_parser("check", help="static LaTeX checks against the citation map")
    s.add_argument("tex")
    s.add_argument("--map", help="lit/citation_map.json")
    s.set_defaults(f=cmd_check)

    s = sp.add_parser("merge-reviews", help="aggregate an ensemble of reviews")
    s.add_argument("--reviews", nargs="+", required=True)
    s.add_argument("--meta")
    s.add_argument("--out", required=True)
    s.set_defaults(f=cmd_merge_reviews)

    s = sp.add_parser("decide", help="accept/revert rule for a refinement round")
    s.add_argument("--old", required=True)
    s.add_argument("--new", required=True)
    s.add_argument("--round", type=int, required=True)
    s.add_argument("--agent-plan", help="refiner worklog JSON for this round")
    s.add_argument("--worklog", help="append entry to this JSON file")
    s.set_defaults(f=cmd_decide)

    s = sp.add_parser("status", help="show which pipeline steps are done")
    s.add_argument("run")
    s.set_defaults(f=cmd_status)

    a = p.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
