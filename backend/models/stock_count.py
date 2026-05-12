"""
Stock Count Models
For regular stock counts and inventory verification
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class StockCountType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    ANNUAL = "annual"
    SPOT_CHECK = "spot_check"


class StockCountStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DISCREPANCY_FOUND = "discrepancy_found"
    CANCELLED = "cancelled"


class StockCount(Document):
    """Regular stock count records"""
    count_id: str = Field(..., unique=True)
    count_type: StockCountType = Field(default=StockCountType.DAILY)
    status: StockCountStatus = Field(default=StockCountStatus.SCHEDULED)
    
    # Tank counts
    tank_id: Optional[str] = Field(None)
    fuel_type: Optional[str] = Field(None)
    
    # Dip stick readings
    dip_stick_reading_before: Optional[float] = Field(None)
    dip_stick_reading_after: Optional[float] = Field(None)
    electronic_meter_reading: Optional[float] = Field(None)
    
    # System vs Physical
    system_level_liters: float = Field(...)
    physical_count_liters: float = Field(...)
    variance_liters: float = Field(default=0)
    variance_percentage: float = Field(default=0)
    
    # Shop inventory counts
    shop_items_counted: int = Field(default=0)
    shop_items_with_variance: int = Field(default=0)
    
    # Lubricant counts
    lubricant_items_counted: int = Field(default=0)
    lubricant_items_with_variance: int = Field(default=0)
    
    # Count details
    counted_by: str = Field(...)
    verified_by: Optional[str] = Field(None)
    scheduled_date: datetime = Field(...)
    completed_date: Optional[datetime] = Field(None)
    shift: str = Field(default="day", description="day, night")
    
    # Discrepancy investigation
    discrepancy_reason: Optional[str] = Field(None)
    investigation_notes: Optional[str] = Field(None)
    corrective_action: Optional[str] = Field(None)
    
    # Approval
    approved_by: Optional[str] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "stock_counts"


class StockCountItem(Document):
    """Individual item counts within a stock count"""
    item_count_id: str = Field(..., unique=True)
    count_id: str = Field(...)
    item_type: str = Field(..., description="tank, shop_item, lubricant")
    item_id: str = Field(...)
    item_name: str = Field(...)
    
    # System vs Physical
    system_quantity: float = Field(...)
    physical_quantity: float = Field(...)
    variance: float = Field(default=0)
    unit_of_measure: str = Field(default="liters")
    
    # Details
    location: Optional[str] = Field(None)
    batch_number: Optional[str] = Field(None)
    expiry_date: Optional[datetime] = Field(None)
    
    # Discrepancy
    has_discrepancy: bool = Field(default=False)
    discrepancy_reason: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "stock_count_items"
