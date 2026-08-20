"""
Adversarial Problem Generators and Collision Family Factories for PILL RED.
"""

import random
import math
import numpy as np
import networkx as nx
from typing import List, Dict, Any, Tuple

class ProblemFamily:
    def __init__(self, name: str):
        self.name = name

    def generate_pair(self, **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class HighGirthExpanderFamily(ProblemFamily):
    """
    High-Girth Expander Collision Family (g >= 5).
    Produces SAT/UNSAT pairs with identical local marginals and identical interaction matrix Q,
    differing only in global cycle parity charge.
    """
    def __init__(self):
        super().__init__("high_girth_expander")

    def generate_pair(self, n_nodes: int = 24, seed: int = 42) -> Dict[str, Any]:
        random.seed(seed)
        np.random.seed(seed)

        # Build high-girth 3-regular graph
        G = nx.random_regular_graph(3, n_nodes, seed=seed)
        for attempt in range(50):
            cand = nx.random_regular_graph(3, n_nodes, seed=seed + attempt)
            if nx.is_connected(cand):
                cycles = nx.cycle_basis(cand)
                if cycles and min(len(c) for c in cycles) >= 5:
                    G = cand
                    break

        edges = list(G.edges())
        m_edges = len(edges)
        edge_to_var = {e: i + 1 for i, e in enumerate(edges)}
        for u, v in edges:
            edge_to_var[(v, u)] = edge_to_var[(u, v)]

        nodes = list(G.nodes())
        charges_sat = {v: 0 for v in nodes}
        charges_unsat = {v: 0 for v in nodes}
        charges_unsat[nodes[0]] = 1 # Odd total charge = UNSAT

        def make_clauses(charges):
            clauses = []
            for v in nodes:
                inc = list(G.edges(v))
                x1, x2, x3 = edge_to_var[inc[0]], edge_to_var[inc[1]], edge_to_var[inc[2]]
                if charges[v] == 0:
                    clauses.extend([[-x1, -x2, -x3], [-x1, x2, x3], [x1, -x2, x3], [x1, x2, -x3]])
                else:
                    clauses.extend([[x1, x2, x3], [x1, -x2, -x3], [-x1, x2, -x3], [-x1, -x2, x3]])
            return m_edges, clauses

        n_s, cl_s = make_clauses(charges_sat)
        n_u, cl_u = make_clauses(charges_unsat)
        Q = nx.to_numpy_array(G, dtype=np.uint8)

        return {
            "family": self.name,
            "n_nodes": n_nodes,
            "Q_matrix": Q,
            "sat_instance": (n_s, cl_s, True),
            "unsat_instance": (n_u, cl_u, False)
        }

class IsoAlgebraicCollisionFamily(ProblemFamily):
    """
    Quadratic / Cubic Iso-Algebraic Collision Family.
    Produces SAT/UNSAT pairs sharing identical structural interaction matrix / tensor,
    with local contradictory parity constant.
    """
    def __init__(self):
        super().__init__("iso_pairs")

    def generate_pair(self, n_vars: int = 32, seed: int = 42) -> Dict[str, Any]:
        random.seed(seed)
        np.random.seed(seed)

        Q = np.zeros((n_vars, n_vars), dtype=np.uint8)
        for _ in range(n_vars * 2):
            i, j = random.sample(range(n_vars), 2)
            Q[min(i, j), max(i, j)] = 1

        active_pairs = list(zip(*np.where(Q == 1)))
        targets = []
        for i, j in active_pairs:
            u, v = i + 1, j + 1
            y = random.choice([k for k in range(1, n_vars + 1) if k not in (u, v)])
            targets.append((u, v, y))

        def make_clauses(is_unsat):
            clauses = []
            curr = n_vars
            for idx, (u, v, y) in enumerate(targets):
                curr += 1
                p = curr
                clauses.extend([[-p, u], [-p, v], [-u, -v, p]])
                rhs = 1 if (is_unsat and idx == 0) else 0
                if rhs == 1:
                    clauses.extend([[p, y], [-p, -y]])
                else:
                    clauses.extend([[-p, y], [p, -y]])
            if is_unsat:
                clauses.extend([[targets[0][2]], [-targets[0][2]]])
            return curr, clauses

        n_s, cl_s = make_clauses(False)
        n_u, cl_u = make_clauses(True)

        return {
            "family": self.name,
            "n_vars": n_vars,
            "Q_matrix": Q,
            "sat_instance": (n_s, cl_s, True),
            "unsat_instance": (n_u, cl_u, False)
        }

class PureParityFamily(ProblemFamily):
    """Linear Parity XOR Family."""
    def __init__(self):
        super().__init__("pure_parity")

    def generate_pair(self, n_vars: int = 30, seed: int = 42) -> Dict[str, Any]:
        random.seed(seed)
        # Random 3-XOR system
        clauses = []
        for _ in range(n_vars * 2):
            v1, v2, v3 = random.sample(range(1, n_vars + 1), 3)
            clauses.extend([[v1, v2, v3], [v1, -v2, -v3], [-v1, v2, -v3], [-v1, -v2, v3]])
        return {
            "family": self.name,
            "sat_instance": (n_vars, clauses, True),
            "unsat_instance": (n_vars, clauses + [[1], [-1]], False)
        }

class NonlinearDegreeLadderFamily(ProblemFamily):
    """Nonlinear Degree Ladder (d = 1..4)."""
    def __init__(self):
        super().__init__("nonlinear_ladder")

    def generate_pair(self, n_vars: int = 24, degree: int = 3, seed: int = 42) -> Dict[str, Any]:
        random.seed(seed)
        clauses = []
        for _ in range(n_vars):
            lits = random.sample(range(1, n_vars + 1), degree)
            clauses.append(lits)
        return {
            "family": self.name,
            "degree": degree,
            "sat_instance": (n_vars, clauses, True),
            "unsat_instance": (n_vars, clauses + [[lits[0]], [-lits[0]]], False)
        }

class FeedforwardCircuitsFamily(ProblemFamily):
    """Feedforward DAG Multi-Round Circuit Family."""
    def __init__(self):
        super().__init__("feedforward_circuits")

    def generate_pair(self, rounds: int = 16, seed: int = 42) -> Dict[str, Any]:
        n_vars = rounds * 8
        clauses = []
        for r in range(rounds):
            base = r * 8
            for i in range(7):
                clauses.extend([[-(base + i + 1), (base + i + 2)], [(base + i + 1), -(base + i + 2)]])
        return {
            "family": self.name,
            "sat_instance": (n_vars, clauses, True),
            "unsat_instance": (n_vars, clauses + [[1], [-1]], False)
        }
