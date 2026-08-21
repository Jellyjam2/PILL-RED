# 🔴 PILL RED RNG Structural Audit Protocol (Track 2)

**Document Version:** `2.0.0-alpha.1`  
**Standard:** Rigorous Out-of-Sample Hypothesis Validation & House-Edge Accounting  
**Epistemic Rule:** Statistical anomalies do NOT imply economic exploits; a certified CSPRNG null result is a successful audit finding.

---

## 🏛️ 1. Core Principles & Philosophy

The PILL RED RNG Structural Audit Engine evaluates whether an observed data stream contains reproducible non-linear, algebraic, or statistical structure.

```
                           OBSERVED DATA STREAM
                                    │
                                    ▼
                     [STEP 1: IN-SAMPLE DISCOVERY]
                     • Sample split: N_train (e.g. 70%)
                     • Multi-battery screening:
                       - Chi-Square Uniformity
                       - Ljung-Box Serial Autocorrelation
                       - Spectral Fourier (FFT) Power Peaks
                       - Berlekamp-Massey GF(2) Linear Complexity
                                    │
                                    ▼
                     [STEP 2: HYPOTHESIS FREEZING]
                     • Exact mathematical predictor / anomaly locked
                     • No further hyperparameter tuning permitted
                                    │
                                    ▼
                 [STEP 3: OUT-OF-SAMPLE VALIDATION]
                 • Tested on N_test unseen observations (e.g. 30%)
                 • Exact Binomial Test vs. random baseline (p < 0.01)
                 • Multi-session / timestamp replication
                                    │
                     ┌──────────────┴──────────────┐
                     ▼                             ▼
        [STATISTICAL ANOMALY CONFIRMED]   [NULL RESULT: NO STRUCTURE]
                     │                    Stream behaves as unpredictable
                     ▼                    noise (CSPRNG / Certified)
      [STEP 4: ECONOMIC ACCOUNTING]
      • Calculate Net Expected Value (EV):
        Net EV = Hit Rate * [Alphabet Size * (1 - House Edge)] - 1.0
      • Distinction:
        - Statistical Structure != Profitable Exploit
        - House edge often absorbs statistical non-uniformities
```

---

## 🔬 2. The 6-Step Audit Pipeline

### Step 1: Passive Observation & Causal Integrity
Data must be logged passively without altering or interfering with the source system. Records must follow the standardized `SpinRecord` schema (timestamp, game title, session ID, spin index, outcome symbols, payout multiplier).

### Step 2: In-Sample Multi-Battery Discovery
The discovery phase evaluates $N_{\text{train}}$ historical samples across:
* **Uniformity:** $\chi^2$ test against theoretical symbol frequencies.
* **Serial Autocorrelation:** Ljung-Box $Q$-statistic over lags $1 \dots 32$ ($Q \sim \chi^2(h)$).
* **Spectral Periodicity:** Discrete Fourier Transform power spectrum to detect hidden periodic cycles.
* **Algebraic Complexity:** Berlekamp-Massey LFSR length over $\mathbb{F}_2$.

### Step 3: Formal Hypothesis Freezing
If a structural anomaly is identified in-sample, the exact mathematical rule or recurrence relation is **frozen in code** before inspecting out-of-sample data.

### Step 4: Out-of-Sample Replication ($\alpha = 0.01$)
The frozen hypothesis is evaluated on $N_{\text{test}}$ completely unseen observations. The predictor must achieve a statistically significant hit rate above random chance under the exact one-tailed Binomial test ($p < 0.01$).

### Step 5: Statistical vs. Economic Significance Separation
A statistically detectable pattern (e.g. a $0.5\%$ frequency bias) does not automatically generate positive expected value ($+EV$) if the game has a $4.0\%$ house edge (e.g. $96\%$ RTP). The audit engine explicitly computes:
$$\text{Net EV} = \text{Hit Rate} \times \big(\text{Alphabet Size} \times (1 - \text{House Edge})\big) - 1.0$$
* **`STATISTICAL_STRUCTURE_WITHOUT_ECONOMIC_EDGE`**: Pattern is real ($p < 0.01$), but Net EV $\le 0$.
* **`REPRODUCIBLE_ECONOMIC_EDGE`**: Pattern is real ($p < 0.01$) AND Net EV $> 0$.

### Step 6: Multi-Session Independent Replication
Any finding must be independently replicated across separate sessions, different days/times, and distinct device contexts before any permanent claim is recorded.

---

## 🎯 3. Commercial & Industrial Applications

1. **RNG Compliance Auditing:** Validating gaming and lottery RNGs against GLI-19 and NIST SP 800-22 standards.
2. **Simulation & Monte Carlo QA:** Verifying that synthetic random variables in financial or physics simulations do not suffer from low-degree algebraic artifacts.
3. **Software & Game Engine Testing:** Detecting unintended state-looping or seed collisions in procedural generation systems.
4. **Security & Cryptographic Review:** Identifying weak PRNG implementations in authentication tokens or session identifiers.
