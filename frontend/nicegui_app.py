"""
NiceGUI Application for Petroleum Station Management
Integrates with existing FastAPI backend
"""
from nicegui import ui, app as nicegui_app, app
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from config import Config
import os
from backend.models.user import User, Role
import httpx
from frontend.state import auth_state, dashboard_layout
from backend.core.database import db
from frontend.pages import superadmin, admin, accountant, inventory, receptionist, home


def login_page():
    """Login page UI"""
    with ui.card().classes('absolute-center w-96 p-6'):
        ui.label('Petroleum Station Management').classes(
            'text-2xl font-bold mb-4')
        ui.label('Login').classes('text-lg mb-4')

        username_input = ui.input('Username', placeholder='Enter username')
        password_input = ui.input(
            'Password', placeholder='Enter password', password=True)
        password_input.props('toggle-mask')

        async def handle_login():
            if await auth_state.login(username_input.value, password_input.value):
                ui.navigate.to('/dashboard')
            else:
                ui.notify(auth_state.error or 'Invalid credentials',
                          type='negative')

        ui.button('Login', on_click=handle_login).classes('w-full mt-4')
        ui.label('Default: superadmin / admin123').classes(
            'text-xs text-gray-500 mt-2 text-center w-full')

        ui.separator().classes('my-4')
        ui.button('Back to Home', on_click=lambda: ui.navigate.to(
            '/'), icon='arrow_back').props('outline color=blue').classes('w-full')


def dashboard_page():
    """Main dashboard page"""
    def content():
        user_data = app.storage.user.get('user', {})
        role_data = user_data.get('role', '')
        if isinstance(role_data, dict):
            role = role_data.get('name', '')
        else:
            role = str(role_data)

        ui.label(f'{role.capitalize()} Dashboard').classes(
            'text-2xl font-bold mb-6')

        with ui.grid(columns=4).classes('w-full gap-4'):
            # Dashboard cards based on role
            if role == 'superadmin':
                with ui.card().classes('p-4 bg-blue-500 text-white'):
                    ui.label('Total Users').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-green-500 text-white'):
                    ui.label('Active Roles').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-purple-500 text-white'):
                    ui.label('System Status').classes('text-sm')
                    ui.label('Active').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-orange-500 text-white'):
                    ui.label('Pending Approvals').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'admin':
                with ui.card().classes('p-4 bg-blue-500 text-white'):
                    ui.label('Staff on Duty').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-green-500 text-white'):
                    ui.label('Today\'s Sales').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-purple-500 text-white'):
                    ui.label('Fuel Levels').classes('text-sm')
                    ui.label('0%').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-orange-500 text-white'):
                    ui.label('Pending Tasks').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'accountant':
                with ui.card().classes('p-4 bg-blue-500 text-white'):
                    ui.label('Today\'s Revenue').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-green-500 text-white'):
                    ui.label('Pending Invoices').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-purple-500 text-white'):
                    ui.label('Cash on Hand').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-orange-500 text-white'):
                    ui.label('Unreconciled').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'pump_attendant':
                with ui.card().classes('p-4 bg-blue-500 text-white'):
                    ui.label("Today's Transactions").classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-green-500 text-white'):
                    ui.label('Active Pumps').classes('text-sm')
                    ui.label('4').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-purple-500 text-white'):
                    ui.label('Shift Status').classes('text-sm')
                    ui.label('Active').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-orange-500 text-white'):
                    ui.label('Recent Sales (RWF)').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

    dashboard_layout(content)


@ui.page('/')
def index():
    home.home_page()


@ui.page('/login')
def login():
    """Login route"""
    if app.storage.user.get('authenticated', False):
        with ui.card().classes('absolute-center w-96 p-6 items-center'):
            ui.label('You are already logged in').classes(
                'text-lg font-bold mb-4')
            ui.button('Go to Dashboard', on_click=lambda: ui.navigate.to(
                '/dashboard')).classes('w-full')
            ui.button('Logout', on_click=lambda: (auth_state.logout(), ui.navigate.to(
                '/login'))).props('flat color=red').classes('mt-4')
    else:
        login_page()


@ui.page('/dashboard')
def dashboard():
    """Dashboard route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        dashboard_page()


# Superadmin routes
@ui.page('/users')
def users():
    """User management route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.users_page()


@ui.page('/permissions')
def permissions():
    """Role permissions route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.roles_page()


@ui.page('/pricing')
def pricing():
    """Fuel pricing route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.pricing_page()


@ui.page('/partners')
def partners():
    """Partner agreements route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.partners_page()


@ui.page('/settings')
def settings():
    """System settings route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.settings_page()


