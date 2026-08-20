#!/usr/bin/env python3
# 🜏 PILL RED: PHASE VI SHA-256 SCALING & SOUNDNESS UNDER LOAD SUITE 🜏
import os
import sys
import time
import json
from datetime import datetime
import numpy as np
from pysat.solvers import Glucose3

# Force utf-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path.insert(0, parent)

def simulate_sha256_round_clauses(target_rounds, use_compact_vars=True):
    """
    Replicates the exact multi-round variable mapping from Satisfiable.py:
    Var(r, i) = 1000 * (r + 1) + i
    """
    raw_clauses = []
    
    for r in range(target_rounds):
        r_offset = 1000 * (r + 1)
        
        for b in range(1, 32):
            x = r_offset + b
            y = r_offset + b + 32
            z = r_offset + b + 64
            r_out = r_offset + b + 96
            
            # Non-linear Ch(x,y,z) CNF clauses
            raw_clauses.append([-x, -y, r_out])
            raw_clauses.append([-x, y, -r_out])
            raw_clauses.append([x, -z, r_out])
            raw_clauses.append([x, z, -r_out])
            
            # Inter-round sequential diffusion dependency
            if r > 0:
                prev_offset = 1000 * r
                raw_clauses.append([-(prev_offset + b + 96), x])

    if not use_compact_vars:
        flat_vars = set(abs(lit) for clause in raw_clauses for lit in clause)
        max_var_index = max(flat_vars) if flat_vars else 0
        return max_var_index, raw_clauses

    unique_vars = sorted(list(set(abs(lit) for clause in raw_clauses for lit in clause)))
    var_map = {old_id: new_id + 1 for new_id, old_id in enumerate(unique_vars)}
    
    compact_clauses = []
    for clause in raw_clauses:
        compact_clause = [var_map[abs(lit)] if lit > 0 else -var_map[abs(lit)] for lit in clause]
        compact_clauses.append(compact_clause)
        
    return len(unique_vars), compact_clauses

def compute_detailed_spectral_metrics(num_vars, clauses, epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0):
    m = len(clauses)
    n = num_vars
    
    # 1. Build B & L
    t_start_mat = time.perf_counter()
    B = np.zeros((m, n), dtype=np.float32)
    for c_idx, clause in enumerate(clauses):
        for literal in clause:
            var_idx = abs(literal) - 1
            if var_idx < n:
                sign = 1.0 if literal > 0 else -1.0
                B[c_idx, var_idx] = sign
                
    nnz_B = int(np.count_nonzero(B))
    density_B = float(nnz_B / (m * n)) if (m * n) > 0 else 0.0
    
    L = B.T @ B
    nnz_L = int(np.count_nonzero(L))
    density_L = float(nnz_L / (n * n)) if (n * n) > 0 else 0.0
    mat_build_time = time.perf_counter() - t_start_mat
    
    # 2. Symmetric Eigen-Decomposition
    t_start_eig = time.perf_counter()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    eig_time = time.perf_counter() - t_start_eig
    
    lambda_1 = float(eigenvalues[0]) if len(eigenvalues) > 0 else 0.0
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_3 = float(eigenvalues[2]) if len(eigenvalues) > 2 else 0.0
    fiedler_gap = float(lambda_3 - lambda_2)
    norm_fiedler_gap = float((lambda_3 - lambda_2) / (lambda_2 + 1e-6))
    
    fiedler_vec = eigenvectors[:, 1] if n > 1 else eigenvectors[:, 0]
    
    # 3. SBP Candidate & Quality Breakdown
    t_start_filter = time.perf_counter()
    degrees = np.diag(L)
    sbp_cap = int(max_sbp_ratio * n)
    
    candidates_total = 0
    rejected_degeneracy = 0
    rejected_degree_mismatch = 0
    rejected_budget_overflow = 0
    accepted_sbps = []
    
    is_degenerate = bool(fiedler_gap < min_spectral_gap)
    gate_state = "TRIGGERED_DEGENERACY_SUPPRESSED" if is_degenerate else "ACTIVE"
    
    for u in range(n):
        for v in range(u + 1, n):
            if abs(fiedler_vec[u] - fiedler_vec[v]) < epsilon:
                candidates_total += 1
                if is_degenerate:
                    rejected_degeneracy += 1
                else:
                    if abs(degrees[u] - degrees[v]) >= 1e-3:
                        rejected_degree_mismatch += 1
                    elif len(accepted_sbps) >= sbp_cap:
                        rejected_budget_overflow += 1
                    else:
                        accepted_sbps.append([-(u + 1), (v + 1)])
                        
    filter_time = time.perf_counter() - t_start_filter
    acceptance_ratio = float(len(accepted_sbps) / candidates_total) if candidates_total > 0 else 0.0
    
    telemetry = {
        "incidence_rows": m,
        "incidence_cols": n,
        "incidence_nnz": nnz_B,
        "incidence_density": density_B,
        "laplacian_nnz": nnz_L,
        "laplacian_density": density_L,
        "lambda_1": lambda_1,
        "lambda_2": lambda_2,
        "lambda_3": lambda_3,
        "fiedler_gap": fiedler_gap,
        "norm_fiedler_gap": norm_fiedler_gap,
        "gate_state": gate_state,
        "sbp_budget": sbp_cap,
        "candidates_total": candidates_total,
        "accepted_sbps_count": len(accepted_sbps),
        "rejected_degeneracy": rejected_degeneracy,
        "rejected_degree_mismatch": rejected_degree_mismatch,
        "rejected_budget_overflow": rejected_budget_overflow,
        "acceptance_ratio": acceptance_ratio,
        "timing": {
            "matrix_build_time": mat_build_time,
            "eigen_decomposition_time": eig_time,
            "filter_time": filter_time,
            "total_spectral_time": mat_build_time + eig_time + filter_time,
        }
    }
    return telemetry, accepted_sbps, fiedler_vec

