from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from datetime import datetime, timezone  # Import timezone
from passlib.context import CryptContext
from backend.models.user import User, Role, Permission, UserPermission
from backend.services.access_control import AccessControlService
from backend.services.audit_service import AuditLogService
from backend.core.security import get_current_user, require_role_level
from backend.core.exceptions import ApprovalRequired

router = APIRouter(prefix="/users", tags=["users"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class CreateUserRequest(BaseModel):
    username: str
    email: Optional[str] = None
    password: str
    role_name: str
    full_name: Optional[str] = None
    employee_id: Optional[str] = None
    phone: Optional[str] = None
    station_id: Optional[str] = None
    salary: Optional[float] = None
    contract_type: Optional[str] = None


class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None


class TogglePermissionRequest(BaseModel):
    permission_id: str
    enabled: bool


class TemporalAccessRequest(BaseModel):
    permission_id: str
    duration_hours: int


class UserResponse(BaseModel):
    id: str
    username: str
    email: Optional[str]
    role: str
    full_name: Optional[str]
    employee_id: Optional[str]
    is_active: bool
    created_at: datetime


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


@router.post("/", response_model=UserResponse)
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Create a new user (requires admin or superadmin)"""

    # Use dictionary query to prevent AttributeError with Beanie/Pydantic v2
    existing_user = await User.find_one({"username": request.username.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Ensure the role exists in the database
    role = await Role.find_one({"name": request.role_name})

    # Debugging help: If role is missing, log it to the terminal
    if not role:
        print(
            f"⚠️ [DATABASE ERROR] Role '{request.role_name}' requested but not found in 'roles' collection.")
        # You can optionally create the role on the fly here if needed,
        # but it's better to seed it correctly.

    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found"
        )

    # Create user
    user = User(
        username=request.username.lower(),
        email=request.email,
        password_hash=get_password_hash(request.password),
        role=role,
        full_name=request.full_name,
        employee_id=request.employee_id,
        phone=request.phone,
        station_id=request.station_id,
        salary=request.salary,
        contract_type=request.contract_type,
        created_by=str(current_user.id),
        created_at=datetime.now(timezone.utc)  # Use timezone-aware datetime
    )

    await user.insert()

    # Safely extract role name
    role_name = getattr(role, "name", "unknown")

    # Log the action
    # await AuditLogService.log_action(...)

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=role_name,
        full_name=user.full_name,
        employee_id=user.employee_id,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user)
):
    """Get all users"""
    # Use dictionary query for stability
    users = await User.find({"is_deleted": False}, fetch_links=True).skip(skip).limit(limit).to_list()

    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            # Safely get role name from the linked document
            role=getattr(user.role, "name",
                         "unknown") if user.role else "unknown",
            full_name=user.full_name,
            employee_id=user.employee_id,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]


@router.get("/roles")
async def get_roles(
    current_user: User = Depends(get_current_user)
):
    """Get all roles"""
    roles = await Role.find_all().to_list()
    return roles


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get a specific user"""
    user = await User.get(user_id, fetch_links=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=getattr(user.role, "name", "unknown") if user.role else "unknown",
        full_name=user.full_name,
        employee_id=user.employee_id,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Update user details"""
    user = await User.get(user_id, fetch_links=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    if request.full_name is not None:
        user.full_name = request.full_name
    if request.phone is not None:
        user.phone = request.phone
    if request.is_active is not None:
        user.is_active = request.is_active

    user.updated_at = datetime.now(timezone.utc)  # Use timezone-aware datetime
    await user.save()

    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=getattr(user.role, "name", "unknown") if user.role else "unknown",
        full_name=user.full_name,
        employee_id=user.employee_id,
        is_active=user.is_active,
        created_at=user.created_at
    )


@router.post("/{user_id}/permissions/toggle")
async def toggle_user_permission(
    user_id: str,
    request: TogglePermissionRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Toggle a user's permission (requires admin)"""

    user = await User.get(user_id, fetch_links=True)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    await AccessControlService.toggle_user_permission(
        admin=current_user,
        target_user=user,
        permission_id=request.permission_id,
        enabled=request.enabled
    )

    return {"message": "Permission toggled successfully"}


@router.get("/{user_id}/permissions")
async def get_user_permissions(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all permissions and their status for a specific user"""
    all_permissions = await Permission.find_all().to_list()
    user_perms = await UserPermission.find(UserPermission.user_id == user_id, fetch_links=True).to_list()

    # Map current status
    status_map = {str(p.permission_id.id): p for p in user_perms}

    return [{
        "id": str(p.id),
        "module": p.module,
        "action": p.action,
        "resource": p.resource,
        "is_enabled": status_map[str(p.id)].is_enabled if str(p.id) in status_map else False,
        "expires_at": status_map[str(p.id)].expires_at if str(p.id) in status_map else None
    } for p in all_permissions]


@router.post("/{user_id}/permissions/temporal")
async def grant_timed_access(
    user_id: str,
    request: TemporalAccessRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Grant limited-time access to a service"""
    target_user = await User.get(user_id)
    await AccessControlService.grant_temporal_access(
        current_user, target_user, request.permission_id, request.duration_hours
    )
    return {"message": f"Temporal access granted for {request.duration_hours} hours"}


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a user (Admins delete directly, Staff trigger approval)"""

    # 1. Check permission via Access Control Service
    can_perform, reason = await AccessControlService.can_user_perform_action(
        user=current_user,
        module="users",
        action="delete",
        resource="user"
    )

    if not can_perform:
        if reason == "APPROVAL_REQUIRED":
            raise ApprovalRequired("User deletion requires admin confirmation")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=reason)

    # 2. Perform soft deletion
    user = await User.get(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user.is_deleted = True
    user.is_active = False
    user.updated_at = datetime.now(timezone.utc)
    await user.save()

    return {"message": "User deleted successfully"}
