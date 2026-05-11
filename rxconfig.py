import reflex as rx

config = rx.Config(
    app_name="Mongodbassignment",
    plugins=[
        rx.plugins.SitemapPlugin(),
        rx.plugins.TailwindV4Plugin(),
        rx.plugins.RadixThemesPlugin(
            theme=rx.theme(
                appearance="light",
                has_background=True,
                accent_color="blue",
            )
        ),
    ]
)