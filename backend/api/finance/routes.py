from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.finance import (
    Payment, DailyCashReconciliation, PettyCash,
    PaymentType, PaymentMethod, PaymentStatus, ExpenseCategory
)

router = APIRouter(prefix="/finance", tags=["finance"])


class CreatePaymentRequest(BaseModel):
    payment_id: str
    payment_type: PaymentType
    amount: float
    payment_method: PaymentMethod
    recipient_name: str
    recipient_account: Optional[str] = None
    reference_number: Optional[str] = None
    description: str
    category: Optional[ExpenseCategory] = None
    requested_by: str
    notes: Optional[str] = None


class ProcessPaymentRequest(BaseModel):
    approved_by: str
    processed_by: str


class PaymentResponse(BaseModel):
    id: str
    payment_id: str
    payment_type: str
    amount: float
    payment_method: str
    recipient_name: str
    recipient_account: Optional[str]
    reference_number: Optional[str]
    description: str
    category: Optional[str]
    status: str
    requested_by: str
    approved_by: Optional[str]
    processed_by: Optional[str]
    requested_at: datetime
    approved_at: Optional[datetime]
    processed_at: Optional[datetime]


class CreateReconciliationRequest(BaseModel):
    reconciliation_id: str
    date: datetime
    opening_balance: float
    cash_sales: float
    mobile_money_sales: float
    card_sales: float
    credit_sales: float
    cash_paid_out: float
    bank_deposit: float
    reconciled_by: str
    notes: Optional[str] = None


class ReconciliationResponse(BaseModel):
    id: str
    reconciliation_id: str
    date: datetime
    opening_balance: float
    cash_sales: float
    mobile_money_sales: float
    card_sales: float
    credit_sales: float
    total_sales: float
    cash_paid_out: float
    bank_deposit: float
    closing_balance: float
    variance: float
    reconciled_by: str
    notes: Optional[str]


class CreatePettyCashRequest(BaseModel):
    transaction_id: str
    transaction_type: str
    amount: float
    description: str
    category: Optional[ExpenseCategory] = None
    performed_by: str
    balance_after: float


class PettyCashResponse(BaseModel):
    id: str
    transaction_id: str
    transaction_type: str
    amount: float
    description: str
    category: Optional[str]
    performed_by: str
    balance_after: float
    created_at: datetime


@router.post("/payments", response_model=PaymentResponse)
async def create_payment(request: CreatePaymentRequest):
    """Create a new payment request"""
    
    existing_payment = await Payment.find_one(Payment.payment_id == request.payment_id)
    if existing_payment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment ID already exists"
        )
    
    payment = Payment(**request.dict())
    await payment.insert()
    
    return PaymentResponse(
        id=str(payment.id),
        payment_id=payment.payment_id,
        payment_type=payment.payment_type.value,
        amount=payment.amount,
        payment_method=payment.payment_method.value,
        recipient_name=payment.recipient_name,
        recipient_account=payment.recipient_account,
        reference_number=payment.reference_number,
        description=payment.description,
        category=payment.category.value if payment.category else None,
        status=payment.status.value,
        requested_by=payment.requested_by,
        approved_by=payment.approved_by,
        processed_by=payment.processed_by,
        requested_at=payment.requested_at,
        approved_at=payment.approved_at,
        processed_at=payment.processed_at
    )


