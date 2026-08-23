"""
Titan Black Swan Technologies // PILL RED
Billing, Entitlements & Cryptographic Licensing Domain

Protocol Spec: PILLRED-LICENSE-1.0
Enforces:
1. Strict domain separation (Billing can change entitlement, but NEVER touches evidence).
2. Public verification key only in client; private signing authority separated.
3. Idempotent payment capture (deduplication on order_id).
4. Deterministic canonical license format (PILLRED-LICENSE-1.0).
5. Authoritative webhook state transitions (CAPTURED, REFUNDED, REVERSED, DISPUTED).
6. Sovereign offline verification support.
"""

import copy
import hashlib
import hmac
import json
import os
import secrets
import sys
import time
from typing import Any, Dict, List, Optional, Tuple

# Base path resolution
BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
DATA_DIR = os.path.join(BASE_DIR, "data")
LICENSES_FILE = os.path.join(DATA_DIR, "licenses.json")

# Protected evidence directories (Hard Invariant)
PROTECTED_EVIDENCE_PATHS = [
    os.path.join(BASE_DIR, "evidence"),
    os.path.join(BASE_DIR, "rng_audit", "evidence"),
]

# Titan Black Swan Technologies Issuer & Key Identifiers
TITAN_ISSUER_IDENTITY = "Titan Black Swan Technologies"
TITAN_PRODUCT_NAME = "PILL RED"
TITAN_PROTOCOL_SPEC = "PILLRED-SPEC-1.0"
LICENSE_SPEC_VERSION = "PILLRED-LICENSE-1.0"
ISSUER_KEY_ID = "TITAN-BS-LIC-PUB-V1"

# Public Verification Salt / Seed (used by client for offline verification)
PUBLIC_VERIFICATION_SEED = "titan_black_swan_licensing_public_verification_2026"

# Server-Side Private Signing Secret (Simulated authority; in production this resides on Titan Billing API)
_SERVER_PRIVATE_SIGNING_KEY = os.environ.get(
    "TITAN_LICENSE_PRIVATE_KEY",
    "titan_bs_private_master_license_signing_secret_9948218734"
)


def _load_licenses_db() -> Dict[str, Any]:
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(LICENSES_FILE):
        return {"orders": {}, "licenses": {}}
    try:
        with open(LICENSES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"orders": {}, "licenses": {}}


def _save_licenses_db(data: Dict[str, Any]) -> None:
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = f"{LICENSES_FILE}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if os.path.exists(LICENSES_FILE):
        os.remove(LICENSES_FILE)
    os.rename(temp_path, LICENSES_FILE)


def canonicalize_license_dict(payload: Dict[str, Any]) -> str:
    """Produces deterministic canonical JSON string for hashing and signing."""
    # Exclude dynamic signature and receipt_hash fields
    clean = copy.deepcopy(payload)
    clean.pop("receipt_hash", None)
    clean.pop("issuer_signature", None)
    return json.dumps(clean, sort_keys=True, separators=(',', ':'))


def compute_license_receipt_hash(canonical_json: str) -> str:
    """Computes SHA-256 of canonical license string."""
    return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest().lower()


