from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx


def visitor_management_page():
    """Visitor management page for sign-in/out and visitor tracking"""
    def content():
        ui.label('Visitor Management').classes('text-3xl font-bold mb-6 text-slate-800')

        # Stats Cards
        with ui.row().classes('w-full gap-6 mb-8'):
            with ui.card().classes('flex-1 p-6 bg-blue-50 border-l-4 border-blue-500'):
                ui.label('Visitors On Site').classes('text-sm text-blue-600 font-bold uppercase tracking-wider')
                on_site_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-green-50 border-l-4 border-green-500'):
                ui.label('Today\'s Total').classes('text-sm text-green-600 font-bold uppercase tracking-wider')
                today_total_label = ui.label('0').classes('text-3xl font-black text-slate-800')

            with ui.card().classes('flex-1 p-6 bg-orange-50 border-l-4 border-orange-500'):
                ui.label('Pending Briefings').classes('text-sm text-orange-600 font-bold uppercase tracking-wider')
                pending_briefing_label = ui.label('0').classes('text-3xl font-black text-slate-800')

        # Main Tabs
        with ui.tabs().classes('w-full') as tabs:
            sign_in_tab = ui.tab('Sign In Visitor')
            visitors_tab = ui.tab('Current Visitors')
            history_tab = ui.tab('Visitor History')

        with ui.tab_panels(tabs, value=sign_in_tab).classes('w-full bg-transparent'):
            # Sign In Panel
            with ui.tab_panel(sign_in_tab):
                with ui.card().classes('max-w-2xl mx-auto p-8 shadow-xl rounded-2xl border border-slate-100'):
                    ui.label('Visitor Sign In').classes('text-2xl font-bold mb-6 text-center')
                    
                    visitor_name = ui.input('Visitor Name').classes('w-full mb-4').props('outlined')
                    company_name = ui.input('Company Name (Optional)').classes('w-full mb-4').props('outlined')
                    visitor_phone = ui.input('Phone Number').classes('w-full mb-4').props('outlined')
                    id_number = ui.input('ID Number (Optional)').classes('w-full mb-4').props('outlined')
                    
                    visitor_type = ui.select(['delivery_driver', 'inspector', 'contractor', 'sales_rep', 'other'], label='Visitor Type').classes('w-full mb-4').props('outlined')
                    purpose = ui.select(['fuel_delivery', 'safety_inspection', 'maintenance', 'sales_meeting', 'audit'], label='Purpose of Visit').classes('w-full mb-4').props('outlined')
                    
                    escort_required = ui.checkbox('Escort Required').classes('w-full mb-4')
                    safety_briefing = ui.checkbox('Safety Briefing Completed').classes('w-full mb-4')
                    
                    # Delivery-specific fields
                    with ui.row().classes('w-full gap-4 mb-4'):
                        vehicle_reg = ui.input('Vehicle Registration').classes('flex-1').props('outlined')
                        vehicle_type = ui.select(['tanker_truck', 'van', 'car'], label='Vehicle Type').classes('flex-1').props('outlined')
                    
                    doc_verified = ui.checkbox('Delivery Document Verified').classes('w-full mb-4')
                    
                    with ui.row().classes('w-full gap-4 mb-4'):
                        doc_type = ui.select(['delivery_note', 'invoice', 'permit'], label='Document Type').classes('flex-1').props('outlined')
                        doc_number = ui.input('Document Number').classes('flex-1').props('outlined')
                    
                    notes = ui.textarea('Notes (Optional)').classes('w-full mb-4').props('outlined')
                    
                    async def sign_in_visitor():
                        if not visitor_name.value or not visitor_phone.value:
                            ui.notify('Visitor name and phone are required', type='warning')
                            return
                        
                        token = app.storage.user.get('token')
                        payload = {
                            "visitor_name": visitor_name.value,
                            "company_name": company_name.value if company_name.value else None,
                            "visitor_phone": visitor_phone.value,
                            "visitor_type": visitor_type.value,
                            "purpose": purpose.value,
                            "id_number": id_number.value if id_number.value else None,
                            "escort_required": escort_required.value,
                            "safety_briefing_completed": safety_briefing.value,
                            "delivery_document_verified": doc_verified.value,
                            "delivery_document_type": doc_type.value if doc_verified.value else None,
                            "delivery_document_number": doc_number.value if doc_verified.value else None,
                            "vehicle_registration": vehicle_reg.value if vehicle_reg.value else None,
                            "vehicle_type": vehicle_type.value if vehicle_reg.value else None,
                            "notes": notes.value if notes.value else None
                        }
                        
                        async with httpx.AsyncClient() as client:
                            url = f"{auth_state.api_base_url}/visitors/log"
                            resp = await client.post(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code in (200, 201):
                                ui.notify('Visitor signed in successfully', type='positive')
                                load_visitor_data()
                                # Clear form
                                visitor_name.value = ''
                                company_name.value = ''
                                visitor_phone.value = ''
                                id_number.value = ''
                                notes.value = ''
                            else:
                                ui.notify(f"Error: {resp.text}", type='negative')
                    
                    ui.button('Sign In Visitor', on_click=sign_in_visitor).props('elevated color=green').classes('w-full')

            # Current Visitors Panel
            with ui.tab_panel(visitors_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Current Visitors On Site').classes('text-xl font-bold')
                
                current_visitors_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'visitor_name'},
                        {'name': 'company', 'label': 'Company', 'field': 'company_name'},
                        {'name': 'type', 'label': 'Type', 'field': 'visitor_type'},
                        {'name': 'purpose', 'label': 'Purpose', 'field': 'purpose'},
                        {'name': 'check_in', 'label': 'Check In', 'field': 'check_in_time'},
                        {'name': 'escort', 'label': 'Escort', 'field': 'escort_required'},
                        {'name': 'briefing', 'label': 'Briefing', 'field': 'safety_briefing_completed'},
                        {'name': 'actions', 'label': 'Actions', 'field': 'id'},
                    ],
                    rows=[],
                    row_key='id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

            # Visitor History Panel
            with ui.tab_panel(history_tab):
                with ui.row().classes('w-full justify-between items-center mb-4'):
                    ui.label('Visitor History').classes('text-xl font-bold')
                
                history_table = ui.table(
                    columns=[
                        {'name': 'name', 'label': 'Name', 'field': 'visitor_name'},
                        {'name': 'company', 'label': 'Company', 'field': 'company_name'},
                        {'name': 'type', 'label': 'Type', 'field': 'visitor_type'},
                        {'name': 'purpose', 'label': 'Purpose', 'field': 'purpose'},
                        {'name': 'check_in', 'label': 'Check In', 'field': 'check_in_time'},
                        {'name': 'check_out', 'label': 'Check Out', 'field': 'check_out_time'},
                        {'name': 'status', 'label': 'Status', 'field': 'status'},
                    ],
                    rows=[],
                    row_key='id'
                ).classes('w-full shadow-md rounded-xl').props('loading')

        def load_visitor_data():
            token = app.storage.user.get('token')
            res = {'done': False, 'visitors': [], 'err': ''}
            current_visitors_table.props(add='loading')
            history_table.props(add='loading')

            def fetch():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    base = auth_state.api_base_url

                    r1 = httpx.get(f'{base}/visitors/log', headers=headers, timeout=10.0)
                    if r1.status_code == 200:
                        res['visitors'] = r1.json()

                except Exception as e:
                    res['err'] = str(e)
                finally:
                    res['done'] = True

            def apply():
                if not res['done']:
                    return
                p.cancel()
                current_visitors_table.props(remove='loading')
                history_table.props(remove='loading')

                if not res['err']:
                    # Split visitors into on-site and history
                    on_site = [v for v in res['visitors'] if v.get('status') == 'on_site']
                    completed = [v for v in res['visitors'] if v.get('status') == 'completed']
                    
                    # Add sign-out button to on-site visitors
                    for v in on_site:
                        v['actions'] = 'Sign Out'
                    
                    current_visitors_table.rows = on_site
                    history_table.rows = completed
                    
                    # Update stats
                    on_site_label.set_text(str(len(on_site)))
                    today_total_label.set_text(str(len(res['visitors'])))
                    pending_briefing_label.set_text(str(len([v for v in on_site if not v.get('safety_briefing_completed', False)])))

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_visitor_data()

    dashboard_layout(content)
