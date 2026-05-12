from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.shift import Shift, CashCount, ShiftStatus

router = APIRouter(prefix="/shift", tags=["shift"])


class CreateShiftRequest(BaseModel):
    shift_id: str
    staff_id: str
    staff_name: str
    opening_cash: float = 0


class CloseShiftRequest(BaseModel):
    closing_cash: float
    notes: Optional[str] = None


class ShiftResponse(BaseModel):
    id: str
    shift_id: str
    staff_id: str
    staff_name: str
    shift_date: datetime
    start_time: datetime
    end_time: Optional[datetime]
    status: str
    opening_cash: float
    closing_cash: float
    expected_cash: float
    cash_variance: float
    total_sales: float
    fuel_sales: float
    shop_sales: float
    cash_sales: float
    mobile_money_sales: float
    card_sales: float
    credit_sales: float
    petrol_sales: float
    diesel_sales: float
    kerosene_sales: float
    total_transactions: int
    fuel_transactions: int
    shop_transactions: int
    notes: Optional[str]
    reconciled_by: Optional[str]
    reconciled_at: Optional[datetime]


class CreateCashCountRequest(BaseModel):
    count_id: str
    shift_id: str
    staff_id: str
    notes_5000: int = 0
    notes_2000: int = 0
    notes_1000: int = 0
    notes_500: int = 0
    notes_200: int = 0
    notes_100: int = 0
    notes_50: int = 0
    coins: float = 0
    expected_amount: float
    notes: Optional[str] = None


class CashCountResponse(BaseModel):
    id: str
    count_id: str
    shift_id: str
    staff_id: str
    counted_at: datetime
    notes_5000: int
    notes_2000: int
    notes_1000: int
    notes_500: int
    notes_200: int
    notes_100: int
    notes_50: int
    coins: float
    total_counted: float
    expected_amount: float
    variance: float
    verified_by: Optional[str]
    notes: Optional[str]


@router.post("/shifts", response_model=ShiftResponse)
async def create_shift(request: CreateShiftRequest):
    """Start a new shift"""
    shift = Shift(
        shift_id=request.shift_id,
        staff_id=request.staff_id,
        staff_name=request.staff_name,
        opening_cash=request.opening_cash,
        expected_cash=request.opening_cash
    )
    
    await shift.insert()
    
    return ShiftResponse(
        id=str(shift.id),
        shift_id=shift.shift_id,
        staff_id=shift.staff_id,
        staff_name=shift.staff_name,
        shift_date=shift.shift_date,
        start_time=shift.start_time,
        end_time=shift.end_time,
        status=shift.status.value,
        opening_cash=shift.opening_cash,
        closing_cash=shift.closing_cash,
        expected_cash=shift.expected_cash,
        cash_variance=shift.cash_variance,
        total_sales=shift.total_sales,
        fuel_sales=shift.fuel_sales,
        shop_sales=shift.shop_sales,
        cash_sales=shift.cash_sales,
        mobile_money_sales=shift.mobile_money_sales,
        card_sales=shift.card_sales,
        credit_sales=shift.credit_sales,
        petrol_sales=shift.petrol_sales,
        diesel_sales=shift.diesel_sales,
        kerosene_sales=shift.kerosene_sales,
        total_transactions=shift.total_transactions,
        fuel_transactions=shift.fuel_transactions,
        shop_transactions=shift.shop_transactions,
        notes=shift.notes,
        reconciled_by=shift.reconciled_by,
        reconciled_at=shift.reconciled_at
    )


@router.put("/shifts/{shift_id}/close", response_model=ShiftResponse)
async def close_shift(shift_id: str, request: CloseShiftRequest, user_id: str = "user"):
    """Close a shift and calculate variance"""
    shift = await Shift.find_one(Shift.shift_id == shift_id)
    
    if not shift:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shift not found"
        )
    
    shift.end_time = datetime.utcnow()
    shift.closing_cash = request.closing_cash
    shift.cash_variance = shift.closing_cash - shift.expected_cash
    shift.status = ShiftStatus.CLOSED
    shift.notes = request.notes
    shift.reconciled_by = user_id
    shift.reconciled_at = datetime.utcnow()
    
    await shift.save()
    
    return ShiftResponse(
        id=str(shift.id),
        shift_id=shift.shift_id,
        staff_id=shift.staff_id,
        staff_name=shift.staff_name,
        shift_date=shift.shift_date,
        start_time=shift.start_time,
        end_time=shift.end_time,
        status=shift.status.value,
        opening_cash=shift.opening_cash,
        closing_cash=shift.closing_cash,
        expected_cash=shift.expected_cash,
        cash_variance=shift.cash_variance,
        total_sales=shift.total_sales,
        fuel_sales=shift.fuel_sales,
        shop_sales=shift.shop_sales,
        cash_sales=shift.cash_sales,
        mobile_money_sales=shift.mobile_money_sales,
        card_sales=shift.card_sales,
        credit_sales=shift.credit_sales,
        petrol_sales=shift.petrol_sales,
        diesel_sales=shift.diesel_sales,
        kerosene_sales=shift.kerosene_sales,
        total_transactions=shift.total_transactions,
        fuel_transactions=shift.fuel_transactions,
        shop_transactions=shift.shop_transactions,
        notes=shift.notes,
        reconciled_by=shift.reconciled_by,
        reconciled_at=shift.reconciled_at
    )


