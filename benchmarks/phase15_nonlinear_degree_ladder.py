#!/usr/bin/env python3
# 🜏 PILL RED: PHASE XV NONLINEAR DEGREE LADDER & INFORMATION-GAP CRUCIBLE (EXP-PHASE15-NONLINEAR-BOUNDARY-001) 🜏
import os
import sys
import time
import json
import hashlib
import random
import math
import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as sla
from pysat.solvers import Glucose3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def compute_instance_hash(clauses, n_vars):
    hasher = hashlib.sha256()
    hasher.update(f"vars:{n_vars}\n".encode())
    for c in clauses:
        hasher.update(f"{sorted(c)}\n".encode())
    return hasher.hexdigest()[:16]

# --- 1. GF(2) GAUSSIAN ELIMINATION ENGINE ---
def solve_gf2_linear(A_gf2, b_gf2):
    m, n = A_gf2.shape
    if m == 0:
        return True, {}, 0
    M = np.hstack([A_gf2.copy() % 2, (b_gf2.reshape(-1, 1).copy()) % 2]).astype(np.uint8)
    pivot_row = 0
    pivots = []
    for col in range(n):
        if pivot_row >= m:
            break
        row = np.where(M[pivot_row:, col] == 1)[0]
        if len(row) == 0:
            continue
        actual_row = pivot_row + row[0]
        if actual_row != pivot_row:
            M[[pivot_row, actual_row]] = M[[actual_row, pivot_row]]
        for r in range(m):
            if r != pivot_row and M[r, col] == 1:
                M[r] = (M[r] ^ M[pivot_row]) % 2
        pivots.append((pivot_row, col))
        pivot_row += 1
    rank = len(pivots)
    for r in range(pivot_row, m):
        if M[r, n] == 1:
            return False, {}, rank # Inconsistent
    units = {}
    for r in range(pivot_row):
        cols = np.where(M[r, :n] == 1)[0]
        if len(cols) == 1:
            units[cols[0] + 1] = bool(M[r, n])
    return True, units, rank

# --- 2. CONTROLLED BOOLEAN POLYNOMIAL DEGREE LADDER GENERATOR ---
def build_degree_d_instance(n_vars=40, m_constraints=50, degree=1, force_unsat=False, seed=42):
    """
    Constructs a Boolean system where each constraint is a polynomial of degree d over GF(2):
      (x_i1 * x_i2 * ... * x_id) ^ y = c
    Converted directly to CNF.
    """
    random.seed(seed)
    clauses = []
    
    # Store linear part for GF(2) extraction
    linear_rows = []
    linear_rhs = []
    
    # For degree 1: pure linear parity (x1 ^ x2 ^ x3 = c)
    if degree == 1:
        for c_idx in range(m_constraints):
            vars_chosen = random.sample(range(1, n_vars + 1), 3)
            rhs = 1 if (force_unsat and c_idx == 0) else 0
            x, y, z = vars_chosen
            row = np.zeros(n_vars, dtype=np.uint8)
            row[x - 1] = 1
            row[y - 1] = 1
            row[z - 1] = 1
            linear_rows.append(row)
            linear_rhs.append(rhs)
            if rhs == 1:
                clauses.extend([[x, y, z], [x, -y, -z], [-x, y, -z], [-x, -y, z]])
            else:
                clauses.extend([[-x, -y, -z], [-x, y, z], [x, -y, z], [x, y, -z]])
    else:
        # Degree d >= 2: (x_1 * ... * x_d) ^ y = c
        # Encode product AND(x_1...x_d) <=> P, then P ^ y = c
        current_vars = n_vars
        for c_idx in range(m_constraints):
            monomial_vars = random.sample(range(1, n_vars + 1), degree)
            y_var = random.choice([v for v in range(1, n_vars + 1) if v not in monomial_vars])
            rhs = 1 if (force_unsat and c_idx == 0) else 0
            
            # Product variable P
            current_vars += 1
            p_var = current_vars
            
            # CNF for P <=> (x_1 and x_2 ... and x_d)
            # P -> x_i: (-P or x_i) for each i
            for x_i in monomial_vars:
                clauses.append([-p_var, x_i])
            # (x_1 and ... and x_d) -> P: (-x_1 or -x_2 ... or -x_d or P)
            clauses.append([-x_i for x_i in monomial_vars] + [p_var])
            
            # Parity P ^ y = c
            if rhs == 1:
                clauses.extend([[p_var, y_var], [-p_var, -y_var]])
            else:
                clauses.extend([[-p_var, y_var], [p_var, -y_var]])

    A_gf2 = np.array(linear_rows, dtype=np.uint8) if linear_rows else np.zeros((0, n_vars), dtype=np.uint8)
    b_gf2 = np.array(linear_rhs, dtype=np.uint8) if linear_rhs else np.zeros((0,), dtype=np.uint8)
    
    cat = f"DEGREE_{degree}_{'UNSAT' if force_unsat else 'SAT'}"
    total_vars = current_vars if degree >= 2 else n_vars
    return total_vars, clauses, A_gf2, b_gf2, degree, cat

