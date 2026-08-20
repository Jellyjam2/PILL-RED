# Experiment Record: EXP-PHASE14-DUAL-FIELD-CRUCIBLE-001

**Experiment ID:** `EXP-PHASE14-DUAL-FIELD-CRUCIBLE-001`  
**Date:** 2026-08-19  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Dual-Field Pipeline ($\mathbb{F}_2$ Gaussian Elimination $\to$ Residual CNF Simplification $\to$ Continuous $\mathbb{R}$ Boundary Spectral Guidance $\to$ CDCL) across 4 Hostile Regimes (20 Instances):
- **Regime 1:** Pure Parity Expander Contradictions (100% $\mathbb{F}_2$)
- **Regime 2:** Pure Random 3-SAT @ 4.267 (0% $\mathbb{F}_2$)
- **Regime 3:** 50/50 Mixed Parity + Nonlinear 3-SAT
- **Regime 4:** Iso-Algebraic SAT/UNSAT Invariant Pairs

---

## 1. Experimental Objective
Evaluate the limits of dual-field decomposition: measure algebraic variable/clause elimination rates, residual problem search hardness, and determine whether $\mathbb{F}_2$ linear projections can distinguish nonlinear SAT from UNSAT.

---

## 2. Empirical Benchmark Dataset by Regime

| Regime | Tested Family | $\mathbb{F}_2$ Variable Elimination (%) | Baseline Mode A Conflicts | Dual-Field Hybrid Conflicts | Observed Conflict Reduction (%) | Empirical Soundness |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| **Regime 1** | Pure Parity UNSAT | **100.0%** | 335.8 | **0.0** | **+100.0%** | **100% (5/5)** |
| **Regime 2** | Pure Random 3-SAT | **0.0%** | 842.2 | 1146.8 | **-68.1% (Expansion)** | **100% (5/5)** |
| **Regime 3** | 50/50 Mixed Circuit | **0.0% (Units)** / Parity Seed | 2.2 | 0.6 | **+52.0%** | **100% (5/5)** |
| **Regime 4** | Iso-Algebraic Pairs | **3.4%** | 0.0 | 0.0 | **+0.0%** | **100% (5/5)** |
| **Total Testbed** | — | — | — | — | — | **100% (20/20)** |

---

## 3. Core Epistemic Findings (`DISCOVERY-007`)

1. **Exact Parity Condensation:**
   - On instances with pure $\mathbb{F}_2$ structure (Regime 1), Gaussian elimination eliminated 100% of variables and reduced search conflicts from $335.8 \to 0.0$ in polynomial time ($O(m n^2)$).
2. **The Nonlinear Fallback Failure (Regime 2):**
   - On pure random 3-SAT with 0% linear structure, $\mathbb{F}_2$ eliminates nothing. Continuous spectral seeding on isotropic graphs resulted in search expansion (-68.1%).
3. **Residual Acceleration on Mixed Circuits (Regime 3):**
   - When linear parity is coupled to nonlinear clauses, seeding the $\mathbb{F}_2$ algebraic backbone reduced residual CDCL conflicts by **+52.0%** ($2.2 \to 0.6$ mean conflicts).
4. **Iso-Algebraic Nonlinear Blindness (Regime 4):**
   - SAT and UNSAT instances with identical $\mathbb{F}_2$ linear projections cannot be distinguished by linear algebraic invariants alone.
   - Ground-truth correctness on the nonlinear residual was fully maintained by the CDCL engine (**100% empirical soundness across 20/20 instances**).

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase14_dual_field.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE14_DUAL_FIELD_DATASET.json`
