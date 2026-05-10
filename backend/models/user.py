from beanie import Document, Link
from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoleLevel(str, Enum):
    SUPERADMIN = "superadmin"
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    RECEPTIONIST = "receptionist"
    INVENTORY_MANAGER = "inventory_manager"
    STAFF = "staff"
    CUSTOMER = "customer"


class Role(Document):
    name: str = Field(..., unique=True)
    description: Optional[str] = None
    level: int = Field(..., description="Hierarchy level: 1=Super, 2=Admin, 3=Accountant, 4=Staff")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "roles"


class Permission(Document):
    module: str = Field(..., description="sales, inventory, finance, reports, settings")
    action: str = Field(..., description="create, read, update, delete, approve")
    resource: str = Field(..., description="transaction, user, report, etc.")
    requires_approval: bool = Field(default=False)
    approval_role_level: Optional[int] = Field(None, description="Which role level can approve")
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "permissions"


class UserPermission(Document):
    user_id: str = Field(..., description="Reference to User ID")
    permission_id: Link[Permission]
    is_enabled: bool = Field(default=True)
    granted_by: Optional[str] = Field(None, description="User ID who granted this permission")
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = Field(None, description="Temporal access expiration")
    
    class Settings:
        collection_name = "user_permissions"


class User(Document):
    username: str = Field(..., unique=True)
    email: Optional[str] = Field(None, unique=True)
    password_hash: str = Field(...)
    role: Link[Role]
    is_active: bool = Field(default=True)
    is_deleted: bool = Field(default=False)
    created_by: Optional[str] = Field(None, description="User ID who created this user")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    # Staff-specific fields
    employee_id: Optional[str] = Field(None)
    full_name: Optional[str] = Field(None)
    phone: Optional[str] = Field(None)
    station_id: Optional[str] = Field(None)
    salary: Optional[float] = Field(None)
    contract_type: Optional[str] = Field(None)
    start_date: Optional[datetime] = Field(None)
    
    class Settings:
        collection_name = "users"
    
    class Config:
        use_enum_values = True
