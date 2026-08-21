# 🔬 PILL RED Scientific & Economic Specification

> **Document Status:** SEALED & AUDITED  
> **Version:** `1.0.0`  
> **Pre-requisite:** [PILLRED-SPEC-1.0](file:///C:/PILL%20RED/docs/PILLRED_SPEC_1.0.md)  

---

## 1. The Epistemic Separation Principle

PILL RED enforces a hard epistemic barrier between **Cryptographic Provenance**, **Statistical Inference**, and **Economic Utility**:

```
                         THE TRI-LAYER BOUNDARY
   ┌──────────────────────────────────────────────────────────────────┐
   │ 1. CRYPTOGRAPHIC PROVENANCE                                      │
   │    • Was the claim committed before reality?                     │
   │    • Output: VERIFIED (Intact SHA-256 hashes, temporal order)    │
   ├──────────────────────────────────────────────────────────────────┤
   │ 2. STATISTICAL INFERENCE                                         │
   │    • Does the performance reject an appropriate null model?      │
   │    • Output: INFERRED (p-values, bootstrap CI, delta baseline)   │
   ├──────────────────────────────────────────────────────────────────┤
   │ 3. ECONOMIC REALIZATION                                          │
   │    • Does the edge create or preserve capital after friction?    │
   │    • Output: MEASURED (Net P/L, avoided loss, max drawdown)      │
   └──────────────────────────────────────────────────────────────────┘
```

---

## 2. Statistical Engine Invariants (Gate 5)

### 2.1 Empirical Baselines
A model cannot claim predictive power unless it outperforms two distinct baselines:
1. **Majority-Class Zero-Rule Null ($B_{\text{maj}}$):**
   $$B_{\text{maj}} = \frac{\max_{k} \text{Count}(c_k)}{N}$$
   If a stream has $70\%$ non-paying spins (`0`), predicting `0` gives $70\%$ accuracy, but $\Delta_{\text{maj}} = 0.00\% \implies \text{FAIL}$.
2. **Uniform Null ($B_{\text{unif}}$):**
   $$B_{\text{unif}} = \frac{1}{K} \quad (K = \text{Unique Outcome Classes})$$

### 2.2 Stationary Block Bootstrap (Politis & Romano, 1994)
To account for serial autocorrelation and dependence in game/market streams, confidence bounds are calculated by resampling blocks of random geometric length:
* Mean block length: $L = 5$ events
* Block length $B \sim \text{Geometric}(1/L)$
* Bootstrap iterations: $M = 1000$
* **Invariant:** If the $99\%$ Block-Bootstrap lower bound $\le B_{\text{maj}}$, the result is classified as `INCONCLUSIVE` or `FAIL`.

### 2.3 Markov Transition Matrix $\chi^2$ Test
Tests for 1st-order serial dependence across consecutive events:
$$C = \begin{bmatrix} N_{0 \to 0} & N_{0 \to 1} \\ N_{1 \to 0} & N_{1 \to 1} \end{bmatrix}$$
* $\chi^2$ test of independence with Yates' continuity correction.
* If $p < 0.05$, the sequence is marked `is_serially_dependent = True`, triggering mandatory dependence-aware intervals.

### 2.4 Multiple-Testing P-Hacking Defense
When a model queries a family of $K$ target hypotheses simultaneously, the nominal significance level ($\alpha = 0.01$) is Bonferroni-adjusted:
$$\alpha_{\text{effective}} = \frac{\alpha_{\text{nominal}}}{K}$$

---

## 3. Economic Engine Invariants (Gate 6)

### 3.1 Strict Ledger Independence (Zero Double-Counting)

#### Active Wager Ledger:
* **Total Stake:** $S = \sum_{i \in \text{Active}} s_i$
* **Gross Return:** $G = \sum_{i \in \text{Active}} s_i \cdot m_i \cdot \mathbb{I}(p_i = a_i)$
* **Friction / House Edge Drag:** $F = S \cdot \mu_{\text{friction}}$
* **Net Realized P/L:** $\Pi_{\text{net}} = (G - S) - F$
* **ROI %:** $\frac{\Pi_{\text{net}}}{S} \times 100\%$

#### Avoided Loss Ledger:
* **Capital Preserved:** $C_{\text{pres}} = \sum_{i \in \text{Skipped}, a_i = 0} s_i$
* **Missed Profit (Opportunity Cost):** $O_{\text{miss}} = \sum_{i \in \text{Skipped}, a_i \ne 0} (s_i \cdot m_i - s_i)$
* **Net Preservation Benefit:** $B_{\text{pres}} = C_{\text{pres}} - O_{\text{miss}}$

> **Anti-Double-Counting Invariant:** Avoided loss $C_{\text{pres}}$ is recorded strictly as *Capital Preserved* and is NEVER added into Net Realized P/L $\Pi_{\text{net}}$.

### 3.2 High-Water Mark Drawdown Tracking
* Peak Bankroll at step $t$: $\text{Peak}_t = \max_{0 \le \tau \le t} W_\tau$
* $\text{DrawdownUnits} = \max_t (\text{Peak}_t - W_t)$
* $\text{DrawdownPct} = \max_t \left( \frac{\text{Peak}_t - W_t}{\text{Peak}_t} \right)$
* **Invariant:** An active strategy with $\text{DrawdownPct} \ge 50\%$ is stamped `FAIL` regardless of positive gross returns.

---

## 4. The 4-State Evidentiary Vocabulary

Every PILL RED Audit Passport divides statements into four non-overlapping categories:

| Tag | Definition | Example Claim |
| :--- | :--- | :--- |
| **`VERIFIED`** | Proven cryptographically without server trust. | *“Prediction hash committed at $t=1700000000$, strictly prior to event at $t=1700000005$.”* |
| **`MEASURED`** | Directly calculated from observed historical telemetry. | *“Net active P/L after $4\%$ friction was $-\text{R52.00}$; Capital preserved was $+\text{R350.00}$.”* |
| **`INFERRED`** | Statistical conclusion supported under stated null model. | *“Reject null hypothesis of serial independence ($p = 0.002$ under Markov transition test).”* |
| **`NOT PROVEN`** | Hypotheses rejected or under-powered. | *“Positive expected value under active betting is NOT PROVEN ($N_{\text{active}} = 0$).”* |
