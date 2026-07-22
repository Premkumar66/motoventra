"""
MotoMod AI — Pydantic Schemas for Builds & Comparisons
"""
import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field

from app.schemas.motorcycle import VariantSpecsResponse, ModificationResponse


# ─── User Build ───────────────────────────────────────────────────────────────

class BuildModificationItem(BaseModel):
    modification_id: uuid.UUID
    quantity: int = 1
    notes: Optional[str] = None


class BuildCreateRequest(BaseModel):
    variant_id: uuid.UUID = Field(..., description="The base motorcycle variant")
    name: str = Field(..., max_length=200, description="Name of this build")
    description: Optional[str] = Field(None, description="Description of the build details")
    modifications: List[BuildModificationItem] = Field(default=[], description="List of accessories to add")
    is_public: bool = False


class BuildResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    variant_id: uuid.UUID
    name: str
    description: Optional[str]
    is_public: bool
    total_mod_cost_inr: float
    total_install_cost_inr: float
    predicted_hp_bhp: Optional[float]
    predicted_torque_nm: Optional[float]
    predicted_mileage_kmpl: Optional[float]
    predicted_top_speed_kmh: Optional[float]
    created_at: datetime
    model_config = {"from_attributes": True}


class BuildDetailResponse(BuildResponse):
    variant: VariantSpecsResponse
    modifications: List[ModificationResponse] = []


class CompareBuildsResponse(BaseModel):
    build_a: BuildResponse
    build_b: BuildResponse
    metrics_comparison: Dict[str, Dict[str, float]]  # {hp: {a: 20, b: 22, diff: 2}, ...}
