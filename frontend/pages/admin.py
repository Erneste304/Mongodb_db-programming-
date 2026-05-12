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

        # Create Schedule Dialog
        with ui.dialog() as schedule_dialog, ui.card().classes('w-96'):
            ui.label('Create Staff Schedule').classes('text-xl font-bold mb-4')
            sched_user_id = ui.input('User ID (Employee)').classes('w-full')
            sched_date = ui.input('Shift Date').props(
                'type=date').classes('w-full')
            sched_start = ui.input('Start Time').props(
                'type=time').classes('w-full')
            sched_end = ui.input('End Time').props(
                'type=time').classes('w-full')
            sched_role = ui.input('Role during Shift').classes('w-full')
            sched_notes = ui.textarea('Notes').classes('w-full')

            async def save_schedule():
                if not all([sched_user_id.value, sched_date.value, sched_start.value, sched_end.value]):
                    ui.notify('Please fill required fields', type='warning')
                    return

                token = app.storage.user.get('token')
                # Convert strings to appropriate types for backend
                payload = {
                    "user_id": sched_user_id.value,
                    "shift_date": f"{sched_date.value}T00:00:00Z",
                    "start_time": sched_start.value,
                    "end_time": sched_end.value,
                    "role_during_shift": sched_role.value,
                    "notes": sched_notes.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/schedules"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Schedule created successfully',
                                  type='positive')
                        schedule_dialog.close()
                        load_schedules()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=schedule_dialog.close).props(
                    'flat')
                ui.button('Save', on_click=save_schedule).props(
                    'elevated color=green')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Create Schedule',
                      on_click=schedule_dialog.open).props('icon=add')
            ui.input('Week').props('placeholder="Select week"')

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
                row_key='schedule_id'
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
            user_id_input = ui.input('User ID')
            schedule_id_input = ui.input('Schedule ID')
            attendance_date = ui.input('Date').props(
                'type=date').classes('w-full')
            status_select = ui.select(
                {'present': 'Present', 'absent': 'Absent', 'late': 'Late',
                 'on_leave': 'On Leave', 'sick': 'Sick'},
                label='Status').classes('w-full')
            check_in = ui.input('Check In Time').props(
                'type=time').classes('w-full')
            check_out = ui.input('Check Out Time').props(
                'type=time').classes('w-full')

            async def save_attendance():
                if not all([user_id_input.value, schedule_id_input.value, attendance_date.value, status_select.value]):
                    ui.notify('Please fill required fields', type='warning')
                    return

                token = app.storage.user.get('token')

                # Format ISO datetimes for the backend Pydantic model
                check_in_dt = f"{attendance_date.value}T{check_in.value}:00Z" if check_in.value else None
                check_out_dt = f"{attendance_date.value}T{check_out.value}:00Z" if check_out.value else None
                attendance_dt_iso = f"{attendance_date.value}T00:00:00Z"

                payload = {
                    "user_id": user_id_input.value,
                    "schedule_id": schedule_id_input.value,
                    "attendance_date": attendance_dt_iso,
                    "status": status_select.value,
                    "check_in_time": check_in_dt,
                    "check_out_time": check_out_dt
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
                    {'name': 'attendance_id', 'label': 'ID',
                        'field': 'attendance_id', 'classes': 'text-xs'},
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'check_in', 'label': 'Check In', 'field': 'check_in'},
                    {'name': 'check_out', 'label': 'Check Out', 'field': 'check_out'},
                    {'name': 'hours', 'label': 'Hours', 'field': 'hours_worked'},
                ],
                rows=[],
                row_key='attendance_id'  # Changed to attendance_id for uniqueness
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
                    if "403" in res['err'] or "Role level" in res['err']:
                        ui.notify("Access Denied: You do not have permission to view attendance records.",
                                  type='negative', icon='security')
                    else:
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

        # Log Operation Dialog
        with ui.dialog() as op_dialog, ui.card().classes('w-96'):
            ui.label('Log Station Operation').classes('text-xl font-bold mb-4')
            op_station = ui.input(
                'Station ID', value='ST-001').classes('w-full')
            op_type = ui.select(['opening', 'closing'],
                                label='Operation Type').classes('w-full')

            with ui.column().classes('w-full gap-1 my-2'):
                ui.label('Checklist').classes('text-sm font-bold')
                pumps_ok = ui.checkbox('Pumps Operational')
                tanks_ok = ui.checkbox('Tanks Checked')
                safety_ok = ui.checkbox('Safety Equipment Checked')
                cash_ok = ui.checkbox('Cash Register Ready')

            op_staff = ui.input(
                'Staff IDs (comma separated)').classes('w-full')
            op_notes = ui.textarea('Issues/Notes').classes('w-full')

            async def save_op():
                token = app.storage.user.get('token')
                payload = {
                    "station_id": op_station.value,
                    "operation_type": op_type.value,
                    "pumps_operational": pumps_ok.value,
                    "tanks_checked": tanks_ok.value,
                    "safety_equipment_checked": safety_ok.value,
                    "cash_register_ready": cash_ok.value,
                    "staff_present": [s.strip() for s in op_staff.value.split(',') if s.strip()],
                    "issues_noted": op_notes.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/station-operations"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Operation logged successfully',
                                  type='positive')
                        op_dialog.close()
                        load_ops()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=op_dialog.close).props('flat')
                ui.button('Log', on_click=save_op).props('elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Log Operation', on_click=op_dialog.open).props(
                'icon=assignment')

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

        # Safety Inspection Dialog
        with ui.dialog() as safety_dialog, ui.card().classes('w-96'):
            ui.label('Record Safety Inspection').classes(
                'text-xl font-bold mb-4')
            safe_station = ui.input(
                'Station ID', value='ST-001').classes('w-full')
            safe_type = ui.select(
                ['Routine', 'Monthly', 'Annual'], label='Inspection Type').classes('w-full')

            with ui.column().classes('w-full gap-0 my-2'):
                fire_ok = ui.checkbox('Fire Extinguishers OK')
                spill_ok = ui.checkbox('Spill Kit Available')
                signs_ok = ui.checkbox('No Smoking Signs Visible')
                exits_ok = ui.checkbox('Emergency Exits Clear')
                leaks_ok = ui.checkbox('Pumps/Leads No Leaks')
                secure_ok = ui.checkbox('Tanks Secure')
                equip_ok = ui.checkbox('Safety Equipment Functional')

            safe_issues = ui.textarea('Issues Found').classes('w-full')
            safe_actions = ui.textarea('Corrective Actions').classes('w-full')

            async def save_safety():
                token = app.storage.user.get('token')
                payload = {
                    "station_id": safe_station.value,
                    "inspection_type": safe_type.value,
                    "fire_extinguishers_ok": fire_ok.value,
                    "spill_kit_available": spill_ok.value,
                    "no_smoking_signs_visible": signs_ok.value,
                    "emergency_exits_clear": exits_ok.value,
                    "pumps_no_leaks": leaks_ok.value,
                    "tanks_secure": secure_ok.value,
                    "safety_equipment_functional": equip_ok.value,
                    "issues_found": safe_issues.value,
                    "corrective_actions": safe_actions.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/safety-inspections"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Safety inspection recorded',
                                  type='positive')
                        safety_dialog.close()
                        load_safety()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=safety_dialog.close).props('flat')
                ui.button('Record', on_click=save_safety).props(
                    'elevated color=red')

        with ui.card().classes('w-full mb-4'):
            ui.button('Record Inspection', on_click=safety_dialog.open).props(
                'icon=security')

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

        # Schedule Calibration Dialog
        with ui.dialog() as calib_dialog, ui.card().classes('w-96'):
            ui.label('Schedule Pump Calibration').classes(
                'text-xl font-bold mb-4')
            pump_id = ui.input('Pump ID').classes('w-full')
            tank_id = ui.input('Tank ID').classes('w-full')
            due_date = ui.input('Next Due Date').props(
                'type=date').classes('w-full')

            async def save_calibration():
                if not pump_id.value or not due_date.value:
                    ui.notify('Pump ID and Date are required', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "pump_id": pump_id.value,
                    "tank_id": tank_id.value,
                    "next_calibration_due": f"{due_date.value}T00:00:00Z",
                    "status": "pending"
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/pump-calibrations"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify(
                            'Calibration scheduled successfully', type='positive')
                        calib_dialog.close()
                        load_calib()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=calib_dialog.close).props('flat')
                ui.button('Schedule', on_click=save_calibration).props(
                    'elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Schedule Calibration',
                      on_click=calib_dialog.open).props('icon=timer')

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
            supplier_id = ui.input('Supplier ID').classes('w-full')
            supplier_name = ui.input('Supplier Name')
            fuel_type = ui.select(
                ['Petrol', 'Diesel', 'Kerosene'], label='Fuel Type').classes('w-full')
            quantity = ui.number(
                'Quantity (L)', format='%.0f').classes('w-full')
            tank_id = ui.input('Tank ID').classes('w-full')
            expected_date = ui.input('Expected Date').props(
                'type=date').classes('w-full')

            async def save_delivery():
                if not all([supplier_id.value, supplier_name.value, fuel_type.value, quantity.value, expected_date.value]):
                    ui.notify('Please fill all fields', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "supplier_id": supplier_id.value,
                    "supplier_name": supplier_name.value,
                    "fuel_type": fuel_type.value,
                    "quantity_ordered": quantity.value,
                    "tank_id": tank_id.value or "TANK-001",
                    "expected_delivery_date": f"{expected_date.value}T00:00:00Z"
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/supplier-deliveries/order"
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

        # Log Complaint Dialog
        with ui.dialog() as complaint_dialog, ui.card().classes('w-96'):
            ui.label('Log Customer Complaint').classes(
                'text-xl font-bold mb-4')
            comp_name = ui.input('Customer Name').classes('w-full')
            comp_phone = ui.input('Customer Phone').classes('w-full')
            comp_type = ui.select(
                ['Service', 'Fuel Quality', 'Pricing', 'Technical'], label='Type').classes('w-full')
            comp_severity = ui.select(
                ['low', 'medium', 'high', 'critical'], label='Severity').classes('w-full')
            comp_desc = ui.textarea('Description').classes('w-full')
            comp_tx = ui.input('Transaction ID (Optional)').classes('w-full')
            comp_pump = ui.number('Pump # (Optional)',
                                  format='%.0f').classes('w-full')

            async def save_complaint():
                if not comp_name.value or not comp_desc.value:
                    ui.notify('Name and Description required', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "customer_name": comp_name.value,
                    "customer_phone": comp_phone.value,
                    "complaint_type": comp_type.value,
                    "description": comp_desc.value,
                    "severity": comp_severity.value,
                    "related_transaction_id": comp_tx.value,
                    "pump_number": comp_pump.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/staff-management/complaints"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Complaint recorded', type='positive')
                        complaint_dialog.close()
                        load_complaints()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=complaint_dialog.close).props(
                    'flat')
                ui.button('Log', on_click=save_complaint).props(
                    'elevated color=orange')

        with ui.card().classes('w-full mb-4'):
            ui.button('Log Complaint', on_click=complaint_dialog.open).props(
                'icon=feedback')

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
