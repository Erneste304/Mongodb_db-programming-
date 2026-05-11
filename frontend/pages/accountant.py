"""
Accountant Dashboard Pages
Bank reconciliation, accounts receivable/payable, tax records, cost tracking, commissions, daily closing, compliance
"""
from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def reconciliation_page():
    """Bank reconciliation page"""
    def content():
        ui.label('Bank Reconciliation').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Create Reconciliation', on_click=lambda: ui.notify(
                'Create reconciliation dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Recent Reconciliations').classes(
                'text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'date', 'label': 'Statement Date',
                        'field': 'statement_date'},
                    {'name': 'bank_account', 'label': 'Bank', 'field': 'bank_name'},
                    {'name': 'system_balance', 'label': 'System Balance',
                        'field': 'system_balance'},
                    {'name': 'bank_balance', 'label': 'Bank Balance',
                        'field': 'statement_balance'},
                    {'name': 'difference', 'label': 'Difference',
                        'field': 'difference'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='reconciliation_id'
            ).classes('w-full').props('loading')

        def load_reconciliations():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/bank-reconciliation'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_reconciliations()

    dashboard_layout(content)


def receivable_page():
    """Accounts receivable page"""
    def content():
        ui.label('Accounts Receivable').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Record Invoice', on_click=lambda: ui.notify(
                'Record invoice dialog', type='info'))
            ui.button('Record Payment', on_click=lambda: ui.notify(
                'Record payment dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Outstanding Invoices').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'invoice_number', 'label': 'Invoice #',
                        'field': 'invoice_number'},
                    {'name': 'customer', 'label': 'Customer',
                        'field': 'customer_name'},
                    {'name': 'amount',
                        'label': 'Amount (RWF)', 'field': 'total_amount'},
                    {'name': 'due_date', 'label': 'Due Date', 'field': 'due_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='ar_id'
            ).classes('w-full').props('loading')

        def load_receivables():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/accounts-receivable'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_receivables()

    dashboard_layout(content)


def payable_page():
    """Accounts payable page"""
    def content():
        ui.label('Accounts Payable').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Record Expense', on_click=lambda: ui.notify(
                'Record expense dialog', type='info'))
            ui.button('Process Payment', on_click=lambda: ui.notify(
                'Process payment dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Outstanding Payments').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'supplier', 'label': 'Supplier',
                        'field': 'supplier_name'},
                    {'name': 'invoice_number', 'label': 'Invoice #',
                        'field': 'invoice_number'},
                    {'name': 'amount',
                        'label': 'Amount (RWF)', 'field': 'total_amount'},
                    {'name': 'due_date', 'label': 'Due Date', 'field': 'due_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='ap_id'
            ).classes('w-full').props('loading')

        def load_payables():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/accounts-payable'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_payables()

    dashboard_layout(content)


def tax_page():
    """Tax records page"""
    def content():
        ui.label('Tax Records').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Create Tax Record', on_click=lambda: ui.notify(
                'Create tax record dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Tax Records').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'tax_type', 'label': 'Tax Type', 'field': 'tax_type'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'amount',
                        'label': 'Amount (RWF)', 'field': 'tax_amount'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='tax_id'
            ).classes('w-full').props('loading')

        def load_tax():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/tax-records'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_tax()

    dashboard_layout(content)


def costs_page():
    """Fuel cost tracking page"""
    def content():
        ui.label('Fuel Cost Tracking').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.button('Record Cost', on_click=lambda: ui.notify(
                'Record cost dialog', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Cost vs Margin Analysis').classes(
                'text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'fuel_type', 'label': 'Fuel Type', 'field': 'fuel_type'},
                    {'name': 'purchase_price', 'label': 'Purchase Price',
                        'field': 'purchase_price'},
                    {'name': 'selling_price', 'label': 'Selling Price',
                        'field': 'selling_price'},
                    {'name': 'profit', 'label': 'Profit/L',
                        'field': 'profit_per_liter'},
                    {'name': 'margin_percent', 'label': 'Margin %',
                        'field': 'profit_margin_percentage'},
                ],
                rows=[],
                row_key='tracking_id'
            ).classes('w-full').props('loading')

        def load_costs():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/fuel-cost-tracking'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_costs()

    dashboard_layout(content)


def commissions_page():
    """Commission calculation page"""
    def content():
        ui.label('Staff Commissions').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Period').props('placeholder="Select period"')
            ui.button('Calculate Commissions', on_click=lambda: ui.notify(
                'Calculating commissions...', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Commission Summary').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'employee', 'label': 'Employee', 'field': 'user_name'},
                    {'name': 'period', 'label': 'Period', 'field': 'period'},
                    {'name': 'sales_amount', 'label': 'Sales Amount',
                        'field': 'total_sales'},
                    {'name': 'commission_amount', 'label': 'Commission',
                        'field': 'total_commission'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='commission_id'
            ).classes('w-full').props('loading')

        def load_commissions():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/commissions/pending'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_commissions()

    dashboard_layout(content)


def closing_page():
    """Daily closing page"""
    def content():
        ui.label('Daily Closing').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full mb-4'):
            ui.input('Date').props('type="date"')
            ui.button('Start Closing Process', on_click=lambda: ui.notify(
                'Starting closing process...', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Closing Summary').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'date', 'label': 'Date', 'field': 'closing_date'},
                    {'name': 'total', 'label': 'Total Sales', 'field': 'total_sales'},
                    {'name': 'variance', 'label': 'Variance',
                        'field': 'cash_variance'},
                    {'name': 'status', 'label': 'Verified', 'field': 'verified'},
                ],
                rows=[],
                row_key='closing_id'
            ).classes('w-full').props('loading')

            def load_closings():
                token = app.storage.user.get('token')
                res = {'done': False, 'rows': [], 'err': ''}
                table.props(add='loading')

                def fetch():
                    try:
                        import httpx  # Use httpx for consistency
                        # Remove redundant replace
                        url = f'{auth_state.api_base_url}/accounting/daily-closing'
                        r = httpx.get(
                            url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                        if r.status_code == 200:
                            res['rows'] = r.json()
                        else:
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

            load_closings()
            ui.button('Verify and Close Day', on_click=lambda: ui.notify(
                'Day closed successfully', type='positive')).classes('mt-4')

    dashboard_layout(content)


def compliance_page():
    """RURA compliance reports page"""
    def content():
        ui.label('RURA Compliance Reports').classes('text-2xl font-bold mb-6')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Report Period').props('placeholder="Select period"')
            ui.button('Generate Report', on_click=lambda: ui.notify(
                'Generating report...', type='info'))

        with ui.card().classes('w-full'):
            ui.label('Recent Reports').classes('text-lg font-bold mb-4')

            table = ui.table(
                columns=[
                    {'name': 'period', 'label': 'Period', 'field': 'report_period'},
                    {'name': 'liters', 'label': 'Total Liters',
                        'field': 'total_sales_liters'},
                    {'name': 'amount', 'label': 'Total Amount',
                        'field': 'total_sales_amount'},
                    {'name': 'date', 'label': 'Submitted Date',
                        'field': 'submitted_date'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='report_id'
            ).classes('w-full').props('loading')

        def load_reports():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:
                    import httpx  # Use httpx for consistency
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/accounting/rura-reports'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    else:
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

        load_reports()

    dashboard_layout(content)
