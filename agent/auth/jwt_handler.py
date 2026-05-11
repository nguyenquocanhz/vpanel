"""
VPS Panel - JWT Token Handler
Creates and validates JWT access tokens.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import jwt, JWTError
from agent.config import settings

SECRET_KEY = settings["auth"]["jwt_secret"]
ALGORITHM = settings["auth"]["jwt_algorithm"]
ACCESS_TOKEN_EXPIRE_MINUTES = settings["auth"]["access_token_expire_minutes"]


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a new JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def create_refresh_token(data: dict) -> str:
    """Create a refresh token with longer expiry (7 days)."""
    return create_access_token(data, expires_delta=timedelta(days=7))
