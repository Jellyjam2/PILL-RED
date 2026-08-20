"""
PILL RED: Candidate Representation Interface & Audit Contracts.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple

@dataclass
class GateAuditResult:
    g1_compression: bool
    g2_construction_poly: bool
    g3_valuation_preservation: bool
    g4_collision_separation: bool
    g5_search_elimination: bool
    g6_no_hidden_exponential_work: bool

    @property
    def all_passed(self) -> bool:
        return (
            self.g1_compression and
            self.g2_construction_poly and
            self.g3_valuation_preservation and
            self.g4_collision_separation and
            self.g5_search_elimination and
            self.g6_no_hidden_exponential_work
        )

@dataclass
class EvaluationResult:
    candidate_name: str
    family_name: str
    structural_size: int
    compressed_size: int
    compression_ratio: float
    construction_time_ms: float
    decision_time_ms: float
    valuation_signature: float
    is_separated: bool
    residual_conflicts: int
    ground_truth_soundness: bool
    gates: GateAuditResult
    metadata: Dict[str, Any]

class CandidateRepresentation(ABC):
    """
    Abstract Base Class for Candidate Boolean Representations submitted to PILL RED.
    External researchers implement this interface to audit their proposed invariants.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def encode(self, n_vars: int, clauses: List[List[int]], **kwargs) -> Dict[str, Any]:
        """
        Constructs the candidate representation from a CNF formula.
        Must return a dict containing:
          - 'compressed_size': integer description length
          - 'structural_rank': integer or float rank summary
          - 'representation_object': the underlying compressed artifact
        """
        pass

    @abstractmethod
    def compute_valuation_signature(self, encoding: Dict[str, Any], clauses: List[List[int]]) -> float:
        """
        Computes a scalar or vector invariant signature designed to distinguish SAT from UNSAT.
        """
        pass

    @abstractmethod
    def decide_or_solve(self, encoding: Dict[str, Any], clauses: List[List[int]]) -> Tuple[Optional[bool], int]:
        """
        Decides satisfiability directly or trims residual CDCL search.
        Returns: (satisfiability_outcome: bool or None, residual_conflicts: int)
        """
        pass

    @abstractmethod
    def audit_complexity_bounds(self) -> Dict[str, str]:
        """
        Returns theoretical asymptotic bounds for:
          - 'construction_complexity'
          - 'representation_size'
          - 'decision_complexity'
        """
        pass
