"""
MotoMod AI — Pydantic Schemas: Auth & User
Request/response models with full validation
"""
import re
import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


# ─── Common ───────────────────────────────────────────────────────────────────

class MessageResponse(BaseModel):
    message: str
    success: bool = True


class PaginationMeta(BaseModel):
    total: int
    page: int
    per_page: int
    total_pages: int
    has_next: bool
    has_prev: bool


# ─── Auth Schemas ─────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="Valid email address")
    username: str = Field(..., min_length=3, max_length=50, description="Alphanumeric + underscore")
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)
    full_name: Optional[str] = Field(None, max_length=150)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError("Username must contain only letters, numbers, and underscores.")
        return v.lower()

    @model_validator(mode="after")
    def passwords_match(self) -> "RegisterRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)
    remember_me: bool = False


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: "UserPublicResponse"


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_new_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "ChangePasswordRequest":
        if self.new_password != self.confirm_new_password:
            raise ValueError("New passwords do not match.")
        return self


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str

    @model_validator(mode="after")
    def passwords_match(self) -> "ResetPasswordRequest":
        if self.new_password != self.confirm_password:
            raise ValueError("Passwords do not match.")
        return self


class VerifyEmailRequest(BaseModel):
    token: str


# ─── User Schemas ─────────────────────────────────────────────────────────────

class UserPublicResponse(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: Optional[str]
    avatar_url: Optional[str]
    bio: Optional[str]
    city: Optional[str]
    country: Optional[str]
    role: str
    status: str
    is_email_verified: bool
    theme_preference: str
    created_at: datetime

    model_config = {"from_attributes": True}


class UserPrivateResponse(UserPublicResponse):
    phone: Optional[str]
    preferred_currency: str
    preferred_language: str
    last_login_at: Optional[datetime]
    notification_preferences: Optional[dict]


class UserUpdateRequest(BaseModel):
    full_name: Optional[str] = Field(None, max_length=150)
    bio: Optional[str] = Field(None, max_length=500)
    phone: Optional[str] = Field(None, max_length=20)
    city: Optional[str] = Field(None, max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    preferred_currency: Optional[str] = Field(None, max_length=3)
    preferred_language: Optional[str] = Field(None, max_length=5)
    theme_preference: Optional[str] = Field(None, pattern="^(dark|light|auto)$")
    notification_preferences: Optional[dict] = None


class AdminUserUpdateRequest(UserUpdateRequest):
    role: Optional[str] = Field(None, pattern="^(admin|user|workshop)$")
    status: Optional[str] = Field(None, pattern="^(active|inactive|banned)$")
    is_email_verified: Optional[bool] = None


class UserListResponse(BaseModel):
    items: list[UserPublicResponse]
    meta: PaginationMeta
