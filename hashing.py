from typing import Tuple
import os
import hashlib
import hmac
import secrets


def hash_new_password(password: str) -> Tuple[str, str]:
    salt = os.urandom(16)
    pw_hash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    return salt.hex(), pw_hash.hex()


def is_correct_password(salt: bytes, pw_hash: bytes, password: str) -> bool:
    return hmac.compare_digest(
        pw_hash,
        hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
    )


def session_token() -> str:
    return secrets.token_urlsafe(16)
