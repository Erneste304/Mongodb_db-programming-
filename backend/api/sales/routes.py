from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.sales import Transaction, Customer, FuelType, PaymentMethod, TransactionStatus
from backend.models.user import User
from backend.services.access_control import AccessControlService
from backend.services.tax_service import TaxService
from backend.services.payment_service import PaymentService
from backend.services.loyalty_service import LoyaltyAIService
from backend.services.pricing_service import PricingService
from backend.core.security import require_role_level

router = APIRouter(prefix="/sales", tags=["sales"])


class CreateTransactionRequest(BaseModel):
    transaction_id: str
    customer_id: Optional[str] = None
    fuel_type: FuelType
    quantity_liters: float
    price_per_liter: float
    payment_method: PaymentMethod
    payment_reference: Optional[str] = None
    pump_number: Optional[int] = None
    attendant_id: Optional[str] = None
    phone_number: Optional[str] = None  # Required for mobile money
    provider: Optional[str] = "MTN"  # MTN or Airtel
    receipt_number: Optional[str] = None
    tin_number: Optional[str] = None


class UpdateTransactionRequest(BaseModel):
    status: Optional[TransactionStatus] = None


class TransactionResponse(BaseModel):
    id: str
    transaction_id: str
    customer_id: Optional[str]
    customer_name: Optional[str] = None
    customer_tin: Optional[str] = None
    fuel_type: str
    quantity_liters: float
    price_per_liter: float
    total_amount: float
    payment_method: str
    payment_reference: Optional[str]
    pump_number: Optional[int]
    attendant_id: Optional[str]
    status: str
    created_at: datetime
    receipt_number: Optional[str]


class CreateCustomerRequest(BaseModel):
    customer_id: str
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    tin_number: Optional[str] = None
    customer_type: str = "cash"
    credit_limit: Optional[float] = 0


