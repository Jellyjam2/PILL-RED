# 05 — Symmetry-Breaking Predicates (SBP) via Spectral Coordinate Alignment

## 1. Geometric Symmetry Detection

Traditional symmetry-breaking tools rely on graph isomorphism detection (e.g., Nauty / Saucy) which operates on discrete automorphism groups $\operatorname{Aut}(\Phi)$.

In PILL RED, structural symmetries are detected directly in the continuous eigenspace of the Graph Laplacian $\mathbf{L}$:

### Definition 1.1 (Spectral Coordinate Distance)
For any pair of variables $u, v \in V$, the spectral coordinate distance in the Fiedler vector is:
$$d_F(u, v) = |(\mathbf{v}_2)_u - (\mathbf{v}_2)_v|$$

### Definition 1.2 (Symmetry-Breaking Predicate Injection)
For a chosen tolerance threshold $\epsilon > 0$, if $d_F(u, v) < \epsilon$ and $u < v$, PILL RED injects a Lexicographic Symmetry-Breaking Clause:
$$\mathcal{C}_{\text{SBP}}(u, v) = (\neg u \vee v)$$

### Theorem 1.1 (Sub-Tree Pruning Bound)
Injecting $(\neg u \vee v)$ eliminates the branch assignment $(u = \text{True}, v = \text{False})$ from the CDCL search tree, reducing the search space by exactly $2^{n-2}$ states (50% of the symmetric sub-tree) without removing valid satisfying witnesses in symmetric equivalence classes.

---

## 2. Gradient-Guided Polarity Phase Re-Seeding

Standard CDCL solvers utilize randomized phase initialization or pure historical activity heuristics (e.g., VSIDS).

PILL RED uses the continuous gradient vector $\mathbf{v}_2$ to pre-seed the initial branching phase of variable $i$:
$$\operatorname{Phase}(i) = \begin{cases} +1 & \text{if } (\mathbf{v}_2)_i \ge 0 \\ -1 & \text{if } (\mathbf{v}_2)_i < 0 \end{cases}$$
This guides initial unit propagations along the physical gradient of the continuous constraint relaxation.
