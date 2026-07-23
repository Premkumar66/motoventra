"""
MotoMod AI — Motorcycle & Catalog ORM Models
Brands, Motorcycles, Variants, Specs, Images
"""
import uuid
from datetime import date, datetime
from enum import Enum as PyEnum
from typing import List, Optional

from sqlalchemy import (
    Uuid, JSON,
    Boolean, Date, DateTime, Enum, Float, ForeignKey,
    Index, Integer, Numeric, String, Text, UniqueConstraint,
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import AuditModel, BaseModel


class FuelType(str, PyEnum):
    PETROL = "petrol"
    DIESEL = "diesel"
    ELECTRIC = "electric"
    HYBRID = "hybrid"
    CNG = "cng"


class CoolingType(str, PyEnum):
    AIR = "air"
    LIQUID = "liquid"
    OIL = "oil"
    AIR_OIL = "air_oil"


class TransmissionType(str, PyEnum):
    MANUAL = "manual"
    AUTOMATIC = "automatic"
    SEMI_AUTOMATIC = "semi_automatic"
    DCT = "dct"


class BikeCategory(str, PyEnum):
    COMMUTER = "commuter"
    SPORT = "sport"
    CRUISER = "cruiser"
    ADVENTURE = "adventure"
    NAKED = "naked"
    SCRAMBLER = "scrambler"
    TOURER = "tourer"
    SUPERMOTO = "supermoto"
    DIRT = "dirt"
    SCOOTER = "scooter"
    ELECTRIC = "electric"


class EmissionStandard(str, PyEnum):
    BS4 = "bs4"
    BS6 = "bs6"
    EURO5 = "euro5"
    EURO6 = "euro6"


class Brand(AuditModel):
    """Motorcycle manufacturers/brands."""
    __tablename__ = "brands"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_brands_slug"),
        Index("ix_brands_slug", "slug"),
        Index("ix_brands_country", "country"),
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    country: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    founded_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    website_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # ─── Relationships ───────────────────────────────────────
    motorcycles: Mapped[List["Motorcycle"]] = relationship(
        "Motorcycle", back_populates="brand", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Brand name={self.name}>"


class Motorcycle(AuditModel):
    """
    A motorcycle model (e.g., Royal Enfield Classic 350).
    This represents the model-level entity, not a specific year variant.
    """
    __tablename__ = "motorcycles"
    __table_args__ = (
        UniqueConstraint("brand_id", "slug", name="uq_motorcycles_brand_slug"),
        Index("ix_motorcycles_brand_id", "brand_id"),
        Index("ix_motorcycles_slug", "slug"),
        Index("ix_motorcycles_category", "category"),
        Index("ix_motorcycles_is_active", "is_active"),
    )

    brand_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("brands.id", ondelete="RESTRICT"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    category: Mapped[BikeCategory] = mapped_column(
        Enum(BikeCategory, name="bike_category_enum"), nullable=False
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_discontinued: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    discontinued_year: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    tags: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ─── Relationships ───────────────────────────────────────
    brand: Mapped["Brand"] = relationship("Brand", back_populates="motorcycles")
    variants: Mapped[List["MotorcycleVariant"]] = relationship(
        "MotorcycleVariant", back_populates="motorcycle", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Motorcycle name={self.name}>"


class MotorcycleVariant(AuditModel):
    """
    A specific variant of a motorcycle with full technical specifications.
    Example: Royal Enfield Classic 350 Halcyon Black (2023)
    """
    __tablename__ = "motorcycle_variants"
    __table_args__ = (
        UniqueConstraint("motorcycle_id", "slug", "year", name="uq_variants_moto_slug_year"),
        Index("ix_variants_motorcycle_id", "motorcycle_id"),
        Index("ix_variants_year", "year"),
        Index("ix_variants_engine_cc", "engine_cc"),
        Index("ix_variants_price", "price_inr"),
    )

    motorcycle_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycles.id", ondelete="RESTRICT"), nullable=False
    )
    # ─── Identity ────────────────────────────────────────────
    variant_name: Mapped[str] = mapped_column(String(200), nullable=False)
    slug: Mapped[str] = mapped_column(String(300), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    generation: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    launch_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    discontinued_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # ─── Engine ──────────────────────────────────────────────
    engine_cc: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    engine_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    cylinders: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    fuel_type: Mapped[FuelType] = mapped_column(
        Enum(FuelType, name="fuel_type_enum"), nullable=False, default=FuelType.PETROL
    )
    fuel_system: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    cooling: Mapped[Optional[CoolingType]] = mapped_column(
        Enum(CoolingType, name="cooling_type_enum"), nullable=True
    )
    compression_ratio: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    emission_standard: Mapped[Optional[EmissionStandard]] = mapped_column(
        Enum(EmissionStandard, name="emission_standard_enum"), nullable=True
    )

    # ─── Performance ─────────────────────────────────────────
    horsepower_bhp: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    horsepower_rpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    torque_nm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    torque_rpm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    top_speed_kmh: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_kmpl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_city_kmpl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    mileage_highway_kmpl: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    acceleration_0_100: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Transmission ────────────────────────────────────────
    transmission: Mapped[Optional[TransmissionType]] = mapped_column(
        Enum(TransmissionType, name="transmission_type_enum"), nullable=True
    )
    gear_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ─── Dimensions & Weight ─────────────────────────────────
    weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    kerb_weight_kg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    wheelbase_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    seat_height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ground_clearance_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    length_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    width_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    height_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Tank & Range ────────────────────────────────────────
    fuel_tank_liters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reserve_fuel_liters: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # ─── Suspension ──────────────────────────────────────────
    front_suspension: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    rear_suspension: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # ─── Brakes ──────────────────────────────────────────────
    front_brake: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    rear_brake: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    front_brake_size_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rear_brake_size_mm: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    has_abs: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    abs_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # ─── Tyres ───────────────────────────────────────────────
    front_tyre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    rear_tyre: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tyre_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # ─── Electronics ─────────────────────────────────────────
    instrument_cluster: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    headlight_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    has_led_tail: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_traction_control: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_ride_modes: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_quickshifter: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_bluetooth: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    has_usb_charging: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    electronics_features: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ─── Pricing ─────────────────────────────────────────────
    price_inr: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    price_usd: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ex_showroom_city: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    official_colors: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)

    # ─── Misc ────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    data_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    data_confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    extra_specs: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    # ─── 3D & 360° Media ───────────────────────────────────
    three_d_model_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # URL/path to GLB/GLTF file
    spin_360_urls: Mapped[Optional[list]] = mapped_column(JSON, nullable=True)  # List of 360° rotation image URLs
    primary_image_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)  # Definitive primary image for this variant

    # ─── Relationships ───────────────────────────────────────
    motorcycle: Mapped["Motorcycle"] = relationship("Motorcycle", back_populates="variants")
    images: Mapped[List["MotorcycleImage"]] = relationship(
        "MotorcycleImage", back_populates="variant", cascade="all, delete-orphan"
    )
    modification_compatibilities: Mapped[List["ModificationCompatibility"]] = relationship(
        "ModificationCompatibility", back_populates="variant"
    )
    garage_motorcycles: Mapped[List["GarageMotorcycle"]] = relationship(
        "GarageMotorcycle", back_populates="variant"
    )
    builds: Mapped[List["UserBuild"]] = relationship(
        "UserBuild", back_populates="variant"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="variant"
    )

    def __repr__(self) -> str:
        return f"<MotorcycleVariant name={self.variant_name} year={self.year}>"


class MotorcycleImage(BaseModel):
    """Images associated with a motorcycle variant."""
    __tablename__ = "motorcycle_images"
    __table_args__ = (
        Index("ix_moto_images_variant_id", "variant_id"),
    )

    variant_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("motorcycle_variants.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    alt_text: Mapped[Optional[str]] = mapped_column(String(300), nullable=True)
    color_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    image_type: Mapped[str] = mapped_column(String(50), default="exterior", nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    width: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    height: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    file_size_bytes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    minio_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # ─── Relationships ───────────────────────────────────────
    variant: Mapped["MotorcycleVariant"] = relationship("MotorcycleVariant", back_populates="images")


# Forward references
from app.models.modifications import ModificationCompatibility  # noqa
from app.models.builds import GarageMotorcycle  # noqa
from app.models.builds import UserBuild  # noqa
from app.models.reviews import Review  # noqa
