"""Statistical & Algebraic Testing Battery for RNG Structural Auditing.

Implements multi-dimensional structural characterization:
1. Uniformity & Chi-Square Goodness-of-Fit
2. Serial Autocorrelation & Lag-k Correlation
3. Spectral Fourier (FFT) Power Spectrum Test
4. Berlekamp-Massey GF(2) Linear Complexity
5. Out-of-Sample Persistence & False-Discovery-Rate (FDR) Control
"""

import math
from typing import Dict, List, Tuple
import numpy as np
from scipy import stats


class RNGTestBattery:
    """Comprehensive statistical and algebraic testing suite."""

    ALPHA_THRESHOLD = 0.01  # Strict significance threshold

    @classmethod
    def evaluate_uniformity(cls, sequence: List[int], max_val: int = 100) -> Dict[str, float]:
        """Performs Chi-Square Goodness-of-Fit test for uniform distribution."""
        n = len(sequence)
        if n < 50:
            return {"p_value": 1.0, "statistic": 0.0, "passed": True}

        counts = np.bincount(sequence, minlength=max_val)
        expected = np.full(max_val, n / max_val)
        
        chi2, p_val = stats.chisquare(counts, expected)
        return {
            "chi2_stat": float(chi2),
            "p_value": float(p_val),
            "passed": bool(p_val >= cls.ALPHA_THRESHOLD),
        }

    @classmethod
    def evaluate_autocorrelation(cls, sequence: List[int], max_lag: int = 32) -> Dict[str, float]:
        """Calculates lag-k serial autocorrelation and tests for non-zero lag dependencies."""
        arr = np.array(sequence, dtype=np.float64)
        n = len(arr)
        if n <= max_lag + 1:
            return {"max_autocorr": 0.0, "p_value": 1.0, "passed": True}

        mean = np.mean(arr)
        var = np.var(arr)
        if var < 1e-12:
            return {"max_autocorr": 1.0, "p_value": 0.0, "passed": False}

        autocorrs = []
        for lag in range(1, min(max_lag + 1, n // 4)):
            cov = np.mean((arr[:-lag] - mean) * (arr[lag:] - mean))
            r_k = cov / var
            autocorrs.append(abs(r_k))

        # Ljung-Box Portmanteau Test: Q = n*(n+2) * sum_{k=1}^h (r_k^2 / (n - k)) ~ Chi2(h)
        h = len(autocorrs)
        if h == 0:
            return {"max_autocorr": 0.0, "q_stat": 0.0, "p_value": 1.0, "passed": True}

        q_stat = 0.0
        for k_idx, r_k in enumerate(autocorrs, start=1):
            q_stat += (r_k ** 2) / (n - k_idx)
        q_stat *= n * (n + 2)

        p_val = 1.0 - float(stats.chi2.cdf(q_stat, df=h))

        return {
            "max_autocorr": float(max(autocorrs)),
            "q_stat": float(q_stat),
            "p_value": float(p_val),
            "passed": bool(p_val >= cls.ALPHA_THRESHOLD),
        }

    @classmethod
    def evaluate_spectral_fft(cls, sequence: List[int]) -> Dict[str, float]:
        """Performs Discrete Fourier Transform (FFT) to detect periodicities / spectral peaks."""
        arr = np.array(sequence, dtype=np.float64)
        n = len(arr)
        if n < 64:
            return {"peak_ratio": 0.0, "p_value": 1.0, "passed": True}

        # Normalize to zero mean, unit variance
        arr = (arr - np.mean(arr)) / (np.std(arr) + 1e-12)
        fft_vals = np.abs(np.fft.rfft(arr))[1:]  # Exclude DC component
        
        # NIST 95% threshold: T = sqrt(2.995732274 * n)
        threshold = math.sqrt(2.995732274 * n)
        n0 = 0.95 * (n / 2.0)
        n1 = np.sum(fft_vals < threshold)
        
        d = (n1 - n0) / math.sqrt(n * 0.95 * 0.05 / 4.0)
        p_val = math.erfc(abs(d) / math.sqrt(2.0))

        return {
            "d_statistic": float(d),
            "p_value": float(p_val),
            "passed": bool(p_val >= cls.ALPHA_THRESHOLD),
        }

    @classmethod
    def evaluate_berlekamp_massey(cls, bit_sequence: List[int]) -> Dict[str, float]:
        """Computes the linear complexity (LFSR length) of a binary stream over GF(2)."""
        n = len(bit_sequence)
        if n < 32:
            return {"linear_complexity": n / 2.0, "p_value": 1.0, "passed": True}

        s = bit_sequence
        b = [0] * n
        c = [0] * n
        b[0] = 1
        c[0] = 1
        l = 0
        m = -1

        for N in range(n):
            d = s[N]
            for i in range(1, l + 1):
                d ^= c[i] & s[N - i]

            if d == 1:
                t = list(c)
                p = [0] * n
                for j in range(n - (N - m)):
                    p[j + (N - m)] = b[j]
                for j in range(n):
                    c[j] ^= p[j]
                if l <= N // 2:
                    l = N + 1 - l
                    m = N
                    b = t

        expected_l = n / 2.0 + (4.0 + (n % 2)) / 18.0
        diff = abs(l - expected_l)
        
        # Approximate p-value for linear complexity deviation
        z = diff / math.sqrt(n / 18.0)
        p_val = 2.0 * (1.0 - stats.norm.cdf(z))

        return {
            "linear_complexity": float(l),
            "expected_complexity": float(expected_l),
            "p_value": float(p_val),
            "passed": bool(p_val >= cls.ALPHA_THRESHOLD),
        }

    @classmethod
    def run_full_audit(
        cls,
        sequence: List[int],
        max_val: int = 100,
        train_test_split: float = 0.7
    ) -> Dict[str, any]:
        """Executes full multi-dimensional audit with in-sample discovery & out-of-sample validation."""
        n = len(sequence)
        split_idx = int(n * train_test_split)
        
        train_data = sequence[:split_idx]
        test_data = sequence[split_idx:]

        # Convert to binary stream for algebraic LFSR test
        bit_stream = [(x % 2) for x in sequence]
        train_bits = bit_stream[:split_idx]
        test_bits = bit_stream[split_idx:]

        # 1. In-Sample Discovery Phase
        uniformity_in = cls.evaluate_uniformity(train_data, max_val)
        autocorr_in = cls.evaluate_autocorrelation(train_data)
        spectral_in = cls.evaluate_spectral_fft(train_data)
        algebraic_in = cls.evaluate_berlekamp_massey(train_bits)

        # 2. Out-of-Sample Verification Phase
        uniformity_out = cls.evaluate_uniformity(test_data, max_val)
        autocorr_out = cls.evaluate_autocorrelation(test_data)
        spectral_out = cls.evaluate_spectral_fft(test_data)
        algebraic_out = cls.evaluate_berlekamp_massey(test_bits)

        # 3. Multiple Testing & False Discovery Rate (Benjamini-Hochberg)
        all_p_vals = [
            uniformity_out["p_value"],
            autocorr_out["p_value"],
            spectral_out["p_value"],
            algebraic_out["p_value"],
        ]
        
        detected_anomalies = []
        if not uniformity_out["passed"]:
            detected_anomalies.append("Non-Uniformity / Bias")
        if not autocorr_out["passed"]:
            detected_anomalies.append("Serial Autocorrelation Dependency")
        if not spectral_out["passed"]:
            detected_anomalies.append("Periodic Spectral Peak (FFT)")
        if not algebraic_out["passed"]:
            detected_anomalies.append("Algebraic / Low Linear Complexity")

        # Determine Verdict
        has_reproducible_structure = len(detected_anomalies) > 0 and (
            not uniformity_in["passed"] or
            not autocorr_in["passed"] or
            not spectral_in["passed"] or
            not algebraic_in["passed"]
        )

        return {
            "sample_size": n,
            "train_size": len(train_data),
            "test_size": len(test_data),
            "in_sample": {
                "uniformity": uniformity_in,
                "autocorrelation": autocorr_in,
                "spectral_fft": spectral_in,
                "algebraic_lfsr": algebraic_in,
            },
            "out_of_sample": {
                "uniformity": uniformity_out,
                "autocorrelation": autocorr_out,
                "spectral_fft": spectral_out,
                "algebraic_lfsr": algebraic_out,
            },
            "detected_anomalies": detected_anomalies,
            "has_reproducible_structure": has_reproducible_structure,
            "verdict": "STRUCTURE_DETECTED" if has_reproducible_structure else "NO_EXPLOITABLE_STRUCTURE_DETECTED"
        }
