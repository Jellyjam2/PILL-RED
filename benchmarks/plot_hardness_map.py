#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION FOR EXP-PHASE6-SHA256-HARDNESS-MAP-001 🜏
import os
import sys
import json
import matplotlib.pyplot as plt

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
dataset_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE6_HARDNESS_MAP_DATASET.json")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

if not os.path.exists(dataset_file):
    print(f"❌ Dataset not found at: {dataset_file}")
    exit(1)

with open(dataset_file, "r", encoding="utf-8") as f:
    data = json.load(f)

labels = [f"({d['input_bits']} In, {d['output_bits']} Out)" for d in data]
in_bits = [d['input_bits'] for d in data]
conflicts_a = [d["mode_a"]["stats"].get("conflicts", 0) for d in data]
decisions_a = [d["mode_a"]["stats"].get("decisions", 0) for d in data]
time_a_ms = [d["mode_a"]["time"] * 1000 for d in data]
delta_f = [d["spectral_telemetry"]["fiedler_gap"] for d in data]

# 4-Panel Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=300)
fig.suptitle("PILL RED Phase VI: Empirical Hardness Map & Transition Discovery\n(EXP-PHASE6-SHA256-HARDNESS-MAP-001 | 16-Round SHA-256 Circuit | n=2048, m=2528..2816)", fontsize=14, fontweight='bold')

# Panel A: CDCL Conflicts (Emergence of Combinatorial Search)
colors = ['#1f77b4' if c == 0 else '#d62728' for c in conflicts_a]
axs[0, 0].bar(range(len(labels)), conflicts_a, color=colors, alpha=0.85, edgecolor='black')
axs[0, 0].set_title("Panel A: CDCL Conflicts (Hardness Emergence at 128 In / 32 Out)", fontweight='bold')
axs[0, 0].set_xticks(range(len(labels)))
axs[0, 0].set_xticklabels(labels, rotation=35, ha='right', fontsize=9)
axs[0, 0].set_ylabel("CDCL Conflicts (Backtracks)")
axs[0, 0].axvline(3.5, color='black', linestyle='--', linewidth=1.5, label='Hardness Boundary (128 In, 32 Out)')
axs[0, 0].legend(loc='upper left')
axs[0, 0].grid(True, alpha=0.3)

# Panel B: CDCL Decisions Scaling
axs[0, 1].plot(range(len(labels)), decisions_a, 'o-', color='#2ca02c', linewidth=2.5, markersize=7)
axs[0, 1].set_title("Panel B: CDCL Decisions (Branch Exploration Volume)", fontweight='bold')
axs[0, 1].set_xticks(range(len(labels)))
axs[0, 1].set_xticklabels(labels, rotation=35, ha='right', fontsize=9)
axs[0, 1].set_ylabel("Decisions Made")
axs[0, 1].axvline(3.5, color='black', linestyle='--', linewidth=1.5, label='Transition Point')
axs[0, 1].legend(loc='upper left')
axs[0, 1].grid(True, alpha=0.3)

# Panel C: Solver Wall-Clock Latency (ms)
axs[1, 0].plot(range(len(labels)), time_a_ms, 's-', color='#ff7f0e', linewidth=2.5, markersize=7)
axs[1, 0].set_title("Panel C: Solver Wall-Clock Execution Time (ms)", fontweight='bold')
axs[1, 0].set_xticks(range(len(labels)))
axs[1, 0].set_xticklabels(labels, rotation=35, ha='right', fontsize=9)
axs[1, 0].set_ylabel("Solve Time (ms)")
axs[1, 0].axvline(3.5, color='black', linestyle='--', linewidth=1.5, label='Transition Point')
axs[1, 0].legend(loc='upper left')
axs[1, 0].grid(True, alpha=0.3)

# Panel D: Spectral Gap ΔF vs Hardness
axs[1, 1].plot(range(len(labels)), delta_f, 'd-', color='#9467bd', linewidth=2.5, markersize=7, label=r'$\Delta_F = \lambda_3 - \lambda_2$')
axs[1, 1].axhline(0.05, color='red', linestyle=':', linewidth=1.5, label=r'Safety Gate ($\Delta_{min}=0.05$)')
axs[1, 1].set_title(r"Panel D: Spectral Gap $\Delta_F$ (Degeneracy Persists Across Transition)", fontweight='bold')
axs[1, 1].set_xticks(range(len(labels)))
axs[1, 1].set_xticklabels(labels, rotation=35, ha='right', fontsize=9)
axs[1, 1].set_ylabel("Spectral Gap (ΔF)")
axs[1, 1].legend(loc='upper right')
axs[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
out_png = os.path.join(release_dir, "sha256_hardness_map.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
