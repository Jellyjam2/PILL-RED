#!/usr/bin/env python3
# 🜏 PILL RED: 3-WAY CONTROLLED ABLATION & METRIC RECORDING SUITE 🜏
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
from spectral_bridge import IntegratedSovereignLumina

def get_full_adder_clauses(a, b, cin, s, cout):
    """Encodes 1-bit full adder into 3-SAT logic clauses."""
    return [
        (-a, -b, -cin, s), (a, b, -cin, s), (a, -b, cin, s), (-a, b, cin, s),
        (a, b, cin, -s), (-a, -b, cin, -s), (-a, b, -cin, -s), (a, -b, -cin, -s),
        (a, b, -cout), (a, cin, -cout), (b, cin, -cout),
        (-a, -b, cout), (-a, -cin, cout), (-b, -cin, cout)
    ]

def build_adder_benchmark(bit_width):
    num_vars = bit_width * 4 + 1
    a_vars = list(range(1, bit_width + 1))
    b_vars = list(range(bit_width + 1, 2 * bit_width + 1))
    s_vars = list(range(2 * bit_width + 1, 3 * bit_width + 1))
    c_vars = list(range(3 * bit_width + 1, 4 * bit_width + 2))
    
    clauses = [[-c_vars[0]]]
    for i in range(bit_width):
        cout = c_vars[i + 1]
        for cl in get_full_adder_clauses(a_vars[i], b_vars[i], c_vars[i], s_vars[i], cout):
            clauses.append(cl)
            
    target_sum = (1 << bit_width) - 1
    for i in range(bit_width):
        clauses.append([s_vars[i]] if (target_sum >> i) & 1 else [-s_vars[i]])
        
    return num_vars, clauses

def compute_matrix_diagnostics(num_vars, clauses):
    m = len(clauses)
    n = num_vars
    B = np.zeros((m, n), dtype=np.float32)
    for c_idx, clause in enumerate(clauses):
        for literal in clause:
            var_idx = abs(literal) - 1
            if var_idx < n:
                sign = 1.0 if literal > 0 else -1.0
                B[c_idx, var_idx] = sign
                
    nnz_B = int(np.count_nonzero(B))
    density_B = float(nnz_B / (m * n)) if (m * n) > 0 else 0.0
    
    # Laplacian L = B^T * B
    L = B.T @ B
    nnz_L = int(np.count_nonzero(L))
    density_L = float(nnz_L / (n * n)) if (n * n) > 0 else 0.0
    
    # Compute Eigenvalues
    eigenvalues = np.sort(np.linalg.eigvalsh(L))
    lambda_1 = float(eigenvalues[0]) if len(eigenvalues) > 0 else 0.0
    lambda_2 = float(eigenvalues[1]) if len(eigenvalues) > 1 else 0.0
    lambda_3 = float(eigenvalues[2]) if len(eigenvalues) > 2 else 0.0
    
    fiedler_gap = float(lambda_3 - lambda_2)
    norm_fiedler_gap = float((lambda_3 - lambda_2) / (lambda_2 + 1e-6))
    
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
    }

