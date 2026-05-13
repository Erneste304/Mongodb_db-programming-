"""
Receptionist Dashboard Pages
Sales Command Center, Customer Management
"""
from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx
from datetime import datetime


def receptionist_page():
    """Sales Command Center page"""
    def content():
        ui.label('Sales Command Center').classes('text-2xl font-bold mb-6')
        ui.label('This is where sales transactions will be processed.').classes(
            'mb-4')
        # Placeholder for sales processing UI
        ui.card().classes('w-full p-4').style('min-height: 300px;')
        ui.label('Sales transaction form and recent sales list will go here.').classes(
            'text-gray-500')

    dashboard_layout(content)


def customers_page():
    """Customer Management page"""
    def content():
        ui.label('Customer Management').classes('text-2xl font-bold mb-6')

        # Add Customer Dialog
        with ui.dialog() as add_customer_dialog, ui.card().classes('w-96'):
            ui.label('Add New Customer').classes('text-xl font-bold mb-4')
            customer_id_input = ui.input('Customer ID').classes('w-full')
            name_input = ui.input('Name').classes('w-full')
            phone_input = ui.input('Phone').classes('w-full')
            email_input = ui.input('Email').classes('w-full')
            tin_input = ui.input('TIN Number (Optional)').classes('w-full')
            customer_type_select = ui.select(
                ['cash', 'credit'], label='Customer Type', value='cash').classes('w-full')
            credit_limit_input = ui.number(
                'Credit Limit (RWF)', value=0).classes('w-full')

            async def save_customer():
                if not all([customer_id_input.value, name_input.value]):
                    ui.notify(
                        'Please fill required fields (Customer ID, Name)', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "customer_id": customer_id_input.value,
                    "name": name_input.value,
                    "phone": phone_input.value,
                    "email": email_input.value,
                    "tin_number": tin_input.value,
                    "customer_type": customer_type_select.value,
                    "credit_limit": credit_limit_input.value
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/sales/customers"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Customer added successfully',
                                  type='positive')
                        add_customer_dialog.close()
                        load_customers()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=add_customer_dialog.close).props(
                    'flat')
                ui.button('Save', on_click=save_customer).props(
                    'elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Add New Customer', on_click=add_customer_dialog.open).props(
                'icon=person_add')

        with ui.card().classes('w-full'):
            ui.label('Existing Customers').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'customer_id', 'label': 'Customer ID',
                        'field': 'customer_id'},
                    {'name': 'name', 'label': 'Name', 'field': 'name'},
                    {'name': 'phone', 'label': 'Phone', 'field': 'phone'},
                    {'name': 'email', 'label': 'Email', 'field': 'email'},
                    {'name': 'customer_type', 'label': 'Type',
                        'field': 'customer_type'},
                    {'name': 'credit_limit', 'label': 'Credit Limit',
                        'field': 'credit_limit'},
                    {'name': 'current_balance', 'label': 'Balance',
                        'field': 'current_balance'},
                    {'name': 'loyalty_points', 'label': 'Loyalty Points',
                        'field': 'loyalty_points'},
                ],
                rows=[],
                row_key='customer_id'
            ).classes('w-full').props('loading')

        def load_customers():
            token = app.storage.user.get('token')

            async def fetch_data():
                try:
                    url = f'{auth_state.api_base_url}/sales/customers'
                    r = await httpx.get(url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        table.rows = r.json()
                    else:
                        ui.notify(
                            f"Error loading customers: {r.status_code} - {r.text[:50]}", type='negative')
                except Exception as e:
                    ui.notify(
                        f"Connection error loading customers: {str(e)}", type='negative')
                finally:
                    table.props(remove='loading')
            # Use ui.timer for async calls in NiceGUI
            ui.timer(0.1, fetch_data, once=True)

        load_customers()

    dashboard_layout(content)
