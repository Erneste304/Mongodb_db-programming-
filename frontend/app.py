import reflex as rx
from frontend.pages.admin_dashboard import admin_dashboard_page
from frontend.pages.login import login_page


class State(rx.State):
    """Global application state"""
    current_user: dict = {}
    is_authenticated: bool = False
    current_page: str = "login"
    
    def set_authenticated(self, user: dict):
        self.current_user = user
        self.is_authenticated = True
        self.current_page = "dashboard"
    
    def logout(self):
        self.current_user = {}
        self.is_authenticated = False
        self.current_page = "login"
    
    def navigate_to(self, page: str):
        self.current_page = page


def index() -> rx.Component:
    """Main app component"""
    return rx.box(
        rx.cond(
            State.is_authenticated,
            admin_dashboard_page(),
            login_page()
        ),
        width="100%",
        min_height="100vh"
    )


app = rx.App(
    style=rx.style(
        background_color="#f8fafc",
        color="#0f172a",
        font_family="system-ui, -apple-system, sans-serif"
    )
)
app.add_page(index, route="/", title="Petroleum Station Management")