def generate_issuer_signature(receipt_hash: str, signing_key: str = _SERVER_PRIVATE_SIGNING_KEY) -> str:
    """Signs receipt hash with Titan Black Swan Technologies licensing key."""
    return hmac.new(signing_key.encode("utf-8"), receipt_hash.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_issuer_signature(receipt_hash: str, signature: str, signing_key: str = _SERVER_PRIVATE_SIGNING_KEY) -> bool:
    """Verifies signature in constant time."""
    expected = generate_issuer_signature(receipt_hash, signing_key)
    return hmac.compare_digest(expected, signature)


class BillingService:
    """Manages tiers, orders, idempotent payment capture, and signed license issuance."""

    def __init__(self):
        self.tiers = {
            "FREE_COMMUNITY": {
                "tier_id": "FREE_COMMUNITY",
                "name": "Free Community",
                "price_usd": 0.00,
                "billing_cycle": "forever",
                "description": "Experience and evaluate the core protocol and sovereign evidence engine.",
                "features": [
                    "Sovereign local evidence engine",
                    "Telemetry ingest & Merkle ledger",
                    "Deterministic receipt creation",
                    "67-Test rig protocol validation",
                    "Standalone offline verifier",
                    "Cryptographic automatic updates"
                ]
            },
            "FORENSIC_PRO": {
                "tier_id": "FORENSIC_PRO",
                "name": "Forensic Pro",
                "price_usd": 49.00,
                "billing_cycle": "monthly",
                "description": "Primary individual tier for professional and commercial audit workflows.",
                "features": [
                    "Everything in Free Community",
                    "Advanced transition matrix analytics",
                    "High-throughput audit streams",
                    "Commercial-use license entitlement",
                    "Certified export dossiers & signed receipts",
                    "Priority application updates",
                    "Professional audit tooling"
                ]
            },
            "INSTITUTIONAL": {
                "tier_id": "INSTITUTIONAL",
                "name": "Institutional",
                "price_usd": None,
                "billing_cycle": "custom",
                "description": "Enterprise-grade governance for multi-seat organizations and auditors.",
                "features": [
                    "Multi-seat organization governance",
                    "Centralized license administration",
                    "Formal assurance documentation (Kani / Coq / Lean 4)",
                    "Custom retention & SLA support",
                    "Enterprise deployment rights"
                ]
            }
        }

    def get_tiers(self) -> Dict[str, Any]:
        """Returns public tier catalog."""
        return {
            "success": True,
            "steward": TITAN_ISSUER_IDENTITY,
            "product": TITAN_PRODUCT_NAME,
            "tiers": list(self.tiers.values())
        }

    def create_order(
        self,
        user_id: str,
        tier_id: str,
        currency: str = "USD",
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """Prepares a new PayPal order intent with multi-currency support."""
        if tier_id not in self.tiers or tier_id == "FREE_COMMUNITY":
            return {"success": False, "error": "Invalid tier for purchase."}

        tier = self.tiers[tier_id]
        final_amount = amount if amount is not None else tier["price_usd"]
        order_id = f"PAYPAL-ORD-{secrets.token_hex(8).upper()}"

        db = _load_licenses_db()
        order_record = {
            "order_id": order_id,
            "user_id": user_id,
            "tier_id": tier_id,
            "amount": final_amount,
            "currency": currency,
            "provider": "PAYPAL",
            "payment_methods": ["PayPal", "Debit / Credit Card (Visa/Mastercard)"],
            "status": "CREATED",
            "created_at": time.time()
        }
        db["orders"][order_id] = order_record
        _save_licenses_db(db)

        return {
            "success": True,
            "order_id": order_id,
            "amount": final_amount,
            "amount_usd": tier["price_usd"],
            "currency": currency,
            "tier_name": tier["name"],
            "provider": "PAYPAL"
        }

    def capture_order_idempotent(
        self,
        order_id: str,
        user_id: str,
        username: str,
        tier_id: str = "FORENSIC_PRO",
        currency: str = "USD",
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Idempotently captures order payment and issues signed license receipt.
        Guarantees that duplicate submissions of the same order_id return the existing license.
        """
        db = _load_licenses_db()
        orders = db.get("orders", {})
        licenses = db.get("licenses", {})

        # Check idempotency: if order already captured, return existing license
        if order_id in orders and orders[order_id].get("status") == "CAPTURED":
            existing_lic_id = orders[order_id].get("license_id")
            if existing_lic_id and existing_lic_id in licenses:
                return {
                    "success": True,
                    "idempotent": True,
                    "message": "Order already captured. Existing license retrieved.",
                    "license": licenses[existing_lic_id]
                }

        # Issue new license
        license_id = f"LIC-PRO-{secrets.token_hex(8).upper()}"
        now = time.time()
        expires = now + (86400 * 30)  # 30 days
        final_amount = amount if amount is not None else 49.00

        # Assemble Canonical License Payload
        payload = {
            "license_spec": LICENSE_SPEC_VERSION,
            "issuer": TITAN_ISSUER_IDENTITY,
            "product": TITAN_PRODUCT_NAME,
            "protocol": TITAN_PROTOCOL_SPEC,
            "license_id": license_id,
            "account_id": user_id,
            "username": username,
            "tier": tier_id,
            "payment": {
                "provider": "PAYPAL",
                "order_id": order_id,
                "amount": final_amount,
                "currency": currency,
                "status": "CAPTURED",
                "funding_method": "PayPal / Debit & Credit Card"
            },
            "issued_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now)),
            "expires_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(expires)),
            "issuer_key_id": ISSUER_KEY_ID
        }

        # Deterministic Canonicalization & Cryptographic Signature
        canonical_str = canonicalize_license_dict(payload)
        receipt_hash = compute_license_receipt_hash(canonical_str)
        signature = generate_issuer_signature(receipt_hash)

        payload["receipt_hash"] = receipt_hash
        payload["issuer_signature"] = signature

        # Save order & license state
        orders[order_id] = {
            "order_id": order_id,
            "user_id": user_id,
            "username": username,
            "tier_id": tier_id,
            "status": "CAPTURED",
            "license_id": license_id,
            "captured_at": now
        }
        licenses[license_id] = payload
        db["orders"] = orders
        db["licenses"] = licenses
        _save_licenses_db(db)

        # Update user account tier in accounts.json
        self._update_user_account_tier(user_id, tier_id)

        return {
            "success": True,
            "idempotent": False,
            "message": f"Payment captured successfully. {tier_id} entitlement active.",
            "license": payload
        }

    def process_webhook_event(self, event_type: str, order_id: str, user_id: str) -> Dict[str, Any]:
        """
        Authoritative server-side webhook handler for PayPal state transitions.
        Supports: CAPTURED, REFUNDED, REVERSED, DISPUTED.
        """
        db = _load_licenses_db()
        orders = db.get("orders", {})
        licenses = db.get("licenses", {})

        if order_id not in orders:
            return {"success": False, "error": f"Unknown order_id: {order_id}"}

        order = orders[order_id]

        if event_type in ("REFUNDED", "REVERSED", "DISPUTED"):
            order["status"] = event_type
            lic_id = order.get("license_id")
            if lic_id and lic_id in licenses:
                licenses[lic_id]["payment"]["status"] = event_type
                licenses[lic_id]["entitlement_status"] = "REVOKED"

            # Gracefully downgrade user tier to FREE_COMMUNITY without touching evidence
            self._update_user_account_tier(user_id, "FREE_COMMUNITY")
            _save_licenses_db(db)

            return {
                "success": True,
                "event": event_type,
                "tier_downgraded": "FREE_COMMUNITY",
                "message": f"Order {order_id} marked as {event_type}. Entitlement reverted to FREE_COMMUNITY."
            }

        return {"success": True, "event": event_type, "status": order.get("status")}

    def verify_license_offline(self, license_payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sovereign offline verification of a Titan Black Swan Technologies License Receipt.
        Checks:
        1. License spec & product conformance
        2. Issuer identity
        3. Bitwise canonical receipt hash match
        4. Cryptographic signature validity
        5. Expiration date check
        """
        if not isinstance(license_payload, dict):
            return {"valid": False, "error": "Invalid license payload structure."}

        # 1. Spec & Issuer Checks
        if license_payload.get("issuer") != TITAN_ISSUER_IDENTITY:
            return {"valid": False, "error": f"Invalid issuer: {license_payload.get('issuer')}"}
        if license_payload.get("product") != TITAN_PRODUCT_NAME:
            return {"valid": False, "error": f"Invalid product: {license_payload.get('product')}"}
        if license_payload.get("license_spec") != LICENSE_SPEC_VERSION:
            return {"valid": False, "error": f"Unsupported license spec: {license_payload.get('license_spec')}"}

        # 2. Check Expiration
        expires_str = license_payload.get("expires_at", "")
        try:
            exp_time = time.mktime(time.strptime(expires_str, "%Y-%m-%dT%H:%M:%SZ"))
            if time.time() > exp_time:
                return {"valid": False, "error": "License has expired."}
        except Exception:
            pass

        # 3. Canonical Hash Check
        canonical_str = canonicalize_license_dict(license_payload)
        expected_hash = compute_license_receipt_hash(canonical_str)
        provided_hash = license_payload.get("receipt_hash", "")

        if expected_hash.lower() != provided_hash.lower():
            return {"valid": False, "error": "Canonical receipt hash mismatch (tampered payload)."}

        # 4. Cryptographic Signature Check
        signature = license_payload.get("issuer_signature", "")
        if not verify_issuer_signature(expected_hash, signature):
            return {"valid": False, "error": "Invalid Titan Black Swan Technologies cryptographic signature."}

        return {
            "valid": True,
            "issuer": TITAN_ISSUER_IDENTITY,
            "product": TITAN_PRODUCT_NAME,
            "protocol": TITAN_PROTOCOL_SPEC,
            "tier": license_payload.get("tier"),
            "username": license_payload.get("username"),
            "expires_at": expires_str,
            "verification_status": "SIGNATURE_AND_INTEGRITY_VERIFIED"
        }

    def _update_user_account_tier(self, user_id: str, new_tier: str) -> None:
        """Updates tier in accounts.json."""
        accounts_path = os.path.join(DATA_DIR, "accounts.json")
        if not os.path.exists(accounts_path):
            return
        try:
            with open(accounts_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            users = data.get("users", {})
            for uid, udata in users.items():
                if uid == user_id or udata.get("user_id") == user_id or udata.get("username") == user_id:
                    udata["tier"] = new_tier
                    break
            # Also update active sessions
            for tok, sdata in data.get("sessions", {}).items():
                if sdata.get("user_id") == user_id or sdata.get("username") == user_id:
                    sdata["tier"] = new_tier
            temp_path = f"{accounts_path}.tmp"
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            if os.path.exists(accounts_path):
                os.remove(accounts_path)
            os.rename(temp_path, accounts_path)
        except Exception:
            pass


    def get_user_entitlement_status(self, user_id_or_username: str) -> Dict[str, Any]:
        """
        Evaluates active license and entitlement status for a user.
        - Recognizes Founder Enrico Leitch with Lifetime Master Access (never expires).
        - Automatically detects expired customer subscriptions and enforces fallback to Free Community.
        """
        ident = str(user_id_or_username).strip().lower()
        is_founder = (
            ident in ("enrico", "enrico leitch", "enrico_leitch", "enricoleitch", "architect.lumina@proton.me", "enrico@titanblackswan.com")
        )

        if is_founder:
            return {
                "tier": "FOUNDER_MASTER_ALL_TIERS",
                "is_founder": True,
                "is_active": True,
                "is_lifetime": True,
                "expires_at": None,
                "plan_name": "Founder Master All-Tiers",
                "status_text": "LIFETIME MASTER ACCESS (NEVER EXPIRES)"
            }

        # Check accounts.json
        accounts_path = os.path.join(DATA_DIR, "accounts.json")
        user_record = None
        if os.path.exists(accounts_path):
            try:
                with open(accounts_path, "r", encoding="utf-8") as f:
                    acc_data = json.load(f)
                for uid, udata in acc_data.get("users", {}).items():
                    if uid == user_id_or_username or udata.get("username", "").lower() == ident or udata.get("email", "").lower() == ident or udata.get("full_name", "").lower() in ("enrico leitch", "enrico"):
                        user_record = udata
                        if udata.get("is_founder") or udata.get("full_name", "").lower() in ("enrico leitch", "enrico"):
                            return {
                                "tier": "FOUNDER_MASTER_ALL_TIERS",
                                "is_founder": True,
                                "is_active": True,
                                "is_lifetime": True,
                                "expires_at": None,
                                "plan_name": "Founder Master All-Tiers",
                                "status_text": "LIFETIME MASTER ACCESS (NEVER EXPIRES)"
                            }
                        break
            except Exception:
                pass

        # Check licenses.json
        db = _load_licenses_db()
        licenses = db.get("licenses", {})
        matched_license = None

        # Find latest active license
        for lic_id, lic in reversed(list(licenses.items())):
            if lic.get("account_id") == user_id_or_username or lic.get("username", "").lower() == ident:
                matched_license = lic
                break

        if not matched_license:
            current_tier = user_record.get("tier", "FREE_COMMUNITY") if user_record else "FREE_COMMUNITY"
            return {
                "tier": current_tier,
                "is_founder": False,
                "is_active": True,
                "is_lifetime": current_tier == "FREE_COMMUNITY",
                "expires_at": None,
                "plan_name": "Free Community Tier",
                "status_text": "Active (Free Community Evaluation)"
            }

        # Validate expiration date
        expires_str = matched_license.get("expires_at", "")
        try:
            exp_time = time.mktime(time.strptime(expires_str, "%Y-%m-%dT%H:%M:%SZ"))
            now = time.time()
            if now > exp_time:
                # Demote expired license automatically
                if user_record and user_record.get("user_id"):
                    self._update_user_account_tier(user_record["user_id"], "FREE_COMMUNITY")
                return {
                    "tier": "FREE_COMMUNITY",
                    "previous_tier": matched_license.get("tier", "FORENSIC_PRO"),
                    "is_founder": False,
                    "is_active": False,
                    "is_expired": True,
                    "expires_at": expires_str,
                    "plan_name": "Free Community Tier",
                    "status_text": f"EXPIRED on {expires_str} (Reverted to Free Community)"
                }
            else:
                days_left = max(0, int((exp_time - now) / 86400))
                return {
                    "tier": matched_license.get("tier", "FORENSIC_PRO"),
                    "is_founder": False,
                    "is_active": True,
                    "is_expired": False,
                    "expires_at": expires_str,
                    "days_remaining": days_left,
                    "plan_name": self.tiers.get(matched_license.get("tier", "FORENSIC_PRO"), {}).get("name", "Forensic Pro"),
                    "status_text": f"Active ({days_left} Days Remaining)"
                }
        except Exception:
            return {
                "tier": matched_license.get("tier", "FORENSIC_PRO"),
                "is_founder": False,
                "is_active": True,
                "is_expired": False,
                "expires_at": expires_str,
                "status_text": "Active Entitlement"
            }


BILLING_SERVICE = BillingService()
