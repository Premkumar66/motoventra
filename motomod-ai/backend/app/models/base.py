"""
MotoMod AI — SQLAlchemy ORM Base Mixins
Shared columns, timestamps, and utilities for all models
"""
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, String, func, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


class UUIDMixin:
    """Provides a UUID primary key."""
    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )


class TimestampMixin:
    """Provides created_at and updated_at audit timestamps."""
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class SoftDeleteMixin:
    """Provides soft delete functionality."""
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )
    is_deleted: Mapped[bool] = mapped_column(default=False, nullable=False)


class BaseModel(UUIDMixin, TimestampMixin, Base):
    """Full base model with UUID PK and timestamps."""
    __abstract__ = True


class AuditModel(UUIDMixin, TimestampMixin, SoftDeleteMixin, Base):
    """Full auditable model with soft delete."""
    __abstract__ = True
