from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.safety import SafetyCheck, SafetyIncident, SafetyCheckType, SafetyStatus

router = APIRouter(prefix="/safety", tags=["safety"])


class CreateSafetyCheckRequest(BaseModel):
    check_id: str
    check_type: SafetyCheckType
    tank_id: Optional[str] = None
    station_id: str
    fire_extinguishers_operational: bool = False
    spill_kit_available: bool = False
    emergency_exits_clear: bool = False
    no_smoking_signs_visible: bool = False
    lighting_functional: bool = False
    ventilation_working: bool = False
    tank_leaks_detected: bool = False
    pipe_connections_secure: bool = False
    grounding_system_ok: bool = False
    ambient_temperature: Optional[float] = None
    tank_temperature: Optional[float] = None
    storage_area_clean: bool = False
    hazardous_materials_labeled: bool = False
    safety_data_sheets_available: bool = False
    overall_status: SafetyStatus = SafetyStatus.PENDING
    checked_by: str
    issues_found: Optional[str] = None
    corrective_actions: Optional[str] = None
    notes: Optional[str] = None


class SafetyCheckResponse(BaseModel):
    id: str
    check_id: str
    check_type: str
    tank_id: Optional[str]
    station_id: str
    fire_extinguishers_operational: bool
    spill_kit_available: bool
    emergency_exits_clear: bool
    no_smoking_signs_visible: bool
    lighting_functional: bool
    ventilation_working: bool
    tank_leaks_detected: bool
    pipe_connections_secure: bool
    grounding_system_ok: bool
    ambient_temperature: Optional[float]
    tank_temperature: Optional[float]
    storage_area_clean: bool
    hazardous_materials_labeled: bool
    safety_data_sheets_available: bool
    overall_status: str
    checked_by: str
    checked_at: datetime
    issues_found: Optional[str]
    corrective_actions: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    notes: Optional[str]


class CreateSafetyIncidentRequest(BaseModel):
    incident_id: str
    incident_type: str
    severity: str
    tank_id: Optional[str] = None
    location_description: str
    description: str
    immediate_action_taken: str
    fuel_loss_liters: Optional[float] = None
    estimated_cost: Optional[float] = None
    created_by: str
    notes: Optional[str] = None


class SafetyIncidentResponse(BaseModel):
    id: str
    incident_id: str
    incident_type: str
    severity: str
    tank_id: Optional[str]
    location_description: str
    incident_date: datetime
    description: str
    immediate_action_taken: str
    fuel_loss_liters: Optional[float]
    estimated_cost: Optional[float]
    investigated_by: Optional[str]
    investigation_date: Optional[datetime]
    root_cause: Optional[str]
    corrective_actions: Optional[str]
    resolved: bool
    resolved_at: Optional[datetime]
    reported_to_rura: bool
    rura_reference_number: Optional[str]
    created_by: str
    created_at: datetime


@router.post("/checks", response_model=SafetyCheckResponse)
async def create_safety_check(request: CreateSafetyCheckRequest):
    """Create a new safety check"""
    
    existing_check = await SafetyCheck.find_one(SafetyCheck.check_id == request.check_id)
    if existing_check:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Check ID already exists"
        )
    
    check = SafetyCheck(**request.dict())
    await check.insert()
    
    return SafetyCheckResponse(
        id=str(check.id),
        check_id=check.check_id,
        check_type=check.check_type.value,
        tank_id=check.tank_id,
        station_id=check.station_id,
        fire_extinguishers_operational=check.fire_extinguishers_operational,
        spill_kit_available=check.spill_kit_available,
        emergency_exits_clear=check.emergency_exits_clear,
        no_smoking_signs_visible=check.no_smoking_signs_visible,
        lighting_functional=check.lighting_functional,
        ventilation_working=check.ventilation_working,
        tank_leaks_detected=check.tank_leaks_detected,
        pipe_connections_secure=check.pipe_connections_secure,
        grounding_system_ok=check.grounding_system_ok,
        ambient_temperature=check.ambient_temperature,
        tank_temperature=check.tank_temperature,
        storage_area_clean=check.storage_area_clean,
        hazardous_materials_labeled=check.hazardous_materials_labeled,
        safety_data_sheets_available=check.safety_data_sheets_available,
        overall_status=check.overall_status.value,
        checked_by=check.checked_by,
        checked_at=check.checked_at,
        issues_found=check.issues_found,
        corrective_actions=check.corrective_actions,
        resolved_by=check.resolved_by,
        resolved_at=check.resolved_at,
        notes=check.notes
    )


