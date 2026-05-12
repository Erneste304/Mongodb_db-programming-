from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
from backend.models.billing import Invoice, InvoiceItem, MonthlyStatement, Payment as CustomerPayment, InvoiceStatus
from backend.models.sales import Transaction, Customer

router = APIRouter(prefix="/billing", tags=["billing"])


class CreateInvoiceRequest(BaseModel):
    invoice_id: str
    customer_id: str
    invoice_number: str
    billing_period_start: datetime
    billing_period_end: datetime
    due_date: datetime
    notes: Optional[str] = None


class InvoiceResponse(BaseModel):
    id: str
    invoice_id: str
    customer_id: str
    customer_name: str
    customer_tin: Optional[str]
    invoice_number: str
    invoice_date: datetime
    due_date: datetime
    billing_period_start: datetime
    billing_period_end: datetime
    subtotal: float
    vat_amount: float
    total_amount: float
    amount_paid: float
    balance_due: float
    transaction_ids: List[str]
    status: str
    payment_reference: Optional[str]
    paid_at: Optional[datetime]
    company_name: Optional[str]
    company_address: Optional[str]
    receipt_number: Optional[str]
    notes: Optional[str]


class CreateMonthlyStatementRequest(BaseModel):
    statement_id: str
    customer_id: str
    statement_month: int
    statement_year: int
    period_start: datetime
    period_end: datetime
    delivery_method: str = "email"
    delivery_address: Optional[str] = None


class MonthlyStatementResponse(BaseModel):
    id: str
    statement_id: str
    customer_id: str
    customer_name: str
    statement_month: int
    statement_year: int
    period_start: datetime
    period_end: datetime
    opening_balance: float
    purchases: float
    payments: float
    adjustments: float
    closing_balance: float
    fuel_transactions: int
    lubricant_transactions: int
    shop_transactions: int
    total_transactions: int
    invoice_id: Optional[str]
    sent: bool
    sent_at: Optional[datetime]
    viewed: bool
    viewed_at: Optional[datetime]
    delivery_method: str
    notes: Optional[str]


class RecordPaymentRequest(BaseModel):
    payment_id: str
    customer_id: str
    amount: float
    payment_method: str
    payment_reference: Optional[str] = None
    invoice_ids: List[str] = []
    recorded_by: str
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    payment_id: str
    customer_id: str
    customer_name: str
    amount: float
    payment_method: str
    payment_reference: Optional[str]
    payment_date: datetime
    invoice_ids: List[str]
    status: str
    recorded_by: str
    notes: Optional[str]


