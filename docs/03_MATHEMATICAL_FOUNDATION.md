# 03 — Mathematical Foundation

## 1. Discrete to Continuous Embedding

Let $\Phi = (V, \mathcal{C})$ be a Boolean formula in Conjunctive Normal Form (CNF) with $n = |V|$ variables and $m = |\mathcal{C}|$ clauses.

### Definition 1.1 (Signed Clause-Variable Incidence Matrix)
The continuous incidence matrix $\mathbf{B} \in \mathbb{R}^{m \times n}$ is defined by:
$$B_{c, v} = \begin{cases} +1 & \text{if literal } v \in c \\ -1 & \text{if literal } \neg v \in c \\ 0 & \text{if variable } v \text{ does not appear in clause } c \end{cases}$$

### Definition 1.2 (Incidence Density)
The density of matrix $\mathbf{B}$ is given by:
$$\rho(\mathbf{B}) = \frac{\operatorname{nnz}(\mathbf{B})}{m \times n}$$
where $\operatorname{nnz}(\mathbf{B})$ denotes the number of non-zero entries. For $k$-SAT formulas, $\operatorname{nnz}(\mathbf{B}) = k \cdot m$, yielding $\rho(\mathbf{B}) = \frac{k}{n}$.

---

## 2. Graph Laplacian Manifold

### Definition 2.1 (Laplacian Matrix)
The associated Graph Laplacian manifold operator $\mathbf{L} \in \mathbb{R}^{n \times n}$ is defined as:
$$\mathbf{L} = \mathbf{B}^T \mathbf{B}$$

The entries of $\mathbf{L}$ are explicitly given by:
$$L_{u, v} = \sum_{c \in \mathcal{C}} B_{c, u} B_{c, v}$$
- **Diagonal Entries ($u = v$):** $L_{u, u} = \operatorname{deg}(u)$, the total number of clauses containing variable $u$.
- **Off-Diagonal Entries ($u \ne v$):** $L_{u, v} = N_{\text{same}}(u, v) - N_{\text{opp}}(u, v)$, representing the signed co-occurrence balance between variables $u$ and $v$.

### Theorem 2.1 (Positive Semi-Definiteness)
For any vector $\mathbf{x} \in \mathbb{R}^n$:
$$\mathbf{x}^T \mathbf{L} \mathbf{x} = \mathbf{x}^T (\mathbf{B}^T \mathbf{B}) \mathbf{x} = \|\mathbf{B} \mathbf{x}\|_2^2 \ge 0$$
Hence, $\mathbf{L}$ is real, symmetric, and positive semi-definite ($\mathbf{L} \succeq 0$).

---

## 3. Spectral Decomposition & The Fiedler Vector

The spectral theorem guarantees an orthonormal basis of eigenvectors $\mathbf{v}_1, \mathbf{v}_2, \dots, \mathbf{v}_n \in \mathbb{R}^n$ with non-negative real eigenvalues:
$$0 = \lambda_1 \le \lambda_2 \le \lambda_3 \le \dots \le \lambda_n$$

### Definition 3.1 (Fiedler Value and Fiedler Vector)
The second smallest eigenvalue $\lambda_2$ is the **algebraic connectivity** (or Fiedler value) of the constraint network. Its corresponding eigenvector $\mathbf{v}_2 \in \mathbb{R}^n$ is the **Fiedler vector**.

### Definition 3.2 (Spectral Gap)
The fundamental spectral gap is:
$$\Delta_F = \lambda_3 - \lambda_2$$
The normalized spectral separation is:
$$\delta_F = \frac{\lambda_3 - \lambda_2}{\lambda_2 + \epsilon} \quad (\epsilon > 0)$$
