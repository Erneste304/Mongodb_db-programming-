from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.inspection import RURAInspection, InspectionDocument, InspectionType, InspectionStatus

router = APIRouter(prefix="/inspection", tags=["inspection"])


class CreateRURAInspectionRequest(BaseModel):
    inspection_id: str
    inspection_type: InspectionType
    station_id: str
    scheduled_date: datetime
    inspector_name: str
    inspector_id: Optional[str] = None
    station_representative: str
    representative_position: str
    notes: Optional[str] = None


class RURAInspectionResponse(BaseModel):
    id: str
    inspection_id: str
    inspection_type: str
    station_id: str
    scheduled_date: datetime
    inspection_date: Optional[datetime]
    inspector_name: str
    inspector_id: Optional[str]
    rura_reference_number: Optional[str]
    status: str
    fuel_storage_compliant: Optional[bool]
    safety_equipment_compliant: Optional[bool]
    documentation_compliant: Optional[bool]
    environmental_compliant: Optional[bool]
    staff_training_compliant: Optional[bool]
    meter_calibration_compliant: Optional[bool]
    findings: Optional[str]
    violations: Optional[str]
    recommendations: Optional[str]
    compliance_score: Optional[float]
    pass_rate: Optional[float]
    follow_up_required: bool
    follow_up_date: Optional[datetime]
    follow_up_completed: bool
    report_document_url: Optional[str]
    certificate_url: Optional[str]
    station_representative: str
    representative_position: str
    notes: Optional[str]


class UpdateInspectionResultRequest(BaseModel):
    inspection_date: datetime
    rura_reference_number: Optional[str] = None
    fuel_storage_compliant: Optional[bool] = None
    safety_equipment_compliant: Optional[bool] = None
    documentation_compliant: Optional[bool] = None
    environmental_compliant: Optional[bool] = None
    staff_training_compliant: Optional[bool] = None
    meter_calibration_compliant: Optional[bool] = None
    findings: Optional[str] = None
    violations: Optional[str] = None
    recommendations: Optional[str] = None
    compliance_score: Optional[float] = None
    pass_rate: Optional[float] = None
    follow_up_required: bool = False
    follow_up_date: Optional[datetime] = None
    report_document_url: Optional[str] = None
    certificate_url: Optional[str] = None


class CreateInspectionDocumentRequest(BaseModel):
    document_id: str
    inspection_id: str
    document_type: str
    document_name: str
    document_url: str
    expiry_date: Optional[datetime] = None
    notes: Optional[str] = None


class InspectionDocumentResponse(BaseModel):
    id: str
    document_id: str
    inspection_id: str
    document_type: str
    document_name: str
    document_url: str
    upload_date: datetime
    uploaded_by: str
    expiry_date: Optional[datetime]
    verified: bool
    verified_by: Optional[str]
    verified_at: Optional[datetime]
    notes: Optional[str]


@router.post("/inspections", response_model=RURAInspectionResponse)
async def create_rura_inspection(request: CreateRURAInspectionRequest):
    """Create a new RURA inspection"""
    
    existing_inspection = await RURAInspection.find_one(RURAInspection.inspection_id == request.inspection_id)
    if existing_inspection:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inspection ID already exists"
        )
    
    inspection = RURAInspection(
        inspection_id=request.inspection_id,
        inspection_type=request.inspection_type,
        station_id=request.station_id,
        scheduled_date=request.scheduled_date,
        inspector_name=request.inspector_name,
        inspector_id=request.inspector_id,
        station_representative=request.station_representative,
        representative_position=request.representative_position,
        notes=request.notes
    )
    
    await inspection.insert()
    
    return RURAInspectionResponse(
        id=str(inspection.id),
        inspection_id=inspection.inspection_id,
        inspection_type=inspection.inspection_type.value,
        station_id=inspection.station_id,
        scheduled_date=inspection.scheduled_date,
        inspection_date=inspection.inspection_date,
        inspector_name=inspection.inspector_name,
        inspector_id=inspection.inspector_id,
        rura_reference_number=inspection.rura_reference_number,
        status=inspection.status.value,
        fuel_storage_compliant=inspection.fuel_storage_compliant,
        safety_equipment_compliant=inspection.safety_equipment_compliant,
        documentation_compliant=inspection.documentation_compliant,
        environmental_compliant=inspection.environmental_compliant,
        staff_training_compliant=inspection.staff_training_compliant,
        meter_calibration_compliant=inspection.meter_calibration_compliant,
        findings=inspection.findings,
        violations=inspection.violations,
        recommendations=inspection.recommendations,
        compliance_score=inspection.compliance_score,
        pass_rate=inspection.pass_rate,
        follow_up_required=inspection.follow_up_required,
        follow_up_date=inspection.follow_up_date,
        follow_up_completed=inspection.follow_up_completed,
        report_document_url=inspection.report_document_url,
        certificate_url=inspection.certificate_url,
        station_representative=inspection.station_representative,
        representative_position=inspection.representative_position,
        notes=inspection.notes
    )


