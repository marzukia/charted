from typing import Optional, Tuple
import tkinter as tk
from tkinter import font as tkfont


class TextMeasurer:
    """This is ussed in `create_font_definition`. This is not used at runtime as I am trying to avoid
    creating a dependency on `tkinter`.
    """

    def __init__(self) -> None:
        self.root: Optional[tk.Tk] = None

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
    ) -> Tuple[float, float]:
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
