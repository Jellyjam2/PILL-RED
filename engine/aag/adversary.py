"""Adaptive Adversary Generator (AAG) Manager for PILL RED v2.0.

Provides multi-level adversarial instance pairs (Level 0 through Level 3).
"""

import random
from typing import Dict, List, Optional
from engine.interfaces import InstancePair, CNFFormula
from engine.aag.expander import HighGirthExpanderGenerator
from engine.aag.nonlinear_expander import NonlinearExpanderGenerator
from engine.aag.hypergraph_expander import HypergraphExpanderGenerator
from engine.aag.pure_degree3_expander import PureDegree3ExpanderGenerator
from engine.aag.pure_degree4_expander import PureDegree4ExpanderGenerator
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
        """Level 2: Mixed Non-linear XOR/3-SAT expander collision pairs (degree d >= 2)."""
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
    def get_level3_hypergraph_pairs(cls, count: int = 5, num_vertices: int = 18) -> List[InstancePair]:
        """Level 3: 3-Uniform Hypergraph Expander parity pairs (degree d = 3)."""
        pairs = []
        for i in range(count):
            seed = 300 + i * 37
            pair = HypergraphExpanderGenerator.generate_degree3_hypergraph_pair(
                num_vertices=num_vertices,
                seed=seed
            )
            pairs.append(pair)
        return pairs

    @classmethod
    def get_level4_pure_degree3_pairs(cls, count: int = 5, num_vertices: int = 18) -> List[InstancePair]:
        """Level 4: Pure Degree-3 Obstruction pairs (Degree 1 and 2 projections identical)."""
        pairs = []
        for i in range(count):
            seed = 400 + i * 43
            pair = PureDegree3ExpanderGenerator.generate_pure_degree3_pair(
                num_vertices=num_vertices,
                seed=seed
            )
            pairs.append(pair)
        return pairs

    @classmethod
    def get_level5_pure_degree4_pairs(cls, count: int = 5, num_vertices: int = 18) -> List[InstancePair]:
        """Level 5: Pure Degree-4 Obstruction pairs (Degree <= 3 projections identical)."""
        pairs = []
        for i in range(count):
            seed = 500 + i * 47
            pair = PureDegree4ExpanderGenerator.generate_pure_degree4_pair(
                num_vertices=num_vertices,
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
            return cls.get_level3_hypergraph_pairs(count=count, num_vertices=18)
        elif level == 4:
            return cls.get_level4_pure_degree3_pairs(count=count, num_vertices=18)
        elif level == 5:
            return cls.get_level5_pure_degree4_pairs(count=count, num_vertices=18)
        else:
            return cls.get_level5_pure_degree4_pairs(count=count, num_vertices=24)
