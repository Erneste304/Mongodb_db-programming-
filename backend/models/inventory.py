from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    KEROSENE = "kerosene"
    LUBRICANT = "lubricant"


class TankStatus(str, Enum):
    ACTIVE = "active"
    MAINTENANCE = "maintenance"
    INACTIVE = "inactive"


class DeliveryStatus(str, Enum):
    PENDING = "pending"
    DELIVERED = "delivered"
    VERIFIED = "verified"
    CANCELLED = "cancelled"


class Tank(Document):
    tank_id: str = Field(..., unique=True)
    tank_number: str = Field(..., description="Physical tank number at station")
    fuel_type: FuelType
    capacity_liters: float = Field(..., gt=0)
    current_level_liters: float = Field(default=0, ge=0)
    threshold_alert_percent: float = Field(default=20, description="Alert when below this %")
    status: TankStatus = Field(default=TankStatus.ACTIVE)
    calibration_certificate_number: Optional[str] = Field(None)
    calibration_expiry_date: Optional[datetime] = Field(None)
    station_id: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "tanks"


class FuelDelivery(Document):
    delivery_id: str = Field(..., unique=True)
    tank_id: str
    supplier_name: str
    supplier_invoice_number: str
    fuel_type: FuelType
    quantity_delivered_liters: float = Field(..., gt=0)
    quantity_verified_liters: Optional[float] = Field(None)
    dip_stick_reading_before: Optional[float] = Field(None)
    dip_stick_reading_after: Optional[float] = Field(None)
    price_per_liter: float = Field(..., gt=0)
    total_cost: float = Field(..., gt=0)
    delivery_date: datetime = Field(default_factory=datetime.utcnow)
    delivered_by: str = Field(..., description="Driver name")
    verified_by: Optional[str] = Field(None, description="Staff ID who verified")
    status: DeliveryStatus = Field(default=DeliveryStatus.PENDING)
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "fuel_deliveries"


class InventoryRecord(Document):
    record_id: str = Field(..., unique=True)
    tank_id: str
    fuel_type: FuelType
    opening_level_liters: float
    closing_level_liters: float
    dispensed_liters: float = Field(default=0)
    deliveries_liters: float = Field(default=0)
    recorded_by: str
    record_date: datetime = Field(default_factory=datetime.utcnow)
    shift: str = Field(default="day", description="day, night")
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "inventory_records"
