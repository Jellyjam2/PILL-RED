#!/usr/bin/env python3
# 🜏 PILL RED: SCIENTIFIC VISUALIZATION GENERATOR FOR EXP-PHASE6-SHA256-INVERSION-001 🜏
import os
import sys
import glob
import json
import matplotlib.pyplot as plt

# Force utf-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
records_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
release_dir = os.path.join(parent, "evidence", "RELEASE_EVIDENCE")
os.makedirs(release_dir, exist_ok=True)

# Load all 5 sweep points
prefix_points = [0, 8, 16, 24, 32]
data = []
for p in prefix_points:
    fpath = os.path.join(records_dir, f"sha256_inversion_{p}bits.json")
    if os.path.exists(fpath):
        with open(fpath, "r", encoding="utf-8") as f:
            data.append(json.load(f))

if not data:
    print("❌ No benchmark records found in evidence/BENCHMARK_RECORDS/")
    exit(1)

prefixes = [d["prefix_bits"] for d in data]
lambda1 = [d["spectral_telemetry"]["lambda_1"] for d in data]
lambda2 = [d["spectral_telemetry"]["lambda_2"] for d in data]
lambda3 = [d["spectral_telemetry"]["lambda_3"] for d in data]
delta_f = [d["spectral_telemetry"]["fiedler_gap"] for d in data]

mode_a_time = [d["ablation_modes"]["mode_a_baseline"]["solver_time"] * 1000 for d in data]
mode_b_time = [d["ablation_modes"]["mode_b_polarity_only"]["solver_time"] * 1000 for d in data]
mode_c_time = [d["ablation_modes"]["mode_c_phase5_gated"]["solver_time"] * 1000 for d in data]

mode_a_decisions = [d["ablation_modes"]["mode_a_baseline"]["stats"]["decisions"] for d in data]
mode_b_decisions = [d["ablation_modes"]["mode_b_polarity_only"]["stats"]["decisions"] for d in data]
mode_c_decisions = [d["ablation_modes"]["mode_c_phase5_gated"]["stats"]["decisions"] for d in data]

mode_a_conflicts = [d["ablation_modes"]["mode_a_baseline"]["stats"]["conflicts"] for d in data]

# Create Publication-Grade 4-Panel Plot
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
fig, axs = plt.subplots(2, 2, figsize=(14, 10), dpi=300)
fig.suptitle("PILL RED Phase VI: Boundary-Constrained SHA-256 Inversion Sweep\n(EXP-PHASE6-SHA256-INVERSION-001 | 16-Round Circuit | n=2048, m=2528..2560)", fontsize=14, fontweight='bold')

# Panel A: Spectrum vs Boundary Difficulty
axs[0, 0].plot(prefixes, lambda1, 'o-', label=r'$\lambda_1$', color='#1f77b4', linewidth=2)
axs[0, 0].plot(prefixes, lambda2, 's--', label=r'$\lambda_2$', color='#ff7f0e', linewidth=2)
axs[0, 0].plot(prefixes, lambda3, '^:', label=r'$\lambda_3$', color='#2ca02c', linewidth=2)
axs[0, 0].set_title("Panel A: Graph Laplacian Spectrum vs Output Pinning", fontweight='bold')
axs[0, 0].set_xlabel("Target Output Prefix (Bits)")
axs[0, 0].set_ylabel("Eigenvalue Magnitude")
axs[0, 0].legend(loc='upper left')
axs[0, 0].grid(True, alpha=0.3)

# Panel B: Spectral Gap ΔF
axs[0, 1].plot(prefixes, delta_f, 'd-', color='#d62728', linewidth=2.5, label=r'$\Delta_F = \lambda_3 - \lambda_2$')
axs[0, 1].axhline(0.05, color='black', linestyle='--', alpha=0.7, label=r'Safety Gate Threshold ($\Delta_{min}=0.05$)')
axs[0, 1].set_title("Panel B: Spectral Gap ΔF & Degeneracy Gating", fontweight='bold')
axs[0, 1].set_xlabel("Target Output Prefix (Bits)")
axs[0, 1].set_ylabel("Spectral Gap (ΔF)")
axs[0, 1].legend(loc='upper right')
axs[0, 1].grid(True, alpha=0.3)

# Panel C: CDCL Decisions vs Boundary Difficulty
axs[1, 0].plot(prefixes, mode_a_decisions, 'o-', label="Mode A (Pure Glucose3)", color='#1f77b4', linewidth=2)
axs[1, 0].plot(prefixes, mode_b_decisions, 's--', label="Mode B (Polarity Reseed)", color='#ff7f0e', linewidth=2)
axs[1, 0].plot(prefixes, mode_c_decisions, '^:', label="Mode C (Phase-V Gated Spectral)", color='#2ca02c', linewidth=2)
axs[1, 0].set_title("Panel C: CDCL Decisions vs Boundary Difficulty", fontweight='bold')
axs[1, 0].set_xlabel("Target Output Prefix (Bits)")
axs[1, 0].set_ylabel("CDCL Decisions")
axs[1, 0].legend(loc='lower left')
axs[1, 0].grid(True, alpha=0.3)

# Panel D: Solver Latency Comparison
axs[1, 1].plot(prefixes, mode_a_time, 'o-', label="Mode A (Pure Glucose3)", color='#1f77b4', linewidth=2)
axs[1, 1].plot(prefixes, mode_b_time, 's--', label="Mode B (Polarity Reseed)", color='#ff7f0e', linewidth=2)
axs[1, 1].plot(prefixes, mode_c_time, '^:', label="Mode C (Phase-V Gated Spectral)", color='#2ca02c', linewidth=2)
axs[1, 1].set_title("Panel D: Solver Execution Latency (ms)", fontweight='bold')
axs[1, 1].set_xlabel("Target Output Prefix (Bits)")
axs[1, 1].set_ylabel("Solver Latency (ms)")
axs[1, 1].legend(loc='upper right')
axs[1, 1].grid(True, alpha=0.3)

plt.tight_layout()
out_png = os.path.join(release_dir, "sha256_inversion_sweep.png")
plt.savefig(out_png, dpi=300)
print(f"📊 [PLOT GENERATED]: {out_png}")
