"""
BikeVerse AI — Data Collector Schemas
Pydantic schemas for Brands, Motorcycle Technical Specs, Image Metadata, and Dataset Exports.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, HttpUrl, ConfigDict


class BrandSchema(BaseModel):
    """Schema for a motorcycle manufacturer brand."""
    id: str = Field(..., description="Unique slug for the brand")
    brand_name: str
    slug: str
    country: str
    year_founded: Optional[int] = None
    official_website: Optional[str] = None
    parent_company: Optional[str] = None
    description: Optional[str] = None
    popular_models: List[str] = Field(default_factory=list)
    logo_path: Optional[str] = None
    cover_path: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MotorcycleSpecsSchema(BaseModel):
    """Schema for complete motorcycle technical specifications."""
    id: str = Field(..., description="Unique slug for the motorcycle model/variant")
    brand: str
    brand_slug: str
    model_name: str
    model_slug: str
    generation: Optional[str] = "Gen 1"
    year: int
    category: str
    engine_cc: float
    power_hp: float
    torque_nm: float
    fuel_tank_l: float
    mileage_kmpl: float
    transmission: str = "6-Speed Manual"
    weight_kg: float = 160.0
    seat_height_mm: float = 800.0
    ground_clearance_mm: float = 160.0
    wheelbase_mm: float = 1380.0
    has_abs: bool = True
    top_speed_kmh: float = 140.0
    fuel_type: str = "Petrol"
    cooling_type: str = "Liquid Cooled"
    cylinders: int = 1
    price_inr: float = 0.0
    price_usd: Optional[float] = None
    color_variants: List[str] = Field(default_factory=list)
    image_paths: List[str] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class ImageMetadataSchema(BaseModel):
    """Metadata schema for collected high-resolution images."""
    id: str
    filename: str
    rel_path: str
    view_type: str  # front, rear, left, right, dashboard, engine, exhaust, color1, etc.
    resolution: str  # e.g., "1920x1080"
    width: int
    height: int
    file_size_kb: float
    phash: str
    source_url: str
    license: str = "Legal Public / Wikipedia Commons"


class DatasetModelWrapper(BaseModel):
    """Model wrapper containing spec and images metadata."""
    brand: str
    model: str
    year: int
    category: str
    engine: str
    specs: MotorcycleSpecsSchema
    images: Dict[str, str]  # view_type -> image path mapping
    all_image_paths: List[str]


class DatasetExportSchema(BaseModel):
    """Wrapper for dataset export formats."""
    total_brands: int
    total_models: int
    total_images: int
    brands: List[BrandSchema]
    models: List[MotorcycleSpecsSchema]
