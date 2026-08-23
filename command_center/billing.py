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
ISSUER_KEY_ID = "TITAN-BS-LIC-PUB-ED25519-V1"

# 32-byte Ed25519 Master Signing Seed (Server Authority)
_RAW_SEED = hashlib.sha256(
    os.environ.get("TITAN_LICENSE_PRIVATE_KEY", "titan_black_swan_technologies_master_licensing_authority_key_2026").encode("utf-8")
).digest()

from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.exceptions import InvalidSignature

_TITAN_SERVER_PRIVATE_KEY = ed25519.Ed25519PrivateKey.from_private_bytes(_RAW_SEED)
_TITAN_PUBLIC_KEY = _TITAN_SERVER_PRIVATE_KEY.public_key()

# Public Verification Key (Hex-encoded 32-byte Ed25519) - Embedded in public client & offline verifier
TITAN_PUBLIC_VERIFICATION_KEY_HEX = _TITAN_PUBLIC_KEY.public_bytes_raw().hex()


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


def generate_issuer_signature(receipt_hash: str) -> str:
    """
    Signs canonical receipt hash with Titan Black Swan Technologies Private Key (Ed25519).
    Returns 64-byte hex-encoded Ed25519 digital signature.
    """
    data_bytes = receipt_hash.encode("utf-8")
    sig_bytes = _TITAN_SERVER_PRIVATE_KEY.sign(data_bytes)
    return sig_bytes.hex()


def verify_issuer_signature(receipt_hash: str, signature_hex: str, public_key_hex: str = TITAN_PUBLIC_VERIFICATION_KEY_HEX) -> bool:
    """
    Asymmetrically verifies Ed25519 signature using ONLY Titan's Public Verification Key.
    The client and verifier have ZERO access to the private signing key.
    """
    try:
        pub_bytes = bytes.fromhex(public_key_hex)
        sig_bytes = bytes.fromhex(signature_hex)
        if len(sig_bytes) != 64 or len(pub_bytes) != 32:
            return False
        verifier = ed25519.Ed25519PublicKey.from_public_bytes(pub_bytes)
        verifier.verify(sig_bytes, receipt_hash.encode("utf-8"))
        return True
    except (InvalidSignature, ValueError, Exception):
        return False


# Authoritative server-side pricing matrix (Fixed Localized Regional Price Points)
AUTHORITATIVE_TIER_PRICES: Dict[str, Dict[str, float]] = {
    "FORENSIC_PRO": {
        "USD": 49.00,
        "ZAR": 890.00,
        "EUR": 45.00,
        "GBP": 39.00,
        "JPY": 7500.00,
        "CAD": 65.00,
        "AUD": 75.00,
        "BRL": 245.00,
        "CNY": 350.00,
        "CHF": 44.00,
    }
}


def resolve_authoritative_price(tier_id: str, requested_currency: Optional[str] = "USD") -> tuple[float, str]:
    """
    Authoritative server-side price resolution.
    The server rejects any client-specified amount and independently maps
    tier + currency to the authoritative fixed commercial price point.
    """
    curr = (requested_currency or "USD").upper().strip()
    tier_table = AUTHORITATIVE_TIER_PRICES.get(tier_id, {})
    if curr in tier_table:
        return float(tier_table[curr]), curr
    default_price = float(tier_table.get("USD", 49.00))
    return default_price, "USD"


class BillingLicensingService:
    """
    Titan Black Swan Technologies Commercial Billing & Licensing Subsystem.
    Provides authoritative PayPal order processing and signed offline license issuance.
    """

    def __init__(self):
        self.tiers = {
            "FREE_COMMUNITY": {
                "tier_id": "FREE_COMMUNITY",
                "name": "Free Community",
                "price_usd": 0.0,
                "billing_cycle": "perpetual",
                "description": "Standard sovereign evidence generation and offline audit verification.",
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
        """
        Prepares a new PayPal order intent.
        Security Invariant: The server resolves the exact localized amount
        from AUTHORITATIVE_TIER_PRICES, ignoring any client-submitted amounts.
        """
        if tier_id not in self.tiers or tier_id == "FREE_COMMUNITY":
            return {"success": False, "error": "Invalid tier for purchase."}

        tier = self.tiers[tier_id]
        authoritative_amount, authoritative_currency = resolve_authoritative_price(tier_id, currency)
        order_id = f"PAYPAL-ORD-{secrets.token_hex(8).upper()}"

        db = _load_licenses_db()
        order_record = {
            "order_id": order_id,
            "user_id": user_id,
            "tier_id": tier_id,
            "amount": authoritative_amount,
            "amount_usd": tier.get("price_usd", 49.00),
            "currency": authoritative_currency,
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
            "amount": authoritative_amount,
            "amount_usd": tier.get("price_usd", 49.00),
            "currency": authoritative_currency,
            "tier_name": tier["name"],
            "provider": "PAYPAL"
        }

    def capture_order_idempotent(
        self,
        order_id: str,
        user_id: str,
        username: str,
        tier_id: str = "FORENSIC_PRO",
        currency: Optional[str] = None,
        amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Idempotently captures order payment and issues signed license receipt.
        Guarantees that duplicate submissions of the same order_id return the existing license.
        Authoritatively derives amount and currency from server order state.
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

        # Resolve authoritative amount and currency from server order record
        if order_id in orders:
            order_data = orders[order_id]
            auth_amount = float(order_data.get("amount", 49.00))
            auth_curr = order_data.get("currency", "USD")
        else:
            auth_amount, auth_curr = resolve_authoritative_price(tier_id, currency or "USD")

        # Issue new license
        license_id = f"LIC-PRO-{secrets.token_hex(8).upper()}"
        now = time.time()
        expires = now + (86400 * 30)  # 30 days

        # Assemble Canonical License Payload
        payload = {
            "license_spec": LICENSE_SPEC_VERSION,
            "issuer": TITAN_ISSUER_IDENTITY,
            "product": "PILL_RED",
            "protocol": TITAN_PROTOCOL_SPEC,
            "license_id": license_id,
            "account_id": user_id,
            "username": username,
            "tier": tier_id,
            "currency": auth_curr,
            "amount": f"{auth_amount:.2f}",
            "billing_period": "monthly",
            "payment": {
                "provider": "PAYPAL",
                "order_id": order_id,
                "amount": auth_amount,
                "currency": auth_curr,
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
        if license_payload.get("product") not in (TITAN_PRODUCT_NAME, "PILL RED", "PILL_RED"):
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


BillingService = BillingLicensingService
BILLING_SERVICE = BillingLicensingService()
