from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.stock_count import StockCount, StockCountItem, StockCountType, StockCountStatus

router = APIRouter(prefix="/stock-count", tags=["stock-count"])


class CreateStockCountRequest(BaseModel):
    count_id: str
    count_type: StockCountType = StockCountType.DAILY
    tank_id: Optional[str] = None
    fuel_type: Optional[str] = None
    dip_stick_reading_before: Optional[float] = None
    dip_stick_reading_after: Optional[float] = None
    electronic_meter_reading: Optional[float] = None
    system_level_liters: float
    physical_count_liters: float
    shop_items_counted: int = 0
    shop_items_with_variance: int = 0
    lubricant_items_counted: int = 0
    lubricant_items_with_variance: int = 0
    counted_by: str
    scheduled_date: datetime
    shift: str = "day"
    notes: Optional[str] = None


class StockCountResponse(BaseModel):
    id: str
    count_id: str
    count_type: str
    status: str
    tank_id: Optional[str]
    fuel_type: Optional[str]
    dip_stick_reading_before: Optional[float]
    dip_stick_reading_after: Optional[float]
    electronic_meter_reading: Optional[float]
    system_level_liters: float
    physical_count_liters: float
    variance_liters: float
    variance_percentage: float
    shop_items_counted: int
    shop_items_with_variance: int
    lubricant_items_counted: int
    lubricant_items_with_variance: int
    counted_by: str
    verified_by: Optional[str]
    scheduled_date: datetime
    completed_date: Optional[datetime]
    shift: str
    discrepancy_reason: Optional[str]
    investigation_notes: Optional[str]
    corrective_action: Optional[str]
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    notes: Optional[str]


class CreateStockCountItemRequest(BaseModel):
    item_count_id: str
    count_id: str
    item_type: str
    item_id: str
    item_name: str
    system_quantity: float
    physical_quantity: float
    unit_of_measure: str = "liters"
    location: Optional[str] = None
    batch_number: Optional[str] = None
    expiry_date: Optional[datetime] = None
    discrepancy_reason: Optional[str] = None


class StockCountItemResponse(BaseModel):
    id: str
    item_count_id: str
    count_id: str
    item_type: str
    item_id: str
    item_name: str
    system_quantity: float
    physical_quantity: float
    variance: float
    unit_of_measure: str
    location: Optional[str]
    batch_number: Optional[str]
    expiry_date: Optional[datetime]
    has_discrepancy: bool
    discrepancy_reason: Optional[str]


@router.post("/counts", response_model=StockCountResponse)
async def create_stock_count(request: CreateStockCountRequest):
    """Create a new stock count"""
    
    existing_count = await StockCount.find_one(StockCount.count_id == request.count_id)
    if existing_count:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Count ID already exists"
        )
    
    variance = request.physical_count_liters - request.system_level_liters
    variance_percentage = (variance / request.system_level_liters * 100) if request.system_level_liters > 0 else 0
    
    count = StockCount(
        count_id=request.count_id,
        count_type=request.count_type,
        status=StockCountStatus.IN_PROGRESS,
        tank_id=request.tank_id,
        fuel_type=request.fuel_type,
        dip_stick_reading_before=request.dip_stick_reading_before,
        dip_stick_reading_after=request.dip_stick_reading_after,
        electronic_meter_reading=request.electronic_meter_reading,
        system_level_liters=request.system_level_liters,
        physical_count_liters=request.physical_count_liters,
        variance_liters=variance,
        variance_percentage=variance_percentage,
        shop_items_counted=request.shop_items_counted,
        shop_items_with_variance=request.shop_items_with_variance,
        lubricant_items_counted=request.lubricant_items_counted,
        lubricant_items_with_variance=request.lubricant_items_with_variance,
        counted_by=request.counted_by,
        scheduled_date=request.scheduled_date,
        shift=request.shift,
        notes=request.notes
    )
    
    await count.insert()
    
    return StockCountResponse(
        id=str(count.id),
        count_id=count.count_id,
        count_type=count.count_type.value,
        status=count.status.value,
        tank_id=count.tank_id,
        fuel_type=count.fuel_type,
        dip_stick_reading_before=count.dip_stick_reading_before,
        dip_stick_reading_after=count.dip_stick_reading_after,
        electronic_meter_reading=count.electronic_meter_reading,
        system_level_liters=count.system_level_liters,
        physical_count_liters=count.physical_count_liters,
        variance_liters=count.variance_liters,
        variance_percentage=count.variance_percentage,
        shop_items_counted=count.shop_items_counted,
        shop_items_with_variance=count.shop_items_with_variance,
        lubricant_items_counted=count.lubricant_items_counted,
        lubricant_items_with_variance=count.lubricant_items_with_variance,
        counted_by=count.counted_by,
        verified_by=count.verified_by,
        scheduled_date=count.scheduled_date,
        completed_date=count.completed_date,
        shift=count.shift,
        discrepancy_reason=count.discrepancy_reason,
        investigation_notes=count.investigation_notes,
        corrective_action=count.corrective_action,
        approved_by=count.approved_by,
        approved_at=count.approved_at,
        notes=count.notes
    )


