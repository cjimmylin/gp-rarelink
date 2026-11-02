"""Figures for version 3 of the interim paper (the short, approachable highlights version).

Every panel is drawn from `analysis.interim_paper.data.load()`; nothing is typed in by hand. Output: PNG files
under reports/interim_paper_v3/figures/. Styling (palette, grid, fonts) is shared with figures.py.
"""
from __future__ import annotations

from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyBboxPatch, Patch

from .data import CONFIRMATORY, DISEASES, SHORT
from .figures import AXIS, BLUE, DEEMPH, GRID, INK, INK2, LIGHT_BLUE, MUTED, ORANGE, ORD4, SURFACE, label, style

OUT = Path(__file__).resolve().parents[2] / "reports/interim_paper_v3/figures"


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    return f"figures/{name}.png"


def N(x):
    return f"{x:,}"


def release_date(s: str) -> str:
    return datetime.strptime(s, "%a, %d %b %Y %H:%M:%S GMT").strftime("%Y-%m-%d")


# ------------------------------------------------------------------------------------------ Figure 1: the workflow
def fig1_workflow(D):
    t = D["totals"]["all"]
    dropped = sum(v for d in DISEASES for k, v in D["build"][d]["counts"].items() if k.startswith("gk_dropped"))
    placed = sum(D["gaps"][d]["tier1_alleles"] for d in DISEASES)
    in_clinvar = sum(D["o2_tiers"][d].get("1", 0) for d in DISEASES)
    live = t["gap_candidates_live"]
    om = D["omimh"]
    fig, ax = plt.subplots(figsize=(13, 5.6))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 52)
    ax.axis("off")

    def box(x, y, w, h, title, lines, kind="read"):
        face = {"read": "#eaf2fc", "key": "#f3f3f1", "human": "#fdf1ec"}[kind]
        edge = {"read": BLUE, "key": MUTED, "human": ORANGE}[kind]
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.2,
                                    edgecolor=edge, facecolor=face, zorder=2))
        ax.text(x + 1.0, y + h - 1.5, title, fontsize=9.2, weight="semibold", color=INK, va="top", zorder=3)
        ax.text(x + 1.0, y + h - 4.6, "\n".join(lines), fontsize=7.4, color=INK2, va="top", zorder=3, linespacing=1.4)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=INK2, lw=1.0, shrinkA=0, shrinkB=0), zorder=4)

    # top row: reading side
    w, h, y = 17.5, 15.5, 33
    xs = [1, 20.5, 40, 59.5, 79]
    box(xs[0], y, w, h, "1. Papers", [f"{N(t['papers'])} open-access papers", "on six rare diseases", "(case reports, series,", "reviews with patient tables)"])
    box(xs[1], y, w, h, "2. One reader per paper", ["A Claude Opus helper reads", "only the paper, the rules and", "the form. Every value it fills", "must carry a verbatim quote."])
    box(xs[2], y, w, h, "3. Quote check (script)", [f"{N(t['claims_all'])} quotes looked up", "in the paper text:", "all found, word for word"])
    box(xs[3], y, w, h, "4. Second read (\"gatekeeper\")", ["A second model asks of every", "claim: does the quote support", f"this value? {N(t['unsupported'])} of {N(t['model_claims'])}", f"judged unsupported; {N(dropped)} claims", "dropped before records are built"])
    box(xs[4], y, w, h, "5. Records", [f"{N(t['phenopackets'])} standard patient records", "(GA4GH phenopackets):", f"{N(t['with_variant'])} with a gene variant,", f"{N(t['features_observed'])} observed and", f"{N(t['features_excluded'])} excluded features"])
    for i in range(4):
        arrow(xs[i] + w + 0.4, y + h / 2, xs[i + 1] - 0.4, y + h / 2)
    # firewall
    ax.plot([0, 100], [29.5, 29.5], ls=(0, (4, 3)), color=ORANGE, lw=1.3, zorder=1)
    ax.text(1, 30.6, "Firewall: nothing below this line is ever shown to the reader in steps 2 to 4", ha="left", va="bottom", fontsize=8, color=ORANGE, weight="medium")
    # bottom row: answer key, harness, people
    y2, h2 = 9, 17
    cv_date = release_date(D["clinvar"]["ssadh"]["release"])
    box(1, y2, 30, h2, "6. The answer key (held out)", [f"ClinVar release {cv_date}", f"OMIM entry pages frozen {om['date']}", "Two published variant catalogues", "(A20 haploinsufficiency, Alexander disease)"], kind="key")
    box(35, y2, 30, h2, "7. Comparison harness (script)", [f"{N(placed)} variants placed on the genome;", f"{N(in_clinvar)} are in ClinVar, {N(placed - in_clinvar)} are not", f"{N(live)} candidates absent from ClinVar and OMIM,", "each with an evidence dossier", f"{om['totals']['recovered_strict']} of {om['totals']['omim_allelic_variants_for_diseases']} OMIM variants recovered"], kind="key")
    box(69, y2, 30, h2, "8. People (not started)", [f"Blinded audit of {D['o1']['n']} claims", "by two panel raters", f"Adjudication of the {N(live)} candidates", "Sign-off before any submission"], kind="human")
    arrow(31.4, y2 + h2 / 2, 34.6, y2 + h2 / 2)
    arrow(65.4, y2 + h2 / 2, 68.6, y2 + h2 / 2)
    # records flow down to the harness
    arrow(xs[4] + w / 2, y - 0.4, 50, y2 + h2 + 0.4)
    ax.text(2, 2.0, "Blue: the reading side, run by the frozen pipeline (v1.0, 2026-10-20). Grey: reference data and scoring, which only the harness reads. Orange: steps that need people.",
            fontsize=7.4, color=MUTED, va="bottom")
    return save(fig, "fig1_workflow")