@router.get("/inspections", response_model=List[RURAInspectionResponse])
async def get_rura_inspections(skip: int = 0, limit: int = 100, station_id: Optional[str] = None, status: Optional[InspectionStatus] = None):
    """Get all RURA inspections with optional filtering"""
    
    query = {}
    if station_id:
        query["station_id"] = station_id
    if status:
        query["status"] = status
    
    inspections = await RURAInspection.find(query).skip(skip).limit(limit).sort("-scheduled_date").to_list()
    
    return [
        RURAInspectionResponse(
            id=str(i.id),
            inspection_id=i.inspection_id,
            inspection_type=i.inspection_type.value,
            station_id=i.station_id,
            scheduled_date=i.scheduled_date,
            inspection_date=i.inspection_date,
            inspector_name=i.inspector_name,
            inspector_id=i.inspector_id,
            rura_reference_number=i.rura_reference_number,
            status=i.status.value,
            fuel_storage_compliant=i.fuel_storage_compliant,
            safety_equipment_compliant=i.safety_equipment_compliant,
            documentation_compliant=i.documentation_compliant,
            environmental_compliant=i.environmental_compliant,
            staff_training_compliant=i.staff_training_compliant,
            meter_calibration_compliant=i.meter_calibration_compliant,
            findings=i.findings,
            violations=i.violations,
            recommendations=i.recommendations,
            compliance_score=i.compliance_score,
            pass_rate=i.pass_rate,
            follow_up_required=i.follow_up_required,
            follow_up_date=i.follow_up_date,
            follow_up_completed=i.follow_up_completed,
            report_document_url=i.report_document_url,
            certificate_url=i.certificate_url,
            station_representative=i.station_representative,
            representative_position=i.representative_position,
            notes=i.notes
        )
        for i in inspections
    ]


