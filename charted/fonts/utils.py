import json
import math
import os
from typing import Union

from charted.utils.helpers import BASE_DIR, nested_defaultdict
from charted.utils.types import MeasuredText


BASE_DEFINITIONS_DIR = os.path.join(BASE_DIR, "charted", "fonts", "definitions")
DEFAULT_FONT = "Helvetica"
DEFAULT_FONT_SIZE = 12
DEFAULT_TITLE_FONT_SIZE = 15

if os.name == "nt":
    DEFAULT_FONT = "Arial"


def create_font_definition(
    font: str,
    min_font_size: int = 8,
    max_font_size: int = 16,
) -> None:
    from charted.fonts.tkinter import TextMeasurer

    chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+[]{}|;:\'",.<>?/\\"£¥€©®™✓•¶§±æøåßüñ¿¡çµ½¼¾×÷°ƒ∆≈∞Ω≠≤≥¬√πø∆¥¤¢₱₩₹₽℅ℓ№©℗℠℮∞‽ '
    lookup = nested_defaultdict()

    with TextMeasurer() as tm:
        for font_size in range(min_font_size, max_font_size):
            for char in chars:
                w, h = tm.measure_text(char, family=font, size=font_size)
                lookup[font_size][ord(char)]["width"] = w
                lookup[font_size][ord(char)]["height"] = h

        with open(os.path.join(BASE_DEFINITIONS_DIR, f"{font}.json"), "w") as dst:
            dst.write(json.dumps(lookup, indent=2))


def calculate_text_dimensions(
    text: str,
    font: str = DEFAULT_FONT,
    font_size: int = DEFAULT_FONT_SIZE,
) -> MeasuredText:
    with open(os.path.join(BASE_DEFINITIONS_DIR, f"{font}.json"), "r") as src:
        lookup = json.loads(src.read())[str(font_size)]
        ord_arr = [ord(char) for char in text]
        width = sum([lookup[str(ord_char)]["width"] for ord_char in ord_arr])
        height = max([lookup[str(ord_char)]["height"] for ord_char in ord_arr])
        return MeasuredText(text, width, height)


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
