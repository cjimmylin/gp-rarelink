"""fig_human_assessment: design diagram of the D-55 human assessment (experimental_log.md §4).

Design only: no results, no rater identities. Every number is copied from the log
(§4, §4.1, §4.2, §4.3, §7). Coordinates are in inches on a 7 x 4.5 in canvas.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch

W, H = 7.0, 4.5
FS = 8          # body text, pt
FS_HEAD = 9     # band titles
LS = 1.2        # line spacing
LINE = FS * LS / 72.0
DARK = "#333333"
ARROW = "#444444"

C = {
    "blue": "#0072B2", "sky": "#56B4E9", "orange": "#E69F00", "purple": "#CC79A7",
    "verm": "#D55E00", "green": "#009E73", "black": "#000000",
}
TITLE_COL = {"#0072B2": "#0072B2", "#E69F00": "#8a5a00", "#CC79A7": "#a0507f",
             "#D55E00": "#a34200", "#009E73": "#00664a", "#000000": DARK}


def tint(hex_color, f):
    """Mix a colour with white (f = share of white)."""
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    r, g, b = (round(v + (255 - v) * f) for v in (r, g, b))
    return f"#{r:02x}{g:02x}{b:02x}"


plt.rcParams.update({"font.family": "sans-serif", "font.sans-serif": ["DejaVu Sans"],
                     "font.size": FS})
fig = plt.figure(figsize=(W, H), facecolor="white")
ax = fig.add_axes([0, 0, 1, 1])
ax.set_xlim(0, W)
ax.set_ylim(0, H)
ax.axis("off")

CHECKS = []  # (text artist, (x0, y0, x1, y1)) for the overflow check


def box(x0, y0, x1, y1, edge, fill_f=0.88, lw=1.0, pad=0.04, z=2):
    ax.add_patch(FancyBboxPatch((x0 + pad, y0 + pad), x1 - x0 - 2 * pad, y1 - y0 - 2 * pad,
                                boxstyle=f"round,pad={pad},rounding_size=0.06",
                                fc=tint(edge, fill_f), ec=edge, lw=lw, zorder=z))


def txt(x, y, s, size=FS, weight="normal", ha="center", va="center", color=DARK, z=5,
        within=None):
    t = ax.text(x, y, s, fontsize=size, fontweight=weight, ha=ha, va=va, color=color,
                zorder=z, linespacing=LS)
    if within is not None:
        CHECKS.append((t, within))
    return t


def titled(x0, y0, x1, y1, title, body, edge, gap=0.05):
    """Box with a bold title line and body text, block centred vertically."""
    box(x0, y0, x1, y1, edge)
    n_body = body.count("\n") + 1
    block = LINE * (n_body + 1) + gap
    top = (y0 + y1) / 2 + block / 2
    xm = (x0 + x1) / 2
    inner = (x0 + 0.06, y0 + 0.05, x1 - 0.06, y1 - 0.05)
    txt(xm, top - LINE / 2, title, weight="bold", color=TITLE_COL[edge], within=inner)
    txt(xm, top - LINE - gap, body, va="top", within=inner)


def arrow(p0, p1, color=ARROW, lw=1.0, z=3):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9, color=color,
                                 lw=lw, shrinkA=0, shrinkB=0, zorder=z))


def line(xs, ys, color=ARROW, lw=1.0, z=3):
    ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle="butt")


# ---------------------------------------------------------------- stage bands
S1 = (2.60, 4.47)
S2 = (0.02, 2.48)
for (y0, y1) in (S1, S2):
    ax.add_patch(FancyBboxPatch((0.03, y0), W - 0.06, y1 - y0,
                                boxstyle="round,pad=0,rounding_size=0.08",
                                fc="#F4F4F4", ec="#D0D0D0", lw=0.6, zorder=0))
txt(0.12, S1[1] - 0.12, "Stage 1: Calibration (due 2026-11-22)", size=FS_HEAD,
    weight="bold", ha="left")
txt(1.32, S2[1] - 0.12, "Stage 2: Main assessment", size=FS_HEAD, weight="bold", ha="left")

# ---------------------------------------------------------------- stage 1
y0s, y1s = 2.68, 4.22
ym1 = (y0s + y1s) / 2

titled(0.10, y0s, 1.42, y1s, "Reference labels",
       "PI labels 99\ncandidate claims\nfrom the registered\nruns, blind to the\ngatekeeper",
       C["blue"])

titled(1.60, y0s, 3.00, y1s, "Fixed set rule",
       "+2 recorded\namendments\n→ 40 claims:\n20 unsupported,\n20 supported,\nfrom 39 papers",
       C["blue"])

# nine identical rater icons R1..R9
rx0, rx1 = 3.18, 4.68
box(rx0, y0s, rx1, y1s, C["sky"], fill_f=0.85)
rxm = (rx0 + rx1) / 2
r, sp = 0.105, 0.24
gy_top = y1s - 0.17
for i in range(9):
    cx = rxm + (i % 3 - 1) * sp
    cy = gy_top - (i // 3) * sp
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=C["sky"], lw=1.0, zorder=4))
    txt(cx, cy, f"R{i + 1}", size=FS, z=6)
txt(rxm, y0s + 0.06, "same 40 claims,\neach in own order;\nno reference label,\n"
    "gatekeeper verdict\nor source pool shown", va="bottom",
    within=(rx0 + 0.05, y0s + 0.04, rx1 - 0.05, gy_top - 2 * sp - r - 0.02))

# floor diamond
dx, dy, hw, hh = 5.88, ym1, 1.02, 0.76
ax.add_patch(Polygon([(dx - hw, dy), (dx, dy + hh), (dx + hw, dy), (dx, dy - hh)],
                     closed=True, fc=tint(C["orange"], 0.82), ec=C["orange"], lw=1.0, zorder=2))
txt(dx, dy + 2.5 * LINE, "Floor", weight="bold", color=TITLE_COL[C["orange"]])
txt(dx, dy - 0.5 * LINE,
    "≥15 of 20\nunsupported caught\nAND\n≥18 of 20\nsupported passed", va="center")

for xa, xb in [(1.42, 1.60), (3.00, 3.18), (4.68, dx - hw)]:
    arrow((xa, ym1), (xb, ym1))

# ---------------------------------------------------------------- connector to stage 2
dec = (0.10, 0.76, 1.16, 1.60)
xm_dec = (dec[0] + dec[2]) / 2
yc = (S1[0] + S2[1]) / 2
line([dx, dx], [dy - hh, yc])
line([dx, xm_dec], [yc, yc])
arrow((xm_dec, yc), (xm_dec, dec[3]))

# ---------------------------------------------------------------- stage 2
titled(*dec, "PI decides", "after calibration:\nwho goes on;\nPlan A or\nPlan B", C["purple"])

pa = (1.32, 1.22, 2.62, 2.24)
pb = (1.32, 0.10, 2.62, 1.12)
titled(*pa, "Plan A",
       "registered six\n250 audit claims\n50 ClinVar misses\n214 gap candidates", C["blue"])
titled(*pb, "Plan B",
       "all twelve\n527 audit claims\n146 ClinVar misses\n269 gap candidates", C["verm"])

ym_a = (pa[1] + pa[3]) / 2
ym_b = (pb[1] + pb[3]) / 2
ym_dec = (dec[1] + dec[3]) / 2
xj = 1.24
line([dec[2], xj], [ym_dec, ym_dec])
line([xj, xj], [ym_b, ym_a])
arrow((xj, ym_a), (pa[0], ym_a))
arrow((xj, ym_b), (pb[0], ym_b))

# three tracks
tx0, tx1 = 2.82, 5.80
lanes = {"audit": (1.16, 2.24), "triage": (0.72, 1.10), "adj": (0.08, 0.68)}
mids = {k: (v[0] + v[1]) / 2 for k, v in lanes.items()}
xc = 2.72
line([pa[2], xc], [ym_a, ym_a])
line([pb[2], xc], [ym_b, ym_b])
line([xc, xc], [min(ym_b, *mids.values()), max(ym_a, *mids.values())])
for m in mids.values():
    arrow((xc, m), (tx0, m))

# (a) audit lane: ring of nine raters, three overlapping groups of three
a0, a1 = lanes["audit"]
box(tx0, a0, tx1, a1, C["green"])
rc = (tx0 + 0.36, (a0 + a1) / 2)
rr = 0.25
pts = [(rc[0] + rr * math.sin(2 * math.pi * i / 9), rc[1] + rr * math.cos(2 * math.pi * i / 9))
       for i in range(9)]
for tri in [(0, 3, 6), (2, 5, 8), (4, 6, 0)]:
    ax.add_patch(Polygon([pts[i] for i in tri], closed=True, fc=tint(C["green"], 0.6),
                         ec=C["green"], lw=0.8, alpha=0.5, zorder=3))
for (px, py) in pts:
    ax.add_patch(Circle((px, py), 0.045, fc="white", ec="#1b6e55", lw=0.9, zorder=4))
lane_in = (tx0 + 0.70, a0 + 0.05, tx1 - 0.05, a1 - 0.05)
tx_a = tx0 + 0.72
txt(tx_a, a1 - 0.07, "(a) Audit", weight="bold", ha="left", va="top",
    color=TITLE_COL[C["green"]], within=lane_in)
txt(tx_a, a1 - 0.07 - LINE,
    "Each claim read by 3 raters in rotating,\n"
    "overlapping groups of three (84 groups\n"
    "with nine raters); equal loads; every\n"
    "pair shares claims. Script names a\n"
    "registered pair + tie-breaker per claim.\n"
    "Rule C: at most 4 of 250 unsupported.",
    ha="left", va="top", within=lane_in)

# (b) triage
t0, t1 = lanes["triage"]
box(tx0, t0, tx1, t1, C["orange"])
txt(tx0 + 0.12, (t0 + t1) / 2 + LINE / 2, "(b) Triage of ClinVar misses", weight="bold",
    ha="left", color=TITLE_COL[C["orange"]], within=(tx0, t0, tx1 - 0.05, t1))
txt(tx0 + 0.12, (t0 + t1) / 2 - LINE / 2, "2 raters per item; PI settles differences",
    ha="left", within=(tx0, t0, tx1 - 0.05, t1))

# (c) gap adjudication
g0, g1 = lanes["adj"]
box(tx0, g0, tx1, g1, C["verm"])
g_top = (g0 + g1) / 2 + 2 * LINE + 0.01
txt(tx0 + 0.12, g_top - LINE / 2, "(c) Gap adjudication", weight="bold", ha="left",
    color=TITLE_COL[C["verm"]], within=(tx0, g0, tx1 - 0.05, g1))
txt(tx0 + 0.12, g_top - LINE,
    "2 raters per candidate; a third where they differ\non the decision or across the "
    "pathogenic /\nuncertain line", ha="left", va="top",
    within=(tx0, g0 + 0.03, tx1 - 0.05, g1))

# collector to sign-off
xs = 5.89
fx0, fx1 = 5.97, 6.94
for m in mids.values():
    line([tx1, xs], [m, m])
line([xs, xs], [min(mids.values()), max(mids.values())])
f_mid = mids["triage"]
arrow((xs, f_mid), (fx0, f_mid))
titled(fx0, f_mid - 0.70, fx1, f_mid + 0.70, "Sign-off",
       "panel approval\n+ PI sign-off\nbefore any\nsubmission\nrecord\n(nothing\nsubmitted yet)",
       C["black"])

# ---------------------------------------------------------------- overflow check
fig.canvas.draw()
rend = fig.canvas.get_renderer()
inv = ax.transData.inverted()
bad = []
for t, (bx0, by0, bx1, by1) in CHECKS:
    (ex0, ey0), (ex1, ey1) = inv.transform(t.get_window_extent(rend).get_points())
    if ex0 < bx0 - 1e-3 or ex1 > bx1 + 1e-3 or ey0 < by0 - 1e-3 or ey1 > by1 + 1e-3:
        bad.append((t.get_text()[:30], round(ex0, 2), round(ey0, 2), round(ex1, 2), round(ey1, 2),
                    (bx0, by0, bx1, by1)))
for b in bad:
    print("OVERFLOW", b)

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
