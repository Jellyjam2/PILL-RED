"""Independent Verifier (IVR) Module for PILL RED v2.0.

Provides multi-engine ground-truth verification and witness validation.
The candidate engine is NEVER allowed to define or certify its own ground truth.
"""

from typing import Any, Dict, List, Optional, Tuple
from pysat.solvers import Glucose3, Minisat22

from engine.interfaces import CNFFormula


class IndependentVerifier:
    """Verifies satisfiability and validates witness assignments using independent oracles."""

    @staticmethod
    def verify_satisfiability(clauses: List[List[int]], num_vars: int) -> Tuple[bool, Optional[Dict[int, bool]], int]:
        """Runs dual independent solvers to establish ground-truth SAT/UNSAT and conflict count.

        Returns:
            (is_satisfiable, witness_assignment, conflict_count)
        """
        # Primary Solver: Glucose3
        with Glucose3(bootstrap_with=clauses) as solver_g:
            sat_g = solver_g.solve()
            model_g = solver_g.get_model() if sat_g else None
            try:
                conflicts_g = solver_g.accum_stats().get("conflicts", 0)
            except Exception:
                conflicts_g = 0

        # Secondary Cross-Validation Solver: Minisat22
        with Minisat22(bootstrap_with=clauses) as solver_m:
            sat_m = solver_m.solve()
            model_m = solver_m.get_model() if sat_m else None

        # Cross-validation assertion
        if sat_g != sat_m:
            raise RuntimeError(
                f"Oracle disagreement detected on formula with {num_vars} vars, {len(clauses)} clauses! "
                f"Glucose3={sat_g}, Minisat22={sat_m}"
            )

        witness: Optional[Dict[int, bool]] = None
        if sat_g and model_g:
            witness = {abs(lit): (lit > 0) for lit in model_g}
            # Verify witness mathematically against all clauses
            if not IndependentVerifier.validate_witness(clauses, witness):
                raise RuntimeError("Oracle returned an invalid witness assignment!")

        return sat_g, witness, conflicts_g

    @staticmethod
    def validate_witness(clauses: List[List[int]], witness: Dict[int, bool]) -> bool:
        """Mathematically verifies that every clause is satisfied by the witness assignment."""
        for clause in clauses:
            clause_sat = False
            for lit in clause:
                var = abs(lit)
                val = witness.get(var, False)
                if (lit > 0 and val) or (lit < 0 and not val):
                    clause_sat = True
                    break
            if not clause_sat:
                return False
        return True

    @classmethod
    def certify_formula(cls, formula: CNFFormula) -> CNFFormula:
        """Certifies a formula by independently checking its satisfiability and attaching ground truth."""
        sat, witness, conflicts = cls.verify_satisfiability(formula.clauses, formula.num_vars)
        formula.is_satisfiable = sat
        formula.witness_assignment = witness
        formula.metadata["oracle_conflicts"] = conflicts
        formula.metadata["oracle_certified"] = True
        return formula
