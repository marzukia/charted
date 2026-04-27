"""Charted - A zero dependency SVG chart generator."""

__version__ = "1.0.0"

from .charts import (
    BarChart,
    Chart,
    ColumnChart,
    LineChart,
    PieChart,
    RadarChart,
    ScatterChart,
)
from .data_loader import load_csv, load_data, load_json
from .markdown import chart_to_data_url, chart_to_markdown, inline_svg

__all__ = [
    "__version__",
    "BarChart",
    "ColumnChart",
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
]
