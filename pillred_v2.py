#!/usr/bin/env python3
"""PILL RED v2.0 Alpha — Autonomous Adversarial Representation Explorer CLI.

Usage:
    python pillred_v2.py list-candidates
    python pillred_v2.py run --candidate <name> [--samples N] [--level L]
    python pillred_v2.py run-all [--samples N] [--level L]
    python pillred_v2.py rediscovery-benchmark [--samples N]
    python pillred_v2.py ledger-status
"""

import argparse
import json
import sys
from typing import List

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from engine.crg.generator import CandidateRepresentationGenerator
from engine.aag.adversary import AdaptiveAdversaryManager
from engine.ace.crucible import AutomatedCrucibleEngine
from engine.classifier.trilemma import TrilemmaClassifier
from engine.ledger.store import EpistemicLedger
from engine.interfaces import CrucibleVerdict, TrilemmaOutcome


def cmd_list_candidates(args):
    """Lists all registered candidate representations with deterministic IDs."""
    candidates = CandidateRepresentationGenerator.list_all_candidates()
    print("=" * 80)
    print("🔴 PILL RED v2.0 — REGISTERED CANDIDATE REPRESENTATIONS")
    print("=" * 80)
    print(f"{'CANDIDATE ID':<18} | {'NAME':<22} | {'DSL EXPRESSION'}")
    print("-" * 80)
    for profile, _ in candidates:
        print(f"{profile.candidate_id:<18} | {profile.name:<22} | {profile.dsl_expression}")
    print("=" * 80)


def execute_pipeline(candidate_name: str, samples: int = 5, level: int = 1) -> CrucibleVerdict:
    """Executes the full 5-module loop for a single candidate."""
    # 1. CRG: Generate Candidate
    profile, primitive = CandidateRepresentationGenerator.get_candidate(candidate_name)

    # 2. AAG: Synthesize Adversarial Instance Pairs (with IVR Ground-Truth Certification)
    pairs = AdaptiveAdversaryManager.get_adversarial_suite(level=level, count=samples)

    # 3. ACE: Run Automated 7-Gate Crucible
    raw_verdict = AutomatedCrucibleEngine.evaluate_candidate(profile, primitive, pairs, q8_level=level)

    # 4. Classifier: Classify into Trilemma Outcomes (A, B, C, D, UNKNOWN)
    classified_verdict = TrilemmaClassifier.classify_verdict(raw_verdict)

    # 5. Ledger: Persist Immutable Record
    ledger = EpistemicLedger()
    ledger.record_verdict(classified_verdict)

    return classified_verdict


def print_verdict(v: CrucibleVerdict):
    """Pretty-prints a crucible verdict."""
    print("\n" + "=" * 80)
    print(f"🔴 CRUCIBLE VERDICT: {v.run_id} (Engine v{v.engine_version})")
    print("=" * 80)
    print(f"Candidate:        {v.candidate.name} ({v.candidate.candidate_id})")
    print(f"DSL Expression:   {v.candidate.dsl_expression}")
    print(f"Adversarial Family: {v.family} (N={v.sample_size} pairs)")
    print(f"Timestamp:        {v.timestamp_utc}")
    print("-" * 80)
    print("GATE EVALUATIONS (D1–D7):")
    for gid in sorted(v.gates.keys()):
        g = v.gates[gid]
        status = "✅ PASS" if g.passed else "❌ FAIL"
        print(f"  [{gid}] {g.gate_name:<30} : {status:<7} (Val={g.metric_value:.4f}, Thresh={g.threshold:.4f}) — {g.notes}")
    print("-" * 80)
    print(f"EPISTEMIC CLASSIFICATION: {v.classification.value}")
    print(f"Confidence:               {v.confidence * 100:.1f}%")
    print(f"Primary Mechanism:        {v.primary_failure_mechanism}")
    print(f"Formal Rationale:         {v.rationale}")
    print("=" * 80 + "\n")


def cmd_run(args):
    """Runs a single candidate through the automated crucible."""
    print(f"[*] Executing PILL RED v2.0 loop on candidate '{args.candidate}' (Samples={args.samples}, Level={args.level})...")
    verdict = execute_pipeline(args.candidate, samples=args.samples, level=args.level)
    print_verdict(verdict)


def cmd_run_all(args):
    """Runs all registered candidates through the automated crucible."""
    candidates = CandidateRepresentationGenerator.list_all_candidates()
    print(f"[*] Executing PILL RED v2.0 loop on ALL {len(candidates)} candidates (Samples={args.samples}, Level={args.level})...\n")
    for profile, _ in candidates:
        verdict = execute_pipeline(profile.name, samples=args.samples, level=args.level)
        print_verdict(verdict)


