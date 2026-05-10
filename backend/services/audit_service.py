from typing import List, Optional, Dict, Any
from datetime import datetime
from backend.models.user import User
from backend.models.audit_log import AuditLog


class AuditLogService:
    
    @staticmethod
    async def log_action(
        user: User,
        action: str,
        resource_type: str,
        resource_id: Optional[str],
        old_value: Optional[Dict[str, Any]],
        new_value: Optional[Dict[str, Any]],
        ip_address: Optional[str] = None
    ):
        """Log user action with visibility rules"""
        
        # Determine who can see this log
        # Rule: User cannot see their own actions
        visible_to_roles = []
        
        if user.role.name == "admin":
            # Other admins and superadmin can see
            visible_to_roles = [1, 2]  # superadmin, admin (except the actor)
        elif user.role.name == "accountant":
            # Admin and superadmin can see
            visible_to_roles = [1, 2]
        elif user.role.name == "staff":
            # Admin and superadmin can see
            visible_to_roles = [1, 2]
        elif user.role.name == "superadmin":
            # Only superadmin can see superadmin actions
            visible_to_roles = [1]
        
        audit_log = AuditLog(
            user_id=str(user.id),
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_value=old_value,
            new_value=new_value,
            ip_address=ip_address,
            timestamp=datetime.utcnow(),
            visible_to_roles=visible_to_roles
        )
        
        await audit_log.insert()
    
    @staticmethod
    async def log_permission_toggle(
        admin: User,
        target_user: User,
        permission_id: str,
        old_state: bool,
        new_state: bool
    ):
        """Specific logging for permission toggles"""
        
        await AuditLogService.log_action(
            user=admin,
            action="toggled_permission",
            resource_type="user_permission",
            resource_id=target_user.id,
            old_value={
                "user_id": target_user.id,
                "permission_id": permission_id,
                "is_enabled": old_state
            },
            new_value={
                "user_id": target_user.id,
                "permission_id": permission_id,
                "is_enabled": new_state
            }
        )
    
    @staticmethod
    async def get_visible_logs(user: User) -> List[AuditLog]:
        """Get audit logs visible to this user"""
        
        if user.role.name == "superadmin":
            # See everything
            return await AuditLog.find_all().sort(-AuditLog.timestamp).to_list()
        else:
            # See logs where:
            # 1. User's role level is in visible_to_roles
            # 2. AND it's not their own action
            return await AuditLog.find(
                AuditLog.visible_to_roles.contains(user.role.level),
                AuditLog.user_id != str(user.id)  # CRITICAL: Cannot see own actions
            ).sort(-AuditLog.timestamp).to_list()
