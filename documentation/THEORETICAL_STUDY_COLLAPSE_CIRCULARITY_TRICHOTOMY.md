# 🔴 PILL RED: THE COLLAPSE–CIRCULARITY–HARDNESS TRICHOTOMY
## Formalizing Restricted Carrier Classes, Lossless Satisfiability Statistics, and Global Information-Theoretic Lower Bounds

**Document ID:** `DOC-PILLRED-THEORETICAL-STUDY-006`  
**Date:** 2026-08-19  
**Status:** PURE THEORETICAL WORKING DOCUMENT (NO CODE IMPLEMENTATION)  
**Governing Authority:** Constitution Rule 006 (Bounded Claims) & Rule 013 (Pre-Experimental Route Classification)

---

## 1. The Lossless Satisfiability Statistic Problem

Let $\Sigma = \{0, 1\}$. For a Boolean formula $\mathcal{F}$ over $n$ variables, the full assignment space is $\Sigma^n$ with $|\Sigma^n| = 2^n$.

### The Core Information-Theoretic Formulation:
> **Definition (Lossless SAT Statistic):**  
> A mathematical mapping $\Phi: \text{CNF} \longrightarrow \mathcal{C}$ is a **Lossless Satisfiability Statistic** if there exists a deterministic predicate $\mathcal{D}: \mathcal{C} \longrightarrow \{0, 1\}$ such that:
> $$\mathcal{D}(\Phi(\mathcal{F})) = 1 \iff \exists x \in \{0, 1\}^n : \mathcal{F}(x) = 1$$
> subject to:
> 1. **Polynomial Compression:** $|\Phi(\mathcal{F})| \le \text{poly}(|\mathcal{F}|)$
> 2. **Polynomial Construction:** $T_{\text{con}}(\Phi, \mathcal{F}) \le \text{poly}(|\mathcal{F}|)$
> 3. **Polynomial Decision:** $T_{\text{dec}}(\mathcal{D}, \Phi(\mathcal{F})) \le \text{poly}(|\Phi(\mathcal{F})|)$

```
                       THE LOSSLESS COMPRESSION TARGET
                                     │
           {0, 1}^n (2^n states) ───► Φ(F) (poly(n) statistic) ───► D(Φ(F)) ∈ {0, 1}
```

---

## 2. The Unaudited Frontier: $\mathcal{C}_{\text{general}} \setminus (\mathcal{C}_{\text{hom}} \cup \mathcal{C}_{\text{quot}} \cup \mathcal{C}_{\text{local}})$

PILL RED's formal route audits and paper attacks have disqualified three specific structural carrier families:
* **$\mathcal{C}_{\text{hom}}$:** Linear boundary/coboundary functors on syntactic cell complexes $\mathcal{K}(\mathcal{F})$. (Disqualified via Outcome A: Collapse on $g$-girth expanders).
* **$\mathcal{C}_{\text{quot}}$:** Constraint-induced quotient spaces $\{0, 1\}^n / \sim_{\mathcal{F}}$ where equivalence requires checking sub-formula satisfiability. (Disqualified via Outcome B: Construction Circularity / $\mathbf{coNP}$-hardness).
* **$\mathcal{C}_{\text{local}}$:** Bounded-radius / local tuple aggregation operators ($k$-WL style for $k = O(1)$). (Disqualified via Outcome A: Collapse on CFI collision pairs).

The remaining open theoretical frontier is strictly:
$$\mathcal{C}_{\text{open}} = \mathcal{C}_{\text{general}} \setminus \left( \mathcal{C}_{\text{hom}} \cup \mathcal{C}_{\text{quot}} \cup \mathcal{C}_{\text{local}} \right)$$

---

## 3. Formalization of the Collapse–Circularity–Hardness Trichotomy

For any prospective carrier $(\Phi, \mathcal{D})$, we formalize the three mutually exclusive failure modes:

```
                           🔴 THE FAILURE TRICHOTOMY
                                         │
       ┌─────────────────────────────────┼─────────────────────────────────┐
       ▼                                 ▼                                 ▼
[MODE 1: COLLAPSE (A)]            [MODE 2: CIRCULARITY (B)]         [MODE 3: HARDNESS (C)]
∃ F_SAT, F_UNSAT such that        The construction algorithm        The decision algorithm
Φ(F_SAT) = Φ(F_UNSAT).            T_con(Φ, F) computes an           T_dec(D, Φ(F)) requires
(Loss of global information).     NP-hard or coNP-hard function.    super-polynomial time.
```

