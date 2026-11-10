"""Build the collaborator dashboard (a static site for GitHub Pages) into site/.

Everything on the page is read from analysis/dashboard/deck_data.json (written by export_deck_data.py from
the same result files as the interim papers), the candidate table, the budget lines and site_config.json.
Documents are copied or rendered from reports/. Nothing here calls a model or the network.

  uv run python -m analysis.dashboard.build_site
Then commit site/ and, on main, the Pages workflow deploys it.
"""
from __future__ import annotations

import csv
import html
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
SITE = ROOT / "site"
DATA = json.loads((HERE / "deck_data.json").read_text())
CFG = json.loads((HERE / "site_config.json").read_text())
S = DATA["stats"]
PAPER_CSS = ROOT / "analysis/interim_paper/paper.css"


def N(x):
    return f"{int(x):,}"


def esc(x):
    return html.escape(str(x), quote=True)


def run(cmd):
    subprocess.run(cmd, check=True)


def pandoc_html(src: Path, out: Path, title: str, resource_path: Path):
    run(["pandoc", str(src), "--from", "gfm+pipe_tables", "--to", "html5", "--standalone", "--embed-resources", "--metadata", f"pagetitle={title}",
         "--css", str(PAPER_CSS), "--resource-path", str(resource_path), "-o", str(out)])


def video_minutes(name="gp_rarelink_overview") -> int:
    f = ROOT / f"reports/video/{name}.mp4"
    if not f.exists():
        return 0
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(f)], capture_output=True, text=True).stdout.strip()
    return max(1, round(float(out) / 60)) if out else 0


DEEP = json.loads((HERE / "deep_dive_data.json").read_text()) if (HERE / "deep_dive_data.json").exists() else None


def size_mb(p: Path) -> str:
    b = p.stat().st_size
    return f"{b / 1e6:.1f} MB" if b >= 1e6 else f"{b / 1e3:.0f} KB"


# ------------------------------------------------------------------------------------------------ documents
def build_documents():
    paper = SITE / "paper"
    deck = SITE / "deck"
    video = SITE / "video"
    for d in (paper, deck / "slides", video, SITE / "data", SITE / "figures", SITE / "assets"):
        d.mkdir(parents=True, exist_ok=True)
    v3, v2 = ROOT / "reports/interim_paper_v3", ROOT / "reports/interim_paper"
    shutil.copy(v3 / "interim_paper_v3.pdf", paper / "interim_paper_v3.pdf")
    shutil.copy(v2 / "interim_paper.pdf", paper / "interim_paper_v2.pdf")
    pandoc_html(v3 / "interim_paper_v3.md", paper / "interim_paper_v3.html", "GP-RareLink in brief (interim, version 3)", v3)
    pandoc_html(v2 / "interim_paper.md", paper / "interim_paper_v2.html", "GP-RareLink interim report (version 2)", v2)
    pandoc_html(v2 / "supplement.md", paper / "supplement_v2.html", "GP-RareLink interim report: supplement", v2)
    pandoc_html(ROOT / "preregistration/analysis_plan.md", paper / "analysis_plan.html", "GP-RareLink pre-registered analysis plan (v1.0, frozen 2026-10-20)", ROOT / "preregistration")
    for f in (ROOT / "reports/interim_paper_v3/figures").glob("*.png"):
        shutil.copy(f, SITE / "figures" / f.name)
    shutil.copy(ROOT / "reports/deck/gp_rarelink_overview.pptx", deck / "gp_rarelink_overview.pptx")
    shutil.copy(ROOT / "reports/deck/gp_rarelink_overview.pdf", deck / "gp_rarelink_overview.pdf")
    for old in (deck / "slides").glob("*.png"):
        old.unlink()
    run(["pdftoppm", "-png", "-scale-to-x", "1280", "-scale-to-y", "720", str(ROOT / "reports/deck/gp_rarelink_overview.pdf"), str(deck / "slides" / "slide")])
    for f in ("gp_rarelink_overview.mp4", "gp_rarelink_overview.srt"):
        shutil.copy(ROOT / "reports/video" / f, video / f)
    pandoc_html(ROOT / "reports/video/gp_rarelink_overview_narration_script.md", video / "narration_script.html", "GP-RareLink overview video: narration script", ROOT / "reports/video")
    if (ROOT / "reports/video/gp_rarelink_deep_dive.mp4").exists():
        for f in ("gp_rarelink_deep_dive.mp4", "gp_rarelink_deep_dive.srt"):
            shutil.copy(ROOT / "reports/video" / f, video / f)
        pandoc_html(ROOT / "reports/video/gp_rarelink_deep_dive_narration_script.md", video / "deep_dive_script.html", "GP-RareLink deep dive: narration script", ROOT / "reports/video")
    if (ROOT / "reports/deck/gp_rarelink_deep_dive.pdf").exists():
        shutil.copy(ROOT / "reports/deck/gp_rarelink_deep_dive.pptx", deck / "gp_rarelink_deep_dive.pptx")
        shutil.copy(ROOT / "reports/deck/gp_rarelink_deep_dive.pdf", deck / "gp_rarelink_deep_dive.pdf")
        (deck / "deep_dive_slides").mkdir(exist_ok=True)
        for old in (deck / "deep_dive_slides").glob("*.png"):
            old.unlink()
        run(["pdftoppm", "-png", "-scale-to-x", "1280", "-scale-to-y", "720", str(ROOT / "reports/deck/gp_rarelink_deep_dive.pdf"), str(deck / "deep_dive_slides" / "slide")])
    (SITE / ".nojekyll").write_text("")


