from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from backend.models.approval_request import ApprovalRequest, ApprovalStatus
from backend.models.user import User
from backend.services.approval_workflow import ApprovalWorkflowService

router = APIRouter(prefix="/approvals", tags=["approvals"])


class CreateApprovalRequest(BaseModel):
    request_type: str
    request_data: Dict[str, Any]
    reason: str


class ProcessApprovalRequest(BaseModel):
    approved: bool
    notes: Optional[str] = None


class ApprovalResponse(BaseModel):
    id: str
    requester_id: str
    approver_id: Optional[str]
    request_type: str
    request_data: Dict[str, Any]
    reason: str
    status: str
    requested_at: str
    reviewed_at: Optional[str]
    reviewer_notes: Optional[str]


@router.post("/", response_model=ApprovalResponse)
async def create_approval_request(
    request: CreateApprovalRequest, 
    requester_id: str = "requester"
):
    """Create a new approval request"""
    
    requester = await User.get(requester_id)
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester not found"
        )
    
    approval_request = await ApprovalWorkflowService.create_approval_request(
        requester=requester,
        request_type=request.request_type,
        request_data=request.request_data,
        reason=request.reason
    )
    
    return ApprovalResponse(
        id=str(approval_request.id),
        requester_id=approval_request.requester_id,
        approver_id=approval_request.approver_id,
        request_type=approval_request.request_type,
        request_data=approval_request.request_data,
        reason=approval_request.reason,
        status=approval_request.status.value,
        requested_at=approval_request.requested_at.isoformat(),
        reviewed_at=approval_request.reviewed_at.isoformat() if approval_request.reviewed_at else None,
        reviewer_notes=approval_request.reviewer_notes
    )


@router.get("/pending")
async def get_pending_approvals(approver_id: str = "approver"):
    """Get pending approvals for a specific approver"""
    
    approver = await User.get(approver_id)
    if not approver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approver not found"
        )
    
    approvals = await ApprovalWorkflowService.get_pending_approvals(approver)
    
    return [
        ApprovalResponse(
            id=str(approval.id),
            requester_id=approval.requester_id,
            approver_id=approval.approver_id,
            request_type=approval.request_type,
            request_data=approval.request_data,
            reason=approval.reason,
            status=approval.status.value,
            requested_at=approval.requested_at.isoformat(),
            reviewed_at=approval.reviewed_at.isoformat() if approval.reviewed_at else None,
            reviewer_notes=approval.reviewer_notes
        )
        for approval in approvals
    ]


@router.get("/my-requests")
async def get_my_requests(requester_id: str = "requester"):
    """Get all requests made by a user"""
    
    requester = await User.get(requester_id)
    if not requester:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requester not found"
        )
    
    approvals = await ApprovalWorkflowService.get_user_requests(requester)
    
    return [
        ApprovalResponse(
            id=str(approval.id),
            requester_id=approval.requester_id,
            approver_id=approval.approver_id,
            request_type=approval.request_type,
            request_data=approval.request_data,
            reason=approval.reason,
            status=approval.status.value,
            requested_at=approval.requested_at.isoformat(),
            reviewed_at=approval.reviewed_at.isoformat() if approval.reviewed_at else None,
            reviewer_notes=approval.reviewer_notes
        )
        for approval in approvals
    ]


@router.post("/{request_id}/process")
async def process_approval(
    request_id: str, 
    request: ProcessApprovalRequest,
    approver_id: str = "approver"
):
    """Process an approval request (approve or reject)"""
    
    approver = await User.get(approver_id)
    if not approver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Approver not found"
        )
    
    await ApprovalWorkflowService.process_approval(
        approver=approver,
        request_id=request_id,
        approved=request.approved,
        notes=request.notes
    )
    
    return {"message": "Approval processed successfully"}
