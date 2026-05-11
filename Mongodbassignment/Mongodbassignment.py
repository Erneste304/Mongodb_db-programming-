import reflex as rx
from rxconfig import config

# Import Pages
from frontend.pages.home import home_page
from frontend.pages.login import login_page
from frontend.pages.admin_dashboard import admin_dashboard_page
from frontend.pages.receptionist_dashboard import receptionist_dashboard_page
from frontend.pages.accountant_dashboard import accountant_dashboard_page
from frontend.pages.inventory_dashboard import inventory_dashboard_page

from frontend.base_state import State

app = rx.App()

# Routes
app.add_page(home_page, route="/")
app.add_page(login_page, route="/login")
app.add_page(admin_dashboard_page, route="/admin")
app.add_page(receptionist_dashboard_page, route="/receptionist")
app.add_page(accountant_dashboard_page, route="/accountant")
app.add_page(inventory_dashboard_page, route="/inventory")
