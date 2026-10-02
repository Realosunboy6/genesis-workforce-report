"""Generate the 4 report figures for the Genesis report."""
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

plt.rcParams.update({"font.size": 10, "axes.grid": True, "grid.alpha": 0.3,
                     "figure.dpi": 150, "savefig.bbox": "tight"})

def read_traj(path):
    rows = []
    with open(path) as f:
        r = csv.DictReader(f)
        for row in r:
            rows.append({k: float(v) for k, v in row.items()})
    return rows

# ---------------------------------------------------------------- Fig 1: stock-flow schematic
fig, ax = plt.subplots(figsize=(10, 3.2))
ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis("off")
stocks = [("Rookies\n(100)", 1.6), ("Experienced\n(250)", 4.6), ("Gray Hairs\n(500)", 7.6)]
for label, x in stocks:
    ax.add_patch(FancyBboxPatch((x - 0.85, 1.0), 1.7, 1.1, boxstyle="round,pad=0.05",
                                fc="#dbeafe", ec="#1e40af", lw=1.5))
    ax.text(x, 1.55, label, ha="center", va="center", fontsize=10, weight="bold")
flows = [("Hiring rate", 0.35, 0.75), ("Learning rate", 2.45, 3.75), ("Maturing rate", 5.45, 6.75),
         ("Retiring rate", 8.45, 9.75)]
for label, x0, x1 in flows:
    ax.add_patch(FancyArrowPatch((x0, 1.55), (x1, 1.55), arrowstyle="-|>",
                                 mutation_scale=14, lw=1.6, color="#111827"))
    ax.text((x0 + x1) / 2, 2.02, label, ha="center", fontsize=8.5, style="italic")
    if label == "Retiring rate":
        ax.text(9.9, 1.55, "out", ha="left", va="center", fontsize=8.5, style="italic")
ax.text(1.6, 0.72, "1,000 lamps/yr", ha="center", fontsize=8.5, color="#1e40af")
ax.text(4.6, 0.72, "2,000 lamps/yr", ha="center", fontsize=8.5, color="#1e40af")
ax.text(7.6, 0.72, "4,000 lamps/yr", ha="center", fontsize=8.5, color="#1e40af")
ax.text(5, 2.75, "Genesis workforce aging chain (Vensim stock-and-flow structure)",
        ha="center", fontsize=11, weight="bold")
fig.savefig("report/figures/fig1_schematic.png")
plt.close(fig)

# ---------------------------------------------------------------- Fig 2: baseline trajectories
base = read_traj("baseline_traj.csv")
t = [r["t"] for r in base]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.plot(t, [r["rookies"] for r in base], label="Rookies")
a1.plot(t, [r["experienced"] for r in base], label="Experienced")
a1.plot(t, [r["gray"] for r in base], label="Gray Hairs")
a1.plot(t, [r["workforce"] for r in base], label="Total", lw=2.2, color="black")
a1.axhline(1700, ls="--", color="red", lw=1.2, label="Target 1,700")
a1.set_xlabel("Year"); a1.set_ylabel("Employees"); a1.legend(fontsize=8); a1.set_title("Workforce")
a2.plot(t, [r["production"] / 1e6 for r in base], color="#047857", lw=2)
a2.axhline(7.8, ls="--", color="red", lw=1.2, label="Target 7.8M")
a2.set_xlabel("Year"); a2.set_ylabel("Million lamps / year"); a2.legend(fontsize=8); a2.set_title("Production")
fig.suptitle("Baseline simulation (hiring 50/yr then 100/yr; learning 1 yr, maturing 5 yr, retiring 10 yr)",
             fontsize=11, weight="bold")
fig.savefig("report/figures/fig2_baseline.png")
plt.close(fig)

# ---------------------------------------------------------------- Fig 3: 8-combo bar chart (Table A responses)
combos = [
    ("1\n(1,3,10)", 2565), ("2*\n(1,3,15)", 2482), ("3\n(1,5,10)", 2784), ("4\n(1,5,15)", 2687),
    ("5\n(2,3,10)", 2810), ("6\n(2,3,15)", 2701), ("7\n(2,5,10)", 3030), ("8\n(2,5,15)", 2912)]
labels = [c[0] for c in combos]; vals = [c[1] for c in combos]
colors = ["#f59e0b" if i == 1 else "#93c5fd" for i in range(8)]
fig, ax = plt.subplots(figsize=(10, 3.8))
bars = ax.bar(labels, vals, color=colors, edgecolor="#1e3a8a")
ax.axhline(1700, ls="--", color="red", lw=1.4, label="Workforce target (1,700)")
ax.set_ylabel("Employees at year 10")
ax.set_xlabel("Combination (learning, maturing, retiring time in years)")
ax.set_title("Employees needed at year 10 to reach 7.8M lamps/year (base productivity)", fontsize=11, weight="bold")
ax.legend(fontsize=9)
ax.text(1, 2482 + 60, "Best: 2,482", ha="center", fontsize=9, weight="bold")
fig.savefig("report/figures/fig3_combos.png")
plt.close(fig)

# ---------------------------------------------------------------- Fig 4: recommended strategy
rec = read_traj("recommended_traj.csv")
t = [r["t"] for r in rec]
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6))
a1.plot(t, [r["workforce"] for r in rec], lw=2.2, color="#1e40af")
a1.axhline(1700, ls="--", color="red", lw=1.2, label="Target 1,700")
a1.set_xlabel("Year"); a1.set_ylabel("Employees"); a1.legend(fontsize=8); a1.set_title("Workforce")
a2.plot(t, [r["production"] / 1e6 for r in rec], color="#047857", lw=2.2)
a2.axhline(7.8, ls="--", color="red", lw=1.2, label="Target 7.8M")
a2.set_xlabel("Year"); a2.set_ylabel("Million lamps / year"); a2.legend(fontsize=8); a2.set_title("Production")
fig.suptitle("Recommended strategy: combination 2 times, hiring \u2248147/yr, productivity +41.7% by year 10",
             fontsize=11, weight="bold")
fig.savefig("report/figures/fig4_recommended.png")
plt.close(fig)
print("figures written to report/figures/")
