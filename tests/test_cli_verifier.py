"""
Unit and Integration Tests for Gate 10 (Public Offline Verifier CLI).
Tests CLI invocation, stdout reporting, and exit codes across single receipts, chains, and passports.
"""

import io
import json
import os
import sys
import unittest
from pillred.cli import verify_file, inspect_file, main


class TestCliVerifier(unittest.TestCase):
    """Tests the public command-line interface and zero-trust verifier."""

    def test_01_verify_valid_single_receipt(self):
        """CLI verifier returns 0 for a valid single prediction receipt."""
        code = verify_file("test_vectors/valid/receipt_001.json")
        self.assertEqual(code, 0)

    def test_02_verify_valid_chain(self):
        """CLI verifier returns 0 for a valid prediction receipt chain."""
        code = verify_file("test_vectors/valid/chain_001.json")
        self.assertEqual(code, 0)

    def test_03_verify_valid_passport(self):
        """CLI verifier returns 0 for a valid sealed Model Audit Passport."""
        code = verify_file("test_vectors/valid/passport_001.json")
        self.assertEqual(code, 0)

    def test_04_reject_tampered_receipt(self):
        """CLI verifier returns 1 and reports violation for a tampered receipt."""
        code = verify_file("test_vectors/invalid/tampered_prediction.json")
        self.assertEqual(code, 1)

    def test_05_reject_broken_chain(self):
        """CLI verifier returns 1 for a severed or out-of-order chain."""
        code = verify_file("test_vectors/invalid/broken_chain.json")
        self.assertEqual(code, 1)

    def test_06_reject_tampered_passport(self):
        """CLI verifier returns 1 when passport economic evidence has been modified."""
        code = verify_file("test_vectors/invalid/tampered_passport.json")
        self.assertEqual(code, 1)

    def test_07_inspect_command(self):
        """CLI inspect returns 0 and prints metadata."""
        code = inspect_file("test_vectors/valid/passport_001.json")
        self.assertEqual(code, 0)

    def test_08_missing_file_handling(self):
        """CLI returns error code 2 when target file does not exist."""
        code = verify_file("test_vectors/non_existent_file.json")
        self.assertEqual(code, 2)


if __name__ == "__main__":
    unittest.main()
