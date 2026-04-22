from __future__ import annotations

import queue
import threading
import tkinter.messagebox as messagebox
import weakref
from typing import Iterable, List

import customtkinter as ctk

from acat.backend.judge_score import LanguageModel, generate_praat_score
from acat.ui.audio_file import AudioFileInfo
from acat.ui.result_popup import ResultPopup
from acat.ui.window_management import get_main_window

# Column definitions: (header text, width, anchor)
_COLUMNS = [
    ("File Name",   320, "w"),
    ("Duration",     80, "center"),
    ("Comp Score",  110, "center"),
    ("Nat Score",   110, "center"),
    ("Actions",     210, "center"),
]


class ContentTable(ctk.CTkScrollableFrame):
    """Scrollable table listing loaded audio files and their scores."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.data: List[AudioFileInfo] = []
        self._rows: List[dict] = []
        self._queue: queue.Queue = queue.Queue()
        self._popup = ResultPopup()
        self._active_popup_file: AudioFileInfo | None = None

        self._build_header()
        self._poll_queue()

    # ── header ──────────────────────────────────────────────────────────────

    def _build_header(self) -> None:
        for col, (text, width, anchor) in enumerate(_COLUMNS):
            lbl = ctk.CTkLabel(
                self, text=text,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=width, anchor=anchor,
            )
            lbl.grid(row=0, column=col, padx=4, pady=(4, 6), sticky="w")
            self.grid_columnconfigure(col, weight=1 if col == 0 else 0)

        sep = ctk.CTkFrame(self, height=2, fg_color=("gray70", "gray40"))
        sep.grid(row=1, column=0, columnspan=len(_COLUMNS), sticky="ew", padx=2, pady=(0, 4))

    # ── queue polling (safe UI updates from background threads) ─────────────

    def _poll_queue(self) -> None:
        try:
            while True:
                callback = self._queue.get_nowait()
                callback()
        except queue.Empty:
            pass
        self.after(100, self._poll_queue)

    # ── adding rows ─────────────────────────────────────────────────────────

    def add_row(self, audio_info: AudioFileInfo) -> None:
        idx = len(self.data)
        grid_row = idx + 2  # offset for header + separator

        fname = ctk.CTkLabel(
            self, text=audio_info.file_name,
            width=_COLUMNS[0][0], anchor="w",
            font=ctk.CTkFont(size=12),
        )
        fname.grid(row=grid_row, column=0, padx=(4, 8), pady=3, sticky="w")

        dur = ctk.CTkLabel(
            self, text=audio_info.audio_length_str,
            width=_COLUMNS[1][1], anchor="center",
            font=ctk.CTkFont(size=12),
            text_color=("gray40", "gray60"),
        )
        dur.grid(row=grid_row, column=1, padx=4, pady=3)

        comp = ctk.CTkLabel(
            self, text="N/A",
            width=_COLUMNS[2][1], anchor="center",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50"),
        )
        comp.grid(row=grid_row, column=2, padx=4, pady=3)

        nat = ctk.CTkLabel(
            self, text="N/A",
            width=_COLUMNS[3][1], anchor="center",
            font=ctk.CTkFont(size=12),
            text_color=("gray50", "gray50"),
        )
        nat.grid(row=grid_row, column=3, padx=4, pady=3)

        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.grid(row=grid_row, column=4, padx=4, pady=3)

        judge_btn = ctk.CTkButton(
            action_frame, text="Judge", width=65, height=28,
            font=ctk.CTkFont(size=12),
            command=lambda i=idx: self.judge_score(i),
        )
        judge_btn.pack(side="left", padx=2)

        info_btn = ctk.CTkButton(
            action_frame, text="Info", width=52, height=28,
            font=ctk.CTkFont(size=12),
            fg_color=("gray60", "gray40"), hover_color=("gray50", "gray30"),
            command=lambda i=idx: self.open_info(i),
        )
        info_btn.pack(side="left", padx=2)

        del_btn = ctk.CTkButton(
            action_frame, text="Delete", width=65, height=28,
            font=ctk.CTkFont(size=12),
            fg_color="#b03030", hover_color="#8a2020",
            command=lambda i=idx: self.delete_row(i),
        )
        del_btn.pack(side="left", padx=2)

        self.data.append(audio_info)
        self._rows.append({
            "fname": fname, "dur": dur, "comp": comp, "nat": nat,
            "action_frame": action_frame,
            "judge_btn": judge_btn, "info_btn": info_btn, "del_btn": del_btn,
            "grid_row": grid_row,
        })

    def add_rows(self, rows: Iterable[AudioFileInfo]) -> None:
        for row in rows:
            self.add_row(row)

    # ── row actions ─────────────────────────────────────────────────────────

    def delete_row(self, idx: int) -> None:
        if not self._valid(idx):
            return
        r = self._rows[idx]
        for w in (r["fname"], r["dur"], r["comp"], r["nat"], r["action_frame"]):
            w.destroy()
        self.data.pop(idx)
        self._rows.pop(idx)
        self._reindex()

    def open_info(self, idx: int) -> None:
        if not self._valid(idx):
            return
        audio_info = self.data[idx]
        self._active_popup_file = audio_info
        self._popup.update_content(audio_info)
        self._popup.show_centered(get_main_window())

    def judge_score(self, idx: int, model: LanguageModel | None = None) -> None:
        if not self._valid(idx):
            return
        if model is None:
            model = get_main_window().get_current_model()

        audio_info = self.data[idx]

        if audio_info.score is not None:
            if not messagebox.askyesno(
                "Reanalyze?",
                f'"{audio_info.file_name}" has already been analyzed.\nReanalyze it?',
            ):
                return

        if not audio_info.path.exists():
            messagebox.showerror("File not found", f"Cannot find:\n{audio_info.path}")
            return

        # Show in-progress state
        self._rows[idx]["comp"].configure(text="…", text_color=("gray50", "gray50"))
        self._rows[idx]["nat"].configure(text="…", text_color=("gray50", "gray50"))
        self._rows[idx]["judge_btn"].configure(state="disabled")

        ref = weakref.ref(audio_info)

        def _run() -> None:
            data = ref()
            if data is None:
                return
            try:
                data.score = generate_praat_score(data.path, model)
            except Exception as exc:
                self._queue.put(
                    lambda e=exc, n=data.file_name: messagebox.showerror(
                        "Analysis Error", f"Error analysing {n}:\n{e}"
                    )
                )
                self._queue.put(lambda i=idx: self._reset_score_labels(i))
                return
            self._queue.put(lambda i=idx, d=data: self._update_score(i, d))

        threading.Thread(target=_run, daemon=True).start()

    def judge_all_scores(self, model: LanguageModel | None = None) -> None:
        if model is None:
            model = get_main_window().get_current_model()

        already = [d.file_name for d in self.data if d.score is not None]
        if already:
            names = "\n".join(already)
            if not messagebox.askyesno(
                "Reanalyze?",
                f"These files have already been analysed:\n{names}\n\nReanalyze them?",
            ):
                return

        for i in range(len(self.data)):
            self.judge_score(i, model)

    # ── internal helpers ─────────────────────────────────────────────────────

    def _valid(self, idx: int) -> bool:
        return 0 <= idx < len(self.data)

    def _reset_score_labels(self, idx: int) -> None:
        if not self._valid(idx):
            return
        self._rows[idx]["comp"].configure(text="N/A", text_color=("gray50", "gray50"))
        self._rows[idx]["nat"].configure(text="N/A", text_color=("gray50", "gray50"))
        self._rows[idx]["judge_btn"].configure(state="normal")

    def _update_score(self, idx: int, data: AudioFileInfo) -> None:
        if not self._valid(idx) or self.data[idx] is not data:
            return
        r = self._rows[idx]
        green = ("#1a6e38", "#3eb86a")
        r["comp"].configure(text=data.comprehensibility_str, text_color=green)
        r["nat"].configure(text=data.nativelikeness_str, text_color=green)
        r["judge_btn"].configure(state="normal")

        # Refresh popup if it's showing this file
        if self._active_popup_file is data and self._popup.winfo_viewable():
            self._popup.update_content(data)

    def _reindex(self) -> None:
        """Re-grid all rows and fix button commands after a deletion."""
        for i, (r, _) in enumerate(zip(self._rows, self.data)):
            gr = i + 2
            r["grid_row"] = gr
            r["fname"].grid(row=gr, column=0)
            r["dur"].grid(row=gr, column=1)
            r["comp"].grid(row=gr, column=2)
            r["nat"].grid(row=gr, column=3)
            r["action_frame"].grid(row=gr, column=4)
            r["judge_btn"].configure(command=lambda i=i: self.judge_score(i))
            r["info_btn"].configure(command=lambda i=i: self.open_info(i))
            r["del_btn"].configure(command=lambda i=i: self.delete_row(i))


class ContentView(ctk.CTkFrame):
    """Outer frame that holds the ContentTable."""

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.table = ContentTable(self)
        self.table.pack(fill="both", expand=True, padx=8, pady=8)
