"""
Superadmin Dashboard Pages
User management, role permissions, fuel pricing, partner agreements, system settings, audit logs
"""
from nicegui import ui, app
from frontend.state import auth_state, dashboard_layout
import httpx
import threading


def users_page():
    """User management page"""
    def content():
        ui.label('User Management').classes('text-2xl font-bold mb-6')

        # Create the dialog outside the button click handler
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add New User').classes('text-xl font-bold mb-4')

            username_input = ui.input('Username', placeholder='Enter username')
            email_input = ui.input('Email', placeholder='Enter email')
            password_input = ui.input(
                'Password', placeholder='Enter password', password=True)
            role_input = ui.select(label='Role', options=[
                                   'admin', 'accountant', 'receptionist', 'inventory_manager', 'staff', 'pump_attendant'])

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=dialog.close)
                ui.button('Create', on_click=lambda: create_user(
                    dialog, username_input.value, email_input.value, password_input.value, role_input.value))

        # Update User Dialog
        with ui.dialog() as edit_dialog, ui.card().classes('w-96'):
            ui.label('Update User Record').classes('text-xl font-bold mb-4')
            edit_id = ui.label('').classes('hidden')  # Hidden storage for ID
            edit_name = ui.input('Full Name')
            edit_phone = ui.input('Phone')
            edit_status = ui.checkbox('Account Active')

            with ui.row().classes('w-full justify-end gap-2 mt-4'):
                ui.button('Cancel', on_click=edit_dialog.close)
                ui.button('Save Changes', on_click=lambda: update_user_record(
                    edit_id.text, edit_name.value, edit_phone.value, edit_status.value))

        def open_edit(row):
            edit_id.set_text(row['id'])
            edit_name.value = row.get('full_name', '')
            edit_phone.value = row.get('phone', '')
            edit_status.value = row['status'] == 'Active'
            edit_dialog.open()

        # ── Live users table (starts empty, populated by load_users) ──────────
        with ui.card().classes('w-full'):
            table = ui.table(
                columns=[
                    {'name': 'username', 'label': 'Username',
                        'field': 'username', 'sortable': True},
                    {'name': 'email',    'label': 'Email',
                        'field': 'email',    'sortable': True},
                    {'name': 'role',     'label': 'Role',
                        'field': 'role',     'sortable': True},
                    {'name': 'status',   'label': 'Status',
                        'field': 'status',   'sortable': True},
                    {'name': 'actions',  'label': 'Actions',
                        'field': 'id'},
                ],
                rows=[],
                row_key='username'
            ).classes('w-full').props('rows-per-page-options=[10,20,50] loading')

        # ── load_users: fetch real data from the API, update table in place ──
        def load_users():  # Changed
            token = app.storage.user.get('token')
            fetch_result = {'done': False, 'rows': [], 'error': ''}
            table.props(add='loading')

            def do_fetch():
                try:
                    headers = {
                        'Authorization': f'Bearer {token}'} if token else {}
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/users/'
                    resp = httpx.get(  # Use httpx
                        url,
                        headers=headers,
                        timeout=10
                    )
                    if resp.status_code == 200:
                        users = resp.json()
                        fetch_result['rows'] = [
                            {
                                'id':       u.get('id', ''),
                                'username': u.get('username', ''),
                                'email':    u.get('email') or '',
                                'role':     u.get('role', ''),
                                'status':   'Active' if u.get('is_active', True) else 'Inactive',
                            }
                            for u in users
                        ]
                    else:
                        fetch_result['error'] = f'HTTP {resp.status_code} at {url}'
                except Exception as exc:
                    fetch_result['error'] = str(exc)
                finally:
                    fetch_result['done'] = True

            def apply_result():
                if not fetch_result['done']:
                    return
                poll_timer.cancel()
                table.props(remove='loading')
                if fetch_result['error']:
                    ui.notify(
                        f'Could not load users: {fetch_result["error"]}', type='negative')
                else:
                    table.rows = fetch_result['rows']
                    table.update()

            threading.Thread(target=do_fetch, daemon=True).start()
            poll_timer = ui.timer(0.5, apply_result)

        # Load users immediately when the page renders
        load_users()

        # ── create_user: POST to API, then refresh the table on success ───────
        def create_user(dialog, username, email, password, role):
            if not all([username, email, password, role]):
                ui.notify('Please fill all fields', type='warning')
                return

            token = app.storage.user.get('token')
            if not token:
                ui.notify('Authentication required', type='warning')
                return

            ui.notify('Creating user...', type='info')
            result = {'done': False, 'success': False, 'message': ''}

            def api_call():
                try:
                    headers = {'Authorization': f'Bearer {token}'}
                    payload = {
                        'username': username,
                        'email': email,
                        'password': password,
                        'role_name': role
                    }
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/users/'
                    response = httpx.post(  # Use httpx
                        url,
                        json=payload,
                        headers=headers
                    )
                    if response.status_code in (200, 201):
                        result['success'] = True
                        result['message'] = f'User {username} created successfully!'
                    else:
                        try:
                            error_data = response.json()
                            result[
                                'message'] = f'Error {response.status_code}: {error_data.get("detail", "Unknown error")}'
                        except Exception:
                            result['message'] = f'Error {response.status_code}: {response.text}'
                except Exception as e:
                    result['message'] = f'Network error: {str(e)}'
                finally:
                    result['done'] = True

            def check_result():
                if not result['done']:
                    return
                create_timer.cancel()
                if result['success']:
                    ui.notify(result['message'], type='positive')
                    dialog.close()
                    load_users()   # ✅ refresh the table so new user appears
                else:
                    ui.notify(result['message'], type='negative')

            threading.Thread(target=api_call, daemon=True).start()
            create_timer = ui.timer(0.5, check_result)

        def delete_user_request(user_id):
            async def do_delete():
                with ui.dialog() as dialog, ui.card():
                    ui.label('Confirm Deletion').classes('text-lg font-bold')
                    ui.label('Are you sure you want to delete this user?')
                    with ui.row().classes('w-full justify-end gap-2'):
                        ui.button('No', on_click=lambda: dialog.submit(
                            False)).props('flat')
                        ui.button('Yes', on_click=lambda: dialog.submit(
                            True)).props('flat color=red')

                if await dialog:
                    token = app.storage.user.get('token')
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/users/{user_id}'
                    async with httpx.AsyncClient() as client:
                        try:
                            resp = await client.delete(url, headers={'Authorization': f'Bearer {token}'})
                            if resp.status_code == 200:
                                ui.notify('User deleted successfully',
                                          type='positive')
                                load_users()
                            elif resp.status_code == 202:  # Assuming 202 for "Approval Submitted"
                                ui.notify(
                                    'Deletion request sent for Admin approval', type='warning')
                            else:
                                ui.notify(
                                    f"Error: {resp.text}", type='negative')
                        except Exception as e:
                            ui.notify(
                                f"Connection error: {str(e)}", type='negative')

            ui.timer(0, do_delete, once=True)

        def update_user_record(uid, name, phone, active):
            async def do_update():
                token = app.storage.user.get('token')
                # Remove redundant replace
                url = f'{auth_state.api_base_url}/users/{uid}'
                payload = {"full_name": name,
                           "phone": phone, "is_active": active}
                async with httpx.AsyncClient() as client:
                    resp = await client.patch(url, json=payload, headers={'Authorization': f'Bearer {token}'})
                    if resp.status_code == 200:
                        ui.notify('User record updated', type='positive')
                        edit_dialog.close()
                        load_users()
                    else:
                        ui.notify('Update failed', type='negative')

            ui.timer(0.1, do_update, once=True)

        # ── Manage Permissions Dialog ────────────────────────────────────────
        with ui.dialog() as perm_dialog, ui.card().classes('w-[500px]'):
            ui.label('User Access Control').classes('text-xl font-bold mb-2')
            perm_container = ui.column().classes('w-full')
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Close', on_click=perm_dialog.close).props('flat')

        def open_permissions(user_id):
            perm_container.clear()
            with perm_container:
                ui.spinner(size='lg').classes('self-center my-4')
            perm_dialog.open()

            def fetch_perms():
                token = app.storage.user.get('token')
                try:
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/users/{user_id}/permissions'
                    r = httpx.get(  # Use httpx
                        url, headers={'Authorization': f'Bearer {token}'}, timeout=10.0)
                    perms = r.json()

                    perm_container.clear()
                    with perm_container:
                        for p in perms:
                            with ui.row().classes('w-full items-center justify-between p-2 border-b'):
                                with ui.column():
                                    ui.label(f"{p['module'].upper()}").classes(
                                        'font-bold text-xs')
                                    ui.label(f"{p['action']} {p['resource']}").classes(
                                        'text-sm text-gray-600')

                                # Toggle Switch for "Enabled"
                                def toggle(p_id=p['id'], current=p['is_enabled']):
                                    def do_toggle():
                                        try:  # Use httpx
                                            # Remove redundant replace
                                            t_url = f'{auth_state.api_base_url}/users/{user_id}/permissions/toggle'
                                            httpx.post(t_url,
                                                       json={
                                                           'permission_id': p_id, 'enabled': not current},
                                                       headers={'Authorization': f'Bearer {token}'})
                                            ui.notify('Service Status Updated')
                                            open_permissions(
                                                user_id)  # Refresh
                                        except:
                                            ui.notify('Update Failed',
                                                      type='negative')
                                    do_toggle()

                                ui.switch(
                                    value=p['is_enabled'], on_change=toggle)
                except Exception as e:
                    ui.notify(f"Error loading services: {e}", type='negative')

            threading.Thread(target=fetch_perms, daemon=True).start()

        # Add Actions Slot to Table
        table.add_slot('body-cell-actions', '''
            <q-td :props="props">
                <q-btn flat round color="blue" size="sm" icon="security" @click="$parent.$emit('manage', props.row.id)">
                    <q-tooltip>Enable/Disable Services</q-tooltip>
                </q-btn>
                <q-btn flat round color="green" size="sm" icon="edit" @click="$parent.$emit('edit', props.row)">
                    <q-tooltip>Edit User Record</q-tooltip>
                </q-btn>
                <q-btn flat round color="red" size="sm" icon="delete" @click="$parent.$emit('delete', props.row.id)">
                    <q-tooltip>Delete User</q-tooltip>
                </q-btn>
            </q-td>
        ''')
        table.on('manage', lambda msg: open_permissions(msg.args))
        table.on('edit', lambda msg: open_edit(msg.args))
        table.on('delete', lambda msg: delete_user_request(msg.args))

        # ── Toolbar ───────────────────────────────────────────────────────────
        with ui.row().classes('w-full mb-4 gap-2'):
            ui.button('Add User', on_click=dialog.open)
            ui.button('Refresh', on_click=load_users)

    dashboard_layout(content)


