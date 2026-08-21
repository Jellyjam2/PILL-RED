"""
Unit Tests for PILL RED Prediction Receipt Protocol and Zero-Trust Offline Verifier.
"""

import time
import unittest
from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    canonical_encode,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root
)
from pillred.protocol.receipt import PredictionReceipt, PredictionEpisode
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.protocol.client import PillRedClient


class TestReceiptProtocol(unittest.TestCase):
    """Verifies deterministic receipt generation, temporal integrity, and zero-trust verification."""

    def test_canonical_jcs_determinism(self):
        """Canonical encoding produces identical bytes regardless of key insertion order."""
        dict1 = {"b": 2, "a": 1, "c": [1, 2]}
        dict2 = {"a": 1, "c": [1, 2], "b": 2}
        self.assertEqual(canonical_encode(dict1), canonical_encode(dict2))

    def test_receipt_commit_and_settlement(self):
        """Receipt correctly commits prior to event and settles with ground truth."""
        t_commit = 1000.0
        t_event = 1005.0
        t_resolve = 1006.0

        r = PredictionReceipt.create_commitment(
            model_id="TEST_MODEL",
            target_event="EVENT_001",
            prediction="7",
            confidence=0.60,
            commit_timestamp=t_commit,
            receipt_id="REC-TEST-001",
            nonce="nonce123"
        )
        self.assertEqual(r.receipt_id, "REC-TEST-001")
        self.assertIsNotNone(r.commit_hash)
        self.assertIsNone(r.receipt_hash)

        # Settle
        r.settle(
            actual_outcome="7",
            event_timestamp=t_event,
            resolution_timestamp=t_resolve,
            payout_multiplier=10.0
        )
        self.assertTrue(r.is_hit)
        self.assertIsNotNone(r.receipt_hash)

        # Verify offline with ZeroTrustVerifier
        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r.to_dict())
        self.assertTrue(is_valid)
        self.assertEqual(len(violations), 0)

    def test_tamper_detection_retroactive_timestamp(self):
        """ZeroTrustVerifier detects and rejects invalid timestamps (t_commit >= t_event)."""
        r = PredictionReceipt.create_commitment(
            model_id="CHEAT_MODEL",
            target_event="EVENT_002",
            prediction="BAR",
            commit_timestamp=2000.0
        )
        # Settle with impossible event timestamp (event happened BEFORE commit)
        r.settle(
            actual_outcome="BAR",
            event_timestamp=1999.0, # Violation!
            resolution_timestamp=2001.0
        )
        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r.to_dict())
        self.assertFalse(is_valid)
        self.assertTrue(any("Causal violation" in v for v in violations))

    def test_tamper_detection_payload_modification(self):
        """ZeroTrustVerifier detects if an attacker retroactively changes the prediction payload."""
        r = PredictionReceipt.create_commitment(
            model_id="CHEAT_MODEL",
            target_event="EVENT_003",
            prediction="PLUM",
            commit_timestamp=3000.0
        )
        r.settle(
            actual_outcome="SEVEN",
            event_timestamp=3001.0,
            resolution_timestamp=3002.0
        )
        
        # Tamper with the prediction in the settled dictionary
        tampered_dict = r.to_dict()
        tampered_dict["prediction"] = "SEVEN" # Faking that they predicted a win

        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(tampered_dict)
        self.assertFalse(is_valid)
        self.assertTrue(any("Commit hash mismatch" in v for v in violations))

    def test_sdk_chain_and_passport_generation(self):
        """PillRedClient captures chained predictions and generates a ModelAuditPassport."""
        client = PillRedClient(model_id="ALPHA_MODEL", model_version="2.0.0")

        # Spin 1
        rec1 = client.commit(target_event="SPIN_1", prediction="7")
        client.resolve(receipt_id=rec1.receipt_id, actual_outcome="7", payout_multiplier=10.0)

        # Spin 2
        rec2 = client.commit(target_event="SPIN_2", prediction="0")
        client.resolve(receipt_id=rec2.receipt_id, actual_outcome="0", payout_multiplier=0.0)

        # Spin 3
        rec3 = client.commit(target_event="SPIN_3", prediction="BAR")
        client.resolve(receipt_id=rec3.receipt_id, actual_outcome="0", payout_multiplier=0.0)

        self.assertEqual(len(client.receipts), 3)
        self.assertEqual(client.receipts[1].previous_receipt_hash, client.receipts[0].receipt_hash)
        self.assertEqual(client.receipts[2].previous_receipt_hash, client.receipts[1].receipt_hash)

        # Compile Passport
        passport = client.get_passport()
        self.assertEqual(passport.identity.model_id, "ALPHA_MODEL")
        self.assertEqual(passport.provenance.total_receipts, 3)
        self.assertAlmostEqual(passport.statistical_evidence.measured["accuracy"], 2 / 3, places=2)
        self.assertTrue(passport.provenance.chain_integrity)
        self.assertEqual(passport.evidentiary_conclusions.provenance, "VERIFIED")


if __name__ == "__main__":
    unittest.main()
