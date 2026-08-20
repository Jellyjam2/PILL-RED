"""Candidate Representation Generator (CRG) for PILL RED v2.0.

Instantiates candidate representations with deterministic fingerprinting.
"""

from typing import Dict, List, Tuple, Type
from engine.interfaces import CandidateProfile
from engine.dsl.primitives import (
    RepresentationPrimitive,
    SpectralLaplacianPrimitive,
    GF2AffinePrimitive,
    TensorRankPrimitive,
    VPTIProjectorPrimitive,
    QuadraticIdealMPOPrimitive,
    CubicIdealMPOPrimitive,
)


class CandidateRepresentationGenerator:
    """Generates and registers candidate representations."""

    REGISTRY: Dict[str, Tuple[str, Type[RepresentationPrimitive], Dict]] = {
        "spectral_laplacian": (
            "SpectralLaplacian(L=B^T*B, Fiedler)",
            SpectralLaplacianPrimitive,
            {"preserves": "graph spectrum / Fiedler vector", "discards": "global parity", "expected_failure": "UNKNOWN"}
        ),
        "gf2_affine": (
            "GF2Affine(GaussianElimination, Parity)",
            GF2AffinePrimitive,
            {"preserves": "linear parity (degree 1)", "discards": "nonlinear monomials (degree >= 2)", "expected_failure": "UNKNOWN"}
        ),
        "tensor_svd": (
            "TensorRank(Matricization, SVD_Nuclear)",
            TensorRankPrimitive,
            {"preserves": "multilinear clause couplings", "discards": "low condition number", "expected_failure": "UNKNOWN"}
        ),
        "vpti_projector": (
            "VPTI(LocalWitnessCut, MarginalOverlap)",
            VPTIProjectorPrimitive,
            {"preserves": "local 2-hop marginals", "discards": "global cycle obstructions", "expected_failure": "UNKNOWN"}
        ),
        "quadratic_ideal_mpo": (
            "QuadraticIdealMPO(TruncatedDegree2, Basis=O(n^2))",
            QuadraticIdealMPOPrimitive,
            {
                "preserves": "degree-1 terms, degree-2 monomials, pairwise clause couplings",
                "discards": "degree >= 3 monomials",
                "hypothesized_state_size": "polynomial (O(n^2) basis coefficients; scaling to be measured)",
                "primary_adversary": "degree-3 / 3-uniform expander structure",
                "expected_failure": "UNKNOWN"
            }
        ),
        "cubic_ideal_mpo": (
            "CubicIdealMPO(TruncatedDegree3, Basis=O(n^3))",
            CubicIdealMPOPrimitive,
            {
                "preserves": "degree-1 terms, degree-2 pairs, degree-3 triplets (x_i*x_j*x_k), 3-clause ANF",
                "discards": "degree >= 4 monomials",
                "hypothesized_state_size": "polynomial (O(n^3) basis coefficients; scaling to be measured)",
                "primary_adversary": "degree-4 / 4-uniform hypergraph expander structure",
                "expected_failure": "UNKNOWN"
            }
        ),
    }

    @classmethod
    def get_candidate(cls, name: str, params: Dict = None) -> Tuple[CandidateProfile, RepresentationPrimitive]:
        """Returns a candidate profile and its executable primitive instance."""
        if name not in cls.REGISTRY:
            raise KeyError(f"Unknown candidate '{name}'. Available: {list(cls.REGISTRY.keys())}")

        dsl_expr, primitive_cls, default_params = cls.REGISTRY[name]
        merged_params = dict(default_params)
        if params:
            merged_params.update(params)
        profile = CandidateProfile.create(name=name, dsl_expr=dsl_expr, params=merged_params)
        primitive = primitive_cls(profile)
        return profile, primitive

    @classmethod
    def list_all_candidates(cls) -> List[Tuple[CandidateProfile, RepresentationPrimitive]]:
        """Returns all registered standard candidate representations."""
        candidates = []
        for name in cls.REGISTRY:
            candidates.append(cls.get_candidate(name))
        return candidates
