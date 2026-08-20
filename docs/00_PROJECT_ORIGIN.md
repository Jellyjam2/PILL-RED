# 00 — Project Origin & Mission

## 1. Context & Motivation

In computational complexity theory, Boolean Satisfiability (SAT) is the canonical NP-complete problem. For over three decades, Conflict-Driven Clause Learning (CDCL) algorithms (e.g., MiniSat, Glucose, CaDiCaL) have dominated practical solving by performing systematic search with conflict analysis and non-chronological backtracking over discrete variable states.

Despite enormous engineering advances, CDCL solvers encounter severe combinatorial bottlenecks when applied to structured, highly symmetric, or cryptographic Boolean formulas (such as modular adders, hash round unrollings, and multiplier circuits). The discrete nature of the search tree forces the solver into exploring exponential numbers of symmetric sub-trees that represent identical topological configurations.

## 2. The PILL RED Inception

PILL RED was conceived to investigate whether **continuous spectral graph theory and Riemannian manifold relaxation** could provide an analytical shortcut around combinatorial search bottlenecks.

Instead of treating SAT formulas as disconnected arrays of discrete literals, PILL RED maps the clause-variable incidence graph onto a continuous Graph Laplacian manifold:
$$\mathbf{L} = \mathbf{B}^T \mathbf{B}$$

By computing the spectral decomposition of $\mathbf{L}$, the system isolates the **Fiedler vector $\mathbf{v}_2$** (the fundamental harmonic vibration mode of the constraint network). This continuous coordinate system exposes hidden geometric symmetries, allowing the injection of Symmetry-Breaking Predicates (SBPs) and gradient-directed phase re-seeding prior to discrete search.

## 3. Project Independence

PILL RED is an independent scientific research initiative with its own distinct architecture, codebase, mathematical formalisms, and verification standards.
