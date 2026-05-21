from nicegui import ui
from frontend.state import auth_state


def home_page():
    """Main landing page in NiceGUI - Petro-Sync Rwanda"""
    
    # Custom CSS for video background, glassmorphism and animations
    ui.add_head_html('''
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
        
        body {
            margin: 0;
            font-family: 'Outfit', sans-serif;
            background: #020617;
            overflow-x: hidden;
        }
        
        .video-container {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            overflow: hidden;
            z-index: -1;
        }
        
        .video-container video {
            min-width: 100%;
            min-height: 100%;
            object-fit: cover;
            opacity: 0.4;
            filter: grayscale(30%) brightness(50%);
        }

        .hero-section {
            position: relative;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(rgba(2, 6, 23, 0.5), rgba(2, 6, 23, 0.5)), url('/static/hero-bg.png') center/cover no-repeat;
            background-attachment: fixed;
        }
        
        .glass-card {
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 24px;
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .glass-card:hover {
            background: rgba(255, 255, 255, 0.06);
            border-color: rgba(59, 130, 246, 0.4);
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.4);
        }
        
        .stat-value {
            background: linear-gradient(to right, #60a5fa, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        .nav-link:hover {
            color: #3b82f6 !important;
        }
        
        .animate-fade-in {
            animation: fadeIn 1.2s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .map-container {
            border-radius: 24px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
        }
    </style>
    ''')

    # Navbar
    with ui.header().classes('items-center justify-between px-12 py-6 bg-transparent border-b border-white/5 fixed w-full z-50'):
        with ui.row().classes('items-center gap-3'):
            with ui.element('div').classes('bg-blue-600 p-2 rounded-lg'):
                ui.icon('local_gas_station', color='white').classes('text-2xl')
            ui.label('PETRO-SYNC').classes('text-2xl font-black tracking-tighter text-white')

        with ui.row().classes('items-center gap-8 hidden md:flex'):
            ui.link('About', '#about').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Achievements', '#achievements').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Map', '#location').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Contact', '#contact').classes('text-gray-300 font-medium no-underline nav-link')
            ui.button('Portal Login', on_click=lambda: ui.navigate.to('/login')).props('unelevated color=blue-600').classes('rounded-full px-8 font-bold')

    # Hero Section with Video Background
    with ui.element('div').classes('hero-section w-full'):
        # Video Background
        ui.html('''
            <div class="video-container">
                <video autoplay muted loop playsinline>
                    <source src="https://assets.mixkit.co/videos/preview/mixkit-aerial-view-of-a-large-city-at-night-11028-large.mp4" type="video/mp4">
                    Your browser does not support the video tag.
                </video>
            </div>
        ''')
        
        with ui.column().classes('items-center animate-fade-in z-10 px-4'):
            ui.label('REACHING CENTRAL AFRICA').classes('text-blue-400 font-bold tracking-[0.4em] text-xs mb-4 bg-blue-400/10 px-4 py-1 rounded-full')
            ui.label('PETRO-SYNC RWANDA').classes('text-7xl md:text-9xl font-black text-white text-center tracking-tighter')
            ui.label('Powering the Heart of Kigali with Excellence').classes('text-xl md:text-3xl text-gray-300 text-center max-w-3xl mt-6 font-light opacity-80')
            
            with ui.row().classes('gap-6 mt-12'):
                ui.button('Access Portal', on_click=lambda: ui.navigate.to('/login')).classes('bg-blue-600 hover:bg-blue-700 text-white px-12 py-5 rounded-full text-lg font-bold transition-all shadow-xl shadow-blue-600/30')
                ui.button('Learn More', on_click=lambda: ui.run_javascript('document.getElementById("about").scrollIntoView({behavior: "smooth"})')).props('outline color=white').classes('px-12 py-5 rounded-full text-lg font-bold border-white/30 text-white hover:bg-white/10')

    # About Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617]').props('id=about'):
        with ui.row().classes('w-full max-w-7xl gap-20 items-center'):
            with ui.column().classes('flex-1 gap-8'):
                ui.label('ABOUT PETRO-SYNC').classes('text-blue-500 font-bold tracking-widest text-sm')
                ui.label('Innovating Energy in Rwanda').classes('text-6xl font-bold text-white tracking-tight leading-tight')
                ui.label('Founded with a specific focus on meeting the escalating energy demands emerging from various sectors within Rwanda. Petro-Sync has swiftly positioned itself as a dedicated provider in the region.').classes('text-xl text-gray-400 leading-relaxed font-light')
                ui.label('Our services focus on agricultural, electricity generation, transport, and infrastructure sectors, anchored by a centralized operation based in Kigali city center.').classes('text-lg text-gray-500 leading-relaxed')
            
            with ui.grid(columns=2).classes('flex-1 gap-6').props('id=achievements'):
                stats = [
                    ('Retail Stations', '7', 'Serving communities'),
                    ('LPG Plant', '1', 'Clean energy solutions'),
                    ('Experience', '20+', 'Years in operation'),
                    ('Headquarters', 'Kigali', 'Makuza Plaza')
                ]
                for title, val, sub in stats:
                    with ui.column().classes('glass-card p-10 items-center text-center'):
                        ui.label(val).classes('text-4xl stat-value mb-2')
                        ui.label(title).classes('text-white font-bold text-sm uppercase tracking-widest')
                        ui.label(sub).classes('text-gray-600 text-xs mt-3')

    # Map Section
    with ui.column().classes('w-full items-center py-32 px-12 gap-12 bg-[#020617] border-t border-white/5').props('id=location'):
        ui.label('GLOBAL POSITION').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Our Presence in Rwanda').classes('text-5xl font-bold text-white mb-4')
        ui.label('Strategically located to serve the growing needs of our customers across the country.').classes('text-gray-400 text-center max-w-2xl mb-8 font-light')
        
        # Google Maps Embed for Kigali
        with ui.element('div').classes('w-full max-w-7xl map-container'):
            ui.html('''
                <iframe 
                    width="100%" 
                    height="500" 
                    frameborder="0" 
                    scrolling="no" 
                    marginheight="0" 
                    marginwidth="0" 
                    src="https://maps.google.com/maps?width=100%25&amp;height=500&amp;hl=en&amp;q=Kigali,%20Rwanda+(Petro-Sync%20Headquarters)&amp;t=&amp;z=14&amp;ie=UTF8&amp;iwloc=B&amp;output=embed">
                </iframe>
            ''')

    # Contact Info Section
    with ui.column().classes('w-full items-center py-32 px-12 gap-12 bg-[#020617] border-t border-white/5').props('id=contact'):
        ui.label('CONTACT US').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Connect With Our Team').classes('text-5xl font-bold text-white mb-8')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            contacts = [
                ('location_on', 'Head Office', '6th Floor, Tower B, YYUSA City Centre (Makuza Plaza), Kigali'),
                ('mail', 'Support Email', 'support@petrosync.rw'),
                ('phone', '24/7 Helpline', '+250 786 890758 / +250 788 855555')
            ]
            for icon, title, desc in contacts:
                with ui.column().classes('glass-card p-12 gap-5'):
                    ui.icon(icon, color='blue-500').classes('text-5xl')
                    ui.label(title).classes('text-2xl font-bold text-white')
                    ui.label(desc).classes('text-gray-400 leading-relaxed font-light')

    # Footer
    with ui.footer().classes('bg-[#020617] border-t border-white/5 py-20 px-12'):
        with ui.row().classes('w-full max-w-7xl mx-auto justify-between items-start gap-16'):
            with ui.column().classes('gap-6 flex-1'):
                ui.label('PETRO-SYNC').classes('text-3xl font-black text-white')
                ui.label('A leading regional oil marketing company in Africa. Committed to innovation, sustainability, and excellence in energy distribution.').classes('text-gray-500 text-base max-w-md leading-relaxed')
            
            with ui.column().classes('gap-5'):
                ui.label('Navigation').classes('text-white font-bold mb-2 uppercase tracking-widest text-xs opacity-50')
                ui.link('About Us', '#about').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Our Services', '#').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Locations', '#location').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
            
            with ui.column().classes('gap-5'):
                ui.label('Connect').classes('text-white font-bold mb-2 uppercase tracking-widest text-xs opacity-50')
                with ui.row().classes('gap-6'):
                    ui.icon('facebook', color='white').classes('text-2xl cursor-pointer hover:text-blue-500 transition-all')
                    ui.icon('twitter', color='white').classes('text-2xl cursor-pointer hover:text-blue-400 transition-all')
                    ui.icon('instagram', color='white').classes('text-2xl cursor-pointer hover:text-pink-500 transition-all')

        ui.separator().classes('my-16 bg-white/5')
        ui.label('© 2024 Petro-Sync Management Systems. All rights reserved.').classes('text-gray-600 text-xs text-center w-full uppercase tracking-widest')
