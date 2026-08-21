//! Rust Test-Vector Conformance Suite for Gate 4A.
//! Consumes test_vectors/ against test_vector_manifest.json without server contact.

use pill_red_core::protocol::{verify_chain, verify_single, RawReceipt};
use serde_json::Value;
use std::fs;

#[test]
fn test_vector_conformance_rust() {
    let manifest_content = fs::read_to_string("test_vectors/expected/test_vector_manifest.json")
        .expect("Manifest must exist");
    let manifest: Value = serde_json::from_str(&manifest_content).expect("Valid manifest JSON");

    // 1. Valid Receipt 001
    let r1_path = manifest["vectors"]["valid_receipt_001"]["file"].as_str().unwrap();
    let r1_content = fs::read_to_string(r1_path).expect("File must exist");
    let r1: RawReceipt = serde_json::from_str(&r1_content).unwrap();
    assert!(verify_single(&r1).is_ok());
    assert_eq!(r1.commit_hash, manifest["vectors"]["valid_receipt_001"]["expected_commit_hash"].as_str().unwrap());
    assert_eq!(r1.receipt_hash.unwrap(), manifest["vectors"]["valid_receipt_001"]["expected_receipt_hash"].as_str().unwrap());

    // 2. Valid Receipt 002
    let r2_path = manifest["vectors"]["valid_receipt_002"]["file"].as_str().unwrap();
    let r2_content = fs::read_to_string(r2_path).expect("File must exist");
    let r2: RawReceipt = serde_json::from_str(&r2_content).unwrap();
    assert!(verify_single(&r2).is_ok());
    assert_eq!(r2.commit_hash, manifest["vectors"]["valid_receipt_002"]["expected_commit_hash"].as_str().unwrap());
    assert_eq!(r2.receipt_hash.unwrap(), manifest["vectors"]["valid_receipt_002"]["expected_receipt_hash"].as_str().unwrap());

    // 3. Valid Chain 001
    let chain_path = manifest["vectors"]["valid_chain_001"]["file"].as_str().unwrap();
    let chain_content = fs::read_to_string(chain_path).expect("File must exist");
    let chain: Vec<RawReceipt> = serde_json::from_str(&chain_content).unwrap();
    let chain_res = verify_chain(&chain);
    assert!(chain_res.is_ok());
    assert_eq!(chain_res.unwrap(), manifest["vectors"]["valid_chain_001"]["expected_merkle_root"].as_str().unwrap());

    // 4. Invalid: Tampered Prediction
    let tampered_path = manifest["vectors"]["invalid_tampered_prediction"]["file"].as_str().unwrap();
    let tampered_content = fs::read_to_string(tampered_path).expect("File must exist");
    let tampered: RawReceipt = serde_json::from_str(&tampered_content).unwrap();
    assert!(verify_single(&tampered).is_err());

    // 5. Invalid: Broken Chain
    let broken_path = manifest["vectors"]["invalid_broken_chain"]["file"].as_str().unwrap();
    let broken_content = fs::read_to_string(broken_path).expect("File must exist");
    let broken: Vec<RawReceipt> = serde_json::from_str(&broken_content).unwrap();
    assert!(verify_chain(&broken).is_err());

    // 6. Invalid: Invalid Timestamp
    let invalid_ts_path = manifest["vectors"]["invalid_invalid_timestamp"]["file"].as_str().unwrap();
    let invalid_ts_content = fs::read_to_string(invalid_ts_path).expect("File must exist");
    let invalid_ts: RawReceipt = serde_json::from_str(&invalid_ts_content).unwrap();
    assert!(verify_single(&invalid_ts).is_err());

    // 7. Valid Passport 001
    let pass_path = manifest["vectors"]["valid_passport_001"]["file"].as_str().unwrap();
    let pass_content = fs::read_to_string(pass_path).expect("File must exist");
    let pass_json: Value = serde_json::from_str(&pass_content).unwrap();
    assert!(pill_red_core::protocol::verify_passport(&pass_json).is_ok());
    assert_eq!(pass_json["passport_hash"].as_str().unwrap(), manifest["vectors"]["valid_passport_001"]["expected_passport_hash"].as_str().unwrap());

    // 8. Invalid: Tampered Passport
    let tampered_pass_path = manifest["vectors"]["invalid_tampered_passport"]["file"].as_str().unwrap();
    let tampered_pass_content = fs::read_to_string(tampered_pass_path).expect("File must exist");
    let tampered_pass_json: Value = serde_json::from_str(&tampered_pass_content).unwrap();
    assert!(pill_red_core::protocol::verify_passport(&tampered_pass_json).is_err());
}
