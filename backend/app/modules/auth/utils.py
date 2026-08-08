import hashlib
import secrets
from typing import Tuple


def generate_session_token() -> Tuple[str, str]:
    """Return (raw_token, token_hash)"""
    token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(token.encode("utf-8")).hexdigest()
    return token, token_hash


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
