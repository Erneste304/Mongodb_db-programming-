"""
Customer Billing and Invoice Models
For managing credit customer billing, monthly statements, and invoices
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PAID = "paid"
    PARTIALLY_PAID = "partially_paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class Invoice(Document):
    """Invoice for credit customers"""
    invoice_id: str = Field(..., unique=True)
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    customer_tin: Optional[str] = Field(None)
    
    # Invoice details
    invoice_number: str = Field(...)
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime = Field(...)
    billing_period_start: datetime = Field(...)
    billing_period_end: datetime = Field(...)
    
    # Financials
    subtotal: float = Field(default=0)
    vat_amount: float = Field(default=0)
    total_amount: float = Field(default=0)
    amount_paid: float = Field(default=0)
    balance_due: float = Field(default=0)
    
    # Transaction references
    transaction_ids: List[str] = Field(default_factory=list)
    
    # Status
    status: InvoiceStatus = Field(default=InvoiceStatus.DRAFT)
    
    # Payment tracking
    payment_reference: Optional[str] = Field(None)
    paid_at: Optional[datetime] = Field(None)
    
    # Company details for invoice
    company_name: Optional[str] = Field(None)
    company_address: Optional[str] = Field(None)
    
    # EBM fields
    receipt_number: Optional[str] = Field(None)
    ebm_signature: Optional[str] = Field(None)
    ebm_mrc: Optional[str] = Field(None)
    ebm_signed_at: Optional[datetime] = Field(None)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "invoices"


class InvoiceItem(Document):
    """Individual line items in an invoice"""
    item_id: str = Field(..., unique=True)
    invoice_id: str = Field(...)
    
    # Item details
    item_type: str = Field(..., description="fuel, lubricant, shop_item")
    description: str = Field(...)
    quantity: float = Field(...)
    unit_price: float = Field(...)
    subtotal: float = Field(...)
    
    # Reference to original transaction
    transaction_id: Optional[str] = Field(None)
    
    # Date of purchase
    purchase_date: datetime = Field(...)
    
    class Settings:
        collection_name = "invoice_items"


class MonthlyStatement(Document):
    """Monthly billing statement for credit customers"""
    statement_id: str = Field(..., unique=True)
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    
    # Statement period
    statement_month: int = Field(..., ge=1, le=12)
    statement_year: int = Field(...)
    period_start: datetime = Field(...)
    period_end: datetime = Field(...)
    
    # Financial summary
    opening_balance: float = Field(default=0)
    purchases: float = Field(default=0)
    payments: float = Field(default=0)
    adjustments: float = Field(default=0)
    closing_balance: float = Field(default=0)
    
    # Transaction counts
    fuel_transactions: int = Field(default=0)
    lubricant_transactions: int = Field(default=0)
    shop_transactions: int = Field(default=0)
    total_transactions: int = Field(default=0)
    
    # Invoice reference
    invoice_id: Optional[str] = Field(None)
    
    # Status
    sent: bool = Field(default=False)
    sent_at: Optional[datetime] = Field(None)
    viewed: bool = Field(default=False)
    viewed_at: Optional[datetime] = Field(None)
    
    # Delivery method
    delivery_method: str = Field(default="email", description="email, sms, print")
    delivery_address: Optional[str] = Field(None)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "monthly_statements"


class Payment(Document):
    """Payment received from credit customers"""
    payment_id: str = Field(..., unique=True)
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    
    # Payment details
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., description="bank_transfer, cash, mobile_money, check")
    payment_reference: Optional[str] = Field(None)
    payment_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Invoice(s) being paid
    invoice_ids: List[str] = Field(default_factory=list)
    
    # Status
    status: str = Field(default="completed", description="pending, completed, failed")
    
    # Recorded by
    recorded_by: str = Field(...)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "customer_payments"
