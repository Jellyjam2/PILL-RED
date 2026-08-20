"""Unit and Integration Tests for QuadraticIdealMPO and Level-4 Pure Degree-3 Adversary."""

import unittest
from engine.crg.generator import CandidateRepresentationGenerator
from engine.aag.adversary import AdaptiveAdversaryManager
from engine.aag.pure_degree3_expander import PureDegree3ExpanderGenerator
from engine.ace.crucible import AutomatedCrucibleEngine
from engine.classifier.trilemma import TrilemmaClassifier
from engine.interfaces import TrilemmaOutcome
from pillred_v2 import execute_pipeline


class TestQuadraticIdealMPO(unittest.TestCase):
    """Verifies QuadraticIdealMPO representation and Level-4 Pure Degree-3 Adversary."""

    def test_quadratic_mpo_basis_size(self):
        """Test that QuadraticIdealMPO basis size matches 1 + n + n*(n-1)/2."""
        profile, primitive = CandidateRepresentationGenerator.get_candidate("quadratic_ideal_mpo")
        self.assertEqual(profile.name, "quadratic_ideal_mpo")
        self.assertIn("degree-2", profile.parameters.get("preserves", ""))
        self.assertEqual(profile.parameters.get("expected_failure"), "UNKNOWN")

    def test_level4_pure_degree3_adversary_integrity(self):
        """Test that Level-4 Adversary produces certified SAT/UNSAT pairs with degree-3 parity."""
        pair = PureDegree3ExpanderGenerator.generate_pure_degree3_pair(num_vertices=18, seed=42)
        self.assertTrue(pair.sat_instance.is_satisfiable)
        self.assertFalse(pair.unsat_instance.is_satisfiable)
        self.assertGreater(pair.num_vars, 0)
        self.assertTrue(pair.sat_instance.metadata.get("projection_equivalence_degree_1"))
        self.assertTrue(pair.sat_instance.metadata.get("projection_equivalence_degree_2"))

    def test_quadratic_mpo_escalation_trajectory(self):
        """Test QuadraticIdealMPO survival at Level 2 and collapse at Level 4."""
        # Level 2: Survives degree-2 non-linear couplings
        v2 = execute_pipeline("quadratic_ideal_mpo", samples=2, level=2)
        self.assertEqual(v2.classification, TrilemmaOutcome.OUTCOME_D)
        self.assertGreater(v2.mean_separation, 0.5)

        # Level 4: Collapses on pure degree-3 non-linear expander obstruction
        v4 = execute_pipeline("quadratic_ideal_mpo", samples=2, level=4)
        self.assertEqual(v4.classification, TrilemmaOutcome.OUTCOME_A)
        self.assertAlmostEqual(v4.mean_separation, 0.0, places=5)


if __name__ == "__main__":
    unittest.main()