@router.get("/payments", response_model=List[PaymentResponse])
async def get_payments(skip: int = 0, limit: int = 100, status: Optional[PaymentStatus] = None):
    """Get all payments with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    payments = await Payment.find(query).skip(skip).limit(limit).sort(-Payment.requested_at).to_list()
    
    return [
        PaymentResponse(
            id=str(payment.id),
            payment_id=payment.payment_id,
            payment_type=payment.payment_type.value,
            amount=payment.amount,
            payment_method=payment.payment_method.value,
            recipient_name=payment.recipient_name,
            recipient_account=payment.recipient_account,
            reference_number=payment.reference_number,
            description=payment.description,
            category=payment.category.value if payment.category else None,
            status=payment.status.value,
            requested_by=payment.requested_by,
            approved_by=payment.approved_by,
            processed_by=payment.processed_by,
            requested_at=payment.requested_at,
            approved_at=payment.approved_at,
            processed_at=payment.processed_at
        )
        for payment in payments
    ]


@router.get("/payments/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: str):
    """Get a specific payment"""
    
    payment = await Payment.find_one(Payment.payment_id == payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return PaymentResponse(
        id=str(payment.id),
        payment_id=payment.payment_id,
        payment_type=payment.payment_type.value,
        amount=payment.amount,
        payment_method=payment.payment_method.value,
        recipient_name=payment.recipient_name,
        recipient_account=payment.recipient_account,
        reference_number=payment.reference_number,
        description=payment.description,
        category=payment.category.value if payment.category else None,
        status=payment.status.value,
        requested_by=payment.requested_by,
        approved_by=payment.approved_by,
        processed_by=payment.processed_by,
        requested_at=payment.requested_at,
        approved_at=payment.approved_at,
        processed_at=payment.processed_at
    )


@router.post("/payments/{payment_id}/approve")
async def approve_payment(payment_id: str, approved_by: str):
    """Approve a payment"""
    
    payment = await Payment.find_one(Payment.payment_id == payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment cannot be approved"
        )
    
    payment.status = PaymentStatus.APPROVED
    payment.approved_by = approved_by
    payment.approved_at = datetime.utcnow()
    await payment.save()
    
    return {"message": "Payment approved successfully"}


@router.post("/payments/{payment_id}/process")
async def process_payment(payment_id: str, request: ProcessPaymentRequest):
    """Process an approved payment"""
    
    payment = await Payment.find_one(Payment.payment_id == payment_id)
    
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    if payment.status != PaymentStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment must be approved before processing"
        )
    
    payment.status = PaymentStatus.PROCESSED
    payment.approved_by = request.approved_by
    payment.processed_by = request.processed_by
    payment.processed_at = datetime.utcnow()
    await payment.save()
    
    return {"message": "Payment processed successfully"}


@router.post("/reconciliations", response_model=ReconciliationResponse)
async def create_reconciliation(request: CreateReconciliationRequest):
    """Create daily cash reconciliation"""
    
    existing_reconciliation = await DailyCashReconciliation.find_one(
        DailyCashReconciliation.reconciliation_id == request.reconciliation_id
    )
    if existing_reconciliation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reconciliation ID already exists"
        )
    
    # Calculate totals
    total_sales = request.cash_sales + request.mobile_money_sales + request.card_sales + request.credit_sales
    closing_balance = request.opening_balance + request.cash_sales - request.cash_paid_out - request.bank_deposit
    variance = closing_balance - (request.opening_balance + request.cash_sales - request.cash_paid_out - request.bank_deposit)
    
    reconciliation = DailyCashReconciliation(
        reconciliation_id=request.reconciliation_id,
        date=request.date,
        opening_balance=request.opening_balance,
        cash_sales=request.cash_sales,
        mobile_money_sales=request.mobile_money_sales,
        card_sales=request.card_sales,
        credit_sales=request.credit_sales,
        total_sales=total_sales,
        cash_paid_out=request.cash_paid_out,
        bank_deposit=request.bank_deposit,
        closing_balance=closing_balance,
        variance=variance,
        reconciled_by=request.reconciled_by,
        notes=request.notes
    )
    
    await reconciliation.insert()
    
    return ReconciliationResponse(
        id=str(reconciliation.id),
        reconciliation_id=reconciliation.reconciliation_id,
        date=reconciliation.date,
        opening_balance=reconciliation.opening_balance,
        cash_sales=reconciliation.cash_sales,
        mobile_money_sales=reconciliation.mobile_money_sales,
        card_sales=reconciliation.card_sales,
        credit_sales=reconciliation.credit_sales,
        total_sales=reconciliation.total_sales,
        cash_paid_out=reconciliation.cash_paid_out,
        bank_deposit=reconciliation.bank_deposit,
        closing_balance=reconciliation.closing_balance,
        variance=reconciliation.variance,
        reconciled_by=reconciliation.reconciled_by,
        notes=reconciliation.notes
    )


@router.get("/reconciliations", response_model=List[ReconciliationResponse])
async def get_reconciliations(skip: int = 0, limit: int = 100):
    """Get all reconciliations"""
    
    reconciliations = await DailyCashReconciliation.find_all().skip(skip).limit(limit).sort(-DailyCashReconciliation.date).to_list()
    
    return [
        ReconciliationResponse(
            id=str(reconciliation.id),
            reconciliation_id=reconciliation.reconciliation_id,
            date=reconciliation.date,
            opening_balance=reconciliation.opening_balance,
            cash_sales=reconciliation.cash_sales,
            mobile_money_sales=reconciliation.mobile_money_sales,
            card_sales=reconciliation.card_sales,
            credit_sales=reconciliation.credit_sales,
            total_sales=reconciliation.total_sales,
            cash_paid_out=reconciliation.cash_paid_out,
            bank_deposit=reconciliation.bank_deposit,
            closing_balance=reconciliation.closing_balance,
            variance=reconciliation.variance,
            reconciled_by=reconciliation.reconciled_by,
            notes=reconciliation.notes
        )
        for reconciliation in reconciliations
    ]


@router.post("/petty-cash", response_model=PettyCashResponse)
async def create_petty_cash_transaction(request: CreatePettyCashRequest):
    """Create petty cash transaction"""
    
    existing_transaction = await PettyCash.find_one(
        PettyCash.transaction_id == request.transaction_id
    )
    if existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction ID already exists"
        )
    
    transaction = PettyCash(**request.dict())
    await transaction.insert()
    
    return PettyCashResponse(
        id=str(transaction.id),
        transaction_id=transaction.transaction_id,
        transaction_type=transaction.transaction_type,
        amount=transaction.amount,
        description=transaction.description,
        category=transaction.category.value if transaction.category else None,
        performed_by=transaction.performed_by,
        balance_after=transaction.balance_after,
        created_at=transaction.created_at
    )


@router.get("/petty-cash", response_model=List[PettyCashResponse])
async def get_petty_cash_transactions(skip: int = 0, limit: int = 100):
    """Get all petty cash transactions"""
    
    transactions = await PettyCash.find_all().skip(skip).limit(limit).sort(-PettyCash.created_at).to_list()
    
    return [
        PettyCashResponse(
            id=str(transaction.id),
            transaction_id=transaction.transaction_id,
            transaction_type=transaction.transaction_type,
            amount=transaction.amount,
            description=transaction.description,
            category=transaction.category.value if transaction.category else None,
            performed_by=transaction.performed_by,
            balance_after=transaction.balance_after,
            created_at=transaction.created_at
        )
        for transaction in transactions
    ]


@router.get("/petty-cash/balance")
async def get_petty_cash_balance():
    """Get current petty cash balance"""
    
    latest_transaction = await PettyCash.find_all().sort(-PettyCash.created_at).limit(1).to_list()
    
    if not latest_transaction:
        return {"balance": 0.0}
    
    return {"balance": latest_transaction[0].balance_after}
