"""Degree-3 Non-Linear Expander Adversary Generator for Level 3 Q8 Escalation.

Constructs 3-regular expander parity formulas with genuine degree d = 3 non-linear clause couplings,
specifically targeting and stress-testing truncated degree-2 polynomial representations.
"""

import itertools
import random
from typing import Dict, List, Set, Tuple
import networkx as nx

from engine.interfaces import CNFFormula, InstancePair
from engine.aag.expander import HighGirthExpanderGenerator
from engine.ivr.verifier import IndependentVerifier


class HypergraphExpanderGenerator:
    """Generates Level 3 expander pairs with degree d = 3 non-linear clause couplings."""

    @classmethod
    def generate_degree3_hypergraph_pair(
        cls,
        num_vertices: int = 18,
        nonlinear_fraction: float = 0.5,
        seed: int = 42
    ) -> InstancePair:
        """Constructs a matched SAT/UNSAT pair over a 3-regular expander with degree-3 non-linear clause couplings.

        Each vertex has 3-XOR parity constraints.
        Additional non-linear 3-clauses (NOT e_i OR NOT e_j OR NOT e_k) connect triplets
        of distant expander edges, requiring degree-3 monomials (e_i * e_j * e_k = 0).
        """
        rng = random.Random(seed)
        G = HighGirthExpanderGenerator.generate_3regular_expander(num_vertices, min_girth=5, seed=seed)

        edge_to_var: Dict[Tuple[int, int], int] = {}
        for idx, (u, v) in enumerate(G.edges(), start=1):
            edge_to_var[(min(u, v), max(u, v))] = idx

        num_vars = len(edge_to_var)
        cycles = nx.cycle_basis(G)
        girth = min(len(c) for c in cycles) if cycles else 5

        # 1. Base Tseitin Parity Constraints (Linear over GF(2))
        sat_tseitin = HighGirthExpanderGenerator._build_tseitin_clauses(G, edge_to_var, odd_vertices=set())
        
        # 2. Inject Genuine Degree-3 Non-linear Clause Couplings (NOT e1 OR NOT e2 OR NOT e3)
        # In ANF over GF(2), (NOT e1 OR NOT e2 OR NOT e3) <=> e1 * e2 * e3 = 0 (Degree 3 monomial)
        nodes = list(G.nodes())
        num_degree3 = int(len(sat_tseitin) * nonlinear_fraction)
        degree3_clauses = []

        for _ in range(num_degree3):
            u, v, w = rng.sample(nodes, 3)
            u_e = [edge_to_var[(min(u, x), max(u, x))] for x in G.neighbors(u)]
            v_e = [edge_to_var[(min(v, x), max(v, x))] for x in G.neighbors(v)]
            w_e = [edge_to_var[(min(w, x), max(w, x))] for x in G.neighbors(w)]
            e1 = rng.choice(u_e)
            e2 = rng.choice(v_e)
            e3 = rng.choice(w_e)
            # Satisfied by all-zero assignment (NOT 0 OR NOT 0 OR NOT 0 = True)
            degree3_clauses.append([-e1, -e2, -e3])

        # 3. Build SAT Instance
        all_sat_clauses = sat_tseitin + degree3_clauses
        sat_formula = CNFFormula(
            num_vars=num_vars,
            clauses=all_sat_clauses,
            is_satisfiable=True,
            family_name="degree3_nonlinear_expander_sat",
            girth=girth,
            metadata={"nonlinear_fraction": nonlinear_fraction, "charge_sum": 0, "anf_degree": 3}
        )
        sat_formula = IndependentVerifier.certify_formula(sat_formula)

        # 4. Build UNSAT Instance: Single odd charge defect (sum(charges) = 1 mod 2)
        unsat_tseitin = HighGirthExpanderGenerator._build_tseitin_clauses(G, edge_to_var, odd_vertices={nodes[0]})
        all_unsat_clauses = unsat_tseitin + degree3_clauses
        unsat_formula = CNFFormula(
            num_vars=num_vars,
            clauses=all_unsat_clauses,
            is_satisfiable=False,
            family_name="degree3_nonlinear_expander_unsat",
            girth=girth,
            metadata={"nonlinear_fraction": nonlinear_fraction, "charge_sum": 1, "defect_vertex": nodes[0], "anf_degree": 3}
        )
        unsat_formula = IndependentVerifier.certify_formula(unsat_formula)

        pair_id = f"PAIR-D3-EXP-N{num_vertices}-G{girth}-S{seed}"
        return InstancePair(
            pair_id=pair_id,
            family="degree3_nonlinear_expander_q8_level3",
            sat_instance=sat_formula,
            unsat_instance=unsat_formula,
            girth=girth,
            num_vars=num_vars,
            num_clauses=len(all_sat_clauses),
            metadata={"nonlinear_fraction": nonlinear_fraction, "anf_degree": 3}
        )
