"""
PILL RED Protocol Data Structures (Receipt, Episode, EvidenceRecord, AuditPassport)
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from pillred.protocol.spec import (
    PROTOCOL_VERSION,
    canonical_encode,
    compute_commit_hash,
    compute_receipt_hash,
    compute_merkle_root
)


@dataclass
class PredictionReceipt:
    """
    The Atomic Primitive of the PILL RED Protocol.
    Represents an independently verifiable unit of prediction provenance.
    """
    receipt_id: str
    model_id: str
    model_version: str
    target_event: str
    prediction: Any
    confidence: float
    commit_timestamp: float
    previous_receipt_hash: str
    commit_hash: str
    protocol_version: str = PROTOCOL_VERSION
    nonce: str = ""

    # Settlement Fields (populated upon reality revelation)
    event_id: Optional[str] = None
    event_timestamp: Optional[float] = None
    resolution_timestamp: Optional[float] = None
    actual_outcome: Optional[Any] = None
    payout_multiplier: float = 0.0
    receipt_hash: Optional[str] = None
    is_hit: Optional[bool] = None

    @classmethod
    def create_commitment(
        cls,
        model_id: str,
        target_event: str,
        prediction: Any,
        confidence: float = 0.5,
        model_version: str = "1.0.0",
        previous_receipt_hash: str = "0" * 64,
        receipt_id: Optional[str] = None,
        commit_timestamp: Optional[float] = None,
        nonce: Optional[str] = None
    ) -> "PredictionReceipt":
        """Creates a pre-commitment receipt locked strictly prior to the event."""
        rid = receipt_id or f"REC-{uuid.uuid4().hex[:12].upper()}"
        ts = round(float(commit_timestamp or time.time()), 6)
        conf = round(float(confidence), 6)
        n_str = nonce or uuid.uuid4().hex[:8]

        c_hash = compute_commit_hash(
            protocol_version=PROTOCOL_VERSION,
            receipt_id=rid,
            model_id=model_id,
            model_version=model_version,
            target_event=target_event,
            prediction=prediction,
            confidence=conf,
            commit_timestamp=ts,
            previous_receipt_hash=previous_receipt_hash,
            nonce=n_str
        )

        return cls(
            receipt_id=rid,
            model_id=model_id,
            model_version=model_version,
            target_event=target_event,
            prediction=prediction,
            confidence=conf,
            commit_timestamp=ts,
            previous_receipt_hash=previous_receipt_hash,
            commit_hash=c_hash,
            nonce=n_str
        )

    def settle(
        self,
        actual_outcome: Any,
        event_timestamp: float,
        event_id: Optional[str] = None,
        resolution_timestamp: Optional[float] = None,
        payout_multiplier: float = 0.0
    ) -> "PredictionReceipt":
        """Settles the receipt against ground truth after the event occurs."""
        self.event_id = str(event_id or self.target_event)
        self.event_timestamp = round(float(event_timestamp), 6)
        self.resolution_timestamp = round(float(resolution_timestamp or time.time()), 6)
        self.actual_outcome = actual_outcome
        self.payout_multiplier = round(float(payout_multiplier), 4)
        self.is_hit = str(self.prediction).strip().upper() == str(actual_outcome).strip().upper()

        self.receipt_hash = compute_receipt_hash(
            commit_hash=self.commit_hash,
            event_id=self.event_id,
            event_timestamp=self.event_timestamp,
            resolution_timestamp=self.resolution_timestamp,
            actual_outcome=self.actual_outcome,
            payout_multiplier=self.payout_multiplier
        )
        return self

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class PredictionEpisode:
    """A structured sequence of linked receipts belonging to a single continuous run."""
    episode_id: str
    model_id: str
    model_version: str
    created_at: float
    receipts: List[PredictionReceipt] = field(default_factory=list)

    @property
    def merkle_root(self) -> str:
        leaf_hashes = [r.receipt_hash for r in self.receipts if r.receipt_hash]
        return compute_merkle_root(leaf_hashes)

    @property
    def total_count(self) -> int:
        return len(self.receipts)

    @property
    def hit_count(self) -> int:
        return sum(1 for r in self.receipts if r.is_hit)


@dataclass
class ModelAuditPassport:
    """
    Portable, cryptographically verifiable Model Audit Passport.
    The primary reputation artifact certifying model evidence.
    """
    passport_id: str
    model_id: str
    model_version: str
    protocol_version: str
    issued_at: float
    total_forward_predictions: int
    out_of_sample_hit_rate: float
    wilson_score_ci_99: List[float]
    merkle_root: str
    causal_integrity_status: str
    statistical_verdict: str
    economic_evaluation: Dict[str, Any]
    chain_intact: bool

    def summary(self) -> str:
        return f"""=======================================================
🔴 PILL RED MODEL AUDIT PASSPORT
Passport ID:  {self.passport_id}
Model:        {self.model_id} (v{self.model_version})
Issued At:    {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime(self.issued_at))}
Integrity:    {self.causal_integrity_status} (Chain Intact: {self.chain_intact})
Predictions:  {self.total_forward_predictions} Forward Wagers
Accuracy:     {self.out_of_sample_hit_rate * 100:.2f}% (99% CI: [{self.wilson_score_ci_99[0]*100:.1f}%, {self.wilson_score_ci_99[1]*100:.1f}%])
Verdict:      {self.statistical_verdict}
Merkle Root:  {self.merkle_root}
======================================================="""
