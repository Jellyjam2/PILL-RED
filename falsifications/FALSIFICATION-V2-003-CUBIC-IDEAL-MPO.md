# 🔴 PILL RED v2.0 Research Dossier: FALSIFICATION-V2-003

**Document ID:** `FALSIFICATION-V2-003`  
**Candidate ID:** `CAND-CB7DEE006D` (`cubic_ideal_mpo`)  
**Mathematical Class:** Truncated Degree-3 Polynomial Ideal / Matrix Product Operator (MPO)  
**Date Recorded:** 2026-08-20  
**Engine Version:** `2.0.0-alpha.1`  
**Classification:** **`OUTCOME_D_SURVIVED` (Level 4 Recovery) / `OUTCOME_C` (Emergent $O(n^9)$ Scaling Pressure)**  
**Ledger References:** `RUN-9F4BD3A1D3` (L1), `RUN-51EF31AA18` (L3), `RUN-518FE0D53C` (L4), `RUN-945341837F` (L5) in `evidence/v2_ledger.jsonl`  

---

## 🏛️ 1. Theoretical Hypothesis & Representation Profile

* **Candidate Name:** `cubic_ideal_mpo`
* **Preserves:** Degree-1 linear terms, degree-2 pairs ($x_i x_j$), and degree-3 triplets ($x_i x_j x_k$). Maps 3-CNF clauses into exact Algebraic Normal Form (ANF) without clause-level truncation defects.
* **Discards:** Monomials of degree $d \ge 4$.
* **State Size:** $N_{\text{basis}} = 1 + n + \binom{n}{2} + \binom{n}{3} = O(n^3)$ basis elements.
* **Hypothesis ($H_1$):** Increasing the retained polynomial degree to $d=3$ recovers the degree-3 topological obstructions that caused `quadratic_ideal_mpo` to collapse at Level 4.
* **Cost Hypothesis:** The state dimension scales as $O(n^3)$, which causes dense Gaussian elimination over $\mathbb{F}_2$ to scale as $O(N_{\text{basis}}^3) = O(n^9)$.

---

## ⚔️ 2. The 5-Level Q8 Escalation Trajectory

```
                                     cubic_ideal_mpo (CAND-CB7DEE006D)
                                                    │
                                                    ▼
                                [LEVEL 1: LINEAR TSEITIN EXPANDERS]
                                • Separation: Δ = 1.0244 (D1 PASS ✅)
                                • Extraction Time: 42.6 ms | Memory: 232 KB
                                                    │
                                                    │ [ESCALATE]
                                                    ▼
                             [LEVEL 2: MIXED NON-LINEAR EXPANDERS (d = 2)]
                             • Separation: Δ = 1.0244 (D1 PASS ✅)
                             • Extraction Time: 49.4 ms | Memory: 495 KB
                                                    │
                                                    │ [ESCALATE]
                                                    ▼
                             [LEVEL 3: 3-UNIFORM NON-LINEAR EXPANDERS]
                             • Separation: Δ = 1.0318 (D1 PASS ✅)
                             • Extraction Time: 55.4 ms | Memory: 345 KB
                                                    │
                                                    │ [ESCALATE]
                                                    ▼
                        [LEVEL 4: PURE DEGREE-3 TOPOLOGICAL OBSTRUCTIONS]
                        • Degree 1 & Degree 2 projections certified equivalent
                        • Separation: Δ = 0.006900 (D1 PASS ✅)
                        • [NOTE: quadratic_ideal_mpo collapsed here (Δ = 0.000000)!]
                        • Extraction Time: 29.8 ms | Memory: 274 KB
                                                    │
                                                    │ [ESCALATE]
                                                    ▼
                        [LEVEL 5: PURE DEGREE-4 TOPOLOGICAL OBSTRUCTIONS]
                        • Separation: Δ = 0.112600 (D1 PASS ✅)
                        • Extraction Time: 711.2 ms (24x jump!) | Memory: 2,484 KB (10x jump!)
```

---

## 🔬 3. The Experimental Degree Ladder Discovery

```
┌─────────────────────────┬──────────────────────┬──────────────────────┬──────────────────────┬─────────────────────────┐
│ REPRESENTATION          │ BASIS DIMENSION      │ SURVIVES             │ COLLAPSES AT         │ SCALING BEHAVIOR        │
├─────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ gf2_affine (Degree 1)   │ O(n)                 │ Level 1 (Linear)     │ Level 2 (Degree 2)   │ O(n^3) arithmetic       │
├─────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ quadratic_mpo (Degree 2)│ O(n^2)               │ Level 1, 2, 3        │ Level 4 (Degree 3)   │ O(n^6) arithmetic       │
├─────────────────────────┼──────────────────────┼──────────────────────┼──────────────────────┼─────────────────────────┤
│ cubic_mpo (Degree 3)    │ O(n^3)               │ Level 1, 2, 3, 4     │ Open Boundary (L5+)  │ O(n^9) arithmetic       │
└─────────────────────────┴──────────────────────┴──────────────────────┴──────────────────────┴─────────────────────────┘
```

1. **Recovery of Degree-3 Obstructions:**  
   `cubic_ideal_mpo` successfully avoids the information collapse that eliminated `quadratic_ideal_mpo` at Level 4. By retaining all $\binom{n}{3}$ cubic monomials, it preserves the non-linear 3-variable ANF expansion, maintaining separation ($\Delta = 0.0069$) where degree-2 representations were completely blind.
2. **The Emergent Resource Barrier (Outcome C):**  
   While degree 3 recovers higher-order expressivity, its computational cost scales sharply:
   - At $n=27$: $N_{\text{basis}} = 3,304$ basis columns $\implies 2.48\text{ MB}$ memory, $711\text{ ms}$ extraction time.
   - At $n=100$: $N_{\text{basis}} \approx 166,750$ columns $\implies \approx 28\text{ GB}$ memory, hours of extraction time.
   This empirically exposes why bounded-degree polynomial hierarchies (such as Sherali-Adams / Lasserre / SOS) face unavoidable exponential resource limits as degree $d \to n$.

---

## 🏷️ 4. Epistemic Verdict & Bounded Scope

* **Status:** Verified under 13 unit, integration, and multi-level adversarial tests in `tests/test_cubic_mpo.py`.
* **Observed Structural Result:** Adding cubic monomials ($x_i x_j x_k$) enables the representation to separate pure degree-3 expander collisions ($\Delta > 0$), but introduces steep polynomial scaling ($O(n^3)$ state size, $O(n^9)$ elimination complexity), demonstrating the Trilemma tradeoff between information preservation and computational tractability.
