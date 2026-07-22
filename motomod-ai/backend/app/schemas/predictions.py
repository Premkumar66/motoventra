"""
MotoMod AI — Pydantic Schemas for AI Predictions
Standardized input and output interfaces for the 11 Machine Learning models.
"""
import uuid
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


# ─── Inputs ───────────────────────────────────────────────────────────────────

class PerformancePredictionRequest(BaseModel):
    variant_id: uuid.UUID = Field(..., description="Target motorcycle variant ID")
    modification_ids: List[uuid.UUID] = Field(..., min_length=1, max_length=20, description="List of planned accessories")


class BudgetRecommendationRequest(BaseModel):
    variant_id: uuid.UUID
    target_budget_inr: float = Field(..., ge=0)
    primary_goal: str = Field("performance", pattern="^(performance|mileage|styling|safety)$")


class MaintenancePredictionRequest(BaseModel):
    variant_id: uuid.UUID
    current_odometer_km: float = Field(..., ge=0)
    last_service_months_ago: int = Field(0, ge=0)
    riding_style: str = Field("commuter", pattern="^(commuter|highway|track|offroad)$")


class ResaleValueRequest(BaseModel):
    variant_id: uuid.UUID
    year_of_manufacture: int = Field(..., ge=1980, le=2030)
    odometer_reading_km: float = Field(..., ge=0)
    ownership_count: int = Field(1, ge=1, le=5)
    overall_condition: str = Field("good", pattern="^(excellent|good|fair|poor)$")


class SentimentAnalysisRequest(BaseModel):
    review_text: str = Field(..., min_length=5, max_length=2000)


# ─── Outputs ──────────────────────────────────────────────────────────────────

class PerformancePredictionResponse(BaseModel):
    variant_id: uuid.UUID
    base_specs: Dict[str, float]       # {bhp, torque, mileage, top_speed}
    predicted_specs: Dict[str, float]  # {bhp, torque, mileage, top_speed}
    differences: Dict[str, float]      # {bhp_gain, torque_gain, mileage_gain, top_speed_gain}
    confidence_score: float
    model_version: str


class RecommendationsListResponse(BaseModel):
    variant_id: uuid.UUID
    recommended_accessories: List[Dict[str, Any]]  # [{mod_id, brand, model, score, reason}]
    total_estimated_cost_inr: float


class MaintenancePredictionResponse(BaseModel):
    next_service_due_km: float
    estimated_service_cost_inr: float
    recommended_checks: List[str]
    risk_level: str


class ResaleValueResponse(BaseModel):
    estimated_resale_value_inr: float
    confidence_range_lower_inr: float
    confidence_range_upper_inr: float
    depreciation_rate_annual_percent: float


class SentimentAnalysisResponse(BaseModel):
    sentiment: str  # positive | neutral | negative
    sentiment_score: float
    confidence: float
