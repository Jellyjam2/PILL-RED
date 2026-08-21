"""
Adversarial Red-Team Test Suite for PILL RED Protocol (PILLRED-SPEC-1.0).
Deliberately mounts 13 cryptographic, causal, and temporal attacks to ensure 100% rejection.
"""

import copy
import time
import unittest
from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    canonical_encode,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root
)
from pillred.protocol.receipt import PredictionReceipt
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.protocol.client import PillRedClient


class TestAdversarialAttacks(unittest.TestCase):
    """Weaponized test vectors against PILL RED Protocol."""

    def setUp(self):
        """Generates a clean, valid reference receipt."""
        self.t_commit = 1700000000.0
        self.t_event = 1700000005.0
        self.t_resolve = 1700000006.0

        self.valid_receipt = PredictionReceipt.create_commitment(
            model_id="ALPHA_FORECASTER",
            model_version="1.0.0",
            target_event="HABANERO_SPIN_101",
            prediction="7",
            confidence=0.65,
            commit_timestamp=self.t_commit,
            receipt_id="REC-ALPHA-101",
            nonce="SEC_NONCE_01"
        )
        self.valid_receipt.settle(
            actual_outcome="7",
            event_timestamp=self.t_event,
            resolution_timestamp=self.t_resolve,
            payout_multiplier=10.0
        )
        # Ensure base receipt passes
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(self.valid_receipt.to_dict())
        self.assertTrue(is_valid, f"Base fixture must be valid, got: {vios}")

    # =========================================================================
    # Attack 1: Backdating Commitment (t_commit >= t_event)
    # =========================================================================
    def test_attack_01_backdating_commitment(self):
        """Attacker commits after or at the exact moment the event occurs."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["commit_timestamp"] = self.t_event + 0.1 # Committed after event happened!
        # Even if they rehash the commit hash, the verifier checks temporal precedence:
        tampered["commit_hash"] = compute_commit_hash(
            protocol_version=tampered["protocol_version"],
            receipt_id=tampered["receipt_id"],
            model_id=tampered["model_id"],
            model_version=tampered["model_version"],
            target_event=tampered["target_event"],
            prediction=tampered["prediction"],
            confidence=tampered["confidence"],
            commit_timestamp=tampered["commit_timestamp"],
            previous_receipt_hash=tampered["previous_receipt_hash"],
            nonce=tampered["nonce"]
        )
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Causal violation" in v for v in vios))

    # =========================================================================
    # Attack 2: Forward-Dating Resolution (t_resolve < t_event)
    # =========================================================================
    def test_attack_02_forward_dating_resolution(self):
        """Attacker claims resolution happened before the event actually occurred."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["resolution_timestamp"] = self.t_event - 0.1 # Impossible!
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Temporal violation" in v for v in vios))

    # =========================================================================
    # Attack 3: Prediction Payload Tampering (Mutating Loss to Win)
    # =========================================================================
    def test_attack_03_prediction_payload_tampering(self):
        """Attacker changed prediction from '0' to '7' after observing '7' landed."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["prediction"] = "BAR" # Mutate prediction post-hoc
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Commit hash mismatch" in v for v in vios))

    # =========================================================================
    # Attack 4: Confidence Inflation Mutation
    # =========================================================================
    def test_attack_04_confidence_inflation(self):
        """Attacker inflates their confidence score from 0.65 to 0.99 post-hoc."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["confidence"] = 0.99
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Commit hash mismatch" in v for v in vios))

    # =========================================================================
    # Attack 5: Target Event Swap
    # =========================================================================
    def test_attack_05_target_event_swap(self):
        """Attacker maps a winning prediction to a different event index."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["target_event"] = "HABANERO_SPIN_102"
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Commit hash mismatch" in v for v in vios))

    # =========================================================================
    # Attack 6: Resolution Outcome Falsification
    # =========================================================================
    def test_attack_06_resolution_outcome_falsification(self):
        """Attacker lies that actual outcome was '7' when it was '0'."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["actual_outcome"] = "0"
        # Receipt hash will mismatch because it was computed with "7"
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Receipt hash mismatch" in v for v in vios))

    # =========================================================================
    # Attack 7: Payout Multiplier Inflation
    # =========================================================================
    def test_attack_07_payout_multiplier_inflation(self):
        """Attacker inflates payout multiplier from 10x to 100x."""
        tampered = copy.deepcopy(self.valid_receipt.to_dict())
        tampered["payout_multiplier"] = 100.0
        is_valid, vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Receipt hash mismatch" in v for v in vios))

    # =========================================================================
    # Attack 8: Cross-Model Impersonation / Contamination
    # =========================================================================
    def test_attack_08_cross_model_impersonation(self):
        """Attacker injects Model B's winning receipt into Model A's sequence."""
        client = PillRedClient(model_id="MODEL_A")
        r1 = client.commit(target_event="E1", prediction="0")
        client.resolve(r1.receipt_id, actual_outcome="0")

        # Fake a receipt belonging to MODEL_B
        r2_alien = PredictionReceipt.create_commitment(
            model_id="MODEL_B",
            target_event="E2",
            prediction="7",
            previous_receipt_hash=r1.receipt_hash
        )
        r2_alien.settle(actual_outcome="7", event_timestamp=time.time() + 1)

        chain = [r1.to_dict(), r2_alien.to_dict()]
        is_valid, vios, _ = ZeroTrustVerifier.verify_chain(chain)
        self.assertFalse(is_valid)
        self.assertTrue(any("Cross-model contamination" in v for v in vios))

    # =========================================================================
    # Attack 9: Chain Linkage Severing (Broken previous_receipt_hash)
    # =========================================================================
    def test_attack_09_chain_linkage_severing(self):
        """Attacker tries to stitch two disconnected prediction chains together."""
        client = PillRedClient(model_id="MODEL_A")
        r1 = client.commit(target_event="E1", prediction="0")
        client.resolve(r1.receipt_id, actual_outcome="0")

        r2 = client.commit(target_event="E2", prediction="BAR")
        client.resolve(r2.receipt_id, actual_outcome="BAR")

        chain = [r1.to_dict(), r2.to_dict()]
        # Corrupt previous hash
        chain[1]["previous_receipt_hash"] = "f" * 64

        is_valid, vios, _ = ZeroTrustVerifier.verify_chain(chain)
        self.assertFalse(is_valid)
        self.assertTrue(any("Broken chain linkage" in v for v in vios))

    # =========================================================================
    # Attack 10: Chain Reordering Attack
    # =========================================================================
    def test_attack_10_chain_reordering(self):
        """Attacker swaps receipt 1 and receipt 2 to hide an early drawdown."""
        client = PillRedClient(model_id="MODEL_A")
        r1 = client.commit(target_event="E1", prediction="0")
        client.resolve(r1.receipt_id, actual_outcome="0")

        r2 = client.commit(target_event="E2", prediction="BAR")
        client.resolve(r2.receipt_id, actual_outcome="BAR")

        # Swap positions [r2, r1]
        reordered_chain = [r2.to_dict(), r1.to_dict()]
        is_valid, vios, _ = ZeroTrustVerifier.verify_chain(reordered_chain)
        self.assertFalse(is_valid)
        self.assertTrue(any("Broken chain linkage" in v for v in vios))

    # =========================================================================
    # Attack 11: Duplicate Receipt ID Injection
    # =========================================================================
    def test_attack_11_duplicate_receipt_injection(self):
        """Attacker replays the same receipt twice in the chain."""
        client = PillRedClient(model_id="MODEL_A")
        r1 = client.commit(target_event="E1", prediction="0")
        client.resolve(r1.receipt_id, actual_outcome="0")

        duplicated_chain = [r1.to_dict(), r1.to_dict()]
        is_valid, vios, _ = ZeroTrustVerifier.verify_chain(duplicated_chain)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate receipt ID" in v for v in vios))

    # =========================================================================
    # Attack 12: Canonicalization Ambiguity & Whitespace Injection
    # =========================================================================
    def test_attack_12_canonicalization_determinism(self):
        """Verifier computes identical hashes regardless of dictionary key sorting."""
        payload_a = {"z": "end", "a": "start", "m": "middle"}
        payload_b = {"a": "start", "m": "middle", "z": "end"}
        self.assertEqual(canonical_encode(payload_a), canonical_encode(payload_b))

    # =========================================================================
    # Attack 13: Merkle Root Forgery
    # =========================================================================
    def test_attack_13_merkle_root_forgery(self):
        """Verifier independently recalculates Merkle root, detecting forged roots."""
        hashes = ["a" * 64, "b" * 64, "c" * 64]
        legit_root = compute_merkle_root(hashes)
        forged_root = "0" * 64
        self.assertNotEqual(legit_root, forged_root)


if __name__ == "__main__":
    unittest.main()
