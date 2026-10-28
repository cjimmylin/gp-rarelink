"""Figures for the interim paper. Every panel is drawn from the dict `analysis.interim_paper.data.load()`
returns; nothing is typed in by hand. Output: PNG files under reports/interim_paper/figures/.

Style follows the project's data-visualization rules: one validated palette (categorical slots in fixed
order; one-hue ramps for magnitude), thin marks, hairline solid grid, text in ink tokens never in series
color, a legend wherever two or more series appear, selective direct labels.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib import font_manager  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Patch  # noqa: E402

from .data import CONFIRMATORY, DISEASES, SHORT  # noqa: E402

# Palette (validated with the dataviz skill's validator, light mode)
BLUE, ORANGE, AQUA, YELLOW, MAGENTA, GREEN, VIOLET, RED = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"
CAT = [BLUE, ORANGE, AQUA, YELLOW, MAGENTA]
SEQ = ["#cde2fb", "#b7d3f6", "#9ec5f4", "#86b6ef", "#6da7ec", "#5598e7", "#3987e5", "#2a78d6", "#256abf", "#1c5cab", "#184f95", "#104281", "#0d366b"]
ORD4 = ["#86b6ef", "#5598e7", "#2a78d6", "#184f95"]  # ordinal ramp, validated --ordinal
ORD3 = ["#86b6ef", "#2a78d6", "#184f95"]
LIGHT_BLUE = "#9ec5f4"
INK, INK2, MUTED, GRID, AXIS, SURFACE = "#0b0b0b", "#52514e", "#898781", "#e1e0d9", "#c3c2b7", "#fcfcfb"
DEEMPH = "#c3c2b7"

OUT = Path(__file__).resolve().parents[2] / "reports/interim_paper/figures"


def _font():
    names = {f.name for f in font_manager.fontManager.ttflist}
    for cand in ("Inter", "Inter Display", "DejaVu Sans"):
        if cand in names:
            return cand
    return "DejaVu Sans"


plt.rcParams.update({
    "font.family": _font(), "font.size": 9, "axes.titlesize": 10, "axes.titleweight": "medium", "axes.labelsize": 9,
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "xtick.color": MUTED, "ytick.color": MUTED, "xtick.labelcolor": INK2,
    "ytick.labelcolor": INK2, "axes.spines.top": False, "axes.spines.right": False, "axes.grid": False,
    "grid.color": GRID, "grid.linewidth": 0.6, "grid.linestyle": "-", "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "savefig.facecolor": SURFACE, "savefig.dpi": 200, "savefig.bbox": "tight", "savefig.pad_inches": 0.15,
    "legend.frameon": False, "legend.fontsize": 8, "axes.titlelocation": "left", "axes.titlepad": 8,
})


def label(d):
    return SHORT[d] + ("*" if d == "ha20" else "")


def style(ax, grid="x"):
    ax.tick_params(length=0)
    ax.spines["left"].set_color(AXIS)
    ax.spines["bottom"].set_color(AXIS)
    if grid:
        ax.grid(True, axis=grid, zorder=0)
        ax.set_axisbelow(True)


def save(fig, name):
    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / f"{name}.png")
    plt.close(fig)
    return f"figures/{name}.png"


def pct(x):
    return 100 * x


# --------------------------------------------------------------------------------------------- Figure 1
def fig_overview(D):
    fig, ax = plt.subplots(figsize=(13, 6.4))
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 62)
    ax.axis("off")

    def box(x, y, w, h, title, lines, status="done", accent=BLUE):
        face = "#eaf2fc" if status == "done" else ("#fdf1ec" if status == "pending" else "#f3f3f1")
        edge = accent if status == "done" else (ORANGE if status == "pending" else MUTED)
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.4,rounding_size=1.2", linewidth=1.2,
                                    edgecolor=edge, facecolor=face, zorder=2))
        ax.text(x + 1.0, y + h - 1.4, title, fontsize=9, weight="semibold", color=INK, va="top", zorder=3)
        ax.text(x + 1.0, y + h - 4.3, "\n".join(lines), fontsize=7.0, color=INK2, va="top", zorder=3, linespacing=1.35)
        tag = {"done": "done", "pending": "waiting on people", "partial": "partly done"}[status]
        ax.text(x + w - 0.8, y + 0.8, tag, fontsize=6.8, color=edge, ha="right", va="bottom", style="italic", zorder=3)

    def arrow(x0, y0, x1, y1):
        ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.0, shrinkA=0, shrinkB=0), zorder=1)

    t = D["totals"]["all"]
    W, G = 18.2, 2.25
    xs = [1 + i * (W + G) for i in range(5)]
    box(xs[0], 44, W, 16, "1 Corpus", ["PubMed search + review references", "title/abstract + full-text screening",
                                       "open access only (D-32)", f"{t['papers']} papers extracted, 6 diseases"])
    box(xs[1], 44, W, 16, "2 Extraction", ["Claude Opus helper, one per paper", "frozen extract_v6, schema v5, rules v1",
                                           "disease, gene, checklist swapped (D-38)", f"{t['individual_rows']:,} individual rows"])
    box(xs[2], 44, W, 16, "3 Span check", ["every quote found verbatim", f"{t['claims_all']:,} values, 0 problems",
                                           "a value without a quote is not kept"])
    box(xs[3], 44, W, 16, "4 Gatekeeper v4", ["second Claude read per value", "entailed by the quote, for this person?",
                                              f"{t['model_claims']:,} claims judged", "a filter, not a measure"])
    box(xs[4], 44, W, 16, "5 Records", ["merge policy v4 (citations only)", "VariantValidator, MANE Select",
                                        "HPO + Mondo binding", f"{t['phenopackets']:,} phenopackets, all valid"])
    for i in range(4):
        arrow(xs[i] + W, 52, xs[i + 1], 52)
    ax.plot([1, 99], [40, 40], color=MUTED, lw=0.9, ls=(0, (4, 3)), zorder=1)
    ax.text(1, 40.8, "ground-truth boundary: nothing below is shown to steps 1–5 (pre-registration §5.3; enforced by a test)",
            fontsize=7.2, color=MUTED, va="bottom")
    W2, G2 = 22.9, 2.3
    x2 = [1 + i * (W2 + G2) for i in range(4)]
    box(x2[0], 24, W2, 13, "Reference snapshots", ["ClinVar release 2026-10-12, read 2026-10-19", "HPO annotations 2026-09-02",
                                                   "catalogues: Chen 2020, Grossi 2024", "OMIM: 12 entry pages frozen 2026-10-28 (D-42)"])
    box(x2[1], 24, W2, 13, "O2 Concordance harness", ["gene; HGVS (tier 1 allele, tier 2 protein);", "classification; phenotype profile",
                                                      "estimates with 95% CIs, no threshold (D-03)"])
    box(x2[2], 24, W2, 13, "O3 Gap candidates", [f"{t['gap_candidates']} tier-1 alleles absent from ClinVar,", "every value gatekeeper-supported",
                                                 f"{D['dossiers']['dossiers']} dossiers, {D['dossiers']['quotes']:,} quotes verbatim"], status="partial")
    box(x2[3], 24, W2, 13, "Completeness", ["recall vs a published catalogue", "HA20: Chen 2020; AxD: Grossi 2024 (D-39)",
                                            "no suitable open catalogue for 4 diseases"])
    arrow(xs[4] + W / 2, 44, xs[4] + W / 2, 40.2)
    ax.plot([x2[1] + W2 / 2, xs[4] + W / 2], [39.0, 39.0], color=MUTED, lw=0.9, zorder=1)
    ax.plot([xs[4] + W / 2, xs[4] + W / 2], [40.2, 39.0], color=MUTED, lw=0.9, zorder=1)
    for xx in (x2[1] + W2 / 2, x2[2] + W2 / 2, x2[3] + W2 / 2):
        arrow(xx, 39.0, xx, 37.4)
    arrow(x2[0] + W2, 27, x2[1], 27)
    ax.text(x2[0] + W2 + G2 / 2, 28.2, "ground truth", fontsize=6.4, color=MUTED, ha="center", va="bottom")
    box(x2[0], 3, W2, 16, "O1 Human audit", ["250 supported claims, drawn by seed", "two blinded raters, then a tie-break",
                                             "rating pages built, not yet shared", "pass: at most 4 unsupported (D-02)"], status="pending")
    box(x2[1], 3, W2, 16, "Panel adjudication (O3, O5)", ["ACMG/AMP review of gap candidates", "adjudication page built, not shared",
                                                          "expert-minutes per record logged there", "then ClinVar / OMIM drafts (D-13)"], status="pending")
    box(x2[2], 3, W2, 16, "O4 Bias arm", ["4 open comparators fetched", "a person lists cohort frequencies first",
                                          "memorization probe done, both models"], status="partial")
    box(x2[3], 3, W2, 16, "O5 Open-weight comparison", ["DeepSeek-V4.1-Flash, same frozen files", "HA20 + SSADH extracted and judged",
                                                        "blinded audit waits on D-11"], status="partial")
    fig.text(0.01, 0.005, "Blue boxes: done. Orange: waiting on people. Gray edge: partly done.", fontsize=7.2, color=MUTED)
    return save(fig, "fig1_overview")


# --------------------------------------------------------------------------------------------- Figure 2
def fig_corpus(D):
    stages = [("Records screened", lambda c, r: c["manifest_rows"]), ("In corpus after title/abstract", lambda c, r: c["in_corpus"]),
              ("Open full text", lambda c, r: c["fulltext"]), ("Extracted", lambda c, r: r["papers"])]
    fig, ax = plt.subplots(figsize=(8.5, 4.6))
    n = len(stages)
    h = 0.17
    ys = range(len(DISEASES))
    for i, (name, f) in enumerate(stages):
        vals = [f(D["coverage"][d], D["run"][d]) for d in DISEASES]
        yy = [y + (i - (n - 1) / 2) * h for y in ys]
        ax.barh(yy, vals, height=h * 0.92, color=ORD4[i], label=name, zorder=2)
        for y, v in zip(yy, vals):
            ax.text(v + 8, y, f"{v:,}", va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(list(ys))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlabel("papers")
    ax.set_xlim(0, max(D["coverage"][d]["manifest_rows"] for d in DISEASES) * 1.12)
    style(ax, "x")
    ax.legend(loc="lower right", ncol=1)
    ax.set_title("Corpus funnel per disease (open access only; HA20 corpus reused from the pilot, not full-text screened)")
    fig.text(0.01, -0.02, "*development disease (D-18). Source: analysis/corpus/coverage_2026-10-20.json; run summaries.", fontsize=7.2, color=MUTED)
    return save(fig, "fig2_corpus")


# --------------------------------------------------------------------------------------------- Figure 3
def fig_gatekeeper(D):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2), gridspec_kw={"width_ratios": [1.25, 0.8, 1.3], "wspace": 0.42})
    ax = axes[0]
    rowsy = DISEASES + ["five", "all"]
    for i, d in enumerate(rowsy):
        if d in ("five", "all"):
            k = D["totals"][d]["unsupported"]; n = D["totals"][d]["model_claims"]
            from .stats import clopper_pearson
            lo, hi = clopper_pearson(k, n)
            share = k / n
            face, edge = (INK2 if d == "five" else SURFACE), INK2
        else:
            r = D["run"][d]["unsupported_or_not_found"]
            share, (lo, hi) = r["share"], r["ci95"]
            face, edge = (SURFACE if d == "ha20" else BLUE), BLUE
        ax.plot([pct(lo), pct(hi)], [i, i], color=edge, lw=1.6, zorder=2)
        ax.scatter([pct(share)], [i], s=46, facecolor=face, edgecolor=edge, linewidth=1.4, zorder=3)
        ax.text(pct(hi) + 0.03, i, f"{pct(share):.2f}%", va="center", fontsize=7.4, color=INK2)
    ax.set_yticks(range(len(rowsy)))
    ax.set_yticklabels([label(d) if d in SHORT else {"five": "Five confirmatory", "all": "All six"}[d] for d in rowsy])
    ax.invert_yaxis()
    ax.axvline(2.0, color=DEEMPH, lw=1, zorder=1)
    ax.text(1.95, len(rowsy) - 1.0, "2%: the O1 target, for scale", fontsize=6.8, color=MUTED, ha="right", va="center")
    ax.set_xlim(0, 2.3)
    ax.set_xlabel("claims judged unsupported or span not found (%), exact 95% CI")
    ax.set_title("A  Gatekeeper v4: unsupported share of model claims")
    style(ax, "x")

    ax = axes[1]
    vals = [D["run"][d]["top3_share_of_unsupported"] for d in DISEASES]
    ax.barh(range(len(DISEASES)), [pct(v) for v in vals], height=0.55, color=[SURFACE if d == "ha20" else BLUE for d in DISEASES],
            edgecolor=BLUE, linewidth=1.2, zorder=2)
    for i, (d, v) in enumerate(zip(DISEASES, vals)):
        ax.text(pct(v) + 1.5, i, f"{pct(v):.0f}%  ({D['run'][d]['papers_with_any_unsupported']} of {D['run'][d]['papers']} papers)",
                va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 125)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share held by the 3 worst papers (%)")
    ax.set_title("B  Concentration in a few papers")
    style(ax, "x")

    ax = axes[2]
    cats = [("this_person", "this person"), ("named_group", "a named group"), ("cohort_general", "the cohort in general"),
            ("other_person", "another person"), ("unclear", "unclear")]
    for i, d in enumerate(DISEASES):
        ab = D["run"][d]["unsupported_by_about"]
        total = sum(ab.values()) or 1
        left = 0
        for j, (k, nm) in enumerate(cats):
            v = ab.get(k, 0)
            w = 100 * v / total
            ax.barh(i, w, left=left, height=0.55, color=CAT[j], edgecolor=SURFACE, linewidth=1.2, zorder=2, label=nm if i == 0 else None)
            if w >= 9:
                ax.text(left + w / 2, i, str(v), ha="center", va="center", fontsize=7, color="#ffffff" if j not in (3,) else INK)
            left += w
        ax.text(101, i, f"n={total}", va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 112)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of unsupported claims (%)")
    ax.set_title("C  Whom the cited quote was about")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    style(ax, "x")
    fig.text(0.01, -0.2, "*development disease. Hollow marker = HA20. Source: analysis/six_disease/run_summary_2026-10-20.json. The gatekeeper's verdicts are not an error rate; the pre-registered measure is the human audit (O1), not yet rated.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig3_gatekeeper")


# --------------------------------------------------------------------------------------------- Figure 4
def fig_repeat(D):
    measures = [("checklist_agreement", "Checklist status agreement (cells)"), ("variant_key_jaccard", "Variants, folded keys (Jaccard)"),
                ("variant_jaccard", "Variants, strings (Jaccard)"), ("feature_jaccard_label_free", "Free-text features, label-free (Jaccard)")]
    fig, axes = plt.subplots(1, 4, figsize=(12, 3.4), sharey=True, gridspec_kw={"wspace": 0.12})
    for ax, (key, title) in zip(axes, measures):
        for i, d in enumerate(DISEASES):
            v = D["repeat"][d][key]
            ax.scatter([v], [i], s=46, facecolor=SURFACE if d == "ha20" else BLUE, edgecolor=BLUE, linewidth=1.4, zorder=3)
            ax.text(1.07, i, f"{v:.2f}", ha="left", va="center", fontsize=6.8, color=INK2)
        if "variant" in key:
            ax.axvline(0.9, color=DEEMPH, lw=1, zorder=1)
            ax.text(0.885, 5.45, "0.9 pilot guide", fontsize=6.4, color=MUTED, ha="right", va="center")
        ax.set_ylim(5.75, -0.6)
        ax.set_xlim(0.3, 1.2)
        ax.set_xticks([0.4, 0.6, 0.8, 1.0])
        ax.set_title(title, fontsize=8.6)
        style(ax, "x")
    axes[0].set_yticks(range(len(DISEASES)))
    axes[0].set_yticklabels([f"{label(d)} ({D['repeat'][d]['papers_compared']} papers)" for d in DISEASES])
    fig.text(0.01, -0.08, f"Run-to-run repeat: a 10% sample of papers per disease (seed {D['repeat_seed']}) re-extracted with the same frozen files. Hollow = HA20 (development disease). Source: analysis/six_disease/repeat_agreement_2026-10-20.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig4_repeat")


# --------------------------------------------------------------------------------------------- Figure 5
def fig_records(D):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9), gridspec_kw={"width_ratios": [1.25, 1, 1.1], "wspace": 0.55})
    ax = axes[0]
    for i, d in enumerate(DISEASES):
        s = D["stage4"][d]
        wv, wo = s["identities_with_target_variant"], s["identities"] - s["identities_with_target_variant"]
        ax.barh(i, wv, height=0.55, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="with a target-gene variant" if i == 0 else None)
        ax.barh(i, wo, left=wv, height=0.55, color=LIGHT_BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="without (relatives, cited patients)" if i == 0 else None)
        ax.text(s["identities"] + 10, i, f"{s['identities']:,} ({s['individual_rows']:,} rows; {s['merged_pairs']} merges)", va="center", fontsize=7, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 1400)
    ax.set_xticks([0, 250, 500, 750])
    ax.set_xlabel("deduplicated identities (= phenopackets)")
    ax.set_title("A  Identities after merging")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    style(ax, "x")

    ax = axes[1]
    for i, d in enumerate(DISEASES):
        sc = D["stage4"][d]["status_counts"]
        ok = sc["normalized"] + sc["corrected"]
        bad = sc["not_normalized"] + sc["unresolvable"]
        tot = ok + bad
        ax.barh(i, 100 * ok / tot, height=0.55, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="normalized (incl. corrected query)" if i == 0 else None)
        ax.barh(i, 100 * bad / tot, left=100 * ok / tot, height=0.55, color=ORANGE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="not normalized or unresolvable" if i == 0 else None)
        ax.text(101, i, f"{100 * ok / tot:.0f}% of {tot}; +{sc['protein_only']} protein-only", va="center", fontsize=7, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 160)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("distinct cDNA descriptions (%)")
    ax.set_title("B  VariantValidator normalization")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    style(ax, "x")

    ax = axes[2]
    for i, d in enumerate(DISEASES):
        s = D["stage4"][d]
        ax.barh(i, s["features_observed"], height=0.55, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="observed" if i == 0 else None)
        ax.barh(i, s["features_excluded"], left=s["features_observed"], height=0.55, color=ORANGE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="excluded" if i == 0 else None)
        ax.text(s["features_observed"] + s["features_excluded"] + 60, i, f"{100 * s['feature_share_bound']:.0f}% of rows bound", va="center", fontsize=7, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 7500)
    ax.set_xticks([0, 2000, 4000, 6000])
    ax.set_xlabel("HPO terms in the phenopackets")
    ax.set_title("C  Phenotype terms, three-state")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=2)
    style(ax, "x")
    fig.text(0.01, -0.3, "*development disease. Source: analysis/six_disease/stage4_summary_2026-10-20.json. 'Not reported' terms carry no row and are not shown.", fontsize=7.2, color=MUTED)
    return save(fig, "fig5_records")


# --------------------------------------------------------------------------------------------- Figure 6
def _ci_panel(ax, items, title, xlabel, two=False):
    """items: list of (ylabel, [(share, lo, hi, k, n, color, hollow), ...])"""
    for i, (yl, series) in enumerate(items):
        off = [-0.17, 0.17] if len(series) == 2 else [0]
        for (share, lo, hi, k, n, color, hollow), o in zip(series, off):
            if share is None:
                ax.text(2, i + o, "undefined (no reference pairs)", fontsize=6.8, color=MUTED, va="center")
                continue
            ax.plot([pct(lo), pct(hi)], [i + o, i + o], color=color, lw=1.6, zorder=2)
            ax.scatter([pct(share)], [i + o], s=40, facecolor=SURFACE if hollow else color, edgecolor=color, linewidth=1.3, zorder=3)
            ax.text(103, i + o, f"{k}/{n}", fontsize=6.8, color=INK2, va="center")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([x[0] for x in items])
    ax.invert_yaxis()
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    style(ax, "x")


def fig_concordance(D):
    fig, axes = plt.subplots(2, 2, figsize=(11, 7), gridspec_kw={"wspace": 0.42, "hspace": 0.5})
    o2 = {d: D["o2"][d]["all_papers"] for d in DISEASES}

    def ser(d, key, color):
        r = o2[d][key]
        if not r or r.get("share") is None:
            return (None, None, None, 0, 0, color, d == "ha20")
        return (r["share"], r["ci95"][0], r["ci95"][1], r["k"], r["n"], color, d == "ha20")

    _ci_panel(axes[0, 0], [(label(d), [ser(d, "hgvs_recall_tier1", BLUE), ser(d, "hgvs_recall_tier12", ORANGE)]) for d in DISEASES],
              "A  HGVS recall against ClinVar's citations (§7.2.2)", "reference (paper, variant) pairs recovered (%)")
    axes[0, 0].legend(handles=[Line2D([], [], marker="o", color=BLUE, lw=0, label="tier 1: same GRCh38 allele"),
                               Line2D([], [], marker="o", color=ORANGE, lw=0, label="tiers 1+2: or same protein change")], loc="upper right", fontsize=7)
    _ci_panel(axes[0, 1], [(label(d), [ser(d, "overlap_tier1", BLUE)]) for d in DISEASES],
              "B  Overlap: extracted tier-1 alleles present in ClinVar", "share of extracted alleles (%); not precision")
    _ci_panel(axes[1, 0], [(label(d), [ser(d, "classification_agreement_among_stated", BLUE)]) for d in DISEASES],
              "C  Classification agreement where authors state one", "authors' P/LP, VUS, B/LB vs ClinVar aggregate (%)")
    ph = []
    for d in DISEASES:
        r = D["o2"][d]["phenotype_7_2_4b"]["annotation_recall"]
        ph.append((label(d), [(r["share"], r["ci95"][0], r["ci95"][1], r["k"], r["n"], BLUE, d == "ha20")]))
    _ci_panel(axes[1, 1], ph, "D  HPO annotation recall (phenotype.hpoa terms seen in ≥1 person)", "annotated terms recovered (%), ontology-aware")
    fig.text(0.01, 0.0, f"Wilson 95% intervals. Hollow = HA20 (development disease). ClinVar release {D['o2']['ha20']['clinvar_variant_summary_last_modified'][:16]}, snapshot {D['o2']['ha20']['snapshot_date']}; the OMIM half is in Figure 11. No pass/fail threshold (D-03). Source: analysis/six_disease/o2/o2_<d>.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig6_concordance")


# --------------------------------------------------------------------------------------------- Figure 7
def fig_gaps(D):
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 3.9), gridspec_kw={"width_ratios": [1.2, 1.0, 0.9], "wspace": 0.75})
    ax = axes[0]
    for i, d in enumerate(DISEASES):
        g = D["gaps"][d]
        present = g["tier1_alleles"] - g["absent_from_clinvar_before_gatekeeper"]
        cand = g["gap_candidates"]
        failed = g["absent_but_every_row_failed_gatekeeper"]
        ax.barh(i, present, height=0.55, color=LIGHT_BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="present in ClinVar" if i == 0 else None)
        ax.barh(i, cand, left=present, height=0.55, color=BLUE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="gap candidate (absent; values supported)" if i == 0 else None)
        ax.barh(i, failed, left=present + cand, height=0.55, color=ORANGE, edgecolor=SURFACE, linewidth=1.2, zorder=2, label="absent, but every row failed the gatekeeper" if i == 0 else None)
        ax.text(g["tier1_alleles"] + 3, i, f"{cand} of {g['tier1_alleles']}", va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 175)
    ax.set_xticks([0, 50, 100, 150])
    ax.set_xlabel("distinct tier-1 alleles (GRCh38) extracted")
    ax.set_title("A  Gap candidates among extracted alleles")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1)
    style(ax, "x")

    ax = axes[1]
    flags = sorted(D["triage"]["by_flag"].items(), key=lambda x: -x[1])
    names = {"possible_same_person": "possible same person twice", "other_variant": "another variant in the same person",
             "carriers_not_attached": "carriers not attached to a person", "review_only": "evidence only from reviews",
             "protein_mismatch": "stated protein differs from prediction", "notation_conflict": "notation conflict",
             "mosaic_or_somatic": "mosaic or somatic", "possible_existing_record": "cites a database accession"}
    ax.barh(range(len(flags)), [v for _, v in flags], height=0.55, color=BLUE, zorder=2)
    for i, (k, v) in enumerate(flags):
        ax.text(v + 1.5, i, str(v), va="center", fontsize=7.2, color=INK2)
    ax.set_yticks(range(len(flags)))
    ax.set_yticklabels([names.get(k, k) for k, _ in flags], fontsize=7.6)
    ax.invert_yaxis()
    ax.set_xlim(0, 95)
    ax.set_xlabel(f"candidates flagged (of {D['triage']['candidates']}; {D['triage']['with_any_flag']} carry ≥1 flag)")
    ax.set_title("B  Triage flags for the panel (pointers, not verdicts)")
    style(ax, "x")

    ax = axes[2]
    for i, d in enumerate(DISEASES):
        bp = D["gaps"][d]["gap_candidates_by_papers"]
        left = 0
        for j, (k, nm) in enumerate((("1", "1 paper"), ("2", "2 papers"), ("3", "3+ papers"))):
            v = bp.get(k, 0)
            ax.barh(i, v, left=left, height=0.55, color=ORD3[j], edgecolor=SURFACE, linewidth=1.2, zorder=2, label=nm if i == 0 else None)
            if v >= 6:
                ax.text(left + v / 2, i, str(v), ha="center", va="center", fontsize=7, color="#ffffff" if j > 0 else INK)
            left += v
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlim(0, 95)
    ax.set_xlabel("gap candidates")
    ax.set_title("C  How many papers report each candidate")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    style(ax, "x")
    fig.text(0.01, -0.3, f"*development disease. ClinVar snapshot {D['gaps_meta']['snapshot']}; all {D['recheck']['candidates_checked']} candidates still absent in the {D['recheck']['snapshot']} re-check; all but one absent from OMIM's allelic variants (D-42), and that one withdrawn (D-43). Sources: adjudication/o3_gaps/summary.json, triage_summary.json, recheck_2026-10-21.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig7_gaps")


# --------------------------------------------------------------------------------------------- Figure 8
def fig_openweight(D):
    dz = ["ha20", "ssadh"]
    fig, axes = plt.subplots(1, 4, figsize=(12.5, 3.4), gridspec_kw={"wspace": 0.45})

    def grouped(ax, vals_c, vals_o, title, ylabel, fmt, ylim=None):
        x = range(len(dz))
        w = 0.32
        bc = ax.bar([i - w / 2 for i in x], vals_c, width=w, color=BLUE, edgecolor=SURFACE, linewidth=1.2, label="Claude (pv1)", zorder=2)
        bo = ax.bar([i + w / 2 for i in x], vals_o, width=w, color=ORANGE, edgecolor=SURFACE, linewidth=1.2, label="DeepSeek-V4.1-Flash (ow)", zorder=2)
        for bars in (bc, bo):
            for b in bars:
                ax.text(b.get_x() + b.get_width() / 2, b.get_height() * 1.02 + (ylim or max(vals_c + vals_o)) * 0.005, fmt(b.get_height()), ha="center", va="bottom", fontsize=7.2, color=INK2)
        ax.set_xticks(list(x))
        ax.set_xticklabels([label(d) for d in dz])
        ax.set_ylabel(ylabel)
        ax.set_title(title, fontsize=8.8)
        if ylim:
            ax.set_ylim(0, ylim)
        style(ax, "y")
        ax.spines["bottom"].set_visible(True)

    grouped(axes[0], [pct(D["ow"][d]["span"]["claude"]["span_not_found_rate"]) for d in dz], [pct(D["ow"][d]["span"]["open"]["span_not_found_rate"]) for d in dz],
            "A  Span not found (all values)", "% of asserted values", lambda v: f"{v:.2f}%", ylim=5)
    grouped(axes[1], [pct(D["ow_gk"][d]["claude"]["unsupported"]["share"]) for d in dz], [pct(D["ow_gk"][d]["open"]["unsupported"]["share"]) for d in dz],
            "B  Judged unsupported by gatekeeper v4", "% of model claims (same Claude judge)", lambda v: f"{v:.2f}%", ylim=10.5)
    grouped(axes[2], [D["ow"][d]["cost_usd"]["claude_median_per_paper"] for d in dz], [D["ow"][d]["cost_usd"]["open_median_per_paper"] for d in dz],
            "C  Cost per paper, median", "USD (Claude: estimate; open: host-reported)", lambda v: f"\\${v:.2f}", ylim=1.45)
    grouped(axes[3], [D["ow"][d]["wall_seconds"]["claude_median"] / 60 for d in dz], [D["ow"][d]["wall_seconds"]["open_median"] / 60 for d in dz],
            "D  Wall-clock per paper, median", "minutes", lambda v: f"{v:.1f}", ylim=25)
    axes[0].legend(loc="upper left", fontsize=7.2)
    fig.text(0.01, -0.1, "*development disease. Same papers, launch prompt, frozen instruction files and scoring on both sides; the scaffolds differ (no shell for the open-weight loop; no repair passes). Sources: analysis/openweight/summary_<d>.json, gatekeeper_compare.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig8_openweight")


# --------------------------------------------------------------------------------------------- Figure 9
def fig_memorization(D):
    strata = [("after", "after cutoff (10 papers)"), ("recent", "recent, 2024-07 to 2026-06 (51)"), ("older", "older (119)")]
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.4), gridspec_kw={"width_ratios": [1.5, 1], "wspace": 0.35})
    ax = axes[0]
    rowsy = []
    for s, nm in strata:
        for m, mn in (("claude", "Claude"), ("open", "DeepSeek")):
            rowsy.append((s, nm, m, mn))
    for i, (s, nm, m, mn) in enumerate(rowsy):
        b = D["mem"][m]["by_stratum"][s]
        tot = b["cb_specific"] + b["cb_guess"] + b["cb_none"]
        left = 0
        for j, (k, lab) in enumerate((("cb_specific", "claims specific recall"), ("cb_guess", "marked as a guess"), ("cb_none", "no recall"))):
            v = b[k]
            w = 100 * v / tot
            ax.barh(i, w, left=left, height=0.6, color=[ORD3[2], ORD3[1], ORD3[0]][j], edgecolor=SURFACE, linewidth=1.2, zorder=2, label=lab if i == 0 else None)
            if w >= 7:
                ax.text(left + w / 2, i, str(v), ha="center", va="center", fontsize=7, color="#ffffff" if j < 2 else INK)
            left += w
    ax.set_yticks(range(len(rowsy)))
    ax.set_yticklabels([f"{nm} — {mn}" for _, nm, _, mn in rowsy], fontsize=7.6)
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("closed-book answers (%)")
    ax.set_title("A  Closed-book recall from PMID, title and year")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=3)
    style(ax, "x")

    ax = axes[1]
    x = range(len(strata))
    w = 0.32
    for off, m, color, lab in ((-w / 2, "claude", BLUE, "Claude"), (w / 2, "open", ORANGE, "DeepSeek-V4.1-Flash")):
        vals = [D["mem"][m]["by_stratum"][s]["cp_mean_rougeL_f1"] for s, _ in strata]
        bars = ax.bar([i + off for i in x], vals, width=w, color=color, edgecolor=SURFACE, linewidth=1.2, label=lab, zorder=2)
        for b in bars:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 0.004, f"{b.get_height():.2f}", ha="center", va="bottom", fontsize=7, color=INK2)
    ax.set_xticks(list(x))
    ax.set_xticklabels(["after", "recent", "older"])
    ax.set_ylim(0, 0.3)
    ax.set_ylabel("mean word-level ROUGE-L F1")
    ax.set_title("B  Guided completion of a 50-word opening")
    ax.legend(loc="upper right", fontsize=7.2)
    style(ax, "y")
    ax.spines["bottom"].set_visible(True)
    fig.text(0.01, -0.3, "Strata are set from Claude's documented cutoff (June 2026); the open-weight checkpoint's cutoff is not documented here. Scored against the full-text extraction, never ClinVar. Sources: analysis/bias/memorization/scores_summary.json, openweight_scores_summary.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig9_memorization")


# --------------------------------------------------------------------------------------------- Figure 10
def fig_budget(D):
    b = D["budget"]
    lines = b["lines"] + [{"n": "—", "name": "Not yet assigned to a line (setup, documents, gaps between runs)", "requested": 0, "spent": b["unassigned"]}]
    fig, ax = plt.subplots(figsize=(10, 3.9))
    for i, L in enumerate(lines):
        if L["requested"]:
            ax.barh(i, L["requested"], height=0.55, color="#e8eef6", zorder=1)
        ax.barh(i, L["spent"], height=0.55, color=BLUE, zorder=2)
        txt = f"\\${L['spent']:,.0f}" + (f" of \\${L['requested']:,.0f}  ({100 * L['spent'] / L['requested']:.1f}%)" if L["requested"] else "")
        ax.text(max(L["spent"], L["requested"]) + 80, i, txt, va="center", fontsize=7.4, color=INK2)
    ax.set_yticks(range(len(lines)))
    ax.set_yticklabels([f"{L['n']}  {L['name'] if len(L['name']) <= 46 else L['name'][:45] + '…'}" for L in lines], fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlim(0, 11500)
    ax.set_xlabel("USD (requested line as the light track; spent as the filled bar)")
    ax.set_title(f"Spend by budget line, estimated from this session's cost readings (\\${b['total']:,.2f} at {b['reading_at']})")
    style(ax, "x")
    fig.text(0.01, -0.06, "Estimates, not billing figures: list-price readings that sometimes freeze; whether the session runs on the funded account is open (D-15). OpenRouter spend (D-10, USD 16–20) is billed outside the award and not counted. Source: analysis/cost/spend_segments.csv via budget_lines.py.",
             fontsize=7.2, color=MUTED)
    return save(fig, "fig10_budget")


# ============================================================================================= Supplementary
def figS_concentration(D):
    fig, axes = plt.subplots(2, 3, figsize=(10.5, 5.6), gridspec_kw={"wspace": 0.3, "hspace": 0.5})
    for ax, d in zip(axes.flat, DISEASES):
        bp = D["gk"][d]["by_paper"]
        counts = sorted([v.get("unsupported", 0) + v.get("span_not_found", 0) for v in bp.values()], reverse=True)
        total = sum(counts) or 1
        cum, acc = [0], 0
        for c in counts:
            acc += c
            cum.append(100 * acc / total)
        ax.plot(range(len(cum)), cum, color=BLUE, lw=2, zorder=3)
        ax.scatter([3], [cum[3] if len(cum) > 3 else cum[-1]], s=40, facecolor=SURFACE, edgecolor=BLUE, linewidth=1.4, zorder=4)
        ax.text(3.6, cum[3] - 6 if len(cum) > 3 else 90, f"3 papers: {cum[3] if len(cum) > 3 else cum[-1]:.0f}%", fontsize=7.2, color=INK2)
        ax.set_xlim(0, len(counts))
        ax.set_ylim(0, 102)
        ax.set_title(f"{label(d)}: {total} unsupported claims in {D['run'][d]['papers']} papers", fontsize=8.6)
        ax.set_xlabel("papers, ranked by unsupported claims")
        ax.set_ylabel("cumulative share (%)")
        style(ax, "both")
    fig.text(0.01, -0.02, "*development disease. Source: data/extracted/<d>/pv1-<d>/gatekeeper_v4_summary.json (by_paper).", fontsize=7.2, color=MUTED)
    return save(fig, "figS1_concentration")


def figS_variant_spectrum(D):
    classes = ["missense", "nonsense", "frameshift", "splice / intronic", "in-frame indel", "start loss", "synonymous", "structural / copy-number",
               "frameshift or nonsense (unplaced)", "other", "not placed"]
    import numpy as np
    M = np.array([[D["pp"][d]["variant_classes"].get(c, 0) for c in classes] for d in DISEASES], dtype=float)
    share = 100 * M / M.sum(axis=1, keepdims=True)
    fig, ax = plt.subplots(figsize=(11, 3.6))
    im = ax.imshow(share, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("blue", [SURFACE] + SEQ[:11]), vmin=0, vmax=80, aspect="auto")
    for i in range(len(DISEASES)):
        for j in range(len(classes)):
            v = M[i, j]
            if v:
                ax.text(j, i, f"{int(v)}\n{share[i, j]:.0f}%", ha="center", va="center", fontsize=6.6, color="#ffffff" if share[i, j] > 45 else INK)
    ax.set_xticks(range(len(classes)))
    ax.set_xticklabels(classes, rotation=35, ha="right", fontsize=7.4)
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([f"{label(d)} (n={int(M[i].sum())})" for i, d in enumerate(DISEASES)])
    ax.set_title("Variant interpretations in the phenopackets, by coarse class (count and row share)")
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    cb = fig.colorbar(im, ax=ax, fraction=0.025, pad=0.02)
    cb.set_label("row share (%)", fontsize=7.6)
    cb.outline.set_visible(False)
    fig.text(0.01, -0.3, "Class read from the MANE protein and cDNA HGVS where VariantValidator placed the variant, else from the paper's label. One count per (identity, variant). Source: data/extracted/<d>/pv1-<d>/phenopackets/.", fontsize=7.2, color=MUTED)
    return save(fig, "figS2_variant_spectrum")


def figS_top_terms(D):
    fig, axes = plt.subplots(2, 3, figsize=(13, 7.2), gridspec_kw={"wspace": 0.95, "hspace": 0.45})
    for ax, d in zip(axes.flat, DISEASES):
        top = D["pp"][d]["top_observed"]
        n = D["pp"][d]["n"]
        for i, (tid, lab, o, e) in enumerate(top):
            ax.barh(i - 0.17, 100 * o / n, height=0.32, color=BLUE, zorder=2, label="observed" if i == 0 else None)
            ax.barh(i + 0.17, 100 * e / n, height=0.32, color=ORANGE, zorder=2, label="excluded" if i == 0 else None)
            ax.text(100 * o / n + 1, i - 0.17, str(o), va="center", fontsize=6.4, color=INK2)
            if e:
                ax.text(100 * e / n + 1, i + 0.17, str(e), va="center", fontsize=6.4, color=INK2)
        ax.set_yticks(range(len(top)))
        ax.set_yticklabels([lab if len(lab) <= 38 else lab[:37] + "…" for _, lab, _, _ in top], fontsize=7.2)
        ax.invert_yaxis()
        ax.set_xlim(0, 100)
        ax.set_xlabel(f"% of {n} identities")
        ax.set_title(f"{label(d)}", fontsize=9)
        style(ax, "x")
        if d == "ha20":
            ax.legend(loc="lower right", fontsize=7)
    fig.text(0.01, 0.0, "*development disease. The ten HPO terms most often observed per disease, with the count excluded for the same term. Terms not reported for a person carry no row. Source: phenopackets.", fontsize=7.2, color=MUTED)
    return save(fig, "figS3_top_terms")


def figS_coverage(D):
    import numpy as np
    fields = sorted({k for d in DISEASES for k in D["o2"][d]["coverage_7_2_5"]})
    fields = [f for f in fields if f.startswith(("individuals.", "variants."))]
    M = np.array([[100 * D["o2"][d]["coverage_7_2_5"].get(f, 0) for d in DISEASES] for f in fields])
    fig, ax = plt.subplots(figsize=(7.5, 0.28 * len(fields) + 1.4))
    im = ax.imshow(M, cmap=matplotlib.colors.LinearSegmentedColormap.from_list("blue", [SURFACE] + SEQ[:11]), vmin=0, vmax=100, aspect="auto")
    for i in range(len(fields)):
        for j in range(len(DISEASES)):
            ax.text(j, i, f"{M[i, j]:.0f}", ha="center", va="center", fontsize=6.6, color="#ffffff" if M[i, j] > 55 else INK)
    ax.set_xticks(range(len(DISEASES)))
    ax.set_xticklabels([label(d) for d in DISEASES])
    ax.set_yticks(range(len(fields)))
    ax.set_yticklabels([f.replace("individuals.", "ind. ").replace("variants.", "var. ") for f in fields], fontsize=7)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    ax.set_title("Field coverage: share of rows with an asserted value rather than 'not reported' (%)", fontsize=9)
    cb = fig.colorbar(im, ax=ax, fraction=0.04, pad=0.02)
    cb.outline.set_visible(False)
    fig.text(0.01, 0.0, "*development disease. Pre-registration §7.2.5. Source: analysis/six_disease/o2/o2_<d>.json (coverage_7_2_5).", fontsize=7.2, color=MUTED)
    return save(fig, "figS4_coverage")


def figS_completeness(D):
    fig, ax = plt.subplots(figsize=(8, 2.8))
    items = []
    for d in ("ha20", "axd"):
        c = D["completeness"][d]
        for key, nm in (("recall_restricted_primary", "restricted (source paper in corpus), primary papers"), ("recall_unrestricted_primary", "unrestricted (all catalogue variants with a PMID)")):
            r = c[key]
            items.append((f"{label(d)}: {nm}", r["share"], r["ci95"][0], r["ci95"][1], r["k"], r["n"], d))
    for i, (yl, s, lo, hi, k, n, d) in enumerate(items):
        ax.plot([pct(lo), pct(hi)], [i, i], color=BLUE, lw=1.6, zorder=2)
        ax.scatter([pct(s)], [i], s=44, facecolor=SURFACE if d == "ha20" else BLUE, edgecolor=BLUE, linewidth=1.4, zorder=3)
        ax.text(104, i, f"{k}/{n}", fontsize=7.2, color=INK2, va="center")
    ax.set_yticks(range(len(items)))
    ax.set_yticklabels([x[0] for x in items], fontsize=7.8)
    ax.invert_yaxis()
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("catalogue variants recovered by extraction (%), Wilson 95% CI")
    ax.set_title("Completeness against published variant catalogues (§7.2.7; HA20 Chen 2020, AxD Grossi 2024 added after extraction, D-39)")
    style(ax, "x")
    fig.text(0.01, -0.1, "*development disease. Four diseases have no suitable open catalogue and report no figure. Source: analysis/six_disease/completeness_pv1-<d>.json.", fontsize=7.2, color=MUTED)
    return save(fig, "figS5_completeness")


def figS_gpsea(D):
    g = D["gpsea"]["diseases"]["danon"]["analyses"]
    rows_ = []
    for an, title, keys in (("sex", "Sex (hemizygous males vs heterozygous females)", ("group_MALE", "group_FEMALE")),
                            ("truncating_vs_missense", "Truncating vs missense", ("group_truncating", "group_missense"))):
        for t in g[an]["top"][:5]:
            a, b = t[keys[0]], t[keys[1]]
            rows_.append((f"{title}: {t['hpo_label']}", a, b, t["p_bh"], keys))
    fig, ax = plt.subplots(figsize=(9, 4.2))
    for i, (yl, a, b, pbh, keys) in enumerate(rows_):
        for v, color, off, lab in ((a, BLUE, -0.15, keys[0].replace("group_", "")), (b, ORANGE, 0.15, keys[1].replace("group_", ""))):
            k, n = map(int, v.split("/"))
            ax.scatter([100 * k / n], [i + off], s=42, facecolor=color, edgecolor=SURFACE, linewidth=1.2, zorder=3)
            ax.text(100 * k / n + 1.5, i + off, v, fontsize=6.6, color=INK2, va="center")
        ax.text(123, i, f"p_BH = {pbh:.3f}" + (" *" if pbh < 0.05 else ""), fontsize=7.2, color=INK if pbh < 0.05 else MUTED, va="center")
    ax.set_yticks(range(len(rows_)))
    ax.set_yticklabels([r[0] for r in rows_], fontsize=7.6)
    ax.invert_yaxis()
    ax.set_xlim(0, 145)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xlabel("share of individuals with the term observed, among those assessed (%)")
    ax.set_title(f"Danon disease, exploratory GPSEA tests ({D['gpsea']['diseases']['danon']['patients']} individuals with a placed variant and ≥1 phenotype)")
    ax.legend(handles=[Line2D([], [], marker="o", color=BLUE, lw=0, label="first group (male / truncating)"),
                       Line2D([], [], marker="o", color=ORANGE, lw=0, label="second group (female / missense)")], loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=7)
    style(ax, "x")
    fig.text(0.01, -0.3, "Fisher exact tests with Benjamini–Hochberg correction; * p_BH < 0.05. Zygosity for untyped calls is an analysis assumption (hemizygous males, heterozygous females). A reproduction check, not independent replication. Source: analysis/exploratory/gpsea/results/summary.json.",
             fontsize=7.2, color=MUTED)
    return save(fig, "figS6_gpsea_danon")


def figS_misses(D):
    fig, axes = plt.subplots(2, 3, figsize=(12, 5.4), gridspec_kw={"wspace": 0.6, "hspace": 0.55})
    for ax, d in zip(axes.flat, DISEASES):
        mm = D["o2_misses_by_paper"].get(d, [])[:5]
        tot = sum(n for _, n in D["o2_misses_by_paper"].get(d, []))
        ax.barh(range(len(mm)), [n for _, n in mm], height=0.55, color=BLUE, zorder=2)
        for i, (p, n) in enumerate(mm):
            ax.text(n + max(1, tot * 0.02), i, str(n), va="center", fontsize=7, color=INK2)
        ax.set_yticks(range(len(mm)))
        ax.set_yticklabels([f"PMID {p}" for p, _ in mm], fontsize=7.4)
        ax.invert_yaxis()
        ax.set_xlim(0, (mm[0][1] if mm else 1) * 1.3)
        ax.xaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.set_title(f"{label(d)}: {tot} misses in {len(D['o2_misses_by_paper'].get(d, []))} papers", fontsize=8.6)
        ax.set_xlabel("reference pairs not recovered")
        style(ax, "x")
    fig.text(0.01, -0.02, "*development disease. HGVS-recall misses (tiers 1+2) by the ClinVar-cited paper they come from. Source: analysis/six_disease/o2/o2_recall_misses.csv.", fontsize=7.2, color=MUTED)
    return save(fig, "figS7_o2_misses")


# --------------------------------------------------------------------------------------------- Figure 11
def fig_omim(D):
    """The OMIM holdout (D-42): allelic-variant recall, where OMIM's source papers stand in our funnel, and OMIM's coverage of the run's P/LP variants."""
    per = D["omimh"]["per"]
    fig, axes = plt.subplots(1, 3, figsize=(13, 4.3), gridspec_kw={"wspace": 0.55, "width_ratios": [1.1, 1.3, 1.0]})

    def ser(r, color, hollow):
        return (r["share"], r["ci95"][0], r["ci95"][1], r["k"], r["n"], color, hollow)

    items = [(label(d), [ser(per[d]["B_allelic_variants"]["recall_unrestricted_strict"], BLUE, d == "ha20")]) for d in DISEASES]
    items.append(("all six", [ser(D["omimh"]["totals"]["recall_all_strict"], BLUE, False)]))
    _ci_panel(axes[0], items, "A  OMIM allelic variants recovered anywhere in the run", "allelic variants recovered at the genomic or protein level (%)")
    # B: allelic-variant source papers by funnel status (ordinal stages, one-hue ramp)
    stages = [("extracted", ORD4[3]), ("in corpus, no open full text", ORD4[2]), ("not found by search", ORD4[1])]
    ax = axes[1]
    for i, d in enumerate(DISEASES):
        cnt = per[d]["A_literature"]["funnel_by_citation_place"].get("allelic-variant narrative", {})
        total = sum(cnt.values())
        left = 0
        for name, color in stages:
            v = cnt.get(name, 0)
            if v:
                ax.barh(i, v, left=left, color=color, edgecolor=SURFACE, linewidth=1.2, height=0.62, zorder=2)
                left += v
        other = total - left
        if other:
            ax.barh(i, other, left=left, color=DEEMPH, edgecolor=SURFACE, linewidth=1.2, height=0.62, zorder=2)
        ax.text(total + 0.6, i, str(total), fontsize=6.8, color=INK2, va="center")
    ax.set_yticks(range(len(DISEASES)))
    ax.set_yticklabels([label(d) for d in DISEASES])
    ax.invert_yaxis()
    ax.set_xlabel("papers OMIM cites as sources for its allelic variants")
    ax.set_title("B  Where OMIM's source papers stand in our corpus")
    ax.legend(handles=[Patch(color=c, label=n) for n, c in stages] + [Patch(color=DEEMPH, label="other (excluded, held out, unclear)")], loc="lower right", fontsize=6.8)
    style(ax, "x")
    # C: OMIM's coverage of the ClinVar P/LP variants the run found
    items = []
    for d in DISEASES:
        r = per[d]["C_clinvar"]["share_of_run_clinvar_plp_in_omim"]
        items.append((label(d), [ser(r, BLUE, d == "ha20")]))
    _ci_panel(axes[2], items, "C  Run's ClinVar P/LP variants that are OMIM allelic variants", "share of the run's ClinVar P/LP variants listed by OMIM (%)")
    fig.text(0.01, -0.06, f"Wilson 95% intervals. Hollow = HA20 (development disease). OMIM entry pages frozen {D['omimh']['date']} (D-42); ClinVar placement of OMIM's variants by E-utilities the same day. "
             "Source: analysis/omim_holdout/results_2026-10-28.json.", fontsize=7.2, color=MUTED)
    return save(fig, "fig11_omim")


def make_all(D) -> dict:
    return {
        "fig1": fig_overview(D), "fig2": fig_corpus(D), "fig3": fig_gatekeeper(D), "fig4": fig_repeat(D), "fig5": fig_records(D),
        "fig6": fig_concordance(D), "fig7": fig_gaps(D), "fig8": fig_openweight(D), "fig9": fig_memorization(D), "fig10": fig_budget(D),
        "fig11": fig_omim(D),
        "figS1": figS_concentration(D), "figS2": figS_variant_spectrum(D), "figS3": figS_top_terms(D), "figS4": figS_coverage(D),
        "figS5": figS_completeness(D), "figS6": figS_gpsea(D), "figS7": figS_misses(D),
    }
