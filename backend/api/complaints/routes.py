from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.staff_management import CustomerComplaint

router = APIRouter(prefix="/complaints", tags=["complaints"])


class CreateComplaintRequest(BaseModel):
    complaint_id: str
    customer_id: Optional[str] = None
    customer_name: str
    customer_phone: Optional[str] = None
    complaint_type: str
    description: str
    severity: str = "medium"
    related_transaction_id: Optional[str] = None
    pump_number: Optional[int] = None
    reported_by: Optional[str] = None


class UpdateComplaintRequest(BaseModel):
    status: Optional[str] = None
    resolution: Optional[str] = None
    refund_amount: Optional[float] = None


class ComplaintResponse(BaseModel):
    id: str
    complaint_id: str
    customer_id: Optional[str]
    customer_name: str
    customer_phone: Optional[str]
    complaint_type: str
    description: str
    severity: str
    related_transaction_id: Optional[str]
    pump_number: Optional[int]
    reported_at: datetime
    reported_by: Optional[str]
    assigned_to: Optional[str]
    status: str
    resolution: Optional[str]
    resolved_by: Optional[str]
    resolved_at: Optional[datetime]
    refund_amount: Optional[float]
    refund_approved_by: Optional[str]


@router.post("/complaints", response_model=ComplaintResponse)
async def create_complaint(request: CreateComplaintRequest):
    """Create a new customer complaint"""
    complaint = CustomerComplaint(
        complaint_id=request.complaint_id,
        customer_id=request.customer_id,
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        complaint_type=request.complaint_type,
        description=request.description,
        severity=request.severity,
        related_transaction_id=request.related_transaction_id,
        pump_number=request.pump_number,
        reported_by=request.reported_by,
        status="open"
    )
    
    await complaint.insert()
    
    return ComplaintResponse(
        id=str(complaint.id),
        complaint_id=complaint.complaint_id,
        customer_id=complaint.customer_id,
        customer_name=complaint.customer_name,
        customer_phone=complaint.customer_phone,
        complaint_type=complaint.complaint_type,
        description=complaint.description,
        severity=complaint.severity,
        related_transaction_id=complaint.related_transaction_id,
        pump_number=complaint.pump_number,
        reported_at=complaint.reported_at,
        reported_by=complaint.reported_by,
        assigned_to=complaint.assigned_to,
        status=complaint.status,
        resolution=complaint.resolution,
        resolved_by=complaint.resolved_by,
        resolved_at=complaint.resolved_at,
        refund_amount=complaint.refund_amount,
        refund_approved_by=complaint.refund_approved_by
    )


@router.get("/complaints", response_model=List[ComplaintResponse])
async def get_complaints(skip: int = 0, limit: int = 100, status: Optional[str] = None):
    """Get all complaints with optional filtering"""
    query = {}
    if status:
        query["status"] = status
    
    complaints = await CustomerComplaint.find(query).skip(skip).limit(limit).sort("-reported_at").to_list()
    
    return [
        ComplaintResponse(
            id=str(c.id),
            complaint_id=c.complaint_id,
            customer_id=c.customer_id,
            customer_name=c.customer_name,
            customer_phone=c.customer_phone,
            complaint_type=c.complaint_type,
            description=c.description,
            severity=c.severity,
            related_transaction_id=c.related_transaction_id,
            pump_number=c.pump_number,
            reported_at=c.reported_at,
            reported_by=c.reported_by,
            assigned_to=c.assigned_to,
            status=c.status,
            resolution=c.resolution,
            resolved_by=c.resolved_by,
            resolved_at=c.resolved_at,
            refund_amount=c.refund_amount,
            refund_approved_by=c.refund_approved_by
        )
        for c in complaints
    ]


@router.put("/complaints/{complaint_id}", response_model=ComplaintResponse)
async def update_complaint(complaint_id: str, request: UpdateComplaintRequest, user_id: str = "user"):
    """Update complaint status and resolution"""
    complaint = await CustomerComplaint.find_one(CustomerComplaint.complaint_id == complaint_id)
    
    if not complaint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Complaint not found"
        )
    
    if request.status:
        complaint.status = request.status
        if request.status == "resolved":
            complaint.resolved_by = user_id
            complaint.resolved_at = datetime.utcnow()
    
    if request.resolution:
        complaint.resolution = request.resolution
    
    if request.refund_amount is not None:
        complaint.refund_amount = request.refund_amount
        complaint.refund_approved_by = user_id
    
    await complaint.save()
    
    return ComplaintResponse(
        id=str(complaint.id),
        complaint_id=complaint.complaint_id,
        customer_id=complaint.customer_id,
        customer_name=complaint.customer_name,
        customer_phone=complaint.customer_phone,
        complaint_type=complaint.complaint_type,
        description=complaint.description,
        severity=complaint.severity,
        related_transaction_id=complaint.related_transaction_id,
        pump_number=complaint.pump_number,
        reported_at=complaint.reported_at,
        reported_by=complaint.reported_by,
        assigned_to=complaint.assigned_to,
        status=complaint.status,
        resolution=complaint.resolution,
        resolved_by=complaint.resolved_by,
        resolved_at=complaint.resolved_at,
        refund_amount=complaint.refund_amount,
        refund_approved_by=complaint.refund_approved_by
    )
