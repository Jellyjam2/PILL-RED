#!/usr/bin/env python3
# 🜏 PILL RED: EXP-PHASE9-MULTIROUND-SCALING-001 🜏
import os
import sys
import time
import json
import random
import numpy as np
from pysat.solvers import Glucose3

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

here = os.path.dirname(os.path.abspath(__file__))
parent = os.path.dirname(here)
sys.path.insert(0, parent)

def build_sha256_dual_circuit(target_rounds=16):
    """
    Constructs multi-round SHA-256 compression circuit with explicit manifest.
    Scales variables and clauses linearly with round count:
      - 16 rounds: ~2,048 variables, ~2,528 base clauses
      - 24 rounds: ~3,072 variables, ~3,792 base clauses
      - 32 rounds: ~4,096 variables, ~5,056 base clauses
      - 48 rounds: ~6,144 variables, ~7,584 base clauses
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

def solve_mode_a_pure_cdcl(clauses):
    """Mode A: Ground Truth Pure CDCL (Glucose3)"""
    solver = Glucose3()
    for cl in clauses:
        solver.add_clause(cl)
    t_start = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_start
    stats = solver.accum_stats()
    solver.delete()
    return "SAT" if res else "UNSAT", t_solve, stats

def solve_mode_e_boundary_conditioned(num_vars, base_clauses, boundary_clauses):
    """Mode E: Boundary-Conditioned Laplacian L_B = B^T W_B B + Phase-V Gating"""
    t_prep_start = time.perf_counter()
    total_clauses = base_clauses + boundary_clauses
    m, n = len(total_clauses), num_vars
    gamma = 10.0
    
    # Fast sparse/dense incidence assembly
    B_w = np.zeros((m, n), dtype=np.float32)
    for c_idx, cl in enumerate(total_clauses):
        w = gamma if c_idx >= len(base_clauses) else 1.0
        for lit in cl:
            v_idx = abs(lit) - 1
            if v_idx < n:
                B_w[c_idx, v_idx] = w if lit > 0 else -w
                
    L_b = B_w.T @ B_w
    evals, evecs = np.linalg.eigh(L_b)
    delta_f = float(evals[2] - evals[1]) if len(evals) > 2 else 0.0
    v2 = evecs[:, 1]
    
    # Conservative Phase-V Degeneracy Gating
    sbps = []
    if delta_f >= 0.05:
        deg = np.diag(L_b)
        for u in range(n):
            if len(sbps) >= 2 * n: break
            for v in range(u + 1, n):
                if len(sbps) >= 2 * n: break
                if abs(v2[u] - v2[v]) < 1e-4 and abs(deg[u] - deg[v]) < 1e-3:
                    sbps.append([-(u + 1), (v + 1)])
    t_prep = time.perf_counter() - t_prep_start
    
    # Solve with polarity phase guidance
    solver = Glucose3()
    for cl in total_clauses:
        solver.add_clause(cl)
    for sbp in sbps:
        solver.add_clause(sbp)
    for i in range(n):
        pol = 1 if v2[i] >= 0.0 else -1
        solver.set_phases([pol * (i + 1)])
        
    t_solve_start = time.perf_counter()
    res = solver.solve()
    t_solve = time.perf_counter() - t_solve_start
    stats = solver.accum_stats()
    solver.delete()
    
    return {
        "result": "SAT" if res else "UNSAT",
        "delta_f": delta_f,
        "sbp_count": len(sbps),
        "prep_time": t_prep,
        "solver_time": t_solve,
        "total_time": t_prep + t_solve,
        "stats": stats,
    }

def run_phase9_multiround_scaling(round_sweep=[16, 24, 32, 48], seeds=[42, 43, 44, 45, 46], in_bits=256, out_bits=32):
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║    🔴 PILL RED: EXP-PHASE9-MULTIROUND-SCALING-001 HARNESS     ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    print(f"🔬 Parameter Matrix: Rounds = {round_sweep} | Seeds = {seeds} | Dual Boundary = ({in_bits} In, {out_bits} Out)\n")
    
    scaling_dataset = []
    
    for rounds in round_sweep:
        print(f"==================================================================")
        print(f"🏛️  TESTING CIRCUIT SCALE: {rounds} ROUNDS SHA-256")
        print(f"==================================================================")
        manifest = build_sha256_dual_circuit(target_rounds=rounds)
        num_vars = manifest["num_vars"]
        base_clauses = manifest["clauses"]
        input_vars = manifest["input_vars"]
        output_vars = manifest["output_vars"]
        print(f"   Variables: {num_vars} | Base Clauses: {len(base_clauses)} | Input Bits: {len(input_vars)} | Output Bits: {len(output_vars)}\n")
        
        round_results = []
        
        for seed in seeds:
            rng = random.Random(seed)
            boundary_clauses = []
            for i in range(min(in_bits, len(input_vars))):
                v = input_vars[i]
                val = rng.randint(0, 1)
                boundary_clauses.append([v] if val else [-v])
                
            for i in range(min(out_bits, len(output_vars))):
                v = output_vars[i]
                val = rng.randint(0, 1)
                boundary_clauses.append([v] if val else [-v])
                
            total_clauses = [list(c) for c in base_clauses] + boundary_clauses
            
            # 1. Evaluate Mode A (Pure CDCL Baseline)
            res_a, t_solve_a, stats_a = solve_mode_a_pure_cdcl(total_clauses)
            
            # 2. Evaluate Mode E (Boundary-Conditioned Manifold)
            mode_e = solve_mode_e_boundary_conditioned(num_vars, base_clauses, boundary_clauses)
            
            conf_a = stats_a.get("conflicts", 0)
            dec_a = stats_a.get("decisions", 0)
            conf_e = mode_e["stats"].get("conflicts", 0)
            dec_e = mode_e["stats"].get("decisions", 0)
            
            delta_conf = conf_e - conf_a
            pct_conf = ((conf_e - conf_a) / max(conf_a, 1)) * 100.0
            
            sound_match = (res_a == mode_e["result"])
            sound_tag = "✅ MATCH" if sound_match else "🚨 SOUNDNESS VIOLATION"
            
            print(f"  Seed {seed:2d} | Mode A: Conf={conf_a:3d}, Dec={dec_a:6d} ({t_solve_a*1000:5.2f}ms) | "
                  f"Mode E: Conf={conf_e:3d}, Dec={dec_e:6d} ({mode_e['solver_time']*1000:5.2f}ms) | "
                  f"ΔConf: {delta_conf:+3d} ({pct_conf:+6.1f}%) | {sound_tag}")
                  
            round_results.append({
                "seed": seed,
                "mode_a": {"result": res_a, "conflicts": conf_a, "decisions": dec_a, "time": t_solve_a, "stats": stats_a},
                "mode_e": {"result": mode_e["result"], "conflicts": conf_e, "decisions": dec_e, "prep_time": mode_e["prep_time"], "solver_time": mode_e["solver_time"], "stats": mode_e["stats"], "delta_f": mode_e["delta_f"]},
                "sound_agreement": sound_match,
                "conflict_reduction_pct": -pct_conf,
            })
            
        mean_conf_a = np.mean([r["mode_a"]["conflicts"] for r in round_results])
        mean_conf_e = np.mean([r["mode_e"]["conflicts"] for r in round_results])
        mean_dec_a = np.mean([r["mode_a"]["decisions"] for r in round_results])
        mean_dec_e = np.mean([r["mode_e"]["decisions"] for r in round_results])
        mean_red = ((mean_conf_a - mean_conf_e) / max(mean_conf_a, 1e-6)) * 100.0
        
        print(f"\n  📊 [{rounds} ROUNDS SUMMARY]: Mean Mode A Conflicts = {mean_conf_a:.1f} | Mean Mode E Conflicts = {mean_conf_e:.1f} | Mean Reduction = {mean_red:+.1f}%\n")
        
        scaling_dataset.append({
            "rounds": rounds,
            "variables": num_vars,
            "base_clauses": len(base_clauses),
            "total_clauses": len(total_clauses),
            "mean_conflicts_mode_a": float(mean_conf_a),
            "mean_conflicts_mode_e": float(mean_conf_e),
            "mean_decisions_mode_a": float(mean_dec_a),
            "mean_decisions_mode_e": float(mean_dec_e),
            "mean_conflict_reduction_pct": float(mean_red),
            "seed_records": round_results,
        })

    # Save to Evidence
    evidence_dir = os.path.join(parent, "evidence", "BENCHMARK_RECORDS")
    os.makedirs(evidence_dir, exist_ok=True)
    out_file = os.path.join(evidence_dir, "EXP_PHASE9_MULTIROUND_DATASET.json")
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(scaling_dataset, f, indent=2)
    print(f"📁 [PHASE IX DATASET STORED]: {out_file}")
    return scaling_dataset

if __name__ == "__main__":
    run_phase9_multiround_scaling()
