from typing import Optional, TypedDict

from charted.utils.defaults import DEFAULT_COLORS


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
    colors=DEFAULT_COLORS,
    v_grid=GridConfig(
        stroke="#CCCCCC",
        stroke_dasharray=None,
    ),
    h_grid=GridConfig(
        stroke="#CCCCCC",
        stroke_dasharray=None,
    ),
)
