"""Evidence Knowledge Graph & Immutable Run Ledger for PILL RED v2.0.

Persists all crucible runs, gate metrics, and trilemma classifications into machine-readable JSONL.
"""

from dataclasses import asdict
import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.interfaces import CrucibleVerdict


class EpistemicLedger:
    """Manages the append-only JSONL run ledger for empirical provenance."""

    DEFAULT_LEDGER_PATH = Path("evidence/v2_ledger.jsonl")

    def __init__(self, ledger_path: Optional[Path] = None):
        self.ledger_path = ledger_path or self.DEFAULT_LEDGER_PATH
        self._ensure_ledger_dir()

    def _ensure_ledger_dir(self) -> None:
        self.ledger_path.parent.mkdir(parents=True, exist_ok=True)

    def record_verdict(self, verdict: CrucibleVerdict) -> str:
        """Appends a crucible verdict record to the immutable ledger.

        Returns:
            The unique run_id of the recorded verdict.
        """
        self._ensure_ledger_dir()
        data = asdict(verdict)
        # Convert enums and nested structures to plain JSON
        data["classification"] = str(verdict.classification.value)
        data_json = json.dumps(data, sort_keys=True)

        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(data_json + "\n")

        return verdict.run_id

    def load_all_records(self) -> List[Dict[str, Any]]:
        """Reads all historical verdict records from the ledger."""
        if not self.ledger_path.exists():
            return []
        records = []
        with open(self.ledger_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
        return records

    def get_records_by_candidate(self, candidate_id: str) -> List[Dict[str, Any]]:
        """Filters ledger records for a specific candidate ID."""
        return [r for r in self.load_all_records() if r.get("candidate", {}).get("candidate_id") == candidate_id]

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Computes summary statistics across all recorded runs in the ledger."""
        records = self.load_all_records()
        total_runs = len(records)
        outcome_counts: Dict[str, int] = {}
        for r in records:
            out = r.get("classification", "UNKNOWN")
            outcome_counts[out] = outcome_counts.get(out, 0) + 1

        return {
            "total_runs": total_runs,
            "outcome_breakdown": outcome_counts,
            "ledger_file": str(self.ledger_path),
        }
