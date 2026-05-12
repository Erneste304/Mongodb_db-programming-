from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.consumption import ConsumptionRecord, ReorderPrediction, ConsumptionPeriod

router = APIRouter(prefix="/consumption", tags=["consumption"])


class CreateConsumptionRecordRequest(BaseModel):
    record_id: str
    tank_id: str
    fuel_type: str
    period: ConsumptionPeriod = ConsumptionPeriod.DAILY
    start_date: datetime
    end_date: datetime
    opening_level_liters: float
    closing_level_liters: float
    dispensed_liters: float = 0
    deliveries_liters: float = 0
    recorded_by: str


class ConsumptionRecordResponse(BaseModel):
    id: str
    record_id: str
    tank_id: str
    fuel_type: str
    period: str
    start_date: datetime
    end_date: datetime
    opening_level_liters: float
    closing_level_liters: float
    dispensed_liters: float
    deliveries_liters: float
    net_consumption_liters: float
    consumption_rate_liters_per_day: float
    average_daily_consumption: float
    estimated_days_until_empty: float
    recommended_reorder_date: Optional[datetime]
    recommended_reorder_quantity_liters: float


class ReorderPredictionResponse(BaseModel):
    id: str
    prediction_id: str
    tank_id: str
    fuel_type: str
    current_level_liters: float
    capacity_liters: float
    current_fill_percentage: float
    predicted_consumption_rate: float
    estimated_days_until_empty: float
    estimated_empty_date: datetime
    recommended_reorder_date: datetime
    recommended_reorder_quantity_liters: float
    urgency_level: str
    suggested_supplier: Optional[str]
    estimated_lead_time_days: int


@router.post("/records", response_model=ConsumptionRecordResponse)
async def create_consumption_record(request: CreateConsumptionRecordRequest):
    """Create a new consumption record"""
    
    existing_record = await ConsumptionRecord.find_one(ConsumptionRecord.record_id == request.record_id)
    if existing_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Record ID already exists"
        )
    
    # Calculate consumption
    net_consumption = request.opening_level_liters + request.deliveries_liters - request.closing_level_liters
    days = (request.end_date - request.start_date).days or 1
    consumption_rate = net_consumption / days
    
    record = ConsumptionRecord(
        record_id=request.record_id,
        tank_id=request.tank_id,
        fuel_type=request.fuel_type,
        period=request.period,
        start_date=request.start_date,
        end_date=request.end_date,
        opening_level_liters=request.opening_level_liters,
        closing_level_liters=request.closing_level_liters,
        dispensed_liters=request.dispensed_liters,
        deliveries_liters=request.deliveries_liters,
        net_consumption_liters=net_consumption,
        consumption_rate_liters_per_day=consumption_rate,
        average_daily_consumption=consumption_rate,
        recorded_by=request.recorded_by
    )
    
    await record.insert()
    
    return ConsumptionRecordResponse(
        id=str(record.id),
        record_id=record.record_id,
        tank_id=record.tank_id,
        fuel_type=record.fuel_type,
        period=record.period.value,
        start_date=record.start_date,
        end_date=record.end_date,
        opening_level_liters=record.opening_level_liters,
        closing_level_liters=record.closing_level_liters,
        dispensed_liters=record.dispensed_liters,
        deliveries_liters=record.deliveries_liters,
        net_consumption_liters=record.net_consumption_liters,
        consumption_rate_liters_per_day=record.consumption_rate_liters_per_day,
        average_daily_consumption=record.average_daily_consumption,
        estimated_days_until_empty=record.estimated_days_until_empty,
        recommended_reorder_date=record.recommended_reorder_date,
        recommended_reorder_quantity_liters=record.recommended_reorder_quantity_liters
    )


@router.get("/records", response_model=List[ConsumptionRecordResponse])
async def get_consumption_records(skip: int = 0, limit: int = 100, tank_id: Optional[str] = None):
    """Get all consumption records with optional filtering"""
    
    query = {}
    if tank_id:
        query["tank_id"] = tank_id
    
    records = await ConsumptionRecord.find(query).skip(skip).limit(limit).sort("-start_date").to_list()
    
    return [
        ConsumptionRecordResponse(
            id=str(r.id),
            record_id=r.record_id,
            tank_id=r.tank_id,
            fuel_type=r.fuel_type,
            period=r.period.value,
            start_date=r.start_date,
            end_date=r.end_date,
            opening_level_liters=r.opening_level_liters,
            closing_level_liters=r.closing_level_liters,
            dispensed_liters=r.dispensed_liters,
            deliveries_liters=r.deliveries_liters,
            net_consumption_liters=r.net_consumption_liters,
            consumption_rate_liters_per_day=r.consumption_rate_liters_per_day,
            average_daily_consumption=r.average_daily_consumption,
            estimated_days_until_empty=r.estimated_days_until_empty,
            recommended_reorder_date=r.recommended_reorder_date,
            recommended_reorder_quantity_liters=r.recommended_reorder_quantity_liters
        )
        for r in records
    ]


