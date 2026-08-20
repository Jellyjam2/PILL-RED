"""Data Schema and Storage for Passive Spin Sequence Logging.

Provides standardized format for recording observable game and RNG telemetry
without interfering with game execution.
"""

from dataclasses import dataclass, field, asdict
import json
import os
import time
from typing import Any, Dict, List, Optional


@dataclass
class SpinRecord:
    """Individual spin observation record."""
    timestamp: float
    game_title: str
    session_id: str
    spin_index: int
    outcome_symbols: List[int]
    payout_multiplier: float
    bonus_event: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SpinRecord":
        return cls(**data)


class SpinLogger:
    """Manages append-only JSONL recording of observed spin sequences."""

    def __init__(self, storage_path: str = "rng_audit/evidence/spin_logs.jsonl"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(os.path.abspath(storage_path)), exist_ok=True)

    def log_spin(self, record: SpinRecord) -> None:
        """Appends a spin record to the ledger."""
        with open(self.storage_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record.to_dict()) + "\n")

    def load_spins(self, game_title: Optional[str] = None, session_id: Optional[str] = None) -> List[SpinRecord]:
        """Loads and filters spin records from the log."""
        if not os.path.exists(self.storage_path):
            return []

        records = []
        with open(self.storage_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    data = json.loads(line)
                    if game_title and data.get("game_title") != game_title:
                        continue
                    if session_id and data.get("session_id") != session_id:
                        continue
                    records.append(SpinRecord.from_dict(data))
        return records
