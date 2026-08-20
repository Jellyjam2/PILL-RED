# 🔴 PILL RED v2.0 Falsification Dossier: FALSIFICATION-V2-002

**Document ID:** `FALSIFICATION-V2-002`  
**Candidate ID:** `CAND-11E3D21E86` (`quadratic_ideal_mpo`)  
**Mathematical Class:** Truncated Degree-2 Polynomial Ideal / Matrix Product Operator (MPO)  
**Date Recorded:** 2026-08-20  
**Engine Version:** `2.0.0-alpha.1`  
**Classification:** **`OUTCOME_A_COLLAPSE`** (Information Collapse at Degree-3 Boundary)  
**Ledger References:** `RUN-FB819998A6` (L1), `RUN-5EB6C23E9C` (L2), `RUN-B60EAD867D` (L3), `RUN-5439ABF8CC` (L4) in `evidence/v2_ledger.jsonl`  

---

## 🏛️ 1. Theoretical Hypothesis & Representation Profile

* **Candidate Name:** `quadratic_ideal_mpo`
* **Preserves:** Degree-1 linear terms, degree-2 pairwise monomials ($x_i x_j$), and pairwise clause couplings.
* **Discards:** Monomials and non-linear cycle relations of degree $d \ge 3$.
* **State Size:** $N_{\text{basis}} = 1 + n + \binom{n}{2} = O(n^2)$ polynomial basis elements.
* **Hypothesis:** Truncating the polynomial ideal basis at degree 2 avoids the $O(n)$ collapse of $\mathbb{F}_2$ affine representations while maintaining a strictly polynomial state size ($O(n^2)$), avoiding the exponential $2^{\Omega(n)}$ blowup of unconstrained tensor matricizations.

---

## ⚔️ 2. The 4-Level Q8 Adversarial Escalation Trajectory

```
                                  quadratic_ideal_mpo (CAND-11E3D21E86)
                                                   │
                                                   ▼
                               [LEVEL 1: LINEAR TSEITIN EXPANDERS]
                               • 3-regular Ramanujan expanders (girth g >= 5)
                               • Separation: Δ = 1.0449 (D1 PASS ✅)
                               • Verdict: OUTCOME_D_SURVIVED (90.0% confidence)
                                                   │
                                                   │ [ESCALATE]
                                                   ▼
                            [LEVEL 2: MIXED NON-LINEAR EXPANDERS (d = 2)]
                            • Pairwise cross-couplings (NOT e_i OR NOT e_j)
                            • Separation: Δ = 1.1080 (D1 PASS ✅)
                            • Verdict: OUTCOME_D_SURVIVED (90.0% confidence)
                            • [NOTE: gf2_affine collapsed here!]
                                                   │
                                                   │ [ESCALATE]
                                                   ▼
                            [LEVEL 3: 3-UNIFORM NON-LINEAR EXPANDERS]
                            • Triplet non-linear couplings + linear background
                            • Separation: Δ = 1.0712 (D1 PASS ✅)
                            • Verdict: OUTCOME_D_SURVIVED (90.0% confidence)
                                                   │
                                                   │ [ESCALATE]
                                                   ▼
                       [LEVEL 4: PURE DEGREE-3 TOPOLOGICAL OBSTRUCTIONS]
                       • Degree 1 & Degree 2 projections PROVABLY IDENTICAL
                       • Obstruction exists strictly in degree-3 cycle relations
                       • Separation: Δ = 0.000000 (D1 FAIL ❌)
                       • Verdict: OUTCOME_A_COLLAPSE (98.0% confidence)
                                                   │
                                                   ▼
                             🛑 ESCALATION HALTED AT LEVEL 4
```

---

## 📊 3. Empirical Gate Evaluation Summary

```
┌──────┬──────────────────────────────────┬─────────┬─────────┬─────────┬─────────┬──────────────┬──────────┐
│ GATE │ NAME                             │ LEVEL 1 │ LEVEL 2 │ LEVEL 3 │ LEVEL 4 │ THRESHOLD    │ STATUS   │
├──────┼──────────────────────────────────┼─────────┼─────────┼─────────┼─────────┼──────────────┼──────────┤
│ D1   │ Decision Separation (Δ)          │ 1.0449  │ 1.1080  │ 1.0712  │ 0.0000  │ > 0.0001     │ ❌ FAIL   │
│ D2   │ Representation Memory (KB)       │ 26.6 KB │ 50.9 KB │ 39.9 KB │ 35.6 KB │ < 102400 KB  │ ✅ PASS  │
│ D3   │ Construction Time (ms)           │ 0.19 ms │ 0.35 ms │ 0.28 ms │ 0.22 ms │ < 5000 ms    │ ✅ PASS  │
│ D4   │ Extraction Time (ms)             │ 11.2 ms │ 21.3 ms │ 19.9 ms │ 13.9 ms │ < 5000 ms    │ ✅ PASS  │
│ D5   │ Numerical Condition Number       │ 1.0000  │ 1.0000  │ 1.0000  │ 1.0000  │ < 1.0e+08    │ ✅ PASS  │
│ D6   │ Gauge Shift Invariance           │ 0.0000  │ 0.0000  │ 0.0000  │ 0.0000  │ < 1.0e-06    │ ✅ PASS  │
│ D7   │ Anti-Circularity (Zero Search)   │ 0 steps │ 0 steps │ 0 steps │ 0 steps │ == 0 steps   │ ✅ PASS  │
└──────┴──────────────────────────────────┴─────────┴─────────┴─────────┴─────────┴──────────────┴──────────┘
```

---

## 🔬 4. The Experimental Discovery of the Degree Boundary

This experiment establishes an empirical and algebraic boundary hierarchy:

```
┌─────────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┐
│ REPRESENTATION          │ BASIS DIMENSION      │ SURVIVES             │ COLLAPSES AT         │
├─────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ gf2_affine (Degree 1)   │ O(n)                 │ Level 1 (Linear)     │ Level 2 (Degree 2)   │
├─────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┤
│ quadratic_mpo (Degree 2)│ O(n^2)               │ Level 1, 2, 3        │ Level 4 (Degree 3)   │
└─────────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┘
```

1. **Why it Survived Level 2:**  
   `quadratic_ideal_mpo` explicitly allocates basis vectors for quadratic monomials $x_i x_j$, allowing it to preserve pairwise non-linear clause couplings $(\neg x_i \lor \neg x_j) \iff x_i x_j = 0$ that caused `gf2_affine` to collapse.
2. **Why it Collapsed on Level 4:**  
   When the adversary constructs instances whose linear (degree-1) and pairwise (degree-2) projections are identical, the unsatisfiability lives exclusively in degree-3 monomial cycle relations ($x_i x_j x_k$). Because the degree-2 truncation projects away all monomials of degree $\ge 3$, the carrier observable becomes identical on SAT and UNSAT ($\Delta = 0.000000$).

---

## 🏷️ 5. Epistemic Verdict & Bounded Scope

* **Formal Classification:** **`OUTCOME_A_COLLAPSE`**
* **Confidence:** 98.0% (Verified under independently certified Level-4 adversarial instances in `tests/test_quadratic_mpo.py`).
* **Observed Structural Result:** The tested `quadratic_ideal_mpo` representation preserves separation across linear and pairwise degree-2 non-linear structures ($\Delta \approx 1.1$), but loses separation ($\Delta = 0.0000$) when distinguishing information exists strictly in degree-3 non-linear relations.
* **Scope Boundary:** This empirical finding characterizes the degree-2 truncated polynomial representation under the audited Level-4 family. It demonstrates an exact structural degree boundary ($d=2 \to d=3$).
