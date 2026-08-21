# 🔴 PILL RED Protocol Specification (PILLRED-SPEC-1.0)

> **Document Status:** FROZEN / BASELINE SPECIFICATION  
> **Version:** `1.0.0`  
> **Target Audience:** Implementers, Auditors, Quantitative Researchers, Regulators  

---

## 1. Abstract & Epistemic Boundary

The **PILL RED Evidence Protocol** is a domain-agnostic, tamper-evident cryptographic evidence layer designed to capture, link, and independently verify claims made by predictive models prior to the occurrence of future events.

### The Tri-Layer Boundary Principle:
1. **The Cryptographic Layer proves Provenance:** Was the claim honestly committed prior to ground truth, and is the evidence chain unaltered?
2. **The Statistical Layer evaluates the Claim:** Does the observed performance reject an appropriate serial or stochastic null hypothesis?
3. **The Economic Layer evaluates the Value:** Does the predictive advantage create or preserve capital after friction, drawdowns, and transaction costs?

> **Fundamental Axiom:** A receipt proves provenance, not correctness. A model with an intact cryptographic receipt can still be a poor predictor. PILL RED certifies that the claim was honestly captured on the record before reality was revealed.

---

## 2. The Atomic Primitive: Prediction Receipt

The atomic unit of the protocol is the **Prediction Receipt**. Every receipt is divided into two immutable phases: **Commitment** and **Settlement**.

### 2.1 Commitment Payload (Phase 1)

Constructed strictly prior to event revelation ($t_{\text{commit}} < t_{\text{event}}$):

```json
{
  "protocol_version": "PILLRED-SPEC-1.0",
  "receipt_id": "REC-A4F98B2C019E",
  "model_id": "MOD-MARKOV-01",
  "model_version": "1.0.0",
  "target_event": "HABANERO_HHF_SPIN_101",
  "prediction": "BAR",
  "confidence": 0.550000,
  "commit_timestamp": 1700000000.123456,
  "previous_receipt_hash": "0000000000000000000000000000000000000000000000000000000000000000",
  "nonce": "SEC_NONCE_8F2A",
  "commit_hash": "4a1b8c9d..."
}
```

#### Commitment Hash Formulation:
$$H_{\text{commit}} = \text{SHA256}(\text{JCS}(\text{Payload}_{\text{commit}}))$$

Where $\text{JCS}$ is the **JSON Canonicalization Scheme (RFC 8785)**:
* Alphabetically sorted keys
* Deterministic float and integer formatting
* No arbitrary whitespace around separators `(',' and ':')`
* Strict UTF-8 character encoding

---

### 2.2 Settlement Payload (Phase 2)

Appended once ground truth arrives ($t_{\text{event}} \le t_{\text{resolution}}$):

```json
{
  "event_id": "HABANERO_HHF_SPIN_101",
  "event_timestamp": 1700000005.654321,
  "resolution_timestamp": 1700000006.000000,
  "actual_outcome": "BAR",
  "payout_multiplier": 6.0,
  "is_hit": true,
  "receipt_hash": "9f8e7d6c..."
}
```

#### Final Receipt Hash Formulation:
$$H_{\text{receipt}} = \text{SHA256}(\text{JCS}(\{ H_{\text{commit}}, \text{event\_id}, t_{\text{event}}, t_{\text{resolve}}, \text{actual\_outcome}, \text{payout\_multiplier} \}))$$

---

## 3. Protocol State Machine

```
              ┌──────────────────────────┐
              │       UNCOMMITTED        │
              └─────────────┬────────────┘
                            │
                            │ client.commit()
                            ▼
              ┌──────────────────────────┐
              │        COMMITTED         │ ─── (Timeout / Stream Broken) ──► [ORPHANED]
              │ (H_commit cryptolocked)  │
              └─────────────┬────────────┘
                            │
                            │ Ground truth revealed
                            │ client.resolve()
                            ▼
              ┌──────────────────────────┐
              │         SETTLED          │
              │ (H_receipt immutable)    │
              └─────────────┬────────────┘
                            │
                            │ Merkle Tree Aggregation
                            ▼
              ┌──────────────────────────┐
              │   MODEL AUDIT PASSPORT   │
              └──────────────────────────┘
```

### Mutability Invariants:
1. **Zero Retroactive Mutation:** No field in Phase 1 may be altered once Phase 2 is attached.
2. **Strict Temporal Ordering:** Any receipt where $t_{\text{commit}} \ge t_{\text{event}}$ or $t_{\text{event}} > t_{\text{resolve}}$ is classified as `CAUSAL_VIOLATION` and permanently disqualified.
3. **Chain Monotonicity:** In a multi-event episode, Receipt $N$ MUST include $H_{N-1}$ as its `previous_receipt_hash`.

---

## 4. Zero-Trust Offline Verification Algorithm

Any third-party verifier MUST execute the following deterministic checks:

1. **Protocol Header:** Verify `protocol_version == "PILLRED-SPEC-1.0"`.
2. **Commitment Recalculation:** Compute $H_{\text{commit}}$ from Phase 1 fields and assert equality.
3. **Temporal Invariant:** Assert $t_{\text{commit}} < t_{\text{event}} \le t_{\text{resolve}}$.
4. **Settlement Recalculation:** Compute $H_{\text{receipt}}$ from Phase 2 fields and assert equality.
5. **Chain Linkage:** For sequence index $i > 0$, assert $R_i.\text{prev\_hash} == R_{i-1}.\text{receipt\_hash}$.
6. **Merkle Aggregation:** Recalculate the binary Merkle root across all $\{H_{\text{receipt}}\}_{i=1}^N$ and match against the claimed Passport root.

---

## 5. Adversarial Threat Model & Mitigations

| Threat | Attack Scenario | Protocol Mitigation |
| :--- | :--- | :--- |
| **Backdating** | Committing after outcome is known | Strict timestamp comparison $t_{\text{commit}} < t_{\text{event}}$ and authoritative network time anchoring. |
| **Payload Tampering** | Mutating prediction from loss to win | $H_{\text{commit}}$ SHA-256 mismatch detected instantly. |
| **Drawdown Hiding** | Reordering or deleting losing spins | Parent-child hash chain linkage broken ($H_{t}.\text{prev} \ne H_{t-1}$). |
| **Cross-Model Spoofing** | Attributing Model B's win to Model A | Single-model identity constraint in episode verification. |
| **JSON Whitespace Drift** | Exploiting parser discrepancies | Deterministic RFC 8785 canonical serialization. |
| **Merkle Forgery** | Submitting fabricated passport roots | Full bottom-up binary Merkle tree recomputation. |

---

> **“Commit. Observe. Settle. Prove.”**  
> *“Don't show me your prediction. Show me the receipt.”*
