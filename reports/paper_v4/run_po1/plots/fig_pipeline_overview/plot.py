"""fig_pipeline_overview: provenance-first pipeline with a database-held-out harness.

Conceptual diagram; no data plotted. The one number (241,730 values, 0 span-check problems,
registered six) is from experimental_log.md §2.1.2. Drawn at final ICLR text width (5.5 in).
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import patheffects
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.sans-serif": ["Liberation Sans", "Arial", "DejaVu Sans"],
    "font.size": 8,
})

W, H = 5.5, 2.95
BLUE, BLUE_T = "#0072B2", "#E8F2F9"
ORANGE, ORANGE_T = "#E69F00", "#FDF3E1"
GREEN, GREEN_T = "#009E73", "#E6F5F0"
WALL = "#4D4D4D"
INK = "#333333"
FS = 8

fig = plt.figure(figsize=(W, H))
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

boxes = []  # (patch, text artist) for the overflow check


def box(x0, x1, y0, y1, title, body, edge, fill, badge=None):
    p = FancyBboxPatch((x0, y0), x1 - x0, y1 - y0, boxstyle="round,pad=0,rounding_size=0.04",
                       fc=fill, ec=edge, lw=0.9, zorder=3)
    ax.add_patch(p)
    t = ax.text(x0 + 0.05, y1 - 0.045, title, fontsize=FS, fontweight="bold", va="top",
                ha="left", zorder=4)
    boxes.append(((x0, x1, y0, y1), t))
    if body:
        b = ax.text(x0 + 0.05, y1 - 0.19, body, fontsize=FS, va="top", ha="left",
                    linespacing=1.15, zorder=4)
        boxes.append(((x0, x1, y0, y1), b))
    if badge:
        bt = ax.text((x0 + x1) / 2, y0 + 0.07, badge, fontsize=FS, va="bottom", ha="center",
                     linespacing=1.1, zorder=5,
                     bbox=dict(boxstyle="round,pad=0.18", fc="white", ec="black", lw=0.6))
        boxes.append(((x0, x1, y0, y1), bt))
    return p


def arrow(pts, label=None, halo=False, z=6):
    """Polyline with an arrowhead on the last segment."""
    pe = [patheffects.withStroke(linewidth=3.2, foreground="white")] if halo else None
    for (xa, ya), (xb, yb) in zip(pts[:-2], pts[1:-1]):
        ax.plot([xa, xb], [ya, yb], color=INK, lw=0.8, solid_capstyle="butt", zorder=z,
                path_effects=pe)
    a = FancyArrowPatch(pts[-2], pts[-1], arrowstyle="-|>", mutation_scale=7, color=INK,
                        lw=0.8, shrinkA=0, shrinkB=0, zorder=z)
    if halo:
        a.set_path_effects(pe)
    ax.add_patch(a)


# ---------------------------------------------------------------- lanes and wall
WALL_Y0, WALL_Y1 = 1.45, 1.62
ax.add_patch(Rectangle((0, WALL_Y1), W, H - WALL_Y1, fc=BLUE_T, ec="none", zorder=0))
ax.add_patch(Rectangle((0, 0), W, WALL_Y0, fc=ORANGE_T, ec="none", zorder=0))
ax.add_patch(Rectangle((0, WALL_Y0), W, WALL_Y1 - WALL_Y0, fc=WALL, ec="none", zorder=1))
ax.text(0.06, (WALL_Y0 + WALL_Y1) / 2, "Isolation test: no ClinVar / OMIM in extraction",
        color="white", fontsize=FS, fontweight="bold", va="center", ha="left", zorder=2)

ax.text(0.06, H - 0.05, "Extraction", fontsize=FS, fontweight="bold", va="top", color=BLUE)
ax.text(0.68, H - 0.05, "(pipeline/extract; frozen 2026-10-20, pre-registration v1.0)",
        fontsize=FS, va="top", color=INK)
ax.text(0.06, 0.05, "Harness", fontsize=FS, fontweight="bold", va="bottom", color="#9A6A00")
ax.text(0.58, 0.05, "(held-out ground truth, read only after extraction)", fontsize=FS,
        va="bottom", color=INK)

# ---------------------------------------------------------------- top lane
TY0, TY1 = 1.70, 2.76
GAP = 0.09
widths = [0.86, 1.00, 0.86, 0.94, 0.99, 0.70]
xs = []
x = (W - sum(widths) - GAP * (len(widths) - 1)) / 2
for w in widths:
    xs.append((x, x + w))
    x += w + GAP

top = [
    ("1 Corpus", "PubMed +\ncitation search;\nSonnet\nscreening;\nopen access\nonly (D-32)"),
    ("2 Extraction", "1 Opus helper\nper paper;\nvalue + verbatim\nquote + PMID;\nobserved /\nexcluded /\nnot reported"),
    ("3 Span check", "every quote\nverbatim in\nits paper"),
    ("4 Gatekeeper v4", "2nd Claude read\nof every claim;\nonly claims\njudged\n‘supported’\ngo on"),
    ("5 Stage 4", "citation-only,\n1-to-1 merges;\nVariantValidator\non MANE Select,\noriginal kept;\nHPO + Mondo"),
    ("6 Output", "GA4GH\nPheno-\npackets v2,\nschema-\nvalidated"),
]
for i, ((x0, x1), (title, body)) in enumerate(zip(xs, top)):
    badge = "241,730 values,\n0 span-check\nproblems\n(registered six)" if i == 2 else None
    box(x0, x1, TY0, TY1, title, body, BLUE, "white", badge=badge)
TMID = (TY0 + TY1) / 2
for (a0, a1), (b0, b1) in zip(xs[:-1], xs[1:]):
    arrow([(a1, TMID), (b0, TMID)])

# ---------------------------------------------------------------- bottom lane
BY0, BY1 = 0.24, 1.02
ref = (0.06, 1.12)
o2 = (1.34, 2.36, 0.68, BY1)
o3 = (1.34, 2.36, BY0, 0.58)
dos = (2.58, 3.66, BY0, 0.76)
ppl = (3.88, 5.44, BY0, BY1)
box(ref[0], ref[1], BY0, BY1, "Held-out reference",
    "ClinVar snapshot\n(dated release);\nOMIM entry pages\nfrozen 2026-10-28", ORANGE, "white")
box(*o2, "O2 concordance", "with ClinVar, OMIM", ORANGE, "white")
box(*o3, "O3 gap candidates", "absent from both", ORANGE, "white")
box(*dos, "Evidence dossiers", "verbatim quotes;\nno classification\nproposed", ORANGE, "white")
box(*ppl, "People",
    "O1 audit of supported claims;\ntriage of ClinVar misses;\ngap adjudication\n(see human-assessment figure)",
    GREEN, GREEN_T)

y_o2 = (o2[2] + o2[3]) / 2
y_o3 = (o3[2] + o3[3]) / 2
arrow([(ref[1], y_o2), (o2[0], y_o2)])
arrow([(ref[1], y_o3), (o3[0], y_o3)])
arrow([(o3[1], y_o3), (dos[0], y_o3)])
arrow([(dos[1], y_o3), (ppl[0], y_o3)])
arrow([(o2[1], 0.89), (ppl[0], 0.89)])

# ---------------------------------------------------------------- downward arrows through the wall
RUN_HI, RUN_LO = 1.31, 1.13
x_out = (xs[5][0] + xs[5][1]) / 2
x_o2o3 = (o2[0] + o2[1]) / 2
# Output -> O2 (and through O2's column to O3): records into the harness
arrow([(x_out, TY0), (x_out, RUN_HI), (x_o2o3, RUN_HI), (x_o2o3, o2[3])])
ax.text((x_o2o3 + 2.95) / 2, RUN_HI + 0.015, "phenopackets", fontsize=FS, va="bottom",
        ha="center", zorder=7)
# Gatekeeper -> People: the O1 claim pool; drawn over the other route with a white gap
x_gk = (xs[3][0] + xs[3][1]) / 2
x_pp = ppl[0] + 0.30
arrow([(x_gk, TY0), (x_gk, RUN_LO), (x_pp, RUN_LO), (x_pp, ppl[3])], halo=True, z=8)
ax.text((x_gk + x_pp) / 2 + 0.05, RUN_LO + 0.015, "supported claims", fontsize=FS,
        va="bottom", ha="center", zorder=9)
# O2 column continues to O3 (records feed both)
arrow([(o2[0] - 0.10, RUN_HI - 0.0), (o2[0] - 0.10, y_o3), (o3[0], y_o3)]) if False else None

# ---------------------------------------------------------------- overflow check
fig.canvas.draw()
r = fig.canvas.get_renderer()
inv = ax.transData.inverted()
for (x0, x1, y0, y1), t in boxes:
    bb = t.get_window_extent(r).transformed(inv)
    if bb.x0 < x0 - 1e-3 or bb.x1 > x1 + 1e-3 or bb.y0 < y0 - 1e-3 or bb.y1 > y1 + 1e-3:
        print(f"OVERFLOW: {t.get_text()[:30]!r} text x{bb.x0:.2f}-{bb.x1:.2f} y{bb.y0:.2f}-{bb.y1:.2f}"
              f" box x{x0:.2f}-{x1:.2f} y{y0:.2f}-{y1:.2f}")

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
