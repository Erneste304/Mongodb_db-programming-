"""
Fuel Consumption Tracking Models
For tracking consumption rates and predicting reorder needs
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ConsumptionPeriod(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


class ConsumptionRecord(Document):
    """Fuel consumption tracking record"""
    record_id: str = Field(..., unique=True)
    tank_id: str = Field(...)
    fuel_type: str = Field(...)
    period: ConsumptionPeriod = Field(default=ConsumptionPeriod.DAILY)
    start_date: datetime = Field(...)
    end_date: datetime = Field(...)
    
    # Consumption data
    opening_level_liters: float = Field(...)
    closing_level_liters: float = Field(...)
    dispensed_liters: float = Field(default=0)
    deliveries_liters: float = Field(default=0)
    net_consumption_liters: float = Field(default=0)
    
    # Rate calculations
    consumption_rate_liters_per_day: float = Field(default=0)
    average_daily_consumption: float = Field(default=0)
    
    # Prediction
    estimated_days_until_empty: float = Field(default=0)
    recommended_reorder_date: Optional[datetime] = Field(None)
    recommended_reorder_quantity_liters: float = Field(default=0)
    
    recorded_by: str = Field(...)
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "consumption_records"


class ReorderPrediction(Document):
    """Reorder prediction and recommendation"""
    prediction_id: str = Field(..., unique=True)
    tank_id: str = Field(...)
    fuel_type: str = Field(...)
    
    # Current state
    current_level_liters: float = Field(...)
    capacity_liters: float = Field(...)
    current_fill_percentage: float = Field(...)
    
    # Predictions
    predicted_consumption_rate: float = Field(...)
    estimated_days_until_empty: float = Field(...)
    estimated_empty_date: datetime = Field(...)
    
    # Recommendations
    recommended_reorder_date: datetime = Field(...)
    recommended_reorder_quantity_liters: float = Field(...)
    urgency_level: str = Field(default="normal", description="critical, high, normal, low")
    
    # Supplier info
    suggested_supplier: Optional[str] = Field(None)
    estimated_lead_time_days: int = Field(default=3)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    valid_until: datetime = Field(...)
    
    class Settings:
        collection_name = "reorder_predictions"
