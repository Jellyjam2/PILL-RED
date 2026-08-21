//! Protocol verification module for PILL RED Protocol (PILLRED-SPEC-1.0).

use hex;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use sha2::{Digest, Sha256};
use std::collections::BTreeMap;

pub const PROTOCOL_VERSION: &str = "PILLRED-SPEC-1.0";

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct RawReceipt {
    pub protocol_version: String,
    pub receipt_id: String,
    pub model_id: String,
    pub model_version: String,
    pub target_event: String,
    pub prediction: Value,
    pub confidence: f64,
    pub commit_timestamp: f64,
    pub previous_receipt_hash: String,
    pub commit_hash: String,
    #[serde(default)]
    pub nonce: String,

    // Settlement
    #[serde(default)]
    pub event_id: Option<String>,
    #[serde(default)]
    pub event_timestamp: Option<f64>,
    #[serde(default)]
    pub resolution_timestamp: Option<f64>,
    #[serde(default)]
    pub actual_outcome: Option<Value>,
    #[serde(default)]
    pub payout_multiplier: Option<f64>,
    #[serde(default)]
    pub receipt_hash: Option<String>,
    #[serde(default)]
    pub is_hit: Option<bool>,
}

pub fn canonical_json(map: &BTreeMap<String, Value>) -> String {
    serde_json::to_string(map).unwrap_or_default()
}

pub fn sha256_hex(data: &str) -> String {
    let mut hasher = Sha256::new();
    hasher.update(data.as_bytes());
    hex::encode(hasher.finalize())
}

pub fn compute_commit_hash(r: &RawReceipt) -> String {
    let mut map = BTreeMap::new();
    map.insert("confidence".to_string(), Value::from(r.confidence));
    map.insert("commit_timestamp".to_string(), Value::from(r.commit_timestamp));
    map.insert("model_id".to_string(), Value::from(r.model_id.clone()));
    map.insert("model_version".to_string(), Value::from(r.model_version.clone()));
    map.insert("nonce".to_string(), Value::from(r.nonce.clone()));
    map.insert("previous_receipt_hash".to_string(), Value::from(r.previous_receipt_hash.clone()));
    map.insert("prediction".to_string(), Value::from(r.prediction.to_string().replace("\"", "")));
    map.insert("protocol_version".to_string(), Value::from(r.protocol_version.clone()));
    map.insert("receipt_id".to_string(), Value::from(r.receipt_id.clone()));
    map.insert("target_event".to_string(), Value::from(r.target_event.clone()));

    let canonical = canonical_json(&map);
    sha256_hex(&canonical)
}

pub fn compute_receipt_hash(r: &RawReceipt) -> String {
    let mut map = BTreeMap::new();
    let actual_str = r.actual_outcome.as_ref().map(|v| v.to_string().replace("\"", "")).unwrap_or_default();
    map.insert("actual_outcome".to_string(), Value::from(actual_str));
    map.insert("commit_hash".to_string(), Value::from(r.commit_hash.clone()));
    map.insert("event_id".to_string(), Value::from(r.event_id.clone().unwrap_or_else(|| r.target_event.clone())));
    map.insert("event_timestamp".to_string(), Value::from(r.event_timestamp.unwrap_or(0.0)));
    map.insert("payout_multiplier".to_string(), Value::from(r.payout_multiplier.unwrap_or(0.0)));
    map.insert("resolution_timestamp".to_string(), Value::from(r.resolution_timestamp.unwrap_or(0.0)));

    let canonical = canonical_json(&map);
    sha256_hex(&canonical)
}

pub fn compute_merkle_root(leaf_hashes: &[String]) -> String {
    if leaf_hashes.is_empty() {
        return sha256_hex("EMPTY_TREE");
    }
    let mut current_level = leaf_hashes.to_vec();
    while current_level.len() > 1 {
        let mut next_level = Vec::new();
        for i in (0..current_level.len()).step_by(2) {
            let left = &current_level[i];
            let right = if i + 1 < current_level.len() { &current_level[i + 1] } else { left };
            let combined = format!("{}{}", left, right);
            next_level.push(sha256_hex(&combined));
        }
        current_level = next_level;
    }
    current_level[0].clone()
}

pub fn verify_single(r: &RawReceipt) -> Result<(), Vec<String>> {
    let mut vios = Vec::new();
    if r.protocol_version != PROTOCOL_VERSION {
        vios.push(format!("Unsupported protocol version: {}", r.protocol_version));
    }
    let expected_commit = compute_commit_hash(r);
    if expected_commit != r.commit_hash {
        vios.push(format!("Commit hash mismatch! Expected: {}, Got: {}", expected_commit, r.commit_hash));
    }
    if let (Some(e_ts), Some(r_ts)) = (r.event_timestamp, r.resolution_timestamp) {
        if r.commit_timestamp >= e_ts {
            vios.push(format!("Causal violation: commit ({}) >= event ({})", r.commit_timestamp, e_ts));
        }
        if e_ts > r_ts {
            vios.push(format!("Temporal violation: event ({}) > resolution ({})", e_ts, r_ts));
        }
        let expected_receipt = compute_receipt_hash(r);
        if let Some(actual_receipt_hash) = &r.receipt_hash {
            if expected_receipt != *actual_receipt_hash {
                vios.push(format!("Receipt hash mismatch! Expected: {}, Got: {}", expected_receipt, actual_receipt_hash));
            }
        }
    }
    if vios.is_empty() { Ok(()) } else { Err(vios) }
}

