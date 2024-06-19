"""Theme validation utilities for WCAG contrast compliance.

This module provides functions to validate theme colors and generate
warnings when contrast ratios don't meet accessibility standards.
"""

from charted.utils.color_manager import ColorManager


def validate_theme(theme) -> list[str]:
    """Validate theme colors for WCAG contrast compliance.

    Checks:
    - Title color vs background
    - Legend text vs background
    - Grid lines vs background

    Args:
        theme: Theme object with color properties (must have title_color,
               legend_position, grid_color, background_color attributes).

    Returns:
        List of warning messages (empty if all pass).
    """
    manager = ColorManager()
    return manager.validate_theme(theme)


def validate_color_contrast(
    fg_color: str, bg_color: str, min_ratio: float = 4.5
) -> tuple[bool, float]:
    """Validate contrast ratio between foreground and background colors.

    Args:
        fg_color: Foreground color in hex format.
        bg_color: Background color in hex format.
        min_ratio: Minimum required contrast ratio (default: 4.5 for WCAG AA).

    Returns:
        Tuple of (passes, ratio) where passes is True if ratio >= min_ratio.
    """
    manager = ColorManager()
    ratio = manager.validate_contrast(fg_color, bg_color, min_ratio)
    return ratio >= min_ratio, ratio


def get_accessible_text_color(
    bg_color: str, dark_colors: list[str], light_colors: list[str]
) -> str:
    """Get an accessible text color for a given background.

    Tests each candidate color in order and returns the first that passes
    contrast validation, or the last one as fallback.

    Args:
        bg_color: Background color in hex format.
        dark_colors: List of dark text colors to try (in priority order).
        light_colors: List of light text colors to try (in priority order).

    Returns:
        An accessible text color (hex format).
    """
    manager = ColorManager()

    # Try dark colors first
    for color in dark_colors:
        if manager.validate_contrast(color, bg_color):
            return color

    # Try light colors
    for color in light_colors:
        if manager.validate_contrast(color, bg_color):
            return color

    # Fallback to first dark color (may not pass)
    return dark_colors[0] if dark_colors else "#000000"