class CustomerResponse(BaseModel):
    id: str
    customer_id: str
    name: str
    phone: Optional[str]
    email: Optional[str]
    tin_number: Optional[str]
    customer_type: str
    credit_limit: Optional[float]
    current_balance: float
    loyalty_points: int
    is_active: bool
    created_at: datetime


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(request: CreateTransactionRequest, user_id: str = "user"):
    """Create a new sales transaction"""

    # 1. Fetch Latest RRA-Approved Price (Secure/Dynamic)
    price_per_liter = await PricingService.get_current_price(request.fuel_type)
    total_amount = request.quantity_liters * price_per_liter

    transaction = Transaction(
        transaction_id=request.transaction_id,
        customer_id=request.customer_id,
        fuel_type=request.fuel_type,
        quantity_liters=request.quantity_liters,
        price_per_liter=price_per_liter,
        total_amount=total_amount,
        payment_method=request.payment_method,
        payment_reference=request.payment_reference,
        pump_number=request.pump_number,
        attendant_id=request.attendant_id,
        receipt_number=request.receipt_number,
        tin_number=request.tin_number,
        status=TransactionStatus.COMPLETED
    )

    # 3. Apply EBM Signing (Rwanda RRA Requirement)
    transaction = await TaxService.sign_transaction(transaction)

    # 4. Handle Mobile Money Payment (Rwanda-Specific Push-to-Pay)
    if request.payment_method == PaymentMethod.MOBILE_MONEY:
        if not request.phone_number:
            raise HTTPException(
                status_code=400, detail="Phone number required for mobile money")

        payment_result = await PaymentService.process_mobile_money_payment(
            phone_number=request.phone_number,
            amount=request.total_amount,
            provider=request.provider
        )

        if payment_result["status"] != "successful":
            raise HTTPException(
                status_code=402,
                detail=f"Payment Failed: {payment_result['message']}"
            )

        transaction.payment_reference = payment_result["external_id"]
        transaction.notes = (transaction.notes or "") + \
            f" | MoMo Payment Verified: {payment_result['external_id']}"

    # 5. Apply AI-Driven Loyalty Rewards
    customer = None
    if request.customer_id:
        customer = await Customer.find_one(Customer.customer_id == request.customer_id)

    if customer:
        loyalty_results = await LoyaltyAIService.apply_loyalty_rewards(transaction, customer)

        # Update customer points and balance
        customer.loyalty_points += loyalty_results["points_earned"]

        if transaction.payment_method == PaymentMethod.CREDIT:
            customer.current_balance += (transaction.total_amount -
                                         loyalty_results["discount_applied"])

        await customer.save()

        transaction.notes = (transaction.notes or "") + \
            f" | Loyalty Points: +{loyalty_results['points_earned']}"
        if loyalty_results["discount_applied"] > 0:
            transaction.notes += f" | AI Discount: -{loyalty_results['discount_applied']} RWF"

    await transaction.insert()

    # Log the action
    # await AuditLogService.log_action(...)

    return TransactionResponse(
        id=str(transaction.id),
        transaction_id=transaction.transaction_id,
        customer_id=transaction.customer_id,
        fuel_type=transaction.fuel_type.value,
        quantity_liters=transaction.quantity_liters,
        price_per_liter=transaction.price_per_liter,
        total_amount=transaction.total_amount,
        payment_method=transaction.payment_method.value,
        payment_reference=transaction.payment_reference,
        pump_number=transaction.pump_number,
        attendant_id=transaction.attendant_id,
        status=transaction.status.value,
        created_at=transaction.created_at,
        receipt_number=transaction.receipt_number,
        customer_name=customer.name if customer else "Walk-in",
        customer_tin=customer.tin_number if customer else request.tin_number
    )


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(skip: int = 0, limit: int = 100, fuel_type: Optional[FuelType] = None):
    """Get all transactions with optional filtering"""

    query = {}
    if fuel_type:
        query["fuel_type"] = fuel_type

    # Use string-based sorting for better stability across Beanie versions
    transactions = await Transaction.find(query).skip(skip).limit(limit).sort("-created_at").to_list()

    res = []
    for tx in transactions:
        cust_name = "Walk-in"
        cust_tin = tx.tin_number
        if tx.customer_id:
            cust = await Customer.find_one(Customer.customer_id == tx.customer_id)
            if cust:
                cust_name = cust.name
                cust_tin = cust.tin_number or tx.tin_number

        res.append(TransactionResponse(
            id=str(tx.id),
            transaction_id=tx.transaction_id,
            customer_id=tx.customer_id,
            customer_name=cust_name,
            customer_tin=cust_tin,
            fuel_type=tx.fuel_type.value,
            quantity_liters=tx.quantity_liters,
            price_per_liter=tx.price_per_liter,
            total_amount=tx.total_amount,
            payment_method=tx.payment_method.value,
            payment_reference=tx.payment_reference,
            pump_number=tx.pump_number,
            attendant_id=tx.attendant_id,
            status=tx.status.value,
            created_at=tx.created_at,
            receipt_number=tx.receipt_number
        ))
    return res


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: str):
    """Get a specific transaction by ID"""
    transaction = await Transaction.find_one(Transaction.transaction_id == transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    customer = await Customer.find_one(Customer.customer_id == transaction.customer_id) if transaction.customer_id else None

    return TransactionResponse(
        id=str(transaction.id),
        transaction_id=transaction.transaction_id,
        customer_id=transaction.customer_id,
        customer_name=customer.name if customer else "Walk-in",
        customer_tin=customer.tin_number if customer else transaction.tin_number,
        fuel_type=transaction.fuel_type.value,
        quantity_liters=transaction.quantity_liters,
        price_per_liter=transaction.price_per_liter,
        total_amount=transaction.total_amount,
        payment_method=transaction.payment_method.value,
        payment_reference=transaction.payment_reference,
        pump_number=transaction.pump_number,
        attendant_id=transaction.attendant_id,
        status=transaction.status.value,
        created_at=transaction.created_at,
        receipt_number=transaction.receipt_number
    )


@router.post("/transactions/{transaction_id}/void")
async def void_transaction(transaction_id: str, reason: str, user_id: str = "user"):
    """Void a transaction (requires admin approval)"""

    transaction = await Transaction.find_one(Transaction.transaction_id == transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    if transaction.status == TransactionStatus.VOIDED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction already voided"
        )

    # Check if approval is required (should be handled by approval workflow)
    # For now, directly void

    transaction.status = TransactionStatus.VOIDED
    transaction.voided_by = user_id
    transaction.voided_at = datetime.utcnow()
    transaction.void_reason = reason
    await transaction.save()

    return {"message": "Transaction voided successfully"}


@router.post("/customers", response_model=CustomerResponse)
async def create_customer(request: CreateCustomerRequest):
    """Create a new customer"""

    existing_customer = await Customer.find_one(Customer.customer_id == request.customer_id)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Customer ID already exists"
        )

    customer = Customer(
        customer_id=request.customer_id,
        name=request.name,
        phone=request.phone,
        email=request.email,
        tin_number=request.tin_number,
        customer_type=request.customer_type,
        credit_limit=request.credit_limit
    )

    await customer.insert()

    return CustomerResponse(
        id=str(customer.id),
        customer_id=customer.customer_id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        tin_number=customer.tin_number,
        customer_type=customer.customer_type,
        credit_limit=customer.credit_limit,
        current_balance=customer.current_balance,
        loyalty_points=customer.loyalty_points,
        is_active=customer.is_active,
        created_at=customer.created_at
    )


