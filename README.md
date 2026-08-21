# 💊 PILL RED (v1.0.0)

[![Protocol](https://img.shields.io/badge/Protocol-PILLRED--SPEC--1.0-red.svg)](docs/PILLRED_SPEC_1.0.md)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Master_Suite-54%2F54_PASS-brightgreen.svg)]()
[![Zero-Trust](https://img.shields.io/badge/Zero--Trust-Offline_Verified-success.svg)]()

> **The Universal Cryptographic Evidence & Model Audit Protocol.**  
> *Before something happens, the system forces a model to put its prediction on the record. Then reality happens. PILL RED keeps the receipt.*

---

## ⚡ Key Guarantees

* **Zero-Hindsight Provenance:** Cryptographically binds predictions strictly prior to event revelation ($t_{\text{commit}} < t_{\text{event}} \le t_{\text{resolve}}$).
* **Adversarial Tamper Detection:** Post-hoc score inflation, retroactive bet alteration, or backdating breaks deterministic SHA-256 / JCS hashes.
* **Separation of Concerns:**
  * **Cryptography** proves the receipt.
  * **Statistics** evaluates the claim against null baselines.
  * **Economics** audits active P/L and capital preservation without double-counting.
* **Model Audit Passport:** Immutable evidence aggregation layer producing honest 4-state evidentiary classifications: `VERIFIED`, `MEASURED`, `INFERRED`, `NOT PROVEN`.
* **Zero-Trust Offline Verifier:** Audits evidence without connecting to any central server.

---

## 🚀 Quickstart

### 1. Installation
```bash
pip install pillred
```

### 2. Basic Python Usage
```python
import pillred

# 1. COMMIT: Lock prediction before reality is revealed
receipt = pillred.commit(
    model_id="ALPHA_FORECAST_V1",
    target_event="NASDAQ_CLOSE_2026_08_22",
    prediction="UP",
    confidence=0.82
)
print(f"Committed! Receipt ID: {receipt.receipt_id} | Hash: {receipt.commit_hash[:16]}...")

# 2. OBSERVE REALITY & SETTLE
receipt = pillred.resolve(
    receipt_id=receipt.receipt_id,
    actual_outcome="UP",
    payout_multiplier=2.0
)
print(f"Settled! Receipt Hash: {receipt.receipt_hash[:16]}... | Hit: {receipt.is_hit}")

# 3. GET SEALED MODEL AUDIT PASSPORT
passport = pillred.get_passport(target_domain="FINANCIAL_MARKETS")
print(f"Passport Seal: {passport.passport_hash}")
print(f"Provenance Status: {passport.evidentiary_conclusions.provenance}")
print(f"Statistical Edge:  {passport.evidentiary_conclusions.statistical_claim}")
print(f"Economic Edge:     {passport.evidentiary_conclusions.economic_claim}")
```

---

## 🔍 Public Offline Verifier (CLI)

Anyone can independently verify any PILL RED artifact without network access:

```bash
# Verify a single receipt
pillred verify receipt.json

# Verify an entire historical chain
pillred verify chain.json

# Verify a Model Audit Passport
pillred verify passport.json
```

### Example Terminal Output:
```text
======================================================================
               PILL RED PUBLIC OFFLINE VERIFIER
                       PILLRED-SPEC-1.0
======================================================================
Target File:  passport.json
Target Type:  MODEL AUDIT PASSPORT (PASS-VEC-001)
Model:        MOD-BENCHMARK-V1 (v1.0.0) | Domain: RNG_SLOT_BENCHMARK

Provenance ............. VERIFIED (3 Receipts)
Temporal Integrity ..... VERIFIED (t_commit < t_event <= t_resolve)
Chain Integrity ........ VERIFIED (Intact Sequential Hashes)
Merkle Root ............ VERIFIED (0x6ee549c59a40bc8a...)
Statistical Evidence ... MEASURED / NOT PROVEN (Acc: 66.7%, Δ: +0.0%, p: 1.0000)
Economic Evidence ...... MEASURED / INCONCLUSIVE (Net PnL: +$17.00, ROI: +850.0%)
Passport Seal .......... VERIFIED (0x77d11e283dfe26e3...391caaf749b5c35b)
----------------------------------------------------------------------
OVERALL VERDICT: EVIDENCE_PRESERVED (PROVENANCE: VERIFIED)
```

---

## 🏛️ Architecture & Verification Pipeline

```
               PRE-EVENT                        POST-EVENT
        ┌─────────────────────┐          ┌─────────────────────┐
        │  Model Prediction   │          │ Real-World Outcome  │
        └──────────┬──────────┘          └──────────┬──────────┘
                   │                                │
                   ▼                                ▼
        ┌─────────────────────┐          ┌─────────────────────┐
        │ Immutable Commit    │ ───────► │ Deterministic Settle│
        │ Hcommit = SHA256    │          │ Hreceipt = SHA256   │
        └─────────────────────┘          └──────────┬──────────┘
                                                    │
                                                    ▼
                                         ┌─────────────────────┐
                                         │  Sequential Chain   │
                                         │  & Merkle Root Tree │
                                         └──────────┬──────────┘
                                                    │
                                 ┌──────────────────┴──────────────────┐
                                 ▼                                     ▼
                      ┌─────────────────────┐               ┌─────────────────────┐
                      │ Statistical Engine  │               │   Economic Engine   │
                      │  • Wilson 99% CI    │               │  • Active Wager PnL │
                      │  • Block Bootstrap  │               │  • Avoided Loss     │
                      │  • Bonferroni Multi │               │  • High-Water DD    │
                      └──────────┬──────────┘               └──────────┬──────────┘
                                 │                                     │
                                 └──────────────────┬──────────────────┘
                                                    │
                                                    ▼
                                      ┌───────────────────────────┐
                                      │   MODEL AUDIT PASSPORT    │
                                      │   Hpassport = SHA256(...) │
                                      └───────────────────────────┘
```

---

## 🧪 Specification & Documentation

* [PILLRED-SPEC-1.0 (Core Cryptographic Protocol)](docs/PILLRED_SPEC_1.0.md)
* [Statistical & Economic Truth Specification](docs/PILLRED_STATISTICAL_AND_ECONOMIC_SPEC.md)
* [High-Throughput Stress & Fault Recovery Specification](docs/PILLRED_STRESS_AND_RECOVERY_SPEC.md)
* [Cross-Language External Test Vector Manifest](test_vectors/expected/test_vector_manifest.json)
