"""Candidate Representation Generator (CRG) for PILL RED v2.0.

Instantiates candidate representations with deterministic fingerprinting.
"""

from typing import Dict, List, Type
from engine.interfaces import CandidateProfile
from engine.dsl.primitives import (
    RepresentationPrimitive,
    SpectralLaplacianPrimitive,
    GF2AffinePrimitive,
    TensorRankPrimitive,
    VPTIProjectorPrimitive,
)


class CandidateRepresentationGenerator:
    """Generates and registers candidate representations."""

    REGISTRY: Dict[str, Tuple[str, Type[RepresentationPrimitive]]] = {
        "spectral_laplacian": ("SpectralLaplacian(L=B^T*B, Fiedler)", SpectralLaplacianPrimitive),
        "gf2_affine": ("GF2Affine(GaussianElimination, Parity)", GF2AffinePrimitive),
        "tensor_svd": ("TensorRank(Matricization, SVD_Nuclear)", TensorRankPrimitive),
        "vpti_projector": ("VPTI(LocalWitnessCut, MarginalOverlap)", VPTIProjectorPrimitive),
    }

    @classmethod
    def get_candidate(cls, name: str, params: Dict = None) -> Tuple[CandidateProfile, RepresentationPrimitive]:
        """Returns a candidate profile and its executable primitive instance."""
        if name not in cls.REGISTRY:
            raise KeyError(f"Unknown candidate '{name}'. Available: {list(cls.REGISTRY.keys())}")

        dsl_expr, primitive_cls = cls.REGISTRY[name]
        profile = CandidateProfile.create(name=name, dsl_expr=dsl_expr, params=params or {})
        primitive = primitive_cls(profile)
        return profile, primitive

    @classmethod
    def list_all_candidates(cls) -> List[Tuple[CandidateProfile, RepresentationPrimitive]]:
        """Returns all registered standard candidate representations."""
        candidates = []
        for name in cls.REGISTRY:
            candidates.append(cls.get_candidate(name))
        return candidates
