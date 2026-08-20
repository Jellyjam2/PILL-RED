# Experiment Record: EXP-PHASE10-ADVERSARIAL-CRUCIBLE-001

**Experiment ID:** `EXP-PHASE10-ADVERSARIAL-CRUCIBLE-001`  
**Date:** 2026-08-18  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** 4 Hostile Adversarial Benchmark Regimes (18 Instances Total):
1. **Full 64-Round SHA-256** ($n=8192, m=10240$, 5 Seeds)
2. **Random 3-SAT @ Critical Phase Transition Threshold** ($n=150, m/n = 4.267$, 5 Seeds)
3. **Tseitin Parity Contradictions on Expander Graphs** ($n=35..36, m=88..96$, 5 Seeds)
4. **Pigeonhole Principle Formulas** ($\text{PHP}_5^6, \text{PHP}_6^7, \text{PHP}_7^8$, $n=30..56, m=81..204$, 3 Instances)

---

## 1. Experimental Objective
Hostile stress-testing of the **Boundary-Conditioned Graph Laplacian ($\mathbf{L}_B = \mathbf{B}^T \mathbf{W}_B \mathbf{B}$)** against non-feedforward, expansion-dominated, and exponential-resolution adversarial SAT families to delineate the exact boundaries of the continuous search guidance phenomenon.

---

## 2. Adversarial Empirical Dataset Summary

| Adversarial Testbed Family | Variables ($n$) | Clauses ($m$) | Baseline Conflicts (Mode A) | Boundary Conflicts (Mode E) | Observed Conflict Reduction | Empirical Soundness Rate | Gate Behavior |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **64-Round SHA-256** | 8,192 | 10,240 | 0.0 | 0.0 | **0.0%** (UP-dominated) | **100% (5/5)** | Active / Sound |
| **Random 3-SAT @ 4.267** | 150 | 640 | 12.4 | 12.0 | **3.2% reduction** | **100% (5/5)** | Active / High Noise |
| **Tseitin Expanders** | 35–36 | 88–96 | 139.6 | 136.4 | **2.3% reduction** | **100% (5/5)** | **Suppressed SBPs** |
| **Pigeonhole Principle (PHP)** | 30–56 | 81–204 | 310.0 | 321.3 | **-3.7% expansion** | **100% (3/3)** | **Suppressed SBPs** |

* **Total Soundness Preserved:** **100% (18/18 instances in exact agreement with ground truth)**.

---

## 3. Core Epistemic Discoveries & Falsifications

### 1. 🚫 Falsification of Universal Search Trimming
- The 12.9% conflict reduction observed across feedforward DAGs (SHA-256 16..48 rounds) **does not generalize to arbitrary adversarial graph topologies**.
- On random 3-SAT at the phase transition threshold, the signal collapsed into stochastic variance ($+66.7\%$ on Seed 46 vs $-85.7\%$ on Seed 43, mean $3.2\%$).
- On Pigeonhole Principle formulas, boundary guidance slightly increased search branching ($-3.7\%$).

### 2. 🌐 Topological Orientation Requirement
- Boundary-conditioned Laplacian preconditioning requires a **coherent spatial or causal topological gradient** (such as feedforward DAG word-mixing between known input and output boundary constraints) to project a useful 1D continuous coordinate.
- On isotropic expander graphs and parity networks, the continuous harmonic mode contains zero low-rank search guidance.

### 3. 🛡️ Absolute Safety of the Degeneracy Gate
- On all worst-case UNSAT parity contradictions (Tseitin) and PHP instances, the **Phase V Safety Gate ($\Delta_F < 0.05$) successfully detected eigenspace degeneracy and suppressed candidate SBPs**, preserving 100% empirical soundness across all 18 instances.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase10_adversarial_crucible.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE10_ADVERSARIAL_DATASET.json`
