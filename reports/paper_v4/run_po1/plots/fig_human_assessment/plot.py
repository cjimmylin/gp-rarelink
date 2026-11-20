"""fig_human_assessment: design diagram of the D-55 human assessment (experimental_log.md §4).

Design only: no results, no rater identities. Every number is copied from the log
(§4, §4.1, §4.2, §4.3, §7). Coordinates are in inches on a 7 x 3.94 in canvas.
"""
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Polygon, Circle, FancyArrowPatch

W, H = 7.0, 3.94
FS = 8          # body text, pt
FS_HEAD = 9     # band titles
DARK = "#333333"
ARROW = "#444444"

C = {
    "blue": "#0072B2", "sky": "#56B4E9", "orange": "#E69F00", "purple": "#CC79A7",
    "verm": "#D55E00", "green": "#009E73", "black": "#000000",
}


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


def box(x0, y0, x1, y1, edge, fill_f=0.88, lw=1.0, pad=0.04, z=2):
    p = FancyBboxPatch((x0 + pad, y0 + pad), x1 - x0 - 2 * pad, y1 - y0 - 2 * pad,
                       boxstyle=f"round,pad={pad},rounding_size=0.06",
                       fc=tint(edge, fill_f), ec=edge, lw=lw, zorder=z)
    ax.add_patch(p)


def txt(x, y, s, size=FS, weight="normal", ha="center", va="center", color=DARK, z=5, ls=1.25):
    ax.text(x, y, s, fontsize=size, fontweight=weight, ha=ha, va=va, color=color,
            zorder=z, linespacing=ls)


def titled(x0, y0, x1, y1, title, body, edge, gap=0.06):
    """Box with a bold title line and body text, block centred vertically."""
    box(x0, y0, x1, y1, edge)
    n_body = body.count("\n") + 1
    line = FS * 1.25 / 72.0
    block = line * (n_body + 1) + gap
    top = (y0 + y1) / 2 + block / 2
    xm = (x0 + x1) / 2
    txt(xm, top - line / 2, title, weight="bold", color=edge if edge != C["black"] else DARK)
    txt(xm, top - line - gap, body, va="top")


def arrow(p0, p1, color=ARROW, lw=1.0, z=3):
    a = FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=9, color=color,
                        lw=lw, shrinkA=0, shrinkB=0, zorder=z)
    ax.add_patch(a)


def line(xs, ys, color=ARROW, lw=1.0, z=3):
    ax.plot(xs, ys, color=color, lw=lw, zorder=z, solid_capstyle="butt")


# ---------------------------------------------------------------- stage bands
for (y0, y1, title) in [(2.18, 3.92, "Stage 1: Calibration (due 2026-11-22)"),
                        (0.02, 2.06, "Stage 2: Main assessment")]:
    band = FancyBboxPatch((0.03, y0), W - 0.06, y1 - y0,
                          boxstyle="round,pad=0,rounding_size=0.08",
                          fc="#F4F4F4", ec="#D0D0D0", lw=0.6, zorder=0)
    ax.add_patch(band)
    txt(0.12, y1 - 0.12, title, size=FS_HEAD, weight="bold", ha="left")

# ---------------------------------------------------------------- stage 1
y0s, y1s = 2.28, 3.62
ym1 = (y0s + y1s) / 2

titled(0.10, y0s, 1.52, y1s, "Reference labels",
       "PI labels 99 candidate\nclaims from the\nregistered runs, blind\nto the gatekeeper",
       C["blue"])

titled(1.72, y0s, 3.22, y1s, "Fixed set rule",
       "(+2 recorded amendments)\n→ 40 claims:\n20 unsupported,\n20 supported,\nfrom 39 papers",
       C["blue"])