@router.put("/inspections/{inspection_id}/result", response_model=RURAInspectionResponse)
async def update_inspection_result(inspection_id: str, request: UpdateInspectionResultRequest):
    """Update inspection results"""
    
    inspection = await RURAInspection.find_one(RURAInspection.inspection_id == inspection_id)
    
    if not inspection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inspection not found"
        )
    
    inspection.inspection_date = request.inspection_date
    inspection.rura_reference_number = request.rura_reference_number
    inspection.fuel_storage_compliant = request.fuel_storage_compliant
    inspection.safety_equipment_compliant = request.safety_equipment_compliant
    inspection.documentation_compliant = request.documentation_compliant
    inspection.environmental_compliant = request.environmental_compliant
    inspection.staff_training_compliant = request.staff_training_compliant
    inspection.meter_calibration_compliant = request.meter_calibration_compliant
    inspection.findings = request.findings
    inspection.violations = request.violations
    inspection.recommendations = request.recommendations
    inspection.compliance_score = request.compliance_score
    inspection.pass_rate = request.pass_rate
    inspection.follow_up_required = request.follow_up_required
    inspection.follow_up_date = request.follow_up_date
    inspection.report_document_url = request.report_document_url
    inspection.certificate_url = request.certificate_url
    
    # Determine status based on compliance
    if inspection.compliance_score and inspection.compliance_score >= 80:
        inspection.status = InspectionStatus.PASSED
    elif inspection.compliance_score and inspection.compliance_score >= 60:
        inspection.status = InspectionStatus.CONDITIONAL
    else:
        inspection.status = InspectionStatus.FAILED
    
    inspection.updated_at = datetime.utcnow()
    await inspection.save()
    
    return RURAInspectionResponse(
        id=str(inspection.id),
        inspection_id=inspection.inspection_id,
        inspection_type=inspection.inspection_type.value,
        station_id=inspection.station_id,
        scheduled_date=inspection.scheduled_date,
        inspection_date=inspection.inspection_date,
        inspector_name=inspection.inspector_name,
        inspector_id=inspection.inspector_id,
        rura_reference_number=inspection.rura_reference_number,
        status=inspection.status.value,
        fuel_storage_compliant=inspection.fuel_storage_compliant,
        safety_equipment_compliant=inspection.safety_equipment_compliant,
        documentation_compliant=inspection.documentation_compliant,
        environmental_compliant=inspection.environmental_compliant,
        staff_training_compliant=inspection.staff_training_compliant,
        meter_calibration_compliant=inspection.meter_calibration_compliant,
        findings=inspection.findings,
        violations=inspection.violations,
        recommendations=inspection.recommendations,
        compliance_score=inspection.compliance_score,
        pass_rate=inspection.pass_rate,
        follow_up_required=inspection.follow_up_required,
        follow_up_date=inspection.follow_up_date,
        follow_up_completed=inspection.follow_up_completed,
        report_document_url=inspection.report_document_url,
        certificate_url=inspection.certificate_url,
        station_representative=inspection.station_representative,
        representative_position=inspection.representative_position,
        notes=inspection.notes
    )


@router.post("/documents", response_model=InspectionDocumentResponse)
async def create_inspection_document(request: CreateInspectionDocumentRequest, uploaded_by: str):
    """Create an inspection document"""
    
    existing_doc = await InspectionDocument.find_one(InspectionDocument.document_id == request.document_id)
    if existing_doc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Document ID already exists"
        )
    
    document = InspectionDocument(
        document_id=request.document_id,
        inspection_id=request.inspection_id,
        document_type=request.document_type,
        document_name=request.document_name,
        document_url=request.document_url,
        expiry_date=request.expiry_date,
        notes=request.notes,
        uploaded_by=uploaded_by
    )
    
    await document.insert()
    
    return InspectionDocumentResponse(
        id=str(document.id),
        document_id=document.document_id,
        inspection_id=document.inspection_id,
        document_type=document.document_type,
        document_name=document.document_name,
        document_url=document.document_url,
        upload_date=document.upload_date,
        uploaded_by=document.uploaded_by,
        expiry_date=document.expiry_date,
        verified=document.verified,
        verified_by=document.verified_by,
        verified_at=document.verified_at,
        notes=document.notes
    )


@router.get("/documents", response_model=List[InspectionDocumentResponse])
async def get_inspection_documents(skip: int = 0, limit: int = 100, inspection_id: Optional[str] = None):
    """Get all inspection documents with optional filtering"""
    
    query = {}
    if inspection_id:
        query["inspection_id"] = inspection_id
    
    documents = await InspectionDocument.find(query).skip(skip).limit(limit).sort("-upload_date").to_list()
    
    return [
        InspectionDocumentResponse(
            id=str(d.id),
            document_id=d.document_id,
            inspection_id=d.inspection_id,
            document_type=d.document_type,
            document_name=d.document_name,
            document_url=d.document_url,
            upload_date=d.upload_date,
            uploaded_by=d.uploaded_by,
            expiry_date=d.expiry_date,
            verified=d.verified,
            verified_by=d.verified_by,
            verified_at=d.verified_at,
            notes=d.notes
        )
        for d in documents
    ]


@router.put("/documents/{document_id}/verify")
async def verify_inspection_document(document_id: str, verified_by: str):
    """Verify an inspection document"""
    
    document = await InspectionDocument.find_one(InspectionDocument.document_id == document_id)
    
    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document not found"
        )
    
    document.verified = True
    document.verified_by = verified_by
    document.verified_at = datetime.utcnow()
    await document.save()
    
    return {"message": "Document verified successfully"}
