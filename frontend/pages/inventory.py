from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


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
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Fuel Tanks').classes('text-xl font-bold')
                    ui.button('Add New Tank', on_click=lambda: ui.notify(
                        'Add tank dialog', type='info')).props('elevated icon=add')

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
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Delivery Logs').classes('text-xl font-bold')
                    ui.button('Record Delivery', on_click=lambda: ui.notify(
                        'Record delivery dialog', type='info')).props('elevated icon=local_shipping color=green')

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
