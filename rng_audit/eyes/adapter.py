"""Observation Adapter for PILL RED Eyes.

Converts multi-source game telemetry (optical frame recognition, DOM events,
or structured logs) into canonical, timestamped SpinRecord instances for the
frozen Track 2 audit engine.
"""

from dataclasses import dataclass
import time
from typing import Any, Dict, List, Optional
from rng_audit.collectors.schema import SpinRecord, SpinLogger


@dataclass
class RawObservation:
    """Raw observation event before canonical normalization."""
    timestamp: float
    source_type: str  # e.g., "optical_cv", "dom_event", "json_stream"
    game_title: str
    session_id: str
    raw_symbols: List[Any]
    payout_multiplier: float
    bonus_flag: bool
    raw_metadata: Dict[str, Any]


class ObservationAdapter:
    """Normalizes raw visual or structured telemetry into canonical SpinRecord streams."""

    def __init__(self, symbol_map: Optional[Dict[str, int]] = None, logger: Optional[SpinLogger] = None):
        self.symbol_map = symbol_map or {}
        self.logger = logger or SpinLogger()
        self.spin_counter = 0

    def register_symbol(self, symbol_name: str, symbol_id: int) -> None:
        """Maps an optical or textual symbol to a discrete integer category."""
        self.symbol_map[symbol_name] = symbol_id

    def normalize(self, raw: RawObservation) -> SpinRecord:
        """Converts raw observation to canonical SpinRecord."""
        self.spin_counter += 1
        
        # Map raw symbols to integer IDs
        mapped_symbols = []
        for s in raw.raw_symbols:
            if isinstance(s, int):
                mapped_symbols.append(s)
            elif isinstance(s, str) and s in self.symbol_map:
                mapped_symbols.append(self.symbol_map[s])
            else:
                try:
                    mapped_symbols.append(int(s))
                except (ValueError, TypeError):
                    # Auto-assign new integer ID if unseen
                    new_id = len(self.symbol_map)
                    self.symbol_map[str(s)] = new_id
                    mapped_symbols.append(new_id)

        record = SpinRecord(
            timestamp=raw.timestamp,
            game_title=raw.game_title,
            session_id=raw.session_id,
            spin_index=self.spin_counter,
            outcome_symbols=mapped_symbols,
            payout_multiplier=float(raw.payout_multiplier),
            bonus_event=bool(raw.bonus_flag),
            metadata={
                "source_type": raw.source_type,
                **raw.raw_metadata
            }
        )

        # Append to immutable session ledger
        self.logger.log_spin(record)
        return record
