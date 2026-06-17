"""Charted - A zero dependency SVG chart generator."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("charted")
except PackageNotFoundError:
    # Running from a source checkout without an installed distribution.
    __version__ = "1.2.0"

from .charts import (
    AreaChart,
    BarChart,
    BoxPlot,
    BubbleChart,
    Chart,
    ColumnChart,
    ComboChart,
    GanttChart,
    HeatmapChart,
    Histogram,
    LineChart,
    PieChart,
    PolarAreaChart,
    RadarChart,
    SankeyChart,
    ScatterChart,
)
from .charts.annotations import (
    BoxAnnotation,
    LabelAnnotation,
    LineAnnotation,
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
from .utils.exceptions import (
    ChartedError,
    DataShapeError,
    InvalidDataError,
    NoDataError,
    RenderError,
    ValidationError,
)
from .utils.series_style import SeriesStyle

__all__ = [
    "__version__",
    "AreaChart",
    "auto",
    "auto_size",
    "BarChart",
    "BoxAnnotation",
    "BoxPlot",
    "BubbleChart",
    "Chart",
    "ChartedError",
    "DataShapeError",
    "LabelAnnotation",
    "LineAnnotation",
    "chart_to_data_url",
    "chart_to_markdown",
    "ColumnChart",
    "ComboChart",
    "from_dataframe",
    "from_dict",
    "GanttChart",
    "HeatmapChart",
    "Histogram",
    "inline_svg",
    "InvalidDataError",
    "LineChart",
    "load_csv",
    "load_data",
    "load_json",
    "NAMED_PALETTES",
    "NoDataError",
    "PieChart",
    "PolarAreaChart",
    "RadarChart",
    "RenderError",
    "resolve_palette",
    "SankeyChart",
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
    "ValidationError",
]