# ------------------------------------------------------------------------------------------------ data
def candidates():
    rows = []
    with (ROOT / "adjudication/o3_gaps/candidates.csv").open(newline="") as fh:
        for r in csv.DictReader(fh):
            if r["status"] == "withdrawn":
                continue
            rows.append({
                "id": r["candidate_id"], "disease": r["disease"], "gene": r["gene"], "hgvs_c": r["hgvs_c"],
                "protein": (r["hgvs_p_predicted"] or "").split(":")[-1], "vcf": r["vcf_grch38"],
                "written": "; ".join(dict.fromkeys(x.strip() for x in re.split(r"\s*\|+\s*|; ", r["original_strings"]) if x.strip())),
                "pmids": r["pmids"].split(), "n_papers": int(r["n_papers"]), "n_identities": int(r["n_identities"]),
                "author_class": r["author_class"] or "not stated", "omim": r["omim_checked"], "protein_check": r["protein_check"],
            })
    (SITE / "data/candidates.json").write_text(json.dumps(rows, indent=0))
    with (SITE / "data/candidates.csv").open("w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["candidate_id", "disease", "gene", "hgvs_c", "predicted_protein", "vcf_grch38", "as_written_in_papers", "pmids", "n_papers", "n_identities", "authors_classification", "omim_check", "protein_check"])
        for r in rows:
            w.writerow([r["id"], r["disease"], r["gene"], r["hgvs_c"], r["protein"], r["vcf"], r["written"], " ".join(r["pmids"]), r["n_papers"], r["n_identities"], r["author_class"], r["omim"], r["protein_check"]])
    return rows


def write_summary():
    (SITE / "data/summary.json").write_text(json.dumps({"date": DATA["date"], "commit": DATA["commit"], "stats": S, "diseases": DATA["diseases"]}, indent=1))
    (SITE / "data/spend.json").write_text(json.dumps({"reading_date": S["spend_date"], "total": S["spend_total"], "lines": S["spend_lines"], "unassigned": S["spend_unassigned"],
                                                      "exploratory_pilot_separate_session": S["ablation"], "open_weight_outside_award": S["ow_key_spend"]}, indent=1))


# ------------------------------------------------------------------------------------------------ page pieces
DISEASE_NAME = {d["key"]: d["name"] for d in DATA["diseases"]}
DISEASE_SHORT = {d["key"]: d["short"] for d in DATA["diseases"]}


def tiles():
    items = [
        (N(S["papers"]), "open-access papers read, six diseases", ""),
        (N(S["records"]), "individual records, every value with a quote", ""),
        (N(S["quotes"]), "quotes checked against the paper text; all found word for word", ""),
        (N(S["placed"]), "distinct variants placed on the genome", ""),
        (str(S["candidates"]), "in neither ClinVar nor OMIM, awaiting adjudication", "accent"),
        (f"{S['omim_k']} of {S['omim_n']}", f"OMIM-listed variants recovered ({S['omim_pct']}%)", ""),
    ]
    return "\n".join(f'<div class="tile {c}"><div class="big">{esc(b)}</div><div class="lab">{esc(l)}</div></div>' for b, l, c in items)


def disease_table():
    rows = []
    for d in DATA["diseases"]:
        star = '<sup title="development disease: its rules were tuned on its own papers">*</sup>' if d["development"] else ""
        rows.append(f"<tr><td><b>{esc(d['name'])}</b> ({esc(d['short'])}){star}</td><td><i>{esc(d['gene'])}</i></td><td>{esc(d['inheritance'])}</td>"
                    f"<td>{d['papers']} ({d['cov_pct']}%)</td><td>{N(d['individuals'])}</td><td>{N(d['with_variant'])}</td><td>{d['placed']}</td>"
                    f"<td class='accent-text'><b>{d['candidates']}</b></td><td>{d['omim_k']} of {d['omim_n']}</td><td>{d['unsup_pct']}%</td><td>{d['clinvar_plp']}</td></tr>")
    return ("<div class='scroll'><table><thead><tr><th>Disease</th><th>Gene</th><th>Inheritance</th><th>Papers read (open-access share)</th><th>Individuals</th><th>With a variant in the gene</th>"
            "<th>Variants placed on the genome</th><th>Absent from ClinVar and OMIM</th><th>OMIM variants recovered</th><th>Values judged unsupported</th><th>ClinVar P/LP records (gene)</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def ow_table():
    rows = []
    for k in ("ha20", "ssadh"):
        o = S["ow"][k]
        rows.append(f"<tr><td>{esc(DISEASE_SHORT[k])}</td><td>{o['papers']}</td><td>0% / {o['no_quote_pct']}%</td><td>{o['claude_unsup']}% / {o['open_unsup']}%</td>"
                    f"<td>{o['shared']} of {o['union']} ({o['jaccard']}%)</td><td>${o['claude_cost']:.2f} / ${o['open_cost']:.2f}</td><td>{o['claude_min']} / {o['open_min']}</td></tr>")
    return ("<div class='scroll'><table><thead><tr><th>Disease</th><th>Papers</th><th>Values with no quote (Claude / open)</th><th>Judged unsupported (Claude / open)</th>"
            "<th>Variants found by both (shared of union)</th><th>Median cost per paper (Claude est. / open)</th><th>Median minutes per paper</th></tr></thead>"
            f"<tbody>{''.join(rows)}</tbody></table></div>")


def spend_table():
    rows = "".join(f"<tr><td>{esc(l['n'])}</td><td>{esc(l['name'])}</td><td>${l['requested']:,.0f}</td><td>${l['spent']:,.2f}</td></tr>" for l in S["spend_lines"])
    rows += f"<tr><td></td><td><i>Not yet assigned to a line</i></td><td></td><td>${S['spend_unassigned']:,.2f}</td></tr>"
    rows += f"<tr class='total'><td></td><td><b>Total</b></td><td><b>$45,000</b></td><td><b>${S['spend_total']:,}</b></td></tr>"
    return f"<div class='scroll'><table><thead><tr><th>Line</th><th>Budget line</th><th>Requested</th><th>Spent (estimate)</th></tr></thead><tbody>{rows}</tbody></table></div>"


def roles_table():
    rows = [
        ("Audit rater", f"Rate {S['n_o1']} extracted values against their quoted evidence on a blinded web page; two raters and a tie-breaker", "10 to 15 hours per rater", "The primary outcome: the first true accuracy figure for the frozen pipeline"),
        ("Adjudicator", f"Review the {S['candidates']} candidate variants from their dossiers and decide whether the evidence supports a submission", "10 to 15 minutes per candidate", "ClinVar literature-only submissions and OMIM allelic-variant candidates"),
        ("Cohort reader", "Fill a comparator sheet of clinical-feature frequencies from a natural-history cohort paper, without looking at our records", "1 to 2 hours per sheet", "The ascertainment-bias arm"),
        ("Methods or domain reviewer", "Read the short paper or the full report and tell us what is wrong, missing or unclear, from your field's point of view", "1 to 3 hours", "A better study before anything is submitted"),
    ]
    body = "".join(f"<tr><td><b>{esc(a)}</b></td><td>{esc(b)}</td><td>{esc(c)}</td><td>{esc(d)}</td></tr>" for a, b, c, d in rows)
    return f"<div class='scroll'><table><thead><tr><th>Role</th><th>What you would do</th><th>Effort</th><th>What it unlocks</th></tr></thead><tbody>{body}</tbody></table></div>"


def form_block():
    if CFG.get("form_url"):
        return f'<a class="btn primary" href="{esc(CFG["form_url"])}" target="_blank" rel="noopener">Open the input form</a>'
    return f'<p class="note">{esc(CFG.get("form_note", "The input form is being set up."))}</p>'


def doc_list(cands_n):
    docs = [
        (f"Overview video ({video_minutes()} min, narrated)", "video/gp_rarelink_overview.mp4", "MP4", "The 14-slide deck with a synthetic voice (Microsoft neural text-to-speech) and captions. <a href='video/narration_script.html'>Script</a> · <a href='video/gp_rarelink_overview.srt'>subtitles</a>."),
        (f"Deep-dive video ({video_minutes('gp_rarelink_deep_dive')} min, narrated)", "video/gp_rarelink_deep_dive.mp4", "MP4", "The full interim report, section by section, over 56 slides with the same synthetic voice and captions. <a href='video/deep_dive_script.html'>Script</a> · <a href='video/gp_rarelink_deep_dive.srt'>subtitles</a> · <a href='deck/deep_dive.html'>slides with narration</a> · <a href='deck/gp_rarelink_deep_dive.pptx'>PowerPoint</a> · <a href='deck/gp_rarelink_deep_dive.pdf'>PDF</a>."),
        ("Short paper, version 3 (8 pages)", "paper/interim_paper_v3.html", "HTML", "For readers new to the field. Also as <a href='paper/interim_paper_v3.pdf'>PDF</a>."),
        ("Full interim report, version 2 (58 pages)", "paper/interim_paper_v2.html", "HTML", "Every table, interval and method; section 5 is the gap list with costs. Also as <a href='paper/interim_paper_v2.pdf'>PDF</a>."),
        ("Supplement to version 2", "paper/supplement_v2.html", "HTML", "Supplementary tables S1 to S18 and figures."),
        ("Overview deck (14 slides)", "deck/deck.html", "HTML", "Also as <a href='deck/gp_rarelink_overview.pptx'>PowerPoint</a> and <a href='deck/gp_rarelink_overview.pdf'>PDF</a>; speaker notes carry the narration."),
        ("Pre-registered analysis plan (v1.0, frozen 2026-10-20)", "paper/analysis_plan.html", "HTML", "What we committed to measure, and how, before the main run."),
        (f"Candidate variants ({cands_n})", "data/candidates.csv", "CSV", "Also as <a href='data/candidates.json'>JSON</a>. Unadjudicated."),
        ("Key numbers", "data/summary.json", "JSON", "The figures on this page, machine-readable. Spend by line in <a href='data/spend.json'>spend.json</a>."),
    ]
    items = []
    for title, href, kind, note in docs:
        p = SITE / href
        sz = f" · {size_mb(p)}" if p.exists() else ""
        items.append(f"<li><a href='{href}'>{esc(title)}</a> <span class='kind'>{esc(kind)}{sz}</span><div class='docnote'>{note}</div></li>")
    return "<ul class='docs'>" + "".join(items) + "</ul>"


def glossary():
    terms = [
        ("ClinVar", "A public database (NIH) where laboratories and researchers deposit genetic variants with a classification such as pathogenic or uncertain significance. Half of our answer key, and the target for new submissions."),
        ("OMIM", "A curated encyclopedia of genes and genetic diseases that lists selected example variants for each disease. The other half of the answer key; a sample, not a catalogue."),
        ("HPO", "The Human Phenotype Ontology, a standard vocabulary of clinical features. Our records use it in three states: observed, excluded, not reported."),
        ("HGVS", "The standard notation for a variant, such as c.1097_1098del, always relative to a named transcript."),
        ("GRCh38", "The current human reference genome. A variant \"placed on the genome\" has an unambiguous position on it, which is what makes it comparable with ClinVar."),
        ("Phenopacket", "A GA4GH standard file describing one individual: clinical features, variants, diagnosis, with sources. The pipeline's output, one per individual."),
        ("Gatekeeper", "Our name for a second model pass that re-reads every extracted value against its quoted evidence and drops what it cannot support. A filter, not a measure of accuracy."),
        ("Pre-registration", "Writing down the analysis plan, metrics and thresholds before running the study, and freezing them. Changes afterwards are logged as numbered deviations."),
        ("Candidate (gap candidate)", "A genome-placed variant with gatekeeper-supported evidence in the papers that is absent from ClinVar and from OMIM's allelic variants. A candidate for submission, after expert adjudication."),
        ("Development disease", "A20 haploinsufficiency (HA20), on which the pipeline was built and piloted. Its results are flagged; the other five diseases form the confirmatory set."),
    ]
    return "<dl class='gloss'>" + "".join(f"<dt>{esc(t)}</dt><dd>{esc(d)}</dd>" for t, d in terms) + "</dl>"


def deck_page(slides_dir="slides", spec=DATA, out="deck.html", label="Overview deck", base="gp_rarelink_overview", lead="Fourteen slides with their narration. The same text is the video's narration and captions and the deck's speaker notes."):
    slides = sorted((SITE / "deck" / slides_dir).glob("slide-*.png"))
    parts = []
    for i, (p, sl) in enumerate(zip(slides, spec["slides"]), start=1):
        parts.append(f"<section class='slide'><img src='{slides_dir}/{p.name}' alt='Slide {i}' loading='lazy'><p class='narr'><b>Slide {i}.</b> {esc(sl['narration'])}</p></section>")
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>GP-RareLink {esc(label.lower())}</title><link rel="stylesheet" href="../assets/style.css"></head><body class="deckpage">
<header class="top"><a href="../">← Dashboard</a><span>{esc(label)} · {esc(spec['date'])}</span>
<span class="links"><a href="{base}.pptx">PowerPoint</a> · <a href="{base}.pdf">PDF</a> · <a href="../video/{base}.mp4">Video</a></span></header>
<main class="deckmain"><p class="lead">{esc(lead)}</p>{''.join(parts)}</main>
<footer class="foot"><p>GP-RareLink · {esc(label.lower())} for collaborators · internal review · every number from the project repository at commit {esc(spec['commit'])}.</p></footer></body></html>"""
    (SITE / "deck" / out).write_text(page)


def index_page(cands):
    cov = f"{S['cov_lo']}% to {S['cov_hi']}%"
    form = form_block()
    not_done = [
        f"The pre-registered human audit of {S['n_o1']} claims is drawn and its blinded rating pages are built; no claim has been rated.",
        f"None of the {S['candidates']} candidate variants has been adjudicated.",
        "The ascertainment-bias arm has no numbers until a person fills four comparator sheets.",
        "OMIM's clinical synopses (its phenotype half) have not been assessed.",
        f"Only open-access papers were read ({cov} of each disease's corpus); a decision on wider access is pending.",
    ]
    findings = [
        ("1. The receipts hold, but the decisive check has not happened", "fig2_checks.png",
         f"Every one of {N(S['quotes'])} quoted values was found verbatim in its paper. A second model read judged {S['unsup_pct5']}% of values unsupported on the five confirmatory diseases ({S['unsup_pct6']}% with the development disease). But the only human-rated figures, from the pilot before the pipeline was frozen, were {S['human1']}% and {S['human2']}%. The pre-registered test is a blinded audit of {S['n_o1']} claims by two panel members; it is built, and nobody has rated a claim. Until then the machine's rate is a filter's reading, not an accuracy.",
         "Blue: the gatekeeper's verdicts per disease run. Orange: two human audits of the pilot's output. Dashed line: the 2% target."),
        ("2. We find what we can read", "fig3_coverage.png",
         f"Against OMIM's listed variants we recovered {S['omim_k']} of {S['omim_n']} ({S['omim_pct']}%), from nearly 90% where the literature is open to 11% for Tangier disease, whose variants come from closed papers. Of the {S['omim_src_all']} papers OMIM cites as sources for those variants, we could read {S['omim_src_extracted']}; {S['omim_src_paywalled']} are behind paywalls and {S['omim_src_notfound']} were never returned by our searches, mostly pre-1990 papers under earlier names for the disease. Where the source paper was read, the variant was in our records {S['omim_restricted_k']} times out of {S['omim_restricted_n']}. Access, not reading, sets the ceiling; the completeness figures and the candidate list are lower bounds.",
         "A: the share of each disease's papers with open full text beside the share of OMIM's listed variants recovered. B: where OMIM's source papers stand in our corpus."),
        ("3. Hundreds of published variants are in neither database", "fig4_gaps.png",
         f"The papers yielded {N(S['placed'])} distinct variants placed on the genome. {N(S['in_clinvar'])} are in ClinVar, {N(S['plp'])} of them classified pathogenic or likely pathogenic. {S['absent']} are absent from ClinVar; after dropping those whose only evidence failed the second read, checking OMIM, and withdrawing one normalization error of our own, {S['candidates']} candidates remain, each with a dossier of every paper, quote and individual. {S['reclass']} more sit in ClinVar as uncertain or conflicting while the papers call them pathogenic. The full list is below. Nothing is submitted without adjudication.",
         "Each bar: one disease's genome-placed variants. Orange: the candidates."),
    ]
    find_html = ""
    for title, fig, text, cap in findings:
        find_html += f"<article class='finding'><h3>{esc(title)}</h3><p>{esc(text)}</p><figure><img src='figures/{fig}' alt='{esc(title)}'><figcaption>{esc(cap)}</figcaption></figure></article>"
    o = S["ow"]
    find_html += f"""<article class='finding'><h3>4. A cheaper open-weight model finds the same variants and loses the receipts</h3>
<p>{esc(f"On identical papers, prompts, forms and scoring, DeepSeek-V4.1-Flash found the same variants {o['ha20']['jaccard']}% to {o['ssadh']['jaccard']}% of the time at about 1/{S['cost_ratio']} of the cost per paper and {S['time_ratio']} times the wall-clock. It left {o['ssadh']['no_quote_pct']}% to {o['ha20']['no_quote_pct']}% of its values with no quote at all, which the rules forbid, and the second read rejected {o['ssadh']['open_unsup']}% to {o['ha20']['open_unsup']}% of its claims against Claude's {o['ha20']['claude_unsup']}% to {o['ssadh']['claude_unsup']}%. The judge is itself Claude, so this is not neutral until the planned blinded human audit of both outputs.")}</p>{ow_table()}</article>
<article class='finding'><h3>5. Repeat runs agree, and the model did not recall the papers</h3>
<p>{esc(f"Running a tenth of the papers a second time ({S['repeat_papers']} papers) gave the same checklist answers {S['chk_lo']}% to {S['chk_hi']}% of the time and the same variants {S['var_lo']}% to {S['var_hi']}% of the time; where the runs differed it was mostly over how many individuals a cohort paper describes. A memorization probe on {S['mem_papers']} papers, stratified around the model's training cutoff, found no sign that either model recalled the papers from training: in the {S['mem_after']} papers published after the cutoff, neither produced a specific recall or a correct variant.")}</p></article>"""
    cand_opts = "".join(f"<option value='{k}'>{esc(DISEASE_NAME[k])}</option>" for k in DISEASE_NAME)
    abl = f" A separate exploratory pilot in another session cost about ${S['ablation']:,}; the open-weight runs cost ${S['ow_key_spend']} outside the award." if S.get("ablation") else ""
    page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>GP-RareLink · collaborator dashboard</title>
<meta name="description" content="Interim results and orientation for collaborators on GP-RareLink: reading the rare-disease literature with a language model, and checking its work.">
<meta name="robots" content="noindex">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap">
<link rel="stylesheet" href="assets/style.css">
</head>
<body>
<header class="top">
  <a href="#top" class="brand">GP-RareLink</a>
  <nav><a href="#start">Start here</a><a href="#problem">The problem</a><a href="#how">How it works</a><a href="#status">Status</a><a href="#findings">Findings</a><a href="#help">What we need</a><a href="#candidates">Candidates</a><a href="#documents">Documents</a><a href="#glossary">Glossary</a></nav>
</header>
<main id="top">
<section class="hero">
  <p class="kicker">Interim results for internal review · updated {esc(DATA['date'])} · repository commit {esc(DATA['commit'])}</p>
  <h1>Reading the rare-disease literature with a language model, and checking its work</h1>
  <p class="lead">GP-RareLink turns published case reports on six rare genetic diseases into structured patient records in which every value carries a quote from its source, then checks those records against ClinVar and OMIM, which the model never sees. This page is the orientation for experts joining the project: what we did, what we found, what is still open, and how you can take part.</p>
  <p class="byline">A project of the Rare Genomics Institute and the Stanford Open Virtual Assistant Lab, led by Dr. Jimmy Lin. Funded by Anthropic's AI for Science program. Shared with invited collaborators; not a publication.</p>
  <div class="cta">
    <a class="btn primary" href="video/gp_rarelink_overview.mp4">Watch the {video_minutes()}-minute overview</a>
    <a class="btn" href="video/gp_rarelink_deep_dive.mp4">Watch the {video_minutes('gp_rarelink_deep_dive')}-minute deep dive</a>
    <a class="btn" href="paper/interim_paper_v3.html">Read the 8-page paper</a>
    <a class="btn" href="#help">Tell us how you would like to help</a>
  </div>
</section>

<section id="start">
  <h2>Start here: a path through the project in about an hour</h2>
  <ol class="path">
    <li><b>Watch the overview video</b> <span class="time">{video_minutes()} min</span><br>Narrated (synthetic voice) with captions. <a href="video/gp_rarelink_overview.mp4">Play</a> · <a href="video/narration_script.html">script</a>. When you have longer: the <a href="video/gp_rarelink_deep_dive.mp4">{video_minutes('gp_rarelink_deep_dive')}-minute deep dive</a> walks through the full report (<a href="deck/deep_dive.html">slides with narration</a>).</li>
    <li><b>Read the short paper</b> <span class="time">20 min</span><br>Eight pages written for readers new to the field. <a href="paper/interim_paper_v3.html">HTML</a> · <a href="paper/interim_paper_v3.pdf">PDF</a></li>
    <li><b>Flip through the deck</b> <span class="time">10 min</span><br>Fourteen slides with their narration. <a href="deck/deck.html">View</a> · <a href="deck/gp_rarelink_overview.pptx">PowerPoint</a> · <a href="deck/gp_rarelink_overview.pdf">PDF</a></li>
    <li><b>Skim the full report</b> <span class="time">15 min for section 5</span><br>Fifty-eight pages with every table and interval; its section 5 lists the gaps and a costed plan to close them. <a href="paper/interim_paper_v2.html">HTML</a> · <a href="paper/interim_paper_v2.pdf">PDF</a> · <a href="paper/supplement_v2.html">supplement</a></li>
    <li><b>Explore the candidate variants</b> <span class="time">10 min</span><br>The {S['candidates']} variants that are published but absent from both databases, with their papers. <a href="#candidates">Table below</a></li>
    <li><b>Tell us who you are</b> <span class="time">5 min</span><br>Name, background, which diseases you know, and how you would like to contribute. <a href="#help">The form</a></li>
  </ol>
</section>

<section id="problem">
  <h2>The problem, and the question</h2>
  <p>When a child with a rare disease finally gets a genetic diagnosis, the responsible variant is often reported in a single case report and never submitted to a public database. A laboratory testing the next child searches ClinVar and finds nothing. For Alexander disease alone, a 2024 review counts 182 causative variants in 550 published patients, against {S['axd_clinvar_plp']} pathogenic or likely-pathogenic ClinVar records for the gene (release {esc(S['clinvar_release'])}). The knowledge exists; it is scattered across thousands of papers in prose and tables no database can query, and hand curation has never kept up.</p>
  <p><b>The question.</b> Can a large language model, reading with strict rules, do the first pass: turn case reports into structured records of which variant, in which person, with which clinical features, each value tied to the sentence it came from, at an accuracy we can measure rather than assume? The method is SLIDERS, an evidence-first systematic-review approach from the Stanford OVAL lab, with Claude doing the reading.</p>
  <div class="cards">
    <div class="card"><span class="num">1</span><h3>Quote everything</h3><p>A value without a verbatim quote is not allowed. A script looks up every quote in the paper. "Not reported" is a valid answer; a paper's silence never becomes a "no".</p></div>
    <div class="card"><span class="num">2</span><h3>Hold out the answer key</h3><p>ClinVar and OMIM are never shown to the model. Code that reads papers cannot read them, and a test fails if it could. They are compared afterwards by a separate harness.</p></div>
    <div class="card"><span class="num">3</span><h3>Decide the rules first</h3><p>Prompts, forms and the analysis plan were frozen on 2026-10-20 after a one-disease pilot (<a href="paper/analysis_plan.html">the plan</a>). Changes since are logged as numbered deviations.</p></div>
  </div>
</section>

<section id="how">
  <h2>How the pipeline works</h2>
  <figure class="wide"><img src="figures/fig1_workflow.png" alt="The workflow: papers, one reader per paper, quote check, second read, records; below the firewall the answer key, the comparison harness and the people"><figcaption>The reading side (blue) never sees the answer key (grey). Steps that need people (orange) have not started. Numbers are from the six-disease run.</figcaption></figure>
  <p>One model reader per paper fills a structured form with quotes. A script checks every quote against the paper text. A second model pass, the gatekeeper, re-reads each value against its quote and drops the ones it cannot support. The output is one standard record per individual, a GA4GH phenopacket, with clinical features as HPO terms in three states (observed, excluded, not reported), the variant written in HGVS on a named transcript and placed on the genome, and the paper and quote behind every value. A separate harness then compares the records with a dated ClinVar release, OMIM's frozen entry pages and two published catalogues, and lists the variants the databases are missing.</p>
</section>

<section id="status">
  <h2>Where things stand</h2>
  <div class="tiles">{tiles()}</div>
  <div class="notdone"><h3>What has not happened yet, and needs people</h3><ul>{''.join(f'<li>{esc(x)}</li>' for x in not_done)}</ul></div>
  <h3>The six diseases</h3>
  <p>Chosen to span inheritance modes and organ systems, all absent from the main public collection of phenopackets. A20 haploinsufficiency (HA20) was used to develop and pilot the pipeline, so its numbers are flagged and the other five form the confirmatory set. Only open-access papers were read.</p>
  {disease_table()}
  <p class="small">* Development disease. "Placed on the genome" = written unambiguously on GRCh38, which is what makes a variant comparable with ClinVar. "Values judged unsupported" = the second model read's verdicts, not a human audit. ClinVar counts are single-gene GRCh38 records in the release of {esc(S['clinvar_release'])}; OMIM counts come from the gene entry pages frozen on {esc(S['omim_date'])}.</p>
</section>

<section id="findings">
  <h2>Findings so far</h2>
  {find_html}
  <div class="notdone soft"><h3>How to read these numbers</h3><ul>
    <li>No accuracy claim is made for the frozen pipeline. Every error rate above is a model's reading of a model's output; the human figures are from the pilot.</li>
    <li>HA20 developed the pipeline; quote the five-disease figures.</li>
    <li>Open access only: completeness, recall and the gap count are measured on what could be read.</li>
    <li>OMIM is a sample. Recall against its listed variants is meaningful; "precision against OMIM" is not.</li>
    <li>Costs are estimates from usage readings, not invoices.</li>
    <li>The pipeline's author (Claude Code) also generated the reports from its outputs. The numbers are reproducible from the committed files; the framing is not independent of the system it describes, which is one more reason the human audit decides.</li>
  </ul></div>
</section>

<section id="help">
  <h2>What we need from you</h2>
  <p>The expensive, decisive parts of this study are the ones only people can do. Each role below unlocks a pre-registered result or a deliverable. Everything is published literature; there is no patient data.</p>
  {roles_table()}
  <div class="formbox"><h3>Tell us who you are and how you would like to contribute</h3><p>Five minutes: name, background, which of the six diseases you know, the roles that suit you, your availability over the next eight weeks, and what you make of the results so far.</p>{form}</div>
</section>

<section id="candidates">
  <h2>Candidate variants absent from ClinVar and OMIM</h2>
  <p>{S['candidates']} variants placed on the genome from the papers we read, with values the second read supported, that are absent from ClinVar in two successive releases and from OMIM's allelic variants. <b>None has been adjudicated</b>; some will prove to be notation differences, the same patient reported twice, or carriers rather than cases, which is what the dossiers and the panel are for. PubMed links open the source papers. Download as <a href="data/candidates.csv">CSV</a> or <a href="data/candidates.json">JSON</a>.</p>
  <div class="controls"><label>Disease <select id="f-disease"><option value="">All</option>{cand_opts}</select></label><label>Search <input id="f-text" type="search" placeholder="variant, gene, PMID…"></label><span id="f-count" class="small"></span></div>
  <div class="scroll"><table id="cand"><thead><tr><th data-k="id">ID</th><th data-k="disease">Disease</th><th data-k="gene">Gene</th><th data-k="hgvs_c">Variant (normalized)</th><th data-k="protein">Predicted protein</th><th>As written in the papers</th><th data-k="n_papers">Papers</th><th data-k="n_identities">Individuals</th><th data-k="author_class">Authors' class</th><th>PubMed</th></tr></thead><tbody></tbody></table></div>
</section>

<section id="spend">
  <h2>Spend so far</h2>
  <p>About ${S['spend_total']:,} of the $45,000 award by this session's own usage readings to {esc(S['spend_date'])}. These are estimates, not billing figures.{esc(abl)} The expensive parts, human rating and adjudication, have not happened.</p>
  {spend_table()}
</section>

<section id="documents">
  <h2>Documents and data</h2>
  {doc_list(len(cands))}
  <p class="small">The project repository is <a href="{esc(CFG['repo_url'])}">{esc(CFG['repo_url'])}</a> (access on request). Every number on this page is produced by scripts there from the committed result files, at commit {esc(DATA['commit'])}; this page regenerates with <code>uv run python -m analysis.dashboard.build_site</code>.</p>
</section>

<section id="glossary">
  <h2>Glossary</h2>
  {glossary()}
</section>
</main>
<footer class="foot">
  <p>GP-RareLink · Rare Genomics Institute and the Stanford Open Virtual Assistant Lab · funded by Anthropic's AI for Science program. Interim results shared with invited collaborators for internal review; please do not redistribute. Literature only; no patient data. Page generated {esc(DATA['date'])}.</p>
</footer>
<script src="assets/app.js"></script>
</body>
</html>
"""
    (SITE / "index.html").write_text(page)


STYLE = """
:root{--ink:#0b0b0b;--ink2:#52514e;--muted:#898781;--grid:#e1e0d9;--paper:#ffffff;--tint:#f3f3f1;--blue:#2a78d6;--deep:#184f95;--navy:#0f2f5c;--orange:#eb6834;--peach:#fdf1ec;--lightblue:#eaf2fc}
*{box-sizing:border-box}html{scroll-behavior:smooth}
body{margin:0;font-family:Inter,system-ui,-apple-system,"Segoe UI",sans-serif;color:var(--ink);background:var(--paper);line-height:1.5;font-size:16px}
a{color:var(--blue);text-decoration:none}a:hover{text-decoration:underline}
header.top{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:16px;padding:10px 16px;background:rgba(255,255,255,.96);border-bottom:1px solid var(--grid);backdrop-filter:blur(6px)}
header.top .brand{font-weight:700;color:var(--ink);font-size:17px}header.top nav{display:flex;flex-wrap:wrap;gap:4px 14px;font-size:14px}header.top nav a{color:var(--ink2)}
header.top .links{margin-left:auto;font-size:14px}header.top span{color:var(--ink2);font-size:14px}
main{max-width:1040px;margin:0 auto;padding:0 16px 48px}section{padding:40px 0 8px;border-bottom:1px solid var(--grid)}section:last-of-type{border-bottom:0}
h1{font-size:clamp(28px,4.2vw,40px);line-height:1.15;margin:8px 0 16px;letter-spacing:-.01em}h2{font-size:26px;margin:0 0 14px;letter-spacing:-.01em}h3{font-size:18px;margin:22px 0 8px}
.hero{padding-top:44px}.kicker{color:var(--muted);font-size:14px;margin:0}.lead{font-size:18px;color:var(--ink2);max-width:62ch}.byline{color:var(--muted);font-size:14px;max-width:70ch}
.cta{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0 8px}
.btn{display:inline-block;padding:10px 16px;border-radius:8px;border:1px solid var(--grid);background:var(--tint);color:var(--ink);font-weight:500;font-size:15px}.btn:hover{text-decoration:none;border-color:var(--blue)}
.btn.primary{background:var(--blue);border-color:var(--blue);color:#fff}
ol.path{counter-reset:p;list-style:none;padding:0;margin:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:12px}
ol.path li{counter-increment:p;background:var(--tint);border-radius:10px;padding:16px 16px 16px 56px;position:relative;font-size:15px;color:var(--ink2)}ol.path li b{color:var(--ink)}
ol.path li::before{content:counter(p);position:absolute;left:14px;top:14px;width:30px;height:30px;border-radius:50%;background:var(--blue);color:#fff;font-weight:600;display:flex;align-items:center;justify-content:center;font-size:14px}
.time{color:var(--muted);font-size:13px;margin-left:6px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin:18px 0}
.card{background:var(--tint);border-radius:10px;padding:18px;position:relative}.card .num{display:inline-flex;width:30px;height:30px;border-radius:50%;background:var(--blue);color:#fff;font-weight:600;align-items:center;justify-content:center;font-size:14px}
.card h3{margin:10px 0 6px}.card p{margin:0;color:var(--ink2);font-size:15px}
figure{margin:18px 0}figure img{width:100%;height:auto;border:1px solid var(--grid);border-radius:8px;background:#fcfcfb}figcaption{color:var(--muted);font-size:13.5px;margin-top:6px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;margin:12px 0 20px}
.tile{background:var(--tint);border-radius:10px;padding:16px}.tile .big{font-size:30px;font-weight:700;color:var(--blue);letter-spacing:-.01em}.tile.accent .big{color:var(--orange)}.tile .lab{color:var(--ink2);font-size:13.5px;margin-top:4px}
.notdone{background:var(--peach);border:1px solid #f4c7b3;border-radius:10px;padding:14px 18px;margin:14px 0 24px}.notdone.soft{background:var(--lightblue);border-color:#bfd6f3}.notdone h3{margin:0 0 8px;font-size:16px}.notdone ul{margin:0;padding-left:20px;color:var(--ink2);font-size:15px}
.scroll{overflow-x:auto;margin:10px 0 14px}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid var(--grid);padding:7px 9px;text-align:left;vertical-align:top}th{background:var(--tint);font-weight:600;position:sticky;top:0}
tr.total td{border-top:2px solid var(--ink2)}.accent-text{color:var(--orange)}.small{color:var(--muted);font-size:13.5px}
.finding{margin:0 0 26px}.finding h3{margin-top:0}.finding p{color:var(--ink2)}
.formbox{background:var(--lightblue);border:1px solid #bfd6f3;border-radius:10px;padding:18px;margin:18px 0}.formbox h3{margin:0 0 8px}.formbox p{color:var(--ink2);margin:0 0 12px}.note{color:var(--ink2);font-style:italic;margin:0}
.controls{display:flex;flex-wrap:wrap;gap:14px;align-items:center;margin:12px 0}.controls label{font-size:14px;color:var(--ink2);display:flex;gap:6px;align-items:center}.controls select,.controls input{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--grid);border-radius:6px;background:#fff;min-width:160px}
#cand{min-width:1180px}#cand td:first-child,#cand td.mono{white-space:nowrap}#cand td.wrap{white-space:normal;max-width:260px}#cand th[data-k]{cursor:pointer}#cand th[data-k]:hover{color:var(--blue)}#cand td.mono{font-family:ui-monospace,"DejaVu Sans Mono",monospace;font-size:13px}
ul.docs{list-style:none;padding:0;margin:0}ul.docs li{padding:10px 0;border-bottom:1px solid var(--grid)}ul.docs li:last-child{border-bottom:0}.kind{color:var(--muted);font-size:13px;margin-left:8px}.docnote{color:var(--ink2);font-size:14px}
dl.gloss{display:grid;grid-template-columns:max-content 1fr;gap:8px 18px}dl.gloss dt{font-weight:600}dl.gloss dd{margin:0;color:var(--ink2)}
footer.foot{border-top:1px solid var(--grid);padding:22px 16px;color:var(--muted);font-size:13.5px;max-width:1040px;margin:0 auto}
body.deckpage .deckmain{max-width:980px;margin:0 auto;padding:16px}.slide{margin:0 0 28px}.slide img{width:100%;height:auto;border:1px solid var(--grid);border-radius:8px}.narr{color:var(--ink2);font-size:15px;margin:8px 0 0}
@media (max-width:700px){header.top nav{display:none}dl.gloss{grid-template-columns:1fr}dl.gloss dd{margin-bottom:8px}section{padding-top:28px}h2{font-size:22px}}
"""

APP_JS = """
(function(){
  const tbody=document.querySelector('#cand tbody'); if(!tbody) return;
  const names={ha20:'HA20',ssadh:'SSADH',tangier:'Tangier',lad1:'LAD-I',axd:'AxD',danon:'Danon'};
  const full={ha20:'A20 haploinsufficiency',ssadh:'SSADH deficiency',tangier:'Tangier disease',lad1:'Leukocyte adhesion deficiency I',axd:'Alexander disease',danon:'Danon disease'};
  let rows=[], sortKey='id', asc=true;
  const esc=s=>String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function render(){
    const d=document.getElementById('f-disease').value, q=document.getElementById('f-text').value.trim().toLowerCase();
    let out=rows.filter(r=>(!d||r.disease===d)&&(!q||[r.id,r.gene,r.hgvs_c,r.protein,r.written,r.pmids.join(' '),r.author_class].join(' ').toLowerCase().includes(q)));
    out.sort((a,b)=>{const x=a[sortKey],y=b[sortKey];const c=(typeof x==='number')?x-y:String(x).localeCompare(String(y));return asc?c:-c;});
    tbody.innerHTML=out.map(r=>`<tr><td>${esc(r.id)}</td><td title="${esc(full[r.disease]||r.disease)}">${esc(names[r.disease]||r.disease)}</td><td><i>${esc(r.gene)}</i></td><td class="mono">${esc(r.hgvs_c)}</td><td class="mono">${esc(r.protein||'—')}</td><td class="mono wrap">${esc(r.written)}</td><td>${r.n_papers}</td><td>${r.n_identities}</td><td>${esc(r.author_class)}</td><td>${r.pmids.map(p=>`<a href="https://pubmed.ncbi.nlm.nih.gov/${esc(p)}/" target="_blank" rel="noopener">${esc(p)}</a>`).join(' ')}</td></tr>`).join('');
    document.getElementById('f-count').textContent=`${out.length} of ${rows.length} candidates`;
  }
  fetch('data/candidates.json').then(r=>r.json()).then(j=>{rows=j;render();});
  document.getElementById('f-disease').addEventListener('change',render);
  document.getElementById('f-text').addEventListener('input',render);
  document.querySelectorAll('#cand th[data-k]').forEach(th=>th.addEventListener('click',()=>{const k=th.dataset.k; if(sortKey===k) asc=!asc; else {sortKey=k; asc=true;} render();}));
})();
"""


def main():
    SITE.mkdir(exist_ok=True)
    build_documents()
    cands = candidates()
    write_summary()
    (SITE / "assets/style.css").write_text(STYLE.strip() + "\n")
    (SITE / "assets/app.js").write_text(APP_JS.strip() + "\n")
    deck_page()
    if DEEP and (SITE / "deck/deep_dive_slides").exists():
        deck_page("deep_dive_slides", DEEP, "deep_dive.html", "Deep-dive deck", "gp_rarelink_deep_dive", f"{len(DEEP['slides'])} slides following the full interim report, with their narration. The same text is the long video's narration and captions and the deck's speaker notes.")
    index_page(cands)
    # privacy check: no email addresses anywhere in the site
    bad = []
    for p in SITE.rglob("*"):
        if p.suffix in (".html", ".json", ".csv", ".md", ".srt", ".js", ".css") and re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", p.read_text(errors="ignore")):
            bad.append(str(p.relative_to(SITE)))
    if bad:
        raise SystemExit(f"email address found in site files: {bad}")
    total = sum(p.stat().st_size for p in SITE.rglob("*") if p.is_file())
    print(f"built {SITE} ({total / 1e6:.1f} MB; {len(cands)} candidates; form_url={'set' if CFG.get('form_url') else 'not set'})")


if __name__ == "__main__":
    main()
