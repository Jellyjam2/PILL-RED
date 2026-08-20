# 📜 PILL RED Changelog

All notable changes to the PILL RED research program and software suite will be documented in this file.

## [v1.0.0-alpha] - 2026-08-18

### Added
- **Graph Laplacian Continuous Manifold Core:**
  - Implemented `FFIOmegaManifold` and `anneal_gradient_manifold` in pure Rust (`src/lib.rs`).
  - Integrated `nalgebra::DMatrix` symmetric eigen-decomposition to compute graph spectrum ($\lambda_1, \lambda_2, \lambda_3 \dots$) and Fiedler vector $v_2$.
- **Hybrid Spectral-CDCL Solver Bridge:**
  - Built `spectral_bridge.py` interfacing Glucose3 with Fiedler symmetry coordinate extraction.
  - Added Lexicographic Symmetry-Breaking Predicate (SBP) generation ($(\neg u \vee v)$ where $|v_2(u) - v_2(v)| < \epsilon$).
  - Added continuous gradient phase re-seeding for Glucose3 literal polarity queues.
- **Formal Verification Proofs:**
  - Added `src/kani_proofs.rs` with formal proofs for stack capacity bounds, ZED binary protocol headers, and zeroize memory scrubbing.
- **Universal Benchmark & Solver Suite:**
  - Built `omega_solver.py` featuring 16-bit modular full-adder inversion and critical ratio 3-SAT benchmarks.
  - Built `sha256_spectral_benchmark.py` testing DAG unrolling across 4, 8, 16, and 24 rounds.
- **Controlled Ablation Benchmark Framework:**
  - Built `benchmarks/ablation_suite.py` supporting 3-way controlled ablation testing (Mode A: Baseline, Mode B: Polarity Only, Mode C: Full Spectral + SBP).
