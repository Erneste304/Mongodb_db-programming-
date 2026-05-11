"""
Accounting API Routes
For accountant financial management, reconciliation, and reporting
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.accounting import (
    BankReconciliation, BankReconciliationStatus, BankAccountType,
    AccountsReceivable, AccountsPayable, CreditStatus,
    TaxRecord, TaxType,
    FuelCostTracking,
    CommissionCalculation,
    CorporateInvoice,
    DailyClosing,
    RURAComplianceReport
)
from backend.models.finance import Payment, PaymentStatus, PaymentMethod
from backend.models.sales import Transaction
from backend.core.security import get_current_user, require_role_level
from backend.models.user import User
from backend.services.audit_service import AuditLogService

router = APIRouter(prefix="/accounting", tags=["accounting"])


# ==================== BANK RECONCILIATION ====================

class CreateBankReconciliationRequest(BaseModel):
    bank_account_id: str
    bank_name: str
    account_number: str
    account_type: BankAccountType
    statement_date: datetime
    statement_balance: float
    system_balance: float
    deposits_total: float = 0
    withdrawals_total: float = 0
    fees_total: float = 0
    mobile_money_provider: Optional[str] = None
    mobile_money_number: Optional[str] = None
    discrepancy_notes: Optional[str] = None


@router.post("/bank-reconciliation")
async def create_bank_reconciliation(
    request: CreateBankReconciliationRequest,
    current_user: User = Depends(require_role_level(3))  # Accountant+
):
    """Create bank reconciliation record - Accountant only"""
    
    difference = request.statement_balance - request.system_balance
    
    status = BankReconciliationStatus.RECONCILED
    if abs(difference) > 0.01:
        status = BankReconciliationStatus.DISCREPANCY
    
    reconciliation = BankReconciliation(
        reconciliation_id=f"BR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        bank_account_id=request.bank_account_id,
        bank_name=request.bank_name,
        account_number=request.account_number,
        account_type=request.account_type,
        statement_date=request.statement_date,
        statement_balance=request.statement_balance,
        system_balance=request.system_balance,
        difference=difference,
        deposits_total=request.deposits_total,
        withdrawals_total=request.withdrawals_total,
        fees_total=request.fees_total,
        mobile_money_provider=request.mobile_money_provider,
        mobile_money_number=request.mobile_money_number,
        status=status,
        discrepancy_notes=request.discrepancy_notes,
        reconciled_by=str(current_user.id) if status == BankReconciliationStatus.RECONCILED else None,
        reconciled_at=datetime.utcnow() if status == BankReconciliationStatus.RECONCILED else None
    )
    
    await reconciliation.insert()
    
    await AuditLogService.log_action(
        user=current_user,
        action="created_bank_reconciliation",
        resource_type="bank_reconciliation",
        resource_id=str(reconciliation.id),
        old_value={},
        new_value={
            "bank": request.bank_name,
            "difference": difference,
            "status": status.value
        }
    )
    
    return {
        "message": "Bank reconciliation created",
        "reconciliation_id": reconciliation.reconciliation_id,
        "status": status.value,
        "difference": difference
    }


@router.get("/bank-reconciliation")
async def get_bank_reconciliations(
    account_id: Optional[str] = None,
    status: Optional[BankReconciliationStatus] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get bank reconciliations - Accountant view"""
    
    query = {}
    if account_id:
        query["bank_account_id"] = account_id
    if status:
        query["status"] = status.value
    
    reconciliations = await BankReconciliation.find(query).to_list()
    
    return [
        {
            "reconciliation_id": r.reconciliation_id,
            "bank_name": r.bank_name,
            "account_number": r.account_number[-4:],  # Mask for security
            "statement_date": r.statement_date,
            "statement_balance": r.statement_balance,
            "system_balance": r.system_balance,
            "difference": r.difference,
            "status": r.status.value
        }
        for r in reconciliations
    ]


# ==================== ACCOUNTS RECEIVABLE (Credit Sales) ====================

class CreateInvoiceRequest(BaseModel):
    customer_id: str
    customer_name: str
    customer_tin: Optional[str] = None
    due_date: datetime
    transaction_ids: List[str]
    fuel_type: Optional[str] = None
    total_quantity_liters: float
    subtotal: float
    vat_amount: float = 0
    credit_terms_days: int = 30
    notes: Optional[str] = None


