from __future__ import annotations
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class DatasetHealth(BaseModel):
    total_rows: int
    valid_rows: int
    missing_values: Dict[str, int]
    health_score: float = Field(..., description="Percentage of usable data (0-100)")

class CustomerSegment(BaseModel):
    new: int
    repeat: int
    high_value: int
    at_risk: int

class TopCustomer(BaseModel):
    name: str
    revenue: float
    rank: int

class ProductClassification(BaseModel):
    product: str
    category: str # "Fast Moving", "Growing", "Declining", "Stable"
    volume_delta: float

class TopProduct(BaseModel):
    product: str
    revenue: float
    volume: int

class DemandForecastPoint(BaseModel):
    period: str
    baseline: float
    upper_bound: float
    lower_bound: float

class ProductionGap(BaseModel):
    required: float
    available: float
    gap: float
    status: str # "Surplus", "Shortage", "Balanced"

class SalesIntelligenceResponse(BaseModel):
    dataset_health: DatasetHealth
    customer_patterns: Dict[str, any] # Using dict for flexible segmentation
    top_customers: List[TopCustomer]
    product_intelligence: List[ProductClassification]
    top_products: List[TopProduct]
    demand_forecast: List[DemandForecastPoint]
    production_gap: Optional[ProductionGap] = None
    forecast_confidence: str # "High", "Medium", "Low"
    confidence_explanation: str
