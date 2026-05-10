import reflex as rx
import requests
from frontend.utils.api_client import api_client


class AdminDashboardState(rx.State):
    """Admin dashboard state"""
    staff_members: list[dict] = []
    pending_approvals: list[dict] = []
    selected_tab: str = "staff"
    
    # Fuel pricing state
    fuel_pricing: list[dict] = []
    partner_agreements: list[dict] = []
    
    # System settings state
    system_settings: dict = {}
    
    def set_selected_tab(self, tab: str):
        self.selected_tab = tab
    
    async def load_staff(self):
        """Load staff members from backend API"""
        try:
            users = api_client.get("/users/")
            self.staff_members = [
                {
                    "id": user["id"],
                    "name": user.get("full_name", user["username"]),
                    "role": user["role"],
                    "employee_id": user.get("employee_id", ""),
                    "is_active": user["is_active"],
                    "permissions": []  # Permissions would be fetched separately
                }
                for user in users
            ]
        except Exception as e:
            # Fallback to mock data if API fails
            self.staff_members = [
                {
                    "id": "1",
                    "name": "Jean Claude Uwimana",
                    "role": "Receptionist",
                    "employee_id": "PS-2024-0045",
                    "is_active": True,
                    "permissions": [
                        {"id": "1", "name": "Sales Module", "enabled": True, "requires_approval": False},
                        {"id": "2", "name": "Inventory View", "enabled": True, "requires_approval": False},
                        {"id": "3", "name": "Financial Reports", "enabled": False, "requires_approval": True},
                        {"id": "4", "name": "Customer Management", "enabled": True, "requires_approval": False}
                    ]
                },
                {
                    "id": "2",
                    "name": "Marie Claire Ingabire",
                    "role": "Inventory Manager",
                    "employee_id": "PS-2024-0046",
                    "is_active": True,
                    "permissions": [
                        {"id": "5", "name": "Inventory View", "enabled": True, "requires_approval": False},
                        {"id": "6", "name": "Inventory Update", "enabled": True, "requires_approval": True},
                        {"id": "7", "name": "Delivery Management", "enabled": True, "requires_approval": False}
                    ]
                }
            ]
    
    async def load_approvals(self):
        """Load pending approvals from backend API"""
        try:
            approvals = api_client.get("/approvals/pending")
            self.pending_approvals = [
                {
                    "id": approval["id"],
                    "type": approval["request_type"],
                    "requester": approval.get("requester_name", "Unknown"),
                    "reason": approval["reason"],
                    "amount": approval.get("request_data", {}).get("amount", ""),
                    "status": approval["status"],
                    "requested_at": approval["requested_at"]
                }
                for approval in approvals
            ]
        except Exception as e:
            # Fallback to mock data if API fails
            self.pending_approvals = [
                {
                    "id": "1",
                    "type": "Large Payment",
                    "requester": "Accountant",
                    "reason": "Monthly fuel supplier payment - Total Rwanda",
                    "amount": "2,500,000 RWF",
                    "status": "pending",
                    "requested_at": "2024-05-10 14:30"
                },
                {
                    "id": "2",
                    "type": "Void Transaction",
                    "requester": "Receptionist",
                    "reason": "Customer complaint - incorrect fuel amount",
                    "transaction_id": "TXN-2024-0123",
                    "status": "pending",
                    "requested_at": "2024-05-10 15:45"
                }
            ]
    
    def on_mount(self):
        """Load data when component mounts"""
        self.load_staff()
        self.load_approvals()


