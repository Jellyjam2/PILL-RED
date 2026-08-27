# 📊 PILL RED — SHA-256 Spectral Benchmark Execution Report

**Document ID:** `PR-BENCH-001`  
**Execution Date:** 2026-08-24  
**Target Engine:** `IntegratedSovereignLumina` (Hybrid Spectral-CDCL Solver)  
**Host Environment:** Windows x86_64 | Python 3.14.3 | Rust FFI `pill_red_core.dll`  

---

## 1. Executive Summary

This report documents the baseline performance and scaling characteristics of the hybrid spectral-CDCL loop on unrolled multi-round SHA-256 circuit formulas. 

To ensure statistical significance and rule out initialization noise, the benchmark execution methodology enforces:
1. **Unrolled Circuit Isolation:** Unrolled clause structures replicate the exact variable mapping equations from `Satisfiable.py`.
2. **2 Warmup Runs:** Runs execution paths to prime the Rust FFI library load, memory allocation, and operating system page cache.
3. **5 Timed Measurements:** Solves the exact same formula instances using fresh `IntegratedSovereignLumina` pipeline instances to prevent clause accumulation bloat in PySAT's database.
4. **Contiguous Variable Compression:** Maps sparse circuit variables to a dense $[1..N]$ index space for optimal Graph Laplacian matrix computations.

---

## 2. Benchmark Configuration

* **Round Steps ($r$):** `[4, 8, 16, 24, 32]`
* **Compact Variable Remapping:** `True`
* **Epsilon Threshold ($\epsilon$):** `1e-4` (for Fiedler coordinate coordinate closeness check)
* **Solver Backend:** `Glucose3` (via PySAT)
* **Degeneracy-Aware Safety Gate:** Enabled (threshold = `0.05`)

---

## 3. Empirical Results

| Round Count ($r$) | Active Variables ($N$) | Total Clauses ($M$) | Density ($M/N$) | Min Latency (s) | Median Latency (s) | P95 Latency (s) | Median Variables/sec | Median Clauses/sec | Solver Result |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **4** | 496 | 589 | 1.188 | 0.1680 | 0.2397 | 0.4173 | 2069.66 | 2457.72 | `SATISFIABLE` |
| **8** | 992 | 1209 | 1.219 | 1.1274 | 1.2286 | 1.5252 | 807.44 | 984.07 | `SATISFIABLE` |
| **16** | 1984 | 2449 | 1.234 | 10.1628 | 10.4484 | 10.5955 | 189.89 | 234.39 | `SATISFIABLE` |
| **24** | 2976 | 3689 | 1.240 | 32.8324 | 33.8238 | 35.0767 | 87.99 | 109.07 | `SATISFIABLE` |
| **32** | 3968 | 4929 | 1.242 | 71.6825 | 71.9415 | 74.1494 | 55.16 | 68.51 | `SATISFIABLE` |

---

## 4. Key Performance Observations

1. **Topological Degeneracy (Failing Safe):**
   Across all round sizes, the spectral gap ($\Delta_F$) dropped below the safety threshold of `0.05` (yielding near-degenerate spectrums). The safety gate successfully triggered, suppressing Symmetry-Breaking Predicate (SBP) injections to prevent potential false `UNSAT` outcomes. The solver cleanly failed open to continuous gradient polarity re-seeding (Mode B), achieving correct `SATISFIABLE` results in all runs.
   
2. **Computational Complexity Scaling:**
   The execution latency scales super-linearly with the number of unrolled rounds, which is expected due to:
   - Constructing the $N \times N$ continuous Graph Laplacian matrix $L = B^T \cdot B$ in Python.
   - Performing symmetric eigen-decomposition on $L$ via SciPy/NumPy to feed the Rust manifold annealer.
   - For $N = 3968$ (32 Rounds), the solver successfully completes the entire extraction, re-seeding, and SAT solution in a median time of `71.94s`.
