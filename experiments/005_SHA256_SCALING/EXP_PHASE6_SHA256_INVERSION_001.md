# Experiment Record: EXP-PHASE6-SHA256-INVERSION-001

**Experiment ID:** `EXP-PHASE6-SHA256-INVERSION-001`  
**Date:** 2026-08-18  
**Status:** COMPLETE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Fixed 16-Round SHA-256 Circuit ($n=2048, m=2528$), Output Pinning Sweep (0, 8, 16, 24, 32 Bits), Target Pattern `0xA5A5A5A5`  

---

## 1. Experimental Motivation

Directly test the hypothesis: *Does increasing output boundary constraint strength break Graph Laplacian nullspace degeneracy ($\Delta_F > 0$) and induce measurable CDCL solver hardness?*

---

## 2. Measured Sweep Telemetry

| Prefix Bits | Total Clauses ($m$) | $m/n$ | $\lambda_1$ | $\lambda_2$ | $\lambda_3$ | $\Delta_F$ | Safety Gate State | Mode A (Conflicts / Decisions) | Mode A Time | Mode B Time | Mode C Time | Result |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **0** | 2528 | 1.234 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | `SUPPRESSED` | 0 / 1570 | 0.000346s | 0.000469s | 0.000303s | **SAT** |
| **8** | 2536 | 1.238 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | `SUPPRESSED` | 0 / 1558 | 0.000585s | 0.000802s | 0.000352s | **SAT** |
| **16** | 2544 | 1.242 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | `SUPPRESSED` | 0 / 1546 | 0.000293s | 0.000295s | 0.000380s | **SAT** |
| **24** | 2552 | 1.246 | 0.0000 | 0.0000 | 0.0000 | **0.0000** | `SUPPRESSED` | 0 / 1534 | 0.000298s | 0.000318s | 0.000329s | **SAT** |
| **32** | 2560 | 1.250 | 0.2412 | 0.2412 | 0.2412 | **0.0000** | `SUPPRESSED` | 0 / 1522 | 0.000358s | 0.000310s | 0.000313s | **SAT** |

---

## 3. Scientific Findings & Discoveries

1. **Spectrum Lift at 32 Bits:** Pinning all 32 output bits successfully lifted the lowest eigenvalue from $0.0000 \to 0.2412$. However, $\lambda_1, \lambda_2, \lambda_3$ shifted identically to $0.2412$, forming an **isotropic degenerate subspace** ($\Delta_F = 0.0000$).
2. **Safety Gate Effectiveness:** The Phase-V safety gate correctly detected $\Delta_F = 0.0000 < 0.05$ across all points, suppressing 100% of candidate SBP injections (over 2.08 million potential false pairings per point) and preventing false UNSAT.
3. **Absence of CDCL Hardness (0 Conflicts):** Across all 5 boundary points, the CDCL solver encountered **0 conflicts** and solved the formula in $< 0.0006$ seconds. In forward unrolled circuits with unconstrained inputs, unit propagation flows backwards deterministically without backtracking.
4. **Research Target Transition:** Demonstrates that unconstrained or single-sided output-pinned hash DAGs do not represent exponential combinatorial hardness. True computational hardness requires simultaneous input-output boundary compression (e.g. fixed message prefixes + fixed hash targets) or critical-ratio clause density.

---

## 4. Visual Evidence Artifact

* **Generated Chart:** `evidence/RELEASE_EVIDENCE/sha256_inversion_sweep.png`
