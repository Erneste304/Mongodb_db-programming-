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
        ui.label('PETRO-SYNC').classes(
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

        # Normalize role for comparison
        role = role.lower()

        ui.label(f'{role.capitalize()} Dashboard').classes(
            'text-2xl font-bold mb-6')

        with ui.grid(columns=4).classes('w-full gap-4'):
            # Dashboard cards based on role
            if role == 'superadmin':
                card_users = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_users.on('click', lambda: ui.navigate.to('/users'))
                with card_users:
                    ui.label('Total Users').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                card_perm = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_perm.on('click', lambda: ui.navigate.to('/permissions'))
                with card_perm:
                    ui.label('Active Roles').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                card_set = ui.card().classes('p-4 bg-purple-500 text-white cursor-pointer')
                card_set.on('click', lambda: ui.navigate.to('/settings'))
                with card_set:
                    ui.label('System Status').classes('text-sm')
                    ui.label('Active').classes('text-3xl font-bold')

                card_audit = ui.card().classes('p-4 bg-orange-500 text-white cursor-pointer')
                card_audit.on('click', lambda: ui.navigate.to('/audit'))
                with card_audit:
                    ui.label('Pending Approvals').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'admin':
                card_att = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_att.on('click', lambda: ui.navigate.to('/attendance'))
                with card_att:
                    ui.label('Staff on Duty').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                card_ops = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_ops.on('click', lambda: ui.navigate.to('/operations'))
                with card_ops:
                    ui.label('Today\'s Sales').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                card_inv = ui.card().classes('p-4 bg-purple-500 text-white cursor-pointer')
                card_inv.on('click', lambda: ui.navigate.to('/inventory'))
                with card_inv:
                    ui.label('Fuel Levels').classes('text-sm')
                    ui.label('0%').classes('text-3xl font-bold')

                card_comp = ui.card().classes('p-4 bg-orange-500 text-white cursor-pointer')
                card_comp.on('click', lambda: ui.navigate.to('/complaints'))
                with card_comp:
                    ui.label('Pending Tasks').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'accountant':
                card_rev = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_rev.on('click', lambda: ui.navigate.to('/receivable'))
                with card_rev:
                    ui.label('Today\'s Revenue').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                card_pay = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_pay.on('click', lambda: ui.navigate.to('/payable'))
                with card_pay:
                    ui.label('Pending Invoices').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                card_cash = ui.card().classes('p-4 bg-purple-500 text-white cursor-pointer')
                card_cash.on('click', lambda: ui.navigate.to('/closing'))
                with card_cash:
                    ui.label('Cash on Hand').classes('text-sm')
                    ui.label('RWF 0').classes('text-3xl font-bold')

                card_recon = ui.card().classes('p-4 bg-orange-500 text-white cursor-pointer')
                card_recon.on(
                    'click', lambda: ui.navigate.to('/reconciliation'))
                with card_recon:
                    ui.label('Unreconciled').classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

            elif role == 'receptionist':
                card_sales = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_sales.on('click', lambda: ui.navigate.to('/sales'))
                with card_sales:
                    ui.label('Sales Command Center').classes('text-sm')
                    ui.label('🛒').classes('text-3xl font-bold')
                    ui.label('Process Transactions').classes(
                        'text-xs opacity-80')

                card_cust = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_cust.on('click', lambda: ui.navigate.to('/customers'))
                with card_cust:
                    ui.label('Customer Management').classes('text-sm')
                    ui.label('👥').classes('text-3xl font-bold')
                    ui.label('Loyalty & Credit').classes('text-xs opacity-80')

            elif role == 'inventory_manager':
                card_inv = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_inv.on('click', lambda: ui.navigate.to('/inventory'))
                with card_inv:
                    ui.label('Inventory Tracking').classes('text-sm')
                    ui.label('📦').classes('text-3xl font-bold')

                card_del = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_del.on('click', lambda: ui.navigate.to('/inventory'))
                with card_del:
                    ui.label('Fuel Deliveries').classes('text-sm')
                    ui.label('🚚').classes('text-3xl font-bold')

                card_cal = ui.card().classes('p-4 bg-purple-500 text-white cursor-pointer')
                card_cal.on('click', lambda: ui.navigate.to('/calibration'))
                with card_cal:
                    ui.label('Tank Calibration').classes('text-sm')
                    ui.label('🔧').classes('text-3xl font-bold')

            elif role in ['staff', 'pump_attendant']:
                card_sched = ui.card().classes('p-4 bg-blue-500 text-white cursor-pointer')
                card_sched.on('click', lambda: ui.navigate.to('/schedules'))
                with card_sched:
                    ui.row().classes('items-center gap-2')
                    ui.icon('calendar_month')
                    ui.label('My Schedule').classes('text-sm')
                    ui.label('View Shift').classes('text-xs opacity-70')

                card_my_att = ui.card().classes('p-4 bg-green-500 text-white cursor-pointer')
                card_my_att.on('click', lambda: ui.navigate.to('/attendance'))
                with card_my_att:
                    ui.row().classes('items-center gap-2')
                    ui.icon('timer')
                    ui.label('My Attendance').classes('text-sm')
                    ui.label('Clock In/Out').classes('text-xs opacity-70')

                card_tx = ui.card().classes('p-4 bg-purple-500 text-white cursor-pointer')
                card_tx.on('click', lambda: ui.navigate.to('/sales'))
                with card_tx:
                    ui.label("Today's Transactions").classes('text-sm')
                    ui.label('0').classes('text-3xl font-bold')

                with ui.card().classes('p-4 bg-orange-500 text-white cursor-pointer'):
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


@ui.page('/customers')
def customers_page():
    """Customer management route"""
    if not app.storage.user.get('authenticated', False):
        ui.navigate.to('/login')
    else:
        # Assumes receptionist module has a customers_page function
        receptionist.customers_page()

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
        from backend.models.accounting import (
            DailyClosing, CommissionCalculation, BankReconciliation,
            AccountsReceivable, AccountsPayable, TaxRecord,
            FuelCostTracking, CorporateInvoice, RURAComplianceReport
        )
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

        # ── JWT Expiry Detection ─────────────────────────────────────────────
        # Validate the actual JWT token to ensure it hasn't expired or been tampered with
        token = app.storage.user.get('token')
        if token:
            from jose import jwt, JWTError
            from backend.core.config import settings
            try:
                # This will raise an ExpiredSignatureError if the token is past its 'exp' claim
                jwt.decode(token, settings.SECRET_KEY,
                           algorithms=[settings.ALGORITHM])
            except JWTError as e:
                print(f"🔄 [AUTH] Session expired or invalid: {str(e)}. Redirecting to login.")
                app.storage.user.update({
                    'authenticated': False,
                    'token': None,
                    'user': {},
                    'token_issued_at': 0
                })
                return RedirectResponse('/login?expired=1')

        # Role-Based Access Control (RBAC) for Frontend Routes
        user_data = app.storage.user.get('user', {})
        # Normalize role for comparison
        role = str(user_data.get('role', '')).lower()
        path = request.url.path

        # Define allowed routes per role
        role_permissions = {
            'superadmin': ['/users', '/permissions', '/pricing', '/partners', '/settings', '/audit', '/dashboard'],
            'admin': ['/schedules', '/attendance', '/timesheets', '/operations', '/safety', '/calibration', '/deliveries', '/complaints', '/inventory', '/sales', '/customers', '/dashboard'],
            'accountant': ['/reconciliation', '/receivable', '/payable', '/tax', '/costs', '/commissions', '/closing', '/compliance', '/dashboard'],
            'inventory_manager': ['/inventory', '/calibration', '/dashboard'],
            'receptionist': ['/sales', '/customers', '/dashboard'],
            'pump_attendant': ['/sales', '/attendance', '/dashboard'],
            'staff': ['/schedules', '/attendance', '/dashboard']
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
