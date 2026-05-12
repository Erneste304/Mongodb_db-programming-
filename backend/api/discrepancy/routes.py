from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.discrepancy import Discrepancy, DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus

router = APIRouter(prefix="/discrepancies", tags=["discrepancies"])


class CreateDiscrepancyRequest(BaseModel):
    discrepancy_id: str
    discrepancy_type: DiscrepancyType
    severity: DiscrepancySeverity
    tank_id: Optional[str] = None
    pump_id: Optional[str] = None
    station_id: Optional[str] = None
    description: str
    expected_amount: float
    actual_amount: float
    detected_by: str
    detection_method: str
    notes: Optional[str] = None


class DiscrepancyResponse(BaseModel):
    id: str
    discrepancy_id: str
    discrepancy_type: str
    severity: str
    tank_id: Optional[str]
    pump_id: Optional[str]
    station_id: Optional[str]
    description: str
    expected_amount: float
    actual_amount: float
    variance: float
    variance_percentage: float
    detected_date: datetime
    detected_by: str
    detection_method: str
    status: str
    investigated_by: Optional[str]
    investigation_date: Optional[datetime]
    root_cause: Optional[str]
    corrective_action: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    estimated_loss: Optional[float]
    recovered_amount: float
    notes: Optional[str]


@router.post("/", response_model=DiscrepancyResponse)
async def create_discrepancy(request: CreateDiscrepancyRequest):
    """Create a new discrepancy record"""
    
    existing_discrepancy = await Discrepancy.find_one(Discrepancy.discrepancy_id == request.discrepancy_id)
    if existing_discrepancy:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Discrepancy ID already exists"
        )
    
    variance = request.expected_amount - request.actual_amount
    variance_percentage = (variance / request.expected_amount * 100) if request.expected_amount > 0 else 0
    
    discrepancy = Discrepancy(
        discrepancy_id=request.discrepancy_id,
        discrepancy_type=request.discrepancy_type,
        severity=request.severity,
        tank_id=request.tank_id,
        pump_id=request.pump_id,
        station_id=request.station_id,
        description=request.description,
        expected_amount=request.expected_amount,
        actual_amount=request.actual_amount,
        variance=variance,
        variance_percentage=variance_percentage,
        detected_by=request.detected_by,
        detection_method=request.detection_method,
        notes=request.notes
    )
    
    await discrepancy.insert()
    
    return DiscrepancyResponse(
        id=str(discrepancy.id),
        discrepancy_id=discrepancy.discrepancy_id,
        discrepancy_type=discrepancy.discrepancy_type.value,
        severity=discrepancy.severity.value,
        tank_id=discrepancy.tank_id,
        pump_id=discrepancy.pump_id,
        station_id=discrepancy.station_id,
        description=discrepancy.description,
        expected_amount=discrepancy.expected_amount,
        actual_amount=discrepancy.actual_amount,
        variance=discrepancy.variance,
        variance_percentage=discrepancy.variance_percentage,
        detected_date=discrepancy.detected_date,
        detected_by=discrepancy.detected_by,
        detection_method=discrepancy.detection_method,
        status=discrepancy.status.value,
        investigated_by=discrepancy.investigated_by,
        investigation_date=discrepancy.investigation_date,
        root_cause=discrepancy.root_cause,
        corrective_action=discrepancy.corrective_action,
        resolved_by=discrepancy.resolved_by,
        resolved_at=discrepancy.resolved_at,
        estimated_loss=discrepancy.estimated_loss,
        recovered_amount=discrepancy.recovered_amount,
        notes=discrepancy.notes
    )


@router.get("/", response_model=List[DiscrepancyResponse])
async def get_discrepancies(skip: int = 0, limit: int = 100, status: Optional[DiscrepancyStatus] = None, severity: Optional[DiscrepancySeverity] = None):
    """Get all discrepancies with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity
    
    discrepancies = await Discrepancy.find(query).skip(skip).limit(limit).sort("-detected_date").to_list()
    
    return [
        DiscrepancyResponse(
            id=str(d.id),
            discrepancy_id=d.discrepancy_id,
            discrepancy_type=d.discrepancy_type.value,
            severity=d.severity.value,
            tank_id=d.tank_id,
            pump_id=d.pump_id,
            station_id=d.station_id,
            description=d.description,
            expected_amount=d.expected_amount,
            actual_amount=d.actual_amount,
            variance=d.variance,
            variance_percentage=d.variance_percentage,
            detected_date=d.detected_date,
            detected_by=d.detected_by,
            detection_method=d.detection_method,
            status=d.status.value,
            investigated_by=d.investigated_by,
            investigation_date=d.investigation_date,
            root_cause=d.root_cause,
            corrective_action=d.corrective_action,
            resolved_by=d.resolved_by,
            resolved_at=d.resolved_at,
            estimated_loss=d.estimated_loss,
            recovered_amount=d.recovered_amount,
            notes=d.notes
        )
        for d in discrepancies
    ]


@router.put("/{discrepancy_id}/investigate")
async def investigate_discrepancy(discrepancy_id: str, investigated_by: str, root_cause: str, corrective_action: str):
    """Investigate a discrepancy"""
    
    discrepancy = await Discrepancy.find_one(Discrepancy.discrepancy_id == discrepancy_id)
    
    if not discrepancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discrepancy not found"
        )
    
    discrepancy.status = DiscrepancyStatus.INVESTIGATING
    discrepancy.investigated_by = investigated_by
    discrepancy.investigation_date = datetime.utcnow()
    discrepancy.root_cause = root_cause
    discrepancy.corrective_action = corrective_action
    await discrepancy.save()
    
    return {"message": "Discrepancy investigation updated successfully"}


@router.put("/{discrepancy_id}/resolve")
async def resolve_discrepancy(discrepancy_id: str, resolved_by: str, recovered_amount: float = 0):
    """Resolve a discrepancy"""
    
    discrepancy = await Discrepancy.find_one(Discrepancy.discrepancy_id == discrepancy_id)
    
    if not discrepancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discrepancy not found"
        )
    
    discrepancy.status = DiscrepancyStatus.RESOLVED
    discrepancy.resolved_by = resolved_by
    discrepancy.resolved_at = datetime.utcnow()
    discrepancy.recovered_amount = recovered_amount
    await discrepancy.save()
    
    return {"message": "Discrepancy resolved successfully"}


@router.put("/{discrepancy_id}/close")
async def close_discrepancy(discrepancy_id: str):
    """Close a discrepancy"""
    
    discrepancy = await Discrepancy.find_one(Discrepancy.discrepancy_id == discrepancy_id)
    
    if not discrepancy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Discrepancy not found"
        )
    
    discrepancy.status = DiscrepancyStatus.CLOSED
    await discrepancy.save()
    
    return {"message": "Discrepancy closed successfully"}
