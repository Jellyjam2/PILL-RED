# 🛡️ PILL RED v1.0.0 THREAT MODEL & SECURITY ARCHITECTURE

> **Specification:** `PILLRED-SPEC-1.0`  
> **Security Objective:** Provenance Preservation, Tamper Evident Auditing, Anti-Hindsight Guarantees  

---

## 1. Adversary Model & Assumptions

PILL RED assumes an adversarial operator or model developer with:
* Full local read/write filesystem access.
* Ability to alter system memory, source code, or historical files post-event.
* Incentive to inflate predictive accuracy, hide losses, cherry-pick winning episodes, or backdate predictions.

---

## 2. Invariants & Defenses

### Invariant 1: Temporal Precedence ($t_{\text{commit}} < t_{\text{event}} \le t_{\text{resolve}}$)
* **Threat:** Operator observes reality at $t = 100$, then creates a prediction claiming it was generated at $t = 90$.
* **Defense:** The external event revelation time $t_{\text{event}}$ is bound to external feeds. If $t_{\text{commit}} \ge t_{\text{event}}$, the receipt is cryptographically rejected. Furthermore, Merkle batch anchoring locks commitments against external chronological logs.

### Invariant 2: Immutable Commitment Hash ($H_{\text{commit}}$)
* **Threat:** Operator commits to prediction $A$, sees that outcome $B$ occurred, and modifies the stored prediction to $B$.
* **Defense:** $H_{\text{commit}} = \text{SHA256}(\text{JCS}(\{ \dots, \text{"prediction"}: A \}))$. Modifying the stored prediction changes the recomputed SHA-256 hash, causing instant verification failure.

### Invariant 3: Sequential Hash Linkage ($H_{\text{receipt}}[i].\text{prev\_hash} = H_{\text{receipt}}[i-1].\text{receipt\_hash}$)
* **Threat:** Operator deletes losing predictions or reorders events to simulate winning streaks.
* **Defense:** Each commitment binds the hash of the preceding settled receipt. Deleting, injecting, or reordering any record breaks the cryptographic chain.

### Invariant 4: Merkle Tree Completeness
* **Threat:** Operator presents only winning subsets of receipts for passport compilation.
* **Defense:** The Model Audit Passport binds the root of the Merkle tree containing *all* sequential receipts in the evaluation window. Omission of any leaf produces a divergent root.

### Invariant 5: Segregated Economic Ledgers
* **Threat:** Operator claims hypothetical savings from avoided losses as real realized cash returns.
* **Defense:** Active wager PnL is tracked strictly on committed stakes in the `ActiveWagerLedger`. Avoided losses are tracked separately in the `AvoidedLossLedger` and never added to realized portfolio equity.

---

## 3. Out-of-Scope Risks (Explicit Honest Boundaries)

1. **Compromised Ground-Truth Event Feed:** If an oracle or external data feed emits false outcomes, PILL RED will accurately record and verify what the oracle emitted, but cannot detect oracle-level falsehoods.
2. **Predictive Capability of Future Data:** Verification of historical receipts proves what *occurred in the past*; it does not guarantee that market dynamics or data generation distributions will remain stationary in the future.
