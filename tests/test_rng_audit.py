"""Unit and Calibration Tests for PILL RED RNG Structural Audit."""

import time
import unittest
from rng_audit.generators.reference_generators import (
    WeakLCG,
    QuadraticPRNG,
    XorShift32,
    MersenneTwisterPRNG,
    CryptographicRNG,
)
from rng_audit.statistics.battery import RNGTestBattery
from rng_audit.collectors.schema import SpinRecord, SpinLogger


class TestRNGAudit(unittest.TestCase):
    """Verifies RNG Audit statistical battery and calibration ladder."""

    def test_weak_lcg_detection(self):
        """Weak LCG should be detected as having non-random structure."""
        gen = WeakLCG(seed=42, a=65, c=1, m=2048)
        seq = gen.generate_sequence(1000, max_val=100)
        audit = RNGTestBattery.run_full_audit(seq, max_val=100)
        self.assertEqual(audit["verdict"], "STRUCTURE_DETECTED")
        self.assertTrue(audit["has_reproducible_structure"])

    def test_cryptographic_rng_null_hypothesis(self):
        """CSPRNG baseline should NOT produce false-positive structure (verdict = NO_EXPLOITABLE_STRUCTURE_DETECTED)."""
        gen = CryptographicRNG()
        seq = gen.generate_sequence(1000, max_val=100)
        audit = RNGTestBattery.run_full_audit(seq, max_val=100)
        self.assertEqual(audit["verdict"], "NO_EXPLOITABLE_STRUCTURE_DETECTED")
        self.assertFalse(audit["has_reproducible_structure"])

    def test_spin_logger_roundtrip(self):
        """SpinLogger correctly writes and loads spin records."""
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
            tmp_path = tmp.name

        try:
            logger = SpinLogger(storage_path=tmp_path)
            rec = SpinRecord(
                timestamp=1700000000.0,
                game_title="Reel Rush",
                session_id="SESS-001",
                spin_index=1,
                outcome_symbols=[7, 7, 7],
                payout_multiplier=25.0,
                bonus_event=True
            )
            logger.log_spin(rec)
            loaded = logger.load_spins(game_title="Reel Rush")
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].game_title, "Reel Rush")
            self.assertEqual(loaded[0].payout_multiplier, 25.0)
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_predictive_hypothesis_tester(self):
        """PredictiveHypothesisTester distinguishes genuine predictive edge from random chance."""
        from rng_audit.statistics.predictor import PredictiveHypothesisTester

        # 1. Deterministic sequence where predictor is 100% accurate
        discovery = [i % 10 for i in range(100)]
        unseen = [i % 10 for i in range(100, 200)]
        
        # Predictor: next value is (last_val + 1) % 10
        predictor_fn = lambda hist: (hist[-1] + 1) % 10

        res = PredictiveHypothesisTester.evaluate_predictive_edge(
            discovery_sequence=discovery,
            unseen_sequence=unseen,
            predictor_fn=predictor_fn,
            alphabet_size=10,
            house_edge_fraction=0.04
        )

        self.assertTrue(res["statistically_significant"])
        self.assertTrue(res["economically_viable"])
        self.assertEqual(res["verdict"], "REPRODUCIBLE_ECONOMIC_EDGE")
        self.assertAlmostEqual(res["observed_hit_rate"], 1.0)

    def test_multi_session_auditor(self):
        """MultiSessionAuditor correctly processes multi-session spin records."""
        from rng_audit.statistics.session_auditor import MultiSessionAuditor

        disc_records = [
            SpinRecord(timestamp=time.time(), game_title="TestSlot", session_id="S1", spin_index=i, outcome_symbols=[i % 5], payout_multiplier=1.0)
            for i in range(100)
        ]
        val_records = [
            SpinRecord(timestamp=time.time(), game_title="TestSlot", session_id="S2", spin_index=i, outcome_symbols=[i % 5], payout_multiplier=1.0)
            for i in range(100, 200)
        ]

        res = MultiSessionAuditor.audit_game_sessions(
            discovery_records=disc_records,
            validation_records=val_records,
            alphabet_size=5,
            house_edge_fraction=0.04
        )

        self.assertIn("verdict", res)
        self.assertEqual(res["game_title"], "TestSlot")
        self.assertTrue(res["statistically_significant"])


if __name__ == "__main__":
    unittest.main()
