import colorsys
from typing import Generator


def hex_to_rgb(hex: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple.

    Args:
        hex: Hex color string (e.g., '#FF5733' or 'FF5733')

    Returns:
        Tuple of (R, G, B) values 0-255

    Raises:
        ValueError: If hex string is invalid or incorrect length
    """
    hex = hex.lstrip("#")
    if len(hex) != 6:
        raise ValueError(
            f"Invalid hex color length: expected 6 characters, got {len(hex)}"
        )
    try:
        return tuple(int(hex[i : i + 2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError(f"Invalid hex color: {hex}")


def rgb_to_hex(rgb: tuple[int, int, int]) -> str:
    """Convert RGB tuple to hex color string.

    Args:
        rgb: Tuple of (R, G, B) values 0-255

    Returns:
        Hex color string (e.g., '#ff5733')

    Raises:
        ValueError: If any RGB value is outside 0-255 range
    """
    r, g, b = rgb
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError(f"RGB values must be 0-255, got ({r}, {g}, {b})")
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


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


def get_contrast_color(hex_color: str) -> str:
    """Return black or white text color for best contrast against the given background.

    Uses luminance calculation (WCAG formula) to determine if text should be
    black or white for optimal readability.

    Args:
        hex_color: Background color in hex format

    Returns:
        '#000000' for dark backgrounds, '#ffffff' for light backgrounds
    """
    rgb = hex_to_rgb(hex_color)
    # WCAG luminance formula
    luminance = (
        0.2126 * (rgb[0] / 255) + 0.7152 * (rgb[1] / 255) + 0.0722 * (rgb[2] / 255)
    )
    return "#000000" if luminance > 0.5 else "#ffffff"


def generate_complementary_colors(hex_colors: list[str]) -> Generator[str, None, None]:
    for color in hex_colors:
        yield complementary_color(color)
