"""
Unit and Integration Tests for Gate 5 (Statistical Engine) and Gate 6 (Economic Engine).
Executes the comprehensive 11-Case Verification Matrix and Test Vector conformance suite.
"""

import json
import os
import random
import unittest
from pillred.statistical.engine import StatisticalEngine
from pillred.economic.engine import EconomicEngine
from pillred.protocol.verifier import ZeroTrustVerifier


class TestStatisticalAndEconomicEngines(unittest.TestCase):
    """Executes the full Gate 5 & Gate 6 Verification Matrix."""

    # -------------------------------------------------------------------------
    # Case 1: Perfect Predictor
    # -------------------------------------------------------------------------
    def test_01_perfect_predictor(self):
        """Perfect predictor is correctly recognized by both engines."""
        preds = ["7"] * 50 + ["BAR"] * 50
        actuals = ["7"] * 50 + ["BAR"] * 50
        payouts = [10.0] * 50 + [6.0] * 50

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals, confidences=[0.95]*100)
        self.assertEqual(stat_res.verdict, "PASS")
        self.assertEqual(stat_res.accuracy, 1.0)
        self.assertGreater(stat_res.delta_over_majority, 0.4)

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=1.0)
        self.assertEqual(econ_res.verdict, "PASS")
        self.assertGreater(econ_res.active_ledger.net_pnl, 500.0)
        self.assertEqual(econ_res.active_ledger.win_rate, 1.0)

    # -------------------------------------------------------------------------
    # Case 2: Random Uniform Predictor
    # -------------------------------------------------------------------------
    def test_02_random_uniform_predictor(self):
        """Random uniform guesser (1/10 accuracy) produces Statistical FAIL and Economic FAIL."""
        random.seed(42)
        symbols = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
        actuals = [random.choice(symbols) for _ in range(200)]
        preds = [random.choice(symbols) for _ in range(200)]
        payouts = [10.0 if a == "7" else (6.0 if a == "1" else 0.0) for a in actuals]

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertEqual(stat_res.verdict, "FAIL")
        self.assertLess(stat_res.accuracy, 0.20)

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts)
        self.assertEqual(econ_res.verdict, "FAIL")
        self.assertLess(econ_res.active_ledger.net_pnl, 0.0)

    # -------------------------------------------------------------------------
    # Case 3: Majority-Class Baseline Predictor (Zero Rule)
    # -------------------------------------------------------------------------
    def test_03_majority_class_predictor(self):
        """Model predicting '0' on a 70% loss stream gets 70% accuracy but ZERO statistical delta (FAIL)."""
        actuals = ["0"] * 70 + ["7"] * 30
        preds = ["0"] * 100  # Zero-rule
        payouts = [0.0] * 70 + [10.0] * 30

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertEqual(stat_res.verdict, "FAIL")
        self.assertEqual(stat_res.accuracy, 0.70)
        self.assertAlmostEqual(stat_res.delta_over_majority, 0.0, places=4)

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts)
        # Zero active wagers placed -> Inconclusive on active wagers
        self.assertEqual(econ_res.active_ledger.wagers_count, 0)
        self.assertEqual(econ_res.avoided_ledger.correctly_avoided_losses_count, 70)
        self.assertEqual(econ_res.avoided_ledger.capital_preserved, 70.0)

    # -------------------------------------------------------------------------
    # Case 4: Serially Correlated Markov Stream
    # -------------------------------------------------------------------------
    def test_04_serially_correlated_stream(self):
        """Markov dependency test accurately flags serially dependent clustered streams."""
        # Long clustered streak: 20 zeroes, 10 wins, 20 zeroes, 10 wins
        actuals = ["0"] * 25 + ["7"] * 15 + ["0"] * 25 + ["7"] * 15
        preds = ["0"] * 80

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertTrue(stat_res.is_serially_dependent)
        self.assertLess(stat_res.markov_transition_p_value, 0.05)

    # -------------------------------------------------------------------------
    # Case 5: Shuffled Predictions Destroy Predictive Advantage
    # -------------------------------------------------------------------------
    def test_05_shuffled_predictions(self):
        """Shuffling predictions destroys alignment with ground truth."""
        actuals = ["7", "0", "7", "0", "7", "0", "7", "0"] * 10 # 80 items
        preds = list(actuals) # Perfect
        random.seed(123)
        random.shuffle(preds) # Destroy alignment

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertLess(stat_res.accuracy, 0.70)

    # -------------------------------------------------------------------------
    # Case 6: Small Sample Size (Under-Powered)
    # -------------------------------------------------------------------------
    def test_06_small_sample_size_inconclusive(self):
        """N=10 observations is appropriately classified as INCONCLUSIVE."""
        actuals = ["7", "7", "7", "7", "7", "7", "7", "7", "0", "0"]
        preds = ["7", "7", "7", "7", "7", "7", "7", "7", "0", "0"]
        stat_res = StatisticalEngine.evaluate_stream(preds, actuals, min_sample_size=30)
        self.assertEqual(stat_res.verdict, "INCONCLUSIVE")
        self.assertIn("below statistical threshold", stat_res.justification)

    # -------------------------------------------------------------------------
    # Case 7: High Accuracy / Bad Economics (The Slot Trap)
    # -------------------------------------------------------------------------
    def test_07_high_accuracy_bad_economics(self):
        """70% accuracy on loss, but 10 active wagers all lose -> Statistical FAIL & Economic FAIL."""
        # 70 losses predicted correctly as 0, 10 active wagers on '7' that landed on '0'
        preds = ["0"] * 70 + ["7"] * 10
        actuals = ["0"] * 70 + ["0"] * 10
        payouts = [0.0] * 80

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=5.0)
        self.assertEqual(econ_res.verdict, "FAIL")
        self.assertEqual(econ_res.active_ledger.winning_wagers, 0)
        self.assertEqual(econ_res.active_ledger.losing_wagers, 10)
        self.assertEqual(econ_res.active_ledger.net_pnl, -52.0) # -50 stake - 4% friction
        self.assertEqual(econ_res.avoided_ledger.capital_preserved, 350.0) # 70 * 5

    # -------------------------------------------------------------------------
    # Case 8: Low Accuracy / Positive Avoided Loss Accounting
    # -------------------------------------------------------------------------
    def test_08_avoided_loss_separate_accounting(self):
        """Avoided loss is strictly isolated and never double-counted into active P/L."""
        preds = ["0"] * 50 + ["BAR"] * 10
        actuals = ["0"] * 50 + ["0"] * 10
        payouts = [0.0] * 60

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=10.0)
        # Active P/L must be negative (-100 stake - friction)
        self.assertLess(econ_res.active_ledger.net_pnl, 0.0)
        # Avoided loss must be exactly 50 * 10 = 500
        self.assertEqual(econ_res.avoided_ledger.capital_preserved, 500.0)
        self.assertEqual(econ_res.avoided_ledger.skipped_events_count, 50)

    # -------------------------------------------------------------------------
    # Case 9: House Margin Friction Degradation
    # -------------------------------------------------------------------------
    def test_09_house_margin_friction(self):
        """Higher house friction appropriately reduces net P/L."""
        preds = ["7"] * 20
        actuals = ["7"] * 20
        payouts = [2.0] * 20 # Gross return = 40 on 20 stake

        res_low_friction = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=1.0, house_edge_friction=0.01)
        res_high_friction = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=1.0, house_edge_friction=0.15)
        self.assertGreater(res_low_friction.active_ledger.net_pnl, res_high_friction.active_ledger.net_pnl)

    # -------------------------------------------------------------------------
    # Case 10: Maximum Drawdown Tracking
    # -------------------------------------------------------------------------
    def test_10_max_drawdown_tracking(self):
        """Peak-to-trough equity drawdown is accurately tracked."""
        # Win 3 times (+30), lose 5 times (-50), win 2 times (+20)
        preds = ["7"] * 10
        actuals = ["7", "7", "7", "0", "0", "0", "0", "0", "7", "7"]
        payouts = [10.0, 10.0, 10.0, 0.0, 0.0, 0.0, 0.0, 0.0, 10.0, 10.0]

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=10.0, initial_bankroll=100.0)
        # Peak bankroll was 100 + 270 = 370. Then lost 50 -> 320. Max drawdown = 50.
        self.assertEqual(econ_res.active_ledger.max_drawdown_units, 50.0)
        self.assertEqual(econ_res.active_ledger.drawdown_duration_events, 5)

    # -------------------------------------------------------------------------
    # Case 11: Cross-Language Test Vectors Conformance
    # -------------------------------------------------------------------------
    def test_11_test_vectors_conformance(self):
        """Standardized test_vectors/ conform 100% with expected manifest."""
        manifest_path = "test_vectors/expected/test_vector_manifest.json"
        self.assertTrue(os.path.exists(manifest_path))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # 1. Check valid receipt
        with open("test_vectors/valid/receipt_001.json", "r", encoding="utf-8") as f:
            r1 = json.load(f)
        valid, vios = ZeroTrustVerifier.verify_single_receipt(r1)
        self.assertTrue(valid)
        self.assertEqual(r1["commit_hash"], manifest["vectors"]["valid_receipt_001"]["expected_commit_hash"])
        self.assertEqual(r1["receipt_hash"], manifest["vectors"]["valid_receipt_001"]["expected_receipt_hash"])

        # 2. Check valid chain
        with open("test_vectors/valid/chain_001.json", "r", encoding="utf-8") as f:
            chain = json.load(f)
        chain_valid, chain_vios, root = ZeroTrustVerifier.verify_chain(chain)
        self.assertTrue(chain_valid)
        self.assertEqual(root, manifest["vectors"]["valid_chain_001"]["expected_merkle_root"])

        # 3. Check invalid fixtures
        with open("test_vectors/invalid/tampered_prediction.json", "r", encoding="utf-8") as f:
            tampered = json.load(f)
        t_valid, t_vios = ZeroTrustVerifier.verify_single_receipt(tampered)
        self.assertFalse(t_valid)


if __name__ == "__main__":
    unittest.main()