@router.get("/shifts", response_model=List[ShiftResponse])
async def get_shifts(skip: int = 0, limit: int = 100, staff_id: Optional[str] = None):
    """Get all shifts with optional filtering"""
    query = {}
    if staff_id:
        query["staff_id"] = staff_id
    
    shifts = await Shift.find(query).skip(skip).limit(limit).sort("-start_time").to_list()
    
    return [
        ShiftResponse(
            id=str(s.id),
            shift_id=s.shift_id,
            staff_id=s.staff_id,
            staff_name=s.staff_name,
            shift_date=s.shift_date,
            start_time=s.start_time,
            end_time=s.end_time,
            status=s.status.value,
            opening_cash=s.opening_cash,
            closing_cash=s.closing_cash,
            expected_cash=s.expected_cash,
            cash_variance=s.cash_variance,
            total_sales=s.total_sales,
            fuel_sales=s.fuel_sales,
            shop_sales=s.shop_sales,
            cash_sales=s.cash_sales,
            mobile_money_sales=s.mobile_money_sales,
            card_sales=s.card_sales,
            credit_sales=s.credit_sales,
            petrol_sales=s.petrol_sales,
            diesel_sales=s.diesel_sales,
            kerosene_sales=s.kerosene_sales,
            total_transactions=s.total_transactions,
            fuel_transactions=s.fuel_transactions,
            shop_transactions=s.shop_transactions,
            notes=s.notes,
            reconciled_by=s.reconciled_by,
            reconciled_at=s.reconciled_at
        )
        for s in shifts
    ]


@router.post("/cash-counts", response_model=CashCountResponse)
async def create_cash_count(request: CreateCashCountRequest):
    """Create a cash count record"""
    total_counted = (
        request.notes_5000 * 5000 +
        request.notes_2000 * 2000 +
        request.notes_1000 * 1000 +
        request.notes_500 * 500 +
        request.notes_200 * 200 +
        request.notes_100 * 100 +
        request.notes_50 * 50 +
        request.coins
    )
    
    variance = total_counted - request.expected_amount
    
    cash_count = CashCount(
        count_id=request.count_id,
        shift_id=request.shift_id,
        staff_id=request.staff_id,
        notes_5000=request.notes_5000,
        notes_2000=request.notes_2000,
        notes_1000=request.notes_1000,
        notes_500=request.notes_500,
        notes_200=request.notes_200,
        notes_100=request.notes_100,
        notes_50=request.notes_50,
        coins=request.coins,
        total_counted=total_counted,
        expected_amount=request.expected_amount,
        variance=variance,
        notes=request.notes
    )
    
    await cash_count.insert()
    
    return CashCountResponse(
        id=str(cash_count.id),
        count_id=cash_count.count_id,
        shift_id=cash_count.shift_id,
        staff_id=cash_count.staff_id,
        counted_at=cash_count.counted_at,
        notes_5000=cash_count.notes_5000,
        notes_2000=cash_count.notes_2000,
        notes_1000=cash_count.notes_1000,
        notes_500=cash_count.notes_500,
        notes_200=cash_count.notes_200,
        notes_100=cash_count.notes_100,
        notes_50=cash_count.notes_50,
        coins=cash_count.coins,
        total_counted=cash_count.total_counted,
        expected_amount=cash_count.expected_amount,
        variance=cash_count.variance,
        verified_by=cash_count.verified_by,
        notes=cash_count.notes
    )


@router.get("/cash-counts", response_model=List[CashCountResponse])
async def get_cash_counts(skip: int = 0, limit: int = 100, shift_id: Optional[str] = None):
    """Get all cash counts with optional filtering"""
    query = {}
    if shift_id:
        query["shift_id"] = shift_id
    
    cash_counts = await CashCount.find(query).skip(skip).limit(limit).sort("-counted_at").to_list()
    
    return [
        CashCountResponse(
            id=str(c.id),
            count_id=c.count_id,
            shift_id=c.shift_id,
            staff_id=c.staff_id,
            counted_at=c.counted_at,
            notes_5000=c.notes_5000,
            notes_2000=c.notes_2000,
            notes_1000=c.notes_1000,
            notes_500=c.notes_500,
            notes_200=c.notes_200,
            notes_100=c.notes_100,
            notes_50=c.notes_50,
            coins=c.coins,
            total_counted=c.total_counted,
            expected_amount=c.expected_amount,
            variance=c.variance,
            verified_by=c.verified_by,
            notes=c.notes
        )
        for c in cash_counts
    ]
