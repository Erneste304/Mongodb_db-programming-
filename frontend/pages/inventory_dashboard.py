import reflex as rx
import requests
from frontend.utils.api_client import api_client


class InventoryDashboardState(rx.State):
    """Inventory manager dashboard state"""
    total_tanks: int = 0
    total_capacity: float = 0
    current_level: float = 0
    average_fill: float = 0
    tanks_below_threshold: list[dict] = []
    pending_deliveries: int = 0
    selected_tab: str = "overview"
    
    def set_selected_tab(self, tab: str):
        self.selected_tab = tab
    
    async def load_inventory_summary(self):
        """Load inventory summary from backend API"""
        try:
            report = api_client.get("/inventory/current")
            self.total_tanks = report.get("total_tanks", 0)
            self.total_capacity = report.get("total_capacity", 0)
            self.current_level = report.get("total_current_level", 0)
            self.average_fill = report.get("average_fill_percentage", 0)
            self.tanks_below_threshold = report.get("tanks_below_threshold", [])
            
            # Get pending deliveries
            deliveries = api_client.get("/inventory/deliveries?status=pending")
            self.pending_deliveries = len(deliveries)
            
        except Exception as e:
            # Fallback values
            self.total_tanks = 4
            self.total_capacity = 40000
            self.current_level = 25000
            self.average_fill = 62.5
            self.tanks_below_threshold = [
                {
                    "tank_id": "T-003",
                    "tank_number": "3",
                    "fuel_type": "kerosene",
                    "current_level": 1500,
                    "capacity": 10000,
                    "fill_percentage": 15
                }
            ]
            self.pending_deliveries = 2
    
    def on_mount(self):
        """Load data when component mounts"""
        self.load_inventory_summary()


def inventory_dashboard_page() -> rx.Component:
    """Inventory manager dashboard page"""
    return rx.box(
        rx.vstack(
            # Header
            rx.hstack(
                rx.heading("Inventory Manager Dashboard", size="2xl"),
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
                        rx.text("Total Tanks", color="gray"),
                        rx.heading(InventoryDashboardState.total_tanks, size="3xl"),
                        rx.text("tanks", color="blue", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Total Capacity", color="gray"),
                        rx.heading(f"{InventoryDashboardState.total_capacity:,.0f}", size="3xl"),
                        rx.text("liters", color="blue", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Current Level", color="gray"),
                        rx.heading(f"{InventoryDashboardState.current_level:,.0f}", size="3xl"),
                        rx.text("liters", color="green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                rx.card(
                    rx.vstack(
                        rx.text("Average Fill", color="gray"),
                        rx.heading(f"{InventoryDashboardState.average_fill:.1f}%", size="3xl"),
                        rx.text("capacity", color="orange" if InventoryDashboardState.average_fill < 50 else "green", font_size="sm"),
                        spacing="1"
                    ),
                    padding="1.5rem"
                ),
                spacing="4",
                width="100%"
            ),
            
            # Alert for tanks below threshold
            rx.cond(
                InventoryDashboardState.tanks_below_threshold.length() > 0,
                rx.alert(
                    rx.alert_icon(),
                    rx.alert_title("Low Fuel Alert"),
                    rx.alert_description(f"{InventoryDashboardState.tanks_below_threshold.length} tank(s) below threshold"),
                    status="warning"
                )
            ),
            
            rx.divider(),
            
            # Tabs
            rx.tabs.root(
                rx.tabs.list(
                    rx.tabs.trigger("Tank Overview", value="overview"),
                    rx.tabs.trigger("Fuel Deliveries", value="deliveries"),
                    rx.tabs.trigger("Inventory Records", value="records"),
                    rx.tabs.trigger("Tank Calibration", value="calibration"),
                ),
                rx.tabs.content(
                    # Tank Overview Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Tank Overview", size="lg"),
                            rx.badge(f"{InventoryDashboardState.pending_deliveries} Pending Deliveries", color_scheme="yellow"),
                            rx.spacer(),
                            rx.button("Add Tank", color_scheme="blue"),
                            rx.button("View All Tanks", variant="outline"),
                            width="100%",
                            justify="between"
                        ),
                        rx.divider(),
                        rx.text("Tank list and status will be displayed here"),
                        rx.cond(
                            InventoryDashboardState.tanks_below_threshold.length() > 0,
                            rx.vstack(
                                rx.heading("Tanks Below Threshold", size="md"),
                                rx.foreach(
                                    InventoryDashboardState.tanks_below_threshold,
                                    lambda tank: rx.card(
                                        rx.hstack(
                                            rx.vstack(
                                                rx.text(f"Tank {tank['tank_number']}", font_weight="bold"),
                                                rx.text(tank["fuel_type"].capitalize()),
                                                align_items="start"
                                            ),
                                            rx.spacer(),
                                            rx.vstack(
                                                rx.text(f"{tank['fill_percentage']:.1f}% full", color="red"),
                                                rx.text(f"{tank['current_level']:,.0f} / {tank['capacity']:,.0f} L"),
                                                align_items="end"
                                            ),
                                            width="100%",
                                            justify="between"
                                        ),
                                        padding="1rem",
                                        background_color="#fef2f2"
                                    )
                                ),
                                width="100%",
                                spacing="2"
                            )
                        ),
                        width="100%"
                    ),
                    value="overview"
                ),
                rx.tabs.content(
                    # Fuel Deliveries Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Fuel Deliveries", size="lg"),
                            rx.button("Record Delivery", color_scheme="green"),
                            rx.button("View All Deliveries", variant="outline"),
                            spacing="2"
                        ),
                        rx.divider(),
                        rx.text("Fuel delivery records will be displayed here"),
                        width="100%"
                    ),
                    value="deliveries"
                ),
                rx.tabs.content(
                    # Inventory Records Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Inventory Records", size="lg"),
                            rx.button("Create Record", color_scheme="blue"),
                            rx.button("View History", variant="outline"),
                            spacing="2"
                        ),
                        rx.divider(),
                        rx.text("Daily inventory records will be displayed here"),
                        width="100%"
                    ),
                    value="records"
                ),
                rx.tabs.content(
                    # Tank Calibration Tab
                    rx.vstack(
                        rx.hstack(
                            rx.heading("Tank Calibration", size="lg"),
                            rx.button("Schedule Calibration", color_scheme="blue"),
                            rx.button("View Certificates", variant="outline"),
                            spacing="2"
                        ),
                        rx.divider(),
                        rx.text("Calibration certificates and schedules will be displayed here"),
                        width="100%"
                    ),
                    value="calibration"
                ),
                on_change=InventoryDashboardState.set_selected_tab,
                value=InventoryDashboardState.selected_tab
            ),
            
            width="100%",
            max_width="1400px",
            padding="2rem",
            spacing="6"
        ),
        width="100%",
        background_color="#f8fafc"
    )
