"""
MotoMod AI — Authentication Routing
/register  POST  – create account
/login     POST  – issue JWT (JSON body: email + password)
/me        GET   – get current user profile (Bearer token)
/refresh   POST  – rotate refresh token
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Header, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token,
    decode_token, ACCESS_TOKEN_TYPE, REFRESH_TOKEN_TYPE, RolePermissions,
)
from app.models.user import User, UserStatus, UserRole
from app.schemas.auth import UserPublicResponse, PaginationMeta

router = APIRouter(prefix="/auth", tags=["Authentication"])


# ── Inline request schemas (relaxed validation for dev) ──────────────────────

class RegisterBody(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None
    full_name: Optional[str] = None
    confirm_password: Optional[str] = None   # optional, ignored if omitted


class LoginBody(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class RefreshBody(BaseModel):
    refresh_token: str


# ── Token helper ─────────────────────────────────────────────────────────────

def _make_token_response(user: User) -> dict:
    perms = RolePermissions.get_permissions(user.role.value)
    return {
        "access_token":  create_access_token(user.id, user.role.value, perms),
        "refresh_token": create_refresh_token(user.id),
        "token_type":    "bearer",
        "expires_in":    1800,
        "user": {
            "id":                str(user.id),
            "email":             user.email,
            "username":          user.username or "",
            "full_name":         user.full_name or "",
            "avatar_url":        user.avatar_url,
            "bio":               user.bio,
            "city":              user.city,
            "country":           user.country,
            "role":              user.role.value,
            "status":            user.status.value,
            "is_email_verified": user.is_email_verified,
            "theme_preference":  user.theme_preference or "dark",
            "created_at":        user.created_at.isoformat() if user.created_at else None,
        },
    }


# ── Auth dependency ───────────────────────────────────────────────────────────

async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Extract Bearer token from Authorization header and return the user."""
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated. Provide Authorization: Bearer <token>",
        )
    token = authorization.split(" ", 1)[1].strip()
    try:
        payload = decode_token(token, ACCESS_TOKEN_TYPE)
        user_id = payload.get("sub")
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
        )
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Bad token payload.")

    try:
        uid = UUID(str(user_id))
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid user ID in token.")

    res = await db.execute(select(User).where(User.id == uid))
    user = res.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found.")
    if user.status == UserStatus.BANNED:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account banned.")
    return user


# ── Routes ───────────────────────────────────────────────────────────────────

@router.post("/register", status_code=201, summary="Register a new user account")
async def register(body: RegisterBody, db: AsyncSession = Depends(get_db)):
    # Check email
    res = await db.execute(select(User).filter_by(email=body.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered.")

    # Auto-generate username if not provided
    username = (body.username or body.email.split("@")[0]).lower().replace(" ", "_")
    res2 = await db.execute(select(User).filter_by(username=username))
    if res2.scalar_one_or_none():
        username = username + "_" + str(hash(body.email))[-4:]

    new_user = User(
        email=body.email,
        username=username,
        hashed_password=hash_password(body.password),
        full_name=body.full_name or username,
        role=UserRole.USER,
        status=UserStatus.ACTIVE,
        is_email_verified=True,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return _make_token_response(new_user)


@router.post("/login", summary="Login with email + password (JSON)")
async def login(body: LoginBody, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(User).filter_by(email=body.email))
    user = res.scalar_one_or_none()

    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    if user.status == UserStatus.BANNED:
        raise HTTPException(status_code=403, detail="Your account has been banned.")

    user.last_login_at = datetime.now(timezone.utc)
    db.add(user)
    await db.commit()

    return _make_token_response(user)


@router.get("/me", summary="Get current authenticated user profile")
async def get_me(current_user: User = Depends(get_current_user)):
    return {
        "id":                str(current_user.id),
        "email":             current_user.email,
        "username":          current_user.username or "",
        "full_name":         current_user.full_name or "",
        "avatar_url":        current_user.avatar_url,
        "bio":               current_user.bio,
        "city":              current_user.city,
        "country":           current_user.country,
        "role":              current_user.role.value,
        "status":            current_user.status.value,
        "is_email_verified": current_user.is_email_verified,
        "theme_preference":  current_user.theme_preference or "dark",
        "created_at":        current_user.created_at.isoformat() if current_user.created_at else None,
    }


@router.post("/refresh", summary="Refresh access token")
async def refresh(body: RefreshBody, db: AsyncSession = Depends(get_db)):
    try:
        claims = decode_token(body.refresh_token, REFRESH_TOKEN_TYPE)
        user_id = claims.get("sub")
        uid = UUID(str(user_id))
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid refresh token.")

    res = await db.execute(select(User).where(User.id == uid))
    user = res.scalar_one_or_none()
    if not user or user.status == UserStatus.BANNED:
        raise HTTPException(status_code=401, detail="User not found.")

    return _make_token_response(user)
