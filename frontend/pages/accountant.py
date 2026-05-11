"""
Accountant Dashboard Pages
Bank reconciliation, accounts receivable/payable, tax records, cost tracking, commissions, daily closing, compliance
"""
from nicegui import ui
from frontend.state import auth_state, dashboard_layout
import httpx


def reconciliation_page():
    """Bank reconciliation page"""
    def content():
        ui.label('Bank Reconciliation').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Create Reconciliation', on_click=lambda: ui.notify('Create reconciliation dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Recent Reconciliations').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'date'},
                    {'name': 'bank_account', 'label': 'Bank Account', 'field': 'bank_account'},
                    {'name': 'book_balance', 'label': 'Book Balance', 'field': 'book_balance'},
                    {'name': 'bank_balance', 'label': 'Bank Balance', 'field': 'bank_balance'},
                    {'name': 'difference', 'label': 'Difference', 'field': 'difference'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[
                    {'date': '2024-01-15', 'bank_account': 'Bank of Kigali - 001', 'book_balance': '5,000,000', 'bank_balance': '5,000,000', 'difference': '0', 'status': 'Reconciled'},
                ],
                row_key='date'
            ).classes('w-full')
    
    dashboard_layout(content)


def receivable_page():
    """Accounts receivable page"""
    def content():
        ui.label('Accounts Receivable').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Record Invoice', on_click=lambda: ui.notify('Record invoice dialog', type='info'))
            ui.button('Record Payment', on_click=lambda: ui.notify('Record payment dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Outstanding Invoices').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'invoice_number', 'label': 'Invoice #', 'field': 'invoice_number'},
                    {'name': 'customer', 'label': 'Customer', 'field': 'customer'},
                    {'name': 'amount', 'label': 'Amount (RWF)', 'field': 'amount'},
                    {'name': 'due_date', 'label': 'Due Date', 'field': 'due_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'invoice_number': 'INV-001', 'customer': 'Corporate Client A', 'amount': '1,500,000', 'due_date': '2024-01-30', 'status': 'Pending', 'actions': ''},
                ],
                row_key='invoice_number'
            ).classes('w-full')
    
    dashboard_layout(content)


def payable_page():
    """Accounts payable page"""
    def content():
        ui.label('Accounts Payable').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Record Expense', on_click=lambda: ui.notify('Record expense dialog', type='info'))
            ui.button('Process Payment', on_click=lambda: ui.notify('Process payment dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Outstanding Payments').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'supplier', 'label': 'Supplier', 'field': 'supplier'},
                    {'name': 'invoice_number', 'label': 'Invoice #', 'field': 'invoice_number'},
                    {'name': 'amount', 'label': 'Amount (RWF)', 'field': 'amount'},
                    {'name': 'due_date', 'label': 'Due Date', 'field': 'due_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'supplier': 'Total Rwanda', 'invoice_number': 'SUP-001', 'amount': '7,500,000', 'due_date': '2024-01-20', 'status': 'Pending', 'actions': ''},
                ],
                row_key='invoice_number'
            ).classes('w-full')
    
    dashboard_layout(content)


def tax_page():
    """Tax records page"""
    def content():
        ui.label('Tax Records').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Create Tax Record', on_click=lambda: ui.notify('Create tax record dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Tax Records').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'tax_type', 'label': 'Tax Type', 'field': 'tax_type'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'amount', 'label': 'Amount (RWF)', 'field': 'amount'},
                    {'name': 'due_date', 'label': 'Due Date', 'field': 'due_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[
                    {'tax_type': 'VAT', 'period': 'January 2024', 'amount': '450,000', 'due_date': '2024-02-15', 'status': 'Pending'},
                ],
                row_key='tax_type'
            ).classes('w-full')
    
    dashboard_layout(content)


