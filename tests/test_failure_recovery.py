"""
Failure and Recovery Test Suite for PILL RED (Gate 8).
Simulates crashes, truncated writes, mid-chain corruptions, orphaned commitments, and chain resumption.
"""

import copy
import json
import os
import unittest
from pillred.protocol.client import PillRedClient
from pillred.protocol.passport import ModelAuditPassport
from pillred.protocol.verifier import ZeroTrustVerifier
from pillred.protocol.receipt import PredictionReceipt


class TestFailureAndRecovery(unittest.TestCase):
    """Verifies fault-tolerance, crash-recovery, and localized corruption detection."""

    def setUp(self):
        self.tmp_storage = "data/test_recovery_store.json"
        if os.path.exists(self.tmp_storage):
            os.remove(self.tmp_storage)

    def tearDown(self):
        if os.path.exists(self.tmp_storage):
            os.remove(self.tmp_storage)

    # -------------------------------------------------------------------------
    # Test 1: Truncated Stream Recovery (Power Loss / Partial Write Simulation)
    # -------------------------------------------------------------------------
    def test_01_truncated_stream_salvage(self):
        """When a file is truncated mid-write, salvage valid prefix and isolate corrupt tail."""
        client = PillRedClient(model_id="RECOVERY_MODEL", storage_path=self.tmp_storage)
        for i in range(1, 11):
            r = client.commit(f"EVENT_{i:02d}", "7" if i % 2 == 1 else "0")
            client.resolve(r.receipt_id, "7" if i % 2 == 1 else "0", payout_multiplier=10.0 if i % 2 == 1 else 0.0)

        # Read saved JSON and simulate hard cut mid-stream (truncating the last 50 bytes)
        with open(self.tmp_storage, "r", encoding="utf-8") as f:
            raw_text = f.read()

        truncated_text = raw_text[: len(raw_text) - 60] # Cuts off half of receipt #10

        # Attempting naive json.loads fails with JSONDecodeError
        with self.assertRaises(Exception):
            json.loads(truncated_text)

        # Robust Recovery Algorithm: Salvage valid prefix by scanning brackets/objects
        # Parse all complete JSON objects up to the cut
        salvaged_receipts = []
        decoder = json.JSONDecoder()
        # Find array start
        text = truncated_text.strip()
        if text.startswith("["):
            text = text[1:]
        
        while text:
            text = text.lstrip(" ,\r\n\t")
            if not text or text.startswith("]"):
                break
            try:
                obj, idx = decoder.raw_decode(text)
                salvaged_receipts.append(obj)
                text = text[idx:]
            except Exception:
                # Stop at the corrupt boundary
                break

        self.assertGreaterEqual(len(salvaged_receipts), 9)
        # Verify that the salvaged prefix is 100% cryptographically valid
        valid, vios, root = ZeroTrustVerifier.verify_chain(salvaged_receipts)
        self.assertTrue(valid, f"Salvaged prefix must be valid, got: {vios}")

    # -------------------------------------------------------------------------
    # Test 2: Localized Mid-Chain Corruption Isolation
    # -------------------------------------------------------------------------
    def test_02_localized_mid_chain_corruption(self):
        """Corrupting receipt #5 out of 10 isolates the exact boundary; #1..#4 remain verified."""
        client = PillRedClient(model_id="CORRUPTION_MODEL")
        for i in range(1, 11):
            r = client.commit(f"EVENT_{i:02d}", "0")
            client.resolve(r.receipt_id, "0", payout_multiplier=0.0)

        receipts_dicts = [r.to_dict() for r in client.receipts]

        # Corrupt receipt #5's actual outcome
        receipts_dicts[4]["actual_outcome"] = "7"

        # Chain audit fails at Receipt #5
        valid_chain, violations, _ = ZeroTrustVerifier.verify_chain(receipts_dicts)
        self.assertFalse(valid_chain)
        # Ensure corruption is specifically identified at Receipt #5
        self.assertTrue(any("Receipt #5" in v for v in violations))

        # Verify that prefix 1..4 remains completely valid
        valid_prefix, prefix_vios, _ = ZeroTrustVerifier.verify_chain(receipts_dicts[:4])
        self.assertTrue(valid_prefix)

    # -------------------------------------------------------------------------
    # Test 3: Crash-Restart and Chain Resumption
    # -------------------------------------------------------------------------
    def test_03_crash_restart_and_chain_resumption(self):
        """Process terminates cleanly, new client instance loads disk and resumes hash chain."""
        # Session 1: Writes 5 receipts
        client1 = PillRedClient(model_id="PERSIST_MODEL", storage_path=self.tmp_storage)
        for i in range(1, 6):
            r = client1.commit(f"EVENT_{i:02d}", "0")
            client1.resolve(r.receipt_id, "0", payout_multiplier=0.0)

        last_hash_s1 = client1.receipts[-1].receipt_hash

        # Session 2: Fresh client instance starts up and loads from disk
        client2 = PillRedClient(model_id="PERSIST_MODEL", storage_path=self.tmp_storage)
        self.assertEqual(len(client2.receipts), 5)
        self.assertEqual(client2.receipts[-1].receipt_hash, last_hash_s1)

        # Append 5 more receipts in Session 2
        for i in range(6, 11):
            r = client2.commit(f"EVENT_{i:02d}", "0")
            client2.resolve(r.receipt_id, "0", payout_multiplier=0.0)

        self.assertEqual(len(client2.receipts), 10)
        # Full 10-receipt chain must be 100% unbroken across sessions
        valid, vios, _ = ZeroTrustVerifier.verify_chain([r.to_dict() for r in client2.receipts])
        self.assertTrue(valid, f"Resumed chain must be intact: {vios}")

    # -------------------------------------------------------------------------
    # Test 4: Duplicate Event Injection Rejection
    # -------------------------------------------------------------------------
    def test_04_duplicate_event_rejection(self):
        """Injecting a duplicate receipt ID is rejected without compromising the valid stream."""
        client = PillRedClient(model_id="DUP_TEST_MODEL")
        r1 = client.commit("EVENT_01", "7")
        client.resolve(r1.receipt_id, "7", payout_multiplier=10.0)

        r2 = client.commit("EVENT_02", "0")
        client.resolve(r2.receipt_id, "0", payout_multiplier=0.0)

        # Attacker injects duplicate r1 into chain
        compromised_chain = [r1.to_dict(), r1.to_dict(), r2.to_dict()]
        valid, vios, _ = ZeroTrustVerifier.verify_chain(compromised_chain)
        self.assertFalse(valid)
        self.assertTrue(any("Duplicate receipt ID" in v for v in vios))

    # -------------------------------------------------------------------------
    # Test 5: Orphaned Pending Commitment Isolation
    # -------------------------------------------------------------------------
    def test_05_orphaned_pending_commitment_isolation(self):
        """Unsettled / orphaned commitments remain isolated and do not corrupt settled chain."""
        client = PillRedClient(model_id="ORPHAN_MODEL")
        r1 = client.commit("EVENT_01", "7")
        client.resolve(r1.receipt_id, "7", payout_multiplier=10.0)

        # Committed but never resolved (game server timeout)
        r_orphaned = client.commit("EVENT_02_TIMEOUT", "BAR")
        self.assertEqual(len(client._pending_receipts), 1)

        # Settled history only contains completed receipts
        self.assertEqual(len(client.receipts), 1)
        valid, vios, _ = ZeroTrustVerifier.verify_chain([r.to_dict() for r in client.receipts])
        self.assertTrue(valid)


if __name__ == "__main__":
    unittest.main()
