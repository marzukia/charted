import colorsys
import re
from typing import Generator


def _hsl_to_rgb(hsl: str) -> tuple[int, int, int]:
    """Convert HSL or HSLA color string to RGB tuple.

    Args:
        hsl: HSL color string (e.g., 'hsl(120, 70%, 50%)' or 'hsla(240, 60%, 40%, 0.8)')

    Returns:
        Tuple of (R, G, B) values 0-255

    Raises:
        ValueError: If HSL string is invalid
    """
    # Remove 'hsl' or 'hsla' prefix and parentheses
    hsl = hsl.strip().lower()
    if hsl.startswith("hsla"):
        hsl = hsl[4:]
    elif hsl.startswith("hsl"):
        hsl = hsl[3:]
    else:
        raise ValueError(f"Invalid HSL format: {hsl}")

    # Parse values - handle "(h, s%, l%)" or "(h, s%, l%, a)" format
    match = re.match(r"[(](\d+)\s*,\s*(\d+)%\s*,\s*(\d+)%\s*(,\s*[\d.]+\s*)?[)]", hsl)
    if not match:
        raise ValueError(f"Invalid HSL format: {hsl}")

    h, s, lightness = int(match.group(1)), int(match.group(2)), int(match.group(3))

    # Convert to RGB using colorsys
    h_norm = h / 360.0
    s_norm = s / 100.0
    l_norm = lightness / 100.0

    r, g, b = colorsys.hls_to_rgb(h_norm, l_norm, s_norm)

    return (int(r * 255), int(g * 255), int(b * 255))


def _parse_color_to_rgb(color: str) -> tuple[int, int, int]:
    """Parse any color format (hex or HSL) to RGB tuple.

    Args:
        color: Color string in hex or HSL/HSLA format

    Returns:
        Tuple of (R, G, B) values 0-255
    """
    color = color.strip()
    if color.startswith("hsl"):
        return _hsl_to_rgb(color)
    # Validate strictly here: hex_to_rgb is intentionally lenient (it accepts
    # hex without a leading '#'), but this is the public color-parsing path, so
    # an input that is not a well-formed '#'-prefixed hex (e.g. '000') must be
    # rejected rather than silently coerced.
    if not is_valid_hex_color(color):
        raise ValueError(f"Invalid color: {color!r}")
    return hex_to_rgb(color)


def is_valid_hex_color(color: str) -> bool:
    """Validate hex color format (#RGB, #RRGGBB, or #RRGGBBAA).

    Args:
        color: Color string to validate

    Returns:
        True if valid hex color format, False otherwise
    """
    if not isinstance(color, str):
        return False
    pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
    return bool(re.match(pattern, color))


