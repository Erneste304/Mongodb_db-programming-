"""
Shift Management Models
For end-of-shift cash counting and reporting
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class ShiftStatus(str, Enum):
    OPEN = "open"
    CLOSED = "closed"
    PENDING_RECONCILIATION = "pending_reconciliation"


class Shift(Document):
    """Work shift management"""
    shift_id: str = Field(..., unique=True)
    staff_id: str = Field(...)
    staff_name: str = Field(...)
    shift_date: datetime = Field(default_factory=datetime.utcnow)
    start_time: datetime = Field(default_factory=datetime.utcnow)
    end_time: Optional[datetime] = Field(None)
    status: ShiftStatus = Field(default=ShiftStatus.OPEN)
    
    # Cash counts
    opening_cash: float = Field(default=0)
    closing_cash: float = Field(default=0)
    expected_cash: float = Field(default=0)
    cash_variance: float = Field(default=0)
    
    # Sales summary
    total_sales: float = Field(default=0)
    fuel_sales: float = Field(default=0)
    shop_sales: float = Field(default=0)
    cash_sales: float = Field(default=0)
    mobile_money_sales: float = Field(default=0)
    card_sales: float = Field(default=0)
    credit_sales: float = Field(default=0)
    
    # Sales by fuel type
    petrol_sales: float = Field(default=0)
    diesel_sales: float = Field(default=0)
    kerosene_sales: float = Field(default=0)
    
    # Transaction counts
    total_transactions: int = Field(default=0)
    fuel_transactions: int = Field(default=0)
    shop_transactions: int = Field(default=0)
    
    notes: Optional[str] = Field(None)
    reconciled_by: Optional[str] = Field(None)
    reconciled_at: Optional[datetime] = Field(None)
    
    class Settings:
        collection_name = "shifts"


class CashCount(Document):
    """Individual cash counting records"""
    count_id: str = Field(..., unique=True)
    shift_id: str = Field(...)
    staff_id: str = Field(...)
    counted_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Denomination breakdown
    notes_5000: int = Field(default=0)
    notes_2000: int = Field(default=0)
    notes_1000: int = Field(default=0)
    notes_500: int = Field(default=0)
    notes_200: int = Field(default=0)
    notes_100: int = Field(default=0)
    notes_50: int = Field(default=0)
    coins: float = Field(default=0)
    
    total_counted: float = Field(default=0)
    expected_amount: float = Field(default=0)
    variance: float = Field(default=0)
    
    verified_by: Optional[str] = Field(None)
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "cash_counts"
