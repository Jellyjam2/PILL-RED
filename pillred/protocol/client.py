"""
PILL RED Developer SDK Client.
Minimal, frictionless evidence capture interface for Python applications and models.
"""

import json
import os
import time
from typing import Any, Dict, List, Optional
from pillred.protocol.spec import PROTOCOL_VERSION, compute_merkle_root
from pillred.protocol.receipt import PredictionReceipt, PredictionEpisode, ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier


class PillRedClient:
    """
    Standard Capture Engine for Predictive Model Evidence.
    """

    def __init__(self, model_id: str = "DEFAULT_MODEL", model_version: str = "1.0.0", storage_path: Optional[str] = None):
        self.model_id = model_id
        self.model_version = model_version
        self.storage_path = storage_path
        self.receipts: List[PredictionReceipt] = []
        self._pending_receipts: Dict[str, PredictionReceipt] = {}

        if self.storage_path and os.path.exists(self.storage_path):
            self._load_from_disk()

    def _load_from_disk(self):
        """Loads and deserializes persisted prediction receipts from disk."""
        try:
            with open(self.storage_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                self.receipts = []
                for item in data:
                    r = PredictionReceipt(
                        receipt_id=item["receipt_id"],
                        model_id=item["model_id"],
                        model_version=item.get("model_version", "1.0.0"),
                        target_event=item["target_event"],
                        prediction=item["prediction"],
                        confidence=item.get("confidence", 0.5),
                        commit_timestamp=item["commit_timestamp"],
                        previous_receipt_hash=item.get("previous_receipt_hash", "0" * 64),
                        commit_hash=item["commit_hash"],
                        protocol_version=item.get("protocol_version", PROTOCOL_VERSION),
                        nonce=item.get("nonce", ""),
                        event_id=item.get("event_id"),
                        event_timestamp=item.get("event_timestamp"),
                        resolution_timestamp=item.get("resolution_timestamp"),
                        actual_outcome=item.get("actual_outcome"),
                        payout_multiplier=item.get("payout_multiplier", 0.0),
                        receipt_hash=item.get("receipt_hash"),
                        is_hit=item.get("is_hit")
                    )
                    self.receipts.append(r)
        except Exception:
            pass

    def commit(
        self,
        target_event: str,
        prediction: Any,
        confidence: float = 0.5,
        model_id: Optional[str] = None,
        model_version: Optional[str] = None
    ) -> PredictionReceipt:
        """
        Cryptographically locks a prediction strictly prior to event revelation.
        """
        m_id = model_id or self.model_id
        m_ver = model_version or self.model_version

        prev_hash = "0" * 64
        if self.receipts:
            prev_hash = self.receipts[-1].receipt_hash or self.receipts[-1].commit_hash

        receipt = PredictionReceipt.create_commitment(
            model_id=m_id,
            target_event=target_event,
            prediction=prediction,
            confidence=confidence,
            model_version=m_ver,
            previous_receipt_hash=prev_hash
        )

        self._pending_receipts[receipt.receipt_id] = receipt
        return receipt

    def resolve(
        self,
        receipt_id: str,
        actual_outcome: Any,
        payout_multiplier: float = 0.0,
        event_timestamp: Optional[float] = None,
        resolution_timestamp: Optional[float] = None,
        event_id: Optional[str] = None
    ) -> PredictionReceipt:
        """
        Settles a pre-committed prediction with ground truth.
        """
        receipt = self._pending_receipts.pop(receipt_id, None)
        if not receipt:
            raise KeyError(f"Receipt ID '{receipt_id}' not found in active pending commitments.")

        now = time.time()
        if event_timestamp is not None:
            e_ts = float(event_timestamp)
            r_ts = float(resolution_timestamp or (e_ts + 0.001))
        else:
            e_ts = max(now, receipt.commit_timestamp + 0.001)
            r_ts = float(resolution_timestamp or (e_ts + 0.001))

        receipt.settle(
            actual_outcome=actual_outcome,
            event_timestamp=e_ts,
            resolution_timestamp=r_ts,
            event_id=event_id,
            payout_multiplier=payout_multiplier
        )

        self.receipts.append(receipt)
        self._persist()
        return receipt

    def get_passport(
        self,
        model_id: Optional[str] = None,
        model_version: Optional[str] = None,
        target_domain: str = "SEQUENTIAL_FORECASTING",
        unit_stake: float = 1.0,
        friction_per_wager: float = 0.0
    ) -> ModelAuditPassport:
        """
        Compiles the full evidence history into a portable, cryptographically sealed ModelAuditPassport.
        Delegates statistical and economic evaluation strictly to Gate 5 & Gate 6 Truth Engines.
        """
        from pillred.statistical.engine import StatisticalEngine
        from pillred.economic.engine import EconomicEngine
        from pillred.protocol.passport import ModelAuditPassport

        m_id = model_id or self.model_id
        m_ver = model_version or self.model_version

        # 1. Provenance Integrity Audit
        receipts_dicts = [r.to_dict() for r in self.receipts]
        valid_chain, violations, merkle_root = ZeroTrustVerifier.verify_chain(receipts_dicts)

        # 2. Extract Streams for Engines
        preds = [r.prediction for r in self.receipts if r.actual_outcome is not None]
        acts = [r.actual_outcome for r in self.receipts if r.actual_outcome is not None]
        confs = [r.confidence for r in self.receipts if r.actual_outcome is not None]
        payouts = [r.payout_multiplier for r in self.receipts if r.actual_outcome is not None]

        # 3. Scientific Evaluation
        stat_eval = StatisticalEngine.evaluate_stream(preds, acts, confs, min_sample_size=30)
        econ_eval = EconomicEngine.evaluate(preds, acts, payouts, unit_stake=unit_stake, house_edge_friction=friction_per_wager, min_active_wagers=10)

        # 4. Passport Compilation (Gate 7)
        return ModelAuditPassport.create(
            model_id=m_id,
            model_version=m_ver,
            target_domain=target_domain,
            receipts=self.receipts,
            merkle_root=merkle_root if valid_chain else "0" * 64,
            chain_valid=valid_chain,
            statistical_result=stat_eval,
            economic_result=econ_eval
        )

    def _persist(self):
        if self.storage_path:
            with open(self.storage_path, "w", encoding="utf-8") as f:
                json.dump([r.to_dict() for r in self.receipts], f, indent=2)
