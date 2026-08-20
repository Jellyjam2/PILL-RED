"""PILL RED RNG Structural Audit CLI & Engine.

Audits pseudorandom and stochastic streams for reproducible algebraic and statistical structure.
Applies rigorous in-sample discovery and out-of-sample persistence testing (alpha = 0.01).
"""

import argparse
import json
import sys
import time
from typing import List

from rng_audit.generators.reference_generators import (
    WeakLCG,
    QuadraticPRNG,
    XorShift32,
    MersenneTwisterPRNG,
    CryptographicRNG,
)
from rng_audit.statistics.battery import RNGTestBattery
from rng_audit.collectors.schema import SpinRecord, SpinLogger


if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


def print_banner():
    print("=" * 80)
    print("[*] PILL RED RNG STRUCTURAL AUDIT ENGINE (Track 2)")
    print("Standard: alpha = 0.01 | In-Sample Discovery + Out-of-Sample Persistence Testing")
    print("=" * 80)


def cmd_test_synthetic(args):
    """Executes the complete calibration ladder across reference generators."""
    print_banner()
    print(f"[*] Running Synthetic Calibration Ladder (Sample Size N={args.samples})...\n")

    generators = [
        ("1. Weak LCG (Linear Congruential, mod 2048)", WeakLCG(), True),
        ("2. Quadratic Non-Linear PRNG (Degree-2 Recurrence)", QuadraticPRNG(), True),
        ("3. XorShift32 (Linear Recurrence over GF(2))", XorShift32(), True),
        ("4. Mersenne Twister (MT19937, Standard PRNG)", MersenneTwisterPRNG(), False),
        ("5. Cryptographic RNG (CSPRNG / OS Entropy Null Baseline)", CryptographicRNG(), False),
    ]

    results = []

    for name, gen, expect_structure in generators:
        seq = gen.generate_sequence(args.samples, max_val=args.max_val)
        audit = RNGTestBattery.run_full_audit(seq, max_val=args.max_val)
        
        status_symbol = "[DETECT]" if audit["has_reproducible_structure"] else "[NULL]"
        verdict = audit["verdict"]
        
        print("-" * 80)
        print(f"{status_symbol} GENERATOR: {name}")
        print(f"   Sample Size: {audit['sample_size']} (Train: {audit['train_size']}, Test: {audit['test_size']})")
        print(f"   Verdict:     {verdict}")
        
        if audit["detected_anomalies"]:
            print(f"   Anomalies:   {', '.join(audit['detected_anomalies'])}")
        else:
            print("   Anomalies:   None (Passed all uniformity, lag, FFT, and LFSR tests)")

        out_stat = audit["out_of_sample"]
        print(f"   Out-of-Sample p-values:")
        print(f"     - Uniformity:      p = {out_stat['uniformity']['p_value']:.5f} ({'PASS' if out_stat['uniformity']['passed'] else 'FAIL'})")
        print(f"     - Autocorrelation: p = {out_stat['autocorrelation']['p_value']:.5f} ({'PASS' if out_stat['autocorrelation']['passed'] else 'FAIL'})")
        print(f"     - Spectral FFT:    p = {out_stat['spectral_fft']['p_value']:.5f} ({'PASS' if out_stat['spectral_fft']['passed'] else 'FAIL'})")
        print(f"     - Algebraic LFSR:  p = {out_stat['algebraic_lfsr']['p_value']:.5f} ({'PASS' if out_stat['algebraic_lfsr']['passed'] else 'FAIL'})")

        results.append((name, verdict, audit["has_reproducible_structure"] == expect_structure))

    print("\n" + "=" * 80)
    print("[*] CALIBRATION SUMMARY:")
    for name, verdict, calibrated in results:
        calib_str = "[OK] CALIBRATED" if calibrated else "[FAIL] MISCALIBRATED"
        print(f"  - {name:<55} -> {verdict:<32} {calib_str}")
    print("=" * 80)


