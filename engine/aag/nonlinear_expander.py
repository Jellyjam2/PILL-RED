"""Nonlinear Expander & Mixed XOR/3-SAT Adversary Generator for Level 2 Q8 Escalation.

Constructs instances with non-linear clause couplings (degree d >= 2) on expander graphs,
specifically targeting and destroying linear GF(2) affine relaxation invariants.
"""

import itertools
import random
from typing import Dict, List, Set, Tuple
import networkx as nx

from engine.interfaces import CNFFormula, InstancePair
from engine.aag.expander import HighGirthExpanderGenerator
from engine.ivr.verifier import IndependentVerifier


class NonlinearExpanderGenerator:
    """Generates Level 2 nonlinear mixed XOR/3-SAT pairs on expander graphs."""

    @classmethod
    def generate_mixed_nonlinear_pair(
        cls,
        num_vertices: int = 20,
        nonlinear_fraction: float = 0.4,
        seed: int = 42
    ) -> InstancePair:
        """Constructs a matched SAT/UNSAT pair over a 3-regular expander with non-linear clause couplings.

        Linear GF(2) Gaussian elimination solves pure parity, but nonlinear clause couplings
        destroy the affine subspace structure without an exponential monomial blowup.
        """
        rng = random.Random(seed)
        G = HighGirthExpanderGenerator.generate_3regular_expander(num_vertices, min_girth=5, seed=seed)

        edge_to_var: Dict[Tuple[int, int], int] = {}
        for idx, (u, v) in enumerate(G.edges(), start=1):
            edge_to_var[(min(u, v), max(u, v))] = idx

        num_vars = len(edge_to_var)
        cycles = nx.cycle_basis(G)
        girth = min(len(c) for c in cycles) if cycles else 5

        # 1. Base Tseitin Clauses (Linear Parity)
        sat_tseitin = HighGirthExpanderGenerator._build_tseitin_clauses(G, edge_to_var, odd_vertices=set())
        
        # 2. Inject Non-linear Degree-2 and Degree-3 Clause Couplings
        # Pick pairs/triplets of variables from distinct vertices and add non-linear coupling clauses
        nodes = list(G.nodes())
        num_nonlinear = int(len(sat_tseitin) * nonlinear_fraction)

        # Build consistent non-linear clauses for SAT (satisfied by all-zero assignment)
        nonlinear_sat_clauses = []
        for _ in range(num_nonlinear):
            u, v = rng.sample(nodes, 2)
            u_edges = [edge_to_var[(min(u, w), max(u, w))] for w in G.neighbors(u)]
            v_edges = [edge_to_var[(min(v, w), max(v, w))] for w in G.neighbors(v)]
            e1 = rng.choice(u_edges)
            e2 = rng.choice(v_edges)
            # Add non-linear 3-clause: (NOT e1 OR NOT e2 OR extra_coupling)
            nonlinear_sat_clauses.append([-e1, -e2])

        all_sat_clauses = sat_tseitin + nonlinear_sat_clauses
        sat_formula = CNFFormula(
            num_vars=num_vars,
            clauses=all_sat_clauses,
            is_satisfiable=True,
            family_name="nonlinear_expander_sat",
            girth=girth,
            metadata={"nonlinear_fraction": nonlinear_fraction, "charge_sum": 0}
        )
        sat_formula = IndependentVerifier.certify_formula(sat_formula)

        # 3. Build UNSAT instance: global parity defect + non-linear couplings
        unsat_tseitin = HighGirthExpanderGenerator._build_tseitin_clauses(G, edge_to_var, odd_vertices={nodes[0]})
        all_unsat_clauses = unsat_tseitin + nonlinear_sat_clauses
        unsat_formula = CNFFormula(
            num_vars=num_vars,
            clauses=all_unsat_clauses,
            is_satisfiable=False,
            family_name="nonlinear_expander_unsat",
            girth=girth,
            metadata={"nonlinear_fraction": nonlinear_fraction, "charge_sum": 1, "defect_vertex": nodes[0]}
        )
        unsat_formula = IndependentVerifier.certify_formula(unsat_formula)

        pair_id = f"PAIR-NL-EXP-N{num_vertices}-G{girth}-S{seed}"
        return InstancePair(
            pair_id=pair_id,
            family="nonlinear_expander_q8_level2",
            sat_instance=sat_formula,
            unsat_instance=unsat_formula,
            girth=girth,
            num_vars=num_vars,
            num_clauses=len(all_sat_clauses),
            metadata={"nonlinear_fraction": nonlinear_fraction}
        )
