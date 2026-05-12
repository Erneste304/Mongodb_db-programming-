"""
Pump Management Models
For managing fuel pump status and operations
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PumpStatus(str, Enum):
    AVAILABLE = "available"
    IN_USE = "in_use"
    MAINTENANCE = "maintenance"
    OUT_OF_SERVICE = "out_of_service"


class Pump(Document):
    """Fuel pump management"""
    pump_id: str = Field(..., unique=True)
    pump_number: int = Field(..., description="Physical pump number")
    tank_id: str = Field(..., description="Connected tank ID")
    fuel_type: str = Field(...)
    status: PumpStatus = Field(default=PumpStatus.AVAILABLE)
    current_customer: Optional[str] = Field(None, description="Customer ID currently using pump")
    current_transaction_id: Optional[str] = Field(None)
    last_service_date: Optional[datetime] = Field(None)
    next_service_due: Optional[datetime] = Field(None)
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "pumps"


class PumpSession(Document):
    """Individual pump usage session"""
    session_id: str = Field(..., unique=True)
    pump_id: str = Field(...)
    customer_id: Optional[str] = Field(None)
    transaction_id: Optional[str] = Field(None)
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = Field(None)
    fuel_dispensed_liters: float = Field(default=0)
    total_amount: float = Field(default=0)
    status: str = Field(default="active", description="active, completed, cancelled")
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "pump_sessions"
