from beanie import Document, Link
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class FuelType(str, Enum):
    PETROL = "petrol"
    DIESEL = "diesel"
    KEROSENE = "kerosene"
    LUBRICANT = "lubricant"


class PaymentMethod(str, Enum):
    CASH = "cash"
    MOBILE_MONEY = "mobile_money"
    CARD = "card"
    CREDIT = "credit"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    VOIDED = "voided"
    REFUNDED = "refunded"
    MODIFIED = "modified"  # Superadmin override


class Transaction(Document):
    transaction_id: str = Field(..., unique=True)
    customer_id: Optional[str] = Field(None, description="Customer ID (null for cash customers)")
    fuel_type: FuelType
    quantity_liters: float = Field(..., gt=0)
    price_per_liter: float = Field(..., gt=0)
    total_amount: float = Field(..., gt=0)
    vat_amount: float = Field(default=0.0, description="18% VAT amount included in total")
    net_amount: float = Field(default=0.0, description="Amount before VAT")
    payment_method: PaymentMethod
    payment_reference: Optional[str] = Field(None, description="Mobile money reference or card transaction ID")
    pump_number: Optional[int] = Field(None)
    attendant_id: Optional[str] = Field(None, description="Staff ID who processed the transaction")
    status: TransactionStatus = Field(default=TransactionStatus.COMPLETED)
    voided_by: Optional[str] = Field(None, description="User ID who voided the transaction")
    voided_at: Optional[datetime] = Field(None)
    void_reason: Optional[str] = Field(None)
    notes: Optional[str] = Field(None, description="Additional notes including override history")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Rwanda-specific EBM (Electronic Billing Machine) fields
    receipt_number: Optional[str] = Field(None)
    tin_number: Optional[str] = Field(None, description="Customer TIN for receipts")
    ebm_signature: Optional[str] = Field(None, description="RRA SCD Signature")
    ebm_mrc: Optional[str] = Field(None, description="Machine Record Code")
    ebm_internal_data: Optional[str] = Field(None, description="EBM Internal Data")
    ebm_signed_at: Optional[datetime] = Field(None)
    
    class Settings:
        collection_name = "transactions"


class Customer(Document):
    customer_id: str = Field(..., unique=True)
    name: str
    phone: Optional[str] = Field(None)
    email: Optional[str] = Field(None)
    tin_number: Optional[str] = Field(None, description="Tax Identification Number")
    customer_type: str = Field(default="cash", description="cash, credit, loyalty")
    credit_limit: Optional[float] = Field(default=0)
    current_balance: float = Field(default=0)
    loyalty_points: int = Field(default=0)
    
    # Corporate account details (for credit customers)
    company_name: Optional[str] = Field(None)
    company_address: Optional[str] = Field(None)
    billing_contact: Optional[str] = Field(None)
    billing_email: Optional[str] = Field(None)
    billing_phone: Optional[str] = Field(None)
    payment_terms: str = Field(default="Net 30", description="Payment terms for credit customers")
    
    # Vehicle registration (for corporate accounts)
    registered_vehicles: List[str] = Field(default_factory=list, description="Vehicle registration numbers")
    
    is_active: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "customers"
