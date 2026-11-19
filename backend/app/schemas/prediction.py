"""Pydantic request/response schemas."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class PredictionRequest(BaseModel):
    """Car details sent by the client. Allowed values are checked against the
    training catalog in the service layer (so they always match the dataset)."""

    brand: str = Field(..., min_length=1, max_length=60, examples=["Maruti"])
    model: str = Field(..., min_length=1, max_length=80, examples=["Swift Dzire"])
    manufacture_year: int = Field(..., ge=1990, le=2030, examples=[2017])
    kms_driven: int = Field(..., ge=0, le=1_000_000, examples=[45000])
    fuel_type: str = Field(..., examples=["Petrol"])
    transmission: str = Field(..., examples=["Manual"])
    ownership: int = Field(..., ge=0, le=5, examples=[1])
    engine_cc: int = Field(..., ge=500, le=8000, examples=[1197])
    seats: int = Field(..., ge=2, le=10, examples=[5])

    @field_validator("brand", "model", "fuel_type", "transmission")
    @classmethod
    def strip(cls, v: str) -> str:
        return v.strip()


class PredictionResult(BaseModel):
    predicted_price: float
    price_low: float
    price_high: float
    price_category: str


class PredictionRecord(PredictionRequest, PredictionResult):
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    disclaimer: str = ("Estimate from a machine-learning model trained on historical listings; "
                       "not a guaranteed market price.")


class HistoryPage(BaseModel):
    total: int
    items: list[PredictionRecord]


class BrandCount(BaseModel):
    brand: str
    count: int


class PricePoint(BaseModel):
    id: int
    created_at: datetime
    predicted_price: float


class DashboardStats(BaseModel):
    total_predictions: int
    average_predicted_price: float
    top_brands: list[BrandCount]
    category_counts: dict[str, int]
    fuel_counts: dict[str, int]
    recent_prices: list[PricePoint]
