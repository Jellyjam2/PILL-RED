# 🔴 PILL RED v2.0 Formal Contract: D1–D7 Gates & Q8 Adversarial Protocol

**Document ID:** `DOC-PILLRED-V2-CONTRACT-001`  
**Status:** BINDING ARCHITECTURAL SPECIFICATION  
**Branch:** `engine-v2`  

---

## 🏛️ 1. Epistemic Principles of the v2 Contract

1. **Pre-Implementation Specification:** All gates, scaling criteria, and classification rules are defined here *before* engine code execution.
2. **Separation of Observation from Interpretation:** Raw empirical metrics (time, memory, bits, separation $\Delta$, conflicts) are recorded as first-class facts before any Trilemma label is applied.
3. **Independent Ground Truth:** Candidates never define or certify their own satisfiability. An independent verifier module (`IVR`) establishes and validates witness certificates.
4. **Asymptotic Scaling over Clock Time:** Polynomial complexity is evaluated via empirical scaling profiles over increasing instance size $n$, not arbitrary millisecond thresholds.
5. **Outcome D Scope:** An Outcome D verdict means *"The candidate representation survived all current adversarial crucible levels without triggering A, B, or C."* It does **not** assert a universal proof of $P = NP$.

---

## 🧭 2. The 7 Formal Gates (D1–D7)

```
┌──────┬──────────────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ GATE │ NAME                             │ FORMAL ACCEPTANCE CRITERION                                            │
├──────┼──────────────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ D1   │ Decision Correctness / Separation│ ‖Φ(F_SAT) - Φ(F_UNSAT)‖ > τ_threshold across all tested pairs.         │
│ D2   │ Representation Size Scaling      │ Bit size S(n) <= O(n^k) with empirical degree k <= 4.                  │
│ D3   │ Construction Complexity          │ Operation count T_con(n) <= O(n^k) with zero exponential scaling.       │
│ D4   │ Decision Extraction Complexity   │ Extraction time T_dec(n) <= O(n^k) without exponential branching.      │
│ D5   │ Numerical & Precision Stability  │ Precision required <= O(log n) bits; condition number κ(n) <= poly(n). │
│ D6   │ Local Tree-Gauge Invariance      │ ‖Φ(F) - Φ(F_gauge)‖ <= 1e-6 under all local tree automorphism shifts.  │
│ D7   │ Anti-Circularity & Zero Search   │ Zero NP/co-NP oracle calls or clause resolution during construction.   │
└──────┴──────────────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```

### Detailed Gate Specifications

#### Gate D1: Decision Correctness & Separation
* **Metric:** Separation gap $\Delta(\Phi) = |\mathcal{O}(\Phi(F_{\text{SAT}})) - \mathcal{O}(\Phi(F_{\text{UNSAT}}))|$.
* **Pass Condition:** $\Delta(\Phi) \ge \tau$ for all tested instances in a family, where $\tau > 0$ is a fixed resolution margin.
* **Failure Mode:** If $\Delta(\Phi) = 0$ on non-trivial pairs, the candidate fails D1.

#### Gate D2: Representation Size Scaling
* **Metric:** Bit-length $S(n)$ of the constructed carrier (e.g. matrix dimension $N \times N$, tensor bond dimension $\chi$, polynomial basis count).
* **Pass Condition:** $\log_2 S(n) / \log_2 n \le k_{\max}$ as $n \to \infty$.
* **Failure Mode (Outcome C):** If $S(n) = 2^{\Omega(n)}$ (e.g. exponential tensor rank or full monomial basis).

#### Gate D3: Construction Complexity
* **Metric:** Operation count $T_{\text{con}}(n)$ and wall-clock scaling exponent $\alpha$ where $T(n) \approx c \cdot n^\alpha$.
* **Pass Condition:** Empirical scaling exponent $\alpha \le 4.0$.
* **Failure Mode (Outcome B/C):** Super-polynomial scaling or timeouts on scaling sweeps.

#### Gate D4: Decision Extraction Complexity
* **Metric:** Operation count $T_{\text{dec}}(n)$ to extract a Boolean decision from the carrier.
* **Pass Condition:** Evaluation requires $O(n^k)$ operations (e.g. spectral eigenvalue, determinant, rank).
* **Failure Mode (Outcome B/C):** Extraction requires enumerating exponentially many paths, permanent evaluation, or SAT solving.

