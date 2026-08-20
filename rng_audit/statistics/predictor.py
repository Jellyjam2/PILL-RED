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
        # Expected payout multiplier for fair single-pick is alphabet_size
        gross_return = hit_rate * alphabet_size
        net_ev = gross_return - (1.0 + house_edge_fraction)

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
            "gross_return_multiplier": float(gross_return),
            "net_expected_value": float(net_ev),
            "economically_viable": is_economically_viable,
            "verdict": verdict,
        }