@router.post("/invoices", response_model=InvoiceResponse)
async def create_invoice(request: CreateInvoiceRequest):
    """Create a new invoice for a credit customer"""
    
    customer = await Customer.find_one(Customer.customer_id == request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    existing_invoice = await Invoice.find_one(Invoice.invoice_id == request.invoice_id)
    if existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invoice ID already exists"
        )
    
    # Get all transactions for the billing period
    transactions = await Transaction.find(
        Transaction.customer_id == request.customer_id,
        Transaction.payment_method == "credit",
        Transaction.created_at >= request.billing_period_start,
        Transaction.created_at <= request.billing_period_end,
        Transaction.status == "completed"
    ).to_list()
    
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No transactions found for the billing period"
        )
    
    # Calculate totals
    subtotal = sum(tx.net_amount for tx in transactions)
    vat_amount = sum(tx.vat_amount for tx in transactions)
    total_amount = sum(tx.total_amount for tx in transactions)
    
    invoice = Invoice(
        invoice_id=request.invoice_id,
        customer_id=request.customer_id,
        customer_name=customer.name,
        customer_tin=customer.tin_number,
        invoice_number=request.invoice_number,
        billing_period_start=request.billing_period_start,
        billing_period_end=request.billing_period_end,
        due_date=request.due_date,
        subtotal=subtotal,
        vat_amount=vat_amount,
        total_amount=total_amount,
        balance_due=total_amount,
        transaction_ids=[tx.transaction_id for tx in transactions],
        company_name=customer.company_name,
        company_address=customer.company_address,
        notes=request.notes
    )
    
    await invoice.insert()
    
    # Create invoice items
    for tx in transactions:
        item = InvoiceItem(
            item_id=f"ITEM-{invoice.invoice_id}-{tx.transaction_id}",
            invoice_id=invoice.invoice_id,
            item_type="fuel",
            description=f"{tx.fuel_type.value} - {tx.quantity_liters}L",
            quantity=tx.quantity_liters,
            unit_price=tx.price_per_liter,
            subtotal=tx.total_amount,
            transaction_id=tx.transaction_id,
            purchase_date=tx.created_at
        )
        await item.insert()
    
    return InvoiceResponse(
        id=str(invoice.id),
        invoice_id=invoice.invoice_id,
        customer_id=invoice.customer_id,
        customer_name=invoice.customer_name,
        customer_tin=invoice.customer_tin,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        billing_period_start=invoice.billing_period_start,
        billing_period_end=invoice.billing_period_end,
        subtotal=invoice.subtotal,
        vat_amount=invoice.vat_amount,
        total_amount=invoice.total_amount,
        amount_paid=invoice.amount_paid,
        balance_due=invoice.balance_due,
        transaction_ids=invoice.transaction_ids,
        status=invoice.status.value,
        payment_reference=invoice.payment_reference,
        paid_at=invoice.paid_at,
        company_name=invoice.company_name,
        company_address=invoice.company_address,
        receipt_number=invoice.receipt_number,
        notes=invoice.notes
    )


@router.get("/invoices", response_model=List[InvoiceResponse])
async def get_invoices(skip: int = 0, limit: int = 100, customer_id: Optional[str] = None, status: Optional[InvoiceStatus] = None):
    """Get all invoices with optional filtering"""
    
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    if status:
        query["status"] = status
    
    invoices = await Invoice.find(query).skip(skip).limit(limit).sort("-invoice_date").to_list()
    
    return [
        InvoiceResponse(
            id=str(inv.id),
            invoice_id=inv.invoice_id,
            customer_id=inv.customer_id,
            customer_name=inv.customer_name,
            customer_tin=inv.customer_tin,
            invoice_number=inv.invoice_number,
            invoice_date=inv.invoice_date,
            due_date=inv.due_date,
            billing_period_start=inv.billing_period_start,
            billing_period_end=inv.billing_period_end,
            subtotal=inv.subtotal,
            vat_amount=inv.vat_amount,
            total_amount=inv.total_amount,
            amount_paid=inv.amount_paid,
            balance_due=inv.balance_due,
            transaction_ids=inv.transaction_ids,
            status=inv.status.value,
            payment_reference=inv.payment_reference,
            paid_at=inv.paid_at,
            company_name=inv.company_name,
            company_address=inv.company_address,
            receipt_number=inv.receipt_number,
            notes=inv.notes
        )
        for inv in invoices
    ]


@router.get("/invoices/{invoice_id}", response_model=InvoiceResponse)
async def get_invoice(invoice_id: str):
    """Get a specific invoice"""
    
    invoice = await Invoice.find_one(Invoice.invoice_id == invoice_id)
    
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    
    return InvoiceResponse(
        id=str(invoice.id),
        invoice_id=invoice.invoice_id,
        customer_id=invoice.customer_id,
        customer_name=invoice.customer_name,
        customer_tin=invoice.customer_tin,
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date,
        due_date=invoice.due_date,
        billing_period_start=invoice.billing_period_start,
        billing_period_end=invoice.billing_period_end,
        subtotal=invoice.subtotal,
        vat_amount=invoice.vat_amount,
        total_amount=invoice.total_amount,
        amount_paid=invoice.amount_paid,
        balance_due=invoice.balance_due,
        transaction_ids=invoice.transaction_ids,
        status=invoice.status.value,
        payment_reference=invoice.payment_reference,
        paid_at=invoice.paid_at,
        company_name=invoice.company_name,
        company_address=invoice.company_address,
        receipt_number=invoice.receipt_number,
        notes=invoice.notes
    )


