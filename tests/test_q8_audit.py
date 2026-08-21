"""Rigorous Mathematical and Computational Audit Suite for Level 2 Q8 Escalation."""

import unittest
from engine.ivr.verifier import IndependentVerifier
from engine.aag.nonlinear_expander import NonlinearExpanderGenerator
from engine.crg.generator import CandidateRepresentationGenerator
from engine.ace.crucible import AutomatedCrucibleEngine
from engine.classifier.trilemma import TrilemmaClassifier
from engine.interfaces import TrilemmaOutcome


class TestQ8EscalationAudit(unittest.TestCase):
    """Deep structural and statistical audit of the Level-2 adversarial machinery."""

    def test_level2_nonlinear_adversary_integrity(self):
        """Audit 1: Verify non-linear clause coupling, girth, and independent ground truth."""
        for seed in [42, 101, 202, 303, 404]:
            pair = NonlinearExpanderGenerator.generate_mixed_nonlinear_pair(
                num_vertices=20,
                nonlinear_fraction=0.4,
                seed=seed
            )
            # 1. Verify Ground Truth
            self.assertTrue(pair.sat_instance.is_satisfiable, f"Seed {seed}: SAT instance marked UNSAT")
            self.assertFalse(pair.unsat_instance.is_satisfiable, f"Seed {seed}: UNSAT instance marked SAT")
            
            # 2. Verify Witness Correctness for SAT
            witness = pair.sat_instance.witness_assignment
            self.assertIsNotNone(witness)
            self.assertTrue(
                IndependentVerifier.validate_witness(pair.sat_instance.clauses, witness),
                f"Seed {seed}: SAT witness failed clause validation"
            )

            # 3. Clause-Level ANF Degree Certificate (Algebraic Non-Linearity Witness)
            # A 2-literal clause (NOT e1 OR NOT e2) maps to monomial e1 * e2 = 0 (Degree 2)
            # A 3-literal clause (e1 OR e2 OR e3) maps to (1+e1)(1+e2)(1+e3) = 0 (Degree 3)
            # This certifies that the clause family introduces genuine degree-k algebraic terms.
            max_clause_degree = 0
            for clause in pair.sat_instance.clauses:
                deg = len(clause)
                if deg > max_clause_degree:
                    max_clause_degree = deg

            self.assertGreaterEqual(
                max_clause_degree, 2,
                f"Seed {seed}: Formula is purely linear/affine (max clause degree < 2)"
            )
            # Verify presence of degree-2 cross-couplings specifically
            has_degree_2_couplings = any(len(c) == 2 for c in pair.sat_instance.clauses)
            self.assertTrue(has_degree_2_couplings, f"Seed {seed}: Missing degree-2 non-linear couplings")
            self.assertGreaterEqual(pair.girth, 4)

    def test_gf2_level2_multi_seed_collapse(self):
        """Audit 2: Verify that GF(2) collapse on Level 2 is robust across 10 distinct random seeds."""
        profile, primitive = CandidateRepresentationGenerator.get_candidate("gf2_affine")
        
        pairs = [
            NonlinearExpanderGenerator.generate_mixed_nonlinear_pair(
                num_vertices=18,
                nonlinear_fraction=0.4,
                seed=1000 + i * 37
            )
            for i in range(10)
        ]

        verdict = AutomatedCrucibleEngine.evaluate_candidate(profile, primitive, pairs, q8_level=2)
        classified = TrilemmaClassifier.classify_verdict(verdict)

        # Assert that ALL 10 seeds trigger Outcome A (Information Collapse)
        self.assertEqual(classified.classification, TrilemmaOutcome.OUTCOME_A)
        self.assertEqual(classified.primary_failure_mechanism, "INFORMATION_COLLAPSE")
        self.assertAlmostEqual(classified.mean_separation, 0.0, places=6)
        self.assertFalse(classified.gates["D1"].passed)
        self.assertTrue(classified.gates["D2"].passed)
        self.assertTrue(classified.gates["D3"].passed)
        self.assertTrue(classified.gates["D7"].passed)


if __name__ == "__main__":
    unittest.main()
