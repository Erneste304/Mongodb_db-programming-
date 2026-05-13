"""
Shared state and layout functions for NiceGUI application
"""
from nicegui import ui, app
from config import Config
import os
import httpx


class AuthState:
    """Authentication state management"""

    def __init__(self):
        self.error = None
        self.api_base_url = f"http://127.0.0.1:{Config.PORT}/api"

    async def login(self, username: str, password: str):
        """Login using backend API"""
        self.error = None
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_base_url}/auth/login",
                    json={"username": username, "password": password},
                    timeout=5.0
                )
            if response.status_code == 200:
                data = response.json()
                app.storage.user['token'] = data.get("access_token")
                app.storage.user['user'] = data.get("user")
                app.storage.user['authenticated'] = True
                return True

            # Safely handle non-JSON error responses
            try:
                error_data = response.json()
                self.error = error_data.get(
                    "detail", f"Login failed: {response.status_code}")
            except Exception:
                self.error = f"Server Error ({response.status_code}): {response.text[:50]}"
            return False
        except Exception as e:
            self.error = f"Connection error: {str(e)}"
            return False

    def logout(self):
        """Logout current user"""
        app.storage.user.clear()


auth_state = AuthState()


def dashboard_layout(content_fn):
    """Dashboard layout with navigation"""
    with ui.column().classes('w-full min-h-screen bg-gray-50'):
        # Header
        with ui.row().classes('w-full bg-blue-600 text-white p-4 items-center justify-between'):
            ui.label('Petroleum Station Management').classes(
                'text-xl font-bold')

            with ui.row().classes('items-center gap-4'):
                user = app.storage.user.get('user')
                if user:
                    ui.label(f"Welcome, {user.get('username', 'User')}").classes(
                        'text-sm')
                    ui.button('Logout', on_click=lambda: (
                        auth_state.logout(),
                        ui.navigate.to('/login')
                    )).props('flat color=white icon=logout')

        # Sidebar navigation
        with ui.row().classes('w-full'):
            with ui.column().classes('w-64 bg-white min-h-screen p-4 shadow-md'):
                ui.label('Navigation').classes('font-bold mb-4')

                def nav_item(label, route, icon):
                    with ui.row().classes('items-center gap-2 p-2 cursor-pointer hover:bg-blue-50 rounded w-full') \
                            .on('click', lambda: ui.navigate.to(route)):
                        ui.label(icon).classes('text-lg')
                        ui.label(label).classes('text-sm font-medium')

                user_data = app.storage.user.get('user', {})
                role_data = user_data.get('role', '')
                if isinstance(role_data, dict):
                    role = role_data.get('name', '')
                else:
                    role = str(role_data)

                # Normalize role for comparison
                role = role.lower()

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
                    nav_item('Inventory Control', '/inventory', '📦')
                    nav_item('Sales & Pos', '/sales', '🛒')

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

                elif role == 'receptionist':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('Sales Command Center', '/sales', '🛒')
                    nav_item('Customers', '/customers', '👥')

                elif role == 'inventory_manager':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('Inventory Tracking', '/inventory', '📦')
                    nav_item('Fuel Deliveries', '/inventory', '🚚')
                    nav_item('Tank Calibration', '/calibration', '🔧')

                elif role == 'staff':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('My Schedule', '/schedules', '📅')
                    nav_item('My Attendance', '/attendance', '🕒')

                elif role == 'pump_attendant':
                    nav_item('Dashboard', '/dashboard', '📊')
                    nav_item('Process Sales', '/sales', '⛽')
                    nav_item('My Attendance', '/attendance', '🕒')

            # Main content area
            with ui.column().classes('flex-1 p-6'):
                with ui.row().classes('w-full justify-end mb-4'):
                    ui.button('Back to Dashboard', on_click=lambda: ui.navigate.to(
                        '/dashboard')).props('flat icon=arrow_back color=blue')
                content_fn()
