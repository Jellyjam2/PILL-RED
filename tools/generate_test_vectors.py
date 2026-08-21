"""
Generates deterministic test vectors for PILLRED-SPEC-1.0.
"""

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pillred.protocol.spec import compute_commit_hash, compute_receipt_hash, compute_merkle_root, PROTOCOL_VERSION

os.makedirs("test_vectors/valid", exist_ok=True)
os.makedirs("test_vectors/invalid", exist_ok=True)
os.makedirs("test_vectors/expected", exist_ok=True)

# 1. Valid Receipt 001
r1 = {
    "protocol_version": PROTOCOL_VERSION,
    "receipt_id": "REC-VEC-001",
    "model_id": "MOD-BENCHMARK-V1",
    "model_version": "1.0.0",
    "target_event": "EVENT_100",
    "prediction": "7",
    "confidence": 0.75,
    "commit_timestamp": 1700000000.0,
    "previous_receipt_hash": "0" * 64,
    "nonce": "VEC_NONCE_001"
}
r1["commit_hash"] = compute_commit_hash(
    protocol_version=r1["protocol_version"],
    receipt_id=r1["receipt_id"],
    model_id=r1["model_id"],
    model_version=r1["model_version"],
    target_event=r1["target_event"],
    prediction=r1["prediction"],
    confidence=r1["confidence"],
    commit_timestamp=r1["commit_timestamp"],
    previous_receipt_hash=r1["previous_receipt_hash"],
    nonce=r1["nonce"]
)
r1["event_id"] = "EVENT_100"
r1["event_timestamp"] = 1700000005.0
r1["resolution_timestamp"] = 1700000006.0
r1["actual_outcome"] = "7"
r1["payout_multiplier"] = 10.0
r1["is_hit"] = True
r1["receipt_hash"] = compute_receipt_hash(
    commit_hash=r1["commit_hash"],
    event_id=r1["event_id"],
    event_timestamp=r1["event_timestamp"],
    resolution_timestamp=r1["resolution_timestamp"],
    actual_outcome=r1["actual_outcome"],
    payout_multiplier=r1["payout_multiplier"]
)

with open("test_vectors/valid/receipt_001.json", "w", encoding="utf-8") as f:
    json.dump(r1, f, indent=2)

# 2. Valid Receipt 002
r2 = {
    "protocol_version": PROTOCOL_VERSION,
    "receipt_id": "REC-VEC-002",
    "model_id": "MOD-BENCHMARK-V1",
    "model_version": "1.0.0",
    "target_event": "EVENT_101",
    "prediction": "0",
    "confidence": 0.80,
    "commit_timestamp": 1700000010.0,
    "previous_receipt_hash": r1["receipt_hash"],
    "nonce": "VEC_NONCE_002"
}
r2["commit_hash"] = compute_commit_hash(
    protocol_version=r2["protocol_version"],
    receipt_id=r2["receipt_id"],
    model_id=r2["model_id"],
    model_version=r2["model_version"],
    target_event=r2["target_event"],
    prediction=r2["prediction"],
    confidence=r2["confidence"],
    commit_timestamp=r2["commit_timestamp"],
    previous_receipt_hash=r2["previous_receipt_hash"],
    nonce=r2["nonce"]
)
r2["event_id"] = "EVENT_101"
r2["event_timestamp"] = 1700000015.0
r2["resolution_timestamp"] = 1700000016.0
r2["actual_outcome"] = "0"
r2["payout_multiplier"] = 0.0
r2["is_hit"] = True
r2["receipt_hash"] = compute_receipt_hash(
    commit_hash=r2["commit_hash"],
    event_id=r2["event_id"],
    event_timestamp=r2["event_timestamp"],
    resolution_timestamp=r2["resolution_timestamp"],
    actual_outcome=r2["actual_outcome"],
    payout_multiplier=r2["payout_multiplier"]
)

with open("test_vectors/valid/receipt_002.json", "w", encoding="utf-8") as f:
    json.dump(r2, f, indent=2)

# 3. Valid Chain 001 (r1, r2, r3)
r3 = {
    "protocol_version": PROTOCOL_VERSION,
    "receipt_id": "REC-VEC-003",
    "model_id": "MOD-BENCHMARK-V1",
    "model_version": "1.0.0",
    "target_event": "EVENT_102",
    "prediction": "BAR",
    "confidence": 0.60,
    "commit_timestamp": 1700000020.0,
    "previous_receipt_hash": r2["receipt_hash"],
    "nonce": "VEC_NONCE_003"
}
r3["commit_hash"] = compute_commit_hash(
    protocol_version=r3["protocol_version"],
    receipt_id=r3["receipt_id"],
    model_id=r3["model_id"],
    model_version=r3["model_version"],
    target_event=r3["target_event"],
    prediction=r3["prediction"],
    confidence=r3["confidence"],
    commit_timestamp=r3["commit_timestamp"],
    previous_receipt_hash=r3["previous_receipt_hash"],
    nonce=r3["nonce"]
)
r3["event_id"] = "EVENT_102"
r3["event_timestamp"] = 1700000025.0
r3["resolution_timestamp"] = 1700000026.0
r3["actual_outcome"] = "0"
r3["payout_multiplier"] = 0.0
r3["is_hit"] = False
r3["receipt_hash"] = compute_receipt_hash(
    commit_hash=r3["commit_hash"],
    event_id=r3["event_id"],
    event_timestamp=r3["event_timestamp"],
    resolution_timestamp=r3["resolution_timestamp"],
    actual_outcome=r3["actual_outcome"],
    payout_multiplier=r3["payout_multiplier"]
)

chain = [r1, r2, r3]
with open("test_vectors/valid/chain_001.json", "w", encoding="utf-8") as f:
    json.dump(chain, f, indent=2)

