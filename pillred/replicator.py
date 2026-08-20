"""
PILL RED: Deterministic Experiment Replicator for Phases I through XVIII.
"""

import os
import sys
import subprocess
from typing import Dict, Any

PHASE_MAP = {
    "IX": "benchmarks/sha256_spectral_benchmark.py",
    "14": "benchmarks/phase14_dual_field_suite.py",
    "XIV": "benchmarks/phase14_dual_field_suite.py",
    "15": "benchmarks/phase15_nonlinear_degree_ladder.py",
    "XV": "benchmarks/phase15_nonlinear_degree_ladder.py",
    "16": "benchmarks/phase16_tensor_compression_suite.py",
    "XVI": "benchmarks/phase16_tensor_compression_suite.py",
    "17": "benchmarks/phase17_valuation_compression_suite.py",
    "XVII": "benchmarks/phase17_valuation_compression_suite.py",
    "18": "benchmarks/phase18_global_valuation_suite.py",
    "XVIII": "benchmarks/phase18_global_valuation_suite.py",
}

def replicate_experiment(phase_id: str) -> bool:
    clean_id = phase_id.upper().replace("PHASE", "").replace("EXP-", "").strip()
    if clean_id not in PHASE_MAP:
        print(f"❌ Unknown Phase ID: '{phase_id}'. Available: {list(PHASE_MAP.keys())}")
        return False

    script_path = PHASE_MAP[clean_id]
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_script = os.path.join(root_dir, script_path)

    print("=" * 100)
    print(f"      🔴 PILL RED REPLICATION ENGINE: EXECUTING PHASE {clean_id.upper()}")
    print("=" * 100)
    print(f"📁 Benchmark Harness: {full_script}")
    print("-" * 100)

    res = subprocess.run([sys.executable, full_script], cwd=root_dir)
    return (res.returncode == 0)
