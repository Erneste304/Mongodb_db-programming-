"""
Admin Dashboard Pages
Staff scheduling, attendance, timesheets, operations, safety, calibration, deliveries, complaints
"""
from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def schedules_page():
    """Staff scheduling page"""
    def content():
        ui.label('Staff Scheduling').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Create Schedule', on_click=lambda: ui.notify(
                'Create schedule dialog', type='info'))
            ui.input('Week').props('placeholder="Select week"')
            ui.button('Generate', on_click=lambda: ui.notify(
                'Generating schedule...', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Weekly Schedule').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'shift_date', 'label': 'Date', 'field': 'shift_date'},
                    {'name': 'start_time', 'label': 'Start', 'field': 'start_time'},
                    {'name': 'end_time', 'label': 'End', 'field': 'end_time'},
                    {'name': 'role', 'label': 'Role', 'field': 'role'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='shift_date'
            ).classes('w-full').props('loading')

        def load_schedules():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/schedules/all'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    ui.notify(f"Load error: {res['err']}", type='negative')
                else:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_schedules()

    dashboard_layout(content)


def attendance_page():
    """Attendance tracking page"""
    def content():
        ui.label('Attendance Tracking').classes('text-2xl font-bold mb-6')

        # Record Attendance Dialog
        with ui.dialog() as record_dialog, ui.card().classes('w-96'):
            ui.label('Record Staff Attendance').classes(
                'text-xl font-bold mb-4')
            employee_name = ui.input('Employee Name')
            attendance_date = ui.input('Date').props(
                'type=date').classes('w-full')
            status_select = ui.select(
                ['Present', 'Absent', 'Late', 'Excused'], label='Status').classes('w-full')
            check_in = ui.input('Check In Time').props(
                'type=time').classes('w-full')
            check_out = ui.input('Check Out Time').props(
                'type=time').classes('w-full')

            async def save_attendance():
                if not all([employee_name.value, attendance_date.value, status_select.value]):
                    ui.notify('Please fill required fields', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "employee": employee_name.value,
                    "date": attendance_date.value,
                    "status": status_select.value,
                    "check_in": check_in.value,
                    "check_out": check_out.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/attendance"
                    response = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if response.status_code in (200, 201):
                        ui.notify('Attendance recorded successfully',
                                  type='positive')
                        record_dialog.close()
                        load_attendance()
                    else:
                        ui.notify(f"Error: {response.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=record_dialog.close).props('flat')
                ui.button('Save', on_click=save_attendance).props(
                    'elevated color=green')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Date').props('type="date"')
            ui.button('Record Attendance', on_click=record_dialog.open)

        with ui.card().classes('w-full'):
            ui.label('Today\'s Attendance').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'check_in', 'label': 'Check In', 'field': 'check_in'},
                    {'name': 'check_out', 'label': 'Check Out', 'field': 'check_out'},
                    {'name': 'hours', 'label': 'Hours', 'field': 'hours_worked'},
                ],
                rows=[],
                row_key='date'
            ).classes('w-full').props('loading')

        def load_attendance():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/attendance/all'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    ui.notify(f"Load error: {res['err']}", type='negative')
                else:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_attendance()

    dashboard_layout(content)


def timesheets_page():
    """Timesheet management page"""
    def content():
        ui.label('Timesheet Management').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Period').props('placeholder="Select period"')
            ui.button('Generate Timesheets', on_click=lambda: ui.notify(
                'Generating timesheets...', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Pending Approval').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'user_id'},
                    {'name': 'period', 'label': 'Period', 'field': 'pay_period'},
                    {'name': 'hours', 'label': 'Total Hours', 'field': 'total_hours'},
                    {'name': 'pay', 'label': 'Total Pay', 'field': 'total_pay'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='timesheet_id'
            ).classes('w-full').props('loading')

        def load_timesheets():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/timesheets/pending'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    ui.notify(f"Load error: {res['err']}", type='negative')
                else:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_timesheets()

    dashboard_layout(content)


def operations_page():
    """Station operations log page"""
    def content():
        ui.label('Station Operations Log').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Log Operation', on_click=lambda: ui.notify(
                'Log operation dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Recent Operations').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
                    {'name': 'operation', 'label': 'Operation',
                        'field': 'operation_type'},
                    {'name': 'performed_by', 'label': 'Performed By',
                        'field': 'performed_by'},
                    {'name': 'notes', 'label': 'Notes', 'field': 'notes'},
                ],
                rows=[],
                row_key='operation_id'
            ).classes('w-full').props('loading')

        def load_ops():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/station-operations'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if not res['err']:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_ops()

    dashboard_layout(content)