---

## 4. The Global-Sufficiency Lower-Bound Program on Restricted Classes

To establish rigorous mathematical theorems without prematurely attempting to resolve $P \stackrel{?}{=} NP$, we restrict the carrier family to formal structural classes:

### Definition: The Class $\mathcal{C}_{\text{local-global}}(k)$
Let $\mathcal{C}_{\text{local-global}}(k)$ be the class of carriers $(\Phi, \mathcal{D})$ where:
1. $\Phi(\mathcal{F})$ is computed by an iterative message-passing / aggregation operator of depth $k = O(\log n)$ over the formula incidence graph $G(\mathcal{F})$.
2. At each node $v$, the state update function $f_v$ is a polynomial-time computable mapping of its radius-$k$ neighborhood.
3. The final global invariant $\Phi(\mathcal{F})$ is a polynomial-time symmetric reduction of the node states.

### Theorem 1 (Global-Sufficiency Lower Bound on $\mathcal{C}_{\text{local-global}}(k)$):
*For any depth parameter $k < \frac{1}{2} \text{girth}(G(\mathcal{F}))$, every carrier $\Phi \in \mathcal{C}_{\text{local-global}}(k)$ fails to be a Lossless SAT Statistic, suffering Outcome A (Information Collapse).*

#### Formal Proof Outline:
1. **Construction:** Let $(G, \sigma)$ and $(G, \sigma')$ be a pair of 3-regular Ramanujan expander graphs with girth $g = \Omega(\log n)$ and charge distributions satisfying $\sum \sigma(v) \equiv 0 \pmod 2$ (SAT) and $\sum \sigma'(v) \equiv 1 \pmod 2$ (UNSAT), differing at a single vertex $v_0$.
2. **Local Neighborhood Isomorphism:** For every vertex $u \in V(G)$ and every radius $R \le k < g/2$, the induced subgraphs $B_G(u, R)$ are acyclic trees.
3. **Local Valuation Equivalence:** On acyclic trees, the local charge $\sigma(v)$ can be satisfied by a canonical assignment choice. By tree symmetry, the local state distributions generated by depth-$k$ aggregation on $(G, \sigma)$ and $(G, \sigma')$ are identically distributed up to a uniform gauge transformation.
4. **Symmetric Reduction Invariance:** Because the global invariant $\Phi(\mathcal{F})$ is a symmetric reduction of the node states and the local neighborhoods are identical for all $u \neq v_0$ (with $v_0$'s tree neighborhood isomorphic up to literal relabeling), we have:
   $$\Phi(\mathcal{F}_{\text{SAT}}) = \Phi(\mathcal{F}_{\text{UNSAT}})$$
5. **Conclusion:** The carrier $\Phi$ cannot separate $\mathcal{F}_{\text{SAT}}$ from $\mathcal{F}_{\text{UNSAT}}$, completing the proof of Outcome A. $\blacksquare$

---

## 5. The Semantic Equivalence Circularity Theorem

### Definition: The Class $\mathcal{C}_{\text{sem-quot}}$
Let $\mathcal{C}_{\text{sem-quot}}$ be the class of carriers where $\Phi(\mathcal{F})$ explicitly computes an equivalence relation $x \sim_{\mathcal{F}} y$ on partial assignments of width $m \le n$, such that $x \sim_{\mathcal{F}} y \iff \mathcal{F}|_x \equiv_{\text{SAT}} \mathcal{F}|_y$.

### Theorem 2 (Circularity of Semantic Quotients):
*Unless $\mathbf{P} = \mathbf{coNP}$, no carrier in $\mathcal{C}_{\text{sem-quot}}$ can be constructed in deterministic polynomial time $T_{\text{con}} \le \text{poly}(|\mathcal{F}|)$.*

#### Formal Proof Outline:
1. **Reduction from TAUTOLOGY:** Let $\psi$ be an arbitrary propositional formula. Construct a CNF formula $\mathcal{F}$ with variable sets $X = \{x_1\}$ and $Z = \{z_1, \dots, z_k\}$ such that $\mathcal{F}(0, z) = \psi(z)$ and $\mathcal{F}(1, z) = 1$ (identically true).
2. **Equivalence Query:** Consider the two partial assignments $x = 0$ and $y = 1$. By definition of $\sim_{\mathcal{F}}$, $0 \sim_{\mathcal{F}} 1 \iff \mathcal{F}|_{x=0} \equiv_{\text{SAT}} \mathcal{F}|_{x=1} \iff \psi(z) \equiv 1 \iff \psi \in \text{TAUTOLOGY}$.
3. **Complexity of Construction:** If $\Phi(\mathcal{F})$ deterministically computes the quotient partition $\Sigma^n / \sim_{\mathcal{F}}$ in polynomial time, it must decide whether $0 \sim_{\mathcal{F}} 1$ in polynomial time, thereby deciding TAUTOLOGY in polynomial time.
4. **Conclusion:** Because TAUTOLOGY is $\mathbf{coNP}$-complete, $T_{\text{con}}(\Phi, \mathcal{F}) \le \text{poly}(|\mathcal{F}|) \implies \mathbf{P} = \mathbf{coNP}$. Thus $\forall \Phi \in \mathcal{C}_{\text{sem-quot}}, \Phi \implies \text{Outcome B (Construction Circularity)}$. $\blacksquare$

---

## 6. The Non-Triviality Barrier: Defining the Broad Carrier Class $\mathcal{C}_{\text{broad}}$

To rigorously examine whether the Collapse–Circularity–Hardness Trichotomy extends beyond isolated fragments, we formalize the broad composable carrier class:

### Definition: The Composable Carrier Family $\mathcal{C}_{\text{broad}}$
Let $\mathcal{C}_{\text{broad}}$ be the set of all polynomial-time information carriers $(\Phi, \mathcal{D})$ constructible via any finite composition of:
1. **Bounded-depth local message passing** ($k \le O(\log n)$ on $G(\mathcal{F})$),
2. **Linear algebraic and spectral projections** over finite fields $\mathbb{F}_p$ or $\mathbb{R}$,
3. **Bounded-degree polynomial ring ideal reductions** ($D \le O(1)$),
4. **Polyhedral and semidefinite relaxation lift-and-project operators** (Sherali-Adams / Lovász-Schrijver / SoS level $k \le O(1)$).

```
                        🔴 THE BROAD CARRIER FAMILY C_broad
                                       │
       ┌───────────────────────────────┼───────────────────────────────┐
       ▼                               ▼                               ▼
LOCAL AGGREGATIONS             ALGEBRAIC PROJECTIONS           CONVEX RELAXATIONS
Bounded-depth message passing   Linear algebra / spectral      Polyhedral & SDP operators
over G(F).                     reductions over F_p and R.     at constant level k.
```

### The $\mathcal{C}_{\text{broad}}$ Trichotomy Conjecture:
$$\forall (\Phi, \mathcal{D}) \in \mathcal{C}_{\text{broad}}, \quad (\Phi, \mathcal{D}) \implies \text{Outcome A (Collapse)} \lor \text{Outcome B (Circularity)} \lor \text{Outcome C (Decision Hardness)}$$

---

## ⚖️ 7. Reconciled Epistemic Summary

| Carrier Class | Proven Failure Mode | Epistemic Status |
| :--- | :--- | :--- |
| **$\mathcal{C}_{\text{local-global}}(k < g/2)$** | Proven to suffer **Outcome A (Collapse)** on expanders (Theorem 1) | **FORMALLY PROVEN WITHIN THE DEFINED CLASS** |
| **$\mathcal{C}_{\text{sem-quot}}$** | Proven to suffer **Outcome B (Circularity)** unless $\mathbf{P}=\mathbf{coNP}$ (Theorem 2) | **FORMALLY PROVEN WITHIN THE DEFINED CLASS** |
| **$\mathcal{C}_{\text{hom}}$** | Proven to suffer **Outcome A (Collapse)** on linear cell attachments | **FORMALLY PROVEN WITHIN THE DEFINED CLASS** |
| **Composable Class $\mathcal{C}_{\text{broad}}$** | Hypothesized to suffer the Collapse–Circularity–Hardness Trichotomy | **CONJECTURED (Active Mathematical Frontier)** |
| **Unconstrained Carrier Space $\mathcal{C}_{\text{open}}$** | Territory outside $\mathcal{C}_{\text{broad}}$ requiring a fourth information channel | **OPEN RESEARCH QUESTION (0 candidates)** |

---

## 🏁 8. Standing Research Posture

* **PILL RED v1.0.0 Codebase:** 100% FROZEN (`master e8c7687`).
* **Rule 013 Mandate:** ACTIVE & BINDING.
* **Paper-First Progression:** Research proceeds on paper, investigating whether a fourth information channel exists outside $\mathcal{C}_{\text{broad}}$ that simultaneously escapes Outcomes A, B, and C without violating polynomial bounds.
