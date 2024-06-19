import json
import os

from charted.utils.defaults import BASE_DEFINITIONS_DIR
from charted.utils.helpers import nested_defaultdict


def create_font_definition(
    font: str,
    min_font_size: int = 8,
    max_font_size: int = 21,
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
