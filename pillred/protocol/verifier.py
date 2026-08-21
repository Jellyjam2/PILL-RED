"""
Standalone Zero-Trust Offline Verifier for PILL RED Protocol.
Performs deterministic cryptographic and temporal audit without trusting any central server.
"""

from typing import Any, Dict, List, Tuple
from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    canonical_encode,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root
)
from pillred.protocol.receipt import PredictionReceipt, PredictionEpisode, ModelAuditPassport


class ZeroTrustVerifier:
    """
    Independently audits receipts and evidence chains.
    Requires zero network calls or server trust.
    """

    @classmethod
    def verify_single_receipt(cls, r_dict: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Audits a single prediction receipt.
        Checks:
        1. Protocol version validity
        2. Recomputed commit_hash matches exactly
        3. Recomputed receipt_hash matches (if settled)
        4. Strict temporal precedence: commit_timestamp < event_timestamp <= resolution_timestamp
        """
        violations = []

        # 1. Protocol Version
        if r_dict.get("protocol_version") != PROTOCOL_VERSION:
            violations.append(f"Invalid protocol version: {r_dict.get('protocol_version')}")

        # 2. Recompute Commit Hash
        expected_commit_hash = compute_commit_hash(
            protocol_version=r_dict.get("protocol_version", PROTOCOL_VERSION),
            receipt_id=r_dict.get("receipt_id", ""),
            model_id=r_dict.get("model_id", ""),
            model_version=r_dict.get("model_version", ""),
            target_event=r_dict.get("target_event", ""),
            prediction=r_dict.get("prediction", ""),
            confidence=float(r_dict.get("confidence", 0.0)),
            commit_timestamp=float(r_dict.get("commit_timestamp", 0.0)),
            previous_receipt_hash=r_dict.get("previous_receipt_hash", ""),
            nonce=r_dict.get("nonce", "")
        )

        if expected_commit_hash != r_dict.get("commit_hash"):
            violations.append(f"Commit hash mismatch! Expected: {expected_commit_hash}, Got: {r_dict.get('commit_hash')}")

        # 3. Check Settlement if present
        if r_dict.get("actual_outcome") is not None:
            c_ts = float(r_dict.get("commit_timestamp", 0.0))
            e_ts = float(r_dict.get("event_timestamp", 0.0))
            r_ts = float(r_dict.get("resolution_timestamp", 0.0))

            # Temporal Precedence Check
            if c_ts >= e_ts:
                violations.append(f"Causal violation: Commit timestamp ({c_ts}) is not strictly prior to event timestamp ({e_ts})")
            if e_ts > r_ts:
                violations.append(f"Temporal violation: Event timestamp ({e_ts}) occurred after resolution timestamp ({r_ts})")

            expected_receipt_hash = compute_receipt_hash(
                commit_hash=r_dict.get("commit_hash", ""),
                event_id=r_dict.get("event_id", ""),
                event_timestamp=e_ts,
                resolution_timestamp=r_ts,
                actual_outcome=r_dict.get("actual_outcome"),
                payout_multiplier=float(r_dict.get("payout_multiplier", 0.0))
            )

            if expected_receipt_hash != r_dict.get("receipt_hash"):
                violations.append(f"Receipt hash mismatch! Expected: {expected_receipt_hash}, Got: {r_dict.get('receipt_hash')}")

            # Hit flag validation
            expected_hit = str(r_dict.get("prediction")).strip().upper() == str(r_dict.get("actual_outcome")).strip().upper()
            if r_dict.get("is_hit") is not None and r_dict.get("is_hit") != expected_hit:
                violations.append(f"Hit scoring mismatch! Scored: {r_dict.get('is_hit')}, Reality: {expected_hit}")

        return len(violations) == 0, violations

    @classmethod
    def verify_chain(cls, receipts_data: List[Dict[str, Any]]) -> Tuple[bool, List[str], str]:
        """
        Audits an entire sequential chain of prediction receipts.
        Verifies individual receipts, chain link integrity, and computes the Merkle root.
        """
        all_violations = []
        leaf_hashes = []
        seen_ids = set()
        model_id = None

        for idx, r in enumerate(receipts_data):
            rid = r.get("receipt_id")
            if rid in seen_ids:
                all_violations.append(f"Duplicate receipt ID detected: {rid}")
            seen_ids.add(rid)

            if model_id is None:
                model_id = r.get("model_id")
            elif r.get("model_id") != model_id:
                all_violations.append(f"Cross-model contamination at Receipt #{idx+1}: Expected {model_id}, got {r.get('model_id')}")

            valid, vios = cls.verify_single_receipt(r)
            if not valid:
                all_violations.extend([f"Receipt #{idx+1} ({rid}): {v}" for v in vios])

            # Verify Chain Linkage (previous_receipt_hash)
            if idx > 0:
                prev_receipt = receipts_data[idx - 1]
                expected_prev = prev_receipt.get("receipt_hash") or prev_receipt.get("commit_hash")
                actual_prev = r.get("previous_receipt_hash")
                if expected_prev != actual_prev:
                    all_violations.append(f"Broken chain linkage at Receipt #{idx+1}! Expected prev: {expected_prev}, Got: {actual_prev}")

            leaf_hashes.append(r.get("receipt_hash") or r.get("commit_hash"))

        merkle_root = compute_merkle_root(leaf_hashes)
        return len(all_violations) == 0, all_violations, merkle_root

