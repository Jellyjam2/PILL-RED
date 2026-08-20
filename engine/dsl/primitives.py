"""Representation DSL Primitives for PILL RED v2.0.

Implements discrete, spectral, multilinear, and algebraic representation operators.
"""

from abc import ABC, abstractmethod
import itertools
import math
import time
from typing import Any, Dict, List, Tuple, Union
import numpy as np
from scipy.linalg import svd, eigh

from engine.interfaces import CNFFormula, CandidateProfile


class RepresentationPrimitive(ABC):
    """Abstract base class for all mathematical representation primitives."""

    def __init__(self, profile: CandidateProfile):
        self.profile = profile

    @abstractmethod
    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        """Constructs representation and extracts numerical observables."""
        pass


class SpectralLaplacianPrimitive(RepresentationPrimitive):
    """Continuous Graph Laplacian Primitive L = B^T * B and Hodge 0-Laplacian."""

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        t0 = time.perf_counter()
        n = formula.num_vars
        m = len(formula.clauses)
        
        if n == 0 or m == 0:
            return {
                "observable": 0.0,
                "construction_time_ms": 0.0,
                "extraction_time_ms": 0.0,
                "condition_number": 1.0,
                "fiedler_value": 0.0,
                "trace": 0.0,
            }

        # Construct Clause-Variable Incidence Matrix B (m x n)
        B = np.zeros((m, n), dtype=np.float64)
        for i, clause in enumerate(formula.clauses):
            for lit in clause:
                var = abs(lit) - 1
                if var < n:
                    B[i, var] = 1.0 if lit > 0 else -1.0

        t_con = (time.perf_counter() - t0) * 1000.0

        # Construct Laplacian L = B^T * B
        t_eval_0 = time.perf_counter()
        L = B.T @ B

        # Compute Eigenvalues
        try:
            evals, evecs = eigh(L)
            evals = np.sort(evals)
            fiedler_val = float(evals[1]) if len(evals) > 1 else float(evals[0])
            trace_val = float(np.trace(L))
            spectral_gap = float(evals[-1] - evals[0]) if len(evals) > 1 else 0.0
            cond_num = float(evals[-1] / (evals[1] + 1e-12)) if len(evals) > 1 else 1.0
            # Primary observable: Normalized Fiedler eigenvalue
            observable = fiedler_val / (n + 1e-12)
        except Exception:
            fiedler_val = 0.0
            trace_val = 0.0
            spectral_gap = 0.0
            cond_num = 1e6
            observable = 0.0

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0

        return {
            "observable": observable,
            "fiedler_value": fiedler_val,
            "trace": trace_val,
            "spectral_gap": spectral_gap,
            "condition_number": cond_num,
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": (B.nbytes + L.nbytes) / 1024.0,
        }


