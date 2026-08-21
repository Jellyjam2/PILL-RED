# ⚠️ PILL RED v1.0.0 BOUNDARIES, LIMITATIONS & NON-CLAIMS

> **Epistemic Principle:** Explicitly define the boundaries of what the protocol guarantees and what it cannot guarantee.

---

## 1. What PILL RED Guarantees (The Evidence Layer)

1. **Pre-Commitment Integrity:** Mathematical proof that a specific prediction string, confidence level, and model ID existed prior to event settlement.
2. **Deterministic Settlement:** Verification that scoring (`is_hit`), payouts, and gross returns match observed ground truth.
3. **Sequential Hash Immutability:** Mathematical detection if any receipt in a historical sequence was modified, inserted, deleted, or backdated.
4. **Honest Null-Model Evaluation:** Performance metrics evaluated against majority-class, zero-information, and dependence-aware null baselines.
5. **No Double-Counting:** Active capital risks and avoided loss benefits remain permanently segregated.

---

## 2. What PILL RED Does NOT Guarantee (Non-Claims)

1. **Future Profitability / Stationarity:**
   * A verified Passport proving positive historical edge in past episodes does **NOT** guarantee future edge. Regimes change, markets adapt, and non-stationary processes evolve.
2. **Oracle Ground Truth Correctness:**
   * PILL RED verifies what the data provider/oracle recorded. If the oracle feed itself is dishonest or compromised, PILL RED cannot magically divine true physical reality.
3. **Model Source Code Quality:**
   * The protocol treats the predictive model as a black box. It does not inspect weights, training sets, or architecture—only commitments and outcomes.
4. **Zero-Latency Network Guarantees:**
   * In ultra-high-frequency environments, network transmission latency between client and timestamp authority must be accounted for within the pre-commitment buffer.

---

## 3. Four-State Classification Rules

PILL RED verifiers and Passports must strictly uphold the four-state taxonomy:
* **`VERIFIED`**: Provenance is intact.
* **`MEASURED`**: Data points calculated directly.
* **`INFERRED`**: Statistical bounds computed under null hypothesis.
* **`NOT PROVEN`**: Null hypothesis cannot be rejected with $p < 0.01$.

The term `PROVEN PREDICTIVE EDGE` must never be outputted unless both statistical significance ($p < 0.01$) and economic edge after friction are empirically established on a validated sample size ($N \ge 30$).
