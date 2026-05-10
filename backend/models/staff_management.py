"""
Staff Management Models
For admin to manage staff scheduling, attendance, timesheets, and operations
"""

from beanie import Document
from pydantic import Field
from typing import Optional, List
from datetime import datetime, time
from enum import Enum


class ShiftStatus(str, Enum):
    SCHEDULED = "scheduled"
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AttendanceStatus(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    LATE = "late"
    ON_LEAVE = "on_leave"
    SICK = "sick"


class StaffSchedule(Document):
    """Staff work schedules and shifts"""
    schedule_id: str = Field(..., unique=True)
    user_id: str = Field(..., description="Staff member ID")
    shift_date: datetime
    start_time: time
    end_time: time
    station_id: Optional[str] = Field(None)
    role_during_shift: str = Field(..., description="Role during this shift")
    status: ShiftStatus = Field(default=ShiftStatus.SCHEDULED)
    created_by: str = Field(..., description="Admin who created the schedule")
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "staff_schedules"


class AttendanceRecord(Document):
    """Daily attendance tracking"""
    attendance_id: str = Field(..., unique=True)
    user_id: str = Field(...)
    schedule_id: str = Field(...)
    attendance_date: datetime
    status: AttendanceStatus
    check_in_time: Optional[datetime] = Field(None)
    check_out_time: Optional[datetime] = Field(None)
    hours_worked: Optional[float] = Field(None)
    check_in_method: Optional[str] = Field(None, description="biometric, card, manual")
    check_out_method: Optional[str] = Field(None)
    approved_by: Optional[str] = Field(None, description="Admin who approved attendance")
    notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "attendance_records"


class Timesheet(Document):
    """Employee timesheets for payroll"""
    timesheet_id: str = Field(..., unique=True)
    user_id: str = Field(...)
    pay_period_start: datetime
    pay_period_end: datetime
    total_hours: float = Field(default=0)
    regular_hours: float = Field(default=0)
    overtime_hours: float = Field(default=0)
    days_present: int = Field(default=0)
    days_absent: int = Field(default=0)
    days_late: int = Field(default=0)
    hourly_rate: float = Field(...)
    regular_pay: float = Field(default=0)
    overtime_pay: float = Field(default=0)
    total_pay: float = Field(default=0)
    approved_by: Optional[str] = Field(None)
    approved_at: Optional[datetime] = Field(None)
    status: str = Field(default="pending", description="pending, approved, rejected")
    admin_notes: Optional[str] = Field(None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "timesheets"


class StationOperationLog(Document):
    """Station opening/closing procedures"""
    operation_id: str = Field(..., unique=True)
    station_id: str = Field(...)
    operation_type: str = Field(..., description="opening, closing")
    performed_by: str = Field(..., description="Admin who performed the operation")
    performed_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Opening checks
    pumps_operational: Optional[bool] = Field(None)
    tanks_checked: Optional[bool] = Field(None)
    safety_equipment_checked: Optional[bool] = Field(None)
    cash_register_ready: Optional[bool] = Field(None)
    staff_present: Optional[List[str]] = Field(None)
    
    # Closing checks
    daily_sales_total: Optional[float] = Field(None)
    cash_counted: Optional[bool] = Field(None)
    tanks_readings: Optional[dict] = Field(None)
    equipment_shutdown: Optional[bool] = Field(None)
    security_activated: Optional[bool] = Field(None)
    
    issues_noted: Optional[str] = Field(None)
    handover_notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "station_operation_logs"


class SafetyComplianceRecord(Document):
    """Safety inspections and compliance records"""
    record_id: str = Field(..., unique=True)
    station_id: str = Field(...)
    inspection_type: str = Field(..., description="daily, weekly, monthly, incident")
    inspected_by: str = Field(..., description="Admin who performed inspection")
    inspection_date: datetime = Field(default_factory=datetime.utcnow)
    
    # Checklist items
    fire_extinguishers_ok: Optional[bool] = Field(None)
    spill_kit_available: Optional[bool] = Field(None)
    no_smoking_signs_visible: Optional[bool] = Field(None)
    emergency_exits_clear: Optional[bool] = Field(None)
    pumps_no_leaks: Optional[bool] = Field(None)
    tanks_secure: Optional[bool] = Field(None)
    safety_equipment_functional: Optional[bool] = Field(None)
    
    issues_found: Optional[str] = Field(None)
    corrective_actions: Optional[str] = Field(None)
    resolved_by: Optional[str] = Field(None)
    resolved_at: Optional[datetime] = Field(None)
    
    status: str = Field(default="pass", description="pass, fail, pending_correction")
    
    class Settings:
        collection_name = "safety_compliance_records"


class PumpCalibrationRecord(Document):
    """Pump calibration certificates and schedules"""
    calibration_id: str = Field(..., unique=True)
    pump_id: str = Field(...)
    tank_id: str = Field(...)
    
    # Calibration details
    calibration_date: datetime
    next_calibration_due: datetime
    calibrated_by: str = Field(..., description="Company or technician name")
    certificate_number: str = Field(...)
    
    # Measurements
    test_volume_dispensed: float
    expected_volume: float
    actual_volume: float
    variance_percentage: float
    within_tolerance: bool = Field(default=True)
    tolerance_percentage: float = Field(default=0.5)
    
    # Approval
    approved_by: Optional[str] = Field(None, description="Admin who approved")
    approved_at: Optional[datetime] = Field(None)
    
    notes: Optional[str] = Field(None)
    document_url: Optional[str] = Field(None, description="Certificate file URL")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Settings:
        collection_name = "pump_calibration_records"


class SupplierDelivery(Document):
    """Supplier fuel delivery coordination"""
    delivery_id: str = Field(..., unique=True)
    supplier_id: str = Field(...)
    supplier_name: str = Field(...)
    
    # Order details
    ordered_by: str = Field(..., description="Admin who placed order")
    ordered_at: datetime = Field(default_factory=datetime.utcnow)
    fuel_type: str = Field(...)
    quantity_ordered: float = Field(...)
    
    # Delivery details
    expected_delivery_date: datetime
    actual_delivery_date: Optional[datetime] = Field(None)
    quantity_received: Optional[float] = Field(None)
    tank_id: str = Field(...)
    
    # Status tracking
    status: str = Field(default="ordered", description="ordered, in_transit, delivered, cancelled")
    
    # Reception
    received_by: Optional[str] = Field(None)
    checked_by: Optional[str] = Field(None)
    quality_check_passed: Optional[bool] = Field(None)
    
    # Invoice
    invoice_number: Optional[str] = Field(None)
    unit_price: Optional[float] = Field(None)
    total_cost: Optional[float] = Field(None)
    
    notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "supplier_deliveries"


class CustomerComplaint(Document):
    """Customer complaints and escalations"""
    complaint_id: str = Field(..., unique=True)
    customer_id: Optional[str] = Field(None)
    customer_name: str = Field(...)
    customer_phone: Optional[str] = Field(None)
    
    # Complaint details
    complaint_type: str = Field(..., description="fuel_quality, service, pricing, pump_issue, other")
    description: str = Field(...)
    severity: str = Field(default="medium", description="low, medium, high, critical")
    
    # Related transaction
    related_transaction_id: Optional[str] = Field(None)
    pump_number: Optional[int] = Field(None)
    
    # Tracking
    reported_at: datetime = Field(default_factory=datetime.utcnow)
    reported_by: Optional[str] = Field(None, description="Staff who reported")
    
    assigned_to: Optional[str] = Field(None, description="Admin assigned to resolve")
    
    status: str = Field(default="open", description="open, investigating, resolved, escalated, closed")
    
    # Resolution
    resolution: Optional[str] = Field(None)
    resolved_by: Optional[str] = Field(None)
    resolved_at: Optional[datetime] = Field(None)
    
    # Compensation/refund if applicable
    refund_amount: Optional[float] = Field(None)
    refund_approved_by: Optional[str] = Field(None)
    
    admin_notes: Optional[str] = Field(None)
    
    class Settings:
        collection_name = "customer_complaints"
