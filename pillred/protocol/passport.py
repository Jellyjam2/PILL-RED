"""
PILL RED Model Audit Passport Engine (Gate 7).
Aggregates and cryptographically binds Provenance, Statistical, and Economic evidence.
Strictly enforces the 4-state evidentiary taxonomy: VERIFIED, MEASURED, INFERRED, NOT PROVEN.
"""

import time
import uuid
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
from pillred.protocol.spec import PROTOCOL_VERSION, canonical_encode, sha256_hex
from pillred.statistical.engine import StatisticalEvaluationResult
from pillred.economic.engine import EconomicEvaluationResult


@dataclass
class PassportIdentity:
    """Section 1: Model & Evaluation Identification."""
    passport_id: str
    protocol_version: str
    model_id: str
    model_version: str
    target_domain: str
    evaluation_window_start: float
    evaluation_window_end: float
    generation_timestamp: float


@dataclass
class ProvenanceEvidence:
    """Section 2: Cryptographic Provenance Evidence."""
    total_receipts: int
    valid_receipts: int
    invalid_receipts: int
    orphaned_receipts: int
    merkle_root: str
    chain_integrity: bool
    temporal_integrity: bool
    status: str  # "VERIFIED" | "COMPROMISED"


@dataclass
class StatisticalEvidenceSection:
    """Section 3: Statistical Evidence (Measured & Inferred)."""
    measured: Dict[str, Any]
    inferred: Dict[str, Any]
    statistical_evidence_hash: str
    status: str  # "INFERRED" | "NOT PROVEN" | "INCONCLUSIVE"


@dataclass
class EconomicEvidenceSection:
    """Section 4: Economic Evidence (Measured & Inferred)."""
    measured: Dict[str, Any]
    inferred: Dict[str, Any]
    economic_evidence_hash: str
    status: str  # "INFERRED" | "NOT PROVEN" | "INCONCLUSIVE"


@dataclass
class EvidentiaryConclusions:
    """Section 5: The 4-State Evidentiary Hierarchy."""
    provenance: str        # "VERIFIED"
    empirical_data: str    # "MEASURED"
    statistical_claim: str # "INFERRED" | "NOT PROVEN" | "INCONCLUSIVE"
    economic_claim: str    # "INFERRED" | "NOT PROVEN" | "INCONCLUSIVE"
    overall_status: str    # "EVIDENCE_PRESERVED" | "INTEGRITY_VIOLATION"


