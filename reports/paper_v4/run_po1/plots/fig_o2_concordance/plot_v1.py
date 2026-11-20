"""fig_o2_concordance: ClinVar concordance (O2) per disease, three measures.

All values copied from raw_materials/experimental_log.md:
registered six from section 2.1.6 (first table), extension five from section 2.2 (O2 table,
Blau with the D-53 fallback), Majeed from section 2.3 (O2 bullet). Intervals are the Wilson 95%
intervals printed in the log; the script only checks them against n/N, it does not redraw them
from a recomputation.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# (label, group, [(pct, n, N, lo, hi) for tier1, tiers1+2, overlap])
ROWS = [
    ("HA20", "reg", [(26.9, 21, 78, 18.3, 37.7), (26.9, 21, 78, 18.3, 37.7), (37.9, 39, 103, 29.1, 47.5)]),
    ("SSADH", "reg", [(10.1, 16, 158, 6.3, 15.8), (14.6, 23, 158, 9.9, 20.9), (87.2, 68, 78, 78.0, 92.9)]),
    ("Tangier", "reg", [(16.7, 1, 6, 3.0, 56.4), (50.0, 3, 6, 18.8, 81.2), (56.2, 9, 16, 33.2, 76.9)]),
    ("LAD-I", "reg", [(23.3, 14, 60, 14.4, 35.4), (31.7, 19, 60, 21.3, 44.2), (34.9, 45, 129, 27.2, 43.4)]),
    ("AxD", "reg", [(27.5, 14, 51, 17.1, 40.9), (66.7, 34, 51, 53.0, 78.0), (73.1, 49, 67, 61.5, 82.3)]),
    ("Danon*", "reg", [(35.0, 7, 20, 18.1, 56.7), (50.0, 10, 20, 29.9, 70.1), (47.9, 35, 73, 36.9, 59.2)]),
    ("GAMT", "ext", [(69.2, 18, 26, 50.0, 83.5), (69.2, 18, 26, 50.0, 83.5), (90.1, 73, 81, 81.7, 94.9)]),
    ("PAPA", "ext", [(57.1, 8, 14, 32.6, 78.6), (71.4, 10, 14, 45.4, 88.3), (90.9, 10, 11, 62.3, 98.4)]),
    ("ATS", "ext", [(80.0, 16, 20, 58.4, 91.9), (80.0, 16, 20, 58.4, 91.9), (96.3, 26, 27, 81.7, 99.3)]),
    ("Blau†", "ext", [(13.6, 3, 22, 4.7, 33.3), (13.6, 3, 22, 4.7, 33.3), (63.0, 17, 27, 44.2, 78.5)]),
    ("LCAT", "ext", [(36.8, 7, 19, 19.1, 59.0), (42.1, 8, 19, 23.1, 63.7), (46.0, 23, 50, 33.0, 59.6)]),
    ("Majeed", "maj", [(6.6, 5, 76, 2.8, 14.5), (10.5, 8, 76, 5.4, 19.4), (50.0, 12, 24, 31.4, 68.6)]),
]

COLORS = {"reg": "#0072B2", "ext": "#E69F00", "maj": "#009E73"}
GROUP_LABELS = {
    "reg": "Registered six",
    "ext": "Extension five (addendum)",
    "maj": "Majeed (exploratory)",
}
FACETS = [
    "HGVS recall\ntier 1",
    "HGVS recall\ntiers 1+2",
    "Overlap, tier 1\n(extracted alleles in ClinVar; not precision)",
]


def wilson(k, n, z=1.959963984540054):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


# Consistency check of the copied numbers (point estimate and Wilson bounds to 0.1 point).
for label, _, cells in ROWS:
    for pct, k, n, lo, hi in cells:
        assert abs(100 * k / n - pct) <= 0.051, (label, pct, k, n)
        wlo, whi = wilson(k, n)
        assert abs(wlo - lo) <= 0.051 and abs(whi - hi) <= 0.051, (label, k, n, wlo, whi, lo, hi)

# y positions: half-row gap between groups
ys, y, prev = [], 0.0, None
for _, g, _ in ROWS:
    if prev is not None and g != prev:
        y += 0.6
    ys.append(y)
    y += 1.0
    prev = g
seps = []
for i in range(1, len(ROWS)):
    if ROWS[i][1] != ROWS[i - 1][1]:
        seps.append((ys[i] + ys[i - 1]) / 2)

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 8.5,
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
})

fig, axes = plt.subplots(1, 3, figsize=(7.0, 3.94), sharey=True)
fig.subplots_adjust(left=0.09, right=0.955, top=0.84, bottom=0.12, wspace=0.30)

for j, ax in enumerate(axes):
    for (label, g, cells), yy in zip(ROWS, ys):
        pct, k, n, lo, hi = cells[j]
        c = COLORS[g]
        ax.plot([lo, hi], [yy, yy], color=c, lw=1.1, solid_capstyle="butt", zorder=2)
        ax.plot(pct, yy, "o", ms=4.5, color=c, mec="white", mew=0.5, zorder=3)
        ax.annotate(f"{k}/{n}", xy=(1.02, yy), xycoords=("axes fraction", "data"),
                    ha="left", va="center", fontsize=8, color="#555555", annotation_clip=False)
    for s in seps:
        ax.axhline(s, color="#999999", lw=0.6, zorder=1)
    ax.set_xlim(0, 100)
    ax.set_xticks([0, 25, 50, 75, 100])
    ax.set_xticklabels(["0", "25", "50", "75", "100"])
    ax.grid(axis="x", color="#DDDDDD", lw=0.4, zorder=0)
    ax.set_axisbelow(True)
    for sp in ("top", "right"):
        ax.spines[sp].set_visible(False)
    for sp in ("left", "bottom"):
        ax.spines[sp].set_color("#444444")
        ax.spines[sp].set_linewidth(0.6)
    ax.tick_params(axis="both", colors="#333333", length=2.5, width=0.6)
    ax.set_title(FACETS[j], loc="left", color="#222222", pad=4)
    if j > 0:
        ax.tick_params(axis="y", left=False)

axes[0].set_yticks(ys)
axes[0].set_yticklabels([r[0] for r in ROWS])
for tick, (_, g, _) in zip(axes[0].get_yticklabels(), ROWS):
    tick.set_color("#222222")
axes[0].set_ylim(ys[-1] + 0.7, ys[0] - 0.7)

handles = [Line2D([0], [0], marker="o", color=COLORS[g], lw=1.1, ms=4.5, mec="white", mew=0.5,
                  label=GROUP_LABELS[g]) for g in ("reg", "ext", "maj")]
fig.legend(handles=handles, loc="upper center", ncol=3, frameon=False, fontsize=8,
           bbox_to_anchor=(0.52, 0.995), handlelength=2.0, columnspacing=2.0)
fig.text(0.52, 0.015, "Percent (dot) with Wilson 95% interval (line); n/N at right of each panel",
         ha="center", va="bottom", fontsize=8, color="#333333")

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
