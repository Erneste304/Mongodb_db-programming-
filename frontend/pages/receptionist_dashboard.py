import reflex as rx
import requests
from frontend.utils.api_client import api_client


class ReceptionistDashboardState(rx.State):
    """Receptionist dashboard state"""
    today_transactions: int = 0
    today_sales: float = 0
    selected_tab: str = "sales"
    fuel_type: str = "petrol"
    quantity: float = 0.0
    payment_method: str = "cash"
    
    def set_selected_tab(self, tab: str):
        self.selected_tab = tab
    
    def set_fuel_type(self, value: str):
        self.fuel_type = value
    
    def set_quantity(self, value: str):
        try:
            self.quantity = float(value)
        except ValueError:
            self.quantity = 0.0
    
    def set_payment_method(self, value: str):
        self.payment_method = value
    
    async def load_today_stats(self):
        """Load today's transaction statistics"""
        try:
            report = api_client.get("/reports/daily-summary")
            self.today_transactions = report.get("total_transactions", 0)
            self.today_sales = report.get("total_sales", 0)
        except Exception as e:
            # Fallback values
            self.today_transactions = 45
            self.today_sales = 3450000
    
    async def process_sale(self):
        """Process a new sale transaction"""
        try:
            # Get current fuel price (would be from API)
            price_per_liter = 1500  # Example price
            total_amount = self.quantity * price_per_liter
            
            # Create transaction
            transaction = api_client.post(
                "/sales/transactions",
                data={
                    "transaction_id": f"TXN-{rx.vars.get('timestamp', '202405101530')}",
                    "fuel_type": self.fuel_type,
                    "quantity_liters": self.quantity,
                    "price_per_liter": price_per_liter,
                    "payment_method": self.payment_method,
                    "pump_number": 1
                }
            )
            
            # Reset form
            self.quantity = 0.0
            await self.load_today_stats()
            
        except Exception as e:
            # Show error (would be in UI)
            pass
    
    def on_mount(self):
        """Load data when component mounts"""
        self.load_today_stats()


def receptionist_dashboard_page() -> rx.Component:
    """Receptionist dashboard page"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Receptionist Dashboard", size="2xl"),
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
                        rx.text("Today's Transactions", color="gray"),
                        rx.heading(ReceptionistDashboardState.today_transactions, size="3xl"),
                        rx.text("transactions", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Today's Sales", color="gray"),
                        rx.heading(f"{ReceptionistDashboardState.today_sales:,.0f}", size="3xl"),
                        rx.text("RWF", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Active Pumps", color="gray"),
                        rx.heading("4", size="3xl"),
                        rx.text("pumps available", color="blue", font_size="sm"),
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
                    rx.tabs.trigger("Process Sale", value="sales"),
                    rx.tabs.trigger("Transactions", value="transactions"),
                    rx.tabs.trigger("Customers", value="customers"),
                ),
                rx.tabs.content(
                    # Process Sale Tab
                    rx.vstack(
                        rx.heading("Process Fuel Sale", size="lg"),
                        rx.divider(),
                        rx.card(
                            rx.vstack(
                                rx.text("Fuel Type", font_weight="medium"),
                                rx.select(
                                    ["petrol", "diesel", "kerosene"],
                                    value=ReceptionistDashboardState.fuel_type,
                                    on_change=ReceptionistDashboardState.set_fuel_type,
                                    width="100%"
                                ),
                                
                                rx.text("Quantity (Liters)", font_weight="medium"),
                                rx.input(
                                    placeholder="Enter quantity in liters",
                                    type="number",
                                    on_change=ReceptionistDashboardState.set_quantity,
                                    width="100%"
                                ),
                                
                                rx.text("Payment Method", font_weight="medium"),
                                rx.select(
                                    ["cash", "mobile_money", "card", "credit"],
                                    value=ReceptionistDashboardState.payment_method,
                                    on_change=ReceptionistDashboardState.set_payment_method,
                                    width="100%"
                                ),
                                
                                rx.divider(),
                                
                                rx.hstack(
                                    rx.text(f"Total: {ReceptionistDashboardState.quantity * 1500:,.0f} RWF"),
                                    rx.spacer(),
                                    rx.button(
                                        "Process Sale",
                                        on_click=ReceptionistDashboardState.process_sale,
                                        color_scheme="green",
                                        size="3"
                                    ),
                                    width="100%",
                                    justify="between"
                                ),
                                
                                width="100%",
                                spacing="4"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="sales"
                ),
                rx.tabs.content(
                    # Transactions Tab
                    rx.vstack(
                        rx.heading("Recent Transactions", size="lg"),
                        rx.hstack(
                            rx.button("View All Transactions", variant="outline"),
                            rx.button("Export Report", variant="outline"),
                            spacing="2"
                        ),
                        rx.divider(),
                        rx.text("Transaction list will be displayed here"),
                        width="100%"
                    ),
                    value="transactions"
                ),
                rx.tabs.content(
                    # Customers Tab
                    rx.vstack(
                        rx.heading("Customer Management", size="lg"),
                        rx.hstack(
                            rx.button("Add Customer", color_scheme="blue"),
                            rx.button("View All Customers", variant="outline"),
                            spacing="2"
                        ),
                        rx.divider(),
                        rx.text("Customer list will be displayed here"),
                        width="100%"
                    ),
                    value="customers"
                ),
                on_change=ReceptionistDashboardState.set_selected_tab,
                value=ReceptionistDashboardState.selected_tab
            ),
            
            width="100%",
            max_width="1400px",
            padding="2rem",
            spacing="6"
        ),
        width="100%",
        background_color="#f8fafc"
    )
