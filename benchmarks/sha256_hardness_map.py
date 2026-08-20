#!/usr/bin/env python3
# 🜏 PILL RED: EXP-PHASE6-SHA256-HARDNESS-MAP-001 🜏
import os
import sys
import time
import json
import random
from datetime import datetime
import numpy as np
from pysat.solvers import Glucose3

# Force utf-8 stdout encoding for Windows console compatibility
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path.insert(0, parent)

def build_sha256_circuit_with_dual_manifest(target_rounds=16):
    """
    Constructs multi-round SHA-256 compression logic and returns an explicit 
    manifest containing distinct input variable lanes and final output variable lanes.
    """
    raw_clauses = []
    initial_input_vars = []
    final_output_vars = []
    
    for r in range(target_rounds):
        r_offset = 1000 * (r + 1)
        current_round_outs = []
        
        for b in range(1, 33):
            x = r_offset + b
            y = r_offset + b + 32
            z = r_offset + b + 64
            r_out = r_offset + b + 96
            current_round_outs.append(r_out)
            
            if r == 0:
                initial_input_vars.extend([x, y, z])
            elif r < 4:
                # Add early round intermediate state to allow up to 256 input constraint bits
                initial_input_vars.extend([y, z])
                
            # Non-linear Ch(x,y,z) CNF clauses
            raw_clauses.append([-x, -y, r_out])
            raw_clauses.append([-x, y, -r_out])
            raw_clauses.append([x, -z, r_out])
            raw_clauses.append([x, z, -r_out])
            
            # Inter-round sequential diffusion dependency
            if r > 0:
                prev_offset = 1000 * r
                raw_clauses.append([-(prev_offset + b + 96), x])
                
        if r == target_rounds - 1:
            final_output_vars = current_round_outs

    # Compact contiguous variable mapping 1..N
    unique_vars = sorted(list(set(abs(lit) for clause in raw_clauses for lit in clause)))
    var_map = {old_id: new_id + 1 for new_id, old_id in enumerate(unique_vars)}
    
    compact_clauses = []
    for clause in raw_clauses:
        compact_clause = [var_map[abs(lit)] if lit > 0 else -var_map[abs(lit)] for lit in clause]
        compact_clauses.append(compact_clause)
        
    mapped_inputs = [var_map[old_id] for old_id in initial_input_vars if old_id in var_map]
    mapped_outputs = [var_map[old_id] for old_id in final_output_vars if old_id in var_map]
    
    return {
        "num_vars": len(unique_vars),
        "clauses": compact_clauses,
        "input_vars": mapped_inputs,
        "output_vars": mapped_outputs,
        "rounds": target_rounds,
    }

def compute_spectral_diagnostics(num_vars, clauses, epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0):
    m = len(clauses)
    n = num_vars
    
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
    mat_time = time.perf_counter() - t_start_mat
    
    t_start_eig = time.perf_counter()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    eig_time = time.perf_counter() - t_start_eig
    
    lambda_1 = float(eigenvalues[0]) if len(eigenvalues) > 0 else 0.0
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_3 = float(eigenvalues[2]) if len(eigenvalues) > 2 else 0.0
    fiedler_gap = float(lambda_3 - lambda_2)
    norm_fiedler_gap = float((lambda_3 - lambda_2) / (lambda_2 + 1e-6))
    
    fiedler_vec = eigenvectors[:, 1] if n > 1 else eigenvectors[:, 0]
    
    degrees = np.diag(L)
    sbp_cap = int(max_sbp_ratio * n)
    candidates_total = 0
    accepted_sbps = []
    
    is_degenerate = bool(fiedler_gap < min_spectral_gap)
    gate_state = "TRIGGERED_DEGENERACY_SUPPRESSED" if is_degenerate else "ACTIVE"
    
    if not is_degenerate:
        for u in range(n):
            if len(accepted_sbps) >= sbp_cap:
                break
            for v in range(u + 1, n):
                if len(accepted_sbps) >= sbp_cap:
                    break
                if abs(fiedler_vec[u] - fiedler_vec[v]) < epsilon:
                    candidates_total += 1
                    if abs(degrees[u] - degrees[v]) < 1e-3:
                        accepted_sbps.append([-(u + 1), (v + 1)])
    else:
        candidates_total = 0 # Gated
        
    return {
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
        "candidates_total": candidates_total,
        "accepted_sbps_count": len(accepted_sbps),
        "total_spectral_time": mat_time + eig_time,
    }, accepted_sbps, fiedler_vec