def staff_card(staff: dict) -> rx.Component:
    """Staff member card with toggle controls"""
    return rx.card(
        rx.vstack(
            # Header
            rx.hstack(
                rx.avatar(
                    name=staff["name"],
                    size="lg"
                ),
                rx.vstack(
                    rx.heading(staff["name"], size="md"),
                    rx.text(f"{staff['role']} - ID: {staff['employee_id']}", color="gray"),
                    align_items="start",
                    spacing="0"
                ),
                rx.spacer(),
                rx.switch(
                    is_checked=staff["is_active"],
                    size="lg",
                    color_scheme="green" if staff["is_active"] else "red"
                ),
                rx.badge(
                    "Active" if staff["is_active"] else "Disabled",
                    color_scheme="green" if staff["is_active"] else "red"
                ),
                width="100%",
                justify="between"
            ),
            
            rx.divider(),
            
            # Permissions Section
            rx.heading("Access Permissions", size="sm"),
            rx.vstack(
                rx.foreach(
                    staff["permissions"],
                    lambda perm: rx.hstack(
                        rx.text(perm["name"], width="60%"),
                        rx.switch(
                            is_checked=perm["enabled"],
                            size="sm",
                            color_scheme="green" if perm["enabled"] else "red"
                        ),
                        rx.badge(
                            "Approval Required" if perm["requires_approval"] else "Direct",
                            color_scheme="orange" if perm["requires_approval"] else "blue",
                            font_size="xs"
                        ),
                        justify="between",
                        width="100%",
                        padding="0.5rem",
                        border_bottom="1px solid #e2e8f0"
                    )
                ),
                width="100%",
                spacing="0"
            ),
            
            rx.divider(),
            
            # Action Buttons
            rx.hstack(
                rx.button(
                    "View Activity",
                    variant="outline"
                ),
                rx.button(
                    "Edit Details",
                    variant="outline"
                ),
                rx.button(
                    "Deactivate",
                    color_scheme="red",
                    variant="ghost"
                ),
                spacing="2"
            ),
            
            width="100%",
            spacing="4"
        ),
        width="100%",
        padding="1.5rem",
        margin_bottom="1rem"
    )


