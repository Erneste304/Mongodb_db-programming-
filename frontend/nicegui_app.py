"""
NiceGUI Application for Petroleum Station Management
Integrates with existing FastAPI backend
"""
from nicegui import ui, app
from fastapi import FastAPI, Request
from backend.models.user import User, Role
import httpx
from frontend.state import auth_state, dashboard_layout
from frontend.pages import superadmin, admin, accountant


def login_page():
    """Login page UI"""
    with ui.card().classes('absolute-center w-96 p-6'):
        ui.label('Petroleum Station Management').classes('text-2xl font-bold mb-4')
        ui.label('Login').classes('text-lg mb-4')
        
        username_input = ui.input('Username', placeholder='Enter username')
        password_input = ui.input('Password', placeholder='Enter password', password=True)
        password_input.props('toggle-mask')
        
        async def handle_login():
            if await auth_state.login(username_input.value, password_input.value):
                ui.navigate.to('/dashboard')
            else:
                ui.notify('Invalid credentials', type='negative')
        
        ui.button('Login', on_click=handle_login).classes('w-full mt-4')
        ui.label('Default: superadmin / admin123').classes('text-xs text-gray-500 mt-2')


def dashboard_page():
    """Main dashboard page"""
    def content():
        user_data = auth_state.current_user if auth_state.current_user else {}
        role_data = user_data.get('role', '')
        if isinstance(role_data, dict):
            role = role_data.get('name', '')
        else:
            role = str(role_data)
        
        ui.label(f'{role.capitalize()} Dashboard').classes('text-2xl font-bold mb-6')
        
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
    
    dashboard_layout(content)


@ui.page('/')
def index():
    """Root redirect"""
    ui.navigate.to('/login')


@ui.page('/login')
def login():
    """Login route"""
    if auth_state.is_authenticated:
        ui.navigate.to('/dashboard')
    else:
        login_page()


@ui.page('/dashboard')
def dashboard():
    """Dashboard route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        dashboard_page()


# Superadmin routes
@ui.page('/users')
def users():
    """User management route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.users_page()

@ui.page('/permissions')
def permissions():
    """Role permissions route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.roles_page()

@ui.page('/pricing')
def pricing():
    """Fuel pricing route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.pricing_page()

@ui.page('/partners')
def partners():
    """Partner agreements route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.partners_page()

@ui.page('/settings')
def settings():
    """System settings route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.settings_page()

@ui.page('/audit')
def audit():
    """Audit logs route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        superadmin.audit_page()


# Admin routes
@ui.page('/schedules')
def schedules():
    """Staff scheduling route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.schedules_page()

@ui.page('/attendance')
def attendance():
    """Attendance tracking route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.attendance_page()

@ui.page('/timesheets')
def timesheets():
    """Timesheet management route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.timesheets_page()

@ui.page('/operations')
def operations():
    """Station operations log route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.operations_page()

@ui.page('/safety')
def safety():
    """Safety compliance route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.safety_page()

@ui.page('/calibration')
def calibration():
    """Pump calibration route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.calibration_page()

@ui.page('/deliveries')
def deliveries():
    """Supplier deliveries route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.deliveries_page()

@ui.page('/complaints')
def complaints():
    """Customer complaints route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        admin.complaints_page()


# Accountant routes
@ui.page('/reconciliation')
def reconciliation():
    """Bank reconciliation route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.reconciliation_page()

@ui.page('/receivable')
def receivable():
    """Accounts receivable route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.receivable_page()

@ui.page('/payable')
def payable():
    """Accounts payable route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.payable_page()

@ui.page('/tax')
def tax():
    """Tax records route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.tax_page()

@ui.page('/costs')
def costs():
    """Cost tracking route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.costs_page()

@ui.page('/commissions')
def commissions():
    """Commission calculation route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.commissions_page()

@ui.page('/closing')
def closing():
    """Daily closing route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.closing_page()

@ui.page('/compliance')
def compliance():
    """Compliance reports route"""
    if not auth_state.is_authenticated:
        ui.navigate.to('/login')
    else:
        accountant.compliance_page()


# Initialize NiceGUI app
def create_nicegui_app():
    """Create and run NiceGUI app instance"""
    ui.run(
        title='Petroleum Station Management',
        port=3000,
        host='localhost',
        reload=False
    )
