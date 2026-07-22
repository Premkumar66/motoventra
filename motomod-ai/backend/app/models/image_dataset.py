"""
MotoMod AI — Bike Image Dataset ORM Models
Covers all image management, source tracking, license compliance, and processing logs.

Tables:
  - ImageLicense          (CC-BY, MIT, Public Domain, etc.)
  - ImageSource           (Wikimedia, Kaggle, GitHub, admin upload…)
  - BikeImageBrand        (catalog — independent of main Motorcycle model)
  - BikeImageModel        (catalog)
  - BikeImageVariant      (color/trim variants)
  - BikeModelYear         (per-year tracking)
  - BikeImage             (the actual image record)
  - BikeImageMetadata     (EXIF + AI embedding + attribution)
  - ImageProcessingLog    (audit trail for every operation)
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    UUID, JSON, Boolean, DateTime, Enum, Float, ForeignKey,
    Index, Integer, String, Text, UniqueConstraint, BigInteger,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditModel, BaseModel


# ─── Enumerations ────────────────────────────────────────────────────────────

class ImageViewType(str, PyEnum):
    FRONT      = "front"
    REAR       = "rear"
    LEFT       = "left"
    RIGHT      = "right"
    FRONT_45   = "front45"
    REAR_45    = "rear45"
    TOP        = "top"
    DASHBOARD  = "dashboard"
    ENGINE     = "engine"
    HEADLIGHT  = "headlight"
    TAILLIGHT  = "taillight"
    WHEEL      = "wheel"
    EXHAUST    = "exhaust"
    SEAT       = "seat"
    OTHER      = "other"


class ImageStatus(str, PyEnum):
    PENDING   = "pending"
    APPROVED  = "approved"
    REJECTED  = "rejected"
    DUPLICATE = "duplicate"
    CORRUPTED = "corrupted"


class LicenseType(str, PyEnum):
    CC_BY         = "cc_by"
    CC_BY_SA      = "cc_by_sa"
    CC_BY_ND      = "cc_by_nd"
    CC_BY_NC      = "cc_by_nc"
    CC_BY_NC_SA   = "cc_by_nc_sa"
    CC0           = "cc0"
    PUBLIC_DOMAIN = "public_domain"
    MIT           = "mit"
    APACHE2       = "apache2"
    PLATFORM_OWN  = "platform_own"
    UNKNOWN       = "unknown"


class ImportSource(str, PyEnum):
    WIKIMEDIA    = "wikimedia"
    KAGGLE       = "kaggle"
    GITHUB       = "github"
    CSV_IMPORT   = "csv_import"
    ZIP_IMPORT   = "zip_import"
    URL_IMPORT   = "url_import"
    ADMIN_UPLOAD = "admin_upload"
    USER_UPLOAD  = "user_upload"


class ProcessingOperation(str, PyEnum):
    VALIDATE    = "validate"
    RESIZE      = "resize"
    COMPRESS    = "compress"
    THUMBNAIL   = "thumbnail"
    HASH        = "hash"
    EXIF        = "exif"
    DEDUPLICATE = "deduplicate"
    EMBED       = "embed"
    CLASSIFY    = "classify"
    STORE       = "store"


class ProcessingStatus(str, PyEnum):
    QUEUED  = "queued"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED  = "failed"
    SKIPPED = "skipped"


# ─── Tables ──────────────────────────────────────────────────────────────────

class ImageLicense(AuditModel):
    """Known open-source licenses for bike images."""
    __tablename__ = "image_licenses"
    __table_args__ = (
        UniqueConstraint("spdx_id", name="uq_image_licenses_spdx"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    spdx_id: Mapped[str] = mapped_column(String(60), nullable=False)
    license_type: Mapped[LicenseType] = mapped_column(
        Enum(LicenseType, name="license_type_enum"), nullable=False
    )
    allows_commercial_use: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_attribution: Mapped[bool] = mapped_column(Boolean, default=True)
    requires_share_alike: Mapped[bool] = mapped_column(Boolean, default=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Relationships
    sources: Mapped[List["ImageSource"]] = relationship("ImageSource", back_populates="license")
    image_metadata: Mapped[List["BikeImageMetadata"]] = relationship("BikeImageMetadata", back_populates="license")

    def __repr__(self) -> str:
        return f"<ImageLicense {self.spdx_id}>"


class ImageSource(AuditModel):
    """Registered image sources (Wikimedia, Kaggle, admin, etc.)."""
    __tablename__ = "image_sources"

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    source_type: Mapped[ImportSource] = mapped_column(
        Enum(ImportSource, name="import_source_enum"), nullable=False
    )
    source_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    license_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("image_licenses.id", ondelete="SET NULL"), nullable=True
    )
    allows_automated_collection: Mapped[bool] = mapped_column(Boolean, default=True)
    attribution_template: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    license: Mapped[Optional["ImageLicense"]] = relationship("ImageLicense", back_populates="sources")
    image_metadata: Mapped[List["BikeImageMetadata"]] = relationship("BikeImageMetadata", back_populates="source")

    def __repr__(self) -> str:
        return f"<ImageSource {self.name}>"


class BikeImageBrand(AuditModel):
    """Bike brands for the image dataset catalog."""
    __tablename__ = "bike_image_brands"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_bike_image_brands_slug"),
        Index("ix_bike_image_brands_slug", "slug"),
    )

    name: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(120), nullable=False)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    models: Mapped[List["BikeImageModel"]] = relationship("BikeImageModel", back_populates="brand")

    def __repr__(self) -> str:
        return f"<BikeImageBrand {self.name}>"


class BikeImageModel(AuditModel):
    """Bike models for the image dataset catalog."""
    __tablename__ = "bike_image_models"
    __table_args__ = (
        UniqueConstraint("brand_id", "slug", name="uq_bike_image_models_brand_slug"),
        Index("ix_bike_image_models_brand_id", "brand_id"),
        Index("ix_bike_image_models_slug", "slug"),
    )

    brand_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_image_brands.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(150), nullable=False)
    category: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    brand: Mapped["BikeImageBrand"] = relationship("BikeImageBrand", back_populates="models")
    variants: Mapped[List["BikeImageVariant"]] = relationship("BikeImageVariant", back_populates="model")
    years: Mapped[List["BikeModelYear"]] = relationship("BikeModelYear", back_populates="model")
    images: Mapped[List["BikeImage"]] = relationship("BikeImage", back_populates="model")

    def __repr__(self) -> str:
        return f"<BikeImageModel {self.name}>"


class BikeImageVariant(AuditModel):
    """Color / trim variants for a bike model."""
    __tablename__ = "bike_image_variants"
    __table_args__ = (
        Index("ix_bike_image_variants_model_id", "model_id"),
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_image_models.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    color: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)
    color_hex: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    model: Mapped["BikeImageModel"] = relationship("BikeImageModel", back_populates="variants")
    images: Mapped[List["BikeImage"]] = relationship("BikeImage", back_populates="variant")

    def __repr__(self) -> str:
        return f"<BikeImageVariant {self.name}>"


class BikeModelYear(AuditModel):
    """Year availability record for a bike model."""
    __tablename__ = "bike_model_years"
    __table_args__ = (
        UniqueConstraint("model_id", "year", name="uq_bike_model_years_model_year"),
        Index("ix_bike_model_years_model_id", "model_id"),
    )

    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_image_models.id", ondelete="CASCADE"), nullable=False
    )
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    model: Mapped["BikeImageModel"] = relationship("BikeImageModel", back_populates="years")
    images: Mapped[List["BikeImage"]] = relationship("BikeImage", back_populates="year_record")

    def __repr__(self) -> str:
        return f"<BikeModelYear {self.year}>"


class BikeImage(AuditModel):
    """Core image record — one row per physical image file."""
    __tablename__ = "bike_images"
    __table_args__ = (
        UniqueConstraint("image_hash", name="uq_bike_images_hash"),
        Index("ix_bike_images_model_id", "model_id"),
        Index("ix_bike_images_status", "status"),
        Index("ix_bike_images_view_type", "view_type"),
    )

    # Foreign keys
    model_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_image_models.id", ondelete="CASCADE"), nullable=False
    )
    variant_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_image_variants.id", ondelete="SET NULL"), nullable=True
    )
    year_record_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_model_years.id", ondelete="SET NULL"), nullable=True
    )

    # File information
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Image properties
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    view_type: Mapped[ImageViewType] = mapped_column(
        Enum(ImageViewType, name="image_view_type_enum"), default=ImageViewType.OTHER, nullable=False
    )
    color: Mapped[Optional[str]] = mapped_column(String(60), nullable=True)

    # Hashes for deduplication
    image_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)   # SHA-256
    phash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)         # Perceptual hash

    # Paths for derived images
    thumbnail_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    preview_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Workflow status
    status: Mapped[ImageStatus] = mapped_column(
        Enum(ImageStatus, name="image_status_enum"), default=ImageStatus.PENDING, nullable=False
    )
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False)
    rejection_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Admin tracking
    approved_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    model: Mapped["BikeImageModel"] = relationship("BikeImageModel", back_populates="images")
    variant: Mapped[Optional["BikeImageVariant"]] = relationship("BikeImageVariant", back_populates="images")
    year_record: Mapped[Optional["BikeModelYear"]] = relationship("BikeModelYear", back_populates="images")
    img_metadata: Mapped[Optional["BikeImageMetadata"]] = relationship(
        "BikeImageMetadata", back_populates="image", uselist=False
    )
    processing_logs: Mapped[List["ImageProcessingLog"]] = relationship(
        "ImageProcessingLog", back_populates="image"
    )

    def __repr__(self) -> str:
        return f"<BikeImage {self.file_name} [{self.status}]>"


class BikeImageMetadata(AuditModel):
    """Extended metadata — source, license, EXIF, AI embeddings."""
    __tablename__ = "bike_image_metadata"
    __table_args__ = (
        UniqueConstraint("image_id", name="uq_bike_image_metadata_image"),
    )

    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_images.id", ondelete="CASCADE"), nullable=False
    )
    source_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("image_sources.id", ondelete="SET NULL"), nullable=True
    )
    license_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("image_licenses.id", ondelete="SET NULL"), nullable=True
    )

    # Source tracking
    original_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attribution: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    copyright_owner: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # EXIF data
    exif_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    camera_make: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    camera_model: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    capture_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # AI features
    ai_embedding: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)
    ai_brand_detected: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    ai_model_detected: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)
    ai_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Relationships
    image: Mapped["BikeImage"] = relationship("BikeImage", back_populates="img_metadata")
    source: Mapped[Optional["ImageSource"]] = relationship("ImageSource", back_populates="image_metadata")
    license: Mapped[Optional["ImageLicense"]] = relationship("ImageLicense", back_populates="image_metadata")

    def __repr__(self) -> str:
        return f"<BikeImageMetadata image_id={self.image_id}>"


class ImageProcessingLog(BaseModel):
    """Audit trail for every image processing operation."""
    __tablename__ = "image_processing_logs"
    __table_args__ = (
        Index("ix_image_processing_logs_image_id", "image_id"),
        Index("ix_image_processing_logs_status", "status"),
    )

    image_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("bike_images.id", ondelete="CASCADE"), nullable=False
    )
    operation: Mapped[ProcessingOperation] = mapped_column(
        Enum(ProcessingOperation, name="processing_operation_enum"), nullable=False
    )
    status: Mapped[ProcessingStatus] = mapped_column(
        Enum(ProcessingStatus, name="processing_status_enum"), nullable=False
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    processed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, nullable=False
    )

    # Relationships
    image: Mapped["BikeImage"] = relationship("BikeImage", back_populates="processing_logs")

    def __repr__(self) -> str:
        return f"<ImageProcessingLog {self.operation} [{self.status}]>"
