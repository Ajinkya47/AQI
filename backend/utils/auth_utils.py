"""
Authentication utilities: password hashing (SHA-256 + salt) and JWT tokens.
No bcrypt dependency needed — avoids the passlib/bcrypt version conflict.
"""

import hashlib
import os
import hmac
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt

# ── Config ────────────────────────────────────────────────────────────────────
SECRET_KEY = "AIRAWARE_SECRET_CHANGE_IN_PRODUCTION_2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day


# ── Password helpers (PBKDF2-HMAC-SHA256) ─────────────────────────────────────
def hash_password(plain: str) -> str:
    """Hash a password with a random salt using PBKDF2."""
    salt = os.urandom(32)
    key = hashlib.pbkdf2_hmac(
        "sha256",
        plain.encode("utf-8"),
        salt,
        iterations=260000,
    )
    # Store as hex: salt_hex:key_hex
    return salt.hex() + ":" + key.hex()


def verify_password(plain: str, stored: str) -> bool:
    """Verify a password against a stored PBKDF2 hash."""
    try:
        salt_hex, key_hex = stored.split(":")
        salt = bytes.fromhex(salt_hex)
        expected_key = bytes.fromhex(key_hex)
        actual_key = hashlib.pbkdf2_hmac(
            "sha256",
            plain.encode("utf-8"),
            salt,
            iterations=260000,
        )
        return hmac.compare_digest(actual_key, expected_key)
    except Exception:
        return False


# ── JWT helpers ───────────────────────────────────────────────────────────────
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None