@router.get("/customers", response_model=List[CustomerResponse])
async def get_customers(skip: int = 0, limit: int = 100):
    """Get all customers"""

    customers = await Customer.find_all().skip(skip).limit(limit).to_list()

    return [
        CustomerResponse(
            id=str(c.id),
            customer_id=c.customer_id,
            name=c.name,
            phone=c.phone,
            email=c.email,
            tin_number=c.tin_number,
            customer_type=c.customer_type,
            credit_limit=c.credit_limit,
            current_balance=c.current_balance,
            loyalty_points=c.loyalty_points,
            is_active=c.is_active,
            created_at=c.created_at
        )
        for c in customers
    ]


@router.get("/customers/{customer_id}", response_model=CustomerResponse)
async def get_customer(customer_id: str):
    """Get a specific customer"""

    customer = await Customer.find_one(Customer.customer_id == customer_id)

    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )

    return CustomerResponse(
        id=str(customer.id),
        customer_id=customer.customer_id,
        name=customer.name,
        phone=customer.phone,
        email=customer.email,
        tin_number=customer.tin_number,
        customer_type=customer.customer_type,
        credit_limit=customer.credit_limit,
        current_balance=customer.current_balance,
        loyalty_points=customer.loyalty_points,
        is_active=customer.is_active,
        created_at=customer.created_at
    )


class TransactionOverrideRequest(BaseModel):
    new_amount: float
    reason: str
    supporting_documents: Optional[List[str]] = None


@router.post("/transactions/{transaction_id}/override")
async def override_transaction(
    transaction_id: str,
    request: TransactionOverrideRequest,
    current_user: User = Depends(require_role_level(1))
):
    """
    Override any transaction - SUPERADMIN ONLY
    Allows superadmin to correct transaction errors
    """
    from backend.core.security import require_role_level
    from backend.models.user import User
    from backend.services.audit_service import AuditLogService

    transaction = await Transaction.find_one(Transaction.transaction_id == transaction_id)

    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )

    # Store old values for audit
    old_values = {
        "total_amount": transaction.total_amount,
        "quantity_liters": transaction.quantity_liters,
        "price_per_liter": transaction.price_per_liter,
        "status": transaction.status.value
    }

    # Calculate new quantity based on new amount
    new_quantity = request.new_amount / transaction.price_per_liter

    # Update transaction
    transaction.total_amount = request.new_amount
    transaction.quantity_liters = new_quantity
    transaction.status = TransactionStatus.MODIFIED
    transaction.notes = f"OVERRIDDEN by Superadmin {current_user.username}: {request.reason}"

    await transaction.save()

    # Log the override action
    await AuditLogService.log_action(
        user=current_user,
        action="overrode_transaction",
        resource_type="transaction",
        resource_id=str(transaction.id),
        old_value=old_values,
        new_value={
            "total_amount": transaction.total_amount,
            "quantity_liters": transaction.quantity_liters,
            "reason": request.reason,
            "overridden_by": current_user.username
        }
    )

    return {
        "message": "Transaction overridden successfully",
        "transaction_id": transaction_id,
        "new_amount": request.new_amount,
        "override_reason": request.reason,
        "overridden_by": current_user.username,
        "overridden_at": datetime.utcnow()
    }