# --- 3. EVALUATION HARNESS ---

def solve_instance(n_vars, clauses, A_gf2, b_gf2, degree):
    t0 = time.perf_counter()
    
    # 1. Measure Linearization Space Size
    # Monomials of degree <= d: sum_{k=1}^d binom(n, k)
    binom_sum = sum(math.comb(n_vars, k) for k in range(1, min(degree + 1, n_vars + 1)))
    
    # 2. Pure CDCL Baseline
    solver_a = Glucose3()
    for c in clauses:
        solver_a.add_clause(c)
    t_a0 = time.perf_counter()
    sat_a = solver_a.solve()
    t_a = (time.perf_counter() - t_a0) * 1000.0
    stats_a = solver_a.accum_stats()
    solver_a.delete()
    
    # 3. Dual-Field Preprocessing
    is_consistent, units, rank = solve_gf2_linear(A_gf2, b_gf2)
    
    if not is_consistent:
        return {
            "sat": False,
            "conflicts_a": stats_a.get("conflicts", 0),
            "decisions_a": stats_a.get("decisions", 0),
            "conflicts_dual": 0,
            "decisions_dual": 0,
            "var_elim_pct": 100.0,
            "monomial_space_dim": binom_sum,
            "path": "GF2_REFUTATION",
            "soundness": (sat_a == False)
        }
        
    # Simplify residual CNF with GF(2) units
    residual_clauses = []
    direct_conflict = False
    for c in clauses:
        sat_lit = False
        new_c = []
        for lit in c:
            v = abs(lit)
            sign = (lit > 0)
            if v in units:
                if units[v] == sign:
                    sat_lit = True
                    break
            else:
                new_c.append(lit)
        if not sat_lit:
            if len(new_c) == 0:
                direct_conflict = True
                break
            residual_clauses.append(new_c)
            
    if direct_conflict:
        return {
            "sat": False,
            "conflicts_a": stats_a.get("conflicts", 0),
            "decisions_a": stats_a.get("decisions", 0),
            "conflicts_dual": 0,
            "decisions_dual": 0,
            "var_elim_pct": len(units) / n_vars * 100.0,
            "monomial_space_dim": binom_sum,
            "path": "UNIT_CONFLICT",
            "soundness": (sat_a == False)
        }

    # CDCL on residual
    solver_d = Glucose3()
    for c in residual_clauses:
        solver_d.add_clause(c)
    for v, pol in units.items():
        solver_d.set_phases([int(v if pol else -v)])
    sat_d = solver_d.solve()
    stats_d = solver_d.accum_stats()
    solver_d.delete()
    
    return {
        "sat": sat_a,
        "conflicts_a": stats_a.get("conflicts", 0),
        "decisions_a": stats_a.get("decisions", 0),
        "conflicts_dual": stats_d.get("conflicts", 0),
        "decisions_dual": stats_d.get("decisions", 0),
        "var_elim_pct": len(units) / n_vars * 100.0,
        "monomial_space_dim": binom_sum,
        "path": "RESIDUAL_CDCL",
        "soundness": (sat_a == sat_d)
    }


