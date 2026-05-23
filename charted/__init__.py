"""Charted - A zero dependency SVG chart generator."""

__version__ = "1.0.0"

from .charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    Chart,
    ColumnChart,
    GanttChart,
    HeatmapChart,
    Histogram,
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
from .themes.core import NAMED_PALETTES, resolve_palette
from .utils.colors import calculate_contrast_ratio, hex_to_rgb, rgb_to_hex
from .utils.data_input import auto, auto_size, from_dataframe, from_dict
from .utils.series_style import SeriesStyle

__all__ = [
    "__version__",
    "AreaChart",
    "auto",
    "auto_size",
    "BarChart",
    "BoxPlot",
    "Chart",
    "chart_to_data_url",
    "chart_to_markdown",
    "ColumnChart",
    "from_dataframe",
    "from_dict",
    "GanttChart",
    "HeatmapChart",
    "Histogram",
    "inline_svg",
    "LineChart",
    "load_csv",
    "load_data",
    "load_json",
    "NAMED_PALETTES",
    "PieChart",
    "RadarChart",
    "resolve_palette",
    "ScatterChart",
    "SeriesStyle",
    "Theme",
    "ColorPalette",
    "register_theme",
    "list_themes",
    "get_theme",
    "get_default_theme",
    "validate_theme",
    "hex_to_rgb",
    "rgb_to_hex",
    "calculate_contrast_ratio",
]
