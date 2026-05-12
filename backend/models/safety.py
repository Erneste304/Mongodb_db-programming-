"""
Safety and Storage Conditions Models
For ensuring proper storage conditions and safety
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class SafetyCheckType(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    INCIDENT = "incident"


class SafetyStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    PENDING = "pending"


class SafetyCheck(Document):
    """Safety and storage condition checks"""
    check_id: str = Field(..., unique=True)
    check_type: SafetyCheckType = Field(...)
    tank_id: Optional[str] = Field(None)
    station_id: str = Field(...)
    
    # Checklist items
    fire_extinguishers_operational: bool = Field(default=False)
    spill_kit_available: bool = Field(default=False)
    emergency_exits_clear: bool = Field(default=False)
    no_smoking_signs_visible: bool = Field(default=False)
    lighting_functional: bool = Field(default=False)
    ventilation_working: bool = Field(default=False)
    tank_leaks_detected: bool = Field(default=False)
    pipe_connections_secure: bool = Field(default=False)
    grounding_system_ok: bool = Field(default=False)
    
    # Temperature monitoring
    ambient_temperature: Optional[float] = Field(None, description="Celsius")
    tank_temperature: Optional[float] = Field(None, description="Celsius")
    
    # Storage conditions
    storage_area_clean: bool = Field(default=False)
    hazardous_materials_labeled: bool = Field(default=False)
    safety_data_sheets_available: bool = Field(default=False)
    
    # Overall status
    overall_status: SafetyStatus = Field(default=SafetyStatus.PENDING)
    
    # Performed by
    checked_by: str = Field(...)
    checked_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Issues
    issues_found: Optional[str] = Field(None)
    corrective_actions: Optional[str] = Field(None)
    resolved_by: Optional[str] = Field(None)
    resolved_at: Optional[datetime] = Field(None)
    
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "safety_checks"


class SafetyIncident(Document):
    """Safety incidents and near-misses"""
    incident_id: str = Field(..., unique=True)
    incident_type: str = Field(..., description="spill, leak, fire, near_miss, equipment_failure")
    severity: str = Field(..., description="low, medium, high, critical")
    
    # Location
    tank_id: Optional[str] = Field(None)
    location_description: str = Field(...)
    
    # Incident details
    incident_date: datetime = Field(default_factory=datetime.utcnow)
    description: str = Field(...)
    immediate_action_taken: str = Field(...)
    
    # Impact
    fuel_loss_liters: Optional[float] = Field(None)
    estimated_cost: Optional[float] = Field(None)
    
    # Investigation
    investigated_by: Optional[str] = Field(None)
    investigation_date: Optional[datetime] = Field(None)
    root_cause: Optional[str] = Field(None)
    
    # Resolution
    corrective_actions: Optional[str] = Field(None)
    resolved: bool = Field(default=False)
    resolved_at: Optional[datetime] = Field(None)
    
    # Reporting
    reported_to_rura: bool = Field(default=False)
    rura_reference_number: Optional[str] = Field(None)
    
    created_by: str = Field(...)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "safety_incidents"