class GF2AffinePrimitive(RepresentationPrimitive):
    """Discrete GF(2) Gaussian Elimination & Linear Parity Condensation."""

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        t0 = time.perf_counter()
        n = formula.num_vars
        clauses = formula.clauses
        
        # Filter parity / XOR sub-clauses or treat 3-SAT as GF(2) linear system
        # Build binary matrix over GF(2)
        m = len(clauses)
        if n == 0 or m == 0:
            return {
                "observable": 0.0,
                "construction_time_ms": 0.0,
                "extraction_time_ms": 0.0,
                "condition_number": 1.0,
                "rank": 0,
                "condensed_vars": 0,
            }

        mat = np.zeros((m, n + 1), dtype=np.uint8)
        for i, c in enumerate(clauses):
            rhs = 1
            for lit in c:
                var = abs(lit) - 1
                if var < n:
                    mat[i, var] ^= 1
                    if lit < 0:
                        rhs ^= 1
            mat[i, n] = rhs

        t_con = (time.perf_counter() - t0) * 1000.0

        # Gaussian Elimination over GF(2)
        t_eval_0 = time.perf_counter()
        pivot_row = 0
        pivots = []
        for col in range(n):
            # Find pivot
            pivot = None
            for row in range(pivot_row, m):
                if mat[row, col] == 1:
                    pivot = row
                    break
            if pivot is not None:
                # Swap rows
                if pivot != pivot_row:
                    mat[[pivot, pivot_row]] = mat[[pivot_row, pivot]]
                # Eliminate
                for row in range(m):
                    if row != pivot_row and mat[row, col] == 1:
                        mat[row] ^= mat[pivot_row]
                pivots.append((pivot_row, col))
                pivot_row += 1

        # Check for GF(2) inconsistency: row of zeros with RHS = 1
        inconsistent = False
        for row in range(m):
            if np.all(mat[row, :n] == 0) and mat[row, n] == 1:
                inconsistent = True
                break

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0
        rank = len(pivots)
        condensed = n - rank

        # Primary observable: Inconsistency indicator + normalized rank
        observable = -1.0 if inconsistent else float(rank) / float(n)

        return {
            "observable": observable,
            "rank": rank,
            "condensed_vars": condensed,
            "inconsistent": inconsistent,
            "condition_number": 1.0,  # Exact discrete algebra
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": mat.nbytes / 1024.0,
        }


class TensorRankPrimitive(RepresentationPrimitive):
    """Multilinear Clause-Variable Tensor SVD & Nuclear Norm Extraction."""

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        t0 = time.perf_counter()
        n = formula.num_vars
        clauses = formula.clauses
        m = len(clauses)

        if n == 0 or m == 0:
            return {
                "observable": 0.0,
                "construction_time_ms": 0.0,
                "extraction_time_ms": 0.0,
                "condition_number": 1.0,
                "nuclear_norm": 0.0,
                "effective_rank": 0,
            }

        # Build 3-way flattened incidence matricization M (m x (n * 2))
        M = np.zeros((m, n * 2), dtype=np.float64)
        for i, c in enumerate(clauses):
            for lit in c:
                var = abs(lit) - 1
                if var < n:
                    col = var * 2 + (0 if lit > 0 else 1)
                    M[i, col] = 1.0

        t_con = (time.perf_counter() - t0) * 1000.0

        # Singular Value Decomposition (SVD)
        t_eval_0 = time.perf_counter()
        try:
            U, s, Vt = svd(M, full_matrices=False)
            nuclear_norm = float(np.sum(s))
            # Effective rank (entropy of singular spectrum)
            s_norm = s / (np.sum(s) + 1e-12)
            entropy = -float(np.sum(s_norm * np.log2(s_norm + 1e-12)))
            eff_rank = 2.0 ** entropy
            cond_num = float(s[0] / (s[-1] + 1e-12)) if len(s) > 0 else 1.0
            observable = nuclear_norm / (math.sqrt(m * n) + 1e-12)
        except Exception:
            nuclear_norm = 0.0
            eff_rank = 0.0
            cond_num = 1e6
            observable = 0.0

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0

        return {
            "observable": observable,
            "nuclear_norm": nuclear_norm,
            "effective_rank": eff_rank,
            "condition_number": cond_num,
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": M.nbytes / 1024.0,
        }


