# 🔴 PILL RED: THEORETICAL STUDY — RESEARCH LEAD 16
## The Invariant-First Formulation: Field-Agnostic Specification & Falsification Audits

**Document ID:** `DOC-PILLRED-THEORETICAL-STUDY-LEAD-016`  
**Date:** 2026-08-19  
**Status:** STEP 1 (DISCOVER) — INVARIANT SPECIFICATION & FALSIFICATION TARGETING  
**Governing Authority:** Constitution Rule 006 (Bounded Claims) & Rule 013 (Pre-Experimental Route Classification)

---

## 1. The Pure Invariant Problem (Field-Agnostic Specification)

We isolate the mathematical target $\mathcal{I}(\mathcal{F})$ with **zero domain assumptions** (no imported topology, quantum mechanics, category theory, or tensor networks):

```
                         🔴 THE PURE INVARIANT TARGET
                                       │
                      F (3-CNF Formula on Expander Graph)
                                       │
                                       ▼
                 I(F) ∈ {0, 1} (or 𝕂) : Deterministic Scalar
```

### 1.1 The Four Invariant Axioms

An invariant $\mathcal{I}: \text{3-CNF} \longrightarrow \{0, 1\}$ belongs to the **Category-D Class** if and only if it simultaneously satisfies:

1. **Axiom 1 (Global Boolean Sensitivity):**
   $$\mathcal{I}(\mathcal{F}_{\text{SAT}}) = 1 \quad \text{and} \quad \mathcal{I}(\mathcal{F}_{\text{UNSAT}}) = 0$$
   for every expander collision pair $(\mathcal{F}_{\text{SAT}}, \mathcal{F}_{\text{UNSAT}})$.
