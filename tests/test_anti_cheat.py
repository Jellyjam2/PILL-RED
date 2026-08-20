"""Unit and Adversarial Attack Tests for Anti-Cheat Forensic Verification Benchmark."""

import unittest
from command_center.anti_cheat_benchmark import (
    AntiCheatForensicBenchmark,
    TamperEvidentPredictionChain
)


class TestAntiCheatBenchmark(unittest.TestCase):
    """Verifies that the pre-commitment hash chain detects and invalidates all cheating vectors."""

    def test_full_anti_cheat_benchmark_suite(self):
        """Runs the 1,000-event tournament and confirms all 6 adversarial attacks are neutralized."""
        results = AntiCheatForensicBenchmark.run_benchmark()

        # 1. Verify 1,000 event tournament concluded
        tournament = results["tournament"]
        self.assertEqual(tournament["events_evaluated"], 1000)
        self.assertTrue(tournament["model_a_chain_valid"])
        self.assertTrue(tournament["model_b_chain_valid"])
        self.assertEqual(tournament["declared_winner"], "MODEL-A")

        # 2. Verify all 6 cheating vectors were detected and rejected
        self.assertTrue(results["all_attacks_neutralized"])

        attacks = results["adversarial_attacks"]
        self.assertTrue(attacks["1_lookahead_leakage"]["detected_and_rejected"])
        self.assertTrue(attacks["2_retroactive_tampering"]["detected_and_rejected"])
        self.assertTrue(attacks["3_timestamp_forgery"]["detected_and_rejected"])
        self.assertTrue(attacks["4_model_substitution"]["detected_and_rejected"])
        self.assertTrue(attacks["5_cherry_picking_drop"]["detected_and_rejected"])
        self.assertTrue(attacks["6_outcome_forgery"]["detected_and_rejected"])


if __name__ == "__main__":
    unittest.main()