class VPTIProjectorPrimitive(RepresentationPrimitive):
    """Valuation-Preserving Tensor-Ideal (VPTI) Local Subspace Projector."""

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        t0 = time.perf_counter()
        n = formula.num_vars
        clauses = formula.clauses
        m = len(clauses)

        if n == 0 or m == 0:
            return {
                "observable": 0.0,
                "construction_time_ms": 0.0,
                "extraction_time_ms": 0.0,
                "condition_number": 1.0,
                "subspace_overlap": 0.0,
            }

        # Build local 2-hop neighborhood clause projectors
        # For each variable, collect all local clauses and build local truth-table projector
        var_to_clauses: Dict[int, List[List[int]]] = {v: [] for v in range(1, n + 1)}
        for c in clauses:
            for lit in c:
                var_to_clauses[abs(lit)].append(c)

        t_con = (time.perf_counter() - t0) * 1000.0

        # Evaluate local valuation consistency across variable boundary cuts
        t_eval_0 = time.perf_counter()
        inconsistent_local_cuts = 0
        total_overlap = 0.0

        for v in range(1, n + 1):
            local_c = var_to_clauses[v]
            if not local_c:
                continue
            
            # Check local 1-variable marginal satisfiability:
            # Does v=True satisfy all local clauses? Does v=False satisfy all local clauses?
            can_be_true = all(any((abs(lit) == v and lit > 0) or (abs(lit) != v) for lit in c) for c in local_c)
            can_be_false = all(any((abs(lit) == v and lit < 0) or (abs(lit) != v) for lit in c) for c in local_c)

            if not can_be_true and not can_be_false:
                inconsistent_local_cuts += 1
            
            # Marginal overlap fraction
            total_overlap += (1.0 if can_be_true else 0.0) + (1.0 if can_be_false else 0.0)

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0
        
        # Primary observable: Inconsistency flag or normalized marginal overlap
        if inconsistent_local_cuts > 0:
            observable = -1.0
        else:
            observable = total_overlap / (2.0 * n + 1e-12)

        return {
            "observable": observable,
            "inconsistent_cuts": inconsistent_local_cuts,
            "subspace_overlap": total_overlap,
            "condition_number": 1.0,
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": (m * 8) / 1024.0,
        }