2. **Axiom 2 (Tree-Gauge Insensitivity):**
   $$\mathcal{I}(\mathcal{F}) = \mathcal{I}(\mathcal{F}')$$
   whenever $\mathcal{F}$ and $\mathcal{F}'$ are related by a local gauge transformation on all acyclic balls $B_G(v, R)$ of radius $R < g/2$ (where $g = \Omega(\log n)$ is the graph girth).
3. **Axiom 3 (Deterministic Polynomial Computability):**
   $$T_{\text{eval}}(\mathcal{I}, \mathcal{F}) \le \text{poly}(|\mathcal{F}|)$$
   requiring at most $O(n^c)$ bit operations on a deterministic Turing machine.
4. **Axiom 4 (Anti-Circularity):**
   The evaluation of $\mathcal{I}(\mathcal{F})$ does not compute or require a satisfying assignment $\mathbf{x}^* \in \{0, 1\}^n$, nor does it solve an $\mathbf{NP}$-hard, $\mathbf{coNP}$-hard, or $\#\mathbf{P}$-hard sub-problem.

---

## 2. The Benchmark Analysis: Why Linear Parity (XOR-SAT) Has a Solution

To understand what a successful invariant $\mathcal{I}$ must accomplish, we analyze the known tractable case: **Linear Parity (XOR-SAT / Tseitin on Expanders)**.

```
                           THE LINEAR BENCHMARK (XOR-SAT)
                                         │
                 System: B x ≡ σ (mod 2) on Expander Graph G
                                         │
                                         ▼
            I_linear(F) = 1 ⟺ rank_𝔽₂([B | σ]) = rank_𝔽₂(B)
```

* **Why $\mathcal{I}_{\text{linear}}$ Works for XOR-SAT:**
  1. *Tree-Gauge Insensitive:* On any acyclic tree $T$, $\text{rank}_{\mathbb{F}_2}(\mathbf{B}|_T) = |V(T)| - 1$. Local gauge transformations do not change the row echelon invariants.
  2. *Global Sensitivity:* A single parity defect shifts the total charge $\sum \sigma(v) \equiv 1 \pmod 2$, which alters the global rank equation across cycle generators.
  3. *Polynomial Time:* Gaussian elimination over $\mathbb{F}_2$ computes the rank in $O(n^3)$ operations without exponential state enumeration.
  4. *Anti-Circular:* Gaussian elimination determines *existence* of a solution without searching through $2^n$ candidates.

---

## 3. The Non-Linear 3-SAT Obstruction

When we transition from XOR-SAT to general 3-SAT, the constraint relations become non-linear:
$$c_j = (l_1 \lor l_2 \lor l_3) \iff (1 - l_1)(1 - l_2)(1 - l_3) = 0$$

```
                         🔴 THE NON-LINEAR GAP
                                   │
      LINEAR (XOR-SAT)                           NON-LINEAR (3-SAT)
      • Basis: F_2 vectors.                      • Basis: Degree-3 monomials.
      • Cycle interactions: Additive (mod 2).    • Cycle interactions: Multiplicative / Branching.
      • Solution space: Affine subspace.         • Solution space: Disjoint discrete points.
      • Exact Invariant: F_2 Rank / Det.         • Invariant: ??? (Must bridge cycles non-linearly).
```

---

## 4. The Candidate Kill Theorems (Falsification Targets)

Before proposing any specific mathematical construction for $\mathcal{I}(\mathcal{F})$, we formulate the **three Kill Theorems** that threaten any candidate invariant:

```
                      🔴 THE THREE KILL THEOREMS
                                   │
    ┌──────────────────────────────┼──────────────────────────────┐
    ▼                              ▼                              ▼
[KILL THEOREM A]               [KILL THEOREM B]               [KILL THEOREM C]
The Local-Global Factorization The Non-Affine Degree Bound    The Information-Dispersion
Theorem (Linear Collapse).     Theorem (Monomial Explosion).  Theorem (Entropy Trap).
```

### 🚨 Kill Theorem A: The Local-Global Factorization Barrier
* **Statement:** Any scalar invariant $\mathcal{I}(\mathcal{F})$ computable by uniform polynomial-size circuits that is invariant under all local tree-gauge transformations on balls $B(v, R)$ factors through the abelianized homology group $H_1(G; \mathbb{F}_2) \cong \mathbb{F}_2^{|E| - |V| + 1}$.
* **Consequence if True:** $\mathcal{I}(\mathcal{F})$ can only evaluate affine linear parity (XOR-SAT). For general 3-SAT, it is blind to non-linear clause conjunctions $\implies$ **Outcome A (Information Collapse)**.

### 🚨 Kill Theorem B: The Non-Affine Degree Lower Bound
* **Statement:** Any polynomial ideal representation $I_{\mathcal{F}}$ over a field $\mathbb{K}$ that separates SAT from UNSAT on expander Tseitin/3-SAT instances requires refutation degree:
  $$\text{Deg}(I_{\mathcal{F}} \vdash 1) = \Omega(n)$$
* **Consequence if True:** Any algebraic invariant tracking non-linear cycle couplings requires evaluating a vector space of dimension $\binom{n}{\Omega(n)} = 2^{\Omega(n)} \implies$ **Outcome C (Exponential Monomial Explosion)**.

### 🚨 Kill Theorem C: The Information-Dispersion / Entanglement Barrier
* **Statement:** On a $d$-regular Ramanujan expander, the global satisfiability bit is delocalized such that any bipartition $(A, B)$ with $|A| = |B| = n/2$ has mutual information $I(A; B \mid \mathcal{F}) = \Omega(n)$.
* **Consequence if True:** Any invariant $\mathcal{I}$ that compresses the state across cut $(A, B)$ to $\text{poly}(n)$ bits discards the mutual information $\implies$ **Outcome A (Information Collapse)**.

---

## ⚖️ 5. The Critical Research Challenge for Lead 16

To survive the Falsification Gate, **Lead 16** must formulate an invariant $\mathcal{I}(\mathcal{F})$ that:
1. Is **strictly non-affine** (bypassing Kill Theorem A).
2. Does **not rely on bounded-degree polynomial ideal expansions** (bypassing Kill Theorem B).
3. Does **not compress across cut boundaries using low-rank tensor/spectral projections** (bypassing Kill Theorem C).

```
┌──────────────────────────────────────────────────────────────────────────────────────┐
│ LEAD 16 STATUS: INVARIANT TARGET SPECIFIED — STANDING BEFORE FALSIFICATION GATE      │
├──────────────────────────────────────────────────────────────────────────────────────┤
│ No mathematical field is yet assumed. The target is a non-affine scalar invariant   │
│ I(F) that proves immunity to Kill Theorems A, B, and C simultaneously.               │
└──────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🏁 6. Standing Research Posture

* **Audited Negative Space:** 15 Scoped Paradigms (Sealed).
* **Lead 16 Invariant Target:** Formally specified and isolated.
* **Codebase State:** 100% FROZEN (`master 30995a1`).
* **Rule 013 Mandate:** ACTIVE & BINDING.

**Ready to analyze whether any proposed invariant $\mathcal{I}(\mathcal{F})$ can escape Kill Theorems A, B, and C.**
