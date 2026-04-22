import customtkinter as ctk

from acat.ui.main_window import MainWindow
from acat.ui.window_management import set_main_window


def start_application() -> None:
    """Start the ACAT application."""
    ctk.set_appearance_mode("system")   # follows OS light/dark setting
    ctk.set_default_color_theme("blue")

    app = MainWindow()
    set_main_window(app)
    app.mainloop()
