from typing import Optional, TypedDict

from charted.utils.defaults import DEFAULT_COLORS, DEFAULT_FONT, DEFAULT_TITLE_FONT_SIZE


class LegendConfig(TypedDict):
    font_size: str | None
    legend_padding: float | None
    position: str | None


class MarkerConfig(TypedDict):
    marker_size = float | None


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
    v_grid = GridConfig | None
    h_grid = GridConfig | None

    @classmethod
    def load(cls, theme: Optional["Theme"]) -> "Theme":
        if not theme:
            return DEFAULT_THEME

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

        return deep_merge(DEFAULT_THEME.copy(), theme)


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