@router.post("/accounts-receivable/invoice")
async def create_corporate_invoice(
    request: CreateInvoiceRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Create invoice for corporate customer - Accountant only"""
    
    total_amount = request.subtotal + request.vat_amount
    
    # Create AR record
    ar = AccountsReceivable(
        ar_id=f"AR-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        customer_id=request.customer_id,
        customer_name=request.customer_name,
        customer_tin=request.customer_tin,
        invoice_number=f"INV-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        due_date=request.due_date,
        transaction_ids=request.transaction_ids,
        fuel_type=request.fuel_type,
        total_quantity_liters=request.total_quantity_liters,
        subtotal=request.subtotal,
        vat_amount=request.vat_amount,
        total_amount=total_amount,
        balance_due=total_amount,
        credit_terms_days=request.credit_terms_days,
        created_by=str(current_user.id),
        notes=request.notes
    )
    
    await ar.insert()
    
    # Also create CorporateInvoice for detailed billing
    invoice = CorporateInvoice(
        invoice_id=ar.ar_id,
        invoice_number=ar.invoice_number,
        customer_id=request.customer_id,
        customer_name=request.customer_name,
        customer_tin=request.customer_tin,
        period_start=datetime.utcnow() - timedelta(days=30),
        period_end=datetime.utcnow(),
        due_date=request.due_date,
        line_items=[],  # Would be populated with actual transactions
        subtotal=request.subtotal,
        vat_amount=request.vat_amount,
        total_amount=total_amount,
        balance_due=total_amount,
        credit_terms_days=request.credit_terms_days,
        prepared_by=str(current_user.id),
        notes=request.notes
    )
    
    await invoice.insert()
    
    await AuditLogService.log_action(
        user=current_user,
        action="created_corporate_invoice",
        resource_type="accounts_receivable",
        resource_id=str(ar.id),
        old_value={},
        new_value={
            "customer": request.customer_name,
            "invoice_number": ar.invoice_number,
            "amount": total_amount
        }
    )
    
    return {
        "message": "Corporate invoice created",
        "ar_id": ar.ar_id,
        "invoice_number": ar.invoice_number,
        "total_amount": total_amount,
        "balance_due": ar.balance_due
    }


@router.get("/accounts-receivable")
async def get_accounts_receivable(
    status: Optional[CreditStatus] = None,
    customer_id: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get accounts receivable - Accountant view"""
    
    query = {}
    if status:
        query["status"] = status.value
    if customer_id:
        query["customer_id"] = customer_id
    
    ar_records = await AccountsReceivable.find(query).to_list()
    
    return [
        {
            "ar_id": ar.ar_id,
            "customer_name": ar.customer_name,
            "invoice_number": ar.invoice_number,
            "invoice_date": ar.invoice_date,
            "due_date": ar.due_date,
            "total_amount": ar.total_amount,
            "balance_due": ar.balance_due,
            "status": ar.status.value,
            "days_overdue": (datetime.utcnow() - ar.due_date).days if ar.status == CreditStatus.OVERDUE else 0
        }
        for ar in ar_records
    ]


@router.post("/accounts-receivable/{ar_id}/payment")
async def record_ar_payment(
    ar_id: str,
    amount: float,
    payment_method: str,
    payment_reference: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Record payment against accounts receivable - Accountant only"""
    
    ar = await AccountsReceivable.find_one({"ar_id": ar_id})
    if not ar:
        raise HTTPException(status_code=404, detail="AR record not found")
    
    ar.amount_paid += amount
    ar.balance_due = ar.total_amount - ar.amount_paid
    ar.last_payment_date = datetime.utcnow()
    ar.last_payment_amount = amount
    
    if ar.balance_due <= 0:
        ar.status = CreditStatus.PAID
    elif datetime.utcnow() > ar.due_date:
        ar.status = CreditStatus.OVERDUE
    
    await ar.save()
    
    await AuditLogService.log_action(
        user=current_user,
        action="recorded_ar_payment",
        resource_type="accounts_receivable",
        resource_id=str(ar.id),
        old_value={"balance_due": ar.balance_due + amount},
        new_value={"balance_due": ar.balance_due, "amount_paid": ar.amount_paid}
    )
    
    return {
        "message": "Payment recorded",
        "ar_id": ar_id,
        "amount_paid": amount,
        "balance_due": ar.balance_due,
        "status": ar.status.value
    }


# ==================== ACCOUNTS PAYABLE (Supplier Payments) ====================

@router.get("/accounts-payable")
async def get_accounts_payable(
    status: Optional[CreditStatus] = None,
    supplier_id: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get accounts payable - Accountant view"""
    
    query = {}
    if status:
        query["status"] = status.value
    if supplier_id:
        query["supplier_id"] = supplier_id
    
    ap_records = await AccountsPayable.find(query).to_list()
    
    return [
        {
            "ap_id": ap.ap_id,
            "supplier_name": ap.supplier_name,
            "invoice_number": ap.invoice_number,
            "fuel_type": ap.fuel_type,
            "quantity_liters": ap.quantity_liters,
            "total_amount": ap.total_amount,
            "balance_due": ap.balance_due,
            "due_date": ap.due_date,
            "status": ap.status.value,
            "days_overdue": (datetime.utcnow() - ap.due_date).days if ap.status == CreditStatus.OVERDUE else 0
        }
        for ap in ap_records
    ]


@router.post("/accounts-payable/{ap_id}/payment")
async def record_ap_payment(
    ap_id: str,
    amount: float,
    payment_method: str,
    payment_reference: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Record payment to supplier - Accountant only"""
    
    ap = await AccountsPayable.find_one({"ap_id": ap_id})
    if not ap:
        raise HTTPException(status_code=404, detail="AP record not found")
    
    ap.amount_paid += amount
    ap.balance_due = ap.total_amount - ap.amount_paid
    ap.last_payment_date = datetime.utcnow()
    ap.last_payment_amount = amount
    
    if ap.balance_due <= 0:
        ap.status = CreditStatus.PAID
    
    await ap.save()
    
    await AuditLogService.log_action(
        user=current_user,
        action="recorded_supplier_payment",
        resource_type="accounts_payable",
        resource_id=str(ap.id),
        old_value={"balance_due": ap.balance_due + amount},
        new_value={"balance_due": ap.balance_due, "amount_paid": ap.amount_paid}
    )
    
    return {
        "message": "Supplier payment recorded",
        "ap_id": ap_id,
        "amount_paid": amount,
        "balance_due": ap.balance_due,
        "status": ap.status.value
    }


# ==================== TAX RECORDS ====================

class CreateTaxRecordRequest(BaseModel):
    tax_type: TaxType
    period_start: datetime
    period_end: datetime
    taxable_amount: float
    tax_rate: float
    declaration_number: Optional[str] = None
    notes: Optional[str] = None


@router.post("/tax-records")
async def create_tax_record(
    request: CreateTaxRecordRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Create tax record (VAT, Income Tax) - Accountant only"""
    
    tax_amount = request.taxable_amount * (request.tax_rate / 100)
    
    tax_record = TaxRecord(
        tax_id=f"TAX-{request.tax_type.value.upper()}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        tax_type=request.tax_type,
        period_start=request.period_start,
        period_end=request.period_end,
        taxable_amount=request.taxable_amount,
        tax_rate=request.tax_rate,
        tax_amount=tax_amount,
        declaration_number=request.declaration_number,
        filed_by=str(current_user.id),
        filed_date=datetime.utcnow(),
        status="filed",
        notes=request.notes
    )
    
    await tax_record.insert()
    
    await AuditLogService.log_action(
        user=current_user,
        action="filed_tax_return",
        resource_type="tax_record",
        resource_id=str(tax_record.id),
        old_value={},
        new_value={
            "tax_type": request.tax_type.value,
            "tax_amount": tax_amount,
            "period": f"{request.period_start.date()} to {request.period_end.date()}"
        }
    )
    
    return {
        "message": "Tax record created",
        "tax_id": tax_record.tax_id,
        "tax_type": tax_record.tax_type.value,
        "tax_amount": tax_amount
    }


@router.get("/tax-records")
async def get_tax_records(
    tax_type: Optional[TaxType] = None,
    status: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get tax records - Accountant view"""
    
    query = {}
    if tax_type:
        query["tax_type"] = tax_type.value
    if status:
        query["status"] = status
    
    tax_records = await TaxRecord.find(query).to_list()
    
    return [
        {
            "tax_id": t.tax_id,
            "tax_type": t.tax_type.value,
            "period": f"{t.period_start.date()} to {t.period_end.date()}",
            "taxable_amount": t.taxable_amount,
            "tax_rate": t.tax_rate,
            "tax_amount": t.tax_amount,
            "status": t.status,
            "filed_date": t.filed_date
        }
        for t in tax_records
    ]


# ==================== FUEL COST TRACKING & PROFIT MARGINS ====================

class CreateFuelCostTrackingRequest(BaseModel):
    fuel_type: str
    supplier_id: str
    supplier_name: str
    delivery_id: str
    quantity_liters: float
    purchase_price_per_liter: float
    transport_cost: float = 0
    storage_cost: float = 0
    other_costs: float = 0
    selling_price_per_liter: float
    period_start: datetime
    period_end: datetime


@router.post("/fuel-cost-tracking")
async def create_fuel_cost_tracking(
    request: CreateFuelCostTrackingRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Track fuel costs and calculate profit margins - Accountant only"""
    
    total_purchase_cost = request.quantity_liters * request.purchase_price_per_liter
    total_additional_costs = request.transport_cost + request.storage_cost + request.other_costs
    total_cost_per_liter = (total_purchase_cost + total_additional_costs) / request.quantity_liters
    
    profit_per_liter = request.selling_price_per_liter - total_cost_per_liter
    profit_margin_percentage = (profit_per_liter / total_cost_per_liter) * 100
    
    tracking = FuelCostTracking(
        tracking_id=f"FCT-{request.fuel_type}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        fuel_type=request.fuel_type,
        purchase_date=datetime.utcnow(),
        supplier_id=request.supplier_id,
        supplier_name=request.supplier_name,
        delivery_id=request.delivery_id,
        quantity_liters=request.quantity_liters,
        purchase_price_per_liter=request.purchase_price_per_liter,
        total_purchase_cost=total_purchase_cost,
        transport_cost=request.transport_cost,
        storage_cost=request.storage_cost,
        other_costs=request.other_costs,
        total_cost_per_liter=total_cost_per_liter,
        selling_price_per_liter=request.selling_price_per_liter,
        profit_per_liter=profit_per_liter,
        profit_margin_percentage=profit_margin_percentage,
        period_start=request.period_start,
        period_end=request.period_end,
        created_by=str(current_user.id)
    )
    
    await tracking.insert()
    
    return {
        "message": "Fuel cost tracking created",
        "tracking_id": tracking.tracking_id,
        "fuel_type": request.fuel_type,
        "total_cost_per_liter": total_cost_per_liter,
        "profit_per_liter": profit_per_liter,
        "profit_margin_percentage": profit_margin_percentage
    }


@router.get("/fuel-cost-tracking")
async def get_fuel_cost_tracking(
    fuel_type: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get fuel cost tracking with profit margins - Accountant view"""
    
    query = {}
    if fuel_type:
        query["fuel_type"] = fuel_type
    
    tracking_records = await FuelCostTracking.find(query).to_list()
    
    return [
        {
            "tracking_id": t.tracking_id,
            "fuel_type": t.fuel_type,
            "supplier_name": t.supplier_name,
            "quantity_liters": t.quantity_liters,
            "purchase_price": t.purchase_price_per_liter,
            "total_cost_per_liter": t.total_cost_per_liter,
            "selling_price": t.selling_price_per_liter,
            "profit_per_liter": t.profit_per_liter,
            "profit_margin_percentage": t.profit_margin_percentage,
            "period": f"{t.period_start.date()} to {t.period_end.date()}"
        }
        for t in tracking_records
    ]


# ==================== COMMISSION CALCULATIONS ====================

class CalculateCommissionRequest(BaseModel):
    user_id: str
    user_name: str
    period_start: datetime
    period_end: datetime
    total_sales_amount: float
    total_transactions: int
    commission_rate: float
    bonus_amount: float = 0
    bonus_reason: Optional[str] = None
    deductions: float = 0
    deduction_reason: Optional[str] = None


@router.post("/commissions/calculate")
async def calculate_commission(
    request: CalculateCommissionRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Calculate staff commission - Accountant only"""
    
    commission_amount = request.total_sales_amount * (request.commission_rate / 100)
    total_commission = commission_amount + request.bonus_amount - request.deductions
    
    commission = CommissionCalculation(
        commission_id=f"COMM-{request.user_id}-{datetime.utcnow().strftime('%Y%m%d')}",
        user_id=request.user_id,
        user_name=request.user_name,
        period_start=request.period_start,
        period_end=request.period_end,
        total_sales_amount=request.total_sales_amount,
        total_transactions=request.total_transactions,
        commission_rate=request.commission_rate,
        commission_amount=commission_amount,
        bonus_amount=request.bonus_amount,
        bonus_reason=request.bonus_reason,
        deductions=request.deductions,
        deduction_reason=request.deduction_reason,
        total_commission=total_commission,
        calculated_by=str(current_user.id)
    )
    
    await commission.insert()
    
    return {
        "message": "Commission calculated",
        "commission_id": commission.commission_id,
        "user_name": request.user_name,
        "commission_amount": commission_amount,
        "total_commission": total_commission
    }


@router.get("/commissions/pending")
async def get_pending_commissions(
    current_user: User = Depends(require_role_level(3))
):
    """Get pending commission approvals - Accountant view"""
    
    commissions = await CommissionCalculation.find({"status": "calculated"}).to_list()
    
    return [
        {
            "commission_id": c.commission_id,
            "user_name": c.user_name,
            "period": f"{c.period_start.date()} to {c.period_end.date()}",
            "total_sales": c.total_sales_amount,
            "commission_amount": c.commission_amount,
            "total_commission": c.total_commission,
            "status": c.status
        }
        for c in commissions
    ]


@router.post("/commissions/{commission_id}/approve")
async def approve_commission(
    commission_id: str,
    current_user: User = Depends(require_role_level(3))
):
    """Approve commission calculation - Accountant only"""
    
    commission = await CommissionCalculation.find_one({"commission_id": commission_id})
    if not commission:
        raise HTTPException(status_code=404, detail="Commission record not found")
    
    commission.status = "approved"
    commission.approved_by = str(current_user.id)
    commission.approved_at = datetime.utcnow()
    
    await commission.save()
    
    return {"message": "Commission approved", "commission_id": commission_id}


# ==================== DAILY CLOSING ====================

class CreateDailyClosingRequest(BaseModel):
    station_id: str
    closing_date: datetime
    opening_cash_balance: float
    cash_sales: float
    cash_refunds: float = 0
    cash_paid_out: float = 0
    actual_cash_balance: float
    card_sales: float = 0
    card_count: int = 0
    mobile_money_sales: float = 0
    mobile_money_count: int = 0
    mobile_money_breakdown: dict = {}
    credit_sales: float = 0
    credit_collections: float = 0
    bank_deposit_amount: float = 0
    deposit_reference: Optional[str] = None
    total_transactions: int
    shift_manager_id: str
    notes: Optional[str] = None
    discrepancies: Optional[str] = None


@router.post("/daily-closing")
async def create_daily_closing(
    request: CreateDailyClosingRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Record daily closing with all payment methods - Accountant only"""
    
    expected_cash = (request.opening_cash_balance + request.cash_sales - 
                    request.cash_refunds - request.cash_paid_out)
    cash_variance = request.actual_cash_balance - expected_cash
    
    total_sales = (request.cash_sales + request.card_sales + 
                   request.mobile_money_sales + request.credit_sales)
    
    closing = DailyClosing(
        closing_id=f"DC-{request.station_id}-{datetime.utcnow().strftime('%Y%m%d')}",
        station_id=request.station_id,
        closing_date=request.closing_date,
        opening_cash_balance=request.opening_cash_balance,
        cash_sales=request.cash_sales,
        cash_refunds=request.cash_refunds,
        cash_paid_out=request.cash_paid_out,
        expected_cash_balance=expected_cash,
        actual_cash_balance=request.actual_cash_balance,
        cash_variance=cash_variance,
        card_sales=request.card_sales,
        card_count=request.card_count,
        mobile_money_sales=request.mobile_money_sales,
        mobile_money_count=request.mobile_money_count,
        mobile_money_provider_breakdown=request.mobile_money_breakdown,
        credit_sales=request.credit_sales,
        credit_collections=request.credit_collections,
        bank_deposit_amount=request.bank_deposit_amount,
        deposit_reference=request.deposit_reference,
        deposited_by=str(current_user.id),
        deposited_at=datetime.utcnow(),
        total_sales=total_sales,
        total_transactions=request.total_transactions,
        shift_manager_id=request.shift_manager_id,
        accountant_id=str(current_user.id),
        verified_by_accountant=True,
        verified_at=datetime.utcnow(),
        notes=request.notes,
        discrepancies=request.discrepancies
    )
    
    await closing.insert()
    
    await AuditLogService.log_action(
        user=current_user,
        action="recorded_daily_closing",
        resource_type="daily_closing",
        resource_id=str(closing.id),
        old_value={},
        new_value={
            "station_id": request.station_id,
            "total_sales": total_sales,
            "cash_variance": cash_variance
        }
    )
    
    return {
        "message": "Daily closing recorded",
        "closing_id": closing.closing_id,
        "total_sales": total_sales,
        "cash_variance": cash_variance
    }


@router.get("/daily-closing")
async def get_daily_closings(
    station_id: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get daily closing records - Accountant view"""
    
    query = {}
    if station_id:
        query["station_id"] = station_id
    if start_date and end_date:
        query["closing_date"] = {"$gte": start_date, "$lte": end_date}
    
    closings = await DailyClosing.find(query).to_list()
    
    return [
        {
            "closing_id": c.closing_id,
            "station_id": c.station_id,
            "closing_date": c.closing_date,
            "total_sales": c.total_sales,
            "cash_sales": c.cash_sales,
            "card_sales": c.card_sales,
            "mobile_money_sales": c.mobile_money_sales,
            "credit_sales": c.credit_sales,
            "cash_variance": c.cash_variance,
            "verified": c.verified_by_accountant
        }
        for c in closings
    ]


# ==================== RURA COMPLIANCE REPORTS ====================

class CreateRURAReportRequest(BaseModel):
    report_period: str  # YYYY-MM format
    petrol_sales_liters: float
    petrol_sales_amount: float
    diesel_sales_liters: float
    diesel_sales_amount: float
    kerosene_sales_liters: float = 0
    kerosene_sales_amount: float = 0
    petrol_avg_price: float
    diesel_avg_price: float
    kerosene_avg_price: float = 0
    opening_stock: dict
    closing_stock: dict
    purchases: dict
    total_vat_collected: float
    total_excise_tax: float
    rura_reference: Optional[str] = None


@router.post("/rura-reports")
async def create_rura_report(
    request: CreateRURAReportRequest,
    current_user: User = Depends(require_role_level(3))
):
    """Create RURA compliance report - Accountant only"""
    
    report = RURAComplianceReport(
        report_id=f"RURA-{request.report_period}-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        report_period=request.report_period,
        petrol_sales_liters=request.petrol_sales_liters,
        petrol_sales_amount=request.petrol_sales_amount,
        diesel_sales_liters=request.diesel_sales_liters,
        diesel_sales_amount=request.diesel_sales_amount,
        kerosene_sales_liters=request.kerosene_sales_liters,
        kerosene_sales_amount=request.kerosene_sales_amount,
        petrol_avg_price=request.petrol_avg_price,
        diesel_avg_price=request.diesel_avg_price,
        kerosene_avg_price=request.kerosene_avg_price,
        opening_stock_liters=request.opening_stock,
        closing_stock_liters=request.closing_stock,
        purchases_liters=request.purchases,
        total_vat_collected=request.total_vat_collected,
        total_excise_tax=request.total_excise_tax,
        rura_reference=request.rura_reference,
        submitted_date=datetime.utcnow(),
        submitted_by=str(current_user.id),
        status="submitted"
    )
    
    await report.insert()
    
    await AuditLogService.log_action(
        user=current_user,
        action="submitted_rura_report",
        resource_type="rura_compliance_report",
        resource_id=str(report.id),
        old_value={},
        new_value={
            "report_period": request.report_period,
            "rura_reference": request.rura_reference
        }
    )
    
    return {
        "message": "RURA compliance report submitted",
        "report_id": report.report_id,
        "report_period": request.report_period,
        "status": "submitted"
    }


@router.get("/rura-reports")
async def get_rura_reports(
    status: Optional[str] = None,
    current_user: User = Depends(require_role_level(3))
):
    """Get RURA compliance reports - Accountant view"""
    
    query = {}
    if status:
        query["status"] = status
    
    reports = await RURAComplianceReport.find(query).to_list()
    
    return [
        {
            "report_id": r.report_id,
            "report_period": r.report_period,
            "total_sales_liters": (r.petrol_sales_liters + r.diesel_sales_liters + 
                                   r.kerosene_sales_liters),
            "total_sales_amount": (r.petrol_sales_amount + r.diesel_sales_amount + 
                                 r.kerosene_sales_amount),
            "total_vat_collected": r.total_vat_collected,
            "status": r.status,
            "submitted_date": r.submitted_date
        }
        for r in reports
    ]