def run_phase15_nonlinear_ladder():
    print("=" * 100)
    print("      🔴 PILL RED: EXP-PHASE15-NONLINEAR-BOUNDARY-001 HARNESS")
    print("=" * 100)
    print("🎯 Objectives: Measure the Information Gap across Boolean Polynomial Degrees d = 1, 2, 3, 4.")
    print("              Quantify GF(2) Elimination, Monomial Dimension, and Residual Search Growth.")
    print("=" * 100)

    # Ladder instances across degrees d = 1, 2, 3, 4
    degrees = [1, 2, 3, 4]
    results = []
    
    for d in degrees:
        for s in [42, 43, 44, 45, 46]:
            force_unsat = (s % 2 == 1)
            n_vars, clauses, A_gf2, b_gf2, deg, cat = build_degree_d_instance(
                n_vars=30, m_constraints=40, degree=d, force_unsat=force_unsat, seed=s
            )
            inst_hash = compute_instance_hash(clauses, n_vars)
            res = solve_instance(n_vars, clauses, A_gf2, b_gf2, deg)
            
            conf_a = res["conflicts_a"]
            conf_d = res["conflicts_dual"]
            red_conf = ((conf_a - conf_d) / conf_a * 100.0) if conf_a > 0 else 0.0
            
            rec = {
                "degree": d,
                "category": cat,
                "n_vars": n_vars,
                "n_clauses": len(clauses),
                "monomial_dim": res["monomial_space_dim"],
                "var_elim_pct": round(res["var_elim_pct"], 1),
                "mode_a_conflicts": conf_a,
                "dual_field_conflicts": conf_d,
                "conflict_reduction_pct": round(red_conf, 1),
                "path": res["path"],
                "soundness": res["soundness"],
                "outcome": "UNSAT" if not res["sat"] else "SAT"
            }
            results.append(rec)
            
            print(f"  [Degree d={d:1d} | {cat:16s}] n={n_vars:3d}, m={len(clauses):3d}, Monomials={res['monomial_space_dim']:7d} | "
                  f"GF(2) Elim: {res['var_elim_pct']:5.1f}% | CDCL A: {conf_a:4d} -> Dual: {conf_d:4d} ({red_conf:+6.1f}%) | {rec['outcome']}")

    # Degree Level Summaries
    print("\n" + "=" * 100)
    print("📊 [PHASE XV DEGREE LADDER SUMMARY & INFORMATION GAP]:")
    summary_by_degree = {}
    for d in degrees:
        subset = [r for r in results if r["degree"] == d]
        mean_elim = float(np.mean([r["var_elim_pct"] for r in subset]))
        mean_mono = int(np.mean([r["monomial_dim"] for r in subset]))
        mean_conf_a = float(np.mean([r["mode_a_conflicts"] for r in subset]))
        mean_conf_d = float(np.mean([r["dual_field_conflicts"] for r in subset]))
        mean_red = float(np.mean([r["conflict_reduction_pct"] for r in subset]))
        summary_by_degree[f"degree_{d}"] = {
            "mean_var_elim_pct": round(mean_elim, 1),
            "monomial_dim": mean_mono,
            "mean_conflicts_a": round(mean_conf_a, 1),
            "mean_conflicts_dual": round(mean_conf_d, 1),
            "mean_reduction_pct": round(mean_red, 1)
        }
        print(f"   Degree d={d:1d}: GF(2) Elim = {mean_elim:5.1f}% | Monomial Dim = {mean_mono:7d} | "
              f"Mean Conflicts: {mean_conf_a:5.1f} -> {mean_conf_d:5.1f} ({mean_red:+5.1f}%)")
    print("=" * 100)

    here = os.path.dirname(os.path.abspath(__file__))
    parent = os.path.dirname(here)
    out_file = os.path.join(parent, "evidence", "BENCHMARK_RECORDS", "EXP_PHASE15_NONLINEAR_DATASET.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump({
            "summary_by_degree": summary_by_degree,
            "instances": results
        }, f, indent=2)

    print(f"📁 [PHASE XV DATASET STORED]: {out_file}\n")

if __name__ == "__main__":
    run_phase15_nonlinear_ladder()