@router.post("/monthly-statements", response_model=MonthlyStatementResponse)
async def create_monthly_statement(request: CreateMonthlyStatementRequest):
    """Create a monthly statement for a credit customer"""
    
    customer = await Customer.find_one(Customer.customer_id == request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    existing_statement = await MonthlyStatement.find_one(MonthlyStatement.statement_id == request.statement_id)
    if existing_statement:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Statement ID already exists"
        )
    
    # Get transactions for the period
    transactions = await Transaction.find(
        Transaction.customer_id == request.customer_id,
        Transaction.created_at >= request.period_start,
        Transaction.created_at <= request.period_end,
        Transaction.status == "completed"
    ).to_list()
    
    # Calculate totals
    purchases = sum(tx.total_amount for tx in transactions if tx.payment_method == "credit")
    fuel_tx = len([tx for tx in transactions if tx.payment_method == "credit" and tx.fuel_type.value in ["petrol", "diesel", "kerosene"]])
    
    # Get payments
    payments = await CustomerPayment.find(
        CustomerPayment.customer_id == request.customer_id,
        CustomerPayment.payment_date >= request.period_start,
        CustomerPayment.payment_date <= request.period_end
    ).to_list()
    
    total_payments = sum(p.amount for p in payments)
    
    # Calculate balances
    opening_balance = customer.current_balance - purchases + total_payments
    closing_balance = opening_balance + purchases - total_payments
    
    statement = MonthlyStatement(
        statement_id=request.statement_id,
        customer_id=request.customer_id,
        customer_name=customer.name,
        statement_month=request.statement_month,
        statement_year=request.statement_year,
        period_start=request.period_start,
        period_end=request.period_end,
        opening_balance=opening_balance,
        purchases=purchases,
        payments=total_payments,
        closing_balance=closing_balance,
        fuel_transactions=fuel_tx,
        total_transactions=len(transactions),
        delivery_method=request.delivery_method,
        delivery_address=request.delivery_address
    )
    
    await statement.insert()
    
    return MonthlyStatementResponse(
        id=str(statement.id),
        statement_id=statement.statement_id,
        customer_id=statement.customer_id,
        customer_name=statement.customer_name,
        statement_month=statement.statement_month,
        statement_year=statement.statement_year,
        period_start=statement.period_start,
        period_end=statement.period_end,
        opening_balance=statement.opening_balance,
        purchases=statement.purchases,
        payments=statement.payments,
        adjustments=statement.adjustments,
        closing_balance=statement.closing_balance,
        fuel_transactions=statement.fuel_transactions,
        lubricant_transactions=statement.lubricant_transactions,
        shop_transactions=statement.shop_transactions,
        total_transactions=statement.total_transactions,
        invoice_id=statement.invoice_id,
        sent=statement.sent,
        sent_at=statement.sent_at,
        viewed=statement.viewed,
        viewed_at=statement.viewed_at,
        delivery_method=statement.delivery_method,
        notes=statement.notes
    )


