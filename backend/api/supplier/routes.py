from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.supplier import Supplier, DeliverySchedule, SupplierStatus

router = APIRouter(prefix="/supplier", tags=["supplier"])


class CreateSupplierRequest(BaseModel):
    supplier_id: str
    supplier_name: str
    contact_person: str
    phone: str
    email: Optional[str] = None
    address: Optional[str] = None
    city: Optional[str] = None
    country: str = "Rwanda"
    supplied_fuel_types: List[str] = []
    supplied_lubricant_brands: List[str] = []
    payment_terms: str = "Net 30"
    credit_limit: Optional[float] = None
    tin_number: Optional[str] = None
    notes: Optional[str] = None


class SupplierResponse(BaseModel):
    id: str
    supplier_id: str
    supplier_name: str
    contact_person: str
    phone: str
    email: Optional[str]
    address: Optional[str]
    city: Optional[str]
    country: str
    supplied_fuel_types: List[str]
    supplied_lubricant_brands: List[str]
    rating: float
    total_deliveries: int
    on_time_delivery_rate: float
    payment_terms: str
    credit_limit: Optional[float]
    status: str
    tin_number: Optional[str]
    notes: Optional[str]


class CreateDeliveryScheduleRequest(BaseModel):
    schedule_id: str
    tank_id: str
    fuel_type: str
    supplier_id: str
    scheduled_date: datetime
    requested_quantity_liters: float
    estimated_cost: float
    purchase_order_number: Optional[str] = None
    created_by: str


class DeliveryScheduleResponse(BaseModel):
    id: str
    schedule_id: str
    tank_id: str
    fuel_type: str
    supplier_id: str
    scheduled_date: datetime
    requested_quantity_liters: float
    estimated_cost: float
    status: str
    confirmed_by: Optional[str]
    confirmed_at: Optional[datetime]
    actual_delivery_date: Optional[datetime]
    actual_quantity_delivered: Optional[float]
    delivery_notes: Optional[str]
    purchase_order_number: Optional[str]
    created_by: str
    created_at: datetime


@router.post("/suppliers", response_model=SupplierResponse)
async def create_supplier(request: CreateSupplierRequest):
    """Create a new supplier"""
    
    existing_supplier = await Supplier.find_one(Supplier.supplier_id == request.supplier_id)
    if existing_supplier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Supplier ID already exists"
        )
    
    supplier = Supplier(**request.dict())
    await supplier.insert()
    
    return SupplierResponse(
        id=str(supplier.id),
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        contact_person=supplier.contact_person,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        city=supplier.city,
        country=supplier.country,
        supplied_fuel_types=supplier.supplied_fuel_types,
        supplied_lubricant_brands=supplier.supplied_lubricant_brands,
        rating=supplier.rating,
        total_deliveries=supplier.total_deliveries,
        on_time_delivery_rate=supplier.on_time_delivery_rate,
        payment_terms=supplier.payment_terms,
        credit_limit=supplier.credit_limit,
        status=supplier.status.value,
        tin_number=supplier.tin_number,
        notes=supplier.notes
    )


