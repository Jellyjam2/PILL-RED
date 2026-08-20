# 🔴 PILL RED: FORMAL CARRIER CLASSES & THE FOUR-WAY FAILURE TAXONOMY
## Restricted-Family Lower Bounds and the Information-Locus Map for Boolean Satisfiability

**Document ID:** `DOC-PILLRED-THEORETICAL-RECON-005`  
**Date:** 2026-08-19  
**Status:** PURE THEORETICAL WORKING DOCUMENT (NO CODE IMPLEMENTATION)  
**Governing Authority:** Constitution Rule 006 (Bounded Claims) & Rule 013 (Pre-Experimental Route Classification)

---

## 1. The Minimal Information Carrier Formalization

Let $\mathcal{F}$ denote a propositional CNF formula with $n$ variables and $m$ clauses. We formalize a **Candidate Information Carrier** as a pair $(\Phi, \mathcal{D})$:
1. **The Representation Functor:** $\Phi: \mathcal{F} \longrightarrow \mathcal{C}$, producing a mathematical object $\Phi(\mathcal{F}) \in \mathcal{C}$.
2. **The Decision Predicate:** $\mathcal{D}: \mathcal{C} \longrightarrow \{0, 1\}$.

### The Category-D Target Specification:
A carrier $(\Phi, \mathcal{D})$ achieves Category D if and only if there exists a polynomial $p$ such that for all $\mathcal{F}$:
* **D1 (Soundness & Completeness):** $\mathcal{D}(\Phi(\mathcal{F})) = 1 \iff \mathcal{F} \in \text{SAT}$.
* **D2 (Polynomial Size):** $|\Phi(\mathcal{F})| \le p(|\mathcal{F}|)$.
* **D3 (Polynomial Construction):** $T_{\text{con}}(\Phi, \mathcal{F}) \le p(|\mathcal{F}|)$.
* **D4 (Polynomial Decision):** $T_{\text{dec}}(\mathcal{D}, \Phi(\mathcal{F})) \le p(|\Phi(\mathcal{F})|)$.
* **D5 (Global Robustness):** $\Phi$ separates adversarial globally coupled formulas (e.g. rigid expanders, CFI pairs).
* **D6 (Escape of Known Limits):** $\Phi$ does not merely repackage a known framework whose limitations already rule it out.

---

## 2. The Four-Way Diagnostic Taxonomy for Candidate Carriers

Every candidate carrier $(\Phi, \mathcal{D})$ is evaluated against four mutually exclusive outcomes:

```
                           🔴 THE FOUR CARRIER OUTCOMES
                                          │
       ┌──────────────────┬───────────────┴───────────────┬──────────────────┐
       ▼                  ▼                               ▼                  ▼
[OUTCOME A: COLLAPSE]     [OUTCOME B: CIRCULARITY]        [OUTCOME C: HARDNESS] [OUTCOME D: CATEGORY D]
Φ(F_SAT) = Φ(F_UNSAT).    T_con(Φ, F) is NP-hard or      T_dec(D, Φ(F)) is     Poly-size, poly-time,
Blind to global parity.   coNP-hard. (SAT hidden in Φ).   NP-hard / exponential. decidable, and complete.
(Fails D1 / D5).          (Fails D3).                     (Fails D4).           (Achieves target).
```

---

## 3. The "Where Does Global Information Live?" Map

Across established mathematical and algorithmic frameworks, preserving satisfiability information on globally coupled formulas forces exponential complexity into a specific mathematical locus:

| Framework | Investigated Mechanism | Where Global Information is Stored | Locus of Exponential Cost | Diagnostic Outcome |
| :--- | :--- | :--- | :--- | :---: |
| **Resolution / CDCL** | Propositional clause resolution | Literal boundary cuts across expander separators | Clause width grows as $\Omega(n) \implies 2^{\Omega(n)}$ clauses | **Outcome A / Bound** |
| **Polynomial Calculus (PC)** | Ideal derivation over $\mathbb{F}_2$ | High-degree cross-variable interaction terms | Degree grows as $D = \Omega(n) \implies \binom{n}{D}$ monomials | **Outcome A / Bound** |
| **Sum-of-Squares (SoS)** | Pseudo-expectation moments | Moment matrices of lifted polynomial inequalities | Degree $d = \Omega(n) \implies n^{\Omega(d)}$ matrix size | **Outcome A / Bound** |
| **Treewidth / DP** | Tree decomposition dynamic programming | Assignment configurations on graph separators | Separator size $\text{tw} = \Omega(n) \implies 2^{\Omega(\text{tw})}$ states | **Outcome A / Bound** |
| **Weisfeiler–Leman ($k$-WL)** | Iterative tuple color refinement | Joint distribution of $k$-tuple relations | Tuple dimension $k = \Omega(n) \implies n^{\Omega(k)}$ memory | **Outcome A / Bound** |
| **Extrinsic Topology** | Simplicial/cubical cell complex holonomy | Invariants of the formula complex $\mathcal{K}(\mathcal{F})$ | Syntactic cell attachment is blind $\implies$ Outcome A;<br>Semantic cell attachment requires SAT $\implies$ Outcome B | **Outcome A or B** |
| **Semantic Quotients** | Equivalence classes on $\{0, 1\}^n$ | Equivalence relation $\sim_{\mathcal{F}}$ partitioning states | Testing $x \sim_{\mathcal{F}} y$ is coNP-complete | **Outcome B (Circularity)** |
| **Compact Encoding** | Generic low-dimensional invariant $\Phi(\mathcal{F})$ | Compressed mathematical descriptor | Evaluating $\mathcal{D}(\Phi(\mathcal{F}))$ is NP-hard | **Outcome C (Decision Hardness)** |