# nine identical rater icons R1..R9
rx0, rx1 = 3.42, 4.80
box(rx0, y0s, rx1, y1s, C["sky"], fill_f=0.85)
rxm = (rx0 + rx1) / 2
txt(rxm, y1s - 0.17, "9 raters", weight="bold", color="#1f6f99")
r = 0.115
sp = 0.31
gy_top = y1s - 0.42
for i in range(9):
    cx = rxm + (i % 3 - 1) * sp
    cy = gy_top - (i // 3) * sp
    ax.add_patch(Circle((cx, cy), r, fc="white", ec=C["sky"], lw=1.0, zorder=4))
    txt(cx, cy, f"R{i + 1}", size=FS - 0.5 if False else FS, z=6)
txt(rxm, y0s + 0.20, "same 40 claims,\neach in own order", va="center")

# floor diamond
dx, dy, hw, hh = 5.85, ym1, 0.98, 0.66
ax.add_patch(Polygon([(dx - hw, dy), (dx, dy + hh), (dx + hw, dy), (dx, dy - hh)],
                     closed=True, fc=tint(C["orange"], 0.82), ec=C["orange"], lw=1.0, zorder=2))
txt(dx, dy + 0.27, "Floor", weight="bold", color="#9a6400")
txt(dx, dy - 0.07, "≥15 of 20 unsupported caught\nAND\n≥18 of 20 supported passed",
    va="center")

for xa, xb in [(1.52, 1.72), (3.22, 3.42), (4.80, dx - hw)]:
    arrow((xa, ym1), (xb, ym1))

# ---------------------------------------------------------------- connector to stage 2
dec_x0, dec_x1 = 0.10, 1.08
dec_y0, dec_y1 = 0.62, 1.40
xm_dec = (dec_x0 + dec_x1) / 2
line([dx, dx], [dy - hh, 2.12])
line([dx, xm_dec], [2.12, 2.12])
arrow((xm_dec, 2.12), (xm_dec, dec_y1 - 0.0))

# ---------------------------------------------------------------- stage 2
titled(dec_x0, dec_y0, dec_x1, dec_y1, "PI decides",
       "after calibration:\nwho goes on;\nPlan A or Plan B", C["purple"])

pa = (1.24, 1.02, 2.30, 1.80)
pb = (1.24, 0.12, 2.30, 0.90)
titled(*pa, "Plan A",
       "registered six\n250 audit claims\n50 ClinVar misses\n214 gap candidates", C["blue"])
titled(*pb, "Plan B",
       "all twelve\n527 audit claims\n146 ClinVar misses\n269 gap candidates", C["verm"])

ym_a = (pa[1] + pa[3]) / 2
ym_b = (pb[1] + pb[3]) / 2
ym_dec = (dec_y0 + dec_y1) / 2
# branch: decision -> Plan A / Plan B
xj = 1.16
line([dec_x1, xj], [ym_dec, ym_dec])
line([xj, xj], [ym_b, ym_a])
arrow((xj, ym_a), (pa[0] + 0.0, ym_a))
arrow((xj, ym_b), (pb[0] + 0.0, ym_b))

# three tracks
tx0, tx1 = 2.50, 5.74
lanes = {
    "audit": (1.00, 1.84),
    "triage": (0.58, 0.94),
    "adj": (0.10, 0.52),
}
# collector from the chosen plan to the three tracks
xc = 2.40
line([pa[2], xc], [ym_a, ym_a])
line([pb[2], xc], [ym_b, ym_b])
lane_mids = {k: (v[0] + v[1]) / 2 for k, v in lanes.items()}
line([xc, xc], [min(lane_mids.values() | {ym_b}) if False else min(ym_b, *lane_mids.values()),
                max(ym_a, *lane_mids.values())])
for k, m in lane_mids.items():
    arrow((xc, m), (tx0, m))

# (a) audit lane with ring of nine and three overlapping triangles
a0, a1 = lanes["audit"]
box(tx0, a0, tx1, a1, C["green"])
ring_c = (tx0 + 0.42, (a0 + a1) / 2)
rr = 0.27
pts = [(ring_c[0] + rr * math.sin(2 * math.pi * i / 9),
        ring_c[1] + rr * math.cos(2 * math.pi * i / 9)) for i in range(9)]
for tri in [(0, 2, 5), (1, 5, 7), (3, 7, 0)]:
    ax.add_patch(Polygon([pts[i] for i in tri], closed=True,
                         fc=tint(C["green"], 0.55), ec=C["green"], lw=0.8, alpha=0.55, zorder=3))
for (px, py) in pts:
    ax.add_patch(Circle((px, py), 0.042, fc="white", ec="#1b6e55", lw=0.9, zorder=4))
ax_text_x = tx0 + 0.80
txt(ax_text_x, a1 - 0.10, "(a) Audit", weight="bold", ha="left", va="top", color="#00664a")
txt(ax_text_x, a1 - 0.25,
    "Each claim read by 3 raters in rotating, overlapping\n"
    "groups of three (84 groups with nine raters); equal\n"
    "loads; every pair shares claims. Script names a\n"
    "registered pair + tie-breaker per claim.\n"
    "Rule C: at most 4 of 250 unsupported.",
    ha="left", va="top")

# (b) triage
t0, t1 = lanes["triage"]
box(tx0, t0, tx1, t1, C["orange"])
txt(tx0 + 0.12, (t0 + t1) / 2, "(b) Triage of ClinVar misses:", weight="bold", ha="left",
    color="#9a6400")
txt(tx0 + 1.95, (t0 + t1) / 2, "2 raters per item;\nPI settles differences", ha="left")

# (c) gap adjudication
g0, g1 = lanes["adj"]
box(tx0, g0, tx1, g1, C["verm"])
txt(tx0 + 0.12, (g0 + g1) / 2, "(c) Gap adjudication:", weight="bold", ha="left",
    color="#a34200")
txt(tx0 + 1.45, (g0 + g1) / 2,
    "2 raters per candidate; a third where they\ndiffer on the decision or across the\n"
    "pathogenic / uncertain line", ha="left")

# collector to sign-off
xs = 5.84
fx0, fx1 = 5.96, 6.92
for k, m in lane_mids.items():
    line([tx1, xs], [m, m])
line([xs, xs], [min(lane_mids.values()), max(lane_mids.values())])
f_mid = lane_mids["triage"]
arrow((xs, f_mid), (fx0, f_mid))
titled(fx0, f_mid - 0.55, fx1, f_mid + 0.55, "Sign-off",
       "panel approval +\nPI sign-off before\nany submission\nrecord (nothing\nsubmitted yet)",
       C["black"])

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
