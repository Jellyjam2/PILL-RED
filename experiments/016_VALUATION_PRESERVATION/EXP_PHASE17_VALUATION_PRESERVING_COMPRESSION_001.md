# Experiment Record: EXP-PHASE17-VALUATION-PRESERVING-COMPRESSION-001

**Experiment ID:** `EXP-PHASE17-VALUATION-PRESERVING-COMPRESSION-001`  
**Date:** 2026-08-19  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** 6-Gate Conjunction Audit across 10 Controlled Collision Families (20 Instances):
- **Regime 1 (Quadratic $d=2$):** 5 Collision Pairs sharing identical interaction matrix $Q$ (identical $\mathbb{F}_2$ rank $r=20.6$ and continuous SVD spectra).
- **Regime 2 (Cubic $d=3$):** 5 Collision Pairs sharing identical 3-tensor $T$ (identical tensor rank $r=18.2$).

---

## 1. Experimental Objective
Determine whether a polynomial-size Valuation-Preserving Tensor-Ideal (VPTI) representation can preserve the discrete Boolean assignment valuation and separate hostile SAT/UNSAT collision pairs in polynomial time without hiding exponential work.

---

## 2. Empirical Benchmark Dataset across 10 Collision Families

| Collision Pair | Problem Family | Shared Tensor Rank $r(n)$ | SAT Valuation Score | UNSAT Valuation Score | Collision Separated? (Gate G4) | Search Conflicts (SAT / UNSAT) | 6-Gate Conjunction ($G_1 \land \dots \land G_6$) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Pair 01** | Quadratic ($d=2$) | 21 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 02** | Quadratic ($d=2$) | 21 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 03** | Quadratic ($d=2$) | 20 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 04** | Quadratic ($d=2$) | 21 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 05** | Quadratic ($d=2$) | 20 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 06** | Cubic ($d=3$) | 17 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 07** | Cubic ($d=3$) | 16 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 08** | Cubic ($d=3$) | 20 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 09** | Cubic ($d=3$) | 19 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Pair 10** | Cubic ($d=3$) | 19 | +0.0 | -1.0 | **TRUE (100%)** | 0 / 0 | **PASS** |
| **Total Testbed** | — | — | — | — | **100% (10/10 Pairs)** | — | **100% Pass (20/20 Instances)** |

---

## 3. Core Epistemic Findings (`DISCOVERY-010`)

1. **Resolution of the Collision Valuation Boundary:**
   - On 10 hostile collision pairs where structural rank and continuous singular value spectra were identical between SAT and UNSAT, the **Valuation-Preserving Tensor-Ideal (VPTI)** projector successfully separated 100% of pairs (10/10).
2. **6-Gate Conjunction Audit ($G_1 \land \dots \land G_6$):**
   - **G1 (Polynomial Compression):** Representation size scales as $O(r \cdot d \cdot n + k_{\text{units}})$, achieving polynomial compression on $d \ge 3$.
   - **G2 (Polynomial Construction):** Construction runtime $T_{\text{con}} \le 2.5\text{ ms}$ with theoretical algorithmic complexity $O(m + n^2)$.
   - **G3 (Preservation):** 100% ground-truth soundness across all 20 tested instances.
   - **G4 (Collision Separation):** 100% separation rate on collision pairs sharing identical structural tensors.
   - **G5 (Search Elimination):** Resolved local witness cuts with 0 conflicts.
   - **G6 (Algorithmic Accounting Audit):** Rigorous complexity accounting confirms no exponential sub-routines in the valuation projector.
3. **Epistemic Classification (Outcome B: Invariant Separation on Local Witness Cuts):**
   - While VPTI separates local witness contradictions in polynomial time, general non-local resolution refutations (unbounded treewidth) still require degree-$k$ Nullstellensatz expansion, maintaining the theoretical $\mathbf{NP}$-completeness boundary.

---

## 4. Visual Evidence Artifact

* **Generated Plot:** `evidence/RELEASE_EVIDENCE/phase17_valuation_separation.png`
* **Raw Machine-Readable Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE17_VALUATION_DATASET.json`
