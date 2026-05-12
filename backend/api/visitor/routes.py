from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.visitor import VisitorLog, BusinessPartner, VisitorType, VisitPurpose, PartnerType
from backend.core.security import get_current_user, require_role_level
from backend.models.user import User

router = APIRouter(prefix="/visitors", tags=["visitors"])


class CreateVisitorLogRequest(BaseModel):
    visitor_name: str
    company_name: Optional[str] = None
    visitor_phone: str
    visitor_type: VisitorType
    purpose: VisitPurpose
    id_number: Optional[str] = None
    escort_required: bool = False
    escorted_by: Optional[str] = None
    safety_briefing_completed: bool = False
    safety_briefing_completed_by: Optional[str] = None
    delivery_document_verified: bool = False
    delivery_document_type: Optional[str] = None
    delivery_document_number: Optional[str] = None
    delivery_document_verified_by: Optional[str] = None
    vehicle_registration: Optional[str] = None
    vehicle_type: Optional[str] = None
    notes: Optional[str] = None


class VisitorLogResponse(BaseModel):
    id: str
    visitor_name: str
    company_name: Optional[str]
    visitor_phone: str
    visitor_type: str
    purpose: str
    id_number: Optional[str]
    check_in_time: datetime
    check_out_time: Optional[datetime]
    escort_required: bool
    escorted_by: Optional[str]
    safety_briefing_completed: bool
    safety_briefing_completed_by: Optional[str]
    safety_briefing_completed_at: Optional[datetime]
    delivery_document_verified: bool
    delivery_document_type: Optional[str]
    delivery_document_number: Optional[str]
    delivery_document_verified_by: Optional[str]
    delivery_document_verified_at: Optional[datetime]
    vehicle_registration: Optional[str]
    vehicle_type: Optional[str]
    status: str


@router.post("/log", response_model=VisitorLogResponse)
async def sign_in_visitor(
    request: CreateVisitorLogRequest,
    current_user: User = Depends(get_current_user)
):
    """Sign in a new visitor"""
    log = VisitorLog(**request.dict())
    
    # Set safety briefing timestamp if completed
    if request.safety_briefing_completed:
        log.safety_briefing_completed_at = datetime.utcnow()
    
    # Set document verification timestamp if verified
    if request.delivery_document_verified:
        log.delivery_document_verified_at = datetime.utcnow()
    
    await log.insert()
    
    return VisitorLogResponse(
        id=str(log.id),
        visitor_name=log.visitor_name,
        company_name=log.company_name,
        visitor_phone=log.visitor_phone,
        visitor_type=log.visitor_type.value,
        purpose=log.purpose.value,
        id_number=log.id_number,
        check_in_time=log.check_in_time,
        check_out_time=log.check_out_time,
        escort_required=log.escort_required,
        escorted_by=log.escorted_by,
        safety_briefing_completed=log.safety_briefing_completed,
        safety_briefing_completed_by=log.safety_briefing_completed_by,
        safety_briefing_completed_at=log.safety_briefing_completed_at,
        delivery_document_verified=log.delivery_document_verified,
        delivery_document_type=log.delivery_document_type,
        delivery_document_number=log.delivery_document_number,
        delivery_document_verified_by=log.delivery_document_verified_by,
        delivery_document_verified_at=log.delivery_document_verified_at,
        vehicle_registration=log.vehicle_registration,
        vehicle_type=log.vehicle_type,
        status=log.status
    )


@router.post("/log/{log_id}/sign-out")
async def sign_out_visitor(
    log_id: str,
    current_user: User = Depends(get_current_user)
):
    """Sign out a visitor"""
    log = await VisitorLog.get(log_id)
    if not log:
        raise HTTPException(status_code=404, detail="Visitor log not found")
    
    log.check_out_time = datetime.utcnow()
    log.status = "completed"
    await log.save()
    
    return {"message": "Visitor signed out successfully"}


@router.get("/log", response_model=List[VisitorLogResponse])
async def get_visitor_logs(
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    """Get visitor logs"""
    query = {}
    if status:
        query["status"] = status
    
    logs = await VisitorLog.find(query).sort(-VisitorLog.check_in_time).to_list()
    return [
        VisitorLogResponse(
            id=str(log.id),
            visitor_name=log.visitor_name,
            company_name=log.company_name,
            visitor_phone=log.visitor_phone,
            visitor_type=log.visitor_type.value,
            purpose=log.purpose.value,
            id_number=log.id_number,
            check_in_time=log.check_in_time,
            check_out_time=log.check_out_time,
            escort_required=log.escort_required,
            escorted_by=log.escorted_by,
            safety_briefing_completed=log.safety_briefing_completed,
            safety_briefing_completed_by=log.safety_briefing_completed_by,
            safety_briefing_completed_at=log.safety_briefing_completed_at,
            delivery_document_verified=log.delivery_document_verified,
            delivery_document_type=log.delivery_document_type,
            delivery_document_number=log.delivery_document_number,
            delivery_document_verified_by=log.delivery_document_verified_by,
            delivery_document_verified_at=log.delivery_document_verified_at,
            vehicle_registration=log.vehicle_registration,
            vehicle_type=log.vehicle_type,
            status=log.status
        )
        for log in logs
    ]
