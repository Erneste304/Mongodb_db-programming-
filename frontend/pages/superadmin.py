"""
Superadmin Dashboard Pages
User management, role permissions, fuel pricing, partner agreements, system settings, audit logs
"""
from nicegui import ui
from frontend.state import auth_state, dashboard_layout
import httpx


async def fetch_users():
    """Fetch users from API"""
    if not auth_state.token:
        return []
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{auth_state.api_base_url}/users/",
                headers={"Authorization": f"Bearer {auth_state.token}"}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching users: {e}")
            return []


async def fetch_roles():
    """Fetch roles from API"""
    if not auth_state.token:
        return []
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{auth_state.api_base_url}/users/roles",
                headers={"Authorization": f"Bearer {auth_state.token}"}
            )
            if response.status_code == 200:
                return response.json()
            return []
        except Exception as e:
            print(f"Error fetching roles: {e}")
            return []


def users_page():
    """User management page"""
    def content():
        ui.label('User Management').classes('text-2xl font-bold mb-6')

        # Create the dialog outside the button click handler
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add New User').classes('text-xl font-bold mb-4')

            username_input = ui.input('Username', placeholder='Enter username')
            email_input = ui.input('Email', placeholder='Enter email')
            password_input = ui.input('Password', placeholder='Enter password', password=True)
            role_input = ui.select(label='Role', options=['admin', 'accountant', 'receptionist', 'inventory_manager', 'staff'])

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Create', on_click=lambda: create_user(dialog, username_input.value, email_input.value, password_input.value, role_input.value))

        def create_user(dialog, username, email, password, role):
            if not all([username, email, password, role]):
                ui.notify('Please fill all fields', type='warning')
                return

            # Show loading notification
            ui.notify('Creating user...', type='info')

            def api_call():
                try:
                    import requests

                    # Get the auth token from auth_state
                    token = auth_state.auth_token
                    if not token:
                        ui.notify('Authentication required', type='warning')
                        return

                    headers = {'Authorization': f'Bearer {token}'}
                    payload = {
                        'username': username,
                        'email': email,
                        'password': password,
                        'role_name': role
                    }

                    response = requests.post('http://localhost:8000/api/users/', json=payload, headers=headers)

                    if response.status_code == 201:
                        ui.notify(f'User {username} created successfully!', type='positive')
                        dialog.close()
                        # TODO: Refresh the user table
                    else:
                        try:
                            error_data = response.json()
                            ui.notify(f'Error creating user: {error_data.get("detail", "Unknown error")}', type='negative')
                        except:
                            ui.notify(f'Error creating user: {response.text}', type='negative')
                except Exception as e:
                    ui.notify(f'Network error: {str(e)}', type='negative')

            # Run the API call in a separate thread to avoid blocking the UI
            import threading
            threading.Thread(target=api_call, daemon=True).start()

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Add User', on_click=dialog.open)
            ui.button('Refresh', on_click=lambda: ui.notify('Refreshing users...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.table(
                columns=[
                    {'name': 'username', 'label': 'Username', 'field': 'username'},
                    {'name': 'email', 'label': 'Email', 'field': 'email'},
                    {'name': 'role', 'label': 'Role', 'field': 'role'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'username': 'superadmin', 'email': 'superadmin@example.com', 'role': 'superadmin', 'status': 'Active', 'actions': ''},
                    {'username': 'john.kamanzi', 'email': 'john@example.com', 'role': 'admin', 'status': 'Active', 'actions': ''},
                ],
                row_key='username'
            ).classes('w-full').props('rows-per-page-options=[10,20,50]')
    
    dashboard_layout(content)


def roles_page():
    """Role and permissions management page"""
    def content():
        ui.label('Role & Permission Management').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full'):
            ui.label('Roles').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'name', 'label': 'Role Name', 'field': 'name'},
                    {'name': 'level', 'label': 'Level', 'field': 'level'},
                    {'name': 'description', 'label': 'Description', 'field': 'description'},
                    {'name': 'permissions', 'label': 'Permissions', 'field': 'permissions'},
                ],
                rows=[
                    {'name': 'superadmin', 'level': '1', 'description': 'Full system control', 'permissions': 'All'},
                    {'name': 'admin', 'level': '2', 'description': 'Operational management', 'permissions': 'Staff, Operations'},
                    {'name': 'accountant', 'level': '3', 'description': 'Financial management', 'permissions': 'Finance, Reports'},
                ],
                row_key='name'
            ).classes('w-full')
    
    dashboard_layout(content)


