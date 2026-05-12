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
    
    # Additional state for missing features
    mobile_money_transactions: list[dict] = []
    profit_margins: list[dict] = []
    daily_reconciliation: dict = {}
    fuel_costs: list[dict] = []
    
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
    
    async def load_mobile_money_transactions(self):
        """Load mobile money transactions"""
        try:
            transactions = api_client.get("/finance/mobile-money")
            self.mobile_money_transactions = transactions
        except Exception as e:
            self.mobile_money_transactions = []
    
    async def load_profit_margins(self):
        """Load profit margins per fuel type"""
        try:
            margins = api_client.get("/accounting/profit-margins")
            self.profit_margins = margins
        except Exception as e:
            self.profit_margins = []
    
    async def load_daily_reconciliation(self):
        """Load daily cash reconciliation data"""
        try:
            reconciliation = api_client.get("/finance/daily-reconciliation")
            self.daily_reconciliation = reconciliation
        except Exception as e:
            self.daily_reconciliation = {}
    
    async def load_fuel_costs(self):
        """Load fuel purchase costs vs selling prices"""
        try:
            costs = api_client.get("/accounting/fuel-costs")
            self.fuel_costs = costs
        except Exception as e:
            self.fuel_costs = []
    
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
        self.load_mobile_money_transactions()
        self.load_profit_margins()
        self.load_daily_reconciliation()
        self.load_fuel_costs()


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
                    rx.tabs.trigger("Mobile Money", value="mobile_money"),
                    rx.tabs.trigger("Profit Margins", value="margins"),
                    rx.tabs.trigger("Fuel Costs", value="fuel_costs"),
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
                        rx.card(
                            rx.vstack(
                                rx.heading("Today's Reconciliation", size="3"),
                                rx.hstack(
                                    rx.text("Cash:", font_weight="bold"),
                                    rx.text(f"{AccountantDashboardState.daily_reconciliation.get('cash', 0):,.0f} RWF"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Credit Cards:", font_weight="bold"),
                                    rx.text(f"{AccountantDashboardState.daily_reconciliation.get('credit_cards', 0):,.0f} RWF"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Mobile Money:", font_weight="bold"),
                                    rx.text(f"{AccountantDashboardState.daily_reconciliation.get('mobile_money', 0):,.0f} RWF"),
                                    justify="between",
                                    width="100%"
                                ),
                                rx.hstack(
                                    rx.text("Total:", font_weight="bold"),
                                    rx.text(f"{AccountantDashboardState.daily_reconciliation.get('total', 0):,.0f} RWF"),
                                    justify="between",
                                    width="100%"
                                ),
                                width="100%",
                                spacing="2"
                            )
                        ),
                        width="100%"
                    ),
                    value="reconciliation"
                ),
                rx.tabs.content(
                    # Mobile Money Tab
                    rx.vstack(
                        rx.heading("Mobile Money Transactions", size="4"),
                        rx.hstack(
                            rx.button("Record Transaction", color_scheme="blue"),
                            rx.button("View All", variant="outline"),
                            spacing="2"
                        ),
                        rx.text("MTN Momo and Airtel Money transactions"),
                        rx.divider(),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Transaction ID"),
                                    rx.table.column_header_cell("Provider"),
                                    rx.table.column_header_cell("Phone"),
                                    rx.table.column_header_cell("Amount"),
                                    rx.table.column_header_cell("Status"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AccountantDashboardState.mobile_money_transactions,
                                    lambda tx: rx.table.row(
                                        rx.table.cell(tx.get("transaction_id", "")),
                                        rx.table.cell(tx.get("provider", "")),
                                        rx.table.cell(tx.get("phone", "")),
                                        rx.table.cell(f"{tx.get('amount', 0):,.0f} RWF"),
                                        rx.table.cell(
                                            rx.badge(
                                                tx.get("status", ""),
                                                color_scheme=rx.cond(tx.get("status") == "completed", "green", "yellow")
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        width="100%"
                    ),
                    value="mobile_money"
                ),
                rx.tabs.content(
                    # Profit Margins Tab
                    rx.vstack(
                        rx.heading("Profit Margins per Fuel Type", size="4"),
                        rx.text("Monitor profit margins by fuel type"),
                        rx.divider(),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Fuel Type"),
                                    rx.table.column_header_cell("Purchase Cost"),
                                    rx.table.column_header_cell("Selling Price"),
                                    rx.table.column_header_cell("Margin"),
                                    rx.table.column_header_cell("Margin %"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AccountantDashboardState.profit_margins,
                                    lambda margin: rx.table.row(
                                        rx.table.cell(margin.get("fuel_type", "")),
                                        rx.table.cell(f"{margin.get('purchase_cost', 0):,.0f} RWF/L"),
                                        rx.table.cell(f"{margin.get('selling_price', 0):,.0f} RWF/L"),
                                        rx.table.cell(f"{margin.get('margin', 0):,.0f} RWF/L"),
                                        rx.table.cell(
                                            rx.badge(
                                                f"{margin.get('margin_percentage', 0):.1f}%",
                                                color_scheme=rx.cond(margin.get('margin_percentage', 0) > 10, "green", "orange")
                                            )
                                        ),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        width="100%"
                    ),
                    value="margins"
                ),
                rx.tabs.content(
                    # Fuel Costs Tab
                    rx.vstack(
                        rx.heading("Fuel Purchase Costs vs Selling Prices", size="4"),
                        rx.text("Track fuel costs and pricing"),
                        rx.divider(),
                        rx.table.root(
                            rx.table.header(
                                rx.table.row(
                                    rx.table.column_header_cell("Fuel Type"),
                                    rx.table.column_header_cell("Purchase Cost (RWF/L)"),
                                    rx.table.column_header_cell("Selling Price (RWF/L)"),
                                    rx.table.column_header_cell("Supplier"),
                                    rx.table.column_header_cell("Last Updated"),
                                )
                            ),
                            rx.table.body(
                                rx.foreach(
                                    AccountantDashboardState.fuel_costs,
                                    lambda cost: rx.table.row(
                                        rx.table.cell(cost.get("fuel_type", "")),
                                        rx.table.cell(f"{cost.get('purchase_cost', 0):,.0f}"),
                                        rx.table.cell(f"{cost.get('selling_price', 0):,.0f}"),
                                        rx.table.cell(cost.get("supplier", "")),
                                        rx.table.cell(cost.get("last_updated", "")),
                                    )
                                )
                            ),
                            width="100%"
                        ),
                        width="100%"
                    ),
                    value="fuel_costs"
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
