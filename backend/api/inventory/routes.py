from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.inventory import Tank, FuelDelivery, InventoryRecord, FuelType, TankStatus, DeliveryStatus
from backend.services.inventory_analysis import InventoryAnalysisService
from backend.services.audit_service import AuditLogService
from backend.models.user import User

router = APIRouter(prefix="/inventory", tags=["inventory"])


class CreateTankRequest(BaseModel):
    tank_id: str
    tank_number: str
    fuel_type: FuelType
    capacity_liters: float
    threshold_alert_percent: float = 20
    calibration_certificate_number: Optional[str] = None
    calibration_expiry_date: Optional[datetime] = None
    station_id: Optional[str] = None


class UpdateTankRequest(BaseModel):
    current_level_liters: Optional[float] = None
    status: Optional[TankStatus] = None
    calibration_certificate_number: Optional[str] = None
    calibration_expiry_date: Optional[datetime] = None


class TankResponse(BaseModel):
    id: str
    tank_id: str
    tank_number: str
    fuel_type: str
    capacity_liters: float
    current_level_liters: float
    threshold_alert_percent: float
    status: str
    calibration_certificate_number: Optional[str]
    calibration_expiry_date: Optional[datetime]
    station_id: Optional[str]


class CreateFuelDeliveryRequest(BaseModel):
    delivery_id: str
    tank_id: str
    supplier_name: str
    supplier_invoice_number: str
    fuel_type: FuelType
    quantity_delivered_liters: float
    dip_stick_reading_before: Optional[float] = None
    price_per_liter: float
    delivered_by: str
    notes: Optional[str] = None


class VerifyDeliveryRequest(BaseModel):
    quantity_verified_liters: float
    dip_stick_reading_after: Optional[float] = None
    verified_by: str


class FuelDeliveryResponse(BaseModel):
    id: str
    delivery_id: str
    tank_id: str
    supplier_name: str
    supplier_invoice_number: str
    fuel_type: str
    quantity_delivered_liters: float
    quantity_verified_liters: Optional[float]
    price_per_liter: float
    total_cost: float
    delivery_date: datetime
    delivered_by: str
    verified_by: Optional[str]
    status: str


class CreateInventoryRecordRequest(BaseModel):
    record_id: str
    tank_id: str
    fuel_type: FuelType
    opening_level_liters: float
    closing_level_liters: float
    dispensed_liters: float = 0
    deliveries_liters: float = 0
    recorded_by: str
    shift: str = "day"
    notes: Optional[str] = None


class InventoryRecordResponse(BaseModel):
    id: str
    record_id: str
    tank_id: str
    fuel_type: str
    opening_level_liters: float
    closing_level_liters: float
    dispensed_liters: float
    deliveries_liters: float
    recorded_by: str
    record_date: datetime
    shift: str


@router.post("/tanks", response_model=TankResponse)
async def create_tank(request: CreateTankRequest):
    """Create a new fuel tank"""
    
    existing_tank = await Tank.find_one(Tank.tank_id == request.tank_id)
    if existing_tank:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tank ID already exists"
        )
    
    tank = Tank(**request.dict())
    await tank.insert()
    
    return TankResponse(
        id=str(tank.id),
        tank_id=tank.tank_id,
        tank_number=tank.tank_number,
        fuel_type=tank.fuel_type.value,
        capacity_liters=tank.capacity_liters,
        current_level_liters=tank.current_level_liters,
        threshold_alert_percent=tank.threshold_alert_percent,
        status=tank.status.value,
        calibration_certificate_number=tank.calibration_certificate_number,
        calibration_expiry_date=tank.calibration_expiry_date,
        station_id=tank.station_id
    )


@router.get("/tanks", response_model=List[TankResponse])
async def get_tanks(skip: int = 0, limit: int = 100, fuel_type: Optional[FuelType] = None):
    """Get all tanks with optional filtering"""
    
    query = {}
    if fuel_type:
        query["fuel_type"] = fuel_type
    
    tanks = await Tank.find(query).skip(skip).limit(limit).to_list()
    
    return [
        TankResponse(
            id=str(tank.id),
            tank_id=tank.tank_id,
            tank_number=tank.tank_number,
            fuel_type=tank.fuel_type.value,
            capacity_liters=tank.capacity_liters,
            current_level_liters=tank.current_level_liters,
            threshold_alert_percent=tank.threshold_alert_percent,
            status=tank.status.value,
            calibration_certificate_number=tank.calibration_certificate_number,
            calibration_expiry_date=tank.calibration_expiry_date,
            station_id=tank.station_id
        )
        for tank in tanks
    ]


