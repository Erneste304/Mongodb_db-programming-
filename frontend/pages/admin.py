"""
Admin Dashboard Pages
Staff scheduling, attendance, timesheets, operations, safety, calibration, deliveries, complaints
"""
from nicegui import ui
from frontend.state import auth_state, dashboard_layout
import httpx


def schedules_page():
    """Staff scheduling page"""
    def content():
        ui.label('Staff Scheduling').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Create Schedule', on_click=lambda: ui.notify('Create schedule dialog', type='info'))
            ui.input('Week').props('placeholder="Select week"')
            ui.button('Generate', on_click=lambda: ui.notify('Generating schedule...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Weekly Schedule').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'monday', 'label': 'Monday', 'field': 'monday'},
                    {'name': 'tuesday', 'label': 'Tuesday', 'field': 'tuesday'},
                    {'name': 'wednesday', 'label': 'Wednesday', 'field': 'wednesday'},
                    {'name': 'thursday', 'label': 'Thursday', 'field': 'thursday'},
                    {'name': 'friday', 'label': 'Friday', 'field': 'friday'},
                    {'name': 'saturday', 'label': 'Saturday', 'field': 'saturday'},
                    {'name': 'sunday', 'label': 'Sunday', 'field': 'sunday'},
                ],
                rows=[
                    {'employee': 'John Doe', 'monday': '8AM-4PM', 'tuesday': '8AM-4PM', 'wednesday': 'Off', 'thursday': '8AM-4PM', 'friday': '8AM-4PM', 'saturday': 'Off', 'sunday': 'Off'},
                ],
                row_key='employee'
            ).classes('w-full')
    
    dashboard_layout(content)


def attendance_page():
    """Attendance tracking page"""
    def content():
        ui.label('Attendance Tracking').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Date').props('type="date"')
            ui.button('Record Attendance', on_click=lambda: ui.notify('Record attendance dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Today\'s Attendance').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'check_in', 'label': 'Check In', 'field': 'check_in'},
                    {'name': 'check_out', 'label': 'Check Out', 'field': 'check_out'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'notes', 'label': 'Notes', 'field': 'notes'},
                ],
                rows=[
                    {'employee': 'John Doe', 'check_in': '8:00 AM', 'check_out': '4:00 PM', 'status': 'Present', 'notes': ''},
                ],
                row_key='employee'
            ).classes('w-full')
    
    dashboard_layout(content)


def timesheets_page():
    """Timesheet management page"""
    def content():
        ui.label('Timesheet Management').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Period').props('placeholder="Select period"')
            ui.button('Generate Timesheets', on_click=lambda: ui.notify('Generating timesheets...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Pending Approval').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'hours', 'label': 'Total Hours', 'field': 'hours'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'employee': 'John Doe', 'period': 'Week 3', 'hours': '40', 'status': 'Pending', 'actions': ''},
                ],
                row_key='employee'
            ).classes('w-full')
    
    dashboard_layout(content)


def operations_page():
    """Station operations log page"""
    def content():
        ui.label('Station Operations Log').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Log Operation', on_click=lambda: ui.notify('Log operation dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Recent Operations').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'timestamp', 'label': 'Timestamp', 'field': 'timestamp'},
                    {'name': 'operation', 'label': 'Operation', 'field': 'operation'},
                    {'name': 'performed_by', 'label': 'Performed By', 'field': 'performed_by'},
                    {'name': 'notes', 'label': 'Notes', 'field': 'notes'},
                ],
                rows=[
                    {'timestamp': '2024-01-15 08:00', 'operation': 'Station Opened', 'performed_by': 'admin', 'notes': 'Daily opening procedure'},
                ],
                row_key='timestamp'
            ).classes('w-full')
    
    dashboard_layout(content)


def safety_page():
    """Safety compliance page"""
    def content():
        ui.label('Safety Compliance').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Record Inspection', on_click=lambda: ui.notify('Record inspection dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Safety Inspections').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'type', 'label': 'Inspection Type', 'field': 'type'},
                    {'name': 'inspector', 'label': 'Inspector', 'field': 'inspector'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'date': '2024-01-15', 'type': 'Daily Safety Check', 'inspector': 'admin', 'status': 'Passed', 'actions': ''},
                ],
                row_key='date'
            ).classes('w-full')
    
    dashboard_layout(content)


def calibration_page():
    """Pump calibration page"""
    def content():
        ui.label('Pump Calibration').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Schedule Calibration', on_click=lambda: ui.notify('Schedule calibration dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Calibration Schedule').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'pump_id', 'label': 'Pump ID', 'field': 'pump_id'},
                    {'name': 'last_calibration', 'label': 'Last Calibration', 'field': 'last_calibration'},
                    {'name': 'next_calibration', 'label': 'Next Calibration', 'field': 'next_calibration'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[
                    {'pump_id': 'PUMP-001', 'last_calibration': '2024-01-01', 'next_calibration': '2024-04-01', 'status': 'OK'},
                ],
                row_key='pump_id'
            ).classes('w-full')
    
    dashboard_layout(content)


def deliveries_page():
    """Supplier deliveries page"""
    def content():
        ui.label('Supplier Deliveries').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Record Delivery', on_click=lambda: ui.notify('Record delivery dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Recent Deliveries').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'supplier', 'label': 'Supplier', 'field': 'supplier'},
                    {'name': 'fuel_type', 'label': 'Fuel Type', 'field': 'fuel_type'},
                    {'name': 'quantity', 'label': 'Quantity (L)', 'field': 'quantity'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[
                    {'date': '2024-01-15', 'supplier': 'Total Rwanda', 'fuel_type': 'Petrol', 'quantity': '5000', 'status': 'Received'},
                ],
                row_key='date'
            ).classes('w-full')
    
    dashboard_layout(content)


def complaints_page():
    """Customer complaints page"""
    def content():
        ui.label('Customer Complaints').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Log Complaint', on_click=lambda: ui.notify('Log complaint dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Open Complaints').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'customer', 'label': 'Customer', 'field': 'customer'},
                    {'name': 'complaint', 'label': 'Complaint', 'field': 'complaint'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'date': '2024-01-15', 'customer': 'Customer A', 'complaint': 'Pump not working properly', 'status': 'In Progress', 'actions': ''},
                ],
                row_key='date'
            ).classes('w-full')
    
    dashboard_layout(content)
