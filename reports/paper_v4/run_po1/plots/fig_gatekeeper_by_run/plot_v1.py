"""fig_gatekeeper_by_run: gatekeeper (second model read) shares per run.
All values copied from raw_materials/experimental_log.md (§2.0, §2.1.2, §2.3); see plan.md."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8,
                     "axes.linewidth": 0.6, "xtick.major.width": 0.6,
                     "ytick.major.width": 0, "ytick.major.size": 0})

C = {"reg": "#0072B2", "ext": "#E69F00", "exp": "#009E73"}

# (label, run, group, kind, n, a_pct, a_lo, a_hi, b_pct, b_lo, b_hi)
rows = [
    ("HA20 (development)", "pv1-ha20", "reg", "run", "23,129", 0.20, 0.15, 0.27, 1.93, 1.75, 2.11),
    ("SSADH", "pv1-ssadh", "reg", "run", "9,759", 0.38, 0.27, 0.52, 2.86, 2.54, 3.21),
    ("Tangier", "pv1-tangier", "reg", "run", "4,830", 0.31, 0.17, 0.51, 4.49, 3.93, 5.12),
    ("LAD-I", "pv1-lad1", "reg", "run", "10,864", 0.43, 0.32, 0.57, 3.47, 3.13, 3.83),
    ("AxD", "pv1-axd", "reg", "run", "14,403", 0.27, 0.19, 0.37, 3.55, 3.26, 3.87),
    ("Danon", "pv1-danon", "reg", "run", "17,963", 0.61, 0.50, 0.74, 3.07, 2.83, 3.34),
    ("Five confirmatory (without HA20)", "pooled", "reg", "pool", "57,819", 0.43, 0.38, 0.49, 3.35, 3.20, 3.50),
    ("All six", "pooled", "reg", "pool", "80,948", 0.36, 0.32, 0.41, 2.94, 2.83, 3.06),
    ("GAMT", "pv1-gamt", "ext", "run", "9,981", 0.63, 0.49, 0.81, 4.8, None, None),
    ("PAPA", "pv1-papa", "ext", "run", "9,146", 0.35, 0.24, 0.49, 3.5, None, None),
    ("ATS", "pv1-ats", "ext", "run", "6,268", 0.86, 0.65, 1.12, 3.5, None, None),
    ("Blau", "pv1-blau", "ext", "run", "15,476", 0.25, 0.18, 0.34, 3.6, None, None),
    ("LCAT", "pv1-lcat", "ext", "run", "7,623", 0.45, 0.31, 0.62, 7.1, None, None),
    ("Majeed", "pv1s-majeed", "exp", "run", "5,161", 0.68, 0.47, 0.94, 3.7, 3.2, 4.2),
]

# y positions with gaps between groups
ys, y, prev = [], 0.0, None
for r in rows:
    if prev is not None and r[2] != prev:
        y += 1.4  # group gap (room for header)
    ys.append(y)
    prev = r[2]
    y += 1.0
ymax = ys[-1]

fig, (axa, axb) = plt.subplots(1, 2, figsize=(7.0, 5.25), sharey=True,
                               gridspec_kw={"width_ratios": [1, 1], "wspace": 0.16})

def draw(ax, ci_idx):
    for r, yy in zip(rows, ys):
        pct, lo, hi = r[ci_idx], r[ci_idx + 1], r[ci_idx + 2]
        col = C[r[2]]
        if lo is not None:
            ax.plot([lo, hi], [yy, yy], color=col, lw=1.1, solid_capstyle="butt", zorder=2)
        if r[3] == "pool":
            ax.plot(pct, yy, marker="D", ms=6, mfc=col, mec="black", mew=0.7, zorder=3)
        elif lo is None:
            ax.plot(pct, yy, marker="o", ms=4.8, mfc="white", mec=col, mew=1.2, zorder=3)
        else:
            ax.plot(pct, yy, marker="o", ms=4.8, mfc=col, mec=col, zorder=3)
    ax.grid(axis="x", color="#DDDDDD", lw=0.5)
    ax.set_axisbelow(True)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    # group separators
    for i in range(1, len(rows)):
        if rows[i][2] != rows[i - 1][2]:
            ax.axhline((ys[i] + ys[i - 1]) / 2, color="#999999", lw=0.5)

draw(axa, 5)
draw(axb, 8)

axa.set_xlim(0, 1.2)
axa.set_xticks([0, 0.2, 0.4, 0.6, 0.8, 1.0, 1.2])
axa.set_xticklabels(["0", "0.2", "0.4", "0.6", "0.8", "1.0", "1.2"])
axb.set_xlim(0, 8)
axb.set_xticks(range(0, 9))
axa.set_xlabel("% of model claims judged")
axb.set_xlabel("% of model claims judged")
axa.set_title("(a) Unsupported or span not found", loc="left", fontsize=8.5, fontweight="bold")
axb.set_title("(b) Not fully supported (adds partially supported)", loc="left",
              fontsize=8.5, fontweight="bold")

labels = []
for r in rows:
    if r[3] == "pool":
        labels.append(r[0] + ", pooled")
    else:
        labels.append(f"{r[0]}  ({r[1]})")
axa.set_yticks(ys)
axa.set_yticklabels(labels)
for t, r in zip(axa.get_yticklabels(), rows):
    t.set_color(C[r[2]] if r[3] != "pool" else "black")
    if r[3] == "pool":
        t.set_fontstyle("italic")
axa.set_ylim(ymax + 0.8, -1.6)

# group headers
heads = {"reg": "Registered six (frozen pipeline)", "ext": "Extension five (addendum)",
         "exp": "Exploratory"}
seen = set()
for r, yy in zip(rows, ys):
    if r[2] not in seen:
        seen.add(r[2])
        axa.text(-0.02, yy - 0.85, heads[r[2]], transform=axa.get_yaxis_transform(),
                 ha="right", va="center", fontsize=8, fontweight="bold", color=C[r[2]])

# n judged column at the right of panel (b)
for r, yy in zip(rows, ys):
    axb.text(1.02, yy, r[4], transform=axb.get_yaxis_transform(), ha="left", va="center",
             fontsize=7.5, color="#333333")
axb.text(1.02, -1.0, "n judged", transform=axb.get_yaxis_transform(), ha="left",
         va="center", fontsize=7.5, fontweight="bold", color="#333333")

from matplotlib.lines import Line2D
key = [Line2D([], [], marker="o", ls="-", lw=1.1, color="#555555", ms=4.8, label="run, exact 95% CI"),
       Line2D([], [], marker="o", ls="none", mfc="white", mec="#555555", mew=1.2, ms=4.8,
              label="run, no CI in log"),
       Line2D([], [], marker="D", ls="none", mfc="#0072B2", mec="black", mew=0.7, ms=6,
              label="pooled, exact 95% CI")]
axb.legend(handles=key, loc="upper right", fontsize=7, frameon=True, framealpha=1,
           edgecolor="#CCCCCC", handlelength=1.6, borderpad=0.5)

fig.savefig(os.environ["PO_OUT"], dpi=300, bbox_inches="tight", facecolor="white")
