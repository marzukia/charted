"""Core Theme dataclass and ColorPalette for charted."""

import re
from dataclasses import dataclass, field, replace
from typing import Optional


def _is_valid_hex_color(color: str) -> bool:
    """Validate color format (hex, HSL, or HSLA).

    Supports:
    - Hex colors: #RGB, #RRGGBB, #RRGGBBAA
    - HSL: hsl(h, s%, l%)
    - HSLA: hsla(h, s%, l%, a)
    """
    if not isinstance(color, str):
        return False

    # Check for hex format
    hex_pattern = r"^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$"
    if re.match(hex_pattern, color):
        return True

    # Check for HSL/HSLA format
    hsl_pattern = r"^hsla?\(\s*\d+\s*,\s*\d+%\s*,\s*\d+%\s*(,\s*[\d.]+\s*)?\)$"
    if re.match(hsl_pattern, color):
        return True

    return False


@dataclass(frozen=True)
class ColorPalette:
    """A frozen color palette with automatic cycling.

    Args:
        colors: List of hex color strings. Defaults to light theme colors.
    """

    colors: list[str] = field(
        default_factory=lambda: ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]
    )

    def get_color(self, index: int) -> str:
        """Get color at index, cycling through the palette.

        Args:
            index: Zero-based index into the palette.

        Returns:
            Hex color string.
        """
        return self.colors[index % len(self.colors)]

    def expand(self, min_colors: int) -> "ColorPalette":
        """Expand palette if more colors are needed.

        Uses HSL cycling to generate additional distinct colors.

        Args:
            min_colors: Minimum number of colors required.

        Returns:
            New ColorPalette with expanded colors.
        """
        if len(self.colors) >= min_colors:
            return self

        base_colors = self.colors.copy()
        extra_count = min_colors - len(base_colors)

        for i in range(extra_count):
            hue = int((i * 360 / min_colors) % 360)
            base_colors.append(f"hsl({hue}, 70%, 50%)")

        return ColorPalette(colors=base_colors)


@dataclass(frozen=True)
class Theme:
    """Immutable theme configuration for charted charts.

    Use `from_preset()` to load built-in themes, or construct directly
    for custom themes. Use `compose()` to layer customizations on top
    of presets.

    Args:
        colors: Color palette (list of hex strings). Empty = use defaults.
        grid_color: Grid line color.
        grid_dasharray: Dash pattern for grid lines (e.g., "2,2").
        grid_visible: Whether grid lines are visible.
        legend_position: Legend position ("topright", "topleft", etc.).
        legend_font_size: Font size for legend text.
        legend_font_family: Font family for legend text.
        legend_font_color: Color for legend text.
        title_color: Color for chart title.
        title_font_size: Font size for title.
        title_font_family: Font family for title.
        background_color: Background color for chart area.
        h_padding: Horizontal padding as fraction of chart width.
        v_padding: Vertical padding as fraction of chart height.

    Raises:
        ValueError: If any color value is invalid or contrast is insufficient.
    """

    colors: list[str] = field(
        default_factory=lambda: ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"]
    )
    grid_color: str = "#CCCCCC"
    grid_dasharray: Optional[str] = None
    grid_visible: bool = True
    legend_position: str = "topright"
    legend_font_size: int = 11
    legend_font_family: str = "Arial"
    legend_font_color: str = "#444444"
    title_color: str = "#444444"
    title_font_size: int = 16
    title_font_family: str = "Arial"
    background_color: str = "#FFFFFF"
    h_padding: float = 0.05
    v_padding: float = 0.05
    marker_size: float = 3.0

    def __post_init__(self) -> None:
        """Validate color format after initialization."""
        for color in self.colors:
            if not _is_valid_hex_color(color):
                raise ValueError(f"Invalid color in palette: {color!r}")

        if not _is_valid_hex_color(self.grid_color):
            raise ValueError(f"Invalid color for grid_color: {self.grid_color!r}")
        if not _is_valid_hex_color(self.title_color):
            raise ValueError(f"Invalid color for title_color: {self.title_color!r}")
        if not _is_valid_hex_color(self.legend_font_color):
            raise ValueError(
                f"Invalid color for legend_font_color: {self.legend_font_color!r}"
            )
        if not _is_valid_hex_color(self.background_color):
            raise ValueError(
                f"Invalid color for background_color: {self.background_color!r}"
            )

        # Validate legend contrast against background
        from charted.utils.colors import calculate_contrast_ratio

        contrast = calculate_contrast_ratio(
            self.legend_font_color, self.background_color
        )
        if contrast < 4.5:
            raise ValueError(
                f"Legend font color contrast ratio ({contrast:.2f}) is below WCAG AA threshold (4.5)"
            )

    @classmethod
    def from_preset(cls, name: str) -> "Theme":
        """Load a built-in preset theme.

        Args:
            name: Preset name ("light", "dark", "high-contrast").

        Returns:
            Theme instance with preset values.

        Raises:
            ValueError: If preset name is unknown.
        """
        presets = {
            "light": cls(
                colors=["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899"],
                title_color="#1f2937",
                grid_color="#6b7280",
                background_color="#f9fafb",
            ),
            "dark": cls(
                colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
                grid_color="#9ca3af",
                title_color="#ffffff",
                background_color="#1a1a1a",
                legend_font_color="#e5e5e5",
            ),
            "high-contrast": cls(
                colors=["#000000", "#FFFF00", "#00FFFF", "#FF00FF", "#00FF00"],
                title_color="#000000",
                background_color="#FFFFFF",
                grid_color="#000000",
            ),
        }
        if name not in presets:
            raise ValueError(
                f"Unknown theme: {name!r}. Available: {list(presets.keys())}"
            )
        return presets[name].__copy__()

    def __copy__(self) -> "Theme":
        """Create a copy of this theme."""
        return replace(self)

    def compose(self, overrides: Optional["Theme"] = None) -> "Theme":
        """Create a new theme by merging self with overrides.

        Only explicitly set (non-default) values from overrides are applied.
        This preserves the base theme's custom values when composing.

        Args:
            overrides: Theme with values to override. Can be None.

        Returns:
            New Theme instance with merged values.

        Example:
            >>> base = Theme.from_preset("light")
            >>> custom = base.compose(Theme(colors=["#ff0000"]))
            >>> custom.colors  # Override applied
            ["#ff0000"]
            >>> custom.title_color  # Inherited from base
            "#1f2937"
        """
        if overrides is None:
            return self.__copy__()

        new_values = {}
        overrides_dict = vars(overrides)

        for key, override_value in overrides_dict.items():
            if key == "colors":
                if override_value and len(override_value) > 0:
                    new_values[key] = override_value.copy()
            else:
                class_default = getattr(Theme, key, None)

                if override_value == class_default:
                    continue

                new_values[key] = override_value

        if not new_values:
            return self.__copy__()

        base_dict = vars(self)
        merged = {**base_dict, **new_values}

        return Theme(**merged)

    def cycle_color(self, index: int) -> str:
        """Get color at index, cycling through the palette.

        Args:
            index: Zero-based index into the palette.

        Returns:
            Hex color string.
        """
        palette = ColorPalette(colors=self.colors)
        return palette.get_color(index)


# Backward compatibility aliases
LegacyThemeDict = dict  # Deprecated - use Theme instead
