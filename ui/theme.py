"""AJL-inspired color palette and tkinter styling."""

import tkinter as tk
from tkinter import ttk

ORANGE = "#F58220"
MAGENTA = "#92278F"
TEXT = "#333333"
TEXT_MUTED = "#666666"
WHITE = "#FFFFFF"
BG = "#F3F3F6"
CARD = "#FFFFFF"
BORDER = "#E4E4EA"
SUCCESS = "#2E9E5B"
ERROR = "#C0392B"

FONT_FAMILY = "Segoe UI"


def _hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)


def _rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def _blend(color_a: str, color_b: str, ratio: float) -> str:
    r1, g1, b1 = _hex_to_rgb(color_a)
    r2, g2, b2 = _hex_to_rgb(color_b)
    return _rgb_to_hex(
        int(r1 + (r2 - r1) * ratio),
        int(g1 + (g2 - g1) * ratio),
        int(b1 + (b2 - b1) * ratio),
    )


def draw_horizontal_gradient(
    canvas: tk.Canvas, width: int, height: int, left: str, right: str
) -> None:
    canvas.delete("gradient")
    steps = max(width, 1)
    for index in range(steps):
        color = _blend(left, right, index / steps)
        canvas.create_line(
            index, 0, index, height, fill=color, tags="gradient"
        )


def apply_theme(root: tk.Tk) -> ttk.Style:
    root.configure(bg=BG)

    style = ttk.Style(root)
    if "clam" in style.theme_names():
        style.theme_use("clam")

    style.configure(".", background=BG, foreground=TEXT, font=(FONT_FAMILY, 10))
    style.configure("TFrame", background=BG)
    style.configure("Card.TFrame", background=CARD)
    style.configure(
        "Card.TLabelframe",
        background=CARD,
        bordercolor=BORDER,
        relief="flat",
        borderwidth=1,
    )
    style.configure(
        "Card.TLabelframe.Label",
        background=CARD,
        foreground=TEXT,
        font=(FONT_FAMILY, 10, "bold"),
    )
    style.configure(
        "TLabel",
        background=BG,
        foreground=TEXT,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Card.TLabel",
        background=CARD,
        foreground=TEXT,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "Muted.TLabel",
        background=BG,
        foreground=TEXT_MUTED,
        font=(FONT_FAMILY, 9),
    )
    style.configure(
        "Header.TLabel",
        background=MAGENTA,
        foreground=WHITE,
        font=(FONT_FAMILY, 16, "bold"),
    )
    style.configure(
        "HeaderSub.TLabel",
        background=MAGENTA,
        foreground=WHITE,
        font=(FONT_FAMILY, 10),
    )
    style.configure(
        "TButton",
        background=WHITE,
        foreground=TEXT,
        bordercolor=BORDER,
        focusthickness=0,
        padding=(10, 6),
        font=(FONT_FAMILY, 10),
    )
    style.map(
        "TButton",
        background=[("active", "#FFF4EC"), ("pressed", "#FCE8D8")],
        bordercolor=[("active", ORANGE)],
    )
    style.configure(
        "Accent.TButton",
        background=ORANGE,
        foreground=WHITE,
        bordercolor=ORANGE,
        font=(FONT_FAMILY, 10, "bold"),
        padding=(12, 6),
    )
    style.map(
        "Accent.TButton",
        background=[("active", "#E67412"), ("pressed", MAGENTA), ("disabled", "#D8D8DE")],
        foreground=[("disabled", "#999999")],
        bordercolor=[("disabled", "#D8D8DE")],
    )
    style.configure(
        "Primary.TButton",
        background=MAGENTA,
        foreground=WHITE,
        bordercolor=MAGENTA,
        font=(FONT_FAMILY, 11, "bold"),
        padding=(16, 8),
    )
    style.map(
        "Primary.TButton",
        background=[("active", "#7A1F78"), ("pressed", ORANGE), ("disabled", "#D8D8DE")],
        foreground=[("disabled", "#999999")],
        bordercolor=[("disabled", "#D8D8DE")],
    )
    style.configure(
        "TCombobox",
        fieldbackground=WHITE,
        background=WHITE,
        foreground=TEXT,
        arrowcolor=MAGENTA,
        bordercolor=BORDER,
        padding=4,
    )
    style.configure(
        "TEntry",
        fieldbackground=WHITE,
        foreground=TEXT,
        bordercolor=BORDER,
        padding=4,
    )
    style.configure(
        "TProgressbar",
        background=ORANGE,
        troughcolor=BORDER,
        bordercolor=BORDER,
        lightcolor=ORANGE,
        darkcolor=MAGENTA,
        thickness=10,
    )

    return style


def style_listbox(listbox: tk.Listbox) -> None:
    listbox.configure(
        bg=WHITE,
        fg=TEXT,
        selectbackground=MAGENTA,
        selectforeground=WHITE,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ORANGE,
        relief="flat",
        borderwidth=0,
        font=(FONT_FAMILY, 10),
        activestyle="none",
    )


def style_log_text(text: tk.Text) -> None:
    text.configure(
        bg=WHITE,
        fg=TEXT,
        insertbackground=MAGENTA,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ORANGE,
        relief="flat",
        borderwidth=0,
        font=(FONT_FAMILY, 9),
        padx=8,
        pady=6,
    )
    text.tag_configure("ok", foreground=SUCCESS)
    text.tag_configure("fail", foreground=ERROR)
