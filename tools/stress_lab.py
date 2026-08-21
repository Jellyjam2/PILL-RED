"""
PILL RED High-Throughput Stress Laboratory (Gate 8).
Benchmarks scale, memory, disk, and zero-trust verification throughput at 1k, 10k, and 100k events.
"""

import gc
import json
import os
import random
import sys
import time
import tracemalloc
from typing import Dict, Any, List

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pillred.protocol.spec import PROTOCOL_VERSION, compute_commit_hash, compute_receipt_hash, compute_merkle_root
from pillred.protocol.passport import ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.statistical.engine import StatisticalEngine
from pillred.economic.engine import EconomicEngine


def run_stress_tier(n_events: int, output_dir: str = "data/stress_lab") -> Dict[str, Any]:
    """
    Executes a complete end-to-end stress test across N events:
    Commitment -> Settlement -> Merkle Root -> Statistical -> Economic -> Passport -> Offline Zero-Trust Verification.
    """
    os.makedirs(output_dir, exist_ok=True)
    json_path = os.path.join(output_dir, f"stress_stream_{n_events}.json")
    passport_path = os.path.join(output_dir, f"stress_passport_{n_events}.json")

    print(f"\n============================================================")
    print(f"[*] RUNNING PILL RED STRESS TIER: {n_events:,} EVENTS")
    print(f"============================================================")

    gc.collect()
    tracemalloc.start()
    t_start_total = time.perf_counter()

    symbols = ["0", "BAR", "7", "Plum", "Melon", "Orange"]
    payout_table = {"0": 0.0, "BAR": 6.0, "7": 10.0, "Plum": 4.0, "Melon": 5.0, "Orange": 3.0}

    # 1. PHASE 1: SEQUENTIAL STREAM CAPTURE (COMMIT -> SETTLE -> CHAIN LINK)
    t_stream_start = time.perf_counter()
    receipts: List[Dict[str, Any]] = []
    prev_hash = "0" * 64
    base_time = 1700000000.0

    preds = []
    acts = []
    payouts = []
    leaf_hashes = []

    for i in range(1, n_events + 1):
        rid = f"REC-STR-{n_events}-{i:07d}"
        pred = "7" if (i % 5 == 0) else "0"
        conf = 0.75 if pred == "7" else 0.85
        t_c = base_time + i * 2.0
        nonce = f"N{i:06x}"
        target_event = f"EVENT_{i:07d}"

        # 1.1 Commit
        c_hash = compute_commit_hash(
            protocol_version=PROTOCOL_VERSION,
            receipt_id=rid,
            model_id="MOD-STRESS-LAB",
            model_version="1.0.0",
            target_event=target_event,
            prediction=pred,
            confidence=conf,
            commit_timestamp=t_c,
            previous_receipt_hash=prev_hash,
            nonce=nonce
        )

        # 1.2 Settle
        t_e = t_c + 0.5
        t_r = t_e + 0.1
        actual = "7" if (i % 7 == 0) else ("BAR" if (i % 11 == 0) else "0")
        payout = payout_table.get(actual, 0.0)
        is_hit = (pred == actual)

        r_hash = compute_receipt_hash(
            commit_hash=c_hash,
            event_id=target_event,
            event_timestamp=t_e,
            resolution_timestamp=t_r,
            actual_outcome=actual,
            payout_multiplier=payout
        )

        r = {
            "protocol_version": PROTOCOL_VERSION,
            "receipt_id": rid,
            "model_id": "MOD-STRESS-LAB",
            "model_version": "1.0.0",
            "target_event": target_event,
            "prediction": pred,
            "confidence": conf,
            "commit_timestamp": t_c,
            "previous_receipt_hash": prev_hash,
            "commit_hash": c_hash,
            "nonce": nonce,
            "event_id": target_event,
            "event_timestamp": t_e,
            "resolution_timestamp": t_r,
            "actual_outcome": actual,
            "payout_multiplier": payout,
            "is_hit": is_hit,
            "receipt_hash": r_hash
        }
        receipts.append(r)
        leaf_hashes.append(r_hash)
        preds.append(pred)
        acts.append(actual)
        payouts.append(payout)

        # Advance chain link for next event
        prev_hash = r_hash

    t_stream_end = time.perf_counter()
    stream_dur = t_stream_end - t_stream_start
    stream_rate = n_events / stream_dur

    # 3. MERKLE ROOT COMPUTATION
    t_merkle_start = time.perf_counter()
    merkle_root = compute_merkle_root(leaf_hashes)
    t_merkle_end = time.perf_counter()
    merkle_dur = t_merkle_end - t_merkle_start

    # 4. STATISTICAL & ECONOMIC ENGINES
    t_stat_start = time.perf_counter()
    stat_res = StatisticalEngine.evaluate_stream(preds, acts, min_sample_size=30)
    t_stat_end = time.perf_counter()
    stat_dur = t_stat_end - t_stat_start

    t_econ_start = time.perf_counter()
    econ_res = EconomicEngine.evaluate(preds, acts, payouts, unit_stake=1.0)
    t_econ_end = time.perf_counter()
    econ_dur = t_econ_end - t_econ_start

    # 5. PASSPORT GENERATION
    t_pass_start = time.perf_counter()
    passport = ModelAuditPassport.create(
        model_id="MOD-STRESS-LAB",
        model_version="1.0.0",
        target_domain="HIGH_THROUGHPUT_BENCHMARK",
        receipts=receipts,
        merkle_root=merkle_root,
        chain_valid=True,
        statistical_result=stat_res,
        economic_result=econ_res,
        passport_id=f"PASS-STR-{n_events}"
    )
    t_pass_end = time.perf_counter()
    passport_dur = t_pass_end - t_pass_start

    # 6. DISK SERIALIZATION
    t_io_start = time.perf_counter()
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(receipts, f)
    with open(passport_path, "w", encoding="utf-8") as f:
        json.dump(passport.to_dict(), f, indent=2)
    t_io_end = time.perf_counter()
    io_dur = t_io_end - t_io_start

    file_size_mb = os.path.getsize(json_path) / (1024 * 1024)

    # 7. ZERO-TRUST OFFLINE VERIFICATION (Full Chain Recalculation)
    t_verify_start = time.perf_counter()
    valid_chain, violations, calc_root = ZeroTrustVerifier.verify_chain(receipts)
    pass_valid, pass_vios = ModelAuditPassport.verify_passport(passport.to_dict())
    t_verify_end = time.perf_counter()
    verify_dur = t_verify_end - t_verify_start
    verify_rate = n_events / verify_dur

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    peak_mem_mb = peak_mem / (1024 * 1024)
    t_total_end = time.perf_counter()
    total_dur = t_total_end - t_start_total

    # Assert 100% cryptographic integrity
    assert valid_chain, f"Chain integrity failed: {violations}"
    assert pass_valid, f"Passport integrity failed: {pass_vios}"
    assert calc_root == merkle_root, "Merkle root mismatch!"

    print(f"[+] SCALE {n_events:,} COMPLETE | 100% PROVENANCE INTACT")
    print(f"    • Stream Ingestion Rate:  {stream_rate:,.0f} events/sec ({stream_dur:.3f}s)")
    print(f"    • Zero-Trust Verify Rate: {verify_rate:,.0f} receipts/sec ({verify_dur:.3f}s)")
    print(f"    • Merkle Tree Build:      {merkle_dur*1000:.2f} ms")
    print(f"    • Passport Seal Gen:      {passport_dur*1000:.2f} ms")
    print(f"    • Peak RAM Footprint:     {peak_mem_mb:.2f} MB")
    print(f"    • JSON Disk Footprint:    {file_size_mb:.2f} MB")
    print(f"    • Verified Merkle Root:   {merkle_root[:16]}...{merkle_root[-16:]}")
    print(f"    • Passport Hash:          {passport.passport_hash[:16]}...{passport.passport_hash[-16:]}")

    return {
        "n_events": n_events,
        "stream_rate": stream_rate,
        "verify_rate": verify_rate,
        "merkle_duration_ms": merkle_dur * 1000.0,
        "passport_duration_ms": passport_dur * 1000.0,
        "peak_ram_mb": peak_mem_mb,
        "disk_size_mb": file_size_mb,
        "total_duration_sec": total_dur,
        "merkle_root": merkle_root,
        "passport_hash": passport.passport_hash,
        "json_path": json_path
    }


if __name__ == "__main__":
    results = {}
    for tier in [1_000, 10_000, 100_000]:
        results[tier] = run_stress_tier(tier)

    # Save summary report
    with open("data/stress_lab/benchmark_summary.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    print("\n[+] Benchmark summary saved to data/stress_lab/benchmark_summary.json")
