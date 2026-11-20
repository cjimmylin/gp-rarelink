"""fig_access_constraint: corpus funnel (log 2.1.1) and OMIM holdout (log 2.1.7).

All values copied from raw_materials/experimental_log.md. Saves to $PO_OUT.
"""
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.gridspec import GridSpec  # noqa: E402

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 8,
    "axes.titlesize": 9,
    "axes.labelsize": 8,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8,
    "legend.fontsize": 8,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.facecolor": "white",
    "axes.facecolor": "white",
})

C_CORPUS = "#BBBBBB"
C_OPEN = "#0072B2"
C_ELIG = "#56B4E9"
C_EXTR = "#009E73"
C_CLOSED = "#E69F00"
C_NEVER = "#D55E00"
C_OTHER = "#999999"

# ---- log 2.1.1 Corpus table -------------------------------------------------
diseases = ["HA20 (dev.)", "SSADH", "Tangier", "LAD-I", "AxD", "Danon"]
corpus = [160, 171, 284, 274, 363, 244]
open_ft = [85, 59, 39, 59, 83, 96]
open_share = ["53.1%", "34.5%", "13.7%", "21.5%", "22.9%", "39.3%"]
eligible = [None, 40, 31, 42, 69, 83]  # HA20: not screened (pilot corpus)
extracted = [85, 40, 31, 42, 69, 83]

# ---- log 2.1.7 OMIM holdout table --------------------------------------------
recall_rows = ["HA20", "SSADH", "Tangier", "LAD-I", "AxD", "Danon"]
recall_k_n = ["8/9", "4/7", "2/19", "12/14", "9/13", "8/13"]
recall_pct = [88.9, 57.1, 10.5, 85.7, 69.2, 61.5]
recall_lo = [56.5, 25.0, 2.9, 60.1, 42.4, 35.5]
recall_hi = [98.0, 84.2, 31.4, 96.0, 87.3, 82.3]
pooled = ("All six", "43/75", 57.3, 46.1, 67.9)

# ---- log 2.1.7 bullet: OMIM's 84 source papers ------------------------------
src_segments = [
    ("extracted", 5, C_EXTR),
    ("in corpus without an open copy", 38, C_CLOSED),
    ("never returned by the searches", 38, C_NEVER),
    ("not in corpus (screened unclear/other)", 3, C_OTHER),
]

fig = plt.figure(figsize=(7.0, 3.94))
gs = GridSpec(2, 2, figure=fig, width_ratios=[1.12, 1.0], height_ratios=[3.1, 0.75],
              wspace=0.42, hspace=0.62)

# ============================ panel (a) ======================================
ax = fig.add_subplot(gs[:, 0])
bh = 0.22
series = [
    ("in corpus (title/abstract)", corpus, C_CORPUS),
    ("open full text", open_ft, C_OPEN),
    ("eligible after full-text screening", eligible, C_ELIG),
    ("extracted", extracted, C_EXTR),
]
n = len(diseases)
for i in range(n):
    y0 = i  # group centre (inverted axis later)
    for j, (name, vals, col) in enumerate(series):
        y = y0 - 1.5 * bh + j * bh
        v = vals[i]
        if v is None:
            ax.text(2, y, "not screened (pilot corpus)", va="center", ha="left",
                    fontsize=8, color="#555555", style="italic")
            continue
        ax.barh(y, v, height=bh * 0.92, color=col, edgecolor="none",
                label=name if i == 0 else None)
        lab = f"{v} ({open_share[i]})" if j == 1 else f"{v}"
        ax.text(v + 4, y, lab, va="center", ha="left", fontsize=8)

ax.set_yticks(range(n))
ax.set_yticklabels(diseases)
ax.set_ylim(n - 0.48, -0.52)
ax.set_xlim(0, 430)
ax.set_xlabel("Papers")
ax.xaxis.grid(True, color="#E5E5E5", linewidth=0.6)
ax.set_axisbelow(True)
ax.tick_params(axis="y", length=0)
ax.set_title("(a) Corpus funnel, registered six", loc="left", fontweight="bold")
handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in series]


# ============================ panel (b) top ==================================
bx = fig.add_subplot(gs[0, 1])
ys = list(range(len(recall_rows)))
for y, p, lo, hi, kn in zip(ys, recall_pct, recall_lo, recall_hi, recall_k_n):
    bx.plot([lo, hi], [y, y], color="#000000", linewidth=1.0)
    bx.plot(p, y, "o", color="#000000", markersize=4)
    bx.text(103, y, kn, va="center", ha="left", fontsize=8)
yp = len(recall_rows) + 0.4
name, kn, p, lo, hi = pooled
bx.plot([lo, hi], [yp, yp], color="#000000", linewidth=1.6)
bx.plot(p, yp, "D", color="#000000", markersize=5)
bx.text(103, yp, kn, va="center", ha="left", fontsize=8, fontweight="bold")
bx.axhline(len(recall_rows) - 0.3, color="#BBBBBB", linewidth=0.6)
bx.set_yticks(ys + [yp])
bx.set_yticklabels(recall_rows + [name])
bx.set_ylim(yp + 0.6, -0.6)
bx.set_xlim(0, 100)
bx.set_xticks([0, 25, 50, 75, 100])
bx.set_xlabel("OMIM allelic variants recovered (%), Wilson 95% CI")
bx.xaxis.grid(True, color="#E5E5E5", linewidth=0.6)
bx.set_axisbelow(True)
bx.tick_params(axis="y", length=0)
bx.set_title("(b) OMIM holdout: recall anywhere in the run", loc="left", fontweight="bold")

# ============================ panel (b) bottom ===============================
cx = fig.add_subplot(gs[1, 1])
left = 0
for lab, v, col in src_segments:
    cx.barh(0, v, left=left, height=0.6, color=col, edgecolor="white", linewidth=0.6)
    left += v
cx.set_xlim(0, 84)
cx.set_ylim(-0.4, 0.4)
cx.set_yticks([])
cx.spines["left"].set_visible(False)
cx.set_xticks([0, 20, 40, 60, 84])
cx.set_xlabel("OMIM's 84 source papers for these variants")
# labels: big segments inside, small ones via legend
left = 0
for lab, v, col in src_segments:
    if v >= 10:
        cx.text(left + v / 2, 0, str(v), va="center", ha="center", fontsize=8,
                color="white", fontweight="bold")
    left += v
leg_handles = [plt.Rectangle((0, 0), 1, 1, color=c) for _, _, c in src_segments]
leg_labels = [f"{lab}: {v}" for lab, v, _ in src_segments]
# both legends below their panels, one column each, tops aligned (figure coordinates)
leg_y = ax.get_position().y0 - 0.13
fig.legend(handles, [s[0] for s in series], loc="upper left",
           bbox_to_anchor=(ax.get_position().x0 - 0.01, leg_y), ncol=1, frameon=False,
           handlelength=1.0, fontsize=8)
fig.legend(leg_handles, leg_labels, loc="upper left",
           bbox_to_anchor=(cx.get_position().x0 - 0.01, leg_y), ncol=1, frameon=False,
           handlelength=1.0, fontsize=8)

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
