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


class PricingType(str, Enum):
    RETAIL = "retail"
    WHOLESALE = "wholesale"
    BULK = "bulk"


class FuelPricing(Document):
    """Fuel pricing model for managing fuel prices based on RURA guidelines"""
    pricing_id: str = Field(..., unique=True)
    fuel_type: FuelType
    pricing_type: PricingType = Field(default=PricingType.RETAIL)
    price_per_liter: float = Field(..., gt=0)
    vat_percentage: float = Field(default=18, description="VAT percentage for Rwanda")
    excise_tax_percentage: float = Field(default=0)
    effective_date: datetime = Field(default_factory=datetime.utcnow)
    expiry_date: Optional[datetime] = Field(None)
    is_active: bool = Field(default=True)
    approved_by: str = Field(..., description="Superadmin who approved the pricing")
    approval_date: datetime = Field(default_factory=datetime.utcnow)
    rura_reference: Optional[str] = Field(None, description="RURA reference number for pricing approval")
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "fuel_pricing"


class PartnerAgreement(Document):
    """Partner agreements and commission structures"""
    agreement_id: str = Field(..., unique=True)
    partner_name: str
    partner_type: str = Field(..., description="supplier, distributor, etc.")
    agreement_start_date: datetime
    agreement_end_date: Optional[datetime] = Field(None)
    commission_percentage: float = Field(default=0, ge=0, le=100)
    credit_terms_days: int = Field(default=30)
    minimum_order_quantity: float = Field(default=0)
    discount_percentage: float = Field(default=0)
    is_active: bool = Field(default=True)
    contact_person: str
    contact_email: str
    contact_phone: str
    notes: Optional[str] = Field(None)
    approved_by: str = Field(..., description="Superadmin who approved the agreement")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "partner_agreements"
