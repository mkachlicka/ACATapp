import customtkinter as ctk

from acat.ui.rubrics import make_rubrics
from acat.ui.subwindow import SubWindow


class HelpWindow(SubWindow):
    """Help window shown at start and on demand."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Help – ACAT")
        self.geometry("720x620")
        self.minsize(600, 400)
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self) -> None:
        scroll = ctk.CTkScrollableFrame(self)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(
            scroll,
            text="Automated Comprehensibility Assessment Tool",
            font=ctk.CTkFont(size=19, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(12, 6))

        ctk.CTkLabel(
            scroll,
            text="Usage Instructions",
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(anchor="w", padx=12, pady=(4, 6))

        steps = [
            'Choose one or multiple ".wav" audio files using the Choose Audio button on the toolbar.',
            'Click "Judge All" to evaluate all chosen files, or click the "Judge" button for each individual file.',
            'Check the judged scores in the table. Click "Info" for each file to see detailed score explanations.',
            'Export the results as a CSV file using the "Export CSV" button.',
        ]
        for i, text in enumerate(steps, 1):
            ctk.CTkLabel(
                scroll,
                text=f"  {i}.   {text}",
                wraplength=650,
                justify="left",
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", padx=16, pady=3)

        make_rubrics(scroll)

        # Close button at bottom
        ctk.CTkButton(
            scroll,
            text="Close",
            width=100,
            command=self.withdraw,
        ).pack(pady=(16, 8))
