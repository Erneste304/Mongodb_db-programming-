from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx  # Import httpx for API calls
import datetime  # Keep datetime for potential date calculations
import random  # Keep random for potential mock data or unique IDs


def receptionist_page():
    """Receptionist/Sales dashboard in NiceGUI"""
    def content():
        ui.label('Sales Command Center').classes(
            'text-3xl font-bold mb-6 text-slate-800')

        # Stats Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label("Today's Revenue").classes(
                    'text-sm text-green-600 font-bold uppercase tracking-wider')
                revenue_label = ui.label('0 RWF').classes(
                    'text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label("Transactions").classes(
                    'text-sm text-blue-600 font-bold uppercase tracking-wider')
                tx_count_label = ui.label('0').classes(
                    'text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-purple-50 border-l-4 border-purple-500'):
                ui.label("Loyalty Points Issued").classes(
                    'text-sm text-purple-600 font-bold uppercase tracking-wider')
                loyalty_label = ui.label('0').classes(
                    'text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            sale_tab = ui.tab('Process Sale')
            tx_tab = ui.tab('Recent Transactions')
            cust_tab = ui.tab('Customers')

        with ui.tab_panels(tabs, value=sale_tab).classes('w-full bg-transparent'):
            # Process Sale Panel
            with ui.tab_panel(sale_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('New Fuel Transaction').classes(
                        'text-2xl font-bold mb-6 text-center')

                    fuel_type = ui.select(['petrol', 'diesel', 'kerosene'], label='Fuel Type').classes(
                        'w-full mb-4').props('outlined')
                    quantity = ui.number('Quantity (Liters)', value=0, format='%.2f').classes(
                        'w-full mb-4').props('outlined prefix=L')
                    payment_method = ui.select(['cash', 'mobile_money', 'card', 'credit'], label='Payment Method').classes(
                        'w-full mb-4').props('outlined')

                    phone_container = ui.column().classes('w-full mb-4')

                    def update_phone_visibility(val):
                        phone_container.clear()
                        if val == 'mobile_money':
                            with phone_container:
                                ui.input('Customer Phone', placeholder='078...').classes(
                                    'w-full').props('outlined prefix=phone')
                    payment_method.on_value_change(update_phone_visibility)

                    ui.separator().classes('my-6')

                    async def process_sale():
                        if not fuel_type.value or not quantity.value:
                            ui.notify(
                                'Please enter fuel type and quantity', type='warning')
                            return

                        token = app.storage.user.get('token')
                        payload = {
                            "transaction_id": f"TXN-{random.randint(1000, 9999)}",
                            "fuel_type": fuel_type.value,
                            "quantity_liters": quantity.value,
                            "payment_method": payment_method.value,
                            "price_per_liter": 1650 if fuel_type.value == 'petrol' else 1550
                        }

                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/sales/transactions"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify(
                                    'Sale Completed & EBM Signed', type='positive')
                                load_sales_data()
                            else:
                                try:
                                    err_data = resp.json()
                                    msg = err_data.get('message') or err_data.get(
                                        'detail') or resp.text
                                    ui.notify(
                                        f'Transaction Error: {msg}', type='negative', duration=10)
                                except:
                                    ui.notify(
                                        f'Server Error: {resp.status_code}', type='negative')

                    with ui.row().classes('w-full justify-between items-center'):
                        with ui.column():
                            ui.label('Estimated Total').classes(
                                'text-sm text-slate-500')
                            total_label = ui.label('0 RWF').classes(
                                'text-2xl font-bold text-blue-600')

                        def calculate_total():
                            # Mock price for now, would be from API
                            price = 1650 if fuel_type.value == 'petrol' else 1550
                            total_label.set_text(
                                f"{quantity.value * price:,.0f} RWF")

                        fuel_type.on_value_change(calculate_total)
                        quantity.on_value_change(calculate_total)

                        ui.button('COMPLETE SALE', on_click=process_sale).props(
                            'elevated color=green size=lg').classes('px-8 py-3 rounded-xl font-bold')

            # Transactions Panel
            with ui.tab_panel(tx_tab):
                tx_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'TX ID',
                            'field': 'transaction_id'},
                        {'name': 'fuel', 'label': 'Fuel', 'field': 'fuel_type'},
                        {'name': 'qty', 'label': 'Quantity',
                            'field': 'quantity_liters'},
                        {'name': 'total',
                            'label': 'Total (RWF)', 'field': 'total_amount'},
                        {'name': 'method', 'label': 'Method',
                            'field': 'payment_method'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='transaction_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Customers Panel
            with ui.tab_panel(cust_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Loyalty Customers').classes('text-xl font-bold')
                    ui.button('Register Customer', on_click=lambda: ui.notify(
                        'Register dialog', type='info')).props('elevated icon=person_add')

                cust_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name'},
                        {'name': 'phone', 'label': 'Phone', 'field': 'phone'},
                        {'name': 'type', 'label': 'Type',
                            'field': 'customer_type'},
                        {'name': 'points', 'label': 'Points',
                            'field': 'loyalty_points'},
                        {'name': 'balance', 'label': 'Balance',
                            'field': 'current_balance'},
                    ],
                    rows=[],
                    row_key='customer_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_sales_data():
            token = app.storage.user.get('token')
            res = {'done': False, 'txs': [], 'custs': [], 'err': ''}
            tx_table.props(add='loading')
            cust_table.props(add='loading')

            def fetch():
                try:
                    # Use httpx for consistency
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url  # Already correctly formatted

                    # Transactions
                    r1 = httpx.get(f'{base}/sales/transactions',
                                   headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        res['txs'] = r1.json()

                    # Customers (assuming this endpoint exists)
                    r2 = httpx.get(f'{base}/sales/customers',
                                   headers=headers, timeout=10.0)
                    if r2.status_code == 200:
                        res['custs'] = r2.json()

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                tx_table.props(remove='loading')
                cust_table.props(remove='loading')

                if not res['err']:
                    tx_table.rows = res['txs']
                    cust_table.rows = res['custs']

                    # Update stats
                    total_rev = sum(tx.get('total_amount', 0)
                                    for tx in res['txs'])
                    revenue_label.set_text(f"{total_rev:,.0f} RWF")
                    tx_count_label.set_text(str(len(res['txs'])))

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_sales_data()

    dashboard_layout(content)