def hex_to_rgb(hex: str) -> tuple[int, int, int]:
    """Convert hex color string to RGB tuple.

    Args:
        hex: Hex color string (e.g., '#FF5733', 'FF5733', '#FFF', or '#FFFFFFFF')

    Returns:
        Tuple of (R, G, B) values 0-255

    Raises:
        ValueError: If hex string is invalid or incorrect length
    """
    hex = hex.lstrip("#")

    # Handle 3-digit shorthand (#FFF -> #FFFFFF)
    if len(hex) == 3:
        hex = "".join(c * 2 for c in hex)
    # Handle 8-digit with alpha (#AARRGGBB -> #RRGGBB, ignore alpha)
    elif len(hex) == 8:
        hex = hex[2:]  # Skip alpha channel

    if len(hex) != 6:
        raise ValueError(
            f"Invalid hex color length: expected 3, 6, or 8 characters, got {len(hex)}"
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


def interpolate_color(a: str, b: str, t: float) -> str:
    """Linearly interpolate between two colors in RGB space.

    Args:
        a: Start color in hex or HSL format.
        b: End color in hex or HSL format.
        t: Position from 0.0 (a) to 1.0 (b). Values outside [0, 1] are clamped.
            NaN maps to 0.0 (the start color).

    Returns:
        6-digit hex color string.
    """
    if t != t:  # NaN guard: max/min won't clamp NaN
        t = 0.0
    t = max(0.0, min(1.0, t))
    r1, g1, b1 = _parse_color_to_rgb(a)
    r2, g2, b2 = _parse_color_to_rgb(b)
    return rgb_to_hex(
        (
            round(r1 + (r2 - r1) * t),
            round(g1 + (g2 - g1) * t),
            round(b1 + (b2 - b1) * t),
        )
    )


def interpolate_palette(palette_or_list, t: float) -> str:
    """Map t in [0, 1] to a color along a multi-stop gradient.

    The palette stops are spread evenly across [0, 1]. The value is
    interpolated within the segment it falls into.

    Args:
        palette_or_list: A named palette key (e.g. 'viridis') or a list of
            hex color stops.
        t: Position from 0.0 (first stop) to 1.0 (last stop). Clamped to range.

    Returns:
        6-digit hex color string.

    Raises:
        ValueError: If the palette resolves to an empty list of stops.
    """
    from charted.themes.core import resolve_palette

    if isinstance(palette_or_list, str):
        stops = resolve_palette(palette_or_list)
    else:
        stops = list(palette_or_list)

    if not stops:
        raise ValueError("Cannot interpolate an empty palette")
    if len(stops) == 1:
        return rgb_to_hex(_parse_color_to_rgb(stops[0]))

    t = max(0.0, min(1.0, t))
    n_segments = len(stops) - 1
    scaled = t * n_segments
    idx = int(scaled)
    if idx >= n_segments:
        idx = n_segments - 1
    local_t = scaled - idx
    return interpolate_color(stops[idx], stops[idx + 1], local_t)


def complementary_color(hex_color: str) -> str:
    """Calculate the complementary color (opposite on color wheel).

    Args:
        hex_color: Input color in hex format

    Returns:
        Complementary color in 6-digit hex format
    """
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


def calculate_contrast_ratio(color1: str, color2: str) -> float:
    """Calculate WCAG contrast ratio between two colors.

    Args:
        color1: First color in hex or HSL/HSLA format (e.g., '#FF5733' or 'hsl(120, 70%, 50%)').
        color2: Second color in hex or HSL/HSLA format.

    Returns:
        Contrast ratio value from 1.0 (same color) to 21.0 (black/white).
    """
    rgb1 = _parse_color_to_rgb(color1)
    rgb2 = _parse_color_to_rgb(color2)

    def get_luminance(rgb: tuple[int, int, int]) -> float:
        """Calculate relative luminance per WCAG formula."""

        def adjust_component(value: int) -> float:
            v = value / 255.0
            if v <= 0.03928:
                return v / 12.92
            return ((v + 0.055) / 1.055) ** 2.4

        r, g, b = rgb
        return (
            0.2126 * adjust_component(r)
            + 0.7152 * adjust_component(g)
            + 0.0722 * adjust_component(b)
        )

    l1 = get_luminance(rgb1)
    l2 = get_luminance(rgb2)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def enforce_contrast_floor(
    foreground: str,
    background: str,
    min_ratio: float,
) -> str:
    """Darken (or lighten) a foreground color until it meets a contrast floor.

    Returns a hex color whose WCAG contrast ratio against ``background`` is at
    least ``min_ratio``. If the foreground already passes, it is returned
    unchanged (re-encoded to 6-digit hex). Otherwise the color is shifted
    toward black on light backgrounds (or toward white on dark backgrounds) in
    small steps until the floor is met, falling back to pure black/white if the
    target is unreachable any other way.

    Args:
        foreground: Foreground color in hex or HSL format.
        background: Background color the contrast is measured against.
        min_ratio: Minimum acceptable WCAG contrast ratio (e.g. 3.0).

    Returns:
        A 6-digit hex foreground color meeting the contrast floor.
    """
    fr, fg, fb = _parse_color_to_rgb(foreground)
    current = rgb_to_hex((fr, fg, fb))
    if calculate_contrast_ratio(current, background) >= min_ratio:
        return current

    # Shift toward black on a light background, toward white on a dark one.
    bg_lum = (
        0.2126 * (_parse_color_to_rgb(background)[0] / 255)
        + 0.7152 * (_parse_color_to_rgb(background)[1] / 255)
        + 0.0722 * (_parse_color_to_rgb(background)[2] / 255)
    )
    target = (0, 0, 0) if bg_lum > 0.5 else (255, 255, 255)

    for i in range(1, 101):
        t = i / 100.0
        blended = (
            round(fr + (target[0] - fr) * t),
            round(fg + (target[1] - fg) * t),
            round(fb + (target[2] - fb) * t),
        )
        candidate = rgb_to_hex(blended)
        if calculate_contrast_ratio(candidate, background) >= min_ratio:
            return candidate

    return rgb_to_hex(target)


def derive_color(base_hex: str, opacity: float, background_hex: str = "#ffffff") -> str:
    """Derive a blended color from a base color, opacity, and background.

    Pre-blends the opacity into a solid 6-digit hex color for maximum
    compatibility (cairosvg doesn't support 8-digit hex).

    Args:
        base_hex: Base color in hex format (e.g., '#FF5733').
        opacity: Opacity value from 0.0 (transparent) to 1.0 (opaque).
        background_hex: Background color to blend against (default white).

    Returns:
        6-digit hex color string (e.g., '#cccccc').
    """
    r, g, b = hex_to_rgb(base_hex)
    br, bg_g, bb = hex_to_rgb(background_hex)
    blended_r = int(r * opacity + br * (1 - opacity))
    blended_g = int(g * opacity + bg_g * (1 - opacity))
    blended_b = int(b * opacity + bb * (1 - opacity))
    return "#{:02x}{:02x}{:02x}".format(blended_r, blended_g, blended_b)


def generate_complementary_colors(hex_colors: list[str]) -> Generator[str, None, None]:
    """Generate complementary colors for a list of input colors.

    Args:
        hex_colors: List of hex color strings

    Yields:
        Complementary color for each input color
    """
    for color in hex_colors:
        yield complementary_color(color)
