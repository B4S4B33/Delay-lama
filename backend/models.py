"""
Pydantic request/response models for the API.
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, time


class PredictionRequest(BaseModel):
    """Single flight prediction request."""
    airline: str = Field(..., description="Airline name (e.g., 'United Airlines')", examples=["United Airlines"])
    origin: str = Field(..., min_length=3, max_length=3, description="Origin airport code (e.g., 'ORD')", examples=["ORD"])
    dest: str = Field(..., min_length=3, max_length=3, description="Destination airport code (e.g., 'LAX')", examples=["LAX"])
    flight_date: date = Field(..., description="Flight date (YYYY-MM-DD)")
    scheduled_dep_time: time = Field(..., description="Scheduled departure time (HH:MM)")
    distance: Optional[int] = Field(None, description="Route distance in miles (auto-looked up if not provided)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "airline": "United Airlines",
                "origin": "ORD",
                "dest": "LAX",
                "flight_date": "2024-06-15",
                "scheduled_dep_time": "08:30",
                "distance": 1744
            }
        }


class TopFactor(BaseModel):
    """A single explainability factor."""
    feature: str = Field(..., description="Feature name")
    impact: float = Field(..., description="Impact magnitude (higher = more influence)")
    direction: str = Field(..., description="Whether this factor increases or decreases delay risk")


class PredictionResponse(BaseModel):
    """Prediction result with explainability."""
    predicted_delayed: bool = Field(..., description="True if model predicts delay (>=15 min)")
    delay_probability: float = Field(..., ge=0.0, le=1.0, description="Probability of delay (0.0 to 1.0)")
    confidence: str = Field(..., description="Confidence level: 'high', 'moderate', or 'low'")
    top_factors: List[TopFactor] = Field(..., description="Top 3 factors influencing this prediction")
    route_historical_delay_rate: Optional[float] = Field(None, description="Historical delay rate for this route")
    route_sample_count: Optional[int] = Field(None, description="Number of historical flights for this route")
    
    class Config:
        json_schema_extra = {
            "example": {
                "predicted_delayed": True,
                "delay_probability": 0.72,
                "confidence": "high",
                "top_factors": [
                    {"feature": "DepHour", "impact": 0.35, "direction": "increases"},
                    {"feature": "Airline", "impact": 0.22, "direction": "increases"},
                    {"feature": "Distance", "impact": 0.15, "direction": "decreases"}
                ],
                "route_historical_delay_rate": 0.28,
                "route_sample_count": 1250
            }
        }


class CompareAirlinesRequest(BaseModel):
    """Request to compare airlines on a route."""
    origin: str = Field(..., min_length=3, max_length=3)
    dest: str = Field(..., min_length=3, max_length=3)
    flight_date: date
    scheduled_dep_time: time


class AirlineComparison(BaseModel):
    """Single airline comparison result."""
    airline: str
    airline_name: str
    predicted_delayed: bool
    delay_probability: float


class CompareAirlinesResponse(BaseModel):
    """Response for airline comparison."""
    route: str
    comparisons: List[AirlineComparison]


class BatchUploadResponse(BaseModel):
    """Response for batch upload initiation."""
    batch_id: str
    status: str
    message: str


class BatchStatusResponse(BaseModel):
    """Response for batch upload status check."""
    batch_id: str
    file_name: str
    status: str
    total_rows: Optional[int] = None
    processed_rows: int = 0
    delayed_count: int = 0
    on_time_count: int = 0
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None


class ModelInfoResponse(BaseModel):
    """Model metadata response."""
    model_version: str
    training_data_range: str
    roc_auc: float
    accuracy: float
    precision: float
    recall: float
    total_features: int
    feature_list: List[str]
    confusion_matrix: dict
    is_active: bool = True


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    model_loaded: bool
    database_connected: bool
    version: str


class ErrorResponse(BaseModel):
    """Error response."""
    detail: str
    code: Optional[str] = None
