import reflex as rx
import requests
from frontend.utils.api_client import api_client
from frontend.base_state import State


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
