"""
Accountant Dashboard Pages
Bank reconciliation, accounts receivable/payable, tax records, cost tracking, commissions, daily closing, compliance
"""
from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx
from datetime import datetime


def reconciliation_page():
    """Bank reconciliation page"""
    def content():
        ui.label('Bank Reconciliation').classes('text-2xl font-bold mb-6')

        # Create Reconciliation Dialog
        with ui.dialog() as recon_dialog, ui.card().classes('w-96'):
            ui.label('New Bank Reconciliation').classes(
                'text-xl font-bold mb-4')
            bank_name = ui.input('Bank Name').classes('w-full')
            account_num = ui.input('Account Number').classes('w-full')
            account_type = ui.select(
                ['current', 'savings', 'mobile_money'], label='Account Type').classes('w-full')
            statement_date = ui.input('Statement Date').props(
                'type=date').classes('w-full')
            bank_bal = ui.number('Statement Balance (RWF)').classes('w-full')
            system_bal = ui.number('System Balance (RWF)').classes('w-full')
            notes = ui.textarea('Notes').classes('w-full')

            async def save_reconciliation():
                if not all([bank_name.value, statement_date.value]):
                    ui.notify('Please fill required fields', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "bank_account_id": f"ACC-{bank_name.value[:3].upper()}",
                    "bank_name": bank_name.value,
                    "account_number": account_num.value,
                    "account_type": account_type.value,
                    "statement_date": f"{statement_date.value}T00:00:00Z",
                    "statement_balance": bank_bal.value,
                    "system_balance": system_bal.value,
                    "discrepancy_notes": notes.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/bank-reconciliation"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Reconciliation created', type='positive')
                        recon_dialog.close()
                        load_reconciliations()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=recon_dialog.close).props('flat')
                ui.button('Save', on_click=save_reconciliation).props(
                    'elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Create Reconciliation',
                      on_click=recon_dialog.open).props('icon=add')

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
                    url = f'{auth_state.api_base_url}/accounting/bank-reconciliation'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_reconciliations, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        # Record Invoice Dialog
        with ui.dialog() as invoice_dialog, ui.card().classes('w-96'):
            ui.label('Record Corporate Invoice').classes(
                'text-xl font-bold mb-4')
            cust_id = ui.input('Customer ID').classes('w-full')
            cust_name = ui.input('Customer Name').classes('w-full')
            due_date = ui.input('Due Date').props(
                'type=date').classes('w-full')
            liters = ui.number('Total Liters').classes('w-full')
            amount = ui.number('Subtotal (RWF)').classes('w-full')
            vat = ui.number('VAT Amount (RWF)', value=0).classes('w-full')

            async def save_invoice():
                token = app.storage.user.get('token')
                payload = {
                    "customer_id": cust_id.value,
                    "customer_name": cust_name.value,
                    "due_date": f"{due_date.value}T00:00:00Z",
                    "transaction_ids": [],  # Would be linked in production
                    "total_quantity_liters": liters.value,
                    "subtotal": amount.value,
                    "vat_amount": vat.value
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/accounts-receivable/invoice"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Invoice recorded', type='positive')
                        invoice_dialog.close()
                        load_receivables()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=invoice_dialog.close).props('flat')
                ui.button('Save', on_click=save_invoice).props(
                    'elevated color=green')

        # Record Payment Dialog
        with ui.dialog() as pay_dialog, ui.card().classes('w-96'):
            ui.label('Record Customer Payment').classes(
                'text-xl font-bold mb-4')
            ar_id_input = ui.input('AR Record ID').classes('w-full')
            pay_amount = ui.number('Payment Amount (RWF)').classes('w-full')
            pay_method = ui.select(
                ['cash', 'bank_transfer', 'cheque'], label='Method').classes('w-full')
            pay_ref = ui.input('Reference (Optional)').classes('w-full')

            async def save_payment():
                if not ar_id_input.value:
                    ui.notify('Please enter an AR Record ID', type='warning')
                    return
                token = app.storage.user.get('token')
                payload = {
                    "amount": pay_amount.value or 0,
                    "payment_method": pay_method.value,
                    "payment_reference": pay_ref.value
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/accounts-receivable/{ar_id_input.value}/payment"
                    resp = await client.post(url, json=payload, params=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code == 200:
                        ui.notify('Payment recorded successfully',
                                  type='positive')
                        pay_dialog.close()
                        load_receivables()
                    elif resp.status_code == 404:
                        ui.notify(
                            f'Error: AR Record "{ar_id_input.value}" not found. Please check the ID.', type='negative')
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=pay_dialog.close).props('flat')
                ui.button('Save', on_click=save_payment).props(
                    'elevated color=blue')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Record Invoice', on_click=invoice_dialog.open).props(
                'icon=description')
            ui.button('Record Payment', on_click=pay_dialog.open).props(
                'icon=payments')

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
                    url = f'{auth_state.api_base_url}/accounting/accounts-receivable'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_receivables, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        # Process Supplier Payment Dialog
        with ui.dialog() as supply_pay_dialog, ui.card().classes('w-96'):
            ui.label('Process Supplier Payment').classes(
                'text-xl font-bold mb-4')
            ap_id_input = ui.input('AP Record ID').classes('w-full')
            sup_amount = ui.number('Payment Amount (RWF)').classes('w-full')
            sup_method = ui.select(
                ['bank_transfer', 'cheque', 'cash'], label='Method').classes('w-full')
            sup_ref = ui.input('Reference (Optional)').classes('w-full')

            async def save_supplier_payment():
                if not ap_id_input.value:
                    ui.notify('Please enter an AP Record ID', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "amount": sup_amount.value,
                    "payment_method": sup_method.value,
                    "payment_reference": sup_ref.value
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/accounts-payable/{ap_id_input.value}/payment"
                    resp = await client.post(url, json=payload, params=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code == 200:
                        ui.notify('Supplier payment recorded', type='positive')
                        supply_pay_dialog.close()
                        load_payables()
                    elif resp.status_code == 404:
                        ui.notify(
                            f'Error: AP Record "{ap_id_input.value}" not found.', type='negative')
                    else:
                        ui.notify(
                            f"Error: {resp.status_code} - {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=supply_pay_dialog.close).props(
                    'flat')
                ui.button('Process', on_click=save_supplier_payment).props(
                    'elevated color=blue')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Process Payment', on_click=supply_pay_dialog.open).props(
                'icon=send')

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
                    url = f'{auth_state.api_base_url}/accounting/accounts-payable'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_payables, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        # Create Tax Record Dialog
        with ui.dialog() as tax_dialog, ui.card().classes('w-96'):
            ui.label('New Tax Record').classes('text-xl font-bold mb-4')
            # Use a dictionary to map display names to backend enum values
            tax_options = {
                'vat': 'VAT',
                'income_tax': 'Income Tax',
                'excise_tax': 'Excise Tax',
                'withholding_tax': 'Withholding Tax'
            }
            tax_type = ui.select(
                tax_options, label='Tax Type').classes('w-full')
            p_start = ui.input('Period Start').props(
                'type=date').classes('w-full')
            p_end = ui.input('Period End').props('type=date').classes('w-full')
            taxable = ui.number('Taxable Amount (RWF)').classes('w-full')
            rate = ui.number('Tax Rate (%)', value=18).classes('w-full')
            decl = ui.input('Declaration Number').classes('w-full')

            async def save_tax():
                if not tax_type.value:
                    ui.notify('Please select tax type', type='warning')
                    return
                token = app.storage.user.get('token')
                payload = {
                    "tax_type": tax_type.value,
                    "period_start": f"{p_start.value}T00:00:00Z",
                    "period_end": f"{p_end.value}T00:00:00Z",
                    "taxable_amount": taxable.value or 0,
                    "tax_rate": rate.value or 0,
                    "declaration_number": decl.value
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/tax-records"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Tax record created', type='positive')
                        tax_dialog.close()
                        load_tax()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=tax_dialog.close).props('flat')
                ui.button('Save', on_click=save_tax).props(
                    'elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Create Tax Record', on_click=tax_dialog.open).props(
                'icon=receipt_long')

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
                    url = f'{auth_state.api_base_url}/accounting/tax-records'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_tax, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        # Record Cost Dialog
        with ui.dialog() as cost_dialog, ui.card().classes('w-96'):
            ui.label('Record Fuel Cost').classes('text-xl font-bold mb-4')
            f_type = ui.select(['Petrol', 'Diesel', 'Kerosene'],
                               label='Fuel Type').classes('w-full')
            s_name = ui.input('Supplier Name').classes('w-full')
            q_liters = ui.number('Quantity (Liters)').classes('w-full')
            p_price = ui.number('Purchase Price / Liter').classes('w-full')
            s_price = ui.number(
                'Current Selling Price / Liter').classes('w-full')
            t_start = ui.input('Period Start').props(
                'type=date').classes('w-full')
            t_end = ui.input('Period End').props('type=date').classes('w-full')

            async def save_cost():
                token = app.storage.user.get('token')
                payload = {
                    "fuel_type": f_type.value,
                    "supplier_id": "SUP-001",  # Placeholder
                    "supplier_name": s_name.value,
                    "delivery_id": "DEL-001",  # Placeholder
                    "quantity_liters": q_liters.value,
                    "purchase_price_per_liter": p_price.value,
                    "selling_price_per_liter": s_price.value,
                    "period_start": f"{t_start.value}T00:00:00Z",
                    "period_end": f"{t_end.value}T00:00:00Z"
                }
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/fuel-cost-tracking"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Cost record saved', type='positive')
                        cost_dialog.close()
                        load_costs()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=cost_dialog.close).props('flat')
                ui.button('Save', on_click=save_cost).props(
                    'elevated color=blue')

        with ui.card().classes('w-full mb-4'):
            ui.button('Record Cost', on_click=cost_dialog.open).props(
                'icon=attach_money')

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
                    url = f'{auth_state.api_base_url}/accounting/fuel-cost-tracking'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_costs, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        async def run_commissions():
            token = app.storage.user.get('token')
            ui.notify('Calculating commissions...', type='info')
            # Mock data for demonstration as per backend logic
            payload = {
                "user_id": "STF-001",
                "user_name": "John Staff",
                "period_start": "2024-01-01T00:00:00Z",
                "period_end": "2024-01-31T23:59:59Z",
                "total_sales_amount": 5000000,
                "total_transactions": 150,
                "commission_rate": 2.5
            }
            async with httpx.AsyncClient() as client:
                url = f"{auth_state.api_base_url}/accounting/commissions/calculate"
                resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                if resp.status_code == 200:
                    ui.notify('Commissions calculated successfully',
                              type='positive')
                    load_commissions()
                else:
                    ui.notify(
                        f"Calculation failed: {resp.text}", type='negative')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Period').props('placeholder="Select period"')
            ui.button('Calculate Commissions',
                      on_click=run_commissions).props('icon=analytics')

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
                    url = f'{auth_state.api_base_url}/accounting/commissions/pending'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_commissions, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
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

        # --- Closing Form Dialog ---
        with ui.dialog() as closing_dialog, ui.card().classes('w-[600px]'):
            ui.label('Start Daily Closing Process').classes(
                'text-xl font-bold mb-4')

            with ui.grid(columns=2).classes('w-full gap-3'):
                station_id_f = ui.input(
                    'Station ID', value='STATION-MAIN').classes('w-full')
                closing_date_f = ui.input('Closing Date').props(
                    'type=date').classes('w-full')
                closing_date_f.value = datetime.now().strftime('%Y-%m-%d')

                ui.label(
                    '--- Cash ---').classes('col-span-2 text-sm font-bold text-gray-500 mt-2')
                opening_cash_f = ui.number(
                    'Opening Cash Balance (RWF)', value=0).classes('w-full')
                cash_sales_f = ui.number(
                    'Cash Sales (RWF)', value=0).classes('w-full')
                cash_refunds_f = ui.number(
                    'Cash Refunds (RWF)', value=0).classes('w-full')
                cash_paid_out_f = ui.number(
                    'Cash Paid Out (RWF)', value=0).classes('w-full')
                actual_cash_f = ui.number(
                    'Actual Cash Balance (RWF)', value=0).classes('w-full')

                ui.label('--- Card / Mobile Money ---').classes(
                    'col-span-2 text-sm font-bold text-gray-500 mt-2')
                card_sales_f = ui.number(
                    'Card Sales (RWF)', value=0).classes('w-full')
                card_count_f = ui.number(
                    'Card Transactions #', value=0).classes('w-full')
                momo_sales_f = ui.number(
                    'Mobile Money Sales (RWF)', value=0).classes('w-full')
                momo_count_f = ui.number(
                    'Mobile Money Transactions #', value=0).classes('w-full')

                ui.label(
                    '--- Credit Sales ---').classes('col-span-2 text-sm font-bold text-gray-500 mt-2')
                credit_sales_f = ui.number(
                    'Credit Sales (RWF)', value=0).classes('w-full')
                credit_coll_f = ui.number(
                    'Credit Collections (RWF)', value=0).classes('w-full')

                ui.label(
                    '--- Bank Deposit ---').classes('col-span-2 text-sm font-bold text-gray-500 mt-2')
                bank_dep_f = ui.number(
                    'Bank Deposit Amount (RWF)', value=0).classes('w-full')
                dep_ref_f = ui.input('Deposit Reference').classes('w-full')

                ui.label(
                    '--- Summary ---').classes('col-span-2 text-sm font-bold text-gray-500 mt-2')
                total_tx_f = ui.number(
                    'Total Transactions #', value=0).classes('w-full')
                shift_mgr_f = ui.input('Shift Manager ID').classes('w-full')
                notes_f = ui.textarea('Notes (Optional)').classes(
                    'col-span-2 w-full')

            async def run_closing():
                if not all([station_id_f.value, closing_date_f.value, shift_mgr_f.value]):
                    ui.notify(
                        'Station ID, Closing Date and Shift Manager ID are required', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "station_id": station_id_f.value,
                    "closing_date": f"{closing_date_f.value}T23:59:59Z",
                    "opening_cash_balance": opening_cash_f.value or 0,
                    "cash_sales": cash_sales_f.value or 0,
                    "cash_refunds": cash_refunds_f.value or 0,
                    "cash_paid_out": cash_paid_out_f.value or 0,
                    "actual_cash_balance": actual_cash_f.value or 0,
                    "card_sales": card_sales_f.value or 0,
                    "card_count": int(card_count_f.value or 0),
                    "mobile_money_sales": momo_sales_f.value or 0,
                    "mobile_money_count": int(momo_count_f.value or 0),
                    "mobile_money_breakdown": {},
                    "credit_sales": credit_sales_f.value or 0,
                    "credit_collections": credit_coll_f.value or 0,
                    "bank_deposit_amount": bank_dep_f.value or 0,
                    "deposit_reference": dep_ref_f.value or None,
                    "total_transactions": int(total_tx_f.value or 0),
                    "shift_manager_id": shift_mgr_f.value,
                    "notes": notes_f.value or None
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/daily-closing"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        data = resp.json()
                        ui.notify(
                            f"Day closed ✔ | Total Sales: RWF {data.get('total_sales', 0):,.0f} | Cash Variance: RWF {data.get('cash_variance', 0):,.0f}",
                            type='positive'
                        )
                        closing_dialog.close()
                        load_closings()
                    else:
                        ui.notify(
                            f"Closing failed: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=closing_dialog.close).props('flat')
                ui.button('Submit Closing', on_click=run_closing).props(
                    'elevated color=green icon=lock')

        # --- Action bar ---
        with ui.card().classes('w-full mb-4'):
            ui.button('Start Closing Process', on_click=closing_dialog.open).props(
                'icon=lock color=primary')

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
                        url = f'{auth_state.api_base_url}/accounting/daily-closing'
                        r = httpx.get(
                            url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                        if r.status_code == 200:
                            res['rows'] = r.json()
                        elif r.status_code == 503:
                            res['err'] = "Database initializing..."
                        else:
                            res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                    except Exception as e:
                        res['err'] = f"Connection error: {str(e)}"
                    finally:
                        res['done'] = True

                def apply():
                    if not res['done']:
                        return
                    p.cancel()
                    table.props(remove='loading')
                    if res['err']:
                        if "initializing" in res['err'].lower():
                            # Retry once after a short delay
                            ui.timer(2.0, load_closings, once=True)
                        else:
                            ui.notify(res['err'], type='negative')
                    else:
                        table.rows = res['rows']

                import threading
                threading.Thread(target=fetch, daemon=True).start()
                p = ui.timer(0.5, apply)

            async def verify_day(closing_id):
                token = app.storage.user.get('token')
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/accounting/daily-closing/{closing_id}/verify"
                    resp = await client.post(url, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code == 200:
                        ui.notify('Day verified and closed', type='positive')
                        load_closings()
                    else:
                        ui.notify(
                            f"Verification failed: {resp.text}", type='negative')

            table.add_slot('header', '''
                <q-tr :props="props">
                    <q-th v-for="col in props.cols" :key="col.name" :props="props">
                        {{ col.label }}
                    </q-th>
                    <q-th>Actions</q-th>
                </q-tr>
            ''')
            table.add_slot('body', '''
                <q-tr :props="props">
                    <q-td v-for="col in props.cols" :key="col.name" :props="props">
                        {{ col.value }}
                    </q-td>
                    <q-td>
                        <q-btn v-if="!props.row.verified_by_accountant" 
                               flat color="primary" icon="check_circle" label="Verify"
                               @click="$parent.$emit('verify', props.row.closing_id)" />
                        <q-badge v-else color="green">Verified</q-badge>
                    </q-td>
                </q-tr>
            ''')
            table.on('verify', lambda msg: verify_day(msg.args))

            load_closings()

    dashboard_layout(content)


def compliance_page():
    """RURA compliance reports page"""
    def content():
        ui.label('RURA Compliance Reports').classes('text-2xl font-bold mb-6')

        async def run_compliance():
            token = app.storage.user.get('token')
            ui.notify('Generating report...', type='info')
            payload = {
                "report_period": "2024-05",
                "petrol_sales_liters": 15000,
                "petrol_sales_amount": 25000000,
                "diesel_sales_liters": 12000,
                "diesel_sales_amount": 20000000,
                "petrol_avg_price": 1639,
                "diesel_avg_price": 1635,
                "opening_stock": {"petrol": 5000, "diesel": 4000},
                "closing_stock": {"petrol": 2000, "diesel": 1500},
                "purchases": {"petrol": 12000, "diesel": 10000},
                "total_vat_collected": 4500000,
                "total_excise_tax": 1200000
            }
            async with httpx.AsyncClient() as client:
                url = f"{auth_state.api_base_url}/accounting/rura-reports"
                resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                if resp.status_code in (200, 201):
                    ui.notify('RURA Compliance Report Generated',
                              type='positive')
                    load_reports()
                else:
                    ui.notify(f"Report failed: {resp.text}", type='negative')

        with ui.row().classes('w-full mb-4 gap-2'):
            ui.input('Report Period').props('placeholder="Select period"')
            ui.button('Generate Report', on_click=run_compliance).props(
                'icon=assessment')

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
                    url = f'{auth_state.api_base_url}/accounting/rura-reports'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    if r.status_code == 200:
                        res['rows'] = r.json()
                    elif r.status_code == 503:
                        res['err'] = "Database initializing..."
                    else:
                        res['err'] = f"Error {r.status_code}: {r.text[:50]}"
                except Exception as e:
                    res['err'] = f"Connection error: {str(e)}"
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                table.props(remove='loading')
                if res['err']:
                    if "initializing" in res['err'].lower():
                        ui.timer(2.0, load_reports, once=True)
                    else:
                        ui.notify(res['err'], type='negative')
                else:
                    table.rows = res['rows']

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_reports()

    dashboard_layout(content)
