from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class VisitorType(str, Enum):
    DELIVERY_DRIVER = "delivery_driver"
    INSPECTOR = "inspector"
    CONTRACTOR = "contractor"
    SALES_REP = "sales_rep"
    OTHER = "other"


class VisitPurpose(str, Enum):
    FUEL_DELIVERY = "fuel_delivery"
    SAFETY_INSPECTION = "safety_inspection"
    MAINTENANCE = "maintenance"
    SALES_MEETING = "sales_meeting"
    AUDIT = "audit"


class VisitorLog(Document):
    """Visitor sign-in/sign-out log"""
    visitor_name: str = Field(...)
    company_name: Optional[str] = Field(None)
    visitor_phone: str = Field(...)
    visitor_type: VisitorType = Field(...)
    purpose: VisitPurpose = Field(...)
    id_number: Optional[str] = Field(None, description="National ID or Passport")
    
    check_in_time: datetime = Field(default_factory=datetime.utcnow)
    check_out_time: Optional[datetime] = Field(None)
    
    escort_required: bool = Field(default=False)
    escorted_by: Optional[str] = Field(None, description="Staff member ID")
    
    safety_briefing_completed: bool = Field(default=False)
    
    notes: Optional[str] = Field(None)
    status: str = Field(default="on_site", description="on_site, completed")
    
    class Settings:
        collection_name = "visitor_logs"


class PartnerType(str, Enum):
    FUEL_SUPPLIER = "fuel_supplier"
    SERVICE_PROVIDER = "service_provider"
    FINANCIAL_PARTNER = "financial_partner"
    BUSINESS_PARTNER = "business_partner"


class BusinessPartner(Document):
    """External business partners and service providers"""
    partner_id: str = Field(..., unique=True)
    name: str = Field(...)
    partner_type: PartnerType = Field(...)
    contact_person: str = Field(...)
    email: str = Field(...)
    phone: str = Field(...)
    address: Optional[str] = Field(None)
    tin_number: Optional[str] = Field(None)
    
    # Contract details
    contract_start_date: datetime = Field(...)
    contract_end_date: Optional[datetime] = Field(None)
    is_active: bool = Field(default=True)
    
    commission_rate: float = Field(default=0.0, description="Percentage commission if applicable")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "business_partners"
