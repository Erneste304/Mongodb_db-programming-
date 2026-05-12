from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx  # Import httpx for API calls
import datetime  # Keep datetime for potential date calculations
import random  # Keep random for potential mock data or unique IDs


def receptionist_page():
    """Receptionist/Sales dashboard in NiceGUI"""
    def content():
        # Local state for receipt details to replace app.storage.temp
        receipt_data = {
            'receipt_tx_id': None,
            'receipt_customer_name': None,
            'receipt_customer_tin': None,
            'receipt_fuel_type': None,
            'receipt_quantity': 0,
            'receipt_price_per_liter': 0,
            'receipt_total_amount': 0,
            'receipt_payment_method': None,
            'receipt_date': None,
        }

        # Improved Receipt Dialog
        with ui.dialog() as receipt_dialog, ui.card().classes('w-96'):
            with ui.column().classes('w-full items-center p-4'):
                ui.icon('receipt', size='4rem', color='blue')
                ui.label('Official Receipt').classes('text-2xl font-bold mb-2')
                ui.label('PetroSync Station').classes('text-slate-500 mb-4')
                ui.separator()

                with ui.grid(columns=2).classes('w-full gap-2 mt-4 text-sm'):
                    ui.label('Transaction ID:')
                    ui.label().bind_text_from(receipt_data, 'receipt_tx_id')
                    ui.label('Customer:')
                    ui.label().bind_text_from(receipt_data, 'receipt_customer_name')
                    ui.label('Fuel Type:')
                    ui.label().bind_text_from(receipt_data, 'receipt_fuel_type')
                    ui.label('Quantity:')
                    ui.label().bind_text_from(receipt_data,
                                              'receipt_quantity', lambda x: f'{x or 0:.2f} L')
                    ui.label('Price/L:')
                    ui.label().bind_text_from(receipt_data, 'receipt_price_per_liter',
                                              lambda x: f'{x or 0:,.0f} RWF')
                    ui.label('Total:').classes('font-bold text-lg')
                    ui.label().bind_text_from(receipt_data, 'receipt_total_amount',
                                              lambda x: f'{x or 0:,.0f} RWF').classes('font-bold text-lg text-blue-600')
                    ui.label('Method:')
                    ui.label().bind_text_from(receipt_data, 'receipt_payment_method')
                    ui.label('Date:')
                    ui.label().bind_text_from(receipt_data, 'receipt_date')

                ui.separator().classes('my-4')
                ui.label('EBM Signed & Verified').classes(
                    'text-xs text-green-600 font-bold uppercase tracking-widest')
                ui.label('Thank you for your business!').classes(
                    'text-center text-sm italic mt-2 text-slate-500')

            with ui.row().classes('w-full mt-4 gap-2'):
                ui.button('Print Receipt', icon='print',
                          on_click=lambda: ui.run_javascript('window.print()')).classes('flex-1')
                ui.button('Close', on_click=receipt_dialog.close).props(
                    'flat').classes('flex-1')

        # Register Customer Dialog
        with ui.dialog() as reg_dialog, ui.card().classes('w-96'):
            ui.label('Register New Customer').classes('text-xl font-bold mb-4')
            new_cust_id = ui.input(
                'Customer ID (Phone or Plate)').classes('w-full')
            new_cust_name = ui.input('Full Name').classes('w-full')
            new_cust_phone = ui.input('Phone Number').classes('w-full')
            new_cust_email = ui.input('Email').classes('w-full')
            new_cust_tin = ui.input('TIN Number (Optional)').classes('w-full')
            new_cust_type = ui.select(
                ['cash', 'credit'], value='cash', label='Customer Type').classes('w-full')

            async def save_customer():
                if not new_cust_id.value or not new_cust_name.value:
                    ui.notify('ID and Name are required', type='warning')
                    return

                token = app.storage.user.get('token')
                payload = {
                    "customer_id": new_cust_id.value,
                    "name": new_cust_name.value,
                    "phone": new_cust_phone.value,
                    "email": new_cust_email.value,
                    "tin_number": new_cust_tin.value,
                    "customer_type": new_cust_type.value
                }

                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/sales/customers"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code in (200, 201):
                        ui.notify('Customer Registered Successfully',
                                  type='positive')
                        reg_dialog.close()
                        load_sales_data()
                    else:
                        ui.notify(f"Error: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=reg_dialog.close).props('flat')
                ui.button('Register', on_click=save_customer).props(
                    'elevated color=green')

        # Top-up Balance Dialog
        selected_cust_id = {'value': None}
        with ui.dialog() as topup_dialog, ui.card().classes('w-96'):
            ui.label('Top-up Customer Balance').classes('text-xl font-bold mb-4')
            topup_name_label = ui.label().classes('mb-4 text-blue-600 font-semibold')
            topup_amount = ui.number('Amount (RWF)', value=0).classes(
                'w-full mb-4').props('outlined')

            async def confirm_topup():
                if topup_amount.value <= 0:
                    ui.notify('Enter a valid amount', type='warning')
                    return
                token = app.storage.user.get('token')
                payload = {"amount": topup_amount.value}
                async with httpx.AsyncClient() as client:
                    url = f"{auth_state.api_base_url}/sales/customers/{selected_cust_id['value']}/topup"
                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code == 200:
                        ui.notify('Balance Updated Successfully',
                                  type='positive')
                        topup_dialog.close()
                        load_sales_data()
                    else:
                        ui.notify(f"Failed: {resp.text}", type='negative')

            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=topup_dialog.close).props('flat')
                ui.button('Add Funds', on_click=confirm_topup).props(
                    'elevated color=blue')

        def open_topup(row):
            selected_cust_id['value'] = row['customer_id']
            topup_name_label.set_text(
                f"Customer: {row['name']} ({row['customer_id']})")
            topup_amount.value = 0
            topup_dialog.open()

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

        # State and logic references
        current_prices = {'petrol': 1650.0,
                          'diesel': 1550.0, 'kerosene': 1200.0}
        logic = {'calculate_total': lambda: None}

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            sale_tab = ui.tab('Process Sale')
            tx_tab = ui.tab('Recent Transactions')
            cust_tab = ui.tab('Customers')
            shop_tab = ui.tab('Shop Sales')
            pump_tab = ui.tab('Pump Management')
            shift_tab = ui.tab('Shift Management')
            complaint_tab = ui.tab('Complaints')
            report_tab = ui.tab('Fuel Sales Report')

        with ui.tab_panels(tabs, value=sale_tab).classes('w-full bg-transparent'):
            # Process Sale Panel
            with ui.tab_panel(sale_tab):
                with ui.row().classes('w-full gap-6 items-start'):
                    # Transaction Form
                    with ui.card().classes('flex-1 p-8 shadow-xl rounded-2xl border border-slate-100'):
                        ui.label('New Fuel Transaction').classes(
                            'text-2xl font-bold mb-6 text-center')

                        fuel_type = ui.select(['petrol', 'diesel', 'kerosene'], label='Fuel Type').classes(
                            'w-full mb-4').props('outlined')
                    customer_id_input = ui.input('Customer ID (Optional)', placeholder='Scan or enter ID').classes(
                        'w-full mb-4').props('outlined prefix=person')
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

                        # IMPORTANT: transaction_id should ideally be generated by the backend.
                        # Removing client-side generation and expecting it in the response.
                        payload = {
                            "transaction_id": f"TXN-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "customer_id": customer_id_input.value if customer_id_input.value else None,
                            "fuel_type": fuel_type.value,
                            "quantity_liters": quantity.value,
                            "payment_method": payment_method.value,
                            "price_per_liter": current_prices.get(fuel_type.value, 0)
                        }

                        async def load_and_display_receipt(transaction_id: str):
                            token = app.storage.user.get('token')
                            async with httpx.AsyncClient() as client:
                                url = f"{auth_state.api_base_url}/sales/transactions/{transaction_id}"
                                resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                                if resp.status_code == 200:
                                    tx_data = resp.json()
                                    receipt_data['receipt_tx_id'] = tx_data.get(
                                        'transaction_id')
                                    receipt_data['receipt_customer_name'] = tx_data.get(
                                        'customer_name')
                                    receipt_data['receipt_customer_tin'] = tx_data.get(
                                        'customer_tin')
                                    receipt_data['receipt_fuel_type'] = tx_data.get(
                                        'fuel_type')
                                    receipt_data['receipt_quantity'] = tx_data.get(
                                        'quantity_liters')
                                    receipt_data['receipt_price_per_liter'] = tx_data.get(
                                        'price_per_liter')
                                    receipt_data['receipt_total_amount'] = tx_data.get(
                                        'total_amount')
                                    receipt_data['receipt_payment_method'] = tx_data.get(
                                        'payment_method')
                                    receipt_data['receipt_date'] = datetime.datetime.fromisoformat(
                                        tx_data['created_at']).strftime('%Y-%m-%d %H:%M:%S') if tx_data.get('created_at') else 'N/A'
                                    receipt_dialog.open()
                                else:
                                    ui.notify(
                                        f"Failed to load receipt: {resp.text}", type='negative')

                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/sales/transactions"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                sale_data = resp.json()
                                transaction_id = sale_data.get(
                                    'transaction_id')
                                ui.notify(
                                    'Sale Completed & EBM Signed', type='positive')
                                load_sales_data()
                                if transaction_id:
                                    await load_and_display_receipt(transaction_id)
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
                        # Use real prices fetched from the pricing service
                        price = current_prices.get(fuel_type.value, 0)
                        val = quantity.value or 0
                        total_label.set_text(f"{val * price:,.0f} RWF")

                    logic['calculate_total'] = calculate_total

                    fuel_type.on_value_change(calculate_total)
                    quantity.on_value_change(calculate_total)

                    ui.button('COMPLETE SALE', on_click=process_sale).props(
                        'elevated color=green size=lg').classes('px-8 py-3 rounded-xl font-bold')

                    # Quick Recent Log (as requested)
                    with ui.card().classes('w-80 p-6 shadow-md rounded-2xl border border-slate-100 bg-slate-50'):
                        ui.label('Recent Activity').classes(
                            'text-xl font-bold mb-4 text-slate-700')
                        recent_preview = ui.column().classes('w-full gap-2')

                        def update_preview():
                            recent_preview.clear()
                            # Display short summary of the last 5 transactions from the table
                            for tx in tx_table.rows[:5]:
                                with recent_preview:
                                    ui.label(
                                        f"{tx.get('transaction_id', '')[-4:]}: {tx.get('total_amount', 0):,.0f} RWF").classes('text-sm font-mono')
                        ui.timer(2.0, update_preview)

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
                    ui.button('Register Customer', on_click=reg_dialog.open).props(
                        'elevated icon=person_add')

                cust_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'name'},
                        {'name': 'phone', 'label': 'Phone', 'field': 'phone'},
                        {'name': 'type', 'label': 'Type',
                            'field': 'customer_type'},
                        {'name': 'points', 'label': 'Points',
                            'field': 'loyalty_points'},
                        {'name': 'balance', 'field': 'current_balance',
                            'label': 'Balance (RWF)'},
                        {'name': 'actions', 'label': 'Actions', 'field': 'actions'}
                    ],
                    rows=[],
                    row_key='customer_id'
                ).classes('w-full shadow-md rounded-xl').props('loading px-4')

                with cust_table.add_slot('body-cell-actions') as slot:
                    ui.button(icon='add_card', on_click=lambda: open_topup(slot.args['row'])) \
                        .props('flat dense color=primary').classes('ml-2')

            # Shop Sales Panel
            with ui.tab_panel(shop_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('Shop Sale').classes(
                        'text-2xl font-bold mb-6 text-center')

                    shop_item = ui.select([], label='Select Item').classes(
                        'w-full mb-4').props('outlined')
                    shop_qty = ui.number('Quantity', value=1, format='%.0f').classes(
                        'w-full mb-4').props('outlined')
                    shop_payment = ui.select(['cash', 'mobile_money', 'card'], label='Payment Method').classes(
                        'w-full mb-4').props('outlined')

                    async def populate_shop_options():
                        token = app.storage.user.get('token')
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shop/items"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                items = resp.json()
                                options = [
                                    f"{i['item_name']} - {i['unit_price']:,.0f} RWF" for i in items]
                                shop_item.options = options
                                shop_item.update()

                    async def process_shop_sale():
                        if not shop_item.value or ' - ' not in shop_item.value:
                            ui.notify('Please select an item', type='warning')
                            return

                        token = app.storage.user.get('token')
                        item_name = shop_item.value.split(' - ')[0]
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shop/items"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                items = resp.json()
                                selected_item = next(
                                    (i for i in items if i['item_name'] == item_name), None)
                                if selected_item:
                                    payload = {
                                        "sale_id": f"SHOP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                                        "items": [{
                                            "item_id": selected_item['item_id'],
                                            "quantity": shop_qty.value,
                                            "unit_price": selected_item['unit_price'],
                                            "subtotal": selected_item['unit_price'] * shop_qty.value
                                        }],
                                        "payment_method": shop_payment.value
                                    }
                                    url = f"{auth_state.api_base_url}/shop/sales"
                                    resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                                    if resp.status_code in (200, 201):
                                        ui.notify(
                                            'Shop sale completed', type='positive')
                                        load_sales_data()
                                    else:
                                        ui.notify(
                                            f"Error: {resp.text}", type='negative')

                    ui.button('Complete Shop Sale', on_click=process_shop_sale).props(
                        'elevated color=green').classes('w-full')

                    ui.separator().classes('my-6')

                    ui.label('Shop Inventory').classes(
                        'text-lg font-bold mb-2')
                    shop_inventory_table = ui.table(
                        columns=[
                            {'name': 'name', 'label': 'Item', 'field': 'item_name'},
                            {'name': 'price',
                                'label': 'Price (RWF)', 'field': 'unit_price'},
                            {'name': 'stock', 'label': 'Stock',
                                'field': 'current_stock'},
                        ],
                        rows=[],
                        row_key='item_id'
                    ).classes('w-full shadow-md rounded-xl')

                    async def load_shop_inventory():
                        token = app.storage.user.get('token')
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shop/items"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                shop_inventory_table.rows = resp.json()

            # Pump Management Panel
            with ui.tab_panel(pump_tab):
                ui.label('Pump Status').classes('text-xl font-bold mb-4')

                pump_table = ui.table(
                    columns=[
                        {'name': 'number', 'label': 'Pump #',
                            'field': 'pump_number'},
                        {'name': 'fuel', 'label': 'Fuel Type', 'field': 'fuel_type'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                        {'name': 'customer', 'label': 'Current Customer',
                            'field': 'current_customer'},
                    ],
                    rows=[],
                    row_key='pump_id'
                ).classes('w-full shadow-md rounded-xl')

                async def load_pumps():
                    token = app.storage.user.get('token')
                    async with httpx.AsyncClient() as client:
                        url = f"{auth_state.api_base_url}/pump/pumps"
                        resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                        if resp.status_code == 200:
                            pumps = resp.json()
                            pump_table.rows = pumps

            # Shift Management Panel
            with ui.tab_panel(shift_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('Shift Management').classes(
                        'text-2xl font-bold mb-6 text-center')

                    shift_opening_cash = ui.number('Opening Cash (RWF)', value=0, format='%.0f').classes(
                        'w-full mb-4').props('outlined')

                    async def start_shift():
                        token = app.storage.user.get('token')
                        user_data = app.storage.user.get('user', {})
                        payload = {
                            "shift_id": f"SHIFT-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "staff_id": user_data.get('id', 'staff'),
                            "staff_name": user_data.get('username', 'Staff'),
                            "opening_cash": float(shift_opening_cash.value or 0)
                        }
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shift/shifts"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify(
                                    'Shift started successfully', type='positive')
                                shift_opening_cash.value = 0
                                await load_shifts()
                            else:
                                ui.notify(
                                    f"Error: {resp.text}", type='negative')

                    ui.button('Start Shift', on_click=start_shift).props(
                        'elevated color=green').classes('w-full mb-4')

                    ui.separator().classes('my-6')

                    shift_closing_cash = ui.number('Closing Cash (RWF)', value=0, format='%.0f').classes(
                        'w-full mb-4').props('outlined')
                    shift_notes = ui.textarea('Notes').classes(
                        'w-full mb-4').props('outlined')

                    async def close_shift():
                        token = app.storage.user.get('token')
                        # Get current shift
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shift/shifts"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                shifts = resp.json()
                                open_shifts = [
                                    s for s in shifts if s.get('status') == 'open']
                                if open_shifts:
                                    shift_id = open_shifts[0].get('shift_id')
                                    payload = {
                                        "closing_cash": float(shift_closing_cash.value or 0),
                                        "notes": shift_notes.value or ""
                                    }
                                    url = f"{auth_state.api_base_url}/shift/shifts/{shift_id}/close"
                                    resp = await client.put(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                                    if resp.status_code == 200:
                                        ui.notify(
                                            'Shift closed successfully', type='positive')
                                        shift_closing_cash.value = 0
                                        shift_notes.value = ''
                                        await load_shifts()
                                    else:
                                        ui.notify(
                                            f"Error: {resp.text}", type='negative')
                                else:
                                    ui.notify('No open shift found',
                                              type='warning')

                    ui.button('Close Shift', on_click=close_shift).props(
                        'elevated color=red').classes('w-full mb-4')

                    ui.separator().classes('my-6')

                    ui.label('Shift History').classes('text-lg font-bold mb-2')
                    shift_table = ui.table(
                        columns=[
                            {'name': 'id', 'label': 'Shift ID', 'field': 'shift_id'},
                            {'name': 'staff', 'label': 'Staff',
                                'field': 'staff_name'},
                            {'name': 'start', 'label': 'Start Time',
                                'field': 'start_time'},
                            {'name': 'status', 'label': 'Status', 'field': 'status'},
                            {'name': 'variance',
                                'label': 'Cash Variance (RWF)', 'field': 'cash_variance'},
                        ],
                        rows=[],
                        row_key='shift_id'
                    ).classes('w-full shadow-md rounded-xl')

                    async def load_shifts():
                        token = app.storage.user.get('token')
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/shift/shifts"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                shifts = resp.json()
                                shift_table.rows = shifts

            # Complaints Panel
            with ui.tab_panel(complaint_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('Customer Complaint').classes(
                        'text-2xl font-bold mb-6 text-center')

                    complaint_customer = ui.input('Customer Name').classes(
                        'w-full mb-4').props('outlined')
                    complaint_phone = ui.input('Customer Phone').classes(
                        'w-full mb-4').props('outlined')
                    complaint_type = ui.select(['fuel_quality', 'service', 'pricing', 'pump_issue',
                                               'other'], label='Complaint Type').classes('w-full mb-4').props('outlined')
                    complaint_severity = ui.select(['low', 'medium', 'high', 'critical'], label='Severity').classes(
                        'w-full mb-4').props('outlined')
                    complaint_desc = ui.textarea('Description').classes(
                        'w-full mb-4').props('outlined')
                    complaint_tx = ui.input('Related Transaction ID (Optional)').classes(
                        'w-full mb-4').props('outlined')

                    async def submit_complaint():
                        if not complaint_customer.value or not complaint_desc.value:
                            ui.notify(
                                'Customer name and description are required', type='warning')
                            return

                        token = app.storage.user.get('token')
                        payload = {
                            "complaint_id": f"COMP-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}",
                            "customer_name": complaint_customer.value,
                            "customer_phone": complaint_phone.value,
                            "complaint_type": complaint_type.value,
                            "severity": complaint_severity.value,
                            "description": complaint_desc.value,
                            "related_transaction_id": complaint_tx.value if complaint_tx.value else None,
                            "reported_by": app.storage.user.get('user', {}).get('id', 'staff')
                        }
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/complaints/complaints"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify(
                                    'Complaint submitted successfully', type='positive')
                                await load_complaints()
                            else:
                                ui.notify(
                                    f"Error: {resp.text}", type='negative')

                    ui.button('Submit Complaint', on_click=submit_complaint).props(
                        'elevated color=orange').classes('w-full mb-4')

                    ui.separator().classes('my-6')

                    ui.label('Complaint History').classes(
                        'text-lg font-bold mb-2')
                    complaint_table = ui.table(
                        columns=[
                            {'name': 'id', 'label': 'Complaint ID',
                                'field': 'complaint_id'},
                            {'name': 'customer', 'label': 'Customer',
                                'field': 'customer_name'},
                            {'name': 'type', 'label': 'Type',
                                'field': 'complaint_type'},
                            {'name': 'severity', 'label': 'Severity',
                                'field': 'severity'},
                            {'name': 'status', 'label': 'Status', 'field': 'status'},
                        ],
                        rows=[],
                        row_key='complaint_id'
                    ).classes('w-full shadow-md rounded-xl')

                    async def load_complaints():
                        token = app.storage.user.get('token')
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/complaints/complaints"
                            resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                complaint_table.rows = resp.json()

            # Fuel Sales Report Panel
            with ui.tab_panel(report_tab):
                ui.label('Daily Sales by Fuel Type').classes(
                    'text-xl font-bold mb-4')

                with ui.row().classes('w-full gap-4 mb-6'):
                    with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                        ui.label('Petrol Sales').classes(
                            'text-sm text-green-600 font-bold')
                        petrol_sales_label = ui.label('0 RWF').classes(
                            'text-2xl font-bold text-slate-800')

                    with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                        ui.label('Diesel Sales').classes(
                            'text-sm text-blue-600 font-bold')
                        diesel_sales_label = ui.label('0 RWF').classes(
                            'text-2xl font-bold text-slate-800')

                    with ui.card().classes('flex-1 p-6 bg-purple-50 border-l-4 border-purple-500'):
                        ui.label('Kerosene Sales').classes(
                            'text-sm text-purple-600 font-bold')
                        kerosene_sales_label = ui.label('0 RWF').classes(
                            'text-2xl font-bold text-slate-800')

                ui.separator().classes('my-6')

                async def update_fuel_sales_report():
                    petrol_sales_label.set_text(
                        f"{receipt_data.get('petrol_sales', 0):,.0f} RWF")
                    diesel_sales_label.set_text(
                        f"{receipt_data.get('diesel_sales', 0):,.0f} RWF")
                    kerosene_sales_label.set_text(
                        f"{receipt_data.get('kerosene_sales', 0):,.0f} RWF")

                # Update fuel sales when data loads
                ui.timer(5.0, update_fuel_sales_report)

        def load_sales_data():
            token = app.storage.user.get('token')
            if not token:
                ui.notify('Session expired. Please login again.',
                          type='warning')
                return

            res = {'done': False, 'txs': [], 'custs': [], 'err': ''}
            tx_table.props(add='loading')
            cust_table.props(add='loading')

            def fetch():
                try:
                    # Use httpx for consistency
                    headers = {
                        'Authorization': f'Bearer {token}',
                        'Accept': 'application/json'
                    }
                    base = auth_state.api_base_url  # Already correctly formatted

                    # Transactions
                    r1 = httpx.get(f'{base}/sales/transactions',
                                   headers=headers, timeout=10.0)
                    if r1.status_code != 200:
                        res['err'] = f"Transactions fetch failed: {r1.status_code}"
                        return
                    res['txs'] = r1.json()

                    # Customers (assuming this endpoint exists)
                    r2 = httpx.get(f'{base}/sales/customers',
                                   headers=headers, timeout=10.0)
                    if r2.status_code != 200:
                        res['err'] = f"Customers fetch failed: {r2.status_code}"
                        return
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

                if res['err']:
                    ui.notify(
                        f"Data Sync Error: {res['err']}", type='negative')
                    return

                tx_table.rows = res['txs']
                cust_table.rows = res['custs']

                # Update stats
                total_rev = sum(tx.get('total_amount', 0)
                                for tx in res['txs'])
                revenue_label.set_text(f"{total_rev:,.0f} RWF")
                tx_count_label.set_text(str(len(res['txs'])))

                # Update Loyalty Points Issued (Sum from customers)
                total_points = sum(c.get('loyalty_points', 0)
                                   for c in res['custs'])
                loyalty_label.set_text(f"{total_points:,}")

                # Update fuel type sales
                petrol_sales = sum(tx.get('total_amount', 0)
                                   for tx in res['txs'] if tx.get('fuel_type') == 'petrol')
                diesel_sales = sum(tx.get('total_amount', 0)
                                   for tx in res['txs'] if tx.get('fuel_type') == 'diesel')
                kerosene_sales = sum(tx.get('total_amount', 0)
                                     for tx in res['txs'] if tx.get('fuel_type') == 'kerosene')

                # Store fuel sales for report tab
                receipt_data['petrol_sales'] = petrol_sales
                receipt_data['diesel_sales'] = diesel_sales
                receipt_data['kerosene_sales'] = kerosene_sales

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        async def fetch_current_prices():
            token = app.storage.user.get('token')
            async with httpx.AsyncClient() as client:
                url = f"{auth_state.api_base_url}/pricing/fuel/current"
                resp = await client.get(url, headers={'Authorization': f'Bearer {token}'})
                if resp.status_code == 200:
                    current_prices.update(resp.json())
                    logic['calculate_total']()

        # Initialize Data Loading
        load_sales_data()
        ui.timer(0.2, fetch_current_prices, once=True)
        ui.timer(0.3, populate_shop_options, once=True)
        ui.timer(0.2, load_shop_inventory, once=True)
        ui.timer(0.3, load_pumps, once=True)
        ui.timer(0.4, load_shifts, once=True)
        ui.timer(0.5, load_complaints, once=True)

    dashboard_layout(content)