# 4. Invalid: Tampered Prediction
tampered_pred = dict(r1)
tampered_pred["prediction"] = "BAR"
with open("test_vectors/invalid/tampered_prediction.json", "w", encoding="utf-8") as f:
    json.dump(tampered_pred, f, indent=2)

# 5. Invalid: Broken Chain Linkage
broken_chain = [dict(r1), dict(r2)]
broken_chain[1]["previous_receipt_hash"] = "e" * 64
with open("test_vectors/invalid/broken_chain.json", "w", encoding="utf-8") as f:
    json.dump(broken_chain, f, indent=2)

# 6. Invalid: Temporal Violation (t_commit > t_event with valid commit_hash to isolate causal check)
invalid_ts = dict(r1)
invalid_ts["commit_timestamp"] = 1700000010.0 # Committed at t=10, event at t=5!
invalid_ts["commit_hash"] = compute_commit_hash(
    protocol_version=invalid_ts["protocol_version"],
    receipt_id=invalid_ts["receipt_id"],
    model_id=invalid_ts["model_id"],
    model_version=invalid_ts["model_version"],
    target_event=invalid_ts["target_event"],
    prediction=invalid_ts["prediction"],
    confidence=invalid_ts["confidence"],
    commit_timestamp=invalid_ts["commit_timestamp"],
    previous_receipt_hash=invalid_ts["previous_receipt_hash"],
    nonce=invalid_ts["nonce"]
)
with open("test_vectors/invalid/invalid_timestamp.json", "w", encoding="utf-8") as f:
    json.dump(invalid_ts, f, indent=2)

# 7. Valid Model Audit Passport 001
from pillred.protocol.passport import ModelAuditPassport
from pillred.statistical.engine import StatisticalEngine
from pillred.economic.engine import EconomicEngine

merkle_root = compute_merkle_root([r1["receipt_hash"], r2["receipt_hash"], r3["receipt_hash"]])

stat_res = StatisticalEngine.evaluate_stream(
    predictions=[r1["prediction"], r2["prediction"], r3["prediction"]],
    actuals=[r1["actual_outcome"], r2["actual_outcome"], r3["actual_outcome"]],
    confidences=[r1["confidence"], r2["confidence"], r3["confidence"]],
    min_sample_size=3
)
econ_res = EconomicEngine.evaluate(
    predictions=[r1["prediction"], r2["prediction"], r3["prediction"]],
    actuals=[r1["actual_outcome"], r2["actual_outcome"], r3["actual_outcome"]],
    payout_multipliers=[r1["payout_multiplier"], r2["payout_multiplier"], r3["payout_multiplier"]],
    min_active_wagers=2
)

passport = ModelAuditPassport.create(
    model_id="MOD-BENCHMARK-V1",
    model_version="1.0.0",
    target_domain="RNG_SLOT_BENCHMARK",
    receipts=chain,
    merkle_root=merkle_root,
    chain_valid=True,
    statistical_result=stat_res,
    economic_result=econ_res,
    passport_id="PASS-VEC-001",
    generation_timestamp=1700000030.0
)
passport_dict = passport.to_dict()

with open("test_vectors/valid/passport_001.json", "w", encoding="utf-8") as f:
    json.dump(passport_dict, f, indent=2)

# 8. Invalid: Tampered Passport (Modifying P/L inside economic evidence)
tampered_passport = dict(passport_dict)
tampered_passport["economic_evidence"] = dict(passport_dict["economic_evidence"])
tampered_passport["economic_evidence"]["measured"] = dict(passport_dict["economic_evidence"]["measured"])
tampered_passport["economic_evidence"]["measured"]["net_pnl"] += 1000.0

with open("test_vectors/invalid/tampered_passport.json", "w", encoding="utf-8") as f:
    json.dump(tampered_passport, f, indent=2)

# Compute Expected Manifest
manifest = {
    "test_vectors_spec": PROTOCOL_VERSION,
    "vectors": {
        "valid_receipt_001": {
            "file": "test_vectors/valid/receipt_001.json",
            "expected_commit_hash": r1["commit_hash"],
            "expected_receipt_hash": r1["receipt_hash"],
            "expected_status": "VALID"
        },
        "valid_receipt_002": {
            "file": "test_vectors/valid/receipt_002.json",
            "expected_commit_hash": r2["commit_hash"],
            "expected_receipt_hash": r2["receipt_hash"],
            "expected_status": "VALID"
        },
        "valid_chain_001": {
            "file": "test_vectors/valid/chain_001.json",
            "expected_merkle_root": merkle_root,
            "expected_count": 3,
            "expected_status": "VALID"
        },
        "valid_passport_001": {
            "file": "test_vectors/valid/passport_001.json",
            "expected_passport_hash": passport.passport_hash,
            "expected_status": "VALID"
        },
        "invalid_tampered_prediction": {
            "file": "test_vectors/invalid/tampered_prediction.json",
            "expected_status": "INVALID",
            "expected_error": "Commit hash mismatch"
        },
        "invalid_broken_chain": {
            "file": "test_vectors/invalid/broken_chain.json",
            "expected_status": "INVALID",
            "expected_error": "Broken chain linkage"
        },
        "invalid_invalid_timestamp": {
            "file": "test_vectors/invalid/invalid_timestamp.json",
            "expected_status": "INVALID",
            "expected_error": "Causal violation"
        },
        "invalid_tampered_passport": {
            "file": "test_vectors/invalid/tampered_passport.json",
            "expected_status": "INVALID",
            "expected_error": "Economic evidence hash mismatch"
        }
    }
}
with open("test_vectors/expected/test_vector_manifest.json", "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2)

print("[+] Deterministic test vectors successfully generated!")