pub fn verify_chain(receipts: &[RawReceipt]) -> Result<String, Vec<String>> {
    let mut all_vios = Vec::new();
    let mut leaf_hashes = Vec::new();
    let mut seen_ids = std::collections::HashSet::new();
    let mut model_id: Option<String> = None;

    for (idx, r) in receipts.iter().enumerate() {
        if !seen_ids.insert(r.receipt_id.clone()) {
            all_vios.push(format!("Duplicate receipt ID: {}", r.receipt_id));
        }
        if let Some(m_id) = &model_id {
            if &r.model_id != m_id {
                all_vios.push(format!("Cross-model contamination at index {}: expected {}, got {}", idx, m_id, r.model_id));
            }
        } else {
            model_id = Some(r.model_id.clone());
        }

        if let Err(vios) = verify_single(r) {
            all_vios.extend(vios.into_iter().map(|v| format!("Receipt #{}: {}", idx + 1, v)));
        }

        if idx > 0 {
            let prev = &receipts[idx - 1];
            let expected_prev = prev.receipt_hash.as_ref().unwrap_or(&prev.commit_hash);
            if r.previous_receipt_hash != *expected_prev {
                all_vios.push(format!("Broken chain linkage at Receipt #{}: expected prev {}, got {}", idx + 1, expected_prev, r.previous_receipt_hash));
            }
        }

        leaf_hashes.push(r.receipt_hash.clone().unwrap_or_else(|| r.commit_hash.clone()));
    }

    if all_vios.is_empty() {
        Ok(compute_merkle_root(&leaf_hashes))
    } else {
        Err(all_vios)
    }
}

pub fn verify_passport(passport_json: &Value) -> Result<(), Vec<String>> {
    let mut vios = Vec::new();
    let claimed_hash = passport_json.get("passport_hash").and_then(|v| v.as_str()).unwrap_or_default();

    // 1. Verify Statistical Evidence Hash
    if let Some(stat_sec) = passport_json.get("statistical_evidence") {
        let stat_claimed_hash = stat_sec.get("statistical_evidence_hash").and_then(|v| v.as_str()).unwrap_or_default();
        let mut map = BTreeMap::new();
        if let Some(m) = stat_sec.get("measured") { map.insert("measured".to_string(), m.clone()); }
        if let Some(i) = stat_sec.get("inferred") { map.insert("inferred".to_string(), i.clone()); }
        let expected_stat_hash = sha256_hex(&canonical_json(&map));
        if stat_claimed_hash != expected_stat_hash {
            vios.push(format!("Statistical evidence hash mismatch! Expected: {}, Claimed: {}", expected_stat_hash, stat_claimed_hash));
        }
    }

    // 2. Verify Economic Evidence Hash
    if let Some(econ_sec) = passport_json.get("economic_evidence") {
        let econ_claimed_hash = econ_sec.get("economic_evidence_hash").and_then(|v| v.as_str()).unwrap_or_default();
        let mut map = BTreeMap::new();
        if let Some(m) = econ_sec.get("measured") { map.insert("measured".to_string(), m.clone()); }
        if let Some(i) = econ_sec.get("inferred") { map.insert("inferred".to_string(), i.clone()); }
        let expected_econ_hash = sha256_hex(&canonical_json(&map));
        if econ_claimed_hash != expected_econ_hash {
            vios.push(format!("Economic evidence hash mismatch! Expected: {}, Claimed: {}", expected_econ_hash, econ_claimed_hash));
        }
    }

    // 3. Verify Overall Passport Seal
    let mut root_map = BTreeMap::new();
    if let Some(v) = passport_json.get("identity") { root_map.insert("identity".to_string(), v.clone()); }
    if let Some(v) = passport_json.get("provenance") { root_map.insert("provenance".to_string(), v.clone()); }
    if let Some(v) = passport_json.get("statistical_evidence") { root_map.insert("statistical_evidence".to_string(), v.clone()); }
    if let Some(v) = passport_json.get("economic_evidence") { root_map.insert("economic_evidence".to_string(), v.clone()); }
    if let Some(v) = passport_json.get("evidentiary_conclusions") { root_map.insert("evidentiary_conclusions".to_string(), v.clone()); }

    let expected_passport_hash = sha256_hex(&canonical_json(&root_map));
    if claimed_hash != expected_passport_hash {
        vios.push(format!("Passport hash mismatch! Expected: {}, Claimed: {}", expected_passport_hash, claimed_hash));
    }

    if vios.is_empty() { Ok(()) } else { Err(vios) }
}
