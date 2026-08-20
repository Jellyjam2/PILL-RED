"""Multi-Session Blinded Audit & Pre-Registered Hypothesis Harness.

Enforces strict causal separation between discovery sessions and evaluation sessions:
1. In-Sample Model Discovery (Session 1)
2. Pre-Registration / Model Freezing (Locking predictor rule)
3. Blinded Out-of-Sample Testing (Session 2)
4. Multi-Day Independent Replication (Session 3+)
5. Exact Binomial Significance + Wilson 99% Confidence Interval
6. Formal Audit Report Generation
"""

import math
import time
from typing import Callable, Dict, List, Optional, Tuple
import numpy as np
from scipy import stats

from rng_audit.collectors.schema import SpinRecord
from rng_audit.statistics.battery import RNGTestBattery
from rng_audit.statistics.predictor import PredictiveHypothesisTester


class MultiSessionAuditor:
    """Orchestrates multi-session blinded auditing with pre-registered hypothesis locking."""

    ALPHA_THRESHOLD = 0.01

    @classmethod
    def compute_wilson_score_interval(cls, hits: int, n: int, confidence: float = 0.99) -> Tuple[float, float]:
        """Calculates exact Wilson score confidence interval for binomial proportion."""
        if n == 0:
            return 0.0, 1.0
        z = stats.norm.ppf(1.0 - (1.0 - confidence) / 2.0)
        p_hat = hits / float(n)
        denominator = 1.0 + (z**2) / n
        center = (p_hat + (z**2) / (2.0 * n)) / denominator
        spread = (z / denominator) * math.sqrt((p_hat * (1.0 - p_hat) / n) + (z**2) / (4.0 * (n**2)))
        lower = max(0.0, center - spread)
        upper = min(1.0, center + spread)
        return float(lower), float(upper)

    @classmethod
    def audit_game_sessions(
        cls,
        discovery_records: List[SpinRecord],
        validation_records: List[SpinRecord],
        replication_records: Optional[List[SpinRecord]] = None,
        alphabet_size: int = 10,
        house_edge_fraction: float = 0.04  # 96% RTP
    ) -> Dict[str, any]:
        """Executes full 3-phase blinded multi-session audit."""
        
        # 1. Extract observation sequences
        disc_seq = [r.outcome_symbols[0] if r.outcome_symbols else int(r.payout_multiplier) for r in discovery_records]
        val_seq = [r.outcome_symbols[0] if r.outcome_symbols else int(r.payout_multiplier) for r in validation_records]
        
        # 2. Phase 1: In-Sample Discovery on Session 1
        disc_audit = RNGTestBattery.run_full_audit(disc_seq, max_val=alphabet_size)
        
        # 3. Phase 2: Build and Lock Pre-Registered Candidate Predictor
        # Candidate model: 1st-order empirical Markov transition matrix
        trans_matrix = np.zeros((alphabet_size, alphabet_size), dtype=np.float64)
        for i in range(len(disc_seq) - 1):
            s_curr, s_next = disc_seq[i] % alphabet_size, disc_seq[i+1] % alphabet_size
            trans_matrix[s_curr, s_next] += 1.0
        
        # Normalize rows to transition probabilities
        row_sums = trans_matrix.sum(axis=1, keepdims=True)
        # Avoid div by zero: fallback to uniform
        trans_probs = np.where(row_sums > 0, trans_matrix / np.maximum(row_sums, 1e-12), 1.0 / alphabet_size)

        # Frozen predictor: argmax over transition probabilities given last state
        def locked_predictor_fn(history: List[int]) -> int:
            if not history:
                return 0
            last_state = history[-1] % alphabet_size
            return int(np.argmax(trans_probs[last_state]))

        # 4. Phase 3: Out-of-Sample Evaluation on Session 2 (Strictly Unseen)
        val_result = PredictiveHypothesisTester.evaluate_predictive_edge(
            discovery_sequence=disc_seq,
            unseen_sequence=val_seq,
            predictor_fn=locked_predictor_fn,
            alphabet_size=alphabet_size,
            house_edge_fraction=house_edge_fraction
        )

        ci_low, ci_high = cls.compute_wilson_score_interval(
            hits=val_result["hits"],
            n=val_result["unseen_sample_size"],
            confidence=0.99
        )

        # 5. Phase 4: Optional Replication on Session 3 (Different Day/Time)
        rep_result = None
        if replication_records and len(replication_records) >= 50:
            rep_seq = [r.outcome_symbols[0] if r.outcome_symbols else int(r.payout_multiplier) for r in replication_records]
            rep_result = PredictiveHypothesisTester.evaluate_predictive_edge(
                discovery_sequence=disc_seq + val_seq,
                unseen_sequence=rep_seq,
                predictor_fn=locked_predictor_fn,
                alphabet_size=alphabet_size,
                house_edge_fraction=house_edge_fraction
            )

        # 6. Synthesize Epistemic Verdict
        if not val_result["statistically_significant"]:
            if disc_audit["has_reproducible_structure"]:
                verdict = "SPURIOUS_OVERFITTING_REJECTED"
                rationale = "In-sample pattern failed to replicate out-of-sample (p >= 0.01). Observation consistent with noise."
            else:
                verdict = "NULL_MODEL_CONFIRMED"
                rationale = "No in-sample or out-of-sample deviation detected. Stream adheres to random null model."
        else:
            if val_result["economically_viable"]:
                verdict = "REPRODUCIBLE_ECONOMIC_EDGE"
                rationale = f"Statistically significant predictive edge (p = {val_result['binomial_p_value']:.4e}) exceeds house edge barrier."
            else:
                verdict = "STATISTICAL_STRUCTURE_WITHOUT_ECONOMIC_EDGE"
                rationale = f"Statistically significant pattern (p = {val_result['binomial_p_value']:.4e}) is absorbed by the {house_edge_fraction*100:.1f}% house edge."

        return {
            "game_title": discovery_records[0].game_title if discovery_records else "Unknown",
            "discovery_samples": len(disc_seq),
            "validation_samples": len(val_seq),
            "replication_samples": len(replication_records) if replication_records else 0,
            "alphabet_size": alphabet_size,
            "baseline_null_rate": val_result["baseline_null_rate"],
            "validation_hit_rate": val_result["observed_hit_rate"],
            "wilson_ci_99": (ci_low, ci_high),
            "binomial_p_value": val_result["binomial_p_value"],
            "statistically_significant": val_result["statistically_significant"],
            "net_expected_value": val_result["net_expected_value"],
            "economically_viable": val_result["economically_viable"],
            "verdict": verdict,
            "rationale": rationale,
            "in_sample_audit": disc_audit,
            "replication_result": rep_result,
        }
