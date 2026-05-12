"""
Discrepancy Investigation Model
For investigating fuel inventory vs sales discrepancies
"""

from beanie import Document
from pydantic import Field
from typing import Optional
from datetime import datetime
from enum import Enum


class DiscrepancyType(str, Enum):
    FUEL_LOSS = "fuel_loss"
    THEFT = "theft"
    LEAKAGE = "leakage"
    MEASUREMENT_ERROR = "measurement_error"
    RECORDING_ERROR = "recording_error"
    CALIBRATION_ISSUE = "calibration_issue"
    OTHER = "other"


class DiscrepancySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DiscrepancyStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Discrepancy(Document):
    """Discrepancy investigation records"""
    discrepancy_id: str = Field(..., unique=True)
    discrepancy_type: DiscrepancyType = Field(...)
    severity: DiscrepancySeverity = Field(...)
    
    # Location
    tank_id: Optional[str] = Field(None)
    pump_id: Optional[str] = Field(None)
    station_id: Optional[str] = Field(None)
    
    # Details
    description: str = Field(...)
    expected_amount: float = Field(...)
    actual_amount: float = Field(...)
    variance: float = Field(...)
    variance_percentage: float = Field(default=0)
    
    # Detection
    detected_date: datetime = Field(default_factory=datetime.utcnow)
    detected_by: str = Field(...)
    detection_method: str = Field(..., description="stock_count, system_alert, manual_report")
    
    # Investigation
    status: DiscrepancyStatus = Field(default=DiscrepancyStatus.OPEN)
    investigated_by: Optional[str] = Field(None)
    investigation_date: Optional[datetime] = Field(None)
    root_cause: Optional[str] = Field(None)
    
    # Resolution
    corrective_action: Optional[str] = Field(None)
    resolved_by: Optional[str] = Field(None)
    resolved_at: Optional[datetime] = Field(None)
    
    # Financial impact
    estimated_loss: Optional[float] = Field(None)
    recovered_amount: float = Field(default=0)
    
    # Evidence
    evidence_document_urls: list = Field(default_factory=list)
    witness_statements: list = Field(default_factory=list)
    
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "discrepancies"
