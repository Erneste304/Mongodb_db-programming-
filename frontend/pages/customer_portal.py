from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def customer_portal_page():
    """Customer portal for checking loyalty points, statements, and invoices"""
    def content():
        ui.label('Customer Portal').classes('text-3xl font-bold mb-6 text-slate-800')

        # Customer Info Card
        with ui.card().classes('max-w-4xl mx-auto p-6 shadow-xl rounded-2xl border border-slate-100 mb-6'):
            ui.label('Account Information').classes('text-xl font-bold mb-4')
            
            customer_name_label = ui.label('Loading...').classes('text-lg')
            customer_type_label = ui.label('Loading...').classes('text-lg')
            customer_phone_label = ui.label('Loading...').classes('text-lg')
            
            # Loyalty Points
            with ui.row().classes('mt-4 p-4 bg-purple-50 rounded-xl'):
                ui.label('Loyalty Points').classes('text-sm text-purple-600 font-bold uppercase tracking-wider')
                loyalty_points_label = ui.label('0').classes('text-3xl font-black text-purple-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            statements_tab = ui.tab('Monthly Statements')
            invoices_tab = ui.tab('Invoices')
            transactions_tab = ui.tab('Transaction History')
            complaints_tab = ui.tab('My Complaints')

        with ui.tab_panels(tabs, value=statements_tab).classes('w-full bg-transparent'):
            # Monthly Statements Panel
            with ui.tab_panel(statements_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Monthly Statements').classes('text-xl font-bold')
                
                statements_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Statement ID', 'field': 'statement_id'},
                        {'name': 'period', 'label': 'Period', 'field': 'period_start'},
                        {'name': 'opening', 'label': 'Opening (RWF)', 'field': 'opening_balance'},
                        {'name': 'purchases', 'label': 'Purchases (RWF)', 'field': 'purchases'},
                        {'name': 'payments', 'label': 'Payments (RWF)', 'field': 'payments'},
                        {'name': 'closing', 'label': 'Closing (RWF)', 'field': 'closing_balance'},
                        {'name': 'status', 'label': 'Status', 'field': 'sent'},
                    ],
                    rows=[],
                    row_key='statement_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Invoices Panel
            with ui.tab_panel(invoices_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Invoices').classes('text-xl font-bold')
                
                invoices_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Invoice #', 'field': 'invoice_number'},
                        {'name': 'date', 'label': 'Invoice Date', 'field': 'invoice_date'},
                        {'name': 'due', 'label': 'Due Date', 'field': 'due_date'},
                        {'name': 'total', 'label': 'Total (RWF)', 'field': 'total_amount'},
                        {'name': 'paid', 'label': 'Paid (RWF)', 'field': 'amount_paid'},
                        {'name': 'balance', 'label': 'Balance (RWF)', 'field': 'balance_due'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='invoice_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Transaction History Panel
            with ui.tab_panel(transactions_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Transaction History').classes('text-xl font-bold')
                
                transactions_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Transaction ID', 'field': 'transaction_id'},
                        {'name': 'date', 'label': 'Date', 'field': 'created_at'},
                        {'name': 'fuel', 'label': 'Fuel Type', 'field': 'fuel_type'},
                        {'name': 'quantity', 'label': 'Quantity (L)', 'field': 'quantity_liters'},
                        {'name': 'amount', 'label': 'Amount (RWF)', 'field': 'total_amount'},
                        {'name': 'payment', 'label': 'Payment', 'field': 'payment_method'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='transaction_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Complaints Panel
            with ui.tab_panel(complaints_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('My Complaints').classes('text-xl font-bold')
                
                complaints_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Complaint ID', 'field': 'complaint_id'},
                        {'name': 'type', 'label': 'Type', 'field': 'complaint_type'},
                        {'name': 'severity', 'label': 'Severity', 'field': 'severity'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                        {'name': 'date', 'label': 'Date', 'field': 'created_at'},
                    ],
                    rows=[],
                    row_key='complaint_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_customer_data():
            token = app.storage.user.get('token')
            customer_id = app.storage.user.get('customer_id')
            
            res = {
                'done': False,
                'customer': None,
                'statements': [],
                'invoices': [],
                'transactions': [],
                'complaints': [],
                'err': ''
            }
            
            statements_table.props(add='loading')
            invoices_table.props(add='loading')
            transactions_table.props(add='loading')
            complaints_table.props(add='loading')

            def fetch():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url

                    # Get customer info
                    if customer_id:
                        r1 = httpx.get(f'{base}/sales/customers/{customer_id}', headers=headers, timeout=10.0)
                        if r1.status_code == 200:
                            res['customer'] = r1.json()

                    # Get statements
                    if customer_id:
                        r2 = httpx.get(f'{base}/billing/monthly-statements?customer_id={customer_id}', headers=headers, timeout=10.0)
                        if r2.status_code == 200:
                            res['statements'] = r2.json()

                    # Get invoices
                    if customer_id:
                        r3 = httpx.get(f'{base}/billing/invoices?customer_id={customer_id}', headers=headers, timeout=10.0)
                        if r3.status_code == 200:
                            res['invoices'] = r3.json()

                    # Get transactions
                    if customer_id:
                        r4 = httpx.get(f'{base}/sales/transactions?customer_id={customer_id}', headers=headers, timeout=10.0)
                        if r4.status_code == 200:
                            res['transactions'] = r4.json()

                    # Get complaints
                    if customer_id:
                        r5 = httpx.get(f'{base}/complaints/complaints', headers=headers, timeout=10.0)
                        if r5.status_code == 200:
                            res['complaints'] = r5.json()

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                statements_table.props(remove='loading')
                invoices_table.props(remove='loading')
                transactions_table.props(remove='loading')
                complaints_table.props(remove='loading')

                if not res['err']:
                    if res['customer']:
                        customer_name_label.set_text(res['customer'].get('name', 'N/A'))
                        customer_type_label.set_text(f"Type: {res['customer'].get('customer_type', 'N/A').capitalize()}")
                        customer_phone_label.set_text(f"Phone: {res['customer'].get('phone', 'N/A')}")
                        loyalty_points_label.set_text(str(res['customer'].get('loyalty_points', 0)))

                    statements_table.rows = res['statements']
                    invoices_table.rows = res['invoices']
                    transactions_table.rows = res['transactions']
                    complaints_table.rows = res['complaints']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_customer_data()

    dashboard_layout(content)
