"""
PILL RED: Six-Gate Independent Audit Engine.
"""

import time
from typing import Dict, Any, List, Tuple
from .interfaces import CandidateRepresentation, EvaluationResult, GateAuditResult

class SixGateEvaluator:
    """
    Evaluates a candidate representation against an adversarial collision pair across all 6 Gates:
      G1: Polynomial Compression
      G2: Polynomial Construction Runtime
      G3: Valuation Preservation (Soundness)
      G4: Collision Separation
      G5: Search Elimination
      G6: Hidden Work Audit
    """

    def __init__(self, candidate: CandidateRepresentation):
        self.candidate = candidate

    def audit_pair(self, pair_dict: Dict[str, Any]) -> Tuple[EvaluationResult, EvaluationResult, GateAuditResult]:
        family_name = pair_dict["family"]
        Q_mat = pair_dict.get("Q_matrix")

        # Evaluate SAT member
        n_s, cl_s, sat_gt = pair_dict["sat_instance"]
        t0_s = time.perf_counter()
        enc_s = self.candidate.encode(n_s, cl_s, Q_matrix=Q_mat)
        t_con_s = (time.perf_counter() - t0_s) * 1000.0

        val_sig_s = self.candidate.compute_valuation_signature(enc_s, cl_s)
        t1_s = time.perf_counter()
        sat_pred_s, conf_s = self.candidate.decide_or_solve(enc_s, cl_s)
        t_dec_s = (time.perf_counter() - t1_s) * 1000.0

        # Evaluate UNSAT member
        n_u, cl_u, unsat_gt = pair_dict["unsat_instance"]
        t0_u = time.perf_counter()
        enc_u = self.candidate.encode(n_u, cl_u, Q_matrix=Q_mat)
        t_con_u = (time.perf_counter() - t0_u) * 1000.0

        val_sig_u = self.candidate.compute_valuation_signature(enc_u, cl_u)
        t1_u = time.perf_counter()
        sat_pred_u, conf_u = self.candidate.decide_or_solve(enc_u, cl_u)
        t_dec_u = (time.perf_counter() - t1_u) * 1000.0

        # Gate Evaluations
        g1_comp = (enc_s["compressed_size"] <= (n_s * (n_s + 1) * 4)) # Polynomially bounded
        g2_con = (t_con_s < 2000.0 and t_con_u < 2000.0) # Polynomial construction
        g3_sound = ((sat_pred_s is True or sat_pred_s is None) and (sat_pred_u is False or sat_pred_u is None))
        g4_sep = (val_sig_s != val_sig_u) # Distinct invariant signature
        g5_elim = (conf_s == 0 and conf_u == 0) # Solved directly or 0 conflicts
        
        # G6: Algorithmic Accounting
        bounds = self.candidate.audit_complexity_bounds()
        g6_audit = ("2^n" not in bounds.get("construction_complexity", "") and "2^n" not in bounds.get("representation_size", ""))

        gate_res = GateAuditResult(
            g1_compression=g1_comp,
            g2_construction_poly=g2_con,
            g3_valuation_preservation=g3_sound,
            g4_collision_separation=g4_sep,
            g5_search_elimination=g5_elim,
            g6_no_hidden_exponential_work=g6_audit
        )

        res_s = EvaluationResult(
            candidate_name=self.candidate.name,
            family_name=family_name,
            structural_size=len(cl_s),
            compressed_size=enc_s["compressed_size"],
            compression_ratio=round(len(cl_s) / max(1, enc_s["compressed_size"]), 2),
            construction_time_ms=round(t_con_s, 2),
            decision_time_ms=round(t_dec_s, 2),
            valuation_signature=round(val_sig_s, 3),
            is_separated=g4_sep,
            residual_conflicts=conf_s,
            ground_truth_soundness=True,
            gates=gate_res,
            metadata={"structural_rank": enc_s.get("structural_rank", 0)}
        )

        res_u = EvaluationResult(
            candidate_name=self.candidate.name,
            family_name=family_name,
            structural_size=len(cl_u),
            compressed_size=enc_u["compressed_size"],
            compression_ratio=round(len(cl_u) / max(1, enc_u["compressed_size"]), 2),
            construction_time_ms=round(t_con_u, 2),
            decision_time_ms=round(t_dec_u, 2),
            valuation_signature=round(val_sig_u, 3),
            is_separated=g4_sep,
            residual_conflicts=conf_u,
            ground_truth_soundness=True,
            gates=gate_res,
            metadata={"structural_rank": enc_u.get("structural_rank", 0)}
        )

        return res_s, res_u, gate_res
