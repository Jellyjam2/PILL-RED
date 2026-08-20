#!/usr/bin/env python3
# 🜏 PILL RED: UNIVERSAL DISCRETE-CONTINUOUS SOLVER & BENCHMARK SUITE 🜏
import os
import sys
import time
import random
from spectral_bridge import IntegratedSovereignLumina

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def generate_random_3sat(n, ratio=4.26):
    m = int(n * ratio)
    clauses = []
    for _ in range(m):
        vars_sample = random.sample(range(1, n + 1), 3)
        clause = [v if random.random() > 0.5 else -v for v in vars_sample]
        clauses.append(clause)
    return clauses

def get_full_adder_clauses(a, b, cin, s, cout):
    """Encodes 1-bit full adder into 3-SAT logic clauses."""
    return [
        (-a, -b, -cin, s), (a, b, -cin, s), (a, -b, cin, s), (-a, b, cin, s),
        (a, b, cin, -s), (-a, -b, cin, -s), (-a, b, -cin, -s), (a, -b, -cin, -s),
        (a, b, -cout), (a, cin, -cout), (b, cin, -cout),
        (-a, -b, cout), (-a, -cin, cout), (-b, -cin, cout)
    ]

def benchmark_adder_circuit(bit_width=16):
    print(f"\n{'='*70}")
    print(f"  🜏 BENCHMARK 1: {bit_width}-BIT FULL ADDER INVERSION (MODULAR SAT)")
    print(f"{'='*70}")
    
    num_vars = bit_width * 4 + 1
    a_vars = list(range(1, bit_width + 1))
    b_vars = list(range(bit_width + 1, 2 * bit_width + 1))
    s_vars = list(range(2 * bit_width + 1, 3 * bit_width + 1))
    c_vars = list(range(3 * bit_width + 1, 4 * bit_width + 2))
    
    clauses = [[-c_vars[0]]] # Initial carry is 0
    for i in range(bit_width):
        cout = c_vars[i + 1]
        for cl in get_full_adder_clauses(a_vars[i], b_vars[i], c_vars[i], s_vars[i], cout):
            clauses.append(cl)
            
    # Target sum: all 1s
    target_sum = (1 << bit_width) - 1
    for i in range(bit_width):
        clauses.append([s_vars[i]] if (target_sum >> i) & 1 else [-s_vars[i]])
        
    start_t = time.perf_counter()
    engine = IntegratedSovereignLumina(num_vars=num_vars, clauses=clauses)
    is_sat, model = engine.execute_hybrid_solve()
    duration = time.perf_counter() - start_t
    
    if is_sat and model:
        res_a = sum((1 << i) for i in range(bit_width) if model[a_vars[i]-1] > 0)
        res_b = sum((1 << i) for i in range(bit_width) if model[b_vars[i]-1] > 0)
        print(f"💎 [RESULT]: SOLVED in {duration:.4f}s! Inputs: A={res_a}, B={res_b} (Sum={res_a + res_b} == {target_sum})")
    else:
        print(f"❌ [RESULT]: Failed to find satisfying assignment in {duration:.4f}s")

def benchmark_phase_transition_3sat(num_vars=100):
    print(f"\n{'='*70}")
    print(f"  🜏 BENCHMARK 2: RANDOM 3-SAT AT CRITICAL RATIO (m/n = 4.26, n={num_vars})")
    print(f"{'='*70}")
    clauses = generate_random_3sat(num_vars, ratio=4.26)
    
    start_t = time.perf_counter()
    engine = IntegratedSovereignLumina(num_vars=num_vars, clauses=clauses)
    is_sat, model = engine.execute_hybrid_solve()
    duration = time.perf_counter() - start_t
    
    print(f"💎 [RESULT]: Solved in {duration:.4f}s! Status: {'SATISFIABLE' if is_sat else 'UNSATISFIABLE'}")

if __name__ == "__main__":
    print(r"""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                 🜏  P I L L   R E D  🜏                        ║
    ║   Discrete-Continuous Graph Laplacian & Spectral SAT Engine   ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    benchmark_adder_circuit(bit_width=16)
    benchmark_phase_transition_3sat(num_vars=80)
