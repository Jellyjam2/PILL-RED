# Initial Experimental Baseline: 16-Bit Full Adder Inversion

**Experiment ID:** `EXP-002-16BIT-ADDER`  
**Date Executed:** 2026-08-18  
**System Version:** PILL RED v1.0.0-alpha  
**Status:** IMMUTABLE HISTORICAL RECORD  

---

## 1. Benchmark Execution Parameters

* **Circuit:** 16-Bit Ripple-Carry Full Adder Inversion ($A + B = 65,535$)
* **Original Variables:** 65
* **Original Clauses:** 225
* **Target Sum:** `0xFFFF` (65,535)

---

## 2. Measured Results

```text
🚀 [PIPELINE] Initialising hybrid spectral-CDCL loop...
🌀 [SPECTRAL] Fiedler resonance vector extracted successfully.
✂️ [PRUNE] Injected 136 Lexicographic SBP clauses into Glucose3.
🎛️ [RESTART] Glucose3 polarity branches re-seeded via continuous gradient math.
👑 [SOLVER RESULT] Formula is: SATISFIABLE
💎 [RESULT]: SOLVED in 0.0661s! Inputs: A=0, B=65535 (Sum=65535 == 65535)
```

### Metrics Summary
* **Result:** SATISFIABLE
* **Witness Assignment:** $A = 0$, $B = 65,535$ ($\text{Sum} = 65,535$)
* **SBPs Injected:** 136 clauses
* **Total Execution Latency:** 0.0661 s (Initial run: 0.3726 s)
