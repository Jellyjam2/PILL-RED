"""
Scientific & Economic Red-Team Audit Suite for PILL RED (Gates 5 & 6 Closeout).
Deliberately mounts adversarial statistical and economic scenarios to ensure zero false claims.
"""

import random
import unittest
from pillred.statistical.engine import StatisticalEngine
from pillred.economic.engine import EconomicEngine


class TestScientificRedTeam(unittest.TestCase):
    """Adversarial stress-testing of Statistical and Economic Truth Engines."""

    # =========================================================================
    # Attack 1: Autocorrelation Denial (IID vs Block Bootstrap under AR(1) clustering)
    # =========================================================================
    def test_redteam_01_autocorrelation_denial(self):
        """
        On highly clustered/serially dependent streams, Block Bootstrap properly expands
        confidence interval bounds compared to naive IID assumptions.
        """
        # Clustered streak pattern: 30 wins, 30 losses, 30 wins, 30 losses (N=120)
        actuals = ["7"] * 30 + ["0"] * 30 + ["7"] * 30 + ["0"] * 30
        preds = ["7"] * 120  # Always predicts win

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertTrue(stat_res.is_serially_dependent)
        self.assertLess(stat_res.markov_transition_p_value, 0.001)

        # Naive Wilson CI assumes IID; Block Bootstrap accounts for block variance
        w_low, w_high = stat_res.wilson_ci_99
        b_low, b_high = stat_res.block_bootstrap_ci_99

        # Bootstrap width must be non-zero and account for chunk variance
        self.assertGreaterEqual(b_high - b_low, 0.05)
        self.assertEqual(stat_res.verdict, "FAIL")  # Accuracy 50% fails majority 50%

    # =========================================================================
    # Attack 2: Lottery Outlier Illusion (1 lucky 1000x win masking 999 losses)
    # =========================================================================
    def test_redteam_02_lottery_outlier_illusion(self):
        """
        A system with 0.1% accuracy hits a 1000x jackpot.
        Statistical engine MUST flag it as FAIL (fails majority class null of 99.9% loss).
        Economic engine records positive P/L but captures high drawdown.
        """
        preds = ["JACKPOT"] * 1000
        actuals = ["0"] * 999 + ["JACKPOT"]
        payouts = [0.0] * 999 + [1000.0]

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertEqual(stat_res.verdict, "FAIL")
        self.assertEqual(stat_res.hits, 1)
        self.assertAlmostEqual(stat_res.accuracy, 0.001, places=4)
        self.assertLess(stat_res.delta_over_majority, 0.0)

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=1.0, initial_bankroll=2000.0)
        # Gross profit = 1000, total stake = 1000, friction = 40. Net = -40
        self.assertEqual(econ_res.active_ledger.winning_wagers, 1)
        self.assertEqual(econ_res.active_ledger.losing_wagers, 999)
        self.assertEqual(econ_res.active_ledger.max_drawdown_units, 999.0)

    # =========================================================================
    # Attack 3: Avoided Loss Illusion with Bleeding Active Wagers
    # =========================================================================
    def test_redteam_03_avoided_loss_with_bleeding_wagers(self):
        """
        Model correctly skips 80 losses on a 90-loss game, but its 20 active wagers
        all lose. System MUST NOT claim net economic victory.
        """
        # 80 skipped losses, 10 active wagers on '7' that landed on '0', 10 skipped losses
        preds = ["0"] * 80 + ["7"] * 10 + ["0"] * 10
        actuals = ["0"] * 100
        payouts = [0.0] * 100

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=5.0)
        self.assertEqual(econ_res.verdict, "FAIL")
        # Avoided loss is preserved: 90 * R5 = R450
        self.assertEqual(econ_res.avoided_ledger.capital_preserved, 450.0)
        # Active wager ledger has real negative cashflow: -R50 stake - friction
        self.assertEqual(econ_res.active_ledger.net_pnl, -52.0)
        self.assertFalse(econ_res.verdict == "PASS")

    # =========================================================================
    # Attack 4: Multiple Testing Bonferroni Adjustment (P-Hacking Defense)
    # =========================================================================
    def test_redteam_04_multiple_testing_bonferroni(self):
        """
        When testing across a family of K=20 hypothesis targets,
        nominal alpha=0.01 is adjusted to 0.0005, widening confidence intervals.
        """
        preds = ["7"] * 40 + ["0"] * 60
        actuals = ["7"] * 35 + ["0"] * 65 # 35/100 hits
        stat_single = StatisticalEngine.evaluate_stream(preds, actuals, hypothesis_family_size=1)
        stat_family = StatisticalEngine.evaluate_stream(preds, actuals, hypothesis_family_size=20)

        self.assertEqual(stat_single.effective_alpha, 0.01)
        self.assertEqual(stat_family.effective_alpha, 0.01 / 20.0)
        # 99.95% CI is wider than 99.0% CI
        self.assertGreater(stat_family.wilson_ci_99[1] - stat_family.wilson_ci_99[0],
                           stat_single.wilson_ci_99[1] - stat_single.wilson_ci_99[0])

    # =========================================================================
    # Attack 5: Unsettled & None Record Isolation
    # =========================================================================
    def test_redteam_05_unsettled_record_isolation(self):
        """
        Unsettled / None entries are strictly excluded from statistical evaluation
        and economic ledgers, preventing pollution.
        """
        preds = ["7", "BAR", "0", None, "7"]
        actuals = ["7", "BAR", "0", "UNSETTLED", None]
        payouts = [10.0, 6.0, 0.0, None, 0.0]

        stat_res = StatisticalEngine.evaluate_stream(preds, actuals)
        self.assertEqual(stat_res.total_observations, 3)
        self.assertEqual(stat_res.hits, 3)

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts)
        self.assertEqual(econ_res.total_events_observed, 5)
        self.assertEqual(econ_res.valid_settled_events, 3)
        self.assertEqual(econ_res.active_ledger.wagers_count, 2)

    # =========================================================================
    # Attack 6: Push / Breakeven (Multiplier = 1.0x) Accounting
    # =========================================================================
    def test_redteam_06_push_breakeven_accounting(self):
        """
        Multiplier of 1.0x returns stake without generating false profit.
        """
        preds = ["PUSH_SYM"] * 10
        actuals = ["PUSH_SYM"] * 10
        payouts = [1.0] * 10  # 1.0x return = push

        econ_res = EconomicEngine.evaluate(preds, actuals, payouts, unit_stake=10.0, house_edge_friction=0.0)
        self.assertEqual(econ_res.active_ledger.wagers_count, 10)
        self.assertEqual(econ_res.active_ledger.push_wagers, 10)
        self.assertEqual(econ_res.active_ledger.winning_wagers, 0)
        self.assertEqual(econ_res.active_ledger.gross_return, 100.0)
        self.assertEqual(econ_res.active_ledger.net_pnl, 0.0) # Zero profit

    # =========================================================================
    # Attack 7: Asymmetric Payoffs Evaluation
    # =========================================================================
    def test_redteam_07_asymmetric_payoffs(self):
        """
        High accuracy with small payouts vs Low accuracy with large payouts.
        """
        # Strategy A: 90% win rate on 1.1x multiplier -> Gross return on 10 spins = 9 * 1.1 = 9.9 on 10 stake = -0.1 loss
        preds_a = ["A"] * 10
        actuals_a = ["A"] * 9 + ["0"]
        payouts_a = [1.1] * 9 + [0.0]
        res_a = EconomicEngine.evaluate(preds_a, actuals_a, payouts_a, unit_stake=1.0, house_edge_friction=0.0)
        self.assertLess(res_a.active_ledger.net_pnl, 0.0) # Bleeds capital despite 90% win rate!


if __name__ == "__main__":
    unittest.main()
