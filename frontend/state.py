"""
Shared state and layout functions for NiceGUI application
"""
from nicegui import ui
import httpx


class AuthState:
    """Authentication state management"""
    def __init__(self):
        self.current_user = None
        self.is_authenticated = False
        self.token = None
        self.api_base_url = "http://localhost:8000"
    
    async def login(self, username: str, password: str):
        """Login using backend API"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.api_base_url}/auth/login",
                    json={"username": username, "password": password}
                )
                if response.status_code == 200:
                    data = response.json()
                    self.token = data.get("access_token")
                    self.current_user = data.get("user")
                    self.is_authenticated = True
                    return True
                return False
            except Exception as e:
                print(f"Login error: {e}")
                return False
    
    def logout(self):
        """Logout current user"""
        self.current_user = None
        self.is_authenticated = False
        self.token = None


auth_state = AuthState()


def dashboard_layout(content_fn):
    """Dashboard layout with navigation"""
    from frontend.state import auth_state
    
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        with ui.row().classes('w-full bg-blue-600 text-white p-4 items-center justify-between'):
            ui.label('Petroleum Station Management').classes('text-xl font-bold')
            
            with ui.row().classes('items-center gap-4'):
                if auth_state.current_user:
                    ui.label(f"Welcome, {auth_state.current_user.get('username', 'User')}").classes('text-sm')
                    ui.button('Logout', on_click=lambda: (
                        auth_state.logout(),
                        ui.navigate.to('/login')
                    )).props('flat color=white')
        
        # Sidebar navigation
        with ui.row().classes('w-full'):
            with ui.column().classes('w-64 bg-white min-h-screen p-4 shadow-md'):
                ui.label('Navigation').classes('font-bold mb-4')
                
                def nav_item(label, route, icon):
                    with ui.row().classes('items-center gap-2 p-2 cursor-pointer hover:bg-blue-50 rounded w-full') \
                            .on('click', lambda: ui.navigate.to(route)):
                        ui.label(icon).classes('text-lg')
                        ui.label(label).classes('text-sm font-medium')
                
                user_data = auth_state.current_user if auth_state.current_user else {}
                role_data = user_data.get('role', '')
                if isinstance(role_data, dict):
                    role = role_data.get('name', '')
                else:
                    role = str(role_data)
                
                if role == 'superadmin':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('User Management', '/users', '👥')
                    nav_item('Role Permissions', '/permissions', '🔐')
                    nav_item('Fuel Pricing', '/pricing', '⛽')
                    nav_item('Partner Agreements', '/partners', '🤝')
                    nav_item('System Settings', '/settings', '⚙️')
                    nav_item('Audit Logs', '/audit', '📋')
                
                elif role == 'admin':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('Staff Scheduling', '/schedules', '📅')
                    nav_item('Attendance', '/attendance', '🕒')
                    nav_item('Timesheets', '/timesheets', '📝')
                    nav_item('Operations Log', '/operations', '📖')
                    nav_item('Safety Compliance', '/safety', '🛡️')
                    nav_item('Pump Calibration', '/calibration', '🔧')
                    nav_item('Supplier Deliveries', '/deliveries', '🚚')
                    nav_item('Customer Complaints', '/complaints', '📢')
                
                elif role == 'accountant':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('Bank Reconciliation', '/reconciliation', '🏦')
                    nav_item('Accounts Receivable', '/receivable', '💰')
                    nav_item('Accounts Payable', '/payable', '💸')
                    nav_item('Tax Records', '/tax', '📄')
                    nav_item('Cost Tracking', '/costs', '📉')
                    nav_item('Commissions', '/commissions', '💵')
                    nav_item('Daily Closing', '/closing', '🔄')
                    nav_item('Compliance Reports', '/compliance', '📊')
            
            # Main content area
            with ui.column().classes('flex-1 p-6'):
                content_fn()
