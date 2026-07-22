"""
MotoMod AI — Builds, Garage, Reviews, Shop, Predictions ORM Models
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Uuid, JSON,
    Boolean, DateTime, Enum, Float, ForeignKey,
    Index, Integer, Numeric, String, Text, UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditModel, BaseModel


# ═══════════════════════════════════════════════════════════════
# BUILDS
# ═══════════════════════════════════════════════════════════════

class BuildStatus(str, PyEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class UserBuild(AuditModel):
    """A user's saved motorcycle build configuration."""
    __tablename__ = "user_builds"
    __table_args__ = (
        Index("ix_builds_user_id", "user_id"),
        Index("ix_builds_variant_id", "variant_id"),
        Index("ix_builds_status", "status"),
        Index("ix_builds_is_public", "is_public"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[BuildStatus] = mapped_column(
        Enum(BuildStatus, name="build_status_enum"), default=BuildStatus.DRAFT, nullable=False
    )
    is_public: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    share_token: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, unique=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Budget & Cost ───────────────────────────────────────
    total_mod_cost_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    total_install_cost_inr: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    # ─── Predicted Performance ───────────────────────────────
    predicted_hp_bhp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_mileage_kmpl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_top_speed_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    prediction_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Engagement ──────────────────────────────────────────
    view_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    like_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    clone_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ─── Relationships ───────────────────────────────────────
    user: Mapped["User"] = relationship("User", back_populates="builds")
    variant: Mapped["MotorcycleVariant"] = relationship("MotorcycleVariant", back_populates="builds")
    build_modifications: Mapped[List["BuildModification"]] = relationship(
        "BuildModification", back_populates="build", cascade="all, delete-orphan"
    )


class BuildModification(BaseModel):
    """Association between a build and its modifications."""
    __tablename__ = "build_modifications"
    __table_args__ = (
        UniqueConstraint("build_id", "modification_id", name="uq_build_mod"),
        Index("ix_build_mods_build_id", "build_id"),
    )

    build_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("user_builds.id", ondelete="CASCADE"), nullable=False
    )
    modification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_installed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    installed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    build: Mapped["UserBuild"] = relationship("UserBuild", back_populates="build_modifications")
    modification: Mapped["Modification"] = relationship("Modification", back_populates="build_modifications")


# ═══════════════════════════════════════════════════════════════
# GARAGE
# ═══════════════════════════════════════════════════════════════

class GarageMotorcycle(AuditModel):
    """A motorcycle in a user's virtual garage."""
    __tablename__ = "garage_motorcycles"
    __table_args__ = (
        UniqueConstraint("user_id", "variant_id", name="uq_garage_user_variant"),
        Index("ix_garage_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="RESTRICT"), nullable=False
    )
    nickname: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    purchase_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    purchase_price: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    current_odometer_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    color: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    insurance_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_service_km: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    last_service_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    images: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="garage_motorcycles")
    variant: Mapped["MotorcycleVariant"] = relationship("MotorcycleVariant", back_populates="garage_motorcycles")


# ═══════════════════════════════════════════════════════════════
# REVIEWS
# ═══════════════════════════════════════════════════════════════

class ReviewType(str, PyEnum):
    MOTORCYCLE = "motorcycle"
    MODIFICATION = "modification"


class ReviewStatus(str, PyEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"


class Review(AuditModel):
    """User reviews for motorcycles and modifications."""
    __tablename__ = "reviews"
    __table_args__ = (
        Index("ix_reviews_user_id", "user_id"),
        Index("ix_reviews_variant_id", "variant_id"),
        Index("ix_reviews_modification_id", "modification_id"),
        Index("ix_reviews_status", "status"),
        Index("ix_reviews_review_type", "review_type"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="CASCADE"), nullable=True
    )
    modification_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="CASCADE"), nullable=True
    )
    review_type: Mapped[ReviewType] = mapped_column(
        Enum(ReviewType, name="review_type_enum"), nullable=False
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    pros: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    cons: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    status: Mapped[ReviewStatus] = mapped_column(
        Enum(ReviewStatus, name="review_status_enum"), default=ReviewStatus.PENDING, nullable=False
    )
    sentiment_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sentiment_label: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    ownership_duration_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="reviews")
    variant: Mapped[Optional["MotorcycleVariant"]] = relationship("MotorcycleVariant", back_populates="reviews")