#### Gate D5: Numerical Stability & Bit Precision
* **Metric:** Matrix condition number $\kappa(M) = \sigma_{\max} / \sigma_{\min}$ and bit precision $p(n)$ needed to prevent catastrophic cancellation.
* **Pass Condition:** $\log_2 \kappa(n) \le O(\log n)$, precision $\le 64$ bits.
* **Failure Mode (Outcome C):** Precision explosion $\epsilon \le 2^{-\Omega(n)}$ (e.g. continuous chaotic flow, Henon saddles).

#### Gate D6: Local Tree-Gauge Invariance
* **Metric:** Variance of observable under local parity-preserving tree-gauge transformations:
  $$\text{Var}_{\text{gauge}}(\Phi) = \mathbb{E}_{\psi \in \text{TreeAut}} \left[ |\mathcal{O}(\Phi(F)) - \mathcal{O}(\Phi(\psi(F)))|^2 \right]$$
* **Pass Condition:** $\text{Var}_{\text{gauge}}(\Phi) < 10^{-10}$.
* **Failure Mode (Outcome A):** Candidate observable changes under local gauge transformations that preserve formula satisfiability.

#### Gate D7: Anti-Circularity & Zero Hidden Search
* **Metric:** Count of internal variable assignments, CDCL conflict clauses, or DPLL branching steps executed during `construct()`.
* **Pass Condition:** Internal search steps $= 0$.
* **Failure Mode (Outcome B):** Candidate secretly executes SAT search or requires finding a satisfying witness to build the carrier.

---

## ⚔️ 3. The Q8 Adversarial Escalation Protocol

Q8 is not a single static check, but an **adaptive 4-level escalation protocol**:

```
                              Q8 ADVERSARIAL ESCALATION
                                          │
        ┌─────────────────────────────────┼─────────────────────────────────┐
        ▼                                 ▼                                 ▼
   [LEVEL 0: SANITY]              [LEVEL 1: EXPANDER]               [LEVEL 2: ADAPTIVE]
   • Small Horn / 2-SAT           • High-girth Ramanujan expanders  • Targeted observable attacks
   • Uncorrelated 3-SAT           • Tseitin parity collisions       • Gradient-guided instance
   • Direct contradictions        • Non-trivial local trees           surgery to nullify Δ(Φ)
```

* **Level 0 (Sanity):** Simple structural pairs to verify basic solver correctness and non-triviality.
* **Level 1 (Expander Collisions):** High-girth expander graph formulas ($g \ge 5$) where SAT and UNSAT instances share identical 2-hop tree neighborhoods.
* **Level 2 (Iso-Algebraic Collisions):** Formulas with identical low-degree spectral and algebraic projections but differing global satisfiability.
* **Level 3 (Adaptive Adversary / SMT Synthesis):** Synthesizes minimal formula perturbations that specifically maximize the candidate's blind spot while flipping satisfiability.

---

## 🏷️ 4. The 5-State Trilemma Classification Taxonomy

Every candidate evaluated by the Automated Crucible Engine (ACE) receives one of five formal outcomes:

```
┌─────────────────────────┬────────────────────────────────────────────────────────────────────────┐
│ OUTCOME                 │ MATHEMATICAL CRITERION                                                 │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ OUTCOME_A_COLLAPSE      │ Fails D1 or D6 on Level 1/2 expander collisions. Tractable (D2-D4 pass)│
│                         │ but projects away global parity information.                           │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ OUTCOME_B_CIRCULARITY   │ Fails D7 (executes hidden SAT search) or construction requires solving │
│                         │ an NP-hard subproblem to preserve exact discrete logic.                │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ OUTCOME_C_BLOWUP        │ Fails D2, D4, or D5. Exact representation requires exponential rank,   │
│                         │ exponential bit precision (2^-Ω(n)), or exponential orbit sums.        │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ OUTCOME_D_SURVIVED      │ Passes ALL gates (D1–D7) across ALL available Q8 adversarial levels.   │
│                         │ Candidate is flagged for higher-level adversarial escalation.          │
├─────────────────────────┼────────────────────────────────────────────────────────────────────────┤
│ UNKNOWN_INCONCLUSIVE    │ Inconsistent gate measurements, numerical solver crashes, or data      │
│                         │ insufficient to distinguish failure mechanism.                         │
└─────────────────────────┴────────────────────────────────────────────────────────────────────────┘
```