def costs_page():
    """Fuel cost tracking page"""
    def content():
        ui.label('Fuel Cost Tracking').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.button('Record Cost', on_click=lambda: ui.notify('Record cost dialog', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Cost vs Margin Analysis').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'fuel_type', 'label': 'Fuel Type', 'field': 'fuel_type'},
                    {'name': 'purchase_price', 'label': 'Purchase Price', 'field': 'purchase_price'},
                    {'name': 'selling_price', 'label': 'Selling Price', 'field': 'selling_price'},
                    {'name': 'margin', 'label': 'Margin', 'field': 'margin'},
                    {'name': 'margin_percent', 'label': 'Margin %', 'field': 'margin_percent'},
                ],
                rows=[
                    {'fuel_type': 'Petrol', 'purchase_price': '1,200', 'selling_price': '1,500', 'margin': '300', 'margin_percent': '25%'},
                    {'fuel_type': 'Diesel', 'purchase_price': '1,100', 'selling_price': '1,400', 'margin': '300', 'margin_percent': '27%'},
                ],
                row_key='fuel_type'
            ).classes('w-full')
    
    dashboard_layout(content)


def commissions_page():
    """Commission calculation page"""
    def content():
        ui.label('Staff Commissions').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Period').props('placeholder="Select period"')
            ui.button('Calculate Commissions', on_click=lambda: ui.notify('Calculating commissions...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Commission Summary').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'employee'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'sales_amount', 'label': 'Sales Amount', 'field': 'sales_amount'},
                    {'name': 'commission_rate', 'label': 'Rate', 'field': 'commission_rate'},
                    {'name': 'commission_amount', 'label': 'Commission', 'field': 'commission_amount'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'employee': 'John Doe', 'period': 'January 2024', 'sales_amount': '10,000,000', 'commission_rate': '2%', 'commission_amount': '200,000', 'status': 'Pending Approval', 'actions': ''},
                ],
                row_key='employee'
            ).classes('w-full')
    
    dashboard_layout(content)


def closing_page():
    """Daily closing page"""
    def content():
        ui.label('Daily Closing').classes('text-2xl font-bold mb-6')
        
        with ui.card().classes('w-full mb-4'):
            ui.input('Date').props('type="date"')
            ui.button('Start Closing Process', on_click=lambda: ui.notify('Starting closing process...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Closing Summary').classes('text-lg font-bold mb-4')
            
            with ui.column().classes('w-full gap-4'):
                with ui.row().classes('w-full justify-between'):
                    ui.label('Total Cash Sales')
                    ui.label('RWF 0').classes('font-bold')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('Total Card Sales')
                    ui.label('RWF 0').classes('font-bold')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('Total Mobile Money')
                    ui.label('RWF 0').classes('font-bold')
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('Total Credit Sales')
                    ui.label('RWF 0').classes('font-bold')
                
                ui.separator()
                
                with ui.row().classes('w-full justify-between'):
                    ui.label('Grand Total')
                    ui.label('RWF 0').classes('font-bold text-xl')
                
                ui.button('Verify and Close Day', on_click=lambda: ui.notify('Day closed successfully', type='positive')).classes('mt-4')
    
    dashboard_layout(content)


def compliance_page():
    """RURA compliance reports page"""
    def content():
        ui.label('RURA Compliance Reports').classes('text-2xl font-bold mb-6')
        
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Report Period').props('placeholder="Select period"')
            ui.button('Generate Report', on_click=lambda: ui.notify('Generating report...', type='info'))
        
        with ui.card().classes('w-full'):
            ui.label('Recent Reports').classes('text-lg font-bold mb-4')
            
            ui.table(
                columns=[
                    {'name': 'report_type', 'label': 'Report Type', 'field': 'report_type'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'generated_date', 'label': 'Generated Date', 'field': 'generated_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                    {'name': 'actions', 'label': 'Actions', 'field': 'actions'},
                ],
                rows=[
                    {'report_type': 'Monthly Fuel Sales', 'period': 'January 2024', 'generated_date': '2024-02-01', 'status': 'Submitted', 'actions': ''},
                ],
                row_key='report_type'
            ).classes('w-full')
    
    dashboard_layout(content)
