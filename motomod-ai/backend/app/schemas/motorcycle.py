"""
MotoMod AI — Pydantic Schemas: Motorcycles & Modifications
"""
import uuid
from datetime import date, datetime
from typing import Any, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.schemas.auth import PaginationMeta


# ─── Brand ────────────────────────────────────────────────────────────────────

class BrandBase(BaseModel):
    name: str = Field(..., max_length=100)
    slug: str = Field(..., max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    founded_year: Optional[int] = Field(None, ge=1600, le=2030)
    website_url: Optional[str] = None
    description: Optional[str] = None
    sort_order: int = 0


class BrandCreate(BrandBase):
    pass


class BrandUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = None
    founded_year: Optional[int] = None
    website_url: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None


class BrandResponse(BrandBase):
    id: uuid.UUID
    logo_url: Optional[str]
    is_active: bool
    motorcycle_count: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class BrandListResponse(BaseModel):
    items: List[BrandResponse]
    meta: PaginationMeta


# ─── Motorcycle ───────────────────────────────────────────────────────────────

class MotorcycleBase(BaseModel):
    name: str = Field(..., max_length=150)
    slug: str = Field(..., max_length=200)
    category: str
    description: Optional[str] = None


class MotorcycleCreate(MotorcycleBase):
    brand_id: uuid.UUID


class MotorcycleResponse(MotorcycleBase):
    id: uuid.UUID
    brand_id: uuid.UUID
    brand: Optional[BrandResponse] = None
    thumbnail_url: Optional[str]
    is_active: bool
    is_discontinued: bool
    variant_count: Optional[int] = None
    created_at: datetime
    model_config = {"from_attributes": True}


class MotorcycleListResponse(BaseModel):
    items: List[MotorcycleResponse]
    meta: PaginationMeta


# ─── Motorcycle Variant (Full Specs) ─────────────────────────────────────────

class VariantSpecsResponse(BaseModel):
    """Full specification sheet for a motorcycle variant."""
    id: uuid.UUID
    motorcycle_id: uuid.UUID
    variant_name: str
    slug: str
    year: int
    generation: Optional[str]
    launch_date: Optional[date]

    # Engine
    engine_cc: Optional[float]
    engine_type: Optional[str]
    cylinders: Optional[int]
    fuel_type: str
    fuel_system: Optional[str]
    cooling: Optional[str]
    compression_ratio: Optional[str]
    emission_standard: Optional[str]

    # Performance
    horsepower_bhp: Optional[float]
    horsepower_rpm: Optional[int]
    torque_nm: Optional[float]
    torque_rpm: Optional[int]
    top_speed_kmh: Optional[float]
    mileage_kmpl: Optional[float]
    mileage_city_kmpl: Optional[float]
    mileage_highway_kmpl: Optional[float]
    acceleration_0_100: Optional[float]

    # Transmission
    transmission: Optional[str]
    gear_count: Optional[int]

    # Dimensions
    weight_kg: Optional[float]
    kerb_weight_kg: Optional[float]
    wheelbase_mm: Optional[float]
    seat_height_mm: Optional[float]
    ground_clearance_mm: Optional[float]

    # Tank
    fuel_tank_liters: Optional[float]

    # Suspension & Brakes
    front_suspension: Optional[str]
    rear_suspension: Optional[str]
    front_brake: Optional[str]
    rear_brake: Optional[str]
    has_abs: bool
    abs_type: Optional[str]

    # Tyres
    front_tyre: Optional[str]
    rear_tyre: Optional[str]

    # Electronics
    has_traction_control: Optional[bool]
    has_ride_modes: Optional[bool]
    has_bluetooth: Optional[bool]
    has_usb_charging: Optional[bool]
    electronics_features: Optional[list]

    # Pricing
    price_inr: Optional[float]
    official_colors: Optional[list]

    # Images
    images: List["VariantImageResponse"] = []

    # Motorcycle details
    motorcycle: Optional["MotorcycleWithBrandResponse"] = None

    model_config = {"from_attributes": True}


class VariantImageResponse(BaseModel):
    id: uuid.UUID
    url: str
    thumbnail_url: Optional[str]
    alt_text: Optional[str]
    color_name: Optional[str]
    image_type: str
    is_primary: bool
    sort_order: int
    model_config = {"from_attributes": True}


class MotorcycleWithBrandResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category: str
    brand: BrandResponse
    model_config = {"from_attributes": True}


class VariantListItem(BaseModel):
    """Compact variant for list views."""
    id: uuid.UUID
    variant_name: str
    year: int
    engine_cc: Optional[float]
    horsepower_bhp: Optional[float]
    torque_nm: Optional[float]
    mileage_kmpl: Optional[float]
    price_inr: Optional[float]
    primary_image_url: Optional[str] = None
    has_abs: bool
    model_config = {"from_attributes": True}


class VariantCompareResponse(BaseModel):
    """Used for side-by-side bike comparison."""
    variant_a: VariantSpecsResponse
    variant_b: VariantSpecsResponse
    differences: dict[str, Any]


# ─── Modifications ────────────────────────────────────────────────────────────

class ModificationCategoryResponse(BaseModel):
    id: uuid.UUID
    name: str
    slug: str
    category_enum: str
    description: Optional[str]
    icon_url: Optional[str]
    affects_performance: bool
    affects_mileage: bool
    sort_order: int
    model_config = {"from_attributes": True}


class ModificationBase(BaseModel):
    brand_name: str = Field(..., max_length=100)
    model_name: str = Field(..., max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    material: Optional[str] = None
    installation_time_minutes: Optional[int] = Field(None, ge=0)
    warranty_months: Optional[int] = Field(None, ge=0)
    price_inr: Optional[float] = Field(None, ge=0)
    installation_cost_inr: Optional[float] = Field(None, ge=0)


class ModificationCreate(ModificationBase):
    category_id: uuid.UUID
    hp_change_bhp: Optional[float] = None
    torque_change_nm: Optional[float] = None
    mileage_change_kmpl: Optional[float] = None
    weight_change_kg: Optional[float] = None


class ModificationResponse(ModificationBase):
    id: uuid.UUID
    slug: str
    category: ModificationCategoryResponse
    hp_change_bhp: Optional[float]
    hp_change_percent: Optional[float]
    torque_change_nm: Optional[float]
    torque_change_percent: Optional[float]
    mileage_change_kmpl: Optional[float]
    mileage_change_percent: Optional[float]
    weight_change_kg: Optional[float]
    average_rating: float
    review_count: int
    is_active: bool
    is_featured: bool
    requires_professional_install: bool
    is_legal_for_road: Optional[bool]
    images: List["ModImageResponse"] = []
    model_config = {"from_attributes": True}


class ModImageResponse(BaseModel):
    id: uuid.UUID
    url: str
    thumbnail_url: Optional[str]
    is_primary: bool
    sort_order: int
    model_config = {"from_attributes": True}


class ModificationListResponse(BaseModel):
    items: List[ModificationResponse]
    meta: PaginationMeta


class CompatibilityCheckRequest(BaseModel):
    variant_id: uuid.UUID
    modification_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=20)


class CompatibilityCheckResponse(BaseModel):
    variant_id: uuid.UUID
    results: List[dict]  # {modification_id, is_compatible, compatibility_type, notes, ai_confidence}
    overall_compatible: bool