@router.get("/monthly-statements", response_model=List[MonthlyStatementResponse])
async def get_monthly_statements(skip: int = 0, limit: int = 100, customer_id: Optional[str] = None):
    """Get all monthly statements with optional filtering"""
    
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    statements = await MonthlyStatement.find(query).skip(skip).limit(limit).sort("-period_start").to_list()
    
    return [
        MonthlyStatementResponse(
            id=str(s.id),
            statement_id=s.statement_id,
            customer_id=s.customer_id,
            customer_name=s.customer_name,
            statement_month=s.statement_month,
            statement_year=s.statement_year,
            period_start=s.period_start,
            period_end=s.period_end,
            opening_balance=s.opening_balance,
            purchases=s.purchases,
            payments=s.payments,
            adjustments=s.adjustments,
            closing_balance=s.closing_balance,
            fuel_transactions=s.fuel_transactions,
            lubricant_transactions=s.lubricant_transactions,
            shop_transactions=s.shop_transactions,
            total_transactions=s.total_transactions,
            invoice_id=s.invoice_id,
            sent=s.sent,
            sent_at=s.sent_at,
            viewed=s.viewed,
            viewed_at=s.viewed_at,
            delivery_method=s.delivery_method,
            notes=s.notes
        )
        for s in statements
    ]


@router.post("/payments", response_model=PaymentResponse)
async def record_payment(request: RecordPaymentRequest):
    """Record a payment from a credit customer"""
    
    customer = await Customer.find_one(Customer.customer_id == request.customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    existing_payment = await CustomerPayment.find_one(CustomerPayment.payment_id == request.payment_id)
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment ID already exists"
        )
    
    payment = CustomerPayment(
        payment_id=request.payment_id,
        customer_id=request.customer_id,
        customer_name=customer.name,
        amount=request.amount,
        payment_method=request.payment_method,
        payment_reference=request.payment_reference,
        invoice_ids=request.invoice_ids,
        recorded_by=request.recorded_by,
        notes=request.notes
    )
    
    await payment.insert()
    
    # Update customer balance
    customer.current_balance -= request.amount
    customer.updated_at = datetime.utcnow()
    await customer.save()
    
    # Update invoice balances if specified
    if request.invoice_ids:
        for inv_id in request.invoice_ids:
            invoice = await Invoice.find_one(Invoice.invoice_id == inv_id)
            if invoice:
                invoice.amount_paid += request.amount
                invoice.balance_due -= request.amount
                if invoice.balance_due <= 0:
                    invoice.status = InvoiceStatus.PAID
                    invoice.paid_at = datetime.utcnow()
                elif invoice.amount_paid > 0:
                    invoice.status = InvoiceStatus.PARTIALLY_PAID
                await invoice.save()
    
    return PaymentResponse(
        id=str(payment.id),
        payment_id=payment.payment_id,
        customer_id=payment.customer_id,
        customer_name=payment.customer_name,
        amount=payment.amount,
        payment_method=payment.payment_method,
        payment_reference=payment.payment_reference,
        payment_date=payment.payment_date,
        invoice_ids=payment.invoice_ids,
        status=payment.status,
        recorded_by=payment.recorded_by,
        notes=payment.notes
    )


@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(skip: int = 0, limit: int = 100, customer_id: Optional[str] = None):
    """Get all payments with optional filtering"""
    
    query = {}
    if customer_id:
        query["customer_id"] = customer_id
    
    payments = await CustomerPayment.find(query).skip(skip).limit(limit).sort("-payment_date").to_list()
    
    return [
        PaymentResponse(
            id=str(p.id),
            payment_id=p.payment_id,
            customer_id=p.customer_id,
            customer_name=p.customer_name,
            amount=p.amount,
            payment_method=p.payment_method,
            payment_reference=p.payment_reference,
            payment_date=p.payment_date,
            invoice_ids=p.invoice_ids,
            status=p.status,
            recorded_by=p.recorded_by,
            notes=p.notes
        )
        for p in payments
    ]


@router.get("/customers/{customer_id}/balance")
async def get_customer_balance(customer_id: str):
    """Get current balance for a customer"""
    
    customer = await Customer.find_one(Customer.customer_id == customer_id)
    
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    return {
        "customer_id": customer.customer_id,
        "customer_name": customer.name,
        "current_balance": customer.current_balance,
        "credit_limit": customer.credit_limit,
        "available_credit": (customer.credit_limit or 0) - customer.current_balance
    }
