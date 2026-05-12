"""
Lubricants and Oil Inventory Models
For managing lubricants, oil, and shop inventory
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class LubricantCategory(str, Enum):
    ENGINE_OIL = "engine_oil"
    TRANSMISSION_OIL = "transmission_oil"
    BRAKE_FLUID = "brake_fluid"
    COOLANT = "coolant"
    GREASE = "grease"
    ADDITIVES = "additives"
    OTHER = "other"


class LubricantItem(Document):
    """Lubricant and oil inventory items"""
    item_id: str = Field(..., unique=True)
    item_name: str = Field(...)
    category: LubricantCategory
    brand: Optional[str] = Field(None)
    specification: Optional[str] = Field(None, description="e.g., 5W-30, API SN")
    
    # Stock
    current_stock: float = Field(default=0, description="In liters or units")
    unit_of_measure: str = Field(default="liters", description="liters, units, bottles")
    reorder_level: float = Field(default=50)
    max_stock: float = Field(default=500)
    
    # Pricing
    cost_price: float = Field(..., gt=0)
    selling_price: float = Field(..., gt=0)
    
    # Storage
    storage_location: Optional[str] = Field(None, description="Shelf/warehouse location")
    storage_conditions: Optional[str] = Field(None, description="Temperature requirements, etc.")
    expiry_date: Optional[datetime] = Field(None)
    
    # Supplier
    supplier: Optional[str] = Field(None)
    supplier_code: Optional[str] = Field(None)
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "lubricant_items"


class LubricantStockCount(Document):
    """Regular stock count records for lubricants"""
    count_id: str = Field(..., unique=True)
    item_id: str = Field(...)
    item_name: str = Field(...)
    
    # Count data
    counted_quantity: float = Field(...)
    system_quantity: float = Field(...)
    variance: float = Field(default=0)
    variance_percentage: float = Field(default=0)
    
    # Count details
    counted_by: str = Field(...)
    counted_at: datetime = Field(default_factory=datetime.utcnow)
    count_type: str = Field(default="regular", description="regular, spot_check, annual")
    
    # Discrepancy
    discrepancy_reason: Optional[str] = Field(None)
    action_taken: Optional[str] = Field(None)
    
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "lubricant_stock_counts"
