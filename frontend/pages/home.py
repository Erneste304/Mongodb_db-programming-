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
            background: rgba(2, 6, 23, 0.6);
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

        .count-up {
            animation: countUp 2s ease-out forwards;
        }

        @keyframes countUp {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .faq-item {
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .faq-item:hover {
            background: rgba(255, 255, 255, 0.08);
            border-color: rgba(59, 130, 246, 0.6);
        }

        .faq-answer {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }

        .faq-answer.open {
            max-height: 500px;
        }

        .stat-card {
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }

        .stat-card:hover {
            transform: translateY(-8px);
            box-shadow: 0 20px 40px rgba(59, 130, 246, 0.3);
        }

        .pulse-animation {
            animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.7; }
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
            ui.link('Services', '#services').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Team', '#team').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Testimonials', '#testimonials').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Pricing', '#pricing').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('Gallery', '#gallery').classes('text-gray-300 font-medium no-underline nav-link')
            ui.link('News', '#blog').classes('text-gray-300 font-medium no-underline nav-link')
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
                    with ui.column().classes('glass-card stat-card p-10 items-center text-center'):
                        ui.label(val).classes('text-4xl stat-value mb-2 count-up')
                        ui.label(title).classes('text-white font-bold text-sm uppercase tracking-widest')
                        ui.label(sub).classes('text-gray-600 text-xs mt-3')

    # Services Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=services'):
        ui.label('OUR SERVICES').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Comprehensive Energy Solutions').classes('text-5xl font-bold text-white mb-4')
        ui.label('Delivering excellence across all sectors with tailored petroleum products and services.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            services = [
                ('local_gas_station', 'Retail Fuel Sales', 'Wide range of fuel types available at all our stations with competitive pricing and loyalty rewards.'),
                ('factory', 'Industrial Solutions', 'Bulk fuel supply for industrial operations, generators, and large-scale requirements with dedicated support.'),
                ('energy_savings_leaf', 'LPG Distribution', 'Clean energy alternative with safe distribution network serving residential and commercial sectors.'),
                ('directions_car', 'Fleet Management', 'Comprehensive fleet fuel solutions with corporate accounts and volume discounts.'),
                ('card_giftcard', 'Loyalty Program', 'Exclusive membership benefits, points accumulation, and tier-based rewards for regular customers.'),
                ('analytics', 'Analytics & Reporting', 'Real-time inventory tracking, sales reports, and business intelligence for partners.')
            ]
            for icon, title, desc in services:
                with ui.column().classes('glass-card p-8 gap-4 items-start'):
                    ui.icon(icon, color='blue-500').classes('text-4xl')
                    ui.label(title).classes('text-lg font-bold text-white')
                    ui.label(desc).classes('text-sm text-gray-400 leading-relaxed')

    # Team Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=team'):
        ui.label('OUR LEADERSHIP').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Meet Our Expert Team').classes('text-5xl font-bold text-white mb-4')
        ui.label('Experienced professionals committed to delivering excellence in energy distribution.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=4).classes('w-full max-w-7xl gap-8'):
            team_members = [
                ('John Kagame', 'General Manager', 'Strategic leadership & operations oversight'),
                ('Alice Mukeshimana', 'Operations Manager', 'Daily operations & station management'),
                ('Peter Habimana', 'Finance Director', 'Financial planning & budget management'),
                ('Marie Nyirahabimana', 'Sales & Marketing', 'Customer relations & market expansion'),
                ('David Ntambara', 'Technical Manager', 'Maintenance & equipment management'),
                ('Patricia Uwase', 'HR Manager', 'Human resources & staff development'),
                ('James Murekezi', 'Inventory Chief', 'Stock management & supply chain'),
                ('Sophie Isingizini', 'Customer Service Lead', 'Client support & satisfaction')
            ]
            for name, position, desc in team_members:
                with ui.column().classes('glass-card p-8 gap-4 items-center text-center hover:scale-105 transition-transform'):
                    ui.icon('person', color='blue-500').classes('text-5xl')
                    ui.label(name).classes('text-lg font-bold text-white')
                    ui.label(position).classes('text-sm text-blue-400 font-semibold')
                    ui.label(desc).classes('text-xs text-gray-400 leading-relaxed')

    # Testimonials Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=testimonials'):
        ui.label('CUSTOMER TESTIMONIALS').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('What Our Clients Say').classes('text-5xl font-bold text-white mb-4')
        ui.label('Real feedback from satisfied customers across Rwanda.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            testimonials = [
                ('⭐⭐⭐⭐⭐', '"Excellent service and reliable fuel supply. Petro-Sync has been our trusted partner for fleet operations."', 'Amani Transport Ltd', 'Rwanda'),
                ('⭐⭐⭐⭐⭐', '"The loyalty program is fantastic! I save significantly on every purchase and the service is impeccable."', 'Jean Ndayisaba', 'Kigali'),
                ('⭐⭐⭐⭐⭐', '"Professional team, competitive pricing, and fastest delivery in the region. Highly recommended!"', 'Rwanda Manufacturing Co.', 'Muhanga'),
                ('⭐⭐⭐⭐⭐', '"Outstanding customer service. They go above and beyond to meet our bulk fuel needs."', 'Grace Habimana', 'Gisenyi'),
                ('⭐⭐⭐⭐⭐', '"Best LPG distribution service in the country. Safe, reliable, and always on time."', 'Energy Solutions Ltd', 'Kigali'),
                ('⭐⭐⭐⭐⭐', '"Petro-Sync makes fueling my business easy. Great staff and honest dealings!"', 'Patrick Mukamana', 'Butare')
            ]
            for rating, comment, author, location in testimonials:
                with ui.column().classes('glass-card p-8 gap-4'):
                    ui.label(rating).classes('text-2xl')
                    ui.label(comment).classes('text-sm text-gray-300 italic leading-relaxed')
                    ui.separator().classes('bg-white/10')
                    ui.label(author).classes('text-white font-bold')
                    ui.label(location).classes('text-xs text-gray-500')

    # FAQ Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=faq'):
        ui.label('FREQUENTLY ASKED QUESTIONS').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Common Questions Answered').classes('text-5xl font-bold text-white mb-4')
        ui.label('Find quick answers to your questions about our services.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.column().classes('w-full max-w-4xl gap-6'):
            faqs = [
                ('What fuel types do you offer?', 'We provide Petrol, Diesel, Super, and LPG (liquefied petroleum gas) at all our stations with premium quality standards.'),
                ('How does the loyalty program work?', 'Earn 1 point per 1,000 RWF spent. Accumulate points to unlock discounts (2.5%-10%) based on tier levels.'),
                ('Are bulk orders available?', 'Yes! We offer volume discounts starting from 500 liters. Contact our sales team for custom corporate packages.'),
                ('What are your opening hours?', 'Most stations operate 6:00 AM - 10:00 PM daily. Contact your nearest station for specific hours.'),
                ('Do you offer home/business delivery?', 'Yes, we provide delivery service for LPG and bulk orders. Call +250 786 890758 to arrange.'),
                ('How can I become a partner?', 'We welcome wholesalers and retailers. Email support@petrosync.rw or visit our head office in Kigali.')
            ]
            for question, answer in faqs:
                with ui.column().classes('glass-card p-8 gap-4'):
                    with ui.row().classes('items-start gap-4'):
                        ui.icon('help_outline', color='blue-500').classes('text-2xl mt-1 flex-shrink-0')
                        with ui.column().classes('gap-2'):
                            ui.label(question).classes('text-white font-bold text-base')
                            ui.label(answer).classes('text-gray-400 text-sm leading-relaxed')

    # Blog/News Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=blog'):
        ui.label('LATEST NEWS').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Industry Updates & Announcements').classes('text-5xl font-bold text-white mb-4')
        ui.label('Stay informed with the latest from Petro-Sync and the energy sector.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            blogs = [
                ('May 2024', 'New Station Opening in Muhanga', 'We are excited to announce the opening of our newest retail station in Muhanga City. This expansion brings our total network to 8 stations.'),
                ('April 2024', 'LPG Safety Campaign Launch', 'Our comprehensive safety awareness program kicks off this month, reaching households and businesses across Kigali and surrounding regions.'),
                ('March 2024', 'Record Quarterly Performance', 'Petro-Sync records its highest quarterly sales with 15% growth. Our loyalty program members increased by 30%.'),
                ('February 2024', 'Partnership with Green Energy Initiative', 'We partner with environmental organizations to promote sustainable fuel alternatives and reduce carbon footprint.'),
                ('January 2024', 'Mobile App Launch Coming Soon', 'Our new mobile application for fuel ordering and loyalty tracking will be available next month on iOS and Android.'),
                ('December 2023', 'Year-End Customer Appreciation Event', 'Thank you for your continued support! Join our year-end celebration with exclusive discounts and giveaways.')
            ]
            for date, title, content in blogs:
                with ui.column().classes('glass-card p-8 gap-4 hover:border-blue-400 transition-colors'):
                    ui.label(date).classes('text-xs text-blue-400 font-semibold uppercase')
                    ui.label(title).classes('text-lg font-bold text-white')
                    ui.label(content).classes('text-sm text-gray-400 leading-relaxed')
                    ui.button('Read More', on_click=lambda: ui.notify('Full article feature coming soon!')).props('flat color=blue-600').classes('text-xs mt-2')

    # Pricing Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=pricing'):
        ui.label('PRICING PLANS').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Flexible Packages for Every Need').classes('text-5xl font-bold text-white mb-4')
        ui.label('Choose the plan that best fits your fuel requirements.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            pricing_plans = [
                ('Personal', 'For individuals', 'RWF 500-5,000/visit', ['Competitive pricing', 'Loyalty rewards', 'Weekly updates'], False),
                ('Business', 'For small businesses', 'RWF 50,000-500,000/month', ['Volume discounts', 'Dedicated support', 'Monthly reports', 'Priority service'], True),
                ('Enterprise', 'For large operations', 'Custom pricing', ['Custom contracts', '24/7 support', 'Analytics dashboard', 'Special rates', 'Free delivery'])
            ]
            for plan_name, desc, price, features, popular in pricing_plans:
                with ui.column().classes(f'glass-card p-8 gap-6 items-start {"border-2 border-blue-500" if popular else ""}').classes('relative'):
                    if popular:
                        ui.label('MOST POPULAR').classes('absolute top-0 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-blue-600 text-white px-4 py-1 rounded-full text-xs font-bold')
                    ui.label(plan_name).classes('text-2xl font-bold text-white')
                    ui.label(desc).classes('text-sm text-gray-400')
                    ui.label(price).classes('text-3xl font-bold text-blue-400')
                    with ui.column().classes('gap-3 w-full'):
                        for feature in features:
                            with ui.row().classes('gap-3 items-center'):
                                ui.icon('check_circle', color='blue-500').classes('text-lg flex-shrink-0')
                                ui.label(feature).classes('text-gray-300 text-sm')
                    ui.button('Get Started', on_click=lambda: ui.notify('Contact our sales team!')).props(f'color={"blue-600" if popular else "gray"}').classes('w-full')

    # Gallery Section
    with ui.column().classes('w-full items-center py-40 px-12 gap-16 bg-[#020617] border-t border-white/5').props('id=gallery'):
        ui.label('GALLERY').classes('text-blue-500 font-bold tracking-widest text-sm')
        ui.label('Our Facilities & Operations').classes('text-5xl font-bold text-white mb-4')
        ui.label('Take a visual tour of our stations and facilities across Rwanda.').classes('text-gray-400 text-center max-w-2xl mb-12 font-light')
        
        with ui.grid(columns=3).classes('w-full max-w-7xl gap-8'):
            gallery_items = [
                ('🏪', 'Kigali Central Station', 'Our flagship station in the heart of Kigali with modern facilities'),
                ('🏭', 'LPG Plant', 'State-of-the-art LPG distribution facility with safety standards'),
                ('🛢️', 'Fuel Storage Tanks', 'Massive capacity storage ensuring consistent supply'),
                ('👷', 'Skilled Workforce', 'Our dedicated team trained in safety and service excellence'),
                ('📊', 'Control Center', 'Advanced monitoring system for operations and inventory'),
                ('🌳', 'Eco-Friendly Station', 'Green initiative with sustainable practices at all stations')
            ]
            for emoji, title, desc in gallery_items:
                with ui.column().classes('glass-card p-12 gap-4 items-center text-center hover:scale-105 transition-transform'):
                    ui.label(emoji).classes('text-6xl')
                    ui.label(title).classes('text-lg font-bold text-white')
                    ui.label(desc).classes('text-sm text-gray-400 leading-relaxed')

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
                ui.link('Our Services', '#services').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Our Team', '#team').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Testimonials', '#testimonials').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Pricing', '#pricing').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
                ui.link('Gallery', '#gallery').classes('text-gray-500 text-sm no-underline hover:text-white transition-colors')
            
            with ui.column().classes('gap-5'):
                ui.label('Connect').classes('text-white font-bold mb-2 uppercase tracking-widest text-xs opacity-50')
                with ui.row().classes('gap-6'):
                    ui.icon('facebook', color='white').classes('text-2xl cursor-pointer hover:text-blue-500 transition-all')
                    ui.icon('twitter', color='white').classes('text-2xl cursor-pointer hover:text-blue-400 transition-all')
                    ui.icon('instagram', color='white').classes('text-2xl cursor-pointer hover:text-pink-500 transition-all')

        ui.separator().classes('my-16 bg-white/5')
        ui.label('© 2024 Petro-Sync Management Systems. All rights reserved.').classes('text-gray-600 text-xs text-center w-full uppercase tracking-widest')
