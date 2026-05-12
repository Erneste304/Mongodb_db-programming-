from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def admin_operations_page():
    """ADMIN operations page with all operational management features"""
    def content():
        ui.label('ADMIN Operations Management').classes('text-3xl font-bold mb-6 text-slate-800')

        # Stats Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label('Staff on Duty').classes('text-sm text-blue-600 font-bold uppercase tracking-wider')
                staff_on_duty_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label('Fuel Deliveries Today').classes('text-sm text-green-600 font-bold uppercase tracking-wider')
                deliveries_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-orange-50 border-l-4 border-orange-500'):
                ui.label('Pending Complaints').classes('text-sm text-orange-600 font-bold uppercase tracking-wider')
                complaints_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-purple-50 border-l-4 border-purple-500'):
                ui.label('Safety Checks Due').classes('text-sm text-purple-600 font-bold uppercase tracking-wider')
                safety_checks_label = ui.label('0').classes('text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            scheduling_tab = ui.tab('Staff Scheduling')
            attendance_tab = ui.tab('Attendance Tracking')
            fuel_deliveries_tab = ui.tab('Fuel Deliveries')
            inventory_tab = ui.tab('Inventory Monitoring')
            complaints_tab = ui.tab('Customer Complaints')
            safety_tab = ui.tab('Safety Compliance')
            calibration_tab = ui.tab('Pump Calibration')
            suppliers_tab = ui.tab('Supplier Coordination')
            timesheets_tab = ui.tab('Timesheet Approval')
            supervision_tab = ui.tab('Pump Supervision')
            cleanliness_tab = ui.tab('Cleanliness & Safety')
            reconciliation_tab = ui.tab('Cash Reconciliation')

        with ui.tab_panels(tabs, value=scheduling_tab).classes('w-full bg-transparent'):
            # Staff Scheduling Panel
            with ui.tab_panel(scheduling_tab):
                ui.label('Staff Scheduling').classes('text-xl font-bold mb-4')
                ui.label('Manage staff schedules and shifts').classes('text-gray-500')

            # Attendance Tracking Panel
            with ui.tab_panel(attendance_tab):
                ui.label('Attendance Tracking').classes('text-xl font-bold mb-4')
                ui.label('Track staff attendance and hours').classes('text-gray-500')

            # Fuel Deliveries Panel
            with ui.tab_panel(fuel_deliveries_tab):
                ui.label('Fuel Deliveries').classes('text-xl font-bold mb-4')
                ui.label('Monitor and coordinate fuel deliveries').classes('text-gray-500')

            # Inventory Monitoring Panel
            with ui.tab_panel(inventory_tab):
                ui.label('Inventory Monitoring').classes('text-xl font-bold mb-4')
                ui.label('Monitor fuel inventory levels').classes('text-gray-500')

            # Customer Complaints Panel
            with ui.tab_panel(complaints_tab):
                ui.label('Customer Complaints').classes('text-xl font-bold mb-4')
                ui.label('Handle customer complaints and escalations').classes('text-gray-500')

            # Safety Compliance Panel
            with ui.tab_panel(safety_tab):
                ui.label('Safety Compliance').classes('text-xl font-bold mb-4')
                ui.label('Ensure safety compliance and maintenance').classes('text-gray-500')

            # Pump Calibration Panel
            with ui.tab_panel(calibration_tab):
                ui.label('Pump Calibration Schedules').classes('text-xl font-bold mb-4')
                ui.label('Manage pump calibration schedules').classes('text-gray-500')

            # Supplier Coordination Panel
            with ui.tab_panel(suppliers_tab):
                ui.label('Supplier Coordination').classes('text-xl font-bold mb-4')
                ui.label('Coordinate with suppliers for fuel deliveries').classes('text-gray-500')

            # Timesheet Approval Panel
            with ui.tab_panel(timesheets_tab):
                ui.label('Timesheet Approval').classes('text-xl font-bold mb-4')
                ui.label('Review and approve employee timesheets').classes('text-gray-500')

            # Pump Supervision Panel
            with ui.tab_panel(supervision_tab):
                ui.label('Pump Attendant Supervision').classes('text-xl font-bold mb-4')
                ui.label('Supervise pump attendants during shifts').classes('text-gray-500')

            # Cleanliness & Safety Panel
            with ui.tab_panel(cleanliness_tab):
                ui.label('Station Cleanliness & Safety Standards').classes('text-xl font-bold mb-4')
                ui.label('Ensure station cleanliness and safety standards').classes('text-gray-500')

            # Cash Reconciliation Panel
            with ui.tab_panel(reconciliation_tab):
                ui.label('Daily Cash Reconciliation').classes('text-xl font-bold mb-4')
                ui.label('Conduct daily cash reconciliation with accountant').classes('text-gray-500')

        def load_operations_data():
            token = app.storage.user.get('token')
            res = {'done': False, 'staff': 0, 'deliveries': 0, 'complaints': 0, 'safety': 0, 'err': ''}
            
            def fetch():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url

                    # Get staff on duty
                    r1 = httpx.get(f'{base}/staff_management/attendance', headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        data = r1.json()
                        res['staff'] = len([s for s in data if s.get('status') == 'present']) if isinstance(data, list) else 0

                    # Get fuel deliveries
                    r2 = httpx.get(f'{base}/inventory/deliveries', headers=headers, timeout=10.0)
                    if r2.status_code == 200:
                        data = r2.json()
                        res['deliveries'] = len(data) if isinstance(data, list) else 0

                    # Get complaints
                    r3 = httpx.get(f'{base}/complaints/complaints', headers=headers, timeout=10.0)
                    if r3.status_code == 200:
                        data = r3.json()
                        res['complaints'] = len([c for c in data if c.get('status') == 'pending']) if isinstance(data, list) else 0

                    # Get safety checks
                    r4 = httpx.get(f'{base}/safety/checks', headers=headers, timeout=10.0)
                    if r4.status_code == 200:
                        data = r4.json()
                        res['safety'] = len([s for s in data if s.get('status') == 'due']) if isinstance(data, list) else 0

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                
                if not res['err']:
                    staff_on_duty_label.set_text(str(res['staff']))
                    deliveries_label.set_text(str(res['deliveries']))
                    complaints_label.set_text(str(res['complaints']))
                    safety_checks_label.set_text(str(res['safety']))

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_operations_data()

    dashboard_layout(content)
