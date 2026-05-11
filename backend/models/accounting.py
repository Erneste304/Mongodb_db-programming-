"""
Accounting Models
For accountant financial management, reconciliation, and reporting
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BankAccountType(str, Enum):
    CHECKING = "checking"
    SAVINGS = "savings"
    MOBILE_MONEY = "mobile_money"


class BankReconciliationStatus(str, Enum):
    PENDING = "pending"
    RECONCILED = "reconciled"
    DISCREPANCY = "discrepancy"


class TaxType(str, Enum):
    VAT = "vat"
    INCOME_TAX = "income_tax"
    EXCISE_TAX = "excise_tax"
    WITHHOLDING_TAX = "withholding_tax"


class CreditStatus(str, Enum):
    ACTIVE = "active"
    OVERDUE = "overdue"
    PAID = "paid"
    SUSPENDED = "suspended"


class BankReconciliation(Document):
    """Bank deposits and reconciliation tracking"""
    reconciliation_id: str = Field(..., unique=True)
    bank_account_id: str = Field(...)
    bank_name: str = Field(...)
    account_number: str = Field(...)
    account_type: BankAccountType
    
    # Statement details
    statement_date: datetime
    statement_balance: float
    system_balance: float
    difference: float
    
    # Transactions summary
    deposits_total: float = Field(default=0)
    withdrawals_total: float = Field(default=0)
    fees_total: float = Field(default=0)
    
    # Mobile money specific
    mobile_money_provider: Optional[str] = Field(None)  # MTN, Airtel
    mobile_money_number: Optional[str] = Field(None)
    
    status: BankReconciliationStatus = Field(default=BankReconciliationStatus.PENDING)
    
    # Reconciliation details
    reconciled_by: Optional[str] = Field(None)
    reconciled_at: Optional[datetime] = Field(None)
    discrepancy_notes: Optional[str] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "bank_reconciliations"


class AccountsReceivable(Document):
    """Credit sales to corporate customers - money owed to station"""
    ar_id: str = Field(..., unique=True)
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    customer_tin: Optional[str] = Field(None)
    
    # Invoice details
    invoice_number: str = Field(..., unique=True)
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime
    
    # Transaction details
    transaction_ids: List[str] = Field(default_factory=list)
    fuel_type: Optional[str] = Field(None)
    total_quantity_liters: float = Field(default=0)
    
    # Financial details
    subtotal: float
    vat_amount: float = Field(default=0)
    total_amount: float
    
    # Payment tracking
    amount_paid: float = Field(default=0)
    balance_due: float
    
    status: CreditStatus = Field(default=CreditStatus.ACTIVE)
    
    # Payment terms
    credit_terms_days: int = Field(default=30)
    
    # Tracking
    last_payment_date: Optional[datetime] = Field(None)
    last_payment_amount: Optional[float] = Field(None)
    
    created_by: str = Field(...)
    notes: Optional[str] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "accounts_receivable"


class AccountsPayable(Document):
    """Money owed to suppliers"""
    ap_id: str = Field(..., unique=True)
    supplier_id: str = Field(...)
    supplier_name: str = Field(...)
    supplier_tin: Optional[str] = Field(None)
    
    # Invoice details
    invoice_number: str = Field(...)
    supplier_invoice_date: datetime
    due_date: datetime
    
    # Order reference
    delivery_id: Optional[str] = Field(None)
    fuel_type: str = Field(...)
    quantity_liters: float
    
    # Financial details
    unit_price: float
    subtotal: float
    vat_amount: float = Field(default=0)
    total_amount: float
    
    # Payment tracking
    amount_paid: float = Field(default=0)
    balance_due: float
    
    status: CreditStatus = Field(default=CreditStatus.ACTIVE)
    
    # Payment terms
    credit_terms_days: int = Field(default=30)
    
    # Tracking
    last_payment_date: Optional[datetime] = Field(None)
    last_payment_amount: Optional[float] = Field(None)
    
    created_by: str = Field(...)
    notes: Optional[str] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "accounts_payable"


class TaxRecord(Document):
    """Tax documents and records (VAT, Income Tax)"""
    tax_id: str = Field(..., unique=True)
    tax_type: TaxType
    period_start: datetime
    period_end: datetime
    
    # Tax calculation
    taxable_amount: float
    tax_rate: float
    tax_amount: float
    
    # Reference numbers
    declaration_number: Optional[str] = Field(None)
    rra_reference: Optional[str] = Field(None)
    
    # Filing status
    filed_date: Optional[datetime] = Field(None)
    filed_by: Optional[str] = Field(None)
    payment_date: Optional[datetime] = Field(None)
    payment_reference: Optional[str] = Field(None)
    
    status: str = Field(default="draft", description="draft, filed, paid, overdue")
    
    # Supporting documents
    document_urls: List[str] = Field(default_factory=list)
    
    # Breakdown by category
    vat_breakdown: Optional[dict] = Field(None)  # input_vat, output_vat, net_vat
    
    notes: Optional[str] = Field(None)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "tax_records"


class FuelCostTracking(Document):
    """Track fuel purchase costs vs selling prices for profit margin analysis"""
    tracking_id: str = Field(..., unique=True)
    fuel_type: str = Field(...)
    
    # Purchase details
    purchase_date: datetime
    supplier_id: str = Field(...)
    supplier_name: str = Field(...)
    delivery_id: str = Field(...)
    
    quantity_liters: float
    purchase_price_per_liter: float
    total_purchase_cost: float
    
    # Additional costs
    transport_cost: float = Field(default=0)
    storage_cost: float = Field(default=0)
    other_costs: float = Field(default=0)
    total_cost_per_liter: float
    
    # Selling details
    selling_price_per_liter: float
    
    # Profit calculation
    profit_per_liter: float
    profit_margin_percentage: float
    
    # Period tracking
    period_start: datetime
    period_end: datetime
    
    # Sales summary for period
    total_sold_liters: float = Field(default=0)
    total_revenue: float = Field(default=0)
    total_profit: float = Field(default=0)

    created_by: str = Field(...)
    notes: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "fuel_cost_tracking"


class CommissionCalculation(Document):
    """Staff commission calculations"""
    commission_id: str = Field(..., unique=True)
    user_id: str = Field(...)
    user_name: str = Field(...)

    # Period
    period_start: datetime
    period_end: datetime

    # Sales performance
    total_sales_amount: float = Field(default=0)
    total_transactions: int = Field(default=0)

    # Commission structure
    commission_rate: float = Field(default=0)  # Percentage
    commission_amount: float = Field(default=0)

    # Bonus calculations
    bonus_amount: float = Field(default=0)
    bonus_reason: Optional[str] = Field(None)

    # Deductions
    deductions: float = Field(default=0)
    deduction_reason: Optional[str] = Field(None)

    # Total
    total_commission: float

    # Approval
    calculated_by: str = Field(...)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = Field(None)
    approved_at: Optional[datetime] = Field(None)

    status: str = Field(default="calculated", description="calculated, approved, paid")

    # Payment
    paid_at: Optional[datetime] = Field(None)
    payment_reference: Optional[str] = Field(None)

    notes: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "commission_calculations"


class CorporateInvoice(Document):
    """Invoices for corporate clients with credit accounts"""
    invoice_id: str = Field(..., unique=True)
    invoice_number: str = Field(..., unique=True)

    # Customer details
    customer_id: str = Field(...)
    customer_name: str = Field(...)
    customer_tin: Optional[str] = Field(None)
    customer_address: Optional[str] = Field(None)

    # Invoice period
    period_start: datetime
    period_end: datetime
    invoice_date: datetime = Field(default_factory=datetime.utcnow)
    due_date: datetime

    # Line items (fuel purchases)
    line_items: List[dict] = Field(default_factory=list)
    # Each item: {date, fuel_type, quantity, unit_price, amount}

    # Totals
    subtotal: float
    vat_rate: float = Field(default=18)  # Rwanda VAT
    vat_amount: float
    total_amount: float

    # Credit terms
    credit_terms_days: int = Field(default=30)

    # Status
    status: str = Field(default="draft", description="draft, sent, paid, overdue, cancelled")

    # Payment tracking
    amount_paid: float = Field(default=0)
    balance_due: float
    paid_date: Optional[datetime] = Field(None)
    payment_reference: Optional[str] = Field(None)

    # Approval
    prepared_by: str = Field(...)
    approved_by: Optional[str] = Field(None)
    approved_at: Optional[datetime] = Field(None)

    # Delivery
    sent_date: Optional[datetime] = Field(None)
    sent_method: Optional[str] = Field(None, description="email, print, courier")

    notes: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "corporate_invoices"


class DailyClosing(Document):
    """Daily closing procedures with all payment methods"""
    closing_id: str = Field(..., unique=True)
    station_id: str = Field(...)
    closing_date: datetime

    # Cash details
    opening_cash_balance: float
    cash_sales: float
    cash_refunds: float = Field(default=0)
    cash_paid_out: float = Field(default=0)
    expected_cash_balance: float
    actual_cash_balance: float
    cash_variance: float

    # Credit card details
    card_sales: float = Field(default=0)
    card_refunds: float = Field(default=0)
    card_count: int = Field(default=0)

    # Mobile money details
    mobile_money_sales: float = Field(default=0)
    mobile_money_refunds: float = Field(default=0)
    mobile_money_count: int = Field(default=0)
    mobile_money_provider_breakdown: dict = Field(default_factory=dict)
    # {mtn_momo: {sales, count}, airtel_money: {sales, count}}

    # Credit sales
    credit_sales: float = Field(default=0)
    credit_collections: float = Field(default=0)

    # Bank deposit
    bank_deposit_amount: float = Field(default=0)
    deposit_reference: Optional[str] = Field(None)
    deposited_by: Optional[str] = Field(None)
    deposited_at: Optional[datetime] = Field(None)

    # Summary
    total_sales: float
    total_transactions: int
    total_refunds: float = Field(default=0)

    # Staff
    shift_manager_id: str = Field(...)
    accountant_id: str = Field(...)

    # Verification
    verified_by_accountant: bool = Field(default=False)
    verified_at: Optional[datetime] = Field(None)

    notes: Optional[str] = Field(None)
    discrepancies: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "daily_closings"


class RURAComplianceReport(Document):
    """Monthly reports for RURA compliance"""
    report_id: str = Field(..., unique=True)
    report_period: str  # YYYY-MM format

    # Fuel sales summary
    petrol_sales_liters: float = Field(default=0)
    petrol_sales_amount: float = Field(default=0)
    diesel_sales_liters: float = Field(default=0)
    diesel_sales_amount: float = Field(default=0)
    kerosene_sales_liters: float = Field(default=0)
    kerosene_sales_amount: float = Field(default=0)

    # Prices
    petrol_avg_price: float = Field(default=0)
    diesel_avg_price: float = Field(default=0)
    kerosene_avg_price: float = Field(default=0)

    # Inventory
    opening_stock_liters: dict = Field(default_factory=dict)
    closing_stock_liters: dict = Field(default_factory=dict)
    purchases_liters: dict = Field(default_factory=dict)

    # Tax summary
    total_vat_collected: float = Field(default=0)
    total_excise_tax: float = Field(default=0)

    # Compliance
    rura_reference: Optional[str] = Field(None)
    submitted_date: Optional[datetime] = Field(None)
    submitted_by: Optional[str] = Field(None)

    status: str = Field(default="draft", description="draft, submitted, approved")

    notes: Optional[str] = Field(None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Settings:
        collection_name = "rura_compliance_reports"
