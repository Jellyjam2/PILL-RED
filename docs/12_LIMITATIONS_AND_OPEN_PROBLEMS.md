# 12 — Limitations, Non-Claims & Open Problems

## 1. Explicit Non-Claims (Scientific Boundaries)

To prevent misinterpretation and maintain rigorous computer science standards:

1. **No Proof of $P = NP$:**
   PILL RED does **not** claim to prove $P = NP$. Boolean SAT remains NP-complete in the general case.
2. **Dense Matrix Scaling Constraints:**
   Computing full dense symmetric eigen-decomposition on $L \in \mathbb{R}^{n \times n}$ has an algorithmic complexity of $\mathcal{O}(n^3)$. For large industrial instances ($n > 20,000$), dense matrix computation becomes memory- and compute-bound unless sparse eigensolvers (e.g., Lanczos / Arnoldi) are used.
3. **Threshold Sensitivity ($\epsilon$ Tuning):**
   Increasing the coordinate distance tolerance $\epsilon$ indiscriminately may cluster non-symmetric variables, leading to over-constrained SBP injection that could render a satisfiable formula UNSAT. Controlled ablation is mandatory.

---

## 2. Open Theoretical & Empirical Questions

1. **Ablation Superiority:**
   Does spectral pre-conditioning consistently reduce CDCL conflicts and decisions on cryptographic circuits compared to modern state-of-the-art pure CDCL solvers?
2. **Spectral Degeneracy in Random Formulas:**
   Why do unstructured random 3-SAT instances at the critical ratio ($m/n = 4.26$) produce near-zero SBP injections ($\text{SBPs} \le 2$), whereas structured modular adders produce hundreds of SBPs?
3. **Sparse Operator Efficiency:**
   Can a sparse iterative Lanczos routine extract $\lambda_2$ in $\mathcal{O}(\operatorname{nnz}(L) \cdot k)$ time, bypassing the $\mathcal{O}(n^3)$ dense bottleneck?
