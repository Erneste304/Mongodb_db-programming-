import reflex as rx
from typing import Optional, Dict, Any
from frontend.utils.api_client import api_client


class State(rx.State):
    """The base state for the app."""
    user: Optional[Dict[str, Any]] = None
    is_authenticated: bool = False

    def logout(self):
        """Log out the user."""
        self.user = None
        self.is_authenticated = False
        api_client.clear_token()
        return rx.redirect("/login")

    def set_authenticated(self, user_data: Dict[str, Any]):
        """Set the user as authenticated."""
        self.user = user_data
        self.is_authenticated = True
        
        # Redirect based on role
        role = user_data.get("role", "").lower()
        if role == "admin":
            return rx.redirect("/admin")
        elif role == "receptionist":
            return rx.redirect("/receptionist")
        elif role == "accountant":
            return rx.redirect("/accountant")
        elif role == "inventory_manager":
            return rx.redirect("/inventory")
        return rx.redirect("/")
