from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from beanie.exceptions import CollectionWasNotInitialized
from backend.core.config import settings
from backend.core.database import db
from backend.core.exceptions import PermissionDenied, ApprovalRequired, ResourceNotFound
from backend.core.error_handlers import (
    permission_denied_handler,
    approval_required_handler,
    resource_not_found_handler,
    validation_exception_handler,
    generic_exception_handler
)
from backend.api.auth.routes import router as auth_router
from backend.api.users.routes import router as users_router
from backend.api.approvals.routes import router as approvals_router
from backend.api.sales.routes import router as sales_router
from backend.api.inventory.routes import router as inventory_router
from backend.api.finance.routes import router as finance_router
from backend.api.reports.routes import router as reports_router
from backend.api.pricing.routes import router as pricing_router
from backend.api.settings.routes import router as settings_router
from backend.api.staff_management.routes import router as staff_management_router
from backend.api.accounting.routes import router as accounting_router
from backend.api.complaints.routes import router as complaints_router
from backend.api.shop.routes import router as shop_router
from backend.api.pump.routes import router as pump_router
from backend.api.shift.routes import router as shift_router
from backend.api.consumption.routes import router as consumption_router
from backend.api.lubricant.routes import router as lubricant_router
from backend.api.supplier.routes import router as supplier_router
from backend.api.safety.routes import router as safety_router
from backend.api.stock_count.routes import router as stock_count_router
from backend.api.inspection.routes import router as inspection_router
from backend.api.billing.routes import router as billing_router
from backend.api.visitor.routes import router as visitor_router
from backend.api.partner.routes import router as partner_router
from backend.api.station.routes import router as station_router
from backend.api.expenditure.routes import router as expenditure_router
from backend.api.discrepancy.routes import router as discrepancy_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure models are imported for initialization
    from backend.models.user import User, Role, Permission, UserPermission
    from backend.models.sales import Transaction, Customer
    from backend.models.shift import Shift
    from backend.models.staff_management import (
        CustomerComplaint, StaffSchedule, AttendanceRecord, Timesheet,
        StationOperationLog, SafetyComplianceRecord, PumpCalibrationRecord,
        SupplierDelivery
    )
    from backend.models.shop import ShopItem, ShopSale
    from backend.models.pump import Pump
    from backend.models.pricing import FuelPricing, PartnerAgreement
    from backend.models.audit_log import AuditLog
    from backend.models.system_settings import SystemSettings
    from backend.models.approval_request import ApprovalRequest
    from backend.models.accounting import (
        DailyClosing, CommissionCalculation, BankReconciliation,
        AccountsReceivable, AccountsPayable, TaxRecord,
        FuelCostTracking, CorporateInvoice, RURAComplianceReport
    )
    from backend.models.inventory import Tank, FuelDelivery, InventoryRecord

    models = [
        User,
        Role,
        Permission,
        UserPermission,
        Transaction,
        Customer,
        Shift,
        CustomerComplaint,
        StaffSchedule,
        AttendanceRecord,
        Timesheet,
        StationOperationLog,
        SafetyComplianceRecord,
        PumpCalibrationRecord,
        SupplierDelivery,
        ShopItem,
        ShopSale,
        Pump,
        FuelPricing,
        PartnerAgreement,
        AuditLog,
        SystemSettings,
        ApprovalRequest,
        DailyClosing,
        CommissionCalculation,
        BankReconciliation,
        AccountsReceivable,
        AccountsPayable,
        TaxRecord,
        FuelCostTracking,
        CorporateInvoice,
        RURAComplianceReport,
        Tank,
        FuelDelivery,
        InventoryRecord
    ]

    # Re-initialize to be safe (idempotent)
    db.connect()
    await db.init_beanie(models)
    yield
    # Shutdown
    db.close()


app = FastAPI(title=settings.APP_NAME,
              version=settings.APP_VERSION, lifespan=lifespan)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register error handlers
app.add_exception_handler(PermissionDenied, permission_denied_handler)
app.add_exception_handler(ApprovalRequired, approval_required_handler)
app.add_exception_handler(ResourceNotFound, resource_not_found_handler)


@app.exception_handler(CollectionWasNotInitialized)
async def beanie_not_initialized_handler(request: Request, exc: CollectionWasNotInitialized):
    """Handle Beanie initialization race conditions during app startup"""
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "Database initialization in progress. Please wait a few seconds."},
        headers={"Retry-After": "5"}
    )
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Middleware


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    return response


# Include routers (after handlers are registered)
app.include_router(auth_router)
app.include_router(users_router)
app.include_router(approvals_router)
app.include_router(sales_router)
app.include_router(inventory_router)
app.include_router(finance_router)
app.include_router(reports_router)
app.include_router(pricing_router)
app.include_router(settings_router)
app.include_router(staff_management_router)
app.include_router(accounting_router)
app.include_router(complaints_router)
app.include_router(shop_router)
app.include_router(pump_router)
app.include_router(shift_router)
app.include_router(consumption_router)
app.include_router(lubricant_router)
app.include_router(supplier_router)
app.include_router(safety_router)
app.include_router(stock_count_router)
app.include_router(inspection_router)
app.include_router(billing_router)
app.include_router(visitor_router)
app.include_router(partner_router)
app.include_router(station_router)
app.include_router(expenditure_router)
app.include_router(discrepancy_router)


@app.get("/")
async def root():
    return {
        "message": "Petroleum Station Management System API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