@router.get("/checks", response_model=List[SafetyCheckResponse])
async def get_safety_checks(skip: int = 0, limit: int = 100, tank_id: Optional[str] = None, check_type: Optional[SafetyCheckType] = None):
    """Get all safety checks with optional filtering"""
    
    query = {}
    if tank_id:
        query["tank_id"] = tank_id
    if check_type:
        query["check_type"] = check_type
    
    checks = await SafetyCheck.find(query).skip(skip).limit(limit).sort("-checked_at").to_list()
    
    return [
        SafetyCheckResponse(
            id=str(c.id),
            check_id=c.check_id,
            check_type=c.check_type.value,
            tank_id=c.tank_id,
            station_id=c.station_id,
            fire_extinguishers_operational=c.fire_extinguishers_operational,
            spill_kit_available=c.spill_kit_available,
            emergency_exits_clear=c.emergency_exits_clear,
            no_smoking_signs_visible=c.no_smoking_signs_visible,
            lighting_functional=c.lighting_functional,
            ventilation_working=c.ventilation_working,
            tank_leaks_detected=c.tank_leaks_detected,
            pipe_connections_secure=c.pipe_connections_secure,
            grounding_system_ok=c.grounding_system_ok,
            ambient_temperature=c.ambient_temperature,
            tank_temperature=c.tank_temperature,
            storage_area_clean=c.storage_area_clean,
            hazardous_materials_labeled=c.hazardous_materials_labeled,
            safety_data_sheets_available=c.safety_data_sheets_available,
            overall_status=c.overall_status.value,
            checked_by=c.checked_by,
            checked_at=c.checked_at,
            issues_found=c.issues_found,
            corrective_actions=c.corrective_actions,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at,
            notes=c.notes
        )
        for c in checks
    ]


@router.post("/incidents", response_model=SafetyIncidentResponse)
async def create_safety_incident(request: CreateSafetyIncidentRequest):
    """Create a new safety incident"""
    
    existing_incident = await SafetyIncident.find_one(SafetyIncident.incident_id == request.incident_id)
    if existing_incident:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incident ID already exists"
        )
    
    incident = SafetyIncident(**request.dict())
    await incident.insert()
    
    return SafetyIncidentResponse(
        id=str(incident.id),
        incident_id=incident.incident_id,
        incident_type=incident.incident_type,
        severity=incident.severity,
        tank_id=incident.tank_id,
        location_description=incident.location_description,
        incident_date=incident.incident_date,
        description=incident.description,
        immediate_action_taken=incident.immediate_action_taken,
        fuel_loss_liters=incident.fuel_loss_liters,
        estimated_cost=incident.estimated_cost,
        investigated_by=incident.investigated_by,
        investigation_date=incident.investigation_date,
        root_cause=incident.root_cause,
        corrective_actions=incident.corrective_actions,
        resolved=incident.resolved,
        resolved_at=incident.resolved_at,
        reported_to_rura=incident.reported_to_rura,
        rura_reference_number=incident.rura_reference_number,
        created_by=incident.created_by,
        created_at=incident.created_at
    )


@router.get("/incidents", response_model=List[SafetyIncidentResponse])
async def get_safety_incidents(skip: int = 0, limit: int = 100, severity: Optional[str] = None):
    """Get all safety incidents with optional filtering"""
    
    query = {}
    if severity:
        query["severity"] = severity
    
    incidents = await SafetyIncident.find(query).skip(skip).limit(limit).sort("-incident_date").to_list()
    
    return [
        SafetyIncidentResponse(
            id=str(i.id),
            incident_id=i.incident_id,
            incident_type=i.incident_type,
            severity=i.severity,
            tank_id=i.tank_id,
            location_description=i.location_description,
            incident_date=i.incident_date,
            description=i.description,
            immediate_action_taken=i.immediate_action_taken,
            fuel_loss_liters=i.fuel_loss_liters,
            estimated_cost=i.estimated_cost,
            investigated_by=i.investigated_by,
            investigation_date=i.investigation_date,
            root_cause=i.root_cause,
            corrective_actions=i.corrective_actions,
            resolved=i.resolved,
            resolved_at=i.resolved_at,
            reported_to_rura=i.reported_to_rura,
            rura_reference_number=i.rura_reference_number,
            created_by=i.created_by,
            created_at=i.created_at
        )
        for i in incidents
    ]


@router.put("/incidents/{incident_id}/resolve")
async def resolve_safety_incident(incident_id: str, corrective_actions: str, resolved_by: str):
    """Resolve a safety incident"""
    
    incident = await SafetyIncident.find_one(SafetyIncident.incident_id == incident_id)
    
    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )
    
    incident.resolved = True
    incident.resolved_at = datetime.utcnow()
    incident.corrective_actions = corrective_actions
    await incident.save()
    
    return {"message": "Incident resolved successfully"}
