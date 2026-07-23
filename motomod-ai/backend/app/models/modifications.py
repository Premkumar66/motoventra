"""
MotoMod AI — Modifications ORM Models
Categories, Products, Images, Compatibility, Ratings
"""
import uuid
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Uuid, JSON,
    Boolean, CheckConstraint, Float, ForeignKey, Index,
    Integer, Numeric, String, Text, UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditModel, BaseModel


class ModificationCategory(str, PyEnum):
    EXHAUST = "exhaust"
    AIR_FILTER = "air_filter"
    FUELX = "fuelx"
    ECU_TUNE = "ecu_tune"
    TYRES = "tyres"
    HANDLEBARS = "handlebars"
    SEATS = "seats"
    CRASH_GUARDS = "crash_guards"
    FRAME_SLIDERS = "frame_sliders"
    HEADLIGHTS = "headlights"
    FOG_LIGHTS = "fog_lights"
    TAIL_LIGHTS = "tail_lights"
    MIRRORS = "mirrors"
    WINDSHIELD = "windshield"
    GRAPHICS = "graphics"
    RIMS = "rims"
    BRAKE_PADS = "brake_pads"
    SUSPENSION = "suspension"
    CHAIN_KIT = "chain_kit"
    SPROCKETS = "sprockets"
    LUGGAGE = "luggage"
    PHONE_MOUNT = "phone_mount"
    USB_CHARGER = "usb_charger"
    OTHER = "other"


class ModificationCategoryModel(AuditModel):
    """Modification categories (Exhaust, Air Filter, etc.)."""
    __tablename__ = "modification_categories"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    category_enum: Mapped[ModificationCategory] = mapped_column(
        String(50), nullable=False, unique=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    icon_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    affects_performance: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    affects_mileage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_dyno: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # ─── Relationships ───────────────────────────────────────
    modifications: Mapped[List["Modification"]] = relationship(
        "Modification", back_populates="category"
    )


class Modification(AuditModel):
    """
    A specific modification product.
    Example: Akrapovic S-Y10SO47-HAPC Slip-On Exhaust for Yamaha R15 V4
    """
    __tablename__ = "modifications"
    __table_args__ = (
        Index("ix_mods_category_id", "category_id"),
        Index("ix_mods_brand_name", "brand_name"),
        Index("ix_mods_price", "price_inr"),
        Index("ix_mods_is_active", "is_active"),
    )

    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modification_categories.id", ondelete="RESTRICT"), nullable=False
    )

    # ─── Product Identity ────────────────────────────────────
    brand_name: Mapped[str] = mapped_column(String(100), nullable=False)
    model_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False, unique=True)
    sku: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    short_description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Specifications ──────────────────────────────────────
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    material: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    color_options: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    dimensions: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    installation_time_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    warranty_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    country_of_origin: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ─── Performance Impact ──────────────────────────────────
    hp_change_bhp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    hp_change_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    torque_change_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    torque_change_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_change_kmpl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_change_percent: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    weight_change_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    noise_level_db: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    performance_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ─── Pricing ─────────────────────────────────────────────
    price_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    installation_cost_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    affiliate_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Ratings & Reviews ───────────────────────────────────
    average_rating: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    review_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ─── Status ──────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_featured: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    requires_professional_install: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_legal_for_road: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    is_universal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # True = compatible with all bikes
    is_universal: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # If True, compatible with ALL motorcycles
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)


    # ─── Relationships ───────────────────────────────────────
    category: Mapped["ModificationCategoryModel"] = relationship(
        "ModificationCategoryModel", back_populates="modifications"
    )
    images: Mapped[List["ModificationImage"]] = relationship(
        "ModificationImage", back_populates="modification", cascade="all, delete-orphan"
    )
    compatibility_entries: Mapped[List["ModificationCompatibility"]] = relationship(
        "ModificationCompatibility", back_populates="modification", cascade="all, delete-orphan"
    )
    build_modifications: Mapped[List["BuildModification"]] = relationship(
        "BuildModification", back_populates="modification"
    )

    def __repr__(self) -> str:
        return f"<Modification {self.brand_name} {self.model_name}>"


class ModificationImage(BaseModel):
    """Images for a modification product."""
    __tablename__ = "modification_images"
    __table_args__ = (
        Index("ix_mod_images_modification_id", "modification_id"),
    )

    modification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    alt_text: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    minio_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    modification: Mapped["Modification"] = relationship("Modification", back_populates="images")


class ModificationCompatibility(BaseModel):
    """
    Defines which motorcycle variants a modification is compatible with.
    Supports exact variant matching and range-based year compatibility.
    """
    __tablename__ = "modification_compatibility"
    __table_args__ = (
        UniqueConstraint("modification_id", "variant_id", name="uq_mod_compat"),
        Index("ix_mod_compat_modification_id", "modification_id"),
        Index("ix_mod_compat_variant_id", "variant_id"),
    )

    modification_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("modifications.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="CASCADE"), nullable=False
    )
    compatibility_type: Mapped[str] = mapped_column(
        String(30), default="direct_fit", nullable=False
    )  # direct_fit | with_adapter | universal
    year_from: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    year_to: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    verified_by: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Relationships ───────────────────────────────────────
    modification: Mapped["Modification"] = relationship(
        "Modification", back_populates="compatibility_entries"
    )
    variant: Mapped["MotorcycleVariant"] = relationship(
        "MotorcycleVariant", back_populates="modification_compatibilities"
    )


# Forward imports
from app.models.builds import BuildModification  # noqa
from app.models.motorcycle import MotorcycleVariant  # noqa