@router.get("/tanks/{tank_id}", response_model=TankResponse)
async def get_tank(tank_id: str):
    """Get a specific tank"""
    
    tank = await Tank.find_one(Tank.tank_id == tank_id)
    
    if not tank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tank not found"
        )
    
    return TankResponse(
        id=str(tank.id),
        tank_id=tank.tank_id,
        tank_number=tank.tank_number,
        fuel_type=tank.fuel_type.value,
        capacity_liters=tank.capacity_liters,
        current_level_liters=tank.current_level_liters,
        threshold_alert_percent=tank.threshold_alert_percent,
        status=tank.status.value,
        calibration_certificate_number=tank.calibration_certificate_number,
        calibration_expiry_date=tank.calibration_expiry_date,
        station_id=tank.station_id
    )


@router.patch("/tanks/{tank_id}", response_model=TankResponse)
async def update_tank(tank_id: str, request: UpdateTankRequest):
    """Update tank information"""
    
    tank = await Tank.find_one(Tank.tank_id == tank_id)
    
    if not tank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tank not found"
        )
    
    if request.current_level_liters is not None:
        tank.current_level_liters = request.current_level_liters
    if request.status is not None:
        tank.status = request.status
    if request.calibration_certificate_number is not None:
        tank.calibration_certificate_number = request.calibration_certificate_number
    if request.calibration_expiry_date is not None:
        tank.calibration_expiry_date = request.calibration_expiry_date
    
    tank.updated_at = datetime.utcnow()
    await tank.save()
    
    return TankResponse(
        id=str(tank.id),
        tank_id=tank.tank_id,
        tank_number=tank.tank_number,
        fuel_type=tank.fuel_type.value,
        capacity_liters=tank.capacity_liters,
        current_level_liters=tank.current_level_liters,
        threshold_alert_percent=tank.threshold_alert_percent,
        status=tank.status.value,
        calibration_certificate_number=tank.calibration_certificate_number,
        calibration_expiry_date=tank.calibration_expiry_date,
        station_id=tank.station_id
    )


@router.post("/deliveries", response_model=FuelDeliveryResponse)
async def create_fuel_delivery(request: CreateFuelDeliveryRequest):
    """Create a new fuel delivery record"""
    
    existing_delivery = await FuelDelivery.find_one(FuelDelivery.delivery_id == request.delivery_id)
    if existing_delivery:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery ID already exists"
        )
    
    # Calculate total cost
    total_cost = request.quantity_delivered_liters * request.price_per_liter
    
    delivery = FuelDelivery(
        delivery_id=request.delivery_id,
        tank_id=request.tank_id,
        supplier_name=request.supplier_name,
        supplier_invoice_number=request.supplier_invoice_number,
        fuel_type=request.fuel_type,
        quantity_delivered_liters=request.quantity_delivered_liters,
        dip_stick_reading_before=request.dip_stick_reading_before,
        price_per_liter=request.price_per_liter,
        total_cost=total_cost,
        delivered_by=request.delivered_by,
        notes=request.notes,
        status=DeliveryStatus.PENDING
    )
    
    await delivery.insert()
    
    return FuelDeliveryResponse(
        id=str(delivery.id),
        delivery_id=delivery.delivery_id,
        tank_id=delivery.tank_id,
        supplier_name=delivery.supplier_name,
        supplier_invoice_number=delivery.supplier_invoice_number,
        fuel_type=delivery.fuel_type.value,
        quantity_delivered_liters=delivery.quantity_delivered_liters,
        quantity_verified_liters=delivery.quantity_verified_liters,
        price_per_liter=delivery.price_per_liter,
        total_cost=delivery.total_cost,
        delivery_date=delivery.delivery_date,
        delivered_by=delivery.delivered_by,
        verified_by=delivery.verified_by,
        status=delivery.status.value
    )


