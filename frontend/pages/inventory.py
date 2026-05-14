from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx
import random


def inventory_page():
    """Inventory management dashboard in NiceGUI"""
    def content():
        ui.label('Inventory Management').classes(
            'text-3xl font-bold mb-6 text-slate-800')

        # Stats Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label('Total Capacity').classes(
                    'text-sm text-blue-600 font-bold uppercase tracking-wider')
                capacity_label = ui.label('0 L').classes(
                    'text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label('Current Level').classes(
                    'text-sm text-green-600 font-bold uppercase tracking-wider')
                level_label = ui.label('0 L').classes(
                    'text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-amber-50 border-l-4 border-amber-500'):
                ui.label('Anomalies Detected').classes(
                    'text-sm text-amber-600 font-bold uppercase tracking-wider')
                anomaly_label = ui.label('0').classes(
                    'text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            tank_tab = ui.tab('Tank Overview')
            delivery_tab = ui.tab('Fuel Deliveries')
            record_tab = ui.tab('Daily Records')

        with ui.tab_panels(tabs, value=tank_tab).classes('w-full bg-transparent'):
            # Tank Overview Panel
            with ui.tab_panel(tank_tab):
                # Add Tank Dialog
                with ui.dialog() as tank_dialog, ui.card().classes('w-96'):
                    ui.label('Add New Fuel Tank').classes(
                        'text-xl font-bold mb-4')
                    tank_num = ui.input(
                        'Tank Number (e.g. T-01)').classes('w-full')
                    fuel_type = ui.select(
                        ['petrol', 'diesel', 'kerosene'], label='Fuel Type').classes('w-full')
                    capacity = ui.number(
                        'Capacity (Liters)', value=10000).classes('w-full')

                    async def save_tank():
                        if not tank_num.value:
                            ui.notify('Tank number is required',
                                      type='warning')
                            return

                        token = app.storage.user.get('token')
                        payload = {
                            "tank_id": f"TANK-{random.randint(1000, 9999)}",
                            "tank_number": tank_num.value,
                            "fuel_type": fuel_type.value,
                            "capacity_liters": capacity.value,
                            "current_level_liters": 0
                        }

                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/inventory/tanks"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Tank added successfully',
                                          type='positive')
                                tank_dialog.close()
                                load_inventory()
                            else:
                                ui.notify(
                                    f"Error: {resp.text}", type='negative')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancel', on_click=tank_dialog.close).props(
                            'flat')
                        ui.button('Save', on_click=save_tank).props(
                            'elevated color=green')

                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Fuel Tanks').classes('text-xl font-bold')
                    ui.button('Add New Tank', on_click=tank_dialog.open).props(
                        'elevated icon=add')

                tank_table = ui.table(
                    columns=[
                        {'name': 'tank_id', 'label': 'ID', 'field': 'tank_id'},
                        {'name': 'tank_number', 'label': 'Number',
                            'field': 'tank_number'},
                        {'name': 'fuel_type', 'label': 'Fuel', 'field': 'fuel_type'},
                        {'name': 'capacity',
                            'label': 'Capacity (L)', 'field': 'capacity_liters'},
                        {'name': 'current',
                            'label': 'Current (L)', 'field': 'current_level_liters'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='tank_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Deliveries Panel
            with ui.tab_panel(delivery_tab):
                with ui.dialog() as delivery_dialog, ui.card().classes('w-96'):
                    ui.label('Record Fuel Delivery').classes('text-xl font-bold mb-4')
                    d_tank_id = ui.input('Tank ID (e.g. TANK-1234)').classes('w-full')
                    d_supplier = ui.input('Supplier Name').classes('w-full')
                    d_invoice = ui.input('Supplier Invoice #').classes('w-full')
                    d_fuel = ui.select(['petrol', 'diesel', 'kerosene'], label='Fuel Type').classes('w-full')
                    d_qty = ui.number('Quantity Delivered (L)').classes('w-full')
                    d_price = ui.number('Price per Liter').classes('w-full')
                    d_driver = ui.input('Delivered By (Driver Name)').classes('w-full')
                    
                    async def save_delivery():
                        if not all([d_tank_id.value, d_supplier.value, d_fuel.value, d_qty.value, d_price.value]):
                            ui.notify('Please fill required fields', type='warning')
                            return
                        token = app.storage.user.get('token')
                        payload = {
                            "delivery_id": f"DEL-{random.randint(10000, 99999)}",
                            "tank_id": d_tank_id.value,
                            "supplier_name": d_supplier.value,
                            "supplier_invoice_number": d_invoice.value or "N/A",
                            "fuel_type": d_fuel.value,
                            "quantity_delivered_liters": d_qty.value,
                            "price_per_liter": d_price.value,
                            "delivered_by": d_driver.value or "Unknown"
                        }
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/inventory/deliveries"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Delivery recorded successfully', type='positive')
                                delivery_dialog.close()
                                load_inventory()
                            else:
                                ui.notify(f"Error: {resp.text}", type='negative')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancel', on_click=delivery_dialog.close).props('flat')
                        ui.button('Save', on_click=save_delivery).props('elevated color=green')

                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Delivery Logs').classes('text-xl font-bold')
                    ui.button('Record Delivery', on_click=delivery_dialog.open).props('elevated icon=local_shipping color=green')

                delivery_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Delivery ID',
                            'field': 'delivery_id'},
                        {'name': 'supplier', 'label': 'Supplier',
                            'field': 'supplier_name'},
                        {'name': 'fuel', 'label': 'Fuel', 'field': 'fuel_type'},
                        {'name': 'qty',
                            'label': 'Quantity (L)', 'field': 'quantity_delivered_liters'},
                        {'name': 'date', 'label': 'Date',
                            'field': 'delivery_date'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='delivery_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Records Panel
            with ui.tab_panel(record_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Inventory Records').classes('text-xl font-bold')

                record_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Record ID', 'field': 'record_id'},
                        {'name': 'tank', 'label': 'Tank', 'field': 'tank_id'},
                        {'name': 'opening',
                            'label': 'Opening (L)', 'field': 'opening_level_liters'},
                        {'name': 'closing',
                            'label': 'Closing (L)', 'field': 'closing_level_liters'},
                        {'name': 'variance',
                            'label': 'Variance (L)', 'field': 'variance_liters'},
                        {'name': 'date', 'label': 'Date', 'field': 'record_date'},
                    ],
                    rows=[],
                    row_key='record_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_inventory():
            token = app.storage.user.get('token')
            res = {'done': False, 'tanks': [],
                   'deliveries': [], 'records': [], 'err': ''}
            tank_table.props(add='loading')
            delivery_table.props(add='loading')
            record_table.props(add='loading')

            def fetch():  # This function runs in a separate thread
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url  # Already correctly formatted

                    # Tanks
                    r1 = httpx.get(f'{base}/inventory/tanks',
                                   headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        res['tanks'] = r1.json()

                    # Deliveries
                    r2 = httpx.get(f'{base}/inventory/deliveries',
                                   headers=headers, timeout=10.0)
                    if r2.status_code == 200:
                        res['deliveries'] = r2.json()

                    # Records
                    r3 = httpx.get(f'{base}/inventory/records',
                                   headers=headers, timeout=10.0)
                    if r3.status_code == 200:
                        res['records'] = r3.json()

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                tank_table.props(remove='loading')
                delivery_table.props(remove='loading')
                record_table.props(remove='loading')

                if not res['err']:
                    tank_table.rows = res['tanks']
                    delivery_table.rows = res['deliveries']
                    record_table.rows = res['records']

                    # Update stats
                    total_cap = sum(t.get('capacity_liters', 0)
                                    for t in res['tanks'])
                    current_lvl = sum(t.get('current_level_liters', 0)
                                      for t in res['tanks'])
                    capacity_label.set_text(f"{total_cap:,.0f} L")
                    level_label.set_text(f"{current_lvl:,.0f} L")

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_inventory()

    dashboard_layout(content)