# ═══════════════════════════════════════════════════════════════
# SHOP
# ═══════════════════════════════════════════════════════════════

class OrderStatus(str, PyEnum):
    PENDING = "pending"
    PAYMENT_PENDING = "payment_pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class WishlistItem(BaseModel):
    """Items in a user's wishlist."""
    __tablename__ = "wishlist_items"
    __table_args__ = (
        UniqueConstraint("user_id", "modification_id", name="uq_wishlist_user_mod"),
        Index("ix_wishlist_user_id", "user_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    modification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="CASCADE"), nullable=False
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    priority: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="wishlist_items")


class Order(AuditModel):
    """Customer orders for accessories/modifications."""
    __tablename__ = "orders"
    __table_args__ = (
        Index("ix_orders_user_id", "user_id"),
        Index("ix_orders_status", "status"),
        Index("ix_orders_razorpay_order_id", "razorpay_order_id"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    order_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status_enum"), default=OrderStatus.PENDING, nullable=False
    )
    subtotal_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    tax_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    shipping_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    total_inr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)
    razorpay_order_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    payment_captured_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    shipping_address: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem", back_populates="order", cascade="all, delete-orphan"
    )


class OrderItem(BaseModel):
    """Individual line items within an order."""
    __tablename__ = "order_items"
    __table_args__ = (
        Index("ix_order_items_order_id", "order_id"),
    )

    order_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    modification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="RESTRICT"), nullable=False
    )
    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    unit_price_inr: Mapped[float] = mapped_column(Float, nullable=False)
    total_price_inr: Mapped[float] = mapped_column(Float, nullable=False)
    snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    order: Mapped["Order"] = relationship("Order", back_populates="items")


# ═══════════════════════════════════════════════════════════════
# PREDICTIONS
# ═══════════════════════════════════════════════════════════════

class PredictionType(str, PyEnum):
    MILEAGE = "mileage"
    HORSEPOWER = "horsepower"
    TORQUE = "torque"
    TOP_SPEED = "top_speed"
    MAINTENANCE = "maintenance"
    RESALE_VALUE = "resale_value"
    COMPATIBILITY = "compatibility"
    BUDGET = "budget"
    RECOMMENDATION = "recommendation"
    SENTIMENT = "sentiment"


class PredictionHistory(AuditModel):
    """Log of all AI predictions made for audit and retraining."""
    __tablename__ = "prediction_history"
    __table_args__ = (
        Index("ix_pred_history_user_id", "user_id"),
        Index("ix_pred_history_prediction_type", "prediction_type"),
        Index("ix_pred_history_variant_id", "variant_id"),
    )

    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="SET NULL"), nullable=True
    )
    prediction_type: Mapped[PredictionType] = mapped_column(
        Enum(PredictionType, name="prediction_type_enum"), nullable=False
    )
    input_features: Mapped[dict] = mapped_column(JSON, nullable=False)
    predicted_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    predicted_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    model_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    inference_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    user_feedback_accurate: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    user_feedback_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    feedback_given_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    user: Mapped[Optional["User"]] = relationship("User", back_populates="prediction_history")


# ═══════════════════════════════════════════════════════════════
# DATASETS
# ═══════════════════════════════════════════════════════════════

class ImportStatus(str, PyEnum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class DatasetImport(AuditModel):
    """Tracks all dataset imports for the ETL pipeline."""
    __tablename__ = "dataset_imports"
    __table_args__ = (
        Index("ix_dataset_imports_status", "status"),
        Index("ix_dataset_imports_source_type", "source_type"),
    )

    name: Mapped[str] = mapped_column(String(200), nullable=False)
    source_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    status: Mapped[ImportStatus] = mapped_column(
        Enum(ImportStatus, name="import_status_enum"), default=ImportStatus.QUEUED, nullable=False
    )
    total_records: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    imported_records: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    failed_records: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duplicate_records: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    error_log: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    minio_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)


# Forward references
from app.models.user import User  # noqa
from app.models.motorcycle import MotorcycleVariant  # noqa
from app.models.modifications import Modification  # noqa
