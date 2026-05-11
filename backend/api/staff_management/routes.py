"""
Staff Management API Routes
Admin controls for schedules, attendance, timesheets, operations, safety, etc.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, time, timedelta, timezone
from backend.models.staff_management import (
    StaffSchedule, AttendanceRecord, Timesheet,
    StationOperationLog, SafetyComplianceRecord,
    PumpCalibrationRecord, SupplierDelivery, CustomerComplaint,
    ShiftStatus, AttendanceStatus
)
from backend.core.security import get_current_user, require_role_level
from backend.models.user import User
from backend.services.audit_service import AuditLogService

router = APIRouter(prefix="/staff-management", tags=["staff-management"])


# ==================== STAFF SCHEDULES ====================

class CreateScheduleRequest(BaseModel):
    user_id: str
    shift_date: datetime
    start_time: time
    end_time: time
    station_id: Optional[str] = None
    role_during_shift: str
    notes: Optional[str] = None


@router.post("/schedules")
async def create_schedule(
    request: CreateScheduleRequest,
    current_user: User = Depends(require_role_level(2))  # Admin+
):
    """Create staff work schedule - Admin only"""

    schedule = StaffSchedule(
        schedule_id=f"SCH-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        user_id=request.user_id,
        shift_date=request.shift_date,
        start_time=request.start_time,
        end_time=request.end_time,
        station_id=request.station_id,
        role_during_shift=request.role_during_shift,
        created_by=str(current_user.id),
        notes=request.notes
    )

    await schedule.insert()

    await AuditLogService.log_action(
        user=current_user,
        action="created_staff_schedule",
        resource_type="staff_schedule",
        resource_id=str(schedule.id),
        old_value={},
        new_value={
            "user_id": request.user_id,
            "shift_date": request.shift_date.isoformat(),
            "role": request.role_during_shift
        }
    )

    return {"message": "Schedule created", "schedule_id": schedule.schedule_id}


@router.get("/schedules/{user_id}")
async def get_staff_schedule(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Get staff schedule for a user"""

    query = {"user_id": user_id}
    if start_date and end_date:
        query["shift_date"] = {"$gte": start_date, "$lte": end_date}

    schedules = await StaffSchedule.find(query).sort("-shift_date").to_list()

    return [
        {
            "schedule_id": s.schedule_id,
            "shift_date": s.shift_date,
            "start_time": s.start_time.isoformat(),
            "end_time": s.end_time.isoformat(),
            "role": s.role_during_shift,
            "status": s.status.value
        }
        for s in schedules
    ]


# ==================== ATTENDANCE ====================

class RecordAttendanceRequest(BaseModel):
    schedule_id: str
    user_id: str
    status: AttendanceStatus
    check_in_time: Optional[datetime] = None
    check_out_time: Optional[datetime] = None
    notes: Optional[str] = None


