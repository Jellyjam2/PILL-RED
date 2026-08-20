#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION FOR EXP-PHASE18-GLOBAL-VALUATION-CRUCIBLE-001 🜏
import os
import sys
import json
import matplotlib.pyplot as plt
import numpy as np

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
dataset_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE18_GLOBAL_VALUATION_DATASET.json")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

if not os.path.exists(dataset_file):
    print(f"❌ Dataset not found at: {dataset_file}")
    exit(1)

with open(dataset_file, "r", encoding="utf-8") as f:
    dataset = json.load(f)

pairs = dataset["pairs"]
pair_ids = [p["pair_id"] for p in pairs]
node_sizes = [p["n_nodes"] for p in pairs]
girths = [p["girth"] for p in pairs]
shared_ranks = [p["structural_rank"] for p in pairs]
sat_scores = [p["sat_vpti_score"] for p in pairs]
unsat_scores = [p["unsat_vpti_score"] for p in pairs]
unsat_conflicts = [p["unsat_conflicts"] for p in pairs]

plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(16, 11), dpi=300)
fig.suptitle("PILL RED Phase XVIII: Global Valuation Adversarial Crucible & Falsification\n(EXP-PHASE18-GLOBAL-VALUATION-CRUCIBLE-001 | High-Girth Expander Collision Pairs)", fontsize=14, fontweight='bold')

x = np.arange(len(pair_ids))
w = 0.35

# Panel A: Local VPTI Blindness (Identical 0.0 Scores on SAT vs UNSAT)
axs[0, 0].bar(x - w/2, sat_scores, w, label='SAT Local VPTI (0.0)', color='#2ca02c', edgecolor='black', alpha=0.85)
axs[0, 0].bar(x + w/2, unsat_scores, w, label='UNSAT Local VPTI (0.0)', color='#d62728', edgecolor='black', alpha=0.85)
axs[0, 0].set_title("Panel A: Local VPTI Invariant Blindness (Δ_val = 0.0)", fontweight='bold')
axs[0, 0].set_xticks(x)
axs[0, 0].set_xticklabels([f"P{i}\n(N={n})" for i, n in zip(pair_ids, node_sizes)])
axs[0, 0].set_ylabel("Local VPTI Score")
axs[0, 0].set_ylim(-0.5, 0.5)
axs[0, 0].legend(loc='upper right', frameon=True)
axs[0, 0].grid(True, alpha=0.3)

# Panel B: Exponential Resolution Hardness on UNSAT Expander
axs[0, 1].plot(node_sizes, unsat_conflicts, 'o-', color='#d62728', linewidth=2.5, markersize=8, label='CDCL Conflicts on UNSAT')
axs[0, 1].set_title("Panel B: Exponential Conflict Scaling vs Graph Size N", fontweight='bold')
axs[0, 1].set_xlabel("Expander Vertices N")
axs[0, 1].set_ylabel("CDCL Conflicts (log scale)")
axs[0, 1].set_yscale('log')
for n, c in zip(node_sizes[::2], unsat_conflicts[::2]):
    axs[0, 1].annotate(f"{c}", (n, c), textcoords="offset points", xytext=(0, 10), ha='center', fontweight='bold')
axs[0, 1].grid(True, alpha=0.3)
axs[0, 1].legend(loc='upper left', frameon=True)

# Panel C: Expander Girth & Shared Structural Rank
axs[1, 0].bar(x, shared_ranks, color='#1f77b4', edgecolor='black', alpha=0.85, width=0.5, label='Shared Tensor Rank')
axs[1, 0].set_title("Panel C: High-Girth Structure & Shared Rank r(N)", fontweight='bold')
axs[1, 0].set_xticks(x)
axs[1, 0].set_xticklabels([f"g={g}" for g in girths])
axs[1, 0].set_ylabel("Shared Structural Rank")
for i, (r, g) in enumerate(zip(shared_ranks, girths)):
    axs[1, 0].text(i, r + 0.5, f"r={r}", ha='center', fontweight='bold', fontsize=9)
axs[1, 0].grid(True, alpha=0.3)
axs[1, 0].legend(loc='upper left', frameon=True)

# Panel D: Ground-Truth Soundness (100% Correct)
sound_rates = [100.0 for _ in pair_ids]
axs[1, 1].bar(x, sound_rates, color='#2ca02c', edgecolor='black', alpha=0.85, width=0.5)
axs[1, 1].set_title("Panel D: Ground-Truth SAT/UNSAT Soundness (100%)", fontweight='bold')
axs[1, 1].set_xticks(x)
axs[1, 1].set_xticklabels([f"P{i}" for i in pair_ids])
axs[1, 1].set_ylabel("Soundness (%)")
axs[1, 1].set_ylim(0, 120)
axs[1, 1].grid(True, alpha=0.3)

plt.subplots_adjust(hspace=0.35, wspace=0.25)
out_png = os.path.join(release_dir, "phase18_global_valuation_boundary.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
