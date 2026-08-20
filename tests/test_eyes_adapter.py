"""Unit and Integration Tests for PILL RED Eyes Observation Layer."""

import json
import time
import unittest
import numpy as np

from rng_audit.eyes.adapter import ObservationAdapter, RawObservation
from rng_audit.eyes.capture import SpinSettleDetector
from rng_audit.collectors.schema import SpinRecord


class TestEyesAdapter(unittest.TestCase):
    """Verifies observation adapter, settle detector, and data normalization."""

    def test_observation_adapter_normalization(self):
        """Adapter correctly maps raw strings to consistent integer categories."""
        adapter = ObservationAdapter()
        
        raw1 = RawObservation(
            timestamp=time.time(),
            source_type="optical_cv",
            game_title="Hot Hot Fruit",
            session_id="SESS-001",
            raw_symbols=["cherry", "seven", "bar"],
            payout_multiplier=2.5,
            bonus_flag=False,
            raw_metadata={"confidence": 0.98}
        )
        rec1 = adapter.normalize(raw1)
        self.assertEqual(rec1.spin_index, 1)
        self.assertEqual(len(rec1.outcome_symbols), 3)
        self.assertEqual(rec1.game_title, "Hot Hot Fruit")

        # Second spin with same symbols should receive identical integer mappings
        raw2 = RawObservation(
            timestamp=time.time(),
            source_type="optical_cv",
            game_title="Hot Hot Fruit",
            session_id="SESS-001",
            raw_symbols=["cherry", "cherry", "cherry"],
            payout_multiplier=10.0,
            bonus_flag=True,
            raw_metadata={"confidence": 0.99}
        )
        rec2 = adapter.normalize(raw2)
        self.assertEqual(rec2.spin_index, 2)
        self.assertEqual(rec2.outcome_symbols[0], rec1.outcome_symbols[0])  # 'cherry' ID matches
        self.assertTrue(rec2.bonus_event)

    def test_spin_settle_detector_lifecycle(self):
        """Settle detector detects motion energy spike and subsequent stillness."""
        detector = SpinSettleDetector(motion_threshold=10.0, settle_duration_sec=0.1, min_spin_duration_sec=0.2)

        # 1. Static initial frames -> IDLE
        f0 = np.zeros((100, 100), dtype=np.uint8)
        event, _ = detector.process_frame(f0, current_time=1.0)
        self.assertEqual(event, "IDLE")

        event, _ = detector.process_frame(f0, current_time=1.05)
        self.assertEqual(event, "IDLE")

        # 2. Motion spike (spinning reels) -> SPIN_STARTED
        f_spin1 = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        event, energy = detector.process_frame(f_spin1, current_time=1.1)
        self.assertEqual(event, "SPIN_STARTED")
        self.assertGreater(energy, 10.0)

        # 3. Continued spinning -> SPINNING
        f_spin2 = np.random.randint(0, 255, (100, 100), dtype=np.uint8)
        event, _ = detector.process_frame(f_spin2, current_time=1.2)
        self.assertEqual(event, "SPINNING")

        # 4. Reels settle (identical frames) after min duration -> SPIN_SETTLED
        f_settle = np.ones((100, 100), dtype=np.uint8) * 128
        detector.process_frame(f_settle, current_time=1.4)  # First still frame
        event, _ = detector.process_frame(f_settle, current_time=1.55)  # Settled for > 0.1s
        self.assertEqual(event, "SPIN_SETTLED")


if __name__ == "__main__":
    unittest.main()
