from typing import Tuple, Optional
from datetime import datetime, timedelta
from backend.models.user import User, Role, Permission, UserPermission
from backend.core.exceptions import PermissionDenied, ApprovalRequired


class AccessControlService:
    
    @staticmethod
    async def can_user_perform_action(
        user: User, 
        module: str, 
        action: str, 
        resource: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if user can perform action.
        Returns: (can_perform, reason_if_denied)
        """
        
        # Super Admin can do everything
        if user.role.name == "superadmin":
            return True, None
        
        # Check if user is active
        if not user.is_active:
            return False, "Account is disabled"
        
        # Get user's permissions
        permission = await Permission.find_one(
            Permission.module == module,
            Permission.action == action,
            Permission.resource == resource
        )
        
        if not permission:
            return False, "Permission not defined"
        
        # Check if user has this permission
        user_perm = await UserPermission.find_one(
            UserPermission.user_id == user.id,
            UserPermission.permission_id.id == permission.id,
            UserPermission.is_enabled == True
        )
        
        if not user_perm:
            return False, "Permission not granted"
        
        # Check if permission has expired (temporal access)
        if user_perm.expires_at and user_perm.expires_at < datetime.utcnow():
            user_perm.is_enabled = False
            await user_perm.save()
            return False, "Permission has expired"
        
        # Check if action requires approval
        if permission.requires_approval:
            # Check if user's role level can bypass approval
            if user.role.level <= permission.approval_role_level:
                return True, None
            else:
                return False, "APPROVAL_REQUIRED"
        
        return True, None
    
    @staticmethod
    async def toggle_user_permission(
        admin: User,
        target_user: User,
        permission_id: str,
        enabled: bool
    ):
        """Admin toggles a user's permission"""
        
        # Verify admin has authority
        if admin.role.level >= target_user.role.level:
            raise PermissionDenied("Cannot manage user of equal or higher role")
        
        permission = await Permission.get(permission_id)
        if not permission:
            raise ValueError("Permission not found")
        
        user_perm = await UserPermission.find_one(
            UserPermission.user_id == target_user.id,
            UserPermission.permission_id.id == permission.id
        )
        
        old_state = user_perm.is_enabled if user_perm else False
        
        if user_perm:
            user_perm.is_enabled = enabled
            user_perm.updated_at = datetime.utcnow()
            await user_perm.save()
        else:
            user_perm = UserPermission(
                user_id=target_user.id,
                permission_id=permission,
                is_enabled=enabled,
                granted_by=admin.id,
                granted_at=datetime.utcnow()
            )
            await user_perm.insert()
        
        # Log the action
        from backend.services.audit_service import AuditLogService
        await AuditLogService.log_permission_toggle(
            admin=admin,
            target_user=target_user,
            permission_id=permission_id,
            old_state=old_state,
            new_state=enabled
        )
    
    @staticmethod
    async def grant_temporal_access(
        admin: User,
        target_user: User,
        permission_id: str,
        duration_hours: int
    ):
        """Grant time-limited access to a permission"""
        
        permission = await Permission.get(permission_id)
        if not permission:
            raise ValueError("Permission not found")
        
        expires_at = datetime.utcnow() + timedelta(hours=duration_hours)
        
        user_perm = await UserPermission.find_one(
            UserPermission.user_id == target_user.id,
            UserPermission.permission_id.id == permission.id
        )
        
        if user_perm:
            user_perm.is_enabled = True
            user_perm.expires_at = expires_at
            await user_perm.save()
        else:
            user_perm = UserPermission(
                user_id=target_user.id,
                permission_id=permission,
                is_enabled=True,
                granted_by=admin.id,
                granted_at=datetime.utcnow(),
                expires_at=expires_at
            )
            await user_perm.insert()
        
        # Send notification to user (implement notification service)
        # NotificationService.send(user=target_user, message=...)
