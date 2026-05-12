from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.expenditure import ExpenditureRequest, ExpenditureType, ExpenditureStatus

router = APIRouter(prefix="/expenditures", tags=["expenditures"])


class CreateExpenditureRequestRequest(BaseModel):
    request_id: str
    expenditure_type: ExpenditureType
    title: str
    description: str
    amount: float
    requested_by: str
    requester_role: str
    requester_department: str
    budget_code: Optional[str] = None
    budget_category: Optional[str] = None
    quote_document_url: Optional[str] = None
    notes: Optional[str] = None


class ExpenditureRequestResponse(BaseModel):
    id: str
    request_id: str
    expenditure_type: str
    title: str
    description: str
    amount: float
    requested_by: str
    requester_role: str
    requester_department: str
    status: str
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    rejection_reason: Optional[str]
    payment_method: Optional[str]
    payment_reference: Optional[str]
    paid_at: Optional[datetime]
    budget_code: Optional[str]
    budget_category: Optional[str]
    notes: Optional[str]


@router.post("/", response_model=ExpenditureRequestResponse)
async def create_expenditure_request(request: CreateExpenditureRequestRequest):
    """Create a new expenditure request"""
    
    existing_request = await ExpenditureRequest.find_one(ExpenditureRequest.request_id == request.request_id)
    if existing_request:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request ID already exists"
        )
    
    expenditure = ExpenditureRequest(**request.dict())
    await expenditure.insert()
    
    return ExpenditureRequestResponse(
        id=str(expenditure.id),
        request_id=expenditure.request_id,
        expenditure_type=expenditure.expenditure_type.value,
        title=expenditure.title,
        description=expenditure.description,
        amount=expenditure.amount,
        requested_by=expenditure.requested_by,
        requester_role=expenditure.requester_role,
        requester_department=expenditure.requester_department,
        status=expenditure.status.value,
        approved_by=expenditure.approved_by,
        approved_at=expenditure.approved_at,
        rejection_reason=expenditure.rejection_reason,
        payment_method=expenditure.payment_method,
        payment_reference=expenditure.payment_reference,
        paid_at=expenditure.paid_at,
        budget_code=expenditure.budget_code,
        budget_category=expenditure.budget_category,
        notes=expenditure.notes
    )


@router.get("/", response_model=List[ExpenditureRequestResponse])
async def get_expenditure_requests(skip: int = 0, limit: int = 100, status: Optional[ExpenditureStatus] = None):
    """Get all expenditure requests with optional filtering"""
    
    query = {}
    if status:
        query["status"] = status
    
    requests = await ExpenditureRequest.find(query).skip(skip).limit(limit).sort("-created_at").to_list()
    
    return [
        ExpenditureRequestResponse(
            id=str(r.id),
            request_id=r.request_id,
            expenditure_type=r.expenditure_type.value,
            title=r.title,
            description=r.description,
            amount=r.amount,
            requested_by=r.requested_by,
            requester_role=r.requester_role,
            requester_department=r.requester_department,
            status=r.status.value,
            approved_by=r.approved_by,
            approved_at=r.approved_at,
            rejection_reason=r.rejection_reason,
            payment_method=r.payment_method,
            payment_reference=r.payment_reference,
            paid_at=r.paid_at,
            budget_code=r.budget_code,
            budget_category=r.budget_category,
            notes=r.notes
        )
        for r in requests
    ]


@router.put("/{request_id}/approve")
async def approve_expenditure_request(request_id: str, approved_by: str):
    """Approve an expenditure request"""
    
    request = await ExpenditureRequest.find_one(ExpenditureRequest.request_id == request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    request.status = ExpenditureStatus.APPROVED
    request.approved_by = approved_by
    request.approved_at = datetime.utcnow()
    await request.save()
    
    return {"message": "Expenditure request approved successfully"}


@router.put("/{request_id}/reject")
async def reject_expenditure_request(request_id: str, rejection_reason: str):
    """Reject an expenditure request"""
    
    request = await ExpenditureRequest.find_one(ExpenditureRequest.request_id == request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    request.status = ExpenditureStatus.REJECTED
    request.rejection_reason = rejection_reason
    await request.save()
    
    return {"message": "Expenditure request rejected successfully"}


@router.put("/{request_id}/mark-paid")
async def mark_expenditure_paid(request_id: str, payment_method: str, payment_reference: str):
    """Mark an expenditure request as paid"""
    
    request = await ExpenditureRequest.find_one(ExpenditureRequest.request_id == request_id)
    
    if not request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Request not found"
        )
    
    request.status = ExpenditureStatus.PAID
    request.payment_method = payment_method
    request.payment_reference = payment_reference
    request.paid_at = datetime.utcnow()
    await request.save()
    
    return {"message": "Expenditure marked as paid successfully"}
