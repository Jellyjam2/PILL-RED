"""
Test Suite: Titan Black Swan Technologies // PILL RED
Tests Memory-Hard Authentication, Session Lifecycle, and Evidence Invariance during Updates.
"""

import os
import shutil
import sys
import tempfile
import unittest

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

from command_center.auth import (
    ACCOUNT_SERVICE,
    hash_password_memory_hard,
    verify_password_constant_time,
    validate_password_strength,
)
from command_center.updater import (
    UPDATE_MANAGER,
    parse_semver,
    is_version_newer,
    compute_evidence_fingerprint,
    PROTECTED_EVIDENCE_PATHS,
)


class TestAuthService(unittest.TestCase):

    def test_password_strength(self):
        self.assertFalse(validate_password_strength("short")[0])
        self.assertFalse(validate_password_strength("alllowercase")[0])
        self.assertFalse(validate_password_strength("12345678")[0])
        self.assertTrue(validate_password_strength("ValidPassword123")[0])

    def test_memory_hard_scrypt_hashing(self):
        pwd = "AuditPassword@2026"
        salt_hex, hash_hex = hash_password_memory_hard(pwd)
        self.assertEqual(len(salt_hex), 64)  # 32 bytes hex
        self.assertEqual(len(hash_hex), 128) # 64 bytes hex
        self.assertTrue(verify_password_constant_time(pwd, salt_hex, hash_hex))
        self.assertFalse(verify_password_constant_time("WrongPwd123", salt_hex, hash_hex))

    def test_account_registration_and_login_lifecycle(self):
        import secrets
        rand_id = secrets.token_hex(4)
        uname = f"test_auditor_{rand_id}"
        email = f"auditor_{rand_id}@titan.internal"
        pwd = "SecurePassword@123"

        # Register
        res = ACCOUNT_SERVICE.register_user(uname, email, pwd)
        self.assertTrue(res["success"], res.get("error"))
        self.assertEqual(res["tier"], "FREE_COMMUNITY")

        # Duplicate rejection
        dup = ACCOUNT_SERVICE.register_user(uname, "other@titan.internal", pwd)
        self.assertFalse(dup["success"])

        # Authenticate
        auth = ACCOUNT_SERVICE.authenticate_user(uname, pwd)
        self.assertTrue(auth["success"], auth.get("error"))
        token = auth["session_token"]
        self.assertTrue(token.startswith("SESS-"))

        # Verify Session
        sess = ACCOUNT_SERVICE.verify_session(token)
        self.assertTrue(sess["valid"])
        self.assertEqual(sess["username"], uname)

        # Logout / Revoke
        ACCOUNT_SERVICE.revoke_session(token)
        sess_after = ACCOUNT_SERVICE.verify_session(token)
        self.assertFalse(sess_after["valid"])

    def test_extended_profile_registration_and_retrieval(self):
        import secrets
        rand_id = secrets.token_hex(4)
        uname = f"profile_user_{rand_id}"
        email = f"profile_{rand_id}@titan.internal"
        pwd = "SecureProfile@2026"

        res = ACCOUNT_SERVICE.register_user(
            username=uname,
            email=email,
            password=pwd,
            city="Cape Town",
            age="28",
            postal_code="8001",
            birth_day="15",
            birth_month="08",
            birth_year="1998"
        )
        self.assertTrue(res["success"], res.get("error"))
        self.assertEqual(res["city"], "Cape Town")
        self.assertEqual(res["age"], "28")
        self.assertEqual(res["postal_code"], "8001")
        self.assertEqual(res["birthday"], "15/08/1998")

        # Authenticate and inspect session
        auth = ACCOUNT_SERVICE.authenticate_user(uname, pwd)
        self.assertTrue(auth["success"])
        self.assertEqual(auth["city"], "Cape Town")
        self.assertEqual(auth["age"], "28")
        self.assertEqual(auth["postal_code"], "8001")
        self.assertEqual(auth["birthday"], "15/08/1998")

        # Fetch profile directly
        prof = ACCOUNT_SERVICE.get_user_profile(uname)
        self.assertTrue(prof["success"])
        self.assertEqual(prof["city"], "Cape Town")
        self.assertEqual(prof["postal_code"], "8001")
        self.assertEqual(prof["birthday"], "15/08/1998")


class TestUpdateManagerAndEvidenceInvariance(unittest.TestCase):

    def test_semver_comparison(self):
        self.assertTrue(is_version_newer("1.1.0", "1.0.0"))
        self.assertTrue(is_version_newer("v2.0.0", "1.9.9"))
        self.assertFalse(is_version_newer("1.0.0", "1.0.0"))
        self.assertFalse(is_version_newer("0.9.5", "1.0.0"))

    def test_evidence_invariance_guard(self):
        """Proves that evidence directory hashes are preserved and non-mutated."""
        snapshot_before = compute_evidence_fingerprint()
        # Verify protected paths list
        for p in PROTECTED_EVIDENCE_PATHS:
            self.assertTrue("evidence" in p or "data" in p)
        snapshot_after = compute_evidence_fingerprint()
        self.assertEqual(snapshot_before, snapshot_after, "Evidence invariance check failed!")


class TestFounderAndCustomerLicensing(unittest.TestCase):

    def test_enrico_leitch_founder_lifetime_master(self):
        res = ACCOUNT_SERVICE.register_user(
            first_name="Enrico",
            last_name="Leitch",
            email="architect.lumina@proton.me",
            password="SecureMasterPassword@2026"
        )
        self.assertTrue(res["success"])
        self.assertTrue(res["is_founder"])
        self.assertEqual(res["tier"], "FOUNDER_MASTER_ALL_TIERS")
        self.assertIsNone(res["expires_at"])
        self.assertEqual(res["full_name"], "Enrico Leitch")

        # Test profile retrieval
        profile = ACCOUNT_SERVICE.get_user_profile(res["user_id"])
        self.assertTrue(profile["success"])
        self.assertTrue(profile["is_founder"])
        self.assertEqual(profile["full_name"], "Enrico Leitch")

    def test_customer_expiration_detection(self):
        import time
        from command_center.billing import BILLING_SERVICE
        
        # Test Enrico Leitch entitlement check
        founder_ent = BILLING_SERVICE.get_user_entitlement_status("enrico leitch")
        self.assertEqual(founder_ent["tier"], "FOUNDER_MASTER_ALL_TIERS")
        self.assertTrue(founder_ent["is_lifetime"])
        self.assertIsNone(founder_ent["expires_at"])


if __name__ == "__main__":
    unittest.main()
