"""PILL RED v2.0 Core Interfaces & Epistemic Dataclasses.

Strictly separates Observation (raw metrics) from Interpretation (trilemma classification).
"""

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional, Tuple


class TrilemmaOutcome(str, Enum):
    """The 5-state epistemic classification for candidate representations."""
    OUTCOME_A = "OUTCOME_A_COLLAPSE"        # Tractable relaxation, but information collapses under adversarial cycles
    OUTCOME_B = "OUTCOME_B_CIRCULARITY"     # Exact discrete logic, but construction secretly solves NP-hard search
    OUTCOME_C = "OUTCOME_C_BLOWUP"          # Exact representation, but requires exponential rank, precision, or orbit sum
    OUTCOME_D = "OUTCOME_D_SURVIVED"        # Survived the current adversarial crucible (Candidate for escalation)
    UNKNOWN   = "UNKNOWN_INCONCLUSIVE"      # Inconclusive data or indeterminate gate failure


@dataclass
class CNFFormula:
    """Represents a Boolean CNF formula with ground-truth metadata."""
    num_vars: int
    clauses: List[List[int]]
    is_satisfiable: bool
    witness_assignment: Optional[Dict[int, bool]] = None
    family_name: str = "unknown"
    girth: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def formula_hash(self) -> str:
        canonical = f"{self.num_vars}:{sorted(sorted(c) for c in self.clauses)}"
        return hashlib.sha256(canonical.encode('utf-8')).hexdigest()[:16]


@dataclass
class InstancePair:
    """A matched pair of SAT and UNSAT formulas sharing structural invariants."""
    pair_id: str
    family: str
    sat_instance: CNFFormula
    unsat_instance: CNFFormula
    girth: int
    num_vars: int
    num_clauses: int
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CandidateProfile:
    """Metadata and deterministic fingerprint of a candidate representation."""
    candidate_id: str
    name: str
    dsl_expression: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    family_type: str = "generic"

    @classmethod
    def create(cls, name: str, dsl_expr: str, params: Optional[Dict[str, Any]] = None) -> "CandidateProfile":
        params = params or {}
        raw = f"{name}::{dsl_expr}::{json.dumps(params, sort_keys=True)}"
        cid = f"CAND-{hashlib.sha256(raw.encode('utf-8')).hexdigest()[:10].upper()}"
        return cls(candidate_id=cid, name=name, dsl_expression=dsl_expr, parameters=params)


@dataclass
class GateResult:
    """Individual gate verdict with quantitative margin."""
    gate_id: str          # D1, D2, D3, D4, D5, D6, D7
    gate_name: str
    passed: bool
    metric_value: float
    threshold: float
    margin: float
    notes: str = ""


@dataclass
class CrucibleMeasurement:
    """Raw empirical observation data before classification."""
    candidate_id: str
    pair_id: str
    family: str
    
    # D1: Separation Observable
    sat_observable: float
    unsat_observable: float
    separation_delta: float
    
    # D2/D3: Resource Accounting
    construction_time_ms: float
    extraction_time_ms: float
    peak_memory_kb: float
    
    # D4: Numerical Stability
    condition_number: float
    bit_precision_required: int
    
    # D5: Gauge Invariance
    gauge_shift_variance: float
    
    # D6: Global Parity Sensitivity (Q8)
    expander_cycle_sensitivity: float
    
    # D7: Anti-Circularity Profiling
    internal_sat_decisions: int
    internal_sat_conflicts: int
    
    # Solver Baseline Profiling
    glucose_sat_conflicts: int
    glucose_unsat_conflicts: int


@dataclass
class CrucibleVerdict:
    """The synthesized verdict containing all 7 gates and the Trilemma classification."""
    run_id: str
    candidate: CandidateProfile
    family: str
    sample_size: int
    
    # Gate Evaluations
    gates: Dict[str, GateResult]
    all_gates_passed: bool
    
    # Aggregated Empirical Averages
    mean_separation: float
    mean_construction_time_ms: float
    mean_extraction_time_ms: float
    mean_gauge_variance: float
    mean_condition_number: float
    mean_internal_conflicts: int
    
    # Epistemic Classification
    classification: TrilemmaOutcome
    confidence: float
    primary_failure_mechanism: str
    rationale: str
    
    # Timestamp and Provenance
    timestamp_utc: str = ""
    engine_version: str = "2.0.0-alpha.1"
