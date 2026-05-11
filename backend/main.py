from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
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


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    db.connect()
    await db.init_beanie()
    yield
    # Shutdown
    db.close()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)

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
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers
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


@app.get("/")
async def root():
    return {
        "message": "Petroleum Station Management System API",
        "version": settings.APP_VERSION
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
