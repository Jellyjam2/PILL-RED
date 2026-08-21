"""Unit and Integration Tests for PILL RED Platform & Command Center."""

import json
import time
import unittest
from command_center.server import PlatformDataStore


class TestPlatformCommandCenter(unittest.TestCase):
    """Verifies Platform DataStore and API logic."""

    def test_datastore_ingest_and_prediction_cycle(self):
        """DataStore correctly resolves pending prediction and locks next target."""
        store = PlatformDataStore()
        
        # Initial state should have a pending prediction for spin #1
        state0 = store.get_dashboard_state()
        self.assertIsNotNone(state0["pending_prediction"])
        self.assertEqual(state0["pending_prediction"]["target_spin_index"], 1)

        # Ingest observation for spin #1
        res1 = store.ingest_observation({
            "timestamp": time.time(),
            "symbols": [7],
            "payout_multiplier": 10.0,
            "bonus_event": True
        })

        self.assertEqual(res1["recorded_spin"]["spin_index"], 1)
        self.assertIsNotNone(res1["resolved_prediction"])
        self.assertEqual(res1["resolved_prediction"]["target_spin_index"], 1)
        self.assertEqual(res1["next_prediction"]["target_spin_index"], 2)

        # Check state after ingest
        state1 = store.get_dashboard_state()
        self.assertEqual(state1["total_observed_spins"], 1)
        self.assertEqual(state1["total_resolved_predictions"], 1)
        self.assertEqual(state1["pending_prediction"]["target_spin_index"], 2)

    def test_datastore_reset_session(self):
        """DataStore reset_session cleanly clears telemetry and resets to Event #1."""
        store = PlatformDataStore()
        store.ingest_observation({"symbols": [7], "payout_multiplier": 10.0})
        self.assertEqual(len(store.observed_records), 1)

        reset_res = store.reset_session()
        self.assertTrue(reset_res["success"])
        self.assertEqual(len(store.observed_records), 0)

        state = store.get_dashboard_state()
        self.assertEqual(state["total_observed_spins"], 0)
        self.assertEqual(state["total_resolved_predictions"], 0)
        self.assertEqual(state["pending_prediction"]["target_spin_index"], 1)

    def test_datastore_delete_and_undo(self):
        """DataStore correctly deletes specific events and supports single undo."""
        store = PlatformDataStore()
        store.ingest_observation({"symbols": [7], "payout_multiplier": 10.0})
        store.ingest_observation({"symbols": ["0"], "payout_multiplier": 0.0})
        store.ingest_observation({"symbols": ["BAR"], "payout_multiplier": 6.0})
        self.assertEqual(len(store.observed_records), 3)

        # Undo last (event #3)
        undo_res = store.undo_last_observation()
        self.assertTrue(undo_res["success"])
        self.assertEqual(len(store.observed_records), 2)
        self.assertEqual(store.observed_records[-1].spin_index, 2)

        # Delete event #1
        del_res = store.delete_observation(1)
        self.assertTrue(del_res["success"])
        self.assertEqual(len(store.observed_records), 1)
        self.assertEqual(store.observed_records[0].spin_index, 1)


if __name__ == "__main__":
    unittest.main()
