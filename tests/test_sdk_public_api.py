"""
Unit Tests for Gate 9 (Public Developer SDK Interface).
Tests module-level convenience functions, client isolation, and zero-trust verification helpers.
"""

import json
import os
import unittest
import pillred


class TestPublicSDKApi(unittest.TestCase):
    """Tests the top-level pillred public API interface."""

    def setUp(self):
        pillred.reset()

    def tearDown(self):
        pillred.reset()

    def test_01_top_level_commit_and_resolve(self):
        """Top-level pillred.commit and pillred.resolve operate frictionlessly."""
        r = pillred.commit(
            target_event="TEST_EVENT_001",
            prediction="7",
            confidence=0.88,
            model_id="ALPHA_MODEL"
        )
        self.assertIsNotNone(r.commit_hash)
        self.assertEqual(r.target_event, "TEST_EVENT_001")
        self.assertEqual(r.prediction, "7")

        r_settled = pillred.resolve(
            receipt_id=r.receipt_id,
            actual_outcome="7",
            payout_multiplier=10.0
        )
        self.assertIsNotNone(r_settled.receipt_hash)
        self.assertTrue(r_settled.is_hit)
        self.assertEqual(r_settled.actual_outcome, "7")

    def test_02_top_level_get_passport(self):
        """Top-level pillred.get_passport compiles and verifies a valid passport."""
        for i in range(1, 6):
            r = pillred.commit(f"SPIN_{i:02d}", "7" if i % 2 == 1 else "0")
            pillred.resolve(r.receipt_id, "7" if i % 2 == 1 else "0", payout_multiplier=10.0 if i % 2 == 1 else 0.0)

        passport = pillred.get_passport(target_domain="CASINO_RNG")
        self.assertIsNotNone(passport.passport_hash)
        self.assertEqual(passport.provenance.total_receipts, 5)
        self.assertEqual(passport.evidentiary_conclusions.provenance, "VERIFIED")

    def test_03_top_level_verify_function(self):
        """pillred.verify audits in-memory dicts, lists, and JSON filepaths."""
        # 1. Single receipt dict
        r = pillred.commit("EV_1", "0")
        r_settled = pillred.resolve(r.receipt_id, "0", payout_multiplier=0.0)
        valid, vios = pillred.verify(r_settled.to_dict())
        self.assertTrue(valid, f"Receipt must verify, got: {vios}")

        # 2. Existing valid test vector file
        valid_file, vios_file = pillred.verify("test_vectors/valid/passport_001.json")
        self.assertTrue(valid_file, f"Passport vector must verify, got: {vios_file}")

        # 3. Existing tampered test vector file
        invalid_file, vios_inv = pillred.verify("test_vectors/invalid/tampered_passport.json")
        self.assertFalse(invalid_file)

    def test_04_session_reset(self):
        """pillred.reset() flushes global state cleanly."""
        pillred.commit("EV_1", "0")
        pillred.reset()
        passport = pillred.get_passport()
        self.assertEqual(passport.provenance.total_receipts, 0)

    def test_05_multi_client_isolation(self):
        """Multiple PillRedClient instances operate independently without memory collision."""
        c1 = pillred.PillRedClient(model_id="MODEL_A")
        c2 = pillred.PillRedClient(model_id="MODEL_B")

        r1 = c1.commit("EV_A", "UP")
        c1.resolve(r1.receipt_id, "UP", 2.0)

        r2 = c2.commit("EV_B", "DOWN")
        c2.resolve(r2.receipt_id, "DOWN", 2.0)

        p1 = c1.get_passport()
        p2 = c2.get_passport()

        self.assertEqual(p1.identity.model_id, "MODEL_A")
        self.assertEqual(p2.identity.model_id, "MODEL_B")
        self.assertNotEqual(p1.passport_hash, p2.passport_hash)


if __name__ == "__main__":
    unittest.main()
