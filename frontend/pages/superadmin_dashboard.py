from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def superadmin_dashboard_page():
    """SUPERADMIN dashboard with full system overview and strategic decision tools"""
    def content():
        ui.label('SUPERADMIN Dashboard').classes('text-3xl font-bold mb-6 text-slate-800')

        # Strategic KPI Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label('Total Revenue').classes('text-sm text-blue-600 font-bold uppercase tracking-wider')
                revenue_label = ui.label('0 RWF').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label('Fuel Sales Volume').classes('text-sm text-green-600 font-bold uppercase tracking-wider')
                sales_volume_label = ui.label('0 L').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-purple-50 border-l-4 border-purple-500'):
                ui.label('Active Users').classes('text-sm text-purple-600 font-bold uppercase tracking-wider')
                active_users_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-orange-50 border-l-4 border-orange-500'):
                ui.label('Pending Approvals').classes('text-sm text-orange-600 font-bold uppercase tracking-wider')
                pending_approvals_label = ui.label('0').classes('text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            overview_tab = ui.tab('System Overview')
            stations_tab = ui.tab('Multi-Station')
            inventory_tab = ui.tab('Inventory Thresholds')
            expenditure_tab = ui.tab('Expenditure Approvals')
            discrepancy_tab = ui.tab('Discrepancy Investigation')
            audit_tab = ui.tab('Audit Logs')

        with ui.tab_panels(tabs, value=overview_tab).classes('w-full bg-transparent'):
            # System Overview Panel
            with ui.tab_panel(overview_tab):
                ui.label('System Performance Overview').classes('text-xl font-bold mb-4')
                ui.label('Detailed analytics and KPIs will be displayed here').classes('text-gray-500')

            # Multi-Station Panel
            with ui.tab_panel(stations_tab):
                with ui.dialog() as station_dialog, ui.card().classes('w-96'):
                    ui.label('Add New Station').classes('text-xl font-bold mb-4')
                    s_id = ui.input('Station ID (e.g. STN-001)').classes('w-full')
                    s_name = ui.input('Station Name').classes('w-full')
                    s_loc = ui.input('Location (Short)').classes('w-full')
                    s_addr = ui.input('Full Address').classes('w-full')
                    s_city = ui.input('City').classes('w-full')
                    s_dist = ui.input('District').classes('w-full')
                    s_mgr_name = ui.input('Manager Name').classes('w-full')
                    s_mgr_phone = ui.input('Manager Phone').classes('w-full')
                    s_mgr_email = ui.input('Manager Email').classes('w-full')
                    
                    async def save_station():
                        if not all([s_id.value, s_name.value, s_loc.value, s_addr.value, s_city.value, s_dist.value, s_mgr_name.value, s_mgr_phone.value, s_mgr_email.value]):
                            ui.notify('Please fill all required fields', type='warning')
                            return
                        token = app.storage.user.get('token')
                        payload = {
                            "station_id": s_id.value,
                            "name": s_name.value,
                            "location": s_loc.value,
                            "address": s_addr.value,
                            "city": s_city.value,
                            "district": s_dist.value,
                            "manager_name": s_mgr_name.value,
                            "manager_phone": s_mgr_phone.value,
                            "manager_email": s_mgr_email.value,
                            "opening_time": "06:00",
                            "closing_time": "22:00"
                        }
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/stations/"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Station added successfully', type='positive')
                                station_dialog.close()
                                load_dashboard_data()
                            else:
                                ui.notify(f"Error: {resp.text}", type='negative')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancel', on_click=station_dialog.close).props('flat')
                        ui.button('Save', on_click=save_station).props('elevated color=blue')

                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Multi-Station Operations').classes('text-xl font-bold')
                    ui.button('Add Station', on_click=station_dialog.open).props('elevated icon=add')
                stations_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Station ID', 'field': 'station_id'},
                        {'name': 'name', 'label': 'Name', 'field': 'name'},
                        {'name': 'location', 'label': 'Location', 'field': 'location'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                        {'name': 'revenue', 'label': 'Revenue (RWF)', 'field': 'revenue'},
                        {'name': 'actions', 'label': 'Actions', 'field': 'id'},
                    ],
                    rows=[],
                    row_key='station_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Inventory Thresholds Panel
            with ui.tab_panel(inventory_tab):
                with ui.dialog() as threshold_dialog, ui.card().classes('w-96'):
                    ui.label('Update Thresholds').classes('text-xl font-bold mb-4')
                    t_tank_id = ui.input('Tank ID').classes('w-full')
                    t_percent = ui.number('Alert Threshold %', value=20).classes('w-full')
                    
                    async def update_threshold():
                        if not t_tank_id.value or t_percent.value is None:
                            ui.notify('Please fill all fields', type='warning')
                            return
                        token = app.storage.user.get('token')
                        payload = {"threshold_alert_percent": t_percent.value}
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/inventory/tanks/{t_tank_id.value}"
                            resp = await client.patch(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Threshold updated', type='positive')
                                threshold_dialog.close()
                                load_dashboard_data()
                            else:
                                ui.notify(f"Error: {resp.text}", type='negative')

                    with ui.row().classes('w-full justify-end gap-2 mt-4'):
                        ui.button('Cancel', on_click=threshold_dialog.close).props('flat')
                        ui.button('Update', on_click=update_threshold).props('elevated color=blue')

                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Inventory Threshold Configuration').classes('text-xl font-bold')
                    ui.button('Update Thresholds', on_click=threshold_dialog.open).props('elevated icon=settings')
                thresholds_table = ui.table(
                    columns=[
                        {'name': 'tank', 'label': 'Tank', 'field': 'tank_id'},
                        {'name': 'fuel', 'label': 'Fuel Type', 'field': 'fuel_type'},
                        {'name': 'capacity', 'label': 'Capacity (L)', 'field': 'capacity'},
                        {'name': 'current', 'label': 'Current (L)', 'field': 'current'},
                        {'name': 'warning', 'label': 'Warning Level (L)', 'field': 'warning_level'},
                        {'name': 'critical', 'label': 'Critical Level (L)', 'field': 'critical_level'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='tank_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Expenditure Approvals Panel
            with ui.tab_panel(expenditure_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Large Expenditure Approvals').classes('text-xl font-bold')
                
                expenditure_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Request ID', 'field': 'request_id'},
                        {'name': 'type', 'label': 'Type', 'field': 'expenditure_type'},
                        {'name': 'amount', 'label': 'Amount (RWF)', 'field': 'amount'},
                        {'name': 'requested_by', 'label': 'Requested By', 'field': 'requested_by'},
                        {'name': 'date', 'label': 'Date', 'field': 'request_date'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                        {'name': 'actions', 'label': 'Actions', 'field': 'id'},
                    ],
                    rows=[],
                    row_key='request_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Discrepancy Investigation Panel
            with ui.tab_panel(discrepancy_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Discrepancy Investigation Tools').classes('text-xl font-bold')
                
                discrepancy_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Discrepancy ID', 'field': 'discrepancy_id'},
                        {'name': 'type', 'label': 'Type', 'field': 'discrepancy_type'},
                        {'name': 'description', 'label': 'Description', 'field': 'description'},
                        {'name': 'severity', 'label': 'Severity', 'field': 'severity'},
                        {'name': 'date', 'label': 'Date', 'field': 'detected_date'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                        {'name': 'actions', 'label': 'Actions', 'field': 'id'},
                    ],
                    rows=[],
                    row_key='discrepancy_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Audit Logs Panel
            with ui.tab_panel(audit_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Audit Trails and Security Logs').classes('text-xl font-bold')
                
                audit_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Log ID', 'field': 'log_id'},
                        {'name': 'user', 'label': 'User', 'field': 'user_id'},
                        {'name': 'action', 'label': 'Action', 'field': 'action'},
                        {'name': 'resource', 'label': 'Resource', 'field': 'resource'},
                        {'name': 'ip', 'label': 'IP Address', 'field': 'ip_address'},
                        {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
                    ],
                    rows=[],
                    row_key='log_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_dashboard_data():
            token = app.storage.user.get('token')
            res = {'done': False, 'revenue': 0, 'sales_volume': 0, 'users': 0, 'approvals': 0, 'err': ''}
            
            def fetch():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url

                    # Get revenue from reports
                    r1 = httpx.get(f'{base}/reports/daily', headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        data = r1.json()
                        res['revenue'] = sum(d.get('total_sales', 0) for d in data) if isinstance(data, list) else data.get('total_sales', 0)

                    # Get sales volume
                    r2 = httpx.get(f'{base}/sales/transactions', headers=headers, timeout=10.0)
                    if r2.status_code == 200:
                        data = r2.json()
                        res['sales_volume'] = sum(d.get('quantity_liters', 0) for d in data) if isinstance(data, list) else 0

                    # Get active users
                    r3 = httpx.get(f'{base}/users/', headers=headers, timeout=10.0)
                    if r3.status_code == 200:
                        data = r3.json()
                        res['users'] = len([u for u in data if u.get('is_active', True)]) if isinstance(data, list) else 0

                    # Get pending approvals
                    r4 = httpx.get(f'{base}/approvals/', headers=headers, timeout=10.0)
                    if r4.status_code == 200:
                        data = r4.json()
                        res['approvals'] = len([a for a in data if a.get('status') == 'pending']) if isinstance(data, list) else 0

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                
                if not res['err']:
                    revenue_label.set_text(f"{res['revenue']:,.0f} RWF")
                    sales_volume_label.set_text(f"{res['sales_volume']:,.0f} L")
                    active_users_label.set_text(str(res['users']))
                    pending_approvals_label.set_text(str(res['approvals']))

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_dashboard_data()

    dashboard_layout(content)
