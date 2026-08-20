# Falsification Record: FALSIFICATION-002

**Falsification ID:** `FALSIFICATION-002`  
**Title:** Empirical Falsification of Synthetic 3D Namespace Coordinates for SBP Generation  
**Date Discovered:** 2026-08-18  
**Producing Experiment:** `EXP-PHASE8-REPRESENTATION-INVARIANCE-001` (Phase VIII)  
**Status:** FALSIFIED (UNSOUND & DESTRUCTIVE TO SAT SOUNDNESS)  

---

## 1. Falsified Hypothesis
*Hypothesis:* Embedding SAT circuit variables into a 3D Euclidean grid based on naming namespaces $(r, \text{word}, \text{bit})$ creates a geometric metric that can guide symmetry breaking without reference to the underlying logical connectivity.

---

## 2. Empirical Discovery & Failure Mechanism
Constructing a spatial Laplacian $\mathbf{L}_{3D} = \mathbf{D}_{3D} - \mathbf{A}_{3D}$ using a Gaussian distance kernel on namespace coordinates generated 4,096 synthetic predicates that paired functionally independent logical nodes together simply because they had adjacent index numbers.

When evaluated across 5 random seeds on the 16-round SHA-256 instance:
- **Soundness Rate:** **0% (5/5 instances collapsed to False UNSAT)**.
- **Root Cause:** Proximity in variable indexing does not equal logical or topological dependency. Injecting spatial predicates into CDCL over-constrains the formula, eliminating valid satisfying assignments.

---

## 3. Architectural Directive
Synthetic spatial coordinate embeddings are **permanently rejected** as a source of SAT symmetry breaking. Pure topological incidence matrices $\mathbf{B}$ and boundary-conditioned Laplacians $\mathbf{L}_B$ must be used instead.
