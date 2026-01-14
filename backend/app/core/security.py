"""Security utilities for authentication."""

from datetime import timedelta

from fastapi_users.jwt import SecretType, generate_jwt
from fastapi_users.password import PasswordHelper
from jose import jwt

from app.core.config import settings

# Password helper
password_helper = PasswordHelper()

# JWT secret
SECRET = settings.secret_key


def generate_token(user_id: str) -> str:
    """Generate JWT token for user."""
    lifetime = timedelta(minutes=settings.access_token_expire_minutes)
    return generate_jwt(
        {"sub": str(user_id), "type": "access"},
        SECRET,
        lifetime,
    )


def decode_token(token: str) -> dict:
    """Decode JWT token."""
    return jwt.decode(token, SECRET, algorithms=[settings.algorithm])


