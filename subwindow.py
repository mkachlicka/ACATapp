import customtkinter as ctk


class SubWindow(ctk.CTkToplevel):
    """Base class for all popup/sub windows."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.withdraw()  # hidden until explicitly shown
        self.protocol("WM_DELETE_WINDOW", self.withdraw)
        self.bind("<Escape>", lambda e: self.withdraw())
        self.bind("<Control-w>", lambda e: self.withdraw())

    def show_centered(self, parent=None):
        """Show the window, optionally centered on parent."""
        self.deiconify()
        self.lift()
        self.focus_force()
        if parent:
            self.update_idletasks()
            pw = parent.winfo_width()
            ph = parent.winfo_height()
            px = parent.winfo_x()
            py = parent.winfo_y()
            w = self.winfo_reqwidth()
            h = self.winfo_reqheight()
            x = px + (pw - w) // 2
            y = py + (ph - h) // 2
            self.geometry(f"+{max(0, x)}+{max(0, y)}")
