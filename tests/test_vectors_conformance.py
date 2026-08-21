"""
Python Test-Vector Conformance Suite for Gate 4A.
Consumes test_vectors/ against test_vector_manifest.json without server contact.
"""

import json
import os
import unittest
from pillred.protocol.verifier import ZeroTrustVerifier


class TestVectorConformancePython(unittest.TestCase):
    """Verifies that the Python verifier strictly conforms to the frozen test vector manifest."""

    def setUp(self):
        self.manifest_path = "test_vectors/expected/test_vector_manifest.json"
        self.assertTrue(os.path.exists(self.manifest_path), "Manifest must exist at expected path")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            self.manifest = json.load(f)

    def test_vector_01_valid_receipt_001(self):
        """Python Verifier audits valid_receipt_001 against manifest expected hashes."""
        v_meta = self.manifest["vectors"]["valid_receipt_001"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            r = json.load(f)

        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r)
        self.assertTrue(is_valid, f"Expected VALID, got violations: {violations}")
        self.assertEqual(r["commit_hash"], v_meta["expected_commit_hash"])
        self.assertEqual(r["receipt_hash"], v_meta["expected_receipt_hash"])

    def test_vector_02_valid_receipt_002(self):
        """Python Verifier audits valid_receipt_002 against manifest expected hashes."""
        v_meta = self.manifest["vectors"]["valid_receipt_002"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            r = json.load(f)

        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r)
        self.assertTrue(is_valid, f"Expected VALID, got violations: {violations}")
        self.assertEqual(r["commit_hash"], v_meta["expected_commit_hash"])
        self.assertEqual(r["receipt_hash"], v_meta["expected_receipt_hash"])

    def test_vector_03_valid_chain_001(self):
        """Python Verifier audits valid_chain_001 against manifest expected Merkle root."""
        v_meta = self.manifest["vectors"]["valid_chain_001"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            chain = json.load(f)

        is_valid, violations, merkle_root = ZeroTrustVerifier.verify_chain(chain)
        self.assertTrue(is_valid, f"Expected VALID chain, got violations: {violations}")
        self.assertEqual(len(chain), v_meta["expected_count"])
        self.assertEqual(merkle_root, v_meta["expected_merkle_root"])

    def test_vector_04_invalid_tampered_prediction(self):
        """Python Verifier rejects tampered_prediction.json with Commit hash mismatch."""
        v_meta = self.manifest["vectors"]["invalid_tampered_prediction"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            r = json.load(f)

        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r)
        self.assertFalse(is_valid)
        self.assertTrue(any(v_meta["expected_error"] in v for v in violations))

    def test_vector_05_invalid_broken_chain(self):
        """Python Verifier rejects broken_chain.json with Broken chain linkage."""
        v_meta = self.manifest["vectors"]["invalid_broken_chain"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            chain = json.load(f)

        is_valid, violations, _ = ZeroTrustVerifier.verify_chain(chain)
        self.assertFalse(is_valid)
        self.assertTrue(any(v_meta["expected_error"] in v for v in violations))

    def test_vector_06_invalid_invalid_timestamp(self):
        """Python Verifier rejects invalid_timestamp.json with Causal violation."""
        v_meta = self.manifest["vectors"]["invalid_invalid_timestamp"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            r = json.load(f)

        is_valid, violations = ZeroTrustVerifier.verify_single_receipt(r)
        self.assertFalse(is_valid)
        self.assertTrue(any(v_meta["expected_error"] in v for v in violations))

    def test_vector_07_valid_passport_001(self):
        """Python Verifier audits valid_passport_001.json against manifest expected hash."""
        from pillred.protocol.passport import ModelAuditPassport
        v_meta = self.manifest["vectors"]["valid_passport_001"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            p = json.load(f)

        is_valid, violations = ModelAuditPassport.verify_passport(p)
        self.assertTrue(is_valid, f"Expected VALID passport, got violations: {violations}")
        self.assertEqual(p["passport_hash"], v_meta["expected_passport_hash"])

    def test_vector_08_invalid_tampered_passport(self):
        """Python Verifier rejects tampered_passport.json with Economic evidence hash mismatch."""
        from pillred.protocol.passport import ModelAuditPassport
        v_meta = self.manifest["vectors"]["invalid_tampered_passport"]
        with open(v_meta["file"], "r", encoding="utf-8") as f:
            p = json.load(f)

        is_valid, violations = ModelAuditPassport.verify_passport(p)
        self.assertFalse(is_valid)
        self.assertTrue(any(v_meta["expected_error"] in v for v in violations))


if __name__ == "__main__":
    unittest.main()
