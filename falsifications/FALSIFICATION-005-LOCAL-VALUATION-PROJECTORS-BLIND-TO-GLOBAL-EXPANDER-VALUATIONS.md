# Falsification Record: FALSIFICATION-005

**Falsification ID:** `FALSIFICATION-005`  
**Title:** Local Valuation Projectors Blindness on Global Expander Valuation Contradictions  
**Date Falsified:** 2026-08-19  
**Producing Experiment:** `EXP-PHASE18-GLOBAL-VALUATION-CRUCIBLE-001` (Phase XVIII)  
**Hypothesis Falsified:** Local Valuation-Preserving Tensor-Ideals (VPTI with bounded witness radius) universally distinguish SAT from UNSAT across arbitrary Boolean collision pairs.

---

## 1. Description of the Falsification

1. **Failure of Local Projector Separation on High-Girth Cycles:**
   - In 10 adversarial collision pairs generated over 3-regular expander graphs with girth $g \ge 5$, every local neighborhood of radius $R < \lfloor g/2 \rfloor$ is a tree and hence locally satisfiable in both instances.
   - As a result, local VPTI marginal operators evaluated to **identically $0.0$ for both SAT and UNSAT**, achieving a **$0.0\%$ collision separation rate (10/10 blind)**.
2. **Search Tree Explosion:**
   - Despite identical local valuation signatures, refuting the global UNSAT instances required exponential resolution conflicts ($435 \to 6,038$), confirming that the contradiction is purely non-local.

---

## 2. Epistemic Impact on PILL RED
- Formally delineates the boundary of local polynomial valuation representations: local witness projectors cannot decide global interacting valuation contradictions on high-treewidth expanders without non-local cycle invariants.

---

## 3. Supporting Evidence
- **Experiment Record:** `experiments/017_GLOBAL_VALUATION/EXP_PHASE18_GLOBAL_VALUATION_CRUCIBLE_001.md`
- **Dataset:** `evidence/BENCHMARK_RECORDS/EXP_PHASE18_GLOBAL_VALUATION_DATASET.json`
- **Plot:** `evidence/RELEASE_EVIDENCE/phase18_global_valuation_boundary.png`