def cmd_rediscovery_benchmark(args):
    """Blinded Rediscovery Experiment: Checks whether v2 autonomously rediscovers v1 boundaries."""
    print("=" * 80)
    print("🔴 PILL RED v2.0 — BLINDED REDISCOVERY EXPERIMENT")
    print("=" * 80)
    print("Objective: Test whether the autonomous engine independently rediscovers the structural")
    print("           failure boundaries identified manually in v1 (Outcome A on expanders, etc.).")
    print("-" * 80)

    results = []
    candidates = CandidateRepresentationGenerator.list_all_candidates()
    for profile, _ in candidates:
        print(f"[*] Testing {profile.name} on high-girth Ramanujan expander Tseitin pairs (g >= 5)...")
        verdict = execute_pipeline(profile.name, samples=args.samples, level=1)
        results.append(verdict)

    print("\n" + "=" * 80)
    print("AUTONOMOUS REDISCOVERY SUMMARY TABLE")
    print("=" * 80)
    print(f"{'CANDIDATE':<22} | {'OUTCOME':<24} | {'CONFIDENCE':<10} | {'MEAN SEP (Δ)'}")
    print("-" * 80)
    for v in results:
        print(f"{v.candidate.name:<22} | {v.classification.value:<24} | {v.confidence * 100:.1f}%     | {v.mean_separation:.6f}")
    print("=" * 80)


def cmd_escalate(args):
    """Executes the Q8 Adversarial Escalation Protocol on a candidate."""
    print("=" * 80)
    print(f"🔴 PILL RED v2.0 — Q8 ADVERSARIAL ESCALATION: {args.candidate}")
    print("=" * 80)
    print(f"Candidate: {args.candidate}")
    print(f"Objective: Progressively escalate adversarial complexity (Level 1 -> 2 -> 3) to test bounds.")
    print("-" * 80)

    for level in [1, 2, 3]:
        level_names = {
            1: "Level 1: Linear High-Girth Tseitin Expanders",
            2: "Level 2: Mixed Non-linear XOR/3-SAT Expanders (degree d >= 2)",
            3: "Level 3: Dense Non-linear Expanders with Higher-Order Couplings"
        }
        print(f"\n[*] Launching {level_names[level]} (Samples={args.samples})...")
        verdict = execute_pipeline(args.candidate, samples=args.samples, level=level)
        print_verdict(verdict)

        if verdict.classification != TrilemmaOutcome.OUTCOME_D:
            print("=" * 80)
            print(f"🛑 ESCALATION HALTED AT {level_names[level].upper()}")
            print(f"Result: Candidate failed to survive Level {level}.")
            print(f"Classified Outcome: {verdict.classification.value}")
            print(f"Primary Failure Mechanism: {verdict.primary_failure_mechanism}")
            print("=" * 80)
            return

    print("=" * 80)
    print(f"🏆 CANDIDATE SURVIVED ALL IMPLEMENTED ESCALATION LEVELS!")
    print(f"Epistemic Status: Candidate survived the currently implemented finite adversarial crucible.")
    print(f"                  (Note: Survival is NOT evidence of P=NP; it marks candidate for human theoretical escalation).")
    print("=" * 80)


def cmd_ledger_status(args):
    """Displays immutable ledger statistics."""
    ledger = EpistemicLedger()
    stats = ledger.get_summary_statistics()
    print("=" * 80)
    print("🔴 PILL RED v2.0 — EPISTEMIC RUN LEDGER STATUS")
    print("=" * 80)
    print(f"Ledger File:   {stats['ledger_file']}")
    print(f"Total Runs:    {stats['total_runs']}")
    print("-" * 80)
    print("Outcome Breakdown:")
    for out, count in stats.get("outcome_breakdown", {}).items():
        print(f"  • {out:<30}: {count} runs")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="PILL RED v2.0 — Autonomous Adversarial Representation Explorer")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # list-candidates
    subparsers.add_parser("list-candidates", help="List registered candidate representations")

    # run
    run_parser = subparsers.add_parser("run", help="Run a single candidate through the crucible")
    run_parser.add_argument("--candidate", required=True, help="Name of candidate representation")
    run_parser.add_argument("--samples", type=int, default=5, help="Number of adversarial pairs (default: 5)")
    run_parser.add_argument("--level", type=int, default=1, help="Q8 adversarial level (default: 1)")

    # run-all
    run_all_parser = subparsers.add_parser("run-all", help="Run all registered candidates")
    run_all_parser.add_argument("--samples", type=int, default=5, help="Number of adversarial pairs (default: 5)")
    run_all_parser.add_argument("--level", type=int, default=1, help="Q8 adversarial level (default: 1)")

    # escalate
    esc_parser = subparsers.add_parser("escalate", help="Run multi-level Q8 adversarial escalation on a candidate")
    esc_parser.add_argument("--candidate", required=True, help="Name of candidate representation")
    esc_parser.add_argument("--samples", type=int, default=5, help="Number of adversarial pairs per level (default: 5)")

    # rediscovery-benchmark
    redisc_parser = subparsers.add_parser("rediscovery-benchmark", help="Run the blinded rediscovery experiment")
    redisc_parser.add_argument("--samples", type=int, default=5, help="Number of pairs per candidate (default: 5)")

    # ledger-status
    subparsers.add_parser("ledger-status", help="Show immutable run ledger statistics")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "list-candidates":
        cmd_list_candidates(args)
    elif args.command == "run":
        cmd_run(args)
    elif args.command == "run-all":
        cmd_run_all(args)
    elif args.command == "escalate":
        cmd_escalate(args)
    elif args.command == "rediscovery-benchmark":
        cmd_rediscovery_benchmark(args)
    elif args.command == "ledger-status":
        cmd_ledger_status(args)


if __name__ == "__main__":
    main()
