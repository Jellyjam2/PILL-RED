# Discovery Record: DISCOVERY-001

**Discovery ID:** `DISCOVERY-001`  
**Title:** Eigenspace Degeneracy Corrupts Naive Spectral Symmetry-Breaking Predicates  
**Date Discovered:** 2026-08-18  
**Producing Experiment:** `EXP-ABLATION-ADDER-001` (Phase IV) & `EXP-ABLATION-ADDER-002` (Phase V)  
**Confidence Level:** High (Mathematically Proven & Empirically Replicated)  

---

## 1. Description of Discovery
When mapping combinatorial SAT circuits to a Graph Laplacian $\mathbf{L} = \mathbf{B}^T \mathbf{B}$, symmetric or disconnected subcircuits cause the Fiedler gap $\Delta_F = \lambda_3 - \lambda_2$ to collapse toward zero ($\Delta_F < 0.05$). Under near-zero $\Delta_F$, orthogonal eigenvectors within the degenerate eigenspace undergo arbitrary basis rotations. 

Generating naive Symmetry-Breaking Predicates (SBPs) by clustering variables based on identical spectral coordinates ($\|v_2[u] - v_2[v]| < \epsilon$) forces functionally distinct variables into false equality constraints. In a 32-bit adder instance, this produced an explosion of 6,005 invalid SBPs, resulting in a **False UNSAT** on a ground-truth SAT formula.

---

## 2. Mathematical Formulation
Let $\mathbf{L} = \mathbf{B}^T \mathbf{B} \in \mathbb{R}^{n \times n}$ be the signed incidence Laplacian. If the eigenspace $E(\lambda) = \{x \in \mathbb{R}^n : \mathbf{L} x = \lambda x\}$ has dimension $k \ge 2$, any orthonormal basis $V = [v_1, \dots, v_k]$ satisfies $\mathbf{L} V = \lambda V$. For any orthogonal matrix $Q \in O(k)$, the rotated basis $\tilde{V} = V Q$ is equally valid:
$$\mathbf{L} \tilde{V} = \mathbf{L} V Q = \lambda V Q = \lambda \tilde{V}$$
Individual coordinate differences $|\tilde{v}_i[u] - \tilde{v}_i[v]|$ depend arbitrarily on $Q$, rendering fixed-$\epsilon$ thresholding unsound.

---

## 3. Impact & Resolution
- **Correction:** Implemented the Phase-V **Degeneracy-Aware Safety Gate**:
  $$\text{If } \Delta_F = \lambda_3 - \lambda_2 < 0.05 \implies \text{Suppress all candidate SBPs, fallback to sound CDCL (Mode B)}.$$
- **Verification:** Restored 100% empirical soundness across all tested 8-bit, 16-bit, and 32-bit instances (`EXP-ABLATION-ADDER-002`).
