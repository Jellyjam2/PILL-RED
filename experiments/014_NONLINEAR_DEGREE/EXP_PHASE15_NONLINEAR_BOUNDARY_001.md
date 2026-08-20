# Experiment Record: EXP-PHASE15-NONLINEAR-BOUNDARY-001

**Experiment ID:** `EXP-PHASE15-NONLINEAR-BOUNDARY-001`  
**Date:** 2026-08-19  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Controlled Boolean Polynomial Degree Ladder ($d = 1, 2, 3, 4$, 20 Instances):
- **Degree $d=1$:** Pure Linear Parity ($\bigoplus x_i = c$)
- **Degree $d=2$:** Quadratic Boolean Constraints ($(x_1 \land x_2) \oplus y = c$)
- **Degree $d=3$:** Cubic Boolean Constraints ($(x_1 \land x_2 \land x_3) \oplus y = c$)
- **Degree $d=4$:** Quartic Boolean Constraints ($(x_1 \land x_2 \land x_3 \land x_4) \oplus y = c$)

---

## 1. Experimental Objective
Measure the information gap and representation size as Boolean constraint degree scales from $d=1$ to $d=4$. Quantify $\mathbb{F}_2$ linear variable elimination rates, monomial linearization dimensions $\binom{n}{\le d}$, and residual search complexity.

---

## 2. Empirical Benchmark Dataset by Polynomial Degree

| Degree $d$ | Characteristic Constraint | Monomial Dimension $\binom{n}{\le d}$ | $\mathbb{F}_2$ Linear Elimination (%) | Raw CDCL Conflicts (Mode A) | Dual-Field Conflicts | Conflict Reduction (%) | Empirical Soundness |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **$d=1$** | Linear Parity $\bigoplus x_i = c$ | **30** | **99.3%** | 5.0 | **0.0** | **+40.0% to +100%** | **100% (5/5)** |
| **$d=2$** | Quadratic $(x_1 \land x_2) \oplus y = c$ | **2,485** | **0.0%** | 0.4 | 0.4 | **+0.0%** | **100% (5/5)** |
| **$d=3$** | Cubic $(x_1 \dots x_3) \oplus y = c$ | **57,225** | **0.0%** | 0.4 | 0.4 | **+0.0%** | **100% (5/5)** |
| **$d=4$** | Quartic $(x_1 \dots x_4) \oplus y = c$ | **974,120** | **0.0%** | 0.8 | 0.8 | **+0.0%** | **100% (5/5)** |
| **Total** | — | — | — | — | — | — | **100% (20/20)** |

---

## 3. Core Epistemic Findings (`DISCOVERY-008`)

1. **The Step-Function Collapse of Linear Invariants:**
   - At degree $d=1$, $\mathbb{F}_2$ Gaussian elimination removes 99.3% of variables and resolves parity refutations directly.
   - At degree $d \ge 2$, $\mathbb{F}_2$ linear elimination drops immediately to **0.0% elimination**, because nonlinear monomials $x_1 \dots x_d$ are linearly independent of individual literals over $\mathbb{F}_2$.
2. **Combinatorial Representation Explosion ($O(n^d)$):**
   - Exact linearization of higher-degree constraints without search requires lifting to the monomial basis $\mathbb{F}_2^{\binom{n}{\le d}}$.
   - For $n=70$, the dimension explodes from $30 \to 2,485 \to 57,225 \to 974,120$ variables.
3. **The Information Gap:**
   - Linear projections throw away higher-degree correlation ideals ($x_i x_j = 0$). Capturing them algebraically requires super-polynomial state expansion unless the underlying circuit ideal exhibits low degree or bounded rank.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase15_nonlinear_gap.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE15_NONLINEAR_DATASET.json`