def roles_page():
    """Role and permissions management page"""
    def content():
        ui.label('Role & Permission Management').classes(
            'text-2xl font-bold mb-6')

        with ui.card().classes('w-full'):
            ui.label('Roles').classes('text-lg font-bold mb-4')
            table = ui.table(
                columns=[
                    {'name': 'name', 'label': 'Role Name',
                        'field': 'name', 'sortable': True},
                    {'name': 'level', 'label': 'Level',
                        'field': 'level', 'sortable': True},
                    {'name': 'description', 'label': 'Description',
                        'field': 'description'},
                ],
                rows=[],
                row_key='name'
            ).classes('w-full').props('loading')

        def load_roles():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:  # Use httpx
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/users/roles'
                    r = httpx.get(
                        url, headers={'Authorization': f'Bearer {token}'})
                    if r.status_code == 200:
                        res['rows'] = [{
                            'name': i['name'],
                            'level': i['level'],
                            'description': i.get('description', '')
                        } for i in r.json()]
                    else:
                        res['err'] = r.text
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
                    table.update()
            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_roles()

    dashboard_layout(content)


def pricing_page():
    """Fuel pricing management page"""
    def content():
        ui.label('Fuel Pricing Management').classes('text-2xl font-bold mb-6')

        # ── Add Price Form ───────────────────────────────────────────────────
        with ui.card().classes('w-full mb-4'):
            with ui.row().classes('w-full gap-4 items-end'):
                fuel_type_input = ui.select(label='Fuel Type', options=[
                                            'petrol', 'diesel', 'kerosene', 'lpg'])
                price_input = ui.number('Price per Liter (RWF)', format='%.0f')
                date_input = ui.input('Effective Date').props('type="date"')

                def add_price():
                    if not all([fuel_type_input.value, price_input.value]):
                        ui.notify('Please fill required fields',
                                  type='warning')
                        return

                    token = app.storage.user.get('token')
                    result = {'done': False, 'success': False, 'message': ''}
                    ui.notify('Adding price...', type='info')

                    def api_call():
                        try:
                            payload = {
                                "fuel_type": fuel_type_input.value,
                                "price_per_liter": price_input.value,
                                "effective_date": date_input.value
                            }
                            # Remove redundant replace
                            url = f'{auth_state.api_base_url}/pricing/fuel'
                            resp = httpx.post(  # Use httpx
                                url,
                                json=payload,
                                headers={'Authorization': f'Bearer {token}'}
                            )
                            if resp.status_code in (200, 201):
                                result['success'] = True
                                result['message'] = 'Price added successfully'
                            else:
                                result['message'] = f'Error: {resp.text}'
                        except Exception as e:
                            result['message'] = str(e)
                        finally:
                            result['done'] = True

                    def check():
                        if not result['done']:
                            return
                        t.cancel()
                        if result['success']:
                            ui.notify(result['message'], type='positive')
                            load_prices()
                        else:
                            ui.notify(result['message'], type='negative')

                    threading.Thread(target=api_call, daemon=True).start()
                    t = ui.timer(0.5, check)

                ui.button('Add Price', on_click=add_price)

        # ── Prices Table ─────────────────────────────────────────────────────
        with ui.card().classes('w-full'):
            ui.label('Current Prices').classes('text-lg font-bold mb-4')
            table = ui.table(
                columns=[
                    {'name': 'fuel_type', 'label': 'Fuel Type',
                        'field': 'fuel_type', 'sortable': True},
                    {'name': 'price',
                        'label': 'Price (RWF/L)', 'field': 'price', 'sortable': True},
                    {'name': 'effective_date', 'label': 'Effective Date',
                        'field': 'effective_date', 'sortable': True},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='fuel_type'
            ).classes('w-full').props('loading')

        def load_prices():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:  # Use httpx
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/pricing/fuel/current'
                    resp = httpx.get(  # Use httpx
                        url,
                        headers={'Authorization': f'Bearer {token}'}
                    )
                    if resp.status_code == 200:
                        data = resp.json()
                        res['rows'] = [{
                            'fuel_type': item['fuel_type'],
                            'price': f"{item['price_per_liter']:,}",
                            'effective_date': item['effective_date'][:10],
                            'status': 'Active' if item['is_active'] else 'Inactive'
                        } for item in data]
                    else:
                        res['err'] = resp.text
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
                    table.update()

            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_prices()

    dashboard_layout(content)


def partners_page():
    """Partner agreements management page"""
    def content():
        ui.label('Partner Agreements').classes('text-2xl font-bold mb-6')

        # ── Add Partner Form ────────────────────────────────────────────────
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('New Agreement').classes('text-xl font-bold mb-4')
            name = ui.input('Partner Name')
            p_type = ui.select(label='Type', options=[
                               'Fuel Supply', 'Corporate Client', 'Service Provider'])
            start = ui.input('Start Date').props('type="date"')
            commission = ui.number('Commission %', value=0).props(
                'min=0 max=100 step=0.1')
            contact = ui.input('Contact Person')
            email = ui.input('Contact Email')
            phone = ui.input('Contact Phone')

            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close)

                def save():
                    if not name.value or not p_type.value or not start.value:
                        ui.notify('Please fill all required fields',
                                  type='warning')
                        return
                    if commission.value is None or not (0 <= commission.value <= 100):
                        ui.notify(
                            'Commission percentage must be between 0 and 100', type='warning')
                        return

                    token = app.storage.user.get('token')
                    res = {'done': False, 'msg': '', 'ok': False}

                    # Capture payload immediately on click
                    payload = {
                        "partner_name": name.value,
                        "partner_type": p_type.value,
                        "agreement_start_date": start.value,
                        "commission_percentage": commission.value,
                        "contact_person": contact.value,
                        "contact_email": email.value,
                        "contact_phone": phone.value
                    }

                    def api():
                        try:  # Use httpx
                            # Remove redundant replace
                            url = f'{auth_state.api_base_url}/pricing/partners'
                            r = httpx.post(url, json=payload, headers={  # Use httpx
                                'Authorization': f'Bearer {token}'})
                            if r.status_code in (200, 201):
                                res['ok'] = True
                            else:
                                try:
                                    error_data = r.json()
                                    res['msg'] = f"Error {r.status_code}: {error_data.get('detail', 'Unknown error')}"
                                except:
                                    res['msg'] = f"Error {r.status_code}: {r.text}"
                        except Exception as e:
                            res['msg'] = str(e)
                        finally:
                            res['done'] = True

                    def check():
                        if not res['done']:
                            return
                        t.cancel()
                        if res['ok']:
                            ui.notify('Agreement saved', type='positive')
                            dialog.close()
                            load_partners()
                        else:
                            ui.notify(f"Error: {res['msg']}", type='negative')
                    threading.Thread(target=api, daemon=True).start()
                    t = ui.timer(0.5, check)
                ui.button('Save', on_click=save)

        with ui.row().classes('w-full mb-4'):
            ui.button('Add New Agreement', on_click=dialog.open)

        # ── Table ────────────────────────────────────────────────────────────
        with ui.card().classes('w-full'):
            table = ui.table(
                columns=[
                    {'name': 'partner', 'label': 'Partner',
                        'field': 'partner', 'sortable': True},
                    {'name': 'type', 'label': 'Type', 'field': 'type'},
                    {'name': 'start', 'label': 'Start', 'field': 'start'},
                    {'name': 'commission', 'label': 'Comm %', 'field': 'commission'},
                    {'name': 'status', 'label': 'Status', 'field': 'status'},
                ],
                rows=[],
                row_key='partner'
            ).classes('w-full').props('loading')

        def load_partners():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:  # Use httpx
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/pricing/partners'
                    r = httpx.get(  # Use httpx
                        url, headers={'Authorization': f'Bearer {token}'})
                    if r.status_code == 200:
                        res['rows'] = [{
                            'partner': i['partner_name'],
                            'type': i['partner_type'],
                            'start': i['agreement_start_date'][:10],
                            'commission': i['commission_percentage'],
                            'status': 'Active' if i['is_active'] else 'Inactive'
                        } for i in r.json()]
                    else:
                        res['err'] = r.text
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
                    table.update()
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_partners()

    dashboard_layout(content)


