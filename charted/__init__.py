"""Charted - A zero dependency SVG chart generator."""

__version__ = "1.0.0"

from .charts import (
    BarChart,
    Chart,
    ColumnChart,
    GanttChart,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)
from .data_loader import load_csv, load_data, load_json
from .markdown import chart_to_data_url, chart_to_markdown, inline_svg
from .themes import (
    ColorPalette,
    Theme,
    get_default_theme,
    get_theme,
    list_themes,
    register_theme,
    validate_theme,
)
from .utils.colors import calculate_contrast_ratio, hex_to_rgb, rgb_to_hex
from .utils.series_style import SeriesStyle

__all__ = [
    "__version__",
    "BarChart",
    "ColumnChart",
    "GanttChart",
    "LineChart",
    "PieChart",
    "RadarChart",
    "ScatterChart",
    "Chart",
    "load_data",
    "load_csv",
    "load_json",
    "chart_to_markdown",
    "inline_svg",
    "chart_to_data_url",
    "Theme",
    "ColorPalette",
    "register_theme",
    "list_themes",
    "get_theme",
    "get_default_theme",
    "validate_theme",
    "SeriesStyle",
    "hex_to_rgb",
    "rgb_to_hex",
    "calculate_contrast_ratio",
]
