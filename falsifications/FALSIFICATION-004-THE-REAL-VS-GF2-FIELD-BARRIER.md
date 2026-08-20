# Falsification Record: FALSIFICATION-004

**Falsification ID:** `FALSIFICATION-004`  
**Title:** The Real vs GF(2) Field Barrier: Continuous Quadratic Forms Invariant to Mod 2 Parity  
**Date Falsified:** 2026-08-19  
**Producing Experiment:** `EXP-PHASE12-FUNDAMENTAL-CYCLE-PARITY-001` (Phase XII)  
**Confidence Level:** High (Mathematically Proven & Empirically Demonstrated across 15 Expander Instances)  

---

## 1. Falsified Hypothesis
*"Augmenting the graph Laplacian with non-local fundamental cycle bases $\mathbf{C}_T$ into a global cycle Laplacian $\mathbf{\Delta}_{\text{cycle}} = \mathbf{B}_1^T \mathbf{B}_1 + \mathbf{C}_T^T \mathbf{C}_T$ over $\mathbb{R}$ enables continuous spectral methods to detect $\text{GF}(2)$ parity obstructions and accelerate CDCL solving on Tseitin expanders."*

---

## 2. Mathematical Proof of Failure (The $\mathbb{R}$ vs $\mathbb{F}_2$ Field Barrier)

1. **Continuous Quadratic Penalty:**
   $$\mathbf{x}^T (\mathbf{C}_T^T \mathbf{C}_T) \mathbf{x} = \|\mathbf{C}_T \mathbf{x}\|_2^2 = \sum_{k=1}^{\dim(C_T)} \left( \sum_{e \in C_k} x_e \right)^2$$
   This operator penalizes deviation from zero under **standard real addition** in $\mathbb{R}$.
2. **The Mod 2 Parity Kernel:**
   In Boolean logic and $\mathbb{F}_2 = \text{GF}(2)$, satisfying a parity cycle requires:
   $$\sum_{e \in C_k} x_e \equiv 0 \pmod 2 \quad \text{or} \quad \sum_{e \in C_k} x_e \equiv 1 \pmod 2$$
3. **The Erasure of Parity in Euclidean Space:**
   In $\mathbb{R}$, assign $x_1 = +1$ and $x_2 = -1$. Then $x_1 + x_2 = 0 \in \mathbb{R}$, yielding zero quadratic penalty. However, in $\mathbb{F}_2$, $1 \oplus 1 = 0 \pmod 2$ and $1 \oplus 0 = 1 \pmod 2$. 
   Linear diffusion over $\mathbb{R}$ or $\mathbb{C}$ cannot distinguish an odd parity sum from an even parity sum because cancellation occurs via opposite real signs, not through modular arithmetic.

---

## 3. Empirical Invalidation
- On hard UNSAT parity contradictions, the mean conflict reduction between Pure CDCL (323.7) and Global Cycle Hodge Preconditioning (323.5) was **+0.1%**.

---

## 4. Preservation & Evidence
- **Experiment Record:** `experiments/011_FUNDAMENTAL_CYCLES/EXP_PHASE12_FUNDAMENTAL_CYCLE_PARITY_001.md`
- **Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE12_FUNDAMENTAL_CYCLE_DATASET.json`
- **Plot:** `evidence/RELEASE_EVIDENCE/phase12_fundamental_cycles.png`