def approval_queue_item(request: dict) -> rx.Component:
    """Single approval request item"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(request["type"], color_scheme="blue"),
                rx.badge(request["status"], color_scheme="yellow"),
                rx.text(request["requested_at"], color="gray", font_size="sm"),
                justify="between",
                width="100%"
            ),
            
            rx.text(f"Requester: {request['requester']}", font_weight="bold"),
            rx.text(f"Reason: {request['reason']}"),
            
            rx.divider(),
            
            # Request Details
            rx.cond(
                request.get("amount"),
                rx.hstack(
                    rx.text("Amount:", font_weight="medium"),
                    rx.text(request["amount"]),
                    justify="between"
                )
            ),
            rx.cond(
                request.get("transaction_id"),
                rx.hstack(
                    rx.text("Transaction ID:", font_weight="medium"),
                    rx.text(request["transaction_id"]),
                    justify="between"
                )
            ),
            
            rx.divider(),
            
            # Approval Actions
            rx.hstack(
                rx.button(
                    "Approve",
                    color_scheme="green",
                    size="sm"
                ),
                rx.button(
                    "Reject",
                    color_scheme="red",
                    variant="outline",
                    size="sm"
                ),
                rx.button(
                    "Request More Info",
                    variant="ghost",
                    size="sm"
                ),
                spacing="2"
            ),
            
            width="100%",
            spacing="3"
        ),
        padding="1rem",
        margin_bottom="1rem"
    )


def admin_dashboard_page() -> rx.Component:
    """Main admin dashboard"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Admin Dashboard", size="2xl"),
                rx.spacer(),
                rx.button(
                    "Logout",
                    on_click=State.logout,
                    variant="outline"
                ),
                width="100%",
                justify="between"
            ),
            
            # Stats Cards
            rx.hstack(
                rx.card(
                    rx.vstack(
                        rx.text("Active Staff", color="gray"),
                        rx.heading("12", size="3xl"),
                        rx.text("↑ 2 from last month", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Pending Approvals", color="gray"),
                        rx.heading("5", size="3xl"),
                        rx.text("↓ 3 from yesterday", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Today's Sales", color="gray"),
                        rx.heading("3,450,000", size="3xl"),
                        rx.text("RWF ↑ 12% from average", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                spacing="4",
                width="100%"
            ),
            
            rx.divider(),
            
            # Tabs
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Staff Management", value="staff"),
                    rx.tabs.trigger("Approval Queue", value="approvals"),
                    rx.tabs.trigger("Fuel Pricing", value="pricing"),
                    rx.tabs.trigger("System Settings", value="settings"),
                    rx.tabs.trigger("Audit Logs", value="audit"),
                    rx.tabs.trigger("Reports", value="reports"),
                ),
                rx.tabs.content(
                    # Staff Management Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Staff Management", size="lg"),
                            rx.spacer(),
                            rx.button(
                                "+ Add New Staff",
                                color_scheme="blue"
                            ),
                            width="100%"
                        ),
                        rx.foreach(
                            AdminDashboardState.staff_members,
                            staff_card
                        ),
                        width="100%"
                    ),
                    value="staff"
                ),
                rx.tabs.content(
                    # Approval Queue Tab
                    rx.vstack(
                        rx.heading("Pending Approvals", size="lg"),
                        rx.foreach(
                            AdminDashboardState.pending_approvals,
                            approval_queue_item
                        ),
                        width="100%"
                    ),
                    value="approvals"
                ),
                rx.tabs.content(
                    # Audit Logs Tab
                    rx.vstack(
                        rx.heading("Audit Trail", size="lg"),
                        rx.alert(
                            rx.alert_icon(),
                            rx.alert_title("Note: You cannot see your own actions in this log"),
                            rx.alert_description("This ensures accountability and prevents self-manipulation of records."),
                            status="info"
                        ),
                        rx.text("Audit logs will be displayed here"),
                        width="100%"
                    ),
                    value="audit"
                ),
                rx.tabs.content(
                    # Fuel Pricing Tab (Superadmin)
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Fuel Pricing Management", size="lg"),
                            rx.badge("Superadmin Only", color_scheme="red"),
                            rx.spacer(),
                            rx.button("Add New Pricing", color_scheme="blue"),
                            rx.button("Manage Partners", variant="outline"),
                            width="100%"
                        ),
                        rx.divider(),
                        rx.text("Set fuel prices based on RURA guidelines"),
                        rx.card(
                            rx.vstack(
                                rx.heading("Current Fuel Prices", size="md"),
                                rx.hstack(
                                    rx.text("Petrol (Retail):", font_weight="bold"),
                                    rx.text("1,650 RWF/liter"),
                                    rx.button("Update", size="sm", variant="outline"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Diesel (Retail):", font_weight="bold"),
                                    rx.text("1,550 RWF/liter"),
                                    rx.button("Update", size="sm", variant="outline"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Kerosene:", font_weight="bold"),
                                    rx.text("1,200 RWF/liter"),
                                    rx.button("Update", size="sm", variant="outline"),
                                    justify="between",
                                    width="100%"
                                ),
                                width="100%",
                                spacing="3"
                            ),
                            padding="1.5rem"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Partner Agreements", size="md"),
                                rx.text("Manage supplier contracts and commissions"),
                                rx.button("View All Agreements", variant="outline"),
                                width="100%",
                                spacing="2"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="pricing"
                ),
                rx.tabs.content(
                    # System Settings Tab (Superadmin)
                    rx.vstack(
                        rx.hstack(
                            rx.heading("System Settings", size="lg"),
                            rx.badge("Superadmin Only", color_scheme="red"),
                            rx.spacer(),
                            rx.button("Save Changes", color_scheme="green"),
                            width="100%"
                        ),
                        rx.divider(),
                        rx.text("Configure system parameters and business rules"),
                        rx.card(
                            rx.vstack(
                                rx.heading("Station Information", size="md"),
                                rx.hstack(
                                    rx.text("Station Name:", width="200px"),
                                    rx.input(value="Petroleum Station", width="300px")
                                ),
                                rx.hstack(
                                    rx.text("Station Code:", width="200px"),
                                    rx.input(value="PS-001", width="300px")
                                ),
                                rx.hstack(
                                    rx.text("TIN Number:", width="200px"),
                                    rx.input(placeholder="Enter TIN", width="300px")
                                ),
                                width="100%",
                                spacing="3"
                            ),
                            padding="1.5rem"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Business Rules", size="md"),
                                rx.hstack(
                                    rx.text("Large Payment Threshold:", width="200px"),
                                    rx.input(value="1000000", width="200px"),
                                    rx.text("RWF")
                                ),
                                rx.hstack(
                                    rx.text("Low Fuel Alert (%):", width="200px"),
                                    rx.input(value="20", width="200px"),
                                    rx.text("%")
                                ),
                                rx.hstack(
                                    rx.text("Critical Fuel Alert (%):", width="200px"),
                                    rx.input(value="10", width="200px"),
                                    rx.text("%")
                                ),
                                width="100%",
                                spacing="3"
                            ),
                            padding="1.5rem"
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Approval Settings", size="md"),
                                rx.hstack(
                                    rx.text("Approval Timeout (hours):", width="200px"),
                                    rx.input(value="24", width="200px")
                                ),
                                rx.hstack(
                                    rx.text("Transaction Void Requires Approval:", width="200px"),
                                    rx.switch(is_checked=True)
                                ),
                                width="100%",
                                spacing="3"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="settings"
                ),
                rx.tabs.content(
                    # Reports Tab
                    rx.heading("Reports", size="lg"),
                    value="reports"
                ),
                on_change=AdminDashboardState.set_selected_tab,
                value=AdminDashboardState.selected_tab
            ),
            
            width="100%",
            max_width="1400px",
            padding="2rem",
            spacing="6"
        ),
        width="100%",
        background_color="#f8fafc"
    )
