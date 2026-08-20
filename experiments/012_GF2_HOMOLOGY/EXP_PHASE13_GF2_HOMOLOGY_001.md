# Experiment Record: EXP-PHASE13-GF2-HOMOLOGY-001

**Experiment ID:** `EXP-PHASE13-GF2-HOMOLOGY-001`  
**Date:** 2026-08-19  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** 5-Track Evaluation Across Pure Parity and Mixed Nonlinear Regimes (20 Instances):
- **Track A:** Pure CDCL (Glucose3 Baseline)
- **Track B:** 1D Graph Laplacian ($\mathbf{L}_0$) over $\mathbb{R}$
- **Track D:** Native $\text{GF}(2)$ Gaussian Elimination ($O(|V| |E|^2)$)
- **Track E:** Hybrid $\text{GF}(2)$ Algebraic Solver + CDCL

---

## 1. Experimental Objective
Determine whether a $\text{GF}(2)$-native algebraic representation exposes the parity invariants that were invisible to real-valued Laplacians, measure its polynomial computational complexity, and evaluate its boundary on mixed nonlinear Boolean circuits.

---

## 2. Empirical Benchmark Dataset

| Regime / Category | Track A Conflicts (CDCL) | Track B Conflicts (Real $\mathbf{L}_0$) | Track E Conflicts ($\text{GF}(2)$ Hybrid) | $\text{GF}(2)$ Refutation Time | Empirical Soundness |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Pure Parity UNSAT** (Mean, 10 inst) | 323.7 | 278.0 | **0.0 (100% reduction)** | **1.3 ms** | **100% (10/10)** |
| **Pure Parity SAT** (Mean, 5 inst) | 0.4 | 3.8 | **0.0 (100% reduction)** | **1.1 ms** | **100% (5/5)** |
| **Mixed Nonlinear (30% Non-linear)** | 0.2 | 0.6 | **0.2 (0.0% reduction)** | — | **100% (5/5)** |
| **Total Testbed** | — | — | — | — | **100% (20/20)** |

---

## 3. Core Epistemic Findings (`DISCOVERY-006`)

1. **Parity Obstruction Resolution in $\mathbf{P}$:**
   - On pure Tseitin parity instances, Gaussian elimination over $\mathbb{F}_2$ directly computes the algebraic consistency of the incidence system $\mathbf{A} \mathbf{x} = \mathbf{q} \pmod 2$ in $O(|V| |E|^2)$ polynomial time.
   - For all 10 UNSAT parity instances, $\text{GF}(2)$ elimination produced a refutation certificate in **$1.1 \dots 2.3\text{ ms}$**, reducing CDCL search conflicts from **$323.7 \to 0.0$** instantly.
2. **The Nonlinear Boolean Complexity Boundary:**
   - When non-linear clauses (`AND`, `OR`, `IF`, `MAJ`) are introduced (e.g. 30% nonlinear fraction), linear $\text{GF}(2)$ systems capture only the linear sub-ideal.
   - General SAT contains higher-degree polynomial equations over $\mathbb{F}_2$ ($\deg \ge 2$), where exact algebraic reduction (Groebner bases / Nullstellensatz) is $\mathbf{NP}$-hard.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase13_gf2_homology.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE13_GF2_DATASET.json`
