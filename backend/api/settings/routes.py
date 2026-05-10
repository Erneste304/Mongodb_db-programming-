"""
System Settings API Routes
Superadmin controls for system configuration and business rules
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from backend.models.system_settings import SystemSettings
from backend.core.security import get_current_user, require_role_level
from backend.models.user import User
from backend.services.audit_service import AuditLogService

router = APIRouter(prefix="/settings", tags=["settings"])


class SystemSettingsRequest(BaseModel):
    # Fuel Pricing Settings
    default_vat_percentage: Optional[float] = 18
    price_update_approval_required: Optional[bool] = True
    max_price_change_percentage: Optional[float] = 10
    
    # Inventory Settings
    low_fuel_threshold_percentage: Optional[float] = 20
    critical_fuel_threshold_percentage: Optional[float] = 10
    delivery_notification_required: Optional[bool] = True
    
    # Transaction Settings
    transaction_void_approval_required: Optional[bool] = True
    large_payment_threshold: Optional[float] = 1000000
    cash_limit_per_transaction: Optional[float] = 500000
    
    # Approval Settings
    approval_timeout_hours: Optional[int] = 24
    auto_approve_small_amounts: Optional[bool] = False
    
    # Audit Settings
    audit_log_retention_days: Optional[int] = 365
    blind_spot_audit_enabled: Optional[bool] = True
    
    # Station Settings
    station_name: Optional[str] = "Petroleum Station"
    station_code: Optional[str] = "PS-001"
    station_address: Optional[str] = None
    station_phone: Optional[str] = None
    station_email: Optional[str] = None
    tin_number: Optional[str] = None
    
    # Multi-station Settings
    multi_station_enabled: Optional[bool] = False
    
    # Business Hours
    business_hours_start: Optional[str] = "06:00"
    business_hours_end: Optional[str] = "22:00"
    
    # Commission Settings
    default_commission_percentage: Optional[float] = 2


class SystemSettingsResponse(BaseModel):
    settings_id: str
    station_name: str
    station_code: str
    station_address: Optional[str]
    station_phone: Optional[str]
    station_email: Optional[str]
    tin_number: Optional[str]
    default_vat_percentage: float
    low_fuel_threshold_percentage: float
    critical_fuel_threshold_percentage: float
    large_payment_threshold: float
    business_hours_start: str
    business_hours_end: str
    multi_station_enabled: bool
    updated_by: str
    updated_at: datetime


@router.get("/system", response_model=SystemSettingsResponse)
async def get_system_settings(
    current_user: User = Depends(get_current_user)
):
    """Get current system settings"""
    
    settings = await SystemSettings.find_one({"settings_id": "system_settings"})
    
    if not settings:
        # Create default settings if none exist
        settings = SystemSettings(
            settings_id="system_settings",
            updated_by=str(current_user.id)
        )
        await settings.insert()
    
    return SystemSettingsResponse(
        settings_id=settings.settings_id,
        station_name=settings.station_name,
        station_code=settings.station_code,
        station_address=settings.station_address,
        station_phone=settings.station_phone,
        station_email=settings.station_email,
        tin_number=settings.tin_number,
        default_vat_percentage=settings.default_vat_percentage,
        low_fuel_threshold_percentage=settings.low_fuel_threshold_percentage,
        critical_fuel_threshold_percentage=settings.critical_fuel_threshold_percentage,
        large_payment_threshold=settings.large_payment_threshold,
        business_hours_start=settings.business_hours_start,
        business_hours_end=settings.business_hours_end,
        multi_station_enabled=settings.multi_station_enabled,
        updated_by=settings.updated_by,
        updated_at=settings.updated_at
    )


@router.put("/system", response_model=SystemSettingsResponse)
async def update_system_settings(
    request: SystemSettingsRequest,
    current_user: User = Depends(require_role_level(1))
):
    """Update system settings - SUPERADMIN ONLY"""
    
    settings = await SystemSettings.find_one({"settings_id": "system_settings"})
    
    if not settings:
        settings = SystemSettings(
            settings_id="system_settings",
            updated_by=str(current_user.id)
        )
    
    # Store old values for audit
    old_values = {
        "station_name": settings.station_name,
        "large_payment_threshold": settings.large_payment_threshold,
        "low_fuel_threshold_percentage": settings.low_fuel_threshold_percentage
    }
    
    # Update all fields
    update_data = request.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    
    settings.updated_by = str(current_user.id)
    settings.updated_at = datetime.utcnow()
    
    await settings.save()
    
    # Log the action
    await AuditLogService.log_action(
        user=current_user,
        action="updated_system_settings",
        resource_type="system_settings",
        resource_id=settings.settings_id,
        old_value=old_values,
        new_value=update_data
    )
    
    return SystemSettingsResponse(
        settings_id=settings.settings_id,
        station_name=settings.station_name,
        station_code=settings.station_code,
        station_address=settings.station_address,
        station_phone=settings.station_phone,
        station_email=settings.station_email,
        tin_number=settings.tin_number,
        default_vat_percentage=settings.default_vat_percentage,
        low_fuel_threshold_percentage=settings.low_fuel_threshold_percentage,
        critical_fuel_threshold_percentage=settings.critical_fuel_threshold_percentage,
        large_payment_threshold=settings.large_payment_threshold,
        business_hours_start=settings.business_hours_start,
        business_hours_end=settings.business_hours_end,
        multi_station_enabled=settings.multi_station_enabled,
        updated_by=settings.updated_by,
        updated_at=settings.updated_at
    )


@router.get("/thresholds")
async def get_inventory_thresholds(
    current_user: User = Depends(get_current_user)
):
    """Get inventory alert thresholds"""
    
    settings = await SystemSettings.find_one({"settings_id": "system_settings"})
    
    if not settings:
        return {
            "low_fuel_threshold_percentage": 20,
            "critical_fuel_threshold_percentage": 10
        }
    
    return {
        "low_fuel_threshold_percentage": settings.low_fuel_threshold_percentage,
        "critical_fuel_threshold_percentage": settings.critical_fuel_threshold_percentage,
        "delivery_notification_required": settings.delivery_notification_required
    }


@router.get("/business-rules")
async def get_business_rules(
    current_user: User = Depends(get_current_user)
):
    """Get business rules for transaction processing"""
    
    settings = await SystemSettings.find_one({"settings_id": "system_settings"})
    
    if not settings:
        return {
            "large_payment_threshold": 1000000,
            "cash_limit_per_transaction": 500000,
            "transaction_void_approval_required": True
        }
    
    return {
        "large_payment_threshold": settings.large_payment_threshold,
        "cash_limit_per_transaction": settings.cash_limit_per_transaction,
        "transaction_void_approval_required": settings.transaction_void_approval_required,
        "approval_timeout_hours": settings.approval_timeout_hours,
        "auto_approve_small_amounts": settings.auto_approve_small_amounts
    }
