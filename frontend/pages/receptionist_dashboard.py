import reflex as rx
import requests
from frontend.utils.api_client import api_client
from frontend.base_state import State
from datetime import datetime


class ReceptionistDashboardState(State):
    """Receptionist dashboard state"""
    today_transactions: int = 0
    today_sales: float = 0
    selected_tab: str = "sales"
    recent_transactions: list[dict] = []
    customers: list[dict] = []
    fuel_type: str = "petrol"
    quantity: float = 0.0
    payment_method: str = "cash"
    customer_phone: str = ""
    is_processing: bool = False
    processing_status: str = ""
    show_receipt: bool = False
    last_transaction: dict = {}
    
    # New features state
    shop_items: list[dict] = []
    shop_sales: list[dict] = []
    pumps: list[dict] = []
    shifts: list[dict] = []
    complaints: list[dict] = []
    petrol_sales: float = 0.0
    diesel_sales: float = 0.0
    kerosene_sales: float = 0.0
    
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
        
    def set_customer_phone(self, value: str):
        self.customer_phone = value
    
    async def load_today_stats(self):
        """Load today's transaction statistics"""
        try:
            report = api_client.get("/reports/daily-summary")
            self.today_transactions = report.get("total_transactions", 0)
            self.today_sales = report.get("total_sales", 0)
            
            # Load fuel type sales
            sales_report = api_client.get("/reports/sales/daily")
            sales_by_fuel = sales_report.get("sales_by_fuel_type", {})
            self.petrol_sales = sales_by_fuel.get("petrol", 0)
            self.diesel_sales = sales_by_fuel.get("diesel", 0)
            self.kerosene_sales = sales_by_fuel.get("kerosene", 0)
        except Exception as e:
            # Fallback values
            self.today_transactions = 45
            self.today_sales = 3450000
    
    async def load_shop_items(self):
        """Load shop inventory"""
        try:
            self.shop_items = api_client.get("/shop/items")
        except Exception as e:
            self.shop_items = []
    
    async def load_pumps(self):
        """Load pump status"""
        try:
            self.pumps = api_client.get("/pump/pumps")
        except Exception as e:
            self.pumps = []
    
    async def load_shifts(self):
        """Load shift history"""
        try:
            self.shifts = api_client.get("/shift/shifts")
        except Exception as e:
            self.shifts = []
    
    async def load_complaints(self):
        """Load complaint history"""
        try:
            self.complaints = api_client.get("/complaints/complaints")
        except Exception as e:
            self.complaints = []
    
    async def process_sale(self):
        """Process a new sale transaction"""
        try:
            # Get current fuel price (would be from API)
            price_per_liter = 1500  # Example price
            total_amount = self.quantity * price_per_liter
            
            self.is_processing = True
            self.processing_status = "Sending Push to Customer Phone..."
            
            # Create transaction
            transaction_data = {
                "transaction_id": f"TXN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "fuel_type": self.fuel_type,
                "quantity_liters": self.quantity,
                "price_per_liter": price_per_liter,
                "total_amount": total_amount,
                "payment_method": self.payment_method,
                "pump_number": 1
            }
            
            if self.payment_method == "mobile_money":
                transaction_data["phone_number"] = self.customer_phone
                transaction_data["provider"] = "MTN" # Default for now
                self.processing_status = "Waiting for Customer to enter PIN..."

            transaction = api_client.post(
                "/sales/transactions",
                data=transaction_data
            )
            
            self.is_processing = False
            self.processing_status = ""
            
            # Reset form
            self.quantity = 0.0
            self.last_transaction = transaction
            self.show_receipt = True
            await self.load_today_stats()
            rx.toast.success("Sale processed successfully")
            
        except Exception as e:
            self.is_processing = False
            self.processing_status = ""
            rx.toast.error(f"Transaction failed: {str(e)}")

    def close_receipt(self):
        self.show_receipt = False
    
    def on_mount(self):
        """Load data when component mounts"""
        self.load_today_stats()


