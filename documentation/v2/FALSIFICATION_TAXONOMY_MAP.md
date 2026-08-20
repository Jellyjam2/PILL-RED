# 🔴 PILL RED v2.0 Falsification Taxonomy Map

**Document ID:** `DOC-PILLRED-V2-TAXONOMY-001`  
**Status:** ACTIVE LIVING RESEARCH MAP  
**Branch:** `engine-v2`  

---

## 🧭 1. Overview & Purpose

The **PILL RED Falsification Map** classifies the exact structural failure mechanisms that prevent polynomial-time candidate representations from separating Boolean Satisfiability (SAT / UNSAT) on adversarial instances.

Rather than asking *"did the algorithm fail?"*, the map asks:
> **"What structural information did the representation fail to preserve, and under what adversarial transformation did that failure become unavoidable?"**

---

## 🗺️ 2. The Structural Falsification Taxonomy

```
                                    🔴 THE FALSIFICATION TAXONOMY
                                                  │
         ┌────────────────────────┬───────────────┴───────────────┬────────────────────────┐
         ▼                        ▼                               ▼                        ▼
[GLOBAL BLINDNESS]      [MARGINAL LOSS]                 [NONLINEAR COLLAPSE]     [DIMENSIONAL BLOWUP]
Spectral Laplacians     Local Valuation Cuts            Linear Affine GF(2)      Multilinear Tensor SVD
• Fails on expanders    • Fails on acyclic trees        • Fails on degree d>=2   • Fails on condition number
• Blind to parity       • Discards global consistency   • Monomial blowup        • Exponential rank
```

---

## 🔬 3. Candidate Failure Dossier Matrix

```
┌──────────────────────┬─────────────┬─────────────────────────────────┬────────────────────────────────────────────────────────┐
│ CANDIDATE            │ OUTCOME     │ ADVERSARIAL TRIGGER             │ EXACT STRUCTURAL CAUSE OF FAILURE                      │
├──────────────────────┼─────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ spectral_laplacian   │ OUTCOME_A   │ High-girth Tseitin expanders    │ Continuous L = B^T * B projects local cycle structure; │
│ (CAND-74F9A1B28C)    │ COLLAPSE    │ (girth g >= 5)                  │ global parity deficiency is in the spectral kernel.    │
├──────────────────────┼─────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ vpti_projector       │ OUTCOME_A   │ Expander 2-hop neighborhood     │ Local truth-table marginal cuts are consistent on all  │
│ (CAND-2918BC44A1)    │ COLLAPSE    │ tree covers                     │ local trees; discards global cycle obstruction.        │
├──────────────────────┼─────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ gf2_affine           │ OUTCOME_A   │ Mixed XOR/3-SAT expanders       │ Linear GF(2) Gaussian elimination solves linear parity │
│ (CAND-078F12A934)    │ COLLAPSE    │ (non-linear degree d >= 2)      │ but collapses under non-linear clause coupling.        │
├──────────────────────┼─────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ quadratic_ideal_mpo  │ OUTCOME_A   │ Pure Degree-3 Expander          │ Truncated degree-2 basis preserves pairwise couplings  │
│ (CAND-11E3D21E86)    │ COLLAPSE    │ Obstructions (Level 4)          │ but collapses when obstruction is pure degree 3.       │
├──────────────────────┼─────────────┼─────────────────────────────────┼────────────────────────────────────────────────────────┤
│ tensor_svd           │ OUTCOME_C   │ Expander incidence matrix       │ Singular value spectrum becomes ill-conditioned        │
│ (CAND-98A121EF03)    │ BLOWUP      │ flattening (m x 2n)             │ (cond > 1e8) or requires exponential bond dimension.   │
└──────────────────────┴─────────────┴─────────────────────────────────┴────────────────────────────────────────────────────────┘
```

---

## 🏛️ 4. The Emerging Trilemma Boundary

Across all tested mathematical representations, every polynomial invariant encounters one of three fundamental barriers:

1. **Outcome A (Information Collapse):**  
   The representation is computationally efficient ($O(n^k)$), but projects away the global topological/algebraic obstruction into a blind invariant quotient ($\Delta \to 0$).
2. **Outcome B (Circularity / Hidden Search):**  
   The representation maintains discrete logic exactly, but constructing the carrier requires solving an NP-hard subproblem (re-encoding SAT).
3. **Outcome C (Exponential Resource Blowup):**  
   The representation attempts to preserve non-linear global information exactly, but requires exponential basis dimension ($2^{\Omega(n)}$), exponential precision ($2^{-\Omega(n)}$), or ill-conditioned scaling.

---

## 🔍 5. The 5-Step Structural Inquiry Protocol

For every candidate representation evaluated by PILL RED, the engine and research team answer five core structural questions:

```
1. What information does this representation preserve?
                     ↓
2. What information does it discard?
                     ↓
3. What adversarial structure exposes that loss?
                     ↓
4. Does the failure appear as:
    • Outcome A: Information Collapse
    • Outcome B: Circularity / Hidden Search
    • Outcome C: Computational / Representational Blowup
    • Outcome D: Survived the Current Crucible
                     ↓
5. Can the failure mechanism be independently and mathematically verified?
```

---

## 🔗 6. Provenance & Machine Evidence

All classifications and empirical measurements in this taxonomy are backed by machine-readable records in [`evidence/v2_ledger.jsonl`](file:///C:/PILL%20RED/evidence/v2_ledger.jsonl) and verified via [`tests/test_q8_audit.py`](file:///C:/PILL%20RED/tests/test_q8_audit.py).