class QuadraticIdealMPOPrimitive(RepresentationPrimitive):
    """Truncated Degree-2 Polynomial Ideal / Matrix Product Operator (MPO) Primitive.

    Preserves degree-1 linear parity and degree-2 pairwise non-linear monomials (x_i * x_j).
    Discards degree >= 3 monomials to maintain a polynomial state size of O(n^2).
    """

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Any]:
        t0 = time.perf_counter()
        n = formula.num_vars
        clauses = formula.clauses
        m = len(clauses)

        if n == 0 or m == 0:
            return {
                "observable": 0.0,
                "construction_time_ms": 0.0,
                "extraction_time_ms": 0.0,
                "condition_number": 1.0,
                "rank": 0,
                "basis_size": 0,
            }

        # 1. Map Monomial Basis: Constant(0), Linear(1..n), Quadratic(n+1..N)
        pair_to_idx: Dict[Tuple[int, int], int] = {}
        idx = n + 1
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                pair_to_idx[(i, j)] = idx
                idx += 1

        num_basis = idx  # Total monomials: 1 + n + n*(n-1)/2
        row_list: List[Dict[int, int]] = []  # Sparse GF(2) equations: dict of col -> 1

        # 2. Encode CNF clauses into degree-2 polynomial equations over GF(2)
        for c in clauses:
            if len(c) == 1:
                # Linear unit: x_i = 1 or x_i = 0
                var = abs(c[0])
                rhs = 1 if c[0] > 0 else 0
                row = {var: 1}
                if rhs == 1:
                    row[0] = 1
                row_list.append(row)

            elif len(c) == 2:
                # 2-clause: (l1 OR l2) -> (1 + l1)(1 + l2) = 0
                # Case 1: (-x_i OR -x_j) -> x_i * x_j = 0
                # Case 2: (x_i OR x_j) -> 1 + x_i + x_j + x_i * x_j = 0
                # Case 3: (-x_i OR x_j) -> x_i + x_i * x_j = 0
                v1, v2 = abs(c[0]), abs(c[1])
                pair = (min(v1, v2), max(v1, v2))
                quad_col = pair_to_idx.get(pair)

                row: Dict[int, int] = {}
                if c[0] < 0 and c[1] < 0:
                    # x_i * x_j = 0
                    if quad_col is not None:
                        row[quad_col] = 1
                elif c[0] > 0 and c[1] > 0:
                    # 1 + x_i + x_j + x_i * x_j = 0
                    row[0] = 1
                    row[v1] = 1
                    row[v2] = 1
                    if quad_col is not None:
                        row[quad_col] = 1
                else:
                    # Pos/neg mix: e.g. (-x_i OR x_j) -> x_i + x_i * x_j = 0
                    neg_v = v1 if c[0] < 0 else v2
                    row[neg_v] = 1
                    if quad_col is not None:
                        row[quad_col] = 1

                if row:
                    row_list.append(row)

            elif len(c) == 3:
                # 3-clause: (l1 OR l2 OR l3)
                # Linear parity relaxation over GF(2): preserves Tseitin parity without spurious truncation defects
                v1, v2, v3 = abs(c[0]), abs(c[1]), abs(c[2])
                row = {v1: 1, v2: 1, v3: 1}
                rhs = 1
                for lit in c:
                    if lit < 0:
                        rhs ^= 1
                if rhs == 1:
                    row[0] = 1
                row_list.append(row)

        t_con = (time.perf_counter() - t0) * 1000.0

        # 3. Dense GF(2) Elimination on Truncated Quadratic Basis
        t_eval_0 = time.perf_counter()
        num_rows = len(row_list)
        mat = np.zeros((num_rows, num_basis), dtype=np.uint8)
        for r_idx, row in enumerate(row_list):
            for col, val in row.items():
                if col < num_basis and val == 1:
                    mat[r_idx, col] ^= 1

        pivot_row = 0
        linear_pivots = []
        quadratic_pivots = []
        
        # Monomial columns: 1..num_basis-1, Column 0 is constant 1 (RHS)
        for col in range(1, num_basis):
            pivot = None
            for r in range(pivot_row, num_rows):
                if mat[r, col] == 1:
                    pivot = r
                    break
            if pivot is not None:
                if pivot != pivot_row:
                    mat[[pivot, pivot_row]] = mat[[pivot_row, pivot]]
                for r in range(num_rows):
                    if r != pivot_row and mat[r, col] == 1:
                        mat[r] ^= mat[pivot_row]
                
                if col <= n:
                    linear_pivots.append(col)
                else:
                    quadratic_pivots.append(col)
                pivot_row += 1

        # Check for GF(2) contradiction: row where all monomial cols are 0 but col 0 (RHS) is 1
        inconsistent = False
        for r in range(num_rows):
            if np.all(mat[r, 1:] == 0) and mat[r, 0] == 1:
                inconsistent = True
                break

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0
        total_rank = len(linear_pivots) + len(quadratic_pivots)

        observable = -1.0 if inconsistent else float(total_rank) / float(num_basis)

        return {
            "observable": observable,
            "rank": total_rank,
            "linear_rank": len(linear_pivots),
            "quadratic_rank": len(quadratic_pivots),
            "basis_size": num_basis,
            "inconsistent": inconsistent,
            "condition_number": 1.0,
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": mat.nbytes / 1024.0,
        }


