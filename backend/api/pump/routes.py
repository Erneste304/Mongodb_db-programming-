from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.pump import Pump, PumpSession, PumpStatus

router = APIRouter(prefix="/pump", tags=["pump"])


class CreatePumpRequest(BaseModel):
    pump_id: str
    pump_number: int
    tank_id: str
    fuel_type: str


class UpdatePumpRequest(BaseModel):
    status: Optional[PumpStatus] = None
    current_customer: Optional[str] = None
    current_transaction_id: Optional[str] = None


class PumpResponse(BaseModel):
    id: str
    pump_id: str
    pump_number: int
    tank_id: str
    fuel_type: str
    status: str
    current_customer: Optional[str]
    current_transaction_id: Optional[str]
    is_active: bool
    created_at: datetime


class StartPumpSessionRequest(BaseModel):
    session_id: str
    pump_id: str
    customer_id: Optional[str] = None
    transaction_id: Optional[str] = None


class EndPumpSessionRequest(BaseModel):
    fuel_dispensed_liters: float
    total_amount: float


class PumpSessionResponse(BaseModel):
    id: str
    session_id: str
    pump_id: str
    customer_id: Optional[str]
    transaction_id: Optional[str]
    started_at: datetime
    ended_at: Optional[datetime]
    fuel_dispensed_liters: float
    total_amount: float
    status: str
    notes: Optional[str]


@router.post("/pumps", response_model=PumpResponse)
async def create_pump(request: CreatePumpRequest):
    """Create a new pump"""
    pump = Pump(
        pump_id=request.pump_id,
        pump_number=request.pump_number,
        tank_id=request.tank_id,
        fuel_type=request.fuel_type
    )
    
    await pump.insert()
    
    return PumpResponse(
        id=str(pump.id),
        pump_id=pump.pump_id,
        pump_number=pump.pump_number,
        tank_id=pump.tank_id,
        fuel_type=pump.fuel_type,
        status=pump.status.value,
        current_customer=pump.current_customer,
        current_transaction_id=pump.current_transaction_id,
        is_active=pump.is_active,
        created_at=pump.created_at
    )


@router.get("/pumps", response_model=List[PumpResponse])
async def get_pumps(skip: int = 0, limit: int = 100, status: Optional[PumpStatus] = None):
    """Get all pumps with optional filtering"""
    query = {"is_active": True}
    if status:
        query["status"] = status
    
    pumps = await Pump.find(query).skip(skip).limit(limit).to_list()
    
    return [
        PumpResponse(
            id=str(p.id),
            pump_id=p.pump_id,
            pump_number=p.pump_number,
            tank_id=p.tank_id,
            fuel_type=p.fuel_type,
            status=p.status.value,
            current_customer=p.current_customer,
            current_transaction_id=p.current_transaction_id,
            is_active=p.is_active,
            created_at=p.created_at
        )
        for p in pumps
    ]


@router.put("/pumps/{pump_id}", response_model=PumpResponse)
async def update_pump(pump_id: str, request: UpdatePumpRequest):
    """Update pump status and current customer"""
    pump = await Pump.find_one(Pump.pump_id == pump_id)
    
    if not pump:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pump not found"
        )
    
    if request.status:
        pump.status = request.status
    
    if request.current_customer is not None:
        pump.current_customer = request.current_customer
    
    if request.current_transaction_id is not None:
        pump.current_transaction_id = request.current_transaction_id
    
    await pump.save()
    
    return PumpResponse(
        id=str(pump.id),
        pump_id=pump.pump_id,
        pump_number=pump.pump_number,
        tank_id=pump.tank_id,
        fuel_type=pump.fuel_type,
        status=pump.status.value,
        current_customer=pump.current_customer,
        current_transaction_id=pump.current_transaction_id,
        is_active=pump.is_active,
        created_at=pump.created_at
    )


@router.post("/sessions", response_model=PumpSessionResponse)
async def start_pump_session(request: StartPumpSessionRequest):
    """Start a new pump session"""
    session = PumpSession(
        session_id=request.session_id,
        pump_id=request.pump_id,
        customer_id=request.customer_id,
        transaction_id=request.transaction_id,
        status="active"
    )
    
    # Update pump status to in_use
    pump = await Pump.find_one(Pump.pump_id == request.pump_id)
    if pump:
        pump.status = PumpStatus.IN_USE
        pump.current_customer = request.customer_id
        pump.current_transaction_id = request.transaction_id
        await pump.save()
    
    await session.insert()
    
    return PumpSessionResponse(
        id=str(session.id),
        session_id=session.session_id,
        pump_id=session.pump_id,
        customer_id=session.customer_id,
        transaction_id=session.transaction_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        fuel_dispensed_liters=session.fuel_dispensed_liters,
        total_amount=session.total_amount,
        status=session.status,
        notes=session.notes
    )


@router.put("/sessions/{session_id}/end", response_model=PumpSessionResponse)
async def end_pump_session(session_id: str, request: EndPumpSessionRequest):
    """End a pump session with fuel dispensed amount"""
    session = await PumpSession.find_one(PumpSession.session_id == session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    session.ended_at = datetime.utcnow()
    session.fuel_dispensed_liters = request.fuel_dispensed_liters
    session.total_amount = request.total_amount
    session.status = "completed"
    
    # Update pump status to available
    pump = await Pump.find_one(Pump.pump_id == session.pump_id)
    if pump:
        pump.status = PumpStatus.AVAILABLE
        pump.current_customer = None
        pump.current_transaction_id = None
        await pump.save()
    
    await session.save()
    
    return PumpSessionResponse(
        id=str(session.id),
        session_id=session.session_id,
        pump_id=session.pump_id,
        customer_id=session.customer_id,
        transaction_id=session.transaction_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        fuel_dispensed_liters=session.fuel_dispensed_liters,
        total_amount=session.total_amount,
        status=session.status,
        notes=session.notes
    )
