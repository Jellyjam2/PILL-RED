"""
PILL RED Protocol Core Package.
Provides the canonical Prediction Receipt specification, Zero-Trust Verifier, and Developer SDK.
"""

from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    canonical_encode,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root
)
from pillred.protocol.receipt import (
    PredictionReceipt,
    PredictionEpisode
)
from pillred.protocol.passport import ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.protocol.client import PillRedClient

# Default global instance for 3-line Python usage
_default_client = PillRedClient()

commit = _default_client.commit
resolve = _default_client.resolve
get_passport = _default_client.get_passport

__all__ = [
    "PROTOCOL_VERSION",
    "canonical_encode",
    "compute_commit_hash",
    "compute_receipt_hash",
    "compute_merkle_root",
    "PredictionReceipt",
    "PredictionEpisode",
    "ModelAuditPassport",
    "ZeroTrustVerifier",
    "PillRedClient",
    "commit",
    "resolve",
    "get_passport"
]
