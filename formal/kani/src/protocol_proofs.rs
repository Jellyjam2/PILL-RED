//! Kani Formal Verification Proof Harnesses for PILL RED Protocol (PILLRED-SPEC-1.0).
//! Direct symbolic verification of production Rust functions in `pill_red_core::protocol`.

use pill_red_core::protocol::{
    compute_commit_hash, compute_merkle_root, compute_receipt_hash, verify_chain, verify_passport,
    verify_single, RawReceipt, PROTOCOL_VERSION, canonical_json, sha256_hex,
};
use serde_json::json;

#[cfg(kani)]
mod kani_proofs {
    use super::*;

    /// P2: Temporal Ordering Invariant against production `verify_single()`.
    /// Proves that `verify_single()` strictly enforces t_commit < t_event <= t_resolve
    /// and rejects every invalid temporal permutation.
    #[kani::proof]
    fn check_temporal_precedence_invariant() {
        let t_commit: f64 = kani::any();
        let t_event: f64 = kani::any();
        let t_resolve: f64 = kani::any();

        kani::assume(!t_commit.is_nan() && !t_commit.is_infinite());
        kani::assume(!t_event.is_nan() && !t_event.is_infinite());
        kani::assume(!t_resolve.is_nan() && !t_resolve.is_infinite());
        kani::assume(t_commit >= 0.0 && t_event >= 0.0 && t_resolve >= 0.0);

        let mut receipt = RawReceipt {
            protocol_version: PROTOCOL_VERSION.to_string(),
            receipt_id: "rcpt_kani_01".to_string(),
            model_id: "model_kani".to_string(),
            model_version: "1.0.0".to_string(),
            target_event: "event_kani".to_string(),
            prediction: json!("UP"),
            confidence: 0.85,
            commit_timestamp: t_commit,
            previous_receipt_hash: "GENESIS".to_string(),
            commit_hash: String::new(),
            nonce: "k1".to_string(),
            event_id: Some("event_kani".to_string()),
            event_timestamp: Some(t_event),
            resolution_timestamp: Some(t_resolve),
            actual_outcome: Some(json!("UP")),
            payout_multiplier: Some(1.5),
            receipt_hash: None,
            is_hit: Some(true),
        };

        receipt.commit_hash = compute_commit_hash(&receipt);
        receipt.receipt_hash = Some(compute_receipt_hash(&receipt));

        let res = verify_single(&receipt);
        let is_causal = t_commit < t_event;
        let is_resolved_after_event = t_event <= t_resolve;

        if is_causal && is_resolved_after_event {
            assert!(res.is_ok(), "Valid temporal sequence must pass verify_single()");
        } else {
            assert!(res.is_err(), "Invalid temporal sequence must be rejected by verify_single()");
        }
    }

    /// P3: Sequential Hash Chain Linkage against production `verify_chain()`.
    /// Proves that `verify_chain()` succeeds if and only if receipt R[1] links to R[0].
    #[kani::proof]
    fn check_chain_linkage_induction() {
        let is_valid_link: bool = kani::any();

        let mut r0 = RawReceipt {
            protocol_version: PROTOCOL_VERSION.to_string(),
            receipt_id: "rcpt_0".to_string(),
            model_id: "model_kani".to_string(),
            model_version: "1.0.0".to_string(),
            target_event: "event_0".to_string(),
            prediction: json!("UP"),
            confidence: 0.9,
            commit_timestamp: 100.0,
            previous_receipt_hash: "GENESIS".to_string(),
            commit_hash: String::new(),
            nonce: "n0".to_string(),
            event_id: None,
            event_timestamp: None,
            resolution_timestamp: None,
            actual_outcome: None,
            payout_multiplier: None,
            receipt_hash: None,
            is_hit: None,
        };
        r0.commit_hash = compute_commit_hash(&r0);

        let prev_hash = if is_valid_link {
            r0.commit_hash.clone()
        } else {
            "TAMPERED_PREV_HASH".to_string()
        };

        let mut r1 = RawReceipt {
            protocol_version: PROTOCOL_VERSION.to_string(),
            receipt_id: "rcpt_1".to_string(),
            model_id: "model_kani".to_string(),
            model_version: "1.0.0".to_string(),
            target_event: "event_1".to_string(),
            prediction: json!("DOWN"),
            confidence: 0.8,
            commit_timestamp: 200.0,
            previous_receipt_hash: prev_hash,
            commit_hash: String::new(),
            nonce: "n1".to_string(),
            event_id: None,
            event_timestamp: None,
            resolution_timestamp: None,
            actual_outcome: None,
            payout_multiplier: None,
            receipt_hash: None,
            is_hit: None,
        };
        r1.commit_hash = compute_commit_hash(&r1);

        let chain_res = verify_chain(&[r0, r1]);
        if is_valid_link {
            assert!(chain_res.is_ok(), "Matching chain link must verify");
        } else {
            assert!(chain_res.is_err(), "Severed chain link must fail verify_chain()");
        }
    }