def cmd_audit_stream(args):
    """Audits an external stream of integers or spin records."""
    print_banner()
    print(f"[*] Auditing stream from: {args.input_file}")
    
    # Load stream
    sequence = []
    with open(args.input_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    val = int(line)
                    sequence.append(val)
                except ValueError:
                    try:
                        data = json.loads(line)
                        if "payout_multiplier" in data:
                            sequence.append(int(data["payout_multiplier"] * 100))
                        elif "outcome_symbols" in data:
                            sequence.extend(data["outcome_symbols"])
                    except Exception:
                        continue

    if len(sequence) < 50:
        print(f"❌ Error: Insufficient sample size ({len(sequence)} values). Need at least 50.")
        return

    print(f"[*] Loaded {len(sequence)} observations. Executing audit...\n")
    audit = RNGTestBattery.run_full_audit(sequence, max_val=args.max_val)

    print("-" * 80)
    print(f"AUDIT VERDICT: {audit['verdict']}")
    print(f"Sample Size:   {audit['sample_size']} (Train: {audit['train_size']}, Test: {audit['test_size']})")
    if audit["detected_anomalies"]:
        print(f"Detected Reproducible Anomalies: {', '.join(audit['detected_anomalies'])}")
    else:
        print("Detected Reproducible Anomalies: NONE")
    print("-" * 80)


from rng_audit.statistics.session_auditor import MultiSessionAuditor


def cmd_audit_sessions(args):
    """Audits multi-session spin records with pre-registered hypothesis testing."""
    print_banner()
    logger = SpinLogger(storage_path=args.input_file)
    all_spins = logger.load_spins(game_title=args.game_title)
    
    if len(all_spins) < 100:
        print(f"[*] Error: Insufficient spin records ({len(all_spins)}). Need at least 100.")
        return

    # Split into Session 1 (Discovery: 50%), Session 2 (Validation: 30%), Session 3 (Replication: 20%)
    n = len(all_spins)
    n_disc = int(n * 0.5)
    n_val = int(n * 0.3)
    
    disc_records = all_spins[:n_disc]
    val_records = all_spins[n_disc:n_disc + n_val]
    rep_records = all_spins[n_disc + n_val:]

    print(f"[*] Loaded {n} records for game '{args.game_title or 'All'}':")
    print(f"    • Discovery Session:   {len(disc_records)} spins")
    print(f"    • Validation Session:  {len(val_records)} spins (Strictly Out-of-Sample)")
    print(f"    • Replication Session: {len(rep_records)} spins (Multi-Session Holdout)\n")

    res = MultiSessionAuditor.audit_game_sessions(
        discovery_records=disc_records,
        validation_records=val_records,
        replication_records=rep_records,
        alphabet_size=args.alphabet_size,
        house_edge_fraction=args.house_edge
    )

    print("=" * 80)
    print(f"🔴 MULTI-SESSION AUDIT VERDICT: {res['verdict']}")
    print("=" * 80)
    print(f"Game Title:            {res['game_title']}")
    print(f"Baseline Chance:       {res['baseline_null_rate']*100:.2f}% (1 in {res['alphabet_size']})")
    print(f"Validation Hit Rate:   {res['validation_hit_rate']*100:.2f}%")
    print(f"99% Wilson CI:         [{res['wilson_ci_99'][0]*100:.2f}%, {res['wilson_ci_99'][1]*100:.2f}%]")
    print(f"Binomial p-value:      {res['binomial_p_value']:.4e} ({'SIGNIFICANT p < 0.01' if res['statistically_significant'] else 'NOT SIGNIFICANT p >= 0.01'})")
    print(f"Net Expected Value:    {res['net_expected_value']*100:+.2f}% (House Edge: {args.house_edge*100:.1f}%)")
    print(f"Economic Viability:    {'POSITIVE (+EV)' if res['economically_viable'] else 'NEGATIVE (-EV / Absorbed by House Edge)'}")
    print("-" * 80)
    print(f"Epistemic Rationale:   {res['rationale']}")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="PILL RED RNG Structural Audit CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # test-synthetic
    synth_parser = subparsers.add_parser("test-synthetic", help="Run 5-tier calibration ladder")
    synth_parser.add_argument("--samples", type=int, default=1000, help="Sample size per generator (default: 1000)")
    synth_parser.add_argument("--max-val", type=int, default=100, help="Output range modulus (default: 100)")

    # audit-stream
    stream_parser = subparsers.add_parser("audit-stream", help="Audit an external data stream")
    stream_parser.add_argument("--input-file", required=True, help="Path to input text/jsonl file")
    stream_parser.add_argument("--max-val", type=int, default=100, help="Output range modulus (default: 100)")

    # audit-sessions
    sess_parser = subparsers.add_parser("audit-sessions", help="Run multi-session blinded audit on spin logs")
    sess_parser.add_argument("--input-file", default="rng_audit/evidence/spin_logs.jsonl", help="Path to spin logs JSONL")
    sess_parser.add_argument("--game-title", default=None, help="Filter by game title")
    sess_parser.add_argument("--alphabet-size", type=int, default=10, help="Number of distinct outcome categories (default: 10)")
    sess_parser.add_argument("--house-edge", type=float, default=0.04, help="House edge fraction (default: 0.04 for 96% RTP)")

    args = parser.parse_args()

    if args.command == "test-synthetic":
        cmd_test_synthetic(args)
    elif args.command == "audit-stream":
        cmd_audit_stream(args)
    elif args.command == "audit-sessions":
        cmd_audit_sessions(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