@router.get("/counts", response_model=List[StockCountResponse])
async def get_stock_counts(skip: int = 0, limit: int = 100, tank_id: Optional[str] = None, status: Optional[StockCountStatus] = None):
    """Get all stock counts with optional filtering"""
    
    query = {}
    if tank_id:
        query["tank_id"] = tank_id
    if status:
        query["status"] = status
    
    counts = await StockCount.find(query).skip(skip).limit(limit).sort("-scheduled_date").to_list()
    
    return [
        StockCountResponse(
            id=str(c.id),
            count_id=c.count_id,
            count_type=c.count_type.value,
            status=c.status.value,
            tank_id=c.tank_id,
            fuel_type=c.fuel_type,
            dip_stick_reading_before=c.dip_stick_reading_before,
            dip_stick_reading_after=c.dip_stick_reading_after,
            electronic_meter_reading=c.electronic_meter_reading,
            system_level_liters=c.system_level_liters,
            physical_count_liters=c.physical_count_liters,
            variance_liters=c.variance_liters,
            variance_percentage=c.variance_percentage,
            shop_items_counted=c.shop_items_counted,
            shop_items_with_variance=c.shop_items_with_variance,
            lubricant_items_counted=c.lubricant_items_counted,
            lubricant_items_with_variance=c.lubricant_items_with_variance,
            counted_by=c.counted_by,
            verified_by=c.verified_by,
            scheduled_date=c.scheduled_date,
            completed_date=c.completed_date,
            shift=c.shift,
            discrepancy_reason=c.discrepancy_reason,
            investigation_notes=c.investigation_notes,
            corrective_action=c.corrective_action,
            approved_by=c.approved_by,
            approved_at=c.approved_at,
            notes=c.notes
        )
        for c in counts
    ]


@router.put("/counts/{count_id}/complete")
async def complete_stock_count(count_id: str, verified_by: str):
    """Complete a stock count"""
    
    count = await StockCount.find_one(StockCount.count_id == count_id)
    
    if not count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Count not found"
        )
    
    count.status = StockCountStatus.COMPLETED
    count.completed_date = datetime.utcnow()
    count.verified_by = verified_by
    await count.save()
    
    return {"message": "Stock count completed successfully"}


@router.post("/items", response_model=StockCountItemResponse)
async def create_stock_count_item(request: CreateStockCountItemRequest):
    """Create a stock count item"""
    
    existing_item = await StockCountItem.find_one(StockCountItem.item_count_id == request.item_count_id)
    if existing_item:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Item count ID already exists"
        )
    
    variance = request.physical_quantity - request.system_quantity
    has_discrepancy = abs(variance) > 0.01  # Small tolerance
    
    item = StockCountItem(
        item_count_id=request.item_count_id,
        count_id=request.count_id,
        item_type=request.item_type,
        item_id=request.item_id,
        item_name=request.item_name,
        system_quantity=request.system_quantity,
        physical_quantity=request.physical_quantity,
        variance=variance,
        unit_of_measure=request.unit_of_measure,
        location=request.location,
        batch_number=request.batch_number,
        expiry_date=request.expiry_date,
        has_discrepancy=has_discrepancy,
        discrepancy_reason=request.discrepancy_reason
    )
    
    await item.insert()
    
    return StockCountItemResponse(
        id=str(item.id),
        item_count_id=item.item_count_id,
        count_id=item.count_id,
        item_type=item.item_type,
        item_id=item.item_id,
        item_name=item.item_name,
        system_quantity=item.system_quantity,
        physical_quantity=item.physical_quantity,
        variance=item.variance,
        unit_of_measure=item.unit_of_measure,
        location=item.location,
        batch_number=item.batch_number,
        expiry_date=item.expiry_date,
        has_discrepancy=item.has_discrepancy,
        discrepancy_reason=item.discrepancy_reason
    )


@router.get("/items", response_model=List[StockCountItemResponse])
async def get_stock_count_items(skip: int = 0, limit: int = 100, count_id: Optional[str] = None):
    """Get all stock count items with optional filtering"""
    
    query = {}
    if count_id:
        query["count_id"] = count_id
    
    items = await StockCountItem.find(query).skip(skip).limit(limit).to_list()
    
    return [
        StockCountItemResponse(
            id=str(i.id),
            item_count_id=i.item_count_id,
            count_id=i.count_id,
            item_type=i.item_type,
            item_id=i.item_id,
            item_name=i.item_name,
            system_quantity=i.system_quantity,
            physical_quantity=i.physical_quantity,
            variance=i.variance,
            unit_of_measure=i.unit_of_measure,
            location=i.location,
            batch_number=i.batch_number,
            expiry_date=i.expiry_date,
            has_discrepancy=i.has_discrepancy,
            discrepancy_reason=i.discrepancy_reason
        )
        for i in items
    ]
