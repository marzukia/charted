"""Color management utilities for charted charts.

This module provides a ColorManager class for automatic color cycling,
palette expansion, and contrast validation.
"""

from typing import List, Optional

from charted.utils.colors import calculate_contrast_ratio


class ColorManager:
    """Manages color palettes with automatic cycling and expansion.

    Provides utilities for:
    - Cycling through colors with `get_color(index)`
    - Expanding palettes beyond 5 colors using HSL generation
    - Validating contrast ratios for WCAG compliance

    Args:
        colors: Initial list of hex color strings.
        min_colors: Minimum palette size before expansion (default: 5).

    Example:
        >>> manager = ColorManager(colors=["#ff0000", "#00ff00"])
        >>> manager.get_color(0)  # First color
        '#ff0000'
        >>> manager.get_color(10)  # Cycles back after 2 colors
        '#ff0000'
    """

    def __init__(self, colors: Optional[List[str]] = None, min_colors: int = 5):
        self._colors: List[str] = colors if colors else []
        self._min_colors = min_colors

    def get_color(self, index: int) -> str:
        """Get color at index, cycling through the palette.

        Args:
            index: Zero-based index into the palette.

        Returns:
            Hex color string.
        """
        if not self._colors:
            return "#5fab9e"  # Default fallback

        return self._colors[index % len(self._colors)]

    def ensure_palette_size(self, min_colors: int) -> List[str]:
        """Expand palette if more colors are needed.

        Uses HSL cycling to generate additional distinct colors when
        the requested size exceeds available colors.

        Args:
            min_colors: Minimum number of colors required.

        Returns:
            Expanded color list (original + generated if needed).
        """
        if len(self._colors) >= min_colors:
            return self._colors.copy()

        base_colors = self._colors.copy()
        extra_count = min_colors - len(base_colors)

        for i in range(extra_count):
            hue = int((i * 360 / min_colors) % 360)
            base_colors.append(f"hsl({hue}, 70%, 50%)")

        return base_colors

    def generate_hsl_colors(
        self, count: int, saturation: int = 70, lightness: int = 50
    ) -> List[str]:
        """Generate HSL-based colors for large palettes.

        Args:
            count: Number of colors to generate.
            saturation: HSL saturation percentage (0-100).
            lightness: HSL lightness percentage (0-100).

        Returns:
            List of HSL color strings.
        """
        colors = []
        for i in range(count):
            hue = int((i * 360 / count) % 360)
            colors.append(f"hsl({hue}, {saturation}%, {lightness}%)")
        return colors

    def validate_contrast(
        self, foreground: str, background: str, min_ratio: float = 4.5
    ) -> float:
        """Check if contrast ratio meets WCAG minimum.

        Args:
            foreground: Text/icon color (hex).
            background: Background color (hex).
            min_ratio: Minimum contrast ratio (default: 4.5 for AA).

        Returns:
            Contrast ratio value.
        """
        ratio = calculate_contrast_ratio(foreground, background)
        return ratio

    def validate_theme(self, theme) -> List[str]:
        """Validate theme colors for WCAG contrast compliance.

        Args:
            theme: Theme object with color properties.

        Returns:
            List of warning messages (empty if all pass).
        """
        warnings = []

        # Check title vs background
        if hasattr(theme, "title_color") and hasattr(theme, "background_color"):
            ratio = self.validate_contrast(theme.title_color, theme.background_color)
            if ratio < 4.5:
                warnings.append(
                    f"Title color '{theme.title_color}' has insufficient contrast "
                    f"against background '{theme.background_color}' (ratio: {ratio:.1f})"
                )

        # Check grid vs background
        if hasattr(theme, "grid_color") and hasattr(theme, "background_color"):
            ratio = self.validate_contrast(theme.grid_color, theme.background_color)
            if theme.grid_visible and ratio < 4.5:
                warnings.append(
                    f"Grid color '{theme.grid_color}' has insufficient contrast "
                    f"against background '{theme.background_color}' (ratio: {ratio:.1f})"
                )

        # Check legend text vs background
        if hasattr(theme, "legend_position") and hasattr(theme, "background_color"):
            legend_colors = ["#444444", "#666666", "#333333"]
            has_accessible = False
            for color in legend_colors:
                if self.validate_contrast(color, theme.background_color) >= 4.5:
                    has_accessible = True
                    break
            if not has_accessible:
                warnings.append(
                    "Legend text colors may have insufficient contrast "
                    f"against background '{theme.background_color}'"
                )

        return warnings
