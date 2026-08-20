#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION FOR EXP-PHASE8-REPRESENTATION-INVARIANCE-001 🜏
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
dataset_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE8_REPRESENTATION_DATASET.json")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

if not os.path.exists(dataset_file):
    print(f"❌ Dataset not found at: {dataset_file}")
    exit(1)

with open(dataset_file, "r", encoding="utf-8") as f:
    seeds_data = json.load(f)

rep_names = [
    "Rep A (Baseline L=BᵀB)",
    "Rep B (Boundary L_B)",
    "Rep C (Unitary U=exp(iθL))",
    "Rep D (Spatial Grid L_3D)",
    "Rep E (Hybrid L_B+αL_3D)"
]

conflicts_by_rep = {r: [] for r in rep_names}
decisions_by_rep = {r: [] for r in rep_names}
time_by_rep = {r: [] for r in rep_names}
soundness_by_rep = {r: [] for r in rep_names}

for s_idx, d in enumerate(seeds_data):
    reps = d["representations"]
    for r_idx, r_res in enumerate(reps):
        name = rep_names[r_idx]
        conflicts_by_rep[name].append(r_res["stats"].get("conflicts", 0))
        decisions_by_rep[name].append(r_res["stats"].get("decisions", 0))
        time_by_rep[name].append(r_res["solver_time"] * 1000)
        soundness_by_rep[name].append(1 if r_res["result"] == "SAT" else 0)

# Create 4-Panel Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=300)
fig.suptitle("PILL RED Phase VIII: 5-Representation Invariance & Falsification Audit\n(EXP-PHASE8-REPRESENTATION-INVARIANCE-001 | 16 Rounds, 256 In / 32 Out | 5 Random Seeds)", fontsize=14, fontweight='bold')

x = np.arange(len(rep_names))

# Panel A: Empirical Soundness Preservation
sound_rates = [np.mean(soundness_by_rep[r]) * 100 for r in rep_names]
colors_sound = ['#2ca02c' if r == 100 else '#d62728' for r in sound_rates]
axs[0, 0].bar(x, sound_rates, color=colors_sound, alpha=0.85, edgecolor='black', width=0.55)
axs[0, 0].set_title("Panel A: Soundness Preservation (% SAT Agreement)", fontweight='bold')
axs[0, 0].set_xticks(x)
axs[0, 0].set_xticklabels(rep_names, rotation=20, ha='right', fontsize=9)
axs[0, 0].set_ylabel("Sound Agreement (%)")
axs[0, 0].set_ylim(0, 120)
for i, v in enumerate(sound_rates):
    axs[0, 0].text(i, v + 3, f"{v:.0f}%", ha='center', fontweight='bold', fontsize=10)
axs[0, 0].grid(True, alpha=0.3)

# Panel B: Mean CDCL Conflicts Across Seeds
mean_conf = [np.mean(conflicts_by_rep[r]) if np.mean(soundness_by_rep[r]) == 1.0 else 0 for r in rep_names]
colors_conf = ['#1f77b4', '#2ca02c', '#ff7f0e', '#d62728', '#9467bd']
axs[0, 1].bar(x, mean_conf, color=colors_conf, alpha=0.85, edgecolor='black', width=0.55)
axs[0, 1].set_title("Panel B: Mean CDCL Conflicts Across Seeds (Sound Modes)", fontweight='bold')
axs[0, 1].set_xticks(x)
axs[0, 1].set_xticklabels(rep_names, rotation=20, ha='right', fontsize=9)
axs[0, 1].set_ylabel("Mean Conflicts")
axs[0, 1].set_ylim(0, max(mean_conf) * 1.35)
for i, v in enumerate(mean_conf):
    txt = f"{v:.1f}" if np.mean(soundness_by_rep[rep_names[i]]) == 1.0 else "CORRUPTED\n(UNSAT)"
    axs[0, 1].text(i, max(v, 1) + 0.5, txt, ha='center', fontsize=9, fontweight='bold')
axs[0, 1].grid(True, alpha=0.3)

# Panel C: Unitary Operator Invariance Verification
residuals = [2.49e-14, 1.40e-13, 6.25e-06]
res_labels = [r"$\|U^\dagger U - I\|_F$", r"$\|ULU^\dagger - L\|_F$", r"$\|\Delta \lambda\|_2$"]
res_x = np.arange(len(residuals))
axs[1, 0].bar(res_x, np.log10(residuals), color=['#1f77b4', '#ff7f0e', '#2ca02c'], alpha=0.85, edgecolor='black', width=0.5)
axs[1, 0].set_title("Panel C: Rep C Invariance Residuals (Log10 Scale)", fontweight='bold')
axs[1, 0].set_xticks(res_x)
axs[1, 0].set_xticklabels(res_labels, fontsize=10)
axs[1, 0].set_ylabel(r"$\log_{10}(\text{Frobenius Residual})$")
axs[1, 0].set_ylim(-16, 0)
for i, (v, val) in enumerate(zip(np.log10(residuals), residuals)):
    axs[1, 0].text(i, v + 0.5, f"{val:.1e}", ha='center', fontsize=9, fontweight='bold')
axs[1, 0].grid(True, alpha=0.3)

# Panel D: Mean Solver Latency (ms)
mean_time = [np.mean(time_by_rep[r]) if np.mean(soundness_by_rep[r]) == 1.0 else 0 for r in rep_names]
axs[1, 1].bar(x, mean_time, color=colors_conf, alpha=0.85, edgecolor='black', width=0.55)
axs[1, 1].set_title("Panel D: Mean Solver Execution Latency (ms)", fontweight='bold')
axs[1, 1].set_xticks(x)
axs[1, 1].set_xticklabels(rep_names, rotation=20, ha='right', fontsize=9)
axs[1, 1].set_ylabel("Latency (ms)")
axs[1, 1].set_ylim(0, max(mean_time) * 1.35)
for i, v in enumerate(mean_time):
    txt = f"{v:.2f}ms" if np.mean(soundness_by_rep[rep_names[i]]) == 1.0 else "N/A"
    axs[1, 1].text(i, max(v, 0.1) + 0.1, txt, ha='center', fontsize=9, fontweight='bold')
axs[1, 1].grid(True, alpha=0.3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)
out_png = os.path.join(release_dir, "phase8_representation_invariance.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
