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

    def test_rare_event_jackpot_target_evaluator(self):
        """Tests that evaluate_rare_event_target correctly assesses rare jackpot triggers."""
        from rng_audit.statistics.predictor import PredictiveHypothesisTester

        # 10,000 spin sequence with a rare jackpot occurring at fixed period of 500 spins
        unseen_spins = [1 if (i > 0 and i % 500 == 0) else 0 for i in range(5000)]
        
        # Trigger: trigger bet only when spin counter is multiple of 500
        trigger_fn = lambda hist: len(hist) > 0 and len(hist) % 500 == 0

        res = PredictiveHypothesisTester.evaluate_rare_event_target(
            discovery_sequence=[],
            unseen_sequence=unseen_spins,
            trigger_fn=trigger_fn,
            null_event_probability=1e-4,  # baseline 1 in 10,000
            payout_multiplier=5000.0       # 5,000x jackpot
        )

        self.assertEqual(res["triggered_bets"], 9)
        self.assertEqual(res["hits"], 9)
        self.assertEqual(res["triggered_hit_rate"], 1.0)
        self.assertTrue(res["statistically_significant"])
        self.assertTrue(res["economically_viable"])
        self.assertEqual(res["verdict"], "REPRODUCIBLE_ECONOMIC_EDGE")


if __name__ == "__main__":
    unittest.main()
