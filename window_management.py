from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from acat.ui.main_window import MainWindow

main_window: None | MainWindow = None


def get_main_window() -> MainWindow:
    if main_window is None:
        raise RuntimeError("main_window is not initialized")
    return main_window


def set_main_window(window: MainWindow) -> None:
    global main_window
    main_window = window