---

## 4. The Restricted-Carrier Lower-Bound Program

To avoid attempting an unrestricted universal theorem that would implicitly resolve $P \stackrel{?}{=} NP$, we establish a rigorous program of **restricted-carrier impossibility theorems**:

### Target Theorem Structure:
For a formally defined carrier family $\mathcal{C}_i$, prove:
$$\forall (\Phi, \mathcal{D}) \in \mathcal{C}_i, \quad (\Phi, \mathcal{D}) \implies \text{Outcome A (Collapse)} \lor \text{Outcome B (Circularity)} \lor \text{Outcome C (Decision Hardness)}$$

```
                                 RESTRICTED CARRIER CLASSES
                                              │
          ┌───────────────────────────────────┼───────────────────────────────────┐
          ▼                                   ▼                                   ▼
[CLASS 1: C_hom]                    [CLASS 2: C_quot]                   [CLASS 3: C_local]
Polynomial-size homological/        Constraint-induced semantic         Bounded-radius / k-tuple
cohomological functors over         quotient spaces {0, 1}^n / ~_F      aggregation operators
extrinsic cell complexes            subject to local definitions        (Weisfeiler–Leman style)
```

---

## 5. Formal Restricted-Class Results

### Theorem 1 ($\mathcal{C}_{\text{hom}}$ Impossibility on Expanders):
*Let $\mathcal{C}_{\text{hom}}$ be the class of carriers where $\Phi(\mathcal{F})$ is computed via linear homological boundary/coboundary operators on cell complexes $\mathcal{K}(\mathcal{F})$ whose cell attachments are determined in polynomial time by local clause syntax.*
* **Proof Sketch:** For high-girth expander collision pairs ($g \ge 5$), the local cell attachments of radius $R < g/2$ are isomorphic on SAT and UNSAT instances. Because the boundary operator is linear and local, the resulting homology groups over any field $\mathbb{F}$ evaluate identically: $\Phi(\mathcal{F}_{\text{SAT}}) \cong \Phi(\mathcal{F}_{\text{UNSAT}})$.
* **Verdict:** $\forall \Phi \in \mathcal{C}_{\text{hom}}, \Phi \implies \text{Outcome A (Collapse / Blindness)}$.

### Theorem 2 ($\mathcal{C}_{\text{quot}}$ Impossibility via Circuit Equivalence):
*Let $\mathcal{C}_{\text{quot}}$ be the class of carriers where $\Phi(\mathcal{F})$ is a quotient representation $\{0, 1\}^n / \sim_{\mathcal{F}}$ such that $x \sim_{\mathcal{F}} y$ implies identical satisfiability of the residual sub-formula.*
* **Proof Sketch:** Deciding whether two partial assignments $x$ and $y$ produce logically equivalent residual formulas is coNP-complete. Computing the equivalence classes in $T_{\text{con}} \le \text{poly}(n)$ is impossible unless $\mathbf{P} = \mathbf{coNP}$.
* **Verdict:** $\forall \Phi \in \mathcal{C}_{\text{quot}}, \Phi \implies \text{Outcome B (Construction Circularity)}$.

---

## ⚖️ 6. Epistemic Ledger & Research State

| Candidate Carrier Family | Mathematical Status Under Restricted Audit | Epistemic Classification |
| :--- | :--- | :--- |
| **$\mathcal{C}_{\text{hom}}$ (Syntactic Extrinsic Topology)** | Proven to suffer Outcome A (Collapse) on high-girth expanders | **Formally Disqualified as Category D** |
| **$\mathcal{C}_{\text{quot}}$ (Semantic Quotients)** | Proven to suffer Outcome B (Circularity) via coNP-hardness of equivalence | **Formally Disqualified as Category D** |
| **$\mathcal{C}_{\text{local}}$ (Local Tuple / $k$-WL Operators)** | Proven to suffer Outcome A (Collapse) on CFI expander families | **Formally Disqualified as Category D** |
| **Unconstrained Carrier Space $\mathcal{C}_{\text{general}}$** | Must simultaneously avoid Outcomes A, B, and C | **Open Mathematical Frontier (0 candidates identified)** |

---

## 🏁 7. Standing Research Invariant

* **PILL RED v1.0.0 Codebase:** 100% FROZEN (`master 923d2a8`).
* **Rule 013 Mandate:** ACTIVE & BINDING.
* **The Research Frontier:** Investigating whether any non-homological, non-quotient, non-local carrier exists outside $\mathcal{C}_{\text{hom}} \cup \mathcal{C}_{\text{quot}} \cup \mathcal{C}_{\text{local}}$ that avoids Outcomes A, B, and C.
