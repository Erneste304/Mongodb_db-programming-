from beanie import Document
from pydantic import Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    MORE_INFO = "more_info"


class ApprovalRequest(Document):
    requester_id: str = Field(..., description="User ID who made the request")
    approver_id: Optional[str] = Field(None, description="User ID assigned to approve")
    request_type: str = Field(..., description="payment, report_access, void_transaction")
    request_data: Dict[str, Any] = Field(default_factory=dict)
    reason: str = Field(...)
    status: ApprovalStatus = Field(default=ApprovalStatus.PENDING)
    requested_at: datetime = Field(default_factory=datetime.utcnow)
    reviewed_at: Optional[datetime] = Field(None)
    reviewer_notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "approval_requests"
