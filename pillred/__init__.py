"""
🔴 PILL RED: An Adversarial Laboratory for Information Preservation in Boolean Constraint Representations.
v1.0.0
"""

from .interfaces import CandidateRepresentation, EvaluationResult, GateAuditResult
from .evaluator import SixGateEvaluator
from .candidates import (
    CDCLBaseline,
    SpectralLaplacianCandidate,
    GF2GaussianCandidate,
    TensorRankCandidate,
    VPTIProjectorCandidate
)
from .families import (
    HighGirthExpanderFamily,
    IsoAlgebraicCollisionFamily,
    NonlinearDegreeLadderFamily,
    PureParityFamily,
    FeedforwardCircuitsFamily
)

__version__ = "1.0.0"