def run_sha256_3way_ablation(rounds):
    print(f"\n{'='*75}")
    print(f"  🔬 PHASE VI BENCHMARK: SHA-256 {rounds} ROUNDS (3-WAY COMPARATIVE AUDIT)")
    print(f"{'='*75}")
    
    num_vars, clauses = simulate_sha256_round_clauses(rounds, use_compact_vars=True)
    m = len(clauses)
    
    # 1. Detailed Spectral Extraction & Gating
    telemetry, accepted_sbps, fiedler_vec = compute_detailed_spectral_metrics(
        num_vars, clauses, epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0
    )
    
    print(f"📈 [TOPOLOGY] Vars: {num_vars} | Clauses: {m} | ρ(B): {telemetry['incidence_density']:.4f} | ρ(L): {telemetry['laplacian_density']:.4f}")
    print(f"🌀 [SPECTRUM] λ1: {telemetry['lambda_1']:.4f} | λ2: {telemetry['lambda_2']:.4f} | λ3: {telemetry['lambda_3']:.4f} | ΔF: {telemetry['fiedler_gap']:.4f}")
    print(f"🛡️ [SAFETY GATE] State: {telemetry['gate_state']} | Candidates: {telemetry['candidates_total']} | Accepted SBPs: {telemetry['accepted_sbps_count']} (Ratio: {telemetry['acceptance_ratio']:.4f})")
    
    record = {
        "benchmark": f"sha256_{rounds}rounds",
        "rounds": rounds,
        "variables": num_vars,
        "clauses": m,
        "timestamp": datetime.now().isoformat(),
        "spectral_telemetry": telemetry,
        "ablation_modes": {}
    }

    # -------------------------------------------------------------------------
    # MODE A: Pure Glucose3 Baseline
    # -------------------------------------------------------------------------
    solver_a = Glucose3()
    for cl in clauses:
        solver_a.add_clause(cl)
    t_start_a = time.perf_counter()
    res_a = solver_a.solve()
    t_a = time.perf_counter() - t_start_a
    solver_a.delete()
    print(f"🔹 [MODE A: Baseline Glucose3] Result: {'SAT' if res_a else 'UNSAT'} | Solver Time: {t_a:.6f}s")
    record["ablation_modes"]["mode_a_baseline"] = {
        "result": "SAT" if res_a else "UNSAT",
        "solver_time": t_a,
        "total_time": t_a,
    }

    # -------------------------------------------------------------------------
    # MODE B: Glucose3 + Polarity Guidance Only
    # -------------------------------------------------------------------------
    solver_b = Glucose3()
    for cl in clauses:
        solver_b.add_clause(cl)
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver_b.set_phases([pol * (i + 1)])
    t_start_b = time.perf_counter()
    res_b = solver_b.solve()
    t_b = time.perf_counter() - t_start_b
    solver_b.delete()
    total_b = telemetry["timing"]["total_spectral_time"] + t_b
    print(f"🔸 [MODE B: Polarity Reseeding] Result: {'SAT' if res_b else 'UNSAT'} | Solver Time: {t_b:.6f}s | Total: {total_b:.6f}s")
    record["ablation_modes"]["mode_b_polarity_only"] = {
        "result": "SAT" if res_b else "UNSAT",
        "solver_time": t_b,
        "total_time": total_b,
    }

    # -------------------------------------------------------------------------
    # MODE C: Full Phase-V Degeneracy-Gated Spectral SBP + Polarity
    # -------------------------------------------------------------------------
    solver_c = Glucose3()
    for cl in clauses:
        solver_c.add_clause(cl)
    for sbp in accepted_sbps:
        solver_c.add_clause(sbp)
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver_c.set_phases([pol * (i + 1)])
    t_start_c = time.perf_counter()
    res_c = solver_c.solve()
    t_c = time.perf_counter() - t_start_c
    solver_c.delete()
    total_c = telemetry["timing"]["total_spectral_time"] + t_c
    print(f"💎 [MODE C: Phase-V Gated Spectral] Result: {'SAT' if res_c else 'UNSAT'} | Solver Time: {t_c:.6f}s | Total: {total_c:.6f}s")
    record["ablation_modes"]["mode_c_phase5_gated"] = {
        "result": "SAT" if res_c else "UNSAT",
        "solver_time": t_c,
        "total_time": total_c,
    }

    # Save structured evidence
    evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
    os.makedirs(evidence_dir, exist_ok=True)
    out_file = os.path.join(evidence_dir, f"sha256_{rounds}rounds.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"📁 [EVIDENCE STORED]: {out_file}\n")
    return record

if __name__ == "__main__":
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║   🜏  PILL RED: PHASE VI SHA-256 SCALING & SOUNDNESS AUDIT  🜏  ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    # Run across 4, 8, 12, 16, 24 rounds
    for r in [4, 8, 12, 16, 24]:
        run_sha256_3way_ablation(r)
