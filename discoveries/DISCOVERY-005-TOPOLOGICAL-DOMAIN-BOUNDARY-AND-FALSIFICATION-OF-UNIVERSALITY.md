# Discovery Record: DISCOVERY-005

**Discovery ID:** `DISCOVERY-005`  
**Title:** Topological Domain Boundary & Falsification of Universal Search Trimming  
**Date Discovered:** 2026-08-18  
**Producing Experiment:** `EXP-PHASE10-ADVERSARIAL-CRUCIBLE-001` (Phase X)  
**Confidence Level:** High (Demonstrated & Replicated across 18 Adversarial Instances)  
**Epistemic Scope:** DEMONSTRATED within the tested Phase X experimental domain (64-Round SHA-256, Random 3-SAT @ 4.267, Tseitin Expanders, PHP).  

---

## 1. Description of Discovery
Hostile adversarial testing demonstrated that the **Boundary-Conditioned Graph Laplacian ($\mathbf{L}_B$) is structure-dependent rather than universal**:

1. **Feedforward Sensitivity:** The positive search guidance signal ($8.2\% \dots 17.7\%$ conflict reduction) is strongly localized to **feedforward circuits with coherent causal input/output boundary constraints**.
2. **Breakdown on Random 3-SAT:** On isotropic random 3-SAT formulas at the phase transition threshold ($m/n = 4.267$), the spectral signal collapses to random noise (mean **3.2% reduction** with high per-instance variance from $+66.7\%$ to $-85.7\%$).
3. **Resolution Lower Bound Invariance:** On classic adversarial worst-case families (Tseitin parity contradictions on expanders, Pigeonhole Principle $\text{PHP}$), $\mathbf{L}_B$ **does not bypass exponential CDCL resolution lower bounds** ($2.3\%$ on Tseitin, $-3.7\%$ on PHP).

---

## 2. Epistemic Significance & Falsification
- **Falsified Hypothesis:** "Boundary-conditioned Laplacian polarity preconditioning universally accelerates SAT solving across arbitrary Boolean graph topologies."
- **Established Boundary:** Continuous spectral preconditioning operates as a **directional topological interpolator** between defined boundary conditions. When problem graphs lack directional topological flow (as in random expanders or symmetric bipartite cliques), the Fiedler mode carries no resolution-shortening coordinate information.

---

## 3. Preservation & Evidence
- **Experiment Record:** `experiments/009_ADVERSARIAL_CRUCIBLE/EXP_PHASE10_ADVERSARIAL_CRUCIBLE_001.md`
- **Raw Benchmark Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE10_ADVERSARIAL_DATASET.json`
- **Visual Diagnostic Chart:** `evidence/RELEASE_EVIDENCE/phase10_adversarial_crucible.png`
