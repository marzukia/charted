import copy
from typing import Optional, TypedDict

from charted.utils.defaults import DEFAULT_COLORS, DEFAULT_FONT, DEFAULT_TITLE_FONT_SIZE


class LegendConfig(TypedDict):
    font_size: str | None
    legend_padding: float | None
    position: str | None


class MarkerConfig(TypedDict):
    marker_size: float | None


class PaddingConfig(TypedDict):
    h_padding: float | None
    v_padding: float | None


class TitleConfig(TypedDict):
    font_size: str | None
    font_family: str | None
    font_weight: str | None
    font_color: str | None


class GridConfig(TypedDict):
    stroke: str | None
    stroke_dasharray: str | None


class Theme(TypedDict):
    colors: list[str] | None
    v_grid: GridConfig | None
    h_grid: GridConfig | None

    @classmethod
    def load(cls, theme: Optional["Theme"] | str = None) -> "Theme":
        """Load theme from dict, name, or None.

        Args:
            theme: Theme dict, preset name ("dark", "light", "high-contrast"), or None.

        Returns:
            Theme with defaults merged in.
        """
        if isinstance(theme, str):
            theme = PRESET_THEMES.get(theme, DEFAULT_THEME)
        elif not theme:
            return copy.deepcopy(DEFAULT_THEME)

        def deep_merge(default, custom):
            for key in custom:
                if key in default:
                    if isinstance(default[key], dict) and isinstance(custom[key], dict):
                        deep_merge(default[key], custom[key])
                    else:
                        default[key] = custom[key]
                else:
                    default[key] = custom[key]
            return default

        return deep_merge(copy.deepcopy(DEFAULT_THEME), theme)


# Preset theme definitions
DARK_THEME = Theme(
    legend=LegendConfig(
        font_size=11,
        legend_padding=0.25,
        position="topright",
    ),
    marker=MarkerConfig(
        marker_size=3,
    ),
    title=TitleConfig(
        font_size=DEFAULT_TITLE_FONT_SIZE,
        font_family=DEFAULT_FONT,
        font_weight="bold",
        font_color="#E0E0E0",
    ),
    colors=["#5fab9e", "#f58b51", "#f7dd72", "#db504a", "#2e4756"],
    v_grid=GridConfig(
        stroke="#444444",
        stroke_dasharray=None,
    ),
    h_grid=GridConfig(
        stroke="#444444",
        stroke_dasharray=None,
    ),
    padding=PaddingConfig(
        h_padding=0.05,
        v_padding=0.05,
    ),
)

LIGHT_THEME = Theme(
    legend=LegendConfig(
        font_size=11,
        legend_padding=0.25,
        position="topright",
    ),
    marker=MarkerConfig(
        marker_size=3,
    ),
    title=TitleConfig(
        font_size=DEFAULT_TITLE_FONT_SIZE,
        font_family=DEFAULT_FONT,
        font_weight="bold",
        font_color="#333333",
    ),
    colors=["#2e7d32", "#1565c0", "#c62828", "#f57c00", "#6a1b9a"],
    v_grid=GridConfig(
        stroke="#E0E0E0",
        stroke_dasharray="2,2",
    ),
    h_grid=GridConfig(
        stroke="#E0E0E0",
        stroke_dasharray="2,2",
    ),
    padding=PaddingConfig(
        h_padding=0.05,
        v_padding=0.05,
    ),
)

HIGH_CONTRAST_THEME = Theme(
    legend=LegendConfig(
        font_size=12,
        legend_padding=0.3,
        position="topright",
    ),
    marker=MarkerConfig(
        marker_size=4,
    ),
    title=TitleConfig(
        font_size=18,
        font_family=DEFAULT_FONT,
        font_weight="bold",
        font_color="#000000",
    ),
    colors=["#000000", "#FFFF00", "#00FFFF", "#FF00FF", "#00FF00"],
    v_grid=GridConfig(
        stroke="#000000",
        stroke_dasharray=None,
    ),
    h_grid=GridConfig(
        stroke="#000000",
        stroke_dasharray=None,
    ),
    padding=PaddingConfig(
        h_padding=0.05,
        v_padding=0.05,
    ),
)

PRESET_THEMES = {
    "dark": DARK_THEME,
    "light": LIGHT_THEME,
    "high-contrast": HIGH_CONTRAST_THEME,
}


DEFAULT_THEME = Theme(
    legend=LegendConfig(
        font_size=11,
        legend_padding=0.25,
        position="topright",
    ),
    marker=MarkerConfig(
        marker_size=3,
    ),
    title=TitleConfig(
        font_size=DEFAULT_TITLE_FONT_SIZE,
        font_family=DEFAULT_FONT,
        font_weight="bold",
        font_color="#444444",
    ),
    colors=DEFAULT_COLORS,
    v_grid=GridConfig(
        stroke="#CCCCCC",
        stroke_dasharray=None,
    ),
    h_grid=GridConfig(
        stroke="#CCCCCC",
        stroke_dasharray=None,
    ),
    padding=PaddingConfig(
        h_padding=0.05,
        v_padding=0.05,
    ),
)
