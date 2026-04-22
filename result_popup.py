from __future__ import annotations

import customtkinter as ctk

from acat.ui.audio_file import AudioFileInfo
from acat.ui.rubrics import make_rubrics
from acat.ui.subwindow import SubWindow


class ResultPopup(SubWindow):
    """Popup showing detailed score info for a single audio file."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Score Details")
        self.geometry("720x560")
        self.minsize(600, 400)
        self.resizable(True, True)
        self._build_ui()

    def _build_ui(self) -> None:
        self._scroll = ctk.CTkScrollableFrame(self)
        self._scroll.pack(fill="both", expand=True, padx=10, pady=10)

        self._title_lbl = ctk.CTkLabel(
            self._scroll,
            text="Score Details",
            font=ctk.CTkFont(size=18, weight="bold"),
        )
        self._title_lbl.pack(anchor="w", padx=12, pady=(12, 6))

        self._comp_lbl = ctk.CTkLabel(
            self._scroll,
            text="Comprehensibility:  N/A",
            font=ctk.CTkFont(size=14),
        )
        self._comp_lbl.pack(anchor="w", padx=12, pady=2)

        self._nat_lbl = ctk.CTkLabel(
            self._scroll,
            text="Nativelikeness:  N/A",
            font=ctk.CTkFont(size=14),
        )
        self._nat_lbl.pack(anchor="w", padx=12, pady=2)

        make_rubrics(self._scroll)

        ctk.CTkButton(
            self._scroll,
            text="Close",
            width=100,
            command=self.withdraw,
        ).pack(pady=(16, 8))

    def update_content(self, audio_info: AudioFileInfo) -> ResultPopup:
        self._title_lbl.configure(text=f'Score of "{audio_info.file_name}"')
        self._comp_lbl.configure(
            text=f"Comprehensibility:  {audio_info.comprehensibility_str}"
        )
        self._nat_lbl.configure(
            text=f"Nativelikeness:  {audio_info.nativelikeness_str}"
        )
        self.title(f"Details – {audio_info.file_name}")
        return self
