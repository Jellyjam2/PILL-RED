#!/usr/bin/env python3
# 🜏 PILL RED: EXP-PHASE7-SPECTRAL-OBSERVABLE-001 🜏
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

def build_sha256_dual_circuit(target_rounds=16):
    """
    Constructs multi-round SHA-256 compression circuit with explicit manifest.
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
                initial_input_vars.extend([y, z])
                
            raw_clauses.append([-x, -y, r_out])
            raw_clauses.append([-x, y, -r_out])
            raw_clauses.append([x, -z, r_out])
            raw_clauses.append([x, z, -r_out])
            
            if r > 0:
                prev_offset = 1000 * r
                raw_clauses.append([-(prev_offset + b + 96), x])
                
        if r == target_rounds - 1:
            final_output_vars = current_round_outs

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

def construct_base_matrices(num_vars, clauses):
    m = len(clauses)
    n = num_vars
    B = np.zeros((m, n), dtype=np.float32)
    for c_idx, clause in enumerate(clauses):
        for literal in clause:
            var_idx = abs(literal) - 1
            if var_idx < n:
                sign = 1.0 if literal > 0 else -1.0
                B[c_idx, var_idx] = sign
    L = B.T @ B
    return B, L

def run_mode_a(clauses):
    """Mode A: Pure Glucose3 Baseline"""
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    t_start = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start
    stats = solver.accum_stats()
    solver.delete()
    return {"mode": "Mode A (Pure Glucose3)", "result": "SAT" if res else "UNSAT", "solver_time": t_solve, "total_time": t_solve, "stats": stats, "sbp_injected": 0}

def run_mode_b_fiedler_gated(num_vars, clauses, B, L):
    """Mode B: Standard Fiedler Vector (v_2) with Phase-V Degeneracy Safety Gate"""
    t_start_prep = time.perf_counter()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    fiedler_gap = float(eigenvalues[2] - eigenvalues[1]) if len(eigenvalues) > 2 else 0.0
    fiedler_vec = eigenvectors[:, 1] if num_vars > 1 else eigenvectors[:, 0]
    
    sbp_clauses = []
    is_degenerate = bool(fiedler_gap < 0.05)
    
    if not is_degenerate:
        degrees = np.diag(L)
        for u in range(num_vars):
            if len(sbp_clauses) >= 2 * num_vars:
                break
            for v in range(u + 1, num_vars):
                if len(sbp_clauses) >= 2 * num_vars:
                    break
                if abs(fiedler_vec[u] - fiedler_vec[v]) < 1e-4 and abs(degrees[u] - degrees[v]) < 1e-3:
                    sbp_clauses.append([-(u + 1), (v + 1)])
    t_prep = time.perf_counter() - t_start_prep
    
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    for sbp in sbp_clauses:
        solver.add_clause(sbp)
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver.set_phases([pol * (i + 1)])
        
    t_start_solve = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start_solve
    stats = solver.accum_stats()
    solver.delete()
    
    return {"mode": "Mode B (Fiedler + Phase-V Gate)", "result": "SAT" if res else "UNSAT", "prep_time": t_prep, "solver_time": t_solve, "total_time": t_prep + t_solve, "stats": stats, "sbp_injected": len(sbp_clauses), "fiedler_gap": fiedler_gap, "gated": is_degenerate}

def run_mode_c_higher_modes(num_vars, clauses, B, L, k=8):
    """Mode C: Higher-Order Multi-Mode Joint Geometry (v_2 ... v_k)"""
    t_start_prep = time.perf_counter()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    k_modes = min(k, eigenvectors.shape[1])
    subspace_coords = eigenvectors[:, 1:k_modes] # shape (n, k-1)
    
    degrees = np.diag(L)
    sbp_clauses = []
    sbp_cap = 2 * num_vars
    
    for u in range(num_vars):
        if len(sbp_clauses) >= sbp_cap:
            break
        for v in range(u + 1, num_vars):
            if len(sbp_clauses) >= sbp_cap:
                break
            # Joint Euclidean distance across top k modes
            dist_k = np.linalg.norm(subspace_coords[u] - subspace_coords[v])
            if dist_k < 1e-4 and abs(degrees[u] - degrees[v]) < 1e-3:
                sbp_clauses.append([-(u + 1), (v + 1)])
    t_prep = time.perf_counter() - t_start_prep
    
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    for sbp in sbp_clauses:
        solver.add_clause(sbp)
        
    # Phase guidance from dominant higher mode
    dominant_vec = subspace_coords[:, -1]
    for i in range(num_vars):
        pol = 1 if dominant_vec[i] >= 0.0 else -1
        solver.set_phases([pol * (i + 1)])
        
    t_start_solve = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start_solve
    stats = solver.accum_stats()
    solver.delete()
    
    return {"mode": "Mode C (Higher Modes v_2..v_k)", "result": "SAT" if res else "UNSAT", "prep_time": t_prep, "solver_time": t_solve, "total_time": t_prep + t_solve, "stats": stats, "sbp_injected": len(sbp_clauses)}

def run_mode_d_subspace_projector(num_vars, clauses, B, L, k_subspace=16):
    """Mode D: Subspace Projector Operator P = sum(v_i v_i^T) (Basis-Rotation Invariant)"""
    t_start_prep = time.perf_counter()
    eigenvalues, eigenvectors = np.linalg.eigh(L)
    k_eff = min(k_subspace, eigenvectors.shape[1])
    V_sub = eigenvectors[:, 0:k_eff] # First k eigenvectors
    P = V_sub @ V_sub.T # Projector matrix (n x n)
    
    degrees = np.diag(L)
    sbp_clauses = []
    sbp_cap = 2 * num_vars
    
    for u in range(num_vars):
        if len(sbp_clauses) >= sbp_cap:
            break
        for v in range(u + 1, num_vars):
            if len(sbp_clauses) >= sbp_cap:
                break
            # Projector column distance
            dist_p = np.linalg.norm(P[:, u] - P[:, v])
            if dist_p < 1e-4 and abs(degrees[u] - degrees[v]) < 1e-3:
                sbp_clauses.append([-(u + 1), (v + 1)])
    t_prep = time.perf_counter() - t_start_prep
    
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    for sbp in sbp_clauses:
        solver.add_clause(sbp)
        
    t_start_solve = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start_solve
    stats = solver.accum_stats()
    solver.delete()
    
    return {"mode": "Mode D (Projector Operator P)", "result": "SAT" if res else "UNSAT", "prep_time": t_prep, "solver_time": t_solve, "total_time": t_prep + t_solve, "stats": stats, "sbp_injected": len(sbp_clauses)}

def run_mode_e_boundary_conditioned_manifold(num_vars, base_clauses, boundary_clauses):
    """Mode E: Boundary-Conditioned Laplacian Manifold L_boundary with weighted boundary rows"""
    t_start_prep = time.perf_counter()
    total_clauses = base_clauses + boundary_clauses
    m = len(total_clauses)
    n = num_vars
    
    # Boundary-weighted incidence matrix
    B_weighted = np.zeros((m, n), dtype=np.float32)
    gamma = 10.0 # Boundary weight multiplier
    
    for c_idx, clause in enumerate(total_clauses):
        weight = gamma if c_idx >= len(base_clauses) else 1.0
        for literal in clause:
            var_idx = abs(literal) - 1
            if var_idx < n:
                sign = weight if literal > 0 else -weight
                B_weighted[c_idx, var_idx] = sign
                
    L_boundary = B_weighted.T @ B_weighted
    eigenvalues, eigenvectors = np.linalg.eigh(L_boundary)
    
    lambda_1 = float(eigenvalues[0])
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_3 = float(eigenvalues[2]) if len(eigenvalues) > 2 else 0.0
    delta_f_boundary = float(lambda_3 - lambda_2)
    
    fiedler_boundary = eigenvectors[:, 1] if n > 1 else eigenvectors[:, 0]
    degrees = np.diag(L_boundary)
    
    sbp_clauses = []
    sbp_cap = 2 * num_vars
    is_degenerate = bool(delta_f_boundary < 0.05)
    
    if not is_degenerate:
        for u in range(num_vars):
            if len(sbp_clauses) >= sbp_cap:
                break
            for v in range(u + 1, n):
                if len(sbp_clauses) >= sbp_cap:
                    break
                if abs(fiedler_boundary[u] - fiedler_boundary[v]) < 1e-4 and abs(degrees[u] - degrees[v]) < 1e-3:
                    sbp_clauses.append([-(u + 1), (v + 1)])
    t_prep = time.perf_counter() - t_start_prep
    
    solver = Glucose3()
    for cl in total_clauses:
        solver.add_clause(cl)
    for sbp in sbp_clauses:
        solver.add_clause(sbp)
    for i in range(num_vars):
        pol = 1 if fiedler_boundary[i] >= 0.0 else -1
        solver.set_phases([pol * (i + 1)])
        
    t_start_solve = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start_solve
    stats = solver.accum_stats()
    solver.delete()
    
    return {"mode": "Mode E (Boundary-Conditioned Manifold)", "result": "SAT" if res else "UNSAT", "prep_time": t_prep, "solver_time": t_solve, "total_time": t_prep + t_solve, "stats": stats, "sbp_injected": len(sbp_clauses), "delta_f_boundary": delta_f_boundary, "gated": is_degenerate}

def execute_phase7_observable_ablation(manifest, in_bits=256, out_bits=32, seeds=[42, 43, 44, 45, 46]):
    print(f"\n{'='*80}")
    print(f"  🔬 EXP-PHASE7-SPECTRAL-OBSERVABLE-001: 5-MODE OBSERVABLE ABLATION")
    print(f"  Target Instance: 16 Rounds | {in_bits} Input Bits | {out_bits} Output Bits")
    print(f"{'='*80}\n")
    
    all_seed_results = []
    
    for seed in seeds:
        print(f"--- 🎲 Testing Instance Seed: {seed} ---")
        rng = random.Random(seed)
        base_clauses = [list(c) for c in manifest["clauses"]]
        num_vars = manifest["num_vars"]
        input_vars = manifest["input_vars"]
        output_vars = manifest["output_vars"]
        
        # Dual boundary clauses
        boundary_clauses = []
        for i in range(min(in_bits, len(input_vars))):
            v = input_vars[i]
            val = rng.randint(0, 1)
            boundary_clauses.append([v] if val else [-v])
            
        for i in range(min(out_bits, len(output_vars))):
            v = output_vars[i]
            val = rng.randint(0, 1)
            boundary_clauses.append([v] if val else [-v])
            
        total_clauses = base_clauses + boundary_clauses
        B, L = construct_base_matrices(num_vars, total_clauses)
        
        # Execute 5 Observable Modes
        res_a = run_mode_a(total_clauses)
        res_b = run_mode_b_fiedler_gated(num_vars, total_clauses, B, L)
        res_c = run_mode_c_higher_modes(num_vars, total_clauses, B, L, k=8)
        res_d = run_mode_d_subspace_projector(num_vars, total_clauses, B, L, k_subspace=16)
        res_e = run_mode_e_boundary_conditioned_manifold(num_vars, base_clauses, boundary_clauses)
        
        modes = [res_a, res_b, res_c, res_d, res_e]
        for m in modes:
            conf = m["stats"].get("conflicts", 0)
            dec = m["stats"].get("decisions", 0)
            sbp = m.get("sbp_injected", 0)
            print(f"  {m['mode']:<36} | {m['result']:<5} | Conf: {conf:3d} | Dec: {dec:5d} | SBPs: {sbp:3d} | Solve: {m['solver_time']*1000:6.2f}ms")
            
        seed_record = {
            "seed": seed,
            "input_bits": in_bits,
            "output_bits": out_bits,
            "variables": num_vars,
            "clauses": len(total_clauses),
            "modes": modes,
        }
        all_seed_results.append(seed_record)
        print()

    # Save to Evidence
    evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
    os.makedirs(evidence_dir, exist_ok=True)
    out_file = os.path.join(evidence_dir, "EXP_PHASE7_SPECTRAL_OBSERVABLE_DATASET.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(all_seed_results, f, indent=2)
    print(f"📁 [PHASE VII DATASET STORED]: {out_file}")
    return all_seed_results

if __name__ == "__main__":
    manifest = build_sha256_dual_circuit(target_rounds=16)
    execute_phase7_observable_ablation(manifest, in_bits=256, out_bits=32, seeds=[42, 43, 44, 45, 46])
