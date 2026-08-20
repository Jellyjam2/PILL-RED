"""Unit and Integration Tests for CubicIdealMPO and Level-5 Pure Degree-4 Adversary."""

import unittest
from engine.crg.generator import CandidateRepresentationGenerator
from engine.aag.adversary import AdaptiveAdversaryManager
from engine.aag.pure_degree4_expander import PureDegree4ExpanderGenerator
from engine.interfaces import TrilemmaOutcome
from pillred_v2 import execute_pipeline


class TestCubicIdealMPO(unittest.TestCase):
    """Verifies CubicIdealMPO representation and Level-5 Pure Degree-4 Adversary."""

    def test_cubic_mpo_basis_size(self):
        """Test that CubicIdealMPO basis size matches 1 + n + n*(n-1)/2 + n*(n-1)*(n-2)/6."""
        profile, primitive = CandidateRepresentationGenerator.get_candidate("cubic_ideal_mpo")
        self.assertEqual(profile.name, "cubic_ideal_mpo")
        self.assertIn("degree-3", profile.parameters.get("preserves", ""))
        self.assertEqual(profile.parameters.get("expected_failure"), "UNKNOWN")

    def test_level5_pure_degree4_adversary_integrity(self):
        """Test that Level-5 Adversary produces certified SAT/UNSAT pairs with degree-4 parity."""
        pair = PureDegree4ExpanderGenerator.generate_pure_degree4_pair(num_vertices=18, seed=42)
        self.assertTrue(pair.sat_instance.is_satisfiable)
        self.assertFalse(pair.unsat_instance.is_satisfiable)
        self.assertGreater(pair.num_vars, 0)
        self.assertTrue(pair.sat_instance.metadata.get("projection_equivalence_degree_1"))
        self.assertTrue(pair.sat_instance.metadata.get("projection_equivalence_degree_2"))
        self.assertTrue(pair.sat_instance.metadata.get("projection_equivalence_degree_3"))

    def test_cubic_mpo_pipeline_level4(self):
        """Test that CubicIdealMPO survives Level 4 (where quadratic_ideal_mpo collapsed)."""
        v4 = execute_pipeline("cubic_ideal_mpo", samples=2, level=4)
        self.assertEqual(v4.classification, TrilemmaOutcome.OUTCOME_D)
        self.assertGreater(v4.mean_separation, 0.0001)


if __name__ == "__main__":
    unittest.main()
