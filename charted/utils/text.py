import math
from typing import Optional, Self, Union
import tkinter as tk
from tkinter import font as tkfont


class TextMeasurer:
    def __init__(self) -> None:
        self.root: Optional[tk.Tk] = None

    def __enter__(self: Self) -> Self:
        self.root = tk.Tk()
        self.root.withdraw()
        return self

    def measure_text(
        self,
        text: str,
        family: str = "Helvetica",
        size: int = 12,
        weight: str = "normal",
    ) -> int:
        if self.root is None:
            raise RuntimeError("TextMeasurer must be used within a 'with' statement")
        font = tkfont.Font(family=family, size=size, weight=weight)
        return font.measure(text)

    def __exit__(self, *args, **kwargs) -> None:
        if self.root:
            self.root.destroy()
            self.root = None


def calculate_rotation_angle(
    total_label_width: float,
    total_permissible_width: float,
) -> Union[float, None]:
    if total_label_width <= total_permissible_width:
        return None

    ratio = total_permissible_width / total_label_width
    if ratio > 1.0 or ratio < 0.0:
        raise ValueError("Invalid ratio: it should be between 0 and 1.")

    rotation_angle_radians = math.acos(ratio)
    rotation_angle_degrees = math.degrees(rotation_angle_radians)

    return rotation_angle_degrees
