"""
RURA Inspection Records Models
For maintaining records for RURA inspections
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class InspectionType(str, Enum):
    ROUTINE = "routine"
    COMPLAINT = "complaint"
    INCIDENT = "incident"
    RENEWAL = "renewal"
    SPECIAL = "special"


class InspectionStatus(str, Enum):
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"
    CANCELLED = "cancelled"


class RURAInspection(Document):
    """RURA inspection records"""
    inspection_id: str = Field(..., unique=True)
    inspection_type: InspectionType = Field(...)
    station_id: str = Field(...)
    
    # Inspection details
    scheduled_date: datetime = Field(...)
    inspection_date: Optional[datetime] = Field(None)
    inspector_name: str = Field(...)
    inspector_id: Optional[str] = Field(None)
    rura_reference_number: Optional[str] = Field(None)
    
    # Status
    status: InspectionStatus = Field(default=InspectionStatus.SCHEDULED)
    
    # Checklist results
    fuel_storage_compliant: Optional[bool] = Field(None)
    safety_equipment_compliant: Optional[bool] = Field(None)
    documentation_compliant: Optional[bool] = Field(None)
    environmental_compliant: Optional[bool] = Field(None)
    staff_training_compliant: Optional[bool] = Field(None)
    meter_calibration_compliant: Optional[bool] = Field(None)
    
    # Findings
    findings: Optional[str] = Field(None)
    violations: Optional[str] = Field(None)
    recommendations: Optional[str] = Field(None)
    
    # Compliance
    compliance_score: Optional[float] = Field(None, ge=0, le=100)
    pass_rate: Optional[float] = Field(None, ge=0, le=100)
    
    # Follow-up
    follow_up_required: bool = Field(default=False)
    follow_up_date: Optional[datetime] = Field(None)
    follow_up_completed: bool = Field(default=False)
    
    # Documents
    report_document_url: Optional[str] = Field(None)
    certificate_url: Optional[str] = Field(None)
    
    # Station representative
    station_representative: str = Field(...)
    representative_position: str = Field(...)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "rura_inspections"


class InspectionDocument(Document):
    """Documents related to RURA inspections"""
    document_id: str = Field(..., unique=True)
    inspection_id: str = Field(...)
    document_type: str = Field(..., description="report, certificate, calibration, safety, environmental")
    document_name: str = Field(...)
    document_url: str = Field(...)
    
    # Document details
    upload_date: datetime = Field(default_factory=datetime.utcnow)
    uploaded_by: str = Field(...)
    expiry_date: Optional[datetime] = Field(None)
    
    # Verification
    verified: bool = Field(default=False)
    verified_by: Optional[str] = Field(None)
    verified_at: Optional[datetime] = Field(None)
    
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "inspection_documents"
