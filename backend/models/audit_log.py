from beanie import Document
from pydantic import Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class AuditLog(Document):
    user_id: str = Field(..., description="User who performed the action")
    action: str = Field(..., description="created_user, toggled_permission, etc.")
    resource_type: str = Field(..., description="user, transaction, report")
    resource_id: Optional[str] = Field(None)
    old_value: Optional[Dict[str, Any]] = Field(None)
    new_value: Optional[Dict[str, Any]] = Field(None)
    ip_address: Optional[str] = Field(None)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    visible_to_roles: List[int] = Field(default_factory=list)
    
    class Settings:
        collection_name = "audit_logs"
