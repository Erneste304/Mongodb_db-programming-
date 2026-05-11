import reflex as rx
import requests
from frontend.utils.api_client import api_client
from frontend.base_state import State


class LoginState(State):
    """Login page state"""
    username: str = ""
    password: str = ""
    error_message: str = ""
    is_loading: bool = False
    
    def set_username(self, value: str):
        self.username = value
    
    def set_password(self, value: str):
        self.password = value
    
    async def handle_login(self):
        """Handle login form submission"""
        self.is_loading = True
        self.error_message = ""
        yield
        
        try:
            # Call the backend API to authenticate
            response = api_client.post(
                "/auth/login",
                data={
                    "username": self.username,
                    "password": self.password
                }
            )
            
            # Store the token
            api_client.set_token(response["access_token"])
            
            # Set authenticated state
            State.set_authenticated(response["user"])
            
            # Redirect based on role
            role = response["user"].get("role", "").lower()
            if "admin" in role:
                yield rx.redirect("/admin")
            elif "reception" in role:
                yield rx.redirect("/receptionist")
            elif "account" in role:
                yield rx.redirect("/accountant")
            elif "inventory" in role:
                yield rx.redirect("/inventory")
            else:
                yield rx.redirect("/dashboard")
        except requests.exceptions.RequestException as e:
            self.error_message = "Login failed. Please check your credentials."
        except Exception as e:
            self.error_message = f"Login failed: {str(e)}"
        
        self.is_loading = False
        yield


def login_page() -> rx.Component:
    """Professional Login Page"""
    return rx.box(
        rx.center(
            rx.vstack(
                rx.card(
                    rx.vstack(
                        # Header with Back Button
                        rx.hstack(
                            rx.link(
                                rx.button(
                                    rx.icon("arrow-left", size=16),
                                    "Home",
                                    variant="ghost",
                                    size="1",
                                    color_scheme="gray",
                                ),
                                href="/",
                            ),
                            rx.spacer(),
                            rx.image(src="/favicon.ico", width="32px", height="auto"),
                            width="100%",
                            align="center",
                        ),
                        
                        rx.vstack(
                            rx.heading(
                                "PETRO-SYNC", 
                                size="8", 
                                weight="bold",
                                letter_spacing="1px",
                                margin_top="1rem"
                            ),
                            rx.text(
                                "Mission Control Login", 
                                size="2", 
                                color="gray",
                                margin_bottom="2rem"
                            ),
                            align="center",
                            spacing="1",
                        ),
                        
                        # Form Fields
                        rx.vstack(
                            rx.vstack(
                                rx.text("Username", size="2", weight="medium"),
                                rx.input(
                                    placeholder="Operator ID",
                                    value=LoginState.username,
                                    on_change=LoginState.set_username,
                                    width="100%",
                                    variant="surface",
                                    size="3",
                                ),
                                width="100%",
                                align_items="start",
                                spacing="1",
                            ),
                            
                            rx.vstack(
                                rx.text("Password", size="2", weight="medium"),
                                rx.input(
                                    placeholder="••••••••",
                                    type="password",
                                    value=LoginState.password,
                                    on_change=LoginState.set_password,
                                    width="100%",
                                    variant="surface",
                                    size="3",
                                ),
                                width="100%",
                                align_items="start",
                                spacing="1",
                            ),
                            
                            rx.cond(
                                LoginState.error_message != "",
                                rx.callout.root(
                                    rx.callout.icon(rx.icon("info")),
                                    rx.callout.text(LoginState.error_message),
                                    color_scheme="red",
                                    size="1",
                                    width="100%",
                                )
                            ),
                            
                            rx.button(
                                "Authorize Access",
                                on_click=LoginState.handle_login,
                                loading=LoginState.is_loading,
                                width="100%",
                                size="3",
                                color_scheme="blue",
                                margin_top="1rem",
                            ),
                            
                            width="100%",
                            spacing="4"
                        ),
                        
                        width="100%",
                        spacing="6"
                    ),
                    width="420px",
                    padding="3rem",
                    class_name="glass-card",
                ),
                rx.text(
                    "© 2024 Secure Energy Management Node", 
                    size="1", 
                    color="gray",
                    margin_top="2rem"
                ),
                align="center",
            ),
            min_height="100vh",
        ),
        background="radial-gradient(circle at 20% 20%, rgba(59, 130, 246, 0.05) 0%, transparent 40%), radial-gradient(circle at 80% 80%, rgba(30, 58, 138, 0.05) 0%, transparent 40%), #f8fafc",
        width="100%",
    )
