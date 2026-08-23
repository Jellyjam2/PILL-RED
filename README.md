# 💊 PILL RED (v1.0.0)

[![Protocol](https://img.shields.io/badge/Protocol-PILLRED--SPEC--1.0-red.svg)](docs/PILLRED_SPEC_1.0.md)
[![Release](https://img.shields.io/badge/Release-v1.0.0-blue.svg)](https://github.com/Jellyjam2/PILL-RED/releases)
[![Tests](https://img.shields.io/badge/Master_Suite-67%2F67_PASS-brightgreen.svg)](tests/)
[![Python ↔ Rust](https://img.shields.io/badge/Parity-Python_↔_Rust-success.svg)](src/)
[![Kani Verified](https://img.shields.io/badge/Kani-Model_Checked-purple.svg)](formal/kani/protocol_proofs.rs)
[![Coq Verified](https://img.shields.io/badge/Coq-Soundness_Proven-blueviolet.svg)](formal/coq/PillRedSoundness.v)
[![Lean 4 Verified](https://img.shields.io/badge/Lean_4-Theorems_Checked-darkblue.svg)](formal/lean/PillRed/Theorems.lean)
[![Licensing](https://img.shields.io/badge/Licensing-Asymmetric_Ed25519-informational.svg)](command_center/billing.py)

> **The Universal Cryptographic Evidence & Model Audit Protocol.**  
> *Developed under Titan Black Swan Technologies.*

**PILL RED** is a cryptographic evidence and model-audit protocol providing deterministic evidence preservation, provenance verification, statistical/economic evidence classification, offline verification, and cryptographically verifiable software and licensing artifacts.

> [!IMPORTANT]
> **Core Scientific Tenet:** PILL RED does **not** claim to predict reality merely because an artifact is cryptographically valid.  
> * **Cryptography** proves what was committed and whether it was altered.  
> * **Statistics** determines what the evidence supports against null baselines.  
> * **Economics** audits real economic payoff and capital preservation without double-counting.  
> * **Formal Proofs** establish that the protocol's stated invariants correspond to machine-checkable mathematics.

---

## 🏛️ The Three Sovereign Cryptographic Pillars

PILL RED enforces complete domain separation across three independent cryptographic pillars:

```
                            TITAN BLACK SWAN TECHNOLOGIES
                                      PILL RED
                                         │
         ┌───────────────────────────────┼───────────────────────────────┐
         ▼                               ▼                               ▼
  EVIDENCE RECEIPT                LICENSE RECEIPT                 RELEASE ARTIFACT
         │                               │                               │
   Evidence Truth                Entitlement Truth             Software Authenticity
         │                               │                               │
   SHA-256 / Merkle               Ed25519 Asymmetric Signature        SHA-256
         │                               │                               │
  Offline Verifier                Offline Verifier                Update Verifier
  (Python / Rust)                 (Public Key Proof)            (Atomic Stage & Swap)
```

1. **Evidence Receipt:** Proves evidence and state transition integrity. Bit-for-bit parity verified offline via `pillred-verify.exe` and `verify_stream.py`.
2. **License Receipt:** Proves commercial entitlement. Deterministically canonicalized JSON signed by Titan's private key and verified offline using Titan's public key (Ed25519).
3. **Release Artifact:** Proves software authenticity and update integrity via SHA-256 digests.

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

## 🖥️ Command Center & Real-Time UI

To launch the interactive visual verification interface:

```bash
# Option A: One-click launcher (Windows)
./launch_command_center.bat

# Option B: Run via Python server
python command_center/server.py 8080
```
Open **`http://localhost:8080`** in your browser to monitor real-time pre-settlement prediction locks, live settle feeds, and automated statistical scorecards.

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