@router.get("/deliveries", response_model=List[FuelDeliveryResponse])
async def get_fuel_deliveries(skip: int = 0, limit: int = 100, status: Optional[DeliveryStatus] = None):
    """Get all fuel deliveries with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    deliveries = await FuelDelivery.find(query).skip(skip).limit(limit).sort(-FuelDelivery.delivery_date).to_list()
    
    return [
        FuelDeliveryResponse(
            id=str(delivery.id),
            delivery_id=delivery.delivery_id,
            tank_id=delivery.tank_id,
            supplier_name=delivery.supplier_name,
            supplier_invoice_number=delivery.supplier_invoice_number,
            fuel_type=delivery.fuel_type.value,
            quantity_delivered_liters=delivery.quantity_delivered_liters,
            quantity_verified_liters=delivery.quantity_verified_liters,
            price_per_liter=delivery.price_per_liter,
            total_cost=delivery.total_cost,
            delivery_date=delivery.delivery_date,
            delivered_by=delivery.delivered_by,
            verified_by=delivery.verified_by,
            status=delivery.status.value
        )
        for delivery in deliveries
    ]


@router.post("/deliveries/{delivery_id}/verify")
async def verify_fuel_delivery(delivery_id: str, request: VerifyDeliveryRequest):
    """Verify a fuel delivery"""
    
    delivery = await FuelDelivery.find_one(FuelDelivery.delivery_id == delivery_id)
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    if delivery.status != DeliveryStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Delivery cannot be verified"
        )
    
    delivery.quantity_verified_liters = request.quantity_verified_liters
    delivery.dip_stick_reading_after = request.dip_stick_reading_after
    delivery.verified_by = request.verified_by
    delivery.status = DeliveryStatus.VERIFIED
    await delivery.save()
    
    # Update tank level
    tank = await Tank.find_one(Tank.tank_id == delivery.tank_id)
    if tank:
        tank.current_level_liters += request.quantity_verified_liters
        tank.updated_at = datetime.utcnow()
        await tank.save()
    
    return {"message": "Delivery verified successfully"}


@router.post("/records", response_model=InventoryRecordResponse)
async def create_inventory_record(request: CreateInventoryRecordRequest):
    """Create an inventory record"""
    
    existing_record = await InventoryRecord.find_one(InventoryRecord.record_id == request.record_id)
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Record ID already exists"
        )
    
    record = InventoryRecord(**request.dict())
    
    # 2. Run Theft/Leakage Analysis (Innovation)
    analysis = await InventoryAnalysisService.analyze_shift_variance(request.tank_id, record)
    
    # Apply analysis results to record
    record.variance_liters = analysis["variance_liters"]
    record.variance_percent = analysis["variance_percent"]
    record.is_anomaly = analysis["is_anomaly"]
    record.anomaly_type = analysis["anomaly_type"]
    record.anomaly_severity = analysis["severity"]
    
    await record.insert()
    
    # 3. Alert Admin if Anomaly detected
    if record.is_anomaly:
        # await NotificationService.send_alert(...)
        pass
    
    return InventoryRecordResponse(
        id=str(record.id),
        record_id=record.record_id,
        tank_id=record.tank_id,
        fuel_type=record.fuel_type.value,
        opening_level_liters=record.opening_level_liters,
        closing_level_liters=record.closing_level_liters,
        dispensed_liters=record.dispensed_liters,
        deliveries_liters=record.deliveries_liters,
        recorded_by=record.recorded_by,
        record_date=record.record_date,
        shift=record.shift
    )


@router.get("/records", response_model=List[InventoryRecordResponse])
async def get_inventory_records(skip: int = 0, limit: int = 100, tank_id: Optional[str] = None):
    """Get all inventory records with optional filtering"""
    
    query = {}
    if tank_id:
        query["tank_id"] = tank_id
    
    records = await InventoryRecord.find(query).skip(skip).limit(limit).sort(-InventoryRecord.record_date).to_list()
    
    return [
        InventoryRecordResponse(
            id=str(record.id),
            record_id=record.record_id,
            tank_id=record.tank_id,
            fuel_type=record.fuel_type.value,
            opening_level_liters=record.opening_level_liters,
            closing_level_liters=record.closing_level_liters,
            dispensed_liters=record.dispensed_liters,
            deliveries_liters=record.deliveries_liters,
            recorded_by=record.recorded_by,
            record_date=record.record_date,
            shift=record.shift
        )
        for record in records
    ]
