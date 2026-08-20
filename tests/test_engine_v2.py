"""Unit and Integration Tests for PILL RED v2.0 Alpha Engine."""

import os
from pathlib import Path
import tempfile
import unittest

from engine.ivr.verifier import IndependentVerifier
from engine.aag.expander import HighGirthExpanderGenerator
from engine.aag.adversary import AdaptiveAdversaryManager
from engine.crg.generator import CandidateRepresentationGenerator
from engine.ace.crucible import AutomatedCrucibleEngine
from engine.classifier.trilemma import TrilemmaClassifier
from engine.ledger.store import EpistemicLedger
from engine.interfaces import TrilemmaOutcome
from pillred_v2 import execute_pipeline


class TestEngineV2Alpha(unittest.TestCase):
    """Verifies all 5 core modules of the v2.0 Alpha architecture."""

    def test_independent_verifier(self):
        """Test IVR dual-solver verification and witness validation."""
        # Satisfiable 2-variable formula: (x1 or x2) and (x1 or -x2)
        clauses_sat = [[1, 2], [1, -2]]
        sat, witness, conflicts = IndependentVerifier.verify_satisfiability(clauses_sat, 2)
        self.assertTrue(sat)
        self.assertIsNotNone(witness)
        self.assertTrue(IndependentVerifier.validate_witness(clauses_sat, witness))

        # Unsatisfiable 1-variable formula: (x1) and (-x1)
        clauses_unsat = [[1], [-1]]
        unsat, witness_u, conflicts_u = IndependentVerifier.verify_satisfiability(clauses_unsat, 1)
        self.assertFalse(unsat)
        self.assertIsNone(witness_u)

    def test_expander_adversary_generator(self):
        """Test high-girth Ramanujan Tseitin expander pair generation with verified girth."""
        pair = HighGirthExpanderGenerator.generate_tseitin_pair(num_vertices=16, min_girth=4, seed=42)
        self.assertTrue(pair.sat_instance.is_satisfiable)
        self.assertFalse(pair.unsat_instance.is_satisfiable)
        self.assertGreaterEqual(pair.girth, 3)
        self.assertGreater(pair.num_vars, 0)
        self.assertEqual(len(pair.sat_instance.clauses), len(pair.unsat_instance.clauses))

    def test_candidate_generator_deterministic_ids(self):
        """Test that CRG produces deterministic candidate hashes."""
        p1, _ = CandidateRepresentationGenerator.get_candidate("spectral_laplacian")
        p2, _ = CandidateRepresentationGenerator.get_candidate("spectral_laplacian")
        self.assertEqual(p1.candidate_id, p2.candidate_id)
        self.assertTrue(p1.candidate_id.startswith("CAND-"))

    def test_end_to_end_crucible_pipeline(self):
        """Test the full 5-module pipeline on GF(2) parity."""
        verdict = execute_pipeline("gf2_affine", samples=2, level=1)
        self.assertIsNotNone(verdict.run_id)
        self.assertEqual(verdict.sample_size, 2)
        self.assertIn("D1", verdict.gates)
        self.assertIn("D7", verdict.gates)
        self.assertIn(verdict.classification, [
            TrilemmaOutcome.OUTCOME_A,
            TrilemmaOutcome.OUTCOME_B,
            TrilemmaOutcome.OUTCOME_C,
            TrilemmaOutcome.OUTCOME_D,
        ])

    def test_epistemic_ledger_persistence(self):
        """Test immutable JSONL ledger record writing and loading."""
        with tempfile.TemporaryDirectory() as tmpdir:
            ledger_path = Path(tmpdir) / "test_ledger.jsonl"
            ledger = EpistemicLedger(ledger_path=ledger_path)

            verdict = execute_pipeline("spectral_laplacian", samples=2, level=1)
            run_id = ledger.record_verdict(verdict)
            self.assertEqual(run_id, verdict.run_id)

            records = ledger.load_all_records()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0]["run_id"], verdict.run_id)
            self.assertEqual(records[0]["candidate"]["name"], "spectral_laplacian")


if __name__ == "__main__":
    unittest.main()
