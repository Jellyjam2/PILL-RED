"""
PILL RED: Universal Cryptographic Evidence & Model Audit Protocol.
Before something happens, the system forces a model to put its prediction on the record.
Then reality happens. PILL RED keeps the receipt.

Core Pipeline:
DISCOVER -> PREDICT -> COMMIT -> OBSERVE -> VERIFY -> RANK -> DEPLOY -> MONITOR
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root,
    canonical_encode
)
from pillred.protocol.receipt import PredictionReceipt, PredictionEpisode
from pillred.protocol.passport import ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.protocol.client import PillRedClient
from pillred.statistical.engine import StatisticalEngine, StatisticalEvaluationResult
from pillred.economic.engine import EconomicEngine, EconomicEvaluationResult

__version__ = "1.0.0"
__protocol_version__ = PROTOCOL_VERSION

# Global default client instance for frictionless top-level usage
_DEFAULT_CLIENT = PillRedClient(model_id="DEFAULT_MODEL", model_version="1.0.0")


def commit(
    target_event: str,
    prediction: Any,
    confidence: float = 0.5,
    model_id: Optional[str] = None,
    model_version: Optional[str] = None
) -> PredictionReceipt:
    """
    Cryptographically locks a prediction strictly prior to event revelation.

    Args:
        target_event: Unique identifier of the future event.
        prediction: The discrete outcome, class, or vector predicted by the model.
        confidence: Probability estimate in [0.0, 1.0].
        model_id: Optional model identifier (defaults to active client model).
        model_version: Optional model semantic version.

    Returns:
        PredictionReceipt: Sealed commitment receipt with commit_hash and commit_timestamp.
    """
    return _DEFAULT_CLIENT.commit(
        target_event=target_event,
        prediction=prediction,
        confidence=confidence,
        model_id=model_id,
        model_version=model_version
    )


def resolve(
    receipt_id: str,
    actual_outcome: Any,
    payout_multiplier: float = 0.0,
    event_timestamp: Optional[float] = None,
    resolution_timestamp: Optional[float] = None
) -> PredictionReceipt:
    """
    Settles a previously committed prediction against observed ground truth.

    Args:
        receipt_id: The receipt_id generated during commit().
        actual_outcome: The verified empirical outcome observed in reality.
        payout_multiplier: Economic return multiple (e.g. 10.0 for 10x, 0.0 for loss, 1.0 for push).
        event_timestamp: Exact UTC epoch timestamp of real-world event revelation.
        resolution_timestamp: Exact UTC epoch timestamp of settlement recording.

    Returns:
        PredictionReceipt: Final immutable receipt with receipt_hash and temporal seal.
    """
    return _DEFAULT_CLIENT.resolve(
        receipt_id=receipt_id,
        actual_outcome=actual_outcome,
        payout_multiplier=payout_multiplier,
        event_timestamp=event_timestamp,
        resolution_timestamp=resolution_timestamp
    )


def get_passport(
    model_id: Optional[str] = None,
    model_version: Optional[str] = None,
    target_domain: str = "GENERAL_PREDICTION",
    unit_stake: float = 1.0,
    friction_per_wager: float = 0.0
) -> ModelAuditPassport:
    """
    Compiles an official Model Audit Passport aggregating Provenance,
    Statistical Evidence, and Economic Evidence with a unified cryptographic seal.
    """
    return _DEFAULT_CLIENT.get_passport(
        model_id=model_id,
        model_version=model_version,
        target_domain=target_domain,
        unit_stake=unit_stake,
        friction_per_wager=friction_per_wager
    )


def verify(target: Union[str, Dict[str, Any], List[Dict[str, Any]]]) -> Tuple[bool, List[str]]:
    """
    Zero-Trust Offline Verifier. Audits a single receipt, receipt chain, or Passport.
    Accepts a filepath (JSON) or an in-memory dictionary/list.
    """
    import json
    import os

    data = target
    if isinstance(target, str):
        if os.path.exists(target):
            with open(target, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            try:
                data = json.loads(target)
            except Exception:
                return False, [f"File not found and invalid JSON string: {target}"]

    if isinstance(data, dict):
        if "passport_hash" in data:
            return ModelAuditPassport.verify_passport(data)
        elif "commit_hash" in data:
            return ZeroTrustVerifier.verify_single_receipt(data)
        else:
            return False, ["Unrecognized PILL RED object schema."]
    elif isinstance(data, list):
        valid, vios, _ = ZeroTrustVerifier.verify_chain(data)
        return valid, vios
    else:
        return False, ["Input must be a receipt dict, chain list, or passport dict."]


def reset() -> None:
    """Resets the global default client instance."""
    global _DEFAULT_CLIENT
    _DEFAULT_CLIENT = PillRedClient(model_id="DEFAULT_MODEL", model_version="1.0.0")


__all__ = [
    "commit",
    "resolve",
    "get_passport",
    "verify",
    "reset",
    "PillRedClient",
    "PredictionReceipt",
    "PredictionEpisode",
    "ModelAuditPassport",
    "ZeroTrustVerifier",
    "StatisticalEngine",
    "StatisticalEvaluationResult",
    "EconomicEngine",
    "EconomicEvaluationResult",
    "PROTOCOL_VERSION",
    "__version__",
]
