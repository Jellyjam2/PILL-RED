# Rejected Approach: Synthetic 3D Namespace Coordinates

**Status:** REJECTED & PROVEN UNSOUND  
**Related Experiment:** `EXP-PHASE8-REPRESENTATION-INVARIANCE-001`  
**Related Falsification:** `falsifications/FALSIFICATION-002-SYNTHETIC-3D-NAMESPACE-COORDINATES.md`  

---

## Summary
Generating symmetry-breaking predicates based on spatial distances in a 3D coordinate space derived from variable index namespaces produced 100% False UNSAT across all tested seeds.

Geometric distance between synthetic coordinate assignments does not capture true boolean circuit topology. All solver guidance must derive from physical incidence matrices $\mathbf{B}$ and boundary-conditioned Laplacians $\mathbf{L}_B$.

The evaluation remains preserved in `benchmarks/representation_invariance_audit.py` (Representation D) as an empirical falsification benchmark.
