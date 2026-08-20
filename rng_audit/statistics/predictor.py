"""Predictive Hypothesis Testing & Economic Viability Harness.

Evaluates whether a detected structural anomaly provides statistically significant
out-of-sample predictive edge over the baseline null model and calculates the expected
value (EV) after house-edge / transaction costs.
"""

import math
from typing import Callable, Dict, List, Optional
import numpy as np
from scipy import stats


class PredictiveHypothesisTester:
    """Rigorous Out-of-Sample Predictive Validation & Economic Edge Evaluator."""

    ALPHA_THRESHOLD = 0.01

    @classmethod
    def evaluate_predictive_edge(
        cls,
        discovery_sequence: List[int],
        unseen_sequence: List[int],
        predictor_fn: Callable[[List[int]], int],
        alphabet_size: int = 100,
        house_edge_fraction: float = 0.04  # e.g. 96% RTP -> 4% house edge
    ) -> Dict[str, any]:
        """Tests a locked predictor function on completely unseen out-of-sample data.

        - Null Hypothesis (H0): Predictor accuracy = 1 / alphabet_size (random chance).
        - Alternative (H1): Predictor accuracy > 1 / alphabet_size.
        - Economic Test: Determines if edge exceeds the house edge barrier.
        """
        n_unseen = len(unseen_sequence)
        if n_unseen < 50:
            return {
                "sample_size": n_unseen,
                "passed": False,
                "p_value": 1.0,
                "notes": "Insufficient out-of-sample size (need >= 50)."
            }

        # Baseline random chance
        p_null = 1.0 / float(alphabet_size)

        # Evaluate predictor step-by-step on unseen sequence (strictly causal: history < t)
        history = list(discovery_sequence)
        hits = 0
        predictions = []

        for actual in unseen_sequence:
            pred = predictor_fn(history)
            predictions.append(pred)
            if pred == actual:
                hits += 1
            history.append(actual)

        hit_rate = hits / float(n_unseen)

        # Exact Binomial Test for predictive edge over random chance
        # Alternative: greater (one-tailed)
        binom_res = stats.binomtest(hits, n=n_unseen, p=p_null, alternative="greater")
        p_val = float(binom_res.pvalue)

        # Calculate Theoretical Economic Return (EV)
        # In standard casino paytables (e.g. 96% RTP -> house_edge_fraction h = 0.04):
        # The offered payout multiplier per $1 stake is: M_actual = alphabet_size * (1 - house_edge_fraction)
        # Net EV per $1 wagered is: hit_rate * M_actual - 1.0 = hit_rate * alphabet_size * (1 - h) - 1.0
        rtp_fraction = 1.0 - house_edge_fraction
        actual_payout_multiplier = float(alphabet_size) * rtp_fraction
        gross_return = hit_rate * actual_payout_multiplier
        net_ev = gross_return - 1.0

        is_statistically_significant = bool(p_val < cls.ALPHA_THRESHOLD)
        is_economically_viable = bool(is_statistically_significant and net_ev > 0.0)

        verdict = "NO_PREDICTIVE_EDGE"
        if is_economically_viable:
            verdict = "REPRODUCIBLE_ECONOMIC_EDGE"
        elif is_statistically_significant:
            verdict = "STATISTICAL_STRUCTURE_WITHOUT_ECONOMIC_EDGE"

        return {
            "unseen_sample_size": n_unseen,
            "hits": hits,
            "observed_hit_rate": float(hit_rate),
            "baseline_null_rate": float(p_null),
            "edge_over_chance": float(hit_rate - p_null),
            "binomial_p_value": float(p_val),
            "statistically_significant": is_statistically_significant,
            "rtp_fraction": float(rtp_fraction),
            "actual_payout_multiplier": float(actual_payout_multiplier),
            "gross_return_multiplier": float(gross_return),
            "net_expected_value": float(net_ev),
            "economically_viable": is_economically_viable,
            "verdict": verdict,
        }

    @classmethod
    def evaluate_rare_event_target(
        cls,
        discovery_sequence: List[int],
        unseen_sequence: List[int],
        trigger_fn: Callable[[List[int]], bool],
        null_event_probability: float = 1e-4,  # e.g. 1 in 10,000 baseline
        payout_multiplier: float = 5000.0,     # e.g. 5,000x jackpot payout
    ) -> Dict[str, any]:
        """Evaluates a selective trigger strategy for rare events / jackpots.
        
        - Input sequences: 1 = Rare Event / Jackpot occurred, 0 = Standard Spin.
        - Trigger Function: trigger_fn(history) -> True (Bet / Trigger Signal), False (Skip).
        - Null Hypothesis (H0): When trigger_fn() == True, P(Event) = null_event_probability.
        - Alternative (H1): P(Event | Trigger) > null_event_probability.
        - Economic Return: Net EV = (Hits / Triggered_Bets) * payout_multiplier - 1.0.
        """
        n_unseen = len(unseen_sequence)
        history = list(discovery_sequence)
        
        triggered_count = 0
        hits = 0
        
        for actual in unseen_sequence:
            should_bet = trigger_fn(history)
            if should_bet:
                triggered_count += 1
                if actual == 1:
                    hits += 1
            history.append(actual)
            
        if triggered_count == 0:
            return {
                "unseen_sample_size": n_unseen,
                "triggered_bets": 0,
                "hits": 0,
                "triggered_hit_rate": 0.0,
                "null_event_probability": float(null_event_probability),
                "edge_over_null": 0.0,
                "binomial_p_value": 1.0,
                "statistically_significant": False,
                "payout_multiplier": float(payout_multiplier),
                "gross_return_multiplier": 0.0,
                "net_expected_value": -1.0,
                "economically_viable": False,
                "verdict": "NO_BETS_TRIGGERED",
                "notes": "Predictor never signaled to bet."
            }
            
        hit_rate = hits / float(triggered_count)
        
        # Exact Binomial Test on triggered bets vs null probability
        binom_res = stats.binomtest(hits, n=triggered_count, p=null_event_probability, alternative="greater")
        p_val = float(binom_res.pvalue)
        
        # Economic Return per triggered bet
        gross_return = hit_rate * payout_multiplier
        net_ev = gross_return - 1.0
        
        is_statistically_significant = bool(p_val < cls.ALPHA_THRESHOLD)
        is_economically_viable = bool(is_statistically_significant and net_ev > 0.0)
        
        verdict = "NO_PREDICTIVE_EDGE"
        if is_economically_viable:
            verdict = "REPRODUCIBLE_ECONOMIC_EDGE"
        elif is_statistically_significant:
            verdict = "STATISTICAL_STRUCTURE_WITHOUT_ECONOMIC_EDGE"
            
        return {
            "unseen_sample_size": n_unseen,
            "triggered_bets": triggered_count,
            "hits": hits,
            "triggered_hit_rate": float(hit_rate),
            "null_event_probability": float(null_event_probability),
            "edge_over_null": float(hit_rate - null_event_probability),
            "binomial_p_value": float(p_val),
            "statistically_significant": is_statistically_significant,
            "payout_multiplier": float(payout_multiplier),
            "gross_return_multiplier": float(gross_return),
            "net_expected_value": float(net_ev),
            "economically_viable": is_economically_viable,
            "verdict": verdict,
        }