def evaluate_hardness_point(manifest, in_bits, out_bits, seed=42):
    rng = random.Random(seed)
    base_clauses = [list(c) for c in manifest["clauses"]]
    num_vars = manifest["num_vars"]
    input_vars = manifest["input_vars"]
    output_vars = manifest["output_vars"]
    
    # 1. Apply Input Prefix Constraints
    in_clauses = []
    for i in range(min(in_bits, len(input_vars))):
        v = input_vars[i]
        bit_val = rng.randint(0, 1)
        in_clauses.append([v] if bit_val else [-v])
        
    # 2. Apply Output Prefix Constraints
    out_clauses = []
    for i in range(min(out_bits, len(output_vars))):
        v = output_vars[i]
        bit_val = rng.randint(0, 1)
        out_clauses.append([v] if bit_val else [-v])
        
    total_clauses = base_clauses + in_clauses + out_clauses
    m = len(total_clauses)
    m_over_n = float(m / num_vars) if num_vars > 0 else 0.0
    
    # 3. Extract Spectral Data
    telemetry, accepted_sbps, fiedler_vec = compute_spectral_diagnostics(num_vars, total_clauses)
    
    # -------------------------------------------------------------------------
    # MODE A: Pure Glucose3 Baseline
    # -------------------------------------------------------------------------
    solver_a = Glucose3()
    for cl in total_clauses:
        solver_a.add_clause(cl)
    t_start_a = time.perf_counter()
    res_a = solver_a.solve()
    t_a = time.perf_counter() - t_start_a
    stats_a = solver_a.accum_stats()
    solver_a.delete()
    
    # -------------------------------------------------------------------------
    # MODE B: Polarity Guidance Only
    # -------------------------------------------------------------------------
    solver_b = Glucose3()
    for cl in total_clauses:
        solver_b.add_clause(cl)
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver_b.set_phases([pol * (i + 1)])
    t_start_b = time.perf_counter()
    res_b = solver_b.solve()
    t_b = time.perf_counter() - t_start_b
    stats_b = solver_b.accum_stats()
    solver_b.delete()
    
    # -------------------------------------------------------------------------
    # MODE C: Phase-V Gated Spectral SBP + Polarity
    # -------------------------------------------------------------------------
    solver_c = Glucose3()
    for cl in total_clauses:
        solver_c.add_clause(cl)
    for sbp in accepted_sbps:
        solver_c.add_clause(sbp)
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver_c.set_phases([pol * (i + 1)])
    t_start_c = time.perf_counter()
    res_c = solver_c.solve()
    t_c = time.perf_counter() - t_start_c
    stats_c = solver_c.accum_stats()
    solver_c.delete()
    
    # Classify Regime Empirically
    conflicts_a = stats_a.get("conflicts", 0)
    decisions_a = stats_a.get("decisions", 0)
    
    if not res_a:
        regime = "CONSTRAINED_UNSAT"
    elif conflicts_a == 0 and decisions_a < 100:
        regime = "TRIVIAL_UNIT_PROPAGATION"
    elif conflicts_a == 0:
        regime = "PROPAGATION_DOMINATED"
    elif conflicts_a < 100:
        regime = "SEARCH_EMERGING"
    else:
        regime = "SEARCH_DOMINATED"
        
    print(f"[{in_bits:3d} In | {out_bits:2d} Out] -> Mode A: {'SAT' if res_a else 'UNSAT'} (Conf: {conflicts_a:3d}, Dec: {decisions_a:5d}, Time: {t_a*1000:6.2f}ms) | ΔF: {telemetry['fiedler_gap']:.4f} | Regime: {regime}")
    
    record = {
        "input_bits": in_bits,
        "output_bits": out_bits,
        "seed": seed,
        "variables": num_vars,
        "base_clauses": len(base_clauses),
        "input_clauses": len(in_clauses),
        "output_clauses": len(out_clauses),
        "total_clauses": m,
        "m_over_n": m_over_n,
        "regime": regime,
        "spectral_telemetry": telemetry,
        "mode_a": {"result": "SAT" if res_a else "UNSAT", "time": t_a, "stats": stats_a},
        "mode_b": {"result": "SAT" if res_b else "UNSAT", "time": t_b, "stats": stats_b},
        "mode_c": {"result": "SAT" if res_c else "UNSAT", "time": t_c, "stats": stats_c},
    }
    return record

if __name__ == "__main__":
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🜏 PILL RED: EXP-PHASE6-SHA256-HARDNESS-MAP-001 SWEEP 🜏     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    manifest = build_sha256_circuit_with_dual_manifest(target_rounds=16)
    print(f"🏛️ [MANIFEST]: 16-Round Dual-Boundary Circuit | Vars: {manifest['num_vars']} | Base Clauses: {len(manifest['clauses'])} | Input Pool: {len(manifest['input_vars'])} | Output Pool: {len(manifest['output_vars'])}\n")
    
    # 2D Parameter Grid Sweep
    test_grid = [
        (0, 0),
        (32, 8),
        (64, 16),
        (96, 24),
        (128, 32),
        (160, 32),
        (192, 32),
        (224, 32),
        (256, 32),
    ]
    
    records = []
    for in_b, out_b in test_grid:
        rec = evaluate_hardness_point(manifest, in_b, out_b, seed=42)
        records.append(rec)
        
        # Save JSON record
        evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
        os.makedirs(evidence_dir, exist_ok=True)
        out_file = os.path.join(evidence_dir, f"hardness_map_in{in_b}_out{out_b}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(rec, f, indent=2)
            
    # Also save complete composite dataset
    composite_file = os.path.join(evidence_dir, "EXP_PHASE6_HARDNESS_MAP_DATASET.json")
    with open(composite_file, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2)
    print(f"\n📁 [DATASET STORED]: {composite_file}")