@ui.page('/audit')
def audit():
    """Audit logs route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        superadmin.audit_page()


# Admin routes
@ui.page('/schedules')
def schedules():
    """Staff scheduling route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.schedules_page()


@ui.page('/attendance')
def attendance():
    """Attendance tracking route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.attendance_page()


@ui.page('/timesheets')
def timesheets():
    """Timesheet management route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.timesheets_page()


@ui.page('/operations')
def operations():
    """Station operations log route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.operations_page()


@ui.page('/safety')
def safety():
    """Safety compliance route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.safety_page()


@ui.page('/calibration')
def calibration():
    """Pump calibration route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.calibration_page()


@ui.page('/deliveries')
def deliveries():
    """Supplier deliveries route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.deliveries_page()


@ui.page('/complaints')
def complaints():
    """Customer complaints route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        admin.complaints_page()


# Accountant routes
@ui.page('/reconciliation')
def reconciliation():
    """Bank reconciliation route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.reconciliation_page()


@ui.page('/receivable')
def receivable():
    """Accounts receivable route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.receivable_page()


@ui.page('/payable')
def payable():
    """Accounts payable route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.payable_page()


@ui.page('/tax')
def tax():
    """Tax records route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.tax_page()


@ui.page('/costs')
def costs():
    """Cost tracking route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.costs_page()


@ui.page('/commissions')
def commissions():
    """Commission calculation route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.commissions_page()


@ui.page('/closing')
def closing():
    """Daily closing route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.closing_page()


@ui.page('/compliance')
def compliance():
    """Compliance reports route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        accountant.compliance_page()


# Inventory routes
@ui.page('/inventory')
def inventory_dashboard():
    """Inventory management route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        inventory.inventory_page()

# Receptionist routes


@ui.page('/sales')
def sales_dashboard():
    """Sales/Receptionist route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        receptionist.receptionist_page()

# Initialize NiceGUI app


def create_nicegui_app(fastapi_app_instance: FastAPI):
    """Create and run NiceGUI app instance"""

    @app.on_startup
    async def startup():
        """Initialize database connection when NiceGUI starts"""
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
        from backend.models.accounting import DailyClosing, CommissionCalculation
        from backend.models.inventory import Tank, FuelDelivery, InventoryRecord

        # List of models to initialize with Beanie
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
            Tank,
            FuelDelivery,
            InventoryRecord
        ]
        db.connect()
        await db.init_beanie(models)

    # Route Guard: Check authentication before serving any page
    @app.middleware("http")
    async def auth_middleware(request: Request, call_next):
        # Allow access to home, login, and static assets
        allowed_paths = ['/', '/login', '/_nicegui', '/static']

        # Bypass middleware for API calls and allowed paths
        if request.url.path.startswith('/api') or request.url.path in allowed_paths:
            return await call_next(request)

        if not app.storage.user.get('authenticated', False):
            return RedirectResponse('/login')

        # Role-Based Access Control (RBAC) for Frontend Routes
        user_data = app.storage.user.get('user', {})
        # Normalize role for comparison
        role = str(user_data.get('role', '')).lower()
        path = request.url.path

        # Define allowed routes per role
        role_permissions = {
            'superadmin': ['/users', '/permissions', '/pricing', '/partners', '/settings', '/audit', '/dashboard'],
            'admin': ['/schedules', '/attendance', '/timesheets', '/operations', '/safety', '/calibration', '/deliveries', '/complaints', '/dashboard'],
            'accountant': ['/reconciliation', '/receivable', '/payable', '/tax', '/costs', '/commissions', '/closing', '/compliance', '/dashboard'],
            'inventory': ['/inventory', '/dashboard'],
            'receptionist': ['/sales', '/dashboard'],
            'pump_attendant': ['/dashboard']
        }

        # Superadmins can access everything
        if role == 'superadmin':
            return await call_next(request)

        # Check if path is protected and if user role is authorized
        protected_routes = [p for routes in role_permissions.values()
                            for p in routes if p != '/dashboard']

        if path in protected_routes:
            allowed_paths = role_permissions.get(role, [])
            if path not in allowed_paths:
                # Log the attempted unauthorized access and redirect
                print(
                    f"🚫 [SECURITY] Unauthorized access attempt by {user_data.get('username')} ({role}) to {path}")
                return RedirectResponse('/dashboard')

        return await call_next(request)

    # Mount the FastAPI backend onto the NiceGUI app to handle API routes
    nicegui_app.mount('/api', fastapi_app_instance)

    ui.run(
        title='Petroleum Station Management',
        port=Config.PORT,
        host='0.0.0.0',
        reload=False,
        storage_secret='PETRO_SYNC_SECURE_KEY_2024'  # Enables app.storage.user
    )
