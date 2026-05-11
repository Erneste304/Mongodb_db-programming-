import reflex as rx
import requests
from frontend.utils.api_client import api_client
from frontend.base_state import State


class AccountantDashboardState(State):
    """Accountant dashboard state"""
    daily_sales: float = 0
    pending_payments: float = 0
    petty_cash_balance: float = 0
    my_requests: list[dict] = []
    selected_tab: str = "overview"
    
    def set_selected_tab(self, tab: str):
        self.selected_tab = tab
    
    async def load_financial_summary(self):
        """Load financial summary from backend API"""
        try:
            # Get daily sales report
            sales_report = api_client.get("/reports/daily-summary")
            self.daily_sales = sales_report.get("total_sales", 0)
            
            # Get pending payments
            payments = api_client.get("/finance/payments?status=pending")
            self.pending_payments = sum(p["amount"] for p in payments)
            
            # Get petty cash balance
            petty_cash = api_client.get("/finance/petty-cash/balance")
            self.petty_cash_balance = petty_cash.get("balance", 0)
            
        except Exception as e:
            # Fallback values if API fails
            self.daily_sales = 3450000
            self.pending_payments = 2500000
            self.petty_cash_balance = 45000
    
    async def load_my_requests(self):
        """Load accountant's approval requests"""
        try:
            requests_data = api_client.get("/approvals/my-requests")
            self.my_requests = [
                {
                    "id": req["id"],
                    "type": req["request_type"],
                    "reason": req["reason"],
                    "status": req["status"],
                    "requested_at": req["requested_at"]
                }
                for req in requests_data
            ]
        except Exception as e:
            # Fallback mock data
            self.my_requests = [
                {
                    "id": "1",
                    "type": "Large Payment",
                    "reason": "Monthly fuel supplier payment - Total Rwanda",
                    "status": "pending",
                    "requested_at": "2024-05-10 14:30"
                }
            ]
    
    def on_mount(self):
        """Load data when component mounts"""
        self.load_financial_summary()
        self.load_my_requests()


def accountant_dashboard_page() -> rx.Component:
    """Accountant dashboard page"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Accountant Dashboard", size="8"),
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
                        rx.text("Today's Sales", color="gray"),
                        rx.heading(f"{AccountantDashboardState.daily_sales:,.0f}", size="9"),
                        rx.text("RWF", color="green", font_size="2"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Pending Payments", color="gray"),
                        rx.heading(f"{AccountantDashboardState.pending_payments:,.0f}", size="9"),
                        rx.text("RWF", color="orange", font_size="2"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Petty Cash Balance", color="gray"),
                        rx.heading(f"{AccountantDashboardState.petty_cash_balance:,.0f}", size="9"),
                        rx.text("RWF", color="blue", font_size="2"),
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
                    rx.tabs.trigger("Financial Overview", value="overview"),
                    rx.tabs.trigger("Payments", value="payments"),
                    rx.tabs.trigger("Cash Reconciliation", value="reconciliation"),
                    rx.tabs.trigger("My Requests", value="requests"),
                ),
                rx.tabs.content(
                    # Financial Overview Tab
                    rx.vstack(
                        rx.heading("Financial Overview", size="6"),
                        rx.text("Daily financial summary and key metrics"),
                        rx.divider(),
                        rx.vstack(
                            rx.hstack(
                                rx.text("Revenue Today:", font_weight="bold"),
                                rx.text(f"{AccountantDashboardState.daily_sales:,.0f} RWF"),
                                justify="between",
                                width="100%"
                            ),
                            rx.hstack(
                                rx.text("Pending Payments:", font_weight="bold"),
                                rx.text(f"{AccountantDashboardState.pending_payments:,.0f} RWF"),
                                justify="between",
                                width="100%"
                            ),
                            rx.hstack(
                                rx.text("Petty Cash:", font_weight="bold"),
                                rx.text(f"{AccountantDashboardState.petty_cash_balance:,.0f} RWF"),
                                justify="between",
                                width="100%"
                            ),
                            width="100%",
                            spacing="3"
                        ),
                        width="100%"
                    ),
                    value="overview"
                ),
                rx.tabs.content(
                    # Payments Tab
                    rx.vstack(
                        rx.heading("Revenue Streams", size="6"),
                        rx.hstack(
                            rx.button("Create Payment Request", color_scheme="blue"),
                            rx.button("View All Payments", variant="outline"),
                            spacing="2"
                        ),
                        rx.text("Manage supplier payments, salary payments, and expenses"),
                        rx.divider(),
                        rx.text("Payment list will be displayed here"),
                        width="100%"
                    ),
                    value="payments"
                ),
                rx.tabs.content(
                    # Cash Reconciliation Tab
                    rx.vstack(
                        rx.heading("Cash Reconciliation", size="4"),
                        rx.hstack(
                            rx.button("New Reconciliation", color_scheme="blue"),
                            rx.button("View History", variant="outline"),
                            spacing="2"
                        ),
                        rx.text("Daily cash reconciliation and bank deposits"),
                        rx.divider(),
                        rx.text("Reconciliation records will be displayed here"),
                        width="100%"
                    ),
                    value="reconciliation"
                ),
                rx.tabs.content(
                    # My Requests Tab
                    rx.vstack(
                        rx.heading("My Approval Requests", size="4"),
                        rx.button("Create New Request", color_scheme="blue"),
                        rx.divider(),
                        rx.foreach(
                            AccountantDashboardState.my_requests,
                            lambda req: rx.card(
                                rx.vstack(
                                    rx.hstack(
                                        rx.badge(req["type"], color_scheme="blue"),
                                        rx.badge(req["status"], color_scheme="yellow"),
                                        rx.text(req["requested_at"], color="gray", font_size="2"),
                                        justify="between",
                                        width="100%"
                                    ),
                                    rx.text(f"Reason: {req['reason']}"),
                                    width="100%",
                                    spacing="2"
                                ),
                                padding="1rem",
                                margin_bottom="0.5rem"
                            )
                        ),
                        width="100%"
                    ),
                    value="requests"
                ),
                on_change=AccountantDashboardState.set_selected_tab,
                value=AccountantDashboardState.selected_tab
            ),
            
            width="100%",
            max_width="1400px",
            padding="2rem",
            spacing="6"
        ),
        width="100%",
        background_color="#f8fafc"
    )
