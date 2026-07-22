"""
MotoMod AI — Security Module
JWT token creation/validation, password hashing, RBAC utilities
"""
from datetime import datetime, timedelta, timezone
from typing import Any, Optional
from uuid import UUID

from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger(__name__)


# Token types
ACCESS_TOKEN_TYPE = "access"
REFRESH_TOKEN_TYPE = "refresh"
EMAIL_VERIFY_TOKEN_TYPE = "email_verify"
PASSWORD_RESET_TOKEN_TYPE = "password_reset"


# ─── Password Utilities ───────────────────────────────────────────────────────

def hash_password(plain_password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def check_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password strength.
    Returns (is_valid, error_message)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long."
    if not any(c.isupper() for c in password):
        return False, "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return False, "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return False, "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        return False, "Password must contain at least one special character."
    return True, ""


# ─── JWT Utilities ────────────────────────────────────────────────────────────

def _create_token(
    subject: str,
    token_type: str,
    expires_delta: timedelta,
    extra_claims: Optional[dict] = None,
) -> str:
    """
    Create a signed JWT token.

    Args:
        subject: User ID or email as the JWT subject.
        token_type: Type of token (access, refresh, etc.).
        expires_delta: Token lifetime.
        extra_claims: Additional claims to embed.
    """
    now = datetime.now(timezone.utc)
    claims = {
        "sub": str(subject),
        "type": token_type,
        "iat": now,
        "exp": now + expires_delta,
    }
    if extra_claims:
        claims.update(extra_claims)
    return jwt.encode(claims, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_access_token(
    user_id: UUID | str,
    role: str,
    permissions: list[str],
) -> str:
    """Create a short-lived access token with role and permission claims."""
    return _create_token(
        subject=str(user_id),
        token_type=ACCESS_TOKEN_TYPE,
        expires_delta=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES),
        extra_claims={
            "role": role,
            "permissions": permissions,
        },
    )


def create_refresh_token(user_id: UUID | str) -> str:
    """Create a long-lived refresh token."""
    return _create_token(
        subject=str(user_id),
        token_type=REFRESH_TOKEN_TYPE,
        expires_delta=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS),
    )


def create_email_verification_token(user_id: UUID | str, email: str) -> str:
    """Create a token for email verification (24h expiry)."""
    return _create_token(
        subject=str(user_id),
        token_type=EMAIL_VERIFY_TOKEN_TYPE,
        expires_delta=timedelta(hours=24),
        extra_claims={"email": email},
    )


def create_password_reset_token(user_id: UUID | str, email: str) -> str:
    """Create a token for password reset (1h expiry)."""
    return _create_token(
        subject=str(user_id),
        token_type=PASSWORD_RESET_TOKEN_TYPE,
        expires_delta=timedelta(hours=1),
        extra_claims={"email": email},
    )


def decode_token(token: str, expected_type: str) -> dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: The raw JWT string.
        expected_type: The expected token type claim.

    Returns:
        Decoded claims dictionary.

    Raises:
        HTTPException: If token is invalid, expired, or wrong type.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        token_type: str = payload.get("type", "")
        if token_type != expected_type:
            logger.warning(
                "token_type_mismatch",
                expected=expected_type,
                received=token_type,
            )
            raise credentials_exception
        sub: str = payload.get("sub", "")
        if not sub:
            raise credentials_exception
        return payload
    except JWTError as e:
        logger.warning("jwt_decode_error", error=str(e))
        raise credentials_exception


# ─── RBAC ────────────────────────────────────────────────────────────────────

class RolePermissions:
    """Static role-permission mapping."""

    PERMISSIONS = {
        "admin": [
            "bikes:read", "bikes:write", "bikes:delete",
            "brands:read", "brands:write", "brands:delete",
            "mods:read", "mods:write", "mods:delete",
            "users:read", "users:write", "users:delete",
            "reviews:read", "reviews:write", "reviews:delete", "reviews:approve",
            "orders:read", "orders:write",
            "datasets:read", "datasets:write", "datasets:delete",
            "predictions:read", "predictions:write",
            "analytics:read",
            "api_keys:read", "api_keys:write", "api_keys:delete",
            "workshops:read", "workshops:write", "workshops:delete",
        ],
        "user": [
            "bikes:read",
            "brands:read",
            "mods:read",
            "reviews:read", "reviews:write",
            "orders:read", "orders:write",
            "predictions:read",
            "builds:read", "builds:write", "builds:delete",
            "garage:read", "garage:write",
            "wishlist:read", "wishlist:write",
        ],
        "workshop": [
            "bikes:read",
            "brands:read",
            "mods:read", "mods:write",
            "reviews:read",
            "orders:read",
            "predictions:read",
            "workshops:read", "workshops:write",
        ],
    }

    @classmethod
    def get_permissions(cls, role: str) -> list[str]:
        return cls.PERMISSIONS.get(role, [])

    @classmethod
    def has_permission(cls, role: str, permission: str) -> bool:
        return permission in cls.get_permissions(role)
