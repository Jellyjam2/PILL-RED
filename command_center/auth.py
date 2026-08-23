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

    def register_user(
        self,
        username: str = "",
        email: str = "",
        password: str = "",
        first_name: str = "",
        last_name: str = "",
        city: str = "",
        age: str = "",
        postal_code: str = "",
        birth_day: str = "",
        birth_month: str = "",
        birth_year: str = "",
        avatar: str = ""
    ) -> Dict[str, Any]:
        """Registers a new user with First Name, Surname, and extended profile details."""
        first_name = first_name.strip()
        last_name = last_name.strip()
        username = username.strip()
        email = email.strip().lower()
        city = city.strip()
        age = str(age).strip()
        postal_code = postal_code.strip()
        birth_day = str(birth_day).strip()
        birth_month = str(birth_month).strip()
        birth_year = str(birth_year).strip()
        avatar = avatar.strip()

        # If username not explicitly provided, generate from first & last name
        if not username and (first_name or last_name):
            clean_first = re.sub(r'[^a-zA-Z0-9_]', '', first_name).lower()
            clean_last = re.sub(r'[^a-zA-Z0-9_]', '', last_name).lower()
            username = f"{clean_first}_{clean_last}" if (clean_first and clean_last) else (clean_first or clean_last or email.split('@')[0])
        elif username and not first_name and not last_name:
            first_name = username.split('_')[0].capitalize()
            last_name = " ".join(part.capitalize() for part in username.split('_')[1:]) if len(username.split('_')) > 1 else ""

        if not username or len(username) < 2:
            return {"success": False, "error": "Name / Username must be at least 2 characters."}
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
                return {"success": False, "error": f"Account with username '@{username}' is already registered."}
            if udata.get("email", "").lower() == email:
                return {"success": False, "error": f"Email '{email}' is already registered."}

        # Hash password with memory-hard scrypt
        salt_hex, hash_hex = hash_password_memory_hard(password)
        user_id = f"USR-{secrets.token_hex(8).upper()}"

        # Founder / Steward Master Entitlement Recognition for Enrico Leitch
        full_name = f"{first_name} {last_name}".strip()
        is_founder = (
            full_name.lower() in ("enrico leitch", "enrico") or
            email in ("architect.lumina@proton.me", "enrico@titanblackswan.com") or
            username.lower() in ("enrico", "enrico_leitch", "enricoleitch")
        )

        user_tier = "FOUNDER_MASTER_ALL_TIERS" if is_founder else "FREE_COMMUNITY"

        user_record = {
            "user_id": user_id,
            "username": username,
            "first_name": first_name or (full_name.split()[0] if full_name else username),
            "last_name": last_name or (" ".join(full_name.split()[1:]) if len(full_name.split()) > 1 else ""),
            "full_name": full_name or username,
            "email": email,
            "salt": salt_hex,
            "password_hash": hash_hex,
            "tier": user_tier,
            "is_founder": is_founder,
            "expires_at": None if is_founder else None,
            "avatar": avatar,
            "city": city,
            "age": age,
            "postal_code": postal_code,
            "birth_day": birth_day,
            "birth_month": birth_month,
            "birth_year": birth_year,
            "organization": "Titan Black Swan Technologies",
            "created_at": time.time(),
            "last_login": time.time()
        }

        users[user_id] = user_record
        data["users"] = users
        _save_accounts(data)

        tier_msg = "Founder Master All-Tiers (Lifetime Access)" if is_founder else "Free Community Tier"
        return {
            "success": True,
            "user_id": user_id,
            "username": username,
            "first_name": user_record["first_name"],
            "last_name": user_record["last_name"],
            "full_name": user_record["full_name"],
            "email": email,
            "tier": user_tier,
            "is_founder": is_founder,
            "expires_at": None,
            "avatar": avatar,
            "city": city,
            "age": age,
            "postal_code": postal_code,
            "birthday": f"{birth_day}/{birth_month}/{birth_year}" if birth_year else "",
            "message": f"Account '{user_record['full_name']}' successfully registered with {tier_msg}."
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
            "first_name": matched_user.get("first_name", ""),
            "last_name": matched_user.get("last_name", ""),
            "full_name": matched_user.get("full_name", matched_user["username"]),
            "email": matched_user["email"],
            "tier": matched_user.get("tier", "FREE_COMMUNITY"),
            "is_founder": matched_user.get("is_founder", False),
            "avatar": matched_user.get("avatar", ""),
            "city": matched_user.get("city", ""),
            "age": matched_user.get("age", ""),
            "postal_code": matched_user.get("postal_code", ""),
            "birth_day": matched_user.get("birth_day", ""),
            "birth_month": matched_user.get("birth_month", ""),
            "birth_year": matched_user.get("birth_year", ""),
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

        bday = f"{matched_user.get('birth_day')}/{matched_user.get('birth_month')}/{matched_user.get('birth_year')}" if matched_user.get('birth_year') else ""

        return {
            "success": True,
            "session_token": session_token,
            "user_id": matched_user["user_id"],
            "username": matched_user["username"],
            "first_name": session_record["first_name"],
            "last_name": session_record["last_name"],
            "full_name": session_record["full_name"],
            "email": matched_user["email"],
            "tier": matched_user.get("tier", "FREE_COMMUNITY"),
            "is_founder": matched_user.get("is_founder", False),
            "avatar": matched_user.get("avatar", ""),
            "city": matched_user.get("city", ""),
            "age": matched_user.get("age", ""),
            "postal_code": matched_user.get("postal_code", ""),
            "birthday": bday,
            "created_at": matched_user.get("created_at", time.time()),
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

        bday = f"{session.get('birth_day')}/{session.get('birth_month')}/{session.get('birth_year')}" if session.get('birth_year') else ""

        return {
            "valid": True,
            "user_id": session.get("user_id", ""),
            "username": session["username"],
            "first_name": session.get("first_name", ""),
            "last_name": session.get("last_name", ""),
            "full_name": session.get("full_name", session["username"]),
            "email": session["email"],
            "tier": session.get("tier", "FREE_COMMUNITY"),
            "is_founder": session.get("is_founder", False),
            "avatar": session.get("avatar", ""),
            "city": session.get("city", ""),
            "age": session.get("age", ""),
            "postal_code": session.get("postal_code", ""),
            "birthday": bday,
            "created_at": session.get("created_at", time.time()),
            "organization": "Titan Black Swan Technologies"
        }

    def get_user_profile(self, user_id_or_username: str) -> Dict[str, Any]:
        """Retrieves full profile for a user."""
        data = _load_accounts()
        users = data.get("users", {})
        for uid, udata in users.items():
            if uid == user_id_or_username or udata.get("username", "").lower() == user_id_or_username.lower():
                bday = f"{udata.get('birth_day')}/{udata.get('birth_month')}/{udata.get('birth_year')}" if udata.get('birth_year') else ""
                return {
                    "success": True,
                    "user_id": udata.get("user_id", uid),
                    "username": udata.get("username", ""),
                    "first_name": udata.get("first_name", ""),
                    "last_name": udata.get("last_name", ""),
                    "full_name": udata.get("full_name", udata.get("username", "")),
                    "email": udata.get("email", ""),
                    "tier": udata.get("tier", "FREE_COMMUNITY"),
                    "is_founder": udata.get("is_founder", False),
                    "avatar": udata.get("avatar", ""),
                    "city": udata.get("city", ""),
                    "age": udata.get("age", ""),
                    "postal_code": udata.get("postal_code", ""),
                    "birthday": bday,
                    "birth_day": udata.get("birth_day", ""),
                    "birth_month": udata.get("birth_month", ""),
                    "birth_year": udata.get("birth_year", ""),
                    "created_at": udata.get("created_at", time.time()),
                    "organization": "Titan Black Swan Technologies"
                }
        return {"success": False, "error": "User profile not found."}

    def update_user_profile(self, identifier: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Updates user profile fields (Name, Surname, City, Postal, DOB, Avatar) sovereignly."""
        data = _load_accounts()
        users = data.get("users", {})
        matched_uid = None
        for uid, udata in users.items():
            if uid == identifier or udata.get("username", "").lower() == identifier.lower() or udata.get("email", "").lower() == identifier.lower():
                matched_uid = uid
                break

        if not matched_uid:
            return {"success": False, "error": "User not found."}

        target = users[matched_uid]
        if "first_name" in updates:
            target["first_name"] = str(updates["first_name"]).strip()
        if "last_name" in updates:
            target["last_name"] = str(updates["last_name"]).strip()
        if "first_name" in updates or "last_name" in updates:
            target["full_name"] = f"{target.get('first_name', '')} {target.get('last_name', '')}".strip() or target.get("username", "")
        if "city" in updates:
            target["city"] = str(updates["city"]).strip()
        if "postal_code" in updates:
            target["postal_code"] = str(updates["postal_code"]).strip()
        if "age" in updates:
            target["age"] = str(updates["age"]).strip()
        if "birth_day" in updates:
            target["birth_day"] = str(updates["birth_day"]).strip()
        if "birth_month" in updates:
            target["birth_month"] = str(updates["birth_month"]).strip()
        if "birth_year" in updates:
            target["birth_year"] = str(updates["birth_year"]).strip()
        if "avatar" in updates:
            target["avatar"] = str(updates["avatar"]).strip()

        _save_accounts(data)
        return {"success": True, "message": "Profile updated successfully.", "profile": self.get_user_profile(matched_uid)}

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