def safety_page():
    """Safety compliance page"""
    def content():
        ui.label('Safety Compliance').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Record Inspection', on_click=lambda: ui.notify(
                'Record inspection dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Safety Inspections').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'type', 'label': 'Inspection Type',
                        'field': 'inspection_type'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'inspector', 'label': 'Inspector',
                        'field': 'inspected_by'},
                ],
                rows=[],
                row_key='record_id'
            ).classes('w-full').props('loading')

        def load_safety():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    # Assuming a default station ID or fetching all if supported
                    url = f'{auth_state.api_base_url}/staff-management/safety-inspections/all'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if not res['err']:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_safety()

    dashboard_layout(content)


def calibration_page():
    """Pump calibration page"""
    def content():
        ui.label('Pump Calibration').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Schedule Calibration', on_click=lambda: ui.notify(
                'Schedule calibration dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Calibration Schedule').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'pump_id', 'label': 'Pump ID', 'field': 'pump_id'},
                    {'name': 'next_due', 'label': 'Next Calibration',
                        'field': 'next_due'},
                    {'name': 'cert', 'label': 'Cert #',
                        'field': 'certificate_number'},
                ],
                rows=[],
                row_key='pump_id'
            ).classes('w-full').props('loading')

        def load_calib():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/pump-calibrations/pending'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if not res['err']:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_calib()

    dashboard_layout(content)


def deliveries_page():
    """Supplier deliveries page"""
    def content():
        ui.label('Supplier Deliveries').classes('text-2xl font-bold mb-6')

        # Record Delivery Dialog
        with ui.dialog() as record_dialog, ui.card().classes('w-96'):
            ui.label('Record Fuel Delivery').classes('text-xl font-bold mb-4')
            supplier_name = ui.input('Supplier Name')
            fuel_type = ui.select(
                ['Petrol', 'Diesel', 'Kerosene'], label='Fuel Type').classes('w-full')
            quantity = ui.number(
                'Quantity (L)', format='%.0f').classes('w-full')
            expected_date = ui.input('Expected Date').props(
                'type=date').classes('w-full')

            async def save_delivery():
                if not all([supplier_name.value, fuel_type.value, quantity.value, expected_date.value]):
                    ui.notify('Please fill all fields', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "supplier_name": supplier_name.value,
                    "fuel_type": fuel_type.value,
                    "quantity_ordered": quantity.value,
                    "expected_date": expected_date.value,
                    "status": "Pending"
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/supplier-deliveries"
                    response = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if response.status_code in (200, 201):
                        ui.notify('Delivery recorded successfully',
                                  type='positive')
                        record_dialog.close()
                        load_deliveries()
                    else:
                        ui.notify(f"Error: {response.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=record_dialog.close).props('flat')
                ui.button('Record', on_click=save_delivery).props(
                    'elevated color=green')

        with ui.card().classes('w-full mb-4'):
            ui.button('Record Delivery', on_click=record_dialog.open)

        with ui.card().classes('w-full'):
            ui.label('Recent Deliveries').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'date', 'label': 'Expected Date',
                        'field': 'expected_date'},
                    {'name': 'supplier', 'label': 'Supplier',
                        'field': 'supplier_name'},
                    {'name': 'fuel_type', 'label': 'Fuel Type', 'field': 'fuel_type'},
                    {'name': 'quantity',
                        'label': 'Quantity (L)', 'field': 'quantity_ordered'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='delivery_id'
            ).classes('w-full').props('loading')

        def load_deliveries():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/supplier-deliveries'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if not res['err']:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_deliveries()

    dashboard_layout(content)


def complaints_page():
    """Customer complaints page"""
    def content():
        ui.label('Customer Complaints').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Log Complaint', on_click=lambda: ui.notify(
                'Log complaint dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Open Complaints').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'reported_at'},
                    {'name': 'customer', 'label': 'Customer',
                        'field': 'customer_name'},
                    {'name': 'type', 'label': 'Type', 'field': 'type'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'severity', 'label': 'Severity', 'field': 'severity'},
                ],
                rows=[],
                row_key='complaint_id'
            ).classes('w-full').props('loading')

        def load_complaints():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                # httpx already imported at top of file
                try:
                    url = f'{auth_state.api_base_url}/staff-management/complaints'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
                        try:
                            err_json = r.json()
                            res['err'] = err_json.get('message') or err_json.get(
                                'detail') or f"HTTP {r.status_code}"
                        except:
                            res['err'] = f"HTTP {r.status_code}"
                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if not res['err']:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_complaints()

    dashboard_layout(content)
