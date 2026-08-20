# Rejected Approach: Unitary Degeneracy Lifting

**Status:** REJECTED & PROVEN INEFFECTIVE  
**Related Experiment:** `EXP-PHASE8-REPRESENTATION-INVARIANCE-001`  
**Related Falsification:** `falsifications/FALSIFICATION-001-UNITARY-DEGENERACY-LIFTING.md`  

---

## Summary
The concept of applying continuous unitary transformations $U = e^{i\theta \mathbf{L}}$ to "tilt" or "rotate" graph Laplacians to lift eigenspace degeneracy was evaluated mathematically and numerically.

Because $[U, \mathbf{L}] = 0$, unitary conjugation leaves $\mathbf{L}$ completely invariant ($\|ULU^\dagger - L\|_F = 1.40 \times 10^{-13}$). It cannot create new structural information, alter the spectrum, or lift degeneracies.

The code remains preserved in `benchmarks/representation_invariance_audit.py` (Representation C) as a permanent diagnostic falsification test.