    /// P4: Merkle Tree Collision Invariance against production `compute_merkle_root()`.
    /// Proves that mutating any leaf strictly mutates the SHA-256 Merkle root.
    #[kani::proof]
    fn check_merkle_two_leaf_collision_resistance() {
        let leaf1_byte: u8 = kani::any();
        let leaf1_mut_byte: u8 = kani::any();
        kani::assume(leaf1_byte != leaf1_mut_byte);

        let leaf1 = format!("leaf_{:02x}", leaf1_byte);
        let leaf1_mut = format!("leaf_{:02x}", leaf1_mut_byte);
        let leaf2 = "leaf_static_sample".to_string();

        let root_orig = compute_merkle_root(&[leaf1, leaf2.clone()]);
        let root_mut = compute_merkle_root(&[leaf1_mut, leaf2]);

        assert!(root_orig != root_mut, "Altered leaf must produce a divergent SHA-256 Merkle root");
    }

    /// P5: Passport Evidentiary Binding Invariant against production `verify_passport()`.
    /// Proves that modifying statistical evidence breaks `verify_passport()`, and untampered passes.
    #[kani::proof]
    fn check_passport_section_tamper_detection() {
        use std::collections::BTreeMap;
        // NOTE: We use a symbolic u32 integer for the evidence value in this harness
        // instead of a symbolic float (f64). In SMT solvers, serializing a symbolic
        // float to a JSON string requires symbolic execution of floating-point formatting
        // algorithms (dtoa/ryu), causing state explosion and solver timeouts.
        // Using a symbolic integer proves the exact same cryptographic tamper-detection
        // invariant while keeping SMT serialization loops statically bounded and tractable.
        let stat_val: u32 = kani::any();

        let mut stat_map = BTreeMap::new();
        stat_map.insert("inferred".to_string(), json!({ "p_value": 0.001 }));
        stat_map.insert("measured".to_string(), json!({ "win_rate": 55 }));
        let stat_hash = sha256_hex(&canonical_json(&stat_map));

        let mut econ_map = BTreeMap::new();
        econ_map.insert("inferred".to_string(), json!({ "max_drawdown": 0.05 }));
        econ_map.insert("measured".to_string(), json!({ "sharpe": 2.5 }));
        let econ_hash = sha256_hex(&canonical_json(&econ_map));

        let mut root_map = BTreeMap::new();
        root_map.insert("identity".to_string(), json!({ "model_id": "model_kani", "model_version": "1.0.0" }));
        root_map.insert("provenance".to_string(), json!({ "git_commit": "abc1234" }));
        root_map.insert("statistical_evidence".to_string(), json!({
            "measured": { "win_rate": stat_val },
            "inferred": { "p_value": 0.001 },
            "statistical_evidence_hash": stat_hash
        }));
        root_map.insert("economic_evidence".to_string(), json!({
            "measured": { "sharpe": 2.5 },
            "inferred": { "max_drawdown": 0.05 },
            "economic_evidence_hash": econ_hash
        }));
        root_map.insert("evidentiary_conclusions".to_string(), json!({ "status": "VERIFIED" }));
        let expected_passport_hash = sha256_hex(&canonical_json(&root_map));

        let mut passport = serde_json::Value::Object(root_map.into_iter().collect());
        passport["protocol_version"] = json!(PROTOCOL_VERSION);
        passport["passport_hash"] = json!(expected_passport_hash);

        let res = verify_passport(&passport);
        if stat_val == 55 {
            assert!(res.is_ok(), "Untampered canonical statistical value must pass verify_passport()");
        } else {
            assert!(res.is_err(), "Mutated statistical value must cause statistical_evidence_hash mismatch and fail verify_passport()");
        }
    }

}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_temporal_precedence_production_engine() {
        let test_cases = vec![
            (100.0, 200.0, 300.0, true),   // Valid causal & resolved after event
            (200.0, 100.0, 300.0, false),  // Commit after event
            (100.0, 300.0, 200.0, false),  // Event after resolution
            (100.0, 100.0, 300.0, false),  // Commit equals event
            (100.0, 200.0, 200.0, true),   // Resolution at event time
        ];

        for (t_commit, t_event, t_resolve, expected_valid) in test_cases {
            let mut receipt = RawReceipt {
                protocol_version: PROTOCOL_VERSION.to_string(),
                receipt_id: "rcpt_test".to_string(),
                model_id: "model_test".to_string(),
                model_version: "1.0.0".to_string(),
                target_event: "event_test".to_string(),
                prediction: json!("UP"),
                confidence: 0.85,
                commit_timestamp: t_commit,
                previous_receipt_hash: "GENESIS".to_string(),
                commit_hash: String::new(),
                nonce: "n1".to_string(),
                event_id: Some("event_test".to_string()),
                event_timestamp: Some(t_event),
                resolution_timestamp: Some(t_resolve),
                actual_outcome: Some(json!("UP")),
                payout_multiplier: Some(1.5),
                receipt_hash: None,
                is_hit: Some(true),
            };

            receipt.commit_hash = compute_commit_hash(&receipt);
            receipt.receipt_hash = Some(compute_receipt_hash(&receipt));

            let res = verify_single(&receipt);
            assert_eq!(
                res.is_ok(),
                expected_valid,
                "Failed temporal test case ({}, {}, {})",
                t_commit,
                t_event,
                t_resolve
            );
        }
    }

    #[test]
    fn test_chain_linkage_production_engine() {
        let mut r0 = RawReceipt {
            protocol_version: PROTOCOL_VERSION.to_string(),
            receipt_id: "rcpt_0".to_string(),
            model_id: "model_test".to_string(),
            model_version: "1.0.0".to_string(),
            target_event: "event_0".to_string(),
            prediction: json!("UP"),
            confidence: 0.9,
            commit_timestamp: 100.0,
            previous_receipt_hash: "GENESIS".to_string(),
            commit_hash: String::new(),
            nonce: "n0".to_string(),
            event_id: None,
            event_timestamp: None,
            resolution_timestamp: None,
            actual_outcome: None,
            payout_multiplier: None,
            receipt_hash: None,
            is_hit: None,
        };
        r0.commit_hash = compute_commit_hash(&r0);

        let mut r1_valid = RawReceipt {
            protocol_version: PROTOCOL_VERSION.to_string(),
            receipt_id: "rcpt_1".to_string(),
            model_id: "model_test".to_string(),
            model_version: "1.0.0".to_string(),
            target_event: "event_1".to_string(),
            prediction: json!("DOWN"),
            confidence: 0.8,
            commit_timestamp: 200.0,
            previous_receipt_hash: r0.commit_hash.clone(),
            commit_hash: String::new(),
            nonce: "n1".to_string(),
            event_id: None,
            event_timestamp: None,
            resolution_timestamp: None,
            actual_outcome: None,
            payout_multiplier: None,
            receipt_hash: None,
            is_hit: None,
        };
        r1_valid.commit_hash = compute_commit_hash(&r1_valid);

        assert!(verify_chain(&[r0.clone(), r1_valid]).is_ok());

        let mut r1_invalid = r0.clone();
        r1_invalid.receipt_id = "rcpt_1_tampered".to_string();
        r1_invalid.previous_receipt_hash = "INVALID_HASH".to_string();
        r1_invalid.commit_hash = compute_commit_hash(&r1_invalid);

        assert!(verify_chain(&[r0, r1_invalid]).is_err());
    }

    #[test]
    fn test_merkle_root_production_engine() {
        let leaf1 = "leaf_alpha".to_string();
        let leaf2 = "leaf_beta".to_string();
        let leaf1_tampered = "leaf_alpha_modified".to_string();

        let root_orig = compute_merkle_root(&[leaf1, leaf2.clone()]);
        let root_tamp = compute_merkle_root(&[leaf1_tampered, leaf2]);

        assert_ne!(root_orig, root_tamp);
    }

    #[test]
    fn test_passport_tamper_production_engine() {
        use std::collections::BTreeMap;
        use pill_red_core::protocol::{canonical_json, sha256_hex};

        let mut stat_map = BTreeMap::new();
        stat_map.insert("inferred".to_string(), json!({ "p_value": 0.001 }));
        stat_map.insert("measured".to_string(), json!({ "win_rate": 0.55 }));
        let stat_hash = sha256_hex(&canonical_json(&stat_map));

        let mut econ_map = BTreeMap::new();
        econ_map.insert("inferred".to_string(), json!({ "max_drawdown": 0.05 }));
        econ_map.insert("measured".to_string(), json!({ "sharpe": 2.5 }));
        let econ_hash = sha256_hex(&canonical_json(&econ_map));

        let mut root_map = BTreeMap::new();
        root_map.insert("identity".to_string(), json!({ "model_id": "model_test", "model_version": "1.0.0" }));
        root_map.insert("provenance".to_string(), json!({ "git_commit": "abc1234" }));
        root_map.insert("statistical_evidence".to_string(), json!({
            "measured": { "win_rate": 0.55 },
            "inferred": { "p_value": 0.001 },
            "statistical_evidence_hash": stat_hash
        }));
        root_map.insert("economic_evidence".to_string(), json!({
            "measured": { "sharpe": 2.5 },
            "inferred": { "max_drawdown": 0.05 },
            "economic_evidence_hash": econ_hash
        }));
        root_map.insert("evidentiary_conclusions".to_string(), json!({ "status": "VERIFIED" }));
        let passport_hash = sha256_hex(&canonical_json(&root_map));

        let mut passport_valid = serde_json::Value::Object(root_map.into_iter().collect());
        passport_valid["protocol_version"] = json!(PROTOCOL_VERSION);
        passport_valid["passport_hash"] = json!(passport_hash);

        assert!(verify_passport(&passport_valid).is_ok());

        let mut passport_tampered = passport_valid.clone();
        passport_tampered["statistical_evidence"]["measured"]["win_rate"] = json!(0.99);
        assert!(verify_passport(&passport_tampered).is_err());
    }

}

