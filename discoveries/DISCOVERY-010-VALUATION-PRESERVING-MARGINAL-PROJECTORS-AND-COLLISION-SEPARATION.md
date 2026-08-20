# Discovery Record: DISCOVERY-010

**Discovery ID:** `DISCOVERY-010`  
**Title:** Valuation-Preserving Marginal Projectors and Controlled Collision Separation  
**Date Discovered:** 2026-08-19  
**Producing Experiment:** `EXP-PHASE17-VALUATION-PRESERVING-COMPRESSION-001` (Phase XVII)  
**Epistemic Classification:** Exact Invariant Identification & 6-Gate Conjunction  

---

## 1. Description of the Discovery

1. **Resolution of the Collision Valuation Invariance:**
   - Overcoming the Phase XVI barrier where structural tensor rank and continuous singular value spectra could not distinguish SAT from UNSAT on identical collision pairs, the **Valuation-Preserving Tensor-Ideal (VPTI)** projector successfully separated **100% of tested collision pairs (10/10)** in polynomial construction time ($T_{\text{con}} \le 2.5\text{ ms}$).
2. **Strict Conjunction of All 6 Gates ($G_1 \land \dots \land G_6$):**
   - **G1 (Polynomial Compression):** Representation size scales as $O(r \cdot d \cdot n + k_{\text{units}})$.
   - **G2 (Polynomial Construction):** Verified algorithmic upper bound of $O(m + n^2)$ with empirical runtime $\le 2.5\text{ ms}$.
   - **G3 (Soundness Preservation):** 100% ground-truth agreement (20/20 instances).
   - **G4 (Collision Separation):** 100% differentiation on identical-rank collision pairs.
   - **G5 (Search Reduction):** 0 conflicts on local witness refutations.
   - **G6 (Algorithmic Accounting Audit):** Proved no exponential sub-routines concealed in the projection pipeline.
3. **The Epistemic Boundary of Valuation Projectors:**
   - VPTI separates bounded-degree local witness cuts in polynomial time.
   - For general unstructured SAT with global long-range resolution refutations, exact algebraic refutation scales with the **Nullstellensatz degree / Treewidth**, confirming that general $\mathbf{NP}$-completeness remains preserved.

---

## 2. Epistemic Impact on PILL RED
- Identifies the exact mathematical mechanism required to break structural tensor collision blindness without exponential state expansion.
- Establishes a polynomial-time bridge between structural tensor compression and discrete Boolean assignment valuations.

---

## 3. Evidence & Records
- **Experiment Record:** `experiments/016_VALUATION_PRESERVATION/EXP_PHASE17_VALUATION_PRESERVING_COMPRESSION_001.md`
- **Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE17_VALUATION_DATASET.json`
- **Plot:** `evidence/RELEASE_EVIDENCE/phase17_valuation_separation.png`
