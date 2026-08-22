"""
Titan Black Swan Technologies // PILL RED
Account Service & Local-First Authentication Engine

Enforces strict domain separation between Account Data (credentials, sessions, tiers)
and Local Evidence (cryptographic ledgers, Merkle trees, and passports).
Uses memory-hard key derivation (scrypt) with cryptographically secure random salts.
"""

import hashlib
import hmac
import json
import os
import re
import secrets
import sys
import time
from typing import Any, Dict, Optional, Tuple

# Base path resolution for frozen bundle vs dev
BASE_DIR = getattr(sys, '_MEIPASS', os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
AUTH_STORE_DIR = os.path.join(BASE_DIR, "data")
AUTH_STORE_PATH = os.path.join(AUTH_STORE_DIR, "accounts.json")


def _get_auth_file_path() -> str:
    # Ensure data directory exists
    os.makedirs(AUTH_STORE_DIR, exist_ok=True)
    return AUTH_STORE_PATH


def _load_accounts() -> Dict[str, Any]:
    path = _get_auth_file_path()
    if not os.path.exists(path):
        return {"users": {}, "sessions": {}}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"users": {}, "sessions": {}}


def _save_accounts(data: Dict[str, Any]) -> None:
    path = _get_auth_file_path()
    temp_path = f"{path}.tmp"
    with open(temp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    if os.path.exists(path):
        os.remove(path)
    os.rename(temp_path, path)


def hash_password_memory_hard(password: str, salt_hex: Optional[str] = None) -> Tuple[str, str]:
    """
    Derives a memory-hard password hash using scrypt (N=16384, r=8, p=1, maxmem=32MB).
    Returns (salt_hex, hash_hex).
    """
    if salt_hex is None:
        salt = secrets.token_bytes(32)
        salt_hex = salt.hex()
    else:
        salt = bytes.fromhex(salt_hex)

    derived = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=16384,
        r=8,
        p=1,
        maxmem=33554432,
        dklen=64
    )
    return salt_hex, derived.hex()


def verify_password_constant_time(password: str, salt_hex: str, expected_hash_hex: str) -> bool:
    """Verifies password using scrypt in constant time."""
    _, actual_hash = hash_password_memory_hard(password, salt_hex=salt_hex)
    return hmac.compare_digest(actual_hash, expected_hash_hex)


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """Validates that password meets high-assurance security criteria."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not re.search(r"[A-Za-z]", password):
        return False, "Password must contain at least one letter."
    if not re.search(r"[0-9]", password):
        return False, "Password must contain at least one number."
    return True, "Password meets security requirements."


class AccountService:
    """Manages user identity, memory-hard authentication, and sovereign sessions."""

    def __init__(self):
        self._ensure_initialized()

    def _ensure_initialized(self):
        data = _load_accounts()
        if "users" not in data:
            data["users"] = {}
        if "sessions" not in data:
            data["sessions"] = {}
        _save_accounts(data)

    def register_user(self, username: str, email: str, password: str) -> Dict[str, Any]:
        """Registers a new user under the Free Community Tier."""
        username = username.strip()
        email = email.strip().lower()

        if not username or len(username) < 3:
            return {"success": False, "error": "Username must be at least 3 characters."}
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", email):
            return {"success": False, "error": "Invalid email address format."}

        is_valid_pwd, msg = validate_password_strength(password)
        if not is_valid_pwd:
            return {"success": False, "error": msg}

        data = _load_accounts()
        users = data.get("users", {})

        # Check uniqueness
        for uid, udata in users.items():
            if udata.get("username", "").lower() == username.lower():
                return {"success": False, "error": f"Username '@{username}' is already registered."}
            if udata.get("email", "").lower() == email:
                return {"success": False, "error": f"Email '{email}' is already registered."}

        # Hash password with memory-hard scrypt
        salt_hex, hash_hex = hash_password_memory_hard(password)
        user_id = f"USR-{secrets.token_hex(8).upper()}"

        user_record = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "salt": salt_hex,
            "password_hash": hash_hex,
            "tier": "FREE_COMMUNITY",
            "organization": "Titan Black Swan Technologies",
            "created_at": time.time(),
            "last_login": time.time()
        }

        users[user_id] = user_record
        data["users"] = users
        _save_accounts(data)

        return {
            "success": True,
            "user_id": user_id,
            "username": username,
            "email": email,
            "tier": "FREE_COMMUNITY",
            "message": f"Account '@{username}' successfully created under Free Community Tier."
        }

    def authenticate_user(self, identifier: str, password: str) -> Dict[str, Any]:
        """Authenticates user with username or email, returning a cryptographic session token."""
        identifier = identifier.strip().lower()
        data = _load_accounts()
        users = data.get("users", {})

        matched_user = None
        for uid, udata in users.items():
            if udata.get("username", "").lower() == identifier or udata.get("email", "").lower() == identifier:
                matched_user = udata
                break

        if not matched_user:
            return {"success": False, "error": "Invalid username/email or password."}

        # Verify password
        is_valid = verify_password_constant_time(
            password=password,
            salt_hex=matched_user["salt"],
            expected_hash_hex=matched_user["password_hash"]
        )

        if not is_valid:
            return {"success": False, "error": "Invalid username/email or password."}

        # Issue session token
        session_token = f"SESS-{secrets.token_hex(24)}"
        session_record = {
            "session_token": session_token,
            "user_id": matched_user["user_id"],
            "username": matched_user["username"],
            "email": matched_user["email"],
            "tier": matched_user.get("tier", "FREE_COMMUNITY"),
            "organization": "Titan Black Swan Technologies",
            "created_at": time.time(),
            "expires_at": time.time() + (86400 * 30)  # 30-day session
        }

        sessions = data.get("sessions", {})
        sessions[session_token] = session_record
        data["sessions"] = sessions

        # Update last login
        matched_user["last_login"] = time.time()
        _save_accounts(data)

        return {
            "success": True,
            "session_token": session_token,
            "username": matched_user["username"],
            "email": matched_user["email"],
            "tier": matched_user.get("tier", "FREE_COMMUNITY"),
            "organization": "Titan Black Swan Technologies"
        }

    def verify_session(self, session_token: str) -> Dict[str, Any]:
        """Verifies active session token validity."""
        if not session_token:
            return {"valid": False}
        data = _load_accounts()
        sessions = data.get("sessions", {})
        session = sessions.get(session_token)

        if not session:
            return {"valid": False}

        if time.time() > session.get("expires_at", 0):
            del sessions[session_token]
            data["sessions"] = sessions
            _save_accounts(data)
            return {"valid": False, "error": "Session expired."}

        return {
            "valid": True,
            "username": session["username"],
            "email": session["email"],
            "tier": session.get("tier", "FREE_COMMUNITY"),
            "organization": "Titan Black Swan Technologies"
        }

    def revoke_session(self, session_token: str) -> Dict[str, Any]:
        """Logs out and revokes active session token."""
        data = _load_accounts()
        sessions = data.get("sessions", {})
        if session_token in sessions:
            del sessions[session_token]
            data["sessions"] = sessions
            _save_accounts(data)
        return {"success": True, "message": "Logged out successfully."}


ACCOUNT_SERVICE = AccountService()
