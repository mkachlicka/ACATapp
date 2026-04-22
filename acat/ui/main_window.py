from __future__ import annotations

import pathlib
import tkinter as tk
import tkinter.filedialog as filedialog
import tkinter.messagebox as messagebox

import customtkinter as ctk
import pandas as pd

from acat.backend.judge_score import LanguageModel
from acat.ui.audio_file import AudioFileInfo, PraatScore
from acat.ui.content_view import ContentView
from acat.ui.help_window import HelpWindow
from acat.ui.ModelChooser import ModelComboChooser


class MainWindow(ctk.CTk):
    """Main application window — replaces the PyQt6 QMainWindow."""

    def __init__(self) -> None:
        super().__init__()
        self.title("ACAT – Automated Comprehensibility Assessment Tool")
        self.geometry("960x620")
        self.minsize(720, 440)

        self._help_window: HelpWindow | None = None

        self._make_toolbar()
        self._make_content()

        # Show help a moment after startup so the main window renders first
        self.after(350, self._show_help_window)

    # ── toolbar ─────────────────────────────────────────────────────────────

    def _make_toolbar(self) -> None:
        bar = ctk.CTkFrame(self, height=48, corner_radius=0)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)

        def tb_btn(text: str, cmd, primary: bool = True, **kw) -> ctk.CTkButton:
            colors = {} if primary else {
                "fg_color": ("gray55", "gray35"),
                "hover_color": ("gray45", "gray25"),
            }
            btn = ctk.CTkButton(bar, text=text, height=32,
                                 font=ctk.CTkFont(size=13),
                                 command=cmd, **colors, **kw)
            btn.pack(side="left", padx=(0, 2), pady=8)
            return btn

        def sep():
            ctk.CTkFrame(bar, width=1, height=28,
                          fg_color=("gray70", "gray40")).pack(
                side="left", padx=6, pady=10)

        ctk.CTkFrame(bar, width=8, height=1,
                      fg_color="transparent").pack(side="left")  # left margin

        tb_btn("Choose Audio", self._choose_file, width=120)
        sep()
        tb_btn("Judge All", self._judge_all, width=100)
        sep()
        tb_btn("Export CSV", self._export_csv, primary=False, width=100)
        sep()
        tb_btn("Help", self._show_help_window, primary=False, width=70)
        sep()

        ctk.CTkLabel(bar, text="Model:", font=ctk.CTkFont(size=13)).pack(
            side="left", padx=(2, 4), pady=8)
        self._model_box = ModelComboChooser(bar, width=130)
        self._model_box.pack(side="left", padx=4, pady=8)

    # ── content area ─────────────────────────────────────────────────────────

    def _make_content(self) -> None:
        self._content_view = ContentView(self, fg_color="transparent")
        self._content_view.pack(fill="both", expand=True)

    # ── actions ──────────────────────────────────────────────────────────────

    def _show_help_window(self) -> None:
        if self._help_window is None:
            self._help_window = HelpWindow()
        self._help_window.show_centered(self)

    def _choose_file(self) -> None:
        files = filedialog.askopenfilenames(
            title="Select Audio Files",
            filetypes=[
                ("Audio Files", "*.wav *.mp3 *.aiff *.flac *.ogg"),
                ("All Files", "*.*"),
            ],
        )
        for f in files:
            try:
                info = AudioFileInfo(pathlib.Path(f))
                self._content_view.table.add_row(info)
            except Exception as exc:
                messagebox.showerror("Load Error", f"Could not load:\n{f}\n\n{exc}")

    def _judge_all(self) -> None:
        self._content_view.table.judge_all_scores(self.get_current_model())

    def get_current_model(self) -> LanguageModel:
        return self._model_box.get_model()

    def _export_csv(self) -> None:
        table = self._content_view.table
        if not table.data:
            messagebox.showinfo("No Data", "No files have been loaded yet.")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
        )
        if not file_path:
            return

        rows = []
        for af in table.data:
            all_data = PraatScore.all_data_or_none(af.score)
            rows.append([af.file_name, str(af.path), *all_data])

        df = pd.DataFrame(
            rows,
            columns=[
                "File Name", "File Path",
                "Comprehensibility Score", "Nativelikeness Score",
                "speechrate", "pauses", "rangef0",
                "sdsylldur", "coeff1", "coeff2", "coeff3",
            ],
        )
        df.to_csv(file_path, index=False)
        messagebox.showinfo("Exported", f"Results saved to:\n{file_path}")

    def show_window(self, widget) -> None:
        """Compatibility shim — show any SubWindow centred on main window."""
        widget.show_centered(self)