@router.post("/predictions", response_model=ReorderPredictionResponse)
async def create_reorder_prediction(tank_id: str):
    """Generate reorder prediction for a tank"""
    from backend.models.inventory import Tank
    
    tank = await Tank.find_one(Tank.tank_id == tank_id)
    if not tank:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tank not found"
        )
    
    # Get recent consumption records
    recent_records = await ConsumptionRecord.find(
        ConsumptionRecord.tank_id == tank_id
    ).sort("-start_date").limit(7).to_list()
    
    if not recent_records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Insufficient consumption data for prediction"
        )
    
    # Calculate average consumption rate
    avg_consumption = sum(r.consumption_rate_liters_per_day for r in recent_records) / len(recent_records)
    
    # Calculate predictions
    current_fill = (tank.current_level_liters / tank.capacity_liters) * 100
    days_until_empty = tank.current_level_liters / avg_consumption if avg_consumption > 0 else 0
    estimated_empty_date = datetime.utcnow() + datetime.timedelta(days=days_until_empty)
    
    # Reorder recommendation (when at 30%)
    reorder_level = tank.capacity_liters * 0.3
    days_to_reorder = (tank.current_level_liters - reorder_level) / avg_consumption if avg_consumption > 0 else 0
    recommended_reorder_date = datetime.utcnow() + datetime.timedelta(days=days_to_reorder)
    
    # Determine urgency
    if current_fill < 20:
        urgency = "critical"
    elif current_fill < 30:
        urgency = "high"
    elif current_fill < 50:
        urgency = "normal"
    else:
        urgency = "low"
    
    prediction = ReorderPrediction(
        prediction_id=f"PRED-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}",
        tank_id=tank.tank_id,
        fuel_type=tank.fuel_type.value,
        current_level_liters=tank.current_level_liters,
        capacity_liters=tank.capacity_liters,
        current_fill_percentage=current_fill,
        predicted_consumption_rate=avg_consumption,
        estimated_days_until_empty=days_until_empty,
        estimated_empty_date=estimated_empty_date,
        recommended_reorder_date=recommended_reorder_date,
        recommended_reorder_quantity_liters=tank.capacity_liters * 0.7,
        urgency_level=urgency,
        estimated_lead_time_days=3,
        valid_until=datetime.utcnow() + datetime.timedelta(days=7)
    )
    
    await prediction.insert()
    
    return ReorderPredictionResponse(
        id=str(prediction.id),
        prediction_id=prediction.prediction_id,
        tank_id=prediction.tank_id,
        fuel_type=prediction.fuel_type,
        current_level_liters=prediction.current_level_liters,
        capacity_liters=prediction.capacity_liters,
        current_fill_percentage=prediction.current_fill_percentage,
        predicted_consumption_rate=prediction.predicted_consumption_rate,
        estimated_days_until_empty=prediction.estimated_days_until_empty,
        estimated_empty_date=prediction.estimated_empty_date,
        recommended_reorder_date=prediction.recommended_reorder_date,
        recommended_reorder_quantity_liters=prediction.recommended_reorder_quantity_liters,
        urgency_level=prediction.urgency_level,
        suggested_supplier=prediction.suggested_supplier,
        estimated_lead_time_days=prediction.estimated_lead_time_days
    )


@router.get("/predictions", response_model=List[ReorderPredictionResponse])
async def get_reorder_predictions(skip: int = 0, limit: int = 100):
    """Get all reorder predictions"""
    
    predictions = await ReorderPrediction.find_all().skip(skip).limit(limit).sort("-created_at").to_list()
    
    return [
        ReorderPredictionResponse(
            id=str(p.id),
            prediction_id=p.prediction_id,
            tank_id=p.tank_id,
            fuel_type=p.fuel_type,
            current_level_liters=p.current_level_liters,
            capacity_liters=p.capacity_liters,
            current_fill_percentage=p.current_fill_percentage,
            predicted_consumption_rate=p.predicted_consumption_rate,
            estimated_days_until_empty=p.estimated_days_until_empty,
            estimated_empty_date=p.estimated_empty_date,
            recommended_reorder_date=p.recommended_reorder_date,
            recommended_reorder_quantity_liters=p.recommended_reorder_quantity_liters,
            urgency_level=p.urgency_level,
            suggested_supplier=p.suggested_supplier,
            estimated_lead_time_days=p.estimated_lead_time_days
        )
        for p in predictions
    ]
