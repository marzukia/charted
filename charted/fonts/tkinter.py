"""Tkinter-based text measurement utilities.

Provides TextMeasurer for measuring text dimensions using tkinter.
Gracefully handles environments where tkinter is not available.
"""

try:
    import tkinter as tk
    from tkinter import font as tkfont

    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    tk = None  # type: ignore
    tkfont = None  # type: ignore


class TextMeasurer:
    """Context manager for measuring text dimensions using tkinter.

    This is used in `create_font_definition` but not at runtime,
    avoiding a hard dependency on tkinter for the end user.
    """

    def __init__(self) -> None:
        if not TKINTER_AVAILABLE:
            raise ImportError(
                "tkinter is not available. TextMeasurer requires tkinter."
            )
        self.root: tk.Tk | None = None

    def __enter__(self) -> "TextMeasurer":
        self.root = tk.Tk()
        self.root.withdraw()
        return self

    def measure_text(
        self,
        text: str,
        family: str = "Helvetica",
        size: int = 12,
        weight: str = "normal",
    ) -> tuple[float, float]:
        if self.root is None:
            raise RuntimeError("TextMeasurer must be used within a 'with' statement")
        font = tkfont.Font(family=family, size=size, weight=weight)

        canvas = tk.Canvas(self.root)
        text_id = canvas.create_text(0, 0, text=text, font=font, anchor="nw")
        bbox = canvas.bbox(text_id)
        height = bbox[3] - bbox[1]

        return font.measure(text), height

    def __exit__(self, *args, **kwargs) -> None:
        if self.root:
            self.root.destroy()
            self.root = None
