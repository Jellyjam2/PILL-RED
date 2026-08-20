# Experiment Record: EXP-ABLATION-ADDER-001 (Failure Discovery)

**Experiment ID:** `EXP-ABLATION-ADDER-001`  
**Date:** 2026-08-18  
**Status:** FALSIFIABLE FAILURE BASELINE (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Fixed-Tolerance Spectral SBP Injection ($\epsilon = 10^{-4}$) without Degeneracy Gating  

---

## 1. Experimental Motivation

Evaluate whether fixed-tolerance Fiedler vector coordinate clustering ($|v_2(u) - v_2(v)| < \epsilon$) remains sound as full-adder bit width scales from 8 to 32 bits.

---

## 2. Measured Results

| Instance | Vars ($n$) | Clauses ($m$) | $\Delta_F = \lambda_3 - \lambda_2$ | Injected SBPs | Mode A (Baseline) | Mode C (Full Spectral) | Ground Truth | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `adder_8bit` | 33 | 121 | 0.2547 | 36 | 0.000718s (SAT) | 0.054547s (SAT) | SAT | Pass |
| `adder_16bit` | 65 | 241 | 0.0845 | 136 | 0.000111s (SAT) | 0.003871s (SAT) | SAT | Pass |
| `adder_32bit` | 129 | 481 | **0.0232** | **6,005** | 0.000141s (SAT) | **0.022668s (UNSAT ⚠️)** | **SAT** | **FALSE UNSAT FAILURE** |

---

## 3. Scientific Root Cause Analysis

1. **Eigenspace Degeneracy:** As the circuit expanded to 32 bits, the spectral gap collapsed to $\Delta_F = 0.0232$ ($\lambda_2 \approx 8.5438, \lambda_3 \approx 8.5670$).
2. **Loss of Coordinate Distinctness:** Near-degeneracy compressed unrelated variable coordinates into an artificially narrow band.
3. **Over-Constraint Explosion:** Fixed $\epsilon = 10^{-4}$ clustered non-symmetric variables, injecting 6,005 conflicting SBPs.
4. **False UNSAT:** The over-constrained formula forced Glucose3 to return UNSAT, violating solver soundness.
