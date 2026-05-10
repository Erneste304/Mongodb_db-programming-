from typing import Optional, Dict, Any
from datetime import datetime
from backend.models.user import User
from backend.models.approval_request import ApprovalRequest, ApprovalStatus
from backend.core.exceptions import PermissionDenied, ResourceNotFound


class ApprovalWorkflowService:
    
    @staticmethod
    async def create_approval_request(
        requester: User,
        request_type: str,
        request_data: Dict[str, Any],
        reason: str
    ) -> ApprovalRequest:
        """Create a new approval request"""
        
        # Determine appropriate approver based on request type
        if request_type == "large_payment":
            approver_role = "admin"
        elif request_type == "historical_report_access":
            approver_role = "admin"
        elif request_type == "void_transaction":
            approver_role = "admin"
        else:
            approver_role = "admin"
        
        # Find available approver
        from backend.models.user import Role
        approver_role_obj = await Role.find_one(Role.name == approver_role)
        
        approver = await User.find_one(
            User.role.id == approver_role_obj.id,
            User.is_active == True
        )
        
        request = ApprovalRequest(
            requester_id=str(requester.id),
            approver_id=str(approver.id) if approver else None,
            request_type=request_type,
            request_data=request_data,
            reason=reason,
            status=ApprovalStatus.PENDING,
            requested_at=datetime.utcnow()
        )
        
        await request.insert()
        
        # Send notification to approver (implement notification service)
        # if approver:
        #     NotificationService.send(...)
        
        return request
    
    @staticmethod
    async def process_approval(
        approver: User,
        request_id: str,
        approved: bool,
        notes: Optional[str] = None
    ):
        """Process an approval request"""
        
        request = await ApprovalRequest.get(request_id)
        
        if not request:
            raise ResourceNotFound("Request not found")
        
        if request.approver_id != str(approver.id):
            raise PermissionDenied("You are not the assigned approver")
        
        if request.status != ApprovalStatus.PENDING:
            raise ValueError("Request already processed")
        
        request.status = ApprovalStatus.APPROVED if approved else ApprovalStatus.REJECTED
        request.approver_id = str(approver.id)
        request.reviewed_at = datetime.utcnow()
        request.reviewer_notes = notes
        
        await request.save()
        
        # Execute the approved action
        if approved:
            await ApprovalWorkflowService._execute_approved_action(request)
        
        # Notify requester
        # NotificationService.send(...)
        
        # Log the approval/rejection
        from backend.services.audit_service import AuditLogService
        await AuditLogService.log_action(
            user=approver,
            action=f"{'approved' if approved else 'rejected'}_request",
            resource_type="approval_request",
            resource_id=request_id,
            old_value={"status": "pending"},
            new_value={"status": request.status, "notes": notes}
        )
    
    @staticmethod
    async def _execute_approved_action(request: ApprovalRequest):
        """Execute the action that was approved"""
        
        if request.request_type == "large_payment":
            # Process the payment
            # PaymentService.process_payment(...)
            pass
        
        elif request.request_type == "historical_report_access":
            # Grant temporal access
            from backend.services.access_control import AccessControlService
            requester = await User.get(request.requester_id)
            approver = await User.get(request.approver_id)
            
            await AccessControlService.grant_temporal_access(
                admin=approver,
                target_user=requester,
                permission_id=request.request_data.get("permission_id"),
                duration_hours=request.request_data.get("duration_hours", 24)
            )
        
        elif request.request_type == "void_transaction":
            # Void the transaction
            # TransactionService.void_transaction(...)
            pass
    
    @staticmethod
    async def get_pending_approvals(approver: User) -> list[ApprovalRequest]:
        """Get pending approvals for a specific approver"""
        return await ApprovalRequest.find(
            ApprovalRequest.approver_id == str(approver.id),
            ApprovalRequest.status == ApprovalStatus.PENDING
        ).sort(-ApprovalRequest.requested_at).to_list()
    
    @staticmethod
    async def get_user_requests(requester: User) -> list[ApprovalRequest]:
        """Get all requests made by a user"""
        return await ApprovalRequest.find(
            ApprovalRequest.requester_id == str(requester.id)
        ).sort(-ApprovalRequest.requested_at).to_list()
