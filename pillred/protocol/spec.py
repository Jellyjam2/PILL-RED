"""
PILL RED Protocol Specification (PILLRED-SPEC-1.0)
Defines canonical schemas, deterministic JCS encoding, and cryptographic hash algorithms.
"""

import hashlib
import json
from typing import Any, Dict, List, Optional


PROTOCOL_VERSION = "PILLRED-SPEC-1.0"


def canonical_encode(data: Dict[str, Any]) -> bytes:
    """
    Deterministic JSON Canonicalization Scheme (RFC 8785 subset).
    Ensures identical byte representations across all platforms and languages:
    - Sorted dictionary keys
    - No whitespace between delimiters (separators=(',', ':'))
    - Strict UTF-8 encoding
    """
    return json.dumps(data, sort_keys=True, separators=(',', ':'), ensure_ascii=False).encode('utf-8')


def sha256_hex(data_bytes: bytes) -> str:
    """Computes standard SHA-256 hex digest."""
    return hashlib.sha256(data_bytes).hexdigest()


def compute_commit_hash(
    protocol_version: str,
    receipt_id: str,
    model_id: str,
    model_version: str,
    target_event: str,
    prediction: Any,
    confidence: float,
    commit_timestamp: float,
    previous_receipt_hash: str,
    nonce: Optional[str] = None
) -> str:
    """
    Computes the authoritative commitment hash prior to event revelation.
    """
    payload = {
        "confidence": round(float(confidence), 6),
        "commit_timestamp": round(float(commit_timestamp), 6),
        "model_id": str(model_id),
        "model_version": str(model_version),
        "nonce": nonce or "",
        "previous_receipt_hash": str(previous_receipt_hash),
        "prediction": str(prediction),
        "protocol_version": str(protocol_version),
        "receipt_id": str(receipt_id),
        "target_event": str(target_event)
    }
    return sha256_hex(canonical_encode(payload))


def compute_receipt_hash(
    commit_hash: str,
    event_id: str,
    event_timestamp: float,
    resolution_timestamp: float,
    actual_outcome: Any,
    payout_multiplier: float = 0.0
) -> str:
    """
    Computes the final receipt hash after reality is revealed and settled.
    """
    payload = {
        "actual_outcome": str(actual_outcome),
        "commit_hash": str(commit_hash),
        "event_id": str(event_id),
        "event_timestamp": round(float(event_timestamp), 6),
        "payout_multiplier": round(float(payout_multiplier), 4),
        "resolution_timestamp": round(float(resolution_timestamp), 6)
    }
    return sha256_hex(canonical_encode(payload))


def compute_merkle_root(leaf_hashes: List[str]) -> str:
    """
    Computes the binary Merkle root of a sequence of receipt hashes.
    """
    if not leaf_hashes:
        return sha256_hex(b"EMPTY_TREE")
    
    current_level = list(leaf_hashes)
    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            left = current_level[i]
            right = current_level[i + 1] if i + 1 < len(current_level) else left
            combined = sha256_hex((left + right).encode('utf-8'))
            next_level.append(combined)
        current_level = next_level
    return current_level[0]
