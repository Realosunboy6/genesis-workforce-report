# Genesis Workforce and Production Report

ISYE 681 — Introduction to System Dynamics and Applications
Raj Nooti, Ibrahim Oyeyinka, Farnood Tavakoli

Genesis plans to grow its workforce from 850 to 1,700 employees and annual
output from 2.6 to 7.8 million lamps within ten years. This repo holds the
system dynamics analysis: a Vensim aging-chain workforce model
(Rookies → Experienced → Gray Hairs), a 2³ experimental design on the
chain's time constants, and the full report.

## Contents

- `report/report.tex` — the report (Overleaf-ready; compile `report.tex` with the `figures/` folder alongside it)
- `report/figures/` — generated figures
- `genesis_model.py` — Python replica of the Vensim aging-chain model (first-order delays); reproduces the report's numbers
- `make_figures.py` — regenerates the report figures from the model
- `genesis_8combo_corrected.csv` — the 8-combination design table: per-combination hiring rate solved to reach 7.8M lamps/year at base productivity
- `genesis_tableB_gain.csv` — per-combination hiring rate for 1,700 employees and the productivity gain needed to reach 7.8M lamps
- `baseline_traj.csv`, `recommended_traj.csv` — year-by-year trajectories

## Key findings

- Baseline policy reaches only 1,233 employees and 3.72M lamps/year by year 10.
- The targets are jointly infeasible at current productivity: 7.8M lamps from 1,700 employees needs 4,588 lamps/employee-year, above the 4,000 of Gray Hairs (the most productive tier).
- At base productivity, hitting 7.8M lamps needs 2,482–3,031 employees — overshooting the workforce target. The best timing combination (1-yr learning, 3-yr maturing, 15-yr retiring) needs the fewest: 2,482.
- Recommended: that timing combination with hiring ≈147/year after year 1 and ≈42% productivity growth by year 10 → 1,700 employees and 7.8M lamps/year. Smallest required gain of all eight combinations tested.
