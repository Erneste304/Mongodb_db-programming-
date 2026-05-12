"""
Expenditure Approval Model
For managing large expenditure approvals
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ExpenditureType(str, Enum):
    EQUIPMENT_PURCHASE = "equipment_purchase"
    MAINTENANCE = "maintenance"
    RENOVATION = "renovation"
    MARKETING = "marketing"
    TRAINING = "training"
    OTHER = "other"


class ExpenditureStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"


class ExpenditureRequest(Document):
    """Large expenditure approval requests"""
    request_id: str = Field(..., unique=True)
    expenditure_type: ExpenditureType = Field(...)
    title: str = Field(...)
    description: str = Field(...)
    amount: float = Field(..., gt=0)
    
    # Requester
    requested_by: str = Field(...)
    requester_role: str = Field(...)
    requester_department: str = Field(...)
    
    # Approval
    status: ExpenditureStatus = Field(default=ExpenditureStatus.PENDING)
    approved_by: Optional[str] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    rejection_reason: Optional[str] = Field(None)
    
    # Payment
    payment_method: Optional[str] = Field(None)
    payment_reference: Optional[str] = Field(None)
    paid_at: Optional[datetime] = Field(None)
    
    # Supporting documents
    quote_document_url: Optional[str] = Field(None)
    invoice_document_url: Optional[str] = Field(None)
    
    # Budget
    budget_code: Optional[str] = Field(None)
    budget_category: Optional[str] = Field(None)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "expenditure_requests"