def settings_page():
    """System settings page"""
    def content():
        ui.label('System Settings').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full'):
            with ui.column().classes('w-full gap-4'):
                ui.label('Business Configuration').classes('text-lg font-bold')

                name = ui.input('Station Name')
                address = ui.input('Station Address')
                phone = ui.input('Contact Phone')
                email = ui.input('Contact Email')

                ui.separator()
                ui.label('Business Rules').classes('text-lg font-bold')

                vat = ui.number('Default VAT %', value=18)
                threshold = ui.number('Low Fuel Threshold %', value=20)
                payment_limit = ui.number(
                    'Large Payment Threshold (RWF)', value=1_000_000)

                def load_settings():
                    token = app.storage.user.get('token')
                    res = {'done': False, 'data': None, 'err': ''}

                    def api():
                        try:  # Use httpx
                            # Remove redundant replace
                            url = f'{auth_state.api_base_url}/settings/system'
                            r = httpx.get(  # Use httpx
                                url, headers={'Authorization': f'Bearer {token}'})
                            if r.status_code == 200:
                                res['data'] = r.json()
                            else:
                                res['err'] = r.text
                        except Exception as e:
                            res['err'] = str(e)
                        finally:
                            res['done'] = True

                    def check():
                        if not res['done']:
                            return
                        t.cancel()
                        if res['data']:
                            d = res['data']
                            name.value = d.get('station_name', '')
                            address.value = d.get('station_address', '')
                            phone.value = d.get('station_phone', '')
                            email.value = d.get('station_email', '')
                            vat.value = d.get('default_vat_percentage', 18)
                            threshold.value = d.get(
                                'low_fuel_threshold_percentage', 20)
                            payment_limit.value = d.get(
                                'large_payment_threshold', 1000000)
                        else:
                            ui.notify(
                                f"Load error: {res['err']}", type='negative')
                    import threading
                    threading.Thread(target=api, daemon=True).start()
                    t = ui.timer(0.5, check)

                def save_settings():
                    token = app.storage.user.get('token')
                    res = {'done': False, 'ok': False, 'err': ''}

                    def api():
                        try:  # Use httpx
                            payload = {
                                "station_name": name.value,
                                "station_address": address.value,
                                "station_phone": phone.value,
                                "station_email": email.value,
                                "default_vat_percentage": vat.value,
                                "low_fuel_threshold_percentage": threshold.value,
                                "large_payment_threshold": payment_limit.value
                            }
                            # Remove redundant replace
                            url = f'{auth_state.api_base_url}/settings/system'
                            r = httpx.put(url, json=payload, headers={  # Use httpx
                                'Authorization': f'Bearer {token}'})
                            if r.status_code == 200:
                                res['ok'] = True
                            else:
                                res['err'] = r.text
                        except Exception as e:
                            res['err'] = str(e)
                        finally:
                            res['done'] = True

                    def check():
                        if not res['done']:
                            return
                        t.cancel()
                        if res['ok']:
                            ui.notify('Settings saved', type='positive')
                        else:
                            ui.notify(
                                f"Save error: {res['err']}", type='negative')
                    import threading
                    threading.Thread(target=api, daemon=True).start()
                    t = ui.timer(0.5, check)

                ui.button('Save Settings',
                          on_click=save_settings).classes('mt-4')
                load_settings()

    dashboard_layout(content)


