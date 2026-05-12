from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def partner_management_page():
    """Partner management page for business collaboration"""
    def content():
        ui.label('Partner Management').classes('text-3xl font-bold mb-6 text-slate-800')

        # Stats Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label('Active Partners').classes('text-sm text-blue-600 font-bold uppercase tracking-wider')
                active_partners_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label('Total Commission').classes('text-sm text-green-600 font-bold uppercase tracking-wider')
                total_commission_label = ui.label('0 RWF').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-orange-50 border-l-4 border-orange-500'):
                ui.label('Contracts Expiring').classes('text-sm text-orange-600 font-bold uppercase tracking-wider')
                expiring_label = ui.label('0').classes('text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            partners_tab = ui.tab('Partners')
            add_partner_tab = ui.tab('Add Partner')
            performance_tab = ui.tab('Performance Reports')

        with ui.tab_panels(tabs, value=partners_tab).classes('w-full bg-transparent'):
            # Partners Panel
            with ui.tab_panel(partners_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Business Partners').classes('text-xl font-bold')
                
                partners_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Partner ID', 'field': 'partner_id'},
                        {'name': 'name', 'label': 'Name', 'field': 'name'},
                        {'name': 'type', 'label': 'Type', 'field': 'partner_type'},
                        {'name': 'contact', 'label': 'Contact', 'field': 'contact_person'},
                        {'name': 'commission', 'label': 'Commission %', 'field': 'commission_rate'},
                        {'name': 'sales', 'label': 'Sales (RWF)', 'field': 'total_sales_volume'},
                        {'name': 'rating', 'label': 'Rating', 'field': 'quality_rating'},
                        {'name': 'status', 'label': 'Status', 'field': 'is_active'},
                    ],
                    rows=[],
                    row_key='partner_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Add Partner Panel
            with ui.tab_panel(add_partner_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('Add New Partner').classes('text-2xl font-bold mb-6 text-center')
                    
                    partner_id = ui.input('Partner ID').classes('w-full mb-4').props('outlined')
                    name = ui.input('Partner Name').classes('w-full mb-4').props('outlined')
                    partner_type = ui.select(['fuel_supplier', 'service_provider', 'financial_partner', 'business_partner'], label='Partner Type').classes('w-full mb-4').props('outlined')
                    contact_person = ui.input('Contact Person').classes('w-full mb-4').props('outlined')
                    email = ui.input('Email').classes('w-full mb-4').props('outlined')
                    phone = ui.input('Phone').classes('w-full mb-4').props('outlined')
                    address = ui.input('Address (Optional)').classes('w-full mb-4').props('outlined')
                    tin_number = ui.input('TIN Number (Optional)').classes('w-full mb-4').props('outlined')
                    
                    with ui.row().classes('w-full gap-4 mb-4'):
                        contract_start = ui.input('Contract Start Date').classes('flex-1').props('type=date outlined')
                        contract_end = ui.input('Contract End Date').classes('flex-1').props('type=date outlined')
                    
                    commission_rate = ui.input('Commission Rate (%)').classes('w-full mb-4').props('type=number outlined')
                    monthly_target = ui.input('Monthly Sales Target (RWF)').classes('w-full mb-4').props('type=number outlined')
                    
                    async def add_partner():
                        if not partner_id.value or not name.value or not contact_person.value or not email.value or not phone.value:
                            ui.notify('Required fields are missing', type='warning')
                            return
                        
                        token = app.storage.user.get('token')
                        payload = {
                            "partner_id": partner_id.value,
                            "name": name.value,
                            "partner_type": partner_type.value,
                            "contact_person": contact_person.value,
                            "email": email.value,
                            "phone": phone.value,
                            "address": address.value if address.value else None,
                            "tin_number": tin_number.value if tin_number.value else None,
                            "contract_start_date": contract_start.value if contract_start.value else datetime.utcnow().isoformat(),
                            "contract_end_date": contract_end.value if contract_end.value else None,
                            "commission_rate": float(commission_rate.value) if commission_rate.value else 0.0,
                            "monthly_sales_target": float(monthly_target.value) if monthly_target.value else None
                        }
                        
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/partners/"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Partner added successfully', type='positive')
                                load_partner_data()
                                # Clear form
                                partner_id.value = ''
                                name.value = ''
                                contact_person.value = ''
                                email.value = ''
                                phone.value = ''
                                address.value = ''
                                tin_number.value = ''
                                commission_rate.value = ''
                                monthly_target.value = ''
                            else:
                                ui.notify(f"Error: {resp.text}", type='negative')
                    
                    ui.button('Add Partner', on_click=add_partner).props('elevated color=green').classes('w-full')

            # Performance Reports Panel
            with ui.tab_panel(performance_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Performance Reports').classes('text-xl font-bold')
                
                performance_table = ui.table(
                    columns=[
                        {'name': 'id', 'label': 'Partner ID', 'field': 'partner_id'},
                        {'name': 'name', 'label': 'Name', 'field': 'partner_name'},
                        {'name': 'sales_volume', 'label': 'Sales Volume (RWF)', 'field': 'total_sales_volume'},
                        {'name': 'commission', 'label': 'Commission Earned (RWF)', 'field': 'total_commission_earned'},
                        {'name': 'delivery_rate', 'label': 'On-Time Delivery %', 'field': 'on_time_delivery_rate'},
                        {'name': 'quality', 'label': 'Quality Rating', 'field': 'quality_rating'},
                        {'name': 'target_achievement', 'label': 'Target Achievement %', 'field': 'target_achievement_percentage'},
                        {'name': 'compliance', 'label': 'Compliance Score', 'field': 'compliance_score'},
                    ],
                    rows=[],
                    row_key='partner_id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_partner_data():
            token = app.storage.user.get('token')
            res = {'done': False, 'partners': [], 'performance': [], 'err': ''}
            partners_table.props(add='loading')
            performance_table.props(add='loading')

            def fetch():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url

                    r1 = httpx.get(f'{base}/partners/', headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        res['partners'] = r1.json()

                    # Get performance reports for each partner
                    for partner in res['partners']:
                        r2 = httpx.get(f'{base}/partners/{partner["partner_id"]}/performance-report', headers=headers, timeout=10.0)
                        if r2.status_code == 200:
                            res['performance'].append(r2.json())

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                partners_table.props(remove='loading')
                performance_table.props(remove='loading')

                if not res['err']:
                    partners_table.rows = res['partners']
                    performance_table.rows = res['performance']
                    
                    # Update stats
                    active_partners = [p for p in res['partners'] if p.get('is_active')]
                    active_partners_label.set_text(str(len(active_partners)))
                    
                    total_comm = sum(p.get('total_commission_earned', 0) for p in res['partners'])
                    total_commission_label.set_text(f"{total_comm:,.0f} RWF")
                    
                    # Count expiring contracts (within 30 days)
                    from datetime import datetime, timedelta
                    thirty_days = datetime.utcnow() + timedelta(days=30)
                    expiring = 0
                    for p in res['partners']:
                        if p.get('contract_end_date'):
                            end_date = datetime.fromisoformat(p['contract_end_date'].replace('Z', '+00:00'))
                            if end_date <= thirty_days:
                                expiring += 1
                    expiring_label.set_text(str(expiring))

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_partner_data()

    dashboard_layout(content)
