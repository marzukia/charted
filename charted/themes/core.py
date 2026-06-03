"""Core Theme dataclass and ColorPalette for charted."""

import re
from dataclasses import dataclass, field, replace
from typing import Optional

from charted.constants import REFERENCE_LINE_WIDTH


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


# Named color palettes for agent-friendly chart creation
NAMED_PALETTES = {
    "default": ["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    "viridis": ["#440154", "#3b5282", "#2198c0", "#90d584", "#fde725"],
    "ocean": ["#006994", "#48b5c4", "#7ec8a0", "#f4d03f", "#e67e22"],
    "categorical": [
        "#3b82f6",
        "#10b981",
        "#f59e0b",
        "#8b5cf6",
        "#ec4899",
        "#06b6d4",
        "#84cc16",
        "#f97316",
        "#6366f1",
        "#14b8a6",
    ],
    "rainbow": ["#ff0000", "#ff8800", "#ffff00", "#00ff00", "#0088ff", "#8800ff"],
    "monochrome": ["#1a1a1a", "#333333", "#555555", "#777777", "#999999"],
    "pastel": ["#ffb3ba", "#bae1ff", "#baffc9", "#ffffba", "#e8baff"],
    "sunset": ["#ff6b6b", "#ffa94d", "#ffd43b", "#69db69", "#4dabf7"],
    "forest": ["#2d6a4f", "#40916c", "#52b788", "#95d5b2", "#d8f3dc"],
    "inferno": ["#000004", "#1c1044", "#7e307a", "#e5612f", "#fca50a"],
    # Okabe-Ito colourblind-safe qualitative palette. Eight hues chosen to
    # stay distinguishable under the common forms of colour vision deficiency
    # (protanopia, deuteranopia, tritanopia).
    "okabe-ito": [
        "#e69f00",
        "#56b4e9",
        "#009e73",
        "#f0e442",
        "#0072b2",
        "#d55e00",
        "#cc79a7",
        "#000000",
    ],
}


def resolve_palette(palette_name: str | list[str] | None) -> list[str]:
    """Resolve a palette name to a color list, or pass through a raw list.

    Args:
        palette_name: Named palette key, list of hex strings, or None for default.

    Returns:
        List of hex color strings.

    Raises:
        ValueError: If the palette name is unknown.
    """
    if palette_name is None:
        return NAMED_PALETTES["default"].copy()
    if isinstance(palette_name, list):
        return list(palette_name)
    if palette_name in NAMED_PALETTES:
        return NAMED_PALETTES[palette_name].copy()
    raise ValueError(
        f"Unknown palette: {palette_name!r}. Available: {list(NAMED_PALETTES.keys())}"
    )


@dataclass(frozen=True)
class ColorScale:
    """A continuous color scale mapping a numeric domain to gradient colors.

    Unlike ColorPalette (discrete cycling), ColorScale interpolates smoothly
    between palette stops. Useful for heatmaps and value-driven fills.

    Args:
        palette: A named palette key (e.g. 'viridis') or a list of hex stops.
        domain: (min, max) range of input values, mapped to [0, 1].
    """

    palette: "str | list[str]" = "viridis"
    domain: tuple[float, float] = (0.0, 1.0)

    def normalize(self, value: float) -> float:
        """Map a domain value to [0, 1], clamped.

        The domain is treated as unordered: a reversed (hi, lo) domain
        produces the same mapping as (lo, hi). A NaN value maps to 0.0.
        """
        if value != value:  # NaN guard: max/min won't clamp NaN
            return 0.0
        lo, hi = sorted(self.domain)
        if hi == lo:
            return 0.0
        return max(0.0, min(1.0, (value - lo) / (hi - lo)))

    def __call__(self, value: float) -> str:
        """Return the hex color for a domain value."""
        from charted.utils.colors import interpolate_palette

        return interpolate_palette(self.palette, self.normalize(value))


def diverging_scale(
    low: str,
    mid: str,
    high: str,
    domain: tuple[float, float] = (0.0, 1.0),
) -> ColorScale:
    """Build a three-stop diverging color scale.

    The midpoint color sits at the center of the domain, with low and high
    colors at the extremes.

    Args:
        low: Color at the domain minimum.
        mid: Color at the domain center.
        high: Color at the domain maximum.
        domain: (min, max) range of input values.

    Returns:
        A ColorScale over the (low, mid, high) stops.
    """
    return ColorScale([low, mid, high], domain=domain)


@dataclass(frozen=True)
class ColorPalette:
    """A frozen color palette with automatic cycling.

    Args:
        colors: List of hex color strings. Defaults to light theme colors.
                 Can also pass a named palette string (e.g. 'viridis').
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


# Opacity tiers for deriving colors from root_color.
# Each key maps to a default opacity applied when the corresponding
# theme field is at its class default value.
OPACITY_TIERS = {
    "grid_color": 0.20,
    # Minor gridlines sit below the major grid so the structure recedes and
    # data plus the zero axis dominate.
    "minor_grid_color": 0.10,
    "axis_border_color": 0.60,
    # Reference lines (incl. the zero crosshair) must read above the grid in
    # every theme, so they sit well clear of the 0.20 grid tier.
    "reference_line_color": 0.75,
    "axis_title_color": 0.80,
    "label_color": 1.0,
    # Quadrant labels are a watermark, but 0.18 was illegible on the dark
    # background; 0.40 stays subtle on light while remaining readable on dark.
    "quadrant_label_color": 0.40,
    # Data labels sit on data points and should read clearly. 0.80 matches the
    # historical axis-title tier the labels previously borrowed.
    "data_label_color": 0.80,
}


@dataclass(frozen=True)
class Theme:
    """Immutable theme configuration for charted charts.

    Use `from_preset()` to load built-in themes, or construct directly
    for custom themes. Use `compose()` to layer customizations on top
    of presets.

    Args:
        colors: Color palette (list of hex strings). Empty = use defaults.
        root_color: Base color for deriving opacity-tiered colors.
        grid_color: Grid line color.
        grid_dasharray: Dash pattern for grid lines (e.g., "2,2").
        grid_visible: Whether grid lines are visible.
        legend_position: Legend position ("topright", "topleft", "bottomright", "bottomleft").
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
    root_color: str = "#000000"
    grid_color: str = "#CCCCCC"
    grid_dasharray: Optional[str] = None
    grid_visible: bool = True
    # Gridline hierarchy / weight control. Defaults reproduce the historical
    # single-weight grid (no minor lines, SVG-default stroke width).
    # grid_width: stroke width for major gridlines. None emits no stroke-width
    #   attribute, leaving the SVG default of 1.
    # minor_grid_divisions: number of subdivisions drawn between adjacent major
    #   gridlines. 0 disables minor gridlines entirely (current behaviour).
    # minor_grid_color: colour for minor gridlines. None derives a lighter tier
    #   from root_color so the minor grid recedes below the major grid.
    # minor_grid_width: stroke width for minor gridlines. None falls back to
    #   half the resolved major width.
    grid_width: Optional[float] = None
    minor_grid_divisions: int = 0
    minor_grid_color: Optional[str] = None
    minor_grid_width: Optional[float] = None
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
    arrow_color: str = "#555555"
    # Stroke width for reference lines (incl. the zero crosshair). These draw
    # on top of the grid as their own layer; a width above the grid line width
    # keeps them reading as the most prominent line. None falls back to the
    # library default (REFERENCE_LINE_WIDTH).
    reference_line_width: Optional[float] = None
    # Colour for data-point labels. None defers to the axis-title tier the
    # labels historically borrowed, keeping existing renders unchanged. Set a
    # hex/HSL string to give data labels their own themed colour.
    data_label_color: Optional[str] = None
    # Mandatory contrasting outline drawn around filled shapes (bars, columns,
    # stacked segments, pie/polar wedges, bubbles, box bodies). None (the
    # default) draws no outline, keeping existing renders byte-for-byte
    # identical. Set a hex/HSL string (the high-contrast preset uses black) to
    # separate adjacent same-ish fills without relying on colour alone.
    shape_outline_color: Optional[str] = None
    # Stroke width for the filled-shape outline. None falls back to 1px.
    shape_outline_width: Optional[float] = None
    # Default stroke width for plotted series lines (line/area/combo). None
    # keeps the historical 2px line stroke. The high-contrast preset raises
    # this so lines read clearly for low-vision users.
    series_stroke_width: Optional[float] = None
    # Font size and weight for axis tick labels. None keeps the library
    # default size (DEFAULT_FONT_SIZE) and an unweighted (normal) label. The
    # high-contrast preset enlarges and bolds these for legibility.
    axis_label_font_size: Optional[int] = None
    axis_label_font_weight: Optional[str] = None
    # Minimum WCAG contrast ratio enforced for foreground colours (the series
    # palette) against the background. None disables enforcement, leaving
    # palettes untouched. The high-contrast preset sets 3.0 so washed-out hues
    # like yellow/cyan on white are darkened until they clear the floor.
    contrast_floor: Optional[float] = None

    def __post_init__(self) -> None:
        """Validate color format after initialization."""
        for color in self.colors:
            if not _is_valid_hex_color(color):
                raise ValueError(f"Invalid color in palette: {color!r}")

        if not _is_valid_hex_color(self.root_color):
            raise ValueError(f"Invalid color for root_color: {self.root_color!r}")
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
        if not _is_valid_hex_color(self.arrow_color):
            raise ValueError(f"Invalid color for arrow_color: {self.arrow_color!r}")
        if self.data_label_color is not None and not _is_valid_hex_color(
            self.data_label_color
        ):
            raise ValueError(
                f"Invalid color for data_label_color: {self.data_label_color!r}"
            )
        if self.shape_outline_color is not None and not _is_valid_hex_color(
            self.shape_outline_color
        ):
            raise ValueError(
                f"Invalid color for shape_outline_color: {self.shape_outline_color!r}"
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

    def _is_explicit(self, field_name: str) -> bool:
        """Check if a field was explicitly set (differs from class default)."""
        class_default = self.__class__.__dataclass_fields__[field_name].default
        return getattr(self, field_name) != class_default

    @property
    def resolved_grid_color(self) -> str:
        """Grid color: explicit override or root_color at 20% opacity."""
        if self._is_explicit("grid_color"):
            return self.grid_color
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color, OPACITY_TIERS["grid_color"], self.background_color
        )

    @property
    def resolved_grid_width(self) -> Optional[float]:
        """Major gridline stroke width, or None for the SVG default."""
        return self.grid_width

    @property
    def resolved_minor_grid_color(self) -> str:
        """Minor gridline colour: explicit override or root_color at 10%."""
        if self.minor_grid_color is not None:
            return self.minor_grid_color
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color,
            OPACITY_TIERS["minor_grid_color"],
            self.background_color,
        )

    @property
    def resolved_minor_grid_width(self) -> float:
        """Minor gridline stroke width: explicit override or half the major."""
        if self.minor_grid_width is not None:
            return self.minor_grid_width
        major = self.resolved_grid_width
        base = major if major is not None else 1.0
        return base / 2.0

    @property
    def resolved_axis_border_color(self) -> str:
        """Axis border color: root_color at 60% opacity."""
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color, OPACITY_TIERS["axis_border_color"], self.background_color
        )

    @property
    def resolved_reference_line_color(self) -> str:
        """Reference line color: root_color at 50% opacity."""
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color,
            OPACITY_TIERS["reference_line_color"],
            self.background_color,
        )

    @property
    def resolved_reference_line_width(self) -> float:
        """Reference-line stroke width: explicit override or library default."""
        if self.reference_line_width is not None:
            return self.reference_line_width
        return REFERENCE_LINE_WIDTH

    @property
    def resolved_axis_title_color(self) -> str:
        """Axis title color: explicit override or root_color at 80% opacity."""
        if self._is_explicit("title_color"):
            return self.title_color
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color, OPACITY_TIERS["axis_title_color"], self.background_color
        )

    @property
    def resolved_label_color(self) -> str:
        """Label color: root_color at 100% opacity."""
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color, OPACITY_TIERS["label_color"], self.background_color
        )

    @property
    def resolved_data_label_color(self) -> str:
        """Data-label colour: explicit override or the axis-title tier.

        Defaulting to ``resolved_axis_title_color`` keeps existing data-label
        renders byte-for-byte identical when ``data_label_color`` is unset.
        """
        if self.data_label_color is not None:
            return self.data_label_color
        return self.resolved_axis_title_color

    @property
    def filled_shape_outline(self) -> tuple[Optional[str], float]:
        """Outline (stroke, width) for filled shapes, or (None, 1.0) when off.

        Returns the configured ``shape_outline_color`` (or None when unset) and
        the stroke width, defaulting to 1px. Charts call this and only emit a
        stroke when the colour is not None, so the default theme leaves filled
        shapes unstroked exactly as before.
        """
        width = (
            self.shape_outline_width if self.shape_outline_width is not None else 1.0
        )
        return self.shape_outline_color, width

    @property
    def resolved_series_stroke_width(self) -> float:
        """Series line stroke width: explicit override or the 2px default.

        The default is returned as ``int`` 2 so unstyled lines serialize to
        ``stroke-width="2"`` exactly as before (a float would emit ``2.0``).
        """
        if self.series_stroke_width is not None:
            return self.series_stroke_width
        return 2

    @property
    def resolved_axis_label_font_size(self) -> int:
        """Axis tick label font size: override or the library default (12)."""
        from charted.constants import AXIS_LABEL_FONT_SIZE

        if self.axis_label_font_size is not None:
            return self.axis_label_font_size
        return AXIS_LABEL_FONT_SIZE

    def enforce_contrast(self, foreground: str) -> str:
        """Apply ``contrast_floor`` to a foreground colour against background.

        Returns ``foreground`` unchanged when no floor is set; otherwise
        darkens/lightens it until it meets the floor against
        ``background_color``.
        """
        if self.contrast_floor is None:
            return foreground
        from charted.utils.colors import enforce_contrast_floor

        return enforce_contrast_floor(
            foreground, self.background_color, self.contrast_floor
        )

    @property
    def resolved_colors(self) -> list[str]:
        """Series palette with the contrast floor applied (if any).

        When ``contrast_floor`` is None this is just ``colors``, keeping every
        existing render byte-for-byte identical. Otherwise each palette colour
        is darkened/lightened until it clears the floor against the background.
        """
        if self.contrast_floor is None:
            return self.colors
        return [self.enforce_contrast(c) for c in self.colors]

    @property
    def resolved_quadrant_label_color(self) -> str:
        """Quadrant label color: root_color at 18% opacity."""
        from charted.utils.colors import derive_color

        return derive_color(
            self.root_color,
            OPACITY_TIERS["quadrant_label_color"],
            self.background_color,
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
                arrow_color="#374151",
            ),
            "dark": cls(
                colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
                root_color="#ffffff",
                grid_color="#9ca3af",
                title_color="#ffffff",
                background_color="#1a1a1a",
                legend_font_color="#e5e5e5",
                arrow_color="#d1d5db",
            ),
            "high-contrast": cls(
                # Okabe-Ito colourblind-safe palette: distinguishable under the
                # common forms of colour vision deficiency.
                colors=NAMED_PALETTES["okabe-ito"].copy(),
                title_color="#000000",
                title_font_size=18,
                background_color="#FFFFFF",
                grid_color="#000000",
                grid_width=1.5,
                # Every filled shape gets a 1px black outline so adjacent
                # wedges/bars/bubbles stay separable without relying on hue.
                shape_outline_color="#000000",
                shape_outline_width=1.0,
                # Heavier line strokes and larger markers so plotted series
                # read clearly for low-vision users.
                series_stroke_width=3.0,
                marker_size=5.0,
                reference_line_width=2.5,
                # Larger, bolder axis tick labels.
                axis_label_font_size=14,
                axis_label_font_weight="bold",
                # Darken washed-out palette hues (yellow/cyan/orange) until they
                # clear 3:1 against the white background.
                contrast_floor=3.0,
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

        # Get the default Theme instance to compare against
        default_theme = Theme()

        for key, override_value in overrides_dict.items():
            if key == "colors":
                if override_value and len(override_value) > 0:
                    new_values[key] = override_value.copy()
            else:
                # Compare against the default theme's value, not the class default
                default_value = getattr(default_theme, key)

                if override_value == default_value:
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
