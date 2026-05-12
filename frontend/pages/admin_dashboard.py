import reflex as rx
import requests
from frontend.utils.api_client import api_client
from frontend.base_state import State

from frontend.base_state import State

# Final attempt at finding the correct Base for 0.9.x
from reflex_base.components.props import PropsBase as Base


class Permission(Base):
    id: str = ""
    name: str = ""
    enabled: bool = False
    requires_approval: bool = False


class StaffMember(Base):
    id: str = ""
    name: str = ""
    role: str = ""
    employee_id: str = ""
    is_active: bool = False
    permissions: list[Permission] = []


class AdminDashboardState(State):
    """Admin dashboard state"""
    # Visitor and Audit state
    visitor_logs: list[dict] = []
    audit_logs: list[dict] = []
    
    # UI State
    selected_tab: str = "staff"
    staff_members: list[StaffMember] = []
    pending_approvals: list[dict] = []
    
    # System settings state
    system_settings: dict = {}
    
    # Operations state
    station_status: str = "closed"
    fuel_deliveries: list[dict] = []
    inventory_levels: list[dict] = []
    complaints: list[dict] = []
    safety_checks: list[dict] = []
    pump_calibrations: list[dict] = []
    timesheets: list[dict] = []
    
    # Opening/closing procedures
    opening_cash: float = 0
    closing_cash: float = 0
    pump_readings: list[dict] = []
    
    async def load_operations_data(self):
        """Load operations data"""
        try:
            # Load fuel deliveries
            self.fuel_deliveries = api_client.get("/inventory/deliveries")
            
            # Load inventory levels
            self.inventory_levels = api_client.get("/inventory/tanks")
            
            # Load complaints
            self.complaints = api_client.get("/complaints/complaints")
            
            # Load safety checks
            self.safety_checks = api_client.get("/safety/checks")
            
            # Load pump calibrations
            self.pump_calibrations = api_client.get("/staff_management/pump-calibrations")
            
            # Load timesheets
            self.timesheets = api_client.get("/staff_management/timesheets")
            
        except Exception as e:
            # Fallback mock data
            self.fuel_deliveries = []
            self.inventory_levels = []
            self.complaints = []
            self.safety_checks = []
            self.pump_calibrations = []
            self.timesheets = []
    
    async def open_station(self):
        """Open station procedure"""
        try:
            api_client.post("/operations/open-station", {"opening_cash": self.opening_cash})
            self.station_status = "open"
            rx.toast.success("Station opened successfully")
        except Exception as e:
            rx.toast.error(f"Failed to open station: {str(e)}")
    
    async def close_station(self):
        """Close station procedure"""
        try:
            api_client.post("/operations/close-station", {"closing_cash": self.closing_cash})
            self.station_status = "closed"
            rx.toast.success("Station closed successfully")
        except Exception as e:
            rx.toast.error(f"Failed to close station: {str(e)}")
    
    def set_selected_tab(self, tab: str):
        self.selected_tab = tab
    
    async def toggle_staff_active(self, staff_id: str, current_status: bool):
        """Toggle staff active status"""
        try:
            api_client.patch(f"/users/{staff_id}", {"is_active": not current_status})
            await self.load_staff()
            rx.toast.success(f"Staff account {'disabled' if current_status else 'enabled'}")
        except Exception as e:
            rx.toast.error(f"Failed to update status: {str(e)}")

    async def toggle_permission(self, staff_id: str, permission_id: str, current_state: bool):
        """Toggle staff permission"""
        try:
            api_client.post(f"/users/{staff_id}/permissions/toggle", {
                "permission_id": permission_id,
                "enabled": not current_state
            })
            await self.load_staff()
            rx.toast.success("Permission updated")
        except Exception as e:
            rx.toast.error(f"Failed to update permission: {str(e)}")

    async def load_audit_logs(self):
        """Load audit logs (Blind-spot rule applied by backend)"""
        try:
            self.audit_logs = api_client.get("/audit/logs")
        except Exception as e:
            self.audit_logs = []

    async def load_visitor_logs(self):
        """Load visitor sign-in logs"""
        try:
            self.visitor_logs = api_client.get("/visitors/log")
        except Exception as e:
            self.visitor_logs = []
    
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
        self.load_audit_logs()
        self.load_visitor_logs()
        self.load_operations_data()


