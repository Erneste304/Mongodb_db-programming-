"""
Supplier Management Models
For coordinating with suppliers for timely deliveries
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class SupplierStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    UNDER_REVIEW = "under_review"


class Supplier(Document):
    """Fuel and lubricant suppliers"""
    supplier_id: str = Field(..., unique=True)
    supplier_name: str = Field(...)
    contact_person: str = Field(...)
    phone: str = Field(...)
    email: Optional[str] = Field(None)
    
    # Address
    address: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    country: str = Field(default="Rwanda")
    
    # Products
    supplied_fuel_types: List[str] = Field(default_factory=list)
    supplied_lubricant_brands: List[str] = Field(default_factory=list)
    
    # Performance
    rating: float = Field(default=5.0, ge=0, le=5)
    total_deliveries: int = Field(default=0)
    on_time_delivery_rate: float = Field(default=100.0)
    
    # Payment terms
    payment_terms: str = Field(default="Net 30")
    credit_limit: Optional[float] = Field(None)
    
    # Status
    status: SupplierStatus = Field(default=SupplierStatus.ACTIVE)
    
    # Tax
    tin_number: Optional[str] = Field(None)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "suppliers"


class DeliverySchedule(Document):
    """Scheduled fuel deliveries"""
    schedule_id: str = Field(..., unique=True)
    tank_id: str = Field(...)
    fuel_type: str = Field(...)
    supplier_id: str = Field(...)
    
    # Schedule details
    scheduled_date: datetime = Field(...)
    requested_quantity_liters: float = Field(...)
    estimated_cost: float = Field(...)
    
    # Status
    status: str = Field(default="scheduled", description="scheduled, confirmed, in_transit, delivered, cancelled")
    
    # Confirmation
    confirmed_by: Optional[str] = Field(None)
    confirmed_at: Optional[datetime] = Field(None)
    
    # Delivery
    actual_delivery_date: Optional[datetime] = Field(None)
    actual_quantity_delivered: Optional[float] = Field(None)
    delivery_notes: Optional[str] = Field(None)
    
    # Order reference
    purchase_order_number: Optional[str] = Field(None)
    
    created_by: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "delivery_schedules"
