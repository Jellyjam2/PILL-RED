#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION FOR EXP-PHASE15-NONLINEAR-BOUNDARY-001 🜏
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
dataset_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE15_NONLINEAR_DATASET.json")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

if not os.path.exists(dataset_file):
    print(f"❌ Dataset not found at: {dataset_file}")
    exit(1)

with open(dataset_file, "r", encoding="utf-8") as f:
    dataset = json.load(f)

summary = dataset["summary_by_degree"]
degrees = [1, 2, 3, 4]
deg_labels = ["d=1 (Linear)", "d=2 (Quadratic)", "d=3 (Cubic)", "d=4 (Quartic)"]
mono_dims = [summary[f"degree_{d}"]["monomial_dim"] for d in degrees]
elims = [summary[f"degree_{d}"]["mean_var_elim_pct"] for d in degrees]
conf_a = [summary[f"degree_{d}"]["mean_conflicts_a"] for d in degrees]
conf_dual = [summary[f"degree_{d}"]["mean_conflicts_dual"] for d in degrees]
reds = [summary[f"degree_{d}"]["mean_reduction_pct"] for d in degrees]

# Create 4-Panel Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
fig.suptitle("PILL RED Phase XV: The Nonlinear Degree Hierarchy & Information-Gap Crucible\n(EXP-PHASE15-NONLINEAR-BOUNDARY-001 | Degrees d = 1, 2, 3, 4, 20 Instances)", fontsize=14, fontweight='bold')

# Panel A: Combinatorial Monomial Space Blow-up (Log Scale)
axs[0, 0].plot(degrees, mono_dims, marker='s', color='#d62728', linewidth=2.5, markersize=8)
axs[0, 0].set_title("Panel A: Monomial Space Dimension O(n^d) [Log Scale]", fontweight='bold')
axs[0, 0].set_yscale('log')
axs[0, 0].set_xticks(degrees)
axs[0, 0].set_xticklabels(deg_labels)
axs[0, 0].set_ylabel("Linearization Monomial Count")
for i, v in enumerate(mono_dims):
    axs[0, 0].text(degrees[i], v * 1.4, f"{v:,}", ha='center', fontweight='bold', fontsize=10)
axs[0, 0].grid(True, alpha=0.3)

# Panel B: GF(2) Linear Elimination Collapse
axs[0, 1].bar(deg_labels, elims, color=['#2ca02c', '#d62728', '#d62728', '#d62728'], width=0.45, edgecolor='black', alpha=0.85)
axs[0, 1].set_title("Panel B: GF(2) Linear Variable Elimination (%)", fontweight='bold')
axs[0, 1].set_ylabel("Variable Elimination (%)")
axs[0, 1].set_ylim(0, 115)
for i, v in enumerate(elims):
    axs[0, 1].text(i, v + 2.0, f"{v:.1f}%", ha='center', fontweight='bold', fontsize=11)
axs[0, 1].grid(True, alpha=0.3)

# Panel C: CDCL Search Conflicts by Degree
x = np.arange(len(degrees))
w = 0.3
axs[1, 0].bar(x - w/2, conf_a, w, label='Mode A (Raw CDCL)', color='#1f77b4', edgecolor='black', alpha=0.85)
axs[1, 0].bar(x + w/2, conf_dual, w, label='Dual-Field Hybrid', color='#2ca02c', edgecolor='black', alpha=0.85)
axs[1, 0].set_title("Panel C: Search Conflicts across Polynomial Degrees", fontweight='bold')
axs[1, 0].set_xticks(x)
axs[1, 0].set_xticklabels(deg_labels)
axs[1, 0].set_ylabel("Mean CDCL Conflicts")
axs[1, 0].legend(loc='upper right', frameon=True)
axs[1, 0].grid(True, alpha=0.3)

# Panel D: Residual Conflict Reduction (%)
axs[1, 1].bar(deg_labels, reds, color=['#2ca02c', '#7f7f7f', '#7f7f7f', '#7f7f7f'], width=0.45, edgecolor='black', alpha=0.85)
axs[1, 1].set_title("Panel D: Residual Search Conflict Reduction (%)", fontweight='bold')
axs[1, 1].set_ylabel("Conflict Reduction (%)")
axs[1, 1].set_ylim(0, 50)
for i, v in enumerate(reds):
    axs[1, 1].text(i, v + 1.0, f"{v:+.1f}%", ha='center', fontweight='bold', fontsize=11)
axs[1, 1].grid(True, alpha=0.3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)
out_png = os.path.join(release_dir, "phase15_nonlinear_gap.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