@router.get("/suppliers", response_model=List[SupplierResponse])
async def get_suppliers(skip: int = 0, limit: int = 100, status: Optional[SupplierStatus] = None):
    """Get all suppliers with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    suppliers = await Supplier.find(query).skip(skip).limit(limit).to_list()
    
    return [
        SupplierResponse(
            id=str(s.id),
            supplier_id=s.supplier_id,
            supplier_name=s.supplier_name,
            contact_person=s.contact_person,
            phone=s.phone,
            email=s.email,
            address=s.address,
            city=s.city,
            country=s.country,
            supplied_fuel_types=s.supplied_fuel_types,
            supplied_lubricant_brands=s.supplied_lubricant_brands,
            rating=s.rating,
            total_deliveries=s.total_deliveries,
            on_time_delivery_rate=s.on_time_delivery_rate,
            payment_terms=s.payment_terms,
            credit_limit=s.credit_limit,
            status=s.status.value,
            tin_number=s.tin_number,
            notes=s.notes
        )
        for s in suppliers
    ]


@router.get("/suppliers/{supplier_id}", response_model=SupplierResponse)
async def get_supplier(supplier_id: str):
    """Get a specific supplier"""
    
    supplier = await Supplier.find_one(Supplier.supplier_id == supplier_id)
    
    if not supplier:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Supplier not found"
        )
    
    return SupplierResponse(
        id=str(supplier.id),
        supplier_id=supplier.supplier_id,
        supplier_name=supplier.supplier_name,
        contact_person=supplier.contact_person,
        phone=supplier.phone,
        email=supplier.email,
        address=supplier.address,
        city=supplier.city,
        country=supplier.country,
        supplied_fuel_types=supplier.supplied_fuel_types,
        supplied_lubricant_brands=supplier.supplied_lubricant_brands,
        rating=supplier.rating,
        total_deliveries=supplier.total_deliveries,
        on_time_delivery_rate=supplier.on_time_delivery_rate,
        payment_terms=supplier.payment_terms,
        credit_limit=supplier.credit_limit,
        status=supplier.status.value,
        tin_number=supplier.tin_number,
        notes=supplier.notes
    )


@router.post("/delivery-schedules", response_model=DeliveryScheduleResponse)
async def create_delivery_schedule(request: CreateDeliveryScheduleRequest):
    """Create a new delivery schedule"""
    
    existing_schedule = await DeliverySchedule.find_one(DeliverySchedule.schedule_id == request.schedule_id)
    if existing_schedule:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Schedule ID already exists"
        )
    
    schedule = DeliverySchedule(**request.dict())
    await schedule.insert()
    
    return DeliveryScheduleResponse(
        id=str(schedule.id),
        schedule_id=schedule.schedule_id,
        tank_id=schedule.tank_id,
        fuel_type=schedule.fuel_type,
        supplier_id=schedule.supplier_id,
        scheduled_date=schedule.scheduled_date,
        requested_quantity_liters=schedule.requested_quantity_liters,
        estimated_cost=schedule.estimated_cost,
        status=schedule.status,
        confirmed_by=schedule.confirmed_by,
        confirmed_at=schedule.confirmed_at,
        actual_delivery_date=schedule.actual_delivery_date,
        actual_quantity_delivered=schedule.actual_quantity_delivered,
        delivery_notes=schedule.delivery_notes,
        purchase_order_number=schedule.purchase_order_number,
        created_by=schedule.created_by,
        created_at=schedule.created_at
    )


@router.get("/delivery-schedules", response_model=List[DeliveryScheduleResponse])
async def get_delivery_schedules(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """Get all delivery schedules with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    schedules = await DeliverySchedule.find(query).skip(skip).limit(limit).sort("scheduled_date").to_list()
    
    return [
        DeliveryScheduleResponse(
            id=str(s.id),
            schedule_id=s.schedule_id,
            tank_id=s.tank_id,
            fuel_type=s.fuel_type,
            supplier_id=s.supplier_id,
            scheduled_date=s.scheduled_date,
            requested_quantity_liters=s.requested_quantity_liters,
            estimated_cost=s.estimated_cost,
            status=s.status,
            confirmed_by=s.confirmed_by,
            confirmed_at=s.confirmed_at,
            actual_delivery_date=s.actual_delivery_date,
            actual_quantity_delivered=s.actual_quantity_delivered,
            delivery_notes=s.delivery_notes,
            purchase_order_number=s.purchase_order_number,
            created_by=s.created_by,
            created_at=s.created_at
        )
        for s in schedules
    ]


@router.put("/delivery-schedules/{schedule_id}/confirm")
async def confirm_delivery_schedule(schedule_id: str, confirmed_by: str):
    """Confirm a delivery schedule"""
    
    schedule = await DeliverySchedule.find_one(DeliverySchedule.schedule_id == schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    schedule.status = "confirmed"
    schedule.confirmed_by = confirmed_by
    schedule.confirmed_at = datetime.utcnow()
    await schedule.save()
    
    return {"message": "Delivery schedule confirmed successfully"}


@router.put("/delivery-schedules/{schedule_id}/complete")
async def complete_delivery_schedule(schedule_id: str, actual_quantity: float, delivery_notes: Optional[str] = None):
    """Mark a delivery schedule as completed"""
    
    schedule = await DeliverySchedule.find_one(DeliverySchedule.schedule_id == schedule_id)
    
    if not schedule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Schedule not found"
        )
    
    schedule.status = "delivered"
    schedule.actual_delivery_date = datetime.utcnow()
    schedule.actual_quantity_delivered = actual_quantity
    schedule.delivery_notes = delivery_notes
    await schedule.save()
    
    return {"message": "Delivery marked as completed"}
