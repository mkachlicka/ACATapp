import tkinter as tk
from tkinter import ttk

import customtkinter as ctk

COMP_DATA = {
    "2.171 – 3.409": "Low comprehensibility – inexperienced L2 learners (no immersion experience)",
    "3.492 – 4.308": "Mid comprehensibility – moderately experienced L2 learners (LOR 1 month to 5 years)",
    "5.378 – 6.147": "High comprehensibility – long-term L2 residents (LOR 6–18 years)",
    "7.6":            "Near-native L2 speaker (maximum)",
    "8.714 – 8.926":  "Native speakers of English",
}

NAT_DATA = {
    "1.445 – 1.955": "Low nativelikeness – inexperienced L2 learners (no immersion experience)",
    "2.312 – 3.053": "Mid nativelikeness – moderately experienced L2 learners (LOR 1 month to 5 years)",
    "3.852 – 4.668": "High nativelikeness – long-term L2 residents (LOR 6–18 years)",
    "6.9":           "Near-native L2 speaker (maximum)",
    "8.450 – 8.930": "Native speakers of English",
}


def make_rubrics(parent: ctk.CTkScrollableFrame | ctk.CTkFrame) -> None:
    """Add rubric tables to a given parent frame (packed layout)."""
    heading = ctk.CTkLabel(
        parent, text="How to Interpret Scores",
        font=ctk.CTkFont(size=15, weight="bold"),
    )
    heading.pack(anchor="w", padx=12, pady=(14, 6))

    comp_lbl = ctk.CTkLabel(
        parent, text="Comprehensibility Score",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    comp_lbl.pack(anchor="w", padx=12, pady=(4, 2))
    _rubric_table(parent, ["Score Range", "Suggested Interpretation"], COMP_DATA)

    nat_lbl = ctk.CTkLabel(
        parent, text="Nativelikeness Score",
        font=ctk.CTkFont(size=13, weight="bold"),
    )
    nat_lbl.pack(anchor="w", padx=12, pady=(12, 2))
    _rubric_table(parent, ["Score Range", "Suggested Interpretation"], NAT_DATA)


def _rubric_table(
    parent: ctk.CTkFrame,
    headers: list[str],
    data: dict[str, str],
) -> None:
    wrap = ctk.CTkFrame(parent, fg_color="transparent")
    wrap.pack(fill="x", padx=12, pady=(0, 4))

    style = ttk.Style()
    style.configure("Rubric.Treeview", rowheight=26)
    style.configure("Rubric.Treeview.Heading", font=("TkDefaultFont", 11, "bold"))

    tree = ttk.Treeview(
        wrap,
        columns=headers,
        show="headings",
        style="Rubric.Treeview",
        height=len(data),
        selectmode="none",
    )
    tree.heading(headers[0], text=headers[0])
    tree.heading(headers[1], text=headers[1])
    tree.column(headers[0], width=150, minwidth=120, anchor="center", stretch=False)
    tree.column(headers[1], width=520, anchor="w",      stretch=True)

    for score, interp in data.items():
        tree.insert("", "end", values=(score, interp))

    tree.pack(fill="x")