# ---------------------------------------------------------------------------- Figure 2: machine check vs human check
def fig2_checks(D):
    rows = []
    for d in DISEASES:
        u = D["run"][d]["unsupported_or_not_found"]
        rows.append((label(d), 100 * u["share"], 100 * u["ci95"][0], 100 * u["ci95"][1], "machine"))
    from .stats import clopper_pearson
    for key, name in (("five", "Five diseases, pooled"), ("all", "All six, pooled")):
        t = D["totals"][key]
        lo, hi = clopper_pearson(t["unsupported"], t["model_claims"])
        rows.append((name, 100 * t["unsupported"] / t["model_claims"], 100 * lo, 100 * hi, "machine"))
    a1, a2 = D["poc"]["audit1"]["unsupported_strict"], D["poc"]["audit2"]["unsupported_strict"]
    rows.append((f"Pilot run, humans ({a1['n']} claims)", 100 * a1["share"], 100 * a1["ci95"][0], 100 * a1["ci95"][1], "human"))
    rows.append((f"Pilot re-run, humans ({a2['n']} claims)", 100 * a2["share"], 100 * a2["ci95"][0], 100 * a2["ci95"][1], "human"))
    fig, ax = plt.subplots(figsize=(9.5, 4.2))
    ys = list(range(len(rows)))[::-1]
    for y, (name, v, lo, hi, kind) in zip(ys, rows):
        c = BLUE if kind == "machine" else ORANGE
        ax.plot([lo, hi], [y, y], color=c, lw=1.6, solid_capstyle="round", zorder=2)
        ax.plot(v, y, "o", color=c, ms=7, mec=SURFACE, mew=1.5, zorder=3)
        ax.text(hi + 0.3, y, f"{Decimal(str(v)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}%", va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([r[0] for r in rows])
    for lab_, r in zip(ax.get_yticklabels(), rows):
        if r[0].startswith(("Five", "All six")):
            lab_.set_fontweight("semibold")
    ax.axvline(2, color=MUTED, lw=1, ls=(0, (4, 3)), zorder=1)
    ax.text(2.15, ys[0] + 0.55, "pre-registered target: under 2%", fontsize=8, color=MUTED, va="bottom")
    ax.set_xlim(0, 19)
    ax.set_ylim(-0.8, len(rows) - 0.2)
    ax.set_xlabel("Values judged unsupported by their quoted evidence (%), with 95% interval")
    style(ax, grid="x")
    ax.legend(handles=[Line2D([], [], marker="o", color=BLUE, lw=1.6, ms=6, label="Second model read (the frozen pipeline's six runs)"),
                       Line2D([], [], marker="o", color=ORANGE, lw=1.6, ms=6, label="Human raters (the pilot, before the pipeline was frozen)")],
              loc="upper right", fontsize=8)
    return save(fig, "fig2_checks")


# ----------------------------------------------------------------------------- Figure 3: coverage is the limit
def fig3_coverage(D):
    om = D["omimh"]
    order = sorted(DISEASES, key=lambda d: om["per"][d]["B_allelic_variants"]["recall_unrestricted_strict"]["share"])
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 3.9), gridspec_kw={"width_ratios": [1.25, 1]})
    ys = list(range(len(order)))
    for y, d in zip(ys, order):
        cov = 100 * D["coverage"][d]["fulltext_share"]
        r = om["per"][d]["B_allelic_variants"]["recall_unrestricted_strict"]
        rec = 100 * r["share"]
        ax.plot([min(cov, rec), max(cov, rec)], [y, y], color=GRID, lw=2.5, zorder=1)
        ax.plot(cov, y, "o", color=LIGHT_BLUE, ms=8, mec=SURFACE, mew=1.2, zorder=3)
        ax.plot(rec, y, "o", color=BLUE, ms=8, mec=SURFACE, mew=1.2, zorder=3)
        ax.text(cov, y + 0.36, f"{cov:.0f}%", ha="center", fontsize=7.5, color=INK2)
        ax.text(rec, y - 0.5, f"{rec:.0f}% ({r['k']}/{r['n']})", ha="center", fontsize=7.5, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([label(d) for d in order])
    ax.set_xlim(0, 100)
    ax.set_ylim(-0.9, len(order) - 0.3)
    ax.set_xlabel("Per cent")
    ax.set_title("A. What we could read, and what we recovered", fontsize=9.5)
    style(ax, grid="x")
    ax.legend(handles=[Line2D([], [], marker="o", color=LIGHT_BLUE, lw=0, ms=7, label="Share of the disease's papers with open full text"),
                       Line2D([], [], marker="o", color=BLUE, lw=0, ms=7, label="Share of OMIM's listed variants found in our records")],
              loc="lower right", fontsize=7.5)
    # B: where OMIM's source papers stand
    f = {}
    for d in DISEASES:
        for st, n in om["per"][d]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {}).items():
            f[st] = f.get(st, 0) + n
    cats = [("extracted", "We read it (open access)"), ("in corpus, no open full text", "Found by our search, but behind a paywall"),
            ("not found by search", "Never returned by our searches"), ("not in corpus (screened unclear/other)", "Screened out or unclear")]
    vals = [f.get(k, 0) for k, _ in cats]
    other = sum(f.values()) - sum(vals)
    if other:
        vals[-1] += other
    total = sum(f.values())
    cols = [ORD4[3], ORD4[2], ORD4[1], ORD4[0]]
    ys = list(range(len(cats)))[::-1]
    bx.barh(ys, vals, color=cols, height=0.62, zorder=2)
    for y, v in zip(ys, vals):
        bx.text(v + 0.8, y, f"{v} ({100 * v / total:.0f}%)", va="center", fontsize=8, color=INK2)
    bx.set_yticks(ys)
    bx.set_yticklabels([c[1] for c in cats])
    bx.set_xlim(0, max(vals) * 1.35)
    bx.set_xlabel("Papers")
    bx.set_title(f"B. The {total} papers OMIM cites for its variants", fontsize=9.5)
    style(bx, grid="x")
    fig.tight_layout(w_pad=2.5)
    return save(fig, "fig3_coverage")


