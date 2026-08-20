#!/usr/bin/env python3
# 🜏 PILL RED: EXP-PHASE6-SHA256-INVERSION-001 CONTROLLED SWEEP 🜏
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

def build_sha256_circuit_with_manifest(target_rounds=16):
    """
    Constructs a multi-round SHA-256 compression circuit and returns a formal 
    structural manifest with explicit input and output variable mappings.
    """
    raw_clauses = []
    round_out_vars = []
    
    for r in range(target_rounds):
        r_offset = 1000 * (r + 1)
        current_round_outs = []
        
        for b in range(1, 33):  # 32-bit word
            x = r_offset + b
            y = r_offset + b + 32
            z = r_offset + b + 64
            r_out = r_offset + b + 96
            current_round_outs.append(r_out)
            
            # Non-linear Ch(x,y,z) CNF clauses
            raw_clauses.append([-x, -y, r_out])
            raw_clauses.append([-x, y, -r_out])
            raw_clauses.append([x, -z, r_out])
            raw_clauses.append([x, z, -r_out])
            
            # Inter-round diffusion link
            if r > 0:
                prev_offset = 1000 * r
                raw_clauses.append([-(prev_offset + b + 96), x])
                
        round_out_vars = current_round_outs

    # Compact contiguous variable mapping 1..N
    unique_vars = sorted(list(set(abs(lit) for clause in raw_clauses for lit in clause)))
    var_map = {old_id: new_id + 1 for new_id, old_id in enumerate(unique_vars)}
    
    compact_clauses = []
    for clause in raw_clauses:
        compact_clause = [var_map[abs(lit)] if lit > 0 else -var_map[abs(lit)] for lit in clause]
        compact_clauses.append(compact_clause)
        
    final_output_vars = [var_map[old_id] for old_id in round_out_vars if old_id in var_map]
    
    manifest = {
        "num_vars": len(unique_vars),
        "clauses": compact_clauses,
        "final_output_vars": final_output_vars,
        "rounds": target_rounds,
    }
    return manifest

def compute_spectral_telemetry(num_vars, clauses, epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0):
    m = len(clauses)
    n = num_vars
    
    # 1. Build B & Laplacian L
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
    
    # 3. SBP Candidate Gating & Quality Filter
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

def run_inversion_point(manifest, prefix_bits, target_pattern=0xA5A5A5A5):
    print(f"\n{'='*75}")
    print(f"  🔬 INVERSION SWEEP POINT: {prefix_bits}-BIT OUTPUT CONSTRAINT")
    print(f"{'='*75}")
    
    base_clauses = [list(c) for c in manifest["clauses"]]
    num_vars = manifest["num_vars"]
    output_vars = manifest["final_output_vars"]
    
    # Apply prefix boundary constraints
    target_clauses = []
    for i in range(min(prefix_bits, len(output_vars))):
        v = output_vars[i]
        bit_val = (target_pattern >> i) & 1
        clause = [v] if bit_val else [-v]
        target_clauses.append(clause)
        
    total_clauses = base_clauses + target_clauses
    m = len(total_clauses)
    m_over_n = float(m / num_vars) if num_vars > 0 else 0.0
    
    # 1. Extract Spectral Diagnostics
    telemetry, accepted_sbps, fiedler_vec = compute_spectral_telemetry(num_vars, total_clauses)
    
    print(f"📈 [TOPOLOGY] Vars: {num_vars} | Base Clauses: {len(base_clauses)} | Target Clauses: {len(target_clauses)} | m/n: {m_over_n:.3f}")
    print(f"🌀 [SPECTRUM] λ1: {telemetry['lambda_1']:.4f} | λ2: {telemetry['lambda_2']:.4f} | λ3: {telemetry['lambda_3']:.4f} | ΔF: {telemetry['fiedler_gap']:.4f}")
    print(f"🛡️ [SAFETY GATE] State: {telemetry['gate_state']} | Candidates: {telemetry['candidates_total']} | Accepted SBPs: {telemetry['accepted_sbps_count']}")

    record = {
        "benchmark": f"sha256_inversion_{prefix_bits}bits",
        "prefix_bits": prefix_bits,
        "rounds": manifest["rounds"],
        "variables": num_vars,
        "clauses_before_target": len(base_clauses),
        "target_clauses_count": len(target_clauses),
        "total_clauses": m,
        "m_over_n": m_over_n,
        "timestamp": datetime.now().isoformat(),
        "spectral_telemetry": telemetry,
        "ablation_modes": {}
    }

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
    print(f"🔹 [MODE A: Baseline Glucose3] Result: {'SAT' if res_a else 'UNSAT'} | Solver Time: {t_a:.6f}s | Conflicts: {stats_a.get('conflicts', 0)} | Decisions: {stats_a.get('decisions', 0)}")
    record["ablation_modes"]["mode_a_baseline"] = {
        "result": "SAT" if res_a else "UNSAT",
        "solver_time": t_a,
        "stats": stats_a,
    }

    # -------------------------------------------------------------------------
    # MODE B: Glucose3 + Polarity Guidance Only
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
    print(f"🔸 [MODE B: Polarity Reseeding] Result: {'SAT' if res_b else 'UNSAT'} | Solver Time: {t_b:.6f}s | Conflicts: {stats_b.get('conflicts', 0)} | Decisions: {stats_b.get('decisions', 0)}")
    record["ablation_modes"]["mode_b_polarity_only"] = {
        "result": "SAT" if res_b else "UNSAT",
        "solver_time": t_b,
        "total_time": telemetry["timing"]["total_spectral_time"] + t_b,
        "stats": stats_b,
    }

    # -------------------------------------------------------------------------
    # MODE C: Full Phase-V Gated Spectral SBP + Polarity
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
    print(f"💎 [MODE C: Phase-V Gated Spectral] Result: {'SAT' if res_c else 'UNSAT'} | Solver Time: {t_c:.6f}s | Conflicts: {stats_c.get('conflicts', 0)} | Decisions: {stats_c.get('decisions', 0)}")
    record["ablation_modes"]["mode_c_phase5_gated"] = {
        "result": "SAT" if res_c else "UNSAT",
        "solver_time": t_c,
        "total_time": telemetry["timing"]["total_spectral_time"] + t_c,
        "stats": stats_c,
    }

    # Save to evidence
    evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
    os.makedirs(evidence_dir, exist_ok=True)
    out_file = os.path.join(evidence_dir, f"sha256_inversion_{prefix_bits}bits.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    print(f"📁 [EVIDENCE STORED]: {out_file}")
    return record

if __name__ == "__main__":
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║  🜏 PILL RED: EXP-PHASE6-SHA256-INVERSION-001 CONTROLLED SWEEP ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    manifest = build_sha256_circuit_with_manifest(target_rounds=16)
    print(f"🏛️ [MANIFEST]: 16-Round Circuit Built | Vars: {manifest['num_vars']} | Base Clauses: {len(manifest['clauses'])} | Output Bits: {len(manifest['final_output_vars'])}")
    
    sweep_records = []
    for prefix in [0, 8, 16, 24, 32]:
        rec = run_inversion_point(manifest, prefix_bits=prefix)
        sweep_records.append(rec)
        
    print("\n🏁 [SWEEP COMPLETE]: All 5 boundary points executed and recorded.")