class CubicIdealMPOPrimitive(RepresentationPrimitive):
    """Truncated Degree-3 Polynomial Ideal / MPO Primitive.

    Maintains full algebraic information for degree-0, degree-1, degree-2, and degree-3 monomials.
    State size: N_basis = 1 + n + n*(n-1)/2 + n*(n-1)*(n-2)/6 = O(n^3).
    3-clauses map exactly into the basis without truncation defects.
    Degree-4+ relations are projected away.
    """

    def construct_and_evaluate(self, formula: CNFFormula) -> Dict[str, Union[float, int, bool]]:
        t0 = time.perf_counter()
        n = formula.num_vars

        # 1. Build Degree-3 Monomial Index Map
        pair_to_idx: Dict[Tuple[int, int], int] = {}
        triplet_to_idx: Dict[Tuple[int, int, int], int] = {}
        
        idx = n + 1
        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                pair_to_idx[(i, j)] = idx
                idx += 1

        for i in range(1, n + 1):
            for j in range(i + 1, n + 1):
                for k in range(j + 1, n + 1):
                    triplet_to_idx[(i, j, k)] = idx
                    idx += 1

        num_basis = idx  # 1 (const) + n (linear) + (n choose 2) + (n choose 3)

        # 2. Map CNF Clauses to Polynomial Equations over GF(2) via exact ANF
        row_list: List[Dict[int, int]] = []

        for c in formula.clauses:
            P = [abs(lit) for lit in c if lit > 0]
            N = [abs(lit) for lit in c if lit < 0]
            
            row: Dict[int, int] = {}
            # Expand sum_{S subseteq P} prod_{v in S cup N} v = 0
            for r in range(len(P) + 1):
                for S in itertools.combinations(P, r):
                    monomial_vars = sorted(list(S) + N)
                    deg = len(monomial_vars)
                    
                    if deg == 0:
                        row[0] = row.get(0, 0) ^ 1
                    elif deg == 1:
                        v = monomial_vars[0]
                        row[v] = row.get(v, 0) ^ 1
                    elif deg == 2:
                        pair = (monomial_vars[0], monomial_vars[1])
                        col = pair_to_idx.get(pair)
                        if col:
                            row[col] = row.get(col, 0) ^ 1
                    elif deg == 3:
                        triplet = (monomial_vars[0], monomial_vars[1], monomial_vars[2])
                        col = triplet_to_idx.get(triplet)
                        if col:
                            row[col] = row.get(col, 0) ^ 1
                    # Degree >= 4 monomials are discarded by degree-3 truncation

            row = {k: v for k, v in row.items() if v == 1}
            if row:
                row_list.append(row)

        t_con = (time.perf_counter() - t0) * 1000.0

        # 3. Dense GF(2) Elimination on Truncated Cubic Basis
        t_eval_0 = time.perf_counter()
        num_rows = len(row_list)
        mat = np.zeros((num_rows, num_basis), dtype=np.uint8)
        for r_idx, row in enumerate(row_list):
            for col, val in row.items():
                if col < num_basis and val == 1:
                    mat[r_idx, col] ^= 1

        pivot_row = 0
        linear_pivots = []
        quadratic_pivots = []
        cubic_pivots = []
        num_quad_max = n + len(pair_to_idx)

        # Monomial columns: 1..num_basis-1, Column 0 is constant 1 (RHS)
        for col in range(1, num_basis):
            pivot = None
            for r in range(pivot_row, num_rows):
                if mat[r, col] == 1:
                    pivot = r
                    break
            if pivot is not None:
                if pivot != pivot_row:
                    mat[[pivot, pivot_row]] = mat[[pivot_row, pivot]]
                for r in range(num_rows):
                    if r != pivot_row and mat[r, col] == 1:
                        mat[r] ^= mat[pivot_row]
                
                if col <= n:
                    linear_pivots.append(col)
                elif col <= num_quad_max:
                    quadratic_pivots.append(col)
                else:
                    cubic_pivots.append(col)
                pivot_row += 1

        # Check for GF(2) contradiction
        inconsistent = False
        for r in range(num_rows):
            if np.all(mat[r, 1:] == 0) and mat[r, 0] == 1:
                inconsistent = True
                break

        t_eval = (time.perf_counter() - t_eval_0) * 1000.0
        total_rank = len(linear_pivots) + len(quadratic_pivots) + len(cubic_pivots)

        observable = -1.0 if inconsistent else float(total_rank) / float(num_basis)

        return {
            "observable": observable,
            "rank": total_rank,
            "linear_rank": len(linear_pivots),
            "quadratic_rank": len(quadratic_pivots),
            "cubic_rank": len(cubic_pivots),
            "basis_size": num_basis,
            "inconsistent": inconsistent,
            "condition_number": 1.0,
            "construction_time_ms": t_con,
            "extraction_time_ms": t_eval,
            "peak_memory_kb": mat.nbytes / 1024.0,
        }
