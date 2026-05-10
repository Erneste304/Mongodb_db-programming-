from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime


class SystemSettings(Document):
    """System settings and business rules configuration"""
    settings_id: str = Field(default="system_settings", unique=True)
    
    # Fuel Pricing Settings
    default_vat_percentage: float = Field(default=18, description="VAT percentage for Rwanda")
    price_update_approval_required: bool = Field(default=True, description="Require approval for price changes")
    max_price_change_percentage: float = Field(default=10, description="Maximum allowed price change without special approval")
    
    # Inventory Settings
    low_fuel_threshold_percentage: float = Field(default=20, description="Alert when tank below this %")
    critical_fuel_threshold_percentage: float = Field(default=10, description="Critical alert when tank below this %")
    delivery_notification_required: bool = Field(default=True, description="Notify when fuel delivery arrives")
    
    # Transaction Settings
    transaction_void_approval_required: bool = Field(default=True, description="Require approval to void transactions")
    large_payment_threshold: float = Field(default=1000000, description="Amount requiring admin approval in RWF")
    cash_limit_per_transaction: float = Field(default=500000, description="Maximum cash per transaction in RWF")
    
    # Approval Settings
    approval_timeout_hours: int = Field(default=24, description="Hours before approval request expires")
    auto_approve_small_amounts: bool = Field(default=False, description="Auto-approve amounts below threshold")
    
    # Audit Settings
    audit_log_retention_days: int = Field(default=365, description="Days to retain audit logs")
    blind_spot_audit_enabled: bool = Field(default=True, description="Users cannot see their own audit logs")
    
    # Station Settings
    station_name: str = Field(default="Petroleum Station")
    station_code: str = Field(default="PS-001")
    station_address: Optional[str] = Field(None)
    station_phone: Optional[str] = Field(None)
    station_email: Optional[str] = Field(None)
    tin_number: Optional[str] = Field(None, description="Tax Identification Number")
    
    # Multi-station Settings
    multi_station_enabled: bool = Field(default=False, description="Enable multi-station management")
    parent_station_id: Optional[str] = Field(None)
    
    # Business Hours
    business_hours_start: str = Field(default="06:00")
    business_hours_end: str = Field(default="22:00")
    
    # Payment Methods
    enabled_payment_methods: list[str] = Field(default=["cash", "mobile_money", "card", "credit"])
    mobile_money_providers: list[str] = Field(default=["MTN", "Airtel"])
    
    # Commission Settings
    default_commission_percentage: float = Field(default=2, description="Default commission on sales")
    
    updated_by: str = Field(..., description="User who updated settings")
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "system_settings"
