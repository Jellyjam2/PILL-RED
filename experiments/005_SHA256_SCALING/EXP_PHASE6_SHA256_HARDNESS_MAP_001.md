# Experiment Record: EXP-PHASE6-SHA256-HARDNESS-MAP-001

**Experiment ID:** `EXP-PHASE6-SHA256-HARDNESS-MAP-001`  
**Date:** 2026-08-18  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Fixed 16-Round SHA-256 Circuit ($n=2048, m=2528 \dots 2816$), 2D Dual-Boundary Parameter Grid (Input: 0..256 bits, Output: 0..32 bits)  

---

## 1. Experimental Motivation

Empirically locate the exact **Hardness Boundary** where forward unit propagation fails and genuine CDCL combinatorial search (backtracking and conflict analysis) emerges on a 16-round SHA-256 circuit.

---

## 2. Measured Sweep Telemetry & Empirical Regime Classification

| Input Prefix | Output Prefix | Total Clauses ($m$) | $m/n$ | CDCL Conflicts | CDCL Decisions | Mode A Time | $\Delta_F$ | Empirical Regime |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **0** | 2,528 | 1.234 | **0** | 1,570 | 0.35 ms | 0.0000 | `PROPAGATION_DOMINATED` |
| **32** | **8** | 2,568 | 1.254 | **0** | 1,517 | 0.29 ms | 0.0000 | `PROPAGATION_DOMINATED` |
| **64** | **16** | 2,608 | 1.273 | **0** | 1,462 | 0.37 ms | 0.0000 | `PROPAGATION_DOMINATED` |
| **96** | **24** | 2,648 | 1.293 | **0** | 1,407 | 0.30 ms | 0.0000 | `PROPAGATION_DOMINATED` |
| **128** | **32** | 2,688 | 1.312 | **1** | 2,680 | 0.65 ms | 0.0000 | **`SEARCH_EMERGING` (TRANSITION)** |
| **160** | **32** | 2,720 | 1.328 | **2** | 3,933 | 0.57 ms | 0.0000 | `SEARCH_EMERGING` |
| **192** | **32** | 2,752 | 1.344 | **4** | 6,201 | 0.79 ms | 0.0000 | `SEARCH_EMERGING` |
| **224** | **32** | 2,784 | 1.359 | **9** | 12,158 | 1.36 ms | 0.0000 | `SEARCH_EMERGING` |
| **256** | **32** | 2,816 | 1.375 | **12** | 12,515 | 1.40 ms | 0.0000 | `SEARCH_EMERGING` |

---

## 3. Scientific Findings

1. **Discovery of the Hardness Boundary (128 In, 32 Out):**
   - Below (128 In, 32 Out), the circuit is **purely propagation-dominated**: CDCL solves the formula with exactly **0 conflicts** in $< 0.37$ ms.
   - At (128 In, 32 Out), forward/backward propagation paths collide, triggering the first non-zero conflict (**Conflicts = 1**) and causing decisions to jump from 1,407 to 2,680.
   - Across (160..256 In, 32 Out), CDCL search intensifies monotonically up to **12 conflicts and 12,515 decisions**.
2. **Spectral Degeneracy Across the Hardness Transition:**
   - Throughout the entire emergence of search hardness, the spectral gap remained at **$\Delta_F = 0.0000$**.
   - **Crucial Theoretical Insight:** Combinatorial search hardness emerged *before* the Graph Laplacian spectral gap $\Delta_F$ widened. This demonstrates that Fiedler vector separation alone does not anticipate CDCL search boundaries on this feedforward DAG structure.
3. **Safety Gate Integrity:**
   - The Phase-V safety gate remained active, correctly suppressing invalid SBP candidates across all 9 grid points and preserving 100% agreement with ground-truth Mode A SAT.

---

## 4. Visual Evidence Artifact

* **Generated Chart:** `evidence/RELEASE_EVIDENCE/sha256_hardness_map.png`
