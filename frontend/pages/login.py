import reflex as rx
import requests
from frontend.utils.api_client import api_client


class LoginState(rx.State):
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
            
        except requests.exceptions.RequestException as e:
            self.error_message = "Login failed. Please check your credentials."
        except Exception as e:
            self.error_message = f"Login failed: {str(e)}"
        
        self.is_loading = False
        yield


def login_page() -> rx.Component:
    """Login page component"""
    return rx.center(
        rx.card(
            rx.vstack(
                rx.heading("Petroleum Station Management", size="2xl"),
                rx.text("Sign in to your account", color="gray"),
                
                rx.divider(),
                
                rx.vstack(
                    rx.text("Username", font_weight="medium"),
                    rx.input(
                        placeholder="Enter your username",
                        value=LoginState.username,
                        on_change=LoginState.set_username,
                        width="100%"
                    ),
                    
                    rx.text("Password", font_weight="medium"),
                    rx.input(
                        placeholder="Enter your password",
                        type="password",
                        value=LoginState.password,
                        on_change=LoginState.set_password,
                        width="100%"
                    ),
                    
                    rx.cond(
                        LoginState.error_message != "",
                        rx.text(
                            LoginState.error_message,
                            color="red",
                            font_size="sm"
                        )
                    ),
                    
                    rx.button(
                        "Sign In",
                        on_click=LoginState.handle_login,
                        loading=LoginState.is_loading,
                        color_scheme="blue",
                        width="100%",
                        size="3"
                    ),
                    
                    width="100%",
                    spacing="4"
                ),
                
                width="100%",
                spacing="6"
            ),
            width="400px",
            padding="2rem"
        ),
        min_height="100vh",
        background_color="#f8fafc"
    )