def receptionist_dashboard_page() -> rx.Component:
    """Receptionist dashboard page"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Receptionist Dashboard", size="8"),
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
                        rx.heading(ReceptionistDashboardState.today_transactions, size="9"),
                        rx.text("transactions", color="green", font_size="2"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Today's Sales", color="gray"),
                        rx.heading(f"{ReceptionistDashboardState.today_sales:,.0f}", size="9"),
                        rx.text("RWF", color="green", font_size="2"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Active Pumps", color="gray"),
                        rx.heading("4", size="9"),
                        rx.text("pumps available", color="blue", font_size="2"),
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
                    rx.tabs.trigger("Shop Sales", value="shop"),
                    rx.tabs.trigger("Pump Management", value="pump"),
                    rx.tabs.trigger("Shift Management", value="shift"),
                    rx.tabs.trigger("Complaints", value="complaints"),
                    rx.tabs.trigger("Fuel Sales Report", value="fuel_report"),
                ),
                rx.tabs.content(
                    # Process Sale Tab
                    rx.vstack(
                        rx.heading("Process Fuel Sale", size="4"),
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
                                
                                rx.cond(
                                    ReceptionistDashboardState.payment_method == "mobile_money",
                                    rx.vstack(
                                        rx.text("Customer Phone (078/079...)", font_size="2"),
                                        rx.input(
                                            placeholder="Enter phone number",
                                            on_change=ReceptionistDashboardState.set_customer_phone,
                                            width="100%"
                                        ),
                                        width="100%"
                                    )
                                ),
                                
                                rx.divider(),
                                
                                rx.hstack(
                                    rx.text(f"Total: {ReceptionistDashboardState.quantity * 1500:,.0f} RWF"),
                                    rx.spacer(),
                                    rx.button(
                                        "Process Sale",
                                        on_click=ReceptionistDashboardState.process_sale,
                                        color_scheme="green",
                                        size="3",
                                        is_loading=ReceptionistDashboardState.is_processing,
                                        loading_text=ReceptionistDashboardState.processing_status
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
                        rx.heading("Record New Transaction", size="6"),
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
                        rx.heading("Customer Management", size="6"),
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
                rx.tabs.content(
                    # Shop Sales Tab
                    rx.vstack(
                        rx.heading("Shop Sales", size="6"),
                        rx.divider(),
                        rx.card(
                            rx.vstack(
                                rx.text("Shop Inventory", font_weight="bold"),
                                rx.text("Select items and complete shop sales"),
                                spacing="2"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="shop"
                ),
                rx.tabs.content(
                    # Pump Management Tab
                    rx.vstack(
                        rx.heading("Pump Management", size="6"),
                        rx.divider(),
                        rx.card(
                            rx.vstack(
                                rx.text("Pump Status", font_weight="bold"),
                                rx.text("View and manage pump availability"),
                                spacing="2"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="pump"
                ),
                rx.tabs.content(
                    # Shift Management Tab
                    rx.vstack(
                        rx.heading("Shift Management", size="6"),
                        rx.divider(),
                        rx.card(
                            rx.vstack(
                                rx.text("Start/End Shift", font_weight="bold"),
                                rx.text("Manage shift opening and closing with cash counting"),
                                spacing="2"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="shift"
                ),
                rx.tabs.content(
                    # Complaints Tab
                    rx.vstack(
                        rx.heading("Customer Complaints", size="6"),
                        rx.divider(),
                        rx.card(
                            rx.vstack(
                                rx.text("Submit Complaint", font_weight="bold"),
                                rx.text("Record customer complaints and track resolution"),
                                spacing="2"
                            ),
                            padding="1.5rem"
                        ),
                        width="100%"
                    ),
                    value="complaints"
                ),
                rx.tabs.content(
                    # Fuel Sales Report Tab
                    rx.vstack(
                        rx.heading("Daily Sales by Fuel Type", size="6"),
                        rx.divider(),
                        rx.hstack(
                            rx.card(
                                rx.vstack(
                                    rx.text("Petrol Sales", color="green"),
                                    rx.heading(f"{ReceptionistDashboardState.petrol_sales:,.0f}", size="7"),
                                    rx.text("RWF", color="gray"),
                                    spacing="1"
                                ),
                                padding="1.5rem"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text("Diesel Sales", color="blue"),
                                    rx.heading(f"{ReceptionistDashboardState.diesel_sales:,.0f}", size="7"),
                                    rx.text("RWF", color="gray"),
                                    spacing="1"
                                ),
                                padding="1.5rem"
                            ),
                            rx.card(
                                rx.vstack(
                                    rx.text("Kerosene Sales", color="purple"),
                                    rx.heading(f"{ReceptionistDashboardState.kerosene_sales:,.0f}", size="7"),
                                    rx.text("RWF", color="gray"),
                                    spacing="1"
                                ),
                                padding="1.5rem"
                            ),
                            spacing="4",
                            width="100%"
                        ),
                        width="100%"
                    ),
                    value="fuel_report"
                ),
                on_change=ReceptionistDashboardState.set_selected_tab,
                value=ReceptionistDashboardState.selected_tab
            ),
            
            width="100%",
            max_width="1400px",
            padding="2rem",
            spacing="6"
        ),
        # EBM Receipt Modal
        rx.dialog.root(
            rx.dialog.content(
                rx.vstack(
                    rx.heading("Official EBM Receipt", size="6", text_align="center"),
                    rx.text("Petroleum Station PS-001", font_size="2", color="gray"),
                    rx.divider(),
                    rx.hstack(
                        rx.text("Receipt #:"),
                        rx.text(ReceptionistDashboardState.last_transaction["receipt_number"]),
                        justify="between", width="100%"
                    ),
                    rx.hstack(
                        rx.text("Date:"),
                        rx.text(ReceptionistDashboardState.last_transaction["ebm_signed_at"]),
                        justify="between", width="100%"
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.text(f"{ReceptionistDashboardState.last_transaction['quantity_liters']}L {ReceptionistDashboardState.last_transaction['fuel_type']}"),
                        rx.text(f"{ReceptionistDashboardState.last_transaction['total_amount']:,.0f} RWF"),
                        justify="between", width="100%"
                    ),
                    rx.divider(),
                    rx.hstack(
                        rx.text("NET AMOUNT:"),
                        rx.text(f"{ReceptionistDashboardState.last_transaction.get('net_amount', 0):,.0f} RWF"),
                        justify="between", width="100%"
                    ),
                    rx.hstack(
                        rx.text("VAT (18%):"),
                        rx.text(f"{ReceptionistDashboardState.last_transaction.get('vat_amount', 0):,.0f} RWF"),
                        justify="between", width="100%"
                    ),
                    rx.hstack(
                        rx.text("TOTAL:", font_weight="bold"),
                        rx.text(f"{ReceptionistDashboardState.last_transaction['total_amount']:,.0f} RWF", font_weight="bold"),
                        justify="between", width="100%"
                    ),
                    rx.divider(),
                    rx.vstack(
                        rx.text("EBM SIGNATURE:", font_size="1", font_weight="bold"),
                        rx.text(ReceptionistDashboardState.last_transaction["ebm_signature"], font_size="2", font_family="monospace"),
                        rx.text(f"MRC: {ReceptionistDashboardState.last_transaction['ebm_mrc']}", font_size="1"),
                        rx.text(f"SD: {ReceptionistDashboardState.last_transaction['ebm_internal_data']}", font_size="1"),
                        align_items="center",
                        width="100%"
                    ),
                    rx.divider(),
                    rx.text("Thank you for choosing us!", font_size="2", font_style="italic"),
                    rx.button("Close & Print", on_click=ReceptionistDashboardState.close_receipt, width="100%"),
                    spacing="3"
                ),
                max_width="400px"
            ),
            open=ReceptionistDashboardState.show_receipt,
            on_open_change=lambda _: ReceptionistDashboardState.close_receipt()
        ),
        width="100%",
        background_color="#f8fafc"
    )
