#!/usr/bin/env python3
"""
🔴 PILL RED v1.0.0: THE ADVERSARIAL MATHEMATICAL LABORATORY FOR BOOLEAN COMPUTATION
Unified CLI for Representation Benchmarking, Adversarial Collision Testing, and Evidence Auditing.
"""

import os
import sys
import argparse
import json
import time

from pillred.interfaces import CandidateRepresentation
from pillred.evaluator import SixGateEvaluator
from pillred.replicator import replicate_experiment, PHASE_MAP
from pillred.candidates import (
    CDCLBaseline,
    SpectralLaplacianCandidate,
    GF2GaussianCandidate,
    TensorRankCandidate,
    VPTIProjectorCandidate
)
from pillred.families import (
    HighGirthExpanderFamily,
    IsoAlgebraicCollisionFamily,
    PureParityFamily,
    NonlinearDegreeLadderFamily,
    FeedforwardCircuitsFamily
)

CANDIDATES = {
    "cdcl": CDCLBaseline,
    "spectral": SpectralLaplacianCandidate,
    "gf2": GF2GaussianCandidate,
    "tensor": TensorRankCandidate,
    "vpti": VPTIProjectorCandidate
}

FAMILIES = {
    "high_girth_expander": HighGirthExpanderFamily,
    "iso_pairs": IsoAlgebraicCollisionFamily,
    "pure_parity": PureParityFamily,
    "nonlinear_ladder": NonlinearDegreeLadderFamily,
    "feedforward_circuits": FeedforwardCircuitsFamily
}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

def run_crucible_command(family_key: str, candidate_key: str, samples: int, out_dir: str):
    if family_key not in FAMILIES:
        print(f"❌ Unknown family: '{family_key}'. Available: {list(FAMILIES.keys())}")
        return
    if candidate_key not in CANDIDATES:
        print(f"❌ Unknown candidate: '{candidate_key}'. Available: {list(CANDIDATES.keys())}")
        return

    family = FAMILIES[family_key]()
    candidate = CANDIDATES[candidate_key]()
    evaluator = SixGateEvaluator(candidate)

    print("=" * 100)
    print("      🔴 PILL RED: ADVERSARIAL CRUCIBLE ENGINE v1.0")
    print("=" * 100)
    print(f"🏛️  Adversarial Family:  {family.name.upper()}")
    print(f"🔬 Candidate Method:    {candidate.name.upper()}")
    print(f"📊 Sample Count:        {samples}")
    print("=" * 100)

    results = []
    t0 = time.perf_counter()

    for idx in range(samples):
        pair_dict = family.generate_pair(seed=100 + idx)
        res_s, res_u, gates = evaluator.audit_pair(pair_dict)

        results.append({
            "sample_id": idx + 1,
            "sat_result": res_s.__dict__,
            "unsat_result": res_u.__dict__,
            "gates_passed": gates.__dict__,
            "all_gates_passed": gates.all_passed
        })

        print(f"  • Sample {idx+1:02d} | Val Sig (SAT/UNSAT): {res_s.valuation_signature:+5.2f} / {res_u.valuation_signature:+5.2f} | "
              f"Separated: {str(res_s.is_separated):5s} | Conflicts (S/U): {res_s.residual_conflicts:4d}/{res_u.residual_conflicts:4d} | "
              f"6-Gates: {'PASS' if gates.all_passed else 'FAIL/PARTIAL'}")

    total_time_ms = (time.perf_counter() - t0) * 1000.0
    sep_count = sum(1 for r in results if r["sat_result"]["is_separated"])
    all_gate_pass_count = sum(1 for r in results if r["all_gates_passed"])

    print("\n" + "=" * 100)
    print("📊 [CRUCIBLE VERDICT]:")
    print(f"   Collision Separation Rate: {sep_count}/{samples} ({(sep_count/samples)*100.0:.1f}%)")
    print(f"   All 6 Gates Conjunction:   {all_gate_pass_count}/{samples} ({(all_gate_pass_count/samples)*100.0:.1f}%)")
    print(f"   Total Audit Runtime:      {total_time_ms:.2f} ms")
    print("=" * 100)

    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"CRUCIBLE_EVIDENCE_{family.name.upper()}_{candidate.name.upper()}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump({
                "family": family.name,
                "candidate": candidate.name,
                "samples": samples,
                "total_time_ms": total_time_ms,
                "summary": {
                    "separation_rate_pct": (sep_count / samples) * 100.0,
                    "all_6_gates_pass_rate_pct": (all_gate_pass_count / samples) * 100.0
                },
                "results": results
            }, f, indent=2)
        print(f"📁 [EVIDENCE PACK SAVED]: {out_file}\n")

def main():
    parser = argparse.ArgumentParser(description="🔴 PILL RED: Adversarial Mathematical Laboratory for Boolean Computation")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Crucible Command
    crucible_p = subparsers.add_parser("crucible", help="Run adversarial collision crucible against a candidate representation")
    crucible_p.add_argument("--family", required=True, choices=list(FAMILIES.keys()), help="Adversarial problem family")
    crucible_p.add_argument("--candidate", default="vpti", choices=list(CANDIDATES.keys()), help="Candidate representation")
    crucible_p.add_argument("--samples", type=int, default=5, help="Number of collision pairs")
    crucible_p.add_argument("--output-dir", default="evidence/CRUCIBLE_REPORTS", help="Directory for JSON evidence pack")

    # Replicate Command
    rep_p = subparsers.add_parser("replicate", help="Replicate a historical PILL RED experiment phase (I through XVIII)")
    rep_p.add_argument("--phase", required=True, help="Phase ID (e.g. 14, 15, 16, 17, 18, IX, XIV, XVIII)")

    # List Candidates
    subparsers.add_parser("list-candidates", help="List available baseline candidate representations")

    # List Families
    subparsers.add_parser("list-families", help="List available adversarial problem families")

    # Status Command
    subparsers.add_parser("status", help="Print verified PILL RED master status")

    args = parser.parse_args()

    if args.command == "crucible":
        run_crucible_command(args.family, args.candidate, args.samples, args.output_dir)
    elif args.command == "replicate":
        replicate_experiment(args.phase)
    elif args.command == "list-candidates":
        print("🏛️  AVAILABLE CANDIDATE REPRESENTATIONS:")
        for k in CANDIDATES:
            print(f"  • {k:15s} ({CANDIDATES[k]().name})")
    elif args.command == "list-families":
        print("🏛️  AVAILABLE ADVERSARIAL PROBLEM FAMILIES:")
        for k in FAMILIES:
            print(f"  • {k:25s} ({FAMILIES[k]().name})")
    elif args.command == "status":
        here = os.path.dirname(os.path.abspath(__file__))
        status_file = os.path.join(here, "PROJECT_MASTER_STATUS.md")
        if os.path.exists(status_file):
            with open(status_file, "r", encoding="utf-8") as f:
                print(f.read())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
