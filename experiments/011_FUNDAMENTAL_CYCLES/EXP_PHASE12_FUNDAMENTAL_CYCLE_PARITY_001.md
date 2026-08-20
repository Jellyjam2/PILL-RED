# Experiment Record: EXP-PHASE12-FUNDAMENTAL-CYCLE-PARITY-001

**Experiment ID:** `EXP-PHASE12-FUNDAMENTAL-CYCLE-PARITY-001`  
**Date:** 2026-08-19  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** 3-Way Search Comparison on 24-Node 3-Regular Expander Tseitin Formulas (15 Instances):
- **Mode A:** Pure CDCL (Glucose3 Baseline)
- **Mode E:** 1D Graph Laplacian ($\mathbf{L}_0 = \mathbf{B}_1^T \mathbf{B}_1$)
- **Mode C:** Global Fundamental Cycle Laplacian ($\mathbf{\Delta}_{\text{cycle}} = \mathbf{B}_1^T \mathbf{B}_1 + \mathbf{C}_T^T \mathbf{C}_T$) based on spanning tree fundamental cycle bases ($\dim(C_T) = |E| - |V| + 1 = 12..13$, mean cycle length $6.1..7.2$).

---

## 1. Experimental Objective
Evaluate whether constructing a continuous quadratic operator from the **Global Fundamental Cycle Basis ($\mathbf{C}_T$)** induced by a spanning tree recovers non-local parity obstructions and reduces CDCL conflicts on Tseitin expanders.

---

## 2. Empirical Benchmark Summary

| Metric | Mode A (Pure CDCL) | Mode E (1D $\mathbf{L}_0$) | Mode C (Cycle $\mathbf{\Delta}_{\text{cycle}}$) | Observed Cycle Reduction | Empirical Soundness |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **UNSAT Parity Contradictions (Mean)** | 323.7 | 321.9 | 323.5 | **+0.1% reduction** | **100% (10/10)** |
| **SAT Parity Instances (Mean)** | 0.4 | 87.4 | 87.8 | **High Variance** | **100% (5/5)** |
| **Overall Dataset** | — | — | — | — | **100% (15/15)** |

---

## 3. Core Epistemic Finding: The Real vs $\mathbb{F}_2$ Field Barrier (`FALSIFICATION-004`)

1. **Falsification:**
   - Incorporating global fundamental cycles into a real-valued quadratic form $\mathbf{C}_T^T \mathbf{C}_T$ **did not reduce CDCL search on UNSAT parity contradictions (+0.1% reduction)**.
2. **Mathematical Root Cause ($\mathbb{R}$ vs $\mathbb{F}_2$):**
   - Real quadratic forms over $\mathbb{R}$ penalize $\sum_{e \in c} x_e \ne 0$.
   - In Boolean parity over $\mathbb{F}_2 = \text{GF}(2)$, satisfying a parity constraint requires $\sum_{e \in c} x_e \equiv 1 \pmod 2$ or $0 \pmod 2$.
   - Continuous diffusion in Euclidean space $\mathbb{R}^n$ cancels positive and negative signs linearly ($+1 + (-1) = 0$), completely erasing the discrete mod 2 parity obstruction.
3. **Soundness Rate:**
   - **100% preserved (15/15 ground truth agreement)**.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase12_fundamental_cycles.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE12_FUNDAMENTAL_CYCLE_DATASET.json`
