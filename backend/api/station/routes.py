from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.station import Station, StationStatus

router = APIRouter(prefix="/stations", tags=["stations"])


class CreateStationRequest(BaseModel):
    station_id: str
    name: str
    location: str
    address: str
    city: str
    district: str
    manager_name: str
    manager_phone: str
    manager_email: str
    opening_time: str = "06:00"
    closing_time: str = "22:00"
    total_tank_capacity: float = 0
    number_of_pumps: int = 0
    number_of_tanks: int = 0
    monthly_revenue_target: Optional[float] = None
    rura_license_number: Optional[str] = None
    rura_license_expiry: Optional[datetime] = None


class StationResponse(BaseModel):
    id: str
    station_id: str
    name: str
    location: str
    address: str
    city: str
    district: str
    manager_name: str
    manager_phone: str
    manager_email: str
    status: str
    opening_time: str
    closing_time: str
    total_tank_capacity: float
    number_of_pumps: int
    number_of_tanks: int
    monthly_revenue_target: Optional[float]
    current_month_revenue: float
    staff_count: int
    rura_license_number: Optional[str]
    rura_license_expiry: Optional[datetime]
    is_active: bool


@router.post("/", response_model=StationResponse)
async def create_station(request: CreateStationRequest):
    """Create a new station"""
    
    existing_station = await Station.find_one(Station.station_id == request.station_id)
    if existing_station:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Station ID already exists"
        )
    
    station = Station(**request.dict())
    await station.insert()
    
    return StationResponse(
        id=str(station.id),
        station_id=station.station_id,
        name=station.name,
        location=station.location,
        address=station.address,
        city=station.city,
        district=station.district,
        manager_name=station.manager_name,
        manager_phone=station.manager_phone,
        manager_email=station.manager_email,
        status=station.status.value,
        opening_time=station.opening_time,
        closing_time=station.closing_time,
        total_tank_capacity=station.total_tank_capacity,
        number_of_pumps=station.number_of_pumps,
        number_of_tanks=station.number_of_tanks,
        monthly_revenue_target=station.monthly_revenue_target,
        current_month_revenue=station.current_month_revenue,
        staff_count=station.staff_count,
        rura_license_number=station.rura_license_number,
        rura_license_expiry=station.rura_license_expiry,
        is_active=station.is_active
    )


@router.get("/", response_model=List[StationResponse])
async def get_stations(skip: int = 0, limit: int = 100, status: Optional[StationStatus] = None):
    """Get all stations with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    stations = await Station.find(query).skip(skip).limit(limit).to_list()
    
    return [
        StationResponse(
            id=str(s.id),
            station_id=s.station_id,
            name=s.name,
            location=s.location,
            address=s.address,
            city=s.city,
            district=s.district,
            manager_name=s.manager_name,
            manager_phone=s.manager_phone,
            manager_email=s.manager_email,
            status=s.status.value,
            opening_time=s.opening_time,
            closing_time=s.closing_time,
            total_tank_capacity=s.total_tank_capacity,
            number_of_pumps=s.number_of_pumps,
            number_of_tanks=s.number_of_tanks,
            monthly_revenue_target=s.monthly_revenue_target,
            current_month_revenue=s.current_month_revenue,
            staff_count=s.staff_count,
            rura_license_number=s.rura_license_number,
            rura_license_expiry=s.rura_license_expiry,
            is_active=s.is_active
        )
        for s in stations
    ]


@router.get("/{station_id}", response_model=StationResponse)
async def get_station(station_id: str):
    """Get a specific station"""
    
    station = await Station.find_one(Station.station_id == station_id)
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    return StationResponse(
        id=str(station.id),
        station_id=station.station_id,
        name=station.name,
        location=station.location,
        address=station.address,
        city=station.city,
        district=station.district,
        manager_name=station.manager_name,
        manager_phone=station.manager_phone,
        manager_email=station.manager_email,
        status=station.status.value,
        opening_time=station.opening_time,
        closing_time=station.closing_time,
        total_tank_capacity=station.total_tank_capacity,
        number_of_pumps=station.number_of_pumps,
        number_of_tanks=station.number_of_tanks,
        monthly_revenue_target=station.monthly_revenue_target,
        current_month_revenue=station.current_month_revenue,
        staff_count=station.staff_count,
        rura_license_number=station.rura_license_number,
        rura_license_expiry=station.rura_license_expiry,
        is_active=station.is_active
    )


@router.put("/{station_id}/status")
async def update_station_status(station_id: str, status: StationStatus):
    """Update station status"""
    
    station = await Station.find_one(Station.station_id == station_id)
    
    if not station:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Station not found"
        )
    
    station.status = status
    station.updated_at = datetime.utcnow()
    await station.save()
    
    return {"message": "Station status updated successfully"}
