#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION FOR EXP-PHASE7-SPECTRAL-OBSERVABLE-001 🜏
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
dataset_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE7_SPECTRAL_OBSERVABLE_DATASET.json")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

if not os.path.exists(dataset_file):
    print(f"❌ Dataset not found at: {dataset_file}")
    exit(1)

with open(dataset_file, "r", encoding="utf-8") as f:
    seeds_data = json.load(f)

mode_names = [
    "Mode A (Pure CDCL)",
    "Mode B (Fiedler Gated)",
    "Mode C (Higher Modes)",
    "Mode D (Projector P)",
    "Mode E (Boundary Manifold)"
]

# Aggregate metrics across seeds
seeds = [d["seed"] for d in seeds_data]
num_seeds = len(seeds)

conflicts_by_mode = {m: [] for m in mode_names}
decisions_by_mode = {m: [] for m in mode_names}
time_by_mode = {m: [] for m in mode_names}
soundness_by_mode = {m: [] for m in mode_names}

for s_idx, d in enumerate(seeds_data):
    modes = d["modes"]
    for m_idx, m_res in enumerate(modes):
        name = mode_names[m_idx]
        conflicts_by_mode[name].append(m_res["stats"].get("conflicts", 0))
        decisions_by_mode[name].append(m_res["stats"].get("decisions", 0))
        time_by_mode[name].append(m_res["solver_time"] * 1000)
        soundness_by_mode[name].append(1 if m_res["result"] == "SAT" else 0)

# Create 4-Panel Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(15, 10), dpi=300)
fig.suptitle("PILL RED Phase VII: 5-Mode Spectral Observable Comparative Ablation\n(EXP-PHASE7-SPECTRAL-OBSERVABLE-001 | 16 Rounds, 256 In / 32 Out | 5 Random Seeds)", fontsize=14, fontweight='bold')

x = np.arange(len(mode_names))

# Panel A: Soundness Preservation Rate (% SAT Agreement)
sound_rates = [np.mean(soundness_by_mode[m]) * 100 for m in mode_names]
colors_sound = ['#2ca02c' if r == 100 else '#d62728' for r in sound_rates]
axs[0, 0].bar(x, sound_rates, color=colors_sound, alpha=0.85, edgecolor='black', width=0.55)
axs[0, 0].set_title("Panel A: Empirical Soundness Preservation (% SAT Agreement)", fontweight='bold')
axs[0, 0].set_xticks(x)
axs[0, 0].set_xticklabels(mode_names, rotation=20, ha='right', fontsize=9)
axs[0, 0].set_ylabel("Sound Agreement (%)")
axs[0, 0].set_ylim(0, 120)
for i, v in enumerate(sound_rates):
    axs[0, 0].text(i, v + 3, f"{v:.0f}%", ha='center', fontweight='bold', fontsize=10)
axs[0, 0].grid(True, alpha=0.3)

# Panel B: Mean CDCL Conflicts (Sound Modes Only)
mean_conf = [np.mean(conflicts_by_mode[m]) if np.mean(soundness_by_mode[m]) == 1.0 else 0 for m in mode_names]
colors_conf = ['#1f77b4', '#ff7f0e', '#d62728', '#d62728', '#2ca02c']
axs[0, 1].bar(x, mean_conf, color=colors_conf, alpha=0.85, edgecolor='black', width=0.55)
axs[0, 1].set_title("Panel B: Mean CDCL Conflicts Across Seeds (Sound Modes)", fontweight='bold')
axs[0, 1].set_xticks(x)
axs[0, 1].set_xticklabels(mode_names, rotation=20, ha='right', fontsize=9)
axs[0, 1].set_ylabel("Mean Conflicts")
axs[0, 1].set_ylim(0, max(mean_conf) * 1.35)
for i, v in enumerate(mean_conf):
    txt = f"{v:.1f}" if np.mean(soundness_by_mode[mode_names[i]]) == 1.0 else "CORRUPTED\n(UNSAT)"
    axs[0, 1].text(i, max(v, 1) + 0.5, txt, ha='center', fontsize=9, fontweight='bold')
axs[0, 1].grid(True, alpha=0.3)

# Panel C: Mean CDCL Decisions (Search Volume)
mean_dec = [np.mean(decisions_by_mode[m]) if np.mean(soundness_by_mode[m]) == 1.0 else 0 for m in mode_names]
axs[1, 0].bar(x, mean_dec, color=colors_conf, alpha=0.85, edgecolor='black', width=0.55)
axs[1, 0].set_title("Panel C: Mean CDCL Decisions (Search Volume)", fontweight='bold')
axs[1, 0].set_xticks(x)
axs[1, 0].set_xticklabels(mode_names, rotation=20, ha='right', fontsize=9)
axs[1, 0].set_ylabel("Mean Decisions")
axs[1, 0].set_ylim(0, max(mean_dec) * 1.3)
for i, v in enumerate(mean_dec):
    txt = f"{v:,.0f}" if np.mean(soundness_by_mode[mode_names[i]]) == 1.0 else "CORRUPTED"
    axs[1, 0].text(i, max(v, 500) + 700, txt, ha='center', fontsize=9, fontweight='bold')
axs[1, 0].grid(True, alpha=0.3)

# Panel D: Mean Solver Latency (ms)
mean_time = [np.mean(time_by_mode[m]) if np.mean(soundness_by_mode[m]) == 1.0 else 0 for m in mode_names]
axs[1, 1].bar(x, mean_time, color=colors_conf, alpha=0.85, edgecolor='black', width=0.55)
axs[1, 1].set_title("Panel D: Mean Solver Execution Latency (ms)", fontweight='bold')
axs[1, 1].set_xticks(x)
axs[1, 1].set_xticklabels(mode_names, rotation=20, ha='right', fontsize=9)
axs[1, 1].set_ylabel("Latency (ms)")
axs[1, 1].set_ylim(0, max(mean_time) * 1.35)
for i, v in enumerate(mean_time):
    txt = f"{v:.2f}ms" if np.mean(soundness_by_mode[mode_names[i]]) == 1.0 else "N/A"
    axs[1, 1].text(i, max(v, 0.1) + 0.1, txt, ha='center', fontsize=9, fontweight='bold')
axs[1, 1].grid(True, alpha=0.3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)
out_png = os.path.join(release_dir, "phase7_spectral_observables.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
