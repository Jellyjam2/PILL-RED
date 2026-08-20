"""Unit and Causal Tests for Forensic Prediction Ledger."""

import os
import tempfile
import time
import unittest

from rng_audit.eyes.prediction_ledger import ForensicPredictionLedger, PredictionRecord


class TestPredictionLedger(unittest.TestCase):
    """Verifies causal integrity and persistence of prediction commitments."""

    def test_causal_prediction_resolution_cycle(self):
        """Prediction locked before spin settlement resolves with VALID causal status."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
            tmp_path = tmp.name

        try:
            ledger = ForensicPredictionLedger(ledger_path=tmp_path)
            t_pred = time.time()

            # 1. Lock prediction for Spin 5 at t_pred
            pred = ledger.lock_prediction(
                session_id="SESS-001",
                source_spin_index=4,
                target_spin_index=5,
                predicted_target="SYMBOL",
                decision=7,
                confidence=0.85,
                model_hash="HASH-MODEL-V1",
                timestamp=t_pred
            )
            self.assertEqual(pred.causal_status, "PENDING")
            self.assertIsNone(pred.actual_result)

            # 2. Resolve prediction at t_res > t_pred with actual result = 7 (HIT)
            t_res = t_pred + 0.5
            resolved = ledger.resolve_prediction(
                session_id="SESS-001",
                target_spin_index=5,
                actual_result=7,
                timestamp_resolved=t_res
            )

            self.assertIsNotNone(resolved)
            self.assertEqual(resolved.causal_status, "VALID")
            self.assertTrue(resolved.is_hit)
            self.assertEqual(resolved.actual_result, 7)

            # 3. Verify ledger reload from disk
            loaded = ledger.load_predictions(session_id="SESS-001")
            self.assertEqual(len(loaded), 1)
            self.assertEqual(loaded[0].prediction_id, pred.prediction_id)
            self.assertEqual(loaded[0].causal_status, "VALID")
            self.assertTrue(loaded[0].is_hit)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)

    def test_causal_leakage_detection(self):
        """Resolution timestamp prior to or equal to prediction timestamp is flagged as INVALID_LEAKAGE."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jsonl") as tmp:
            tmp_path = tmp.name

        try:
            ledger = ForensicPredictionLedger(ledger_path=tmp_path)
            t_pred = 1000.0

            # Lock prediction at t=1000.0
            ledger.lock_prediction(
                session_id="SESS-002",
                source_spin_index=1,
                target_spin_index=2,
                predicted_target="JACKPOT",
                decision="BET",
                confidence=0.9,
                model_hash="HASH-MODEL-V1",
                timestamp=t_pred
            )

            # Illegitimate resolution at t=999.0 (prior to prediction)
            resolved = ledger.resolve_prediction(
                session_id="SESS-002",
                target_spin_index=2,
                actual_result=1,
                timestamp_resolved=999.0
            )

            self.assertIsNotNone(resolved)
            self.assertEqual(resolved.causal_status, "INVALID_LEAKAGE")
            self.assertFalse(resolved.is_hit)

        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()
