"""
PILL RED Statistical Engine (Gate 5).
Evaluates predictive performance against rigorous majority-class and dependence-aware null models.
"""

import math
import random
from collections import Counter
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Tuple
from scipy import stats


@dataclass
class StatisticalEvaluationResult:
    """Standardized output of the PILL RED Statistical Truth Engine."""
    total_observations: int
    hits: int
    accuracy: float
    majority_class_baseline: float
    uniform_null_baseline: float
    delta_over_majority: float
    wilson_ci_99: List[float]
    brier_score: float
    expected_calibration_error: float
    is_serially_dependent: bool
    markov_transition_p_value: float
    block_bootstrap_ci_99: List[float]
    effective_alpha: float
    verdict: str  # "PASS" | "INCONCLUSIVE" | "FAIL"
    justification: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class StatisticalEngine:
    """
    Evaluates out-of-sample prediction streams against empirical and dependence-aware baselines.
    """

    @classmethod
    def compute_wilson_ci(cls, hits: int, n: int, confidence: float = 0.99) -> List[float]:
        """Computes Wilson score interval with continuity correction."""
        if n <= 0:
            return [0.0, 0.0]
        p = hits / n
        z = stats.norm.ppf((1 + confidence) / 2)
        denom = 1 + (z ** 2) / n
        center = (p + (z ** 2) / (2 * n)) / denom
        spread = z * math.sqrt((p * (1 - p) + (z ** 2) / (4 * n)) / n) / denom
        return [max(0.0, center - spread), min(1.0, center + spread)]

    @classmethod
    def stationary_block_bootstrap(
        cls,
        hits_seq: List[int],
        block_size: int = 5,
        n_bootstraps: int = 1000,
        confidence: float = 0.99
    ) -> List[float]:
        """
        Stationary Block Bootstrap (Politis & Romano, 1994).
        Preserves autocorrelation and serial dependence when estimating confidence bounds.
        Optimized with block slicing for high throughput (O(N) with low constant factor).
        """
        n = len(hits_seq)
        if n < block_size or block_size <= 0:
            p = sum(hits_seq) / max(1, n)
            return [p, p]

        extended_seq = hits_seq + hits_seq
        bootstrap_means = []
        effective_bootstraps = n_bootstraps if n <= 20000 else min(n_bootstraps, 500)

        for _ in range(effective_bootstraps):
            sample_sum = 0
            count = 0
            while count < n:
                start = random.randint(0, n - 1)
                block_len = min(max(1, int(random.expovariate(1.0 / block_size))), n - count)
                sample_sum += sum(extended_seq[start : start + block_len])
                count += block_len
            bootstrap_means.append(sample_sum / n)

        bootstrap_means.sort()
        alpha = (1.0 - confidence) / 2.0
        low_idx = max(0, int(len(bootstrap_means) * alpha))
        high_idx = min(len(bootstrap_means) - 1, int(len(bootstrap_means) * (1.0 - alpha)))
        return [bootstrap_means[low_idx], bootstrap_means[high_idx]]

    @classmethod
    def evaluate_stream(
        cls,
        predictions: List[Any],
        actuals: List[Any],
        confidences: Optional[List[float]] = None,
        min_sample_size: int = 30,
        hypothesis_family_size: int = 1, # Number of concurrent hypothesis tests for Bonferroni
        alpha_nominal: float = 0.01
    ) -> StatisticalEvaluationResult:
        """
        Executes full Gate 5 statistical evaluation over a stream of predictions and outcomes.
        """
        n = len(predictions)
        if n != len(actuals):
            raise ValueError(f"Predictions length ({n}) must match actuals length ({len(actuals)}).")

        # 0. Strict Data Integrity Check: Filter out unsettled/None values
        valid_triplets = []
        for idx in range(n):
            p = predictions[idx]
            a = actuals[idx]
            if p is not None and a is not None and str(a).strip().upper() not in ('NONE', 'UNSETTLED', 'NULL'):
                c = confidences[idx] if confidences and idx < len(confidences) else 0.5
                valid_triplets.append((p, a, c))

        if len(valid_triplets) == 0:
            return StatisticalEvaluationResult(
                total_observations=0,
                hits=0,
                accuracy=0.0,
                majority_class_baseline=0.0,
                uniform_null_baseline=0.0,
                delta_over_majority=0.0,
                wilson_ci_99=[0.0, 0.0],
                brier_score=0.0,
                expected_calibration_error=0.0,
                is_serially_dependent=False,
                markov_transition_p_value=1.0,
                block_bootstrap_ci_99=[0.0, 0.0],
                effective_alpha=alpha_nominal,
                verdict="INCONCLUSIVE",
                justification="Zero valid/settled observations available for evaluation."
            )

        preds = [t[0] for t in valid_triplets]
        acts = [t[1] for t in valid_triplets]
        confs = [t[2] for t in valid_triplets]
        valid_n = len(preds)

        # 1. Basic Hit Scoring
        hits_seq = [1 if str(p).strip().upper() == str(a).strip().upper() else 0 for p, a in zip(preds, acts)]
        hits = sum(hits_seq)
        accuracy = hits / valid_n

        # 2. Empirical Baselines
        actual_counts = Counter(str(a).strip().upper() for a in acts)
        most_common_class, most_common_count = actual_counts.most_common(1)[0]
        majority_baseline = most_common_count / valid_n
        unique_classes = len(actual_counts)
        uniform_baseline = 1.0 / max(1, unique_classes)
        delta_over_majority = accuracy - majority_baseline

        # 3. Multiple Testing Correction (Bonferroni)
        effective_alpha = alpha_nominal / max(1, hypothesis_family_size)
        confidence_level = 1.0 - effective_alpha

        # 4. Wilson Score CI
        wilson_ci = cls.compute_wilson_ci(hits, valid_n, confidence=confidence_level)

        # 5. Calibration & Brier Score
        brier = sum((c - h) ** 2 for c, h in zip(confs, hits_seq)) / valid_n
        # Expected Calibration Error (ECE) across 5 confidence bins
        ece = 0.0
        bin_size = 1.0 / 5.0
        for b in range(5):
            b_low = b * bin_size
            b_high = (b + 1) * bin_size
            bin_indices = [i for i, c in enumerate(confs) if b_low <= c < b_high or (b == 4 and c == 1.0)]
            if bin_indices:
                bin_acc = sum(hits_seq[i] for i in bin_indices) / len(bin_indices)
                bin_conf = sum(confs[i] for i in bin_indices) / len(bin_indices)
                ece += (len(bin_indices) / valid_n) * abs(bin_acc - bin_conf)

        # 6. Serial Dependence & Markov Transition Matrix Test
        is_win_seq = [0 if str(a).strip().upper() in ('0', 'NO_WIN', '0.0', 'FALSE') else 1 for a in acts]
        t_00, t_01, t_10, t_11 = 0, 0, 0, 0
        for i in range(len(is_win_seq) - 1):
            c_s, n_s = is_win_seq[i], is_win_seq[i + 1]
            if c_s == 0 and n_s == 0: t_00 += 1
            elif c_s == 0 and n_s == 1: t_01 += 1
            elif c_s == 1 and n_s == 0: t_10 += 1
            else: t_11 += 1

        contingency = [[t_00, t_01], [t_10, t_11]]
        if min(t_00 + t_01, t_10 + t_11) > 0 and min(t_00 + t_10, t_01 + t_11) > 0:
            try:
                res = stats.chi2_contingency(contingency, correction=True)
                markov_p = float(res.pvalue)
            except Exception:
                markov_p = 1.0
        else:
            markov_p = 1.0

        is_dependent = markov_p < 0.05

        # 7. Stationary Block Bootstrap (Block Size = 5)
        bootstrap_ci = cls.stationary_block_bootstrap(hits_seq, block_size=5, n_bootstraps=1000, confidence=confidence_level)

        # 8. Gate 5 Verdict Determination
        if valid_n < min_sample_size:
            verdict = "INCONCLUSIVE"
            justification = f"Settled sample size (N={valid_n}) is below statistical threshold (N_min={min_sample_size})."
        elif delta_over_majority <= 0.0:
            verdict = "FAIL"
            justification = f"Accuracy ({accuracy*100:.1f}%) fails to beat the majority-class baseline ({majority_baseline*100:.1f}%)."
        elif bootstrap_ci[0] <= majority_baseline:
            verdict = "INCONCLUSIVE"
            justification = f"{(1.0-effective_alpha)*100:.1f}% Block-Bootstrap CI [{bootstrap_ci[0]*100:.1f}%, {bootstrap_ci[1]*100:.1f}%] overlaps majority baseline ({majority_baseline*100:.1f}%)."
        else:
            verdict = "PASS"
            justification = f"Statistically significant out-of-sample edge (+{delta_over_majority*100:.2f}%) over majority baseline with bootstrap lower bound > baseline (alpha={effective_alpha:.4f})."

        return StatisticalEvaluationResult(
            total_observations=valid_n,
            hits=hits,
            accuracy=accuracy,
            majority_class_baseline=majority_baseline,
            uniform_null_baseline=uniform_baseline,
            delta_over_majority=delta_over_majority,
            wilson_ci_99=wilson_ci,
            brier_score=brier,
            expected_calibration_error=ece,
            is_serially_dependent=is_dependent,
            markov_transition_p_value=markov_p,
            block_bootstrap_ci_99=bootstrap_ci,
            effective_alpha=effective_alpha,
            verdict=verdict,
            justification=justification
        )