@router.post("/attendance")
async def record_attendance(
    request: RecordAttendanceRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Record staff attendance - Admin only"""

    # Calculate hours worked
    hours_worked = None
    if request.check_in_time and request.check_out_time:
        hours_worked = (request.check_out_time -
                        request.check_in_time).total_seconds() / 3600

    attendance = AttendanceRecord(
        attendance_id=f"ATT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        user_id=request.user_id,
        schedule_id=request.schedule_id,
        attendance_date=datetime.now(timezone.utc),
        status=request.status,
        check_in_time=request.check_in_time,
        check_out_time=request.check_out_time,
        hours_worked=hours_worked,
        approved_by=str(current_user.id),
        notes=request.notes
    )

    await attendance.insert()

    return {"message": "Attendance recorded", "attendance_id": attendance.attendance_id}


@router.get("/attendance/{user_id}")
async def get_attendance(
    user_id: str,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Get attendance records for a staff member"""

    query = {"user_id": user_id}
    if start_date and end_date:
        query["attendance_date"] = {"$gte": start_date, "$lte": end_date}

    records = await AttendanceRecord.find(query).sort("-attendance_date").to_list()

    return [
        {
            "attendance_id": r.attendance_id,
            "date": r.attendance_date,
            "status": r.status.value,
            "check_in": r.check_in_time,
            "check_out": r.check_out_time,
            "hours_worked": r.hours_worked
        }
        for r in records
    ]


@router.get("/attendance/all")
async def get_all_attendance(
    current_user: User = Depends(require_role_level(2))
):
    """Get all attendance records (Admin oversight)"""
    # Use find_all() to retrieve multiple records and sort them
    records = await AttendanceRecord.find_all().sort("-attendance_date").to_list()
    return [
        {
            "employee": r.user_id,  # Assuming user_id can be mapped to employee name later
            "date": r.attendance_date.isoformat().split('T')[0],
            "status": r.status.value,
            "check_in": r.check_in_time.isoformat() if r.check_in_time else None,
            "check_out": r.check_out_time.isoformat() if r.check_out_time else None,
            "hours_worked": round(r.hours_worked, 2) if r.hours_worked else 0,
        }
        for r in records
    ]


# ==================== TIMESHEETS ====================

@router.post("/timesheets/generate/{user_id}")
async def generate_timesheet(
    user_id: str,
    pay_period_start: datetime,
    pay_period_end: datetime,
    hourly_rate: float,
    current_user: User = Depends(require_role_level(2))
):
    """Generate timesheet for payroll - Admin only"""

    # Get attendance records for the period
    attendance_records = await AttendanceRecord.find({
        "user_id": user_id,
        "attendance_date": {"$gte": pay_period_start, "$lte": pay_period_end}
    }).to_list()

    # Calculate totals
    total_hours = sum(r.hours_worked or 0 for r in attendance_records)
    regular_hours = min(total_hours, 40)  # Assuming 40-hour work week
    overtime_hours = max(0, total_hours - 40)

    days_present = len(
        [r for r in attendance_records if r.status == AttendanceStatus.PRESENT])
    days_absent = len(
        [r for r in attendance_records if r.status == AttendanceStatus.ABSENT])
    days_late = len(
        [r for r in attendance_records if r.status == AttendanceStatus.LATE])

    regular_pay = regular_hours * hourly_rate
    overtime_pay = overtime_hours * hourly_rate * 1.5  # 1.5x for overtime
    total_pay = regular_pay + overtime_pay

    timesheet = Timesheet(
        timesheet_id=f"TS-{user_id}-{pay_period_start.strftime('%Y%m')}",
        user_id=user_id,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        total_hours=total_hours,
        regular_hours=regular_hours,
        overtime_hours=overtime_hours,
        days_present=days_present,
        days_absent=days_absent,
        days_late=days_late,
        hourly_rate=hourly_rate,
        regular_pay=regular_pay,
        overtime_pay=overtime_pay,
        total_pay=total_pay
    )

    await timesheet.insert()

    return {
        "timesheet_id": timesheet.timesheet_id,
        "total_hours": total_hours,
        "regular_hours": regular_hours,
        "overtime_hours": overtime_hours,
        "total_pay": total_pay
    }


@router.get("/timesheets/pending")
async def get_pending_timesheets(
    current_user: User = Depends(require_role_level(2))
):
    """Get all pending timesheets for admin approval"""

    timesheets = await Timesheet.find({"status": "pending"}).to_list()

    return [
        {
            "timesheet_id": t.timesheet_id,
            "user_id": t.user_id,
            "pay_period": f"{t.pay_period_start.date()} to {t.pay_period_end.date()}",
            "total_hours": t.total_hours,
            "total_pay": t.total_pay,
            "status": t.status
        }
        for t in timesheets
    ]


@router.post("/timesheets/{timesheet_id}/approve")
async def approve_timesheet(
    timesheet_id: str,
    notes: Optional[str] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Approve timesheet - Admin only"""

    timesheet = await Timesheet.find_one({"timesheet_id": timesheet_id})
    if not timesheet:
        raise HTTPException(status_code=404, detail="Timesheet not found")

    timesheet.status = "approved"
    timesheet.approved_by = str(current_user.id)
    timesheet.approved_at = datetime.now(timezone.utc)
    timesheet.admin_notes = notes

    await timesheet.save()

    await AuditLogService.log_action(
        user=current_user,
        action="approved_timesheet",
        resource_type="timesheet",
        resource_id=str(timesheet.id),
        old_value={"status": "pending"},
        new_value={"status": "approved", "total_pay": timesheet.total_pay}
    )

    return {"message": "Timesheet approved"}


# ==================== STATION OPERATIONS ====================

class StationOperationRequest(BaseModel):
    station_id: str
    operation_type: str  # "opening" or "closing"
    pumps_operational: bool
    tanks_checked: bool
    safety_equipment_checked: bool
    cash_register_ready: bool
    staff_present: List[str]
    issues_noted: Optional[str] = None
    handover_notes: Optional[str] = None

    # For closing only
    daily_sales_total: Optional[float] = None
    cash_counted: Optional[bool] = None
    tanks_readings: Optional[dict] = None
    equipment_shutdown: Optional[bool] = None
    security_activated: Optional[bool] = None


@router.post("/station-operations")
async def record_station_operation(
    request: StationOperationRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Record station opening or closing - Admin only"""

    operation = StationOperationLog(
        operation_id=f"OP-{request.operation_type.upper()}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        station_id=request.station_id,
        operation_type=request.operation_type,
        performed_by=str(current_user.id),
        pumps_operational=request.pumps_operational,
        tanks_checked=request.tanks_checked,
        safety_equipment_checked=request.safety_equipment_checked,
        cash_register_ready=request.cash_register_ready,
        staff_present=request.staff_present,
        daily_sales_total=request.daily_sales_total,
        cash_counted=request.cash_counted,
        tanks_readings=request.tanks_readings,
        equipment_shutdown=request.equipment_shutdown,
        security_activated=request.security_activated,
        issues_noted=request.issues_noted,
        handover_notes=request.handover_notes
    )

    await operation.insert()

    await AuditLogService.log_action(
        user=current_user,
        action=f"station_{request.operation_type}",
        resource_type="station_operation",
        resource_id=str(operation.id),
        old_value={},
        new_value={"station_id": request.station_id,
                   "operation": request.operation_type}
    )

    return {
        "message": f"Station {request.operation_type} recorded",
        "operation_id": operation.operation_id
    }


@router.get("/station-operations")
async def get_station_operations(
    station_id: Optional[str] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Get station operations log - Admin oversight"""

    query = {}
    if station_id:
        query["station_id"] = station_id

    logs = await StationOperationLog.find(query).to_list()

    return [
        {
            "operation_id": l.operation_id,
            "station_id": l.station_id,
            "operation_type": l.operation_type,
            "timestamp": l.timestamp,
            "performed_by": l.performed_by,
            "notes": l.issues_noted
        }
        for l in logs
    ]


# ==================== SAFETY COMPLIANCE ====================

class SafetyInspectionRequest(BaseModel):
    station_id: str
    inspection_type: str
    fire_extinguishers_ok: bool
    spill_kit_available: bool
    no_smoking_signs_visible: bool
    emergency_exits_clear: bool
    pumps_no_leaks: bool
    tanks_secure: bool
    safety_equipment_functional: bool
    issues_found: Optional[str] = None
    corrective_actions: Optional[str] = None


@router.post("/safety-inspections")
async def record_safety_inspection(
    request: SafetyInspectionRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Record safety inspection - Admin only"""

    # Determine if passed or failed
    status = "pass"
    checks = [
        request.fire_extinguishers_ok,
        request.spill_kit_available,
        request.no_smoking_signs_visible,
        request.emergency_exits_clear,
        request.pumps_no_leaks,
        request.tanks_secure,
        request.safety_equipment_functional
    ]

    if not all(checks) or request.issues_found:
        status = "fail"

    inspection = SafetyComplianceRecord(
        record_id=f"SAF-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        station_id=request.station_id,
        inspection_type=request.inspection_type,
        inspected_by=str(current_user.id),
        fire_extinguishers_ok=request.fire_extinguishers_ok,
        spill_kit_available=request.spill_kit_available,
        no_smoking_signs_visible=request.no_smoking_signs_visible,
        emergency_exits_clear=request.emergency_exits_clear,
        pumps_no_leaks=request.pumps_no_leaks,
        tanks_secure=request.tanks_secure,
        safety_equipment_functional=request.safety_equipment_functional,
        issues_found=request.issues_found,
        corrective_actions=request.corrective_actions,
        status=status
    )

    await inspection.insert()

    return {
        "message": "Safety inspection recorded",
        "record_id": inspection.record_id,
        "status": status
    }


@router.get("/safety-inspections/{station_id}")
async def get_safety_inspections(
    station_id: str,
    current_user: User = Depends(require_role_level(2))
):
    """Get safety inspections for a station"""

    inspections = await SafetyComplianceRecord.find({"station_id": station_id}).to_list()

    return [
        {
            "record_id": i.record_id,
            "inspection_type": i.inspection_type,
            "date": i.inspection_date,
            "status": i.status,
            "inspected_by": i.inspected_by
        }
        for i in inspections
    ]


# ==================== PUMP CALIBRATION ====================

@router.get("/pump-calibrations/pending")
async def get_pending_calibrations(
    current_user: User = Depends(require_role_level(2))
):
    """Get pumps due for calibration - Admin oversight"""

    # Get calibrations due within next 30 days
    thirty_days_from_now = datetime.now(timezone.utc) + timedelta(days=30)

    calibrations = await PumpCalibrationRecord.find({
        "next_calibration_due": {"$lte": thirty_days_from_now}
    }).to_list()

    return [
        {
            "calibration_id": c.calibration_id,
            "pump_id": c.pump_id,
            "tank_id": c.tank_id,
            "next_due": c.next_calibration_due,
            "certificate_number": c.certificate_number
        }
        for c in calibrations
    ]


# ==================== SUPPLIER DELIVERIES ====================

class CreateDeliveryOrderRequest(BaseModel):
    supplier_id: str
    supplier_name: str
    fuel_type: str
    quantity_ordered: float
    tank_id: str
    expected_delivery_date: datetime
    notes: Optional[str] = None


@router.post("/supplier-deliveries/order")
async def create_delivery_order(
    request: CreateDeliveryOrderRequest,
    current_user: User = Depends(require_role_level(2))
):
    """Create supplier delivery order - Admin only"""

    delivery = SupplierDelivery(
        delivery_id=f"DEL-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        supplier_id=request.supplier_id,
        supplier_name=request.supplier_name,
        ordered_by=str(current_user.id),
        fuel_type=request.fuel_type,
        quantity_ordered=request.quantity_ordered,
        expected_delivery_date=request.expected_delivery_date,
        tank_id=request.tank_id,
        notes=request.notes
    )

    await delivery.insert()

    return {
        "message": "Delivery order created",
        "delivery_id": delivery.delivery_id
    }


@router.get("/supplier-deliveries")
async def get_delivery_orders(
    status: Optional[str] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Get delivery orders - Admin oversight"""

    query = {}
    if status:
        query["status"] = status

    deliveries = await SupplierDelivery.find(query).to_list()

    return [
        {
            "delivery_id": d.delivery_id,
            "supplier_name": d.supplier_name,
            "fuel_type": d.fuel_type,
            "quantity_ordered": d.quantity_ordered,
            "status": d.status,
            "expected_date": d.expected_delivery_date
        }
        for d in deliveries
    ]


# ==================== CUSTOMER COMPLAINTS ====================

class CreateComplaintRequest(BaseModel):
    customer_name: str
    customer_phone: Optional[str] = None
    complaint_type: str
    description: str
    severity: str = "medium"
    related_transaction_id: Optional[str] = None
    pump_number: Optional[int] = None


@router.post("/complaints")
async def create_complaint(
    request: CreateComplaintRequest,
    current_user: User = Depends(get_current_user)
):
    """Create customer complaint - Staff and Admin"""

    complaint = CustomerComplaint(
        complaint_id=f"COMP-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}",
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        complaint_type=request.complaint_type,
        description=request.description,
        severity=request.severity,
        related_transaction_id=request.related_transaction_id,
        pump_number=request.pump_number,
        reported_by=str(
            current_user.id) if current_user.role != "customer" else None
    )

    await complaint.insert()

    return {
        "message": "Complaint recorded",
        "complaint_id": complaint.complaint_id
    }


@router.get("/complaints")
async def get_complaints(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Get customer complaints - Admin oversight"""

    query = {}
    if status:
        query["status"] = status
    if severity:
        query["severity"] = severity

    complaints = await CustomerComplaint.find(query).to_list()

    return [
        {
            "complaint_id": c.complaint_id,
            "customer_name": c.customer_name,
            "type": c.complaint_type,
            "severity": c.severity,
            "status": c.status,
            "reported_at": c.reported_at,
            "assigned_to": c.assigned_to
        }
        for c in complaints
    ]


@router.post("/complaints/{complaint_id}/assign")
async def assign_complaint(
    complaint_id: str,
    admin_id: str,
    current_user: User = Depends(require_role_level(2))
):
    """Assign complaint to admin for resolution"""

    complaint = await CustomerComplaint.find_one({"complaint_id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.assigned_to = admin_id
    complaint.status = "investigating"

    await complaint.save()

    return {"message": "Complaint assigned", "assigned_to": admin_id}


@router.post("/complaints/{complaint_id}/resolve")
async def resolve_complaint(
    complaint_id: str,
    resolution: str,
    refund_amount: Optional[float] = None,
    current_user: User = Depends(require_role_level(2))
):
    """Resolve customer complaint - Admin only"""

    complaint = await CustomerComplaint.find_one({"complaint_id": complaint_id})
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.resolution = resolution
    complaint.resolved_by = str(current_user.id)
    complaint.resolved_at = datetime.now(timezone.utc)
    complaint.status = "resolved"

    if refund_amount:
        complaint.refund_amount = refund_amount
        complaint.refund_approved_by = str(current_user.id)

    await complaint.save()

    await AuditLogService.log_action(
        user=current_user,
        action="resolved_complaint",
        resource_type="complaint",
        resource_id=str(complaint.id),
        old_value={"status": "investigating"},
        new_value={"status": "resolved", "refund": refund_amount}
    )

    return {"message": "Complaint resolved"}
