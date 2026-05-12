"""
Multi-Station Operations Model
For managing multiple fuel stations
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StationStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_MAINTENANCE = "under_maintenance"
    CLOSED = "closed"


class Station(Document):
    """Multi-station operations model"""
    station_id: str = Field(..., unique=True)
    name: str = Field(...)
    location: str = Field(...)
    address: str = Field(...)
    city: str = Field(...)
    district: str = Field(...)
    
    # Contact
    manager_name: str = Field(...)
    manager_phone: str = Field(...)
    manager_email: str = Field(...)
    
    # Operations
    status: StationStatus = Field(default=StationStatus.ACTIVE)
    opening_time: str = Field(default="06:00")
    closing_time: str = Field(default="22:00")
    
    # Capacity
    total_tank_capacity: float = Field(default=0)
    number_of_pumps: int = Field(default=0)
    number_of_tanks: int = Field(default=0)
    
    # Financials
    monthly_revenue_target: Optional[float] = Field(None)
    current_month_revenue: float = Field(default=0)
    
    # Staff
    staff_count: int = Field(default=0)
    
    # RURA License
    rura_license_number: Optional[str] = Field(None)
    rura_license_expiry: Optional[datetime] = Field(None)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "stations"