def audit_page():
    """Audit logs page"""
    def content():
        ui.label('Audit Logs').classes('text-2xl font-bold mb-6')

        with ui.card().classes('w-full'):
            table = ui.table(
                columns=[
                    {'name': 'timestamp', 'label': 'Timestamp',
                        'field': 'timestamp', 'sortable': True},
                    {'name': 'user', 'label': 'User ID', 'field': 'user'},
                    {'name': 'action', 'label': 'Action',
                        'field': 'action', 'sortable': True},
                    {'name': 'resource', 'label': 'Resource', 'field': 'resource'},
                ],
                rows=[],
                row_key='timestamp'
            ).classes('w-full').props('loading')

        def load_logs():
            token = app.storage.user.get('token')
            res = {'done': False, 'rows': [], 'err': ''}
            table.props(add='loading')

            def fetch():
                try:  # Use httpx
                    # Remove redundant replace
                    url = f'{auth_state.api_base_url}/settings/logs'
                    r = httpx.get(  # Use httpx
                        url, headers={'Authorization': f'Bearer {token}'})
                    if r.status_code == 200:
                        res['rows'] = [{
                            'timestamp': i['timestamp'][:19].replace('T', ' '),
                            'user': i['user_id'],
                            'action': i['action'],
                            'resource': f"{i['resource_type']}:{i['resource_id']}"
                        } for i in r.json()]
                    else:
                        res['err'] = r.text
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
                    table.update()
            import threading
            threading.Thread(target=fetch, daemon=True).start()
            p = ui.timer(0.5, apply)

        load_logs()
        ui.button('Refresh', on_click=load_logs).classes('mt-4')

    dashboard_layout(content)
