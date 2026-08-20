# Experiment Record: EXP-PHASE11-HODGE-PARITY-CRUCIBLE-001

**Experiment ID:** `EXP-PHASE11-HODGE-PARITY-CRUCIBLE-001`  
**Date:** 2026-08-18  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** 3-Way Observable Ablation on Tseitin Expander Parity Formulas:
- **Mode A:** Pure CDCL (Glucose3 Baseline)
- **Mode E:** 1D Graph Laplacian ($\mathbf{L}_0 = \mathbf{B}_1^T \mathbf{B}_1$)
- **Mode H:** 2D Hodge Laplacian ($\mathbf{\Delta}_1 = \mathbf{B}_1^T \mathbf{B}_1 + \mathbf{B}_2^T \mathbf{B}_2$) on 2-simplices (3-cycles)
- **Instances:** 15 total instances (10 UNSAT odd-charge parity contradictions, 5 SAT even-charge formulas) on 3-regular Ramanujan expanders ($n=35..36, m=88..96$).

---

## 1. Experimental Objective
Evaluate whether augmenting the graph Laplacian with higher-dimensional simplicial boundary operators ($\mathbf{B}_2$) into the **1-Hodge Laplacian ($\mathbf{\Delta}_1$)** provides structural search guidance for parity obstructions on expander graphs that defeated 1D graph Laplacians in Phase X.

---

## 2. Empirical 3-Way Benchmark Dataset

| Instance Category | Mode A Conflicts (Pure CDCL) | Mode E Conflicts (1D $\mathbf{L}_0$) | Mode H Conflicts (2D Hodge $\mathbf{\Delta}_1$) | Hodge Conflict Reduction (%) | Empirical Soundness |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **UNSAT Parity Contradictions** (Mean) | 323.7 | 280.2 | 321.7 | **+0.6% reduction** | **100% (10/10)** |
| **SAT Parity Instances** (Mean) | 0.4 | 0.8 | 3.8 | **-750.0% variance** | **100% (5/5)** |
| **Overall Dataset** | — | — | — | — | **100% (15/15)** |

---

## 3. Core Epistemic Findings & Falsification

### 1. 🚫 Falsification of Local Simplicial Hodge Guidance (`FALSIFICATION-003`)
- 2D Hodge Laplacians built on local 2-simplices (triangles $n=3$) **failed to provide meaningful search reduction (+0.6% on UNSAT parity)**.
- **Mathematical Root Cause (Girth Barrier):** Expander graphs have high girth ($g \ge 5$). The number of small 2-simplices is negligible ($0 \dots 2$ triangles per instance), causing $H_1\text{\_dim} = 0$. Consequently, $\mathbf{B}_2 \approx \mathbf{0}$, causing $\mathbf{\Delta}_1$ to degenerate back into $\mathbf{L}_0$.

### 2. 🛡️ Robust Soundness Preservation
- Across all 15 instances, the solver maintained **100% ground-truth SAT/UNSAT agreement**.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase11_hodge_parity.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE11_HODGE_DATASET.json`
