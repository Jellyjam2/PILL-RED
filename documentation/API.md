# PILL RED Candidate Representation API Guide

**Version:** 1.0.0  
**Target Audience:** Mathematical researchers, complexity theorists, and SAT algorithm developers.

---

## 1. Overview
The PILL RED API allows external researchers to submit proposed Boolean representations or invariants to an **adversarial crucible**. 

Rather than reporting arbitrary benchmark runtimes on easy instances, PILL RED tests whether your candidate representation:
1. **Compresses structure** into polynomial description length (**Gate G1**).
2. **Constructs in polynomial time** without hidden exponential pre-processing (**Gate G2 & G6**).
3. **Preserves satisfiability-relevant information** without losing the SAT/UNSAT distinction (**Gate G3**).
4. **Separates hostile collision families** sharing identical ranks and spectra (**Gate G4**).
5. **Reduces search tree exploration** on the residual core (**Gate G5**).

---

## 2. Implementing a Custom Candidate Representation

To test your own representation, subclass `CandidateRepresentation` from `pillred.interfaces`:

```python
from pillred.interfaces import CandidateRepresentation
from typing import List, Dict, Any, Tuple, Optional

class MySpectralInvariant(CandidateRepresentation):
    def __init__(self):
        super().__init__("My_Spectral_Invariant")

    def encode(self, n_vars: int, clauses: List[List[int]], **kwargs) -> Dict[str, Any]:
        """
        Constructs your representation from the formula.
        Must return:
          - 'compressed_size': integer description length
          - 'structural_rank': integer/float rank summary
          - 'representation_object': the computed mathematical artifact
        """
        # Example: Compute custom matrix or graph spectrum
        compressed_size = n_vars * 4
        return {
            "compressed_size": compressed_size,
            "structural_rank": 10,
            "representation_object": None
        }

    def compute_valuation_signature(self, encoding: Dict[str, Any], clauses: List[List[int]]) -> float:
        """
        Computes a scalar or vector invariant intended to distinguish SAT from UNSAT.
        """
        # Return distinct values for SAT vs UNSAT
        return 0.0

    def decide_or_solve(self, encoding: Dict[str, Any], clauses: List[List[int]]) -> Tuple[Optional[bool], int]:
        """
        Directly decides SAT/UNSAT or runs residual solver.
        Returns: (satisfiability_decision: bool or None, residual_conflicts: int)
        """
        return None, 100

    def audit_complexity_bounds(self) -> Dict[str, str]:
        """
        Returns theoretical asymptotic complexity bounds.
        """
        return {
            "construction_complexity": "O(n^2)",
            "representation_size": "O(n)",
            "decision_complexity": "O(m)"
        }
```

---

## 3. Auditing with the CLI

Run your representation against any adversarial family:

```bash
# Test on high-girth expander collisions (g >= 5)
python pillred_cli.py crucible --family high_girth_expander --candidate vpti --samples 10

# Test on quadratic/cubic iso-algebraic collisions
python pillred_cli.py crucible --family iso_pairs --candidate tensor --samples 10
```

---

## 4. Understanding the 6 Gates

| Gate | Name | Requirement |
| :--- | :--- | :--- |
| **G1** | Polynomial Compression | Description length $S(I) \le \text{poly}(n)$. |
| **G2** | Polynomial Construction | Construction runtime $T_{\text{con}} \le \text{poly}(n)$. |
| **G3** | Valuation Preservation | $100\%$ agreement with ground-truth satisfiability. |
| **G4** | Collision Separation | Yields distinct invariant signatures ($\Delta_{\text{val}} \neq 0$) on identical-rank pairs. |
| **G5** | Search Elimination | Direct decision or $0$ residual solver conflicts. |
| **G6** | No Hidden Work | Explicit algorithmic accounting confirming no $2^{\Omega(n)}$ sub-routines. |