def pricing_page():
    """Fuel pricing management page"""
    def content():
        ui.label('Fuel Pricing Management').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            with ui.row().classes('w-full gap-4 items-end'):
                ui.input('Fuel Type').props('placeholder="e.g., Petrol"')
                ui.input('Price per Liter (RWF)').props('type="number"')
                ui.input('Effective Date').props('type="date')
                ui.button('Add Price', on_click=lambda: ui.notify('Price added', type='positive'))
        
        with ui.card().classes('w-full'):
            ui.label('Current Prices').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'fuel_type', 'label': 'Fuel Type', 'field': 'fuel_type'},
                    {'name': 'price', 'label': 'Price (RWF/L)', 'field': 'price'},
                    {'name': 'effective_date', 'label': 'Effective Date', 'field': 'effective_date'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'fuel_type': 'Petrol', 'price': '1500', 'effective_date': '2024-01-01', 'actions': ''},
                    {'fuel_type': 'Diesel', 'price': '1400', 'effective_date': '2024-01-01', 'actions': ''},
                ],
                row_key='fuel_type'
            ).classes('w-full')
    
    dashboard_layout(content)


def partners_page():
    """Partner agreements management page"""
    def content():
        ui.label('Partner Agreements').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Add New Agreement', on_click=lambda: ui.notify('Add agreement dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Active Agreements').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'partner_name', 'label': 'Partner Name', 'field': 'partner_name'},
                    {'name': 'agreement_type', 'label': 'Type', 'field': 'agreement_type'},
                    {'name': 'start_date', 'label': 'Start Date', 'field': 'start_date'},
                    {'name': 'end_date', 'label': 'End Date', 'field': 'end_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[
                    {'partner_name': 'Total Rwanda', 'agreement_type': 'Fuel Supply', 'start_date': '2024-01-01', 'end_date': '2024-12-31', 'status': 'Active'},
                ],
                row_key='partner_name'
            ).classes('w-full')
    
    dashboard_layout(content)


def settings_page():
    """System settings page"""
    def content():
        ui.label('System Settings').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full'):
            with ui.column().classes('w-full gap-4'):
                ui.label('Business Configuration').classes('text-lg font-bold')
                
                ui.input('Station Name').props('placeholder="Enter station name"')
                ui.input('Station Address').props('placeholder="Enter address"')
                ui.input('Contact Phone').props('placeholder="Enter phone number"')
                ui.input('Contact Email').props('placeholder="Enter email"')
                
                ui.separator()
                
                ui.label('Business Rules').classes('text-lg font-bold')
                
                ui.input('Minimum Stock Level (Liters)').props('type="number"')
                ui.input('Maximum Credit Limit (RWF)').props('type="number"')
                ui.input('Commission Rate (%)').props('type="number"')
                
                ui.button('Save Settings', on_click=lambda: ui.notify('Settings saved', type='positive')).classes('mt-4')
    
    dashboard_layout(content)


def audit_page():
    """Audit logs page"""
    def content():
        ui.label('Audit Logs').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full'):
            ui.input('Search').props('placeholder="Search logs..."')
            ui.input('Date Range').props('placeholder="Select date range"')
            ui.select(label='User', options=['All Users', 'superadmin', 'admin', 'accountant'])
            ui.select(label='Action', options=['All Actions', 'create', 'update', 'delete'])
            ui.button('Filter', on_click=lambda: ui.notify('Filtering...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.table(
                columns=[
                    {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
                    {'name': 'user', 'label': 'User', 'field': 'user'},
                    {'name': 'action', 'label': 'Action', 'field': 'action'},
                    {'name': 'resource', 'label': 'Resource', 'field': 'resource'},
                    {'name': 'ip_address', 'label': 'IP Address', 'field': 'ip_address'},
                ],
                rows=[
                    {'timestamp': '2024-01-15 10:30:00', 'user': 'superadmin', 'action': 'create_user', 'resource': 'user', 'ip_address': '192.168.1.1'},
                    {'timestamp': '2024-01-15 11:00:00', 'user': 'admin', 'action': 'update_schedule', 'resource': 'schedule', 'ip_address': '192.168.1.2'},
                ],
                row_key='timestamp'
            ).classes('w-full')
    
    dashboard_layout(content)
