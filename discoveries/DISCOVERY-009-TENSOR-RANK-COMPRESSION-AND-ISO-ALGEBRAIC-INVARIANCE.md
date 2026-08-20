# Discovery Record: DISCOVERY-009

**Discovery ID:** `DISCOVERY-009`  
**Title:** Tensor Rank Compression Scaling and Iso-Algebraic Valuation Invariance  
**Date Discovered:** 2026-08-19  
**Producing Experiment:** `EXP-PHASE16-NONLINEAR-COMPRESSION-001` (Phase XVI)  
**Epistemic Classification:** Exact Representation & Complexity Mapping (5 Gates, 3 Tracks)  

---

## 1. Description of the Discovery

1. **Degree-Dependent Tensor Compression Advantage:**
   - On quadratic systems ($d=2$), low-rank matrix descriptions ($2 r n$) do not compress moderate systems ($C(I) = 0.34\text{x}..0.45\text{x} < 1.0$), because the naive triangular representation $\frac{n^2}{2}$ is already relatively compact.
   - On cubic systems ($d=3$), 3-way tensor decompositions achieve significant polynomial compression (**$6.80\text{x}$ on planted low-rank, $2.61\text{x}$ on random dense**), compressing $4,060 \to 600$ parameters in $51.1\text{ ms}$ polynomial time.
2. **5-Gate Evaluation Audit:**
   - **G1 (Compression):** Confirmed effective on $d \ge 3$ cubic tensors.
   - **G2 (Construction Time):** Verified strictly polynomial ($T_{\text{con}} \le 51.1\text{ ms}$).
   - **G3 (Preservation):** Preserved 100% ground-truth soundness across all 16 instances.
   - **G4 (Decision Runtime):** Verified polynomial on residual solvers ($T_{\text{dec}} \le 1.4\text{ ms}$).
   - **G5 (No Hidden Exponential Work):** Confirmed that low-rank decompositions do not hide exponential scaling on the tested instances.
3. **Iso-Algebraic Valuation Blindness:**
   - On hostile iso-algebraic pairs (Track C), SAT and UNSAT instances share **identical $\mathbb{F}_2$ rank ($r=25..26$) and identical continuous singular value spectra**.
   - Proves that structural/rank summaries alone are insufficient to decide SAT; the discrete assignment valuation on the compressed core is strictly necessary.

---

## 2. Epistemic Impact on PILL RED
- Formally characterizes where algebraic tensor compression works ($d \ge 3$) and where it fails to provide space savings ($d=2$).
- Confirms that polynomial-time tensor rank compression preserves structural geometry without hiding exponential work on tested instances, while delineating the boundary where valuation search remains necessary.

---

## 3. Evidence & Records
- **Experiment Record:** `experiments/015_TENSOR_COMPRESSION/EXP_PHASE16_NONLINEAR_COMPRESSION_001.md`
- **Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE16_COMPRESSION_DATASET.json`
- **Plot:** `evidence/RELEASE_EVIDENCE/phase16_tensor_compression.png`