def run_controlled_ablation(instance_name, num_vars, clauses, rust_dll_path=None):
    print(f"\n==========================================================================")
    print(f"  🔬 CONTROLLED ABLATION: {instance_name} (Vars: {num_vars}, Clauses: {len(clauses)})")
    print(f"==========================================================================")
    
    # 1. Compute Matrix & Spectral Diagnostics
    spectral_start = time.perf_counter()
    diag = compute_matrix_diagnostics(num_vars, clauses)
    spectral_diag_time = time.perf_counter() - spectral_start
    
    print(f"📊 [DIAGNOSTICS] ρ(B): {diag['incidence_density']:.4f} | ρ(L): {diag['laplacian_density']:.4f}")
    print(f"🌀 [SPECTRUM] λ1: {diag['lambda_1']:.4f} | λ2: {diag['lambda_2']:.4f} | λ3: {diag['lambda_3']:.4f} | ΔF: {diag['fiedler_gap']:.4f}")

    results = {
        "instance": instance_name,
        "timestamp": datetime.now().isoformat(),
        "variables": num_vars,
        "clauses": len(clauses),
        "diagnostics": diag,
        "ablation_modes": {}
    }

    # -------------------------------------------------------------------------
    # MODE A: Pure Glucose3 Baseline
    # -------------------------------------------------------------------------
    solver_a = Glucose3()
    for cl in clauses:
        solver_a.add_clause(cl)
    start_a = time.perf_counter()
    res_a = solver_a.solve()
    time_a = time.perf_counter() - start_a
    solver_a.delete()
    print(f"🔹 [MODE A: Baseline Glucose3] Result: {'SAT' if res_a else 'UNSAT'} | Latency: {time_a:.6f}s")
    results["ablation_modes"]["mode_a_baseline"] = {
        "result": "SAT" if res_a else "UNSAT",
        "solver_time": time_a,
        "sbp_count": 0,
        "sbp_ratio": 0.0,
    }

    # -------------------------------------------------------------------------
    # MODE B: Glucose3 + Continuous Gradient Polarity Re-seeding Only
    # -------------------------------------------------------------------------
    engine_b = IntegratedSovereignLumina(num_vars=num_vars, clauses=clauses, rust_path=rust_dll_path)
    start_b = time.perf_counter()
    # Execute with large epsilon so 0 SBPs are injected, only polarities reseeded
    # Or explicitly reseed
    solver_b = Glucose3()
    for cl in clauses:
        solver_b.add_clause(cl)
    # Compute Fiedler for polarity
    B = np.zeros((len(clauses), num_vars), dtype=np.float32)
    for c_idx, cl in enumerate(clauses):
        for lit in cl:
            v_idx = abs(lit) - 1
            if v_idx < num_vars:
                B[c_idx, v_idx] = 1.0 if lit > 0 else -1.0
    _, vecs = np.linalg.eigh(B.T @ B)
    fiedler_vec = vecs[:, 1] if num_vars > 1 else vecs[:, 0]
    for i in range(num_vars):
        pol = 1 if fiedler_vec[i] >= 0.0 else -1
        solver_b.set_phases([pol * (i + 1)])
    res_b = solver_b.solve()
    time_b = time.perf_counter() - start_b
    solver_b.delete()
    print(f"🔸 [MODE B: Polarity Reseeding] Result: {'SAT' if res_b else 'UNSAT'} | Latency: {time_b:.6f}s")
    results["ablation_modes"]["mode_b_polarity_only"] = {
        "result": "SAT" if res_b else "UNSAT",
        "solver_time": time_b,
        "sbp_count": 0,
        "sbp_ratio": 0.0,
    }

    # -------------------------------------------------------------------------
    # MODE C: Full Spectral Pipeline (Fiedler SBP Injection + Polarity + Glucose3)
    # -------------------------------------------------------------------------
    engine_c = IntegratedSovereignLumina(num_vars=num_vars, clauses=clauses, rust_path=rust_dll_path)
    start_c = time.perf_counter()
    res_c, model_c, sbp_count_c, diag_c = engine_c.execute_hybrid_solve(epsilon=1e-4, min_spectral_gap=0.05, max_sbp_ratio=2.0)
    time_c = time.perf_counter() - start_c
    print(f"💎 [MODE C: Full Spectral+SBP] Result: {'SAT' if res_c else 'UNSAT'} | SBPs: {sbp_count_c} | Latency: {time_c:.6f}s")
    results["ablation_modes"]["mode_c_full_spectral"] = {
        "result": "SAT" if res_c else "UNSAT",
        "solver_time": time_c,
        "sbp_count": sbp_count_c,
        "sbp_ratio": float(sbp_count_c / len(clauses)) if len(clauses) > 0 else 0.0,
        "degeneracy_gated": diag_c.get("degeneracy_gated", False),
    }

    # Save to evidence directory
    evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
    os.makedirs(evidence_dir, exist_ok=True)
    out_file = os.path.join(evidence_dir, f"{instance_name}.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"📁 [EVIDENCE STORED]: {out_file}\n")
    return results

if __name__ == "__main__":
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║        🜏  PILL RED 3-WAY CONTROLLED ABLATION SUITE  🜏        ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    # Run Adder benchmarks at 8, 16, 32 bits
    for bits in [8, 16, 32]:
        n_vars, clauses = build_adder_benchmark(bits)
        run_controlled_ablation(f"adder_{bits}bit", n_vars, clauses)
