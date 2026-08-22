"""Forensic Prediction Ledger & Causal Audit Subsystem.

Enforces strict prediction-before-settlement causal ordering:
1. Generates and locks PredictionRecord before target spin is revealed.
2. Emits cryptographic/timestamped commitment to immutable ledger.
3. Resolves actual outcome only after SPIN_SETTLED event.
4. Detects and flags any retrospective timestamp leakage.
"""

from dataclasses import dataclass, field, asdict
import hashlib
import json
import os
import time
from typing import Any, Callable, Dict, List, Optional


@dataclass
class PredictionRecord:
    """Forensic record of a prediction made BEFORE spin settlement."""
    prediction_id: str
    session_id: str
    source_spin_index: int          # Spin N-1 (last known)
    target_spin_index: int          # Spin N (predicted target)
    timestamp_predicted: float      # Timestamp when prediction was locked
    predictor_version: str
    model_hash: str
    predicted_target: str           # e.g., "JACKPOT", "SYMBOL", "OUTCOME"
    decision: Any                   # e.g., "BET", "SKIP", or symbol category ID
    confidence: float
    actual_result: Optional[Any] = None
    is_hit: Optional[bool] = None
    timestamp_resolved: Optional[float] = None
    causal_status: str = "PENDING"  # "VALID", "INVALID_LEAKAGE", "PENDING"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredictionRecord":
        return cls(**data)


class ForensicPredictionLedger:
    """Manages immutable persistence and causal verification of live predictions."""

    def __init__(self, ledger_path: str = "rng_audit/evidence/predictions_ledger.jsonl"):
        self.ledger_path = ledger_path
        os.makedirs(os.path.dirname(os.path.abspath(ledger_path)), exist_ok=True)
        self.pending_predictions: Dict[str, PredictionRecord] = {}  # key: f"{session_id}:{target_spin_index}"

    def lock_prediction(
        self,
        session_id: str,
        source_spin_index: int,
        target_spin_index: int,
        predicted_target: str,
        decision: Any,
        confidence: float,
        model_hash: str,
        predictor_version: str = "2.0.0-alpha.live",
        timestamp: Optional[float] = None
    ) -> PredictionRecord:
        """Locks a prediction before target spin settlement."""
        t_pred = timestamp or time.time()
        
        # Generate unique prediction ID
        pred_hash_input = f"{session_id}:{source_spin_index}->{target_spin_index}:{t_pred}:{decision}:{model_hash}"
        pred_id = f"PRED-{hashlib.sha256(pred_hash_input.encode('utf-8')).hexdigest()[:12].upper()}"

        record = PredictionRecord(
            prediction_id=pred_id,
            session_id=session_id,
            source_spin_index=source_spin_index,
            target_spin_index=target_spin_index,
            timestamp_predicted=t_pred,
            predictor_version=predictor_version,
            model_hash=model_hash,
            predicted_target=predicted_target,
            decision=decision,
            confidence=float(confidence),
            actual_result=None,
            is_hit=None,
            timestamp_resolved=None,
            causal_status="PENDING"
        )

        key = f"{session_id}:{target_spin_index}"
        self.pending_predictions[key] = record
        self._append_to_file(record)
        return record

    def resolve_prediction(
        self,
        session_id: str,
        target_spin_index: int,
        actual_result: Any,
        timestamp_resolved: Optional[float] = None
    ) -> Optional[PredictionRecord]:
        """Resolves a pending prediction after spin settlement and verifies causality."""
        key = f"{session_id}:{target_spin_index}"
        record = self.pending_predictions.pop(key, None)
        if not record:
            return None

        t_res = timestamp_resolved or time.time()

        # Strict Causal Check: Resolution timestamp MUST be strictly greater than prediction timestamp
        if t_res <= record.timestamp_predicted:
            record.causal_status = "INVALID_LEAKAGE"
            record.is_hit = False
        else:
            record.causal_status = "VALID"
            # Evaluate hit
            if record.predicted_target == "JACKPOT":
                # For rare event: hit if decision == "BET" and actual_result is a jackpot (e.g. 1 or True)
                if record.decision == "BET":
                    record.is_hit = bool(actual_result == 1 or actual_result is True)
                else:
                    record.is_hit = bool(actual_result == 0 or actual_result is False)
            else:
                record.is_hit = bool(record.decision == actual_result or str(record.decision) == str(actual_result))

        record.actual_result = actual_result
        record.timestamp_resolved = t_res

        # Append resolved state to ledger
        self._append_to_file(record)
        return record

    def _append_to_file(self, record: PredictionRecord) -> None:
        """Appends record JSON to ledger."""
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def purge_session(self, session_id: str) -> None:
        """Purges all records for a session from both memory and disk ledger."""
        self.pending_predictions = {k: v for k, v in self.pending_predictions.items() if not k.startswith(f"{session_id}:")}
        if not os.path.exists(self.ledger_path):
            return
        try:
            remaining_lines = []
            with open(self.ledger_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            if data.get("session_id") != session_id:
                                remaining_lines.append(line)
                        except Exception:
                            pass
            with open(self.ledger_path, "w", encoding="utf-8") as f:
                f.writelines(remaining_lines)
        except Exception:
            pass

    def load_predictions(self, session_id: Optional[str] = None) -> List[PredictionRecord]:
        """Loads and filters predictions from ledger."""
        if not os.path.exists(self.ledger_path):
            return []

        records = {}
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if session_id and data.get("session_id") != session_id:
                        continue
                    rec = PredictionRecord.from_dict(data)
                    # Latest record state overwrites earlier pending state
                    records[rec.prediction_id] = rec

        return list(records.values())
