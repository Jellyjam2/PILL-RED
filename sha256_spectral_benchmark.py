import os
import sys
import time
import math
import statistics
from spectral_bridge import IntegratedSovereignLumina

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# High-speed execution configuration constants
ROUND_STEPS = [4, 8, 16, 24, 32]
COMPACT_VARIABLES = True
EPSILON = 1e-4
WARMUP_RUNS = 2
MEASURED_RUNS = 5

def simulate_sha256_round_clauses(target_rounds, use_compact_vars=True):
    """
    Replicates the exact variable mapping equation from Satisfiable.py (L59-72)
    Var(r, i) = 1000 * (r + 1) + i for isolated multi-round circuit execution.
    
    If use_compact_vars=True, remaps sparse variable IDs (1000, 2000...) into 
    a contiguous 1..N index space to optimize the Graph Laplacian B matrix.
    """
    raw_clauses = []
    
    for r in range(target_rounds):
        r_offset = 1000 * (r + 1)
        
        for b in range(1, 32):  # Working across 32-bit word structures
            x = r_offset + b
            y = r_offset + b + 32
            z = r_offset + b + 64
            r_out = r_offset + b + 96
            
            # Non-linear Ch(x,y,z) CNF clauses
            raw_clauses.append([-x, -y, r_out])
            raw_clauses.append([-x, y, -r_out])
            raw_clauses.append([x, -z, r_out])
            raw_clauses.append([x, z, -r_out])
            
            # Inter-round dependency
            if r > 0:
                prev_offset = 1000 * r
                raw_clauses.append([-(prev_offset + b + 96), x])

    if not use_compact_vars:
        flat_vars = set(abs(lit) for clause in raw_clauses for lit in clause)
        max_var_index = max(flat_vars) if flat_vars else 0
        return max_var_index, raw_clauses

    # Compact variable compression: map distinct active variable IDs to 1..N
    unique_vars = sorted(list(set(abs(lit) for clause in raw_clauses for lit in clause)))
    var_map = {old_id: new_id + 1 for new_id, old_id in enumerate(unique_vars)}
    
    compact_clauses = []
    for clause in raw_clauses:
        compact_clause = [var_map[abs(lit)] if lit > 0 else -var_map[abs(lit)] for lit in clause]
        compact_clauses.append(compact_clause)
        
    num_compact_vars = len(unique_vars)
    return num_compact_vars, compact_clauses

def execute_scaling_audit(rust_library_path=None):
    print("=========================================================================")
    print("🔬 [EXPERIMENT] RUNNING MULTI-ROUND SHA-256 FIEDLER OPTIMIZATION AUDIT  ")
    print("=========================================================================\n")
    
    if rust_library_path is None:
        candidate_paths = [
            r"C:\PILL RED\target\release\pill_red_core.dll",
            r"C:\LUMINA RED PILL\target\release\aerowave_dsp.dll",
            r"C:\PILL RED\pill_red_core.dll",
            r"C:\LUMINA RED PILL\aerowave_dsp.dll",
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                rust_library_path = p
                break

    print(f"🏛️ [CORE ENGINE]: Using Rust FFI at: {rust_library_path}\n")

    for rounds in ROUND_STEPS:
        print(f"--- Round Target: {rounds} Rounds ---")
        
        # 1. Synthesize unrolled circuit configuration once
        num_vars, clauses = simulate_sha256_round_clauses(rounds, use_compact_vars=COMPACT_VARIABLES)
        clause_density = len(clauses) / num_vars if num_vars > 0 else 0
        print(f"📈 [DAG MAP] Active Variables: {num_vars} | Total Clauses: {len(clauses)} | Density (m/n): {clause_density:.3f}")
        
        # 2. Warmup Runs
        print(f"🔥 [WARMUP] Running {WARMUP_RUNS} iterations...")
        for w_idx in range(WARMUP_RUNS):
            pipeline = IntegratedSovereignLumina(
                num_vars=num_vars, 
                clauses=clauses, 
                rust_path=rust_library_path
            )
            pipeline.execute_hybrid_solve(epsilon=EPSILON)
            
        # 3. Measured Runs
        print(f"⏱️ [MEASURE] Running {MEASURED_RUNS} timed iterations...")
        durations = []
        is_sat = False
        for m_idx in range(MEASURED_RUNS):
            pipeline = IntegratedSovereignLumina(
                num_vars=num_vars, 
                clauses=clauses, 
                rust_path=rust_library_path
            )
            start_time = time.perf_counter()
            is_sat, model, sbp_injected, diag = pipeline.execute_hybrid_solve(epsilon=EPSILON)
            duration = time.perf_counter() - start_time
            durations.append(duration)

        # 4. Latency and Throughput Metrics
        min_val = min(durations)
        median_val = statistics.median(durations)
        
        sorted_durations = sorted(durations)
        p95_idx = max(0, min(len(sorted_durations) - 1, math.ceil(0.95 * len(sorted_durations)) - 1))
        p95_val = sorted_durations[p95_idx]
        
        vars_per_sec = num_vars / median_val if median_val > 0 else 0
        clauses_per_sec = len(clauses) / median_val if median_val > 0 else 0
        
        print(f"⏱️ [LATENCY] Min: {min_val:.4f}s | Median: {median_val:.4f}s | P95: {p95_val:.4f}s")
        print(f"⚡ [THROUGHPUT] {vars_per_sec:.2f} vars/sec | {clauses_per_sec:.2f} clauses/sec")
        print(f"🏁 Status for {rounds} Rounds: {'SUCCESS (SAT)' if is_sat else 'UNSAT'}\n")

if __name__ == "__main__":
    execute_scaling_audit()
