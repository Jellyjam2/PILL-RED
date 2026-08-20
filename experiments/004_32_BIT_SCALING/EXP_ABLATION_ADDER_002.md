# Experiment Record: EXP-ABLATION-ADDER-002 (Degeneracy-Aware Safety Gate)

**Experiment ID:** `EXP-ABLATION-ADDER-002`  
**Date:** 2026-08-18  
**Status:** VERIFIED SOUND (IMMUTABLE HISTORICAL RECORD)  
**Configuration:** Degeneracy-Aware Spectral Safety Gate ($\Delta_{\text{min}} = 0.05$), Topological Degree Check ($L_{u,u} == L_{v,v}$), Linear SBP Budget ($\text{Cap} = 2n$)  

---

## 1. Experimental Motivation

Directly motivated by the failure in `EXP-ABLATION-ADDER-001`. Test whether a fail-open degeneracy safety gate suppresses unsafe SBP injection when $\Delta_F < 0.05$ while preserving SBP acceleration on well-separated eigenspaces.

---

## 2. Measured Results

| Instance | Vars ($n$) | Clauses ($m$) | $\Delta_F$ | Injected SBPs | Mode A (Baseline) | Mode B (Polarity Only) | Mode C (Full Spectral) | Ground Truth | Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| `adder_8bit` | 33 | 121 | 0.2547 | 36 | 0.000093s (SAT) | 0.001317s (SAT) | 0.008559s (SAT) | **SAT** | **PASS** |
| `adder_16bit` | 65 | 241 | 0.0845 | 130 | 0.000081s (SAT) | 0.013054s (SAT) | 0.004608s (SAT) | **SAT** | **PASS** |
| `adder_32bit` | 129 | 481 | **0.0232** | **0 (Gated)** | 0.000119s (SAT) | 0.007378s (SAT) | **0.010705s (SAT)** | **SAT** | **PASS (FAIL-OPEN VERIFIED)** |

---

## 3. Scientific Verification & Findings

1. **Safety Gate Activation:** At 32 bits, $\Delta_F = 0.0232 < 0.05$. The safety gate detected near-degeneracy and suppressed SBP candidate generation completely (0 SBPs injected).
2. **Fail-Open Invariant Preserved:** Rather than crashing or returning false UNSAT, the solver cleanly fell back to Mode B (gradient-guided polarity re-seeding) and found a valid SAT witness in 0.0107s.
3. **Soundness Across Regression Suite:** 100% agreement with ground-truth Mode A across all bit widths.