# ------------------------------------------------------------------------------ Figure 4: what the databases hold
def fig4_gaps(D):
    order = sorted(DISEASES, key=lambda d: D["gaps"][d]["tier1_alleles"])
    seg = {"plp": [], "other": [], "cand": [], "nocand": []}
    for d in order:
        t, cl, g = D["o2_tiers"][d], D["o2_tier1_classes"][d], D["gaps"][d]
        plp = sum(v for k, v in cl.items() if k in ("P", "LP", "P/LP"))
        seg["plp"].append(plp)
        seg["other"].append(t.get("1", 0) - plp)
        live = D["omimh"]["gap_live"][d]
        seg["cand"].append(live)
        seg["nocand"].append(t.get("unmatched", 0) - live)
    fig, ax = plt.subplots(figsize=(9.5, 3.9))
    ys = list(range(len(order)))
    left = [0] * len(order)
    spec = [("plp", BLUE, "In ClinVar as pathogenic or likely pathogenic"), ("other", LIGHT_BLUE, "In ClinVar with another classification (uncertain, conflicting, benign, none)"),
            ("cand", ORANGE, "Absent from ClinVar and OMIM: candidate for submission, awaiting the panel"), ("nocand", DEEMPH, "Absent, but not a candidate (evidence failed the second read or withdrawn)")]
    for key, c, _ in spec:
        vals = seg[key]
        ax.barh(ys, vals, left=left, color=c, height=0.62, zorder=2, edgecolor=SURFACE, linewidth=1.2)
        if key == "cand":
            for y, v, l in zip(ys, vals, left):
                if v:
                    ax.text(l + v / 2, y, str(v), ha="center", va="center", fontsize=8, color="white", weight="semibold")
        left = [a + b for a, b in zip(left, vals)]
    for y, tot in zip(ys, left):
        ax.text(tot + 1.5, y, N(tot), va="center", fontsize=8, color=INK2)
    ax.set_yticks(ys)
    ax.set_yticklabels([label(d) for d in order])
    ax.set_xlim(0, max(left) * 1.12)
    ax.set_xlabel("Distinct variants placed on the genome (GRCh38) from the papers we read")
    style(ax, grid="x")
    ax.legend(handles=[Patch(color=c, label=l) for _, c, l in spec], loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=2, fontsize=7.6, frameon=False)
    return save(fig, "fig4_gaps")


def make_all(D):
    return {"fig1": fig1_workflow(D), "fig2": fig2_checks(D), "fig3": fig3_coverage(D), "fig4": fig4_gaps(D)}
