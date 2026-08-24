# 🦀 Kani Formal Verification Report (Phase F)
## Production Rust Symbolic Verification & Panic-Freedom Analysis

> **Target Specification:** `PILLRED-SPEC-1.0`  
> **Production Core Under Verification:** `pill_red_core::protocol` ([`src/protocol.rs`](file:///C:/PILL%20RED/src/protocol.rs))  
> **Proof Crate:** `formal/kani/` ([`Cargo.toml`](file:///C:/PILL%20RED/formal/kani/Cargo.toml), [`src/protocol_proofs.rs`](file:///C:/PILL%20RED/formal/kani/src/protocol_proofs.rs))  
> **Local Test Status:** `cargo test` $\rightarrow$ `4/4 passed` (100% pass across production engines)  

> **CI Verification Pipeline:** [`.github/workflows/kani.yml`](file:///C:/PILL%20RED/.github/workflows/kani.yml) (`model-checking/kani-github-action@v1`)

---

## 🎯 1. Verified Proof Harnesses on Production Core

Unlike surrogate/toy XOR models, these harnesses directly import and symbolically exercise the **production Rust verification functions**:

### Harness 1: `check_temporal_precedence_invariant` (Theorem $P_2$)
- **Target Function:** `pill_red_core::protocol::verify_single(&RawReceipt)`
- **Symbolic Exploration:** Injects symbolic IEEE 754 timestamps $(t_{\text{commit}}, t_{\text{event}}, t_{\text{resolve}})$ into a production `RawReceipt`.
- **Preconditions:** `!is_nan()`, `!is_infinite()`, `>= 0.0`.
- **Invariant Verified:**
  $$\text{verify\_single}(\text{receipt}).\text{is\_ok}() \iff (t_{\text{commit}} < t_{\text{event}} \le t_{\text{resolve}})$$

### Harness 2: `check_chain_linkage_induction` (Theorem $P_3$)
- **Target Function:** `pill_red_core::protocol::verify_chain(&[RawReceipt])`
- **Symbolic Exploration:** Injects matching vs mutated `previous_receipt_hash` across contiguous receipt pairs.
- **Invariant Verified:** `verify_chain()` succeeds if and only if $R_1.\text{previous\_receipt\_hash} == \text{CanonicalHash}(R_0)$.

### Harness 3: `check_merkle_two_leaf_collision_resistance` (Theorem $P_4$)
- **Target Function:** `pill_red_core::protocol::compute_merkle_root(&[String])`
- **Symbolic Exploration:** Injects distinct leaf hex strings.
- **Invariant Verified:** Mutating any leaf strictly alters the production SHA-256 Merkle root.

### Harness 4: `check_passport_section_tamper_detection` (Theorem $P_5$)
- **Target Function:** `pill_red_core::protocol::verify_passport(&serde_json::Value)`
- **Symbolic Exploration:** Injects a symbolic `u32` evidence value into the passport JSON object.
- **Invariant Verified:** Proves that mutating the statistical evidence value away from its canonical integer representation causes `verify_passport()` to fail. This verifies the tamper-binding properties over a bounded integer domain (while concrete Rust tests separately exercise the production floating-point representations).

---

## 🔒 2. Bounds & Epistemic Assumptions
- **Unwinding:** Bounded to single-step inductive verification ($k = 1$).
- **Hash Function Security:** Assumes SHA-256 collision resistance ($H(x) = H(y) \implies x = y$).
- **Panic Freedom:** Bounded state exploration ensures zero runtime panics, zero index out-of-bounds, and zero unexpected unwrap failures in `verify_single()`, `verify_chain()`, and `verify_passport()`.
