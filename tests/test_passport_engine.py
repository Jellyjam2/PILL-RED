"""
Unit and Adversarial Tests for Gate 7 (Model Audit Passport Engine).
Validates deterministic cryptographic sealing, 4-state evidentiary taxonomy, and anti-tamper defenses.
"""

import copy
import json
import unittest
from pillred.protocol.client import PillRedClient
from pillred.protocol.passport import ModelAuditPassport
from pillred.statistical.engine import StatisticalEngine
from pillred.economic.engine import EconomicEngine
from pillred.protocol.verifier import ZeroTrustVerifier


class TestModelAuditPassportEngine(unittest.TestCase):
    """Tests Gate 7 Model Audit Passport generation, verification, and tamper resistance."""

    def setUp(self):
        # Generate a clean 10-event synthetic client history
        self.client = PillRedClient(model_id="ALPHA_MODEL_V1")
        for i in range(1, 11):
            pred = "7" if i % 2 == 1 else "0"
            r = self.client.commit(f"EVENT_{i:03}", pred, confidence=0.85)
            # Settle with alternating win / loss
            outcome = pred
            payout = 10.0 if pred == "7" else 0.0
            self.client.resolve(r.receipt_id, outcome, payout_multiplier=payout)

    # -------------------------------------------------------------------------
    # Test 1: Deterministic Generation and Verification
    # -------------------------------------------------------------------------
    def test_01_passport_creation_and_deterministic_hash(self):
        """Passport creates valid sub-hashes and deterministic passport_hash."""
        passport = self.client.get_passport(target_domain="RNG_SLOT_TELEMETRY")
        p_dict = passport.to_dict()

        is_valid, vios = ModelAuditPassport.verify_passport(p_dict)
        self.assertTrue(is_valid, f"Passport must be cryptographically valid, got: {vios}")
        self.assertEqual(p_dict["evidentiary_conclusions"]["provenance"], "VERIFIED")
        self.assertEqual(p_dict["evidentiary_conclusions"]["empirical_data"], "MEASURED")

    # -------------------------------------------------------------------------
    # Test 2: 4-State Evidentiary Taxonomy Separation
    # -------------------------------------------------------------------------
    def test_02_evidentiary_taxonomy_separation(self):
        """Passport correctly classifies Provenance: VERIFIED vs Statistical/Economic claims."""
        # 1. Winning model (100% hits on active wagers)
        pass_win = self.client.get_passport()
        self.assertEqual(pass_win.evidentiary_conclusions.provenance, "VERIFIED")
        self.assertEqual(pass_win.evidentiary_conclusions.empirical_data, "MEASURED")

        # 2. Naive zero-rule model (predicts 0 on 100% win stream -> Statistical & Economic FAIL)
        client_fail = PillRedClient(model_id="ZERO_RULE_MODEL")
        for i in range(1, 35):
            r = client_fail.commit(f"SPIN_{i:03}", "0", confidence=0.99)
            client_fail.resolve(r.receipt_id, actual_outcome="7", payout_multiplier=10.0) # Always misses!

        pass_fail = client_fail.get_passport()
        self.assertEqual(pass_fail.evidentiary_conclusions.provenance, "VERIFIED")
        self.assertEqual(pass_fail.evidentiary_conclusions.statistical_claim, "NOT PROVEN")
        self.assertEqual(pass_fail.evidentiary_conclusions.economic_claim, "INCONCLUSIVE") # 0 active wagers

    # -------------------------------------------------------------------------
    # Test 3: Adversarial Tamper Detection (Statistical Payload Tampering)
    # -------------------------------------------------------------------------
    def test_03_adversarial_statistical_tampering(self):
        """Altering measured accuracy post-hoc invalidates the statistical sub-hash and passport hash."""
        passport = self.client.get_passport()
        p_tampered = copy.deepcopy(passport.to_dict())

        # Attacker tries to forge accuracy from 1.0 to 0.99
        p_tampered["statistical_evidence"]["measured"]["accuracy"] = 0.99
        is_valid, vios = ModelAuditPassport.verify_passport(p_tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Statistical evidence hash mismatch" in v for v in vios))
        self.assertTrue(any("Passport hash mismatch" in v for v in vios))

    # -------------------------------------------------------------------------
    # Test 4: Adversarial Tamper Detection (Economic P/L Tampering)
    # -------------------------------------------------------------------------
    def test_04_adversarial_economic_tampering(self):
        """Altering net_pnl post-hoc invalidates the economic sub-hash and passport hash."""
        passport = self.client.get_passport()
        p_tampered = copy.deepcopy(passport.to_dict())

        # Attacker tries to inflate net_pnl
        p_tampered["economic_evidence"]["measured"]["net_pnl"] += 1000.0
        is_valid, vios = ModelAuditPassport.verify_passport(p_tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Economic evidence hash mismatch" in v for v in vios))
        self.assertTrue(any("Passport hash mismatch" in v for v in vios))

    # -------------------------------------------------------------------------
    # Test 5: Adversarial Tamper Detection (Identity Tampering)
    # -------------------------------------------------------------------------
    def test_05_adversarial_identity_tampering(self):
        """Altering model_id or target_domain invalidates the passport seal."""
        passport = self.client.get_passport()
        p_tampered = copy.deepcopy(passport.to_dict())

        p_tampered["identity"]["model_id"] = "IMPOSTOR_MODEL"
        is_valid, vios = ModelAuditPassport.verify_passport(p_tampered)
        self.assertFalse(is_valid)
        self.assertTrue(any("Passport hash mismatch" in v for v in vios))


if __name__ == "__main__":
    unittest.main()
