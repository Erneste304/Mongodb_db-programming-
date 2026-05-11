from nicegui import ui
from frontend.state import auth_state


def home_page():
    """Main landing page in NiceGUI"""
    ui.query('body').style(
        'background-color: #0f172a; color: white; margin: 0; font-family: "Inter", sans-serif;')

    # Navbar
    with ui.header().classes('items-center justify-between px-8 py-4 bg-[#0f172a]/80 backdrop-blur-md border-b border-white/10'):
        with ui.row().classes('items-center gap-2'):
            ui.icon('local_gas_station', color='white').classes('text-2xl')
            ui.label(
                'PETRO-SYNC').classes('text-xl font-bold tracking-widest text-white')

        with ui.row().classes('items-center gap-6'):
            ui.link('Features', '#features').classes(
                'text-white hover:text-blue-400 no-underline')
            ui.link('Security', '#security').classes(
                'text-white hover:text-blue-400 no-underline')
            ui.button('Login to Portal', on_click=lambda: ui.navigate.to('/login')).props(
                'flat color=blue').classes('bg-blue-600/20 text-blue-400 rounded-lg px-4')

    # Hero Section
    with ui.column().classes('w-full items-center py-24 px-4 gap-8').props('id=hero-section'):
        ui.label('v2.0 PRODUCTION READY').classes(
            'bg-blue-600/20 text-blue-400 px-4 py-1 rounded-full text-sm font-semibold')

        ui.label('Modern Petroleum Management System').classes(
            'text-6xl font-bold text-center leading-tight max-w-4xl text-transparent bg-clip-text bg-gradient-to-r from-white to-slate-400')

        ui.label('The all-in-one command center for fuel stations. Real-time inventory tracking, automated billing, and detailed financial audits at your fingertips.').classes(
            'text-xl text-slate-400 text-center max-w-3xl leading-relaxed')

        with ui.row().classes('gap-4 mt-8'):
            ui.button('Access Control Center', on_click=lambda: ui.navigate.to('/login')).classes(
                'bg-blue-600 hover:bg-blue-700 text-white px-8 py-3 rounded-lg text-lg font-bold transition-all')
            ui.button('View Demo').props('outline color=white').classes(
                'px-8 py-3 rounded-lg text-lg font-bold border-slate-700 text-slate-300')

    # Features Section
    with ui.column().classes('w-full items-center py-20 px-8 gap-4 bg-[#0f172a]').props('id=features'):
        ui.label('Engineered for Excellence').classes(
            'text-4xl font-bold text-center text-white')
        ui.label('Built to handle high-volume operations with precision and speed.').classes(
            'text-lg text-slate-500 text-center mb-12')

        with ui.grid(columns=4).classes('w-full max-w-7xl gap-6'):
            features = [
                ('database', 'MongoDB Powered',
                 'Massive scalability for millions of transactions with Beanie ODM integration.'),
                ('security', 'Secure Auth',
                 'Enterprise-grade JWT tokens and role-based access control for your data.'),
                ('bolt', 'Real-time Analytics',
                 'Instant dashboard updates for fuel levels, sales, and staff activity.'),
                ('description', 'Automated Invoicing',
                 'Generate EBM-compliant receipts and financial reports with one click.')
            ]

            for icon, title, desc in features:
                with ui.card().classes('bg-slate-800/50 border border-white/10 p-8 rounded-2xl gap-4 hover:border-blue-500/50 transition-all'):
                    with ui.column().classes('bg-blue-500/10 p-3 rounded-xl'):
                        ui.icon(icon, color='blue').classes('text-3xl')
                    ui.label(title).classes('text-xl font-bold text-white')
                    ui.label(desc).classes('text-slate-400 leading-relaxed')

    # Footer
    with ui.footer().classes('bg-[#0f172a] border-t border-white/10 py-12 px-8'):
        with ui.row().classes('w-full max-w-7xl mx-auto justify-between items-center'):
            ui.label('© 2024 Petro-Sync Management Systems. All rights reserved.').classes(
                'text-slate-500 text-sm')
            with ui.row().classes('gap-6'):
                ui.icon('account_tree', color='grey').classes(
                    'text-xl cursor-pointer')
                ui.icon('chat', color='grey').classes('text-xl cursor-pointer')
