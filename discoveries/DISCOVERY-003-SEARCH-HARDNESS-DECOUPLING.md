# Discovery Record: DISCOVERY-003

**Discovery ID:** `DISCOVERY-003`  
**Title:** CDCL Search Hardness Emergence Decoupled from Ordinary Fiedler Spectral Gap  
**Date Discovered:** 2026-08-18  
**Producing Experiment:** `EXP-PHASE6-SHA256-HARDNESS-MAP-001` (Phase VI)  
**Confidence Level:** High (Empirically Documented in Full 2D Parameter Grid)  

---

## 1. Description of Discovery
In a systematic 2D boundary constraint sweep ($(0..256\text{ Input Bits}) \times (0..32\text{ Output Bits})$) on 16-round SHA-256 compression instances, single-sided constraints exhibited 0 CDCL conflicts (propagation-dominated). 

Search hardness (non-zero conflicts) emerged strictly under **dual-boundary conditions**, first appearing at $(128\text{ In}, 32\text{ Out})$ and scaling up to 12 conflicts and 12,515 decisions at $(256\text{ In}, 32\text{ Out})$. 

Crucially, throughout this transition, the unconditioned Fiedler spectral gap remained strictly degenerate ($\Delta_F = 0.0000$), demonstrating that ordinary Fiedler gap collapse cannot serve as an empirical proxy for SAT hardness.

---

## 2. Parameter Sweep Summary Table

| Input Bits | Output Bits | Mean Conflicts | Mean Decisions | Solver Time | Fiedler Gap $\Delta_F$ | Gating State |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **0** | **32** | 0 | 0 | 0.35 ms | 0.0000 | SUPPRESSED (Sound) |
| **64** | **32** | 0 | 0 | 0.36 ms | 0.0000 | SUPPRESSED (Sound) |
| **128** | **32** | **1** | **2,680** | 0.58 ms | 0.0000 | **Search Emergence Point** |
| **192** | **32** | **4** | **6,201** | 0.90 ms | 0.0000 | Hardness Scaling |
| **256** | **32** | **12** | **12,515** | 1.40 ms | 0.0000 | Max Tested Workload |

---

## 3. Impact & Resolution
- **Falsified Hypothesis:** $\Delta_F \to 0$ does not indicate exponential SAT difficulty.
- **Empirical Insight:** Hardness is dictated by multi-boundary algebraic propagation collisions, necessitating boundary-conditioned operators ($\mathbf{L}_B$) rather than unweighted Laplacians.