@dataclass
class ModelAuditPassport:
    """
    Standardized, portable, tamper-evident PILL RED Model Audit Passport.
    Cryptographically seals the complete chain of evidence without altering engine outputs.
    """
    identity: PassportIdentity
    provenance: ProvenanceEvidence
    statistical_evidence: StatisticalEvidenceSection
    economic_evidence: EconomicEvidenceSection
    evidentiary_conclusions: EvidentiaryConclusions
    passport_hash: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def create(
        cls,
        model_id: str,
        model_version: str,
        target_domain: str,
        receipts: List[Dict[str, Any]],
        merkle_root: str,
        chain_valid: bool,
        statistical_result: StatisticalEvaluationResult,
        economic_result: EconomicEvaluationResult,
        passport_id: Optional[str] = None,
        generation_timestamp: Optional[float] = None
    ) -> "ModelAuditPassport":
        """
        Constructs and cryptographically seals a Model Audit Passport from engine outputs.
        Does NOT alter, recompute, or guess any scientific metrics.
        """
        pid = passport_id or f"PASSPORT-{uuid.uuid4().hex[:12].upper()}"
        ts = round(float(generation_timestamp or time.time()), 6)

        # Normalize receipts (accepts List[PredictionReceipt] or List[Dict])
        receipts_dicts = [r.to_dict() if hasattr(r, "to_dict") else r for r in receipts]

        # 1. Identity & Timestamps
        timestamps = [
            r.get("commit_timestamp", 0.0) for r in receipts_dicts if r.get("commit_timestamp") is not None
        ]
        start_ts = min(timestamps) if timestamps else ts
        end_ts = max(timestamps) if timestamps else ts

        identity = PassportIdentity(
            passport_id=pid,
            protocol_version=PROTOCOL_VERSION,
            model_id=model_id,
            model_version=model_version,
            target_domain=target_domain,
            evaluation_window_start=round(float(start_ts), 6),
            evaluation_window_end=round(float(end_ts), 6),
            generation_timestamp=ts
        )

        # 2. Provenance Evidence
        total_r = len(receipts)
        valid_r = total_r if chain_valid else 0
        prov_status = "VERIFIED" if chain_valid and total_r > 0 else "COMPROMISED"

        provenance = ProvenanceEvidence(
            total_receipts=total_r,
            valid_receipts=valid_r,
            invalid_receipts=total_r - valid_r,
            orphaned_receipts=0,
            merkle_root=merkle_root,
            chain_integrity=chain_valid,
            temporal_integrity=chain_valid,
            status=prov_status
        )

        # 3. Statistical Evidence (Measured & Inferred)
        stat_measured = {
            "observations": statistical_result.total_observations,
            "hits": statistical_result.hits,
            "accuracy": round(statistical_result.accuracy, 6),
            "majority_baseline": round(statistical_result.majority_class_baseline, 6),
            "uniform_null_baseline": round(statistical_result.uniform_null_baseline, 6),
            "delta_over_majority": round(statistical_result.delta_over_majority, 6),
            "wilson_ci_99": [round(c, 6) for c in statistical_result.wilson_ci_99],
            "brier_score": round(statistical_result.brier_score, 6),
            "expected_calibration_error": round(statistical_result.expected_calibration_error, 6)
        }
        stat_inferred = {
            "is_serially_dependent": statistical_result.is_serially_dependent,
            "markov_transition_p_value": round(statistical_result.markov_transition_p_value, 6),
            "block_bootstrap_ci_99": [round(c, 6) for c in statistical_result.block_bootstrap_ci_99],
            "effective_alpha": round(statistical_result.effective_alpha, 6),
            "engine_verdict": statistical_result.verdict,
            "justification": statistical_result.justification
        }
        stat_evidence_payload = {"measured": stat_measured, "inferred": stat_inferred}
        stat_hash = sha256_hex(canonical_encode(stat_evidence_payload))

        # Map engine verdict to evidentiary status
        if statistical_result.verdict == "PASS":
            stat_status = "INFERRED"
        elif statistical_result.verdict == "INCONCLUSIVE":
            stat_status = "INCONCLUSIVE"
        else:
            stat_status = "NOT PROVEN"

        statistical_evidence = StatisticalEvidenceSection(
            measured=stat_measured,
            inferred=stat_inferred,
            statistical_evidence_hash=stat_hash,
            status=stat_status
        )

        # 4. Economic Evidence (Measured & Inferred)
        act = economic_result.active_ledger
        avd = economic_result.avoided_ledger
        econ_measured = {
            "wagers_count": act.wagers_count,
            "winning_wagers": act.winning_wagers,
            "losing_wagers": act.losing_wagers,
            "push_wagers": act.push_wagers,
            "total_stake": round(act.total_stake, 4),
            "gross_return": round(act.gross_return, 4),
            "friction_cost": round(act.friction_cost, 4),
            "net_pnl": round(act.net_pnl, 4),
            "roi_pct": round(act.roi_pct, 4),
            "win_rate": round(act.win_rate, 4),
            "profit_factor": round(act.profit_factor, 4),
            "max_drawdown_units": round(act.max_drawdown_units, 4),
            "max_drawdown_pct": round(act.max_drawdown_pct, 4),
            "drawdown_duration_events": act.drawdown_duration_events,
            "skipped_events_count": avd.skipped_events_count,
            "correctly_avoided_losses_count": avd.correctly_avoided_losses_count,
            "missed_winning_opportunities_count": avd.missed_winning_opportunities_count,
            "capital_preserved": round(avd.capital_preserved, 4),
            "missed_gross_profit": round(avd.missed_gross_profit, 4),
            "net_preservation_benefit": round(avd.net_preservation_benefit, 4),
            "filter_precision": round(avd.filter_precision, 4)
        }
        econ_inferred = {
            "exposure_rate": round(economic_result.exposure_rate, 4),
            "engine_verdict": economic_result.verdict,
            "justification": economic_result.justification
        }
        econ_evidence_payload = {"measured": econ_measured, "inferred": econ_inferred}
        econ_hash = sha256_hex(canonical_encode(econ_evidence_payload))

        if economic_result.verdict == "PASS":
            econ_status = "INFERRED"
        elif economic_result.verdict == "INCONCLUSIVE":
            econ_status = "INCONCLUSIVE"
        else:
            econ_status = "NOT PROVEN"

        economic_evidence = EconomicEvidenceSection(
            measured=econ_measured,
            inferred=econ_inferred,
            economic_evidence_hash=econ_hash,
            status=econ_status
        )

        # 5. Evidentiary Conclusions
        overall_status = "EVIDENCE_PRESERVED" if prov_status == "VERIFIED" else "INTEGRITY_VIOLATION"
        conclusions = EvidentiaryConclusions(
            provenance=prov_status,
            empirical_data="MEASURED",
            statistical_claim=stat_status,
            economic_claim=econ_status,
            overall_status=overall_status
        )

        # 6. Cryptographic Passport Hash Formulation
        sealable_payload = {
            "identity": asdict(identity),
            "provenance": asdict(provenance),
            "statistical_evidence": asdict(statistical_evidence),
            "economic_evidence": asdict(economic_evidence),
            "evidentiary_conclusions": asdict(conclusions)
        }
        passport_hash = sha256_hex(canonical_encode(sealable_payload))

        return cls(
            identity=identity,
            provenance=provenance,
            statistical_evidence=statistical_evidence,
            economic_evidence=economic_evidence,
            evidentiary_conclusions=conclusions,
            passport_hash=passport_hash
        )

    @classmethod
    def verify_passport(cls, passport_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Independently audits the cryptographic seal and sub-hashes of a Model Audit Passport.
        """
        violations = []
        p_data = dict(passport_data)
        claimed_hash = p_data.get("passport_hash", "")

        # Check sub-hashes
        stat_sec = p_data.get("statistical_evidence", {})
        stat_claimed_hash = stat_sec.get("statistical_evidence_hash", "")
        stat_payload = {"measured": stat_sec.get("measured", {}), "inferred": stat_sec.get("inferred", {})}
        expected_stat_hash = sha256_hex(canonical_encode(stat_payload))
        if stat_claimed_hash != expected_stat_hash:
            violations.append(f"Statistical evidence hash mismatch! Expected: {expected_stat_hash}, Claimed: {stat_claimed_hash}")

        econ_sec = p_data.get("economic_evidence", {})
        econ_claimed_hash = econ_sec.get("economic_evidence_hash", "")
        econ_payload = {"measured": econ_sec.get("measured", {}), "inferred": econ_sec.get("inferred", {})}
        expected_econ_hash = sha256_hex(canonical_encode(econ_payload))
        if econ_claimed_hash != expected_econ_hash:
            violations.append(f"Economic evidence hash mismatch! Expected: {expected_econ_hash}, Claimed: {econ_claimed_hash}")

        # Check overall passport hash
        sealable_payload = {
            "identity": p_data.get("identity", {}),
            "provenance": p_data.get("provenance", {}),
            "statistical_evidence": stat_sec,
            "economic_evidence": econ_sec,
            "evidentiary_conclusions": p_data.get("evidentiary_conclusions", {})
        }
        expected_passport_hash = sha256_hex(canonical_encode(sealable_payload))
        if claimed_hash != expected_passport_hash:
            violations.append(f"Passport hash mismatch! Expected: {expected_passport_hash}, Claimed: {claimed_hash}")

        return len(violations) == 0, violations
