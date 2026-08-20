# Discovery Record: DISCOVERY-004

**Discovery ID:** `DISCOVERY-004`  
**Title:** Multi-Round Persistence of Boundary-Conditioned Search Guidance  
**Date Discovered:** 2026-08-18  
**Producing Experiment:** `EXP-PHASE9-MULTIROUND-SCALING-001` (Phase IX)  
**Confidence Level:** High (Demonstrated & Replicated across 20 Independent Instances)  
**Epistemic Scope:** DEMONSTRATED within the tested Phase IX experimental domain ($16, 24, 32, 48$ rounds, 5 seeds, 20 instances).  

---

## 1. Description of Discovery
Boundary-conditioned Laplacian preprocessing ($\mathbf{L}_B = \mathbf{B}^T \mathbf{W}_B \mathbf{B}$) with incidence weighting $\gamma = 10$ produced a positive CDCL conflict-reduction signal at every tested circuit depth from 16 through 48 SHA-256 rounds.

$$\text{Conflict Reduction} = \frac{\text{Baseline Conflicts} - \text{Boundary Conflicts}}{\text{Baseline Conflicts}} \times 100\%$$

---

## 2. Experimental Test Domain & Measured Reductions

- **Rounds Swept:** 16, 24, 32, 48
- **Seeds per Scale:** 5 (Seeds 42, 43, 44, 45, 46)
- **Total Tested Instances:** 20
- **Boundary Pinning:** 256 Input Bits, 32 Output Bits

### Measured Reductions by Scale:
- **16 Rounds ($n=2048$):** **8.2% reduction** in mean CDCL conflicts ($14.6 \to 13.4$)
- **24 Rounds ($n=3072$):** **17.7% reduction** in mean CDCL conflicts ($15.8 \to 13.0$)
- **32 Rounds ($n=4096$):** **14.9% reduction** in mean CDCL conflicts ($14.8 \to 12.6$)
- **48 Rounds ($n=6144$):** **10.7% reduction** in mean CDCL conflicts ($15.0 \to 13.4$)
- **Overall Mean Conflict Reduction:** **12.9%** across all 20 tested instances.

### Empirical Soundness:
- **SAT Agreement Rate:** **20 / 20 = 100%** (Zero false UNSAT outcomes).

---

## 3. Strict Epistemic Boundaries & Non-Claims

1. **Bounded Scientific Scope:**
   - This discovery demonstrates that the boundary-conditioned search guidance signal persists through 48 rounds on the tested family of circuits.
   - **No claim is made that the signal scales indefinitely or eliminates exponential complexity.**
   - Decision workloads continue to scale with instance size ($14.7\text{k} \to 53.7\text{k}$ mean decisions).
2. **Open Research Question:**
   - Does the conflict-reduction signal persist beyond 48 rounds (e.g., standard 64-round SHA-256), and does its magnitude remain stable under deeper feedforward cascades?

---

## 4. Provenance & Artifact Links
- **Experiment Record:** `experiments/008_MULTIROUND_SCALING/EXP_PHASE9_MULTIROUND_SCALING_001.md`
- **Raw Benchmark Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE9_MULTIROUND_DATASET.json`
- **Visual Diagnostic Chart:** `evidence/RELEASE_EVIDENCE/phase9_multiround_scaling.png`
- **Native Instrument:** `red_pill_dock/`
