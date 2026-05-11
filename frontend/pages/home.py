import reflex as rx
from frontend.base_state import State

class HomeState(State):
    """Home page state"""
    pass

def navbar() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.icon("fuel", size=24, color="white"),
                rx.heading("PETRO-SYNC", size="6", color="white", letter_spacing="2px"),
                spacing="2",
                align="center",
            ),
            rx.spacer(),
            rx.hstack(
                rx.link("Features", href="#features", color="white", variant="ghost"),
                rx.link("Security", href="#security", color="white", variant="ghost"),
                rx.link(
                    rx.button(
                        "Login to Portal",
                        color_scheme="blue",
                        variant="soft",
                        size="3",
                    ),
                    href="/login",
                ),
                spacing="6",
                align="center",
            ),
            width="100%",
            max_width="1200px",
            padding="1rem 2rem",
            margin="0 auto",
        ),
        background="rgba(15, 23, 42, 0.8)",
        backdrop_filter="blur(10px)",
        position="sticky",
        top="0",
        z_index="100",
        width="100%",
        border_bottom="1px solid rgba(255, 255, 255, 0.1)",
    )

def hero_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.badge(
                "v2.0 PRODUCTION READY",
                color_scheme="blue",
                variant="soft",
                padding="0.5rem 1rem",
                border_radius="full",
            ),
            rx.heading(
                "Modern Petroleum Management System",
                size="9",
                weight="bold",
                text_align="center",
                background="linear-gradient(to right, #fff, #94a3b8)",
                background_clip="text",
                color="transparent",
                line_height="1.2",
            ),
            rx.text(
                "The all-in-one command center for fuel stations. Real-time inventory tracking, automated billing, and detailed financial audits at your fingertips.",
                size="5",
                color="rgba(255, 255, 255, 0.7)",
                text_align="center",
                max_width="800px",
            ),
            rx.hstack(
                rx.link(
                    rx.button(
                        "Access Control Center",
                        size="4",
                        color_scheme="blue",
                        variant="classic",
                        padding="0 2rem",
                    ),
                    href="/login",
                ),
                rx.button(
                    "View Demo",
                    size="4",
                    variant="outline",
                    color_scheme="gray",
                    padding="0 2rem",
                ),
                spacing="4",
                margin_top="2rem",
            ),
            spacing="6",
            align="center",
            padding_top="8rem",
            padding_bottom="12rem",
        ),
        background="radial-gradient(circle at 50% 50%, rgba(30, 58, 138, 0.2) 0%, transparent 50%), #0f172a",
        width="100%",
    )

def feature_card(icon: str, title: str, description: str) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=32, color="#3b82f6"),
                padding="1rem",
                background="rgba(59, 130, 246, 0.1)",
                border_radius="1rem",
            ),
            rx.heading(title, size="4", margin_top="1rem"),
            rx.text(description, size="2", color="rgba(255, 255, 255, 0.6)"),
            align="start",
            spacing="3",
        ),
        variant="surface",
        background="rgba(30, 41, 59, 0.5)",
        border="1px solid rgba(255, 255, 255, 0.1)",
        padding="2rem",
    )

def features_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading("Engineered for Excellence", size="8", text_align="center"),
            rx.text(
                "Built to handle high-volume operations with precision and speed.",
                size="4",
                color="rgba(255, 255, 255, 0.5)",
                margin_bottom="4rem",
            ),
            rx.grid(
                feature_card(
                    "database", 
                    "MongoDB Powered", 
                    "Massive scalability for millions of transactions with Beanie ODM integration."
                ),
                feature_card(
                    "shield-check", 
                    "Secure Authentication", 
                    "Enterprise-grade JWT tokens and role-based access control for your data."
                ),
                feature_card(
                    "zap", 
                    "Real-time Analytics", 
                    "Instant dashboard updates for fuel levels, sales, and staff activity."
                ),
                feature_card(
                    "file-text", 
                    "Automated Invoicing", 
                    "Generate EBM-compliant receipts and financial reports with one click."
                ),
                columns="4",
                spacing="4",
                width="100%",
            ),
            spacing="4",
            align="center",
            padding="6rem 2rem",
            max_width="1200px",
            margin="0 auto",
        ),
        id="features",
        background="#0f172a",
        width="100%",
    )

def footer() -> rx.Component:
    return rx.box(
        rx.divider(background="rgba(255, 255, 255, 0.1)"),
        rx.hstack(
            rx.text("© 2024 Petro-Sync Management Systems. All rights reserved.", size="1", color="gray"),
            rx.spacer(),
            rx.hstack(
                rx.icon("git_branch", size=18, color="gray"),
                rx.icon("message_square", size=18, color="gray"),
                spacing="4",
            ),
            width="100%",
            padding="2rem 0",
            max_width="1200px",
            margin="0 auto",
        ),
        background="#0f172a",
        width="100%",
        padding="0 2rem",
    )

def home_page() -> rx.Component:
    return rx.box(
        navbar(),
        hero_section(),
        features_section(),
        footer(),
        background="#0f172a",
        color="white",
        min_height="100vh",
    )
