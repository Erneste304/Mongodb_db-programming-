from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from passlib.context import CryptContext
from backend.models.user import User, Role, Permission, UserPermission
from backend.services.access_control import AccessControlService
from backend.services.audit_service import AuditLogService
from backend.core.security import get_current_user, require_role_level
from passlib.context import CryptContext

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
    
    # Check if username already exists
    existing_user = await User.find_one(User.username == request.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )
    
    # Get role
    role = await Role.find_one(Role.name == request.role_name)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role not found"
        )
    
    # Create user
    user = User(
        username=request.username,
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
        created_at=datetime.utcnow()
    )
    
    await user.insert()
    
    # Log the action
    # await AuditLogService.log_action(...)
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.name,
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
    users = await User.find_all(fetch_links=True).skip(skip).limit(limit).to_list()
    return [
        UserResponse(
            id=str(user.id),
            username=user.username,
            email=user.email,
            role=user.role.name,
            full_name=user.full_name,
            employee_id=user.employee_id,
            is_active=user.is_active,
            created_at=user.created_at
        )
        for user in users
    ]


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
        role=user.role.name,
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
    
    user.updated_at = datetime.utcnow()
    await user.save()
    
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        role=user.role.name,
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
