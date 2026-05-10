from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class PaymentType(str, Enum):
    SUPPLIER_PAYMENT = "supplier_payment"
    SALARY_PAYMENT = "salary_payment"
    EXPENSE = "expense"
    REFUND = "refund"
    DEPOSIT = "deposit"


class PaymentMethod(str, Enum):
    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    MOBILE_MONEY = "mobile_money"
    CHECK = "check"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    PROCESSED = "processed"
    CANCELLED = "cancelled"


class ExpenseCategory(str, Enum):
    FUEL_PURCHASE = "fuel_purchase"
    SALARIES = "salaries"
    UTILITIES = "utilities"
    MAINTENANCE = "maintenance"
    SUPPLIES = "supplies"
    TAXES = "taxes"
    OTHER = "other"


class Payment(Document):
    payment_id: str = Field(..., unique=True)
    payment_type: PaymentType
    amount: float = Field(..., gt=0)
    payment_method: PaymentMethod
    recipient_name: str
    recipient_account: Optional[str] = Field(None)
    reference_number: Optional[str] = Field(None)
    description: str
    category: Optional[ExpenseCategory] = Field(None)
    status: PaymentStatus = Field(default=PaymentStatus.PENDING)
    requested_by: str = Field(..., description="User ID who requested payment")
    approved_by: Optional[str] = Field(None, description="User ID who approved payment")
    processed_by: Optional[str] = Field(None, description="User ID who processed payment")
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    approved_at: Optional[datetime] = Field(None)
    processed_at: Optional[datetime] = Field(None)
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "payments"


class DailyCashReconciliation(Document):
    reconciliation_id: str = Field(..., unique=True)
    date: datetime = Field(default_factory=datetime.utcnow)
    opening_balance: float = Field(default=0)
    cash_sales: float = Field(default=0)
    mobile_money_sales: float = Field(default=0)
    card_sales: float = Field(default=0)
    credit_sales: float = Field(default=0)
    total_sales: float = Field(default=0)
    cash_paid_out: float = Field(default=0)
    bank_deposit: float = Field(default=0)
    closing_balance: float = Field(default=0)
    variance: float = Field(default=0)
    reconciled_by: str
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "cash_reconciliations"


class PettyCash(Document):
    transaction_id: str = Field(..., unique=True)
    transaction_type: str = Field(..., description="deposit, withdrawal")
    amount: float = Field(..., gt=0)
    description: str
    category: Optional[ExpenseCategory] = Field(None)
    performed_by: str
    balance_after: float = Field(..., description="Petty cash balance after transaction")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "petty_cash"