def staff_card(staff: StaffMember) -> rx.Component:
    """Premium staff member card"""
    return rx.card(
        rx.vstack(
            # Header
            rx.hstack(
                rx.avatar(
                    fallback=staff.name[0:2].upper(),
                    size="4",
                    color_scheme="blue",
                    radius="full",
                ),
                rx.vstack(
                    rx.heading(staff.name, size="4", weight="bold"),
                    rx.text(f"{staff.role} | ID: {staff.employee_id}", size="1", color="gray"),
                    align_items="start",
                    spacing="0",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.switch(
                        is_checked=staff.is_active,
                        on_change=lambda _: AdminDashboardState.toggle_staff_active(staff.id, staff.is_active),
                        size="3",
                        color_scheme=rx.cond(staff.is_active, "green", "red"),
                    ),
                    rx.badge(
                        rx.cond(staff.is_active, "ACTIVE", "INACTIVE"),
                        color_scheme=rx.cond(staff.is_active, "green", "red"),
                        variant="soft",
                        class_name="status-badge",
                    ),
                    spacing="3",
                    align="center",
                ),
                width="100%",
                align="center",
            ),
            
            rx.divider(),
            
            # Permissions Section
            rx.heading("Access Permissions", size="2"),
            rx.vstack(
                rx.foreach(
                    staff.permissions,
                    lambda perm: rx.hstack(
                        rx.text(perm.name, width="60%"),
                        rx.switch(
                            is_checked=perm.enabled,
                            on_change=lambda _: AdminDashboardState.toggle_permission(
                                staff.id, perm.id, perm.enabled
                            ),
                            size="2",
                            color_scheme=rx.cond(perm.enabled, "green", "red")
                        ),
                        rx.badge(
                            rx.cond(perm.requires_approval, "Approval Required", "Direct"),
                            color_scheme=rx.cond(perm.requires_approval, "orange", "blue"),
                            font_size="1"
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
        class_name="glass-card",
        margin_bottom="1rem"
    )


def approval_queue_item(request: dict) -> rx.Component:
    """Single approval request item"""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.badge(request["type"], color_scheme="blue"),
                rx.badge(request["status"], color_scheme="yellow"),
                rx.text(request["requested_at"], color="gray", font_size="2"),
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
                    size="2"
                ),
                rx.button(
                    "Reject",
                    color_scheme="red",
                    variant="outline",
                    size="2"
                ),
                rx.button(
                    "Request More Info",
                    variant="ghost",
                    size="2"
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
    """Premium Admin Dashboard"""
    return rx.box(
        # Navigation Bar
        rx.box(
            rx.hstack(
                rx.vstack(
                    rx.heading("COMMAND CENTER", size="7", weight="bold", letter_spacing="1px"),
                    rx.text("Petroleum Management Mission Control", size="2", color="gray"),
                    spacing="0",
                    align_items="start",
                ),
                rx.spacer(),
                rx.hstack(
                    rx.badge("System Secure", color_scheme="green", variant="surface"),
                    rx.badge("EBM Active", color_scheme="blue", variant="surface"),
                    rx.button(
                        "Logout", 
                        variant="soft", 
                        color_scheme="red",
                        on_click=State.logout,
                    ),
                    spacing="4",
                ),
                width="100%",
                max_width="1400px",
                margin="0 auto",
                align="center",
            ),
            class_name="app-header",
            width="100%",
        ),
        
        # Main Content
        rx.box(
            rx.vstack(
                # Stats Grid
                rx.grid(
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("users", size=20, color="gray"),
                                rx.text("Active Personnel", size="2", color="gray"),
                                spacing="2",
                            ),
                            rx.text("12", class_name="stats-value"),
                            rx.text("2 pending approval", color="orange", size="2"),
                            align_items="start",
                        ),
                        class_name="glass-card",
                        padding="2rem",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("triangle_alert", size=20, color="gray"),
                                rx.text("System Anomalies", size="2", color="gray"),
                                spacing="2",
                            ),
                            rx.text("2", class_name="stats-value", color="red"),
                            rx.text("Theft/Leakage detected", color="red", size="2"),
                            align_items="start",
                        ),
                        class_name="glass-card",
                        padding="2rem",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("banknote", size=20, color="gray"),
                                rx.text("Today's Revenue", size="2", color="gray"),
                                spacing="2",
                            ),
                            rx.text("3,450,000", class_name="stats-value"),
                            rx.text("RWF (100% EBM Verified)", color="green", size="2"),
                            align_items="start",
                        ),
                        class_name="glass-card",
                        padding="2rem",
                    ),
                    rx.card(
                        rx.vstack(
                            rx.hstack(
                                rx.icon("map_pin", size=20, color="gray"),
                                rx.text("Current Visitors", size="2", color="gray"),
                                spacing="2",
                            ),
                            rx.text("3", class_name="stats-value"),
                            rx.text("Tankers on-site", color="blue", size="2"),
                            align_items="start",
                        ),
                        class_name="glass-card",
                        padding="2rem",
                    ),
                    columns="4",
                    spacing="6",
                    width="100%",
                    margin_bottom="2rem",
                ),
                
                # Space for Tabs
                rx.divider(),
            
            # Tabs
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Staff Management", value="staff"),
                    rx.tabs.trigger("Approval Queue", value="approvals"),
                    rx.tabs.trigger("Fuel Pricing", value="pricing"),
                    rx.tabs.trigger("System Settings", value="settings"),
                    rx.tabs.trigger("Visitor Logs", value="visitors"),
                    rx.tabs.trigger("Audit Logs", value="audit"),
                    rx.tabs.trigger("Reports", value="reports"),
                    rx.tabs.trigger("Operations", value="operations"),
                    rx.tabs.trigger("Opening/Closing", value="procedures"),
                ),
                rx.tabs.content(
                    # Staff Management Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Staff Management", size="6"),
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
                        rx.heading("Pending Approvals", size="6"),
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
                        rx.foreach(
                            AdminDashboardState.audit_logs,
                            lambda log: rx.card(
                                rx.hstack(
                                    rx.vstack(
                                        rx.text(log["action"], font_weight="bold"),
                                        rx.text(f"Resource: {log['resource_type']} ({log['resource_id']})", font_size="2"),
                                        align_items="start"
                                    ),
                                    rx.spacer(),
                                    rx.vstack(
                                        rx.text(log["timestamp"], font_size="1", color="gray"),
                                        rx.badge(log.get("actor_name", "Staff"), color_scheme="purple"),
                                        align_items="end"
                                    ),
                                    width="100%"
                                ),
                                padding="1rem",
                                margin_bottom="0.5rem"
                            )
                        ),
                        width="100%"
                    ),
                    value="audit"
                ),
                rx.tabs.content(
                    # Visitor Logs Tab
                    rx.vstack(
                        rx.heading("Visitor Sign-in Log", size="6"),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Visitor"),
                                    rx.table.column_header_cell("Type"),
                                    rx.table.column_header_cell("Purpose"),
                                    rx.table.column_header_cell("Check-in"),
                                    rx.table.column_header_cell("Status"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AdminDashboardState.visitor_logs,
                                    lambda log: rx.table.row(
                                        rx.table.cell(log["visitor_name"]),
                                        rx.table.cell(log["visitor_type"]),
                                        rx.table.cell(log["purpose"]),
                                        rx.table.cell(log["check_in_time"]),
                                        rx.table.cell(
                                            rx.badge(
                                                log["status"],
                                                color_scheme=rx.cond(log["status"] == "completed", "green", "yellow")
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        width="100%"
                    ),
                    value="visitors"
                ),
                rx.tabs.content(
                    # Fuel Pricing Tab (Superadmin)
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Fuel Pricing Management", size="6"),
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
                                rx.heading("Current Fuel Prices", size="4"),
                                rx.hstack(
                                    rx.text("Petrol (Retail):", font_weight="bold"),
                                    rx.text("1,650 RWF/liter"),
                                    rx.button("Update", size="2", variant="outline"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Diesel (Retail):", font_weight="bold"),
                                    rx.text("1,550 RWF/liter"),
                                    rx.button("Update", size="2", variant="outline"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Kerosene:", font_weight="bold"),
                                    rx.text("1,200 RWF/liter"),
                                    rx.button("Update", size="2", variant="outline"),
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
                                rx.heading("Partner Agreements", size="4"),
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
                            rx.heading("System Settings", size="6"),
                            rx.badge("Superadmin Only", color_scheme="red"),
                            rx.spacer(),
                            rx.button("Save Changes", color_scheme="green"),
                            width="100%"
                        ),
                        rx.divider(),
                        rx.text("Configure system parameters and business rules"),
                        rx.card(
                            rx.vstack(
                                rx.heading("Station Information", size="4"),
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
                                rx.heading("Business Rules", size="4"),
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
                                rx.heading("Approval Settings", size="4"),
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
                    rx.heading("Reports", size="6"),
                    value="reports"
                ),
                rx.tabs.content(
                    # Operations Tab
                    rx.vstack(
                        rx.heading("Daily Operations", size="6"),
                        rx.card(
                            rx.vstack(
                                rx.heading("Fuel Deliveries", size="4"),
                                rx.foreach(
                                    AdminDashboardState.fuel_deliveries,
                                    lambda delivery: rx.card(
                                        rx.hstack(
                                            rx.text(f"{delivery.get('delivery_id', '')}"),
                                            rx.text(f"{delivery.get('fuel_type', '')}"),
                                            rx.text(f"{delivery.get('quantity_liters', 0)} L"),
                                            rx.text(f"{delivery.get('delivery_date', '')}")
                                        )
                                    )
                                )
                            )
                        ),
                        rx.card(
                            rx.vstack(
                                rx.heading("Inventory Levels", size="4"),
                                rx.foreach(
                                    AdminDashboardState.inventory_levels,
                                    lambda tank: rx.card(
                                        rx.hstack(
                                            rx.text(f"{tank.get('tank_id', '')}"),
                                            rx.text(f"{tank.get('fuel_type', '')}"),
                                            rx.text(f"{tank.get('current_level', 0)} / {tank.get('capacity', 0)} L")
                                        )
                                    )
                                )
                            )
                        ),
                        width="100%"
                    ),
                    value="operations"
                ),
                rx.tabs.content(
                    # Opening/Closing Procedures Tab
                    rx.vstack(
                        rx.heading("Station Opening/Closing Procedures", size="6"),
                        rx.card(
                            rx.vstack(
                                rx.heading("Current Status", size="4"),
                                rx.badge(
                                    rx.cond(AdminDashboardState.station_status == "open", "STATION OPEN", "STATION CLOSED"),
                                    color_scheme=rx.cond(AdminDashboardState.station_status == "open", "green", "red")
                                ),
                                rx.input(
                                    placeholder="Opening Cash (RWF)",
                                    on_change=lambda v: setattr(AdminDashboardState, 'opening_cash', float(v) if v else 0)
                                ),
                                rx.button(
                                    "Open Station",
                                    on_click=AdminDashboardState.open_station,
                                    color_scheme="green"
                                ),
                                rx.input(
                                    placeholder="Closing Cash (RWF)",
                                    on_change=lambda v: setattr(AdminDashboardState, 'closing_cash', float(v) if v else 0)
                                ),
                                rx.button(
                                    "Close Station",
                                    on_click=AdminDashboardState.close_station,
                                    color_scheme="red"
                                )
                            )
                        ),
                        width="100%"
                    ),
                    value="procedures"
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
        background_color="#f8fafc",
    )
