"""Adaptive Adversary Generator (AAG) Manager for PILL RED v2.0.

Provides multi-level adversarial instance pairs (Level 0 through Level 3).
"""

import random
from typing import Dict, List, Optional
from engine.interfaces import InstancePair, CNFFormula
from engine.aag.expander import HighGirthExpanderGenerator
from engine.aag.nonlinear_expander import NonlinearExpanderGenerator
from engine.ivr.verifier import IndependentVerifier


class AdaptiveAdversaryManager:
    """Orchestrates generation of multi-level adversarial collision families."""

    @classmethod
    def get_level0_sanity_pairs(cls, count: int = 3, num_vars: int = 15) -> List[InstancePair]:
        """Level 0: Small sanity structural pairs for basic pipeline verification."""
        pairs = []
        for seed in range(count):
            rng = random.Random(100 + seed)
            # Generate random 3-SAT formula
            clauses = []
            for _ in range(num_vars * 3):
                vars_chosen = rng.sample(range(1, num_vars + 1), 3)
                clause = [v if rng.random() > 0.5 else -v for v in vars_chosen]
                clauses.append(clause)

            sat, witness, conflicts = IndependentVerifier.verify_satisfiability(clauses, num_vars)
            if sat:
                sat_formula = CNFFormula(
                    num_vars=num_vars, clauses=clauses, is_satisfiable=True,
                    family_name="level0_sanity_sat"
                )
                sat_formula = IndependentVerifier.certify_formula(sat_formula)
                
                # Make a distinct UNSAT by adding a 3-clause cycle
                unsat_clauses = [list(c) for c in clauses]
                # Add parity defect without 1-literal contradiction
                unsat_clauses.extend([[1, 2, 3], [-1, -2, -3], [1, -2, 3], [-1, 2, -3], [1, 2, -3], [-1, -2, 3], [1, -2, -3], [-1, 2, 3]])
                unsat_formula = CNFFormula(
                    num_vars=num_vars, clauses=unsat_clauses, is_satisfiable=False,
                    family_name="level0_sanity_unsat"
                )
                try:
                    unsat_formula = IndependentVerifier.certify_formula(unsat_formula)
                    if not unsat_formula.is_satisfiable:
                        pair = InstancePair(
                            pair_id=f"PAIR-L0-N{num_vars}-S{seed}",
                            family="level0_sanity",
                            sat_instance=sat_formula,
                            unsat_instance=unsat_formula,
                            girth=3,
                            num_vars=num_vars,
                            num_clauses=len(clauses),
                        )
                        pairs.append(pair)
                except Exception:
                    continue

        return pairs

    @classmethod
    def get_level1_expander_pairs(cls, count: int = 5, num_vertices: int = 18, min_girth: int = 5) -> List[InstancePair]:
        """Level 1: Linear High-girth Ramanujan Tseitin expander collision pairs."""
        pairs = []
        for i in range(count):
            seed = 42 + i * 17
            pair = HighGirthExpanderGenerator.generate_tseitin_pair(
                num_vertices=num_vertices,
                min_girth=min_girth,
                seed=seed
            )
            pairs.append(pair)
        return pairs

    @classmethod
    def get_level2_nonlinear_pairs(cls, count: int = 5, num_vertices: int = 20, nonlinear_fraction: float = 0.4) -> List[InstancePair]:
        """Level 2: Mixed Non-linear XOR/3-SAT expander collision pairs."""
        pairs = []
        for i in range(count):
            seed = 100 + i * 23
            pair = NonlinearExpanderGenerator.generate_mixed_nonlinear_pair(
                num_vertices=num_vertices,
                nonlinear_fraction=nonlinear_fraction,
                seed=seed
            )
            pairs.append(pair)
        return pairs

    @classmethod
    def get_level3_dense_nonlinear_pairs(cls, count: int = 5, num_vertices: int = 26) -> List[InstancePair]:
        """Level 3: Dense Non-linear expander collision pairs with higher-order couplings."""
        pairs = []
        for i in range(count):
            seed = 200 + i * 31
            pair = NonlinearExpanderGenerator.generate_mixed_nonlinear_pair(
                num_vertices=num_vertices,
                nonlinear_fraction=0.75,
                seed=seed
            )
            pairs.append(pair)
        return pairs

    @classmethod
    def get_adversarial_suite(cls, level: int = 1, count: int = 5) -> List[InstancePair]:
        """Returns the appropriate adversarial instance suite for the specified Q8 level."""
        if level == 0:
            return cls.get_level0_sanity_pairs(count=count)
        elif level == 1:
            return cls.get_level1_expander_pairs(count=count, num_vertices=18, min_girth=5)
        elif level == 2:
            return cls.get_level2_nonlinear_pairs(count=count, num_vertices=20, nonlinear_fraction=0.4)
        elif level == 3:
            return cls.get_level3_dense_nonlinear_pairs(count=count, num_vertices=26)
        else:
            return cls.get_level3_dense_nonlinear_pairs(count=count, num_vertices=30)
