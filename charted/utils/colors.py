import colorsys
from typing import Generator, Tuple, List


def hex_to_rgb(hex: str) -> Tuple[int, int, int]:
    hex = hex.lstrip("#")
    return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def complementary_color(hex_color: str) -> str:
    rgb = hex_to_rgb(hex_color)
    hsv = colorsys.rgb_to_hsv(
        r=rgb[0] / 255.0,
        g=rgb[1] / 255.0,
        b=rgb[2] / 255.0,
    )
    comp_hsv = ((hsv[0] + 0.5) % 1.0, hsv[1], hsv[2])
    comp_rgb = colorsys.hsv_to_rgb(*comp_hsv)
    comp_rgb = tuple(int(c * 255) for c in comp_rgb)
    return rgb_to_hex(comp_rgb)


def generate_complementary_colors(hex_colors: List[str]) -> Generator[str, None, None]:
    for color in hex_colors:
        yield complementary_color(color)
